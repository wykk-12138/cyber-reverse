using System.Text.RegularExpressions;
using Cybersole.Http;

namespace Cybersole.Stores.Flows;

/// <summary>
/// GOAT — the sneaker resale marketplace.
///
/// Written from a live capture (tools/NetworkCapture) rather than from guesswork, because the
/// binary carries only the display name "Goat": no host, no endpoint. What the product page
/// actually calls:
///
///   GET /web-api/v1/countries
///   GET /web-api/v1/product_variants/buy_bar_data?productTemplateId={id}&amp;countryCode={cc}  // inferred: no image evidence (R298)
///   GET /web-api/v1/product_variants/buy_bar_copies?productTemplateId={id}
///   GET /web-api/v1/product_templates/recommended?productTemplateId={id}&amp;count=8
///   GET /web-api/v1/consumer-segment-access/get-user-segments/{cc}
///
/// Three things a naive implementation gets wrong:
///   * the API prefix is /web-api/, not /api/
///   * every call carries the CSRF header, lifted from the cookie jar (R296: sent as <c>x-xsrf-token</c>,
///     the form the image carries — the earlier X-CSRF-TOKEN spelling was not in the pool)
///   * products are keyed on a numeric productTemplateId, not the URL slug
///
/// GOAT is also not a normal storefront: it is a marketplace, so "add to cart" creates a
/// purchase against a specific seller's ask. The flow models that as one order per variant.
/// </summary>
public class GoatFlow : StoreFlow
{
    public override string Id => "goat";
    public override string Name => "Goat";
    public override IReadOnlyList<string> Domains => new[] { "goat.com" };

    /// <summary>GOAT's JSON surface; it refuses requests without the CSRF header.</summary>
    private static string WebApi(FlowContext c, string path) => Origin(c.Url) + "/web-api" + path;

    private string Region(FlowContext c) =>
        c.Session.Vars.TryGetValue("goat.country", out var cc) && cc is { Length: 2 }
            ? cc
            : "US";

    /// <summary>Lift the CSRF token the page left in a cookie or a meta tag.</summary>
    private void AbsorbCsrf(FlowContext c, string body)
    {
        if (c.Session.CsrfToken is { Length: > 0 }) return;

        if (c.Session.Cookies.TryGetValue("XSRF-TOKEN", out var xsrf) && xsrf.Length > 0)
        {
            c.Session.CsrfToken = Uri.UnescapeDataString(xsrf);
            return;
        }

        var meta = Regex.Match(body, @"name=""csrf-token""\s+content=""([^""]+)""").Groups[1].Value;
        if (!string.IsNullOrEmpty(meta)) c.Session.CsrfToken = meta;
    }

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "goat-product-page", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("goat unreachable", retryable: true);
        if (res.StatusCode == 403)
            return StepOutcome.Fail("goat blocked (cloudflare) — needs a real browser session",
                retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"goat HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["home"] = res.Body;
        AbsorbCsrf(c, res.Body);

        // the page embeds the numeric template id; the URL only carries the slug
        var id = Regex.Match(res.Body, @"""productTemplateId""\s*:\s*(\d+)").Groups[1].Value;
        if (string.IsNullOrEmpty(id))
            id = Regex.Match(res.Body, @"""product_template_id""\s*:\s*(\d+)").Groups[1].Value;

        if (!string.IsNullOrEmpty(id)) c.Session.Vars["productTemplateId"] = id;

        var cc = Regex.Match(c.Url, @"goat\.com/([a-z]{2})/").Groups[1].Value;
        if (cc.Length == 2) c.Session.Vars["goat.country"] = cc.ToUpperInvariant();

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.Vars.TryGetValue("productTemplateId", out var id) || id is not { Length: > 0 })
        {
            // no embedded id: fall back to the buy-bar call keyed on nothing useful, so fail
            // with a clear reason instead of firing a malformed request
            return StepOutcome.Fail("goat: page carried no productTemplateId");
        }

        var res = await GetAsync(c,
            WebApi(c, $"/v1/product_variants/buy_bar_data?productTemplateId={id}&countryCode={Region(c)}"),
            "goat-buy-bar", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("goat buy bar unreachable", retryable: true);
        if (res.StatusCode == 403)
            return StepOutcome.Fail("goat blocked (cloudflare)", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"goat buy bar HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;

        var title = Regex.Match(c.Session.Vars.TryGetValue("home", out var home) ? home : "",
            @"<title>([^<|]+)").Groups[1].Value.Trim();
        if (!string.IsNullOrEmpty(title)) c.Session.Vars["product"] = title;

        var price = Regex.Match(res.Body, @"""lowestPriceCents""\s*:\s*(\d+)").Groups[1].Value;
        if (string.IsNullOrEmpty(price))
            price = Regex.Match(res.Body, @"""amount""\s*:\s*(\d+)").Groups[1].Value;

        if (!string.IsNullOrEmpty(price) && long.TryParse(price, out var cents))
            c.Session.Vars["price"] = (cents / 100m).ToString("0.00");

        return StepOutcome.Success();
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        var wanted = c.Product?.Sizes.FirstOrDefault();

        // buy_bar_data returns one entry per size, each with its own productVariantId.
        string? chosen = null;
        string? chosenSize = null;

        foreach (Match m in Regex.Matches(body,
                     @"""size""\s*:\s*""([^""]+)""[^}]*?""(?:productVariantId|id)""\s*:\s*""?([A-Za-z0-9_\-]+)""?"))
        {
            var size = m.Groups[1].Value;
            var vid = m.Groups[2].Value;

            if (chosen is null) { chosen = vid; chosenSize = size; }

            if (wanted is not null && size.Equals(wanted, StringComparison.OrdinalIgnoreCase))
            {
                chosen = vid;
                chosenSize = size;
                break;
            }
        }

        if (chosen is null)
        {
            var fallback = Regex.Match(body, @"""productVariantId""\s*:\s*""?([A-Za-z0-9_\-]+)""?");
            if (!fallback.Success)
                return Task.FromResult(StepOutcome.Fail("goat: no variant in buy bar"));
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

        // an empty buy bar means nobody is selling in that size
        var hasAsk = body.Contains("\"lowestPriceCents\":", StringComparison.OrdinalIgnoreCase) ||
                     body.Contains("\"amount\":", StringComparison.OrdinalIgnoreCase);

        c.Session.Vars["available"] = hasAsk && body.Length > 20 ? "true" : "false";

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
            return StepOutcome.Fail("goat: no variant to buy");

        // GOAT has no cart in the shop sense; a purchase is created against the ask.
        var payload = new Newtonsoft.Json.Linq.JObject
        {
            ["productVariantId"] = c.Session.VariantId,
            ["quantity"] = c.Session.Quantity,
        };

        var res = await PostJsonAsync(c, WebApi(c, "/v1/buys"),  // inferred: no image evidence (R294)
            payload.ToString(Newtonsoft.Json.Formatting.None), "goat-buy", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("goat buy failed", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("goat buy blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"goat buy HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;

        var buyId = TryRead(res.Body, "id") ?? TryRead(res.Body, "buyId");
        if (!string.IsNullOrEmpty(buyId)) c.Session.CartId = buyId;

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.CartId))
        {
            // no purchase yet — treat the buy bar's ask count as the "stock" signal
            c.Session.Vars["cart"] = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : "{}";
            return StepOutcome.Success();
        }

        var res = await GetAsync(c, WebApi(c, $"/v1/buys/{c.Session.CartId}"),  // inferred: no image evidence (R294)
            "goat-buy-state", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("goat buy state unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"goat buy state HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
        OpenCheckoutAsync(c, "goat-checkout", "/checkout", ct);

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.CartId))
            return StepOutcome.Fail("goat: no purchase to submit");

        // GOAT confirms the purchase server-side; the buy id is the order reference.
        var res = await GetAsync(c, WebApi(c, $"/v1/buys/{c.Session.CartId}"),
            "goat-confirm", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("goat confirm failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"goat confirm HTTP {res.StatusCode}", retryable: true);

        var status = TryRead(res.Body, "status") ?? string.Empty;
        if (status.Contains("cancel", StringComparison.OrdinalIgnoreCase) ||
            status.Contains("fail", StringComparison.OrdinalIgnoreCase))
            return StepOutcome.Fail($"goat purchase {status}");

        c.Session.OrderNumber = c.Session.CartId;
        return StepOutcome.Success();
    }
}
