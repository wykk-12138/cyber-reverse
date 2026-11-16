using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Common;

namespace Cybersole.Ui.Views.Proxies;

/// <summary>
/// The proxy table (Cybersole.Ui.Views.Proxies.ProxyGrid).
///
/// <para>
/// R56 turned the proxies page from an interpolated string list into a table; R72 gives it the
/// shape the original actually has. Driving the live 5.18.32 by hand:
/// </para>
///
/// <code>
/// [☐]  IP ⇅     Port ⇅     Username ⇅     Status ⇅     [Add Proxies][Clear All][More]
/// </code>
///
/// <para>
/// Four columns, every one of them sortable. The replica carried a fifth, <c>Usage</c>, which is
/// not a column in the locale (<c>Proxies.Column.IP</c>, <c>.Port</c>, <c>.Username</c>,
/// <c>.Status</c> — and nothing else). Usage still governs <c>Proxies.More.ClearOver</c>; it is
/// simply not printed.
/// </para>
///
/// <para>
/// The toolbar is on the header line and the checkbox selects everything, the same two findings
/// R70/R71 made on the accounts table — the three tables are one component in the original, so
/// they are one shape here.
/// </para>
/// </summary>
public sealed class ProxyGrid : UserControl
{
    /// <summary>The sortable columns, in the order the live page shows them (R332).</summary>
    internal static readonly string[] Headers = { "IP", "Port", "Username", "Status" };

    /// <summary>The same columns as sort keys, positionally aligned with <see cref="Headers"/>.</summary>
    private static readonly ProxyColumn[] HeaderColumns =
    {
        ProxyColumn.Ip, ProxyColumn.Port, ProxyColumn.Username, ProxyColumn.Status,
    };

    private readonly IList<Proxy> _rows;
    private readonly Action? _onChanged;

    /// <summary>
    /// <paramref name="proxies"/> is the live list, not a copy: "Clear Failed" and "Clear Over"
    /// have to remove from the model, and a copy would make them silently do nothing.
    /// </summary>
    public ProxyGrid(IList<Proxy> proxies, Action? onChanged = null)
    {
        _rows = proxies;
        _onChanged = onChanged;
        Content = Build();
    }

    // ---------------------------------------------------------------- state

    private readonly List<Proxy> _selection = new();
    private readonly List<(Proxy Proxy, Grid Row)> _rowVisuals = new();
    private Proxy? _anchor;

    private ProxyColumn _sortColumn = ProxyColumn.Ip;
    private bool _sortAscending = true;
    private string? _filter;

    /// <summary>The four columns the locale names, in its order.</summary>
    public enum ProxyColumn
    {
        Ip,
        Port,
        Username,
        Status,
    }

    public ProxyColumn SortColumn => _sortColumn;
    public bool SortAscending => _sortAscending;
    public string? Filter => _filter;

    /// <summary>Painted behind a selected row. Same band as the accounts table.</summary>
    private static readonly IBrush SelectionBrush = new SolidColorBrush(Color.Parse("#2A2E3A"));

    private void Rebuild() => Content = Build();

    private void PaintSelection()
    {
        foreach (var (proxy, row) in _rowVisuals)
            row.Background = _selection.Contains(proxy) ? SelectionBrush : Brushes.Transparent;
    }

    // ---------------------------------------------------------------- ordering

    internal void SortBy(ProxyColumn column)
    {
        if (_sortColumn == column) _sortAscending = !_sortAscending;
        else
        {
            _sortColumn = column;
            _sortAscending = true;
        }

        Rebuild();
    }

    /// <summary>The rows in display order; the model list keeps insertion order.</summary>
    internal List<Proxy> Ordered()
    {
        var source = string.IsNullOrWhiteSpace(_filter)
            ? _rows.ToList()
            : _rows.Where(p => (p.Address ?? string.Empty).Contains(_filter, StringComparison.OrdinalIgnoreCase)
                            || (p.Username ?? string.Empty).Contains(_filter, StringComparison.OrdinalIgnoreCase))
                   .ToList();

        Func<Proxy, IComparable> key = _sortColumn switch
        {
            ProxyColumn.Port => p => p.Port,
            ProxyColumn.Username => p => p.Username ?? string.Empty,
            ProxyColumn.Status => p => p.Status.Text,
            _ => p => p.Host,
        };

        return (_sortAscending ? source.OrderBy(key) : source.OrderByDescending(key)).ToList();
    }

    /// <summary>The glyph the sorted column shows: ↑ when ascending, ↓ when descending.</summary>
    internal string SortGlyph(ProxyColumn column) =>
        _sortColumn != column ? string.Empty : _sortAscending ? "↑" : "↓";

    /// <summary>Filters by address or username. <c>Proxies</c> has no search key of its own; the
    /// page's box is the same "Search groups"-style field.</summary>
    public ProxyGrid SetFilter(string? filter)
    {
        _filter = filter;
        Rebuild();
        return this;
    }

    // ---------------------------------------------------------------- selection

    public IReadOnlyList<Proxy> SelectedProxies
    {
        get
        {
            _selection.RemoveAll(p => !_rows.Contains(p));
            return _selection;
        }
    }

    internal void SelectSingle(Proxy proxy)
    {
        _selection.Clear();
        _selection.Add(proxy);
        _anchor = proxy;
        PaintSelection();
    }

    internal void SelectToggle(Proxy proxy)
    {
        if (!_selection.Remove(proxy)) _selection.Add(proxy);
        _anchor = proxy;
        PaintSelection();
    }

    internal void SelectRange(Proxy proxy)
    {
        var view = Ordered();
        var anchor = _anchor is not null && view.Contains(_anchor) ? _anchor : proxy;
        var from = view.IndexOf(anchor);
        var to = view.IndexOf(proxy);
        if (from < 0 || to < 0) return;

        _selection.Clear();
        for (var i = Math.Min(from, to); i <= Math.Max(from, to); i++) _selection.Add(view[i]);
        PaintSelection();
    }

    internal void SelectForMenu(Proxy proxy)
    {
        if (_selection.Contains(proxy)) return;
        _selection.Clear();
        _selection.Add(proxy);
        _anchor = proxy;
        PaintSelection();
    }

    /// <summary>The header checkbox. The original's is decorative; this one selects.</summary>
    internal void SelectAll()
    {
        _selection.Clear();
        _selection.AddRange(_rows);
        _anchor = _rows.FirstOrDefault();
        Rebuild();
    }

    internal bool AllSelected => _rows.Count > 0 && _rows.All(_selection.Contains);

    // ---------------------------------------------------------------- captions

    /// <summary>
    /// <c>Proxies.LoadedNone</c> / <c>.LoadedOne</c> / <c>.LoadedFormat</c> — three forms, and the
    /// original really does show "No Proxies Loaded" rather than "0 Proxies Loaded". The accounts
    /// page has no zero form, which is a difference between the two pages and not an oversight.
    /// </summary>
    internal static string LoadedCaption(int count) => count switch
    {
        0 => "No Proxies Loaded",
        1 => "1 Proxy Loaded",
        _ => $"{count} Proxies Loaded",
    };

    /// <summary><c>Proxies.SelectedOne</c> / <c>.SelectedMany</c>.</summary>
    internal static string SelectionHeader(int count) =>
        count == 1 ? "1 PROXY SELECTED" : $"{count} PROXIES SELECTED";

    /// <summary>
    /// The group's traffic line. The original prints two labelled counters,
    /// <c>Proxies.CurrentDownload</c> and <c>.CurrentUpload</c>, with "0 B" when nothing has moved.
    /// </summary>
    internal static string TrafficCaption(long bytes) =>
        bytes < 1024 ? $"{bytes} B"
        : bytes < 1024 * 1024 ? $"{bytes / 1024.0:0.#} KB"
        : $"{bytes / (1024.0 * 1024.0):0.#} MB";

    /// <summary><c>Proxies.More.ClearOverFormat</c> = "Clear {0} Proxies".</summary>
    internal static string ClearOverCaption(int count) => $"Clear {count} Proxies";

    // ---------------------------------------------------------------- actions

    private Func<Proxy, Task>? _tester;
    private Func<Proxy, Task>? _mover;
    private int? _limit;

    /// <summary>Supplies the per-row test action (<c>Proxies.More.TestOn</c>).</summary>
    public ProxyGrid WithTester(Func<Proxy, Task> test)
    {
        _tester = test;
        Rebuild();
        return this;
    }

    /// <summary>Supplies the "Move to" action (<c>Proxies.Context.MoveTo</c>).</summary>
    public ProxyGrid WithMover(Func<Proxy, Task> move)
    {
        _mover = move;
        Rebuild();
        return this;
    }

    /// <summary>
    /// Sets the usage ceiling "Clear Over" compares against. Rebuilds, because the buttons were
    /// already built and this changes what they act on (R59).
    /// </summary>
    public ProxyGrid WithUsageLimit(int? limit)
    {
        _limit = limit;
        Rebuild();
        return this;
    }

    internal void TestProxy(Proxy proxy)
    {
        if (_tester is null) return;
        _ = _tester(proxy);
    }

    internal void CloneProxy(Proxy proxy)
    {
        var copy = proxy.Clone();
        copy.GroupId = proxy.GroupId;
        _rows.Add(copy);
        Rebuild();
        _onChanged?.Invoke();
    }

    internal void MoveProxy(Proxy proxy)
    {
        if (_mover is null) return;
        _ = _mover(proxy);
    }

    internal void DeleteProxy(Proxy proxy)
    {
        if (!_rows.Remove(proxy)) return;
        _selection.Remove(proxy);
        Rebuild();
        _onChanged?.Invoke();
    }

    /// <summary>Removes every selected row.</summary>
    internal void DeleteSelected()
    {
        var doomed = SelectedProxies.ToList();
        if (doomed.Count == 0) return;

        foreach (var proxy in doomed) _rows.Remove(proxy);
        _selection.Clear();
        Rebuild();
        _onChanged?.Invoke();
    }

    /// <summary>Copies the selected rows, one <c>host:port</c> per line.</summary>
    internal void CopySelected()
    {
        var selected = SelectedProxies;
        if (selected.Count == 0) return;
        Copy(string.Concat(selected.Select(p => p.Address + "\n")));
    }

    /// <summary>
    /// Removes every proxy whose status is not a success. <c>Proxies.More.ClearFailed</c>.
    /// </summary>
    internal void ClearFailed()
    {
        var doomed = _rows.Where(p => string.Equals(p.Status.Text, "Failed", StringComparison.Ordinal)).ToList();
        if (doomed.Count == 0) return;

        foreach (var proxy in doomed) _rows.Remove(proxy);
        Rebuild();
        _onChanged?.Invoke();
    }

    /// <summary>How many rows "Clear Over" would remove, so the menu can say the number.</summary>
    internal int OverLimitCount()
    {
        var limit = _limit;
        return limit is null or <= 0 ? 0 : _rows.Count(p => p.Usage >= limit.Value);
    }

    /// <summary>
    /// Removes every proxy that has been used at least as many times as the group allows.
    /// <c>Proxies.More.ClearOverFormat</c> = "Clear {0} Proxies".
    /// </summary>
    internal void ClearOver()
    {
        var limit = _limit;
        if (limit is null or <= 0) return;

        var doomed = _rows.Where(p => p.Usage >= limit.Value).ToList();
        if (doomed.Count == 0) return;

        foreach (var proxy in doomed) _rows.Remove(proxy);
        Rebuild();
        _onChanged?.Invoke();
    }

    // ---------------------------------------------------------------- menu

    /// <summary>The items the menu shows for <paramref name="selection"/>.</summary>
    internal List<object> MenuFor(IReadOnlyList<Proxy> selection)
    {
        var count = selection.Count;
        var items = new List<object>
        {
            new MenuItem { Header = SelectionHeader(count), IsEnabled = false },
        };

        items.Add(Item("Copy Proxies", CopySelected));

        if (_tester is not null && count == 1)
            items.Add(Item("Test Proxies", () => TestProxy(selection[0])));

        if (count == 1) items.Add(Item("Clone Proxies", () => CloneProxy(selection[0])));
        if (_mover is not null) items.Add(Item("Move proxies to", () => MoveSelected()));

        items.Add(Item("Delete Proxies", DeleteSelected));
        return items;
    }

    internal void MoveSelected()
    {
        if (_mover is null) return;
        foreach (var proxy in SelectedProxies.ToList()) _ = _mover(proxy);
    }

    private Control? _headerActions;

    /// <summary>Puts buttons in the table's own header row, right of the last column.</summary>
    public ProxyGrid WithHeaderActions(Control actions)
    {
        _headerActions = actions;
        Rebuild();
        return this;
    }

    // ---------------------------------------------------------------- build

    /// <summary>
    /// One column template for the header and every row.
    ///
    /// <para>
    /// R72: the last column used to be <c>Auto</c>, which sized itself to the toolbar in the header
    /// and to nothing in the rows — so the header said IP/Port/Username/Status at one set of x
    /// positions and the cells landed at another. A screenshot showed it. The two grids have to
    /// reserve the same fixed width.
    /// </para>
    /// </summary>
    private const string RowColumns = "34,1.6*,0.9*,1.5*,1.2*," + ActionsWidth;

    /// <summary>Width reserved for the header's buttons, in every row as well.</summary>
    internal const string ActionsWidth = "300";

    private Control Build()
    {
        var header = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions(RowColumns),
            Margin = new Thickness(4, 0, 4, 6),
        };

        var selectAll = new CheckBox { IsChecked = AllSelected, VerticalAlignment = VerticalAlignment.Center };
        selectAll.IsCheckedChanged += (_, _) =>
        {
            if (selectAll.IsChecked == true) SelectAll();
            else
            {
                _selection.Clear();
                PaintSelection();
            }
        };
        Grid.SetColumn(selectAll, 0);
        header.Children.Add(selectAll);

        // R333: one array drives the row, so the order the live page shows (R332) is data and testable.
        for (var i = 0; i < Headers.Length; i++)
            header.Children.Add(HeaderButton(Headers[i], HeaderColumns[i], i + 1));

        if (_headerActions is not null)
        {
            _headerActions.VerticalAlignment = VerticalAlignment.Center;
            Grid.SetColumn(_headerActions, 5);
            header.Children.Add(_headerActions);
        }

        var body = new StackPanel { Spacing = 2 };
        _rowVisuals.Clear();
        var ordered = Ordered();
        foreach (var proxy in ordered)
            body.Children.Add(BuildRow(proxy));

        if (_rows.Count == 0)
        {
            // R209: Empty.Nothing.Title + Proxies.Empty.Subtitle now live in the shared EmptyView.
            var empty = EmptyView.For("proxies");
            empty.Margin = new Thickness(0, 60, 0, 0);
            body.Children.Add(empty);
        }

        return new DockPanel
        {
            LastChildFill = true,
            Children =
            {
                Docked(header, Avalonia.Controls.Dock.Top),
                new ScrollViewer { Content = body },
            },
        };
    }

    private Control HeaderButton(string label, ProxyColumn column, int gridColumn)
    {
        var glyph = SortGlyph(column);
        var button = new Button
        {
            Content = new TextBlock
            {
                Text = glyph.Length == 0 ? label : $"{label} {glyph}",
                FontWeight = FontWeight.SemiBold,
                VerticalAlignment = VerticalAlignment.Center,
            },
            Background = Brushes.Transparent,
            BorderThickness = new Thickness(0),
            Padding = new Thickness(4, 0),
            HorizontalAlignment = HorizontalAlignment.Left,
            HorizontalContentAlignment = HorizontalAlignment.Left,
        };
        button.Click += (_, _) => SortBy(column);

        Grid.SetColumn(button, gridColumn);
        return button;
    }

    private Control BuildRow(Proxy proxy)
    {
        var row = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions(RowColumns),
            Margin = new Thickness(4, 3, 4, 3),
            Background = _selection.Contains(proxy) ? SelectionBrush : Brushes.Transparent,
        };

        var check = new CheckBox
        {
            IsChecked = _selection.Contains(proxy),
            VerticalAlignment = VerticalAlignment.Center,
        };
        check.IsCheckedChanged += (_, _) =>
        {
            if (check.IsChecked == true) SelectToggle(proxy);
            else if (_selection.Contains(proxy)) SelectToggle(proxy);
        };
        Grid.SetColumn(check, 0);
        row.Children.Add(check);

        row.Children.Add(Cell(proxy.Host, 1));
        row.Children.Add(Cell(proxy.Port.ToString(), 2));
        row.Children.Add(Cell(string.IsNullOrEmpty(proxy.Username) ? "—" : proxy.Username!, 3));

        // R66: was proxy.Status.ToString(), which printed the type name. Status.Text is the pill's
        // own label.
        row.Children.Add(Cell(proxy.Status.Text, 4));

        row.PointerPressed += (_, e) =>
        {
            if (!e.GetCurrentPoint(row).Properties.IsLeftButtonPressed) return;
            if (e.KeyModifiers.HasFlag(KeyModifiers.Shift)) SelectRange(proxy);
            else if (e.KeyModifiers.HasFlag(KeyModifiers.Control)) SelectToggle(proxy);
            else SelectSingle(proxy);
        };

        var menu = new ContextMenu { ItemsSource = MenuFor(new[] { proxy }) };
        menu.Opening += (_, _) =>
        {
            SelectForMenu(proxy);
            menu.ItemsSource = MenuFor(SelectedProxies.Count > 0 ? SelectedProxies : new[] { proxy });
        };
        row.ContextMenu = menu;

        _rowVisuals.Add((proxy, row));
        return row;
    }

    private static TextBlock Cell(string text, int column)
    {
        var block = new TextBlock
        {
            Text = text,
            VerticalAlignment = VerticalAlignment.Center,
            TextTrimming = TextTrimming.CharacterEllipsis,
        };
        Grid.SetColumn(block, column);
        return block;
    }

    private static MenuItem Item(string header, Action action)
    {
        var item = new MenuItem { Header = header };
        item.Click += (_, _) => action();
        return item;
    }

    private static void Copy(string text) => _ = TryCopy(text);

    private static async Task TryCopy(string text)
    {
        try
        {
            var window = (Application.Current?.ApplicationLifetime as
                Avalonia.Controls.ApplicationLifetimes.IClassicDesktopStyleApplicationLifetime)
                ?.MainWindow;
            if (window?.Clipboard is { } clipboard) await clipboard.SetTextAsync(text);
        }
        catch
        {
            // no clipboard, no window, or the platform refused — the menu closes either way
        }
    }

    private static Control Docked(Control control, Avalonia.Controls.Dock dock)
    {
        DockPanel.SetDock(control, dock);
        return control;
    }
}
