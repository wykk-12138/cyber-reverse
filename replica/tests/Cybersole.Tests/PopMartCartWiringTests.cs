using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 123: Pop Mart's buying half, wired into the flow.
///
/// <para>
/// R122 found a six-method cart class beside the twenty-four-step draw class. Three of its six methods
/// now exist in <see cref="PopMartFlow"/> against real endpoints —
/// <c>GetCartDataList</c> → <c>shoppingCartDataList</c>, <c>FetchCoupons</c> → <c>coupons/list</c>,
/// <c>SubmitDiscount</c> → <c>coupons/verify</c> — and the two the endpoint family cannot serve
/// (<c>ClearCart</c>, <c>FetchAddress</c>) are left out rather than invented.
/// </para>
///
/// <para>
/// The shape matters more than the count: before this round the replica went
/// product → cart → buy and never read the cart it had built, so a coupon or an address could not
/// affect the order at all.
/// </para>
/// </summary>
public sealed class PopMartCartWiringTests
{
    private readonly ITestOutputHelper _out;

    public PopMartCartWiringTests(ITestOutputHelper output) => _out = output;

    private static string Flow()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        return File.ReadAllText(Path.Combine(dir!.FullName, "src", "Cybersole.Stores",
            "Flows", "PopMartFlow.cs"));
    }

    /// <summary>The three wired methods are overrides or helpers that use real endpoints.</summary>
    [Fact]
    public void TheThreeCartMethodsUseRealEndpoints()
    {
        var flow = Flow();

        Assert.Contains("GetCartAsync", flow);
        Assert.Contains("PopMartEndpoints.ShoppingCartDataList", flow);
        Assert.Contains("PopMartEndpoints.CouponsList", flow);
        Assert.Contains("PopMartEndpoints.CouponsVerify", flow);

        // and the constants resolve to the /shop/v1 paths this session recorded
        Assert.StartsWith("/shop/v1/", PopMartEndpoints.ShoppingCartDataList);
        Assert.StartsWith("/shop/v1/", PopMartEndpoints.CouponsList);
        Assert.StartsWith("/shop/v1/", PopMartEndpoints.CouponsVerify);

        _out.WriteLine("GetCart → shoppingCartDataList, FetchCoupons → coupons/list, SubmitDiscount → coupons/verify");
    }

    /// <summary>
    /// The cart read calls the coupons read, in the order the cart class does.
    /// </summary>
    [Fact]
    public void TheCartReadThenReadsCoupons()
    {
        var flow = Flow();

        var cartAt = flow.IndexOf("GetCartAsync", System.StringComparison.Ordinal);
        var callAt = flow.IndexOf("await FetchCouponsAsync(c, ct)", System.StringComparison.Ordinal);

        Assert.True(cartAt > 0);
        Assert.True(callAt > cartAt, "coupons should be read after the cart");

        _out.WriteLine($"cart at {cartAt}, coupons call at {callAt}");
    }

    /// <summary>
    /// <c>FetchCoupons</c> is a private helper, not an override — <c>StoreFlow</c> has no such step and
    /// inventing one would put a step in the vocabulary the binary never asks for.
    /// </summary>
    [Fact]
    public void FetchCouponsIsAHelperNotAnInventedStep()
    {
        var flow = Flow();

        Assert.Contains("private async Task<StepOutcome> FetchCouponsAsync", flow);
        Assert.DoesNotContain("public override async Task<StepOutcome> FetchCouponsAsync", flow);
    }

    /// <summary>
    /// A rejected coupon is not a failed order — the cart stays orderable, the way a non-raffle store
    /// stays checkout-capable.
    /// </summary>
    [Fact]
    public void ARejectedCouponStillLeavesAnOrderableCart()
    {
        var flow = Flow();

        Assert.Contains("discount\"] = \"absent\"", flow);
        Assert.Contains("applied", flow);
        Assert.Contains("rejected", flow);

        // no failure path for the discount step: it always returns success
        var discountAt = flow.IndexOf("SubmitDiscountAsync", System.StringComparison.Ordinal);
        var afterDiscount = flow.Substring(discountAt);
        var nextStep = afterDiscount.IndexOf("public override", System.StringComparison.Ordinal);
        var body = nextStep > 0 ? afterDiscount.Substring(0, nextStep) : afterDiscount;

        Assert.DoesNotContain("StepOutcome.Fail", body);
        _out.WriteLine("discount absent/applied/rejected, never Fail");
    }

    /// <summary>The two methods the endpoints cannot serve are absent, not invented.</summary>
    [Fact]
    public void TheUnservableMethodsAreAbsent()
    {
        var flow = Flow();

        // ClearCartAsync and FetchAddressAsync belong to the cart class but no endpoint serves them,
        // so PopMartFlow does not implement them
        Assert.DoesNotContain("ClearCartAsync", flow);
        Assert.DoesNotContain("FetchAddressAsync", flow);

        Assert.False(PopMartCartSteps.IsMember("ClearCart") &&
                     PopMartEndpoints.IsKnown("/shop/v1/cart/clear"));
        _out.WriteLine("ClearCart / FetchAddress left out: no endpoint in the family");
    }
}
