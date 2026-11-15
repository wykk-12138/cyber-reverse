import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
old = '| 变异检查 | **24 条，全部 guard fired** | `tools/mutation-check.py` |'
new = '| 变异检查 | **27 条**（R286 跑过 24 条全 fired；R305 新增 3 条待全量跑） | `tools/mutation-check.py` |'
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('guide count 24 -> 27')
