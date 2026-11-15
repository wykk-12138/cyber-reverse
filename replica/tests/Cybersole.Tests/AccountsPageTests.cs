using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Accounts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 71: the accounts page is two panes, not one table.
///
/// <para>
/// R70 walked the real 5.18.32 and wrote down what the page is: a left pane of platforms and their
/// groups, a right pane showing one group, a title that reads <c>{Store} - {Name}</c>, a count
/// under it, a gear that opens Group Settings, a search box, and a toolbar that belongs to the
/// group. The six views behind it are named in <c>docs/ORIGINAL_VIEWS.md</c>.
/// </para>
///
/// <para>
/// Everything asserted here is a string the locale ships or a behaviour the GUI showed — none of
/// it is a guess about layout.
/// </para>
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class AccountsPageTests
{
    private readonly ITestOutputHelper _out;

    public AccountsPageTests(ITestOutputHelper output) => _out = output;

    private static Account Make(string email, DateTime? created = null) => new()
    {
        Email = email,
        Password = "pw-" + email.Split('@')[0],
        Created = created ?? new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc),
    };

    private static AccountGroup Group(string type, string store, string name, params Account[] accounts)
    {
        var group = new AccountGroup { Type = type, Store = store, Name = name };
        foreach (var account in accounts)
        {
            account.GroupId = group.Id;
            group.Accounts.Add(account);
        }
        return group;
    }

    /// <summary>The group caption on screen is <c>{Store} - {Name}</c>, as the title bar reads it.</summary>
    [Fact]
    public void TheGroupCaptionIsStoreDashName()
    {
        var group = Group("Nike", "Nike US", "zz-probe");

        _out.WriteLine($"display = {group.Display}");

        Assert.Equal("Nike US - zz-probe", group.Display);
        Assert.Equal("Nike US - zz-probe", AccountView.GroupCaption(group));
    }

    /// <summary>A group with no store falls back to its name rather than printing " - name".</summary>
    [Fact]
    public void AGroupWithoutAStoreFallsBackToItsName()
    {
        Assert.Equal("Group 1", new AccountGroup { Name = "Group 1" }.Display);
        // A store with the default name still reads as the pair the title bar prints.
        Assert.Equal("Nike US - Group 1", new AccountGroup { Store = "Nike US" }.Display);
        // Only a blank name collapses to the store alone.
        Assert.Equal("Nike US", new AccountGroup { Store = "Nike US", Name = "" }.Display);
    }

    /// <summary>
    /// <c>Accounts.LoadedOne</c> / <c>Accounts.LoadedFormat</c>. The original ships both and uses
    /// only the format, so one account reads "1 Accounts Loaded" on screen; the singular is used.
    /// </summary>
    [Fact]
    public void TheLoadedCaptionHasASingular()
    {
        _out.WriteLine($"1 -> {AccountView.LoadedCaption(1)}");
        _out.WriteLine($"3 -> {AccountView.LoadedCaption(3)}");

        Assert.Equal("1 Account Loaded", AccountView.LoadedCaption(1));
        Assert.Equal("3 Accounts Loaded", AccountView.LoadedCaption(3));
        Assert.Equal("0 Accounts Loaded", AccountView.LoadedCaption(0));
    }

    /// <summary>The page opens on the first group that exists, and can be repointed.</summary>
    [Fact]
    public void ThePageOpensOnTheFirstGroup()
    {
        var first = Group("Nike", "Nike US", "one", Make("a@example.com"));
        var second = Group("Shopify", "Shopify", "two");
        var doc = new AccountsDocument();
        doc.AccountGroups.Add(first);
        doc.AccountGroups.Add(second);

        var page = new AccountView(doc);
        _out.WriteLine($"opened on {page.SelectedGroup?.Display}");

        Assert.Same(first, page.SelectedGroup);

        page.SelectGroup(second);
        Assert.Same(second, page.SelectedGroup);
    }

    /// <summary>Groups are grouped under their platform, and an unknown platform is still shown.</summary>
    [Fact]
    public void PlatformsShowTheirOwnGroupsAndUnknownOnesAreNotHidden()
    {
        var doc = new AccountsDocument();
        doc.AccountGroups.Add(Group("Nike", "Nike US", "a"));
        doc.AccountGroups.Add(Group("Nike", "Nike GB", "b"));
        doc.AccountGroups.Add(Group("Walmart", "Walmart", "c"));

        var page = new AccountView(doc);

        Assert.Equal(2, page.GroupsFor("Nike").Count);
        Assert.Single(page.GroupsFor("Walmart"));
        Assert.Contains("Walmart", page.VisiblePlatforms());
    }

    /// <summary>
    /// A group with neither Type nor Store — every group written before R71 — must still appear.
    /// Hiding it would put its accounts on disk and nowhere on screen.
    /// </summary>
    [Fact]
    public void AGroupWithNoTypeOrStoreIsStillListed()
    {
        var doc = new AccountsDocument();
        doc.AccountGroups.Add(Group(string.Empty, string.Empty, "Group 1", Make("a@example.com")));

        var page = new AccountView(doc);

        _out.WriteLine($"platform = {AccountView.PlatformOf(doc.AccountGroups[0])}");
        Assert.Equal("Ungrouped", AccountView.PlatformOf(doc.AccountGroups[0]));
        Assert.Single(page.GroupsFor(AccountView.UngroupedPlatform));
        Assert.Contains(AccountView.UngroupedPlatform, page.VisiblePlatforms());
        Assert.Same(doc.AccountGroups[0], page.SelectedGroup);
    }

    /// <summary>
    /// The Store dropdown for Nike offers country stores, and the catalogue carries the ten R70 saw
    /// plus the twenty-two <c>NIKE_PARITY.md</c> recovered from the string pool.
    /// </summary>
    [Fact]
    public void TheStoreCatalogueOffersNikeCountries()
    {
        var stores = StoreCatalog.StoresFor("Nike");

        _out.WriteLine($"nike stores = {stores.Count}");
        _out.WriteLine("first five: " + string.Join(", ", stores.Take(5)));

        Assert.Contains("Nike US", stores);
        Assert.Contains("Nike GB", stores);
        Assert.Contains("Nike JP", stores);
        Assert.Contains("Nike FR", stores);
        Assert.Contains("Nike ZA", stores);
        Assert.True(stores.Count >= 22, $"only {stores.Count} Nike stores");

        // A platform without a country split offers one store, named after itself.
        Assert.Equal(new[] { "Shopify" }, StoreCatalog.StoresFor("Shopify"));
    }

    /// <summary>
    /// The Create Group dialog stays unusable until Type, Store and Name are all set — the original
    /// ships no <c>invoke</c> action on "Add Group" until a store is picked.
    /// </summary>
    [Fact]
    public void AddGroupIsDisabledUntilEveryFieldIsSet()
    {
        var modal = new CreateGroupModal("Nike", _ => false);

        Assert.False(modal.CanAdd);          // no store, no name
        Assert.False(modal.AddButton.IsEnabled);

        modal.ChooseStore(0);                // a store, still no name
        Assert.False(modal.CanAdd);
        Assert.False(modal.AddButton.IsEnabled);

        modal.TypeName("probe");             // all three
        Assert.True(modal.CanAdd);
        Assert.True(modal.AddButton.IsEnabled);

        modal.TypeName("");                  // name removed again
        Assert.False(modal.CanAdd);
        Assert.False(modal.AddButton.IsEnabled);
    }

    /// <summary>
    /// The Add Group button must be in the tree, not merely constructed.
    ///
    /// <para>
    /// R71: the first version created the button, wired its handler, exposed it as a property, and
    /// never added it to the dialog — so the dialog opened with only a Close button while every
    /// assertion above still passed, because they asked the object rather than the screen. Found by
    /// opening the dialog in the replica. This test asks whether the control has a parent.
    /// </para>
    /// </summary>
    [Fact]
    public void TheAddGroupButtonIsActuallyInTheDialog()
    {
        var modal = new CreateGroupModal("Nike", _ => false);

        _out.WriteLine($"AddButton.Parent = {modal.AddButton.Parent?.GetType().Name ?? "<null>"}");

        Assert.NotNull(modal.AddButton.Parent);

        // And it is reachable from the dialog's own content, not parked somewhere else.
        var found = Descendants(modal).OfType<Button>().Any(b => ReferenceEquals(b, modal.AddButton));
        Assert.True(found, "Add Group is not in the content tree");
    }

    /// <summary>Walks a control's logical tree breadth-first.</summary>
    private static IEnumerable<Control> Descendants(Control root)
    {
        var queue = new Queue<Control>();
        queue.Enqueue(root);
        while (queue.Count > 0)
        {
            var current = queue.Dequeue();
            if (!ReferenceEquals(current, root)) yield return current;

            foreach (var child in Avalonia.LogicalTree.LogicalExtensions
                         .GetLogicalChildren(current).OfType<Control>())
                queue.Enqueue(child);
        }
    }

    /// <summary>A name already in use keeps the button disabled rather than creating a duplicate.</summary>
    [Fact]
    public void ADuplicateNameKeepsAddDisabled()
    {
        var taken = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { "probe" };
        var modal = new CreateGroupModal("Nike", taken.Contains);

        modal.ChooseStore(0);
        modal.TypeName("probe");
        _out.WriteLine($"canAdd(duplicate) = {modal.CanAdd}");
        Assert.False(modal.CanAdd);

        modal.TypeName("probe2");
        Assert.True(modal.CanAdd);
    }

    /// <summary>The dialog builds a group carrying Type and Store, which is what the caption needs.</summary>
    [Fact]
    public void TheDialogBuildsAGroupWithTypeAndStore()
    {
        var modal = new CreateGroupModal("Nike", _ => false);
        modal.ChooseStore(0);
        modal.TypeName("probe");

        var group = modal.Build();
        _out.WriteLine($"built: type={group.Type} store={group.Store} name={group.Name} display={group.Display}");

        Assert.Equal("Nike", group.Type);
        Assert.StartsWith("Nike ", group.Store);
        Assert.Equal("probe", group.Name);
        Assert.Equal($"{group.Store} - probe", group.Display);
    }

    /// <summary>
    /// <c>Accounts.Group.DeleteConfirm.*</c> — "Delete {0}?" /
    /// "Are you sure you want to delete the {0} account group?" / "Delete {0}".
    /// </summary>
    [Fact]
    public void DeletingAGroupSpeaksInTheLocalesWords()
    {
        var (title, message, action) = AccountGroupView.DeleteConfirm("Nike US - zz-probe");
        _out.WriteLine($"{title} / {action}");

        Assert.Equal("Delete Nike US - zz-probe?", title);
        Assert.Equal(
            "Are you sure you want to delete the Nike US - zz-probe account group?\nYou cannot undo this action.",
            message);
        Assert.Equal("Delete Nike US - zz-probe", action);
    }

    /// <summary>Group Settings starts on the current name and hands back what was typed.</summary>
    [Fact]
    public void GroupSettingsStartsOnTheCurrentName()
    {
        var view = new AccountGroupView(Group("Nike", "Nike US", "zz-probe"));
        _out.WriteLine($"chosen = {view.ChosenName}");
        Assert.Equal("zz-probe", view.ChosenName);
    }

    // ---------------------------------------------------------------- the table

    /// <summary>
    /// Both visible headers sort: click once ascending, again descending, and the glyph follows.
    /// The original draws the up/down glyph next to Email and Added.
    /// </summary>
    [Fact]
    public void TheHeadersSortBothWays()
    {
        var rows = new List<Account>
        {
            Make("b@example.com", new DateTime(2026, 3, 1)),
            Make("a@example.com", new DateTime(2026, 1, 1)),
            Make("c@example.com", new DateTime(2026, 2, 1)),
        };
        var grid = new AccountGrid(rows);

        Assert.Equal(new[] { "a@example.com", "b@example.com", "c@example.com" },
            grid.Ordered().Select(r => r.Email));
        Assert.Equal("↑", grid.SortGlyph(AccountGrid.AccountColumn.Email));
        Assert.Equal(string.Empty, grid.SortGlyph(AccountGrid.AccountColumn.Added));

        grid.SortBy(AccountGrid.AccountColumn.Added);
        _out.WriteLine("by added: " + string.Join(",", grid.Ordered().Select(r => r.Email)));
        Assert.Equal(new[] { "a@example.com", "c@example.com", "b@example.com" },
            grid.Ordered().Select(r => r.Email));

        grid.SortBy(AccountGrid.AccountColumn.Added);
        _out.WriteLine("by added desc: " + string.Join(",", grid.Ordered().Select(r => r.Email)));
        Assert.Equal(new[] { "b@example.com", "c@example.com", "a@example.com" },
            grid.Ordered().Select(r => r.Email));
        Assert.Equal("↓", grid.SortGlyph(AccountGrid.AccountColumn.Added));
    }

    /// <summary><c>Accounts.SearchPlaceholder</c> — the search box filters the table by email.</summary>
    [Fact]
    public void TheSearchBoxFiltersByEmail()
    {
        var rows = new List<Account> { Make("alpha@example.com"), Make("beta@example.com") };
        var grid = new AccountGrid(rows);

        grid.SetFilter("bet");
        _out.WriteLine("filtered: " + string.Join(",", grid.Ordered().Select(r => r.Email)));
        Assert.Equal(new[] { "beta@example.com" }, grid.Ordered().Select(r => r.Email));

        grid.SetFilter(null);
        Assert.Equal(2, grid.Ordered().Count);
    }

    /// <summary>
    /// The header checkbox selects everything. In the shipped build it toggles its own visual and
    /// nothing else; selecting is what it is for, so it selects here.
    /// </summary>
    [Fact]
    public void TheHeaderCheckboxSelectsEverything()
    {
        var rows = new List<Account> { Make("a@example.com"), Make("b@example.com"), Make("c@example.com") };
        var grid = new AccountGrid(rows);

        Assert.False(grid.AllSelected);

        grid.SelectAll();
        _out.WriteLine($"selected = {grid.SelectedAccounts.Count}, all = {grid.AllSelected}");

        Assert.Equal(3, grid.SelectedAccounts.Count);
        Assert.True(grid.AllSelected);
    }

    /// <summary>The eye in the password header flips every row at once.</summary>
    [Fact]
    public void TheHeaderEyeRevealsEveryRow()
    {
        var grid = new AccountGrid(new List<Account> { Make("a@example.com") });

        Assert.False(grid.RevealAll);
        grid.ToggleRevealAll();
        Assert.True(grid.RevealAll);
        grid.ToggleRevealAll();
        Assert.False(grid.RevealAll);
    }

    /// <summary>Delete asks the caller first when a confirm hook is supplied, and not otherwise.</summary>
    [Fact]
    public void DeleteConsultsTheConfirmHook()
    {
        var rows = new List<Account> { Make("a@example.com"), Make("b@example.com") };
        var asked = new List<int>();
        var grid = new AccountGrid(rows).WithDeleteConfirm(count =>
        {
            asked.Add(count);
            return false;   // the user changed their mind
        });

        grid.SelectAll();
        grid.DeleteSelectedCore();

        _out.WriteLine($"asked about {string.Join(",", asked)}; left {rows.Count}");
        Assert.Equal(new[] { 2 }, asked);
        Assert.Equal(2, rows.Count);

        var permissive = new AccountGrid(rows);
        permissive.SelectAll();
        permissive.DeleteSelectedCore();
        Assert.Empty(rows);
    }

    /// <summary>The row's pencil opens the caller's editor for that row.</summary>
    [Fact]
    public void ThePencilEditsOneRow()
    {
        var account = Make("a@example.com");
        Account? edited = null;
        var grid = new AccountGrid(new List<Account> { account }).WithEditor(a => edited = a);

        grid.EditAccount(account);
        _out.WriteLine($"edited = {edited?.Email}");
        Assert.Same(account, edited);
    }

    /// <summary>
    /// Same guard as the proxies table: the header and the rows have to reserve the same width for
    /// the toolbar column, or the columns drift apart.
    /// </summary>
    [Fact]
    public void TheHeaderAndTheRowsReserveTheSameToolbarWidth()
    {
        var actions = new StackPanel { Children = { new Button { Content = "Add Accounts" } } };
        var grid = new AccountGrid(new List<Account> { Make("a@example.com") }).WithHeaderActions(actions);
        var root = (DockPanel)grid.Content!;

        var header = (Grid)root.Children[0];
        var body = (StackPanel)((ScrollViewer)root.Children.OfType<ScrollViewer>().Single()).Content!;
        var row = body.Children.OfType<Grid>().First();

        Assert.Equal(header.ColumnDefinitions.Count, row.ColumnDefinitions.Count);

        var headerLast = header.ColumnDefinitions[header.ColumnDefinitions.Count - 1];
        var rowLast = row.ColumnDefinitions[row.ColumnDefinitions.Count - 1];

        _out.WriteLine($"header last = {headerLast.Width}, row last = {rowLast.Width}");

        Assert.True(headerLast.Width.IsAbsolute, "the toolbar column must be a fixed width");
        Assert.Equal(headerLast.Width.Value, rowLast.Width.Value);
    }
}
