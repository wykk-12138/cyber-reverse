"""IDAPython: canonical instruction-sequence hash per function (R573).

Run *inside* IDA via `python analysis/ida.py py "exec(open('…/_run_dump_orig.py', encoding='utf-8').read())"`.

## Why this exists

R572 measured the count-based key family and it failed: `(size, nblocks)` was unique for 6.02 % of functions,
adding `ncallees` + `nstrrefs` only reached 13.27 %, and the largest buckets stayed at ~5,370 members — all small
functions with no string references. More features of that kind cannot help, because two different getters with
the same size / block count / call count are *identical* to a counter.

So this is a **different family**: hash the instruction sequence itself, normalising away exactly the things that
are allowed to differ between two builds.

## What is normalised

For every instruction in the function, in order:

    mnemonic        kept verbatim (`d.get_canon_mnem()`)
    register operand kept as its register number
    immediate       -> "#imm"      addresses, constants
    memory/displacement -> "#mem"  address-shaped operands
    everything else -> "t<type>"

Concatenated and hashed with SHA-256. Two functions with the same hash have the **same instruction template**:
same mnemonics in the same order, same registers, same operand *kinds* — with no dependence on where they sit in
the image.

## What it still cannot see

* Register **allocation** differences (same template, different physical registers) produce different hashes.
* Inlining differences between .NET 10 and .NET 8 AOT produce different *sequences* — a known mismatch source
  (BLOCKERS.md §13 §6).
* Jump targets are normalised away, so two functions differing only in which branch goes where hash the same.
  That is deliberate: it makes the key robust, and it means a match is a **candidate**, never proof.

## Chunking

The IDA MCP plugin enforces a 60 s hard limit per call (`ida_mcp/sync.py`); the caller cannot raise it. So
`main()` takes `(start_index, limit)` over *eligible* functions and appends.
"""

import hashlib
import io

import ida_funcs
import idautils

OUT = r"D:\projects\cyber-reverse\analysis\_fp_{tag}_H.tsv"

MIN_SIZE = 32
MAX_SIZE = 8192
HEADER = "start_ea\tsize\tinsns\thash\tname\n"

# operand types that are address/constant shaped and therefore must be normalised
NORMALISE_TYPES = {"o_imm", "o_mem", "o_near", "o_far", "o_displ"}


def instruction_template(func):
    """Canonical template string for one function, plus its instruction count."""
    import ida_ua                    # local: keeps module import cheap for callers that do not need it

    # numeric operand-type constants; `ida_ua.get_optype_name` does not exist (R573 first attempt died on it)
    normalise = {ida_ua.o_imm, ida_ua.o_mem, ida_ua.o_near, ida_ua.o_far, ida_ua.o_displ}
    tags = {ida_ua.o_imm: "#imm", ida_ua.o_mem: "#mem", ida_ua.o_near: "#near",
            ida_ua.o_far: "#far", ida_ua.o_displ: "#displ"}

    parts = []
    count = 0
    for ea in idautils.FuncItems(func.start_ea):
        insn = ida_ua.insn_t()
        if ida_ua.decode_insn(insn, ea) <= 0:
            parts.append("?")
            count += 1
            continue
        try:
            mnem = insn.get_canon_mnem()
        except Exception:
            mnem = "?"
        ops = []
        for op in insn.ops:
            if op.type == ida_ua.o_void:
                break
            if op.type == ida_ua.o_reg:
                ops.append("r%d" % op.reg)
            elif op.type in normalise:
                ops.append(tags[op.type])
            else:
                ops.append("t%d" % op.type)
        parts.append(mnem if not ops else mnem + " " + " ".join(ops))
        count += 1
    return "\n".join(parts), count


def main(tag, start_index=0, limit=0):
    out_path = OUT.format(tag=tag)
    total = ida_funcs.get_func_qty()

    eligible_seen = 0
    written = 0
    with io.open(out_path, "a", encoding="utf-8", newline="") as fh:
        if fh.tell() == 0:
            fh.write(HEADER)

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

            template, insns = instruction_template(func)
            digest = hashlib.sha256(template.encode("utf-8", "replace")).hexdigest()[:32]
            fh.write("%X\t%d\t%d\t%s\t%s\n" % (
                func.start_ea, size, insns, digest, ida_funcs.get_func_name(func.start_ea) or ""))

            eligible_seen += 1
            written += 1

    print("chunk start=%d limit=%d -> wrote %d rows to %s" % (start_index, limit, written, out_path))
    return written
