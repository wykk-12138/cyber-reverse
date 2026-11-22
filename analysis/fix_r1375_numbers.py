"""Fill the measured numbers into the R1375 verdict section, without python string escapes."""

import io

PATH = 'replica/docs/VERDICT.md'
text = io.open(PATH, encoding='utf-8', newline='').read()

old_product = '`stepUpUrl` \u68c0\u51fa\uff08\u89c1\u4e0b\uff09\uff1b\u5c3a\u5bf8\u89c1\u4e0b\u3002'
new_product = ('`stepUpUrl` **\u4e09\u4e2a\u90fd ASCII \u547d\u4e2d 1**\uff08UTF-16 \u5404 0\uff09\uff1b\n'
               '  \u5c3a\u5bf8 62,054,400 \u2192 **62,063,616**\u3002')
old_check = '\u4ea7\u7269\u547d\u4e2d\u89c1\u4e0b\u3002'
new_check = '\u4ea7\u7269\u4e09\u4e32\u5404 ASCII \u547d\u4e2d 1\uff1b\u5c3a\u5bf8 +9,216 \u5b57\u8282\u3002'

changed = 0
if old_product in text:
    text = text.replace(old_product, new_product, 1)
    changed += 1
if old_check in text:
    text = text.replace(old_check, new_check, 1)
    changed += 1

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('replacements applied: %d' % changed)
