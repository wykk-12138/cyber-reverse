using System.Linq;
using Cybersole.Core.Models;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R1076: the Nike buy-API request bodies, pinned to the two decompiled builders.
///
/// <para>
/// <c>sub_140B1DCC0</c> POSTs the preview, <c>sub_140B248A0</c> POSTs the checkout. Every
/// constant these tests assert was decoded out of the image with <c>names_at.py</c>:
/// <c>NIKECOM</c> (0x146E11460), <c>SHIP</c> (0x146E747F0), <c>address/shipping</c>
/// (0x146F6EAB0), <c>NOT_CALCULATED</c> (0x146E11E58), the <c>ASTLA</c>/<c>CA</c> state
/// sentinels (0x146B34B08 / 0x146B655C8) and the <c>discount_code</c> key (0x147006180).
/// </para>
///
/// <para>
/// Key order is asserted as well, because the two builders assemble in different orders —
/// the checkout reads its email <b>first</b>, the preview <b>last</b> — and that difference
/// is part of what the decompile established.
/// </para>
/// </summary>
public sealed class NikeBuyRequestTests
{
    private readonly ITestOutputHelper _out;
    public NikeBuyRequestTests(ITestOutputHelper output) => _out = output;

    private static (NikeFlow Flow, FlowContext Ctx) Context(
        string? state = "NY",
        string? country = "US",
        string marketplace = "US",
        Profile? profile = null,
        string? thread = null,
        string? discount = null)
    {
        var flow = new NikeFlow { CountryCode = marketplace };
        var ctx = new FlowContext
        {
            Http = null!,
            Url = "https://www.nike.com/launch/t/air-max-1",
            Shipping = new Address
            {
                FirstName = "Ada", LastName = "Lovelace",
                Address1 = "1 Analytical Way", Address2 = "Suite 2",
                City = "New York", State = state, ZipCode = "10001", Country = country,
            },
            ProfileData = profile ?? new Profile
            {
                Email = "ada@example.com", Phone = "+1 212 555 0100",
                JapaneseName = "エイダ", JapaneseSurname = "ラブレス",
            },
        };
        if (thread is not null) ctx.Session.Vars["thread"] = thread;
        if (discount is not null) ctx.Session.Vars["discount_code"] = discount;
        return (flow, ctx);
    }

    /// <summary>
    /// The preview request, in the builder's own key order, with the delivery block inline —
    /// the answer R1014 spent four rounds refusing to guess.
    /// </summary>
    [Fact]
    public void ThePreviewRequestCarriesTheDeliveryBlockInTheDecompiledOrder()
    {
        var (flow, ctx) = Context(thread: Thread());
        ctx.Session.Quantity = 2;
        var request = flow.BuildBuyRequest(ctx, checkout: false);

        var names = ((JObject)request).Properties().Select(p => p.Name).ToArray();
        Assert.Equal(new[] { "country", "currency", "locale", "channel", "items",
                             "promotionCodes", "email" }, names);

        Assert.Equal("US", request["country"]);
        Assert.Equal("USD", request["currency"]);
        Assert.Equal("en_US", request["locale"]);
        Assert.Equal("NIKECOM", request["channel"]);
        Assert.Equal("ada@example.com", request["email"]);

        // The preview always sends the code cell — null when the task has none.
        Assert.Equal(JTokenType.Null, request["promotionCodes"]![0]!.Type);

        var item = (JObject)request["items"]![0]!;
        Assert.Equal("sku-1", item["id"]);
        Assert.Equal("sku-1", item["skuId"]);
        Assert.Equal("prod-1", item["productId"]);
        Assert.Empty((JArray)item["offers"]!);
        Assert.Equal(2, item["quantity"]!.Value<int>());

        var fulfillment = item["fulfillmentDetails"]!;
        Assert.Equal("SHIP", fulfillment["type"]);
        Assert.Equal("address/shipping", fulfillment["location"]!["type"]);
        var postal = fulfillment["location"]!["postalAddress"]!;
        Assert.Equal("1 Analytical Way", postal["address1"]);
        Assert.Equal("Suite 2", postal["address2"]);
        Assert.Equal("10001", postal["postalCode"]);
        Assert.Equal("New York", postal["city"]);
        Assert.Equal("NY", postal["state"]);

        Assert.Equal("Ada", item["recipient"]!["firstName"]);
        Assert.Equal("Lovelace", item["recipient"]!["lastName"]);
        Assert.Equal("+1 212 555 0100", item["contactInfo"]!["phoneNumber"]);
        Assert.Equal("ada@example.com", item["contactInfo"]!["email"]);
    }

    /// <summary>
    /// The preview's priceInfo holds null where the server computes and zero where the client
    /// asserts nothing — exactly the placeholder cells the decompile shows.
    /// </summary>
    [Fact]
    public void ThePreviewPriceInfoUsesTheDecompiledPlaceholders()
    {
        var (flow, ctx) = Context(thread: Thread());
        var item = flow.BuildBuyItem(ctx, checkout: false, discount: null);

        var priceInfo = (JObject)item["itemCosts"]!["priceInfo"]!;
        var names = priceInfo.Properties().Select(p => p.Name).ToArray();
        Assert.Equal(new[] { "price", "fullPrice", "subtotal", "discount",
                             "valueAddedServices", "taxTotal", "total", "fullPriceTotal" }, names);

        foreach (var nullKey in new[] { "price", "fullPrice", "subtotal", "total", "fullPriceTotal" })
            Assert.Equal(JTokenType.Null, priceInfo[nullKey]!.Type);
        foreach (var zeroKey in new[] { "discount", "valueAddedServices", "taxTotal" })
            Assert.Equal(0, priceInfo[zeroKey]!.Value<int>());

        // The preview's promotion slot always carries the (possibly null) code cell.
        var discounts = (JArray)item["itemCosts"]!["promotionDiscounts"]!;
        Assert.Single(discounts);
        Assert.Equal(JTokenType.Null, discounts[0]!["code"]!.Type);

        // offers and valueAddedServices are the marker-only arrays — empty on the wire.
        Assert.Empty((JArray)item["offers"]!);
        Assert.Empty((JArray)item["valueAddedServices"]!);
    }

    /// <summary>
    /// The checkout request reads email first, carries the payment token, and appends the
    /// totals block exactly as sub_140B248A0 assembles it.
    /// </summary>
    [Fact]
    public void TheCheckoutRequestCarriesPaymentTokenEmailFirstAndTotals()
    {
        var (flow, ctx) = Context(thread: Thread());
        ctx.Session.PaymentToken = "tok-77";
        var request = flow.BuildBuyRequest(ctx, checkout: true);

        var names = ((JObject)request).Properties().Select(p => p.Name).ToArray();
        Assert.Equal(new[] { "email", "country", "currency", "locale", "channel", "items",
                             "paymentToken", "promotionCodes", "totals" }, names);

        Assert.Equal("ada@example.com", request["email"]);
        Assert.Equal("tok-77", request["paymentToken"]);
        Assert.Empty((JArray)request["promotionCodes"]!);   // no discount_code in the task

        Assert.Equal(
            "{\"total\":null,\"items\":{\"total\":null,\"details\":{\"price\":null,\"discount\":0}}," +
            "\"taxes\":{\"total\":0,\"details\":{" +
            "\"items\":{\"tax\":0,\"type\":\"NOT_CALCULATED\"}," +
            "\"shipping\":{\"type\":\"NOT_CALCULATED\"}," +
            "\"valueAddedServices\":{\"tax\":0,\"type\":\"NOT_CALCULATED\"}," +
            "\"fulfillment\":{\"tax\":0,\"type\":\"NOT_CALCULATED\"}}}," +
            "\"valueAddedServices\":{\"total\":0,\"details\":{\"price\":0,\"discount\":0}}," +
            "\"fulfillment\":{\"total\":null,\"details\":{\"price\":null,\"discount\":0}}}",
            request["totals"]!.ToString(Newtonsoft.Json.Formatting.None));
    }

    /// <summary>
    /// A task with a discount_code fills the checkout's promotion arrays the way the
    /// conditional block in sub_140B248A0's tail does — and the preview's unconditional cell.
    /// </summary>
    [Fact]
    public void ADiscountCodeFillsThePromotionArraysOnBothSides()
    {
        var (flow, ctx) = Context(thread: Thread(), discount: "SAVE10");

        var checkout = flow.BuildBuyRequest(ctx, checkout: true);
        Assert.Equal("SAVE10", checkout["promotionCodes"]![0]!.Value<string>());

        var checkoutItem = (JObject)checkout["items"]![0]!;
        var itemCostsNames = ((JObject)checkoutItem["itemCosts"]!).Properties()
            .Select(p => p.Name).ToArray();
        Assert.Equal(new[] { "priceInfo", "taxes", "promotionDiscounts" }, itemCostsNames);
        Assert.Equal("SAVE10",
            checkoutItem["itemCosts"]!["promotionDiscounts"]![0]!["code"]!.Value<string>());

        var preview = flow.BuildBuyRequest(ctx, checkout: false);
        Assert.Equal("SAVE10", preview["promotionCodes"]![0]!.Value<string>());
        Assert.Equal("SAVE10",
            ((JObject)preview["items"]![0]!)["itemCosts"]!["promotionDiscounts"]![0]!["code"]!
                .Value<string>());
    }

    /// <summary>
    /// The state sentinels: <c>ASTLA</c> and <c>CA</c> join country and state with a dash;
    /// any other state passes through untouched.
    /// </summary>
    [Theory]
    [InlineData("CA", "US-CA")]
    [InlineData("ASTLA", "US-ASTLA")]
    [InlineData("NY", "NY")]
    [InlineData(null, null)]
    public void TheStateSentinelsJoinCountryAndState(string? state, string? expected)
    {
        var (flow, ctx) = Context(state: state);
        var item = flow.BuildBuyItem(ctx, checkout: false, discount: null);
        var stateToken = item["fulfillmentDetails"]!["location"]!["postalAddress"]!["state"]!;
        Assert.Equal(expected, stateToken.Type == JTokenType.Null ? null : stateToken.Value<string>());
    }

    /// <summary>
    /// The checkout item decorates priceInfo with the price ids from the thread's merchPrice —
    /// the fields the original reads from its feed-filled context (ctx 30 / 31).
    /// </summary>
    [Fact]
    public void TheCheckoutItemCarriesPriceIdsFromTheThread()
    {
        var (flow, ctx) = Context(thread: Thread());
        var item = flow.BuildBuyItem(ctx, checkout: true, discount: null);

        Assert.Equal("price-9", item["itemCosts"]!["priceInfo"]!["priceId"]);
        Assert.Equal("snap-9", item["itemCosts"]!["priceInfo"]!["priceSnapshotId"]);

        var previewItem = flow.BuildBuyItem(ctx, checkout: false, discount: null);
        Assert.Null(previewItem["itemCosts"]!["priceInfo"]!["priceId"]);   // preview never carries it
    }

    /// <summary>
    /// The JP decoration: on the JP marketplace the checkout recipient gains the kana names
    /// and the postal address gains address3 = address2; the preview never decorates.
    /// </summary>
    [Fact]
    public void TheJapanMarketDecoratesTheCheckoutRecipientAndPostalAddress()
    {
        var (flow, ctx) = Context(marketplace: "JP", thread: Thread());

        var checkout = (JObject)flow.BuildBuyRequest(ctx, checkout: true)["items"]![0]!;
        Assert.Equal("エイダ", checkout["recipient"]!["altFirstName"]);
        Assert.Equal("ラブレス", checkout["recipient"]!["altLastName"]);
        Assert.Equal("Suite 2", checkout["fulfillmentDetails"]!["location"]!["postalAddress"]!["address3"]);

        var preview = (JObject)flow.BuildBuyRequest(ctx, checkout: false)["items"]![0]!;
        Assert.Null(preview["recipient"]!["altFirstName"]);
        Assert.Null(preview["fulfillmentDetails"]!["location"]!["postalAddress"]!["address3"]);
    }

    private static string Thread() =>
        "{\"productInfo\":[{" +
        "\"merchProduct\":{\"id\":\"prod-1\",\"styleColor\":\"DD1391-100\"}," +
        "\"merchPrice\":{\"currentPrice\":150,\"priceId\":\"price-9\",\"priceSnapshotId\":\"snap-9\"}}]}";
}
