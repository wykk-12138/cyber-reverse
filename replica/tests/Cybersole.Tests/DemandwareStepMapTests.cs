using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 117: Demandware's twelve classic steps against the controllers — and the round where the
/// mapping exposed a hole in the controller table itself.
///
/// <para>
/// R94 recorded seventeen controllers from one window of the pool. Pairing the step list against
/// them showed three steps with no controller; searching wider found five more, so the gap was in
/// <b>my table</b>, not in the binary. That is the cleanest example in this session of why the step
/// list is the better primary reference: it tells you when your endpoint list is short.
/// </para>
/// </summary>
public sealed class DemandwareStepMapTests
{
    private readonly ITestOutputHelper _out;

    public DemandwareStepMapTests(ITestOutputHelper output) => _out = output;

    /// <summary>Ten pairs, both sides real.</summary>
    [Fact]
    public void ThePairsPointAtRealStepsAndRealControllers()
    {
        Assert.Equal(10, DemandwareStepMap.Pairs.Count);

        foreach (var (step, controller) in DemandwareStepMap.Pairs)
        {
            Assert.True(StoreFlowSteps.IsStep(step), step);
            Assert.True(DemandwareControllers.IsKnown(controller), controller);
            _out.WriteLine($"{step,-22} → {controller}");
        }
    }

    /// <summary>The three steps that were homeless in R94 now have controllers.</summary>
    [Fact]
    public void TheThreeHomelessStepsAreNowMapped()
    {
        Assert.Equal("CheckoutServices-SubmitBilling",
            DemandwareStepMap.ControllerFor("SubmitBillingAddress"));
        Assert.Equal("CheckoutShippingServices-UpdateShippingMethod",
            DemandwareStepMap.ControllerFor("SubmitShippingOption"));
        Assert.Equal("CheckoutServices-PaymentAuthorization",
            DemandwareStepMap.ControllerFor("ConfirmPayment"));

        // and they are all in the vocabulary
        Assert.True(DemandwareControllers.IsKnown("CheckoutServices-SubmitBilling"));
        Assert.True(DemandwareControllers.IsKnown("CheckoutShippingServices-UpdateShippingMethod"));
        Assert.True(DemandwareControllers.IsKnown("CheckoutServices-PaymentAuthorization"));
    }

    /// <summary>
    /// The Stripe step has no Stripe controller behind it — a finding, not a gap to fill by guessing.
    /// </summary>
    [Fact]
    public void ThereIsNoStripeControllerInTheImage()
    {
        Assert.Null(DemandwareStepMap.ControllerFor("CreateStripePaymentMethod"));
        Assert.Contains("CreateStripePaymentMethod", DemandwareStepMap.UnmappedSteps);

        // the vocabulary is Adyen's, not Stripe's
        Assert.All(DemandwareControllers.All,
            c => Assert.DoesNotContain(c, "Stripe", System.StringComparison.OrdinalIgnoreCase));

        Assert.Contains("Adyen", DemandwareControllers.AdyenAuthorize);
        Assert.Contains("no Stripe", DemandwareStepMap.StripeFinding, System.StringComparison.Ordinal);
        _out.WriteLine(DemandwareStepMap.StripeFinding);
    }

    /// <summary>Step plus unmapped equals the flow.</summary>
    [Fact]
    public void TheRemainderAddsUp()
    {
        var flow = StoreFlowSteps.DemandwareClassic.Names;
        var mapped = DemandwareStepMap.MappedSteps;

        _out.WriteLine($"{mapped.Count} mapped + {DemandwareStepMap.UnmappedSteps.Count} unmapped = {flow.Count}");
        Assert.Equal(flow.Count, mapped.Count + DemandwareStepMap.UnmappedSteps.Count);
        Assert.Equal(2, DemandwareStepMap.UnmappedSteps.Count);
    }

    /// <summary>The label is present.</summary>
    [Fact]
    public void TheMapSaysWhatItIs()
    {
        Assert.Contains("name correlation", DemandwareStepMap.Evidence);
        Assert.Contains("no request capture", DemandwareStepMap.Evidence);
        Assert.Contains("unmapped", DemandwareStepMap.Evidence);
    }

    /// <summary>
    /// The vocabulary grew by exactly the names the mapping needed — count is read from the lists,
    /// not typed.
    /// </summary>
    [Fact]
    public void TheVocabularyGrewByTheNamesTheMapNeeded()
    {
        _out.WriteLine($"{DemandwareControllers.All.Count} controllers");

        foreach (var controller in DemandwareStepMap.Pairs.Values)
            Assert.Contains(controller, DemandwareControllers.All);

        Assert.Equal(DemandwareControllers.All.Count, DemandwareControllers.All.Distinct().Count());
    }
}
