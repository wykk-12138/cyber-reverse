import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
before = t
t = t.replace('40 分钟内**0 条错误**', '40 分钟内**0 条 error 级记录**')
t = t.replace('40 分钟内 0 条错误', '40 分钟内 0 条 error 级记录')
print('changed:', t != before)
io.open(p, 'w', encoding='utf-8', newline='').write(t)

import re
pat = re.compile(r'(\d+)\s*条(?:逐字|错误文案|文案|错误)')
print('claims now:', sorted(set(int(m.group(1)) for m in pat.finditer(t))))
