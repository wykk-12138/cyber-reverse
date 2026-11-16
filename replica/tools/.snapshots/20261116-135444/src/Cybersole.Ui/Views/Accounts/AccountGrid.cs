using Avalonia;
using System.Windows.Input;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Ui.Views;
using Cybersole.Ui.Views.Modals;

namespace Cybersole.Ui.Views.Accounts;

/// <summary>
/// The account table (Cybersole.Ui.Views.Accounts.AccountGrid).
///
/// <para>
/// R55: the accounts page was an <c>ObservableCollection&lt;string&gt;</c> rendered by a ListBox,
/// one interpolated line per account. R70 turned that into a real table and gave it a selection
/// model; this class is that table, named what the original names it.
/// </para>
///
/// <para>
/// The original's table was driven by hand in R70 and has three columns, not four:
/// <c>Accounts.Column.Email</c>, <c>.Password</c>, <c>.Added</c> — there is no Status column in
/// the locale, so the fourth column the replica had was invented. Both visible headers are
/// sortable (they carry the up/down glyph) and the password header carries an eye that reveals
/// every row at once; the row itself ends with a pencil and a bin.
/// </para>
///
/// <para>
/// The caption above the menu is <c>Accounts.SelectedOne</c> / <c>Accounts.SelectedMany</c>, and
/// the copy item switches from <c>Copy Account</c> to <c>Copy Accounts</c> with it. The original
/// ships the singular key and never uses it, which is why one selected row still reads
/// <c>1 ACCOUNTS SELECTED</c> on screen; the singular is used here.
/// </para>
/// </summary>
public sealed class AccountGrid : UserControl
{
    private readonly IList<Account> _rows;
    private readonly Action? _onChanged;

    /// <summary>
    /// The account group these rows belong to, as the model records it (bound as <c>AccountGroup</c>; the image exposes it
    /// read-only). A grid is always shown for one group, so the first row's <c>GroupId</c> is the group's; empty when the
    /// grid has no rows.
    /// </summary>
    public string AccountGroup => _rows.FirstOrDefault()?.GroupId ?? string.Empty;

    /// <summary>
    /// Whether the grid is showing an existing group's accounts (bound as <c>Edit</c>, read-only in the image). True when the
    /// grid has rows, which is when an edit makes sense.
    /// </summary>
    public bool Edit => _rows.Count > 0;

    /// <summary>
    /// <paramref name="accounts"/> is the live list, not a copy: Delete and Move have to remove
    /// from the model, and a copy would make them silently do nothing — the same defect R59 found
    /// in <c>ProxyView.WithUsageLimit</c>.
    /// </summary>
    public AccountGrid(IList<Account> accounts, Action? onChanged = null)
    {
        Add = new RelayCommand(AddCore);
        Clear = new RelayCommand(ClearCore);
        DeleteSelected = new RelayCommand(DeleteSelectedCore);
        MoveGroup = new RelayCommand(MoveGroupCore);
        OpenSettings = new RelayCommand(() => OpenSettingsCore());
        CopyAccounts = new RelayCommand(CopyAccountsCore);
        CopyPassword = new RelayCommand(CopyPasswordCore);
        _rows = accounts;
        _onChanged = onChanged;
        Content = Build();
    }

    // ---------------------------------------------------------------- state

    /// <summary>The accounts the menu acts on, in list order.</summary>
    private readonly List<Account> _selection = new();

    /// <summary>
    /// The row control behind each account, so a selection change can repaint in place. Selecting
    /// must never rebuild the tree: <c>PointerPressed</c> fires before the context menu opens, so a
    /// rebuild destroys the row that owns the menu and right-clicking produces nothing at all.
    /// </summary>
    private readonly List<(Account Account, Grid Row)> _rowVisuals = new();

    /// <summary>Where a shift+click range starts.</summary>
    private Account? _anchor;

    private bool _revealAll;
    private AccountColumn _sortColumn = AccountColumn.Email;
    private bool _sortAscending = true;

    /// <summary>The three columns the locale names, in its order.</summary>
    public enum AccountColumn
    {
        Email,
        Password,
        Added,
    }

    /// <summary>Which column the table is ordered by. Only the two named columns sort.</summary>
    public AccountColumn SortColumn => _sortColumn;

    /// <summary>Sort direction; ties go to insertion order.</summary>
    public bool SortAscending => _sortAscending;

    /// <summary>Whether every password is shown. The header eye toggles this.</summary>
    public bool RevealAll => _revealAll;

    private void Rebuild() => Content = Build();

    /// <summary>Repaints the row backgrounds without touching the tree.</summary>
    private void PaintSelection()
    {
        foreach (var (account, row) in _rowVisuals)
            row.Background = _selection.Contains(account) ? SelectionBrush : Brushes.Transparent;
    }

    /// <summary>Painted behind a selected row. Matches the original's lighter row band.</summary>
    private static readonly IBrush SelectionBrush = new SolidColorBrush(Color.Parse("#2A2E3A"));

    // ---------------------------------------------------------------- ordering

    internal void SortBy(AccountColumn column)
    {
        if (_sortColumn == column) _sortAscending = !_sortAscending;
        else
        {
            _sortColumn = column;
            _sortAscending = true;
        }

        Rebuild();
    }

    /// <summary>
    /// The accounts on screen, in display order (bound as <c>Rows</c>). Same list <see cref="Ordered"/> produces.
    /// </summary>
    public IReadOnlyList<Account> Rows => Ordered();

    /// <summary>The rows in display order. Sorting is a view concern — <see cref="_rows"/> keeps insertion order.</summary>
    internal List<Account> Ordered()
    {
        var source = string.IsNullOrWhiteSpace(_filter)
            ? _rows
            : _rows.Where(a =>
                (a.Email ?? string.Empty).Contains(_filter, StringComparison.OrdinalIgnoreCase)).ToList();

        var ordered = _sortColumn switch
        {
            AccountColumn.Added => _sortAscending
                ? source.OrderBy(a => a.Created).ThenBy(a => a.Email, StringComparer.OrdinalIgnoreCase).ToList()
                : source.OrderByDescending(a => a.Created).ThenBy(a => a.Email, StringComparer.OrdinalIgnoreCase).ToList(),
            _ => _sortAscending
                ? source.OrderBy(a => a.Email, StringComparer.OrdinalIgnoreCase).ToList()
                : source.OrderByDescending(a => a.Email, StringComparer.OrdinalIgnoreCase).ToList(),
        };
        return ordered;
    }

    /// <summary>
    /// <c>Accounts.SearchPlaceholder</c> — "Search accounts". Filters on the email only, because
    /// that is the column a person searches by, and the password is masked.
    /// </summary>
    public AccountGrid SetFilter(string? filter)
    {
        _filter = filter;
        Rebuild();
        return this;
    }

    private string? _filter;

    /// <summary>The filter in force, or null.</summary>
    public string? Filter => _filter;

    /// <summary>The glyph the sorted column shows: ↑ when ascending, ↓ when descending.</summary>
    internal string SortGlyph(AccountColumn column) =>
        _sortColumn != column ? string.Empty : _sortAscending ? "↑" : "↓";

    // ---------------------------------------------------------------- selection

    /// <summary>What the menu and the copy actions act on. Never includes removed rows.</summary>
    public IReadOnlyList<Account> SelectedAccounts
    {
        get
        {
            _selection.RemoveAll(a => !_rows.Contains(a));
            return _selection;
        }
    }

    /// <summary>Click: this row only.</summary>
    internal void SelectSingle(Account account)
    {
        _selection.Clear();
        _selection.Add(account);
        _anchor = account;
        PaintSelection();
    }

    /// <summary>Ctrl+click: add or remove one row, leaving the rest alone.</summary>
    internal void SelectToggle(Account account)
    {
        if (!_selection.Remove(account)) _selection.Add(account);
        _anchor = account;
        PaintSelection();
    }

    /// <summary>Shift+click: everything from the anchor to this row, in display order.</summary>
    internal void SelectRange(Account account)
    {
        var view = Ordered();
        var anchor = _anchor is not null && view.Contains(_anchor) ? _anchor : account;
        var from = view.IndexOf(anchor);
        var to = view.IndexOf(account);
        if (from < 0 || to < 0) return;

        _selection.Clear();
        for (var i = Math.Min(from, to); i <= Math.Max(from, to); i++) _selection.Add(view[i]);
        PaintSelection();
    }

    /// <summary>
    /// Right-click: a row already in the selection keeps the whole selection (that is how the
    /// original let you copy several at once); a row outside it becomes the selection.
    /// </summary>
    internal void SelectForMenu(Account account)
    {
        if (_selection.Contains(account)) return;
        _selection.Clear();
        _selection.Add(account);
        _anchor = account;
        PaintSelection();
    }

    /// <summary>
    /// The header checkbox. In the shipped 5.18.32 it toggles its own visual and nothing else —
    /// the three row boxes stay unchecked and the menu count does not move. It selects everything
    /// here, because a control that cannot act is not a behaviour worth matching.
    /// </summary>
    internal void SelectAll()
    {
        _selection.Clear();
        _selection.AddRange(_rows);
        _anchor = _rows.FirstOrDefault();
        Rebuild();
    }

    /// <summary>Whether every row is selected, which is what the header box reads.</summary>
    internal bool AllSelected => _rows.Count > 0 && _rows.All(_selection.Contains);

    private void HandleRowPressed(Account account, KeyModifiers modifiers)
    {
        if (modifiers.HasFlag(KeyModifiers.Shift)) SelectRange(account);
        else if (modifiers.HasFlag(KeyModifiers.Control)) SelectToggle(account);
        else SelectSingle(account);
    }

    // ---------------------------------------------------------------- menu

    /// <summary><c>Accounts.SelectedOne</c> / <c>Accounts.SelectedMany</c>.</summary>
    internal static string SelectionHeader(int count) =>
        count == 1 ? "1 ACCOUNT SELECTED" : $"{count} ACCOUNTS SELECTED";

    /// <summary>The label the copy item carries for a selection of this size.</summary>
    internal static string CopyItemLabel(int count) =>
        count == 1 ? "Copy Account" : "Copy Accounts";

    /// <summary>
    /// <c>Account:Password</c> per line, newline separated, with a terminating newline — the shape
    /// that came off the original's clipboard for one account, extended to the many case.
    /// </summary>
    internal static string FormatAccounts(IEnumerable<Account> accounts) =>
        string.Concat(accounts.Select(a => $"{a.Email}:{a.Password}\n"));

    /// <summary>
    /// <c>Accounts.DeleteConfirm.TitleFormat</c>, <c>.MessageFormat</c>, <c>.ActionFormat</c>.
    /// Returned rather than shown so the wording can be asserted without a window.
    /// </summary>
    internal static (string Title, string Message, string Action) DeleteConfirm(int count) => (
        $"Delete {count} accounts?",
        $"Are you sure you want to delete {count} accounts?\nYou cannot undo this action.",
        $"Delete ({count}) accounts");

    /// <summary>
    /// The items the menu shows for <paramref name="selection"/>. Built as a list rather than
    /// fixed at construction because the item set and the labels both depend on the count.
    /// </summary>
    internal List<object> MenuFor(IReadOnlyList<Account> selection)
    {
        var count = selection.Count;
        var items = new List<object>
        {
            // Not an action: the count is the menu's own caption.
            new MenuItem { Header = SelectionHeader(count), IsEnabled = false },
        };

        // A password is only unambiguous for one account; the original drops this item when
        // several are selected, and keeps the combined form for every count.
        if (count == 1) items.Add(Item("Copy Password", CopySelectedPassword));
        items.Add(Item(CopyItemLabel(count), CopySelectedAccount));

        if (_mover is not null) items.Add(Item("Move accounts to", MoveSelected));

        items.Add(Item("Delete Accounts", DeleteSelectedCore));
        return items;
    }

    /// <summary>Copies the selected account in <c>email:password</c> form.</summary>
    internal void CopySelectedAccount()
    {
        var selected = SelectedAccounts;
        if (selected.Count == 0) return;
        Copy(FormatAccounts(selected));
    }

    /// <summary>Copies the selected account's password. Only offered for a single selection.</summary>
    internal void CopySelectedPassword()
    {
        var selected = SelectedAccounts;
        if (selected.Count != 1) return;
        Copy(selected[0].Password);
    }

    // ------------------------------------------------ bound names (R236)
    //
    // The original binds these two on AccountGrid (analysis/xaml_bindings.json). The behaviour was already here as
    // CopySelectedAccount / CopySelectedPassword, reachable only from the row menu; the bound names are what a keybind
    // or a rebinding addresses. One implementation, two ways in.

    /// <summary>
    /// R491: the original binds <c>MoveGroup</c> / <c>OpenSettings</c> / <c>CopyAccounts</c> as **properties**
    /// (descriptor table: all three carry Getter+Setter). The behaviour was already here as methods, so each
    /// method keeps its body under a `…Core` name and the bound name becomes the command — that is what a keybind
    /// or a rebinding actually addresses.
    /// </summary>
    public ICommand MoveGroup { get; }

    /// <inheritdoc cref="MoveGroup"/>
    public ICommand OpenSettings { get; }

    /// <inheritdoc cref="MoveGroup"/>
    public ICommand CopyAccounts { get; }

    /// <inheritdoc cref="MoveGroup"/>
    public ICommand CopyPassword { get; }

    // R508: bound names observed on the original (docs/R507_ROUTE_C_WORKED.md).
    /// <summary>Opens the bulk-import dialog (was only reachable from the header Button).</summary>
    public ICommand Add { get; }

    /// <summary>Asks, then empties this group's accounts — the group itself survives.</summary>
    public ICommand Clear { get; }

    /// <summary>Deletes the ticked rows (the row menu's "Delete Accounts").</summary>
    public ICommand DeleteSelected { get; }

    private Action? _importer;

    /// <summary>Supplies the import dialog's opener.</summary>
    public AccountGrid WithImporter(Action import)
    {
        _importer = import;
        return this;
    }

    private void AddCore() => _importer?.Invoke();

    private void ClearCore()
    {
        if (_rows.Count == 0) return;
        if (TopLevel.GetTopLevel(this) is not Window host) return;

        var (title, message, action) = DeleteConfirm(_rows.Count);
        var box = new MessageBoxDialog(title, message, MessageBoxType.Warning, action, "Cancel", true, true);
        box.Closed += (_, _) =>
        {
            if (!box.Confirmed) return;
            foreach (var account in _rows.ToList()) _rows.Remove(account);
            _selection.Clear();
            Rebuild();
            _onChanged?.Invoke();
        };
        _ = box.ShowDialog(host);
    }

    /// <summary>Moves the selection to another group (behind <c>MoveGroup</c>).</summary>
    private void MoveGroupCore() => MoveSelected();

    /// <summary>Opens Settings' account page (behind <c>OpenSettings</c>).</summary>
    private bool OpenSettingsCore()
    {
        if (TopLevel.GetTopLevel(this) is not MainWindow shell) return false;
        return shell.Navigate("Settings");
    }

    /// <summary>Copies the selected accounts (behind <c>CopyAccounts</c>).</summary>
    private void CopyAccountsCore() => CopySelectedAccount();

    /// <summary>Copies the single selected account's password (behind <c>CopyPassword</c>).</summary>
    private void CopyPasswordCore() => CopySelectedPassword();

    // ---------------------------------------------------------------- actions

    private Func<Account, Task>? _mover;

    /// <summary>Asks the caller before deleting. Returns false to cancel.</summary>
    private Func<int, bool>? _confirmDelete;

    /// <summary>Supplies the "Move to" action (<c>Accounts.Context.MoveTo</c>).</summary>
    public AccountGrid WithMover(Func<Account, Task> move)
    {
        _mover = move;
        Rebuild();
        return this;
    }

    /// <summary>
    /// Supplies the <c>Accounts.DeleteConfirm</c> gate. Without one, Delete acts immediately — the
    /// dialog lives in the page because a modal needs a window.
    /// </summary>
    public AccountGrid WithDeleteConfirm(Func<int, bool> confirm)
    {
        _confirmDelete = confirm;
        return this;
    }

    /// <summary>Opens the move dialog for the whole selection.</summary>
    internal void MoveSelected()
    {
        if (_mover is null) return;
        foreach (var account in SelectedAccounts.ToList()) _ = _mover(account);
    }

    /// <summary>Removes every selected row from the caller's list.</summary>
    internal void DeleteSelectedCore()
    {
        var selected = SelectedAccounts.ToList();
        if (selected.Count == 0) return;
        if (_confirmDelete is not null && !_confirmDelete(selected.Count)) return;

        foreach (var account in selected) _rows.Remove(account);
        _selection.Clear();
        Rebuild();
        _onChanged?.Invoke();
    }

    /// <summary>Asks the caller where to send this row.</summary>
    internal void MoveAccount(Account account)
    {
        if (_mover is null) return;
        _ = _mover(account);
    }

    /// <summary>Removes one row. The row's bin button calls this.</summary>
    internal void DeleteAccount(Account account)
    {
        if (_confirmDelete is not null && !_confirmDelete(1)) return;
        if (!_rows.Remove(account)) return;
        _selection.Remove(account);
        Rebuild();
        _onChanged?.Invoke();
    }

    /// <summary>The row's pencil. Opens the caller's editor for one account.</summary>
    internal void EditAccount(Account account) => _editor?.Invoke(account);

    private Action<Account>? _editor;

    /// <summary>Supplies the row editor (<c>Accounts.EditPassword</c>).</summary>
    public AccountGrid WithEditor(Action<Account> edit)
    {
        _editor = edit;
        Rebuild();
        return this;
    }

    private Control? _headerActions;

    /// <summary>
    /// Puts buttons in the table's own header row, right of the last column.
    ///
    /// <para>
    /// R71: the original's "Add Accounts" / "Clear Accounts" sit on the column-header line, level
    /// with Email / Password / Added — not on a toolbar above it. Driving the replica showed the
    /// two rows the replica had invented; a screenshot compared side by side is what caught it.
    /// </para>
    /// </summary>
    public AccountGrid WithHeaderActions(Control actions)
    {
        _headerActions = actions;
        Rebuild();
        return this;
    }

    /// <summary>Flips every password between masked and shown.</summary>
    internal void ToggleRevealAll()
    {
        _revealAll = !_revealAll;
        Rebuild();
    }

    // ---------------------------------------------------------------- build

    /// <summary>
    /// One column template for the header and every row.
    ///
    /// <para>
    /// R71/R72: the last column was <c>Auto</c>, which sized itself to the toolbar in the header and
    /// to nothing in the rows — so the header's Email/Password/Added sat at different x positions
    /// than the cells under them. A screenshot showed it. The reserved width has to be fixed.
    /// </para>
    /// </summary>
    private const string RowColumns = "34,2*,1.4*,1.3*,88," + ActionsWidth;

    /// <summary>Width reserved for the header's buttons, in every row as well.</summary>
    // R72: 200 clipped "Clear Accounts" — two buttons side by side need the room, and the
    // reserved column is what keeps the header and the rows aligned.
    internal const string ActionsWidth = "270";

    private Control Build()
    {
        var ordered = Ordered();

        var header = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions(RowColumns),
            Margin = new Thickness(4, 0, 4, 6),
        };

        var selectAll = new CheckBox
        {
            IsChecked = AllSelected,
            VerticalAlignment = VerticalAlignment.Center,
        };
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

        header.Children.Add(HeaderButton("Email", AccountColumn.Email, 1));
        header.Children.Add(PasswordHeader());
        header.Children.Add(HeaderButton("Added", AccountColumn.Added, 3));

        if (_headerActions is not null)
        {
            _headerActions.VerticalAlignment = VerticalAlignment.Center;
            Grid.SetColumn(_headerActions, 5);
            header.Children.Add(_headerActions);
        }

        var body = new StackPanel { Spacing = 2 };
        _rowVisuals.Clear();
        foreach (var account in ordered)
            body.Children.Add(BuildRow(account));

        if (_rows.Count == 0)
        {
            body.Children.Add(new TextBlock
            {
                // Accounts.Empty.NoAccounts.Subtitle
                Text = "Add some accounts to get started",
                Opacity = 0.6,
                Margin = new Thickness(4, 8, 4, 0),
            });
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

    /// <summary>A sortable column header: the label plus the up/down glyph for the sorted column.</summary>
    private Control HeaderButton(string label, AccountColumn column, int gridColumn)
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

    /// <summary>
    /// <c>Accounts.Column.Password</c> plus the eye that reveals every row. The original puts the
    /// reveal switch in the header, not on each row.
    /// </summary>
    private Control PasswordHeader()
    {
        var panel = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 6,
            VerticalAlignment = VerticalAlignment.Center,
        };
        panel.Children.Add(new TextBlock
        {
            Text = "Password",
            FontWeight = FontWeight.SemiBold,
            VerticalAlignment = VerticalAlignment.Center,
        });

        var eye = new Button
        {
            Content = _revealAll ? "◉" : "◎",
            Background = Brushes.Transparent,
            BorderThickness = new Thickness(0),
            Padding = new Thickness(2, 0),
            VerticalAlignment = VerticalAlignment.Center,
        };
        eye.Click += (_, _) => ToggleRevealAll();
        panel.Children.Add(eye);

        Grid.SetColumn(panel, 2);
        return panel;
    }

    private Control BuildRow(Account account)
    {
        var row = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions(RowColumns),
            Margin = new Thickness(4, 3, 4, 3),
            Background = _selection.Contains(account) ? SelectionBrush : Brushes.Transparent,
        };

        var check = new CheckBox
        {
            IsChecked = _selection.Contains(account),
            VerticalAlignment = VerticalAlignment.Center,
        };
        check.IsCheckedChanged += (_, _) =>
        {
            if (check.IsChecked == true) SelectToggle(account);
            else if (_selection.Contains(account)) SelectToggle(account);
        };
        Grid.SetColumn(check, 0);
        row.Children.Add(check);

        var email = Cell(account.Email, 1);
        row.Children.Add(email);

        var password = new TextBlock
        {
            Text = _revealAll ? account.Password : Mask(account.Password),
            VerticalAlignment = VerticalAlignment.Center,
            FontFamily = new FontFamily("Consolas,monospace"),
        };
        var passwordHost = new Border { Child = password };
        // Double-tap still reveals one row; the header eye reveals them all.
        passwordHost.DoubleTapped += (_, _) =>
        {
            password.Text = password.Text == Mask(account.Password)
                ? account.Password
                : Mask(account.Password);
        };
        Grid.SetColumn(passwordHost, 2);
        row.Children.Add(passwordHost);

        // MM/dd/yyyy HH:mm:ss — the format the original prints, not an ISO date.
        row.Children.Add(Cell(
            account.Created == default ? "—" : account.Created.ToString("MM/dd/yyyy HH:mm:ss"), 3));

        var actions = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 4,
            VerticalAlignment = VerticalAlignment.Center,
        };

        var pencil = new Button
        {
            Content = "✏",
            Padding = new Thickness(6, 1),
            Background = Brushes.Transparent,
            BorderThickness = new Thickness(1),
        };
        pencil.Click += (_, _) => EditAccount(account);
        actions.Children.Add(pencil);

        var bin = new Button
        {
            Content = "🗑",
            Padding = new Thickness(6, 1),
            Background = Brushes.Transparent,
            BorderThickness = new Thickness(1),
        };
        bin.Click += (_, _) => DeleteAccount(account);
        actions.Children.Add(bin);

        Grid.SetColumn(actions, 4);
        row.Children.Add(actions);

        // R70: the row body is the selection surface, and the modifiers decide the extent. Only the
        // left button selects — a right-click opens the menu and must leave the selection alone,
        // otherwise the menu would collapse to the row under the cursor before it was ever drawn.
        row.PointerPressed += (_, e) =>
        {
            if (!e.GetCurrentPoint(row).Properties.IsLeftButtonPressed) return;
            HandleRowPressed(account, e.KeyModifiers);
        };

        // The menu is rebuilt on open so it can speak for the current selection rather than for
        // the row that happened to own the menu when the table was built.
        var menu = new ContextMenu { ItemsSource = MenuFor(new[] { account }) };
        menu.Opening += (_, _) =>
        {
            SelectForMenu(account);
            menu.ItemsSource = MenuFor(SelectedAccounts.Count > 0 ? SelectedAccounts : new[] { account });
        };
        row.ContextMenu = menu;

        _rowVisuals.Add((account, row));
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

    private static void Copy(string text)
    {
        // Avalonia's clipboard is async and needs a TopLevel; failing to copy must not throw out
        // of a menu handler, so this is fire-and-forget with a swallow.
        _ = TryCopy(text);
    }

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

    internal static string Mask(string password) =>
        string.IsNullOrEmpty(password) ? "—" : new string('•', Math.Min(password.Length, 12));

    private static Control Docked(Control control, Avalonia.Controls.Dock dock)
    {
        DockPanel.SetDock(control, dock);
        return control;
    }
}
