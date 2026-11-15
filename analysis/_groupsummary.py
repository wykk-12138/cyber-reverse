import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()

anchor = '''    /// <summary>Whether the group is pinned to the top of the picker (bound as <c>PinGroup</c>).</summary>'''
add = '''    /// <summary>
    /// Starts every task in this group (bound as <c>StartAll</c>). The engine decides what "start" means for each task,
    /// exactly as the tasks page does.
    /// </summary>
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
        _services.Tasks.StopAll(tasks);
        return tasks.Count;
    }

    /// <summary>Whether the group is pinned to the top of the picker (bound as <c>PinGroup</c>).</summary>'''
assert anchor in t
t = t.replace(anchor, add, 1)

# GroupSummary needs the services handle
old_ctor = '''    private readonly TaskGroup _summaryGroup;'''
new_ctor = '''    private readonly TaskGroup _summaryGroup;
    private readonly AppServices _services;'''
assert old_ctor in t
t = t.replace(old_ctor, new_ctor, 1)
t = t.replace('''    public GroupSummary(AppServices services, TaskGroup group)
    {
        _summaryGroup = group;''', '''    public GroupSummary(AppServices services, TaskGroup group)
    {
        _services = services;
        _summaryGroup = group;''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('GroupSummary: StartAll + StopAll')
