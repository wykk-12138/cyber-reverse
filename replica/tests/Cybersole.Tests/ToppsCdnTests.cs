using System.Linq;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1305: the Topps CDN payload read as the type the image deserialises it into.
///
/// <para>
/// The seven property names come out of the reflection metadata the image still ships
/// (<c>get_X</c>/<c>Create_X</c>/<c>XPropInit</c> at 0x143351CB7… and the field names <c>_X</c> at
/// 0x143352084…). The serialised casing did not come out of it, so the interesting cases here are the
/// two spellings resolving to the same product — that is the behaviour, not an accident of the test.
/// </para>
/// </summary>
public sealed class ToppsCdnTests
{
    private const string PascalItem =
        "{\"PriceAmount\":\"12.50\",\"ProductImage\":\"img-a\",\"ProductVariant\":\"var-a\"," +
        "\"SelectedOption\":\"opt-a\",\"VariantImage\":\"vimg-a\"," +
        "\"ToppsCommerceProductUrl\":\"https://shop.topps.com/products/a\",\"JToken\":{}}";

    private const string CamelItem =
        "{\"priceAmount\":\"9.99\",\"productImage\":\"img-b\",\"productVariant\":\"var-b\"," +
        "\"selectedOption\":\"opt-b\",\"variantImage\":\"vimg-b\"," +
        "\"toppsCommerceProductUrl\":\"https://shop.topps.com/products/b\"}";

    [Fact]
    public void TheSevenPropertyNamesAreTheOnesInTheMetadata()
    {
        Assert.Equal(7, ToppsCdn.PropertyNames.Count);
        Assert.Equal("PriceAmount", ToppsCdn.PropertyNames[0]);
        Assert.Contains("ToppsCommerceProductUrl", ToppsCdn.PropertyNames);
        Assert.Contains("JToken", ToppsCdn.PropertyNames);

        Assert.Equal(4, ToppsCdn.ListPropertyNames.Count);
        Assert.Contains("ListToppsCommerceProduct", ToppsCdn.ListPropertyNames);
    }

    [Fact]
    public void ABareArrayIsTheList()
    {
        var items = ToppsCdn.Parse("[" + PascalItem + "]");

        Assert.Single(items);
        Assert.Equal("12.50", items[0].PriceAmount);
        Assert.Equal("var-a", items[0].ProductVariant);
        Assert.Equal("https://shop.topps.com/products/a", items[0].ToppsCommerceProductUrl);
    }

    [Theory]
    [InlineData("ListToppsCommerceProduct")]
    [InlineData("listToppsCommerceProduct")]
    [InlineData("LISTTOPPSCOMMERCEPRODUCT")]
    public void AnObjectWrappedListIsFoundUnderAnyCasingOfItsCarrierName(string carrier)
    {
        var items = ToppsCdn.Parse("{\"" + carrier + "\":[" + PascalItem + "," + CamelItem + "]}");

        Assert.Equal(2, items.Count);
    }

    /// <summary>
    /// The behaviour the casing Unknown buys: the same product reads the same whether the serializer
    /// emitted PascalCase or camelCase, so a capture is not needed before the reader is useful.
    /// </summary>
    [Fact]
    public void BothSpellingsReadIntoTheSameFields()
    {
        var pascal = ToppsCdn.Parse("[" + PascalItem + "]")[0];
        var camel = ToppsCdn.Parse("[" + CamelItem + "]")[0];

        Assert.Equal("12.50", pascal.PriceAmount);
        Assert.Equal("9.99", camel.PriceAmount);
        Assert.Equal("opt-a", pascal.SelectedOption);
        Assert.Equal("opt-b", camel.SelectedOption);
        Assert.Equal("vimg-b", camel.VariantImage);
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData("not json at all")]
    [InlineData("{\"unexpected\":true}")]
    [InlineData("[1,2,3]")]
    [InlineData(null)]
    public void AnythingElseIsAnEmptyListRatherThanACrash(string? payload)
    {
        Assert.Empty(ToppsCdn.Parse(payload));
    }

    [Fact]
    public async Task TheFlowRecordsTheShapeItRecognisedAndTheFirstProductUrl()
    {
        using var server = new TinyServer((_, _) => (200, "{\"ListToppsCommerceProduct\":[" + PascalItem + "]}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/collections/all" };
        ctx.Session.Vars["topps.input"] = "Product 1234-56";
        ctx.Session.Vars["topps.cdnOrigin"] = server.BaseUrl;

        var outcome = await new ShopifyFlow().FindProductCdnAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("ToppsCommerceProduct", ctx.Session.Vars["topps.schema"]);
        Assert.Equal("1", ctx.Session.Vars["topps.count"]);
        Assert.Equal("https://shop.topps.com/products/a", ctx.Session.Vars["topps.productUrl"]);
        Assert.Contains("/variants/topps-product.json", server.Requests[0].Path);
    }
}
