import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Controls\ComboBoxEdit.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('using Cybersole.Core;\n', 'using Cybersole.Core.Models;\n')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('namespace fixed to Cybersole.Core.Models')
