"""Append the R294 marker as a trailing comment on the line that names /api/beast (R1284).

The ratchet binds a path to the line naming it, so the marker has to end that same line; a comment on the next line
does not satisfy it (and would have been a lie about what the guard checks).
"""

import io

P = 'src/Cybersole.Stores/Flows/BstnFlow.cs'
lines = io.open(P, encoding='utf-8').read().split('\n')

changed = 0
for i, line in enumerate(lines):
    if '/api/beast' in line and not line.lstrip().startswith('//') \
            and 'inferred: no image evidence' not in line:
        stripped = line.rstrip()
        # a trailing comment after '+' is valid C#: the expression continues on the next line
        lines[i] = stripped + '  // inferred: no image evidence'
        changed += 1
        print('marked line %d' % (i + 1))

io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('lines marked:', changed)
