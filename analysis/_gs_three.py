import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>Starts every task in this group (bound as <c>StartAll</c>). Returns how many were started.</summary>'''
add = '''    /// <summary>Whether this summary exists to be edited rather than viewed (bound as <c>Edit</c>) — always true for a
    /// summary that already names a group.</summary>
    public bool Edit => _summaryGroup is not null;

    /// <summary>
    /// Duplicates this group and its tasks (bound as <c>Clone</c>). The copy is named "&lt;name&gt; copy" and appended to the
    /// configuration; returns the new group.
    /// </summary>
    public TaskGroup Clone()
    {
        var copy = new TaskGroup
        {
            Name = _summaryGroup.Name + " copy",
            MonitorDelay = _summaryGroup.MonitorDelay,
            RetryDelay = _summaryGroup.RetryDelay,
            ErrorDelay = _summaryGroup.ErrorDelay,
            Timeout = _summaryGroup.Timeout,
            CheckoutLimit = _summaryGroup.CheckoutLimit,
            ProfileLimit = _summaryGroup.ProfileLimit,
            Pinned = _summaryGroup.Pinned,
        };

        foreach (var task in _summaryGroup.Tasks)
            copy.Tasks.Add(new BotTask
            {
                Name = task.Name,
                Store = task.Store,
                Product = task.Product,
                GroupId = copy.Id,
                MonitorDelay = task.MonitorDelay,
                RetryDelay = task.RetryDelay,
                Timeout = task.Timeout,
            });

        _services.Config.TaskGroups.Add(copy);
        _services.Config.Save();
        return copy;
    }

    /// <summary>Deletes this group from the configuration (bound as <c>Delete</c>). False when it was not there.</summary>
    public bool Delete()
    {
        if (!_services.Config.TaskGroups.Remove(_summaryGroup)) return false;

        _services.Config.Save();
        return true;
    }

''' + anchor
assert anchor in t and 'public TaskGroup Clone()' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('GroupSummary gains Edit / Clone / Delete')
