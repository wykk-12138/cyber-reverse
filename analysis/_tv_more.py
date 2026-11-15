import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs'
t = io.open(p, encoding='utf-8').read()

# the private StartSelected already delegates to the service; point the whole bound family at the grid's new names
anchor = '''    /// <summary>Moves the group picker to the next group (bound as <c>NextGroup</c>).</summary>'''
add = '''    /// <summary>Starts the selection staggered (bound as <c>OpenStaggerStart</c>).</summary>
    public void OpenStaggerStart() => _grid?.StaggerStartSelectedTasks();

    /// <summary>Starts the selection ignoring delays (bound as <c>ForceStartSelected</c>).</summary>
    public void ForceStartSelected() => _grid?.ForceStartSelectedTasks();

    /// <summary>Edits the first selected task (bound as <c>EditSelected</c>; <c>EditAll</c> is the same command in the
    /// original — it opens the editor for the whole selection, and the replica's editor takes one task).</summary>
    public void EditSelected() => _grid?.EditSelectedTasks();

    /// <inheritdoc cref="EditSelected"/>
    public void EditAll() => _grid?.EditSelectedTasks();

    /// <summary>Opens the task detail window for the first selected task (bound as <c>OpenTaskView</c>).</summary>
    public void OpenTaskView() => _grid?.ViewSelectedTask();

    /// <summary>Opens the first selected task's browser (bound as <c>OpenBrowser</c>).</summary>
    public void OpenBrowser() => _grid?.OpenSelectedTask();

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('TaskView bound commands extended')
