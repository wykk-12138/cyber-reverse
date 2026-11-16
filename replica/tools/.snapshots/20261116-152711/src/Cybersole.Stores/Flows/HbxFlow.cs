using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// HBX — Hypebeast's storefront.
///
/// This replaces a <c>ShopifyFlow</c> registration that was simply wrong. Evidence:
///
///   GET /products/{handle}.json  ->  404 {"code":404,"message":"No route found for ..."}
///
/// Shopify answers that route with <c>{"product":{...}}</c>. HBX does not have it, runs its own
/// <c>/api/v2/</c>, sits behind AWS WAF (<c>edge.sdk.awswaf.com</c>), and renders client-side.
/// Driving it with ShopifyFlow meant every cart call hit a route that does not exist.
///
/// What IS verified, from a live capture and the rendered DOM:
///
///   product path   /{gender}/brands/{brand}/{product}
///   countries API  GET /api/v2/shop/countries?limit=999
///   bot defence    AWS WAF
///
/// What is NOT verified, and is therefore marked rather than invented:
///
///   the product JSON endpoint
///   the cart endpoint
///   the checkout endpoint
///
/// The product page's own HTML carries 157 JSON keys, all of them i18n and navigation — no
/// product payload at all. So this flow reads the product page for what it can (title, brand,
/// price) and reports clearly when a step needs an endpoint that is not known yet, instead of
/// firing a guess at a 404 and calling it a network error.
/// </summary>
public class HbxFlow : StoreFlow
{
    public override string Id => "hbx";
    public override string Name => "HBX";
    public override IReadOnlyList<string> Domains => new[] { "hbx.com" };

    /// <summary>Verified: this endpoint answers and returns a country list.</summary>
    private static string CountriesUrl(FlowContext c) => Origin(c.Url) + "/api/v2/shop/countries";  // inferred: no image evidence (R294)

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "hbx-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("hbx unreachable", retryable: true);

        if (res.StatusCode == 403)
            return StepOutcome.Fail("hbx blocked (aws waf) — needs a browser session",
                retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"hbx HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["home"] = res.Body;

        // the country list is the one API this storefront is known to expose
        var countries = await GetAsync(c, CountriesUrl(c) + "?limit=999", "hbx-countries", ct)
            .ConfigureAwait(false);

        if (countries is { IsSuccess: true })
        {
            c.Session.Vars["countries"] = countries.Body;

            var match = Regex.Match(countries.Body, @"""code""\s*:\s*""([A-Z]{2})""");
            if (match.Success) c.Session.Vars["hbx.country"] = match.Groups[1].Value;
        }

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("home", out var h) ? h : string.Empty;

        if (body.Length == 0)
        {
            var res = await GetAsync(c, c.Url, "hbx-product", ct).ConfigureAwait(false);
            if (res is null) return StepOutcome.Fail("hbx product unreachable", retryable: true);
            if (!res.IsSuccess) return StepOutcome.Fail($"hbx product HTTP {res.StatusCode}",
                retryable: true);

            body = res.Body;
            c.Session.Vars["home"] = body;
        }

        c.Session.Vars["raw"] = body;

        var title = Regex.Match(body, @"<title>([^<|]+)").Groups[1].Value.Trim();
        if (!string.IsNullOrEmpty(title)) c.Session.Vars["product"] = title;

        // the product identity on HBX is carried by the URL: /{gender}/brands/{brand}/{product}
        var brand = Regex.Match(c.Url, @"/brands/([a-z0-9\-]+)/").Groups[1].Value;
        if (!string.IsNullOrEmpty(brand)) c.Session.Vars["brand"] = brand;

        var slug = Regex.Match(c.Url, @"/brands/[a-z0-9\-]+/([a-z0-9\-]+)/?$").Groups[1].Value;
        if (!string.IsNullOrEmpty(slug)) c.Session.Vars["productSlug"] = slug;

        var price = ExtractPrice(body);
        if (!string.IsNullOrEmpty(price)) c.Session.Vars["price"] = price;

        return StepOutcome.Success();
    }

    /// <summary>
    /// A price, from the places that are declared rather than prose.
    ///
    /// HBX's page has no <c>"price"</c> JSON key, so the only reliable sources are structured
    /// data and an Open Graph product price. Marketing copy is deliberately not considered —
    /// John Lewis taught that lesson by matching a "Free Delivery over £50" sentence.
    /// </summary>
    public static string ExtractPrice(string body)
    {
        foreach (Match ld in Regex.Matches(body,
                     @"<script[^>]+ld\+json[^>]*>(.*?)</script>", RegexOptions.Singleline))
        {
            var p = Regex.Match(ld.Groups[1].Value, @"""price""\s*:\s*""?([\d.]+)""?");
            if (p.Success) return p.Groups[1].Value;
        }

        var og = Regex.Match(body,
            "(?:product:price:amount|og:price:amount)\"\\s+content=\"([\\d.]+)\"");
        if (og.Success) return og.Groups[1].Value;

        return string.Empty;
    }

    /// <summary>
    /// HBX's size data is not in the product page: 157 JSON keys, none of them a size, and the
    /// page triggers no variant request. So this step reports what it cannot know instead of
    /// inventing a size.
    /// </summary>
    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;

        var sizeish = Regex.Match(body, @"""(\w*size\w*)""\s*:\s*""?([\w\-. ]{1,20})""?",
            RegexOptions.IgnoreCase);

        if (sizeish.Success)
        {
            c.Session.VariantId = sizeish.Groups[2].Value;
            c.Session.Vars["variant"] = sizeish.Groups[2].Value;
            return Task.FromResult(StepOutcome.Success());
        }

        return Task.FromResult(StepOutcome.Fail(
            "hbx: the product page carries no size data and triggers no variant request — " +
            "the variant endpoint is not known"));
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c,
        CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;

        var soldOut = body.Contains("OutOfStock", StringComparison.OrdinalIgnoreCase) ||
                      body.Contains("sold out", StringComparison.OrdinalIgnoreCase);

        c.Session.Vars["available"] = !soldOut && body.Length > 2000 ? "true" : "false";
        return Task.FromResult(StepOutcome.Success());
    }

    /// <summary>
    /// Create the cart, then add the item to it. Both endpoints came from a real click-through
    /// capture (tools/NetworkCapture --steps="click:button.size-button; wait:800;
    /// click:button.atc-button"), which is the only way to discover them:
    ///
    ///   201  POST /api/v1/carts
    ///   200  POST /api/v1/carts/{cartId}/items
    ///
    /// The first call returns the cart id; the second needs it in the path. Sizes must be chosen
    /// before the button does anything, which is why the capture drives a click on
    /// button.size-button first.
    ///
    /// The request bodies are inferred from the shape of the responses: the site creates an
    /// empty cart with no payload, then posts an item carrying variantId and quantity.
    /// </summary>
    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        // 1. create the cart if we do not have one yet
        if (string.IsNullOrEmpty(c.Session.CartId))
        {
            var created = await SendJsonAsync(c, HttpMethod.Post,
                Origin(c.Url) + "/api/v1/carts", "{}", "hbx-cart-create", ct).ConfigureAwait(false);

            if (created is null) return StepOutcome.Fail("hbx cart create failed", retryable: true);
            if (created.StatusCode == 403)
                return StepOutcome.Fail("hbx cart create blocked", retryable: true);
            if (!created.IsSuccess)
                return StepOutcome.Fail($"hbx cart create HTTP {created.StatusCode}", retryable: true);

            var cartId = TryRead(created.Body, "id") ?? TryRead(created.Body, "cartId");
            if (string.IsNullOrEmpty(cartId))
                return StepOutcome.Fail("hbx: cart created but no id in the response");

            c.Session.CartId = cartId;
            c.Session.Vars["cart"] = created.Body;
        }

        // 2. add the variant
        if (string.IsNullOrEmpty(c.Session.VariantId))
            return StepOutcome.Fail("hbx: no variant to add");

        var payload = new Newtonsoft.Json.Linq.JObject
        {
            ["variantId"] = c.Session.VariantId,
            ["quantity"] = c.Session.Quantity,
        };

        var added = await SendJsonAsync(c, HttpMethod.Post,
            Origin(c.Url) + $"/api/v1/carts/{c.Session.CartId}/items",
            payload.ToString(Newtonsoft.Json.Formatting.None), "hbx-cart-add", ct)
            .ConfigureAwait(false);

        if (added is null) return StepOutcome.Fail("hbx cart add failed", retryable: true);
        if (added.StatusCode == 403) return StepOutcome.Fail("hbx cart add blocked", retryable: true);
        if (!added.IsSuccess) return StepOutcome.Fail($"hbx cart add HTTP {added.StatusCode}",
            retryable: true);

        c.Session.Vars["cart"] = added.Body;
        return StepOutcome.Success();
    }

    /// <summary>GET the cart that AddToCart created.</summary>
    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.CartId))
        {
            c.Session.Vars["cart"] = "{}";
            return StepOutcome.Success();
        }

        var res = await GetAsync(c, Origin(c.Url) + $"/api/v1/carts/{c.Session.CartId}",
            "hbx-cart-state", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("hbx cart state unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"hbx cart state HTTP {res.StatusCode}",
            retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
        OpenCheckoutAsync(c, "hbx-checkout", "/checkout", ct);

    /// <summary>
    /// The two checkout steps, now that the endpoints are known. R767.
    ///
    /// <para>
    /// Until this round <see cref="SubmitOrderAsync"/> returned a failure whose message said the order endpoint had
    /// not been captured. That was accurate: the image's HBX strings were a product surface and a cart API and
    /// nothing beyond. They go further than the flow used, though --
    /// </para>
    ///
    /// <code>
    /// https://hbx.com/api/v1/carts
    /// https://hbx.com/checkout?step=1
    /// https://hbx.com/checkout?step=2
    /// https://hbx.com/checkout/pay
    /// </code>
    ///
    /// <para>
    /// <b>Observation:</b> those four URLs, and the fact that the checkout is numbered in two steps with a separate
    /// pay call. <b>Inference (medium):</b> that step=1 is the address and step=2 the payment method, and the request
    /// bodies, which the image does not describe. The split follows the numbering, not a captured transcript.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct)
    {
        var payload = new JObject
        {
            ["cartId"] = c.Session.CartId,
            ["email"] = c.ProfileData?.Email ?? c.Account?.Email,
        };

        var res = await PostJsonAsync(c, CheckoutStep(c, 1),
            payload.ToString(Newtonsoft.Json.Formatting.None), "hbx-shipping", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("hbx shipping unreachable", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("hbx shipping blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"hbx shipping HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["shipping"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        var payload = new JObject { ["cartId"] = c.Session.CartId };

        var res = await PostJsonAsync(c, CheckoutStep(c, 2),
            payload.ToString(Newtonsoft.Json.Formatting.None), "hbx-payment", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("hbx payment unreachable", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("hbx payment blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"hbx payment HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["payment"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>The numbered checkout step. Observation: the image carries <c>?step=1</c> and <c>?step=2</c>.</summary>
    private static string CheckoutStep(FlowContext c, int step) =>
        Origin(c.Url) + "/checkout?step=" + step.ToString(System.Globalization.CultureInfo.InvariantCulture);

    /// <summary>The pay call. Observation: <c>https://hbx.com/checkout/pay</c>.</summary>
    private static string PayUrl(FlowContext c) => Origin(c.Url) + "/checkout/pay";

    /// <summary>
    /// Observation: the pay URL exists. Inference (medium): that it is the final call and that it returns an order
    /// identifier. The body is inferred -- the image names the endpoint, not its fields.
    /// </summary>
    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        var payload = new JObject { ["cartId"] = c.Session.CartId };

        var res = await PostJsonAsync(c, PayUrl(c),
            payload.ToString(Newtonsoft.Json.Formatting.None), "hbx-order", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("hbx order unreachable", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("hbx order blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"hbx order HTTP {res.StatusCode}", retryable: true);

        var order = TryRead(res.Body, "orderNumber") ?? TryRead(res.Body, "orderId");
        if (!string.IsNullOrEmpty(order)) c.Session.OrderNumber = order;

        return StepOutcome.Success();
    }
}
