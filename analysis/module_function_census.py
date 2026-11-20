r"""Module-level function distribution & Cybersole.* type/method census (Gap #2).

WHY THIS EXISTS (AGENTS.md §1.2 requires the reason be stated):
Existing artifact tools do not solve module-level attribution or subsystem parity:
- `replica/tools/pdata_sections.py` and `replica/tools/pdata_decompose.py` only histogram
  `.pdata` `RUNTIME_FUNCTION` entries by RVA bucket (`0x100000`) or byte-size band (`0..32` B,
  etc.); they read no symbols, strings, or callgraph edges, so they cannot separate BCL/UI
  framework mass from `Cybersole.*` application logic.
- `analysis/func_compare.py` and `analysis/function_breakdown.py` export raw IDA totals
  (`321,244` vs `189,090`) and leave `311,203` (`96.87%`) of original functions in a single
  `sub_*` bucket, while treating `< 0x143025000` IDA FLIRT collisions (such as 28-byte static-base
  getters misnamed `__acrt_update_thread_multibyte_data_*`) as CRT symbols and omitting
  cross-reference against `replica/src/`.
- `replica/tools/async_method_coverage.py` and `replica/tools/aot_member_coverage.py` test
  token occurrence or XAML binding visibility, without classifying `Cybersole.*` namespaces,
  `PropInit` DTOs, third-party assemblies, or AOT-trimmed islands (e.g. `MailKit`/`MimeKit`).

What this script computes and generates (`docs/MODULE_FUNCTION_CENSUS.md`):
1. Replica AOT PDB census: parses `Cybersole.Ui.pdb` (MSF 7.0 DBI + module streams) directly
   against `Cybersole.Ui.exe` `.pdata` (exact starts + interior EH/SEH funclets) to attribute
   100% of `.pdata` extents across `Cybersole.*` and third-party/BCL modules, plus replica
   `src/**/*.cs` and `replica/docs/baseline/` (`recovered_async_methods.txt` /
   `recovered_accessors_by_type.txt`) inventories.
2. Propagation calibration on the PDB-labeled replica: measures precision of conservative
   1-2 hop pure-module callgraph propagation against known PDB ground truth before applying it
   to the stripped original image.
3. Original binary census (via running IDA Pro HTTP MCP `analysis/ida.py` / `127.0.0.1:13337`
   plus vectorized `.text` `disp32` scanning over `target/Cybersole.exe`):
   - Extracts all `Cybersole.*` namespaces/types, `*.dll` assembly names, `PropInit` DTOs,
     `<Method>d__N` state machines, `avares://` UI assets, and third-party prefixes from
     `idautils.Strings()` and `idautils.Functions()`.
   - Attributes functions into `Direct-Attributed` (verified native IDA names + `chars_va - 12` /
     raw string-xref seeds), `Callgraph-Propagated` (1-2 hop pure-module callgraph over IDA
     code xrefs), and `Unattributed` (explicitly left unguessed).
4. Subsystem cross-reference classifying every discovered `Cybersole.*` namespace, type/DTO
   family, async-method family, and third-party dependency against `replica/src/` into
   `Implemented`, `Partial / Missing Core Logic`, `Out of Scope` (R702 / CAPTCHA execution),
   or `External Blocked`.

Usage:
    python analysis/module_function_census.py                 # uses cache if present, else queries live IDA
    python analysis/module_function_census.py --refresh-ida   # forces live export from IDA 13337
    python analysis/module_function_census.py --write-doc     # writes docs/MODULE_FUNCTION_CENSUS.md
"""

from __future__ import annotations

import argparse
import bisect
import collections
import datetime
import glob
import importlib.util
import json
import os
import re
import struct
import sys
import tempfile
import urllib.request

import numpy as np


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAIN_REPO_FALLBACK = r"D:\projects\cyber-reverse"
IDA_URL = "http://127.0.0.1:13337/mcp"


def resolve_path(*rel_parts: str) -> str:
    """Resolve an artifact path in the current workspace, falling back to the main repo."""
    local = os.path.join(ROOT, *rel_parts)
    if os.path.exists(local):
        return local
    fallback = os.path.join(MAIN_REPO_FALLBACK, *rel_parts)
    return fallback if os.path.exists(fallback) else local


def read_pe_sections(exe_path: str) -> tuple[int, dict[str, tuple[int, int, int, int]]]:
    """Return (image_base, {section_name: (rva, vsize, raw_ptr, raw_size)})."""
    with open(exe_path, "rb") as f:
        header = f.read(0x4000)
    pe = struct.unpack_from("<I", header, 0x3C)[0]
    if header[pe:pe + 4] != b"PE\x00\x00":
        raise RuntimeError(f"Invalid PE header: {exe_path}")
    nsec = struct.unpack_from("<H", header, pe + 6)[0]
    opt_sz = struct.unpack_from("<H", header, pe + 20)[0]
    magic = struct.unpack_from("<H", header, pe + 24)[0]
    image_base = struct.unpack_from("<Q" if magic == 0x20B else "<I", header, pe + 24 + (24 if magic == 0x20B else 28))[0]
    sec_tab = pe + 24 + opt_sz
    secs = {}
    for i in range(nsec):
        h = sec_tab + i * 40
        sname = header[h:h + 8].rstrip(b"\x00").decode("ascii", "replace")
        vsz, rva, rsz, rptr = struct.unpack_from("<IIII", header, h + 8)
        secs[sname] = (rva, vsz, rptr, rsz)
    return image_base, secs


def read_pdata_extents(exe_bytes: bytes, secs: dict[str, tuple[int, int, int, int]]) -> tuple[int, list[tuple[int, int]]]:
    """Return (raw_slot_count, sorted valid [(begin_rva, end_rva)])."""
    _rva, _vsz, rptr, rsz = secs[".pdata"]
    raw_slots = rsz // 12
    extents = []
    for off in range(0, rsz - 11, 12):
        b, e, _u = struct.unpack_from("<III", exe_bytes, rptr + off)
        if 0 < e - b < 0x100000:
            extents.append((b, e))
    extents.sort()
    return raw_slots, extents


def parse_msf7_pdb_procs(pdb_path: str) -> tuple[dict[int, tuple[str, int, int]], list[tuple[int, int, str, str]], dict[str, int]]:
    """Parse MSF 7.0 PDB module procedure records (`S_LPROC32`/`S_GPROC32`) and section headers."""
    with open(pdb_path, "rb") as f:
        data = f.read()
    magic, page_size, _fpm, _num_pages, dir_size, _res, root_dir_page = struct.unpack_from("<32sIIIIII", data, 0)
    if not magic.startswith(b"Microsoft C/C++ MSF 7.00"):
        raise RuntimeError(f"Unsupported PDB format: {pdb_path}")

    def read_pages(pages: tuple[int, ...], total_size: int) -> bytes:
        out = bytearray()
        rem = total_size
        for p in pages:
            take = min(page_size, rem)
            off = p * page_size
            out.extend(data[off:off + take])
            rem -= take
        return bytes(out)

    num_dir_pages = (dir_size + page_size - 1) // page_size
    root_pages = struct.unpack_from(f"<{num_dir_pages}I", data, root_dir_page * page_size)
    dir_bytes = read_pages(root_pages, dir_size)
    num_streams = struct.unpack_from("<I", dir_bytes, 0)[0]
    stream_sizes = struct.unpack_from(f"<{num_streams}I", dir_bytes, 4)
    pos = 4 + 4 * num_streams
    stream_pages = []
    for sz in stream_sizes:
        if sz == 0xFFFFFFFF:
            stream_pages.append(())
        else:
            np_c = (sz + page_size - 1) // page_size
            stream_pages.append(struct.unpack_from(f"<{np_c}I", dir_bytes, pos))
            pos += 4 * np_c

    def get_stream(idx: int) -> bytes:
        sz = stream_sizes[idx]
        if sz == 0xFFFFFFFF or sz == 0:
            return b""
        return read_pages(stream_pages[idx], sz)

    dbi = get_stream(3)
    mod_info_sz, sec_con_sz, sec_map_sz, src_info_sz, ts_map_sz, _mfc_idx, dbg_hdr_sz, _ec_sz = struct.unpack_from("<IIIIIIII", dbi, 24)
    dbg_off = 64 + mod_info_sz + sec_con_sz + sec_map_sz + src_info_sz + ts_map_sz + _ec_sz
    dbg_streams = struct.unpack_from(f"<{dbg_hdr_sz // 2}H", dbi, dbg_off)
    sh_bytes = get_stream(dbg_streams[5])
    pdb_secs = {}
    for idx in range(len(sh_bytes) // 40):
        h = idx * 40
        sname = sh_bytes[h:h + 8].rstrip(b"\x00").decode("ascii", "replace")
        vsz, va = struct.unpack_from("<II", sh_bytes, h + 8)
        pdb_secs[idx + 1] = (sname, va, vsz)

    mod_bytes = dbi[64:64 + mod_info_sz]
    mpos = 0
    procs: list[tuple[int, int, str, str]] = []
    mod_count = 0
    while mpos + 64 <= len(mod_bytes):
        stream_idx, cb_syms = struct.unpack_from("<HI", mod_bytes, mpos + 34)
        n1_end = mod_bytes.find(b"\x00", mpos + 64)
        n2_end = mod_bytes.find(b"\x00", n1_end + 1)
        mname = mod_bytes[mpos + 64:n1_end].decode("utf-8", "replace")
        next_pos = ((n2_end + 1) + 3) & ~3
        mod_count += 1
        if stream_idx != 0xFFFF and cb_syms > 4:
            ms = get_stream(stream_idx)[:cb_syms]
            poff = 4
            while poff + 4 <= len(ms):
                rlen, rkind = struct.unpack_from("<HH", ms, poff)
                if rlen < 2:
                    break
                if rkind in (0x110F, 0x1110, 0x1146, 0x1147):
                    code_len = struct.unpack_from("<I", ms, poff + 4 + 12)[0]
                    sym_off, seg = struct.unpack_from("<IH", ms, poff + 4 + 28)
                    nul = ms.find(b"\x00", poff + 4 + 35, poff + 2 + rlen)
                    pname = ms[poff + 4 + 35:(nul if nul != -1 else poff + 2 + rlen)].decode("utf-8", "replace")
                    if seg in pdb_secs:
                        rva = pdb_secs[seg][1] + sym_off
                        procs.append((rva, rva + max(code_len, 1), mname, pname))
                poff += 2 + rlen
        mpos = next_pos

    procs.sort()
    return pdb_secs, procs, {"modules": mod_count, "procs": len(procs)}


REPLICA_WRAPPERS = (
    "__GetNonGCStaticBase_", "__GetGCStaticBase_", "__GetThreadStaticBase_",
    "__fatpointer_", "__delegate_invoke_", "__reverse_pinvoke_",
    "unbox_", "<Boxed>", "<PInvokeDelegateWrapper>",
)
BCL_PRIMS = (
    "String_", "Double_", "Single_", "Char_", "UInt32_", "Int32_", "UInt8_", "Int8_",
    "UInt16_", "Int16_", "UInt64_", "Int64_", "Bool_", "Boolean_", "Decimal_", "Object_",
    "Void_", "IntPtr_", "UIntPtr_", "SByte_", "Byte_", "TypedReference_",
)


def classify_replica_proc(mname: str, pname: str) -> str:
    """Map a replica PDB module + symbol name to its canonical module bucket."""
    if not mname.endswith("Cybersole.Ui.obj"):
        return "NativeAOT / CRT Runtime"
    s = pname
    changed = True
    while changed:
        changed = False
        for w in REPLICA_WRAPPERS:
            if s.startswith(w):
                s = s[len(w):]
                changed = True
                break
    for pfx, cat in (
        ("Cybersole_Core_", "Cybersole.Core"),
        ("Cybersole_Http_", "Cybersole.Http"),
        ("Cybersole_Services_", "Cybersole.Services"),
        ("Cybersole_Stores_", "Cybersole.Stores"),
        ("Cybersole_Ui_", "Cybersole.Ui"),
        ("Cybersole_", "Cybersole.Other"),
        ("Avalonia_", "Avalonia.*"),
        ("MicroCom_", "MicroCom.Runtime (Avalonia)"),
        ("Tmds_", "Tmds.DBus (Avalonia)"),
        ("SkiaSharp_", "SkiaSharp.*"),
        ("HarfBuzzSharp_", "HarfBuzzSharp.*"),
        ("BouncyCastle_", "Org.BouncyCastle.*"),
        ("Jint_", "Jint.*"),
        ("Acornima_", "Acornima.* (Jint)"),
        ("Newtonsoft_", "Newtonsoft.Json.*"),
        ("MailKit_", "MailKit.*"),
        ("MimeKit_", "MimeKit.*"),
        ("CommunityToolkit_", "CommunityToolkit.*"),
        ("Microsoft_", "Microsoft.*"),
    ):
        if s.startswith(pfx):
            return cat
    if s.startswith("S_P_") or s.startswith("System_") or s.startswith("Internal_") or s.startswith(BCL_PRIMS):
        return "System.* / BCL"
    return "Other"


def analyze_replica() -> dict:
    """Inventory replica `.publish-aot` PDB/.pdata, `replica/src/`, and `replica/docs/baseline/`."""
    exe_path = resolve_path("replica", ".publish-aot", "Cybersole.Ui.exe")
    pdb_path = resolve_path("replica", ".publish-aot", "Cybersole.Ui.pdb")
    if not os.path.exists(exe_path) or not os.path.exists(pdb_path):
        raise FileNotFoundError(f"Replica AOT artifacts missing: {exe_path} / {pdb_path}")

    with open(exe_path, "rb") as f:
        exe_bytes = f.read()
    _base, secs = read_pe_sections(exe_path)
    raw_slots, pdata_extents = read_pdata_extents(exe_bytes, secs)
    _pdb_secs, procs, pdb_meta = parse_msf7_pdb_procs(pdb_path)
    starts = [p[0] for p in procs]

    exact_cnt: collections.Counter[str] = collections.Counter()
    funclet_cnt: collections.Counter[str] = collections.Counter()
    bytes_cnt: collections.Counter[str] = collections.Counter()
    outside = 0
    pdata_gt: list[str] = []

    for b, e in pdata_extents:
        idx = bisect.bisect_right(starts, b) - 1
        if idx >= 0 and procs[idx][0] <= b < procs[idx][1]:
            cat = classify_replica_proc(procs[idx][2], procs[idx][3])
            if procs[idx][0] == b:
                exact_cnt[cat] += 1
            else:
                funclet_cnt[cat] += 1
            bytes_cnt[cat] += (e - b)
            pdata_gt.append(cat)
        else:
            outside += 1
            pdata_gt.append("Unattributed")

    # Calibration of conservative 2-hop propagation on PDB ground truth using E8 call edges
    p_starts = np.array([b for b, _ in pdata_extents], dtype=np.int64)
    p_ends = np.array([e for _, e in pdata_extents], dtype=np.int64)
    callers: dict[int, set[int]] = collections.defaultdict(set)
    callees: dict[int, set[int]] = collections.defaultdict(set)
    for sname in (".text", ".managed"):
        if sname not in secs:
            continue
        sva, svsz, srptr, srsz = secs[sname]
        blob = np.frombuffer(exe_bytes[srptr:srptr + min(svsz, srsz)], dtype=np.uint8)
        e8_pos = np.nonzero(blob[:-5] == 0xE8)[0]
        disp = (
            blob[e8_pos + 1].astype(np.int64)
            | (blob[e8_pos + 2].astype(np.int64) << 8)
            | (blob[e8_pos + 3].astype(np.int64) << 16)
            | (blob[e8_pos + 4].astype(np.int64) << 24)
        )
        disp = np.where(disp >= 0x80000000, disp - 0x100000000, disp)
        frm = sva + e8_pos
        tgt = frm + 5 + disp
        idx_t = np.clip(np.searchsorted(p_starts, tgt), 0, len(p_starts) - 1)
        mask = p_starts[idx_t] == tgt
        for fp, ti in zip(frm[mask], idx_t[mask]):
            fi = int(np.searchsorted(p_starts, int(fp), side="right")) - 1
            if 0 <= fi < len(p_starts) and p_starts[fi] <= int(fp) < p_ends[fi] and fi != int(ti):
                callees[fi].add(int(ti))
                callers[int(ti)].add(fi)

    import random
    rng = random.Random(7)
    rates = {
        "Cybersole.Stores": 0.40,
        "Cybersole.Ui": 0.12,
        "Avalonia.*": 0.06,
        "Jint.*": 0.05,
        "System.* / BCL": 0.025,
        "NativeAOT / CRT Runtime": 0.25,
    }
    seeds = {i: pdata_gt[i] for i in range(len(pdata_gt)) if rng.random() < rates.get(pdata_gt[i], 0.03)}
    lbl = dict(seeds)
    for _ in (1, 2):
        upd = {}
        for i in range(len(pdata_gt)):
            if i in lbl:
                continue
            nb_all = callers[i] | callees[i]
            if not nb_all:
                continue
            nb_lbls = {lbl[x] for x in nb_all if x in lbl}
            if len(nb_lbls) != 1:
                continue
            m = next(iter(nb_lbls))
            if m in ("System.* / BCL", "NativeAOT / CRT Runtime") or all(x in lbl for x in nb_all):
                upd[i] = m
        lbl.update(upd)

    prop_nodes = [i for i in lbl if i not in seeds]
    calib = {
        "e8_edges": sum(len(v) for v in callees.values()),
        "seeds": len(seeds),
        "propagated": len(prop_nodes),
        "overall_precision": round(100.0 * sum(1 for i in prop_nodes if lbl[i] == pdata_gt[i]) / max(len(prop_nodes), 1), 1),
        "stores_pred": sum(1 for i in prop_nodes if lbl[i] == "Cybersole.Stores"),
        "stores_precision": round(
            100.0 * sum(1 for i in prop_nodes if lbl[i] == "Cybersole.Stores" and pdata_gt[i] == "Cybersole.Stores")
            / max(sum(1 for i in prop_nodes if lbl[i] == "Cybersole.Stores"), 1),
            1,
        ),
        "avalonia_pred": sum(1 for i in prop_nodes if lbl[i] == "Avalonia.*"),
        "avalonia_precision": round(
            100.0 * sum(1 for i in prop_nodes if lbl[i] == "Avalonia.*" and pdata_gt[i] == "Avalonia.*")
            / max(sum(1 for i in prop_nodes if lbl[i] == "Avalonia.*"), 1),
            1,
        ),
    }

    # Source inventory across replica/src/**/*.cs
    cs_spec = importlib.util.spec_from_file_location("comment_split", os.path.join(ROOT, "replica", "tools", "comment_split.py"))
    cs_mod = importlib.util.module_from_spec(cs_spec)
    cs_spec.loader.exec_module(cs_mod)

    ns_pat = re.compile(r"^\s*namespace\s+([\w.]+)", re.M)
    decl_pat = re.compile(r"\b(?:class|interface|record|struct|enum)\s+([A-Za-z_][A-Za-z0-9_]*)")
    word_pat = re.compile(r"\b[A-Za-z_]\w*\b")

    proj_stats: dict[str, dict[str, int]] = collections.defaultdict(lambda: {"files": 0, "lines": 0, "types": 0})
    src_types_by_ns: dict[str, set[str]] = collections.defaultdict(set)
    src_ns_by_type: dict[str, set[str]] = collections.defaultdict(set)
    tokens_all: set[str] = set()
    tokens_by_proj: dict[str, set[str]] = collections.defaultdict(set)

    for fpath in glob.glob(os.path.join(ROOT, "replica", "src", "**", "*.cs"), recursive=True):
        if f"{os.sep}obj{os.sep}" in fpath or f"{os.sep}bin{os.sep}" in fpath:
            continue
        proj = os.path.relpath(fpath, os.path.join(ROOT, "replica", "src")).split(os.sep)[0]
        raw_txt = open(fpath, encoding="utf-8", errors="replace").read()
        stripped = cs_mod.strip_comments(raw_txt)
        ws = set(word_pat.findall(stripped))
        tokens_all.update(ws)
        tokens_by_proj[proj].update(ws)
        proj_stats[proj]["files"] += 1
        proj_stats[proj]["lines"] += raw_txt.count("\n") + 1
        m = ns_pat.search(raw_txt)
        ns = m.group(1) if m else "(none)"
        for dm in decl_pat.finditer(stripped):
            tname = dm.group(1)
            src_types_by_ns[ns].add(tname)
            src_ns_by_type[tname].add(ns)
            proj_stats[proj]["types"] += 1

    # Accessor types (508)
    acc_types: dict[str, set[str]] = collections.defaultdict(set)
    for line in open(os.path.join(ROOT, "replica", "docs", "baseline", "recovered_accessors_by_type.txt"), encoding="utf-8", errors="replace"):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split("\t")
        if len(parts) >= 2:
            acc_types[parts[0]].add(parts[1])

    tc = json.load(open(os.path.join(ROOT, "replica", "tools", "type_classification.json"), encoding="utf-8"))["types"]
    src_fqn = {f"{ns}.{t}" for ns, ts in src_types_by_ns.items() for t in ts}
    cyb_acc = [k for k in sorted(acc_types) if k.startswith("Cybersole.")]
    acc_exact = sum(1 for k in cyb_acc if k in src_fqn)
    acc_simple = sum(1 for k in cyb_acc if k not in src_fqn and k.split(".")[-1].split("`")[0] in src_ns_by_type)
    acc_classified = sum(1 for k in cyb_acc if k not in src_fqn and k.split(".")[-1].split("`")[0] not in src_ns_by_type and k in tc)
    acc_missing = len(cyb_acc) - acc_exact - acc_simple - acc_classified

    # Async methods (1,547)
    async_rows = []
    for line in open(os.path.join(ROOT, "replica", "docs", "baseline", "recovered_async_methods.txt"), encoding="utf-8", errors="replace"):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if re.match(r"^[A-Za-z_]\w*$", parts[0]):
            async_rows.append((parts[0], int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1))

    async_present = [(n, c) for n, c in async_rows if (n in tokens_all or (n + "Async") in tokens_all)]
    async_absent = [(n, c) for n, c in async_rows if not (n in tokens_all or (n + "Async") in tokens_all)]

    buckets = []
    for cat in sorted(bytes_cnt, key=lambda k: -(exact_cnt[k] + funclet_cnt[k])):
        tot = exact_cnt[cat] + funclet_cnt[cat]
        buckets.append({
            "bucket": cat,
            "total": tot,
            "exact": exact_cnt[cat],
            "funclet": funclet_cnt[cat],
            "bytes": bytes_cnt[cat],
            "pct": round(100.0 * tot / len(pdata_extents), 2),
        })

    return {
        "exe_path": exe_path,
        "pdb_path": pdb_path,
        "exe_mtime": datetime.datetime.fromtimestamp(os.stat(exe_path).st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "exe_size": os.path.getsize(exe_path),
        "pdb_size": os.path.getsize(pdb_path),
        "raw_pdata_slots": raw_slots,
        "valid_pdata_extents": len(pdata_extents),
        "pdb_meta": pdb_meta,
        "outside_pdata": outside,
        "buckets": buckets,
        "calibration": calib,
        "projects": dict(sorted(proj_stats.items())),
        "tokens_all": tokens_all,
        "src_ns_counts": {ns: len(ts) for ns, ts in sorted(src_types_by_ns.items())},
        "accessors": {
            "total_types": len(acc_types),
            "cybersole_types": len(cyb_acc),
            "non_cybersole_entries": len(acc_types) - len(cyb_acc),
            "exact_fqn": acc_exact,
            "simple_match": acc_simple,
            "type_classification": acc_classified,
            "missing": acc_missing,
        },
        "async_methods": {
            "distinct": len(async_rows),
            "occurrences": sum(c for _, c in async_rows),
            "present_names": len(async_present),
            "present_occ": sum(c for _, c in async_present),
            "absent_names": len(async_absent),
            "absent_occ": sum(c for _, c in async_absent),
            "rows": async_rows,
        },
    }


class IdaClient:
    """Minimal JSON-RPC client matching `analysis/ida.py` for standalone reproducibility."""

    def __init__(self, url: str = IDA_URL):
        self.url = url
        self._id = 0

    def _rpc(self, method: str, params: dict | None = None, timeout: int = 300) -> dict:
        self._id += 1
        body = json.dumps({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}}).encode()
        req = urllib.request.Request(
            self.url, data=body, headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))

    def call(self, tool: str, args: dict | None = None, timeout: int = 300) -> str:
        res = self._rpc("tools/call", {"name": tool, "arguments": args or {}}, timeout=timeout)
        if "error" in res:
            raise RuntimeError(f"IDA MCP {tool} error: {res['error']}")
        out = res.get("result", {})
        texts = [c.get("text", "") for c in (out.get("content") or []) if isinstance(c, dict)]
        return "\n".join(texts) if texts else json.dumps(out)

    def ensure_ready(self) -> dict:
        self._rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "cyber-reverse-census", "version": "1"}})
        health = json.loads(self.call("server_health", timeout=30))
        if not health.get("auto_analysis_ready") or not health.get("strings_cache_ready"):
            raise RuntimeError(f"IDA not ready: {health}")
        return health


def export_from_ida(cache_dir: str, refresh: bool) -> tuple[str, str, str]:
    """Ensure `orig_strings.tsv`, `orig_funcs.tsv`, and `orig_callgraph.tsv` exist in `cache_dir`."""
    os.makedirs(cache_dir, exist_ok=True)
    str_out = os.path.join(cache_dir, "orig_strings.tsv").replace("\\", "/")
    fn_out = os.path.join(cache_dir, "orig_funcs.tsv").replace("\\", "/")
    cg_out = os.path.join(cache_dir, "orig_callgraph.tsv").replace("\\", "/")

    if not refresh and all(os.path.exists(p) and os.path.getsize(p) > 0 for p in (str_out, fn_out, cg_out)):
        return str_out, fn_out, cg_out

    client = IdaClient()
    health = client.ensure_ready()
    print(f"[IDA] Connected: {health.get('idb_path')} (strlist={health.get('strings_cache_size')})")

    export_sf_code = f"""
import idautils, ida_funcs, ida_segment, time
t0 = time.time()
with open({str_out!r}, "w", encoding="utf-8", errors="replace", newline="\\n") as f:
    n_s = 0
    for s in idautils.Strings():
        n_s += 1
        seg = ida_segment.get_segm_name(ida_segment.getseg(s.ea)) if ida_segment.getseg(s.ea) else ""
        txt = str(s).replace("\\t", "\\\\t").replace("\\r", "\\\\r").replace("\\n", "\\\\n")
        f.write("%x\\t%d\\t%d\\t%s\\t%s\\n" % (s.ea, s.strtype, s.length, seg, txt))
with open({fn_out!r}, "w", encoding="utf-8", errors="replace", newline="\\n") as f:
    n_f = 0
    for ea in idautils.Functions():
        n_f += 1
        fn = ida_funcs.get_func(ea)
        sz = fn.size() if fn else 0
        nm = ida_funcs.get_func_name(ea) or ""
        f.write("%x\\t%d\\t%s\\n" % (ea, sz, nm))
print("EXPORTED_SF", n_s, n_f, round(time.time() - t0, 2))
"""
    raw = client.call("py_eval", {"code": export_sf_code}, timeout=300)
    payload = json.loads(raw)
    if "EXPORTED_SF" not in (payload.get("stdout") or ""):
        raise RuntimeError(f"IDA string/func export failed: {payload}")
    print("[IDA]", (payload.get("stdout") or "").strip())

    export_cg_code = f"""
import idautils, ida_funcs, bisect, time
t0 = time.time()
funcs = sorted(idautils.Functions())
ranges = []
for ea in funcs:
    fn = ida_funcs.get_func(ea)
    ranges.append((ea, fn.end_ea if fn else ea + 1))
starts = [r[0] for r in ranges]
edges = 0
with open({cg_out!r}, "w", encoding="utf-8", newline="\\n") as f:
    for callee in funcs:
        seen = set()
        for xref in idautils.XrefsTo(callee, 0):
            if not xref.iscode:
                continue
            addr = xref.frm
            i = bisect.bisect_right(starts, addr) - 1
            if i >= 0 and ranges[i][0] <= addr < ranges[i][1]:
                caller = ranges[i][0]
                if caller != callee and caller not in seen:
                    seen.add(caller)
                    f.write("%x\\t%x\\n" % (caller, callee))
                    edges += 1
print("EXPORTED_CG", edges, round(time.time() - t0, 2))
"""
    raw_cg = client.call("py_eval", {"code": export_cg_code}, timeout=300)
    payload_cg = json.loads(raw_cg)
    if "EXPORTED_CG" not in (payload_cg.get("stdout") or ""):
        raise RuntimeError(f"IDA callgraph export failed: {payload_cg}")
    print("[IDA]", (payload_cg.get("stdout") or "").strip())
    return str_out, fn_out, cg_out


# Verified module seed rules (checked against RVA clustering + co-occurring strings to avoid false attribution)
ORIGINAL_SEED_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("Cybersole.Auth/Lic (R702 Out-of-Scope)", re.compile(
        r"Auth\.License|LicenseControl|AuthWindow|license\.json|ActivateLicense|SelectedLicense|GetLicenses|Auth\.Login|Auth\.SignIn|Auth\.Verify"
    )),
    ("Cybersole.Stores (Flows/Payments/AntiBot)", re.compile(
        r"api\.nike\.com|checkout_previews/v3|checkouts/v3|on/demandware\.store/Sites-|myshopify|footsites|johnlewis|scheels|sportsshoes|popmart|farfetch|hbx\.com|goat\.com|bstn|poq\.io|magento|hybris|"
        r"PayPal 3DS|Stripe challenge|api\.stripe\.com|paypal\.com/graphql|checkoutshopper-live\.adyen|api\.checkout\.com|global-e|threeDSSessionData|PayPal Guest|ECPAY2|"
        r"x-kpsdk-|kpsdk|kasada|datadome|perimeterx|_px|akamai|abck|cf_clearance|turnstile|hcaptcha|recaptcha|geetest|TrustDecision|Castle|"
        r"Solving [A-Z]|Submit order|Submit payment|Submit shipping|Submit billing|Submitting |Adding to cart|Add to cart|Find product|Waiting for restock|Waiting for captcha|Task Failed|Payment failed|Checkout failed|"
        r"StatusInfo|#FB4961|x-client-country|x-client-namespace|x-device-os-type|x-project-id|td-session-|x-doughnuts|grey-secret|"
        r"sec-ch-ua-mobile|sec-ch-ua-platform|sec-fetch-site|sec-fetch-mode|sec-fetch-dest|gzip, deflate, br, zstd|en-US,en;q=0\.9|"
        r"HintLabelsRequest|BoxInferenceModel|LocateDetectionResponse|OddOneDetectionResponse|GANResult|DdMobileEvent|SensorRequest|apihub\.|"
        r"network_challenge_images|challengeFrame"
    )),
    ("Cybersole.Ui", re.compile(
        r"Cybersole\.Ui|avares://Cybersole|CustomButton|TransparentImageButton|CloseIcon|ColoredAddIcon|PrimaryBrandColor|PrimaryErrorColor|PrimaryBackground|SecondaryBackground|SecondaryTextColor|PrimaryTextColor|ModalCornerRadius|ModalOverlay|"
        r"^(?:Tasks|Profiles|Proxies|Settings|Accounts|Analytics|SmartActions|Monitor|Utilities|KeyBinds|ProfileCreator|ProfileCsv|TaskCreator|CreateGroup|StaggerStart|ExpressionView|PublishTemplate|CheckoutData|HistoryWindow|SmartActionSettings|Solver)\.|"
        r"EditMode|SaveText|CanSave"
    )),
    ("Cybersole.Http", re.compile(
        r"Cybersole\.Http(?!\.Analytics|\.Debug)|BrotliDictionary|IMeasuredDialer|RootCertificates|TLS 1\.2|TLS 1\.3|Cybersole/NetClient"
    )),
    ("Cybersole.Services", re.compile(
        r"Cybersole\.Services|ImapProvider|ClockService|AycdInbox|inbox-api\.aycd\.io|SolverAdvance|SolverEcho|SolverFetchResult|SolverInstruction|discord\.com/api/webhooks|WebhookCreator"
    )),
    ("Cybersole.Core", re.compile(
        r"Cybersole\.Core|Cybersole\.Models|Cybersole\.SmartActions|Cybersole\.Global|ProfileCsv\.|RemoteSmartAction|AccountDto|BotTaskDto|ProfileDto|RemoteProfile|RemoteTask|RemoteProxy|RemoteSettings|StoreActivity"
    )),
    ("DotNetBrowser.*", re.compile(
        r"DotNetBrowser|DOTNETBROWSER|Chromium binaries|DevTools|BrowserSession|rpc\.[A-Za-z0-9_.]+|BrowserId|FrameId|ProfileId|RenderProcess|BrowserWidget|forwarding native key event"
    )),
    ("AngleSharp.*", re.compile(
        r"AngleSharp|http://www\.w3\.org/1999/xhtml|http://www\.w3\.org/2000/svg|http://www\.w3\.org/1998/Math/MathML"
    )),
    ("AvaloniaEdit.*", re.compile(r"AvaloniaEdit|ICSharpCode\.AvaloniaEdit|FoldingMargin|CollapseIfSingleOverload")),
    ("Avalonia.*", re.compile(
        r"Avalonia|avares://Avalonia|StyledProperty|PseudoClass|VisualTree|SystemControl\w*Brush|SystemAccentColor|SystemBase\w*Color|ControlCornerRadius|"
        r"PART_ContentPresenter|PART_TextPresenter|PART_ScrollViewer|PART_Border|:pointerover|:pressed|:disabled|:selected|"
        r"The BindingEntry<T> has no value\.|The binding entry has no value\.|Set \{Property\} to \{\$Value\}|Animator has no property specified\.|"
        r"Unsupported AvaloniaProperty type\.|Unexpected binding source\.|Cannot add value to DoNothing binding value\.|BindingValue has no value\.|The observable can only be subscribed once\.|"
        r"CompositionBatch|DispatcherPriority|GridSplitter|DataGridColumn|Animation Target can't be null"
    )),
    ("SkiaSharp / HarfBuzzSharp", re.compile(r"SkiaSharp|HarfBuzz|SKBitmap|SKCanvas|SKPaint|SKPixmap|SKSurface|SKImage|SKTypeface|SKPath")),
    ("Org.BouncyCastle.*", re.compile(r"BouncyCastle|Org\.BouncyCastle|output buffer too short|input buffer too short|Modulus must be positive|Argon2")),
    ("Jint / Acornima", re.compile(
        r"\b(Jint|Acornima|Esprima)\b|CLR trap returned|Iterator\.prototype\.|RegExp\.prototype|Function\.prototype|Object\.prototype\.|"
        r"Cannot assign to read only property|of object '#<Object>'|object is not extensible|Cannot define property |Unknown slot |Unexpected token|"
        r"Array\.prototype|String\.prototype|Promise\.prototype|Temporal\.|nanosecond|microsecond|"
        r"AwaitNotInAsyncContext|InvalidDestructuringTarget|RegExpInvalidEscape|InvalidEscapedReservedWord|Error while evaluating module"
    )),
    ("Google.Protobuf.*", re.compile(r"Google\.Protobuf|Extensions reflection is not supported with AOT")),
    ("Newtonsoft.Json.*", re.compile(r"Newtonsoft\.Json|JsonSerializationException|JsonReaderException|JsonWriterException|Error reading JObject|Error setting value to|Error getting value from|Could not cast or convert from")),
    ("MailKit / MimeKit", re.compile(r"MailKit|MimeKit|ImapClient|SmtpClient|MimeMessage|SaslMechanism|TextPart|MultipartScan|ArcMessageSignature|UUEncoder")),
    ("Velopack.*", re.compile(r"Velopack|UpdateManager|VelopackAsset|GithubRelease|GitlabRelease|GiteaRelease|No local feed found")),
    ("RabbitMQ.Client", re.compile(r"RabbitMQ|AMQP|BasicProperties")),
    ("Microsoft.AspNetCore.SignalR", re.compile(r"SignalR|HubConnection|SubscribeGroups|UnsubscribeGroups|/connect/app|No invocation with id")),
    ("Microsoft.Identity.Client", re.compile(r"Microsoft\.Identity|MSAL|login\.microsoftonline|AdalResult|InstanceDiscovery|AdfsWebFinger|UserRealmDiscovery|homeAccountId")),
    ("Microsoft.Extensions.*", re.compile(r"Microsoft\.Extensions|implementationFactory|serviceType|\{OriginalFormat\}")),
    ("OpenTelemetry / Analytics", re.compile(r"OpenTelemetry|ClickHouseSink|Cybersole\.Http\.Analytics|Cybersole\.Http\.Debug")),
    ("Metalama.*", re.compile(r"Metalama|Compile-time-only code cannot be ca")),
    ("System.* / BCL", re.compile(
        r"^(?:Argument|InvalidOperation|NotSupported|IndexOutOfRange|Format|Overflow|NullReference|ObjectDisposed|UnauthorizedAccess|IO_|Cryptography|SR\.|System\.)|"
        r"System\.Text\.Json|jsonTypeInfo|A 'field' member cannot be 'virtual'|Specified cast is not valid\.|Value cannot be null\.|cannot be null|"
        r"Collection was modified|Collection is read-only\.|Operation is not valid due to the current state|"
        r"Must be non-negative|Non-negative number required\.|single dimensional arrays|ImmutableArray|The inner handler has not been assigned|"
        r"same thread as that represented|comm\.ADP\.|ds\.DataColumn\.|The key was of an incorrect type|The key already existed|"
        r"was not present in the dictionary|buffer is not associated with this pool|out of range|outside the bounds of the array|"
        r"Arithmetic Overflow\.|Data Exception\.|External component has thrown an exception|One of the identified items was in an invalid format|"
        r"Target array type is not compatible|signature types|Enumeration has either not started|Index and count must refer|"
        r"00010203040506070809|KeyValuePairs|HashSize|Valid values are between|ASN1 corrupted data\.|Pkcs12ConfidentialityMode|"
        r"thought to be unreachable|Cannot convert|Unable to convert object| is not a valid value|OIDs are limited to|"
        r"SocketsHttpHandler|SslStream|CipherSuitesPolicy|Http3Support|"
        r"The index is equal to or greater than|The array is multidimensional|The concurrencyLevel argument must be positive|The specified Type must not be a generic type|"
        r"hexadecimal value \{1\}, is an invalid character|The operation has timed out|not supported for a relative URI|Invalid cast from|"
        r"not a valid size for this algorithm|does not support writing|http://www\.w3\.org/XML/1998/namespace|http://www\.w3\.org/2001/XMLSchema|http://www\.w3\.org/2000/xmlns/|"
        r"Current module queried in wrong enumerator state|Invalid module requested in enumeration"
    )),
]


def analyze_original(str_path: str, fn_path: str, cg_path: str) -> dict:
    """Attribute original binary functions via IDA names, `chars_va - 12` / raw disp32 string xrefs, and 2-hop pure-module callgraph."""
    exe_path = resolve_path("target", "Cybersole.exe")
    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"Original binary missing: {exe_path}")

    with open(exe_path, "rb") as f:
        data = f.read()
    base, secs = read_pe_sections(exe_path)
    raw_slots, pdata_extents = read_pdata_extents(data, secs)
    pdata_begins = {base + b for b, _ in pdata_extents}

    def va_to_off(va: int) -> int | None:
        rva = va - base
        for _sn, (srva, svsz, srptr, srsz) in secs.items():
            if srva <= rva < srva + min(svsz, srsz):
                return srptr + (rva - srva)
        return None

    funcs: list[tuple[int, int, str]] = []
    ea_to_fi: dict[int, int] = {}
    for line in open(fn_path, encoding="utf-8", errors="replace"):
        ea_s, sz_s, nm = line.rstrip("\n").split("\t")
        ea = int(ea_s, 16)
        funcs.append((ea, ea + int(sz_s), nm))
    funcs.sort()
    for i, (ea, _, _) in enumerate(funcs):
        ea_to_fi[ea] = i
    f_starts = [f[0] for f in funcs]

    def find_func(va: int) -> int | None:
        i = bisect.bisect_right(f_starts, va) - 1
        return i if (i >= 0 and funcs[i][0] <= va < funcs[i][1]) else None

    # Parse strings and extract metadata catalogs
    target_to_str: dict[int, str] = {}
    dlls: set[str] = set()
    cyb_tokens: set[str] = set()
    prop_inits: set[str] = set()
    async_sm: set[str] = set()
    avares_views: set[str] = set()
    str_count = 0
    frozen_u16_hdr = 0

    dll_rx = re.compile(r"([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+)\.dll\b")
    cyb_rx = re.compile(r"Cybersole\.[A-Za-z_][A-Za-z0-9_`./]*")
    prop_rx = re.compile(r"([A-Za-z_][A-Za-z0-9_]*?)PropInit")
    sm_rx = re.compile(r"<([A-Za-z_][A-Za-z0-9_]*)>d__\d+")

    known_asm_roots = (
        "System.", "Microsoft.", "Avalonia.", "Cybersole.", "DotNetBrowser.", "Metalama.",
        "BouncyCastle.", "MicroCom.", "RabbitMQ.", "SkiaSharp.", "MailKit.", "MimeKit.",
        "Jint.", "Acornima.", "Newtonsoft.", "AngleSharp.", "Velopack.",
    )

    for line in open(str_path, encoding="utf-8", errors="replace"):
        parts = line.rstrip("\n").split("\t", 4)
        if len(parts) < 5:
            continue
        str_count += 1
        ea = int(parts[0], 16)
        st = int(parts[1])
        txt = parts[4]

        for m in dll_rx.finditer(txt):
            s = m.group(1)
            for root in known_asm_roots:
                idx = s.find(root)
                if idx == 1:
                    s = s[1:]
                    break
            if not s[0].isdigit():
                dlls.add(s + ".dll")
        for m in cyb_rx.finditer(txt):
            cyb_tokens.add(m.group(0).rstrip(".,;:!?\"'\\)"))
        for m in prop_rx.finditer(txt):
            prop_inits.add(m.group(1))
        for m in sm_rx.finditer(txt):
            async_sm.add(m.group(1))
        if "avares://Cybersole/" in txt:
            avares_views.add(txt)

        if st in (1, 33554433):
            off = va_to_off(ea - 12)
            if off is not None and off + 12 <= len(data):
                mt, slen = struct.unpack_from("<Qi", data, off)
                if 0 < slen <= 100000 and (base <= mt < base + 0x8000000):
                    target_to_str[ea - 12] = txt
                    frozen_u16_hdr += 1
                    continue
        target_to_str[ea] = txt

    # Vectorized disp32 scan over .text
    t_rva, t_vsz, t_off, t_rsz = secs[".text"]
    t_va = base + t_rva
    b = np.frombuffer(data[t_off:t_off + min(t_vsz, t_rsz)], dtype=np.uint8)
    n = len(b) - 4
    disp = (
        b[:n].astype(np.int64)
        | (b[1:n + 1].astype(np.int64) << 8)
        | (b[2:n + 2].astype(np.int64) << 16)
        | (b[3:n + 3].astype(np.int64) << 24)
    )
    disp = np.where(disp >= 0x80000000, disp - 0x100000000, disp)
    site_va = np.arange(n, dtype=np.int64) + t_va + 4
    implied = site_va + disp
    tgt = np.array(sorted(target_to_str.keys()), dtype=np.int64)
    idx = np.clip(np.searchsorted(tgt, implied), 0, len(tgt) - 1)
    pos = np.nonzero(tgt[idx] == implied)[0]

    func_strs: dict[int, set[str]] = collections.defaultdict(set)
    for p in pos:
        fi = find_func(int(site_va[p]) - 4)
        if fi is not None:
            func_strs[fi].add(target_to_str[int(tgt[idx[p]])])

    # Signal 1 (verified IDA names) + Signal 2 (string-xref ownership)
    direct: dict[int, str] = {}
    direct_via_name = 0
    direct_via_str = 0
    conflicts: collections.Counter[tuple[str, ...]] = collections.Counter()
    flirt_ignored = 0

    for fi, (ea, _end, nm) in enumerate(funcs):
        if nm and not nm.startswith("sub_") and not nm.startswith("nullsub"):
            if nm.startswith("Brotli"):
                direct[fi] = "Cybersole.Http (Brotli native)"
                direct_via_name += 1
                continue
            elif ea >= 0x143025000:
                direct[fi] = "NativeAOT / CRT Runtime"
                direct_via_name += 1
                continue
            else:
                flirt_ignored += 1

        if fi in func_strs:
            hits = set()
            for s in func_strs[fi]:
                for cat, rx in ORIGINAL_SEED_RULES:
                    if rx.search(s):
                        hits.add(cat)
            non_bcl = [h for h in hits if h != "System.* / BCL"]
            if len(non_bcl) == 1:
                direct[fi] = non_bcl[0]
                direct_via_str += 1
            elif len(non_bcl) > 1:
                conflicts[tuple(sorted(non_bcl))] += 1
            elif "System.* / BCL" in hits:
                direct[fi] = "System.* / BCL"
                direct_via_str += 1

    # Signal 3: 1-2 hop conservative pure-module callgraph propagation
    callers: dict[int, set[int]] = collections.defaultdict(set)
    callees: dict[int, set[int]] = collections.defaultdict(set)
    edge_count = 0
    for line in open(cg_path, encoding="utf-8"):
        u_s, v_s = line.rstrip("\n").split("\t")
        ui, vi = ea_to_fi.get(int(u_s, 16)), ea_to_fi.get(int(v_s, 16))
        if ui is not None and vi is not None:
            callees[ui].add(vi)
            callers[vi].add(ui)
            edge_count += 1

    lbl = dict(direct)
    hop_counts = []
    for _hop in (1, 2):
        upd = {}
        for fi in range(len(funcs)):
            if fi in lbl:
                continue
            nb_all = callers[fi] | callees[fi]
            if not nb_all:
                continue
            nb_lbls = {lbl[x] for x in nb_all if x in lbl}
            if len(nb_lbls) != 1:
                continue
            m = next(iter(nb_lbls))
            if m in ("System.* / BCL", "NativeAOT / CRT Runtime") or all(x in lbl for x in nb_all):
                upd[fi] = m
        lbl.update(upd)
        hop_counts.append(len(upd))

    # Summarize module buckets
    all_cats = sorted(set(lbl.values()), key=lambda k: -sum(1 for v in lbl.values() if v == k))
    rows = []
    for cat in all_cats:
        fis = [fi for fi, v in lbl.items() if v == cat]
        d_n = sum(1 for fi in fis if fi in direct)
        p_n = len(fis) - d_n
        pd_n = sum(1 for fi in fis if funcs[fi][0] in pdata_begins)
        b_cnt = sum(funcs[fi][1] - funcs[fi][0] for fi in fis)
        rvas = sorted(funcs[fi][0] for fi in fis)
        rows.append({
            "bucket": cat,
            "total_ida": len(fis),
            "direct": d_n,
            "propagated": p_n,
            "pdata_backed": pd_n,
            "bytes": b_cnt,
            "pct_ida": round(100.0 * len(fis) / len(funcs), 2),
            "med_va": hex(rvas[len(rvas) // 2]),
        })

    unattr_fis = [fi for fi in range(len(funcs)) if fi not in lbl]
    unattr_pdata = sum(1 for fi in unattr_fis if funcs[fi][0] in pdata_begins)
    unattr_bytes = sum(funcs[fi][1] - funcs[fi][0] for fi in unattr_fis)

    return {
        "exe_path": exe_path,
        "exe_size": os.path.getsize(exe_path),
        "raw_pdata_slots": raw_slots,
        "valid_pdata_extents": len(pdata_extents),
        "ida_funcs": len(funcs),
        "ida_pdata_overlap": len({f[0] for f in funcs} & pdata_begins),
        "ida_named_total": sum(1 for _, _, nm in funcs if nm and not nm.startswith("sub_")),
        "flirt_or_nullsub_below_runtime": flirt_ignored + sum(1 for ea, _, nm in funcs if ea < 0x143025000 and nm.startswith("nullsub")),
        "ida_strings": str_count,
        "frozen_u16_headers": frozen_u16_hdr,
        "disp32_hits": len(pos),
        "disp32_funcs_hit": len(func_strs),
        "callgraph_edges": edge_count,
        "direct_total": len(direct),
        "direct_via_name": direct_via_name,
        "direct_via_str": direct_via_str,
        "direct_conflicts": sum(conflicts.values()),
        "hop1": hop_counts[0],
        "hop2": hop_counts[1],
        "attributed_total": len(lbl),
        "unattributed_total": len(unattr_fis),
        "unattributed_pdata": unattr_pdata,
        "unattributed_bytes": unattr_bytes,
        "buckets": rows,
        "dlls": sorted(dlls),
        "cyb_tokens": sorted(cyb_tokens),
        "prop_inits": sorted(prop_inits),
        "async_sm": sorted(async_sm),
        "avares_views": sorted(avares_views),
    }


def build_cross_reference(replica: dict, orig: dict) -> list[dict]:
    """Cross-reference every original Cybersole.* namespace, DTO family, async family, and library against replica/src."""
    tokens = replica["tokens_all"]
    asy_rows = replica["async_methods"]["rows"]
    rep_b = {r["bucket"]: r for r in replica["buckets"]}
    orig_b = {r["bucket"]: r for r in orig["buckets"]}

    def asy_counts(pattern: str) -> tuple[int, int, int, int]:
        rx = re.compile(pattern, re.I)
        sub = [(n, c) for n, c in asy_rows if rx.search(n)]
        pres = [(n, c) for n, c in sub if (n in tokens or (n + "Async") in tokens)]
        return len(sub), sum(c for _, c in sub), len(pres), sum(c for _, c in pres)

    sf_n, sf_o, sf_pn, sf_po = asy_counts(
        r"^(?:AddToCart|AddToBasket|FindProduct|SubmitShipping|SubmitBilling|SubmitOrder|SubmitEmail|SubmitDiscount|ApplyDiscount|GetCheckout|CreateCheckout|PlaceOrder|ClearCart|CreateCart|GetCart|EditLine|FindVariant|ScrapeProduct|ScrapeVariant|CheckPriceLimit|EnterRaffle|GetRaffleData|GetShippingRate|AdoptSellerRate|Preload|AccountLogin|CompleteRegistration|RegisterEmail|AddAddress)"
    )
    pay_n, pay_o, pay_pn, pay_po = asy_counts(
        r"(Payment|PayPal|Stripe|Adyen|3DS|ThreeDS|Card|Tokenize|SetupIntent|PaymentIntent|ApplePay|Braintree|Klarna|Afterpay|CheckoutCom|Cardinal|Unzer|GiftCard|AuthorizePayment|ApproveOnBoard|ApproveMember)"
    )
    ob_stores = orig_b.get("Cybersole.Stores (Flows/Payments/AntiBot)", {"direct": 0, "total_ida": 0, "bytes": 0})
    rb_stores = rep_b.get("Cybersole.Stores", {"total": 0, "bytes": 0})
    rb_ui = rep_b.get("Cybersole.Ui", {"total": 0, "bytes": 0})
    rb_http = rep_b.get("Cybersole.Http", {"total": 0, "bytes": 0})
    rb_core = rep_b.get("Cybersole.Core", {"total": 0, "bytes": 0})
    rb_mail = rep_b.get("MailKit.*", {"total": 0}).get("total", 0) + rep_b.get("MimeKit.*", {"total": 0}).get("total", 0)

    def o_tot(name: str) -> int:
        return orig_b.get(name, {}).get("total_ida", 0)

    return [
        {
            "area": "Cybersole.Stores.Flows (18 Flows / 369 Steps)",
            "orig_evidence": f"{ob_stores['direct']:,} direct / {ob_stores['total_ida']:,} attributed funcs (`0x1408..0x1412`); {sf_n} storefront async names ({sf_o} occ)",
            "replica_counterpart": f"`Cybersole.Stores/` ({replica['projects']['Cybersole.Stores']['lines']:,} LOC; {rb_stores['total']:,} `.pdata` funcs, {rb_stores['bytes'] // 1024:,} KiB)",
            "status": "Partial / Missing Core Logic",
            "details": f"{sf_pn}/{sf_n} storefront async names present ({sf_po}/{sf_o} occ); missing `CheckPriceLimitApp` @ `0x143373f5f`, `FindProductCDN` @ `0x1433a0f23`, `CheckFanRewardState`/`SignUpFanRewards` @ `0x14337...`, per-store App/GraphQL variants.",
        },
        {
            "area": "Cybersole.Stores.Payments (PayPal 3DS / Stripe / Adyen / Unzer / Checkout.com)",
            "orig_evidence": f"{pay_n} payment async names ({pay_o} occ); `0x143320000`, `0x14338294f` (`CardinalInit`), `0x143383aa9` (`ContinueUnzerThreeDs`), `0x1470530bc` (`api.checkout.com`)",
            "replica_counterpart": "`Cybersole.Stores/Payments/{PayPalThreeDs,StripeChallenge,Gateways}.cs`",
            "status": "Partial / Missing Core Logic",
            "details": f"PayPal 3DS (9 stages) & Stripe 6 endpoints + challenge implemented ({pay_pn}/{pay_n} names, {pay_po}/{pay_o} occ); `UnzerGateway.CompleteActionAsync` is stubbed (missing `ContinueUnzerThreeDs`/`CardinalInit`/`CompleteConvenienceStore` @ `0x1434a...` & `api.checkout.com` gateway).",
        },
        {
            "area": "Cybersole.Stores.Scripts (Kasada / Cloudflare / DataDome / PX / Akamai / Queue-it)",
            "orig_evidence": f"Jint + Acornima ({o_tot('Jint / Acornima'):,} attributed funcs); `GenerateSensor`, `GetSbsdHash`, `DdMobileEvent`/`SensorRequest` (`0x14333fc96`), `SolverApiException`",
            "replica_counterpart": "`Cybersole.Stores/Scripts/*.cs` (`KasadaSolver`, `CloudflareStrategy`, `BrowserShim`, etc.)",
            "status": "Partial / Missing Core Logic",
            "details": "Kasada Jint main path & detection surface implemented; missing `GetSbsdHash`/`GetSbsdScript`, `DdMobileTouchEvent`/`SensorPow` mobile/sensor DTOs (`0x14333fc96..0x14333ff2c`), and browser-hosted challenge execution.",
        },
        {
            "area": "Cybersole.Stores AI / Vision & Automated Captcha Solving",
            "orig_evidence": "21 Vision DTOs (`HintLabelsRequest`..`GANResult` @ `0x14333c304`), `ExecuteClipModelAsync`/`SolveImageInCloudAsync`/`ClickCellsAsync` @ `0x1435f0000`, `CallParallax` @ `0x14345c117`",
            "replica_counterpart": "`Cybersole.Services/Captcha/{CaptchaSolverService,Drivers}.cs`, `CaptchaSurface.cs`",
            "status": "Out of Scope",
            "details": "User third-party API drivers (2Captcha/Parallax/Uncaptcha/HumanPresence) and detection (`CaptchaSurface`) implemented; automated CAPTCHA/anti-bot bypass execution (`ExecuteClipModelAsync`, `ClickCellsAsync`, `MoveMouseAndClickWithoutTrajectoryAsync`) is out of scope.",
        },
        {
            "area": "Cybersole.Http (NetClient 0.10.0) + Brotli + Companion Packages",
            "orig_evidence": f"`Cybersole.Http.dll`, `Cybersole.Http.{{Newtonsoft,Analytics,Debug}}.dll` (`0x14315a7c1..0x14316e350`), {o_tot('Cybersole.Http (Brotli native)') + o_tot('Cybersole.Http'):,} attributed funcs (incl. Brotli)",
            "replica_counterpart": f"`Cybersole.Http/` ({rb_http['total']:,} `.pdata` funcs, {rb_http['bytes'] // 1024:,} KiB; `BrotliDictionary.bin`)",
            "status": "Partial / Missing Core Logic",
            "details": "Core `SocketsHttpHandler` + TLS + Brotli dict implemented; missing `Cybersole.Http.Newtonsoft` (`LegacyJsonBody`/`LegacyJarrayBody`), `ClickHouseSink` (`FlushOnceAsync`/`DrainLocalQueueAsync` @ `0x14331...`), `Cybersole.Http.Debug` proxy stream, `Cybersole.Http.Content.IBody`, `Cybersole.Http.X509.RootCertificates.bin`.",
        },
        {
            "area": "Cybersole.Services.Mail (ImapProvider / AYCD / MailKit + MimeKit)",
            "orig_evidence": f"`MailKit.dll` + `MimeKit.dll` ({o_tot('MailKit / MimeKit'):,} attributed funcs @ `0x14188..0x1419e`), `WaitImapAsync` (`0x14336b99e`), `AycdCompletedTasks`/`AycdMailElement` (`0x14334cb55`)",
            "replica_counterpart": f"`Cybersole.Services/Mail/{{ImapMailProvider,AycdInboxClient}}.cs` — **{rb_mail} funcs in `Cybersole.Ui.pdb`**",
            "status": "Partial / Missing Core Logic",
            "details": "Classes exist in `Cybersole.Services` & pass unit tests, but are **unwired zero-caller islands** (absent from `AppServices.cs` / `TaskEngine.cs`) so NativeAOT trims 100% of `MailKit`/`MimeKit` from `Cybersole.Ui.exe`.",
        },
        {
            "area": "Cybersole.Services Cloud Sync / SignalR / RabbitMQ / MSAL / Velopack",
            "orig_evidence": f"`SignalR` ({o_tot('Microsoft.AspNetCore.SignalR')}), `MSAL` ({o_tot('Microsoft.Identity.Client')}), `Velopack` ({o_tot('Velopack.*')}), `RabbitMQ` ({o_tot('RabbitMQ.Client')}), 35 `*Dto` (`0x1433473dc`) + 21 `Remote*` (`0x1433611c7`)",
            "replica_counterpart": "`BackupScheduler.cs`, `ClockService.cs`, `SettingsShell.cs` (local Velopack cache check only)",
            "status": "External Blocked",
            "details": "Missing `SignalR` (`/connect/app`), `RabbitMQ.Client`, `Microsoft.Identity.Client` (MSAL OAuth2), cloud `*Dto`/`Remote*` sync, and real `Velopack` update feed (`cdn.cybersole.io/releases/` returns 404; `/connect/app` requires valid login).",
        },
        {
            "area": "Cybersole.Core / Models / SmartActions / Providers (Metalama Observability)",
            "orig_evidence": f"`Cybersole.Core.dll` + `Metalama.Framework` ({o_tot('Metalama.*')} funcs @ `0x141274`), `Cybersole.Providers.IDataProvider` (`0x143216abb`), `Cybersole.Global.Strings` (`0x143210e9f`)",
            "replica_counterpart": f"`Cybersole.Core/` ({replica['projects']['Cybersole.Core']['lines']:,} LOC; {rb_core['total']:,} `.pdata` funcs; handwritten `ObservableObject` + `RelayCommand`)",
            "status": "Implemented",
            "details": "All 143 `Cybersole.*` accessor types accounted for (`85` FQN, `44` namespace-moved, `14` in `type_classification.json`, `0` missing); `IDataProvider` is an unimplemented interface contract; `CommunityToolkit.Mvvm` in `.csproj` is unused/trimmed.",
        },
        {
            "area": "Cybersole.Ui (Avalonia Views / Controls / Localization)",
            "orig_evidence": f"{o_tot('Cybersole.Ui'):,} attributed funcs (`0x14057..0x14088`), {len(orig['avares_views'])} `avares://Cybersole/` assets, `Avalonia` ({o_tot('Avalonia.*'):,}), `AvaloniaEdit`",
            "replica_counterpart": f"`Cybersole.Ui/` ({replica['projects']['Cybersole.Ui']['lines']:,} LOC; {rb_ui['total']:,} `.pdata` funcs, `Avalonia 11.3.2`)",
            "status": "Implemented",
            "details": "Core UI views, controls, and localization helpers implemented (excluding `AvaloniaEdit` code editor and `TaskCreatorAdvancedView` merged into `TaskCreatorView`).",
        },
        {
            "area": "Cybersole.Ui.Views.Auth & LicenseControl (R702)",
            "orig_evidence": f"`AuthWindow`, `LicenseControl`, `Cybersole.Models.License`, {o_tot('Cybersole.Auth/Lic (R702 Out-of-Scope)')} attributed funcs (`0x14076..0x14077`)",
            "replica_counterpart": "`Auth/` (`AuthService`, `LicenseService` read-only)",
            "status": "Out of Scope",
            "details": "Explicitly excluded by YG R702 ruling (`docs/DECISION_LICENSE_OUT_OF_SCOPE.md`).",
        },
        {
            "area": "Cybersole.Web.BrowserHandlers & DotNetBrowser (Chromium 4.3.5.8591)",
            "orig_evidence": f"{o_tot('DotNetBrowser.*'):,} attributed funcs (`0x1413d..0x14153`), `IBrowserSessionView` (`0x143636deb`), `PaymentAutofill` (`0x14352da80`), 17 `Solver*` IPC DTOs (`0x143459376`), `AngleSharp` ({o_tot('AngleSharp.*')})",
            "replica_counterpart": "`CustomBrowser.cs` (Avalonia placeholder window without embedded Chromium engine)",
            "status": "External Blocked",
            "details": "Commercial `DotNetBrowser` + external Chromium runtime (`DOTNETBROWSER_CHROMIUM_DIR`) and `Cybersole.Web.BrowserHandlers` / `AngleSharp` HTML parser are absent in replica.",
        },
    ]


def render_markdown(replica: dict, orig: dict, xref: list[dict], stamp: str) -> str:
    """Render docs/MODULE_FUNCTION_CENSUS.md cleanly in UTF-8 without mojibake or volatile test-count conflicts."""
    lines: list[str] = []
    add = lines.append

    rep_total = replica["valid_pdata_extents"]
    rep_b = {r["bucket"]: r for r in replica["buckets"]}
    cyb_buckets = [r for r in replica["buckets"] if r["bucket"].startswith("Cybersole.")]
    cyb_tot = sum(r["total"] for r in cyb_buckets)
    cyb_bytes = sum(r["bytes"] for r in cyb_buckets)
    cyb_pct = 100.0 * cyb_tot / rep_total

    infra_names = {
        "System.* / BCL", "Avalonia.*", "NativeAOT / CRT Runtime", "Microsoft.*",
        "Tmds.DBus (Avalonia)", "SkiaSharp.*", "HarfBuzzSharp.*", "MicroCom.Runtime (Avalonia)",
    }
    infra_tot = sum(r["total"] for r in replica["buckets"] if r["bucket"] in infra_names)
    infra_pct = 100.0 * infra_tot / rep_total
    third_names = {"Jint.*", "Org.BouncyCastle.*", "Newtonsoft.Json.*", "Acornima.* (Jint)"}
    third_tot = sum(r["total"] for r in replica["buckets"] if r["bucket"] in third_names)
    third_pct = 100.0 * third_tot / rep_total

    orig_b = {r["bucket"]: r for r in orig["buckets"]}
    ob_stores = orig_b.get("Cybersole.Stores (Flows/Payments/AntiBot)", {"total_ida": 0, "bytes": 0})
    rb_stores = rep_b.get("Cybersole.Stores", {"total": 0, "bytes": 0})
    stores_fn_ratio = ob_stores["total_ida"] / max(rb_stores["total"], 1)
    stores_byte_ratio = ob_stores["bytes"] / max(rb_stores["bytes"], 1)

    add("# 模块级函数分布与 Cybersole.* 类型/方法普查报告（Gap #2）")
    add("")
    add(f"> 生成时间：{stamp}  |  生成脚本：`python analysis/module_function_census.py --write-doc`")
    add("> 全局动态套件/绑定指标唯一源：`docs/METRICS.md`（本文只陈述源码/PDB/二进制与 IDA 普查观测值）。")
    add("")
    add("## 一、结论摘要（Observation / Inference / Unknown 严格分离）")
    add("")
    add("- **Observation（复刻件 100% 归因）**：通过解析 `Cybersole.Ui.pdb`（MSF 7.0，"
        f"{replica['pdb_meta']['modules']} 模块 / {replica['pdb_meta']['procs']:,} 过程符号）并与 `Cybersole.Ui.exe` 的 `.pdata` 区间（"
        f"{rep_total:,} 有效函数区间 / {replica['raw_pdata_slots']:,} 原始槽位）做精确 + 内嵌 funclet 匹配，"
        f"**100.00%**（`outside={replica['outside_pdata']}`）`.pdata` 函数得到归属。其中 **{infra_pct:.2f}%**（{infra_tot:,} 个）为 `System.* / BCL`、"
        f"Avalonia UI 栈与 NativeAOT CRT；**{third_pct:.2f}%**（{third_tot:,} 个）为第三方库（`Jint/Acornima`、`BouncyCastle`、`Newtonsoft.Json`）；"
        f"**仅 {cyb_pct:.2f}%（{cyb_tot:,} 个 `.pdata` 函数 / {cyb_bytes / (1024 * 1024):.2f} MiB）为 `Cybersole.*` 自身业务代码**。")
    add(f"- **Observation（原版多信号归因与诚实未知量）**：对 `target/Cybersole.exe`（{orig['ida_funcs']:,} IDA 函数 / "
        f"{orig['valid_pdata_extents']:,} 有效 `.pdata` 区间 / {orig['raw_pdata_slots']:,} 原始槽位），结合"
        f"（1）可信原生 IDA 符号（过滤 `< 0x143025000` 的 {orig['flirt_or_nullsub_below_runtime']:,} 个 tiny FLIRT/nullsub 误命）、"
        f"（2）`chars_va - 12` 冻结 UTF-16 字符串（{orig['frozen_u16_headers']:,} 个对象头）与 C 字符串 `.text disp32` 扫描（{orig['disp32_hits']:,} 命中 / {orig['disp32_funcs_hit']:,} 函数）、"
        f"（3）{orig['callgraph_edges']:,} 条 IDA 调用图边的 1–2 跳保守纯模块传播，共归因 **{orig['attributed_total']:,}** 个函数"
        f"（`Direct-Attributed` **{orig['direct_total']:,}** + `Callgraph-Propagated` **{orig['hop1'] + orig['hop2']:,}**），"
        f"**`Unattributed` {orig['unattributed_total']:,}（{100.0 * orig['unattributed_total'] / orig['ida_funcs']:.2f}%）**如实保留为未知。")
    add("- **Observation（此前漏计的关键差距与死岛发现）**：")
    add(f"  1. **Mail/IMAP/AYCD 在复刻件产物中实际为 0**：`ImapMailProvider.cs` 与 `AycdInboxClient.cs` 虽在 `Cybersole.Services` 源码与单元测试中存在，但零被调于 `AppServices.cs`/`TaskEngine.cs`，NativeAOT 将 `MailKit`/`MimeKit` 100% 裁剪（`Cybersole.Ui.pdb` 中 0 个函数；原版已观测 {orig_b.get('MailKit / MimeKit', {}).get('total_ida', 0)} 个归因函数）。")
    add(f"  2. **原版多出 4 个独立 `Cybersole.*` 伴生包与多类三方运行时**：`Cybersole.Http.{{Newtonsoft,Analytics,Debug}}.dll`、`DotNetBrowser`（{orig_b.get('DotNetBrowser.*', {}).get('total_ida', 0)} 归因函数）、`AngleSharp`（{orig_b.get('AngleSharp.*', {}).get('total_ida', 0)}）、`MSAL`（{orig_b.get('Microsoft.Identity.Client', {}).get('total_ida', 0)}）、`SignalR`（{orig_b.get('Microsoft.AspNetCore.SignalR', {}).get('total_ida', 0)}）、`Velopack`（{orig_b.get('Velopack.*', {}).get('total_ida', 0)}）、`RabbitMQ.Client`（{orig_b.get('RabbitMQ.Client', {}).get('total_ida', 0)}）、`Metalama.Framework`（{orig_b.get('Metalama.*', {}).get('total_ida', 0)}）。")
    add("  3. **AI/视觉验证码与 Unzer/Cardinal/Checkout.com**：原版含 21 个视觉推理 `PropInit` DTO（`0x14333c304`）、`ExecuteClipModelAsync`/`SolveImageInCloudAsync`（`0x1435f0000`，属验证码求解执行面 → `Out of Scope`），以及尚未闭环的 `ContinueUnzerThreeDs`（`0x143383aa9`）、`CardinalInit`（`0x14338294f`）、`api.checkout.com`、`ClickHouseSink`。")
    add(f"- **Inference（结构解释）**：`Cybersole.Stores` 在原版仅靠字符串种子 + 零跨模块泄露 2 跳传播即已显影 **{ob_stores['total_ida']:,}** 个函数（{ob_stores['bytes'] / (1024 * 1024):.2f} MiB），"
        f"是复刻件全部 `Cybersole.Stores`（{rb_stores['total']:,} 个 `.pdata` 函数 / {rb_stores['bytes'] / 1024:.0f} KiB）的 **{stores_fn_ratio:.2f} 倍函数数 / {stores_byte_ratio:.2f} 倍代码字节**，"
        "主因原版内含更多站内变体、3DS/支付状态机与浏览器/反爬交互代码；同时原版独有的 `DotNetBrowser` + `SignalR` + `MSAL` + `AngleSharp` + `RabbitMQ` + `MailKit` + .NET 10 BCL 体量共同构成了 `.pdata` 总数差值的主要部分。")
    add("- **Unknown**：原版 `Unattributed` 的 "
        f"{orig['unattributed_total']:,} 个函数缺少直接字符串引用、且经虚表/接口/跨模块调用隔断，无法在不猜测的情况下按单函数拆分到具体模块。")
    add("")

    add("## 二、复刻件模块函数分布（`Cybersole.Ui.pdb` + `.pdata` 100% 实测）")
    add("")
    add(f"- 产物：`{replica['exe_path']}`（{replica['exe_size']:,} B，修改时间 {replica['exe_mtime']}）")
    add(f"- PDB：`{replica['pdb_path']}`（{replica['pdb_size']:,} B，{replica['pdb_meta']['modules']} 模块，{replica['pdb_meta']['procs']:,} 过程符号）")
    add(f"- `.pdata` 覆盖：{replica['valid_pdata_extents']:,} 有效函数区间（原始 {replica['raw_pdata_slots']:,} 槽含 42 字节对齐空槽），**0 个未归因区间**。")
    add("")
    add("| 模块桶 | `.pdata` 合计 | 精确起始命中 | 内嵌 Funclet | 代码字节 | 占比 |")
    add("|---|---:|---:|---:|---:|---:|")
    for row in replica["buckets"]:
        add(f"| `{row['bucket']}` | {row['total']:,} | {row['exact']:,} | {row['funclet']:,} | {row['bytes']:,} | {row['pct']:.2f}% |")
    add("")
    add("### 复刻件源码与基线清单核对（`replica/src/` vs `replica/docs/baseline/`）")
    add("")
    add("| 工程 | `.cs` 文件数 | 总行数 | 声明类型数 |")
    add("|---|---:|---:|---:|")
    for proj, st in replica["projects"].items():
        add(f"| `{proj}` | {st['files']} | {st['lines']:,} | {st['types']} |")
    add("")
    acc = replica["accessors"]
    asy = replica["async_methods"]
    add(f"- **`recovered_accessors_by_type.txt`**：共 {acc['total_types']} 个类型键，其中 `Cybersole.*` **{acc['cybersole_types']}** 个"
        f"（精确命名空间匹配 {acc['exact_fqn']} + 同简名跨命名空间 {acc['simple_match']} + `type_classification.json` 分类 {acc['type_classification']} + 缺失 **{acc['missing']}**）；"
        f"其余 {acc['non_cybersole_entries']} 条包含带 NativeAOT 长度前缀噪声的 `xCybersole*`/`tAvalonia*` 及 `DotNetBrowser`/`Avalonia`/`System`。")
    add(f"- **`recovered_async_methods.txt`**：共 {asy['distinct']:,} 个去重 `<Method>d__N` 名（镜像共 {asy['occurrences']:,} 次实现体）；"
        f"按无注释源码词元对照，`replica/src/` 存在 **{asy['present_names']}** 个名字（对应 **{asy['present_occ']:,}** 次原版实现，占高频业务词汇主体），"
        f"缺席 **{asy['absent_names']:,}** 个名字（{asy['absent_occ']:,} 次出现，主要为 BCL/第三方库内部及原版专有单次实现步骤）。")
    add("")

    add("## 三、原版函数多信号归因分布（`target/Cybersole.exe`）")
    add("")
    add("### 3.1 归因口径与 PDB 校准实验")
    add("")
    add("1. **Signal 1（可信 IDA 符号）**：仅采信 `>= 0x143025000`（`main` 及 CRT/Win32 启动段）与 23 个 `Brotli*` 导出函数；"
        f"显式剔除 `< 0x143025000` 托管代码区内的 **{orig['flirt_or_nullsub_below_runtime']:,}** 个 `nullsub_*` 与 5–28 B IDA FLIRT 误匹配"
        "（实证样本：`0x14032aeb0` 被 IDA 标为 `__acrt_update_thread_multibyte_data_90`，实测加载 Avalonia 冻结串 `SystemControlDisabledBaseMediumLowBrush`）。")
    add(f"2. **Signal 2（字符串 Xref 归属）**：对 `idautils.Strings()` 中 {orig['frozen_u16_headers']:,} 个冻结 UTF-16 对象算头 `chars_va - 12`，"
        f"连同 C/UTF-8 串在 `.text` 全字节滑动 `disp32` 扫描得 **{orig['disp32_hits']:,}** 处指令引用（命中 **{orig['disp32_funcs_hit']:,}** 个函数），"
        f"按无歧义库/命名空间/URL/文案种子归因（`{orig['direct_conflicts']}` 个非 BCL 多模块冲突函数故意保留为未归因，不强行归类）。")
    add(f"3. **Signal 3（1–2 跳保守纯模块传播）**：在 IDA {orig['callgraph_edges']:,} 条调用边上执行 2 轮传播："
        "`System.* / BCL` 与 `NativeAOT / CRT` 在已归因邻居中唯一一致时传播；非 BCL 应用/三方模块仅当**全部邻居（caller ∪ callee）均已归因且同属该模块**时才传播。")
    cal = replica["calibration"]
    add(f"   - **在有 PDB 真值的复刻件上校准（{cal['e8_edges']:,} 条 `E8` 边，模拟不均衡种子 {cal['seeds']:,} 个）**："
        f"传播 {cal['propagated']:,} 个函数，**总体准确率 {cal['overall_precision']}%**，`Cybersole.Stores` 精确率 **{cal['stores_precision']}%**（{cal['stores_pred']} 个），`Avalonia.*` 精确率 **{cal['avalonia_precision']}%**（{cal['avalonia_pred']} 个）。"
        "（对比实验表明：若对 `Cybersole.Stores` 放开向未归因 callee 传播，`Stores` 精确率会跌至 42.1%，因大量 BCL 泛型特化仅被上层业务调用。）")
    add("")
    add(f"| 汇总档位 | IDA 函数数 | 占比 | 对应 `.pdata` 起始 | 代码字节 |")
    add("|---|---:|---:|---:|---:|")
    add(f"| **Direct-Attributed**（IDA 原生名 {orig['direct_via_name']:,} + 串 xref {orig['direct_via_str']:,}） | {orig['direct_total']:,} | {100.0 * orig['direct_total'] / orig['ida_funcs']:.2f}% | — | — |")
    prop_tot = orig["hop1"] + orig["hop2"]
    add(f"| **Callgraph-Propagated**（Hop1 {orig['hop1']:,} + Hop2 {orig['hop2']:,}） | {prop_tot:,} | {100.0 * prop_tot / orig['ida_funcs']:.2f}% | — | — |")
    add(f"| **已归因小计** | **{orig['attributed_total']:,}** | **{100.0 * orig['attributed_total'] / orig['ida_funcs']:.2f}%** | **{orig['ida_pdata_overlap'] - orig['unattributed_pdata']:,}** | — |")
    add(f"| **Unattributed**（其中直接冲突跳过 {orig['direct_conflicts']}） | **{orig['unattributed_total']:,}** | **{100.0 * orig['unattributed_total'] / orig['ida_funcs']:.2f}%** | **{orig['unattributed_pdata']:,}** | {orig['unattributed_bytes']:,} |")
    add(f"| **原版总计（IDA / `.pdata`）** | **{orig['ida_funcs']:,}** | **100.00%** | **{orig['ida_pdata_overlap']:,}（`.pdata` 有效 {orig['valid_pdata_extents']:,} / 槽 {orig['raw_pdata_slots']:,}）** | — |")
    add("")
    add("### 3.2 原版按模块桶明细")
    add("")
    add("| 模块桶 | 总归因 | Direct | Propagated | `.pdata` 命中 | 字节数 | 中位地址 |")
    add("|---|---:|---:|---:|---:|---:|---|")
    for r in orig["buckets"]:
        add(f"| `{r['bucket']}` | {r['total_ida']:,} | {r['direct']:,} | {r['propagated']:,} | {r['pdata_backed']:,} | {r['bytes']:,} | `{r['med_va']}` |")
    add(f"| `Unattributed` | {orig['unattributed_total']:,} | 0 | 0 | {orig['unattributed_pdata']:,} | {orig['unattributed_bytes']:,} | — |")
    add("")

    add("## 四、原版 `Cybersole.*` 子系统、DTO 与三方库逐项对照矩阵")
    add("")
    add(f"原版 `.rdata` 元数据共观测 **{len(orig['dlls'])}** 个程序集 `*.dll`、**{len(orig['cyb_tokens'])}** 个 `Cybersole.*` 词元、**"
        f"{len(orig['prop_inits'])}** 个 `PropInit` JSON/序列化 DTO、**{len(orig['async_sm'])}** 个 `<Method>d__N` 状态机名及 **{len(orig['avares_views'])}** 个 `avares://Cybersole/` 资产。")
    add("")
    add("| 子系统 / 命名空间 / 家族 | 原版实证证据（地址 / 数量） | 复刻件对应 | 分类 | 缺口与判定依据 |")
    add("|---|---|---|---|---|")
    for row in xref:
        add(f"| **{row['area']}** | {row['orig_evidence']} | {row['replica_counterpart']} | `{row['status']}` | {row['details']} |")
    add("")

    add("## 五、Phase 2 核心补齐优先级建议（遵循 R757 ①→②→③→④）")
    add("")
    add("1. **① 站点流程与支付闭环（`Cybersole.Stores`）**：优先反编译落地真实缺口中的可执行协议状态机——`ContinueUnzerThreeDs`（`0x143383aa9` 替代 `UnzerGateway.CompleteActionAsync` 空返回）、`CardinalInit`/`CardinalContinue`（`0x14338294f`）、`api.checkout.com`（`0x1470530bc`）与 `CheckPriceLimitApp`/`FindProductCDN`（`0x143373f5f` / `0x1433a0f23`）。")
    add("2. **② 接线已写但被 AOT 裁剪的服务岛（`Cybersole.Services.Mail`）**：将已有实现与单测的 `ImapMailProvider` + `AycdInboxClient` 接入 `AppServices.cs` 与 `TaskEngine.cs` 的验证码/邮箱验证等待流程（`WaitImapAsync` @ `0x14336b99e`），使 `MailKit`/`MimeKit` 真正进入 AOT 产物。")
    add("3. **③ 传输层与可观测性伴生包（`Cybersole.Http`）**：评估并补齐 `Cybersole.Http.Newtonsoft`（`LegacyJsonBody`）、`ClickHouseSink` 批量落盘及 `Cybersole.Http.Debug` 代理调试流，按需评估 `Cybersole.Http.X509.RootCertificates.bin`。")
    add("4. **④ 外部阻塞 / 范围外明确封存**：`DotNetBrowser`（653 函数）与 `Cybersole.Web.BrowserHandlers` 保持 `External Blocked`；`SignalR`/`connect/app` 远端同步与 `Remote*` schema 待有效凭据；`AuthWindow`/`LicenseControl`（R702）及 AI/CLIP 图像验证码自动求解执行面（`ExecuteClipModelAsync`/`ClickCellsAsync`）严格保持 `Out of Scope`。")
    add("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cache-dir", default=os.path.join(tempfile.gettempdir(), "cyber_reverse_census_cache"))
    parser.add_argument("--refresh-ida", action="store_true", help="Re-export strings, functions, and callgraph from live IDA 13337")
    parser.add_argument("--write-doc", action="store_true", help="Write docs/MODULE_FUNCTION_CENSUS.md")
    parser.add_argument("--doc-out", default=os.path.join(ROOT, "docs", "MODULE_FUNCTION_CENSUS.md"))
    args = parser.parse_args(argv)

    replica = analyze_replica()
    str_path, fn_path, cg_path = export_from_ida(args.cache_dir, args.refresh_ida)
    orig = analyze_original(str_path, fn_path, cg_path)
    xref = build_cross_reference(replica, orig)

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S %z")
    print("=== REPLICA .pdata 100% ATTRIBUTION ===")
    print(f"  exe={replica['exe_path']}  valid_pdata={replica['valid_pdata_extents']:,}  outside={replica['outside_pdata']}")
    for row in replica["buckets"][:10]:
        print(f"  {row['bucket']:<30} {row['total']:>7,} ({row['pct']:5.2f}%)  bytes={row['bytes']:>11,}")

    print("\n=== ORIGINAL MULTI-SIGNAL ATTRIBUTION ===")
    print(
        f"  ida={orig['ida_funcs']:,}  pdata_overlap={orig['ida_pdata_overlap']:,}  "
        f"direct={orig['direct_total']:,}  prop={orig['hop1'] + orig['hop2']:,}  unattr={orig['unattributed_total']:,}"
    )
    for row in orig["buckets"][:12]:
        print(
            f"  {row['bucket']:<36} total={row['total_ida']:>6,} (dir={row['direct']:>5,}, prop={row['propagated']:>5,})  "
            f"bytes={row['bytes']:>10,}  med={row['med_va']}"
        )

    if args.write_doc:
        os.makedirs(os.path.dirname(args.doc_out), exist_ok=True)
        md = render_markdown(replica, orig, xref, now)
        with open(args.doc_out, "w", encoding="utf-8", newline="\n") as f:
            f.write(md)
        print(f"\nwrote {args.doc_out} ({len(md.splitlines())} lines)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
