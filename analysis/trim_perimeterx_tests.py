"""Trim PerimeterXMarkerTests to its two behavioural tests (R1278)."""
import io

P = 'tests/Cybersole.Tests/PerimeterXMarkerTests.cs'
lines = io.open(P, encoding='utf-8').read().split('\n')

# find the end of the second test method (the one that asserts page-level literals are absent)
marker = None
for i, line in enumerate(lines):
    if 'NoneOfTheFourIsAPageLevelLiteral' in line:
        marker = i
        break
if marker is None:
    raise SystemExit('second test not found')

# walk forward to the closing brace of that method at the same indent level
depth = 0
end = None
started = False
for i in range(marker, len(lines)):
    depth += lines[i].count('{') - lines[i].count('}')
    if '{' in lines[i]:
        started = True
    if started and depth == 0:
        end = i
        break
if end is None:
    raise SystemExit('closing brace not found')

note = [
    '',
    '    // R1278: the two assertions that used to sit here read VendorWiring.Rows to check the gap kind, the marker',
    '    // source and that both gap kinds have a live example. Those are rows in the audit table, which now lives in',
    '    // docs/VENDOR_WIRING.md; what stays in this file is what the runtime inventory can be asked about.',
    '}',
    '',
]

out = lines[:end + 1] + note
io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print('trimmed to line %d, total %d lines' % (end + 1, len(out)))
