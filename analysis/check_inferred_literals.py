"""R1289: check every `inferred` literal in StoreFlow and MagentoFlow against the artifact's string dump.

The point is not to count them but to classify each one: a literal that the dump contains can be promoted to evidenced
(with its address), and one that does not can at least say "0 hits" instead of leaving a vague mark.
"""

import io
import re

DUMP = 'analysis/ida_strings.txt'
TARGETS = [
    'replica/src/Cybersole.Stores/Flows/StoreFlow.cs',
    'replica/src/Cybersole.Stores/Flows/MagentoFlow.cs',
]

# address <TAB> string
entries = []
for line in io.open(DUMP, encoding='utf-8', errors='replace'):
    if '\t' in line:
        addr, _, s = line.partition('\t')
        entries.append((addr.strip(), s.rstrip('\n')))
print('dump entries:', len(entries))

PATHISH = re.compile(r'"(/[^"\\]{2,80})"')
BARE = re.compile(r'"([A-Za-z0-9_.\-]{6,60})"')


def look(needle):
    hits = [(a, s) for a, s in entries if needle in s]
    return hits


for path in TARGETS:
    print('\n==', path.rsplit('/', 1)[-1])
    lines = io.open(path, encoding='utf-8').read().split('\n')
    seen = set()
    for i, line in enumerate(lines):
        if 'inferred' not in line.lower():
            continue
        for rx in (PATHISH, BARE):
            for m in rx.finditer(line):
                lit = m.group(1)
                if lit in seen or lit.startswith('/v1/') or len(lit) < 5:
                    continue
                seen.add(lit)
                hits = look(lit)
                if hits:
                    print('  HIT  %-46s %s  %s' % (lit, hits[0][0], hits[0][1][:44]))
                else:
                    print('  MISS %-46s' % lit)
