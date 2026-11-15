using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Accounts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 62: <c>Accounts.Context.MoveTo</c>, and the two defects found on the way in.
///
/// <see cref="AccountGrid"/> took <c>IEnumerable&lt;Account&gt;</c> and called <c>ToList()</c>, so
/// anything it removed came off a copy — the same defect R59 fixed on <see cref="ProxyGrid"/>.
/// And its Delete item called <c>_rows.Remove</c> with no rebuild, so even a real removal would
/// have left the deleted row on screen.
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class AccountMoveTests
{
    private readonly ITestOutputHelper _out;

    public AccountMoveTests(ITestOutputHelper output) => _out = output;

    private static Account Make(string email, string groupId = "ga") => new()
    {
        Email = email,
        Password = "pw",
        GroupId = groupId,
        Created = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc),
    };

    /// <summary>
    /// Move updates both sides: the account leaves whichever group held it and joins the target,
    /// and its GroupId is repointed. Updating only one leaves the tree and the reference
    /// disagreeing.
    /// </summary>
    [Fact]
    public void MovingAnAccountUpdatesBothSides()
    {
        var account = Make("a@example.com", "ga");
        var groupA = new AccountGroup { Name = "A", Id = "ga", Accounts = { account } };
        var groupB = new AccountGroup { Name = "B", Id = "gb" };
        var groups = new List<AccountGroup> { groupA, groupB };

        // The confirm button's body, without needing a window.
        foreach (var group in groups) group.Accounts.Remove(account);
        groupB.Accounts.Add(account);
        account.GroupId = groupB.Id;

        _out.WriteLine($"A={groupA.Accounts.Count} B={groupB.Accounts.Count} GroupId={account.GroupId}");

        Assert.Empty(groupA.Accounts);
        Assert.Single(groupB.Accounts);
        Assert.Equal("gb", account.GroupId);

        // History stays with it.
        Assert.Equal("a@example.com", account.Email);
        Assert.Equal("pw", account.Password);
        Assert.Equal(new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc), account.Created);
    }

    /// <summary>Delete removes from the caller's list, not a copy.</summary>
    [Fact]
    public void DeletingRemovesFromTheCallersList()
    {
        var rows = new List<Account> { Make("a@example.com"), Make("b@example.com") };
        var changed = 0;
        var view = new AccountGrid(rows, () => changed++);

        view.DeleteAccount(rows[0]);

        _out.WriteLine($"left={rows.Count} changed={changed}");
        Assert.Single(rows);
        Assert.Equal("b@example.com", rows[0].Email);
        Assert.Equal(1, changed);
    }

    /// <summary>
    /// Move accounts to appears only when a mover was supplied, same rule as the proxy menu.
    /// R70: the label is the locale's <c>Accounts.Context.MoveTo</c> — "Move accounts to", with a
    /// lower-case "accounts" and no ellipsis. The old "Move To…" was invented.
    /// </summary>
    [Fact]
    public void MoveIsOnlyOfferedWithAMover()
    {
        var with = MenuLabels(new AccountGrid(new List<Account> { Make("a@example.com") })
            .WithMover(_ => Task.CompletedTask));
        var without = MenuLabels(new AccountGrid(new List<Account> { Make("a@example.com") }));

        _out.WriteLine($"with mover: {string.Join(" | ", with)}");
        _out.WriteLine($"without:    {string.Join(" | ", without)}");

        Assert.Contains("Move accounts to", with);
        Assert.DoesNotContain("Move accounts to", without);
    }

    /// <summary>The account menu copies credentials but never prints them.</summary>
    [Fact]
    public void TheMenuOffersBothCopyForms()
    {
        var labels = MenuLabels(new AccountGrid(new List<Account> { Make("a@example.com") }));

        _out.WriteLine($"menu: {string.Join(" | ", labels)}");
        Assert.Contains("Copy Password", labels);
        Assert.Contains("Copy Account", labels);
    }

    private static List<string> MenuLabels(AccountGrid view)
    {
        var root = (DockPanel)view.Content!;
        var scroll = root.Children.OfType<ScrollViewer>().Single();
        var body = (StackPanel)scroll.Content!;
        var row = body.Children.OfType<Grid>().First();

        return row.ContextMenu!.ItemsSource!.Cast<object>()
            .OfType<MenuItem>()
            .Select(m => m.Header?.ToString() ?? string.Empty)
            .ToList();
    }
}
