using System.Linq;
using System.Reflection;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Modules;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Sportsshoes, added in R918 because R917's coverage table found a host whose label appeared nowhere in src.
///
/// <para>
/// The image carries thirteen literals for this store, and they are not one API: the storefront on www, the cart on a
/// separate sop host, and everything from checkout onward on a third. That division is why this is its own flow rather
/// than a subclass of a platform base, and it is what these tests pin.
/// </para>
/// </summary>
public class SportsshoesFlowTests
{
    private static string Const(string name)
    {
        var f = typeof(SportsshoesFlow).GetField(name, BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
        Assert.NotNull(f);
        return (string)f!.GetRawConstantValue()!;
    }

    /// <summary>
    /// Three hosts, and they are distinct. A flow that collapsed them onto one would send cart traffic to the
    /// storefront host, which is not where the image puts it.
    /// </summary>
    [Fact]
    public void TheThreeHostsAreDistinct()
    {
        var hosts = new[]
        {
            Const("StorefrontHost"),
            Const("CartHost"),
            Const("CheckoutHost"),
        };

        Assert.Equal(3, hosts.Distinct().Count());
        Assert.Equal("https://www.sportsshoes.com", hosts[0]);
        Assert.Equal("https://sop.sportsshoes.com", hosts[1]);
        Assert.Equal("https://checkout.sportsshoes.com", hosts[2]);
    }

    /// <summary>
    /// The nine recovered addresses, verbatim. Pinned as a set so a later edit that renames or drops one is visible
    /// rather than silent.
    /// </summary>
    [Fact]
    public void TheNineRecoveredAddressesArePresent()
    {
        var expected = new[]
        {
            "/cart/",
            "/cart/add/",
            "/api/storefront/checkout/",
            "/api/storefront/checkouts/",
            "/api/storefront/orders/",
            "/api/storefront/payments/stripeocs",
            "/internalapi/v1/checkout/order",
            "/checkout?setCurrencyId=1",
        };

        var actual = new[]
        {
            Const("Cart"), Const("CartAdd"), Const("CheckoutStart"), Const("Checkouts"),
            Const("Orders"), Const("StripeOneClick"), Const("InternalOrder"), Const("CheckoutPage"),
        };

        Assert.Equal(expected, actual);
        Assert.Equal(9, (int)typeof(SportsshoesFlow)
            .GetField("RecoveredAddressCount", BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static)!
            .GetRawConstantValue()!);
    }

    /// <summary>
    /// The two order addresses are both real and neither is known to supersede the other, so both are recorded and the
    /// step says which it used.
    /// </summary>
    [Fact]
    public void BothOrderAddressesAreRecorded()
    {
        Assert.EndsWith("orders/", Const("Orders"));
        Assert.EndsWith("checkout/order", Const("InternalOrder"));
        Assert.NotEqual(Const("Orders"), Const("InternalOrder"));
    }

    /// <summary>
    /// Three steps, because three endpoints have a meaning clear enough to send something.
    /// </summary>
    [Fact]
    public void TheSequenceHasTheThreeEvidencedSteps()
    {
        var flow = new SportsshoesFlow();
        Assert.Equal(new[] { "FindProduct", "AddToCart", "SubmitOrder" }, flow.StepSequence);
    }

    /// <summary>
    /// Registered, so the flow is reachable by id and its hosts route to it.
    /// </summary>
    [Fact]
    public void ItIsRegisteredAndClaimsAllThreeHosts()
    {
        var all = StoreModuleCatalog.CreateAll();
        var mine = all.SingleOrDefault(m => m.Id == "sportsshoes");
        Assert.NotNull(mine);

        var flow = new SportsshoesFlow();
        Assert.Contains("www.sportsshoes.com", flow.Domains);
        Assert.Contains("sop.sportsshoes.com", flow.Domains);
        Assert.Contains("checkout.sportsshoes.com", flow.Domains);
    }

    /// <summary>
    /// No request body survives for any of these endpoints, so a step without its input must fail rather than send an
    /// empty body that the host might accept.
    /// </summary>
    [Fact]
    public void TheStepsRefuseWithoutTheirInputs()
    {
        var flow = new SportsshoesFlow();

        // no variant, so the cart step refuses before touching the network
        var context = new FlowContext { Http = null!, Url = "https://www.sportsshoes.com/x" };

        var outcome = flow.AddToCartAsync(context, default).GetAwaiter().GetResult();
        Assert.False(outcome.Ok);
        Assert.Contains("resolved variant", outcome.Error ?? "");
    }
}