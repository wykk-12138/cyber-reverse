r"""Function-inventory comparison across the two live IDA instances.

WHY THIS TOOL EXISTS (AGENTS.md §1.2 requires the reason be stated):
REA is the project's declared second opinion, and its `compare_functions` / `compare_artifacts` would be
the natural home for this. They are not usable here: every native provider REA could route to is
unavailable in this session (`binary_session` observed ghidra=not_configured, hopper=unsupported_host,
kuna=not_configured, ida=not_configured), and the `ida` adapter only accepts the LEGACY tool profile
(`get_metadata` / `list_functions` / `decompile_function` from upstream 1.4.0) while this host's
`ida_pro_mcp` plugin serves the modern catalog (`list_funcs` / `decompile` / `server_health`). Downgrading
the plugin would break the 66-tool matrix 400+ rounds depend on; installing Ghidra would add a third
disassembly authority. The host already has TWO live IDA instances over a plain MCP endpoint -- the
original on 13337, the replica (with PDB symbols loaded) on 13338 -- so the honest thing is to ask those
two instances the same question and compare their inventories, rather than invent a new engine.

What this can and cannot answer (keep it straight):
    CAN   : function counts, how many are named on each side, the name inventory of the replica,
            which binding-table members are visible as their own function in the replica image.
    CANNOT: whether any two functions are semantically equivalent. That needs pseudocode-level
            comparison (decompile both sides and align); these instances are used at inventory level only.

Reproduce:
    cd D:\projects\cyber-reverse
    python analysis/func_compare.py              # both sides, summary
    python analysis/func_compare.py --page 0 --size 40
    python analysis/func_compare.py --export-only

Outputs land in analysis/ (original_funcs.txt, replica_funcs.txt, func_compare.md).
"""

import argparse
import datetime
import io
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BINDS = os.path.join(ROOT, "replica", "docs", "xaml_bindings.json")
OUT_DIR = os.path.join(ROOT, "analysis")

DEFAULT_ORIGINAL = "http://127.0.0.1:13337/mcp"
DEFAULT_REPLICA = "http://127.0.0.1:13338/mcp"

EXPORT_TEMPLATE = "\n".join([
    "import idautils, ida_funcs",
    "rows = []",
    "for ea in idautils.Functions():",
    "    f = ida_funcs.get_func(ea)",
    "    rows.append((ea, f.size() if f else 0, ida_funcs.get_func_name(ea) or ''))",
    "lines = ['%x\\t%d\\t%s' % r for r in rows]",
    "open(__DEST__, 'w', encoding='utf-8', newline=chr(10)).write(chr(10).join(lines))",
    "print('EXPORTED', len(rows))",
])


class Client:
    def __init__(self, url):
        self.url = url
        self._id = 0

    def _rpc(self, method, params=None, timeout=1800):
        self._id += 1
        body = json.dumps({"jsonrpc": "2.0", "id": self._id, "method": method,
                           "params": params or {}}).encode()
        req = urllib.request.Request(self.url, data=body,
                                     headers={"Content-Type": "application/json",
                                              "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))

    def initialize(self):
        self._rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                 "clientInfo": {"name": "cyber-reverse", "version": "1"}})

    def call(self, tool, args=None, timeout=1800):
        res = self._rpc("tools/call", {"name": tool, "arguments": args or {}}, timeout=timeout)
        if "error" in res:
            raise RuntimeError("%s: %s" % (tool, json.dumps(res["error"], ensure_ascii=False)))
        out = res.get("result", {})
        texts = [c.get("text", "") for c in (out.get("content") or []) if isinstance(c, dict)]
        return "\n".join(texts) if texts else json.dumps(out, ensure_ascii=False)


def _ready(health):
    """auto_analysis_ready from a server_health reply that may arrive as dict or JSON text."""
    if isinstance(health, str):
        try:
            health = json.loads(health)
        except json.JSONDecodeError:
            return None
    if isinstance(health, dict):
        # the plugin may nest the payload one level down
        if "auto_analysis_ready" in health:
            return health["auto_analysis_ready"]
        for v in health.values():
            if isinstance(v, dict) and "auto_analysis_ready" in v:
                return v["auto_analysis_ready"]
    return None


def export(url, dest, label):
    client = Client(url)
    client.initialize()
    health = client.call("server_health")

    # R697: refuse to export from an instance whose auto-analysis has not finished.
    # Port-open is not readiness -- the plugin answers while functions are still being recognised, and the partial
    # count is *stable* (wrong/right = 0.730 at both R433 and R694, 260 rounds apart), so two identical samples prove
    # nothing. This gate is the operational entry point for BLOCKERS 44/45, which until R697 lived only in a report.
    ready = _ready(health)
    if ready is not True:
        raise SystemExit(
            "%s: auto_analysis_ready is %r -- refusing to export.\n"
            "  Port-open is not readiness; functions are still being recognised.\n"
            "  Wait first:  python analysis/wait_ready.py <port> <timeout>\n"
            "  Background:  BLOCKERS 44/45 and 129, PARITY_PRODUCT section 8, IDA_STARTUP_CHECKLIST."
            % (label, ready))
    code = EXPORT_TEMPLATE.replace("__DEST__", repr(dest.replace("\\", "/")))
    raw = client.call("py_eval", {"code": code})
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        raise SystemExit("%s: py_eval did not return JSON: %s" % (label, raw[:400]))
    stdout = payload.get("stdout") or ""
    m = re.search(r"EXPORTED\s+(\d+)", stdout)
    if not m:
        stderr = payload.get("stderr") or ""
        raise SystemExit("%s: export failed\nstdout: %s\nstderr: %s"
                         % (label, stdout[:400], stderr[:400]))
    if not os.path.exists(dest):
        raise SystemExit("%s: IDA reported %s rows but %s is absent" % (label, m.group(1), dest))
    return int(m.group(1)), health


def load_rows(path):
    rows = []
    for line in io.open(path, encoding="utf-8", errors="replace"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 3 and parts[0]:
            rows.append((int(parts[0], 16), int(parts[1]), parts[2]))
    return rows


def binding_probe(rows, binds):
    """Which binding-table members are visible as their own function in the replica image.

    Suffix match (`endswith`), not substring: a substring test would count `Profile__Name` as present
    when the only symbol is `Profile__NameSort`, which is a different member. This is the same rule
    and therefore the same number as `replica/tools/aot_member_coverage.py` -- one figure, not two.
    """
    names = [r[2] for r in rows]
    hit, miss = [], []
    for full, members in sorted(binds.items()):
        short = full.split(".")[-1]
        for member in sorted(members):
            found = None
            for suffix in ("__get_" + member, "__set_" + member, "__" + member):
                needle = "_" + short + suffix
                if any(name.endswith(needle) for name in names):
                    found = suffix
                    break
            (hit if found else miss).append((short, member))
    return hit, miss


def size_hist(rows):
    buckets = [(0, 32), (32, 64), (64, 128), (128, 256), (256, 512),
               (512, 1024), (1024, 4096), (4096, 1 << 62)]
    counts = [0] * len(buckets)
    for _, size, _ in rows:
        for i, (lo, hi) in enumerate(buckets):
            if lo <= size < hi:
                counts[i] += 1
                break
    labels = ["%d-%d" % (lo, min(hi - 1, 99999)) for lo, hi in buckets]
    return list(zip(labels, counts))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--original-url", default=DEFAULT_ORIGINAL)
    parser.add_argument("--replica-url", default=DEFAULT_REPLICA)
    parser.add_argument("--page", type=int, default=0)
    parser.add_argument("--size", type=int, default=40)
    parser.add_argument("--export-only", action="store_true")
    args = parser.parse_args(argv)

    os.makedirs(OUT_DIR, exist_ok=True)
    orig_path = os.path.join(OUT_DIR, "original_funcs.txt")
    repl_path = os.path.join(OUT_DIR, "replica_funcs.txt")

    print("original  <- %s" % args.original_url)
    n_orig, health_orig = export(args.original_url, orig_path, "original")
    print("  exported %d rows -> %s" % (n_orig, orig_path))
    print("replica   <- %s" % args.replica_url)
    n_repl, health_repl = export(args.replica_url, repl_path, "replica")
    print("  exported %d rows -> %s" % (n_repl, repl_path))
    if args.export_only:
        return 0

    orig = load_rows(orig_path)
    repl = load_rows(repl_path)
    binds = json.load(io.open(BINDS, encoding="utf-8"))

    def named(rows):
        return sum(1 for _, _, name in rows if name and not name.startswith("sub_"))

    hit, miss = binding_probe(repl, binds)
    total_members = len(hit) + len(miss)
    pct = (100.0 * len(hit) / total_members) if total_members else 0.0

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp = now.strftime("%Y-%m-%d %H:%M:%S %z")

    lines = []
    lines.append("# 双实例函数清单对照（生成文件，请勿手改）")
    lines.append("")
    lines.append("> 由 `python analysis/func_compare.py` 生成。")
    lines.append("> 两条链：原版 `%s`、复刻件 `%s`（带 PDB 符号）。" % (args.original_url, args.replica_url))
    lines.append("")
    lines.append("| 项 | 值 |")
    lines.append("|---|---|")
    lines.append("| 生成时间 | %s |" % stamp)
    lines.append("| 原版函数总数 | %d |" % len(orig))
    lines.append("| 原版可命名函数 | %d |" % named(orig))
    lines.append("| 复刻件函数总数 | %d |" % len(repl))
    lines.append("| 复刻件可命名函数 | %d |" % named(repl))
    lines.append("| 差值（复刻件 − 原版） | %+d |" % (len(repl) - len(orig)))
    lines.append("| 原版 IDB / 镜像 | `%s` |" % (json.loads(health_orig).get("idb_path", "?") if health_orig.strip().startswith("{") else "?"))
    lines.append("| 复刻件 IDB / 镜像 | `%s` |" % (json.loads(health_repl).get("idb_path", "?") if health_repl.strip().startswith("{") else "?"))
    lines.append("")
    lines.append("## 函数大小分布（同口径）")
    lines.append("")
    lines.append("| 区间（字节） | 原版 | 复刻件 |")
    lines.append("|---|---|---|")
    for (label, a), (_, b) in zip(size_hist(orig), size_hist(repl)):
        lines.append("| %s | %d | %d |" % (label, a, b))
    lines.append("")
    lines.append("## 绑定表成员在复刻件侧的命中率")
    lines.append("")
    lines.append("| 项 | 值 |")
    lines.append("|---|---|")
    lines.append("| 绑定成员总数 | %d |" % total_members)
    lines.append("| 在复刻件镜像里可见（独立符号） | %d |" % len(hit))
    lines.append("| 命中率 | %.1f%% |" % pct)
    lines.append("")
    lines.append("> **命中率低不等于缺口**：NativeAOT 会内联/裁剪不可达成员，属性 getter 常无独立符号。")
    lines.append("> 按 `docs/PARITY_CLAIMS.md` 的证据纪律，看不到 ≠ 不存在，本条整体记 Unknown。")
    lines.append("")

    start = args.page * args.size
    end = start + args.size
    lines.append("## 复刻件侧可命名函数（分页 %d，每页 %d，共 %d）" % (args.page, args.size, named(repl)))
    lines.append("")
    named_rows = [(a, s, n) for a, s, n in repl if n and not n.startswith("sub_")]
    lines.append("| 地址 | 大小 | 名字 |")
    lines.append("|---|---|---|")
    for a, s, n in named_rows[start:end]:
        lines.append("| `0x%x` | %d | `%s` |" % (a, s, n))
    lines.append("")
    lines.append("## 绑定成员未命中的清单（分页 %d，每页 %d，共 %d）" % (args.page, args.size, len(miss)))
    lines.append("")
    lines.append("| 类型 | 成员 |")
    lines.append("|---|---|")
    for short, member in miss[start:end]:
        lines.append("| %s | %s |" % (short, member))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 这两条链能回答什么 / 不能回答什么")
    lines.append("")
    lines.append("**能**：函数数量、各侧可命名数、复刻件名字清单、绑定成员在产物里的可见性、函数大小分布。")
    lines.append("")
    lines.append("**不能**：任意两个函数是否语义等价 —— 那需要**伪代码级**对照（两侧 `decompile` 后对齐），")
    lines.append("本次两个实例只做清单级对照。claim C7（逐函数等价）因此记 Unknown，")
    lines.append("缺的证据写在 `docs/PARITY_CLAIMS.md`。")
    lines.append("")

    out_path = os.path.join(OUT_DIR, "func_compare.md")
    io.open(out_path, "w", encoding="utf-8").write("\n".join(lines) + "\n")

    print()
    print("original : %d functions, %d named" % (len(orig), named(orig)))
    print("replica  : %d functions, %d named" % (len(repl), named(repl)))
    print("binding members visible in replica image: %d/%d (%.1f%%)"
          % (len(hit), total_members, pct))
    print("wrote %s" % out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
