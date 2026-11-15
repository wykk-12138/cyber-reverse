import io, re
p = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
t = io.open(p, encoding='utf-8').read()
pat = re.compile(r'(\d+)\s*条(?:[：:]|逐字|错误文案|文案|错误)')
hits = [(m.group(1), t[max(0, m.start()-40):m.end()+10].replace('\n', ' ')) for m in pat.finditer(t)]
print('claims found:', len(hits))
for n, ctx in hits[-8:]:
    print('  ', n, '|', ctx)
