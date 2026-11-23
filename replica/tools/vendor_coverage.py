"""Generate docs/VENDOR_COVERAGE.md -- the original's risk-vendor list against VendorWiring's rows.

Completion criterion (f) asks for the vendor list to be taken from the binary and reconciled row by row against the
replica. R1040-R1045 showed the store catalogue cannot be had that way, but the vendor list can: the original names its
own solvers in user-facing progress text, and that family is data, not symbols.

Why a generator rather than a document: R1030 recorded that append-only lists fossilise, R1041 that hand-written tables
drift from the tools that produce them. This re-probes the image and re-reads VendorWiring on every run.

Controls: the family is only an inventory if vendors known to be present appear in it. kpsdk and datadome are probed
alongside, and their counts are printed first so a zero beneath them can be read.

Run: python tools/vendor_coverage.py   (writes docs/VENDOR_COVERAGE.md)
"""

import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "docs", "VENDOR_COVERAGE.md")
WIRING = os.path.join(ROOT, "src", "Cybersole.Stores", "Scripts", "VendorWiring.cs")
STORE_FLOW = os.path.join(ROOT, "src", "Cybersole.Stores", "Flows", "StoreFlow.cs")
CF_STRATEGY = os.path.join(ROOT, "src", "Cybersole.Stores", "Scripts", "CloudflareStrategy.cs")
DD_CLEARANCE = os.path.join(ROOT, "src", "Cybersole.Stores", "Scripts", "DataDomeClearance.cs")

SITE_ANTIBOT_VENDORS = {
    "Akamai", "BotDeflector", "Cloudflare", "DataDome", "Kasada", "PerimeterX", "Queue-it", "Vercel",
}

# The image's own vocabulary. Each vendor needs its own probe because the wording differs per vendor -- Kasada never
# appears in the Solving family at all, and Queue-it only ever appears in an error line, which is exactly the kind of
# shape difference AGENTS 2.7 warns about.
VENDORS = [
    ("Akamai", r"Solving Akamai \("),
    ("BotDeflector", r"Solving BotDeflector"),
    ("Cloudflare", r"Solving Cloudflare \("),
    ("DataDome", r"Solving DataDome \("),
    ("Kasada", r"kpsdk"),
    ("PerimeterX", r"Solving PerimeterX"),
    ("Queue-it", r"Solving Queue-it"),
    ("Vercel", r"Solving Vercel"),
    ("Stripe challenge", r"Solving Stripe challenge"),
    ("PayPal 3DS", r"Solving PayPal 3DS"),
    ("captcha", r"Solving captcha \("),
    ("proof of work", r"Solving POW challange"),
    ("checkpoint", r"Solving checkpoint"),
]

CONTROLS = [("kpsdk", r"kpsdk"), ("datadome", r"datadome")]

# R1048: the seven gaps the reconciliation finds are not one kind of thing, and criterion (f) asks each uncovered item
# to say why. Three of them are challenge types the Row shape does not model -- they are not vendors, and adding them
# as rows would make the table claim something false about its own subject. The other four are missing rows, and the
# disposition column says what each needs before a row can be written honestly.
DISPOSITION = {
    "BotDeflector": (
        "vendor",
        "原版有两条文案（`Solving BotDeflector icons` · `Solving BotDeflector proof of work`），"
        "所以它是**两种挑战**（图标点选 + PoW）。补行需要先定 `Solver`：镜像里没有第三方指向，"
        "但那不等于自建 —— R1029 的 `Relayed` 两轴就是为这种情形留的。",
    ),
    "Vercel": (
        "vendor",
        "只有 `Solving Vercel` 一条，没有分期文案。补行的最小诚实形态是 `State.DetectedOnly` + "
        "`Solver.Unknown`，因为镜像只证明它被走到，不证明怎么解。",
    ),
    "Stripe challenge": (
        "payment",
        "支付侧挑战，不是站点风控。`VendorWiring` 是站点风控台账 ⇒ **不该进这张表**；"
        "它属于支付层（`AdyenGateway` 那一族），要在那里记。",
    ),
    "PayPal 3DS": (
        "payment",
        "九条分期文案（`(1)`…`(8)` 加 `(2.1)` 子阶段），是 3DS 流程的阶段，同样**不属于站点风控台账**。"
        "→ 归支付层。分期数本身是有用证据：3DS 有 9 个可观察阶段（详见 `PAYMENT_CHALLENGES.md`）。",
    ),
    "captcha": ("challenge", "通用验证码挑战，不是某个厂商 ⇒ 台账形状不建模，且不该建模。"),
    "proof of work": ("challenge", "通用 PoW 挑战，同上。注意镜像原文拼作 `challange` —— 保留拼写，不修正。"),
    "checkpoint": ("challenge", "通用检查点，同上。"),
}


def probe(pattern, limit=600):
    p = subprocess.run(
        [sys.executable, os.path.join(REPO, "analysis", "ida.py"), "str", pattern, "--limit", str(limit)],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        return json.loads((p.stdout or "").strip())
    except Exception:
        m = re.search(r"\{.*\}", p.stdout or "", re.S)
        return json.loads(m.group(0)) if m else {"n": 0, "matches": []}


def wiring_rows():
    """Each row is `new Row("vendor", "marker", cookie, State.X, ... Solver.Y, bool)`.

    R1047: the first version looked for `Vendor.X` and found nothing, then reported all thirteen image vendors as
    missing -- a wrong parser producing a confident false inventory, which is the R764 shape. The vendor is a plain
    lowercase string, so the split is on the constructor and each block is parsed for its state, solver and relay.
    """
    if not os.path.exists(WIRING):
        # R1296: R1282 removed VendorWiring.cs because nothing in the running product called it. The
        # image-side vendor inventory is still a real measurement, so "the table is gone" must not look
        # like "the parser found nothing".
        return None
    text = io.open(WIRING, encoding="utf-8", errors="replace").read()
    rows = []
    for block in text.split("new Row(")[1:]:
        m = re.match(r'\s*"([a-z0-9\-]+)"', block)
        if not m:
            continue
        vendor = m.group(1)
        head = block[:1200]
        state = re.search(r"State\.(\w+)", head)
        solver = re.search(r"Solver\.(\w+)", head)
        relay = re.search(r"Solver\.\w+,\s*(true|false)", head)
        rows.append((vendor,
                     state.group(1) if state else "?",
                     solver.group(1) if solver else "?",
                     relay.group(1) == "true" if relay else None))
    return rows


def runtime_vendor_audit():
    """Inspect StoreFlow.SolveDetectedWallAsync to measure real runtime anti-bot solver wiring.

    R1382: R1282 deleted VendorWiring.cs, and R1296 then short-circuited `missing` to 0 whenever the table
    was absent — making METRICS.md read `wiring rows=0 / missing=0` while 7 of 8 site anti-bot vendors have
    no live runtime solver (Cloudflare and DataDome call `.Default()` with null callbacks; Akamai, BotDeflector,
    PerimeterX, Queue-it and Vercel are not dispatched in SolveDetectedWallAsync at all).
    """
    flow_text = io.open(STORE_FLOW, encoding="utf-8", errors="replace").read() if os.path.exists(STORE_FLOW) else ""
    cf_text = io.open(CF_STRATEGY, encoding="utf-8", errors="replace").read() if os.path.exists(CF_STRATEGY) else ""
    dd_text = io.open(DD_CLEARANCE, encoding="utf-8", errors="replace").read() if os.path.exists(DD_CLEARANCE) else ""

    m = re.search(r"SolveDetectedWallAsync\([^)]*\)\s*\{(?P<body>.*?\n    \})", flow_text, re.S)
    body = m.group("body") if m else ""

    rows = []
    # Check each of the 8 site anti-bot vendors against actual runtime dispatch in SolveDetectedWallAsync
    for vendor in ("Akamai", "BotDeflector", "Cloudflare", "DataDome", "Kasada", "PerimeterX", "Queue-it", "Vercel"):
        key = vendor.lower()
        if key == "kasada":
            has_live = ("KasadaStrategyRunner.Default(" in body and
                        ("ChromiumKasadaSolver" in body or "HttpKasadaSolver" in body))
            rows.append((vendor, "RuntimeWired" if has_live else "NotDispatched",
                         "ChromiumKasadaSolver + HttpKasadaSolver", False))
        elif key == "cloudflare":
            dispatched = "CloudflareClearance" in body
            default_null = ("CloudflareStrategyRunner.Default()" in body and
                            "serviceCall = null" in cf_text and "inBotSolve = null" in cf_text)
            state = "StubDefaultNull" if (dispatched and default_null) else ("RuntimeWired" if dispatched else "NotDispatched")
            rows.append((vendor, state, "CloudflareStrategyRunner.Default() (null callbacks)" if default_null else "Custom", True))
        elif key == "datadome":
            dispatched = "DataDomeClearance" in body
            default_null = ("InjectedDataDomeSensor.Default()" in body and "call = null" in dd_text)
            state = "StubDefaultNull" if (dispatched and default_null) else ("RuntimeWired" if dispatched else "NotDispatched")
            rows.append((vendor, state, "InjectedDataDomeSensor.Default() (null callback)" if default_null else "Custom", True))
        else:
            dispatched = f'"{key}"' in body
            rows.append((vendor, "RuntimeWired" if dispatched else "NotDispatched", "None", False))
    return rows


def main():
    controls = [(name, probe(pat).get("n", -1)) for name, pat in CONTROLS]
    control_ok = all(n > 0 for _, n in controls)
    if not control_ok:
        print("  !! controls failed (%s) -- IDA is not ready; refusing to overwrite docs/VENDOR_COVERAGE.md with false zeros"
              % ", ".join("%s=%d" % (k, v) for k, v in controls))
        return 2

    found = []
    for name, pattern in VENDORS:
        d = probe(pattern)
        n = d.get("n", -1)
        addr = (d.get("matches") or [{}])[0].get("addr", "")
        found.append((name, pattern, n, addr))

    rows = wiring_rows()
    wiring_removed = rows is None
    runtime_rows = runtime_vendor_audit() if wiring_removed else []
    if wiring_removed:
        rows = runtime_rows
        live_wired = {r[0] for r in runtime_rows if r[1] == "RuntimeWired"}
        # Every site anti-bot vendor present in the image without a live runtime solver is an honest gap.
        missing = [(name, n, addr) for name, _pat, n, addr in found
                   if n > 0 and name in SITE_ANTIBOT_VENDORS and name not in live_wired]
        live_count = len(live_wired)
    elif not rows:
        print("  !! parsed zero wiring rows -- refusing to publish a table that would claim every vendor is missing")
        return 2
    else:
        wired = {r[0] for r in rows}
        missing = []
        for name, pattern, n, addr in found:
            if n <= 0:
                continue
            stem = re.sub(r"[^a-z]", "", name.lower())[:5]
            if not any(stem in k for k in wired):
                missing.append((name, n, addr))
        live_count = len(rows)

    lines = []
    add = lines.append
    add("# 风控厂商覆盖表（生成物 —— 不要手改）")
    add("")
    add("由 `python tools/vendor_coverage.py` 生成。完成判据 (f) 的风控一半：")
    if wiring_removed:
        add("**原版清单从二进制取证 ↔ 复刻件运行时 `StoreFlow.SolveDetectedWallAsync` 真实求解接线核查**（R1382 修复了 R1296 删表后将 `missing` 强行置 0 的口径遮蔽）。")
    else:
        add("**原版清单从二进制取证 ↔ `VendorWiring` 逐条对**。")
    add("")
    add("## 一、对照是否成立")
    add("")
    add("| 对照串 | 命中 |")
    add("|---|---|")
    for name, n in controls:
        add("| `%s` | **%d** |" % (name, n))
    add("")
    add("**→ 对照%s。**" % ("成立，下方的零可读" if control_ok else "不成立 —— 下方的零不可读，本表作废"))
    add("")
    add("## 二、原版在进度文案里点名的求解对象")
    add("")
    add("**取证依据**：原版对用户显示 `Solving <X>` 形式的进度文案，那是**它自己写的**清单，"
        "而不是我们的分类。")
    add("")
    add("| 厂商/挑战 | 命中 | 首条地址 |")
    add("|---|---|---|")
    for name, pattern, n, addr in found:
        add("| **%s** | **%d** | `%s` |" % (name, n, addr or "—"))
    add("")
    add("**注意形状差异**（AGENTS §2.7）：Kasada 从不以 `Solving` 出现 —— 它只在 `x-kpsdk-*` 头里；")
    add("Queue-it 只在 `Error Solving Queue-it (Softblock)` 这一条错误文案里。")
    add("**所以「用同一个前缀扫全体」会漏掉两家**，这也是每个厂商单独一条查询的原因。")
    add("")
    add("## 三、与复刻件运行时反爬分派（`StoreFlow.SolveDetectedWallAsync`）的对账")
    add("")
    add("8 家站点风控中，运行时实际接通非空求解器：**%d** 家；未接通或仅空回调占位：**%d** 家：" % (live_count, len(missing)))
    add("")
    add("| Vendor | State | Solver | Relayed |")
    add("|---|---|---|---|")
    for name, state, solver, relayed in rows:
        add("| `%s` | `%s` | `%s` | %s |" % (name, state, solver, relayed))
    add("")
    add("### 原版点名而复刻件运行时未接通求解的站点风控（%d）" % len(missing))
    add("")
    if missing:
        add("| 缺的 | 命中 | 类别 | 处置 |")
        add("|---|---|---|---|")
        state_map = {r[0]: (r[1], r[2]) for r in rows}
        for name, n, addr in missing:
            st, slv = state_map.get(name, ("?", "?"))
            default_why = ("运行时状态 `%s`（`%s`）；" % (st, slv)) + DISPOSITION.get(
                name, ("vendor", "原版有明确求解文案，复刻件运行时尚未接通可用求解器。"))[1]
            kind = DISPOSITION.get(name, ("vendor", ""))[0]
            add("| **%s** | %d | %s | %s |" % (name, n, kind, default_why))
        add("")
        add("**→ 说明**：支付侧挑战（`Stripe challenge`、`PayPal 3DS`）归支付层单独核查；通用挑战名（`captcha`、`proof of work`、`checkpoint`）不按单厂商计缺口。")
    else:
        add("（无）")
    add("")
    add("## 四、边界")
    add("")
    add("- **有文案不等于有本地自建 solver**：文案说明原版走到那一步，而它交给第三方、自建还是内联，要按反编译证据核实。")
    add("- **没有文案不等于没处理**：Kasada 与 Queue-it 都已经证明这一点（形状不同）。")
    add("- **对照只能证明「查得到」**：前缀查询 > 0 不等于该厂商在所有站上都启用。")
    add("")

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines))
    print("  wrote docs/VENDOR_COVERAGE.md")
    print("  controls ok=%s  vendors named=%d  wiring rows=%d  missing=%d"
          % (control_ok, sum(1 for f in found if f[2] > 0), live_count, len(missing)))
    for name, n, addr in missing:
        print("    missing: %-18s n=%-3d %s" % (name, n, addr))
    return 0


if __name__ == "__main__":
    sys.exit(main())
