using Cybersole.Ui.Views.Accounts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R392: the Accounts page copy the replica was missing, verbatim from the image's locale (Accounts.* in the string table).
///
/// <para>
/// A tool now measures this gap: <c>python tools/locale_text_gap.py Accounts</c> lists locale values whose exact text does
/// not appear anywhere in the replica's source. It reported ten strings on this page, all of them confirmations,
/// counters and the empty-search line. They live here as constants so the wording cannot drift.
/// </para>
/// </summary>
public sealed class AccountCopyTests
{
    private readonly ITestOutputHelper _out;
    public AccountCopyTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheConfirmationWordingIsTheImagesWording()
    {
        Assert.Equal("Delete {0} accounts?", AccountView.DeleteConfirmTitleFormat);
        Assert.Equal("Are you sure you want to delete {0} accounts?\nYou cannot undo this action.",
            AccountView.DeleteConfirmMessageFormat);
        Assert.Equal("Delete ({0}) accounts", AccountView.DeleteConfirmActionFormat);
        Assert.Equal("Edit ({0})", AccountView.EditPasswordTitleFormat);
    }

    [Fact]
    public void TheEmptySearchLineIsTheImagesLine()
    {
        Assert.Equal("There are no accounts matching your search", AccountView.NoResultsSubtitle);
        Assert.Equal("Delete Group", AccountView.DeleteGroupLabel);
    }

    [Theory]
    [InlineData(0, "0 Account Groups Loaded")]
    [InlineData(1, "1 Account Group Loaded")]
    [InlineData(3, "3 Account Groups Loaded")]
    public void TheGroupFooterSplitsOnOne(int count, string expected)
    {
        var text = AccountView.GroupsLoaded(count);
        _out.WriteLine(text);
        Assert.Equal(expected, text);
    }

    [Theory]
    [InlineData(1, "1 ACCOUNT SELECTED")]
    [InlineData(4, "4 ACCOUNTS SELECTED")]
    public void TheSelectionCounterSplitsOnOne(int count, string expected)
    {
        var text = AccountView.SelectionCaption(count);
        _out.WriteLine(text);
        Assert.Equal(expected, text);
    }
}
