using System;
using System.Collections.Generic;
using Cybersole.Core.Reporting;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Behaviour probes for <see cref="StoreGroupDeletePrompt"/>, which reimplements the text half of
/// <c>sub_140579E40</c>.
///
/// The templates are the shipped catalogue's; the choice between them comes from the decompiled branch, which tests
/// truthiness (<c>if (v6)</c>) rather than positivity. <see cref="ANegativeCountStillTakesTheInUseText"/> is the case
/// that separates the two readings; every realistic input lands on the same answer either way.
/// </summary>
public class StoreGroupDeletePromptTests
{
    private readonly ITestOutputHelper _out;

    public StoreGroupDeletePromptTests(ITestOutputHelper output) => _out = output;

    private static readonly Dictionary<string, string> Copy = new(StringComparer.Ordinal)
    {
        ["Utilities.StoreGroups.Delete.TitleFormat"] = "Delete {0}?",
        ["Utilities.StoreGroups.Delete.MessageFormat"] =
            "This will permanently delete the store group \"{0}\".",
        ["Utilities.StoreGroups.Delete.UsedMessageFormat"] =
            "This will permanently delete the store group \"{0}\".\nIt is used by {1} smart action filter(s), which will stop matching.",
    };

    private static (string Title, string Message) For(string name, int usedBy)
        => StoreGroupDeletePrompt.For(name, usedBy, k => Copy[k]);

    [Fact]
    public void TheTitleNamesTheGroup()
    {
        Assert.Equal("Delete Sizes?", For("Sizes", 0).Title);
        Assert.Equal("Delete Sizes?", For("Sizes", 4).Title);
    }

    [Fact]
    public void AnUnusedGroupGetsTheSingleClauseMessage()
    {
        var (_, message) = For("Sizes", 0);
        _out.WriteLine(message);
        Assert.Equal("This will permanently delete the store group \"Sizes\".", message);
        Assert.DoesNotContain("smart action", message, StringComparison.Ordinal);
    }

    [Theory]
    [InlineData(1)]
    [InlineData(4)]
    [InlineData(37)]
    public void AnInUseGroupGetsTheSecondClauseWithItsCount(int usedBy)
    {
        var (_, message) = For("Sizes", usedBy);
        _out.WriteLine(message);
        Assert.Contains("It is used by " + usedBy + " smart action filter(s)", message, StringComparison.Ordinal);
        Assert.StartsWith("This will permanently delete the store group \"Sizes\".", message, StringComparison.Ordinal);
    }

    [Fact]
    // The decompiled condition is `if (v6)` — truthiness. A positivity test would take the other branch here.
    public void ANegativeCountStillTakesTheInUseText()
    {
        var (_, message) = For("Sizes", -1);
        Assert.Contains("smart action filter(s)", message, StringComparison.Ordinal);
        Assert.Contains("-1", message, StringComparison.Ordinal);
    }

    [Fact]
    // The name is substituted, not concatenated, in both messages: a name that itself contains braces must not be
    // re-interpreted by the formatter.
    public void TheGroupNameIsASubstitutionArgument()
    {
        var (title, message) = For("Odd {0} name", 2);
        Assert.Equal("Delete Odd {0} name?", title);
        Assert.Contains("store group \"Odd {0} name\"", message, StringComparison.Ordinal);
        Assert.Contains("used by 2 smart", message, StringComparison.Ordinal);
    }
}
