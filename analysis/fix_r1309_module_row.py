"""R1309: move the module-count status row in VERDICT.md from 65 to 66.

The row is the one current claim the consistency guard reads; the file's thousands of historical prose
claims stay untouched, which is why the guard was narrowed to the row in R918. Byte-level edit with a
count assertion, UTF-8, because the file also carries CRLF and a blind rewrite would touch every line.
"""
import io
import re
import sys

PATH = 'replica/docs/VERDICT.md'

text = io.open(PATH, encoding='utf-8', newline='').read()
pattern = re.compile(r'(\|\s*\u6ce8\u518c\u6a21\u5757\s*\|\s*\*\*)65(\*\*)')
found = pattern.findall(text)
print('occurrences of the status row at 65: %d' % len(found))
if len(found) != 1:
    sys.exit(1)

updated = pattern.sub(r'\g<1>66\g<2>', text)
io.open(PATH, 'w', encoding='utf-8', newline='').write(updated)

check = io.open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'\|\s*\u6ce8\u518c\u6a21\u5757\s*\|\s*\*\*(\d+)\*\*', check)
print('now reads: %s' % (m.group(1) if m else 'MISSING'))
