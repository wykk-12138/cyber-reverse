import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Controls\ComboBoxEdit.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('Cybersole.Core.Primitives.RelayCommand', 'RelayCommand')
t = t.replace('using Avalonia.Layout;', 'using Avalonia.Layout;\nusing Cybersole.Core;')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('using fixed')
