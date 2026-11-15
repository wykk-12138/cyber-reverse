using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 118: John Lewis's seventeen steps against its twelve BFF endpoints.
///
/// <para>
/// The first map with <b>more steps than endpoints</b>: fourteen steps reach nine endpoints, three
/// steps reach none, three endpoints are named by no step. A BFF endpoint is a resource and a step is
/// a client phase, so two steps sharing one endpoint is normal — not a mistake to "fix".
/// </para>
///
/// <para>
/// The three unmapped steps split into a page load and two Stripe calls, which is the mirror of
/// R117's demandware finding and is recorded as <c>StripeContrast</c>.
/// </para>
/// </summary>
public sealed class JohnLewisStepMapTests
{
    private readonly ITestOutputHelper _out;

    public JohnLewisStepMapTests(ITestOutputHelper output) => _out = output;

    /// <summary>Fourteen pairs, both sides real.</summary>
    [Fact]
    public void ThePairsPointAtRealStepsAndRealEndpoints()
    {
        Assert.Equal(14, JohnLewisStepMap.Pairs.Count);

        foreach (var (step, endpoint) in JohnLewisStepMap.Pairs)
        {
            Assert.True(StoreFlowSteps.IsStep(step), step);
            Assert.True(RetailApiFamilies.JohnLewisBff.All.Contains(endpoint), endpoint);
        }
    }

    /// <summary>Fourteen steps reach nine endpoints — the many-to-one shape is the reading.</summary>
    [Fact]
    public void MoreStepsThanEndpoints()
    {
        _out.WriteLine($"{JohnLewisStepMap.MappedSteps.Count} mapped steps → " +
                       $"{JohnLewisStepMap.Targets.Count} distinct endpoints");

        Assert.Equal(14, JohnLewisStepMap.MappedSteps.Count);
        Assert.Equal(9, JohnLewisStepMap.Targets.Count);
        Assert.True(JohnLewisStepMap.MappedSteps.Count > JohnLewisStepMap.Targets.Count);

        // the two shared endpoints, each serving two named steps
        Assert.Equal(2, JohnLewisStepMap.Pairs.Values
            .Count(v => v == RetailApiFamilies.JohnLewisBff.SessionHandoverV2));
        Assert.Equal(2, JohnLewisStepMap.Pairs.Values
            .Count(v => v == RetailApiFamilies.JohnLewisBff.DeliveriesV4));
    }

    /// <summary>The three unmapped steps are a page load and two Stripe calls.</summary>
    [Fact]
    public void TheUnmappedStepsAreAPageLoadAndTwoStripeCalls()
    {
        foreach (var step in JohnLewisStepMap.UnmappedSteps) _out.WriteLine("unmapped: " + step);

        // five, not three: R119 added FindProduct(21) and AddToCart(22) to the flow, and the BFF has
        // no cart endpoints at all — it starts at the handover.
        Assert.Equal(5, JohnLewisStepMap.UnmappedSteps.Count);
        Assert.Contains("GetHome", JohnLewisStepMap.UnmappedSteps);
        Assert.Contains("FindProduct", JohnLewisStepMap.UnmappedSteps);
        Assert.Contains("AddToCart", JohnLewisStepMap.UnmappedSteps);
        Assert.Contains("HandleRequiresAction", JohnLewisStepMap.UnmappedSteps);
        Assert.Contains("GetStripePaymentIntent", JohnLewisStepMap.UnmappedSteps);

        Assert.Null(JohnLewisStepMap.EndpointFor("GetStripePaymentIntent"));
        Assert.Null(JohnLewisStepMap.EndpointFor(null));
    }

    /// <summary>Fourteen mapped plus three unmapped is the seventeen-step flow.</summary>
    [Fact]
    public void TheRemainderAddsUp()
    {
        var flow = StoreFlowSteps.JohnLewis.Names;

        _out.WriteLine($"{JohnLewisStepMap.MappedSteps.Count} + {JohnLewisStepMap.UnmappedSteps.Count} = {flow.Count}");
        Assert.Equal(flow.Count, JohnLewisStepMap.MappedSteps.Count + JohnLewisStepMap.UnmappedSteps.Count);
    }

    /// <summary>Three endpoints are named by no step — one of them a trailing-slash duplicate.</summary>
    [Fact]
    public void TheUnusedEndpointsAreRecorded()
    {
        foreach (var endpoint in JohnLewisStepMap.UnusedEndpoints) _out.WriteLine("unused: " + endpoint);

        // four, not three: R129 added the guest login callback, which no step names
        Assert.Equal(4, JohnLewisStepMap.UnusedEndpoints.Count);
        Assert.Contains(RetailApiFamilies.JohnLewisBff.DeliveryAddressV4,
            JohnLewisStepMap.UnusedEndpoints);
        Assert.Contains(RetailApiFamilies.JohnLewisBff.DeliveriesSlashV4,
            JohnLewisStepMap.UnusedEndpoints);
    }

    /// <summary>The Stripe contrast with R117 is recorded, and the label says correlation.</summary>
    [Fact]
    public void TheMapSaysWhatItIsAndCitesTheContrast()
    {
        Assert.Contains("name correlation", JohnLewisStepMap.Evidence);
        Assert.Contains("no request capture", JohnLewisStepMap.Evidence);

        // the contrast is the mirror of the demandware finding and names both sides
        Assert.Contains("Stripe", JohnLewisStepMap.StripeContrast);
        Assert.Contains("Demandware", JohnLewisStepMap.StripeContrast);
        Assert.Contains("no Stripe controller", JohnLewisStepMap.StripeContrast);

        _out.WriteLine(JohnLewisStepMap.StripeContrast);
    }
}
