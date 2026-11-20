"""R1296 (cont.): vendor_coverage.py opened the file R1282 deleted, so criterion (f)'s vendor column died.

Two changes, both about telling two situations apart that used to look the same:
  * no file            -> the wiring table was removed on purpose; the image-side inventory is still worth reporting;
  * file but zero rows -> a parser problem, which must keep failing loudly.
"""

import io

P = 'D:/projects/cyber-reverse/replica/tools/vendor_coverage.py'
text = io.open(P, encoding='utf-8').read()

# 1. the reader distinguishes "gone" from "empty"
old_read = '    text = io.open(WIRING, encoding="utf-8", errors="replace").read()\n    rows = []'
new_read = ('    if not os.path.exists(WIRING):\n'
            '        # R1296: R1282 removed VendorWiring.cs because nothing in the running product called it. The\n'
            '        # image-side vendor inventory is still a real measurement, so "the table is gone" must not look\n'
            '        # like "the parser found nothing".\n'
            '        return None\n'
            '    text = io.open(WIRING, encoding="utf-8", errors="replace").read()\n'
            '    rows = []')
if old_read not in text:
    raise SystemExit('reader anchor missing')
text = text.replace(old_read, new_read)

# 2. main() keeps failing on an empty parse but reports a removed table
old_main = ('    rows = wiring_rows()\n'
            '    if not rows:\n'
            '        print("  !! parsed zero wiring rows -- refusing to publish a table that would claim every vendor is missing")\n'
            '        return 2\n')
new_main = ('    rows = wiring_rows()\n'
            '    wiring_removed = rows is None\n'
            '    if wiring_removed:\n'
            '        rows = []\n'
            '    elif not rows:\n'
            '        print("  !! parsed zero wiring rows -- refusing to publish a table that would claim every vendor is missing")\n'
            '        return 2\n')
if old_main not in text:
    raise SystemExit('main anchor missing')
text = text.replace(old_main, new_main)

io.open(P, 'w', encoding='utf-8', newline='\n').write(text)
print('vendor_coverage.py updated')
