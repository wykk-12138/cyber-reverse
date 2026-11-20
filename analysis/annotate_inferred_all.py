"""R1290: annotate every remaining `inferred` line in Stores/Flows with what the dump said.

23 of 24 literals answer zero hits; per R1266 that is unknown, not absent, and the annotation says exactly that. The
`inferred: no image evidence` phrase stays intact because EndpointEvidenceRatchetTests binds on it.
"""

import glob
import io

MARK = 'inferred: no image evidence'
SUFFIX = '; 0 hits in the 324,901-entry dump; R1266: absence carries no information'

total = 0
for path in sorted(glob.glob('D:/projects/cyber-reverse/replica/src/Cybersole.Stores/Flows/*.cs')):
    text = io.open(path, encoding='utf-8').read()
    if MARK not in text:
        continue
    lines = text.split('\n')
    changed = 0
    for i, line in enumerate(lines):
        if MARK not in line or 'R1266' in line:
            continue
        idx = line.find(MARK) + len(MARK)
        lines[i] = line[:idx] + SUFFIX + line[idx:]
        changed += 1
    if changed:
        io.open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
        print('%-28s %d line(s)' % (path.rsplit('/', 1)[-1], changed))
        total += changed

print('total annotated:', total)
