using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 100: the Pop Mart storefront API — thirty-nine <c>/shop/v1/*</c> endpoints from the image.
///
/// <para>
/// The replica's flow posted to <c>/api/cart/add</c>, <c>/api/order/submit</c> and <c>/api/stock</c>.
/// None of the three is in the image. That is the fifth store family in this session where a
/// plausible-looking route was invented while the real one was a different shape entirely
/// (Nike <c>buy/orders/v2</c>, BSTN <c>/api/beast</c>, Demandware <c>Checkout-Submit</c>,
/// Shopify <c>cart/change.js</c>, and now this).
/// </para>
///
/// <para>
/// The names carry the flow the replica never had: a Pop Mart purchase is a <b>box set</b>. You pick a
/// series (<c>box_set/preview</c>), extract a position (<c>box_set/extract</c>), add the box list to
/// the basket (<c>boxCart/addBoxListToCart</c>), and pay at a per-provider cash desk
/// (<c>cash/desk/{adyen,alipayGlobal,paypal,stripe}</c>).
/// </para>
/// </summary>
public sealed class PopMartEndpointTests
{
    private readonly ITestOutputHelper _out;

    public PopMartEndpointTests(ITestOutputHelper output) => _out = output;

    /// <summary>Thirty-nine endpoints, all under <c>/shop/v1/</c>, all distinct.</summary>
    [Fact]
    public void TheImageCarriesThirtyNineEndpoints()
    {
        foreach (var e in PopMartEndpoints.All) _out.WriteLine(e);

        Assert.Equal(39, PopMartEndpoints.All.Count);
        Assert.Equal(39, PopMartEndpoints.All.Distinct().Count());
        Assert.All(PopMartEndpoints.All, e => Assert.StartsWith("/shop/v1/", e));
    }

    /// <summary>The purchase chain is present, in the order a buyer walks it.</summary>
    [Fact]
    public void ThePurchaseChainIsPresent()
    {
        Assert.Equal("/shop/v1/box/box_set/preview", PopMartEndpoints.BoxSetPreview);
        Assert.Equal("/shop/v1/box/box_set/extract", PopMartEndpoints.BoxSetExtract);
        Assert.Equal("/shop/v1/box/boxCart/addBoxListToCart", PopMartEndpoints.AddBoxListToCart);
        Assert.Equal("/shop/v1/order/pre/v2/buyNow", PopMartEndpoints.BuyNow);
        Assert.Equal("/shop/v1/shop/can/place/order", PopMartEndpoints.CanPlaceOrder);

        _out.WriteLine($"{PopMartEndpoints.BoxSetPreview} → {PopMartEndpoints.BoxSetExtract} → " +
                       $"{PopMartEndpoints.AddBoxListToCart} → {PopMartEndpoints.BuyNow}");
    }

    /// <summary>Four payment providers, each with its own cash-desk path.</summary>
    [Fact]
    public void EveryPaymentProviderHasACashDesk()
    {
        var desks = new[]
        {
            PopMartEndpoints.CashDeskAdyenPay,
            PopMartEndpoints.CashDeskAlipayGlobalPay,
            PopMartEndpoints.CashDeskPayPalPay,
            PopMartEndpoints.CashDeskStripePay,
        };

        _out.WriteLine(string.Join(", ", desks));
        Assert.Equal(4, desks.Length);
        Assert.All(desks, d => Assert.Contains(d, PopMartEndpoints.All));
        Assert.Equal("/shop/v1/shop/cash/desk/pay/query", PopMartEndpoints.CashDeskQuery);
    }

    /// <summary>The invented paths are not in the family — the assertion that keeps them out.</summary>
    [Fact]
    public void TheInventedPathsAreNotInTheFamily()
    {
        foreach (var invented in PopMartEndpoints.Invented)
        {
            _out.WriteLine($"{invented}: known={PopMartEndpoints.IsKnown(invented)}");
            Assert.False(PopMartEndpoints.IsKnown(invented));
        }

        Assert.True(PopMartEndpoints.IsKnown("/shop/v1/order/pre/v2/buyNow"));
    }

    /// <summary>The flow source no longer builds an invented path.</summary>
    [Fact]
    public void TheFlowUsesTheFamily()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        var source = File.ReadAllText(Path.Combine(dir!.FullName, "src", "Cybersole.Stores",
            "Flows", "PopMartFlow.cs"));

        foreach (var invented in PopMartEndpoints.Invented)
        {
            var live = source.Split('\n')
                .Where(l => l.Contains('"' + invented + '"', StringComparison.Ordinal)
                            && !l.TrimStart().StartsWith("//", StringComparison.Ordinal))
                .ToList();

            _out.WriteLine($"{invented}: {live.Count} live literal(s)");
            Assert.Empty(live);
        }

        Assert.Contains("PopMartEndpoints.AddBoxListToCart", source);
        Assert.Contains("PopMartEndpoints.BuyNow", source);
    }
}
