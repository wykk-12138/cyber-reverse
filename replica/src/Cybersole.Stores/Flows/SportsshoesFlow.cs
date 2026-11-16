using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Sportsshoes — three hosts, and the division of labour between them is the interesting part.
///
/// <para>
/// R918. Thirteen literals name this store in the image, and they are not one API:
/// </para>
///
/// <code>
/// https://www.sportsshoes.com                    the storefront, where a product is read
/// https://sop.sportsshoes.com/cart/              cart state
/// https://sop.sportsshoes.com/cart/add/          adding to it
/// https://checkout.sportsshoes.com/api/storefront/checkout/     starting a checkout
/// https://checkout.sportsshoes.com/api/storefront/checkouts/    the plural, a second collection
/// https://checkout.sportsshoes.com/api/storefront/orders/       placing one
/// https://checkout.sportsshoes.com/api/storefront/payments/stripeocs   Stripe one-click
/// https://checkout.sportsshoes.com/internalapi/v1/checkout/order       an internal twin of the orders call
/// https://checkout.sportsshoes.com/checkout?setCurrencyId=1            the page, with a currency parameter
/// </code>
///
/// <para>
/// So a purchase crosses from the storefront to a separate <c>sop</c> host for the cart and then to a
/// <c>checkout</c> host for everything after it. That is why this is its own flow rather than a Demandware or Hybris
/// subclass: neither platform divides its work across hosts that way, and the endpoint family here is
/// <c>api/storefront</c>, which neither of them uses.
/// </para>
///
/// <para>
/// <b>What is not known.</b> No request body survives for any of these; what is recovered is the set of addresses and
/// two host roles. So each step below sends the smallest body the endpoint's name implies and reports an HTTP failure
/// rather than a success it cannot substantiate. The two order endpoints — <c>api/storefront/orders</c> and
/// <c>internalapi/v1/checkout/order</c> — are both present and neither is known to supersede the other, so the step
/// posts to the internal one and records which it used.
/// </para>
/// </summary>
public sealed class SportsshoesFlow : StoreFlow
{
    public override string Id => "sportsshoes";
    public override string Name => "Sportsshoes";

    /// <summary>
    /// All three hosts are claimed, because all three are part of buying here and a task pointed at any of them should
    /// route to this flow rather than fall through to nothing.
    /// </summary>
    public override IReadOnlyList<string> Domains => new[] { "www.sportsshoes.com", "sop.sportsshoes.com", "checkout.sportsshoes.com" };

    // ── the recovered addresses ───────────────────────────────────────────────
    internal const string StorefrontHost = "https://www.sportsshoes.com";
    internal const string CartHost = "https://sop.sportsshoes.com";
    internal const string CheckoutHost = "https://checkout.sportsshoes.com";

    internal const string Cart = "/cart/";
    internal const string CartAdd = "/cart/add/";
    internal const string CheckoutStart = "/api/storefront/checkout/";
    internal const string Checkouts = "/api/storefront/checkouts/";
    internal const string Orders = "/api/storefront/orders/";
    internal const string StripeOneClick = "/api/storefront/payments/stripeocs";
    internal const string InternalOrder = "/internalapi/v1/checkout/order";
    internal const string CheckoutPage = "/checkout?setCurrencyId=1";

    /// <summary>How many addresses were recovered, so a test can pin the set rather than a count of usages.</summary>
    internal const int RecoveredAddressCount = 9;

    /// <summary>
    /// The steps this flow can actually run. Three, because three endpoints have a clear enough meaning to send
    /// something: read the product, add to the cart, place the order.
    /// </summary>
    public override IReadOnlyList<string> StepSequence => new[] { "FindProduct", "AddToCart", "SubmitOrder" };

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "sportsshoes-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("sportsshoes product unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"sportsshoes product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;
        c.Session.Vars["product"] = Regex.Match(res.Body, @"""name""\s*:\s*""([^""]+)""").Groups[1].Value;
        return StepOutcome.Success();
    }

    /// <summary>
    /// The cart lives on its own host. A body carrying sku and quantity is the least the endpoint's name implies; the
    /// real one is unknown.
    /// </summary>
    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.VariantId))
            return StepOutcome.Fail("sportsshoes AddToCart needs a resolved variant and none was set");

        var body = new JObject
        {
            ["sku"] = c.Session.VariantId,
            ["quantity"] = c.Session.Quantity,
        };

        var res = await PostJsonAsync(c, CartHost + CartAdd, body.ToString(Newtonsoft.Json.Formatting.None),
            "sportsshoes-cart", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("sportsshoes cart host unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"sportsshoes cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// Posts the order to the internal endpoint and records which of the two order addresses it used, because the
    /// image holds both and nothing says which one a working purchase reaches.
    /// </summary>
    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.Vars.TryGetValue("cart", out var cart) || string.IsNullOrEmpty(cart))
            return StepOutcome.Fail("sportsshoes SubmitOrder has no cart in the session");

        var body = new JObject { ["cart"] = cart };
        var res = await PostJsonAsync(c, CheckoutHost + InternalOrder,
            body.ToString(Newtonsoft.Json.Formatting.None), "sportsshoes-order", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("sportsshoes checkout host unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"sportsshoes order HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["order"] = res.Body;
        c.Session.Vars["sportsshoes.orderPath"] = InternalOrder;
        return StepOutcome.Success();
    }
}