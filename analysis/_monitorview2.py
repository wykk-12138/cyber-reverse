import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Monitor\MonitorView.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('        Title = TabLabel;\n\n', '', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('removed the Window-only Title assignment')
