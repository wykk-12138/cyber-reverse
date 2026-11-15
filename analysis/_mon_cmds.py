import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\MonitorWindow.cs'
t = io.open(p, encoding='utf-8').read()

old = '''        var root = new DockPanel { LastChildFill = true, Margin = new Thickness(10) };
        DockPanel.SetDock(bar, Dock.Top);
        root.Children.Add(bar);
        root.Children.Add(_stream);
        Content = root;
        UpdateSummary();'''
new = '''        var root = new DockPanel { LastChildFill = true, Margin = new Thickness(10) };
        DockPanel.SetDock(bar, Dock.Top);
        root.Children.Add(bar);
        root.Children.Add(_stream);

        // R234: the original binds ShowMonitor / ShowSmartActions / ShowUtilities on this window, which is only possible
        // if the window holds all three panes. The replica had the request stream alone.
        _tabs = new TabControl
        {
            Items =
            {
                new TabItem { Header = "Monitor", Content = root },
                new TabItem { Header = "Smart Actions", Content = new SmartActions.SmartActionsView(_services) },
                new TabItem { Header = "Utilities", Content = new Utilities.UtilitiesView(_services) },
            },
        };

        Content = _tabs;
        UpdateSummary();'''
assert old in t
t = t.replace(old, new, 1)

anchor = '''    private bool Matches(HttpRequestEvent e)'''
add = '''    // ------------------------------------------------ bound commands (R234)

    private readonly TabControl? _tabs;

    /// <summary>Shows the request stream (bound as <c>ShowMonitor</c>).</summary>
    public void ShowMonitor() => Select(0);

    /// <summary>Shows the smart-actions pane (bound as <c>ShowSmartActions</c>).</summary>
    public void ShowSmartActions() => Select(1);

    /// <summary>Shows the utilities pane (bound as <c>ShowUtilities</c>).</summary>
    public void ShowUtilities() => Select(2);

    /// <summary>Minimises the window (bound as <c>Minimise</c>).</summary>
    public void Minimise() => WindowState = WindowState.Minimized;

    /// <summary>Closes the window (bound as <c>Exit</c>).</summary>
    public void Exit() => Close();

    /// <summary>Which pane is showing; 0 Monitor, 1 Smart Actions, 2 Utilities.</summary>
    public int Pane => _tabs?.SelectedIndex ?? 0;

    private void Select(int index)
    {
        if (_tabs is null) return;
        _tabs.SelectedIndex = index;
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('MonitorWindow is a three-pane shell now')
