import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''    /// <summary>The group on screen.</summary>
    public TaskGroup? SelectedGroup => _group;'''
add = '''    /// <summary>The group on screen.</summary>
    public TaskGroup? SelectedGroup => _group;

    // ------------------------------------------------ bound commands (R227)
    //
    // The original's compiled XAML binds these names on TaskView (analysis/xaml_bindings.json). Several were already
    // reachable as buttons or row-menu items; the names are what a rebinding, a keybind or the window's own automation
    // can address, so they exist here as commands that call the same code the buttons call.

    /// <summary>Tasks the selection (bound as <c>StartSelected</c>).</summary>
    public void StartSelected() => _grid?.StartSelectedTasks();

    /// <summary>Stops everything running (bound as <c>StopAll</c>).</summary>
    public void StopAll() => _grid?.StopSelectedTasks();

    /// <summary>Duplicates the selection (bound as <c>CloneSelected</c>).</summary>
    public void CloneSelected() => _grid?.CloneSelectedTasks();

    /// <summary>Removes the selection (bound as <c>DeleteSelected</c>).</summary>
    public void DeleteSelected() => _grid?.DeleteSelectedTasks();

    /// <summary>
    /// Copies the product URL of the first selected task (bound as <c>CopyUrl</c>). Returns false when there is nothing
    /// to copy or no clipboard is reachable, so a caller can tell "copied an empty string" from "did not copy".
    /// </summary>
    public bool CopyUrl(Action<string>? copyToClipboard = null)
    {
        var task = _grid?.FirstSelectedTask;
        var url = task?.Product;
        if (string.IsNullOrWhiteSpace(url)) return false;

        var target = copyToClipboard ?? ClipboardWriter;
        if (target is null) return false;

        target(url);
        _status.Text = "Copied " + url;
        return true;
    }

    /// <summary>Moves the group picker to the next group (bound as <c>NextGroup</c>).</summary>
    public bool NextGroup() => CycleGroup(+1);

    /// <summary>Moves the group picker to the previous group (bound as <c>PreviousGroup</c>).</summary>
    public bool PreviousGroup() => CycleGroup(-1);

    /// <summary>Sets the table's filter query (bound as <c>SetQuery</c>).</summary>
    public void SetQuery(string? query)
    {
        _search.Text = query ?? string.Empty;
        _grid?.SetFilter(query);
    }

    /// <summary>Where <see cref="CopyUrl"/> writes when the caller does not supply a sink. Null in a host without a clipboard.</summary>
    public Action<string>? ClipboardWriter { get; set; }

    private bool CycleGroup(int delta)
    {
        var groups = _services.Config.TaskGroups;
        if (groups.Count == 0) return false;

        var index = _group is null ? 0 : Math.Max(0, groups.IndexOf(_group));
        var next = ((index + delta) % groups.Count + groups.Count) % groups.Count;
        _groups.SelectedIndex = next;
        _group = groups[next];
        Content = Build();
        return true;
    }'''
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('TaskView bound commands added')
