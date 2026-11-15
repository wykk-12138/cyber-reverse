import io

def patch(path, cls, anchor_in_cls, member):
    t = io.open(path, encoding='utf-8').read()
    start = t.index(cls)
    if member.split('=>')[0].split('{')[0].strip().split()[-1] + ' ' in t[start:start+2000] or member.strip().split('\n')[0] in t:
        print('skip (present):', cls.split()[-1])
        return
    a = t.index(anchor_in_cls, start)
    t = t[:a] + member + t[a:]
    io.open(path, 'w', encoding='utf-8', newline='').write(t)
    print('patched', cls.split()[-1])

# ProfileGroupView.GroupName — it has a name TextBox created inside the ctor, so expose the composed name
patch(r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs",
      'public sealed class ProfileGroupView',
      '    private readonly AppServices _services;',
      '''    /// <summary>The group name on screen (bound as <c>GroupName</c>). Updated as the box changes.</summary>
    public string GroupName => _typedName;

    private string _typedName = string.Empty;

''')

# AccountGroupView.GroupName
patch(r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Accounts\AccountModals.cs",
      'public sealed class AccountGroupView',
      '    private readonly TextBox _name;',
      '''    /// <summary>The group name in the box (bound as <c>GroupName</c>).</summary>
    public string GroupName => _name.Text ?? string.Empty;

''')

# TaskGroupListView.Groups
patch(r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs",
      'public sealed class TaskGroupListView',
      '    private readonly AppServices _services;',
      '''    /// <summary>The groups this list shows (bound as <c>Groups</c>).</summary>
    public IReadOnlyList<TaskGroup> Groups => _services.Config.TaskGroups;

''')
