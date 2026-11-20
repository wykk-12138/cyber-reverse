"""R1289: say what was actually checked on each `inferred` line in StoreFlow and MagentoFlow.

Checked against the 324,901-entry string dump: `/rest/V1` is there (146AB72A4); the other seven paths are not. R1266
says absence carries no information, so "0 hits" is written as exactly that and not as "not in the image". The
`inferred: no image evidence` phrase stays intact because EndpointEvidenceRatchetTests binds on it.
"""

import io

FILES = {
    'D:/projects/cyber-reverse/replica/src/Cybersole.Stores/Flows/StoreFlow.cs': '0 hits in the 324,901-entry dump',
    'D:/projects/cyber-reverse/replica/src/Cybersole.Stores/Flows/MagentoFlow.cs': '0 hits in the 324,901-entry dump',
}

MARK = 'inferred: no image evidence'
SUFFIX = '; {note}; R1266: absence carries no information'

for path, note in FILES.items():
    lines = io.open(path, encoding='utf-8').read().split('\n')
    changed = 0
    for i, line in enumerate(lines):
        if MARK not in line:
            continue
        if 'R1266' in line:          # already annotated
            continue
        # /rest/V1 is the one literal of the eight that the dump does contain
        tag = 'present at 146AB72A4' if '/rest/V1' in line and 'carts' not in line else note
        idx = line.find(MARK) + len(MARK)
        lines[i] = line[:idx] + SUFFIX.format(note=tag) + line[idx:]
        changed += 1
    io.open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
    print('%s: annotated %d line(s)' % (path.rsplit('/', 1)[-1], changed))
