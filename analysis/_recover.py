import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()

# 1) DeleteGroup back (it lived in the span that was cut)
anchor = '''    private void Save()
    {
        try'''
add = '''    /// <summary>
    /// Removes this group from the configuration (bound as <c>Delete</c> — the live dialog's red button, R350).
    /// Returns false when the group was never saved, so a caller can tell "deleted" from "nothing to delete".
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
        try'''
assert anchor in t and 'public bool DeleteGroup()' not in t
t = t.replace(anchor, add, 1)

# 2) TaskDetailsView rebuilt to its two bound members (Close, Task). The original text was destroyed by a bad
#    line-splice in R352; this version is reconstructed and says so.
details = '''
/// <summary>
/// Read-only detail for one task (Cybersole.Ui.Views.Tasks.Modals.TaskDetailsView).
///
/// <para>
/// The image binds exactly two members here: <c>Task</c> (which task) and <c>Close</c>. This body was <b>reconstructed</b>
/// in R352 after a line-splice deleted the original; it shows the fields the task grid and the editor already carry, and
/// nothing beyond what the binding table and the model can justify.
/// </para>
/// </summary>
public sealed class TaskDetailsView : UserControl
{
    /// <summary>The task on screen (bound as <c>Task</c>).</summary>
    public BotTask Task { get; }

    private readonly TextBlock _status = UiKit.Status();

    /// <summary>Closes the hosting modal (bound as <c>Close</c>). Returns false when there is nothing to close.</summary>
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
# insert before the final '}' that closes the file's last class? Put it after the last class instead.
t = t.rstrip('\n') + '\n' + details
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('TaskDetailsView reconstructed + DeleteGroup restored')
