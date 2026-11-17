using System.Text.RegularExpressions;
using Cybersole.Http;

namespace Cybersole.Stores.Flows;

/// <summary>
/// BSTN — the German sneaker store (beastinpeace).
///
/// Registered against <c>ShopifyFlow</c> until a live capture showed otherwise:
///
///   GET /api/beast/geoIP
///   POST /api/beast/monetate
///   checkoutanalytics-live.adyen.com        <- Adyen, not Shopify Payments
///   GET /cart.js -> 404
///
/// <c>/api/beast/</c> is BSTN's own prefix (the brand is "beastinpeace"), which no Shopify
/// storefront has. So the Shopify registration was wrong in the same way `hbx` and `converse`
/// were: it compiles, it runs, and every cart call hits a route that is not there.
///
/// Verified:   the /api/beast/ prefix, the Adyen checkout, the /us_en locale path
/// Unknown:    the product endpoint, the cart endpoint, the checkout endpoint
///
/// The unknown steps report that they are unknown. A guessed POST would land on BSTN's 404
/// handler, return a response, and look like progress.
/// </summary>
public class BstnFlow : StoreFlow
{
    public override string Id => "bstn";
    public override string Name => "BSTN";
    public override IReadOnlyList<string> Domains => new[] { "bstn.com" };

    /// <summary>Verified: this prefix answers (geoIP and monetate both live under it).</summary>
    private static string BeastApi(FlowContext c, string path) => Origin(c.Url) + "/api/beast" + path;  // inferred: no image evidence (R294)

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "bstn-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("bstn unreachable", retryable: true);

        if (res.StatusCode == 403)
            return StepOutcome.Fail("bstn blocked — needs a browser session", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"bstn HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["home"] = res.Body;

        // the locale segment is part of every path on this site: /us_en/... or /en-US/us_en/...
        var locale = Regex.Match(c.Url, @"bstn\.com/(?:[a-zA-Z\-]+/)?([a-z]{2}_[a-z]{2})");
        if (locale.Success) c.Session.Vars["bstn.locale"] = locale.Groups[1].Value;

        var geo = await GetAsync(c, BeastApi(c, "/geoIP"), "bstn-geo", ct).ConfigureAwait(false);
        if (geo is { IsSuccess: true })
        {
            c.Session.Vars["geo"] = geo.Body;

            var country = Regex.Match(geo.Body, @"""country(?:Code)?""\s*:\s*""([A-Z]{2})""");
            if (country.Success) c.Session.Vars["bstn.country"] = country.Groups[1].Value;
        }

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("home", out var h) ? h : string.Empty;

        if (body.Length == 0)
        {
            var res = await GetAsync(c, c.Url, "bstn-product", ct).ConfigureAwait(false);
            if (res is null) return StepOutcome.Fail("bstn product unreachable", retryable: true);
            if (!res.IsSuccess) return StepOutcome.Fail($"bstn product HTTP {res.StatusCode}",
                retryable: true);

            body = res.Body;
            c.Session.Vars["home"] = body;
        }

        c.Session.Vars["raw"] = body;

        var title = Regex.Match(body, @"<title>([^<|]+)").Groups[1].Value.Trim();
        if (!string.IsNullOrEmpty(title)) c.Session.Vars["product"] = title;

        var price = ExtractPrice(body);
        if (!string.IsNullOrEmpty(price)) c.Session.Vars["price"] = price;

        return StepOutcome.Success();
    }

    /// <summary>
    /// A price from declared sources only. Marketing copy is not consulted — a delivery
    /// threshold reads exactly like a price and John Lewis already proved that trap.
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

        var meta = Regex.Match(body, @"""price""\s*:\s*""?(\d+(?:\.\d{1,2})?)""?\s*[,}]");
        if (meta.Success) return meta.Groups[1].Value;

        return string.Empty;
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;

        var size = Regex.Match(body, @"""size""\s*:\s*""?([\w\-. ]{1,20})""?", RegexOptions.IgnoreCase);
        if (size.Success)
        {
            c.Session.VariantId = size.Groups[1].Value;
            c.Session.Vars["variant"] = size.Groups[1].Value;
            return Task.FromResult(StepOutcome.Success());
        }

        return Task.FromResult(StepOutcome.Fail(
            "bstn: no size data on the product page — the variant endpoint is not known"));
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c,
        CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;

        var soldOut = body.Contains("ausverkauft", StringComparison.OrdinalIgnoreCase) ||
                      body.Contains("sold out", StringComparison.OrdinalIgnoreCase) ||
                      body.Contains("outOfStock", StringComparison.OrdinalIgnoreCase);

        c.Session.Vars["available"] = !soldOut && body.Length > 2000 ? "true" : "false";
        return Task.FromResult(StepOutcome.Success());
    }

    public override Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail(
            "bstn: cart endpoint unknown — /cart.js is 404 and the cart lives under /api/beast/ " +  // inferred: no image evidence (R294)
            "at a path not yet captured"));

    /// <summary>
    /// BSTN's CSRF token, read the way this shop actually serves it.
    ///
    /// <para>
    /// R964. R963 established that a virtual method on StoreFlow survives into the artifact only when a concrete flow
    /// overrides it, because the dispatch table is reflection-based and reflection does not root methods under NativeAOT.
    /// Writing shared base bodies, which is what the previous eight rounds did, therefore changed nothing in the artifact.
    /// This is the first override written to test that conclusion rather than assume it, and it carries a string no other
    /// code in the repository contains so the artifact can be checked instead of trusted.
    /// </para>
    ///
    /// <para>
    /// The page is fetched once. The token is looked for in the shop's own shape first -- a hidden input on the cart form --
    /// and then in the two fallbacks every shop of this generation also uses, and a miss is a failure rather than a
    /// success, because a POST without a token is refused further downstream where the cause is invisible.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> GetCsrfAsync(FlowContext c, CancellationToken ct)
    {
        var page = await c.Http.GetAsync("https://www.bstn.com/", new RequestOptions(), ct).ConfigureAwait(false);

        if (page.StatusCode is < 200 or >= 300)
            return StepOutcome.Fail("bstn: csrf page " + page.StatusCode, retryable: page.StatusCode is 429 or >= 500);

        var token = StoreFlow.FindCsrfToken(page.Body);

        if (string.IsNullOrEmpty(token) && page.Cookies.TryGetValue("csrftoken", out var cookie))
            token = cookie;

        if (string.IsNullOrEmpty(token))
            return StepOutcome.Fail("bstn: no csrf token on the landing page", retryable: false);

        c.Session.CsrfToken = token;
        c.Session.Vars["csrfToken"] = token;
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail("bstn: cart endpoint unknown"));

    public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail("bstn: checkout endpoint unknown (Adyen)"));

    public override Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail("bstn: order endpoint unknown"));
}
