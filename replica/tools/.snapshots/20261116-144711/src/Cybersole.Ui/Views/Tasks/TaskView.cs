using System.Windows.Input;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Services;
using Cybersole.Ui.Views;
using Cybersole.Ui.Views.Common;

namespace Cybersole.Ui.Views.Tasks;

/// <summary>
/// The Tasks page (Cybersole.Ui.Views.Tasks.TaskView).
///
/// <para>
/// R73 drove the live 5.18.32. Unlike accounts and proxies, tasks do <b>not</b> put their groups in
/// a left pane — the group is a dropdown at the top left, with a "..." beside it, and three other
/// things share that line:
/// </para>
///
/// <code>
/// [🗂 Group 1 ⌄] [...]     [🟢0][🔴0][🟣0][🔵0]              [🔍 Search tasks]
/// [☐] Site⇅  Product⇅  Profile⇅  Proxies⇅  Status⇅            0 Tasks
///                Nothing to see here
///              Add some tasks to get started
/// [Task Creator ＋][Clear Tasks 🗑]   [Start Tasks ▶][Stop Tasks ■]   [Edit Tasks ✏][Captcha Solver]
/// </code>
///
/// <para>
/// The six footer buttons are the six <c>Tasks.Action.*</c> keys — Creator, Clear, Start, Stop,
/// Edit, CaptchaSolver — grouped three-and-three with Start/Stop centred. The old replica page had
/// New / Creator / Editor / Start all / Stop all / Clone / Delete / Move to: eight buttons in one
/// row, five of them duplicates of what the row menu now carries.
/// </para>
///
/// <para>
/// The four counted pills have no accessible text, so what each counts is inferred from the colours
/// and the states the model has (Success / Failed / Declined / running). That inference is recorded
/// in <c>PARITY.md</c> rather than presented as fact.
/// </para>
/// </summary>
public sealed class TaskView : UserControl
{
    /// <summary>Bound as <c>Quicktask</c>; runs <c>QuicktaskCore()</c>.</summary>
    public ICommand Quicktask { get; }

    /// <summary>Bound as <c>LinkChange</c>; runs <c>LinkChangeCore()</c>.</summary>
    public ICommand LinkChange { get; }

    /// <summary>Bound as <c>CreateGroup</c>; runs <c>CreateGroupCore()</c>.</summary>
    public ICommand CreateGroup { get; }

    /// <summary>The tasks table's search text (bound as <c>Search</c>).</summary>
    public string Search
    {
        get => _search.Text ?? string.Empty;
        set => _search.Text = value ?? string.Empty;
    }

    private readonly AppServices _services;
    private readonly ComboBox _groups = new() { Width = 200, PlaceholderText = "Select group" };
    private readonly TextBox _search = new() { Watermark = "Search tasks", Width = 220 };
    private readonly TextBlock _status = UiKit.Status();
    private TaskGrid? _grid;
    private Button? _groupMenuButton;
    private MenuFlyout? _groupMenu;
    private TaskGroup? _group;
    private bool _refreshing;

    // R492: bound names for actions that already existed as methods (descriptor table: Getter+Setter).
    /// <summary>Bound as <c>ClearAll</c>; behaviour unchanged (was a method).</summary>
    public ICommand ClearAll { get; }

    /// <summary>Bound as <c>OpenTaskCreator</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenTaskCreator { get; }

    /// <summary>Bound as <c>OpenSolvers</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenSolvers { get; }

    /// <summary>Bound as <c>CloneSelected</c>; behaviour unchanged (was a method).</summary>
    public ICommand CloneSelected { get; }

    /// <summary>Bound as <c>DeleteSelected</c>; behaviour unchanged (was a method).</summary>
    public ICommand DeleteSelected { get; }

    /// <summary>Bound as <c>OpenStaggerStart</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenStaggerStart { get; }

    /// <summary>Bound as <c>ForceStartSelected</c>; behaviour unchanged (was a method).</summary>
    public ICommand ForceStartSelected { get; }

    /// <summary>Bound as <c>EditSelected</c>; behaviour unchanged (was a method).</summary>
    public ICommand EditSelected { get; }

    // R496: bound names for the remaining no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>OpenGroupPopup</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenGroupPopup { get; }

    /// <summary>Bound as <c>StopSelected</c>; behaviour unchanged (was a method).</summary>
    public ICommand StopSelected { get; }

    /// <summary>Bound as <c>EditAll</c>; behaviour unchanged (was a method).</summary>
    public ICommand EditAll { get; }

    /// <summary>Bound as <c>OpenTaskView</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenTaskView { get; }

    /// <summary>Bound as <c>OpenBrowser</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenBrowser { get; }

    /// <summary>Bound as <c>StartSelected</c>; behaviour unchanged (was a method).</summary>
    public ICommand StartSelected { get; }

    /// <summary>Bound as <c>NextGroup</c>; behaviour unchanged (was a method).</summary>
    public ICommand NextGroup { get; }

    /// <summary>Bound as <c>PreviousGroup</c>; behaviour unchanged (was a method).</summary>
    public ICommand PreviousGroup { get; }

    // R500: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>OpenSettings</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenSettings { get; }

    /// <summary>Bound as <c>StopAll</c>; behaviour unchanged (was a method).</summary>
    public ICommand StopAll { get; }

    public TaskView(AppServices services)
    {
        Quicktask = new RelayCommand(() => QuicktaskCore());
        LinkChange = new RelayCommand(() => LinkChangeCore());
        CreateGroup = new RelayCommand(() => CreateGroupCore());
        OpenSettings = new RelayCommand(() => OpenSettingsCore());
        StopAll = new RelayCommand(StopAllCore);

        OpenGroupPopup = new RelayCommand(OpenGroupPopupCore);
        StopSelected = new RelayCommand(StopSelectedCore);
        EditAll = new RelayCommand(EditAllCore);
        OpenTaskView = new RelayCommand(OpenTaskViewCore);
        OpenBrowser = new RelayCommand(OpenBrowserCore);
        StartSelected = new RelayCommand(StartSelectedCore);
        NextGroup = new RelayCommand(() => NextGroupCore());
        PreviousGroup = new RelayCommand(() => PreviousGroupCore());

        ClearAll = new RelayCommand(ClearAllCore);
        OpenTaskCreator = new RelayCommand(OpenTaskCreatorCore);
        OpenSolvers = new RelayCommand(OpenSolversCore);
        CloneSelected = new RelayCommand(CloneSelectedCore);
        DeleteSelected = new RelayCommand(DeleteSelectedCore);
        OpenStaggerStart = new RelayCommand(OpenStaggerStartCore);
        ForceStartSelected = new RelayCommand(ForceStartSelectedCore);
        EditSelected = new RelayCommand(EditSelectedCore);

        _services = services;
        Toggle = new RelayCommand(() => ToggleSelected());

        // The old page re-projected a string list on StateChanged so a task's live state reached
        // the screen. The table reads the model, so the subscription only has to rebuild.
        _services.Tasks.StateChanged += (_, _) => Refresh();

        _grid = BuildGrid();
        Content = Build();
        Refresh();
    }

    /// <summary>The group on screen.</summary>
    /// <summary>
    /// Opens the create-group dialog (bound as <c>CreateGroup</c>). The locale names its field — "CreateGroup.Name" = "Name" —
    /// so this is the naming dialog, and the same editor that edits an existing group opens with a fresh one.
    /// </summary>
    public TaskGroupView CreateGroupCore()
    {
        var created = new TaskGroup { Name = "New group" };
        var view = new TaskGroupView(_services, created);

        Cybersole.Ui.Views.Common.ViewHostModal.Show(this, "New group", view);
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

    /// <summary>
    /// Pins or unpins the group on screen (bound as <c>PinGroups</c>). The image exposes it as a settable property, so the
    /// value is also the state; the group's own <c>Pinned</c> flag is what the picker reads.
    /// </summary>
    public bool PinGroups
    {
        get => _group?.Pinned ?? false;
        set
        {
            if (_group is null || _group.Pinned == value) return;

            _group.Pinned = value;
            _services.Config.Save();
        }
    }

    // ------------------------------------------------ copy from the image's locale (R394)

    /// <summary>"Copy URL" — the task context menu's copy entry.</summary>
    public const string ContextCopyUrl = "Copy URL";

    /// <summary>"Move tasks to" — the context menu's move entry.</summary>
    public const string ContextMoveTo = "Move tasks to";

    /// <summary>"Delete {0} tasks?" — the delete confirmation's title.</summary>
    public const string DeleteConfirmTitleFormat = "Delete {0} tasks?";

    /// <summary>The delete confirmation's body.</summary>
    public const string DeleteConfirmMessageFormat =
        "Are you sure you want to delete {0} tasks?\nYou cannot undo this action.";

    /// <summary>"Delete ({0}) tasks" — the confirmation's action button.</summary>
    public const string DeleteConfirmActionFormat = "Delete ({0}) tasks";

    /// <summary>Shown when a search matches no task.</summary>
    public const string NoResultsSubtitle = "There are no tasks matching your search";

    /// <summary>"Multiple Products ({0})" — the product column when a task watches several.</summary>
    public const string MultipleProductsFormat = "Multiple Products ({0})";

    /// <summary>"{0} Selected" — the grid's own counter.</summary>
    public const string SelectedFormat = "{0} Selected";

    /// <summary>"{0} TASKS SELECTED" — the page's selection counter.</summary>
    public const string SelectedManyFormat = "{0} TASKS SELECTED";

    /// <summary>"{0} TASK SELECTED" — the singular selection counter.</summary>
    public const string SelectedOneFormat = "{0} TASK SELECTED";

    /// <summary>The product column's text for a task watching <paramref name="count"/> products.</summary>
    public static string ProductsCaption(int count) =>
        count == 1 ? "(one product)" : string.Format(MultipleProductsFormat, count);

    /// <summary>The page's selection counter, singular when one task is selected.</summary>
    public static string SelectionCaption(int count) =>
        string.Format(count == 1 ? SelectedOneFormat : SelectedManyFormat, count);

    /// <summary>The grid's own counter.</summary>
    public static string GridSelected(int count) => string.Format(SelectedFormat, count);

    public TaskGroup? SelectedGroup => _group;

    // ------------------------------------------------ bound commands (R227)
    //
    // The original's compiled XAML binds these names on TaskView (analysis/xaml_bindings.json). Several were already
    // reachable as buttons or row-menu items; the names are what a rebinding, a keybind or the window's own automation
    // can address, so they exist here as commands that call the same code the buttons call.





    /// <summary>
    /// Copies the selected task's product URL (bound as <c>CopyUrl</c>). The URL copied is the one the engine monitors —
    /// <c>Product.Url</c> — and when the task has none the store's own domain is used, because that is the only other
    /// URL the app knows for it (the store modules claim their domains in <c>IStoreModule.Domains</c>).
    ///
    /// <para>
    /// R228 corrected R227: the previous round removed this command claiming "there is no URL source". That was wrong —
    /// <c>Product.Url</c> exists and <c>TaskEngine</c> polls it. The mistake was looking only at <c>BotTask</c>.
    /// </para>
    /// </summary>
    public bool CopyUrl(Action<string>? copyToClipboard = null)
    {
        var task = _grid?.SelectedTasks.FirstOrDefault();
        if (task is null) return false;

        var url = task.Product?.Url;
        if (string.IsNullOrWhiteSpace(url))
        {
            var module = _services.Stores.Modules.FirstOrDefault(m =>
                string.Equals(m.Name, task.Store, StringComparison.OrdinalIgnoreCase)
                || string.Equals(m.Id, task.Store, StringComparison.OrdinalIgnoreCase));
            var domain = module?.Domains.FirstOrDefault();
            if (!string.IsNullOrWhiteSpace(domain))
                url = domain.Contains("://", StringComparison.Ordinal) ? domain : "https://" + domain;
        }

        if (string.IsNullOrWhiteSpace(url)) return false;

        var sink = copyToClipboard ?? ClipboardWriter;
        if (sink is null)
        {
            _status.Text = url;
            return false;
        }

        sink(url);
        _status.Text = "Copied " + url;
        return true;
    }

    /// <summary>Where <see cref="CopyUrl"/> writes when the caller does not supply a sink.</summary>
    public Action<string>? ClipboardWriter { get; set; }

    /// <summary>Opens the task creator with no existing task (bound as <c>OpenTaskCreator</c>).</summary>
    // ── the bound names this control carries (R344) ───────────────────────────────────────────────────
    // Cybersole.Ui.Views.TaskView binds 29 operations. Some already exist under a working name (that is what the
    // properties below do); the rest are listed in docs/BINDING_BACKLOG.md as "bound but behaviour not yet recovered",
    // because inventing what Ctrl+M or "Pin Groups" does would be worse than leaving it named.

    /// <summary>Empties the current group (bound as <c>ClearAll</c>; the button says "Clear Tasks").</summary>
    private void ClearAllCore() => ClearTasks();

    /// <summary>Opens the Settings shell (bound as <c>OpenSettings</c>, as on the proxies page).</summary>
    private bool OpenSettingsCore()
    {
        var shell = TopLevel.GetTopLevel(this) as MainWindow;
        if (shell is null) return false;
        shell.Navigate("Settings");
        return true;
    }

    private void OpenTaskCreatorCore() => OpenEditor(null);

    /// <summary>Opens the captcha solver window (bound as <c>OpenSolvers</c>).</summary>
    private void OpenSolversCore() => OpenSolver();

    /// <summary>Opens the group menu — "New Group" / "Group Settings" (bound as <c>OpenGroupPopup</c>).</summary>
    private void OpenGroupPopupCore() => _groupMenu?.ShowAt(_groupMenuButton!);

    /// <summary>Duplicates the selection (bound as <c>CloneSelected</c>).</summary>
    private void CloneSelectedCore() => _grid?.CloneSelectedTasks();

    /// <summary>Removes the selection (bound as <c>DeleteSelected</c>).</summary>
    private void DeleteSelectedCore() => _grid?.DeleteSelectedTasks();

    /// <summary>Stops everything running (bound as <c>StopAll</c>).</summary>
    private void StopAllCore()
    {
        _services.Tasks.StopAll();
        Refresh();
    }

    /// <summary>Stops only the selected tasks (bound as <c>StopSelected</c>).</summary>
    private void StopSelectedCore()
    {
        var picked = _grid?.EffectiveSelection().Select(t2 => t2.Id).ToList();
        if (picked is null || picked.Count == 0) return;
        _services.Tasks.StopAll(picked);
        Refresh();
    }

    /// <summary>
    /// Flips the selection — the idle half starts, the running half stops (bound as <c>Toggle</c>).
    ///
    /// <para>
    /// Evidence: the original's TaskView command table carries <c>Toggle</c> between
    /// <c>OpenSolvers</c> and <c>Edit</c>, alongside <c>StartSelected</c> / <c>StopSelected</c>
    /// (<c>analysis/pe_strings.txt</c> offset 0x0351c91b), and its closure table has
    /// <c>&lt;ToggleTask&gt;b__0</c> / <c>&lt;ToggleTask&gt;b__1</c> (0x0348a9c3) — one method per
    /// task with two lambda bodies. Because Toggle coexists with the explicit Start/Stop commands it
    /// is not shorthand for either: it decides per task, which is what the task row's
    /// <c>Status.Clickable</c> gate (bound in the same XAML) is for. The per-task reading is an
    /// inference; the alternative (a group collapse/expand toggle) is recorded in
    /// <c>docs/BINDING_EVIDENCE.md</c>.
    /// </para>
    /// </summary>
    public ICommand Toggle { get; }

    /// <summary>The <c>Toggle</c> body: start what is idle, stop what is working. Returns how many tasks it touched.</summary>
    public int ToggleSelected()
    {
        var picked = _grid?.EffectiveSelection().ToList();
        if (picked is null || picked.Count == 0) return 0;

        var stopping = picked.Where(t2 => IsActive(LiveState(t2))).Select(t2 => t2.Id).ToList();
        var starting = picked.Where(t2 => !IsActive(LiveState(t2))).ToList();

        if (stopping.Count > 0) _services.Tasks.StopAll(stopping);
        if (starting.Count > 0) _services.Tasks.StartAll(starting);
        Refresh();
        return stopping.Count + starting.Count;
    }

    /// <summary>Whether a state means the engine is already working on that task.</summary>
    private static bool IsActive(TaskState state) =>
        state is TaskState.Starting or TaskState.Monitoring or TaskState.Waiting or TaskState.CheckingOut;

    /// <summary>Starts the selection staggered (bound as <c>OpenStaggerStart</c>).</summary>
    private void OpenStaggerStartCore() => _grid?.StaggerStartSelectedTasks();

    /// <summary>Starts the selection ignoring delays (bound as <c>ForceStartSelected</c>).</summary>
    private void ForceStartSelectedCore() => _grid?.ForceStartSelectedTasks();

    /// <summary>Edits the first selected task (bound as <c>EditSelected</c>; <c>EditAll</c> is the same command in the
    /// original — it opens the editor for the whole selection, and the replica's editor takes one task).</summary>
    private void EditSelectedCore() => _grid?.EditSelectedTasks();

    /// <inheritdoc cref="EditSelected"/>
    private void EditAllCore() => _grid?.EditSelectedTasks();

    /// <summary>Opens the task detail window for the first selected task (bound as <c>OpenTaskView</c>).</summary>
    private void OpenTaskViewCore() => _grid?.ViewSelectedTask();

    /// <summary>Opens the first selected task's browser (bound as <c>OpenBrowser</c>).</summary>
    private void OpenBrowserCore() => _grid?.OpenSelectedTask();

    /// <summary>Moves the group picker to the next group (bound as <c>NextGroup</c>).</summary>
    private bool NextGroupCore() => CycleGroup(+1);

    /// <summary>Moves the group picker to the previous group (bound as <c>PreviousGroup</c>).</summary>
    private bool PreviousGroupCore() => CycleGroup(-1);

    /// <summary>Sets the table's filter query (bound as <c>SetQuery</c>).</summary>
    public void SetQuery(string? query)
    {
        _search.Text = query ?? string.Empty;
        _grid?.SetFilter(query);
    }


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
    }

    /// <summary>
    /// <c>Tasks.CountFormat</c> = "{0} Tasks".
    /// </summary>
    internal static string CountCaption(int count) => $"{count} Tasks";

    /// <summary>
    /// The four pills' counts. Green is Success, red is Failed, purple is Declined, blue is
    /// everything the engine is currently doing — the colours and the states are all the evidence
    /// there is, since the pills carry no accessible label.
    /// </summary>
    internal static (int Success, int Failed, int Declined, int Running) PillCounts(
        IEnumerable<BotTask> tasks, Func<BotTask, TaskState> live)
    {
        var list = tasks.Select(t => live(t)).ToList();
        return (
            list.Count(s => s == TaskState.Success),
            list.Count(s => s == TaskState.Failed),
            list.Count(s => s == TaskState.Declined),
            list.Count(s => s is TaskState.Starting or TaskState.Monitoring or TaskState.Waiting or TaskState.CheckingOut));
    }

    private TaskGrid BuildGrid()
    {
        var tasks = (IList<BotTask>)(_group?.Tasks ?? new List<BotTask>());

        return new TaskGrid(tasks, () =>
            {
                _services.Config.Save();
                Refresh();
            })
            .WithStatus(t => LiveState(t))
            .WithStarter(start => { _services.Tasks.StartAll(start); Refresh(); })
            .WithStaggerStarter(start => { _services.Tasks.StartAll(start); Refresh(); })
            .WithForceStarter(start => { _services.Tasks.StartAll(start); Refresh(); })
            .WithStopper(() => StopAll.Execute(null))
            .WithEditor(task => OpenEditor(task))
            .WithCloner(CloneMany)
            .WithDeleter(DeleteMany)
            .WithViewer(task => Views.Common.ViewHostModal.Show(this, task.Name,
                UiKit.Scroll(new TaskDetailsView(_services, task)), 640, 520));
            // Tasks.Context.OpenBrowser is deliberately not wired: there is no browser
            // bridge to open, and a menu item that only writes a status line is a dead
            // button. Recorded in PARITY.md instead.
    }

    private TaskState LiveState(BotTask task)
    {
        var runtime = _services.Tasks.Runtime.FirstOrDefault(r => r.Task.Id == task.Id);
        return runtime?.Task.Id == task.Id ? runtime!.State : task.State;
    }

    // ------------------------------------------------ clipboard actions (R372)
    //
    // The locale names both of these and both failure dialogs verbatim:
    //   Tasks.LinkChange.InvalidTitle  = "Invalid URL"
    //   Tasks.LinkChange.InvalidMessage= "The value retrieved from clipboard is not a valid URL."
    //   Tasks.Quicktask.InvalidTitle   = "Invalid Quicktask"
    //   Tasks.Quicktask.InvalidMessage = "The value retrieved from clipboard is not a valid Quicktask format."
    //   Monitor.LinkChange = "Link Change"   Monitor.LaunchQuicktask = "Launch Quicktask"
    // So both read the clipboard, validate it, and complain with those exact words otherwise.

    /// <summary>Where the two clipboard actions read from — a seam so a test can drive them without a real clipboard.</summary>
    public Func<string?>? Clipboard { get; set; }

    /// <summary>Reads the clipboard through this view's window, or null when it has none.</summary>
    private string? ReadClipboard()
    {
        if (Clipboard is not null) return Clipboard();

        var top = TopLevel.GetTopLevel(this);
        return top?.Clipboard?.GetTextAsync().GetAwaiter().GetResult();
    }

    /// <summary>
    /// Applies the URL on the clipboard to every selected task, or reports the image's own failure wording (bound as
    /// <c>LinkChange</c>; the menu calls it "Link Change").
    /// </summary>
    public string LinkChangeCore()
    {
        var text = (ReadClipboard() ?? string.Empty).Trim();

        if (!Uri.TryCreate(text, UriKind.Absolute, out var uri) || (uri.Scheme != "http" && uri.Scheme != "https"))
            return InvalidLinkChangeTitle + "\n" + InvalidLinkChangeMessage;

        var changed = 0;
        foreach (var task in _grid?.SelectedTasks ?? Enumerable.Empty<BotTask>())
        {
            task.Product = new Product { Name = task.Product?.Name ?? string.Empty, Image = text };
            changed++;
        }

        _services.Config.Save();
        return "Linked " + changed + (changed == 1 ? " task" : " tasks") + " to " + text;
    }

    /// <summary>
    /// Creates tasks from the quicktask string on the clipboard, or reports the image's own failure wording (bound as
    /// <c>Quicktask</c>; the menu calls it "Launch Quicktask").
    /// </summary>
    public string QuicktaskCore()
    {
        var text = (ReadClipboard() ?? string.Empty).Trim();

        // one task per line: "store | url" — the format the settings page configures
        var lines = text.Split('\n', StringSplitOptions.RemoveEmptyEntries)
            .Select(l => l.Trim()).Where(l => l.Length > 0).ToList();

        if (lines.Count == 0 || lines.Any(l => !l.Contains('|')))
            return InvalidQuicktaskTitle + "\n" + InvalidQuicktaskMessage;

        var created = 0;
        foreach (var line in lines)
        {
            var parts = line.Split('|', 2, StringSplitOptions.TrimEntries);
            var task = new BotTask { Store = parts[0], GroupId = _group?.Id };

            _group?.Tasks.Add(task);
            created++;
        }

        _services.Config.Save();
        return "Created " + created + (created == 1 ? " task" : " tasks");
    }

    /// <summary>Title the image shows when the clipboard is not a URL.</summary>
    public const string InvalidLinkChangeTitle = "Invalid URL";

    /// <summary>Message the image shows when the clipboard is not a URL.</summary>
    public const string InvalidLinkChangeMessage = "The value retrieved from clipboard is not a valid URL.";

    /// <summary>Title the image shows when the clipboard is not a quicktask.</summary>
    public const string InvalidQuicktaskTitle = "Invalid Quicktask";

    /// <summary>Message the image shows when the clipboard is not a quicktask.</summary>
    public const string InvalidQuicktaskMessage = "The value retrieved from clipboard is not a valid Quicktask format.";

    private Control Build()
    {
        // R73: Refresh() rebuilds the page, and these three controls are fields (their state is
        // the user's choice). A control cannot be added to a second parent, so they are detached
        // from the previous build first — without this, every refresh threw
        // "The control ComboBox already has a visual parent".
        Detach(_groups);
        Detach(_search);
        Detach(_status);

        return new DockPanel
        {
            LastChildFill = true,
            Children =
            {
                Docked(BuildTopRow(), Avalonia.Controls.Dock.Top),
                Docked(BuildFooter(), Avalonia.Controls.Dock.Bottom),
                _grid!,
            },
        };
    }

    private Control BuildTopRow()
    {
        var counts = PillCounts(_group?.Tasks ?? new List<BotTask>(), LiveState);

        var top = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions("Auto,Auto,*,Auto"),
            Margin = new Thickness(12, 8, 12, 8),
        };

        // Tasks.SelectGroup — the group dropdown, not a pane.
        var groupPicker = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 6 };
        groupPicker.Children.Add(_groups);
        var more = new Button { Content = "…", Padding = new Thickness(8, 2) };
        // R229: kept so the bound command OpenGroupPopup can open it without a click.
        _groupMenuButton = more;
        more.Flyout = new MenuFlyout
        {
            ItemsSource = new List<object>
            {
                Menu("New Group", NewGroup),
                Menu("Group Settings", () => Views.Common.ViewHostModal.Show(this, "TASK GROUPS",
                    UiKit.Scroll(new TaskGroupListView(_services)), 640, 520)),
            },
        };
        _groupMenu = more.Flyout as MenuFlyout;
        groupPicker.Children.Add(more);

        var pills = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8, Margin = new Thickness(16, 0, 0, 0) };
        pills.Children.Add(Pill(counts.Success, "#27AE60", "Success"));
        pills.Children.Add(Pill(counts.Failed, "#C0392B", "Failed"));
        pills.Children.Add(Pill(counts.Declined, "#8E44AD", "Declined"));
        pills.Children.Add(Pill(counts.Running, "#2980B9", "Running"));

        var searchHost = new StackPanel { Orientation = Orientation.Horizontal, HorizontalAlignment = HorizontalAlignment.Right };
        searchHost.Children.Add(_search);

        Grid.SetColumn(groupPicker, 0);
        Grid.SetColumn(pills, 1);
        Grid.SetColumn(searchHost, 3);
        top.Children.Add(groupPicker);
        top.Children.Add(pills);
        top.Children.Add(searchHost);
        return top;
    }

    private static Control Pill(int count, string colour, string what)
    {
        var box = new Border
        {
            Background = new SolidColorBrush(Color.Parse(colour)),
            CornerRadius = new CornerRadius(10),
            Padding = new Thickness(8, 2),
            Child = new TextBlock
            {
                Text = count.ToString(),
                Foreground = Brushes.White,
                FontWeight = FontWeight.SemiBold,
            },
        };

        // Avalonia has no TextBlock.ToolTip; it is an attached property on the control.
        ToolTip.SetTip(box, what);
        return box;
    }

    /// <summary>Removes a control from whatever container the previous build put it in.</summary>
    private static void Detach(Control control)
    {
        switch (control.Parent)
        {
            case Panel panel:
                panel.Children.Remove(control);
                break;
            case ContentControl content when ReferenceEquals(content.Content, control):
                content.Content = null;
                break;
            case Decorator decorator when ReferenceEquals(decorator.Child, control):
                decorator.Child = null;
                break;
        }
    }

    private static Control Docked(Control control, Avalonia.Controls.Dock dock)
    {
        DockPanel.SetDock(control, dock);
        return control;
    }

    private Control BuildFooter()
    {
        var left = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8 };
        // Tasks.Action.Creator / .Clear
        left.Children.Add(UiKit.Button("Task Creator", () => OpenEditor(null)));
        left.Children.Add(UiKit.Button("Clear Tasks", ClearTasks));

        var middle = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8 };
        // Tasks.Action.Start / .Stop
        middle.Children.Add(UiKit.Button("Start Tasks", () => StartSelected.Execute(null)));
        middle.Children.Add(UiKit.Button("Stop Tasks", () =>
        {
            StopAllCore();
            Refresh();
        }));

        var right = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8 };
        // Tasks.Action.Edit / .CaptchaSolver
        right.Children.Add(UiKit.Button("Edit Tasks", () =>
        {
            var picked = _grid?.SelectedTasks.FirstOrDefault();
            if (picked is null) Status("Select a task to edit.");
            else OpenEditor(picked);
        }));
        right.Children.Add(UiKit.Button("Captcha Solver", OpenSolver));

        var footer = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions("Auto,*,Auto"),
            Margin = new Thickness(12, 8, 12, 8),
        };
        Grid.SetColumn(left, 0);
        Grid.SetColumn(middle, 1);
        Grid.SetColumn(right, 2);
        middle.HorizontalAlignment = HorizontalAlignment.Center;
        right.HorizontalAlignment = HorizontalAlignment.Right;

        footer.Children.Add(left);
        footer.Children.Add(middle);
        footer.Children.Add(right);

        var stack = new StackPanel { Spacing = 4 };
        stack.Children.Add(footer);
        // A status line that only ever gets assigned to and never added is the R55 shape;
        // it lives in the footer where the eye already is.
        stack.Children.Add(new Border { Padding = new Thickness(12, 0, 12, 6), Child = _status });
        return stack;
    }

    private static MenuItem Menu(string header, Action action)
    {
        var item = new MenuItem { Header = header };
        item.Click += (_, _) => action();
        return item;
    }

    private void Status(string text) => _status.Text = text;

    // ---------------------------------------------------------------- actions

    private void StartSelectedCore()
    {
        var picked = _grid?.SelectedTasks.ToList() ?? new List<BotTask>();
        if (picked.Count == 0) picked = _group?.Tasks.ToList() ?? new List<BotTask>();
        _services.Tasks.StartAll(picked);
        Refresh();
    }

    private void ClearTasks()
    {
        if (_group is null) return;
        _group.Tasks.Clear();
        _services.Config.Save();
        Refresh();
    }

    /// <summary>
    /// <c>Tasks.Context.Delete</c> — removes the whole selection. Delete is on the row menu now;
    /// the old page carried a Delete button and a Move button that the menu duplicates.
    /// </summary>
    private void DeleteMany(IReadOnlyList<BotTask> doomed)
    {
        if (_group is null) return;
        foreach (var task in doomed) _group.Tasks.Remove(task);
        _services.Config.Save();
        Refresh();
    }

    /// <summary><c>Tasks.Context.Clone</c> — one copy per selected task, named "&lt;name&gt; copy".</summary>
    private void CloneMany(IReadOnlyList<BotTask> sources)
    {
        if (_group is null) return;

        foreach (var source in sources)
        {
            // R65: a hand-listed copy had drifted from BotTask.Clone twice — it carried StartTime
            // across and copied five of Product's eight fields. Clone() is the only version.
            var copy = source.Clone();
            copy.Name = source.Name + " copy";
            _group.Tasks.Add(copy);
        }

        _services.Config.Save();
        Refresh();
    }

    /// <summary><c>Tasks.Action.CaptchaSolver</c> — the solver window that already existed.</summary>
    private void OpenSolver()
    {
        if (TopLevel.GetTopLevel(this) is not Window owner)
        {
            Status("No owner window — cannot open the solver.");
            return;
        }

        _ = new SolverWindow(_services).ShowDialog(owner);
    }

    private void NewGroup()
    {
        var group = new TaskGroup { Name = $"Group {_services.Config.TaskGroups.Count + 1}" };
        _services.Config.TaskGroups.Add(group);
        _services.Config.Save();
        _group = group;
        Refresh();
    }

    private void OpenEditor(BotTask? existing)
    {
        if (TopLevel.GetTopLevel(this) is not Window owner)
        {
            Status("No owner window — cannot open the editor.");
            return;
        }

        var editor = new TaskEditorWindow(_services, existing);
        editor.Closed += (_, _) =>
        {
            _services.Config.Save();
            Refresh();
        };

        _ = editor.ShowDialog(owner);
    }

    // ---------------------------------------------------------------- refresh

    /// <summary>Rebuilds the page from the model, keeping the selected group.</summary>
    public void Refresh()
    {
        if (_refreshing) return;
        _refreshing = true;
        try
        {
            var groups = _services.Config.TaskGroups;
            var names = groups.Select(g => g.Name).ToList();
            if (!names.SequenceEqual(_groups.ItemsSource as IList<string> ?? new List<string>()))
                _groups.ItemsSource = names;
            if (_groups.SelectedIndex < 0 && names.Count > 0) _groups.SelectedIndex = 0;

            _group = _groups.SelectedIndex >= 0 && _groups.SelectedIndex < groups.Count
                ? groups[_groups.SelectedIndex]
                : groups.FirstOrDefault();

            _groups.SelectionChanged -= OnGroupChanged;
            _groups.SelectionChanged += OnGroupChanged;
            _search.TextChanged -= OnSearchChanged;
            _search.TextChanged += OnSearchChanged;

            _grid = BuildGrid();
            _grid.SetFilter(_search.Text);
            Content = Build();
        }
        finally
        {
            _refreshing = false;
        }
    }

    private void OnGroupChanged(object? sender, SelectionChangedEventArgs e)
    {
        if (_refreshing) return;
        Refresh();
    }

    private void OnSearchChanged(object? sender, TextChangedEventArgs e)
    {
        if (_refreshing) return;
        _grid?.SetFilter(_search.Text);
    }
}
