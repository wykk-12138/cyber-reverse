"""R1290: classify every remaining `inferred` literal across Stores/Flows against the string dump.

Same judgement as R1289, applied to the whole directory: a literal the dump contains is promoted with its address; one
that does not is recorded as zero hits, which per R1266 means unknown and not absent.
"""

import glob
import io
import re

DUMP = 'analysis/ida_strings.txt'
FILES = sorted(glob.glob('replica/src/Cybersole.Stores/Flows/*.cs'))

entries = []
for line in io.open(DUMP, encoding='utf-8', errors='replace'):
    if '\t' in line:
        addr, _, s = line.partition('\t')
        entries.append((addr.strip(), s.rstrip('\n')))
print('dump entries:', len(entries))

PATHISH = re.compile(r'"(/[^"\\]{2,80})"')
BARE = re.compile(r'"([A-Za-z0-9_.\-]{6,60})"')

hits_total = 0
miss_total = 0
for path in FILES:
    text = io.open(path, encoding='utf-8').read()
    if 'inferred' not in text.lower():
        continue
    lines = text.split('\n')
    seen = set()
    rows = []
    for line in lines:
        if 'inferred' not in line.lower():
            continue
        for rx in (PATHISH, BARE):
            for m in rx.finditer(line):
                lit = m.group(1)
                if lit in seen or len(lit) < 5:
                    continue
                seen.add(lit)
                hit = next(((a, s) for a, s in entries if lit in s), None)
                rows.append((lit, hit))
    if not rows:
        continue
    print('\n==', path.rsplit('/', 1)[-1])
    for lit, hit in rows:
        if hit:
            hits_total += 1
            print('  HIT  %-44s %s  %s' % (lit, hit[0], hit[1][:40]))
        else:
            miss_total += 1
            print('  MISS %-44s' % lit)

print('\nTOTAL hit=%d miss=%d' % (hits_total, miss_total))
