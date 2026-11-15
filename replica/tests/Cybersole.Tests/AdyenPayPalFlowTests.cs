using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 125: a sixth flow — Adyen/PayPal express checkout — found while asking whether the SCAPI
/// family was complete.
///
/// <para>
/// Two results came out of one question. The first is a negative that confirms R124: the
/// <c>/scapi/</c> family is exactly nine paths, with no order creation and no coupon — so the four
/// app-side steps really are endpoint-less.
/// </para>
///
/// <para>
/// The second is the flow itself, read with R119's discipline: the literal's first token
/// (<c>&lt;PlaceOrder&gt;d__32</c>) is the previous string's tail, so the flow is six steps at
/// ordinals 33–38, not seven with an ordinal list that cannot ascend. Unlike the Demandware app path,
/// this payment path <b>does</b> complete on one side.
/// </para>
/// </summary>
public sealed class AdyenPayPalFlowTests
{
    private readonly ITestOutputHelper _out;

    public AdyenPayPalFlowTests(ITestOutputHelper output) => _out = output;

    /// <summary>Six steps, ascending, distinct.</summary>
    [Fact]
    public void TheFlowHasSixSteps()
    {
        Assert.Equal(6, AdyenPayPalFlow.All.Count);
        Assert.Equal(6, AdyenPayPalFlow.Names.Distinct().Count());

        var ordinals = AdyenPayPalFlow.All.Select(s => s.Ordinal).ToList();
        Assert.Equal(ordinals.OrderBy(o => o), ordinals);
        Assert.Equal(33, ordinals[0]);
        Assert.Equal(38, ordinals[^1]);

        // consecutive: no helper gaps at all
        Assert.Equal(Enumerable.Range(33, 6), ordinals);

        foreach (var step in AdyenPayPalFlow.All) _out.WriteLine($"d__{step.Ordinal} {step.Name}");
    }

    /// <summary>The foreign tail token is recorded, and it is not a step.</summary>
    [Fact]
    public void TheTailTokenIsNotAStep()
    {
        Assert.False(AdyenPayPalFlow.IsStep("PlaceOrder"));
        Assert.Null(AdyenPayPalFlow.OrdinalOf("PlaceOrder"));

        Assert.Contains("previous literal's tail", AdyenPayPalFlow.TailToken);
        _out.WriteLine(AdyenPayPalFlow.TailToken);
    }

    /// <summary>The two controllers this flow pinned are in the vocabulary.</summary>
    [Fact]
    public void TheFlowPinnedTwoNewControllers()
    {
        Assert.True(DemandwareControllers.IsKnown("Adyen-SaveExpressShopperDetails"));
        Assert.True(DemandwareControllers.IsKnown("ShopperInfo-IP"));
        Assert.Equal("Adyen-SaveExpressShopperDetails",
            DemandwareControllers.AdyenSaveExpressShopperDetails);
        Assert.Equal("ShopperInfo-IP", DemandwareControllers.ShopperInfoIp);

        foreach (var c in AdyenPayPalFlow.Controllers)
        {
            Assert.True(DemandwareControllers.IsKnown(c), c);
            _out.WriteLine("controller: " + c);
        }
    }

    /// <summary>Both payment halves are present: Adyen's and PayPal's.</summary>
    [Fact]
    public void BothPaymentHalvesArePresent()
    {
        Assert.True(AdyenPayPalFlow.IsStep("SubmitPaymentPayPal"));
        Assert.True(AdyenPayPalFlow.IsStep("GetPayPalAccessToken"));
        Assert.True(AdyenPayPalFlow.IsStep("AdyenSession"));
        Assert.True(AdyenPayPalFlow.IsStep("ShowConfirmationPaymentFromComponent"));

        // the demandware classic flow also has PayPal steps; this is the express variant
        Assert.True(StoreFlowSteps.IsStep("SubmitPayment"));
        Assert.False(StoreFlowSteps.IsStep("SubmitPaymentPayPal"));
    }

    /// <summary>
    /// The negative that confirms R124: nine SCAPI paths, no orders, no coupon.
    /// </summary>
    [Fact]
    public void TheScapiFamilyIsNinePathsWithNoOrders()
    {
        Assert.Equal(9, ScapiEndpoints.All.Count);
        Assert.Equal(9, ScapiEndpoints.All.Distinct().Count());

        Assert.All(ScapiEndpoints.All,
            e => Assert.DoesNotContain("Order", e, System.StringComparison.OrdinalIgnoreCase));
        Assert.All(ScapiEndpoints.All,
            e => Assert.DoesNotContain("coupon", e, System.StringComparison.OrdinalIgnoreCase));

        _out.WriteLine("9 SCAPI paths: 7 ShopperBaskets + 2 ShopperLogin, no order, no coupon");
    }
}
