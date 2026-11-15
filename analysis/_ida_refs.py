"""IDAPython: locate a literal by text, then find who references it (data-indirect or code).

Why not a public tool: `ida_pro_mcp`'s xrefs_to only reports references IDA has already recorded,
and NativeAOT keeps frozen string literals in one big blob. A literal therefore usually starts at
an *interior* offset of the blob IDA sees as one string, so xrefs_to on the blob start returns 0
for a literal that is definitely used. This script finds the literal's own address first, then
looks for both code references and 8-byte pointer slots (the layout frozen-string loads use).

Run inside IDA through the plugin:
    python analysis/ida.py call py_exec_file '{"file_path":"D:/projects/cyber-reverse/analysis/_ida_refs.py"}'

Edit NEEDLES below before running.
"""
import ida_bytes
import ida_funcs
import ida_segment
import ida_xref
import idc

NEEDLES = [
    'TaskView,Cybersole.Toggle!',
    'TaskView,Cybersole.LinkChange!',
    'MonitorView,Cybersole.Quicktask!',
]


def segments():
    for i in range(ida_segment.get_segm_qty()):
        seg = ida_segment.getnseg(i)
        if seg is not None:
            yield seg


def find_text(needle, limit=8):
    raw = needle.encode('utf-8')
    hits = []
    for seg in segments():
        ea, end = seg.start_ea, seg.end_ea
        while ea < end and len(hits) < limit:
            size = min(1 << 20, end - ea)
            blob = ida_bytes.get_bytes(ea, size)
            if blob:
                pos = blob.find(raw)
                while pos >= 0 and len(hits) < limit:
                    hits.append(ea + pos)
                    pos = blob.find(raw, pos + 1)
            ea += size
    return hits


def func_of(ea):
    f = ida_funcs.get_func(ea)
    return None if f is None else (f.start_ea, ida_funcs.get_func_name(f.start_ea))


def drefs(ea, limit=12):
    out, x = [], ida_xref.get_first_dref_to(ea)
    while x != idc.BADADDR and len(out) < limit:
        out.append(x)
        x = ida_xref.get_next_dref_to(ea, x)
    return out


def pointer_hits(value, limit=8):
    needle = value.to_bytes(8, 'little')
    hits = []
    for seg in segments():
        ea, end = seg.start_ea, seg.end_ea
        while ea < end and len(hits) < limit:
            size = min(1 << 20, end - ea)
            blob = ida_bytes.get_bytes(ea, size)
            if blob:
                pos = blob.find(needle)
                while pos >= 0 and len(hits) < limit:
                    hits.append(ea + pos)
                    pos = blob.find(needle, pos + 1)
            ea += size
    return hits


for needle in NEEDLES:
    print('=== %r' % needle)
    addresses = find_text(needle)
    print('  literal addresses: %d  %s' % (len(addresses), ' '.join('%#x' % a for a in addresses)))
    for addr in addresses:
        text = idc.get_strlit_contents(addr, -1, 0)
        print('   @%#x  %r' % (addr, (text or b'')[:80]))
        for d in drefs(addr):
            print('     code/data ref from %#x %s' % (d, func_of(d)))
        for slot in pointer_hits(addr):
            readers = drefs(slot)
            print('     pointer slot %#x readers=%d' % (slot, len(readers)))
            for r in readers[:6]:
                print('        from %#x %s' % (r, func_of(r)))
    print()
