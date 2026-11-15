import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('        var url = task?.Product;', '        var url = task?.Url ?? task?.Product?.Name;', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('CopyUrl reads the task url')
