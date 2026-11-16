using System;
using System.Collections.Generic;
using Cybersole.Core.Reporting;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Behaviour probes for <see cref="SmartActionTriggerLabel"/>, reimplemented from <c>sub_1405FFFA0</c>.
///
/// Two sentences and no middle case. The cluster's other counter has three sentences because it counts; this one names,
/// so a single trigger is not a special case.
/// </summary>
public class SmartActionTriggerLabelTests
{
    private readonly ITestOutputHelper _out;

    public SmartActionTriggerLabelTests(ITestOutputHelper output) => _out = output;

    private static readonly Dictionary<string, string> Copy = new(StringComparer.Ordinal)
    {
        ["SmartActionsCreator.NoTrigger"] = "No Trigger",
        ["SmartActionsCreator.TriggerFormat"] = "{0} Trigger",
    };

    private static string Describe(string? trigger)
        => SmartActionTriggerLabel.Describe(trigger, k => Copy[k]);

    [Theory]
    [InlineData("Timer", "Timer Trigger")]
    [InlineData("Checkout Success", "Checkout Success Trigger")]
    public void TheLabelAppendsTriggerToTheName(string name, string expected)
    {
        _out.WriteLine(expected);
        Assert.Equal(expected, Describe(name));
    }

    [Fact]
    public void NoTriggerGetsItsOwnSentence()
    {
        Assert.Equal("No Trigger", Describe(null));
    }

    [Fact]
    // A name is not a count, so there is no "1 Trigger" case: an empty name still formats rather than falling back.
    public void AnEmptyNameStillFormats()
    {
        Assert.Equal(" Trigger", Describe(string.Empty));
        Assert.NotEqual("No Trigger", Describe(string.Empty));
    }

    [Fact]
    // And there is no third sentence to reach, unlike the saved-count counters which split at zero and one.
    public void TheTwoSentencesAreDistinctAndThatIsAllOfThem()
    {
        Assert.NotEqual(Describe(null), Describe("X"));
        Assert.Equal(2, Copy.Count);
    }
}
