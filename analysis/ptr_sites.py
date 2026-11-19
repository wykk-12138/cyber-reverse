"""Find where a function pointer is stored in the image's data sections.

Why this is not one of the existing scripts: disp32_scan_any.py scans .text for rip-relative displacements, which
finds instructions that reference an address. A delegate or vtable slot references the thunk the other way round,
as an eight-byte little-endian pointer stored in .rdata/.data/.idata, so the search runs over data sections for an
absolute value and has to use ida_bytes.find_bytes rather than a text scan.

Usage:
    python analysis/ptr_sites.py 0x1425456E0 [more addresses...]
"""
import json
import subprocess
import sys

TEMPLATE = (
    "import ida_bytes, ida_segment, ida_idaapi, json\n"
    "BADADDR = ida_idaapi.BADADDR\n"
    "target = %d\n"
    "pattern = target.to_bytes(8, 'little')\n"
    "hits = []\n"
    "s = ida_segment.get_first_seg()\n"
    "while s:\n"
    "    name = ida_segment.get_segm_name(s)\n"
    "    if name != '.text':\n"
    "        ea = ida_bytes.find_bytes(pattern, s.start_ea, s.end_ea)\n"
    "        while ea != BADADDR:\n"
    "            hits.append(hex(ea))\n"
    "            ea = ida_bytes.find_bytes(pattern, ea + 1, s.end_ea)\n"
    "    s = ida_segment.get_next_seg(s.start_ea)\n"
    "print(json.dumps(hits[:40]))\n"
)


def main(argv):
    for addr in argv:
        target = int(addr, 16)
        out = subprocess.run([sys.executable, 'analysis/ida.py', 'py', TEMPLATE % target, '--timeout', '600'],
                             capture_output=True, text=True, encoding='utf-8', errors='replace')
        doc = json.JSONDecoder().raw_decode(out.stdout)[0]
        err = (doc.get('stderr') or '').strip()
        if err:
            print('%s ERR %s' % (addr, err.split('\n')[-1][:100]))
            continue
        raw = (doc.get('stdout') or '').strip().split('\n')[-1]
        hits = json.loads(raw)
        print('%s stored at %d site(s): %s' % (addr, len(hits), ' '.join(hits[:8])))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
