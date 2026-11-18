using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 103: John Lewis's BFF and Scheels's Frontastic hub, dumped before anything was written
/// against them.
///
/// <para>
/// <b>John Lewis</b> — twelve endpoints across <b>four</b> API versions. The billing address is on
/// v1, the payment page on v2, the delivery page on v3, the delivery address on v4. This is the
/// cleanest example in the session of why "one base URL + paths" is a modelling error: there is no
/// single base to pin.
/// </para>
///
/// <para>
/// <b>Scheels</b> — seventeen actions under one hub, and two of them are a fraud step-up
/// (<c>sendSignifydStepUpCode</c>, <c>completeSignifydStepUpCheckout</c>). An order cannot complete
/// until the code is sent and accepted; a flow that skips these looks like it is being declined.
/// </para>
/// </summary>
public sealed class RetailApiFamiliesTests
{
    private readonly ITestOutputHelper _out;

    public RetailApiFamiliesTests(ITestOutputHelper output) => _out = output;

    /// <summary>Twelve and seventeen — twenty-nine distinct URLs.</summary>
    [Fact]
    public void TheTwoFamiliesHaveTheirImagesCounts()
    {
        // R1137: 13 -> 14 -- the derived .../deliveries/methods endpoint is listed too.
        Assert.Equal(14, RetailApiFamilies.JohnLewisBff.All.Count);   // R129 guest callback, R1137 methods
        Assert.Equal(17, RetailApiFamilies.ScheelsFrontastic.All.Count);

        Assert.Equal(31, RetailApiFamilies.All.Count);   // R1137: 14 + 17
        Assert.Equal(31, RetailApiFamilies.All.Distinct().Count());
    }

    /// <summary>The John Lewis steps are split across four versions — no single base URL.</summary>
    [Fact]
    public void TheJohnLewisStepsSpanFourVersions()
    {
        var perVersion = RetailApiFamilies.JohnLewisBff.StepsPerVersion();

        foreach (var kv in perVersion) _out.WriteLine($"{kv.Key}: {kv.Value} step(s)");

        Assert.Equal(1, perVersion["v1"]);
        Assert.Equal(4, perVersion["v2"]);
        Assert.Equal(3, perVersion["v3"]);
        // R1137: 4 -> 5 -- the derived .../deliveries/methods URL is a v4 endpoint too.
        Assert.Equal(5, perVersion["v4"]);
        // R1137: 12 -> 13 -- the four buckets now hold the thirteen BFF literals plus the derived
        // methods URL (GuestLoginCallback sits outside bff/ and is counted separately).
        Assert.Equal(13, perVersion.Values.Sum());

        // every one really sits under the documented base
        // twelve sit under bff/, one sits beside it (the guest login callback, R129)
        Assert.All(RetailApiFamilies.JohnLewisBff.All.Where(u => u != RetailApiFamilies.JohnLewisBff.GuestLoginCallback),
            u => Assert.StartsWith("https://checkout.johnlewis.com/bff/v", u));
        Assert.StartsWith("https://checkout.johnlewis.com/callback/login/guest",
            RetailApiFamilies.JohnLewisBff.GuestLoginCallback);

        Assert.Equal("https://checkout.johnlewis.com/bff/v1/orderforms/payments/billing-address",
            RetailApiFamilies.JohnLewisBff.BillingAddressV1);
    }

    /// <summary>The Scheels hub is seventeen actions over four areas.</summary>
    [Fact]
    public void TheScheelsHubHasFourAreas()
    {
        var all = RetailApiFamilies.ScheelsFrontastic.All;
        Assert.All(all, u => Assert.StartsWith("https://apihub.scheels.com/frontastic/action/", u));

        var areas = all.Select(u => u.Split("/action/")[1].Split('/')[0])
            .Distinct().OrderBy(a => a).ToList();
        _out.WriteLine("areas: " + string.Join(", ", areas));

        Assert.Equal(new[] { "account", "adyen", "cart", "product" }, areas);

        Assert.Equal(5, all.Count(u => u.Contains("/account/")));
        Assert.Equal(2, all.Count(u => u.Contains("/adyen/")));
        Assert.Equal(9, all.Count(u => u.Contains("/cart/")));
        Assert.Equal(1, all.Count(u => u.Contains("/product/")));
    }

    /// <summary>
    /// The Signifyd step-up is part of the chain, not an optional extra — an order that skips it
    /// does not fail with an obvious error.
    /// </summary>
    [Fact]
    public void TheFraudStepUpIsInTheChain()
    {
        Assert.Contains(RetailApiFamilies.ScheelsFrontastic.SignifydStepUpCode,
            RetailApiFamilies.ScheelsFrontastic.Chain);
        Assert.Contains(RetailApiFamilies.ScheelsFrontastic.CompleteSignifydStepUp,
            RetailApiFamilies.ScheelsFrontastic.Chain);

        // and it comes after the details checkout that triggers it
        var chain = RetailApiFamilies.ScheelsFrontastic.Chain;
        var details = chain.ToList().IndexOf(RetailApiFamilies.ScheelsFrontastic.CompleteDetailsCheckout);
        var code = chain.ToList().IndexOf(RetailApiFamilies.ScheelsFrontastic.SignifydStepUpCode);
        var complete = chain.ToList().IndexOf(RetailApiFamilies.ScheelsFrontastic.CompleteSignifydStepUp);

        _out.WriteLine($"details={details} code={code} complete={complete}");
        Assert.True(details < code && code < complete);
    }

    /// <summary>Exact match only — a URL that merely shares a prefix is not "known".</summary>
    [Fact]
    public void KnownIsAnExactMatch()
    {
        Assert.True(RetailApiFamilies.IsKnown(RetailApiFamilies.ScheelsFrontastic.AddToCart));
        Assert.False(RetailApiFamilies.IsKnown("https://apihub.scheels.com/frontastic/action/cart/nope"));
        Assert.False(RetailApiFamilies.IsKnown(null));

        // the trailing-slash variant is its own literal in the image, and both are recorded
        Assert.True(RetailApiFamilies.IsKnown(RetailApiFamilies.JohnLewisBff.DeliveriesV4));
        Assert.True(RetailApiFamilies.IsKnown(RetailApiFamilies.JohnLewisBff.DeliveriesSlashV4));
        Assert.NotEqual(RetailApiFamilies.JohnLewisBff.DeliveriesV4,
            RetailApiFamilies.JohnLewisBff.DeliveriesSlashV4);
    }
}
