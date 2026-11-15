"""IDAPython: dump per-function structural fingerprints, in chunks (R572).

Run *inside* IDA via `python analysis/ida.py py "exec(open('…/_run_dump_orig.py', encoding='utf-8').read())"`.

Why not the existing tools:

* `rea`'s `match_native_functions` is the right instrument, but REA's `ida` provider is `not_configured` on the
  running server (its `REA_IDA_MCP_CONFIG` needs a process restart — BLOCKERS.md §13). Same idea, done by hand.
* `analysis/ida.py funcs` cannot filter (`name_contains` is not in `func_query`'s schema; R570) and pages 50 rows
  per call — 321,244 functions would need ~6,400 round trips.

## Why chunked

The IDA MCP plugin enforces its own **60 s hard limit per tool call** (`ida_mcp/sync.py`:
`Tool timed out after 60.00s`). A whole-image pass at level 2 exceeds it, and the plugin's limit is not something
the caller can raise. So `main()` takes `(start_index, limit)` and appends; the caller loops until it has what it
needs.

## Levels

`LEVEL = 1` — only facts IDA already has (`size`, CFG block count). It ran over 203,878 functions in 17 s and the
measurement killed it (`analysis/fp_discrimination.py`): 20,752 distinct tuples, 6.0 % of rows unique, largest
bucket 5,466.

`LEVEL = 2` — adds `ncallees` (distinct functions called) and `nstrrefs` (distinct string literals referenced),
one instruction pass per function. Calls and literals are far more specific than a size.

If level 2 is still non-discriminating, the conclusion is that this key *family* cannot pair .NET-AOT functions
and the next attempt must be a different kind of key (canonical CFG hash, instruction-sequence hash) — not more
features of the same sort.

Columns: `start_ea  size  nblocks  ncallees  nstrrefs  name`.
Two functions with the same tuple are structurally similar — never proven identical. A match is a candidate.
"""

import io

import ida_bytes
import ida_funcs
import ida_gdl
import idautils

OUT = r"D:\projects\cyber-reverse\analysis\_fp_{tag}_L{level}.tsv"

MIN_SIZE = 32
MAX_SIZE = 8192
LEVEL = 2
HEADER_L2 = "start_ea\tsize\tnblocks\tncallees\tnstrrefs\tname\n"


def callee_count(func):
    seen = set()
    for ea in idautils.FuncItems(func.start_ea):
        for cref in idautils.CodeRefsFrom(ea, 0):
            target = ida_funcs.get_func(cref)
            if target is not None and target.start_ea != func.start_ea:
                seen.add(target.start_ea)
    return len(seen)


def string_ref_count(func):
    seen = set()
    for ea in idautils.FuncItems(func.start_ea):
        for dref in idautils.DataRefsFrom(ea):
            if ida_bytes.is_strlit(ida_bytes.get_flags(dref)):
                seen.add(dref)
    return len(seen)


def main(tag, start_index=0, limit=0, level=LEVEL):
    """Scan from `start_index` over eligible functions, writing at most `limit` rows.

    `start_index` indexes *eligible* functions (those inside the size window), not raw IDB order, so successive
    chunks never overlap and never skip. Returns how many rows were written.
    """
    out_path = OUT.format(tag=tag, level=level)
    total = ida_funcs.get_func_qty()

    eligible_seen = 0
    written = 0
    with io.open(out_path, "a", encoding="utf-8", newline="") as fh:
        if fh.tell() == 0:
            fh.write(HEADER_L2)

        for i in range(total):
            func = ida_funcs.getn_func(i)
            if func is None:
                continue
            size = func.end_ea - func.start_ea
            if size < MIN_SIZE or size > MAX_SIZE:
                continue

            if eligible_seen < start_index:
                eligible_seen += 1
                continue
            if limit and written >= limit:
                break

            try:
                nblocks = len(list(ida_gdl.FlowChart(func)))
            except Exception:                      # a broken CFG is data, not a crash
                nblocks = -1

            fh.write("%X\t%d\t%d\t%d\t%d\t%s\n" % (
                func.start_ea, size, nblocks, callee_count(func), string_ref_count(func),
                ida_funcs.get_func_name(func.start_ea) or ""))

            eligible_seen += 1
            written += 1

    print("chunk start=%d limit=%d -> wrote %d rows to %s" % (start_index, limit, written, out_path))
    return written
