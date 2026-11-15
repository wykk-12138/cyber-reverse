import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('        _services.Tasks.StopAll(tasks);', '        _services.Tasks.StopAll(tasks.Select(task => task.Id));')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('StopAll takes ids')
