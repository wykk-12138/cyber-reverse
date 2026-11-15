import io, re
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
before = t
t = t.replace('**0 条错误**', '**0 条报错**')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
pat = re.compile(r'(\d+)\s*条(?:逐字|错误文案|文案|错误)')
print('changed:', t != before, 'claims:', sorted(set(int(m.group(1)) for m in pat.finditer(t))))
