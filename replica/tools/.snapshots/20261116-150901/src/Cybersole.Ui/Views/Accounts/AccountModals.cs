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
/// The platform list the left pane shows and the country stores each one offers.
///
/// <para>
/// R70 read the live Store dropdown for Type=Nike and saw <c>Nike US</c>, <c>Nike GB</c>,
/// <c>Nike NL</c>, <c>Nike BE</c>, <c>Nike JP</c>, <c>Nike AT</c>, <c>Nike CZ</c>,
/// <c>Nike DK</c>, <c>Nike FI</c>, <c>Nike FR</c> with more below the fold;
/// <c>docs/NIKE_PARITY.md</c> had already recovered 22 country codes from the string pool
/// (<c>Nike IT</c> … <c>Nike ZA</c>). The union of the two is what is offered here — the dropdown
/// is a country list, and neither source alone is complete.
/// </para>
///
/// <para>
/// Only Nike has a recovered country list. Every other platform offers a single store named after
/// itself, which is what the original shows for a platform whose store is not partitioned.
/// </para>
/// </summary>
public static class StoreCatalog
{
    /// <summary>The platform names in the left pane, in the order the original lists them.</summary>
    public static readonly string[] Platforms =
    {
        "Nike", "Nike GS", "Shopify", "Footlocker (Asia)", "Farfetch", "Demandware (Funko)",
        "Demandware", "Magento", "Casio", "HBX", "Popmart", "Goat", "Scheels", "Warhammer",
    };

    /// <summary>ISO-3166 alpha-2 codes the Nike store dropdown offers.</summary>
    public static readonly string[] NikeCountries =
    {
        "AT", "BE", "CZ", "DE", "DK", "ES", "FI", "FR", "GB", "IE", "IT", "JP", "LU", "MX",
        "MY", "NL", "NO", "NZ", "PH", "PL", "PT", "RO", "SE", "SG", "SI", "SK", "TH", "TR",
        "TW", "US", "VN", "ZA",
    };

    /// <summary>Every store a platform offers.</summary>
    public static IReadOnlyList<string> StoresFor(string platform) =>
        platform is "Nike" or "Nike GS"
            ? NikeCountries.Select(cc => $"{platform} {cc}").ToList()
            : new List<string> { platform };
}

/// <summary>
/// Group Settings (Cybersole.Ui.Views.Accounts.Modals.AccountGroupView). Opened by the gear beside
/// the group title.
///
/// <para>
/// R70 drove it: the dialog is one field and two buttons — <c>GroupModal.GroupName</c> over a text
/// box, then <c>Delete</c> in red and <c>Save</c> in green. Delete confirms with
/// <c>Accounts.Group.DeleteConfirm.*</c> ("Delete {0}?" / "Are you sure you want to delete the {0}
/// account group?"), which is why it is not in <see cref="AccountGrid"/>'s menu: groups are
/// managed here and accounts are managed in the table.
/// </para>
/// </summary>
public sealed class AccountGroupView : UserControl
{
    /// <summary>
    /// The group name (bound as <c>GroupName</c>). The image exposes it with a setter too (see
    /// docs/BINDING_SHAPES.md), so writing it updates the box as well as the group.
    /// </summary>
    public string GroupName
    {
        get => _name.Text ?? string.Empty;
        set
        {
            _name.Text = value ?? string.Empty;
            if (_group is not null) _group.Name = _name.Text!;
        }
    }

    private readonly TextBox _name;
    private readonly AccountGroup? _group;

    public AccountGroupView(AccountGroup group)
    {
        Close = new RelayCommand(CloseCore);

        _group = group;
        _name = new TextBox { Text = group.Name, HorizontalAlignment = HorizontalAlignment.Stretch };

        var body = new StackPanel
        {
            Spacing = 8,
            Children =
            {
                new TextBlock { Text = "Group Name", Opacity = 0.8 },
                _name,
            },
        };

        Body = body;
        Content = UiKit.Scroll(body);
    }

    /// <summary>The editable body, so a host can read the name without reaching into the tree.</summary>
    public Panel Body { get; }

    /// <summary>The name as typed.</summary>
    public string ChosenName => _name.Text?.Trim() ?? string.Empty;

    /// <summary><c>Accounts.Group.DeleteConfirm</c> — title and message for deleting one group.</summary>
    internal static (string Title, string Message, string Action) DeleteConfirm(string groupName) => (
        $"Delete {groupName}?",
        $"Are you sure you want to delete the {groupName} account group?\nYou cannot undo this action.",
        $"Delete {groupName}");

    /// <summary>
    /// Opens Group Settings. <paramref name="onSaved"/> gets the new name; <paramref name="onDeleted"/>
    /// runs when the group is deleted. Both are the caller's because the group list is the caller's.
    /// </summary>
    public static bool Show(Control owner, AccountGroup group, Action<string> onSaved, Action onDeleted)
    {
        var view = new AccountGroupView(group);

        var delete = UiKit.Button("Delete", () =>
        {
            onDeleted();
            if (TopLevel.GetTopLevel(owner) is Window window) window.Close();
        });
        delete.Background = new SolidColorBrush(Color.Parse("#C0392B"));

        var save = UiKit.Button("Save", () =>
        {
            onSaved(view.ChosenName);
            if (TopLevel.GetTopLevel(owner) is Window window) window.Close();
        });
        save.Background = new SolidColorBrush(Color.Parse("#27AE60"));

        return ViewHostModal.Show(owner, "Group Settings", view, 520, 260, delete, save);
    }

    /// <summary>
    /// R502: the original binds <c>Close</c> on this type (descriptor table: Getter + Setter). The replica
    /// declares no `Close()` here, so the name is free — unlike the seven `Window`-derived classes, where
    /// `Window.Close()` occupies it.
    /// </summary>
    public ICommand Close { get; }

    private void CloseCore()
    {
        if (TopLevel.GetTopLevel(this) is Avalonia.Controls.Window host) host.Close();
    }
}

/// <summary>
/// Create Group (Cybersole.Ui.Views.Accounts.Modals.CreateGroupModal).
///
/// <para>
/// Three fields in the order the original shows them — <c>CreateGroup.Type</c>,
/// <c>CreateGroup.Store</c>, <c>CreateGroup.Name</c> — and one button, <c>CreateGroup.Button</c>
/// ("Add Group"). R70 clicked it before choosing a store: the button carried no accessibility
/// actions at all, and only after a store was picked did it become
/// <c>Button "Add Group" [id=CreateButton actions=[invoke]]</c>. So the button is genuinely
/// disabled until Type, Store and Name are all set, and this reproduces that.
/// </para>
/// </summary>
public sealed class CreateGroupModal : UserControl
{
    /// <summary>The account types this dialog offers (bound as <c>Types</c>).</summary>
    public IReadOnlyList<string> Types => StoreCatalog.Platforms;

    private readonly ComboBox _type;
    private readonly ComboBox _store;
    private readonly TextBox _name;
    private readonly Button _add;

    public CreateGroupModal(string presetType, Func<string, bool> nameTaken)
    {
        Close = new RelayCommand(CloseCore);

        _type = new ComboBox
        {
            ItemsSource = StoreCatalog.Platforms,
            SelectedIndex = Math.Max(0, Array.IndexOf(StoreCatalog.Platforms, presetType)),
            HorizontalAlignment = HorizontalAlignment.Stretch,
        };

        _store = new ComboBox
        {
            ItemsSource = StoreCatalog.StoresFor(StoreCatalog.Platforms[
                Math.Max(0, Array.IndexOf(StoreCatalog.Platforms, presetType))]),
            PlaceholderText = "Select Store",
            HorizontalAlignment = HorizontalAlignment.Stretch,
        };

        _name = new TextBox { Watermark = "Group Name", HorizontalAlignment = HorizontalAlignment.Stretch };
        _add = UiKit.Button("Add Group", () => { });

        // Store list follows Type, and the button follows all three.
        _store.ItemsSource = StoreCatalog.StoresFor(SelectedType());
        _type.SelectionChanged += (_, _) =>
        {
            _store.ItemsSource = StoreCatalog.StoresFor(SelectedType());
            _store.SelectedIndex = -1;
            Refresh();
        };
        _store.SelectionChanged += (_, _) => Refresh();
        _name.TextChanged += (_, _) => Refresh();

        _nameTaken = nameTaken;
        Refresh();

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.Row("Type", _type),
            UiKit.Row("Store", _store),
            UiKit.Row("Name", _name),
            // R71: this button was created and never parented — the dialog opened with only a
            // Close button, and every unit test passed because they asked the object, not the
            // screen. Found by opening the dialog in the replica. It goes in the body, where the
            // original has it.
            _add));
    }

    private readonly Func<string, bool> _nameTaken;

    /// <summary>The button, so a host can attach the confirm action and tests can read its state.</summary>
    public Button AddButton => _add;

    /// <summary>The platform currently chosen.</summary>
    public string SelectedType() =>
        _type.SelectedIndex >= 0 && _type.SelectedIndex < StoreCatalog.Platforms.Length
            ? StoreCatalog.Platforms[_type.SelectedIndex]
            : StoreCatalog.Platforms[0];

    /// <summary>The store currently chosen, or null.</summary>
    public string? SelectedStore()
    {
        var stores = StoreCatalog.StoresFor(SelectedType());
        var index = _store.SelectedIndex;
        return index >= 0 && index < stores.Count ? stores[index] : null;
    }

    /// <summary>The name as typed.</summary>
    public string ChosenName => _name.Text?.Trim() ?? string.Empty;

    /// <summary>
    /// True when all three fields are filled and the name is not already used. The original's
    /// disabled <c>Add Group</c> is the observable half of this.
    /// </summary>
    public bool CanAdd => SelectedStore() is not null && ChosenName.Length > 0 && !_nameTaken(ChosenName);

    /// <summary>Sets Type by index. The Store list follows it, and the selection is cleared.</summary>
    internal void ChooseType(int index)
    {
        _type.SelectedIndex = index;
        _store.SelectedIndex = -1;
        Refresh();
    }

    /// <summary>Sets Store by index.</summary>
    internal void ChooseStore(int index)
    {
        _store.SelectedIndex = index;
        Refresh();
    }

    /// <summary>Types a name.</summary>
    internal void TypeName(string name)
    {
        _name.Text = name;
        Refresh();
    }

    private void Refresh() => _add.IsEnabled = CanAdd;

    /// <summary>Builds the group this dialog describes, without adding it anywhere.</summary>
    public AccountGroup Build()
    {
        var type = SelectedType();
        return new AccountGroup { Type = type, Store = SelectedStore() ?? type, Name = ChosenName };
    }

    /// <summary>
    /// Opens the dialog. <paramref name="onCreated"/> receives the group and is responsible for
    /// adding it — the caller owns the list.
    /// </summary>
    public static bool Show(Control owner, string presetType, Func<string, bool> nameTaken,
        Action<AccountGroup> onCreated)
    {
        var view = new CreateGroupModal(presetType, nameTaken);

        view.AddButton.Click += (_, _) =>
        {
            if (!view.CanAdd) return;
            onCreated(view.Build());
            if (TopLevel.GetTopLevel(owner) is Window window) window.Close();
        };

        return ViewHostModal.Show(owner, "Create Group", view, 520, 320);
    }

    /// <summary>
    /// R502: the original binds <c>Close</c> on this type (descriptor table: Getter + Setter). The replica
    /// declares no `Close()` here, so the name is free — unlike the seven `Window`-derived classes, where
    /// `Window.Close()` occupies it.
    /// </summary>
    public ICommand Close { get; }

    private void CloseCore()
    {
        if (TopLevel.GetTopLevel(this) is Avalonia.Controls.Window host) host.Close();
    }
}
