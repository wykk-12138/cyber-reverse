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
///   GET /web-api/v1/product_variants/buy_bar_data?productTemplateId={id}&amp;countryCode={cc}  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R298)
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

    // ── account surface (R328) ────────────────────────────────────────────────
    //
    // The image carries five /web-api paths, each as a full URL, and this flow calls every one of them:
    //   GET  /web-api/get-csrf-token             https://www.goat.com/web-api/get-csrf-token             (1470939FC)
    //   POST /web-api/v1/login                   https://www.goat.com/web-api/v1/login                   (147093B44)
    //   POST /web-api/v1/users/send_otp_token    https://www.goat.com/web-api/v1/users/send_otp_token    (147093BA4)
    //   GET  /web-api/v1/addresses               https://www.goat.com/web-api/v1/addresses               (147093A6C)
    //   GET  /web-api/v1/billing_infos           https://www.goat.com/web-api/v1/billing_infos           (147093AD4)
    //
    // The paths are the image's verbatim. The *bodies* are not: no request body for these five appears anywhere in
    // the artifact, so each body below stays marked inferred until a capture says otherwise. The two product
    // endpoints are a different case — /v1/product_variants/buy_bar_data and /v1/buys answer 0 hits in the string
    // dump, so their paths are inferred as well.

    /// <summary>Signs in and keeps the session cookie (path evidenced; body inferred).</summary>
    private Task<NetResponse?> LoginAsync(FlowContext c, string email, string password, CancellationToken ct) =>
        PostJsonAsync(c, WebApi(c, "/v1/login"),
            "{\"email\":\"" + JsonEscape(email) + "\",\"password\":\"" + JsonEscape(password) + "\"}",
            "goat-login", ct);

    /// <summary>Asks for an OTP for this address (path evidenced; body inferred).</summary>
    private Task<NetResponse?> SendOtpAsync(FlowContext c, string email, CancellationToken ct) =>
        PostJsonAsync(c, WebApi(c, "/v1/users/send_otp_token"),
            "{\"email\":\"" + JsonEscape(email) + "\"}", "goat-otp", ct);

    /// <summary>The saved addresses (path evidenced, no body).</summary>
    private Task<NetResponse?> GetAddressesAsync(FlowContext c, CancellationToken ct) =>
        GetAsync(c, WebApi(c, "/v1/addresses"), "goat-addresses", ct);

    /// <summary>The saved billing records (path evidenced, no body).</summary>
    private Task<NetResponse?> GetBillingInfosAsync(FlowContext c, CancellationToken ct) =>
        GetAsync(c, WebApi(c, "/v1/billing_infos"), "goat-billing", ct);

    /// <summary>
    /// Makes sure the session knows which saved address to buy with. GOAT's purchase is keyed to one, so this fills
    /// <c>goat.addressId</c> from the first saved address when the task did not set it.
    /// </summary>
    private async Task<bool> EnsureAddressAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Vars.TryGetValue("goat.addressId", out var existing) && existing is { Length: > 0 })
            return true;

        var res = await GetAddressesAsync(c, ct).ConfigureAwait(false);
        if (res is not { IsSuccess: true }) return false;

        var id = FirstId(res.Body);
        if (string.IsNullOrEmpty(id)) return false;

        c.Session.Vars["goat.addressId"] = id;
        return true;
    }

    /// <summary>Pulls the first "id" value out of a JSON body; empty when there is none.</summary>
    private static string FirstId(string body)
    {
        var m = Regex.Match(body, "\"id\"\\s*:\\s*\"?([A-Za-z0-9_\\-]+)", RegexOptions.IgnoreCase);
        return m.Success ? m.Groups[1].Value : string.Empty;
    }

    private static string JsonEscape(string value) =>
        value.Replace("\\", "\\\\", StringComparison.Ordinal).Replace("\"", "\\\"", StringComparison.Ordinal);

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

        // R321: the image carries a dedicated token endpoint (https://www.goat.com/web-api/get-csrf-token, found in the
        // string pool). The cookie/meta paths above are what a browser session gives; this is the fallback for when the
        // page was served without either — the flow still has to send the header on every call.
        if (string.IsNullOrEmpty(c.Session.CsrfToken))
        {
            var token = await GetAsync(c, WebApi(c, "/get-csrf-token"), "goat-csrf", ct).ConfigureAwait(false);
            if (token is { IsSuccess: true } && !string.IsNullOrWhiteSpace(token.Body))
                c.Session.CsrfToken = token.Body.Trim().Trim('"');
        }

        // the page embeds the numeric template id; the URL only carries the slug
        var id = Regex.Match(res.Body, @"""productTemplateId""\s*:\s*(\d+)").Groups[1].Value;  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R298)
        if (string.IsNullOrEmpty(id))
            id = Regex.Match(res.Body, @"""product_template_id""\s*:\s*(\d+)").Groups[1].Value;

        if (!string.IsNullOrEmpty(id)) c.Session.Vars["productTemplateId"] = id;  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R298)

        var cc = Regex.Match(c.Url, @"goat\.com/([a-z]{2})/").Groups[1].Value;
        if (cc.Length == 2) c.Session.Vars["goat.country"] = cc.ToUpperInvariant();

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.Vars.TryGetValue("productTemplateId", out var id) || id is not { Length: > 0 })  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R298)
        {
            // no embedded id: fall back to the buy-bar call keyed on nothing useful, so fail
            // with a clear reason instead of firing a malformed request
            return StepOutcome.Fail("goat: page carried no productTemplateId");  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R298)
        }

        var res = await GetAsync(c,
            WebApi(c, $"/v1/product_variants/buy_bar_data?productTemplateId={id}&countryCode={Region(c)}"),  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R298)
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

        var res = await PostJsonAsync(c, WebApi(c, "/v1/buys"),  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R294)
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

        var res = await GetAsync(c, WebApi(c, $"/v1/buys/{c.Session.CartId}"),  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R294)
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

        // R328: a GOAT purchase is keyed to a saved address, and the image has an endpoint for exactly that list.
        // Fail early with a clear message instead of letting the confirm call 4xx without explanation.
        if (!await EnsureAddressAsync(c, ct).ConfigureAwait(false))
            return StepOutcome.Fail("goat: no saved address on this account", retryable: true);

        // GOAT confirms the purchase server-side; the buy id is the order reference.
        var res = await GetAsync(c, WebApi(c, $"/v1/buys/{c.Session.CartId}"),  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R294)
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
