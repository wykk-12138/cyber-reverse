import io

# 1) GroupSummary.PinGroup — a task group can be pinned; the original binds PinGroup on the summary card
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs'
t = io.open(p, encoding='utf-8').read()
old = '''    public GroupSummary(AppServices services, TaskGroup group)
    {'''
new = '''    private readonly TaskGroup _summaryGroup;

    /// <summary>Whether the group is pinned to the top of the picker (bound as <c>PinGroup</c>).</summary>
    public bool PinGroup
    {
        get => _summaryGroup.Pinned;
        set => _summaryGroup.Pinned = value;
    }

    public GroupSummary(AppServices services, TaskGroup group)
    {
        _summaryGroup = group;'''
assert old in t
t = t.replace(old, new, 1)

# 2) TaskGroupView.Draft — the group being edited before it is saved
old2 = '''    public TaskGroupView(AppServices services, TaskGroup? group = null)
    {'''
new2 = '''    /// <summary>The group this dialog is editing — the draft (bound as <c>Draft</c>).</summary>
    public TaskGroup Draft => _group;

    public TaskGroupView(AppServices services, TaskGroup? group = null)
    {'''
assert old2 in t
t = t.replace(old2, new2, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('GroupSummary.PinGroup + TaskGroupView.Draft')

# 3) ProxyGroupView.Draft
p2 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Proxies\ProxyGroupView.cs'
t2 = io.open(p2, encoding='utf-8').read()
old3 = '''    public ProxyGroupView(ProxyGroup group)
    {'''
new3 = '''    /// <summary>The group being edited (bound as <c>Draft</c>).</summary>
    public ProxyGroup Draft => _group;

    public ProxyGroupView(ProxyGroup group)
    {'''
assert old3 in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(old3, new3, 1))
print('ProxyGroupView.Draft')
