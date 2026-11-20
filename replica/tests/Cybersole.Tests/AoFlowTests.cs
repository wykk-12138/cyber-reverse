using System.Linq;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1313: AO.com, the second store the catalogue was missing.
///
/// <para>
/// The endpoints are pinned because they are the finding: the image keeps the shop and the basket on
/// different hosts and names three checkout API paths — contact, delivery, payment. What this round does
/// NOT do is post to them, because their bodies are not in the image and a fabricated checkout payload is
/// the mistake this project has retracted most often. The last case pins that restraint rather than the
/// feature: the steps that would post fall through to the base class's own refusal.
/// </para>
/// </summary>
public sealed class AoFlowTests
{
    [Fact]
    public void TheCatalogueHasTheStore()
    {
        var modules = Cybersole.Stores.Modules.StoreModuleCatalog.CreateAll();

        var module = Assert.Single(modules.Where(m => m.Id == "ao"));
        Assert.Equal("AO", module.Name);
        Assert.Contains("ao.com", module.Domains);
    }

    [Fact]
    public void TheEndpointsAreTheLiteralsTheImageHolds()
    {
        Assert.Equal("https://ao.com", AoFlow.Origin);
        Assert.Equal("https://checkout.ao.com", AoFlow.CheckoutOrigin);
        Assert.Equal("/shoppingbasket.aspx", AoFlow.BasketPath);
        Assert.Equal("/v2/app/contact", AoFlow.ContactPath);
        Assert.Equal("/v2/app/delivery", AoFlow.DeliveryPath);
        Assert.Equal("/v2/app/payment", AoFlow.PaymentPath);
    }

    /// <summary>The basket is a different origin from the shop, which is the reason the constants exist.</summary>
    [Fact]
    public void TheBasketLivesOnTheCheckoutHost()
    {
        Assert.Equal("https://checkout.ao.com/shoppingbasket.aspx", AoFlow.BasketUrl());
        Assert.Equal("https://checkout.ao.com/v2/app/payment", AoFlow.StepUrl(AoFlow.PaymentPath));
        Assert.NotEqual(AoFlow.Origin, AoFlow.CheckoutOrigin);
    }

    [Fact]
    public async Task TheProductStepReadsNameAndPrice()
    {
        using var server = new TinyServer((_, _) =>
            (200, "<html><title>AO | Bosch Serie 4</title><script>{\"name\":\"Bosch Serie 4\",\"price\":\"449.00\"}</script></html>"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/product" };

        var outcome = await new AoFlow().FindProductAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("Bosch Serie 4", ctx.Session.Vars["product"]);
        Assert.Equal("449.00", ctx.Session.Vars["price"]);
        Assert.Equal("IN_STOCK", ctx.Session.Vars["stock"]);
    }

    [Fact]
    public async Task AnOutOfStockPageSaysSo()
    {
        using var server = new TinyServer((_, _) => (200, "<html><title>AO</title><p>Out of stock</p></html>"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/product" };

        await new AoFlow().FindProductAsync(ctx, default);

        Assert.Equal("OUT_OF_STOCK", ctx.Session.Vars["stock"]);
    }

    /// <summary>
    /// The restraint, pinned: the checkout steps are not overridden, so asking for one gets the base class's
    /// own failure rather than a request aimed at an endpoint whose body nobody has seen.
    /// </summary>
    [Fact]
    public async Task TheCheckoutStepsAreNotInvented()
    {
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = AoFlow.Origin + "/product" };

        var outcome = await new AoFlow().SubmitPaymentAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.DoesNotContain("v2/app", outcome.Error);
    }
}
