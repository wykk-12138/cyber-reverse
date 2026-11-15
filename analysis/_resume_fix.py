import io
p = r'D:\projects\cyber-reverse\replica\docs\RESUME.md'
t = io.open(p, encoding='utf-8').read()
t = t.replace('2. **跑一次全套**确认 1442+（R282 之后又改过工具，没改产品代码）。',
              '2. **跑一次全套**确认 1443+（R290 时点为 1443；条数会因为合并/新增断言而变，别把旧数字当基准）。')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('stale 1442 reference replaced')
