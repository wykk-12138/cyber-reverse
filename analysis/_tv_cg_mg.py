import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>
    /// Pins or unpins the group on screen'''
add = '''    /// <summary>
    /// Opens the create-group dialog (bound as <c>CreateGroup</c>). The locale names its field — "CreateGroup.Name" = "Name" —
    /// so this is the naming dialog, and the same editor that edits an existing group opens with a fresh one.
    /// </summary>
    public TaskGroupView CreateGroup()
    {
        var created = new TaskGroup { Name = "New group" };
        var view = new TaskGroupView(_services, created);

        ViewHostModal.Show(this, "New group", view);
        return view;
    }

    /// <summary>
    /// Moves the selected tasks into another group (bound as <c>MoveGroup</c>). Returns how many moved; false cases return 0:
    /// no selection, or a group id that is not in the configuration.
    /// </summary>
    public int MoveGroup(string groupId)
    {
        var target = _services.Config.TaskGroups.FirstOrDefault(g => g.Id == groupId);
        if (target is null) return 0;

        var moved = 0;
        foreach (var task in (_grid?.SelectedTasks ?? Enumerable.Empty<BotTask>()).ToList())
        {
            foreach (var from in _services.Config.TaskGroups)
                from.Tasks.Remove(task);

            task.GroupId = target.Id;
            target.Tasks.Add(task);
            moved++;
        }

        _services.Config.Save();
        return moved;
    }

''' + anchor
assert anchor in t and 'public TaskGroupView CreateGroup()' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('CreateGroup + MoveGroup added')
