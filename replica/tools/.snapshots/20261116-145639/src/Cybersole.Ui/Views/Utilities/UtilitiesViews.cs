using Avalonia;
using System.Windows.Input;
using Avalonia.Controls;
using Avalonia.Layout;
using Cybersole.Core.Models;
using Cybersole.Services;

namespace Cybersole.Ui.Views.Utilities;

/// <summary>
/// Store groups page (Cybersole.Ui.Views.Utilities.UtilitiesView) — the recovered commands are
/// New / Clone / Delete / Edit over a list of named store sets, plus the empty state.
/// </summary>
public sealed class UtilitiesView : UserControl
{
    /// <summary>Bound as <c>CloneStoreGroup</c>; runs <c>CloneStoreGroupCore()</c>.</summary>
    public ICommand CloneStoreGroup { get; }

    private readonly AppServices _services;
    /// <summary>"{0} stores" — the caption under the stores column (Utilities.StoreGroups.CountFormat).</summary>
    public const string StoresCountFormat = "{0} stores";

    /// <summary>"No stores" — the zero form (Utilities.StoreGroups.CountNone).</summary>
    public const string StoresCountNone = "No stores";

    /// <summary>"1 store" — the singular form (Utilities.StoreGroups.CountOne is "1 " + the noun).</summary>
    public const string StoresCountOne = "1 store";

    /// <summary>The caption for <paramref name="count"/> stores, with the image's zero and one forms.</summary>
    public static string StoresCount(int count) => count switch
    {
        0 => StoresCountNone,
        1 => StoresCountOne,
        _ => string.Format(StoresCountFormat, count),
    };


    // ------------------------------------------------ copy from the image's locale (R411)
    //
    // The Utilities.StoreGroups.* family, verbatim. Same shape as ProfileCsvEditorView.Copy: short name → text, with
    // the locale key on each line. Two Delete messages are left out — their pool values are truncated mid-sentence.
    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)
    {
        ["Title"] = "Utilities",   // Utilities.Title
        ["Subtitle"] = "Reusable pieces you can share across your smart actions",   // Utilities.Subtitle
        ["StoreGroupsTitle"] = "Store Groups",   // Utilities.StoreGroups.Title
        ["StoreGroupsSubtitle"] = "Save a set of stores once and reuse it as a smart action filter",   // Utilities.StoreGroups.Subtitle
        ["StoreGroupsNew"] = "New Group",   // Utilities.StoreGroups.New
        ["StoreGroupsEmpty"] = "No store groups yet. Create one to reuse it as a filter.",   // Utilities.StoreGroups.Empty
        ["ContextCloneFormat"] = "Clone {0}",   // Utilities.StoreGroups.Context.CloneFormat
        ["ContextDeleteFormat"] = "Delete {0}",   // Utilities.StoreGroups.Context.DeleteFormat
        ["ContextEditFormat"] = "Edit {0}",   // Utilities.StoreGroups.Context.EditFormat
        ["DeleteTitleFormat"] = "Delete {0}?",   // Utilities.StoreGroups.Delete.TitleFormat
                ["DeleteMessageFormat"] = "This will permanently delete the store group \"{0}\".",   // Utilities.StoreGroups.Delete.MessageFormat
                ["DeleteUsedMessageFormat"] = "This will permanently delete the store group \"{0}\".\nIt is used by {1} smart action filter(s), which will stop matching.",   // Utilities.StoreGroups.Delete.UsedMessageFormat
        ["ModalTitleNew"] = "New Store Group",   // Utilities.StoreGroups.Modal.Title.New
        ["ModalTitleEdit"] = "Store Group",   // Utilities.StoreGroups.Modal.Title.Edit
        ["ModalName"] = "Group Name",   // Utilities.StoreGroups.Modal.Name
        ["ModalNamePlaceholder"] = "Enter a group name",   // Utilities.StoreGroups.Modal.NamePlaceholder
        ["ModalStores"] = "Stores",   // Utilities.StoreGroups.Modal.Stores
        ["ModalStoresPlaceholder"] = "Add a store",   // Utilities.StoreGroups.Modal.StoresPlaceholder
        ["ModalErrorDuplicate"] = "A store group with that name already exists",   // Utilities.StoreGroups.Modal.Error.Duplicate
        ["ModalErrorNoName"] = "Enter a group name",   // Utilities.StoreGroups.Modal.Error.NoName
    };

    /// <summary>One of the image's utilities-page strings, by the short name used in <see cref="Copy"/>.</summary>
    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;
    private readonly ListBox _groups = new() { Height = 260 };
    private readonly ListBox _stores = new() { Height = 200 };
    private readonly TextBlock _status = UiKit.Status();

    // R500: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>DeleteStoreGroup</c>; behaviour unchanged (was a method).</summary>
    public ICommand DeleteStoreGroup { get; }

    /// <summary>Bound as <c>EditStoreGroup</c>; behaviour unchanged (was a method).</summary>
    public ICommand EditStoreGroup { get; }

    public UtilitiesView(AppServices services)
    {
        CloneStoreGroup = new RelayCommand(() => CloneStoreGroupCore());
        DeleteStoreGroup = new RelayCommand(() => DeleteStoreGroupCore());
        EditStoreGroup = new RelayCommand(EditStoreGroupCore);

        _services = services;

        _groups.SelectionChanged += (_, _) => RefreshStores();

        Content = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions("340,*"),
            Children =
            {
                BuildGroupsColumn(),
                BuildStoresColumn(),
            },
        };

        Refresh();
    }

    private Control BuildGroupsColumn()
    {
        var name = UiKit.Text(watermark: "Group name");

        var column = new StackPanel { Spacing = 6, Margin = new Thickness(0, 0, 12, 0) };
        column.Children.Add(UiKit.Title("Store groups"));
        column.Children.Add(UiKit.Caption("A named set of stores that tasks and monitors can target."));
        column.Children.Add(_groups);
        column.Children.Add(UiKit.Row("Name", name, 70));
        column.Children.Add(UiKit.Buttons(
            UiKit.Button("New", () => CreateStoreGroup(name.Text)),
            UiKit.Button("Clone", () => CloneStoreGroupCore()),
            UiKit.Button("Delete", () => DeleteStoreGroupCore())));
        column.Children.Add(_status);

        Grid.SetColumn(column, 0);
        return column;
    }

    private Control BuildStoresColumn()
    {
        var stores = new StackPanel { Spacing = 2 };

        void Rebuild()
        {
            stores.Children.Clear();
            var group = Selected();
            if (group is null)
            {
                stores.Children.Add(UiKit.Empty("Create a group first."));
                return;
            }

            foreach (var module in _services.Stores.Modules.OrderBy(m => m.Name))
            {
                var box = UiKit.Check(module.Name, group.Stores.Contains(module.Id), on =>
                {
                    if (on)
                    {
                        if (!group.Stores.Contains(module.Id)) group.Stores.Add(module.Id);
                    }
                    else
                    {
                        group.Stores.Remove(module.Id);
                    }
                    _services.Config.Save();
                });
                stores.Children.Add(box);
            }
        }

        var column = new StackPanel { Spacing = 6 };
        column.Children.Add(UiKit.Title("Stores"));
        column.Children.Add(UiKit.Caption("Tick every store this group covers."));
        column.Children.Add(UiKit.Scroll(stores));
        column.Children.Add(UiKit.Buttons(
            UiKit.Button("Select all", () =>
            {
                var group = Selected();
                if (group is null) return;
                group.Stores = _services.Stores.Modules.Select(m => m.Id).ToList();
                _services.Config.Save();
                Rebuild();
                Refresh();
                _status.Text = "All stores selected.";
            }),
            UiKit.Button("Clear", () =>
            {
                var group = Selected();
                if (group is null) return;
                group.Stores.Clear();
                _services.Config.Save();
                Rebuild();
                Refresh();
                _status.Text = "Selection cleared.";
            })));

        Rebuild();
        _rebuildStores = Rebuild;

        Grid.SetColumn(column, 1);
        return column;
    }

    private Action? _rebuildStores;

    // ------------------------------------------------ bound commands (R231)
    //
    // The original binds these five members on UtilitiesView (analysis/xaml_bindings.json):
    //   CloneStoreGroup, CreateStoreGroup, () => DeleteStoreGroup.Execute(null), () => EditStoreGroup.Execute(null), StoreGroups
    // The behaviour existed inside the "New / Clone / Delete" lambdas; the names are what a keybind or a rebinding
    // addresses, so they exist here and the buttons call them.

    /// <summary>The store groups on screen (bound as <c>StoreGroups</c>).</summary>
    public IReadOnlyList<StoreGroup> StoreGroups => _services.Config.Settings.StoreGroups;

    /// <summary>Creates a group, named from <paramref name="name"/> or "Group N" (bound as <c>CreateStoreGroup</c>).</summary>
    public StoreGroup CreateStoreGroup(string? name)
    {
        var group = new StoreGroup
        {
            Name = string.IsNullOrWhiteSpace(name)
                ? $"Group {_services.Config.Settings.StoreGroups.Count + 1}"
                : name!.Trim(),
        };
        _services.Config.Settings.StoreGroups.Add(group);
        _services.Config.Save();
        Refresh();
        _status.Text = "Group created.";
        return group;
    }

    /// <summary>Duplicates the selected group (bound as <c>CloneStoreGroup</c>).</summary>
    public StoreGroup? CloneStoreGroupCore()
    {
        var src = Selected();
        if (src is null) return null;

        var copy = new StoreGroup
        {
            Name = src.Name + " copy",
            Enabled = src.Enabled,
            Stores = src.Stores.ToList(),
        };
        _services.Config.Settings.StoreGroups.Add(copy);
        _services.Config.Save();
        Refresh();
        _status.Text = "Group cloned.";
        return copy;
    }

    /// <summary>Removes the selected group (bound as <c>DeleteStoreGroup</c>).</summary>
    private bool DeleteStoreGroupCore()
    {
        var target = Selected();
        if (target is null) return false;

        _services.Config.Settings.StoreGroups.Remove(target);
        _services.Config.Save();
        Refresh();
        _status.Text = "Group deleted.";
        return true;
    }

    /// <summary>Opens the group editor for the selection (bound as <c>EditStoreGroup</c>).</summary>
    private void EditStoreGroupCore()
    {
        var existing = Selected();
        if (TopLevel.GetTopLevel(this) is Window owner)
            _ = new StoreGroupModal(_services, existing).ShowDialog(owner);
        else if (existing is not null)
            _status.Text = "No window host to edit " + existing.Name;
    }

    private StoreGroup? Selected()
    {
        var index = _groups.SelectedIndex;
        var groups = _services.Config.Settings.StoreGroups;
        return index < 0 || index >= groups.Count ? groups.FirstOrDefault() : groups[index];
    }

    private void RefreshStores()
    {
        _rebuildStores?.Invoke();
        RefreshList();
    }

    private void RefreshList()
    {
        var groups = _services.Config.Settings.StoreGroups;
        _groups.ItemsSource = groups.Count == 0
            ? new List<string> { "(no groups yet)" }
            : groups.Select(g => $"{(g.Enabled ? "*" : "-")} {g.Name}  ({g.Stores.Count} stores)").ToList();
    }

    public void Refresh()
    {
        RefreshList();
        _rebuildStores?.Invoke();
        _stores.ItemsSource = Selected()?.Stores.ToList() ?? new List<string>();
    }
}

/// <summary>
/// Store group editor (Cybersole.Ui.Views.Utilities.StoreGroupModal) — Title / Close / Save.
/// </summary>
public sealed class StoreGroupModal : Window
{
    // R260: the original binds RemoveStore here (analysis/xaml_bindings.json) — the dialog edits a group, and a group
    // is a list of stores, so removing one belongs to it.

    /// <summary>The group being edited, or the one that will be created.</summary>
    private StoreGroup? _editing;

    /// <summary>
    /// Whether this dialog is editing an existing group rather than creating one (bound as <c>IsEditing</c>). Read-only: it
    /// is decided by the constructor argument.
    /// </summary>
    public bool IsEditing => _editing is not null;

    /// <summary>
    /// Deletes the group being edited from the configuration (bound as <c>Delete</c>). False when this dialog is creating a
    /// new group, or when the group was not in the list.
    /// </summary>
    private bool DeleteCore()
    {
        if (_editing is null) return false;
        if (!_storeServices.Config.Settings.StoreGroups.Remove(_editing)) return false;

        _storeServices.Config.Save();
        return true;
    }

    /// <summary>
    /// Removes a store from the group being edited (bound as <c>RemoveStore</c>). Returns false when the group does not
    /// contain it. The caller saves afterwards, the same way the other rows of this dialog work.
    /// </summary>
    public bool RemoveStore(string storeId)
    {
        if (_editing is null || string.IsNullOrWhiteSpace(storeId)) return false;
        return _editing.Stores.Remove(storeId);
    }

    private readonly AppServices _storeServices;

    // R500: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>Delete</c>; behaviour unchanged (was a method).</summary>
    public ICommand Delete { get; }

    public StoreGroupModal(AppServices services, StoreGroup? existing = null)
    {
        Delete = new RelayCommand(() => DeleteCore());

        _storeServices = services;
        _editing = existing;
        Title = existing is null ? "New store group" : $"Edit {existing.Name}";
        Width = 480;
        Height = 300;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;
        CanResize = false;

        var name = UiKit.Text(existing?.Name, watermark: "Group name", width: 320);
        var enabled = UiKit.Check("Enabled", existing?.Enabled ?? true);
        var status = UiKit.Status();

        Content = new StackPanel
        {
            Margin = new Thickness(16),
            Spacing = 8,
            Children =
            {
                UiKit.Title(existing is null ? "New store group" : "Edit store group"),
                UiKit.Form(
                    UiKit.Row("Name", name, 120),
                    UiKit.Row("State", enabled, 120)),
                UiKit.Buttons(
                    new Button
                    {
                        Content = "Save",
                        Command = new RelayCommand(() =>
                        {
                            var target = existing ?? new StoreGroup();
                            target.Name = string.IsNullOrWhiteSpace(name.Text)
                                ? "Group"
                                : name.Text!;
                            target.Enabled = enabled.IsChecked == true;

                            if (existing is null)
                                services.Config.Settings.StoreGroups.Add(target);

                            services.Config.Save();
                            Close();
                        }),
                    },
                    new Button { Content = "Close", Command = new RelayCommand(Close) }),
                status,
            },
        };
    }
}
