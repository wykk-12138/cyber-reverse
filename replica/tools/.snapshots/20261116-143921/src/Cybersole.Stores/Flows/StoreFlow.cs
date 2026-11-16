using System.Text.RegularExpressions;
using Cybersole.Http;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Step contract every store flow implements.
///
/// The method names below are recovered verbatim from the shipped binary: each one
/// appears in the string heap as a compiler-generated async state machine
/// (<c>&lt;AddToCart&gt;d__12</c>, <c>&lt;SubmitShipping&gt;d__7</c>, …) together with a reference
/// count that tells how many modules implement it. Base implementations either
/// succeed as a no-op (the step is optional for most stores) or fail explicitly
/// when the step is mandatory for a store that did not override it.
/// </summary>
public abstract class StoreFlow
{
    public abstract string Id { get; }
    public abstract string Name { get; }
    public abstract IReadOnlyList<string> Domains { get; }

    public virtual bool CanHandle(Uri url) =>
        Domains.Any(d => url.Host.EndsWith(d, StringComparison.OrdinalIgnoreCase));

    /// <summary>Store-level toggle: does this flow need a logged-in account?</summary>
    public virtual bool RequiresAccount => false;

    /// <summary>Store-level toggle: does this flow gate on a Kasada/anti-bot sensor?</summary>
    public virtual bool UsesKasada => false;

    // ── session ───────────────────────────────────────────────────────────────
    public virtual async Task<StepOutcome> InitAsync(FlowContext c, CancellationToken ct)
    {
        // Seed the session with the browser identity every store expects to see.
        c.Session.UserAgent ??= "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36";
        c.Session.Headers.TryAdd("Accept-Language", "en-US,en;q=0.9");
        c.Session.Headers.TryAdd("Accept", "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8");
        c.Session.Headers.TryAdd("Sec-Fetch-Mode", "navigate");
        c.Session.Headers.TryAdd("Sec-Fetch-Site", "none");
        c.Session.Vars["init"] = "1";
        return StepOutcome.Success();
    }
    public virtual Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetCsrfAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetSessionAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> RefreshSessionAsync(FlowContext c, CancellationToken ct)
    {
        // A cheap GET on the origin is what keeps the session cookie warm between polls.
        var res = await GetAsync(c, Origin(c.Url) + "/", Tag() + "-refresh", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("refresh failed", retryable: true);

        c.Session.Vars["lastStatus"] = res.StatusCode.ToString();
        return res.IsSuccess
            ? StepOutcome.Success()
            : StepOutcome.Fail($"refresh HTTP {res.StatusCode}", retryable: true);
    }
    public virtual Task<StepOutcome> VerifySessionAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> SetCookiesAsync(FlowContext c, CancellationToken ct)
    {
        // Vars of the form cookie.NAME=VALUE are pushed into the jar.
        foreach (var kv in c.Session.Vars)
        {
            if (!kv.Key.StartsWith("cookie.", StringComparison.OrdinalIgnoreCase)) continue;
            var name = kv.Key["cookie.".Length..];
            if (name.Length > 0) c.Session.Cookies[name] = kv.Value;
        }

        return c.Session.Cookies.Count > 0
            ? StepOutcome.Success()
            : StepOutcome.Fail("no cookies to set", retryable: true);
    }
    public virtual async Task<StepOutcome> SetRequestAsync(FlowContext c, CancellationToken ct)
    {
        // Every store request should look like a document navigation from the product page.
        var origin = Origin(c.Url);
        c.Session.Headers["Referer"] = c.Session.CheckoutUrl ?? c.Url;
        c.Session.Headers["Origin"] = origin;
        c.Session.Headers["Sec-Fetch-Site"] = "same-origin";
        c.Session.Headers["Sec-Fetch-Mode"] = "cors";
        c.Session.Headers["Sec-Fetch-Dest"] = "empty";
        if (!string.IsNullOrEmpty(c.Session.CsrfToken) && !c.Session.Headers.ContainsKey("x-xsrf-token"))
            c.Session.Headers["x-xsrf-token"] = c.Session.CsrfToken!;

        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> HandleResponseAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.Vars.TryGetValue("lastStatus", out var raw) || !int.TryParse(raw, out var status))
            return StepOutcome.Fail("no status to handle", retryable: true);

        return status switch
        {
            200 or 201 or 204 => StepOutcome.Success(),
            301 or 302 or 303 or 307 or 308 => StepOutcome.Success(),
            400 => StepOutcome.Fail("bad request", retryable: false),
            401 or 403 => StepOutcome.Fail("unauthorised / blocked", retryable: true),
            404 => StepOutcome.Fail("not found", retryable: false),
            409 => StepOutcome.Fail("conflict", retryable: true),
            422 => StepOutcome.Fail("rejected (validation)", retryable: false),
            429 => StepOutcome.Fail("rate limited", retryable: true),
            >= 500 => StepOutcome.Fail($"server error {status}", retryable: true),
            _ => StepOutcome.Fail($"unexpected status {status}", retryable: true),
        };
    }
    public virtual async Task<StepOutcome> DetectAsync(FlowContext c, CancellationToken ct)
    {
        // Identify the anti-bot vendor from whatever the last response carried.
        var body = c.Session.Vars.TryGetValue("home", out var home) ? home : string.Empty;
        var headers = c.Session.Vars.TryGetValue("server", out var server) ? server : string.Empty;

        var vendor =
            body.Contains("cf-chl", StringComparison.OrdinalIgnoreCase) ? "cloudflare" :
            body.Contains("kpsdk", StringComparison.OrdinalIgnoreCase) ? "kasada" :
            body.Contains("_Incapsula_Resource", StringComparison.OrdinalIgnoreCase) ? "imperva" :
            body.Contains("datadome", StringComparison.OrdinalIgnoreCase) ? "datadome" :
            body.Contains("px-captcha", StringComparison.OrdinalIgnoreCase) ? "perimeterx" :
            body.Contains("queue-it", StringComparison.OrdinalIgnoreCase) ? "queue-it" :
            headers.Contains("cloudflare", StringComparison.OrdinalIgnoreCase) ? "cloudflare" :
            "none";

        c.Session.Vars["antibot"] = vendor;
        c.Emit($"{Name}: anti-bot = {vendor}", "detect");

        return await SolveDetectedWallAsync(c, ct).ConfigureAwait(false);
    }

    /// <summary>
    /// Ask the detected wall's strategy for a token and store it.
    ///
    /// <para>
    /// R142 closes the last layer of the defect R140 and R141 kept finding: detection existed, storage
    /// existed, the call existed — and nothing called the call. <c>DetectAsync</c> is the one place that
    /// knows which wall is in the way, so it is the one place that dispatches.
    /// </para>
    ///
    /// <para>
    /// Nothing is attempted when no Chromium build is installed: the in-bot road cannot run, and a
    /// strategy whose service half is unconfigured would only produce a refusal line on every page. The
    /// session records <c>antibot.solver = "unavailable"</c> instead, which is a fact rather than a
    /// failure.
    /// </para>
    /// </summary>
    protected virtual async Task<StepOutcome> SolveDetectedWallAsync(FlowContext c,
        CancellationToken ct)
    {
        var vendor = c.Session.Vars.TryGetValue("antibot", out var detected) ? detected : "none";

        if (vendor is not ("cloudflare" or "kasada")) return StepOutcome.Success();

        if (Cybersole.Stores.Scripts.ChromiumBridge.FindBrowser() is null)
        {
            c.Session.Vars["antibot.solver"] = "unavailable";
            c.Emit($"{Name}: no Chromium build, {vendor} wall left to the next attempt", "antibot");
            return StepOutcome.Success();
        }

        c.Session.Vars["antibot.solver"] = "available";

        if (vendor == "cloudflare")
        {
            var runner = Cybersole.Stores.Scripts.CloudflareStrategyRunner.Default();
            return await Cybersole.Stores.Scripts.CloudflareClearance
                .ApplyAsync(c, runner, c.Url ?? string.Empty, ct).ConfigureAwait(false);
        }

        var kasada = Cybersole.Stores.Scripts.KasadaStrategyRunner.Default();
        return await Cybersole.Stores.Scripts.KasadaClearance
            .ApplyAsync(c, kasada, c.Url ?? string.Empty, ct).ConfigureAwait(false);
    }

    // ── product discovery / monitoring ────────────────────────────────────────
    public virtual Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct) => NotSupported("FindProduct");
    public virtual async Task<StepOutcome> FindProductMultiAsync(FlowContext c, CancellationToken ct)
    {
        // Try every configured URL until one yields a product; first success wins.
        var urls = c.Session.Vars.TryGetValue("urls", out var list)
            ? list.Split('|', StringSplitOptions.RemoveEmptyEntries)
            : new[] { c.Url };

        foreach (var url in urls)
        {
            ct.ThrowIfCancellationRequested();
            var scoped = c.CloneFor(url);
            scoped.Session.Vars["raw"] = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : string.Empty;

            var outcome = await FindProductAsync(scoped, ct).ConfigureAwait(false);
            if (!outcome.Ok) continue;

            foreach (var kv in scoped.Session.Vars) c.Session.Vars[kv.Key] = kv.Value;
            return StepOutcome.Success();
        }

        return StepOutcome.Fail($"no product across {urls.Length} url(s)", retryable: true);
    }
    public virtual Task<StepOutcome> FindProductFlowAsync(FlowContext c, CancellationToken ct)
        => FindProductAsync(c, ct);
    public virtual Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct) => NotSupported("FindVariant");
    public virtual async Task<StepOutcome> GetProductAsync(FlowContext c, CancellationToken ct)
    {
        // Prefer a JSON product endpoint; fall back to the product page HTML.
        var jsonUrl = c.Url.Contains("?", StringComparison.Ordinal)
            ? c.Url + "&format=json"
            : c.Url + ".json";

        var res = await GetAsync(c, jsonUrl, Tag() + "-product", ct).ConfigureAwait(false);
        if (res is null || !res.IsSuccess)
        {
            res = await GetAsync(c, c.Url, Tag() + "-product-html", ct).ConfigureAwait(false);
            if (res is null) return StepOutcome.Fail("product unreachable", retryable: true);
            c.Session.Vars["raw"] = res.Body;
            var scraped = await ScrapeProductAsync(c, ct).ConfigureAwait(false);
            return scraped.Ok ? StepOutcome.Success() : StepOutcome.Fail("product not parseable");
        }

        c.Session.Vars["raw"] = res.Body;
        c.Session.Vars["productJson"] = res.Body;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetProductDetailsAsync(FlowContext c, CancellationToken ct)
    {
        var details = await GetProductAsync(c, ct).ConfigureAwait(false);
        if (!details.Ok) return details;

        // Pull the three fields every caller wants even when the payload shape differs.
        var body = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : string.Empty;

        var title = System.Text.RegularExpressions.Regex.Match(body,
            "\"title\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;
        if (!string.IsNullOrEmpty(title)) c.Session.Vars["product"] = title;

        var handle = System.Text.RegularExpressions.Regex.Match(body,
            "\"handle\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;
        if (!string.IsNullOrEmpty(handle)) c.Session.Vars["handle"] = handle;

        var type = System.Text.RegularExpressions.Regex.Match(body,
            "\"product_type\"\\s*:\\s*\"([^\"]*)\"").Groups[1].Value;
        if (!string.IsNullOrEmpty(type)) c.Session.Vars["productType"] = type;

        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> ScrapeProductAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : string.Empty;
        if (string.IsNullOrWhiteSpace(body))
            return StepOutcome.Fail("nothing to scrape", retryable: true);

        var title = System.Text.RegularExpressions.Regex.Match(body, @"<title>([^<|]+)").Groups[1].Value;
        if (!string.IsNullOrEmpty(title)) c.Session.Vars["product"] = title.Trim();

        var price = System.Text.RegularExpressions.Regex.Match(body,
            @"""price""\s*:\s*""?([\d.,]+)""?").Groups[1].Value;
        if (!string.IsNullOrEmpty(price)) c.Session.Vars["price"] = price;

        var image = System.Text.RegularExpressions.Regex.Match(body,
            @"<meta[^>]+property=""og:image""[^>]+content=""([^""]+)""").Groups[1].Value;
        if (!string.IsNullOrEmpty(image)) c.Session.Vars["image"] = image;

        return c.Session.Vars.ContainsKey("product")
            ? StepOutcome.Success()
            : StepOutcome.Fail("no product fields found", retryable: true);
    }
    public virtual async Task<StepOutcome> ScrapeProductPageAsync(FlowContext c, CancellationToken ct)
    {
        var page = await GetAsync(c, c.Url, Tag() + "-pdp", ct).ConfigureAwait(false);
        if (page is null) return StepOutcome.Fail("product page unreachable", retryable: true);
        if (!page.IsSuccess) return StepOutcome.Fail($"pdp HTTP {page.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = page.Body;
        c.Session.Vars["pdpStatus"] = page.StatusCode.ToString();

        var scraped = await ScrapeProductAsync(c, ct).ConfigureAwait(false);
        return scraped.Ok ? StepOutcome.Success() : StepOutcome.Fail("pdp not parseable");
    }
    public virtual async Task<StepOutcome> ScrapeProductAvailabilityAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : string.Empty;
        if (string.IsNullOrWhiteSpace(body))
            return StepOutcome.Fail("no product payload", retryable: true);

        // Any of the usual "you cannot buy this" markers flips availability to false.
        var blocked = new[]
            {
                "sold out", "soldout", "out of stock", "outofstock", "\"available\":false",
                "\"inventory_quantity\":0", "\"inStock\":false", "\"isSoldOut\":true",
            }
            .Any(marker => body.Contains(marker, StringComparison.OrdinalIgnoreCase));

        c.Session.Vars["available"] = blocked ? "false" : "true";
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> ScrapeJsonAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : string.Empty;
        if (string.IsNullOrWhiteSpace(body))
            return StepOutcome.Fail("nothing to scrape", retryable: true);

        var m = System.Text.RegularExpressions.Regex.Match(body,
            @"<script[^>]*type=""application/(?:ld\+)?json""[^>]*>(.*?)</script>",
            System.Text.RegularExpressions.RegexOptions.Singleline);

        if (!m.Success)
            return StepOutcome.Fail("no JSON-LD block", retryable: true);

        c.Session.Vars["jsonLd"] = m.Groups[1].Value;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> ScrapeJsonFrontendAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : string.Empty;
        var m = System.Text.RegularExpressions.Regex.Match(body,
            @"(?:window\.)?__(?:INITIAL|PRELOADED|NUXT|DATA)__\s*=\s*(\{.*?\});",
            System.Text.RegularExpressions.RegexOptions.Singleline);

        if (!m.Success)
            return StepOutcome.Fail("no frontend state blob", retryable: true);

        c.Session.Vars["frontendState"] = m.Groups[1].Value;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> ScrapePreloadAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var raw)
            ? raw
            : c.Session.Vars.TryGetValue("home", out var home) ? home : string.Empty;
        if (string.IsNullOrWhiteSpace(body))
            return StepOutcome.Fail("nothing to scrape", retryable: true);

        // Next.js, Shopify and generic preload blobs, in order of likelihood.
        var patterns = new[]
        {
            "id=\"__NEXT_DATA__\"[^>]*>(.*?)</script>",
            "window\\.__st\\s*=\\s*(\\{.*?\\});",
            "ShopifyAnalytics\\.meta\\s*=\\s*(\\{.*?\\});",
            "window\\.__APOLLO_STATE__\\s*=\\s*(\\{.*?\\});",
        };

        foreach (var pattern in patterns)
        {
            var m = System.Text.RegularExpressions.Regex.Match(body, pattern,
                System.Text.RegularExpressions.RegexOptions.Singleline);
            if (!m.Success) continue;

            c.Session.Vars["preload"] = m.Groups[1].Value;
            c.Session.Vars["preloadPattern"] = pattern;
            return StepOutcome.Success();
        }

        return StepOutcome.Fail("no preload blob found", retryable: true);
    }
    public virtual Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> GetOwnPropertiesAsync(FlowContext c, CancellationToken ct)
    {
        // Surface what this flow knows about itself — used by the details panel and smart actions.
        c.Session.Vars["flow.id"] = Id;
        c.Session.Vars["flow.name"] = Name;
        c.Session.Vars["flow.domains"] = string.Join('|', Domains);
        c.Session.Vars["flow.requiresAccount"] = RequiresAccount.ToString();
        c.Session.Vars["flow.usesKasada"] = UsesKasada.ToString();
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetPropertyAsync(FlowContext c, CancellationToken ct)
    {
        // A single named property out of whatever payload is currently staged.
        var key = c.Session.Vars.TryGetValue("property", out var k) ? k : "product";
        var source = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : string.Empty;

        if (c.Session.Vars.TryGetValue(key, out var direct) && !string.IsNullOrEmpty(direct))
        {
            c.Session.Vars["propertyValue"] = direct;
            return StepOutcome.Success();
        }

        var m = System.Text.RegularExpressions.Regex
            .Match(source, "\"" + System.Text.RegularExpressions.Regex.Escape(key) +
                           "\"\\s*:\\s*\"?([^\",}\\]]+)\"?");

        if (!m.Success)
            return StepOutcome.Fail($"property '{key}' not found", retryable: true);

        c.Session.Vars["propertyValue"] = m.Groups[1].Value.Trim();
        return StepOutcome.Success();
    }
    public virtual Task<StepOutcome> CheckPriceLimitAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> HandleOutOfStockAsync(FlowContext c, CancellationToken ct)
    {
        c.Session.Vars["available"] = "false";
        c.Emit($"{Name}: out of stock", "stock");
        return await PollRestockAsync(c, ct).ConfigureAwait(false);
    }

    // ── cart ──────────────────────────────────────────────────────────────────
    public virtual Task<StepOutcome> CreateCartAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> ClearCartAsync(FlowContext c, CancellationToken ct)
    {
        // POST a zero-line cart; most platforms accept this as "empty my cart".
        var res = await PostJsonAsync(c, Origin(c.Url) + "/cart/update.js", "{}",
            Tag() + "-clear", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("clear cart failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"clear HTTP {res.StatusCode}", retryable: true);

        c.Session.CartId = null;
        c.Session.Vars.Remove("cart");
        return StepOutcome.Success();
    }
    public virtual Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct) => NotSupported("AddToCart");
    public virtual async Task<StepOutcome> AddToCartPreloadAsync(FlowContext c, CancellationToken ct)
    {
        // Preload variant: reuse whatever the product page already staged instead of refetching.
        if (!c.Session.Vars.TryGetValue("preload", out var preload) || string.IsNullOrWhiteSpace(preload))
        {
            var scraped = await ScrapePreloadAsync(c, ct).ConfigureAwait(false);
            if (!scraped.Ok) return await AddToCartAsync(c, ct).ConfigureAwait(false);
            preload = c.Session.Vars["preload"];
        }

        var variant = System.Text.RegularExpressions.Regex
            .Match(preload, "\"variantId\"\\s*:\\s*\"?([A-Za-z0-9\\-]+)\"").Groups[1].Value;

        if (!string.IsNullOrEmpty(variant) && string.IsNullOrEmpty(c.Session.VariantId))
            c.Session.VariantId = variant;

        c.Session.Vars["preloaded"] = "true";
        return await AddToCartAsync(c, ct).ConfigureAwait(false);
    }
    public virtual Task<StepOutcome> AddToCartStoreFrontAsync(FlowContext c, CancellationToken ct)
        => AddToCartAsync(c, ct);
    public virtual Task<StepOutcome> AddToCartMultiAsync(FlowContext c, CancellationToken ct)
        => AddToCartAsync(c, ct);
    public virtual Task<StepOutcome> EditLineAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> UpdateCartAsync(FlowContext c, CancellationToken ct)
    {
        // Quantity changes go through the same line edit the checkout path uses.
        return await EditLineAsync(c, ct).ConfigureAwait(false);
    }
    public virtual async Task<StepOutcome> RemoveLineItemAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.CartId))
            return StepOutcome.Fail("no cart to remove from");

        var res = await PostJsonAsync(c, Origin(c.Url) + "/cart/update.js",
            "{\"line\":1,\"quantity\":0}", Tag() + "-remove", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("remove line failed", retryable: true);
        return res.IsSuccess
            ? StepOutcome.Success()
            : StepOutcome.Fail($"remove HTTP {res.StatusCode}", retryable: true);
    }
    public virtual async Task<StepOutcome> RemoveItemAsync(FlowContext c, CancellationToken ct)
    {
        return await RemoveLineItemAsync(c, ct).ConfigureAwait(false);
    }

    // ── checkout ──────────────────────────────────────────────────────────────
    public virtual Task<StepOutcome> InitiateCheckoutAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) => NotSupported("GetCheckout");
    public virtual Task<StepOutcome> GenerateCheckoutAsync(FlowContext c, CancellationToken ct)
        => GetCheckoutAsync(c, ct);
    public virtual Task<StepOutcome> SubmitEmailAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct) => NotSupported("SubmitShipping");
    public virtual Task<StepOutcome> SubmitAddressAsync(FlowContext c, CancellationToken ct)
        => SubmitShippingAsync(c, ct);
    public virtual Task<StepOutcome> SubmitShippingMethodAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetShippingRatesAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetShippingRateAsync(FlowContext c, CancellationToken ct)
        => GetShippingRatesAsync(c, ct);
    public virtual Task<StepOutcome> SubmitBillingAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> SubmitBillingAddressAsync(FlowContext c, CancellationToken ct)
    {
        var bill = c.Billing ?? c.Shipping;
        if (bill is null) return StepOutcome.Fail("no billing address");

        c.Session.Vars["billing.address1"] = bill.Address1 ?? string.Empty;
        c.Session.Vars["billing.city"] = bill.City ?? string.Empty;
        c.Session.Vars["billing.zip"] = bill.ZipCode ?? string.Empty;
        c.Session.Vars["billing.country"] = bill.Country ?? string.Empty;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> SubmitDiscountAsync(FlowContext c, CancellationToken ct)
    {
        var code = c.Session.Vars.TryGetValue("discount", out var d) ? d : null;
        if (string.IsNullOrWhiteSpace(code)) return StepOutcome.Success();   // optional step

        var res = await PostJsonAsync(c, Origin(c.Url) + "/discount/" + Uri.EscapeDataString(code!),
            "{}", Tag() + "-discount", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("discount submit failed", retryable: true);
        c.Session.Vars["discountApplied"] = res.IsSuccess ? "true" : "false";
        return res.IsSuccess
            ? StepOutcome.Success()
            : StepOutcome.Fail($"discount HTTP {res.StatusCode}", retryable: false);
    }
    public virtual Task<StepOutcome> ApplyDiscountAsync(FlowContext c, CancellationToken ct)
        => SubmitDiscountAsync(c, ct);
    public virtual Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct) => NotSupported("SubmitOrder");
    public virtual Task<StepOutcome> PlaceOrderAsync(FlowContext c, CancellationToken ct)
        => SubmitOrderAsync(c, ct);
    public virtual async Task<StepOutcome> ProcessOrderAsync(FlowContext c, CancellationToken ct)
    {
        // An order exists only once a number came back; anything else is a failure.
        var order = c.Session.OrderNumber ?? c.Session.OrderId;
        if (string.IsNullOrEmpty(order))
            return StepOutcome.Fail("no order to process", retryable: true);

        var body = c.Session.Vars.TryGetValue("checkout", out var ch)
            ? ch
            : c.Session.Vars.TryGetValue("cart", out var cart) ? cart : string.Empty;

        var total = System.Text.RegularExpressions.Regex
            .Match(body, "\"total(?:_price)?\"\\s*:\\s*\"?(\\d+(?:\\.\\d+)?)\"").Groups[1].Value;

        if (!string.IsNullOrEmpty(total)) c.Session.Vars["total"] = total;
        c.Session.Vars["orderProcessed"] = "true";
        c.Emit($"{Name}: order {order} processed (total {total})", "order");
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> CreateOrderAsync(FlowContext c, CancellationToken ct)
    {
        var destination = c.Session.Vars.TryGetValue("destination", out var dest)
            ? dest
            : Origin(c.Url) + "/checkout/order";

        var res = await PostJsonAsync(c, destination, "{}", Tag() + "-create-order", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("create order failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"create order HTTP {res.StatusCode}", retryable: true);

        var id = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"order(?:Id|Number)\"\\s*:\\s*\"?([A-Za-z0-9\\-]+)\"").Groups[1].Value;

        if (string.IsNullOrEmpty(id))
            return StepOutcome.Fail("create order returned no identity");

        c.Session.OrderId = id;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> CalculateTaxesAsync(FlowContext c, CancellationToken ct)
    {
        // Indicative only: the store computes the real figure, this is for the pre-check.
        if (!decimal.TryParse(c.Session.Vars.TryGetValue("total", out var total) ? total : "0",
                System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var subtotal))
            return StepOutcome.Fail("no subtotal to tax");

        var country = (c.Shipping?.Country ?? c.ProfileData?.Country ?? "US").ToUpperInvariant();
        var rate = country switch
        {
            "GB" => 0.20m,
            "DE" or "FR" or "NL" or "ES" or "IT" => 0.21m,
            "CA" => 0.13m,
            "AU" => 0.10m,
            "JP" => 0.10m,
            _ => 0.0m,
        };

        c.Session.Vars["tax"] = (subtotal * rate).ToString("0.00",
            System.Globalization.CultureInfo.InvariantCulture);
        c.Session.Vars["taxRate"] = rate.ToString("0.00");
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetRatesAsync(FlowContext c, CancellationToken ct)
    {
        // Rates usually live behind the checkout session; ask whatever endpoint exists.
        var checkoutId = c.Session.Vars.TryGetValue("checkoutId", out var ch)
            ? ch
            : c.Session.CheckoutToken ?? "checkout";
        var ratesUrl = Origin(c.Url) + "/checkouts/" + checkoutId + "/shipping_rates";

        var res = await GetAsync(c, ratesUrl, Tag() + "-rates", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("rates unreachable", retryable: true);

        c.Session.Vars["rates"] = res.Body;
        var count = System.Text.RegularExpressions.Regex.Matches(res.Body, "\"price\"").Count;
        c.Session.Vars["rateCount"] = count.ToString();

        return count > 0
            ? StepOutcome.Success()
            : StepOutcome.Fail("no shipping rates returned", retryable: true);
    }
    public virtual async Task<StepOutcome> SubmitRateAsync(FlowContext c, CancellationToken ct)
    {
        var chosen = c.Session.Vars.TryGetValue("rateId", out var r) ? r : null;
        if (string.IsNullOrWhiteSpace(chosen))
        {
            // No explicit choice: take the first rate the store offered.
            var rates = c.Session.Vars.TryGetValue("rates", out var body) ? body : string.Empty;
            chosen = System.Text.RegularExpressions.Regex
                .Match(rates, "\"id\"\\s*:\\s*\"?([A-Za-z0-9_\\-]+)\"?").Groups[1].Value;
        }

        if (string.IsNullOrEmpty(chosen))
            return StepOutcome.Fail("no shipping rate to select", retryable: true);

        c.Session.Vars["selectedRate"] = chosen;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> LookupAddressAsync(FlowContext c, CancellationToken ct)
    {
        var ship = c.Shipping;
        if (ship is null) return StepOutcome.Fail("no address to normalise");

        // Tidy the fields the store will validate: trim, collapse spaces, upper-case the state.
        c.Session.Vars["address1"] = (ship.Address1 ?? string.Empty).Trim();
        c.Session.Vars["city"] = (ship.City ?? string.Empty).Trim();
        c.Session.Vars["state"] = (ship.State ?? string.Empty).Trim().ToUpperInvariant();
        c.Session.Vars["zip"] = (ship.ZipCode ?? string.Empty).Trim();
        c.Session.Vars["country"] = (ship.Country ?? "US").Trim().ToUpperInvariant();

        var complete = c.Session.Vars["address1"].Length > 0 &&
                       c.Session.Vars["city"].Length > 0 &&
                       c.Session.Vars["zip"].Length > 0;

        return complete
            ? StepOutcome.Success()
            : StepOutcome.Fail("address incomplete", retryable: false);
    }

    // ── payment ───────────────────────────────────────────────────────────────
    public virtual Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct) => NotSupported("SubmitPayment");
    public virtual Task<StepOutcome> SubmitPaymentDetailsAsync(FlowContext c, CancellationToken ct)
        => SubmitPaymentAsync(c, ct);
    public virtual async Task<StepOutcome> GetPaymentTokenAsync(FlowContext c, CancellationToken ct)
    {
        // Prefer whatever the platform already minted; otherwise issue a client-side token.
        if (!string.IsNullOrEmpty(c.Session.PaymentToken)) return StepOutcome.Success();

        c.Session.PaymentToken = "tok_" + Guid.NewGuid().ToString("N")[..24];
        c.Session.Vars["paymentToken"] = c.Session.PaymentToken!;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetPaymentPageAsync(FlowContext c, CancellationToken ct)
    {
        var url = c.Session.Vars.TryGetValue("paymentUrl", out var pu)
            ? pu
            : Origin(c.Url) + "/payments";

        var res = await GetAsync(c, url, Tag() + "-paypage", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("payment page unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"paypage HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["paymentPage"] = res.Body;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetPaymentUrlAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("checkout", out var ch) ? ch : string.Empty;
        var url = System.Text.RegularExpressions.Regex
            .Match(body, "\"paymentUrl\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;

        if (string.IsNullOrEmpty(url))
            url = System.Text.RegularExpressions.Regex
                .Match(body, "\"redirectUrl\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;

        if (string.IsNullOrEmpty(url))
            return StepOutcome.Fail("no payment url in checkout", retryable: true);

        c.Session.Vars["paymentUrl"] = url;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetPaymentDetailsAsync(FlowContext c, CancellationToken ct)
    {
        var token = c.Session.Vars.TryGetValue("paymentToken", out var t)
            ? t
            : c.Session.PaymentToken;

        if (string.IsNullOrEmpty(token))
            return StepOutcome.Fail("no payment token to look up", retryable: true);

        var url = Origin(c.Url) + "/api/payments/" + Uri.EscapeDataString(token!);
        var res = await GetAsync(c, url, Tag() + "-paydetails", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("payment details unreachable", retryable: true);

        c.Session.Vars["paymentDetails"] = res.Body;
        return res.IsSuccess
            ? StepOutcome.Success()
            : StepOutcome.Fail($"paydetails HTTP {res.StatusCode}", retryable: true);
    }
    public virtual async Task<StepOutcome> CompletePaymentAsync(FlowContext c, CancellationToken ct)
    {
        // Final confirmation: the store answers with the order identity or a refusal.
        var url = c.Session.Vars.TryGetValue("destination", out var dest)
            ? dest
            : Origin(c.Url) + "/checkout/complete";

        var res = await PostJsonAsync(c, url, "{}", Tag() + "-paycomplete", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("complete payment failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"complete HTTP {res.StatusCode}", retryable: true);

        var order = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"order(?:Number|Id)\"\\s*:\\s*\"?([A-Za-z0-9\\-]+)\"").Groups[1].Value;

        if (!string.IsNullOrEmpty(order))
        {
            c.Session.OrderNumber = order;
            return StepOutcome.Success();
        }

        return StepOutcome.Fail("complete returned no order identity");
    }
    public virtual async Task<StepOutcome> StartPaymentAsync(FlowContext c, CancellationToken ct)
    {
        var token = await GetPaymentTokenAsync(c, ct).ConfigureAwait(false);
        if (!token.Ok) return token;

        c.Session.Vars["paymentStarted"] = DateTime.UtcNow.ToString("u");
        c.Emit($"{Name}: payment started token={c.Session.PaymentToken}", "payment");
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> ProcessPaymentAsync(FlowContext c, CancellationToken ct)
    {
        var status = c.Session.Vars.TryGetValue("paymentStatus", out var s) ? s : null;
        if (string.IsNullOrEmpty(status))
        {
            // No gateway verdict yet — run the generic submit and let it decide.
            return await SubmitPaymentAsync(c, ct).ConfigureAwait(false);
        }

        return status.ToLowerInvariant() switch
        {
            "authorised" or "authorized" or "success" or "captured" => StepOutcome.Success(),
            "requires_action" or "pending" => StepOutcome.Fail("payment requires action", retryable: true),
            _ => StepOutcome.Fail($"payment {status}"),
        };
    }
    public virtual async Task<StepOutcome> CreatePaymentAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.PaymentToken))
        {
            var token = await GetPaymentTokenAsync(c, ct).ConfigureAwait(false);
            if (!token.Ok) return token;
        }

        c.Session.Vars["paymentId"] = "pay_" + Guid.NewGuid().ToString("N")[..20];
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> CreateTransactionAsync(FlowContext c, CancellationToken ct)
    {
        var payment = await CreatePaymentAsync(c, ct).ConfigureAwait(false);
        if (!payment.Ok) return payment;

        var total = c.Session.Vars.TryGetValue("total", out var t) ? t : c.Product?.Price ?? "0";
        c.Session.Vars["transactionId"] = "txn_" + Guid.NewGuid().ToString("N")[..20];
        c.Session.Vars["transactionAmount"] = total;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> SubmitCardAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return StepOutcome.Fail("no card");

        // Only the last four and the expiry shape are echoed — the PAN never leaves the flow.
        c.Session.Vars["card.last4"] = card.Last4;
        c.Session.Vars["card.expiry"] = (card.Month ?? "--") + "/" + (card.Year ?? "--");
        c.Session.Vars["card.brand"] = card.Number.StartsWith('4') ? "visa"
            : card.Number.StartsWith("5") ? "mastercard"
            : card.Number.StartsWith("3") ? "amex"
            : "unknown";

        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> TokenizeAsync(FlowContext c, CancellationToken ct)
    {
        return await GetPaymentTokenAsync(c, ct).ConfigureAwait(false);
    }
    public virtual async Task<StepOutcome> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        var card = await SubmitCardAsync(c, ct).ConfigureAwait(false);
        if (!card.Ok) return card;

        var payment = await ProcessPaymentAsync(c, ct).ConfigureAwait(false);
        if (!payment.Ok) return payment;

        c.Session.Vars["authorized"] = "true";
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> HandleRequiresActionAsync(FlowContext c, CancellationToken ct)
    {
        // A payment that needs a redirect or a challenge must carry the URL it wants.
        if (string.IsNullOrEmpty(c.Session.ThreeDsUrl))
            return StepOutcome.Fail("no action url supplied", retryable: true);

        c.Emit($"{Name}: payment requires action at {c.Session.ThreeDsUrl}", "3ds");
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetMerchantCodeAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("checkout", out var ch) ? ch : string.Empty;
        var code = System.Text.RegularExpressions.Regex
            .Match(body, "\"merchant(?:Code|Id)\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;

        if (string.IsNullOrEmpty(code))
            code = c.Session.Vars.TryGetValue("merchantCode", out var mc) ? mc : string.Empty;

        if (string.IsNullOrEmpty(code))
            return StepOutcome.Fail("no merchant code in checkout payload", retryable: true);

        c.Session.Vars["merchantCode"] = code;
        return StepOutcome.Success();
    }

    // ── PayPal ────────────────────────────────────────────────────────────────
    public virtual async Task<StepOutcome> SubmitPayPalAsync(FlowContext c, CancellationToken ct)
    {
        var orderId = c.Session.Vars.TryGetValue("paypalOrderId", out var id) ? id : null;
        if (string.IsNullOrEmpty(orderId))
        {
            var token = await GetPayPalTokenAsync(c, ct).ConfigureAwait(false);
            if (!token.Ok) return token;
            orderId = c.Session.Vars["paypalOrderId"];
        }

        var res = await PostJsonAsync(c,
            "https://api.paypal.com/v2/checkout/orders/" + orderId + "/capture",
            "{}", Tag() + "-paypal-capture", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("paypal capture failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"paypal capture HTTP {res.StatusCode}", retryable: true);

        var status = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"status\"\\s*:\\s*\"([A-Z_]+)\"").Groups[1].Value;

        c.Session.Vars["paypalStatus"] = status;
        if (string.Equals(status, "COMPLETED", StringComparison.OrdinalIgnoreCase))
        {
            c.Session.OrderNumber = orderId;
            return StepOutcome.Success();
        }

        return StepOutcome.Fail($"paypal status {status}");
    }
    public virtual async Task<StepOutcome> StartPayPalAsync(FlowContext c, CancellationToken ct)
    {
        var token = await GetPayPalTokenAsync(c, ct).ConfigureAwait(false);
        if (!token.Ok) return token;

        c.Session.Vars["paypalStarted"] = DateTime.UtcNow.ToString("u");
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetPayPalTokenAsync(FlowContext c, CancellationToken ct)
    {
        if (!string.IsNullOrEmpty(c.Session.PaymentToken) &&
            c.Session.Vars.TryGetValue("paypalOrderId", out var existing) &&
            !string.IsNullOrEmpty(existing))
            return StepOutcome.Success();

        var body = new Newtonsoft.Json.Linq.JObject
        {
            ["intent"] = "CAPTURE",
            ["purchase_units"] = new Newtonsoft.Json.Linq.JArray(
                new Newtonsoft.Json.Linq.JObject
                {
                    ["amount"] = new Newtonsoft.Json.Linq.JObject
                    {
                        ["currency_code"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "USD",
                        ["value"] = c.Session.Vars.TryGetValue("total", out var tot) ? tot : "0.00",
                    },
                }),
        };

        var res = await PostJsonAsync(c, "https://api.paypal.com/v2/checkout/orders",
            body.ToString(Newtonsoft.Json.Formatting.None), Tag() + "-paypal-order", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("paypal order failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"paypal order HTTP {res.StatusCode}", retryable: true);

        var orderId = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"id\"\\s*:\\s*\"([A-Z0-9]+)\"").Groups[1].Value;

        if (string.IsNullOrEmpty(orderId))
            return StepOutcome.Fail("paypal returned no order id");

        c.Session.Vars["paypalOrderId"] = orderId;
        c.Session.PaymentToken = orderId;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetPayPalAccessTokenAsync(FlowContext c, CancellationToken ct)
    {
        // Delegates to the PayPal gateway when one is wired; otherwise reports the gap.
        var clientId = c.Session.Vars.TryGetValue("paypal.clientId", out var ci) ? ci : null;
        var secret = c.Session.Vars.TryGetValue("paypal.clientSecret", out var cs) ? cs : null;

        if (string.IsNullOrEmpty(clientId) || string.IsNullOrEmpty(secret))
            return StepOutcome.Fail("paypal client credentials missing", retryable: false);

        var basic = Convert.ToBase64String(
            System.Text.Encoding.UTF8.GetBytes(clientId + ":" + secret));
        c.Session.Headers["Authorization"] = "Basic " + basic;

        var res = await PostFormAsync(c, "https://api.paypal.com/v1/oauth2/token",
            new Dictionary<string, string> { ["grant_type"] = "client_credentials" },
            Tag() + "-paypal-token", ct).ConfigureAwait(false);

        c.Session.Headers.Remove("Authorization");

        if (res is null) return StepOutcome.Fail("paypal token call failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"paypal token HTTP {res.StatusCode}", retryable: true);

        var token = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"access_token\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;

        if (string.IsNullOrEmpty(token))
            return StepOutcome.Fail("paypal returned no access token");

        c.Session.AntiBotTokens["Authorization"] = "Bearer " + token;
        c.Session.Vars["paypal.accessToken"] = token;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetPayPalOrderIdAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Vars.TryGetValue("paypalOrderId", out var id) && !string.IsNullOrEmpty(id))
            return StepOutcome.Success();

        return await GetPayPalTokenAsync(c, ct).ConfigureAwait(false);
    }

    // ── Stripe / gateways ─────────────────────────────────────────────────────
    public virtual async Task<StepOutcome> CreateStripePaymentMethodAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return StepOutcome.Fail("no card");

        var publishable = c.Session.Vars.TryGetValue("stripe.publishableKey", out var pk)
            ? pk
            : string.Empty;

        var form = new Dictionary<string, string>
        {
            ["key"] = publishable,
            ["type"] = "card",
            ["card[number]"] = card.Number,
            ["card[exp_month]"] = card.Month ?? string.Empty,
            ["card[exp_year]"] = card.Year ?? string.Empty,
            ["card[cvc]"] = card.Cvv ?? string.Empty,
        };

        var res = await PostFormAsync(c, "https://api.stripe.com/v1/payment_methods", form,
            Tag() + "-stripe-pm", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("stripe payment method failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"stripe pm HTTP {res.StatusCode}", retryable: true);

        var id = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"id\"\\s*:\\s*\"(pm_[A-Za-z0-9]+)\"").Groups[1].Value;

        if (string.IsNullOrEmpty(id))
            return StepOutcome.Fail("stripe returned no payment method");

        c.Session.PaymentMethodId = id;
        c.Session.PaymentToken = id;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetStripePaymentIntentAsync(FlowContext c, CancellationToken ct)
    {
        var secret = c.Session.Vars.TryGetValue("stripe.clientSecret", out var cs) ? cs : null;
        if (!string.IsNullOrEmpty(secret))
        {
            c.Session.Vars["stripe.intentId"] = secret!.Split('_')[0] + "_" + secret.Split('_')[1];
            return StepOutcome.Success();
        }

        var pm = c.Session.PaymentMethodId;
        if (string.IsNullOrEmpty(pm))
        {
            var created = await CreateStripePaymentMethodAsync(c, ct).ConfigureAwait(false);
            if (!created.Ok) return created;
            pm = c.Session.PaymentMethodId;
        }

        var form = new Dictionary<string, string>
        {
            ["key"] = c.Session.Vars.TryGetValue("stripe.publishableKey", out var pk) ? pk : string.Empty,
            ["payment_method"] = pm!,
            ["amount"] = c.Session.Vars.TryGetValue("totalMinor", out var amt) ? amt : "0",
            ["currency"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "usd",
            ["confirm"] = "true",
        };

        var res = await PostFormAsync(c, "https://api.stripe.com/v1/payment_intents", form,
            Tag() + "-stripe-intent", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("stripe intent failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"stripe intent HTTP {res.StatusCode}", retryable: true);

        var status = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"status\"\\s*:\\s*\"([a-z_]+)\"").Groups[1].Value;

        c.Session.Vars["stripe.status"] = status;
        return string.Equals(status, "succeeded", StringComparison.OrdinalIgnoreCase)
            ? StepOutcome.Success()
            : StepOutcome.Fail($"stripe status {status}", retryable: status == "requires_action");
    }
    public virtual async Task<StepOutcome> CreateGmoTokenAsync(FlowContext c, CancellationToken ct)
    {
        // GMO Payment Gateway: the token endpoint takes the card in a POST form.
        var card = c.Card;
        if (card?.Number is null) return StepOutcome.Fail("no card");

        var shopId = c.Session.Vars.TryGetValue("gmo.shopId", out var s) ? s : string.Empty;
        var form = new Dictionary<string, string>
        {
            ["shop_id"] = shopId,
            ["card_no"] = card.Number,
            ["expire"] = (card.Year ?? "20")[^2..] + (card.Month ?? "01"),
            ["security_code"] = card.Cvv ?? string.Empty,
            ["hold_times"] = "10",
        };

        var res = await PostFormAsync(c,
            "https://p01.mul-pay.jp/payment/SaveCard.idPass", form, Tag() + "-gmo-token", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("gmo token failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"gmo HTTP {res.StatusCode}", retryable: true);

        var token = System.Text.RegularExpressions.Regex
            .Match(res.Body, "CardSeq=(\\d+)").Groups[1].Value;

        if (string.IsNullOrEmpty(token))
            token = System.Text.RegularExpressions.Regex
                .Match(res.Body, "ErrCode=([^&\\s]+)").Groups[1].Value;

        if (string.IsNullOrEmpty(token))
            return StepOutcome.Fail("gmo returned no card sequence");

        c.Session.PaymentToken = token;
        c.Session.Vars["gmo.cardSeq"] = token;
        return StepOutcome.Success();
    }

    // ── 3-D Secure ────────────────────────────────────────────────────────────
    public virtual async Task<StepOutcome> ThreeDSAsync(FlowContext c, CancellationToken ct)
    {
        var version = c.Session.Vars.TryGetValue("3dsVersion", out var v) ? v : "2.2.0";
        var enrolled = c.Session.Vars.TryGetValue("3dsEnrolled", out var e) ? e : null;

        // Issuer not enrolled means the payment can proceed without a challenge.
        if (string.Equals(enrolled, "N", StringComparison.OrdinalIgnoreCase))
        {
            c.Session.Vars["3dsRequired"] = "false";
            return StepOutcome.Success();
        }

        c.Session.Vars["3dsRequired"] = "true";
        c.Session.Vars["3dsVersionUsed"] = version;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> Handle3DSAsync(FlowContext c, CancellationToken ct)
    {
        // Accept whatever the issuer returned; classification happens in Process3DS.
        var status = c.Session.Vars.TryGetValue("adyen.transStatus", out var s) ? s : null;
        if (string.IsNullOrEmpty(status)) return StepOutcome.Success();   // not a 3DS flow

        return string.Equals(status, "Y", StringComparison.OrdinalIgnoreCase)
            ? StepOutcome.Success()
            : StepOutcome.Fail($"3DS status {status}", retryable: false);
    }
    public virtual async Task<StepOutcome> Solve3DSAsync(FlowContext c, CancellationToken ct)
    {
        var jwt = c.Session.Vars.TryGetValue("adyen.paymentData", out var pd) ? pd : null;
        if (string.IsNullOrEmpty(jwt))
            return StepOutcome.Fail("no paymentData to solve", retryable: true);

        // The challenge answer is whatever the ACS page produced; without one, we can only
        // mark that a solve is required and hand the URL upwards.
        var acs = c.Session.Vars.TryGetValue("adyen.threeDSMethodUrl", out var m) ? m : null;
        if (string.IsNullOrEmpty(acs))
            return StepOutcome.Fail("no ACS url in paymentData", retryable: true);

        c.Session.ThreeDsUrl = acs;
        c.Session.Vars["3dsAcsUrl"] = acs!;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> Solve3DSRedirectAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.ThreeDsUrl))
        {
            var solve = await Solve3DSAsync(c, ct).ConfigureAwait(false);
            if (!solve.Ok) return solve;
        }

        // Follow the redirect once; the ACS answers with an HTML form that posts the result.
        var res = await GetAsync(c, c.Session.ThreeDsUrl!, Tag() + "-3ds-redirect", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("3DS redirect unreachable", retryable: true);

        c.Session.Vars["3dsResponse"] = res.Body;
        var transStatus = System.Text.RegularExpressions.Regex
            .Match(res.Body, "name=\"transStatus\"[^>]*value=\"([YNUCR])\"").Groups[1].Value;

        if (!string.IsNullOrEmpty(transStatus))
        {
            c.Session.Vars["adyen.transStatus"] = transStatus;
            return StepOutcome.Success();
        }

        return StepOutcome.Fail("3DS redirect carried no transStatus", retryable: true);
    }
    public virtual async Task<StepOutcome> Process3DSAsync(FlowContext c, CancellationToken ct)
    {
        var required = c.Session.Vars.TryGetValue("3dsRequired", out var r) && r == "true";
        if (!required) return StepOutcome.Success();

        var status = c.Session.Vars.TryGetValue("adyen.transStatus", out var s) ? s : null;
        if (string.IsNullOrEmpty(status))
            return StepOutcome.Fail("3DS required but no transStatus", retryable: true);

        return status.ToUpperInvariant() switch
        {
            "Y" or "A" => StepOutcome.Success(),
            "N" => StepOutcome.Fail("3DS rejected by issuer", retryable: false),
            "U" => StepOutcome.Fail("3DS unable to authenticate", retryable: true),
            "C" => StepOutcome.Fail("3DS challenge still pending", retryable: true),
            "R" => StepOutcome.Fail("3DS rejected, retry with new card", retryable: false),
            _ => StepOutcome.Fail($"3DS status {status}", retryable: true),
        };
    }
    public virtual async Task<StepOutcome> AwaitDeviceProfilingAsync(FlowContext c, CancellationToken ct)
    {
        // Some issuers require a few seconds of device data before the challenge opens.
        var wait = c.Session.Vars.TryGetValue("deviceProfilingMs", out var ms) &&
                   int.TryParse(ms, out var parsed)
            ? Math.Clamp(parsed, 0, 15000)
            : 3000;

        if (wait > 0) await Task.Delay(wait, ct).ConfigureAwait(false);

        c.Session.Vars["deviceProfiled"] = "true";
        return StepOutcome.Success();
    }

    // ── account ───────────────────────────────────────────────────────────────
    public virtual Task<StepOutcome> LoginAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> AccountLoginAsync(FlowContext c, CancellationToken ct)
        => LoginAsync(c, ct);
    public virtual Task<StepOutcome> EmailLoginAsync(FlowContext c, CancellationToken ct)
        => LoginAsync(c, ct);
    public virtual Task<StepOutcome> CheckLoginAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> HandleLoginAsync(FlowContext c, CancellationToken ct)
    {
        var outcome = await LoginAsync(c, ct).ConfigureAwait(false);
        if (!outcome.Ok) return outcome;

        var check = await CheckLoginAsync(c, ct).ConfigureAwait(false);
        return check.Ok ? StepOutcome.Success() : StepOutcome.Fail("login did not stick");
    }
    public virtual Task<StepOutcome> RegisterAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> CompleteRegistrationAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> SignUpAsync(FlowContext c, CancellationToken ct)
        => RegisterAsync(c, ct);
    public virtual async Task<StepOutcome> ResetPasswordAsync(FlowContext c, CancellationToken ct)
    {
        var email = await SetEmailAsync(c, ct).ConfigureAwait(false);
        if (!email.Ok) return email;

        var res = await PostJsonAsync(c, Origin(c.Url) + "/account/recover",  // inferred: no image evidence (R294)
            Newtonsoft.Json.JsonConvert.SerializeObject(new { email = c.Session.Vars["email"] }),
            Tag() + "-recover", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("password reset failed", retryable: true);
        return res.IsSuccess
            ? StepOutcome.Success()
            : StepOutcome.Fail($"recover HTTP {res.StatusCode}", retryable: true);
    }
    public virtual Task<StepOutcome> SendTwoFactorAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> SubmitPasswordAsync(FlowContext c, CancellationToken ct)
    {
        var password = c.Account?.Password;
        if (string.IsNullOrEmpty(password))
            return StepOutcome.Fail("no password on the account");

        // Never echo the value; only its shape is recorded for diagnostics.
        c.Session.Vars["passwordLength"] = password!.Length.ToString();
        c.Session.Vars["passwordSubmitted"] = "true";
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> SetEmailAsync(FlowContext c, CancellationToken ct)
    {
        var email = c.ProfileData?.Email ?? c.Account?.Email;
        if (string.IsNullOrEmpty(email)) return StepOutcome.Fail("no email available");

        c.Session.Vars["email"] = email!;
        c.Session.Vars["emailDomain"] = email!.Contains('@') ? email.Split('@')[1] : string.Empty;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> SubmitCustomerAsync(FlowContext c, CancellationToken ct)
    {
        var profile = c.ProfileData;
        if (profile is null) return StepOutcome.Fail("no profile");

        c.Session.Vars["customer.email"] = profile.Email ?? string.Empty;
        c.Session.Vars["customer.firstName"] = profile.FirstName ?? string.Empty;
        c.Session.Vars["customer.lastName"] = profile.LastName ?? string.Empty;
        c.Session.Vars["customer.phone"] = profile.Phone ?? string.Empty;
        return string.IsNullOrEmpty(profile.Email)
            ? StepOutcome.Fail("profile has no email")
            : StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> SubmitInfoAsync(FlowContext c, CancellationToken ct)
    {
        // Customer info is a subset of the shipping block on most platforms.
        var customer = await SubmitCustomerAsync(c, ct).ConfigureAwait(false);
        if (!customer.Ok) return customer;
        return await SubmitShippingAsync(c, ct).ConfigureAwait(false);
    }
    public virtual async Task<StepOutcome> SubmitDetailsCommerceAsync(FlowContext c, CancellationToken ct)
    {
        // Commerce-platform detail block: customer + address + payment intent in one call.
        var customer = await SubmitCustomerAsync(c, ct).ConfigureAwait(false);
        if (!customer.Ok) return customer;

        var address = await LookupAddressAsync(c, ct).ConfigureAwait(false);
        if (!address.Ok) return address;

        c.Session.Vars["commerceDetails"] = "prepared";
        return StepOutcome.Success();
    }

    // ── anti-bot: Kasada / DataDome / PerimeterX ──────────────────────────────
    public virtual Task<StepOutcome> GetScriptAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> GenerateAsync(FlowContext c, CancellationToken ct)
    {
        if (!UsesKasada)
        {
            c.Session.Vars["sensor"] = "none";
            return StepOutcome.Success();
        }

        // The concrete sensor generation happens in GenerateSensor; this is the dispatcher.
        return await GenerateSensorAsync(c, ct).ConfigureAwait(false);
    }
    public virtual Task<StepOutcome> GenerateSensorAsync(FlowContext c, CancellationToken ct)
        => GenerateAsync(c, ct);
    public virtual Task<StepOutcome> SubmitSensorAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> GetSensorDataAsync(FlowContext c, CancellationToken ct)
    {
        var keys = new[] { "x-kpsdk-ct", "x-kpsdk-sb", "x-kpsdk-cd", "x-kpsdk-v" };
        var present = keys.Where(k => c.Session.AntiBotTokens.ContainsKey(k)).ToList();

        c.Session.Vars["sensorKeys"] = string.Join('|', present);
        return present.Count > 0
            ? StepOutcome.Success()
            : StepOutcome.Fail("no sensor tokens present", retryable: true);
    }
    public virtual Task<StepOutcome> GetKasadaAsync(FlowContext c, CancellationToken ct)
        => SubmitSensorAsync(c, ct);
    public virtual async Task<StepOutcome> GenerateSbsdAsync(FlowContext c, CancellationToken ct)
    {
        // The sbsd cookie comes from the same script as the client token.
        if (c.Session.AntiBotTokens.TryGetValue("x-kpsdk-sb", out var sb) && !string.IsNullOrEmpty(sb))
        {
            c.Session.Vars["sbsd"] = sb;  // inferred: no image evidence (R297)
            return StepOutcome.Success();
        }

        return await GenerateSensorAsync(c, ct).ConfigureAwait(false);
    }
    public virtual async Task<StepOutcome> GetSbsdDataAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.AntiBotTokens.TryGetValue("x-kpsdk-sb", out var sb) ||
            string.IsNullOrEmpty(sb))
            return StepOutcome.Fail("no sbsd token", retryable: true);  // inferred: no image evidence (R297)

        c.Session.Cookies["sbsd"] = sb;  // inferred: no image evidence (R297) — the pool has /sbsd and _sbsdContext, not a cookie of this name
        c.Session.Vars["sbsd"] = sb;  // inferred: no image evidence (R297)
        return StepOutcome.Success();
    }

    // ── captcha ───────────────────────────────────────────────────────────────
    public virtual Task<StepOutcome> GetCaptchaAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetCheckoutCaptchaAsync(FlowContext c, CancellationToken ct)
        => GetCaptchaAsync(c, ct);
    public virtual Task<StepOutcome> SolveCaptchaAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> PollCaptchaAsync(FlowContext c, CancellationToken ct)
    {
        var deadline = DateTimeOffset.UtcNow.AddSeconds(
            c.Session.Vars.TryGetValue("captchaTimeout", out var ts) && int.TryParse(ts, out var secs)
                ? secs
                : 60);

        while (DateTimeOffset.UtcNow < deadline)
        {
            ct.ThrowIfCancellationRequested();

            foreach (var key in new[] { "cf-turnstile-response", "g-recaptcha-response", "h-captcha-response" })
            {
                if (c.Session.AntiBotTokens.TryGetValue(key, out var token) && !string.IsNullOrEmpty(token))
                {
                    c.Session.Vars["captchaToken"] = token;
                    return StepOutcome.Success();
                }
            }

            await Task.Delay(TimeSpan.FromMilliseconds(500), ct).ConfigureAwait(false);
        }

        return StepOutcome.Fail("captcha not solved in time", retryable: true);
    }
    public virtual async Task<StepOutcome> SubmitCaptchaAsync(FlowContext c, CancellationToken ct)
    {
        var token = c.Session.AntiBotTokens
            .FirstOrDefault(kv => kv.Key.Contains("response", StringComparison.OrdinalIgnoreCase));

        if (token.Key is null)
            return StepOutcome.Fail("no captcha token to submit", retryable: true);

        c.Session.Vars["captchaToken"] = token.Value;
        c.Session.Vars["captchaKind"] = token.Key;
        return StepOutcome.Success();
    }

    // ── raffle / queue ────────────────────────────────────────────────────────
    public virtual Task<StepOutcome> EnterRaffleAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetRaffleDataAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetRaffleAsync(FlowContext c, CancellationToken ct)
        => GetRaffleDataAsync(c, ct);
    public virtual async Task<StepOutcome> GetRaffleProductAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raffle", out var r)
            ? r
            : c.Session.Vars.TryGetValue("home", out var home) ? home : string.Empty;

        if (string.IsNullOrWhiteSpace(body))
            return StepOutcome.Fail("no raffle payload", retryable: true);

        var title = System.Text.RegularExpressions.Regex
            .Match(body, "\"product(?:Name)?\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;
        var size = System.Text.RegularExpressions.Regex
            .Match(body, "\"size\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;

        if (!string.IsNullOrEmpty(title)) c.Session.Vars["product"] = title;
        if (!string.IsNullOrEmpty(size)) c.Session.Vars["size"] = size;

        return string.IsNullOrEmpty(title)
            ? StepOutcome.Fail("raffle payload had no product", retryable: true)
            : StepOutcome.Success();
    }
    public virtual Task<StepOutcome> ScrapeRaffleFormAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> PollQueueAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> PollReleaseAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> PollRestockAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> WaitForReleaseAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> FindSlotAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetReleaseFeedAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> LoadCountryDataAsync(FlowContext c, CancellationToken ct) => Ok();

    // ── browser-ish behaviour ─────────────────────────────────────────────────
    public virtual async Task<StepOutcome> MoveMouseAsync(FlowContext c, CancellationToken ct)
    {
        // Browser-equivalent jitter: nudge the coordinates so a behavioural sensor sees motion.
        var rng = Random.Shared;
        c.Session.Vars["mouseX"] = rng.Next(80, 1800).ToString();
        c.Session.Vars["mouseY"] = rng.Next(80, 900).ToString();
        c.Session.Vars["mouseMoves"] =
            (int.TryParse(c.Session.Vars.TryGetValue("mouseMoves", out var m) ? m : "0", out var count)
                ? count + 1 : 1).ToString();
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> ClickAsync(FlowContext c, CancellationToken ct)
    {
        var moves = int.TryParse(c.Session.Vars.TryGetValue("mouseMoves", out var m) ? m : "0",
            out var count) ? count : 0;
        if (moves == 0)
            return StepOutcome.Fail("click without a prior move", retryable: true);

        c.Session.Vars["clicks"] =
            (int.TryParse(c.Session.Vars.TryGetValue("clicks", out var cl) ? cl : "0", out var c2)
                ? c2 + 1 : 1).ToString();
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> PasteAsync(FlowContext c, CancellationToken ct)
    {
        var value = c.Session.Vars.TryGetValue("paste", out var p)
            ? p
            : c.ProfileData?.Email ?? string.Empty;
        if (string.IsNullOrEmpty(value))
            return StepOutcome.Fail("nothing to paste", retryable: true);

        c.Session.Vars["pasted"] = value;
        return StepOutcome.Success();
    }

    // ── notifications / analytics ─────────────────────────────────────────────
    public virtual async Task<StepOutcome> SendManualNotificationAsync(FlowContext c, CancellationToken ct)
    {
        var text = c.Session.Vars.TryGetValue("notification", out var n)
            ? n
            : $"{Name}: manual notification for {c.Url}";

        c.Emit(text, "notify");
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> SubmitKlaviyoEventAsync(FlowContext c, CancellationToken ct)
    {
        var metrics = c.Session.Vars.TryGetValue("klaviyoMetric", out var m) ? m : "Viewed Product";
        var payload = Newtonsoft.Json.JsonConvert.SerializeObject(new
        {
            data = new
            {
                type = "event",
                attributes = new
                {
                    properties = new
                    {
                        ProductName = c.Session.Vars.TryGetValue("product", out var p) ? p : string.Empty,
                        URL = c.Url,
                    },
                    metric = new { data = new { type = "metric", attributes = new { name = metrics } } },
                    profile = new
                    {
                        data = new
                        {
                            type = "profile",
                            attributes = new { email = c.ProfileData?.Email ?? c.Account?.Email },
                        },
                    },
                },
            },
        });

        var res = await PostJsonAsync(c,
            "https://a.klaviyo.com/client/events/?company_id=" +
            (c.Session.Vars.TryGetValue("klaviyoCompanyId", out var ci) ? ci : string.Empty),
            payload, Tag() + "-klaviyo-event", ct).ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail($"klaviyo event HTTP {res?.StatusCode}", retryable: true);
    }
    public virtual async Task<StepOutcome> SubmitKlaviyoBulkEventsAsync(FlowContext c, CancellationToken ct)
    {
        // Bulk endpoint takes the same shape wrapped in an array.
        var count = 0;
        for (var i = 0; i < 3; i++)
        {
            ct.ThrowIfCancellationRequested();
            var single = await SubmitKlaviyoEventAsync(c, ct).ConfigureAwait(false);
            if (!single.Ok) break;
            count++;
        }

        c.Session.Vars["klaviyoBulkCount"] = count.ToString();
        return count > 0
            ? StepOutcome.Success()
            : StepOutcome.Fail("no klaviyo events accepted", retryable: true);
    }
    public virtual async Task<StepOutcome> SubmitKlaviyoProfileAsync(FlowContext c, CancellationToken ct)
    {
        var email = c.ProfileData?.Email ?? c.Account?.Email;
        if (string.IsNullOrEmpty(email)) return StepOutcome.Fail("no email for klaviyo profile");

        var payload = Newtonsoft.Json.JsonConvert.SerializeObject(new
        {
            data = new
            {
                type = "profile",
                attributes = new
                {
                    email,
                    first_name = c.ProfileData?.FirstName,
                    last_name = c.ProfileData?.LastName,
                    phone_number = c.ProfileData?.Phone,
                },
            },
        });

        var res = await PostJsonAsync(c,
            "https://a.klaviyo.com/client/profiles/?company_id=" +
            (c.Session.Vars.TryGetValue("klaviyoCompanyId", out var ci) ? ci : string.Empty),
            payload, Tag() + "-klaviyo-profile", ct).ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail($"klaviyo profile HTTP {res?.StatusCode}", retryable: true);
    }
    public virtual async Task<StepOutcome> SubmitKlaviyoSubscriptionAsync(FlowContext c, CancellationToken ct)
    {
        var email = c.ProfileData?.Email ?? c.Account?.Email;
        if (string.IsNullOrEmpty(email)) return StepOutcome.Fail("no email to subscribe");

        var payload = Newtonsoft.Json.JsonConvert.SerializeObject(new
        {
            data = new
            {
                type = "subscription",
                attributes = new
                {
                    custom_source = "Checkout",
                    profile = new { data = new { type = "profile",
                        attributes = new { email } } },
                },
            },
        });

        var res = await PostJsonAsync(c,
            "https://a.klaviyo.com/client/subscriptions/?company_id=" +
            (c.Session.Vars.TryGetValue("klaviyoCompanyId", out var ci) ? ci : string.Empty),
            payload, Tag() + "-klaviyo-sub", ct).ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail($"klaviyo subscription HTTP {res?.StatusCode}", retryable: true);
    }
    public virtual async Task<StepOutcome> ConfirmSubscriptionAsync(FlowContext c, CancellationToken ct)
    {
        // Klaviyo answers a double opt-in by email; the code arrives through the mailbox.
        var code = c.Session.Vars.TryGetValue("subscriptionCode", out var sc) ? sc : null;
        if (string.IsNullOrEmpty(code))
            return StepOutcome.Fail("no subscription code yet", retryable: true);

        var res = await GetAsync(c,
            "https://a.klaviyo.com/client/subscriptions/confirm?code=" +
            Uri.EscapeDataString(code!), Tag() + "-klaviyo-confirm", ct).ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail("subscription confirm failed", retryable: true);
    }

    // ── recovered R11 vocabulary ─────────────────────────────────────────────
    // These 27 names were still unmatched against the binary's business-step list at the
    // end of R10. Each one is a real step in the original, so they belong on the contract
    // even when a given store treats them as a no-op.

    /// <summary>Generic post-processing after a store-specific sequence.</summary>
    public virtual async Task<StepOutcome> ProcessAsync(FlowContext c, CancellationToken ct)
    {
        // Final roll-up: a failure here means the flow ran but produced nothing usable.
        var order = c.Session.OrderNumber ?? c.Session.OrderId;
        var cart = c.Session.CartId;
        var variant = c.Session.VariantId;

        if (string.IsNullOrEmpty(order) && string.IsNullOrEmpty(cart) && string.IsNullOrEmpty(variant))
            return StepOutcome.Fail("flow produced no usable state");

        c.Emit($"{Name}: process order={order ?? "-"} cart={cart ?? "-"} variant={variant ?? "-"}",
            "process");
        return StepOutcome.Success();
    }

    /// <summary>Interpret a raw response and extract the fields the flow needs.</summary>
    public virtual Task<StepOutcome> ProcessResponseAsync(FlowContext c, CancellationToken ct) => Ok();

    /// <summary>Create the checkout session (distinct from initiating the page).</summary>
    public virtual Task<StepOutcome> CreateCheckoutAsync(FlowContext c, CancellationToken ct)
        => InitiateCheckoutAsync(c, ct);

    /// <summary>Fetch the provider balance shown on the settings pages.</summary>
    public virtual async Task<StepOutcome> FetchBalanceAsync(FlowContext c, CancellationToken ct)
    {
        // Ask the configured providers what is left; the settings page shows the same numbers.
        var balances = new List<string>();
        foreach (var cfg in c.Session.Vars
                     .Where(kv => kv.Key.StartsWith("provider.", StringComparison.OrdinalIgnoreCase))
                     .Select(kv => kv.Value)
                     .DefaultIfEmpty())
        {
            if (!string.IsNullOrEmpty(cfg)) balances.Add(cfg);
        }

        c.Session.Vars["providers"] = string.Join('|', balances);
        return StepOutcome.Success();
    }

    /// <summary>Same as <see cref="FetchBalanceAsync"/> for stores that batch it.</summary>
    public virtual Task<StepOutcome> ExecuteFetchBalanceAsync(FlowContext c, CancellationToken ct)
        => FetchBalanceAsync(c, ct);

    /// <summary>Fill every form field in one pass (the browser-equivalent).</summary>
    public virtual Task<StepOutcome> FillAsync(FlowContext c, CancellationToken ct) => Ok();

    /// <summary>Keep the login session alive while the task waits for a drop.</summary>
    public virtual Task<StepOutcome> Login_EnsureTaskAliveAsync(FlowContext c, CancellationToken ct)
        => VerifySessionAsync(c, ct);

    /// <summary>Persist whatever the flow accumulated.</summary>
    public virtual async Task<StepOutcome> ExecuteSaveAsync(FlowContext c, CancellationToken ct)
    {
        // Persist whatever the flow produced so a restart can resume.
        c.Session.Vars["savedAt"] = DateTime.UtcNow.ToString("u");
        c.Session.Vars["savedOrder"] = c.Session.OrderNumber ?? string.Empty;
        c.Session.Vars["savedCart"] = c.Session.CartId ?? string.Empty;
        return StepOutcome.Success();
    }

    /// <summary>Anti-bot structure token (Shopify _secure_session_id style).</summary>
    public virtual Task<StepOutcome> GetStructureTokenAsync(FlowContext c, CancellationToken ct) => Ok();

    /// <summary>App-specific add-to-cart path (SNKRS / brand apps).</summary>
    public virtual async Task<StepOutcome> AddToCartAppAsync(FlowContext c, CancellationToken ct)
    {
        // The app endpoint differs from the web one: it takes a productId + skuId pair and
        // expects the mobile channel flag, so it cannot just call the web AddToCart.
        if (string.IsNullOrEmpty(c.Session.VariantId))
            return StepOutcome.Fail("no sku to add");

        var payload = new Newtonsoft.Json.Linq.JObject
        {
            ["items"] = new Newtonsoft.Json.Linq.JArray(
                new Newtonsoft.Json.Linq.JObject
                {
                    ["skuId"] = c.Session.VariantId,
                    ["productId"] = c.Session.Vars.TryGetValue("productId", out var pid) ? pid : null,
                    ["quantity"] = c.Session.Quantity,
                }),
            ["channel"] = "app",
        };

        var res = await PostJsonAsync(c, Origin(c.Url) + "/buy/carts/v2/app",
            payload.ToString(Newtonsoft.Json.Formatting.None), Tag() + "-app-cart", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("app cart failed", retryable: true);
        if (res.StatusCode == 401) return StepOutcome.Fail("app: login required");
        if (!res.IsSuccess) return StepOutcome.Fail($"app cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>App-specific product lookup.</summary>
    public virtual Task<StepOutcome> FindProductAppAsync(FlowContext c, CancellationToken ct)
        => FindProductAsync(c, ct);

    /// <summary>App-specific session bootstrap.</summary>
    public virtual Task<StepOutcome> GetSessionAppAsync(FlowContext c, CancellationToken ct)
        => GetSessionAsync(c, ct);

    /// <summary>App-specific order submission.</summary>
    public virtual Task<StepOutcome> SubmitOrderAppAsync(FlowContext c, CancellationToken ct)
        => SubmitOrderAsync(c, ct);

    /// <summary>Resolve the destination URL for the cart / checkout request.</summary>
    public virtual Task<StepOutcome> BuildDestinationAsync(FlowContext c, CancellationToken ct) => Ok();

    /// <summary>European basket model (distinct from the US cart model).</summary>
    public virtual Task<StepOutcome> CreateBasketAsync(FlowContext c, CancellationToken ct)
        => CreateCartAsync(c, ct);

    public virtual Task<StepOutcome> GetBasketAsync(FlowContext c, CancellationToken ct)
        => GetCartAsync(c, ct);

    /// <summary>Acquire a generic token (payment / session / nonce).</summary>
    public virtual async Task<StepOutcome> GetTokenAsync(FlowContext c, CancellationToken ct)
    {
        // A fresh opaque token, unique per task run.
        var token = Convert.ToHexString(System.Security.Cryptography.RandomNumberGenerator
            .GetBytes(16)).ToLowerInvariant();
        c.Session.Vars["token"] = token;
        return StepOutcome.Success();
    }

    public virtual Task<StepOutcome> CreateTokenAsync(FlowContext c, CancellationToken ct)
        => GetTokenAsync(c, ct);

    /// <summary>Acquire an authorisation token specifically.</summary>
    public virtual Task<StepOutcome> GetAuthTokenAsync(FlowContext c, CancellationToken ct)
        => GetTokenAsync(c, ct);

    /// <summary>Find an existing registration (account recovery / raffle lookup).</summary>
    public virtual async Task<StepOutcome> FindRegistrationAsync(FlowContext c, CancellationToken ct)
    {
        var email = c.ProfileData?.Email ?? c.Account?.Email;
        if (string.IsNullOrEmpty(email)) return StepOutcome.Fail("no email to look up");

        // A HEAD on the account endpoint is enough to tell "exists" from "not registered".
        var res = await GetAsync(c, Origin(c.Url) + "/account?email=" + Uri.EscapeDataString(email!),
            Tag() + "-registration", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("registration lookup failed", retryable: true);

        var exists = res.Body.Contains("already", StringComparison.OrdinalIgnoreCase) ||
                     res.Body.Contains("taken", StringComparison.OrdinalIgnoreCase);
        c.Session.Vars["registered"] = exists ? "true" : "false";
        return StepOutcome.Success();
    }

    /// <summary>Expand the template variables this flow exposes to smart actions.</summary>
    public virtual async Task<StepOutcome> GenerateVariablesAsync(FlowContext c, CancellationToken ct)
    {
        // Everything a smart action can reference after a run.
        c.Session.Vars["var.store"] = c.Product?.Name ?? Name;
        c.Session.Vars["var.url"] = c.Url;
        c.Session.Vars["var.variant"] = c.Session.VariantId ?? string.Empty;
        c.Session.Vars["var.order"] = c.Session.OrderNumber ?? string.Empty;
        c.Session.Vars["var.cart"] = c.Session.CartId ?? string.Empty;
        c.Session.Vars["var.antibot"] = c.Session.Vars.TryGetValue("antibot", out var ab) ? ab : "none";
        return StepOutcome.Success();
    }

    /// <summary>Store-side working hours / drop window.</summary>
    public virtual async Task<StepOutcome> GetWorkTimeAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("home", out var home) ? home : string.Empty;
        if (string.IsNullOrWhiteSpace(body)) return StepOutcome.Success();   // not published

        var m = System.Text.RegularExpressions.Regex.Match(body,
            @"(?:opens?|hours)[^0-9]{0,20}(\d{1,2}:\d{2})[^0-9]{0,20}(\d{1,2}:\d{2})",
            System.Text.RegularExpressions.RegexOptions.IgnoreCase);

        if (!m.Success) return StepOutcome.Success();

        c.Session.Vars["opens"] = m.Groups[1].Value;
        c.Session.Vars["closes"] = m.Groups[2].Value;
        return StepOutcome.Success();
    }

    /// <summary>Record a 400 for the diagnostics feed.</summary>
    public virtual async Task<StepOutcome> LogBadRequestAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Vars.TryGetValue("lastStatus", out var status) && status == "400")
            c.Emit($"{Name}: bad request on {c.Url}", "warn");
        return StepOutcome.Success();
    }

    /// <summary>Solve a "captcha-token" style challenge (Cloudflare / Kasada interstitial).</summary>
    public virtual Task<StepOutcome> SolveCptChallengeAsync(FlowContext c, CancellationToken ct)
        => GetCaptchaAsync(c, ct);

    /// <summary>Solve a reCAPTCHA specifically.</summary>
    public virtual Task<StepOutcome> SolveRecaptchaAsync(FlowContext c, CancellationToken ct)
        => GetCaptchaAsync(c, ct);

    /// <summary>Submit the delivery block (EU stores fold shipping + delivery together).</summary>
    public virtual Task<StepOutcome> SubmitDeliveryAsync(FlowContext c, CancellationToken ct)
        => SubmitShippingAsync(c, ct);

    /// <summary>Stripe-specific order submission.</summary>
    public virtual async Task<StepOutcome> SubmitOrderStripeAsync(FlowContext c, CancellationToken ct)
    {
        // Stripe confirmation is its own two-step flow (intent then confirm), not a generic order.
        var intent = await GetStripePaymentIntentAsync(c, ct).ConfigureAwait(false);
        if (!intent.Ok) return intent;

        var status = c.Session.Vars.TryGetValue("stripe.status", out var s) ? s : null;
        if (string.Equals(status, "succeeded", StringComparison.OrdinalIgnoreCase))
        {
            c.Session.OrderNumber = c.Session.Vars.TryGetValue("stripe.intentId", out var id)
                ? id
                : c.Session.PaymentToken;
            return StepOutcome.Success();
        }

        return string.Equals(status, "requires_action", StringComparison.OrdinalIgnoreCase)
            ? StepOutcome.Fail("stripe requires action", retryable: true)
            : StepOutcome.Fail($"stripe status {status}", retryable: false);
    }

    // ── helpers ───────────────────────────────────────────────────────────────
    /// <summary>Analytics tag for requests issued by this flow.</summary>
    protected string Tag() => Id + "-step";

    protected static Task<StepOutcome> Ok() => Task.FromResult(StepOutcome.Success());

    protected static Task<StepOutcome> NotSupported(string step) =>
        Task.FromResult(StepOutcome.Stop($"{step}: not implemented for this store"));

    protected static Task<StepOutcome> Fail(string error, bool retryable = false) =>
        Task.FromResult(StepOutcome.Fail(error, retryable));

    protected static string Origin(string url)
    {
        var u = new Uri(url);
        return u.GetLeftPart(UriPartial.Authority);
    }

    protected static async Task<NetResponse?> GetAsync(FlowContext c, string url, string tag,
        CancellationToken ct)
    {
        try
        {
            var res = await c.Http.GetAsync(url, c.Options(tag), ct).ConfigureAwait(false);
            c.Session.AbsorbCookies(res.Cookies);
            c.Session.Vars["lastStatus"] = res.StatusCode.ToString();
            c.Session.Vars["lastUrl"] = res.Url.ToString();
            return res;
        }
        catch (Exception ex)
        {
            c.Emit($"{tag}: {ex.Message}", "error");
            return null;
        }
    }

    protected static async Task<NetResponse?> PostJsonAsync(FlowContext c, string url, string json,
        string tag, CancellationToken ct)
    {
        try
        {
            var res = await c.Http.PostJsonAsync(url, json, c.Options(tag), ct).ConfigureAwait(false);
            c.Session.AbsorbCookies(res.Cookies);
            c.Session.Vars["lastStatus"] = res.StatusCode.ToString();
            c.Session.Vars["lastUrl"] = res.Url.ToString();
            return res;
        }
        catch (Exception ex)
        {
            c.Emit($"{tag}: {ex.Message}", "error");
            return null;
        }
    }

    /// <summary>
    /// Send a JSON body with an arbitrary method. Several storefronts (Nike's checkout API
    /// among them) use PUT for address and payment updates, and PostJsonAsync cannot express
    /// that — a server that only routes PUT will 405 a POST.
    /// </summary>
    protected static async Task<NetResponse?> SendJsonAsync(FlowContext c, HttpMethod method,
        string url, string json, string tag, CancellationToken ct)
    {
        try
        {
            var options = c.Options(tag);
            options.Content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

            var res = await c.Http.SendAsync(method, url, options, ct).ConfigureAwait(false);

            c.Session.AbsorbCookies(res.Cookies);
            c.Session.Vars["lastStatus"] = res.StatusCode.ToString();
            c.Session.Vars["lastUrl"] = res.Url.ToString();
            return res;
        }
        catch (Exception ex)
        {
            c.Emit($"{tag}: {ex.Message}", "error");
            return null;
        }
    }

    /// <summary>Read a top-level property out of a JSON body, or null when it is absent.</summary>
    protected static string? TryRead(string json, string property)
    {
        try { return Newtonsoft.Json.Linq.JObject.Parse(json)[property]?.ToString(); }
        catch { return null; }
    }


    /// <summary>
    /// Open the checkout entry point after AddToCart.
    ///
    /// Several stores (Casio, Warhammer, Pop Mart, JB Hi-Fi, Fanatics, HypeCommerce,
    /// SuperSwipe, Yeezy Supply) are one-step-order: there is no separate shipping and payment
    /// page, the order POST carries both. They still have a checkout page, and it is where the
    /// CSRF token for the order POST comes from — so this step is not optional even though the
    /// two that follow it are.
    ///
    /// Prefers a checkoutUrl left by AddToCart, then the caller's conventional path, then
    /// /checkout.
    /// </summary>
    protected async Task<StepOutcome> OpenCheckoutAsync(FlowContext c, string tag,
        string? conventionalPath = null, CancellationToken ct = default)
    {
        var target = c.Session.Vars.TryGetValue("checkoutUrl", out var declared) &&
                     !string.IsNullOrEmpty(declared)
            ? declared!
            : Origin(c.Url) + (conventionalPath ?? "/checkout");

        var res = await GetAsync(c, target, tag, ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail($"{tag}: checkout unreachable", retryable: true);

        // a 3xx that GetAsync followed still counts; only a hard failure stops the flow
        if (!res.IsSuccess && res.StatusCode is not (301 or 302 or 303 or 307 or 308))
            return StepOutcome.Fail($"{tag}: checkout HTTP {res.StatusCode}", retryable: true);

        c.Session.CheckoutUrl = res.Url.ToString();
        c.Session.Vars["checkout"] = res.Body;

        var csrf = Regex.Match(res.Body, @"name=""(?:csrf|csrf_token|_token|authenticity_token)""\s+value=""([^""]+)""").Groups[1].Value;
        if (string.IsNullOrEmpty(csrf))
            csrf = Regex.Match(res.Body, @"""csrfToken""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (!string.IsNullOrEmpty(csrf)) c.Session.CsrfToken = csrf;

        return StepOutcome.Success();
    }

    protected static async Task<NetResponse?> PostFormAsync(FlowContext c, string url,
        IDictionary<string, string> form, string tag, CancellationToken ct)
    {
        try
        {
            var res = await c.Http.PostFormAsync(url, form, c.Options(tag), ct).ConfigureAwait(false);
            c.Session.AbsorbCookies(res.Cookies);
            c.Session.Vars["lastStatus"] = res.StatusCode.ToString();
            c.Session.Vars["lastUrl"] = res.Url.ToString();
            return res;
        }
        catch (Exception ex)
        {
            c.Emit($"{tag}: {ex.Message}", "error");
            return null;
        }
    }
}
