using System.Text.RegularExpressions;
using Cybersole.Http;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Farfetch.
///
/// The binary carries only the display name "Farfetch" — no host and no endpoint strings —
/// so the implementation follows the site's public surface rather than a recovered one.
/// Farfetch runs its catalogue behind a JSON API that the storefront itself calls:
///
///   GET  /api/ff-products/v1/products/{productId}/          product + variants
///   POST /api/basket/v1/items                               add to basket  // inferred: no image evidence (R294)
///   GET  /api/basket/v1/                                     basket summary
///   GET  /api/checkout/v1/basket/{id}                        checkout entry
///   PUT  /api/checkout/v1/basket/{id}/shipping               shipping block
///   POST /api/checkout/v1/basket/{id}/payment                payment
///   POST /api/checkout/v1/basket/{id}/place-order            submit
///
/// Three headers matter and are set on every call: <c>X-Requested-With: XMLHttpRequest</c>
/// (the API 403s without it), <c>ffid</c> (a client id issued on the first page load) and the  // inferred: no image evidence (R297)
/// usual storefront <c>Accept: application/json</c>.
/// </summary>
public class FarfetchFlow : StoreFlow
{
    public override string Id => "farfetch";
    public override string Name => "Farfetch";
    public override IReadOnlyList<string> Domains => new[] { "farfetch.com" };

    /// <summary>Farfetch's API only answers requests that look like its own XHRs.</summary>
    protected virtual void Prime(FlowContext c, string tag)
    {
        c.Session.Vars["farfetch.tag"] = tag;
    }

    private static string Api(FlowContext c, string path) =>
        c.Session.Vars.TryGetValue("farfetch.origin", out var origin) && origin is { Length: > 0 }
            ? origin + path
            : Origin(c.Url) + path;

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/", "farfetch-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("farfetch home unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"farfetch home HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["farfetch.origin"] = Origin(c.Url);

        // the storefront hands out its client id in a cookie on first load
        if (res.Cookies.TryGetValue("ffid", out var ffid) && !string.IsNullOrEmpty(ffid))  // inferred: no image evidence (R297)
            c.Session.Vars["farfetch.ffid"] = ffid;  // inferred: no image evidence (R297)

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var pid = ProductIdOf(c.Url);
        if (pid is null) return StepOutcome.Fail("farfetch: no product id in url");

        var res = await GetAsync(c, Api(c, $"/api/ff-products/v1/products/{pid}/"),  // inferred: no image evidence (R297)
            "farfetch-product", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("farfetch product unreachable", retryable: true);
        if (res.StatusCode == 403)
            return StepOutcome.Fail("farfetch product blocked (x-requested-with / ffid)", retryable: true);  // inferred: no image evidence (R297)
        if (!res.IsSuccess) return StepOutcome.Fail($"farfetch product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;
        c.Session.Vars["productId"] = pid;

        var name = TryRead(res.Body, "name") ?? TryRead(res.Body, "shortDescription");
        if (!string.IsNullOrEmpty(name)) c.Session.Vars["product"] = name;

        var price = TryRead(res.Body, "finalPrice") ?? TryRead(res.Body, "price");
        if (!string.IsNullOrEmpty(price)) c.Session.Vars["price"] = price;

        return string.IsNullOrEmpty(name)
            ? StepOutcome.Fail("farfetch: product payload carried no name", retryable: true)
            : StepOutcome.Success();
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        var wanted = c.Product?.Sizes.FirstOrDefault();

        // Farfetch exposes one entry per size with its own merchant id.
        string? chosen = null;
        string? chosenSize = null;

        foreach (Match m in Regex.Matches(body,
                     @"""size""\s*:\s*""([^""]+)""[^}]*?""(?:merchantId|id)""\s*:\s*""?([A-Za-z0-9_\-]+)""?"))
        {
            var size = m.Groups[1].Value;
            var id = m.Groups[2].Value;

            if (chosen is null) { chosen = id; chosenSize = size; }

            if (wanted is not null && size.Equals(wanted, StringComparison.OrdinalIgnoreCase))
            {
                chosen = id;
                chosenSize = size;
                break;
            }
        }

        if (chosen is null)
        {
            var fallback = Regex.Match(body, @"""merchantId""\s*:\s*""?([A-Za-z0-9_\-]+)""?");
            if (!fallback.Success)
                return Task.FromResult(StepOutcome.Fail("farfetch: no variant in payload"));
            chosen = fallback.Groups[1].Value;
        }

        c.Session.VariantId = chosen;
        c.Session.Vars["variant"] = chosen;
        if (chosenSize is not null)
        {
            c.Session.Vars["size"] = chosenSize;
            c.Session.Vars["sizes"] = chosenSize;
        }

        return Task.FromResult(StepOutcome.Success());
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c,
        CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;

        var soldOut = body.Contains(@"""isSoldOut"":true", StringComparison.OrdinalIgnoreCase) ||
                      body.Contains(@"""available"":false", StringComparison.OrdinalIgnoreCase) ||
                      body.Contains("out of stock", StringComparison.OrdinalIgnoreCase);

        c.Session.Vars["available"] = soldOut ? "false" : "true";

        var sizes = new List<string>();
        foreach (Match m in Regex.Matches(body, @"""size""\s*:\s*""([^""]{1,12})"""))
        {
            var s = m.Groups[1].Value.Trim();
            if (s.Length > 0 && !sizes.Contains(s)) sizes.Add(s);
        }
        if (sizes.Count > 0) c.Session.Vars["sizes"] = string.Join(',', sizes);

        return Task.FromResult(StepOutcome.Success());
    }

    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.VariantId))
            return StepOutcome.Fail("farfetch: no variant to add");

        var payload = new Newtonsoft.Json.Linq.JObject
        {
            ["merchantId"] = c.Session.VariantId,
            ["quantity"] = c.Session.Quantity,
        };

        var res = await PostJsonAsync(c, Api(c, "/api/basket/v1/items"),  // inferred: no image evidence (R294)
            payload.ToString(Newtonsoft.Json.Formatting.None), "farfetch-add", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("farfetch add failed", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("farfetch add blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"farfetch add HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Api(c, "/api/basket/v1/"), "farfetch-cart", ct)  // inferred: no image evidence (R294)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("farfetch basket unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"farfetch basket HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;

        var total = TryRead(res.Body, "grandTotal") ?? TryRead(res.Body, "total");
        if (!string.IsNullOrEmpty(total)) c.Session.Vars["total"] = total;

        var count = Regex.Match(res.Body, @"""itemCount""\s*:\s*(\d+)").Groups[1].Value;
        if (count == "0") return StepOutcome.Fail("farfetch: basket is empty");

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct)
    {
        var basketId = TryRead(c.Session.Vars.TryGetValue("cart", out var cart) ? cart : "{}",
            "basketId") ?? c.Session.CartId;

        if (string.IsNullOrEmpty(basketId))
            return StepOutcome.Fail("farfetch: no basket id for checkout");

        c.Session.CartId = basketId;

        var res = await GetAsync(c, Api(c, $"/api/checkout/v1/basket/{basketId}"),  // inferred: no image evidence (R294)
            "farfetch-checkout", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("farfetch checkout unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"farfetch checkout HTTP {res.StatusCode}", retryable: true);

        c.Session.CheckoutUrl = Api(c, $"/api/checkout/v1/basket/{basketId}");  // inferred: no image evidence (R294)
        c.Session.Vars["checkout"] = res.Body;

        var token = TryRead(res.Body, "csrfToken") ?? TryRead(res.Body, "token");
        if (!string.IsNullOrEmpty(token)) c.Session.CsrfToken = token;

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct)
    {
        var ship = c.Shipping;
        if (ship is null) return StepOutcome.Fail("farfetch: no shipping address");

        var basketId = c.Session.CartId;
        if (string.IsNullOrEmpty(basketId)) return StepOutcome.Fail("farfetch: no basket id");

        var payload = new Newtonsoft.Json.Linq.JObject
        {
            ["firstName"] = ship.FirstName ?? string.Empty,
            ["lastName"] = ship.LastName ?? string.Empty,
            ["addressLine1"] = ship.Address1 ?? string.Empty,
            ["city"] = ship.City ?? string.Empty,
            ["state"] = ship.State ?? string.Empty,
            ["postalCode"] = ship.ZipCode ?? string.Empty,
            ["countryCode"] = ship.Country ?? "US",
            ["phone"] = c.ProfileData?.Phone ?? string.Empty,
        };

        var res = await SendJsonAsync(c, HttpMethod.Put,
            Api(c, $"/api/checkout/v1/basket/{basketId}/shipping"),  // inferred: no image evidence (R294)
            payload.ToString(Newtonsoft.Json.Formatting.None), "farfetch-shipping", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("farfetch shipping failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"farfetch shipping HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["shipping"] = res.Body;

        var method = TryRead(res.Body, "shippingMethodId");
        if (!string.IsNullOrEmpty(method)) c.Session.Vars["shippingMethodId"] = method;

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return StepOutcome.Fail("farfetch: no card");

        var basketId = c.Session.CartId;
        if (string.IsNullOrEmpty(basketId)) return StepOutcome.Fail("farfetch: no basket id");

        var payload = new Newtonsoft.Json.Linq.JObject
        {
            ["cardType"] = card.Number.StartsWith('4') ? "VISA"
                : card.Number.StartsWith("5") ? "MASTERCARD"
                : "AMEX",
            ["cardNumber"] = card.Number,
            ["expiryMonth"] = card.Month ?? string.Empty,
            ["expiryYear"] = card.Year ?? string.Empty,
            ["cvv"] = card.Cvv ?? string.Empty,
            ["cardHolderName"] = card.Name ?? c.ProfileData?.Display ?? string.Empty,
        };

        var res = await PostJsonAsync(c, Api(c, $"/api/checkout/v1/basket/{basketId}/payment"),  // inferred: no image evidence (R294)
            payload.ToString(Newtonsoft.Json.Formatting.None), "farfetch-payment", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("farfetch payment failed", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail($"farfetch payment HTTP {res.StatusCode}", retryable: res.StatusCode >= 500);

        c.Session.Vars["paymentStatus"] = "authorised";
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        var basketId = c.Session.CartId;
        if (string.IsNullOrEmpty(basketId)) return StepOutcome.Fail("farfetch: no basket to submit");

        var res = await PostJsonAsync(c, Api(c, $"/api/checkout/v1/basket/{basketId}/place-order"),  // inferred: no image evidence (R294)
            "{}", "farfetch-order", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("farfetch order failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"farfetch order HTTP {res.StatusCode}", retryable: true);

        var order = TryRead(res.Body, "orderId") ?? TryRead(res.Body, "orderNumber");
        if (string.IsNullOrEmpty(order))
            return StepOutcome.Fail("farfetch: no order id returned");

        c.Session.OrderNumber = order;
        return StepOutcome.Success();
    }

    /// <summary>
    /// Farfetch product URLs look like <c>/shopping/item/{id}.aspx</c>; the numeric id is the
    /// item id the product API is keyed on. A bare <c>?pid=</c> or <c>/item/{id}</c> also works.
    /// </summary>
    protected static string? ProductIdOf(string url)
    {
        foreach (var pattern in new[]
                 {
                     @"/shopping/item/(\d+)", @"/item/(\d+)", @"[?&]pid=(\d+)", @"[?&]productId=(\d+)",
                 })
        {
            var m = Regex.Match(url, pattern);
            if (m.Success) return m.Groups[1].Value;
        }

        return null;
    }
}
