import io, re
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
pat = re.compile(r'(\d+)\s*条(?:逐字|错误文案|文案|错误)')
for m in pat.finditer(t):
    s = max(0, m.start() - 60)
    ctx = t[s:m.end() + 10].replace('\n', '\\n')
    print(m.group(1), '|', ctx.encode('unicode_escape').decode()[:150])
