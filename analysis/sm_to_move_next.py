"""From an async state-machine type name to the function that implements it.

WHY THIS EXISTS: the tail map (docs/ASYNC_TAIL.md) lists methods by name, and the image keeps those
names as `<Name>d__NN` strings, but a name is not an address. The obvious route -- code xrefs -- does
not work, because the name is referenced from the type's metadata structure in .rdata, not from .text.

So: the string object is at `chars_va - 12` (the NativeAOT string layout this project uses everywhere);
the EEType for the state machine holds a pointer to it; the EEType's interface slots sit *before* that
pointer, and each slot is a code address. This walks that: find the data slot holding the pointer, read
the qwords around it, keep the ones that land in .text, and report each with its .pdata size so the
biggest candidate -- a state machine's MoveNext is always the big one -- is obvious.

It reports candidates rather than a verdict on purpose: which slot is MoveNext depends on the interface
list, and claiming one without decompiling it would be exactly the kind of guess this project keeps
having to retract.

Usage:
    python analysis/sm_to_move_next.py Complete3DSOrder
"""
import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

TEXT_LO, TEXT_HI = 0x140001000, 0x147000000


def find_string_addresses(name):
    """Every chars_va whose text is exactly `<name>d__NN`.

    Goes through `ida.py str` rather than a direct tool call: that wrapper already knows which plugin
    tool answers a string query (the name is not `search_strings` -- that tool does not exist, and
    guessing tool names is how this script failed on its first run).
    """
    import subprocess
    done = subprocess.run(
        [sys.executable, 'analysis/ida.py', 'str', '<' + name + '>d__', '--limit', '20'],
        capture_output=True, text=True, encoding='utf-8', errors='replace')
    try:
        res = json.loads(done.stdout)
    except json.JSONDecodeError:
        print('string query failed: %s' % (done.stdout or done.stderr)[:300])
        return []
    out = []
    for m in (res.get('matches') or []):
        addr = int(m['addr'], 16)
        text = m.get('string') or ''
        idx = text.find('<' + name + '>d__')
        if idx >= 0:
            # chars_va is the start of the whole listed string, which may carry a leading length byte.
            out.append((addr + idx, text))
    return out


def find_data_pointers(obj_va):
    """Data addresses holding an 8-byte pointer to obj_va."""
    pattern = ' '.join('%02X' % b for b in obj_va.to_bytes(8, 'little'))
    res = call('find_bytes', {'patterns': [pattern]})
    if isinstance(res, str):
        res = json.loads(res)
    hits = []
    for entry in res:
        for addr in (entry.get('matches') or []):
            value = int(addr, 16)
            # A cell that holds the pointer must itself live in data, not in .text.
            if not (TEXT_LO <= value < TEXT_HI):
                hits.append(value)
    return hits


def read_qwords(addr, before=0x40, after=0x10):
    start = addr - before
    size = before + after
    res = call('get_bytes', {'regions': [{'addr': hex(start), 'size': size}]})
    if isinstance(res, str):
        res = json.loads(res)
    blob = bytes(int(t, 16) for t in res[0]['data'].split())
    out = []
    for off in range(0, len(blob) - 7, 8):
        value = int.from_bytes(blob[off:off + 8], 'little')
        out.append((start + off, value))
    return out


def pdata_size(addr):
    res = call('lookup_funcs', {'queries': [{'address': hex(addr)}]})
    if isinstance(res, str):
        res = json.loads(res)
    for f in (res.get('functions') or res.get('funcs') or []):
        if isinstance(f, dict):
            return f.get('size') or f.get('end')
    return None


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    name = argv[0]
    strings = find_string_addresses(name)
    print('string sites for <%s>d__: %d' % (name, len(strings)))
    for chars_va, text in strings:
        print('  chars_va=0x%X  %r' % (chars_va, text[:60]))

    for chars_va, _ in strings:
        obj_va = chars_va - 12
        print('\n--- obj_va=0x%X' % obj_va)
        pointers = find_data_pointers(obj_va)
        print('  data cells holding that pointer: %d' % len(pointers))
        for cell in pointers:
            print('    cell=0x%X' % cell)
            for slot, value in read_qwords(cell):
                if TEXT_LO <= value < TEXT_HI:
                    size = pdata_size(value)
                    print('      slot 0x%X -> 0x%X  size=%s' % (slot, value, size))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
