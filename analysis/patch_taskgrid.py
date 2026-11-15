import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Tasks\TaskGrid.cs"
t = io.open(p, encoding="utf-8").read()

# Cell becomes an instance method so the status column can prefer the live runtime state.
old_static = '''    /// <summary>What a cell prints. One place, so sorting and rendering cannot disagree.</summary>
    internal static string Cell(BotTask task, TaskColumn column) => column switch
    {
        TaskColumn.Product => string.IsNullOrWhiteSpace(task.Product?.Name) ? "—" : task.Product!.Name,
        TaskColumn.Profile => string.IsNullOrWhiteSpace(task.ProfileId) ? "—" : task.ProfileId!,
        TaskColumn.Proxies => string.IsNullOrWhiteSpace(task.ProxyGroupId) ? "—" : task.ProxyGroupId!,
        TaskColumn.Status => string.IsNullOrWhiteSpace(task.State.ToString()) ? "—" : task.State.ToString(),
        _ => string.IsNullOrWhiteSpace(task.Store) ? "—" : task.Store,
    };'''

new_instance = '''    /// <summary>
    /// What a cell prints. One place, so sorting and rendering cannot disagree.
    ///
    /// <para>
    /// The status column prefers <see cref="WithStatus"/>'s live value over the persisted
    /// <see cref="BotTask.State"/>: two states exist — the one that only settles when a run ends,
    /// and the one the engine is in right now — and printing the persisted one left a running task
    /// saying Idle (found on the old page, kept fixed here).
    /// </para>
    /// </summary>
    internal string Cell(BotTask task, TaskColumn column) => column switch
    {
        TaskColumn.Product => string.IsNullOrWhiteSpace(task.Product?.Name) ? "—" : task.Product!.Name,
        TaskColumn.Profile => string.IsNullOrWhiteSpace(task.ProfileId) ? "—" : task.ProfileId!,
        TaskColumn.Proxies => string.IsNullOrWhiteSpace(task.ProxyGroupId) ? "—" : task.ProxyGroupId!,
        TaskColumn.Status => (_statusOf?.Invoke(task) ?? task.State).ToString(),
        _ => string.IsNullOrWhiteSpace(task.Store) ? "—" : task.Store,
    };

    private Func<BotTask, TaskState>? _statusOf;

    /// <summary>Supplies the live state for a task, when the engine has one.</summary>
    public TaskGrid WithStatus(Func<BotTask, TaskState> statusOf)
    {
        _statusOf = statusOf;
        Rebuild();
        return this;
    }'''

if old_static not in t:
    raise SystemExit("Cell anchor missing")
t = t.replace(old_static, new_instance, 1)

# The row renderer used the static overload; point it at the instance one.
t = t.replace("""    private static TextBlock Cell(BotTask task, TaskColumn column, int gridColumn)""",
              """    private TextBlock DataCell(BotTask task, TaskColumn column, int gridColumn)""", 1)
t = t.replace("row.Children.Add(Cell(task, TaskColumn.Site, 1));", "row.Children.Add(DataCell(task, TaskColumn.Site, 1));", 1)
t = t.replace("row.Children.Add(Cell(task, TaskColumn.Product, 2));", "row.Children.Add(DataCell(task, TaskColumn.Product, 2));", 1)
t = t.replace("row.Children.Add(Cell(task, TaskColumn.Profile, 3));", "row.Children.Add(DataCell(task, TaskColumn.Profile, 3));", 1)
t = t.replace("row.Children.Add(Cell(task, TaskColumn.Proxies, 4));", "row.Children.Add(DataCell(task, TaskColumn.Proxies, 4));", 1)
t = t.replace("row.Children.Add(Cell(task, TaskColumn.Status, 5));", "row.Children.Add(DataCell(task, TaskColumn.Status, 5));", 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("TaskGrid: Cell is an instance method with a live-status hook")
