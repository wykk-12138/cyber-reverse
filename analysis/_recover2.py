import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()

# 1) four tabs only
t = t.replace('            new TabItem { Header = "General", Content = BuildGeneral() },\n', '', 1)
t = t.replace('            new TabItem { Header = "Manual", Content = BuildManual() },\n', '', 1)

# 2) restore Save / Reset / DeleteGroup at the end of TaskGroupView (before the class-closing brace that follows
#    BuildNotifications)
anchor = '''            UiKit.Caption("Add webhooks under Settings'''
idx = t.index(anchor)
close = t.index('\n}', idx)
restored = '''
    /// <summary>
    /// Removes this group from the configuration (bound as <c>Delete</c> — the live dialog's red button, R350).
    /// Returns false when the group was never saved.
    /// </summary>
    public bool DeleteGroup()
    {
        if (!_services.Config.TaskGroups.Remove(_group)) return false;

        _services.Config.Save();
        _status.Text = "Group deleted.";
        return true;
    }

    private void Save()
    {
        try
        {
            if (!_services.Config.TaskGroups.Contains(_group))
                _services.Config.TaskGroups.Add(_group);

            _services.Config.Save();
            _status.Text = "Group saved.";
        }
        catch (Exception ex)
        {
            _status.Text = ex.Message;
        }
    }

    /// <summary>Clears every per-group override, so the global delays and limits apply again.</summary>
    public void Reset()
    {
        _group.MonitorDelay = null;
        _group.RetryDelay = null;
        _group.ErrorDelay = null;
        _group.Timeout = null;
        _group.CheckoutLimit = null;
        _group.ProfileLimit = null;
        _status.Text = "Overrides cleared.";
    }'''
t = t[:close] + restored + t[close:]

# 3) the reconstructed details view, appended after the last class
details = '''
/// <summary>
/// Read-only detail for one task (Cybersole.Ui.Views.Tasks.Modals.TaskDetailsView).
///
/// <para>
/// The image binds exactly two members here: <c>Task</c> and <c>Close</c>. This body was <b>reconstructed in R352</b> after
/// a bad line-splice deleted the original; it shows only fields the task grid and editor already carry.
/// </para>
/// </summary>
public sealed class TaskDetailsView : UserControl
{
    /// <summary>The task on screen (bound as <c>Task</c>).</summary>
    public BotTask Task { get; }

    private readonly TextBlock _status = UiKit.Status();

    /// <summary>Closes the hosting window (bound as <c>Close</c>). False when there is nothing to close.</summary>
    public bool Close()
    {
        if (TopLevel.GetTopLevel(this) is not Window host) return false;

        host.Close();
        return true;
    }

    public TaskDetailsView(AppServices services, BotTask task)
    {
        Task = task;

        Content = new StackPanel
        {
            Spacing = 8,
            Children =
            {
                UiKit.Title(Task.Name),
                UiKit.Section("Task",
                    UiKit.Row("Store", new TextBlock { Text = Task.Store ?? "-" }),
                    UiKit.Row("Product", new TextBlock { Text = Task.Product?.Name ?? "-" }),
                    UiKit.Row("Profile", new TextBlock { Text = Task.Profile?.Name ?? "-" }),
                    UiKit.Row("Proxy group", new TextBlock { Text = Task.ProxyGroup?.Name ?? "-" }),
                    UiKit.Row("Status", new TextBlock { Text = Task.State.ToString() })),
                UiKit.Buttons(UiKit.Button("Close", () => Close())),
                _status,
            },
        };
    }
}
'''
t = t.rstrip('\n') + '\n' + details
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('tabs=4, Save/Reset/DeleteGroup restored, details view appended')
