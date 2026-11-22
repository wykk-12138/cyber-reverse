"""Add the fourth limit C8 needs: the image pool's entries are IDA's own, and it concatenates neighbours.

The samples make it visible — `Bogus.dllg`, `DSystem.Text.RegularExpressions.dll.Syst` are two strings run together in
one pool entry. That inflates the locale-key and dependency classes, and a reader who did not know would read those
counts as real.
"""
import io

PATH = 'analysis/c8_string_class_compare.py'
text = io.open(PATH, encoding='utf-8').read()

if 'ida_strings.txt' in text and 'concatenat' in text:
    raise SystemExit('already recorded')

old = """    lines.append('  3. this answers \"what is comparable\", not \"what matches\": it is a comparison instrument,')
    lines.append('     not a verdict on parity.')"""
new = """    lines.append('  3. the image side is IDA\\'s own list, and it concatenates adjacent strings into one entry —')
    lines.append('     samples like \"Bogus.dllg\" are two strings run together — which inflates the dotted classes;')
    lines.append('  4. this answers \"what is comparable\", not \"what matches\": it is a comparison instrument,')
    lines.append('     not a verdict on parity.')"""

if old not in text:
    raise SystemExit('limits block not found')
io.open(PATH, 'w', encoding='utf-8', newline='').write(text.replace(old, new, 1))
print('fourth limit added')
