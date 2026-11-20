"""R1295: resync the four mutation anchors my own edits invalidated.

R1290 appended a R1266 note to 41 `inferred: no image evidence` lines, and R1294 reworded Farfetch's seven messages.
Both are the kind of edit that leaves a mutation anchor behind: the guard still exists and still passes, but the checker
can no longer find the text to mutate, so it reports SKIP and the "all fired" criterion quietly stops holding. The four
anchors are updated to the text that is actually in the files now.
"""

import io

P = 'D:/projects/cyber-reverse/replica/tools/mutation-check.py'
text = io.open(P, encoding='utf-8').read()

SUFFIX = '; 0 hits in the 324,901-entry dump; R1266: absence carries no information'

pairs = [
    ("'inferred: no image evidence (R297)'",
     "'inferred: no image evidence" + SUFFIX + " (R297)'"),
    ("'inferred: no image evidence (R298)'",
     "'inferred: no image evidence" + SUFFIX + " (R298)'"),
    ("'inferred: no image evidence (R294)'",
     "'inferred: no image evidence" + SUFFIX + " (R294)'"),
]

for old, new in pairs:
    if old not in text:
        print('MISS:', old)
        continue
    text = text.replace(old, new)
    print('ok:', old[:44])

old_far = ('"find": \'            "farfetch: product endpoint unknown -- server-delivered route (connect/app config), '
           'schema needs the original login"\',')
new_far = ('"find": \'            "farfetch: product route unrecorded locally \u2014 it is a server-delivered '
           'connect/app config entry, schema needs the original login to capture"\',')
if old_far in text:
    text = text.replace(old_far, new_far)
    print('ok: farfetch find')
else:
    print('MISS: farfetch find')

old_rep = '"replace": \'            "farfetch: product endpoint unknown");\','
new_rep = '"replace": \'            "farfetch: product route unrecorded locally");\','
if old_rep in text:
    text = text.replace(old_rep, new_rep)
    print('ok: farfetch replace')
else:
    print('MISS: farfetch replace')

io.open(P, 'w', encoding='utf-8', newline='\n').write(text)
print('done')
