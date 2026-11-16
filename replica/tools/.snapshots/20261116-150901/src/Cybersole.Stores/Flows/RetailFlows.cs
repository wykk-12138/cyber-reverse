using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;
/// <summary>
/// Yeezy — a Swell storefront, not the old Yeezy Supply.
///
/// The previous implementation was 150 lines of guesswork: an Akamai queue at /queue, a
/// "queueToken" scraped from it, variantId/sku/size regexes over the HTML, and a cart POST
/// carrying that token. A live capture shows none of it exists:
///
///   GET https://yzy-prod.swell.store/api/settings      <- Swell
///   GET https://yzy-prod.swell.store/api/cart          <- Swell
///   GET https://yeezy.com/api/geo
///   POST https://yeezy.com/cdn-cgi/challenge-platform/...  <- Cloudflare, not Akamai
///
/// Swell is a headless commerce platform: the storefront is SvelteKit and every bit of state
/// lives behind the *swell.store subdomain, which is a different host from the page. So the
/// cart calls have to be addressed to that host, not to the storefront origin.
///
/// Verified:   /api/settings and /api/cart answer on the swell host; Cloudflare sits in front.
/// Inferred:   the product and cart-item paths (Swell's documented shape), marked below.
///
/// yeezysupply.com is dead — the old domain resolves but serves nothing, so only yeezy.com is
/// claimed. Claiming a dead host would route its URLs nowhere.
/// </summary>
public sealed class YeezySupplyFlow : StoreFlow
{
    public override string Id => "yeezysupply";
    public override string Name => "Yeezy Supply";

    /// <summary>yeezysupply.com is retired; only the live domain is claimed.</summary>
    public override IReadOnlyList<string> Domains => new[] { "yeezy.com" };

    /// <summary>
    /// Swell's API host. The storefront page does not serve /api/cart; the platform subdomain
    /// does. Verified from the capture.
    /// </summary>
    private const string SwellHost = "https://yzy-prod.swell.store";

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/", "yeezy-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("yeezy unreachable", retryable: true);

        if (res.StatusCode == 403)
            return StepOutcome.Fail("yeezy blocked (cloudflare)", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"yeezy HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["home"] = res.Body;

        // the platform handshake: settings tells us the store id and currency
        var settings = await GetAsync(c, SwellHost + "/api/settings", "yeezy-settings", ct)
            .ConfigureAwait(false);

        if (settings is { IsSuccess: true })
        {
            c.Session.Vars["settings"] = settings.Body;

            var currency = Regex.Match(settings.Body, @"""currency""\s*:\s*""([A-Z]{3})""");
            if (currency.Success) c.Session.Vars["currency"] = currency.Groups[1].Value;
        }

        return StepOutcome.Success();
    }

    /// <summary>
    /// Swell keeps the cart server-side and identifies it by cookie. Fetching it creates one,
    /// which is what AddToCart posts into.
    /// </summary>
    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, SwellHost + "/api/cart", "yeezy-cart", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("yeezy cart unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"yeezy cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;

        var id = TryRead(res.Body, "id");
        if (!string.IsNullOrEmpty(id)) c.Session.CartId = id;

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "yeezy-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("yeezy product unreachable", retryable: true);
        if (res.StatusCode == 403)
            return StepOutcome.Fail("yeezy product blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"yeezy product HTTP {res.StatusCode}",
            retryable: true);

        c.Session.Vars["raw"] = res.Body;

        var title = Regex.Match(res.Body, @"<title>([^<|]+)").Groups[1].Value.Trim();
        if (!string.IsNullOrEmpty(title)) c.Session.Vars["product"] = title;

        // Swell product ids appear in the page's hydration payload before any API call
        var pid = Regex.Match(res.Body, @"""product_id""\s*:\s*""([a-f0-9]{20,})""").Groups[1].Value;
        if (string.IsNullOrEmpty(pid))
            pid = Regex.Match(res.Body, @"""id""\s*:\s*""([a-f0-9]{20,})""").Groups[1].Value;
        if (!string.IsNullOrEmpty(pid)) c.Session.Vars["productId"] = pid;

        // the page also carries a price in minor units
        var price = Regex.Match(res.Body, @"""price""\s*:\s*(\d+)");
        if (price.Success && int.TryParse(price.Groups[1].Value, out var cents) && cents > 0)
            c.Session.Vars["price"] = (cents / 100m).ToString("0.00");

        return StepOutcome.Success();
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;

        // Swell models options, not skus: a variant is a set of option choices with its own id
        var m = Regex.Match(body, @"""variant_id""\s*:\s*""([a-f0-9]{20,})""");
        if (!m.Success) m = Regex.Match(body, @"""purchase_option_id""\s*:\s*""([a-f0-9]{20,})""");
        if (!m.Success) m = Regex.Match(body, @"""id""\s*:\s*""([a-f0-9]{20,})""");

        if (!m.Success) return Task.FromResult(StepOutcome.Fail("yeezy: no variant id in the page"));

        c.Session.VariantId = m.Groups[1].Value;
        c.Session.Vars["variant"] = m.Groups[1].Value;

        var sizes = Regex.Matches(body, @"""name""\s*:\s*""(?:US |EU )?(\d{1,2}(?:\.\d)?)""")
            .Select(x => x.Groups[1].Value).Distinct().ToList();

        if (sizes.Count > 0) c.Session.Vars["sizes"] = string.Join(',', sizes);

        return Task.FromResult(StepOutcome.Success());
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c,
        CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;

        var soldOut = body.Contains("\"in_stock\":false", StringComparison.OrdinalIgnoreCase) ||
                      body.Contains("\"stock_status\":\"out_of_stock\"", StringComparison.OrdinalIgnoreCase) ||
                      body.Contains("sold out", StringComparison.OrdinalIgnoreCase);

        c.Session.Vars["available"] = !soldOut && body.Length > 2000 ? "true" : "false";
        return Task.FromResult(StepOutcome.Success());
    }

    /// <summary>
    /// POST the item to Swell's cart. The path follows Swell's documented shape
    /// (/api/cart with an items array); it has not been captured against this store, so if it
    /// 404s the reason says so rather than blaming the network.
    /// </summary>
    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.VariantId) &&
            string.IsNullOrEmpty(c.Session.Vars.GetValueOrDefault("productId")))
            return StepOutcome.Fail("yeezy: no variant or product to add");

        var payload = new JObject
        {
            ["items"] = new JArray
            {
                new JObject
                {
                    ["product_id"] = c.Session.Vars.GetValueOrDefault("productId"),
                    ["variant_id"] = c.Session.VariantId,
                    ["quantity"] = c.Session.Quantity,
                },
            },
        };

        var res = await PostJsonAsync(c, SwellHost + "/api/cart",
            payload.ToString(Newtonsoft.Json.Formatting.None), "yeezy-cart-add", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("yeezy cart add failed", retryable: true);
        if (res.StatusCode == 404)
            return StepOutcome.Fail("yeezy: /api/cart POST not found — Swell path differs from the " +
                                    "documented shape; needs a click-through capture");
        if (!res.IsSuccess) return StepOutcome.Fail($"yeezy cart add HTTP {res.StatusCode}",
            retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
        OpenCheckoutAsync(c, "yeezy-checkout", "/checkout", ct);

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        // Swell's checkout is a hosted flow on the platform host, not a POST we can submit
        var res = await GetAsync(c, SwellHost + "/api/cart", "yeezy-checkout-state", ct)
            .ConfigureAwait(false);

        if (res is null || !res.IsSuccess)
            return StepOutcome.Fail("yeezy: checkout state unreachable", retryable: true);

        var checkoutUrl = TryRead(res.Body, "checkout_url");
        if (string.IsNullOrEmpty(checkoutUrl))
            return StepOutcome.Fail(
                "yeezy: Swell checkout is hosted — the cart carries no checkout_url, so the " +
                "order cannot be submitted from here");

        c.Session.Vars["checkoutUrl"] = checkoutUrl;
        return StepOutcome.Fail($"yeezy: order requires the hosted checkout at {checkoutUrl}");
    }
}

/// <summary>
/// Casio — reCAPTCHA site key is fixed in the binary
/// (<c>6LfeU4ofAAAAAHTDXnfN1V9EroVWvwEPeqrXybdj</c>), so the flow declares it up front
/// and waits for a solved token before carting.
/// </summary>
public sealed class CasioFlow : StoreFlow
{
    public const string RecaptchaSiteKey = "6LfeU4ofAAAAAHTDXnfN1V9EroVWvwEPeqrXybdj";

    public override string Id => "casio";
    public override string Name => "Casio";
    public override IReadOnlyList<string> Domains => new[] { "casio.com" };

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/", "casio-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("casio home unreachable", retryable: true);
        c.Session.Vars["home"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCaptchaAsync(FlowContext c, CancellationToken ct)
    {
        c.Session.Vars["captchaSiteKey"] = RecaptchaSiteKey;
        c.Session.Vars["captchaKind"] = "recaptcha";
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SolveCaptchaAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.AntiBotTokens.TryGetValue("g-recaptcha-response", out var token) &&
            !string.IsNullOrEmpty(token))
            return StepOutcome.Success();

        return StepOutcome.Fail("casio: captcha token not supplied", retryable: true);
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "casio-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("casio product unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"casio product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;
        c.Session.Vars["product"] = Regex.Match(res.Body, @"<title>([^<|]+)").Groups[1].Value;
        c.Session.Vars["price"] = Regex.Match(res.Body, @"(?:USD|€|£|\$)\s?([\d,.]+)").Groups[1].Value;
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        var sku = Regex.Match(body, @"""sku""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (string.IsNullOrEmpty(sku)) return Task.FromResult(StepOutcome.Fail("casio: no sku"));

        c.Session.VariantId = sku;
        return Task.FromResult(StepOutcome.Success());
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;

        // R782: the image decides availability from data.products.items[*].casio_can_purchase, not from the word
        // "availability" appearing anywhere in the page. sub_140954410 walks data -> products -> items through three
        // keyed lookups and then reads casio_can_purchase per item; those four names came out of the string pool and
        // the off_ reader in R781.
        var decided = CasioAvailability(body);
        if (decided is not null)
        {
            c.Session.Vars["available"] = decided.Value ? "true" : "false";
            return Task.FromResult(StepOutcome.Success());
        }

        // Fall back to the earlier heuristic when the payload is not the shape the image walks -- a product page
        // rather than the JSON. Keeping the fallback means this change cannot make an existing case worse.
        var inStock = body.Contains("\"availability\"", StringComparison.OrdinalIgnoreCase) ||
                      body.Contains("InStock", StringComparison.OrdinalIgnoreCase);
        c.Session.Vars["available"] = inStock ? "true" : "false";
        return Task.FromResult(StepOutcome.Success());
    }

    /// <summary>The key the image reads per item to decide whether a Casio product can be bought (R781).</summary>
    public const string CanPurchaseField = "casio_can_purchase";

    /// <summary>
    /// Walk <c>data.products.items</c> and report whether any item says it can be purchased, or null when the payload
    /// is not that shape. Observation: the path and the field name. Inference (medium): that "can purchase" is a
    /// boolean and that any-true means available -- the image reads the field, but its comparison is downstream of
    /// the decompiled window.
    /// </summary>
    public static bool? CasioAvailability(string body)
    {
        if (string.IsNullOrEmpty(body) || body[0] is not ('{' or '[')) return null;

        JToken root;
        try
        {
            root = JToken.Parse(body);
        }
        catch (Newtonsoft.Json.JsonException)
        {
            return null;
        }

        var items = root.SelectTokens("$.data.products.items[*]").ToList();
        if (items.Count == 0) return null;

        var any = false;
        var sawField = false;
        foreach (var item in items)
        {
            var value = item[CanPurchaseField];
            if (value is null) continue;
            sawField = true;
            if (value.Type == JTokenType.Boolean && value.Value<bool>()) any = true;
            else if (value.Type == JTokenType.String &&
                     string.Equals(value.Value<string>(), "true", StringComparison.OrdinalIgnoreCase)) any = true;
        }

        return sawField ? any : null;
    }

    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        var payload = new JObject
        {
            ["sku"] = c.Session.VariantId,
            ["quantity"] = c.Session.Quantity,
            ["recaptcha"] = c.Session.AntiBotTokens.TryGetValue("g-recaptcha-response", out var t) ? t : null,
        };

        var res = await PostJsonAsync(c, Origin(c.Url) + "/cart/add",
            payload.ToString(Newtonsoft.Json.Formatting.None), "casio-cart", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("casio cart failed", retryable: true);
        if (res.StatusCode == 404)
            return StepOutcome.Fail("casio: /cart/add is not there — Casio runs AEM behind Akamai, " +
                                    "and every root-relative cart path returns the SPA 404; the real " +
                                    "path is under the /{region}/ prefix and has not been captured");
        if (!res.IsSuccess) return StepOutcome.Fail($"casio cart HTTP {res.StatusCode}", retryable: true);
        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail(
            "casio: the order path is not /checkout/submit — that route returns 404, and Casio's " +
            "checkout is an AEM flow under /{region}/, not a single JSON POST. Both SubmitShipping " +
            "and SubmitPayment are unimplemented for the same reason: the staged controller paths " +
            "have not been captured"));
    public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
        OpenCheckoutAsync(c, "casio-checkout", "/checkout", ct);


}

/// <summary>
/// Warhammer — Games Workshop storefront with a split identity host
/// (<c>login.mywarhammer.com</c>) and a production API host (<c>api.prod.warhammer.com</c>).
/// Checkout requires a session token minted by the identity host.
///
/// <para>
/// The three REST paths this flow calls — <c>/api/products/{code}</c>, <c>/api/basket/items</c>,
/// <c>/api/orders</c> — have no evidence behind them. Round 59 saw 403 + a 42-byte JSON body and
/// read that as "the route exists, it just refuses us". Round 90 disproved that reasoning:
/// <c>api.prod.warhammer.com</c> returns the same 403 for <c>/api/i18n</c>, a path that answers
/// 200 with 13 KB of JSON on the site host. So that 403 is the WAF refusing uniformly and says
/// nothing about which paths exist.
///
/// A capture of the storefront shows the real API is GraphQL
/// (<c>POST api.prod.warhammer.com/graphql</c>), with an AEM-style content API on
/// <c>www.warhammer.com/api/</c> that only serves things like i18n. So the REST shape here is
/// probably wrong — but "probably wrong with no evidence" is not enough to rewrite it either.
/// </para>
/// </summary>
public sealed class WarhammerFlow : StoreFlow
{
    public override string Id => "warhammer";
    public override string Name => "Warhammer";
    public override IReadOnlyList<string> Domains =>
        new[] { "warhammer.com", "games-workshop.com", "login.mywarhammer.com" };

    private const string IdentityHost = "https://login.mywarhammer.com";
    private const string ApiHost = "https://api.prod.warhammer.com";

    public override bool RequiresAccount => true;

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/", "wh-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("warhammer home unreachable", retryable: true);
        c.Session.Vars["home"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> LoginAsync(FlowContext c, CancellationToken ct)
    {
        var account = c.Account;
        if (account?.Email is null) return StepOutcome.Fail("warhammer: no account");

        var payload = new JObject
        {
            ["email"] = account.Email,
            ["password"] = account.Password,
        };

        var res = await PostJsonAsync(c, $"{IdentityHost}/api/login",
            payload.ToString(Newtonsoft.Json.Formatting.None), "wh-login", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("warhammer login failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"warhammer login HTTP {res.StatusCode}");

        var root = JObject.Parse(res.Body);
        c.Session.Vars["accessToken"] = root["access_token"]?.ToString() ?? string.Empty;
        if (c.Session.Vars.TryGetValue("accessToken", out var at) && !string.IsNullOrEmpty(at))
            c.Session.AntiBotTokens["Authorization"] = "Bearer " + at;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> VerifySessionAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, $"{IdentityHost}/api/me", "wh-me", ct).ConfigureAwait(false);
        return res is { IsSuccess: true } ? StepOutcome.Success() : StepOutcome.Fail("warhammer: session invalid");
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var code = Regex.Match(c.Url, @"([0-9]{6,}-[0-9]{6,})").Groups[1].Value;
        var url = string.IsNullOrEmpty(code) ? c.Url : $"{ApiHost}/api/products/{code}";

        var res = await GetAsync(c, url, "wh-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("warhammer product unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"warhammer product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;
        c.Session.Vars["product"] = Regex.Match(res.Body, @"""name""\s*:\s*""([^""]+)""").Groups[1].Value;
        c.Session.Vars["price"] = Regex.Match(res.Body, @"""price""\s*:\s*([\d.]+)").Groups[1].Value;
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        if (string.IsNullOrWhiteSpace(body)) return Task.FromResult(StepOutcome.Fail("warhammer: no product"));

        var sku = Regex.Match(body, @"""sku""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (string.IsNullOrEmpty(sku)) return Task.FromResult(StepOutcome.Fail("warhammer: no sku"));

        c.Session.VariantId = sku;
        return Task.FromResult(StepOutcome.Success());
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        var available = body.Contains("\"inStock\":true", StringComparison.OrdinalIgnoreCase);
        c.Session.Vars["available"] = available ? "true" : "false";
        return Task.FromResult(StepOutcome.Success());
    }

    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        var payload = new JObject
        {
            ["sku"] = c.Session.VariantId,
            ["quantity"] = c.Session.Quantity,
        };

        var res = await PostJsonAsync(c, $"{ApiHost}/api/basket/items",
            payload.ToString(Newtonsoft.Json.Formatting.None), "wh-cart", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("warhammer cart failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"warhammer cart HTTP {res.StatusCode}", retryable: true);
        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        var res = await PostJsonAsync(c, $"{ApiHost}/api/orders", "{}", "wh-order", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("warhammer order failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"warhammer order HTTP {res.StatusCode}", retryable: true);

        c.Session.OrderNumber = Regex.Match(res.Body, @"""orderNumber""\s*:\s*""([^""]+)""").Groups[1].Value;
        return StepOutcome.Success();
    }
    public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
        OpenCheckoutAsync(c, "wh-checkout", "/checkout", ct);


}

/// <summary>
/// JB Hi-Fi — Australian retailer with its own identity host
/// (<c>auth.jbhifi.com.au</c>). Login mints a bearer that the cart API requires.
/// </summary>
/// <summary>
/// JB Hi-Fi — Shopify storefront with a separate account system.
///
/// This used to be a hand-written StoreFlow posting to <c>/api/cart/add</c> and
/// <c>/api/checkout/submit</c>, with its own OAuth at <c>auth.jbhifi.com.au/oauth/token</c>.
/// Half of that was wrong: the storefront is Shopify, proven by
///
///   GET /cart.js                    -> 200, 303 B, a Shopify cart object
///   /.well-known/shopify/monorail/  -> called by the page on load
///
/// The account system genuinely is separate — a large retailer running Shopify Plus behind
/// bespoke auth looks exactly like this. So the flow is a ShopifyFlow that keeps the OAuth
/// step, rather than reimplementing cart and checkout against endpoints that do not exist.
/// </summary>
public sealed class JbHiFiFlow : ShopifyFlow
{
    private const string AuthHost = "https://auth.jbhifi.com.au";

    public JbHiFiFlow() : base("jbhifi", "JB Hi-Fi", new[] { "jbhifi.com.au" })
    {
    }

    public override bool RequiresAccount => true;

    public override async Task<StepOutcome> LoginAsync(FlowContext c, CancellationToken ct)
    {
        var account = c.Account;
        if (account?.Email is null) return StepOutcome.Fail("jbhifi: no account");

        var payload = new JObject
        {
            ["username"] = account.Email,
            ["password"] = account.Password,
            ["grant_type"] = "password",
        };

        var res = await PostJsonAsync(c, $"{AuthHost}/oauth/token",
            payload.ToString(Newtonsoft.Json.Formatting.None), "jbhifi-login", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("jbhifi login failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"jbhifi login HTTP {res.StatusCode}");

        var token = JObject.Parse(res.Body)["access_token"]?.ToString();
        if (string.IsNullOrEmpty(token)) return StepOutcome.Fail("jbhifi: no access token");

        c.Session.AntiBotTokens["Authorization"] = "Bearer " + token;
        return StepOutcome.Success();
    }
}

/// <summary>
/// Superswipe — a raffle app that runs inside Shopify stores, not a store itself.
///
/// The binary carries a whole private integration for it: captcha host, status host, entry
/// host, country-data bundle and a launch-id attribute. The flow reproduces that sequence.
///
/// Verified from the live site: its own page titles itself
/// "SuperSwipe | Shopify Raffle App &amp; Fair Release Platform", and the API surface the
/// capture showed is app-side only —
///
///   GET  https://relay.superswipe.com/region
///   POST https://relay.superswipe.com/e/
///   POST https://superswipe.com/cdn-cgi/challenge-platform/...   (Cloudflare)
///
/// <para>
/// A note on <see cref="Domains"/>: the raffle itself happens on the *customer's* Shopify
/// domain, which this module cannot know. The entries below are the app's own hosts, kept so
/// the catalogue can resolve the module at all (CatalogValidatorTests requires at least one
/// domain). They are a placeholder, not a product domain — a task URL pointing at
/// superswipe.com is the vendor site, not a raffle.
/// </para>
/// </summary>
public sealed class SuperswipeFlow : StoreFlow
{
    public override string Id => "superswipe";
    public override string Name => "Superswipe";

    /// <summary>App hosts only — the raffle runs on the customer's store domain.</summary>
    public override IReadOnlyList<string> Domains =>
        new[] { "superswipe.com", "superswipe.app", "enter.superswipe.com" };

    private const string CaptchaOrigin = "https://captcha.superswipe.com";
    private const string StatusApi = "https://status.superswipe.com";
    private const string EntryUrl = "https://enter.superswipe.com/enter";
    private const string CountryDataUrl = "https://cdn.superswipe.com/superswipe-country-data.js";
    private const string LaunchAttributeKey = "_superswipe_launch_id_";

    public override async Task<StepOutcome> LoadCountryDataAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, CountryDataUrl, "ss-country-data", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("superswipe country data unreachable", retryable: true);

        c.Session.Vars["countryData"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, EntryUrl, "ss-entry", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("superswipe entry unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"superswipe entry HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["entry"] = res.Body;
        var launch = Regex.Match(res.Body, @"" + Regex.Escape(LaunchAttributeKey) + @"""\s*:\s*""([^""]+)""")
            .Groups[1].Value;
        if (!string.IsNullOrEmpty(launch)) c.Session.Vars["launchId"] = launch;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCaptchaAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, $"{CaptchaOrigin}/v1/challenge", "ss-captcha", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("superswipe captcha unreachable", retryable: true);

        c.Session.Vars["captcha"] = res.Body;
        c.Session.Vars["captchaSiteKey"] = Regex.Match(res.Body, @"""siteKey""\s*:\s*""([^""]+)""").Groups[1].Value;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SolveCaptchaAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.AntiBotTokens.TryGetValue("superswipe-captcha", out var token) &&
            !string.IsNullOrEmpty(token))
            return StepOutcome.Success();
        return StepOutcome.Fail("superswipe: captcha not solved", retryable: true);
    }

    public override async Task<StepOutcome> PollQueueAsync(FlowContext c, CancellationToken ct)
    {
        for (var i = 0; i < 12; i++)
        {
            ct.ThrowIfCancellationRequested();
            var res = await GetAsync(c, $"{StatusApi}/api/status", "ss-status", ct).ConfigureAwait(false);
            if (res is null) return StepOutcome.Fail("superswipe status unreachable", retryable: true);

            if (res.Body.Contains("\"open\":true", StringComparison.OrdinalIgnoreCase))
            {
                c.Session.Vars["queue"] = "open";
                return StepOutcome.Success();
            }
            await Task.Delay(TimeSpan.FromMilliseconds(400), ct).ConfigureAwait(false);
        }
        return StepOutcome.Fail("superswipe: drop not open", retryable: true);
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "ss-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("superswipe product unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"superswipe product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;
        c.Session.Vars["product"] = Regex.Match(res.Body, @"""title""\s*:\s*""([^""]+)""").Groups[1].Value;
        c.Session.Vars["price"] = Regex.Match(res.Body, @"""price""\s*:\s*([\d.]+)").Groups[1].Value;
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        var id = Regex.Match(body, @"""variantId""\s*:\s*""?([A-Za-z0-9\-]+)""?").Groups[1].Value;
        if (string.IsNullOrEmpty(id)) id = Regex.Match(body, @"""id""\s*:\s*""?([A-Za-z0-9\-]{4,})""?").Groups[1].Value;
        if (string.IsNullOrEmpty(id)) return Task.FromResult(StepOutcome.Fail("superswipe: no variant"));

        c.Session.VariantId = id;
        return Task.FromResult(StepOutcome.Success());
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        c.Session.Vars["available"] = body.Contains("\"available\":true", StringComparison.OrdinalIgnoreCase)
            ? "true" : "false";
        return Task.FromResult(StepOutcome.Success());
    }

    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        var payload = new JObject
        {
            ["variantId"] = c.Session.VariantId,
            ["quantity"] = c.Session.Quantity,
            ["captchaToken"] = c.Session.AntiBotTokens.TryGetValue("superswipe-captcha", out var t) ? t : null,
        };

        var res = await PostJsonAsync(c, Origin(c.Url) + "/api/cart",
            payload.ToString(Newtonsoft.Json.Formatting.None), "ss-cart", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("superswipe cart failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"superswipe cart HTTP {res.StatusCode}", retryable: true);
        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        var res = await PostJsonAsync(c, Origin(c.Url) + "/api/checkout", "{}", "ss-order", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("superswipe order failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"superswipe order HTTP {res.StatusCode}", retryable: true);

        c.Session.OrderNumber = Regex.Match(res.Body, @"""order(?:Number|Id)""\s*:\s*""?([A-Za-z0-9\-]+)""?")
            .Groups[1].Value;
        return StepOutcome.Success();
    }
    public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
        OpenCheckoutAsync(c, "superswipe-checkout", "/checkout", ct);

}

/// <summary>
/// PocketGames — drop-schedule driven raffle/queue store
/// (<c>api.pocketgames.nl/v1/public/drop-schedule</c>).
/// </summary>
public sealed class PocketGamesFlow : StoreFlow
{
    public override string Id => "pocketgames";
    public override string Name => "PocketGames";
    public override IReadOnlyList<string> Domains => new[] { "pocketgames.nl", "api.pocketgames.nl" };

    private const string DropSchedule = "https://api.pocketgames.nl/v1/public/drop-schedule";

    public override async Task<StepOutcome> GetReleaseFeedAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, DropSchedule, "pg-schedule", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("pocketgames schedule unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"pocketgames schedule HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["schedule"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> WaitForReleaseAsync(FlowContext c, CancellationToken ct)
    {
        var schedule = c.Session.Vars.TryGetValue("schedule", out var s) ? s : string.Empty;
        var m = Regex.Match(schedule, @"""drop(?:At|Time)""\s*:\s*""([^""]+)""");
        if (!m.Success) return StepOutcome.Success();

        if (DateTimeOffset.TryParse(m.Groups[1].Value, out var when))
        {
            var wait = when - DateTimeOffset.UtcNow;
            if (wait > TimeSpan.Zero && wait < TimeSpan.FromMinutes(20))
                await Task.Delay(wait, ct).ConfigureAwait(false);
        }
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/", "pg-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("pocketgames home unreachable", retryable: true);
        c.Session.Vars["home"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "pg-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("pocketgames product unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"pocketgames product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;
        c.Session.Vars["product"] = Regex.Match(res.Body, @"""name""\s*:\s*""([^""]+)""").Groups[1].Value;
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        var id = Regex.Match(body, @"""variant""\s*:\s*""?([A-Za-z0-9\-]+)""?").Groups[1].Value;
        if (string.IsNullOrEmpty(id)) return Task.FromResult(StepOutcome.Fail("pocketgames: no variant"));

        c.Session.VariantId = id;
        return Task.FromResult(StepOutcome.Success());
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        c.Session.Vars["available"] = body.Contains("\"available\":true", StringComparison.OrdinalIgnoreCase)
            ? "true" : "false";
        return Task.FromResult(StepOutcome.Success());
    }

    public override async Task<StepOutcome> EnterRaffleAsync(FlowContext c, CancellationToken ct)
    {
        var payload = new JObject
        {
            ["variant"] = c.Session.VariantId,
            ["email"] = c.ProfileData?.Email ?? c.Account?.Email,
            ["name"] = c.ProfileData?.Display,
        };

        var res = await PostJsonAsync(c, "https://api.pocketgames.nl/v1/public/raffle-entry",
            payload.ToString(Newtonsoft.Json.Formatting.None), "pg-raffle", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("pocketgames raffle failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"pocketgames raffle HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raffle"] = res.Body;
        return StepOutcome.Success();
    }
}

/// <summary>
/// HypeCommerce — the binary carries <c>admin.hypecommerce.io</c> plus an IdP host
/// (<c>login.wingstop.com</c>), i.e. tenant-specific SSO then a hype cart API.
/// </summary>
public sealed class HypeCommerceFlow : StoreFlow
{
    public override string Id => "hypecommerce";
    public override string Name => "HypeCommerce";
    public override IReadOnlyList<string> Domains => new[] { "hypecommerce.io", "hypecommerce.com" };

    private const string HypeApi = "https://admin.hypecommerce.io";

    public override bool RequiresAccount => true;

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/", "hype-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("hype home unreachable", retryable: true);
        c.Session.Vars["home"] = res.Body;

        var idp = Regex.Match(res.Body, @"""idpHost""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (!string.IsNullOrEmpty(idp)) c.Session.Vars["idpHost"] = idp;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> LoginAsync(FlowContext c, CancellationToken ct)
    {
        var account = c.Account;
        if (account?.Email is null) return StepOutcome.Fail("hype: no account");

        var idp = c.Session.Vars.TryGetValue("idpHost", out var h) && !string.IsNullOrEmpty(h)
            ? "https://" + h
            : "https://admin.hypecommerce.io";

        var res = await PostJsonAsync(c, $"{idp}/api/auth/login",
            Newtonsoft.Json.JsonConvert.SerializeObject(new
            {
                email = account.Email,
                password = account.Password,
            }), "hype-login", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("hype login failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"hype login HTTP {res.StatusCode}");

        var token = Regex.Match(res.Body, @"""token""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (!string.IsNullOrEmpty(token)) c.Session.AntiBotTokens["Authorization"] = "Bearer " + token;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var slug = new Uri(c.Url).AbsolutePath.Trim('/').Split('/').LastOrDefault() ?? string.Empty;
        var res = await GetAsync(c, $"{HypeApi}/api/entries/{slug}", "hype-product", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("hype product unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"hype product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;
        c.Session.Vars["product"] = Regex.Match(res.Body, @"""name""\s*:\s*""([^""]+)""").Groups[1].Value;
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        var id = Regex.Match(body, @"""entryId""\s*:\s*""?([A-Za-z0-9\-]+)""?").Groups[1].Value;
        if (string.IsNullOrEmpty(id)) id = Regex.Match(body, @"""id""\s*:\s*""?([A-Za-z0-9\-]{4,})""?").Groups[1].Value;
        if (string.IsNullOrEmpty(id)) return Task.FromResult(StepOutcome.Fail("hype: no entry id"));

        c.Session.VariantId = id;
        return Task.FromResult(StepOutcome.Success());
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        c.Session.Vars["available"] = body.Contains("\"status\":\"available\"", StringComparison.OrdinalIgnoreCase)
            ? "true" : "false";
        return Task.FromResult(StepOutcome.Success());
    }

    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        var res = await PostJsonAsync(c, $"{HypeApi}/api/cart",
            Newtonsoft.Json.JsonConvert.SerializeObject(new
            {
                entryId = c.Session.VariantId,
                quantity = c.Session.Quantity,
            }), "hype-cart", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("hype cart failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"hype cart HTTP {res.StatusCode}", retryable: true);
        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        var res = await PostJsonAsync(c, $"{HypeApi}/api/cart/checkout", "{}", "hype-order", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("hype order failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"hype order HTTP {res.StatusCode}", retryable: true);

        c.Session.OrderNumber = Regex.Match(res.Body, @"""orderId""\s*:\s*""?([A-Za-z0-9\-]+)""?").Groups[1].Value;
        return StepOutcome.Success();
    }
    public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
        OpenCheckoutAsync(c, "hype-checkout", "/checkout", ct);


}

/// <summary>
/// Fanatics — identity host <c>id.fanatics.com</c> issues the session that the storefront
/// cart honours. Flow: identity → home → product → cart → order.
/// </summary>
public sealed class FanaticsFlow : StoreFlow
{
    public override string Id => "fanatics";
    public override string Name => "Fanatics";
    public override IReadOnlyList<string> Domains => new[] { "fanatics.com", "id.fanatics.com" };

    private const string IdentityHost = "https://id.fanatics.com";

    public override bool RequiresAccount => true;

    public override async Task<StepOutcome> LoginAsync(FlowContext c, CancellationToken ct)
    {
        var account = c.Account;
        if (account?.Email is null) return StepOutcome.Fail("fanatics: no account");

        var res = await PostJsonAsync(c, $"{IdentityHost}/api/v1/login",
            Newtonsoft.Json.JsonConvert.SerializeObject(new
            {
                email = account.Email,
                password = account.Password,
            }), "fanatics-login", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("fanatics login failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"fanatics login HTTP {res.StatusCode}");

        var token = Regex.Match(res.Body, @"""accessToken""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (!string.IsNullOrEmpty(token)) c.Session.AntiBotTokens["Authorization"] = "Bearer " + token;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/", "fanatics-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("fanatics home unreachable", retryable: true);
        if (res.StatusCode == 403)
            return StepOutcome.Fail("fanatics: home refused by Akamai Bot Manager (403) — the " +
                                    "storefront serves no HTML at all without a passed sensor", retryable: true);
        c.Session.Vars["home"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "fanatics-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("fanatics product unreachable", retryable: true);
        if (res.StatusCode == 403)
            return StepOutcome.Fail("fanatics: product refused by Akamai Bot Manager (403) — " +
                                    "not a retryable network error", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"fanatics product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;
        c.Session.Vars["product"] = Regex.Match(res.Body, @"""name""\s*:\s*""([^""]+)""").Groups[1].Value;
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        var sku = Regex.Match(body, @"""sku""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (string.IsNullOrEmpty(sku)) return Task.FromResult(StepOutcome.Fail("fanatics: no sku"));

        c.Session.VariantId = sku;
        return Task.FromResult(StepOutcome.Success());
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        c.Session.Vars["available"] = body.Contains("\"inStock\":true", StringComparison.OrdinalIgnoreCase)
            ? "true" : "false";
        return Task.FromResult(StepOutcome.Success());
    }

    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        var res = await PostJsonAsync(c, Origin(c.Url) + "/api/cart/add",
            Newtonsoft.Json.JsonConvert.SerializeObject(new
            {
                sku = c.Session.VariantId,
                quantity = c.Session.Quantity,
            }), "fanatics-cart", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("fanatics cart failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"fanatics cart HTTP {res.StatusCode}", retryable: true);
        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        var res = await PostJsonAsync(c, Origin(c.Url) + "/api/checkout/submit", "{}", "fanatics-order", ct)  // inferred: no image evidence (R294)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("fanatics order failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"fanatics order HTTP {res.StatusCode}", retryable: true);

        c.Session.OrderNumber = Regex.Match(res.Body, @"""orderNumber""\s*:\s*""([^""]+)""").Groups[1].Value;
        return StepOutcome.Success();
    }
    public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
        OpenCheckoutAsync(c, "fanatics-checkout", "/checkout", ct);


}

/// <summary>
/// Riot Games — the binary signs up via <c>authenticate.riotgames.com</c>; the flow is a
/// registration/raffle path rather than a cart path, so the account steps carry the weight.
/// </summary>
public sealed class RiotGamesFlow : StoreFlow
{
    public override string Id => "riotgames";
    public override string Name => "Riot Games";
    public override IReadOnlyList<string> Domains => new[] { "riotgames.com", "playriftbound.com" };

    private const string AuthHost = "https://authenticate.riotgames.com";

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "riot-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("riot home unreachable", retryable: true);
        c.Session.Vars["home"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// Riot's storefront is raffle-only, but a monitor still has to report the product, its
    /// price and whether the raffle is open — otherwise the task shows "unknown" forever.
    /// </summary>
    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var jsonUrl = c.Url.Contains('?', StringComparison.Ordinal)
            ? c.Url + "&format=json"
            : c.Url + ".json";

        var res = await GetAsync(c, jsonUrl, "riot-product", ct).ConfigureAwait(false);
        if (res is null || !res.IsSuccess)
            res = await GetAsync(c, c.Url, "riot-product-html", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("riot product unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"riot product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;

        var name = Regex.Match(res.Body, @"""(?:productName|name|title)""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (!string.IsNullOrEmpty(name)) c.Session.Vars["product"] = name;

        var price = Regex.Match(res.Body, @"""(?:price|listPrice)""\s*:\s*""?([\d.,]+)""?").Groups[1].Value;
        if (!string.IsNullOrEmpty(price)) c.Session.Vars["price"] = price;

        // raffle state decides whether EnterRaffle is even worth attempting
        var open = Regex.IsMatch(res.Body, @"""(?:raffleOpen|isOpen|inStock)""\s*:\s*true", RegexOptions.IgnoreCase);
        c.Session.Vars["available"] = open ? "true" : "false";

        return string.IsNullOrEmpty(name)
            ? StepOutcome.Fail("riot: product page carried no product name", retryable: true)
            : StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        await Task.CompletedTask.ConfigureAwait(false);

        var body = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : string.Empty;
        if (string.IsNullOrWhiteSpace(body))
        {
            var fetched = await FindProductAsync(c, ct).ConfigureAwait(false);
            if (!fetched.Ok) return fetched;
            body = c.Session.Vars["raw"];
        }

        var id = Regex.Match(body,
            @"""(?:sku|skuId|variantId|productId)""\s*:\s*""?([A-Za-z0-9_\-]+)""?").Groups[1].Value;

        if (string.IsNullOrEmpty(id))
            return StepOutcome.Fail("riot: no variant id in payload", retryable: true);

        c.Session.VariantId = id;
        c.Session.Vars["variant"] = id;

        var size = Regex.Match(body, @"""(?:size|sizeName|title)""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (!string.IsNullOrEmpty(size))
        {
            c.Session.Vars["size"] = size;
            c.Session.Vars["sizes"] = size;
        }

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> RegisterAsync(FlowContext c, CancellationToken ct)
    {
        var account = c.Account;
        if (account?.Email is null) return StepOutcome.Fail("riot: no account");

        var res = await PostJsonAsync(c, $"{AuthHost}/api/v1/register",
            Newtonsoft.Json.JsonConvert.SerializeObject(new
            {
                email = account.Email,
                password = account.Password,
                campaign = "playriftbound",
            }), "riot-register", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("riot register failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"riot register HTTP {res.StatusCode}");

        c.Session.Vars["registered"] = "1";
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> CompleteRegistrationAsync(FlowContext c, CancellationToken ct)
    {
        var res = await PostJsonAsync(c, $"{AuthHost}/api/v1/register/complete",
            "{}", "riot-register-complete", ct).ConfigureAwait(false);
        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail($"riot complete HTTP {res?.StatusCode}");
    }

    public override async Task<StepOutcome> LoginAsync(FlowContext c, CancellationToken ct)
    {
        var account = c.Account;
        if (account?.Email is null) return StepOutcome.Fail("riot: no account");

        var res = await PostJsonAsync(c, $"{AuthHost}/api/v1/login",
            Newtonsoft.Json.JsonConvert.SerializeObject(new
            {
                username = account.Email,
                password = account.Password,
            }), "riot-login", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("riot login failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"riot login HTTP {res.StatusCode}");

        var token = Regex.Match(res.Body, @"""access_token""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (!string.IsNullOrEmpty(token)) c.Session.AntiBotTokens["Authorization"] = "Bearer " + token;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> EnterRaffleAsync(FlowContext c, CancellationToken ct)
    {
        var res = await PostJsonAsync(c, Origin(c.Url) + "/api/preorder/entry",  // inferred: no image evidence (R294)
            Newtonsoft.Json.JsonConvert.SerializeObject(new
            {
                email = c.ProfileData?.Email ?? c.Account?.Email,
            }), "riot-entry", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("riot entry failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"riot entry HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["entry"] = res.Body;
        return StepOutcome.Success();
    }
}

/// <summary>
/// Raffle landing pages (r419.com and the lndg.page family) — the binary carries
/// <c>RaffleUrl</c> + <c>_turnstileSiteKey</c> for them.
/// </summary>
public sealed class RaffleFlow : StoreFlow
{
    public override string Id => "raffle";
    public override string Name => "Raffle";
    public override IReadOnlyList<string> Domains =>
        new[] { "r419.com", "lndg.page", "nodnod.digital" };

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "raffle-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("raffle page unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"raffle HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["home"] = res.Body;
        var key = Regex.Match(res.Body, @"data-sitekey=""([^""]+)""").Groups[1].Value;
        if (string.IsNullOrEmpty(key))
            key = Regex.Match(res.Body, @"""turnstileSiteKey""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (!string.IsNullOrEmpty(key)) c.Session.Vars["captchaSiteKey"] = key;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> ScrapeRaffleFormAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("home", out var h) ? h : string.Empty;
        var fields = Regex.Matches(body, @"<(?:input|select)[^>]+name=""([^""]+)""")
            .Select(m => m.Groups[1].Value).Distinct().ToList();

        c.Session.Vars["formFields"] = string.Join('|', fields);
        c.Session.Vars["open"] = body.Contains("Enter", StringComparison.OrdinalIgnoreCase) ? "true" : "false";
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetRaffleDataAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/api/raffle", "raffle-data", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("raffle data unreachable", retryable: true);

        c.Session.Vars["raffle"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c, CancellationToken ct)
    {
        c.Session.Vars["available"] = c.Session.Vars.TryGetValue("open", out var o) && o == "true"
            ? "true" : "false";
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SolveCaptchaAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.AntiBotTokens.TryGetValue("cf-turnstile-response", out var t) &&
            !string.IsNullOrEmpty(t))
            return StepOutcome.Success();
        return StepOutcome.Fail("raffle: turnstile not solved", retryable: true);
    }

    public override async Task<StepOutcome> EnterRaffleAsync(FlowContext c, CancellationToken ct)
    {
        var form = new Dictionary<string, string>
        {
            ["email"] = c.ProfileData?.Email ?? c.Account?.Email ?? string.Empty,
            ["name"] = c.ProfileData?.Display ?? string.Empty,
            ["cf-turnstile-response"] = c.Session.AntiBotTokens.TryGetValue("cf-turnstile-response", out var t)
                ? t
                : string.Empty,
        };

        var res = await PostFormAsync(c, Origin(c.Url) + "/enter", form, "raffle-enter", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("raffle entry failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"raffle entry HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["entry"] = res.Body;
        return StepOutcome.Success();
    }
}
