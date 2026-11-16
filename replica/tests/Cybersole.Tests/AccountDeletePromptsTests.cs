using System;
using System.Collections.Generic;
using Cybersole.Core.Reporting;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Behaviour probes for the two account delete confirmations, which are the family's clearest counter-example to a
/// shared shape: same three texts, same placeholder, different argument type and different guard.
/// </summary>
public class AccountDeletePromptsTests
{
    private readonly ITestOutputHelper _out;

    public AccountDeletePromptsTests(ITestOutputHelper output) => _out = output;

    private static readonly Dictionary<string, string> Copy = new(StringComparer.Ordinal)
    {
        ["Accounts.DeleteConfirm.TitleFormat"] = "Delete {0} accounts?",
        ["Accounts.DeleteConfirm.MessageFormat"] =
            "Are you sure you want to delete {0} accounts?\nYou cannot undo this action.",
        ["Accounts.DeleteConfirm.ActionFormat"] = "Delete ({0}) accounts",
        ["Accounts.Group.DeleteConfirm.TitleFormat"] = "Delete {0}?",
        ["Accounts.Group.DeleteConfirm.MessageFormat"] =
            "Are you sure you want to delete the {0} account group?\nYou cannot undo this action.",
        ["Accounts.Group.DeleteConfirm.ActionFormat"] = "Delete {0}",
    };

    private static (string Title, string Message, string Action)? Accounts(int count)
        => AccountDeletePrompts.Accounts(count, k => Copy[k]);

    private static (string Title, string Message, string Action) Group(string name)
        => AccountDeletePrompts.AccountGroup(name, k => Copy[k]);

    [Fact]
    // The accounts body tests the count and returns before building anything.
    public void AZeroSelectionBuildsNothingForAccounts()
    {
        Assert.Null(Accounts(0));
    }

    [Theory]
    [InlineData(1)]
    [InlineData(5)]
    public void AccountsSubstitutesACountIntoAllThreeTexts(int count)
    {
        var pair = Accounts(count);
        Assert.NotNull(pair);
        _out.WriteLine(pair!.Value.Title + " | " + pair.Value.Action);
        Assert.Equal("Delete " + count + " accounts?", pair.Value.Title);
        Assert.Contains("delete " + count + " accounts?", pair.Value.Message, StringComparison.Ordinal);
        Assert.Equal("Delete (" + count + ") accounts", pair.Value.Action);
    }

    [Fact]
    // The counter-example the family needed: the group variant has no value for which it builds nothing. Its guard
    // is the host window, not the name, so an empty name still yields texts.
    public void TheAccountGroupBuildsTextsEvenForAnEmptyName()
    {
        var pair = Group(string.Empty);
        Assert.Equal("Delete ?", pair.Title);
        Assert.Contains("the  account group?", pair.Message, StringComparison.Ordinal);
        Assert.Equal("Delete ", pair.Action);
    }

    [Fact]
    // The same placeholder carries a NAME here, not a count.
    public void TheAccountGroupSubstitutesItsName()
    {
        var pair = Group("Main");
        _out.WriteLine(pair.Title);
        Assert.Equal("Delete Main?", pair.Title);
        Assert.Contains("delete the Main account group?", pair.Message, StringComparison.Ordinal);
        Assert.Equal("Delete Main", pair.Action);
    }

    [Fact]
    // The two screens disagree about parenthesising: accounts puts the value in brackets in the action label,
    // account groups does not. Keeping both as shipped is the point.
    public void TheTwoScreensUseDifferentActionShapes()
    {
        Assert.Equal("Delete (3) accounts", Accounts(3)!.Value.Action);
        Assert.Equal("Delete Main", Group("Main").Action);
    }
}
