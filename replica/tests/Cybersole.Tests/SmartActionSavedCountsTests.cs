using System;
using System.Collections.Generic;
using Cybersole.Core.Reporting;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Behaviour probes for <see cref="SmartActionSavedCounts"/>, reimplemented from <c>sub_140600020</c> and
/// <c>sub_1406000E0</c>.
///
/// Three sentences per counter, and the boundary that matters is the one at a single item: it has its own sentence with
/// the digit written out, so "{0} Filters Saved" is only the text from two upwards. An implementation using
/// <c>count &lt;= 1</c> or a plural rule would get one of these wrong.
/// </summary>
public class SmartActionSavedCountsTests
{
    private readonly ITestOutputHelper _out;

    public SmartActionSavedCountsTests(ITestOutputHelper output) => _out = output;

    private static readonly Dictionary<string, string> Copy = new(StringComparer.Ordinal)
    {
        ["SmartActionsCreator.NoFilters"] = "No Filters",
        ["SmartActionsCreator.FilterOne"] = "1 Filter Saved",
        ["SmartActionsCreator.FiltersFormat"] = "{0} Filters Saved",
        ["SmartActionsCreator.NoActions"] = "No Actions",
        ["SmartActionsCreator.ActionOne"] = "1 Action Saved",
        ["SmartActionsCreator.ActionsFormat"] = "{0} Actions Saved",
    };

    private static string Filters(int n) => SmartActionSavedCounts.Filters(n, k => Copy[k]);
    private static string Actions(int n) => SmartActionSavedCounts.Actions(n, k => Copy[k]);

    [Theory]
    [InlineData(0, "No Filters")]
    [InlineData(1, "1 Filter Saved")]
    [InlineData(2, "2 Filters Saved")]
    [InlineData(7, "7 Filters Saved")]
    public void TheFiltersCounterSplitsAtZeroAndOne(int count, string expected)
    {
        _out.WriteLine(count + " -> " + expected);
        Assert.Equal(expected, Filters(count));
    }

    [Theory]
    [InlineData(0, "No Actions")]
    [InlineData(1, "1 Action Saved")]
    [InlineData(2, "2 Actions Saved")]
    public void TheActionsCounterSplitsTheSameWay(int count, string expected)
    {
        Assert.Equal(expected, Actions(count));
    }

    [Fact]
    // The sentence for one writes the digit itself, so it is not the format with 1 substituted.
    public void OneIsItsOwnSentenceNotTheFormat()
    {
        Assert.Equal("1 Filter Saved", Filters(1));
        Assert.NotEqual(string.Format("{0} Filters Saved", 1), Filters(1));
        Assert.NotEqual("1 Filters Saved", Filters(1));
    }

    [Fact]
    // Negative counts fall into the else branch and are formatted like any other non-zero, non-one value: the
    // decompiled condition is "non-zero, then equal to one", with no lower bound.
    public void ANegativeCountIsFormattedRatherThanTreatedAsNone()
    {
        Assert.Equal("-2 Filters Saved", Filters(-2));
    }
}
