using Avalonia;
using System.Windows.Input;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Ui.Views;
using Cybersole.Ui.Views.Common;

namespace Cybersole.Ui.Views.Accounts;

/// <summary>
/// The accounts page (Cybersole.Ui.Views.Accounts.AccountView).
///
/// <para>
/// The original is two panes and a detail area, and R70 walked all of it by hand:
/// </para>
///
/// <code>
/// ACCOUNT GROUPS                    [folder] Nike US - zz-probe [gear]     [search accounts]
/// [search stores]                            3 Accounts Loaded
/// Nike                              [all] Email ⇅  Password 👁  Added ⇅   [Add][Clear]
///   Nike US                         [ ]  probe1@…  ••••••••  11/11/2026 16:29:43  [✏][🗑]
/// Nike GS                           [ ]  probe2@…  ••••••••  11/11/2026 16:29:43  [✏][🗑]
/// Shopify
/// …
/// [New Group                    +]
/// </code>
///
/// <para>
/// Two behaviours in that layout are not guessable from the layout itself:
/// </para>
///
/// <list type="number">
/// <item>clicking a platform that has no group opens <see cref="CreateGroupModal"/> with Type
///       already filled in — it does not select anything;</item>
/// <item>the group title is <c>{Store} - {Name}</c>, not just the name, and the line under it
///       counts loaded accounts with a singular form for one
///       (<c>Accounts.LoadedOne</c> / <c>Accounts.LoadedFormat</c>).</item>
/// </list>
///
/// <para>
/// R55/R70 had this page as one flat table over every group's accounts. That is why the table had
/// no idea which group it was showing and the toolbar said "Import Accounts" / "Refresh" instead
/// of the original's "Add Accounts" / "Clear Accounts".
/// </para>
/// </summary>
public sealed class AccountView : UserControl
{

    /// <summary>
    /// "Are you sure you want to delete the {0} account group?\nYou cannot undo this action."
    /// (Accounts.Group.DeleteConfirm.MessageFormat) — the group-delete confirmation, wired to the group pane's Delete.
    /// </summary>
    public const string DeleteGroupConfirmFormat =
        "Are you sure you want to delete the {0} account group?\nYou cannot undo this action.";

    /// <summary>The confirmation text for deleting the group named <paramref name="group"/>.</summary>
    public static string DeleteGroupConfirm(string group) => string.Format(DeleteGroupConfirmFormat, group);
    private readonly AccountsDocument _doc;
    private readonly Action? _onChanged;

    private AccountGrid? _grid;
    private AccountGroup? _selectedGroup;
    private string _storeSearch = string.Empty;

    // R500: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>CreateGroup</c>; behaviour unchanged (was a method).</summary>
    public ICommand CreateGroup { get; }

    public AccountView(AccountsDocument doc, Action? onChanged = null)
    {
        CreateGroup = new RelayCommand(CreateGroupCore);

        _doc = doc;
        _onChanged = onChanged;

        // Open on whatever the original would: the first group that exists.
        _selectedGroup = doc.AccountGroups.FirstOrDefault();
        Content = Build();
    }

    /// <summary>
    /// The platform row a group belongs under.
    ///
    /// <para>
    /// Type first, then Store, then "Ungrouped". The fallback is not cosmetic: groups written
    /// before R71 have neither field, and a left pane that only lists catalogue platforms would
    /// hide them completely — every account would be on disk and nowhere on screen. That is the
    /// R55 shape again (data present, nothing binds it), so the page refuses to hide them.
    /// </para>
    /// </summary>
    internal static string PlatformOf(AccountGroup group) =>
        !string.IsNullOrWhiteSpace(group.Type) ? group.Type
        : !string.IsNullOrWhiteSpace(group.Store) ? group.Store
        : UngroupedPlatform;

    /// <summary>The row legacy groups without a Type or Store appear under.</summary>
    internal const string UngroupedPlatform = "Ungrouped";

    /// <summary>The groups of one platform, in list order.</summary>
    internal IReadOnlyList<AccountGroup> GroupsFor(string platform) =>
        _doc.AccountGroups.Where(g => string.Equals(PlatformOf(g), platform, StringComparison.OrdinalIgnoreCase))
                          .ToList();

    /// <summary>The platform rows the left pane shows, filtered by the store search box.</summary>
    internal IReadOnlyList<string> VisiblePlatforms()
    {
        var platforms = StoreCatalog.Platforms.ToList();
        // A group can carry a type that is not in the catalogue (hand-edited config, or a platform
        // added later); show those too rather than hiding the group.
        foreach (var type in _doc.AccountGroups
                     .Select(PlatformOf)
                     .Where(t => t.Length > 0 && !platforms.Contains(t, StringComparer.OrdinalIgnoreCase)))
            platforms.Add(type);

        if (string.IsNullOrWhiteSpace(_storeSearch)) return platforms;
        return platforms
            .Where(p => p.Contains(_storeSearch, StringComparison.OrdinalIgnoreCase))
            .ToList();
    }

    /// <summary>The group on screen, or null when there is nothing to show.</summary>
    // ------------------------------------------------ copy from the image's locale (R392)
    //
    // Ten strings the live page has and this view did not (Accounts.* in the string table). They are constants rather than
    // literals at the call sites so a test can assert them verbatim, which is how every other recovered string is kept.

    /// <summary>"Delete {0} accounts?" — the delete confirmation's title.</summary>
    public const string DeleteConfirmTitleFormat = "Delete {0} accounts?";

    /// <summary>The delete confirmation's body.</summary>
    public const string DeleteConfirmMessageFormat =
        "Are you sure you want to delete {0} accounts?\nYou cannot undo this action.";

    /// <summary>"Delete ({0}) accounts" — the confirmation's action button.</summary>
    public const string DeleteConfirmActionFormat = "Delete ({0}) accounts";

    /// <summary>"Edit ({0})" — title of the edit-password dialog.</summary>
    public const string EditPasswordTitleFormat = "Edit ({0})";

    /// <summary>Shown when a search matches no account.</summary>
    public const string NoResultsSubtitle = "There are no accounts matching your search";

    /// <summary>The group list's delete entry.</summary>
    public const string DeleteGroupLabel = "Delete Group";

    /// <summary>"{0} Account Groups Loaded" — the group pane's footer.</summary>
    public const string GroupsLoadedFormat = "{0} Account Groups Loaded";

    /// <summary>"1 Account Group Loaded" — singular footer.</summary>
    public const string GroupsLoadedOne = "1 Account Group Loaded";

    /// <summary>"{0} ACCOUNTS SELECTED" — the selection counter.</summary>
    public const string SelectedManyFormat = "{0} ACCOUNTS SELECTED";

    /// <summary>"{0} ACCOUNT SELECTED" — the singular selection counter.</summary>
    public const string SelectedOneFormat = "{0} ACCOUNT SELECTED";

    /// <summary>The group-pane footer for <paramref name="count"/> groups, with the image's singular/plural split.</summary>
    public static string GroupsLoaded(int count) =>
        count == 1 ? GroupsLoadedOne : string.Format(GroupsLoadedFormat, count);

    /// <summary>The selection counter for <paramref name="count"/> accounts, singular when it is one.</summary>
    public static string SelectionCaption(int count) =>
        string.Format(count == 1 ? SelectedOneFormat : SelectedManyFormat, count);

    public AccountGroup? SelectedGroup => _selectedGroup;

    /// <summary>
    /// The caption under the group title. <c>Accounts.LoadedOne</c> is "1 Account Loaded" and
    /// <c>Accounts.LoadedFormat</c> is "{0} Accounts Loaded"; the original uses only the format, so
    /// one account reads "1 Accounts Loaded" on screen. The singular is used here.
    /// </summary>
    internal static string LoadedCaption(int count) =>
        count == 1 ? "1 Account Loaded" : $"{count} Accounts Loaded";

    /// <summary>Selects a group and repaints. Selecting is a page concern, not the table's.</summary>
    internal void SelectGroup(AccountGroup? group)
    {
        _selectedGroup = group;
        Content = Build();
    }

    /// <summary>Groups shown for a platform, as the left pane prints them.</summary>
    internal static string GroupCaption(AccountGroup group) => group.Display;

    /// <summary>
    /// Opens the "create account group" dialog for the first platform (bound as <c>CreateGroup</c>). The button that used to
    /// hold this inline now calls the member, so a keybind reaches the same place.
    /// </summary>
    private void CreateGroupCore() =>
        CreateGroupModal.Show(this, StoreCatalog.Platforms[0], NameTaken, AddGroup);

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

    // ---------------------------------------------------------------- left pane

    private Control BuildLeftPane()
    {
        var rows = new StackPanel { Spacing = 2 };

        foreach (var platform in VisiblePlatforms())
        {
            // Accounts.Groups
            var header = new Button
            {
                Content = new TextBlock { Text = platform, FontWeight = FontWeight.SemiBold },
                Background = Brushes.Transparent,
                BorderThickness = new Thickness(0),
                Padding = new Thickness(6, 4),
                HorizontalAlignment = HorizontalAlignment.Stretch,
                HorizontalContentAlignment = HorizontalAlignment.Left,
            };
            var type = platform;
            header.Click += (_, _) => OnPlatformClicked(type);
            rows.Children.Add(header);

            foreach (var group in GroupsFor(platform))
            {
                var caption = new TextBlock
                {
                    Text = GroupCaption(group),
                    Margin = new Thickness(18, 2, 4, 2),
                    Opacity = _selectedGroup?.Id == group.Id ? 1.0 : 0.75,
                };
                var target = group;
                var hit = new Button
                {
                    Content = caption,
                    Background = _selectedGroup?.Id == group.Id ? AccentBrush : Brushes.Transparent,
                    BorderThickness = new Thickness(0),
                    Padding = new Thickness(0),
                    HorizontalAlignment = HorizontalAlignment.Stretch,
                    HorizontalContentAlignment = HorizontalAlignment.Left,
                };
                hit.Click += (_, _) => SelectGroup(target);
                rows.Children.Add(hit);
            }
        }

        if (rows.Children.Count == 0)
            rows.Children.Add(new TextBlock
            {
                // Accounts.Empty.NoStores.Subtitle
                Text = "No stores matched your search",
                Opacity = 0.6,
                Margin = new Thickness(6, 8, 6, 0),
            });

        var search = new TextBox
        {
            Watermark = "Search stores",
            Margin = new Thickness(0, 0, 0, 6),
        };
        search.TextChanged += (_, _) =>
        {
            _storeSearch = search.Text ?? string.Empty;
            Content = Build();
        };

        var newGroup = UiKit.Button("New Group", () => CreateGroupCore());

        var body = new DockPanel { LastChildFill = true };
        var head = new StackPanel
        {
            Margin = new Thickness(0, 0, 0, 6),
            Children =
            {
                // Accounts.Groups
                new TextBlock { Text = "ACCOUNT GROUPS", Opacity = 0.7, Margin = new Thickness(4, 0, 0, 6) },
                search,
            },
        };
        DockPanel.SetDock(head, Avalonia.Controls.Dock.Top);
        body.Children.Add(head);
        body.Children.Add(new ScrollViewer { Content = rows });

        // R222: 324 px, the measured rail width (was 300).
        var pane = new DockPanel { LastChildFill = true, Width = 324 };
        DockPanel.SetDock(newGroup, Avalonia.Controls.Dock.Bottom);
        pane.Children.Add(newGroup);
        pane.Children.Add(body);

        var outer = new Border
        {
            Padding = new Thickness(8),
            BorderThickness = new Thickness(0, 0, 1, 0),
            BorderBrush = new SolidColorBrush(Color.Parse("#2A2E3A")),
            Child = pane,
        };
        return outer;
    }

    private static readonly IBrush AccentBrush = new SolidColorBrush(Color.Parse("#2A2E3A"));

    private static Control Docked(Control control, Avalonia.Controls.Dock dock)
    {
        DockPanel.SetDock(control, dock);
        return control;
    }

    /// <summary>
    /// A platform row was clicked. The original opens Create Group with Type preset instead of
    /// selecting, which R70 observed by clicking Nike with no groups under it.
    /// </summary>
    private void OnPlatformClicked(string platform)
    {
        var existing = GroupsFor(platform);
        if (existing.Count > 0)
        {
            SelectGroup(existing[0]);
            return;
        }

        CreateGroupModal.Show(this, platform, NameTaken, AddGroup);
    }

    private bool NameTaken(string name) =>
        _doc.AccountGroups.Any(g => string.Equals(g.Name, name, StringComparison.OrdinalIgnoreCase));

    private void AddGroup(AccountGroup group)
    {
        _doc.AccountGroups.Add(group);
        _selectedGroup = group;
        _onChanged?.Invoke();
        Content = Build();
    }

    // ---------------------------------------------------------------- detail

    private Control BuildDetail()
    {
        if (_selectedGroup is not { } group)
        {
            return new StackPanel
            {
                Margin = new Thickness(16),
                Spacing = 8,
                Children =
                {
                    // Accounts.Empty.NoGroups.Subtitle
                    UiKit.Empty("Add a group to get started"),
                },
            };
        }

        var caption = new StackPanel { Spacing = 2 };
        caption.Children.Add(new TextBlock
        {
            Text = GroupCaption(group),
            FontSize = 20,
            FontWeight = FontWeight.SemiBold,
        });
        caption.Children.Add(new TextBlock
        {
            Text = GroupsLoaded(_doc.AccountGroups.Count),
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
        gear.Click += (_, _) => AccountGroupView.Show(this, target,
            name =>
            {
                target.Name = name;
                _onChanged?.Invoke();
                Content = Build();
            },
            () =>
            {
                _doc.AccountGroups.Remove(target);
                _selectedGroup = _doc.AccountGroups.FirstOrDefault();
                _onChanged?.Invoke();
                Content = Build();
            });

        var title = new StackPanel { Orientation = Orientation.Horizontal };
        title.Children.Add(caption);
        title.Children.Add(gear);

        var search = new TextBox
        {
            Watermark = "Search accounts",
            Width = 240,
            VerticalAlignment = VerticalAlignment.Center,
        };
        var searchHost = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            HorizontalAlignment = HorizontalAlignment.Right,
            VerticalAlignment = VerticalAlignment.Center,
            Children = { search },
        };

        var top = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto"), Margin = new Thickness(12, 8, 12, 8) };
        Grid.SetColumn(title, 0);
        Grid.SetColumn(searchHost, 1);
        top.Children.Add(title);
        top.Children.Add(searchHost);

        _grid = new AccountGrid(group.Accounts, () =>
        {
            _onChanged?.Invoke();
            Content = Build();
        })
            .WithMover(account => MoveAccount(account, group))
            .WithEditor(account => EditPassword(account, group))
            // R508: the bound `Add` command needs the dialog opener; the header Button below uses the same one.
            .WithImporter(() =>
            {
                var import = new AccountImportWindow(_doc, group);
                import.Closed += (_, _) =>
                {
                    _onChanged?.Invoke();
                    Content = Build();
                };
                if (TopLevel.GetTopLevel(this) is Window owner) _ = import.ShowDialog(owner);
            });

        search.TextChanged += (_, _) => _grid?.SetFilter(search.Text);

        // Accounts.Action.Add / .Clear sit on the column-header line, level with the column names —
        // that is where the original puts them, and where the replica's separate toolbar row was
        // wrong.
        _grid.WithHeaderActions(new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            HorizontalAlignment = HorizontalAlignment.Right,
            Children =
            {
                UiKit.Button("Add Accounts", () =>
                {
                    var import = new AccountImportWindow(_doc, group);
                    import.Closed += (_, _) =>
                    {
                        _onChanged?.Invoke();
                        Content = Build();
                    };
                    if (TopLevel.GetTopLevel(this) is Window window) _ = import.ShowDialog(window);
                }),
                UiKit.Button("Clear Accounts", () =>
                {
                    // R508: go through the bound command so the "Delete N accounts?" gate is asked —
                    // the original asks (docs/R507_ROUTE_C_WORKED.md). This used to clear silently.
                    _grid?.Clear.Execute(null);
                }),
            },
        });

        var dock = new DockPanel { LastChildFill = true };
        DockPanel.SetDock(top, Avalonia.Controls.Dock.Top);
        dock.Children.Add(top);
        dock.Children.Add(new Border { Padding = new Thickness(12, 0, 12, 12), Child = _grid });
        return dock;
    }

    private Task MoveAccount(Account account, AccountGroup from)
    {
        AccountMoveView.Show(this, account, _doc.AccountGroups, from, () =>
        {
            _onChanged?.Invoke();
            Content = Build();
        });
        return Task.CompletedTask;
    }

    /// <summary>
    /// <c>Accounts.EditPassword.*</c> — the row's pencil opens "Edit ({email})" with one password
    /// box and an "Edit Password" button.
    /// </summary>
    private void EditPassword(Account account, AccountGroup group)
    {
        var box = new TextBox { Text = account.Password, HorizontalAlignment = HorizontalAlignment.Stretch };
        var body = UiKit.Scroll(UiKit.Form(
            UiKit.Row("Password", box),
            UiKit.Caption("The email stays as it is; only the password changes.")));

        var save = UiKit.Button("Edit Password", () =>
        {
            account.Password = box.Text ?? string.Empty;
            _onChanged?.Invoke();
            Content = Build();
        });

        ViewHostModal.Show(this, $"Edit ({account.Email})", body, 480, 220, save);
    }
}
