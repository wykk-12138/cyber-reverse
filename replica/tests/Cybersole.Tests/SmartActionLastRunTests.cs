using System;
using System.Collections.Generic;
using Cybersole.Core.Reporting;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Behaviour probes for <see cref="SmartActionLastRun"/>, which reimplements <c>sub_14061E0E0</c>.
///
/// The decompiled body guards each property and returns zero for every mismatch, so a record that is missing a field
/// produces no label rather than one with a placeholder left in it. Those two early returns are the behaviour worth
/// pinning; the type-tag half of each guard has no counterpart in a typed model and is recorded in the source.
/// </summary>
public class SmartActionLastRunTests
{
    private readonly ITestOutputHelper _out;

    public SmartActionLastRunTests(ITestOutputHelper output) => _out = output;

    private static string? Format(string? action, int? count)
        => SmartActionLastRun.Format(action, count,
            k => "Triggered {0} ({1})");

    [Theory]
    [InlineData("Checkout", 1, "Triggered Checkout (1)")]
    [InlineData("Checkout", 12, "Triggered Checkout (12)")]
    [InlineData("Reload Profile", 0, "Triggered Reload Profile (0)")]
    public void TheLabelNamesTheActionAndItsCount(string action, int count, string expected)
    {
        _out.WriteLine(expected);
        Assert.Equal(expected, Format(action, count));
    }

    [Theory]
    [InlineData(null, 3)]
    [InlineData("Checkout", null)]
    [InlineData(null, null)]
    // Both properties are guarded, and the guard returns zero rather than substituting a blank.
    public void AMissingFieldProducesNoLabelAtAll(string? action, int? count)
    {
        Assert.Null(Format(action, count));
    }

    [Fact]
    // A count of zero is a real value and still produces a label; only a missing count suppresses it.
    public void ZeroIsALabelNotAnAbsence()
    {
        Assert.Equal("Triggered X (0)", Format("X", 0));
        Assert.Null(Format("X", null));
    }

    [Fact]
    // The name is inserted as an argument and is not re-scanned, so braces inside it survive literally.
    public void BracesInTheNameAreLiteral()
    {
        Assert.Equal("Triggered {0} (1)", Format("{0}", 1));
    }
}
