import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('''        return UiKit.Scroll(UiKit.Form(
            UiKit.Row("Name", name),
            UiKit.Row("Pinned", pinned),
            UiKit.Row("Order", order)));''',
'''        return UiKit.Scroll(UiKit.Form(
            UiKit.Row("Pinned", pinned),
            UiKit.Row("Order", order)));''', 1)
t = t.replace('UiKit.Button("Delete", DeleteGroup),', 'UiKit.Button("Delete", () => DeleteGroup()),')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('wrapped the delete call, dropped the dead row')
