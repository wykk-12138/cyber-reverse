import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()

old = '''        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                UiKit.Title("Task group"),
                tabs,
                UiKit.Buttons(
                    UiKit.Button("Save", Save),
                    UiKit.Button("Reset", Reset)),
                _status,
            },
        };'''
new = '''        // R351: the live dialog prints "Group Name" as its own field ABOVE the tab strip (measured R350), so the name
        // no longer lives inside the General tab. Pinned / Order stay where they were until their real home is found.
        var title = new TextBlock { Text = "Group Settings", FontSize = 16, FontWeight = FontWeight.SemiBold };
        var groupName = UiKit.Text(_group.Name, watermark: "Group Name");
        groupName.TextChanged += (_, _) => _group.Name = groupName.Text ?? _group.Name;

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                title,
                UiKit.Row("Group Name", groupName),
                tabs,
                UiKit.Buttons(
                    UiKit.Button("Delete", Delete, danger: true),
                    UiKit.Button("Save", Save)),
                _status,
            },
        };'''
assert old in t
t = t.replace(old, new, 1)

# the General tab keeps Pinned/Order but no longer the name
t = t.replace('''    private Control BuildGeneral()
    {
        var name = UiKit.Text(_group.Name, watermark: "Group name");
        var pinned = UiKit.Check("Pinned", _group.Pinned);''',
'''    private Control BuildGeneral()
    {
        // R351: the name moved above the tabs (as the live dialog shows); what is left here is Pinned/Order, whose real
        // home has not been found yet — see docs/GUI_BASELINE.md R350/R351.
        var pinned = UiKit.Check("Pinned", _group.Pinned);''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('name moved above the tabs; footer Delete/Save')
