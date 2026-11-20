"""R1294: Farfetch's seven placeholders already say what they are — make the wording say it too.

R1077 closed the question: the route is a server-delivered connect/app config entry and the entry's schema needs the
original login to capture. That is a classification, not an open unknown, so the message stops claiming "unknown" while
keeping the word `unrecorded` (FlowWorkAuditTests accepts either spelling) and keeping the reason in place.
"""

import io
import re

P = 'D:/projects/cyber-reverse/replica/src/Cybersole.Stores/Flows/FarfetchFlow.cs'
text = io.open(P, encoding='utf-8').read()

pattern = re.compile(
    r'"farfetch: ([a-z\-]+) endpoint unknown -- server-delivered route \(connect/app config\), schema needs the original login"')

replaced = pattern.findall(text)
text = pattern.sub(
    lambda m: ('"farfetch: %s route unrecorded locally — it is a server-delivered connect/app config entry, '
               'and that entry\'s schema needs the original login to capture"' % m.group(1)),
    text)

io.open(P, 'w', encoding='utf-8', newline='\n').write(text)
print('replaced %d message(s): %s' % (len(replaced), ', '.join(replaced)))
print('remaining "endpoint unknown" in file:', text.count('endpoint unknown'))
