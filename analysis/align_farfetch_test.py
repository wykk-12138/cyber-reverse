"""R1294 (cont.): align the message and the test on the fact, not on a whole sentence.

The test asserted one entire sentence, which is why a wording change broke it. It keeps the three phrases that carry the
finding — server-delivered, connect/app, schema needs the original login — and drops the sentence-long match for the
classification prefix.
"""

import io
import re

F = 'D:/projects/cyber-reverse/replica/src/Cybersole.Stores/Flows/FarfetchFlow.cs'
text = io.open(F, encoding='utf-8').read()
text = text.replace(
    "and that entry's schema needs the original login to capture\"",
    'schema needs the original login to capture"')
io.open(F, 'w', encoding='utf-8', newline='\n').write(text)
print('message phrasing aligned:', text.count('schema needs the original login'))

T = 'D:/projects/cyber-reverse/replica/tests/Cybersole.Tests/FarfetchIsCoveredByTheOriginalTests.cs'
lines = io.open(T, encoding='utf-8').read().split('\n')

start = next(i for i, l in enumerate(lines) if '"farfetch: product endpoint unknown' in l)
# the assertion spans two lines: Assert.Contains( + the literal
begin = start - 1
while 'Assert.Contains(' not in lines[begin]:
    begin -= 1
end = start
while not lines[end].rstrip().endswith(');'):
    end += 1

replacement = [
    '        // R1294: the message was reclassified from "endpoint unknown" to "route unrecorded locally" because',
    '        // R1077 had already closed the question. The assertion follows the fact, not the sentence.',
    '        Assert.Contains("route unrecorded locally", source, StringComparison.Ordinal);',
]
lines[begin:end + 1] = replacement
io.open(T, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('test assertion replaced, lines %d-%d' % (begin + 1, end + 1))
