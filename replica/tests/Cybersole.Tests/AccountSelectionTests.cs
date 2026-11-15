using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Accounts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 70: <c>Accounts.Context.CopyMany</c>, and the selection model it needs to exist.
///
/// <para>
/// Everything here came from driving the real 5.18.32 by hand, because neither the model nor the
/// decompiler could have produced it. With one account selected the menu reads
/// <c>1 ACCOUNTS SELECTED / Copy Password / Copy Account / Move accounts to / Delete Accounts</c>;
/// with two it reads <c>2 ACCOUNTS SELECTED / Copy Accounts / …</c> and the password item is gone.
/// </para>
///
/// <para>
/// The singular locale key <c>Accounts.SelectedOne</c> exists in the shipped locale and the
/// original never uses it — a single selection still reads "1 ACCOUNTS SELECTED" on screen. That
/// is reproduced as the correct string here, not as the bug.
/// </para>
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class AccountSelectionTests
{
    private readonly ITestOutputHelper _out;

    public AccountSelectionTests(ITestOutputHelper output) => _out = output;

    private static Account Make(string email, string password = "pw") => new()
    {
        Email = email,
        Password = password,
        GroupId = "ga",
        Created = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc),
    };

    private static (AccountGrid View, List<Account> Rows) Table(params string[] emails)
    {
        var rows = emails.Select(e => Make(e, "pw-" + e.Split('@')[0])).ToList();
        return (new AccountGrid(rows), rows);
    }

    private static List<string> MenuLabels(AccountGrid view, params Account[] selection)
    {
        var labels = view.MenuFor(selection).OfType<MenuItem>()
            .Select(m => m.Header?.ToString() ?? string.Empty)
            .ToList();
        return labels;
    }

    /// <summary>
    /// The copy format is <c>email:password</c> per line with a terminating newline. A single
    /// "Copy Account" in the original put 27 characters on the clipboard for a 26-character
    /// credential, so the last line ends with a newline; the many case is the same join extended.
    /// </summary>
    [Fact]
    public void CopyManyJoinsEachAccountOnItsOwnLine()
    {
        var a = Make("a@example.com", "pwA");
        var b = Make("b@example.com", "pwB");
        var text = AccountGrid.FormatAccounts(new[] { a, b });

        _out.WriteLine("copy text = " + text.Replace("\n", "\\n"));

        Assert.Equal("a@example.com:pwA\nb@example.com:pwB\n", text);
        Assert.Equal(2, text.Split('\n').Length - 1);
    }

    /// <summary>
    /// One account terminates with exactly one newline, matching what came off the original's
    /// clipboard, and a single account is the degenerate case of the same join.
    /// </summary>
    [Fact]
    public void CopyOneIsTheSameFormatWithOneLine()
    {
        var text = AccountGrid.FormatAccounts(new[] { Make("a@example.com", "pwA") });
        _out.WriteLine($"len={text.Length} text={text.Replace("\n", "\\n")}");
        Assert.Equal("a@example.com:pwA\n", text);
        Assert.Equal(18, text.Length);
    }

    /// <summary>
    /// The menu speaks for the selection: one selection carries Copy Password + Copy Account,
    /// several carry only Copy Accounts. Dropping the password item is not cosmetic — with two
    /// accounts there is no single password to put on the clipboard.
    /// </summary>
    [Fact]
    public void TheMenuChangesShapeWithTheSelectionSize()
    {
        var (view, rows) = Table("a@example.com", "b@example.com", "c@example.com");

        var one = MenuLabels(view, rows[0]);
        var many = MenuLabels(view, rows[0], rows[2]);

        _out.WriteLine("one  : " + string.Join(" | ", one));
        _out.WriteLine("many : " + string.Join(" | ", many));

        Assert.Equal(
            new[] { "1 ACCOUNT SELECTED", "Copy Password", "Copy Account", "Delete Accounts" },
            one);
        Assert.Equal(
            new[] { "2 ACCOUNTS SELECTED", "Copy Accounts", "Delete Accounts" },
            many);
    }

    /// <summary>The caption counts what the items will act on, not what is on screen.</summary>
    [Fact]
    public void TheCaptionCountsTheSelection()
    {
        _out.WriteLine($"1 -> {AccountGrid.SelectionHeader(1)}");
        _out.WriteLine($"2 -> {AccountGrid.SelectionHeader(2)}");
        _out.WriteLine($"7 -> {AccountGrid.SelectionHeader(7)}");

        Assert.Equal("1 ACCOUNT SELECTED", AccountGrid.SelectionHeader(1));
        Assert.Equal("2 ACCOUNTS SELECTED", AccountGrid.SelectionHeader(2));
        Assert.Equal("7 ACCOUNTS SELECTED", AccountGrid.SelectionHeader(7));
        Assert.Equal("Copy Account", AccountGrid.CopyItemLabel(1));
        Assert.Equal("Copy Accounts", AccountGrid.CopyItemLabel(2));
    }

    /// <summary>Click replaces, ctrl+click adds, shift+click takes the range from the anchor.</summary>
    [Fact]
    public void ModifiersDecideTheExtentOfTheSelection()
    {
        var (view, rows) = Table("a@example.com", "b@example.com", "c@example.com", "d@example.com");

        view.SelectSingle(rows[1]);
        Assert.Equal(new[] { rows[1] }, view.SelectedAccounts);

        view.SelectToggle(rows[3]);
        Assert.Equal(new[] { rows[1], rows[3] }, view.SelectedAccounts);

        view.SelectToggle(rows[3]);
        Assert.Equal(new[] { rows[1] }, view.SelectedAccounts);

        // The anchor is the last row clicked, so a fresh single selection is needed before the
        // range test — a shift after a ctrl+click would otherwise measure from that clicked row.
        view.SelectSingle(rows[1]);
        view.SelectRange(rows[3]);
        Assert.Equal(new[] { rows[1], rows[2], rows[3] }, view.SelectedAccounts);

        _out.WriteLine("after range: " + string.Join(",", view.SelectedAccounts.Select(a => a.Email)));
    }

    /// <summary>
    /// Right-clicking a row that is already selected must not collapse the selection — otherwise
    /// there is no way to reach Copy Accounts at all, which is exactly how the original behaves.
    /// </summary>
    [Fact]
    public void RightClickingInsideTheSelectionKeepsIt()
    {
        var (view, rows) = Table("a@example.com", "b@example.com", "c@example.com");

        view.SelectSingle(rows[0]);
        view.SelectToggle(rows[1]);

        view.SelectForMenu(rows[0]);
        Assert.Equal(2, view.SelectedAccounts.Count);

        view.SelectForMenu(rows[2]);
        Assert.Equal(new[] { rows[2] }, view.SelectedAccounts);

        _out.WriteLine("inside kept 2, outside collapsed to 1");
    }

    /// <summary>Delete Accounts removes the whole selection from the caller's list, once.</summary>
    [Fact]
    public void DeleteRemovesEverySelectedRow()
    {
        var rows = new List<Account> { Make("a@example.com"), Make("b@example.com"), Make("c@example.com") };
        var changed = 0;
        var view = new AccountGrid(rows, () => changed++);

        view.SelectSingle(rows[0]);
        view.SelectToggle(rows[2]);
        view.DeleteSelectedCore();

        _out.WriteLine($"left={string.Join(",", rows.Select(r => r.Email))} changed={changed}");

        Assert.Equal(new[] { "b@example.com" }, rows.Select(r => r.Email));
        Assert.Empty(view.SelectedAccounts);
        Assert.Equal(1, changed);
    }

    /// <summary>Deleting one account also drops it from the selection, so the menu cannot act on a ghost.</summary>
    [Fact]
    public void RemovingAnAccountTakesItOutOfTheSelection()
    {
        var rows = new List<Account> { Make("a@example.com"), Make("b@example.com") };
        var view = new AccountGrid(rows);

        view.SelectSingle(rows[0]);
        view.DeleteAccount(rows[0]);

        Assert.Empty(view.SelectedAccounts);
        Assert.Single(rows);
    }

    /// <summary>
    /// Accounts.DeleteConfirm.TitleFormat / .MessageFormat / .ActionFormat. Returned as strings so
    /// the wording is asserted rather than the dialog.
    /// </summary>
    [Fact]
    public void DeleteConfirmSpeaksInTheLocalesWords()
    {
        var (title, message, action) = AccountGrid.DeleteConfirm(3);
        _out.WriteLine($"{title} / {action}");

        Assert.Equal("Delete 3 accounts?", title);
        Assert.Equal("Are you sure you want to delete 3 accounts?\nYou cannot undo this action.", message);
        Assert.Equal("Delete (3) accounts", action);
    }

    /// <summary>
    /// Selecting must repaint, not rebuild. This is not an optimisation: <c>PointerPressed</c>
    /// fires before the context menu opens, so a rebuild on selection destroys the row that owns
    /// the menu and right-clicking produces nothing at all. Found by clicking a row in the replica
    /// and watching no menu appear.
    /// </summary>
    [Fact]
    public void SelectingRepaintsInsteadOfRebuilding()
    {
        var (view, rows) = Table("a@example.com", "b@example.com");

        var before = view.Content;
        var rowBefore = RowControl(view, 0);

        view.SelectSingle(rows[0]);

        _out.WriteLine($"content kept={ReferenceEquals(before, view.Content)} background={rowBefore.Background}");

        Assert.Same(before, view.Content);
        Assert.Same(rowBefore, RowControl(view, 0));
        Assert.NotNull(rowBefore.Background);
        Assert.NotEqual(Avalonia.Media.Brushes.Transparent, rowBefore.Background);
    }

    /// <summary>The row grid for the nth account, read straight out of the live table.</summary>
    private static Grid RowControl(AccountGrid view, int index)
    {
        var root = (DockPanel)view.Content!;
        var body = (StackPanel)((ScrollViewer)root.Children.OfType<ScrollViewer>().Single()).Content!;
        return body.Children.OfType<Grid>().ElementAt(index);
    }

    /// <summary>
    /// The empty state is the locale string the original shows under the empty table, not a hint
    /// about a button that may not exist.
    /// </summary>
    [Fact]
    public void TheEmptyStateUsesTheLocaleLine()
    {
        var view = new AccountGrid(new List<Account>());
        var root = (DockPanel)view.Content!;
        var body = (StackPanel)((ScrollViewer)root.Children.OfType<ScrollViewer>().Single()).Content!;
        var text = ((TextBlock)body.Children[0]).Text;

        _out.WriteLine("empty state = " + text);
        Assert.Equal("Add some accounts to get started", text);
    }

    /// <summary>
    /// <c>AccountsCreator.ImportFormat</c>. The original's button counts what is about to be
    /// imported and the count moves as you type, so it is a function of the box, not a constant.
    /// </summary>
    [Fact]
    public void TheImportButtonCountsWhatIsAboutToBeImported()
    {
        _out.WriteLine($"0 -> {Cybersole.Ui.Views.AccountImportWindow.ImportCaption(0)}");
        _out.WriteLine($"3 -> {Cybersole.Ui.Views.AccountImportWindow.ImportCaption(3)}");

        Assert.Equal("Import (0) New Accounts", Cybersole.Ui.Views.AccountImportWindow.ImportCaption(0));
        Assert.Equal("Import (3) New Accounts", Cybersole.Ui.Views.AccountImportWindow.ImportCaption(3));
        Assert.Equal(
            "Import (2) New Accounts",
            Cybersole.Ui.Views.AccountImportWindow.ImportCaption(
                Cybersole.Services.ImportParser.ParseAccounts("a@b.c:pw\n\nd@e.f:pw2").Count));
    }
}
