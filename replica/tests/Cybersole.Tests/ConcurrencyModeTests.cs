using System.Collections.Generic;
using Cybersole.Core.Models;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// ConcurrencyMode and the arithmetic the locale spells out for one of its modes.
///
/// <para>
/// R930. The third mode is Both, not Unlimited: the settings screen's three choices are named by locale entries ending
/// Maximum, Ratio and Both, and searching the image for a concurrency-scoped Unlimited found nothing. Both states its own
/// rule -- "whichever is greater" of the maximum and the ratio -- and that is the only specification of the arithmetic
/// recovered anywhere, so it is implemented once and these tests pin it.
/// </para>
/// </summary>
public class ConcurrencyModeTests
{
    /// <summary>The three values, in the order the settings screen shows them.</summary>
    [Fact]
    public void TheThreeValuesAreMaximumRatioAndBoth()
    {
        Assert.Equal(new[] { "Maximum", "Ratio", "Both" }, System.Enum.GetNames<ConcurrencyMode>());
    }

    /// <summary>Unlimited was invented; nothing in the image names a concurrency mode by that word.</summary>
    [Fact]
    public void ThereIsNoUnlimitedMode()
    {
        Assert.DoesNotContain("Unlimited", System.Enum.GetNames<ConcurrencyMode>());
    }

    /// <summary>Maximum caps at the maximum, and at the task count when there are fewer tasks than the cap.</summary>
    [Theory]
    [InlineData(100, 10, 0d, 10)]
    [InlineData(5, 10, 0d, 5)]
    [InlineData(100, 0, 0d, 100)]
    public void MaximumCapsAndFallsBackWhenUnset(int tasks, int max, double ratio, int expected)
    {
        Assert.Equal(expected, ConcurrencyLimit.Resolve(ConcurrencyMode.Maximum, tasks, max, ratio));
    }

    /// <summary>Ratio takes a fraction of the tasks, rounded down so a pool is not over-started.</summary>
    [Theory]
    [InlineData(100, 0.5d, 50)]
    [InlineData(101, 0.5d, 50)]
    [InlineData(10, 0.25d, 2)]
    [InlineData(10, 0d, 0)]
    [InlineData(10, 1d, 10)]
    public void RatioTakesAFloorOfTheCount(int tasks, double ratio, int expected)
    {
        Assert.Equal(expected, ConcurrencyLimit.Resolve(ConcurrencyMode.Ratio, tasks, 0, ratio));
    }

    /// <summary>
    /// The locale's own sentence: whichever is greater. Asserted both ways round, since a test that only covered one
    /// direction would pass against a maximum-only implementation.
    /// </summary>
    [Fact]
    public void BothTakesWhicheverIsGreater()
    {
        // ratio larger: 50 vs 10
        Assert.Equal(50, ConcurrencyLimit.Resolve(ConcurrencyMode.Both, 100, 10, 0.5d));
        // maximum larger: 40 vs 10
        Assert.Equal(40, ConcurrencyLimit.Resolve(ConcurrencyMode.Both, 100, 40, 0.1d));
        // equal, and never more than the tasks that exist
        Assert.Equal(10, ConcurrencyLimit.Resolve(ConcurrencyMode.Both, 10, 40, 0.5d));
    }

    /// <summary>No tasks means nothing to resolve, whatever the settings say.</summary>
    [Fact]
    public void NoTasksResolvesToZero()
    {
        foreach (var mode in System.Enum.GetValues<ConcurrencyMode>())
            Assert.Equal(0, ConcurrencyLimit.Resolve(mode, 0, 10, 0.5d));
    }

    /// <summary>The settings overload unpacks the object, so callers cannot disagree about which fields it reads.</summary>
    [Fact]
    public void TheSettingsOverloadMatchesTheScalarOne()
    {
        var s = new ConcurrencySettings { Mode = ConcurrencyMode.Both, Maximum = 12, Ratio = 0.4d };
        Assert.Equal(ConcurrencyLimit.Resolve(ConcurrencyMode.Both, 100, 12, 0.4d),
                     ConcurrencyLimit.Resolve(s.Mode, 100, s));
    }
}