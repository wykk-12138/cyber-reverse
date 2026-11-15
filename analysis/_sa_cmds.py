import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs'
t = io.open(p, encoding='utf-8').read()

# 1) Save becomes a bound command
t = t.replace('    private void Save()', '    public void Save()', 1)

anchor = '''    public int Step => _index;'''
add = '''    public int Step => _index;

    // ------------------------------------------------ bound commands (R230)
    //
    // The original binds nineteen members on SmartActionsCreator (analysis/xaml_bindings.json):
    //   AddAction, AddFilter, AddInput, Clone, CloseOverlay, Delete, DeleteAction, DeleteFilter, DeleteInput, DeleteParam,
    //   Exit, IsEditing, Minimise, Save, Settings, SmartAction, TimeSpans, ToggleFilterBehaviour, UseTemplate
    // The ones below have a model to stand on. The rest are listed in docs/XAML_BINDINGS.md as blocked, with the reason.

    /// <summary>True when the creator was opened on an existing action (bound as <c>IsEditing</c>).</summary>
    public bool IsEditing { get; private set; }

    /// <summary>The action being edited (bound as <c>SmartAction</c>).</summary>
    public SmartAction SmartAction => _action;

    /// <summary>Adds a filter and repaints step 2 (bound as <c>AddFilter</c>).</summary>
    public void AddFilter(SmartActionFilter filter)
    {
        _filters.Add(filter);
        _action.Filters.Add(filter);
        if (_index != 1) Navigate(1);
        else Navigate(1);
    }

    /// <summary>Removes the filter at <paramref name="index"/> (bound as <c>DeleteFilter</c>).</summary>
    public bool DeleteFilter(int index)
    {
        if (index < 0 || index >= _filters.Count) return false;
        var filter = _filters[index];
        _filters.RemoveAt(index);
        _action.Filters.Remove(filter);
        if (_index == 1) Navigate(1);
        return true;
    }

    /// <summary>Duplicates the action and opens the copy (bound as <c>Clone</c>).</summary>
    public SmartAction Clone()
    {
        var copy = new SmartAction
        {
            Name = _action.Name + " copy",
            Trigger = _action.Trigger,
            Kind = _action.Kind,
            Target = _action.Target,
            RunOnce = _action.RunOnce,
            RunInterval = _action.RunInterval,
            Notifications = _action.Notifications,
            Enabled = _action.Enabled,
        };
        foreach (var filter in _filters) copy.Filters.Add(new SmartActionFilter
        {
            Field = filter.Field, Operator = filter.Operator, Value = filter.Value,
        });

        _services.Config.SmartActions.Add(copy);
        _services.Config.Save();
        _status.Text = "Cloned to " + copy.Name;
        return copy;
    }

    /// <summary>Minimises the hosting window (bound as <c>Minimise</c>).</summary>
    public void Minimise()
    {
        if (TopLevel.GetTopLevel(this) is Window w) w.WindowState = WindowState.Minimized;
    }

    /// <summary>Closes the hosting window (bound as <c>Exit</c>).</summary>
    public void Exit()
    {
        if (TopLevel.GetTopLevel(this) is Window w) w.Close();
    }

    /// <summary>Dismisses the overlay the creator is hosted in, if any (bound as <c>CloseOverlay</c>).</summary>
    public void CloseOverlay() => Exit();'''
assert anchor in t
t = t.replace(anchor, add, 1)

# 2) the step-2 buttons go through the named commands
t = t.replace('''                UiKit.Button("New filter", () =>
                {
                    _filters.Add(new SmartActionFilter
                    {
                        Field = field.SelectedItem as string ?? "store",
                        Operator = op.SelectedItem as string ?? "equals",
                        Value = value.Text ?? string.Empty,
                    });
                    Refresh();
                }),
                UiKit.Button("Delete", () =>
                {
                    if (rows.SelectedIndex < 0 || rows.SelectedIndex >= _filters.Count) return;
                    _filters.RemoveAt(rows.SelectedIndex);
                    Refresh();
                }))));''',
'''                // R230: the buttons go through the bound commands instead of editing the list themselves
                UiKit.Button("New filter", () => AddFilter(new SmartActionFilter
                {
                    Field = field.SelectedItem as string ?? "store",
                    Operator = op.SelectedItem as string ?? "equals",
                    Value = value.Text ?? string.Empty,
                })),
                UiKit.Button("Delete", () => DeleteFilter(rows.SelectedIndex)))));''')

io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('SmartActionsCreator bound commands added')
