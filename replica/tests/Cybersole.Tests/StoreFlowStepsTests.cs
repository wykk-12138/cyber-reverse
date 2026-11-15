using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 112: every store flow's step list, from the image's own string pool.
///
/// <para>
/// R111 found Nike's sixteen steps sitting in one adjacent run with compiler ordinals. The same run
/// holds the other stores: Pop Mart's twenty-four (draws, points, reservations), John Lewis's
/// seventeen (BFF handover and Stripe), and two Demandware flows — a classic twelve and a
/// fifteen-step one that keeps an <c>App</c> path and a <c>Dw</c> path alive side by side.
/// </para>
///
/// <para>
/// Each of these lines up with an endpoint family this session has already proven, which is why the
/// stores can be named rather than guessed: Pop Mart's steps match <c>/shop/v1/*</c> (R100), John
/// Lewis's match the BFF versions (R103), and the Demandware classic chain matches the controllers
/// (R94). The dual flow is the same story R101 found in the endpoints and R107 wired.
/// </para>
/// </summary>
public sealed class StoreFlowStepsTests
{
    private readonly ITestOutputHelper _out;

    public StoreFlowStepsTests(ITestOutputHelper output) => _out = output;

    /// <summary>Five flows with the counts the image gives them.</summary>
    [Fact]
    public void TheFiveFlowsHaveTheirImagesCounts()
    {
        foreach (var flow in StoreFlowSteps.All)
            _out.WriteLine($"{flow.Store,-20} {flow.Count} steps");

        Assert.Equal(16, StoreFlowSteps.Nike.Count);
        Assert.Equal(24, StoreFlowSteps.PopMart.Count);
        Assert.Equal(19, StoreFlowSteps.JohnLewis.Count);   // R119: FindProduct 21 + AddToCart 22
        Assert.Equal(12, StoreFlowSteps.DemandwareClassic.Count);
        Assert.Equal(15, StoreFlowSteps.DemandwareDual.Count);

        Assert.True(StoreFlowSteps.All.Count >= 5);   // R113 added three more
    }

    /// <summary>Every flow's ordinals ascend, and its names are distinct.</summary>
    [Fact]
    public void EveryFlowIsOrderedAndDistinct()
    {
        foreach (var flow in StoreFlowSteps.All)
        {
            var ordinals = flow.Steps.Select(s => s.Ordinal).ToList();
            Assert.Equal(ordinals.OrderBy(o => o), ordinals);
            Assert.Equal(flow.Count, flow.Names.Distinct().Count());
        }
    }

    /// <summary>Pop Mart's steps are the draw/points/reservation chain its API describes.</summary>
    [Fact]
    public void ThePopMartChainCoversDrawsPointsAndReservations()
    {
        var names = StoreFlowSteps.PopMart.Names;

        Assert.Contains("EnterDraw", names);
        Assert.Contains("FindMegaDraw", names);
        Assert.Contains("RedeemLuckPoints", names);
        Assert.Contains("EnterReservation", names);
        Assert.Contains("EnterExhibit", names);

        // 24 steps is far more than a checkout: it is a draw platform
        Assert.True(StoreFlowSteps.PopMart.Count > StoreFlowSteps.Nike.Count);
    }

    /// <summary>The dual Demandware flow keeps both paths — <c>App</c> and <c>Dw</c> variants.</summary>
    [Fact]
    public void TheDemandwareDualFlowKeepsBothPaths()
    {
        var names = StoreFlowSteps.DemandwareDual.Names;

        Assert.Contains("AddToCartApp", names);
        Assert.Contains("AddToCartAppDw", names);
        Assert.Contains("GetCartDw", names);
        Assert.Contains("SaveSessionDw", names);
        Assert.Contains("StartAppFast", names);
        Assert.Contains("StartAppSafe", names);

        // the same action twice, once per path
        var app = names.Count(n => n.EndsWith("App", System.StringComparison.Ordinal));
        var dw = names.Count(n => n.EndsWith("Dw", System.StringComparison.Ordinal));
        _out.WriteLine($"{app} App steps, {dw} Dw steps");

        Assert.True(app >= 3);
        Assert.True(dw >= 3);
    }

    /// <summary>The classic Demandware chain is the controller sequence R94 proved.</summary>
    [Fact]
    public void TheClassicDemandwareChainMatchesTheControllers()
    {
        var names = StoreFlowSteps.DemandwareClassic.Names;

        Assert.Contains("InitiateCheckout", names);
        Assert.Contains("GenerateCSRF", names);
        Assert.Contains("SubmitConsignment", names);
        Assert.Contains("ConfirmPayment", names);

        // consignment is the Salesforce word for a delivery, and it is a step, not an address
        Assert.Contains("SubmitBillingAddress", names);
        Assert.DoesNotContain("SubmitShippingAddress", names);
    }

    /// <summary>
    /// Round 113: three more flows, named for their evidence rather than for a brand.
    ///
    /// <para>
    /// The pool names no store for these three, so neither does the code. What it does record is what
    /// identifies them: a UK click-and-collect pair (<c>GetCollectPlusLocations</c> /
    /// <c>SubmitCollectPlus</c>) and an engine that issues a <b>structure token</b> before taking a
    /// payment, in two shapes (multi-variant and single).
    /// </para>
    /// </summary>
    [Fact]
    public void TheThreeUnnamedFlowsHaveTheirCounts()
    {
        Assert.Equal(17, StoreFlowSteps.CollectPlusApp.Count);
        Assert.Equal(15, StoreFlowSteps.StructureTokenMulti.Count);
        Assert.Equal(12, StoreFlowSteps.StructureTokenSingle.Count);

        foreach (var flow in new[]
                 {
                     StoreFlowSteps.CollectPlusApp, StoreFlowSteps.StructureTokenMulti,
                     StoreFlowSteps.StructureTokenSingle,
                 })
            _out.WriteLine($"{flow.Store,-24} {flow.Count} steps");
    }

    /// <summary>Eight flows in total now, all distinct.</summary>
    [Fact]
    public void ThereAreEightFlows()
    {
        Assert.Equal(8, StoreFlowSteps.All.Count);
        Assert.Equal(8, StoreFlowSteps.All.Select(f => f.Store).Distinct().Count());

        foreach (var flow in StoreFlowSteps.All)
        {
            var ordinals = flow.Steps.Select(s => s.Ordinal).ToList();
            Assert.Equal(ordinals.OrderBy(o => o), ordinals);
            Assert.Equal(flow.Count, flow.Names.Distinct().Count());
        }
    }

    /// <summary>The CollectPlus flow is the one with a click-and-collect pair, and it keeps App steps.</summary>
    [Fact]
    public void TheCollectPlusFlowIsRecognisableByItsPair()
    {
        var names = StoreFlowSteps.CollectPlusApp.Names;

        Assert.Contains("GetCollectPlusLocations", names);
        Assert.Contains("SubmitCollectPlus", names);
        Assert.Contains("GetPaymentUrl", names);

        // it keeps an app path beside the web steps
        Assert.Contains("FindProductApp", names);
        Assert.Contains("CreateCheckoutApp", names);

        // the pair appears in this flow only
        Assert.Equal("collectplus-app", StoreFlowSteps.FlowFor("SubmitCollectPlus")?.Store);
    }

    /// <summary>
    /// The two structure-token flows are one engine in two shapes: nine shared step names, different
    /// totals.
    /// </summary>
    [Fact]
    public void TheStructureTokenFlowsShareTenSteps()
    {
        var multi = StoreFlowSteps.StructureTokenMulti.Names.ToHashSet();
        var single = StoreFlowSteps.StructureTokenSingle.Names.ToHashSet();
        var shared = multi.Intersect(single).OrderBy(n => n).ToList();

        _out.WriteLine($"shared: {string.Join(", ", shared)}");

        // ten names are shared: the payment engine's spine. The count is read from the two lists,
        // not hand-counted — a hand count here was wrong twice (8, then "nine" in the test name).
        Assert.Equal(10, shared.Count);
        Assert.Equal(new[]
        {
            // R287: GetMerchantCode was in this list because structure-token-single wrongly carried it; the literal at
            // 0x034b23a5 has CalculateTaxes at 45 instead. The shared count stays ten.
            "CalculateTaxes", "CreateTransaction", "GetCheckout", "GetPayPalToken",
            "GetShippingRate", "GetStructureToken", "ProcessPayment", "SubmitPayment",
            "SubmitPayPal", "SubmitShipping",
        }, shared);
        // R287: GetMerchantCode is NOT shared — it belongs to the multi flow only (ordinal 38). Checking it was the
        // assertion that encoded the defect.
        Assert.DoesNotContain("GetMerchantCode", shared);
        Assert.Contains("CalculateTaxes", shared);
        Assert.Contains("ProcessPayment", shared);

        // R287: the difference is the multi-variant opening, NOT the tax step. CalculateTaxes sits at ordinal 45 in the
        // literal at 0x034b23a5, i.e. it belongs to BOTH shapes; the earlier assertion here ("CalculateTaxes is multi
        // only") was the same defect as the single flow's missing step, restated as a guard.
        Assert.Contains("FindProductMulti", multi);
        Assert.DoesNotContain("FindProductMulti", single);
        Assert.Contains("CalculateTaxes", multi);
        Assert.Contains("CalculateTaxes", single);
        Assert.Contains("GetMerchantCode", multi);
        Assert.DoesNotContain("GetMerchantCode", single);
        Assert.Contains("EditLine", single);
        Assert.DoesNotContain("EditLine", multi);

        // and they are distinct flows, not one
        Assert.NotEqual(StoreFlowSteps.StructureTokenMulti.Count,
            StoreFlowSteps.StructureTokenSingle.Count);
    }

    /// <summary>Every unnamed flow carries its identity evidence, and none claims a brand.</summary>
    [Fact]
    public void TheUnnamedFlowsCarryEvidenceNotBrands()
    {
        Assert.Equal(3, StoreFlowSteps.IdentityEvidence.Count);

        foreach (var (flow, evidence) in StoreFlowSteps.IdentityEvidence)
        {
            _out.WriteLine($"{flow}: {evidence}");
            Assert.False(string.IsNullOrWhiteSpace(evidence));
            Assert.DoesNotContain("is ", evidence, System.StringComparison.OrdinalIgnoreCase);
        }

        Assert.Contains("collectplus-app", StoreFlowSteps.IdentityEvidence.Keys);
    }

    /// <summary>Lookup by step name returns the flow it belongs to.</summary>
    [Fact]
    public void StepsResolveToTheirFlow()
    {
        Assert.Equal("nike", StoreFlowSteps.FlowFor("BeginCheckout")?.Store);
        Assert.Equal("popmart", StoreFlowSteps.FlowFor("FindMegaDraw")?.Store);
        Assert.Equal("johnlewis", StoreFlowSteps.FlowFor("GetStripePaymentIntent")?.Store);

        Assert.Null(StoreFlowSteps.FlowFor("NotAStep"));
        Assert.Null(StoreFlowSteps.FlowFor(null));
        Assert.False(StoreFlowSteps.IsStep("Checkout"));
        Assert.True(StoreFlowSteps.IsStep("EnterDraw"));
    }
}
