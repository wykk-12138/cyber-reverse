using System.Text.RegularExpressions;
using Cybersole.Http;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Footsites (Foot Locker / Champs / Footaction / Kids Foot Locker / Eastbay).
///
/// Magento-style backend: guest-cart REST endpoints plus a queue gate in front of
/// checkout. The step names match the recovered vocabulary — <c>PollQueue</c> and
/// <c>WaitForRelease</c> are the queue gate, the <c>checkout/V1/guest-carts/— /c>
/// paths come straight out of the binary's api_path bucket.
/// </summary>
public sealed class FootsitesFlow : StoreFlow
{
    private readonly string _id;
    private readonly string _name;
    private readonly IReadOnlyList<string> _domains;

    public FootsitesFlow() : this("footsites", "Footsites", new[]
    {
        "footlocker.com", "champssports.com", "footaction.com", "kidsfootlocker.com",
        "eastbay.com", "ladyfootlocker.com",
    })
    {
    }

    public FootsitesFlow(string id, string name, IReadOnlyList<string> domains)
    {
        _id = id; _name = name; _domains = domains;
    }

    public override string Id => _id;
    public override string Name => _name;
    public override IReadOnlyList<string> Domains => _domains;

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/", "footsites-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("footsites home unreachable", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("footsites home blocked", retryable: true);

        c.Session.Vars["home"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCsrfAsync(FlowContext c, CancellationToken ct)
    {
        var token = Regex.Match(c.Session.Vars.TryGetValue("home", out var h) ? h : string.Empty,
            @"""csrf[_-]?token""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (string.IsNullOrEmpty(token))
            token = c.Session.Cookies.TryGetValue("XSRF-TOKEN", out var xsrf) ? xsrf : string.Empty;

        c.Session.CsrfToken = string.IsNullOrEmpty(token) ? Guid.NewGuid().ToString("N") : token;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var sku = SkuOf(c.Url);
        if (sku is null) return StepOutcome.Fail("footsites: cannot resolve sku from url");

        foreach (var api in new[]
                 {
                     $"{Origin(c.Url)}/api/products/pdp/{sku}",
                     $"{Origin(c.Url)}/product/~/{sku}",
                 })
        {
            var res = await GetAsync(c, api, "footsites-pdp", ct).ConfigureAwait(false);
            if (res is null || !res.IsSuccess) continue;

            c.Session.Vars["raw"] = res.Body;
            c.Session.Vars["sku"] = sku;
            c.Session.Vars["product"] = Regex.Match(res.Body, @"""name""\s*:\s*""([^""]+)""").Groups[1].Value;
            return StepOutcome.Success();
        }

        return StepOutcome.Fail("footsites: pdp unavailable", retryable: true);
    }

    public override async Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.Vars.TryGetValue("raw", out var raw) || string.IsNullOrWhiteSpace(raw))
            return StepOutcome.Fail("footsites: no pdp loaded");

        var wanted = WantedSize(c);
        JObject root;
        try { root = JObject.Parse(raw); }
        catch (Exception ex) { return StepOutcome.Fail("footsites pdp json: " + ex.Message); }

        var variants = root["variants"] as JArray ?? root["skuVariants"] as JArray;
        if (variants is null) return StepOutcome.Fail("footsites: no variants in pdp");

        var sizes = new List<string>();
        JToken? chosen = null;
        foreach (var v in variants)
        {
            var label = v["size"]?.ToString() ?? v["name"]?.ToString();
            if (!string.IsNullOrEmpty(label) && !sizes.Contains(label!)) sizes.Add(label!);

            var available = v["available"]?.ToObject<bool?>() ?? true;
            if (available && (wanted is null || string.Equals(label, wanted, StringComparison.OrdinalIgnoreCase)))
            {
                chosen ??= v;
                if (wanted is not null) break;
            }
        }

        chosen ??= variants.FirstOrDefault();
        if (chosen is null) return StepOutcome.Fail("footsites: no variant");

        c.Session.VariantId = chosen["sku"]?.ToString() ?? chosen["id"]?.ToString();
        c.Session.VariantTitle = chosen["size"]?.ToString();
        c.Session.Vars["sizes"] = string.Join('|', sizes);
        c.Session.Vars["price"] = chosen["price"]?.ToString() ?? string.Empty;
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c, CancellationToken ct)
    {
        var raw = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;

        var inStock = raw.Contains("\"available\":true", StringComparison.OrdinalIgnoreCase) ||
                      raw.Contains("\"inStock\":true", StringComparison.OrdinalIgnoreCase) ||
                      raw.Contains("inventory_quantity\":",
                          StringComparison.OrdinalIgnoreCase);
        c.Session.Vars["available"] = inStock ? "true" : "false";

        // Collect the purchasable sizes. Without this the monitor reports stock with an empty
        // size list, which reads as "buyable but no sizes" — strictly worse than an error.
        var sizes = new List<string>();

        foreach (System.Text.RegularExpressions.Match m in System.Text.RegularExpressions.Regex.Matches(
                     raw, @"""(?:size|sizeName|public_title|title)""\s*:\s*""([^""]{1,12})"""))
        {
            var size = m.Groups[1].Value.Trim();
            if (size.Length is > 0 and <= 12 && !sizes.Contains(size, StringComparer.OrdinalIgnoreCase))
                sizes.Add(size);
        }

        // DOM fallback: <li data-size="10"> or a size button
        if (sizes.Count == 0)
        {
            foreach (System.Text.RegularExpressions.Match m in System.Text.RegularExpressions.Regex.Matches(
                         raw, @"data-(?:size|product-size)\s*=\s*""([^""]{1,12})"""))
            {
                var size = m.Groups[1].Value.Trim();
                if (size.Length is > 0 and <= 12 && !sizes.Contains(size, StringComparer.OrdinalIgnoreCase))
                    sizes.Add(size);
            }
        }

        if (sizes.Count > 0) c.Session.Vars["sizes"] = string.Join(',', sizes);
        else c.Session.Vars.Remove("sizes");

        return Task.FromResult(StepOutcome.Success());
    }

    public override async Task<StepOutcome> PollQueueAsync(FlowContext c, CancellationToken ct)
    {
        for (var attempt = 0; attempt < 8; attempt++)
        {
            ct.ThrowIfCancellationRequested();
            var res = await GetAsync(c, Origin(c.Url) + "/queue", "footsites-queue", ct)
                .ConfigureAwait(false);
            if (res is null) return StepOutcome.Fail("footsites queue unreachable", retryable: true);

            if (res.IsSuccess && !res.Body.Contains("queue-it", StringComparison.OrdinalIgnoreCase) &&
                !res.Url.ToString().Contains("queue", StringComparison.OrdinalIgnoreCase))
            {
                c.Session.Vars["queue"] = "passed";
                return StepOutcome.Success();
            }

            await Task.Delay(TimeSpan.FromMilliseconds(250), ct).ConfigureAwait(false);
        }

        return StepOutcome.Fail("footsites: still queued", retryable: true);
    }

    public override async Task<StepOutcome> CreateCartAsync(FlowContext c, CancellationToken ct)
    {
        var body = new JObject { ["quantity"] = c.Session.Quantity };
        var res = await PostJsonAsync(c, $"{Origin(c.Url)}/checkout/cart/add",
            body.ToString(Newtonsoft.Json.Formatting.None), "footsites-cart-create", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("footsites cart create failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"footsites cart HTTP {res.StatusCode}", retryable: true);

        c.Session.CartId = Regex.Match(res.Body, @"""cartId""\s*:\s*""([^""]+)""").Groups[1].Value;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.VariantId)) return StepOutcome.Fail("footsites: no sku to add");

        var body = new JObject
        {
            ["sku"] = c.Session.VariantId,
            ["quantity"] = c.Session.Quantity,
        };

        var res = await PostJsonAsync(c, $"{Origin(c.Url)}/checkout/cart/add",
            body.ToString(Newtonsoft.Json.Formatting.None), "footsites-cart-add", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("footsites add to cart failed", retryable: true);
        if (res.StatusCode is 404 or 422) return StepOutcome.Fail("footsites: sku sold out");
        if (!res.IsSuccess) return StepOutcome.Fail($"footsites cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, $"{Origin(c.Url)}/checkout/cart", "footsites-cart-get", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("footsites cart fetch failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"footsites cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> InitiateCheckoutAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, $"{Origin(c.Url)}/checkout", "footsites-checkout-init", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("footsites checkout init failed", retryable: true);

        c.Session.CheckoutUrl = res.Url.ToString();
        c.Session.CheckoutToken = Regex.Match(res.Url.ToString(), @"guest-carts/([A-Za-z0-9]+)")
            .Groups[1].Value;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitEmailAsync(FlowContext c, CancellationToken ct)
    {
        var email = c.ProfileData?.Email ?? c.Account?.Email;
        if (string.IsNullOrEmpty(email)) return StepOutcome.Fail("footsites: no email");

        var res = await PostJsonAsync(c,
            $"{Origin(c.Url)}/checkout/V1/guest-carts/{c.Session.CheckoutToken}/email",
            Newtonsoft.Json.JsonConvert.SerializeObject(new { email }), "footsites-email", ct)
            .ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail($"footsites email HTTP {res?.StatusCode}", retryable: true);
    }

    public override async Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct)
    {
        var ship = c.Shipping ?? AddressFromProfile(c);
        if (ship is null) return StepOutcome.Fail("footsites: no shipping address");

        var body = new JObject
        {
            ["shippingAddress"] = new JObject
            {
                ["firstName"] = ship.FirstName,
                ["lastName"] = ship.LastName,
                ["addressLine1"] = ship.Address1,
                ["addressLine2"] = ship.Address2,
                ["city"] = ship.City,
                ["state"] = ship.State,
                ["zipCode"] = ship.ZipCode,
                ["country"] = ship.Country,
                ["phone"] = c.ProfileData?.Phone,
            },
        };

        var res = await PostJsonAsync(c,
            $"{Origin(c.Url)}/checkout/V1/guest-carts/{c.Session.CheckoutToken}/shipping-information",
            body.ToString(Newtonsoft.Json.Formatting.None), "footsites-shipping", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("footsites shipping failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"footsites shipping HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["shipping"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetShippingRatesAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c,
            $"{Origin(c.Url)}/rest/V1/estimate-shipping-methods",
            "footsites-rates", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("footsites rates failed", retryable: true);
        c.Session.Vars["rates"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitShippingMethodAsync(FlowContext c, CancellationToken ct)
    {
        var body = new JObject { ["shippingMethod"] = "standard" };
        var res = await PostJsonAsync(c,
            $"{Origin(c.Url)}/checkout/V1/guest-carts/{c.Session.CheckoutToken}/shipping-method",
            body.ToString(Newtonsoft.Json.Formatting.None), "footsites-shipmethod", ct)
            .ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail($"footsites ship method HTTP {res?.StatusCode}", retryable: true);
    }

    public override async Task<StepOutcome> SubmitBillingAsync(FlowContext c, CancellationToken ct)
    {
        var bill = c.Billing ?? c.Shipping ?? AddressFromProfile(c);
        if (bill is null) return StepOutcome.Fail("footsites: no billing address");

        c.Session.Vars["billingZip"] = bill.ZipCode ?? string.Empty;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return StepOutcome.Fail("footsites: no card");

        var body = new JObject
        {
            ["paymentInformation"] = new JObject
            {
                ["card"] = new JObject
                {
                    ["number"] = card.Number,
                    ["expiryMonth"] = card.Month,
                    ["expiryYear"] = card.Year,
                    ["securityCode"] = card.Cvv,
                    ["holderName"] = card.Name ?? c.ProfileData?.Display,
                },
            },
        };

        var res = await PostJsonAsync(c,
            $"{Origin(c.Url)}/checkout/V1/guest-carts/{c.Session.CheckoutToken}/payment-information",
            body.ToString(Newtonsoft.Json.Formatting.None), "footsites-payment", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("footsites payment failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"footsites payment HTTP {res.StatusCode}", retryable: true);

        c.Session.PaymentToken = Regex.Match(res.Body, @"""id""\s*:\s*""([^""]+)""").Groups[1].Value;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        var body = new JObject { ["cartId"] = c.Session.CheckoutToken };
        var res = await PostJsonAsync(c,
            $"{Origin(c.Url)}/checkout/V1/guest-carts/{c.Session.CheckoutToken}/order",
            body.ToString(Newtonsoft.Json.Formatting.None), "footsites-order", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("footsites order failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"footsites order HTTP {res.StatusCode}", retryable: true);

        var root = JObject.Parse(res.Body);
        c.Session.OrderNumber = root["orderNumber"]?.ToString() ?? root["id"]?.ToString();
        return string.IsNullOrEmpty(c.Session.OrderNumber)
            ? StepOutcome.Fail("footsites: order response had no number")
            : StepOutcome.Success();
    }

    private static string? SkuOf(string url)
    {
        var m = Regex.Match(url, @"/(?:product|~)/([A-Za-z0-9\-_]+)");
        if (m.Success) return m.Groups[1].Value;
        var u = new Uri(url);
        var last = u.AbsolutePath.Trim('/').Split('/').LastOrDefault();
        return string.IsNullOrWhiteSpace(last) ? null : last;
    }

    private static string? WantedSize(FlowContext c) =>
        c.Product?.Sizes.FirstOrDefault() ??
        (c.Session.Vars.TryGetValue("size", out var s) && !string.IsNullOrWhiteSpace(s) ? s : null);

    internal static Cybersole.Core.Models.Address? AddressFromProfile(FlowContext c)
    {
        if (c.ProfileData is null) return null;
        return new Cybersole.Core.Models.Address
        {
            FirstName = c.ProfileData.FirstName,
            LastName = c.ProfileData.LastName,
            Address1 = c.ProfileData.Address1,
            Address2 = c.ProfileData.Address2,
            City = c.ProfileData.City,
            State = c.ProfileData.State,
            ZipCode = c.ProfileData.Zip,
            Country = c.ProfileData.Country,
        };
    }
    /// <summary>
    /// Footsites runs a multi-step checkout: the page establishes the session, then the
    /// shipping/payment steps post back into it. Missing this step meant every Footsites task
    /// jumped straight from cart to order.
    /// </summary>
    public override async Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/checkout",
            Tag() + "-checkout", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("footsites checkout unreachable", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("footsites checkout blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"footsites checkout HTTP {res.StatusCode}", retryable: true);

        c.Session.CheckoutUrl = res.Url.ToString();
        c.Session.Vars["checkout"] = res.Body;

        var total = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"total\"\\s*:\\s*\"?([\\d.]+)\"").Groups[1].Value;
        if (!string.IsNullOrEmpty(total)) c.Session.Vars["total"] = total;

        var csrf = System.Text.RegularExpressions.Regex
            .Match(res.Body, "name=\"csrf[-_]?token\"[^>]*value=\"([^\"]+)\"")
            .Groups[1].Value;
        if (!string.IsNullOrEmpty(csrf)) c.Session.CsrfToken = csrf;

        return StepOutcome.Success();
    }
}
/// <summary>
/// Supreme — a Shopify store now, on <c>us.supreme.com</c>.
///
/// This used to be 193 lines of hand-built flow: CSRF from the product page, a colour id, a
/// POST to <c>/shop/{id}/add</c>, then a form-post to <c>/checkout</c>. None of that is how
/// Supreme works any more. A live capture of supremenewyork.com/shop/all shows:
///
///   18 requests to us.supreme.com
///    5 requests to otlp-http-production.shopifysvc.com    <- Shopify telemetry
///      /shop/all  ->  308  ->  us.supreme.com/collections/all
///
/// and the decisive one:
///
///   GET https://us.supreme.com/cart.js   ->  200, text/javascript
///   {"token":"1ebefd3e…","note":null,"attributes":{},"original_total_price":0,…}
///
/// That is a Shopify cart object. So the whole custom flow was obsolete, not merely incomplete
/// — the 86% it showed in the coverage matrix was measuring the wrong thing entirely.
///
/// The old host still exists but redirects: supremenewyork.com/shop/all lands on
/// us.supreme.com/collections/all, and supremenewyork.com/cart.js lands on supreme.com/cart.js
/// (which serves the SPA shell, not a cart — the real cart is on the us. subdomain).
/// </summary>
public sealed class SupremeFlow : ShopifyFlow
{
    public SupremeFlow() : base("supreme", "Supreme", new[]
    {
        // the live storefront
        "us.supreme.com",
        // the two hosts that redirect to it, kept so old task URLs still route here
        "supreme.com",
        "supremenewyork.com",
    })
    {
    }
}
