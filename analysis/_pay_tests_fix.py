import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PaymentViewTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('using Avalonia.VisualTree;', 'using Avalonia.LogicalTree;')
t = t.replace('''        view.GetVisualDescendants()''', '''        view.GetLogicalDescendants()''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('switched to the logical tree (no layout needed)')
