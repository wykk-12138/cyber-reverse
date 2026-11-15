import io, re
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
t = t.replace('| 变异检查 | **27 条**（R286 跑过 24 条全 fired；R305 新增 3 条待全量跑） | `tools/mutation-check.py` |',
              '| 变异检查 | **29 条**（R305 全量 27/27 fired；R307 再加 2 条） | `tools/mutation-check.py` |')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('guide count -> 29')
