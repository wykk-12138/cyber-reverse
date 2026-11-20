using System.Linq;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1309: Saucony, the store the catalogue was missing.
///
/// <para>
/// The interesting assertions are the refusals. A flow that fetches a home page and a product page and
/// then declines the rest <em>by name</em> is a different claim from one that pretends to check out, and
/// these cases pin the difference: each undecoded step must name its own state-machine ordinal, so a
/// reader lands on the right function in the image instead of on a generic failure.
/// </para>
/// </summary>
public sealed class SauconyFlowTests
{
    [Fact]
    public void TheCatalogueCarriesTheStoreAndItsDomain()
    {
        var modules = Cybersole.Stores.Modules.StoreModuleCatalog.CreateAll();

        var module = Assert.Single(modules.Where(m => m.Id == "saucony"));
        Assert.Equal("Saucony", module.Name);
        Assert.Contains("saucony.com", module.Domains);
    }

    [Fact]
    public void TheFourStoreIdsAreTheOnesInTheImage()
    {
        Assert.Equal(new[] { "saucony_us", "saucony_ca", "saucony_eu", "saucony_europe" },
            SauconyFlow.StoreIds);
    }

    [Theory]
    [InlineData("https://www.saucony.com/collections/all", "saucony_us")]
    [InlineData("https://saucony.ca/products/x", "saucony_ca")]
    [InlineData("https://www.saucony.co.uk/products/x", "saucony_eu")]
    [InlineData("https://saucony.eu/products/x", "saucony_europe")]
    [InlineData("https://example.com/x", null)]
    [InlineData("", null)]
    public void TheStoreIdFollowsTheHost(string url, string? expected)
    {
        Assert.Equal(expected, SauconyFlow.StoreIdFor(url));
    }

    [Fact]
    public async Task TheHomeStepFetchesAndTheProductStepReportsWhatItFound()
    {
        using var server = new TinyServer((req, _) =>
            (req.RawUrl ?? string.Empty).Contains("/product", System.StringComparison.Ordinal)
                ? (200, "{\"name\":\"Endorphin Elite\",\"price\":\"225.00\"}")
                : (200, "<html>saucony</html>"));
        using var http = new NetClient { Transport = TransportMode.SChannel };

        var flow = new SauconyFlow();

        var home = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        Assert.True((await flow.GetHomeAsync(home, default)).Ok);

        var product = new FlowContext { Http = http, Url = server.BaseUrl + "/product/1" };
        Assert.True((await flow.FindProductAsync(product, default)).Ok);
        Assert.Equal("Endorphin Elite", product.Session.Vars["product"]);
        Assert.Equal("225.00", product.Session.Vars["price"]);
    }

    /// <summary>
    /// Each refusal names the image's ordinal. That is the whole point of the step: the next session
    /// should be able to open `<Name>d__NN` directly rather than re-deriving which step is missing.
    /// </summary>
    [Theory]
    [InlineData("AddToCart", "d__7")]
    [InlineData("SubmitShipping", "d__9")]
    [InlineData("SubmitBilling", "d__10")]
    [InlineData("SubmitOrder", "d__11")]
    public async Task TheUndecodedStepsRefuseWithTheirOrdinal(string step, string ordinal)
    {
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = "https://www.saucony.com/" };
        var flow = new SauconyFlow();

        var outcome = step switch
        {
            "AddToCart" => await flow.AddToCartAsync(ctx, default),
            "SubmitShipping" => await flow.SubmitShippingAsync(ctx, default),
            "SubmitBilling" => await flow.SubmitBillingAsync(ctx, default),
            _ => await flow.SubmitOrderAsync(ctx, default),
        };

        Assert.False(outcome.Ok);
        Assert.Contains(step, outcome.Error);
        Assert.Contains(ordinal, outcome.Error);
        Assert.Contains("endpoint unknown", outcome.Error);
    }

    [Fact]
    public void TheTwoStepsAfterTheOrderAlsoRefuseWithTheirOrdinals()
    {
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = "https://www.saucony.com/" };
        var flow = new SauconyFlow();

        var handled = flow.HandleOrderResult(ctx);
        Assert.False(handled.Ok);
        Assert.Contains("d__12", handled.Error);

        var payer = flow.PayerAuthenticate(ctx);
        Assert.False(payer.Ok);
        Assert.Contains("d__13", payer.Error);
    }
}
