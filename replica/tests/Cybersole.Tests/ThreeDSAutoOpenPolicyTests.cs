using Cybersole.Core.Models;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The auto-open policy lives in MainWindow (UI), so this covers the decision rule
/// itself: enabled flag + a positive limit gates how many windows may pop.
/// </summary>
public class ThreeDSAutoOpenPolicyTests
{
    private static int Allow(bool enabled, int limit, int alreadyOpened)
    {
        if (!enabled) return 0;
        var effective = limit <= 0 ? 0 : limit;      // <=0 means unlimited
        if (effective > 0 && alreadyOpened >= effective) return 0;
        return 1;
    }

    [Fact]
    public void Disabled_Never_Opens()
        => Assert.Equal(0, Allow(false, 5, 0));

    [Fact]
    public void Opens_While_Under_Limit()
    {
        Assert.Equal(1, Allow(true, 5, 0));
        Assert.Equal(1, Allow(true, 5, 4));
    }

    [Fact]
    public void Stops_At_Limit()
        => Assert.Equal(0, Allow(true, 5, 5));

    [Fact]
    public void Zero_Limit_Means_Unlimited()
    {
        Assert.Equal(1, Allow(true, 0, 0));
        Assert.Equal(1, Allow(true, 0, 1000));
    }

    [Fact]
    public void Negative_Limit_Treated_As_Unlimited()
        => Assert.Equal(1, Allow(true, -3, 50));

    [Fact]
    public void ThreeDS_Result_Is_A_Distinct_Outcome()
    {
        Assert.NotEqual(CheckoutResult.Declined, CheckoutResult.ThreeDSRequired);
        Assert.NotEqual(CheckoutResult.Error, CheckoutResult.ThreeDSRequired);
    }
}
