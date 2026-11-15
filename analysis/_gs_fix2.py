import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('FontSize = 16, FontWeight = FontWeight.SemiBold', 'FontSize = 16, FontWeight = Avalonia.Media.FontWeight.SemiBold')
t = t.replace('UiKit.Button("Delete", Delete, danger: true),', 'UiKit.Button("Delete", DeleteGroup, danger: true),')
# BuildGeneral still referenced `name`
t = t.replace('''        name.TextChanged += (_, _) => _group.Name = name.Text ?? _group.Name;
        pinned.IsCheckedChanged''', '''        pinned.IsCheckedChanged''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('fixes applied')
