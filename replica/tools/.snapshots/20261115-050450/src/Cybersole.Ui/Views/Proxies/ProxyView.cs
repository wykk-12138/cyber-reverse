using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Services;
using Cybersole.Ui.Views.Common;
using System.Windows.Input;

namespace Cybersole.Ui.Views.Proxies;

/// <summary>
/// The proxies page (Cybersole.Ui.Views.Proxies.ProxyView).
///
/// <para>
/// R72 drove the live 5.18.32 and it is the same two-pane shape as accounts, with one extra
/// control and one extra caption:
/// </para>
///
/// <code>
/// PROXY GROUPS            [Custom ⌄]      [folder] Group 1 [gear]        ● 0 B  ● 0 B
/// [Search groups]                                  No Proxies Loaded      dl     ul
/// Group 1            [0]                 [☐] IP⇅ Port⇅ Username⇅ Status⇅ [Add][Clear All][More]
/// [New Group        +]                       Nothing to see here
///                                            Add some proxies to get started
/// </code>
///
/// <para>
/// Three things the replica did not have and the locale already named:
/// <c>Proxies.LoadedNone</c> ("No Proxies Loaded" — a zero form the accounts page does not have),
/// <c>Proxies.CurrentDownload</c> / <c>.CurrentUpload</c>, and the count badge beside each group
/// in the left pane.
/// </para>
///
/// <para>
/// R56–R61 had this page as one flat table over every group's proxies, with the import box and six
/// buttons above it. That is why "Clear Over" had to guess a limit: a flat list cannot say which
/// group's <c>MaxUsage</c> governs a row. Selecting a group is what makes the limit knowable.
/// </para>
/// </summary>
public sealed class ProxyView : UserControl
{
    // ------------------------------------------------ copy from the image's locale (R393)

    /// <summary>"Delete {0} proxies?" — the delete confirmation's title.</summary>
    public const string DeleteConfirmTitleFormat = "Delete {0} proxies?";

    /// <summary>The delete confirmation's body.</summary>
    public const string DeleteConfirmMessageFormat =
        "Are you sure you want to delete {0} proxies?\nYou cannot undo this action.";

    /// <summary>"Delete ({0}) proxies" — the confirmation's action button.</summary>
    public const string DeleteConfirmActionFormat = "Delete ({0}) proxies";

    /// <summary>"{0} Proxies Loaded" — the page footer.</summary>
    public const string LoadedFormat = "{0} Proxies Loaded";

    /// <summary>"{0} PROXIES SELECTED" — the selection counter.</summary>
    public const string SelectedManyFormat = "{0} PROXIES SELECTED";

    /// <summary>"{0} PROXY SELECTED" — the singular selection counter.</summary>
    public const string SelectedOneFormat = "{0} PROXY SELECTED";

    /// <summary>The footer for <paramref name="count"/> proxies.</summary>
    public static string Loaded(int count) => string.Format(LoadedFormat, count);

    /// <summary>The selection counter, singular when one proxy is selected.</summary>
    public static string SelectionCaption(int count) =>
        string.Format(count == 1 ? SelectedOneFormat : SelectedManyFormat, count);

    private readonly IList<ProxyGroup> _groups;
    private readonly Action? _onChanged;

    private ProxyGrid? _grid;
    private ProxyGroup? _selectedGroup;
    private string _groupSearch = string.Empty;
    private string _order = GroupOrder.Custom;

    /// <summary>
    /// R474: the original binds <c>Test</c> as a **property** on the proxies view. The action already exists
    /// (<see cref="TestProxies"/> tests every selected row through <c>ProxyGrid.TestProxy</c>); this only
    /// exposes it where the binding expects it.
    ///
    /// <para><c>TestAll</c> is NOT added here: it needs the grid's *whole* set, and <c>ProxyGrid</c> currently
    /// publishes only <see cref="SelectedProxies"/>. Inventing a "test all" over the selection would look
    /// right in a binding table and be wrong in use, so it stays an explicit gap (see BINDING_BACKLOG).</para>
    /// </summary>
    public ICommand Test { get; }

    // R495: bound names for actions that already existed as methods.
    /// <summary>Bound as <c>CopyProxies</c>; behaviour unchanged (was a method).</summary>
    public ICommand CopyProxies { get; }

    /// <summary>Bound as <c>CloneProxies</c>; behaviour unchanged (was a method).</summary>
    public ICommand CloneProxies { get; }

    /// <summary>Bound as <c>DeleteProxies</c>; behaviour unchanged (was a method).</summary>
    public ICommand DeleteProxies { get; }

    /// <summary>Bound as <c>OpenSettings</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenSettings { get; }

    // R500: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>TestProxies</c>; behaviour unchanged (was a method).</summary>
    public ICommand TestProxies { get; }

    public ProxyView(IList<ProxyGroup> groups, Action? onChanged = null)
    {
        TestProxies = new RelayCommand(TestProxiesCore);

        CopyProxies = new RelayCommand(CopyProxiesCore);
        CloneProxies = new RelayCommand(CloneProxiesCore);
        DeleteProxies = new RelayCommand(DeleteProxiesCore);
        OpenSettings = new RelayCommand(() => OpenSettingsCore());
        Test = new RelayCommand(TestProxiesCore);
        _groups = groups;
        _onChanged = onChanged;
        _selectedGroup = groups.FirstOrDefault();
        Content = Build();
    }

    /// <summary>
    /// <c>TaskGroups.Order.*</c> — the same six orders the task-group pane offers. The original
    /// shows "Custom" as the selected one on a fresh install.
    /// </summary>
    public static class GroupOrder
    {
        public const string Custom = "Custom";
        public const string Newest = "Newest";
        public const string Oldest = "Oldest";
        public const string Alpha = "A-Z";
        public const string Count = "Count";
        public const string Running = "Running";

        public static readonly string[] All = { Custom, Newest, Oldest, Alpha, Count, Running };
    }

    /// <summary>Orders the left pane. <c>Custom</c> keeps the configured order.</summary>
    internal static List<ProxyGroup> SortGroups(IEnumerable<ProxyGroup> groups, string order)
    {
        var list = groups.ToList();
        return order switch
        {
            GroupOrder.Newest => list.OrderByDescending(g => g.Order).ToList(),
            GroupOrder.Oldest => list.OrderBy(g => g.Order).ToList(),
            GroupOrder.Alpha => list.OrderBy(g => g.Name, StringComparer.OrdinalIgnoreCase).ToList(),
            GroupOrder.Count => list.OrderByDescending(g => g.Proxies.Count).ToList(),
            GroupOrder.Running => list.OrderByDescending(g => g.Proxies.Count(p => string.Equals(p.Status.Text, "Running", StringComparison.Ordinal))).ToList(),
            _ => list,
        };
    }

    /// <summary>The groups the left pane lists, after the search box.</summary>
    internal IReadOnlyList<ProxyGroup> VisibleGroups()
    {
        var filtered = string.IsNullOrWhiteSpace(_groupSearch)
            ? _groups
            : _groups.Where(g => g.Name.Contains(_groupSearch, StringComparison.OrdinalIgnoreCase));
        return SortGroups(filtered, _order);
    }

    /// <summary>The group on screen.</summary>
    public ProxyGroup? SelectedGroup => _selectedGroup;

    /// <summary>Selects a group and repaints.</summary>
    internal void SelectGroup(ProxyGroup? group)
    {
        _selectedGroup = group;
        Content = Build();
    }

    /// <summary>Sets the order of the left pane.</summary>
    internal void SetOrder(string order)
    {
        _order = order;
        Content = Build();
    }

    /// <summary>
    /// Rebuilds the page from the model. The caller's <c>ProxiesChanged</c> handler calls this, so
    /// an import or a test run that mutates a group shows up without the whole page being replaced.
    /// </summary>
    public void Reload() => Content = Build();

    /// <summary>The count badge the original prints beside a group name.</summary>
    internal static string CountBadge(ProxyGroup group) => group.Proxies.Count.ToString();

    // ------------------------------------------------ bound commands (R226)
    //
    // The original's compiled XAML binds these names on ProxyView:
    //   AddProxies, ClearAll, ClearFailed, ClearOver, CloneProxies, CopyProxies, CreateGroup, Delete, DeleteProxies,
    //   Groups, MoveGroup, OpenSettings, ProxyTesters, Test, TestAll, TestAllKeybind, TestProxies
    // (analysis/xaml_bindings.json). The replica had the behaviour but not the names, inside inline lambdas. A name is
    // what a rebinding, a keybind or a test can reach, so the behaviour now lives behind the original's vocabulary.

    /// <summary>Imports proxies into the selected group (bound as <c>AddProxies</c>).</summary>
    public void AddProxies(ProxyGroup group)
    {
        if (_importer is null || !_importer(group)) return;
        _onChanged?.Invoke();
        Content = Build();
    }

    /// <summary>Empties the selected group (bound as <c>ClearAll</c>).</summary>
    public void ClearAll(ProxyGroup group)
    {
        group.Proxies.Clear();
        _onChanged?.Invoke();
        Content = Build();
    }

    /// <summary>Copies the selection to the clipboard (bound as <c>CopyProxies</c>).</summary>
    private void CopyProxiesCore() => _grid?.CopySelected();

    /// <summary>Duplicates the selection in place (bound as <c>CloneProxies</c>).</summary>
    private void CloneProxiesCore()
    {
        if (_grid is null) return;
        foreach (var proxy in _grid.SelectedProxies.ToList()) _grid.CloneProxy(proxy);
        _onChanged?.Invoke();
        Content = Build();
    }

    /// <summary>
    /// Adds a group to the rail (bound as <c>CreateGroup</c>). The view is handed the live group list, so the group is
    /// created in the document the caller owns; it returns the new group so the caller can persist and select it.
    /// </summary>
    public ProxyGroup CreateGroup(string? name)
    {
        var group = new ProxyGroup
        {
            Name = string.IsNullOrWhiteSpace(name) ? $"Group {_groups.Count + 1}" : name!.Trim(),
        };
        _groups.Add(group);
        _onChanged?.Invoke();
        Content = Build();
        return group;
    }

    /// <summary>
    /// Moves the selected proxies into <paramref name="target"/> (bound as <c>MoveGroup</c>). Returns how many moved.
    /// </summary>
    public int MoveGroup(ProxyGroup target)
    {
        if (_grid is null || target is null) return 0;

        var picked = _grid.SelectedProxies.ToList();
        if (picked.Count == 0) return 0;

        foreach (var proxy in picked)
        {
            proxy.GroupId = target.Id;
            if (_mover is not null) _ = _mover(proxy, SourceGroupOf(proxy) ?? target);
        }

        _onChanged?.Invoke();
        Content = Build();
        return picked.Count;
    }

    /// <summary>Opens Settings' proxy page (bound as <c>OpenSettings</c>).</summary>
    private bool OpenSettingsCore()
    {
        if (TopLevel.GetTopLevel(this) is not MainWindow shell) return false;
        return shell.Navigate("Settings");
    }

    /// <summary>
    /// How many proxy testers run at once (bound as <c>ProxyTesters</c>). Follows the global concurrency setting when
    /// the host supplies it, otherwise reports the single tester this page drives.
    /// </summary>
    public int ProxyTesters => _testerCount ?? 1;

    private int? _testerCount;

    /// <summary>Supplies the tester count; the caller owns the setting.</summary>
    public ProxyView WithTesterCount(int count)
    {
        _testerCount = count;
        return this;
    }

    /// <summary>
    /// The chord that runs "Test All", as the settings page stores it (bound as <c>TestAllKeybind</c>). Empty when the
    /// host has no keybind set.
    /// </summary>
    public string TestAllKeybind
    {
        get => _testAllKeybind ?? string.Empty;
        set => _testAllKeybind = value;
    }

    private string? _testAllKeybind;

    private ProxyGroup? SourceGroupOf(Proxy proxy) =>
        _groups.FirstOrDefault(g => g.Id == proxy.GroupId);

    /// <summary>Removes the selection (bound as <c>DeleteProxies</c>).</summary>
    private void DeleteProxiesCore()
    {
        if (_grid is null) return;
        _grid.DeleteSelected();
        _onChanged?.Invoke();
        Content = Build();
    }

    /// <summary>Tests the selection against the echo service (bound as <c>TestProxies</c>).</summary>
    private void TestProxiesCore()
    {
        if (_grid is null) return;
        foreach (var proxy in _grid.SelectedProxies.ToList()) _grid.TestProxy(proxy);
    }

    // ---------------------------------------------------------------- hooks

    private Func<Proxy, Task>? _tester;
    private Func<Proxy, ProxyGroup, Task>? _mover;

    /// <summary>Supplies the per-row test action (<c>Proxies.Context.Test</c>).</summary>
    public ProxyView WithTester(Func<Proxy, Task> test)
    {
        _tester = test;
        Content = Build();
        return this;
    }

    /// <summary>Supplies "Move to" (<c>Proxies.Context.MoveTo</c>); the group is the source.</summary>
    public ProxyView WithMover(Func<Proxy, ProxyGroup, Task> move)
    {
        _mover = move;
        Content = Build();
        return this;
    }

    /// <summary>Supplies "Test All" (<c>Proxies.More.TestAllOn</c>).</summary>
    private Func<Task>? _testAll;

    public ProxyView WithTestAll(Func<Task> testAll)
    {
        _testAll = testAll;
        Content = Build();
        return this;
    }

    /// <summary>
    /// The per-site tester: <c>Proxies.More.TestAllOn</c> ("Test All On") over
    /// <c>Proxies.More.SelectSite</c> ("Select Site"). R58 established that a proxy which reaches
    /// ipify can still be blocked by the store, so this is the question a drop actually asks.
    /// </summary>
    private IReadOnlyList<string> _sites = Array.Empty<string>();
    private Func<string, string?>? _urlForSite;
    private Func<string?, Task>? _testOn;

    public ProxyView WithSites(IEnumerable<string> sites, Func<string, string?> urlForSite, Func<string?, Task> testOn)
    {
        _sites = sites.ToList();
        _urlForSite = urlForSite;
        _testOn = testOn;
        Content = Build();
        return this;
    }

    /// <summary>Supplies "Add Proxies" — the caller owns the document and the save.</summary>
    private Func<ProxyGroup, bool>? _importer;

    public ProxyView WithImporter(Func<ProxyGroup, bool> import)
    {
        _importer = import;
        Content = Build();
        return this;
    }

    // ---------------------------------------------------------------- build

    private Control Build()
    {
        return new DockPanel
        {
            LastChildFill = true,
            Children =
            {
                Docked(BuildLeftPane(), Avalonia.Controls.Dock.Left),
                BuildDetail(),
            },
        };
    }

    private Control BuildLeftPane()
    {
        // R210: the rail is the shared GroupGrid now. The row it draws — name left, muted count right, selected row
        // tinted, "No groups matched your search" when a filter empties the list — was hand-built here and copied into
        // two other pages; the original has it as one class.
        // R222: the rail is a fixed 324 px. Measured on the running build at window widths 1375 and 1566 — the group
        // card inside the rail spanned x 25..349 (324 px) at BOTH widths, so it is fixed, not proportional. This rail
        // had no width at all and sized itself to its content.
        var grid = new GroupGrid();
        grid.Width = RailWidth;
        grid.SetRows(
            VisibleGroups().Select(g => (g.Id, g.Name, CountBadge(g))),
            _selectedGroup?.Id,
            key => SelectGroup(_groups.FirstOrDefault(g => g.Id == key)),
            AccentBrush);

        return grid;
    }

    /// <summary>The left rail's fixed width, measured (see the comment in <see cref="BuildLeftPane"/>).</summary>
    internal const double RailWidth = 324;

    private static readonly IBrush AccentBrush = new SolidColorBrush(Color.Parse("#2A2E3A"));

    private static Control DockedRight(Control control)
    {
        Grid.SetColumn(control, 1);
        return control;
    }

    private static Control Docked(Control control, Avalonia.Controls.Dock dock)
    {
        DockPanel.SetDock(control, dock);
        return control;
    }

    private Control BuildDetail()
    {
        if (_selectedGroup is not { } group)
        {
            return new StackPanel
            {
                Margin = new Thickness(16),
                Spacing = 8,
                Children = { UiKit.Empty("Add a group to get started") },
            };
        }

        var caption = new StackPanel { Spacing = 2 };
        caption.Children.Add(new TextBlock
        {
            Text = group.Name,
            FontSize = 20,
            FontWeight = FontWeight.SemiBold,
        });
        caption.Children.Add(new TextBlock
        {
            Text = ProxyGrid.LoadedCaption(group.Proxies.Count),
            Opacity = 0.7,
        });

        var gear = new Button
        {
            Content = "⚙",
            Background = Brushes.Transparent,
            BorderThickness = new Thickness(0),
            VerticalAlignment = VerticalAlignment.Center,
            Margin = new Thickness(8, 0, 0, 0),
        };
        var target = group;
        gear.Click += (_, _) =>
        {
            ProxyGroupView.Show(this, target);
            _onChanged?.Invoke();
            Content = Build();
        };

        var title = new StackPanel { Orientation = Orientation.Horizontal };
        title.Children.Add(caption);
        title.Children.Add(gear);

        // Proxies.CurrentDownload / .CurrentUpload — two labelled counters, "0 B" when idle.
        var traffic = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 18,
            HorizontalAlignment = HorizontalAlignment.Right,
            VerticalAlignment = VerticalAlignment.Center,
            Children =
            {
                Counter(ProxyGrid.TrafficCaption(group.TotalDownload), "current download"),
                Counter(ProxyGrid.TrafficCaption(group.TotalUpload), "current upload"),
            },
        };

        var top = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto"), Margin = new Thickness(12, 8, 12, 8) };
        Grid.SetColumn(title, 0);
        Grid.SetColumn(traffic, 1);
        top.Children.Add(title);
        top.Children.Add(traffic);

        _grid = new ProxyGrid(group.Proxies, () =>
        {
            _onChanged?.Invoke();
            Content = Build();
        })
            .WithUsageLimit(group.MaxUsage)
            .WithTester(proxy => _tester?.Invoke(proxy) ?? Task.CompletedTask)
            .WithMover(proxy => _mover?.Invoke(proxy, group) ?? Task.CompletedTask);

        var add = UiKit.Button("Add Proxies", () => AddProxies(target));

        // R204: one proxy at a time, or a dropped list. The original has both paths — its creator is named in the image
        // (`ProxyCreator.DragDrop`, 0x06e5071c) and this page only had the bulk importer behind "Add Proxies".
        var create = UiKit.Button("Add One", () =>
        {
            var creator = new ProxyCreatorView();
            creator.Created += proxies =>
            {
                foreach (var proxy in proxies)
                {
                    proxy.GroupId = target.Id;
                    target.Proxies.Add(proxy);
                }
                _onChanged?.Invoke();
                Content = Build();
            };

            // the owner comes from the visual tree, the way the other modals in this project find it
            if (TopLevel.GetTopLevel(this) is Window owner)
            {
                var host = new Cybersole.Ui.Views.Common.ViewHostModal("Add Proxy", creator, 560, 460)
                {
                    WindowStartupLocation = WindowStartupLocation.CenterOwner,
                };
                _ = host.ShowDialog(owner);
            }
        });

        var clearAll = UiKit.Button("Clear All", () => ClearAll(target));

        // Proxies.Action.More — Test All / Clear Failed / Clear Over, with the counts the locale
        // prints ("Clear {0} Proxies").
        var more = new Button { Content = "More", Padding = new Thickness(14, 5) };
        var moreItems = new List<object>();
        if (_testAll is not null) moreItems.Add(MoreItem("Test All", () => _ = _testAll()));
        if (_sites.Count > 0 && _testOn is not null)
        {
            // Proxies.More.TestOn ("Test On:") over Proxies.More.SelectSite ("Select Site").
            var perSite = new List<object>();
            foreach (var site in _sites)
            {
                var chosen = site;
                perSite.Add(MoreItem(chosen, () => _ = _testOn(_urlForSite?.Invoke(chosen))));
            }

            moreItems.Add(new MenuItem
            {
                Header = "Test On:",
                ItemsSource = perSite,
            });
        }

        moreItems.Add(MoreItem("Clear Failed", () => _grid?.ClearFailed()));
        moreItems.Add(MoreItem(ProxyGrid.ClearOverCaption(_grid.OverLimitCount()), () => _grid?.ClearOver()));
        more.Flyout = new MenuFlyout { ItemsSource = moreItems };

        var actions = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            HorizontalAlignment = HorizontalAlignment.Right,
        };

        actions.Children.Add(add);
        actions.Children.Add(create);
        actions.Children.Add(clearAll);
        actions.Children.Add(more);
        _grid.WithHeaderActions(actions);

        var dock = new DockPanel { LastChildFill = true };
        DockPanel.SetDock(top, Avalonia.Controls.Dock.Top);
        dock.Children.Add(top);
        dock.Children.Add(new Border { Padding = new Thickness(12, 0, 12, 12), Child = _grid });
        return dock;
    }

    private static Control Counter(string value, string label)
    {
        var panel = new StackPanel { Spacing = 0 };
        panel.Children.Add(new TextBlock { Text = value, FontWeight = FontWeight.SemiBold });
        panel.Children.Add(new TextBlock { Text = label, Opacity = 0.6, FontSize = 11 });
        return panel;
    }

    private static MenuItem MoreItem(string header, Action action)
    {
        var item = new MenuItem { Header = header };
        item.Click += (_, _) => action();
        return item;
    }
}
