import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()

# ---- R345 again: GroupSummary gains StartAll / StopAll
anchor = '''    /// <summary>Whether the group is pinned to the top of the picker (bound as <c>PinGroup</c>).</summary>'''
add = '''    private readonly AppServices _services;

    /// <summary>Starts every task in this group (bound as <c>StartAll</c>). Returns how many were started.</summary>
    public int StartAll()
    {
        var tasks = _summaryGroup.Tasks.Where(t => !t.IsRunning).ToList();
        if (tasks.Count > 0) _services.Tasks.StartAll(tasks);
        return tasks.Count;
    }

    /// <summary>Stops every running task in this group (bound as <c>StopAll</c>). Returns how many were stopped.</summary>
    public int StopAll()
    {
        var tasks = _summaryGroup.Tasks.Where(t => t.IsRunning).ToList();
        _services.Tasks.StopAll(tasks.Select(task => task.Id));
        return tasks.Count;
    }

''' + anchor
assert anchor in t and 'public int StartAll()' not in t
t = t.replace(anchor, add, 1)
t = t.replace('''    public GroupSummary(AppServices services, TaskGroup group)
    {
        _summaryGroup = group;''', '''    public GroupSummary(AppServices services, TaskGroup group)
    {
        _services = services;
        _summaryGroup = group;''', 1)

# ---- R351: name above the tabs, Delete/Save footer, DeleteGroup
t = t.replace('''        Content = new StackPanel
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
        };''', '''        // R351: the live dialog prints "Group Name" as its own field above the tab strip.
        var groupName = UiKit.Text(_group.Name, watermark: "Group Name");
        groupName.TextChanged += (_, _) => _group.Name = groupName.Text ?? _group.Name;

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                new TextBlock { Text = "Group Settings", FontSize = 16, FontWeight = Avalonia.Media.FontWeight.SemiBold },
                UiKit.Row("Group Name", groupName),
                tabs,
                UiKit.Buttons(
                    UiKit.Button("Delete", () => DeleteGroup()),
                    UiKit.Button("Save", Save)),
                _status,
            },
        };''', 1)

# the General tab no longer edits the name
t = t.replace('''        var name = UiKit.Text(_group.Name, watermark: "Group name");
        var pinned''', '''        var pinned''', 1)
t = t.replace('''        name.TextChanged += (_, _) => _group.Name = name.Text ?? _group.Name;
''', '', 1)
t = t.replace('''            UiKit.Row("Name", name),
            UiKit.Row("Pinned", pinned),''', '''            UiKit.Row("Pinned", pinned),''', 1)

# DeleteGroup next to Save
t = t.replace('''    private void Save()
    {''', '''    /// <summary>Removes this group from the configuration (bound as <c>Delete</c>). False when it was never saved.</summary>
    public bool DeleteGroup()
    {
        if (!_services.Config.TaskGroups.Remove(_group)) return false;

        _services.Config.Save();
        _status.Text = "Group deleted.";
        return true;
    }

    private void Save()
    {''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('R345 + R351 re-applied')
