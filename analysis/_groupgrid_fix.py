import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Proxies\ProxyView.cs'
t = io.open(p, encoding='utf-8').read()
old = '        var grid = new GroupGrid { Width = RailWidth };'
new = '        var grid = new GroupGrid();\n        grid.Width = RailWidth;'
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('ProxyView keeps the parenthesised construction')
