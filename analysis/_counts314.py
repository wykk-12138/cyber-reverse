import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
old = '| UI 类 | 98 个，**30 个不可达**（31%） | `UnreachedUiTypesTests` |'
new = '| UI 类 | 99 个，**30 个不可达**（30%） | `UnreachedUiTypesTests` |'
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('guide UI classes 98 -> 99 (unreachable stays 30)')
