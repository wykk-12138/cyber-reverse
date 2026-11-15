"""Print one stored name blob in full, split into fragments (NativeAOT closure/method-name tables).

Why not a public tool: same reason as analysis/_nameblobs.py — these tables are the only surviving
compiler identifiers in a symbol-stripped NativeAOT image, and no public tool indexes them.

Usage: python analysis/_nameblobs.py --blob 0x0351c91b [more addresses]
"""
import io
import re
import sys

POOL = 'analysis/pe_strings.txt'
want = [a for a in sys.argv[1:] if a.startswith('0x')]

line_pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
frag_pat = re.compile(r'<[^<>]{1,80}>[A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]{6,}')

rows = {}
for line in io.open(POOL, encoding='utf-8', errors='replace').read().splitlines():
    m = line_pat.match(line)
    if m:
        rows[m.group(1)] = m.group(2)

for addr in want:
    text = rows.get(addr)
    print('=== %s  len=%d' % (addr, len(text or '')))
    if text is None:
        print('  (not in pool)')
        continue
    frags = [f for f in frag_pat.findall(text)]
    for f in frags:
        print('   ', f)
    print()
