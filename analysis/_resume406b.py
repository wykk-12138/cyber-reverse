import io
p = r"D:\projects\cyber-reverse\replica\docs\RESUME.md"
t = io.open(p, encoding='utf-8').read()
import re
m = re.search(r'2\. \*\*跑一次全套\*\*[^\n]*', t)
print('found:', bool(m))
if m:
    t = t[:m.start()] + '2. **跑一次全套** 确认 1575+（R405 时点为 1575；条数会因为合并/新增断言而变，别把旧数当基准）。' + t[m.end():]
    io.open(p, 'w', encoding='utf-8', newline='').write(t)
    print('full-suite line replaced')
else:
    # fall back: show the neighbourhood
    i = t.find('跑一次全套')
    print(repr(t[max(0,i-40):i+90]))
