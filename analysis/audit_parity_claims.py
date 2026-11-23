"""R1299: check criterion (d) mechanically instead of by reading.

docs/PARITY_CLAIMS.md states the rule it must satisfy: every claim carries an authority, and every claim whose status is
not unknown also carries a recomputable command; an unknown claim says what evidence is missing. This parses every
table in that file and reports the four ways a claim can fall short, so the criterion is a number rather than an
impression.
"""

import io
import re

P = 'D:/projects/cyber-reverse/docs/PARITY_CLAIMS.md'
lines = io.open(P, encoding='utf-8').read().split('\n')

rows = []
malformed = []
header = None
for lineno, line in enumerate(lines, 1):
    s = line.strip()
    if not s.startswith('|'):
        header = None if not s else header
        continue
    cells = [c.strip() for c in s.strip('|').split('|')]
    low = [c.lower() for c in cells]
    if 'claim' in low and 'authority' in low:
        header = low
        continue
    if header is None or set(''.join(cells)) <= set('-: '):
        continue
    if len(cells) != len(header):
        malformed.append((lineno, len(cells), len(header), cells[0] if cells else '?'))
        continue
    rows.append(dict(zip(header, cells)))

print('claims parsed:', len(rows))
print('malformed claim rows:', len(malformed))
for lineno, got, want, cid in malformed:
    print('  MALFORMED L%d (%s): got %d cells, expected %d' % (lineno, cid, got, want))
if not rows:
    raise SystemExit('no claim rows found -- check the table format')

no_authority = [r for r in rows if not r.get('authority') or r.get('authority') in ('—', '-', '?')]
unknown = [r for r in rows if 'unknown' in r.get('status', '').lower()]
no_command = [r for r in rows if 'unknown' not in r.get('status', '').lower()
              and (not r.get('command') or r.get('command') in ('—', '-'))]
unknown_without_gap = [r for r in unknown if not r.get('gap_reason') or r.get('gap_reason') in ('—', '-', '')]

print('status counts:', {k: sum(1 for r in rows if k in r.get('status', '').lower())
                         for k in ('pass', 'fail', 'unknown')})
print('claims without authority      :', len(no_authority))
print('non-unknown without a command :', len(no_command))
print('unknown without a gap_reason  :', len(unknown_without_gap))

for label, group in (('NO-AUTHORITY', no_authority), ('NO-COMMAND', no_command),
                     ('UNKNOWN-NO-GAP', unknown_without_gap)):
    for r in group[:8]:
        print('  %-14s %-6s %s' % (label, r.get('id', '?'), r.get('claim', '')[:70]))

print()
met = not (malformed or no_authority or no_command or unknown_without_gap)
print('CRITERION (d):', 'MET' if met else 'NOT MET')
if not met:
    raise SystemExit(1)
