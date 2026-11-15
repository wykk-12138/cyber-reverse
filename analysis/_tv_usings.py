import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('using Cybersole.Ui.Views;', 'using Cybersole.Ui.Views;\nusing Cybersole.Ui.Views.Common;', 1)
t = t.replace('        ViewHostModal.Show(this, "New group", view);', '        Cybersole.Ui.Views.Common.ViewHostModal.Show(this, "New group", view);', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('using added, call qualified')
