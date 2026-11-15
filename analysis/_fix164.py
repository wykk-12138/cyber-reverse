import io
p = r'D:\projects\cyber-reverse\replica\tools\mutation-check.py'
t = io.open(p, encoding='utf-8').read()
old = '**83 个 UI 类：26 个'
new = '**84 个 UI 类：26 个'
assert old in t, 'anchor text not found'
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('round 164 UI-count anchor: 83 -> 84 (PARITY.md moved at R312)')
