using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 124: the dual Demandware path is not two complete paths — and the split is the finding.
///
/// <para>
/// Pairing the fifteen dual steps against both endpoint families splits them three ways: three app
/// steps have an SCAPI endpoint, three dw steps have a classic controller, and four app steps have
/// neither. The reason for the fourth group is structural: <b>the SCAPI family in the image has no
/// orders endpoint</b> — six ShopperBaskets calls and two ShopperLogin calls, nothing that creates an
/// order. A store that starts on the app path must therefore cross back to the classic controllers to
/// finish.
/// </para>
///
/// <para>
/// This is also why <c>SubmitOrderAsync</c> in the replica's flow is classic-only: wiring an app-side
/// order would have meant inventing <c>/scapi/ShopperOrders/createOrder</c>, which the image does not
/// contain.
/// </para>
/// </summary>
public sealed class ScapiAppPathTests
{
    private readonly ITestOutputHelper _out;

    public ScapiAppPathTests(ITestOutputHelper output) => _out = output;

    /// <summary>Three app, three dw, four gaps — ten steps accounted for.</summary>
    [Fact]
    public void TheFifteenStepsSplitThreeWays()
    {
        Assert.Equal(3, ScapiAppPath.AppWithEndpoint.Count);
        Assert.Equal(3, ScapiAppPath.DwWithEndpoint.Count);
        Assert.Equal(4, ScapiAppPath.AppWithoutEndpoint.Count);
        Assert.Equal(10, ScapiAppPath.AccountedCount);

        foreach (var (step, url) in ScapiAppPath.AppWithEndpoint) _out.WriteLine($"app: {step} → {url}");
        foreach (var (step, url) in ScapiAppPath.DwWithEndpoint) _out.WriteLine($"dw:  {step} → {url}");
        foreach (var step in ScapiAppPath.AppWithoutEndpoint) _out.WriteLine($"gap: {step}");
    }

    /// <summary>Every paired step is a step of the dual flow, and every target exists.</summary>
    [Fact]
    public void ThePairsPointAtRealStepsAndRealEndpoints()
    {
        foreach (var (step, url) in ScapiAppPath.AppWithEndpoint)
        {
            Assert.True(StoreFlowSteps.IsStep(step), step);
            Assert.Contains(url, ScapiEndpoints.All);
        }

        foreach (var (step, url) in ScapiAppPath.DwWithEndpoint)
        {
            Assert.True(StoreFlowSteps.IsStep(step), step);
            Assert.True(DemandwareControllers.IsKnown(url), url);
        }

        foreach (var step in ScapiAppPath.AppWithoutEndpoint)
            Assert.True(StoreFlowSteps.IsStep(step), step);
    }

    /// <summary>
    /// The finding: no orders endpoint exists in the SCAPI family, so an app-path order cannot finish.
    /// </summary>
    [Fact]
    public void ThereIsNoScapiOrdersEndpoint()
    {
        Assert.All(ScapiEndpoints.All,
            e => Assert.DoesNotContain("Order", e, System.StringComparison.OrdinalIgnoreCase));

        // and the classic side does have one
        Assert.True(DemandwareControllers.IsKnown(DemandwareControllers.PlaceOrder));

        Assert.Contains("no orders endpoint", ScapiAppPath.NoOrdersEndpoint);
        Assert.Contains("cross back", ScapiAppPath.NoOrdersEndpoint);

        _out.WriteLine(ScapiAppPath.NoOrdersEndpoint);
    }

    /// <summary>The four app gaps are exactly the storefront-proxied steps.</summary>
    [Fact]
    public void TheFourAppGapsAreTheStorefrontProxiedSteps()
    {
        Assert.True(ScapiAppPath.IsAppGap("SubmitOrderApp"));
        Assert.True(ScapiAppPath.IsAppGap("GetCheckoutApp"));
        Assert.False(ScapiAppPath.IsAppGap("AddToCartApp"));

        Assert.True(ScapiAppPath.IsAppMapped("AddToCartApp"));
        Assert.True(ScapiAppPath.IsDwMapped("AddToCartAppDw"));
        Assert.False(ScapiAppPath.IsAppMapped(null));
    }

    /// <summary>The label says correlation, and names the alternative it refused.</summary>
    [Fact]
    public void TheLabelRefusesInventedPaths()
    {
        Assert.Contains("name correlation", ScapiAppPath.Evidence);
        Assert.Contains("no request capture", ScapiAppPath.Evidence);
        Assert.Contains("recorded, not given invented paths", ScapiAppPath.Evidence);
    }
}
