using System;
using System.Collections.Generic;
using Cybersole.Core.Reporting;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Behaviour probes for <see cref="TaskGroupPinLabel"/>, which reimplements <c>sub_1405C52E0</c>.
///
/// The decompiled condition is three-part — the read succeeded, the type tag matched, and the byte was non-zero — and
/// the third part decides the label. The type-tag part has no counterpart in the replica, which is recorded in the
/// source rather than pretended away.
/// </summary>
public class TaskGroupPinLabelTests
{
    private readonly ITestOutputHelper _out;

    public TaskGroupPinLabelTests(ITestOutputHelper output) => _out = output;

    private static readonly Dictionary<string, string> Copy = new(StringComparer.Ordinal)
    {
        ["TaskGroups.Context.PinFormat"] = "Pin {0}",
        ["TaskGroups.Context.UnpinFormat"] = "Unpin {0}",
    };

    private static string Describe(bool pinned, string name)
        => TaskGroupPinLabel.Describe(pinned, name, k => Copy[k]);

    [Theory]
    [InlineData(true, "Main", "Unpin Main")]
    [InlineData(false, "Main", "Pin Main")]
    public void TheLabelOffersTheOppositeOfTheCurrentState(bool pinned, string name, string expected)
    {
        _out.WriteLine(pinned + " -> " + expected);
        Assert.Equal(expected, Describe(pinned, name));
    }

    [Theory]
    [InlineData("")]
    [InlineData("Odd {0} name")]
    // The name is substituted as an argument, so a name containing a placeholder is not re-formatted.
    public void TheNameIsSubstituted(string name)
    {
        Assert.Equal("Pin " + name, Describe(false, name));
        Assert.Equal("Unpin " + name, Describe(true, name));
    }

    [Fact]
    public void ANullNameBehavesLikeAnEmptyOne()
    {
        Assert.Equal("Pin ", Describe(false, null!));
    }

    [Fact]
    // Two entries, one per state -- there is no third label and no plural rule here.
    public void TheTwoStatesUseTwoDistinctKeys()
    {
        Assert.NotEqual(Describe(true, "X"), Describe(false, "X"));
        Assert.StartsWith("Unpin", Describe(true, "X"), StringComparison.Ordinal);
        Assert.StartsWith("Pin", Describe(false, "X"), StringComparison.Ordinal);
    }
}
