import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs'
t = io.open(p, encoding='utf-8').read()

# 1) the bound names for the three "open" commands + StopSelected, next to the ones R229 added
anchor = '''    /// <summary>Starts the selection staggered (bound as <c>OpenStaggerStart</c>).</summary>'''
add = '''    /// <summary>Opens the task creator with no existing task (bound as <c>OpenTaskCreator</c>).</summary>
    public void OpenTaskCreator() => OpenEditor(null);

    /// <summary>Opens the captcha solver window (bound as <c>OpenSolvers</c>).</summary>
    public void OpenSolvers() => OpenSolver();

    /// <summary>Opens the group menu — "New Group" / "Group Settings" (bound as <c>OpenGroupPopup</c>).</summary>
    public void OpenGroupPopup() => _groupMenu?.ShowAt(_groupMenuButton!);

    /// <summary>Stops only the selected tasks (bound as <c>StopSelected</c>).</summary>
    public void StopSelected()
    {
        var picked = _grid?.EffectiveSelection().Select(t2 => t2.Id).ToList();
        if (picked is null || picked.Count == 0) return;
        _services.Tasks.StopAll(picked);
        Refresh();
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)

# 2) keep a handle on the group menu so OpenGroupPopup can open it
old_more = '''        var more = new Button { Content = "\\u2026", Padding = new Thickness(8, 2) };
        more.Flyout = new MenuFlyout'''
old_more_actual = None
for candidate in ('var more = new Button { Content = "\u2026", Padding = new Thickness(8, 2) };',):
    if candidate in t:
        old_more_actual = candidate
        break
if old_more_actual is None:
    # fall back: locate the line that creates the group menu button
    import re
    m = re.search(r'        var more = new Button \{ Content = "[^"]*", Padding = new Thickness\(8, 2\) \};', t)
    old_more_actual = m.group(0) if m else None
assert old_more_actual, 'group menu button line not found'
new_more = (old_more_actual + '\n'
            '        // R229: kept so the bound command OpenGroupPopup can open it without a click.\n'
            '        _groupMenuButton = more;')
t = t.replace(old_more_actual, new_more, 1)

old_flyout = '''        groupPicker.Children.Add(more);'''
new_flyout = '''        _groupMenu = more.Flyout as MenuFlyout;
        groupPicker.Children.Add(more);'''
assert old_flyout in t
t = t.replace(old_flyout, new_flyout, 1)

# 3) the fields
old_fields = '''    private TaskGrid? _grid;'''
new_fields = '''    private TaskGrid? _grid;
    private Button? _groupMenuButton;
    private MenuFlyout? _groupMenu;'''
assert old_fields in t
t = t.replace(old_fields, new_fields, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('four more bound commands wired')
