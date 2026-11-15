import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
t = t.replace('| UI 类 | 97 个，**36 个不可达**（37%） | `UnreachedUiTypesTests` |',
              '| UI 类 | 97 个，**37 个不可达**（38%） | `UnreachedUiTypesTests` |')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('guide: 97 / 37')
