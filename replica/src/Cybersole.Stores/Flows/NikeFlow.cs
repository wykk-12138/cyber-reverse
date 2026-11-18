using System.Text.RegularExpressions;
using Cybersole.Http;
using Cybersole.Stores.Scripts;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Nike SNKRS flow.
///
/// Nike fronts its whole surface with Kasada, so every request has to carry a locally
/// generated <c>x-kpsdk-ct</c>. The binary does this the same way: fetch the store's own
/// <c>ips.js</c>, run it in Jint, read the token the script produced. Nothing is proxied
/// through a solver service.
/// </summary>
public class NikeFlow : StoreFlow
{
    public override string Id => "nike";

    /// <summary>
    /// Nike's own order — the image's sixteen steps, recovered from one adjacent run of compiler ordinals (R112).
    ///
    /// <para>
    /// R869. Nine of these sixteen have no same-named method on this flow, and R843 established why: the image
    /// separates ValidateAddress, CheckInventory, GetShopperIp and GetPaymentMethods into stages that can fail
    /// independently, while the replica collapses them into SubmitShipping and SubmitPayment. Declaring the sequence is
    /// what makes that visible as a number rather than as a remark.
    /// </para>
    /// </summary>
    public override IReadOnlyList<string> StepSequence => StoreFlowSteps.Nike.Names;

    public override string Name => "Nike";
    public override IReadOnlyList<string> Domains => new[] { "nike.com", "snkrs.nike.com" };
    public override bool UsesKasada => true;

    /// <summary>
    /// The marketplaces the binary supports: <b>forty-two</b>.
    ///
    /// <para>
    /// R89 read them out of the image with <c>find_regex "Nike [A-Z]{2}$"</c> — one string per
    /// market, alphabetically ordered, 0x28 bytes apart. The earlier note in NIKE_PARITY said
    /// twenty-two; that was a window of this table, not the table. Twenty markets were missing and
    /// one of them was GB.
    /// </para>
    /// </summary>
    public static readonly IReadOnlyList<string> Countries = new[]
    {
        "AT", "AU", "BE", "BG", "CA", "CH", "CZ", "DE", "DK", "ES", "FI",
        "FR", "GB", "GR", "GS", "HR", "HU", "IE", "IL", "IN", "IT", "JP",
        "LU", "MX", "MY", "NL", "NO", "NZ", "PH", "PL", "PT", "RO", "SE",
        "SG", "SI", "SK", "TH", "TR", "TW", "US", "VN", "ZA",
    };

    /// <summary>
    /// The country for this flow instance.
    ///
    /// <para>
    /// R86: this was <c>const string Marketplace = "US"</c> — one hardcoded market in a build that
    /// ships forty-two, while the binary carries the choice in an <b>instance</b> field
    /// (<c>_countryCode</c>). A constant cannot be per-task, so the flow could only ever check out in
    /// the United States no matter what the profile said.
    /// </para>
    /// </summary>
    public string CountryCode { get; set; } = "US";

    /// <summary>
    /// Maps a profile's ISO country onto a supported marketplace: an exact match if the binary
    /// supports it, otherwise US. Accepts a lowercase code, and treats "UK" as GB — the binary does
    /// have a GB market, so the alias resolves to something real rather than falling back.
    /// </summary>
    public static string CountryFor(string? profileCountry)
    {
        if (string.IsNullOrWhiteSpace(profileCountry)) return "US";

        var code = profileCountry.Trim().ToUpperInvariant();
        if (code == "UK") code = "GB";

        return Countries.Contains(code) ? code : "US";
    }

    private const string Language = "en";
    private const string ChannelId = "d9a5bc42-4b9c-4976-858a-f159cf99c647";

    // 鈹€鈹€ session 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, "https://www.nike.com/", "nike-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("nike home unreachable", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("nike home blocked (kasada)", retryable: true);

        c.Session.Vars["home"] = res.Body;
        var script = KasadaSolver.FindScriptUrl(res.Body, "https://www.nike.com/");
        if (script is not null) c.Session.Vars["kasada.url"] = script;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetSessionAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Cookies.TryGetValue("NIKE_COMMERCE_COUNTRY", out var country))  // inferred: no image evidence (R297)
            c.Session.Vars["country"] = country;

        // R88: the image carries four Nike request headers (nike-api-caller-id, x-nike-ux-id,
        // x-nike-visitid, x-nike-visitorid) plus the Kasada version, and the replica sent none of
        // them. The rest come from what the site hands back — the flow records them as session vars —
        // so a header is only sent when it is actually known. See NikeHeaders.
        //
        // R202: the caller id is the ONE value the image states outright, and it was never seeded, so
        // `nike-api-caller-id` had not been sent once since R88 wrote the table. It is seeded here as the web
        // checkout client; the iOS composed value in the image (`nike:com.nike.commerce.omega.ios:ios:26.8`)
        // would be a claim to be an app this session is not.
        if (!c.Session.Vars.ContainsKey("nike.apiCallerId"))
            c.Session.Vars["nike.apiCallerId"] = NikeHeaders.WebCallerId;

        NikeHeaders.Apply(c.Session.Vars, c.Session.Headers);

        return StepOutcome.Success();
    }

    // 鈹€鈹€ kasada 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
    public override async Task<StepOutcome> GetScriptAsync(FlowContext c, CancellationToken ct)
    {
        using var solver = new KasadaSolver(new BrowserShim
        {
            Href = c.Session.Vars.TryGetValue("kasada.url", out var u) ? u : "https://www.nike.com/",
            Cookie = c.Session.CookieHeader(),
        });

        var (script, url) = await solver.FetchScriptAsync(
            c.Http, c.Url, c.Options("nike-kasada-script"), ct).ConfigureAwait(false);

        if (script is null) return StepOutcome.Fail("nike: ips.js not found", retryable: true);

        c.Session.Vars["kasada.script"] = script;
        c.Session.Vars["kasada.scriptUrl"] = url ?? string.Empty;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GenerateSensorAsync(FlowContext c, CancellationToken ct)
    {
        // 1. A real browser is the only thing that finishes this payload (R17/R20). Use it
        //    whenever one is installed; the token it mints is the genuine article.
        if (ChromiumKasadaSolver.IsAvailable)
        {
            var browser = new ChromiumKasadaSolver();
            var live = await browser.SolveAsync(c.Url, TimeSpan.FromSeconds(45), null, ct)
                .ConfigureAwait(false);

            if (live.Ok)
            {
                AbsorbKasada(c, live);
                c.Session.Vars["kasada.source"] = "chromium";
                return StepOutcome.Success();
            }

            c.Session.Vars["kasada.browserError"] = live.Error ?? "unknown";
        }

        // 2. Fall back to the script engine. This used to be a dead end on current builds -- KPSDK exposes
        //    only configure/isReady, so probing for ct() found nothing. It is not a dead end any more: with a
        //    resourceAddress the sensor issues its own interrogation (GET /mfc then POST /r), and the token
        //    is read off that response. The requests go out through our own HTTP stack so the TLS/HTTP-2
        //    fingerprint matches the rest of the flow.
        if (!c.Session.Vars.TryGetValue("kasada.script", out var script) || string.IsNullOrEmpty(script))
            return StepOutcome.Fail("nike: no kasada script loaded");

        var scriptUrl = c.Session.Vars.TryGetValue("kasada.scriptUrl", out var u) ? u : c.Url;
        var origin = KasadaSolver.OriginOf(scriptUrl) ?? KasadaSolver.OriginOf(c.Url) ?? "https://www.nike.com/";

        // Bounded on purpose: this sits on the checkout path, so a slow interrogation endpoint must not
        // hold the flow. The browser alternative above stays available when this gives up.
        var interrogationOptions = c.Options("nike-kasada-interrogation");
        interrogationOptions.Timeout = TimeSpan.FromSeconds(15);
        interrogationOptions.Retries = 0;

        using var solver = new KasadaSolver(new BrowserShim
        {
            Href = scriptUrl,
            Cookie = c.Session.CookieHeader(),
        })
        {
            ResourceAddress = origin,
            Store = "nike",
            Transport = KasadaSolver.NetTransport(c.Http, interrogationOptions),
        };

        // The transport completes asynchronously under a synchronous JavaScript call, so run the whole
        // solve off this thread rather than blocking it on a sync-over-async wait.
        var result = await Task.Run(() => solver.Solve(script), ct).ConfigureAwait(false);
        if (!result.Ok)
        {
            var browserWhy = c.Session.Vars.TryGetValue("kasada.browserError", out var be) ? be : null;
            return StepOutcome.Fail(
                result.Error + (browserWhy is null ? string.Empty : $" (browser: {browserWhy})"),
                retryable: true);
        }

        AbsorbKasada(c, result);
        c.Session.Vars["kasada.source"] = "script";
        return StepOutcome.Success();
    }

    /// <summary>
    /// Push a Kasada result into the session. The UA travels with the token: a request that
    /// presents someone else's user agent is rejected just as surely as no token at all.
    /// </summary>
    private static void AbsorbKasada(FlowContext c, KasadaResult result)
    {
        foreach (var kv in result.Headers) c.Session.AntiBotTokens[kv.Key] = kv.Value;

        foreach (var cookie in result.Cookies)
        {
            var eq = cookie.IndexOf('=');
            if (eq > 0) c.Session.Cookies[cookie[..eq].Trim()] = cookie[(eq + 1)..].Trim();
        }

        if (!string.IsNullOrEmpty(result.UserAgent))
        {
            c.Session.UserAgent = result.UserAgent;
            // FlowContext.Options pins the UA from this key; without it the pin has nothing
            // to pin to and the identity check silently does nothing.
            c.Session.Vars["kasada.ua"] = result.UserAgent!;
        }

        if (result.Ct is not null) c.Session.Vars["kasada.ct"] = result.Ct;
        if (result.Sbsd is not null) c.Session.Vars["kasada.sb"] = result.Sbsd;
        if (result.Version is not null) c.Session.Vars["kasada.v"] = result.Version;
        if (result.ClientData is not null) c.Session.Vars["kasada.cd"] = result.ClientData!;
    }

    public override async Task<StepOutcome> SubmitSensorAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.AntiBotTokens.ContainsKey("x-kpsdk-ct"))
            return StepOutcome.Fail("nike: no kasada token to submit");

        // Kasada expects the token to be warmed against the same host that issued the script.
        var url = c.Session.Vars.TryGetValue("kasada.scriptUrl", out var s) && !string.IsNullOrEmpty(s)
            ? s
            : "https://www.nike.com/";

        var res = await GetAsync(c, url, "nike-kasada-submit", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("kasada submit failed", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("kasada token rejected", retryable: true);

        c.Session.Vars["kasada.warm"] = "1";
        return StepOutcome.Success();
    }

    // 鈹€鈹€ product 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var styleColor = StyleColorOf(c.Url);
        if (styleColor is null) return StepOutcome.Fail("nike: cannot resolve styleColor from url");

        var api = "https://api.nike.com/product_feed/threads/v2/" +
                  $"?filter=marketplace({CountryCode})&filter=language({Language})" +
                  $"&filter=channelId({ChannelId})&filter=productInfo.merchProduct.styleColor({styleColor})";

        var res = await GetAsync(c, api, "nike-thread", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("nike thread request failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"nike thread HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;
        c.Session.Vars["styleColor"] = styleColor;

        JObject root;
        try { root = JObject.Parse(res.Body); }
        catch (Exception ex) { return StepOutcome.Fail("nike thread json: " + ex.Message); }

        var objects = root["objects"] as JArray;
        if (objects is null || objects.Count == 0) return StepOutcome.Fail("nike: product not in feed", retryable: true);

        c.Session.Vars["thread"] = objects[0]?.ToString() ?? string.Empty;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.Vars.TryGetValue("thread", out var threadJson))
            return StepOutcome.Fail("nike: no thread loaded");

        var thread = JObject.Parse(threadJson);
        var infos = thread["productInfo"] as JArray;
        if (infos is null || infos.Count == 0) return StepOutcome.Fail("nike: thread has no productInfo");

        var wanted = WantedSize(c);
        var sizes = new List<string>();
        JToken? chosenInfo = null;
        JToken? chosenSku = null;

        foreach (var info in infos)
        {
            var skus = info["skus"] as JArray;
            if (skus is null) continue;

            foreach (var sku in skus)
            {
                var label = SkuLabel(sku);
                if (label is null) continue;
                if (!sizes.Contains(label)) sizes.Add(label);

                if (wanted is null || string.Equals(label, wanted, StringComparison.OrdinalIgnoreCase))
                {
                    chosenInfo ??= info;
                    chosenSku ??= sku;
                    if (wanted is not null) break;
                }
            }

            chosenInfo ??= info;
            if (wanted is not null && chosenSku is not null) break;
        }

        if (chosenInfo is null) return StepOutcome.Fail("nike: no variant found");

        var merchProduct = chosenInfo["merchProduct"];
        var merchPrice = chosenInfo["merchPrice"];

        c.Session.VariantId = chosenSku?["id"]?.ToString() ?? merchProduct?["id"]?.ToString();
        c.Session.VariantTitle = chosenSku?["nikeSize"]?.ToString()
                                 ?? chosenSku?["countrySpecifications"]?.FirstOrDefault()?["localizedSize"]?.ToString()
                                 ?? wanted;
        c.Session.Vars["product"] = chosenInfo["productContent"]?["fullTitle"]?.ToString() ?? string.Empty;
        c.Session.Vars["price"] = merchPrice?["currentPrice"]?.ToString() ?? string.Empty;
        c.Session.Vars["sizes"] = string.Join('|', sizes);
        c.Session.Vars["gTin"] = merchProduct?["gtin"]?.ToString() ?? string.Empty;
        c.Session.Vars["styleColor"] = merchProduct?["styleColor"]?.ToString() ?? string.Empty;

        if (chosenSku?["id"] is null)
            return StepOutcome.Fail("nike: variant has no sku id");
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.Vars.TryGetValue("thread", out var threadJson))
            return StepOutcome.Fail("nike: no thread loaded");

        var thread = JObject.Parse(threadJson);
        var infos = thread["productInfo"] as JArray;
        if (infos is null) return StepOutcome.Fail("nike: thread has no productInfo");

        var anyAvailable = false;
        foreach (var info in infos)
        {
            var status = info["merchProduct"]?["status"]?.ToString();
            var available = info["availability"]?["available"]?.ToObject<bool?>() ?? false;
            var skus = info["skus"] as JArray;
            if (skus is not null)
            {
                foreach (var sku in skus)
                {
                    var skuAvailable = sku["available"]?.ToObject<bool?>() ?? available;
                    if (skuAvailable) anyAvailable = true;
                }
            }
            if (string.Equals(status, "ACTIVE", StringComparison.OrdinalIgnoreCase) && available)
                anyAvailable = true;
        }

        c.Session.Vars["available"] = anyAvailable ? "true" : "false";
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> CheckPriceLimitAsync(FlowContext c, CancellationToken ct)
    {
        var limit = c.Product?.Price;
        if (string.IsNullOrWhiteSpace(limit) || c.Product?.PriceCheck != true) return StepOutcome.Success();

        if (!decimal.TryParse(limit, System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var max))
            return StepOutcome.Success();

        if (!decimal.TryParse(c.Session.Vars.TryGetValue("price", out var p) ? p : "0",
                System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var actual))
            return StepOutcome.Success();

        return actual > max
            ? StepOutcome.Fail($"nike: price {actual} over limit {max}")
            : StepOutcome.Success();
    }

    // 鈹€鈹€ cart / checkout 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
    public override async Task<StepOutcome> CreateCartAsync(FlowContext c, CancellationToken ct)
    {
        var body = new JObject
        {
            ["items"] = new JArray(),
        };
        var res = await PostJsonAsync(c, CartUrl(), body.ToString(Newtonsoft.Json.Formatting.None),
            "nike-cart-create", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("nike cart create failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"nike cart HTTP {res.StatusCode}", retryable: true);

        c.Session.CartId = TryRead(res.Body, "id");
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.VariantId))
            return StepOutcome.Fail("nike: no sku to add");

        var body = new JObject
        {
            ["items"] = new JArray(new JObject
            {
                ["skuId"] = c.Session.VariantId,
                ["quantity"] = c.Session.Quantity,
            }),
            ["shippingAddress"] = new JObject
            {
                ["countryCode"] = c.ProfileData?.Country ?? "US",
            },
        };

        var res = await PostJsonAsync(c, CartUrl(), body.ToString(Newtonsoft.Json.Formatting.None),
            "nike-cart-add", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("nike add to cart failed", retryable: true);

        if (res.StatusCode == 401) return StepOutcome.Fail("nike: login required");
        if (res.StatusCode == 403) return StepOutcome.Fail("nike: kasada rejected cart", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"nike cart HTTP {res.StatusCode}", retryable: true);

        c.Session.CartId = TryRead(res.Body, "id") ?? c.Session.CartId;
        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, CartUrl(), "nike-cart-get", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("nike cart fetch failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"nike cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        c.Session.CartId = TryRead(res.Body, "id") ?? c.Session.CartId;

        var total = TryRead(res.Body, "total");
        if (total is not null) c.Session.Vars["total"] = total;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> EditLineAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.CartId)) return StepOutcome.Fail("nike: no cart to edit");
        return StepOutcome.Success();
    }

    /// <summary>
    /// Nike's checkout is a single page on the storefront origin; the guest token it hands
    /// back is what the payment step posts to.
    /// </summary>
    public override async Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, "https://www.nike.com/checkout",
            Tag() + "-nike-checkout", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("nike checkout unreachable", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("nike checkout blocked (kasada)", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"nike checkout HTTP {res.StatusCode}", retryable: true);

        c.Session.CheckoutUrl = res.Url.ToString();
        c.Session.Vars["checkout"] = res.Body;

        var token = System.Text.RegularExpressions.Regex
            .Match(res.Body, "(?:guestToken|checkoutId)\"?\\s*[:=]\\s*\"([A-Za-z0-9\\-]{8,})\"")
            .Groups[1].Value;
        if (!string.IsNullOrEmpty(token)) c.Session.CheckoutToken = token;

        var total = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"amount\"\\s*:\\s*\"([\\d.]+)\"").Groups[1].Value;
        if (!string.IsNullOrEmpty(total)) c.Session.Vars["total"] = total;

        return StepOutcome.Success();
    }


    /// <summary>
    /// The delivery half of Nike's buy API — R1014's open question, answered by decompilation.
    ///
    /// <para>
    /// <c>sub_140B1DCC0</c> (reached from the frozen <c>checkout_previews/v3</c> literal at
    /// <c>0x147053c94</c> via the <c>chars_va - 12</c> chain) POSTs one request whose
    /// <c>request</c> object carries the delivery block inline —
    /// <c>fulfillmentDetails.location.postalAddress</c>, <c>recipient</c>, <c>contactInfo</c>.
    /// So the resource that takes a delivery write is <b>the preview POST itself</b>; there is no
    /// separate orders surface and never was.
    /// </para>
    ///
    /// <para>
    /// The state machine then makes exactly one more call: <c>checkout_previews_jobs/v3/{suffix}</c>
    /// with no body (the 3-arg send <c>sub_1408B61E0</c>), and never reads the response. The
    /// suffix is the same context field the preview URL read; the reading that explains both
    /// calls is that the transport's response mapper replaced it with the preview job reference
    /// between the awaits — the same mapper path that fills <c>priceId</c> / <c>priceSnapshotId</c> /
    /// <c>paymentToken</c> for the checkout body. The replica follows the job reference when the
    /// response carries one, and the marketplace otherwise.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct)
    {
        var ship = c.Shipping;
        if (ship is null) return StepOutcome.Fail("nike: no shipping address");
        if (string.IsNullOrEmpty(c.Session.VariantId)) return StepOutcome.Fail("nike: no sku id to preview");

        var body = new JObject { ["request"] = BuildBuyRequest(c, checkout: false) };
        var res = await PostJsonAsync(c, NikeEndpoints.CheckoutPreviews + CountryCode,
            body.ToString(Newtonsoft.Json.Formatting.None), "nike-preview", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("nike preview request failed", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("nike preview blocked (kasada)", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"nike preview HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["nike.preview"] = res.Body ?? string.Empty;
        var previewJob = TryRead(res.Body, "id");
        if (!string.IsNullOrEmpty(previewJob)) c.Session.Vars["nike.previewJob"] = previewJob;

        // The follow-up the original always makes (state 0 resume inside sub_140B1DCC0). Its
        // body is discarded there too — the call itself and the mapper's absorption are the point.
        var suffix = c.Session.Vars.TryGetValue("nike.previewJob", out var job) && !string.IsNullOrEmpty(job)
            ? job
            : CountryCode;
        await GetAsync(c, NikeEndpoints.CheckoutPreviewsJobs + suffix, "nike-preview-job", ct)
            .ConfigureAwait(false);

        return StepOutcome.Success();
    }

    /// <summary>
    /// Step <c>GetPaymentMethods</c>, ordinal 57 — the first half of the decoded payment-initiation
    /// chain (<c>sub_140B35420</c>, progress string <c>Initialize payment</c> at 0x146dbca08).
    ///
    /// <para>
    /// <b>R1086: the chain is decompiled, and this step carries its first GET</b> —
    /// <c>https://www.nike.com/gs/checkout-api/api/v5/Order/{order}/InitiatePayment</c> with the
    /// two query parameters the machine assembles (<c>singleStep=true</c>, 0x14715d7e8/0x147173de8,
    /// and <c>deliveryCountryIso</c>, 0x147001c30, ← the profile's shipping country). The URL
    /// prefix is the frozen <c>OrderV5</c> constant the image has carried since R127
    /// (<c>0x1470969f0</c>, 50 chars) and the <c>/InitiatePayment</c> segment is the inline
    /// literal at <c>0x145e92700</c>. The answer carries a payment id this step stores for
    /// <see cref="SubmitPaymentAsync"/>'s half of the chain.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> GetPaymentMethodsAsync(FlowContext c, CancellationToken ct)
    {
        var orderId = c.Session.CartId;
        if (string.IsNullOrEmpty(orderId))
            return StepOutcome.Fail("nike: no order to read payment methods for", retryable: true);

        var country = c.Shipping?.Country ?? "US";

        // The decoded machine's progress label, then its GET: the +8 verb slot (sub_1408b61e0,
        // no payload — the parameters ride the query string the builder assembles). The prefix is
        // the frozen OrderV5 constant; the session var is the replica's standard test/config seam
        // (the checkStockUrl convention) — it overrides the PREFIX, so the composition (order id,
        // segment, the two decoded parameters) is always the machine's own.
        c.Emit("Initialize payment", "StatusInfo");
        var prefix = c.Session.Vars.TryGetValue("nike.initiatePaymentUrl", out var urlOverride) &&
                     !string.IsNullOrEmpty(urlOverride)
            ? urlOverride
            : NikeEndpoints.OrderV5;
        var url = prefix.TrimEnd('/') + "/" + orderId + "/InitiatePayment?singleStep=true" +
                  "&deliveryCountryIso=" + Uri.EscapeDataString(country);
        var res = await GetAsync(c, url, "nike-initiate-payment", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("nike: initiate-payment unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"nike initiate-payment HTTP {res.StatusCode}", retryable: true);

        // The payment id the machine's resume state reads (ctx field 53) and hands to the
        // payment-methods half. Whatever shape the answer takes, an id-shaped field is the
        // contract the second GET keys on.
        c.Session.Vars["nike.paymentBody"] = res.Body ?? string.Empty;
        var paymentId = TryRead(res.Body, "paymentId") ?? TryRead(res.Body, "id");
        if (!string.IsNullOrEmpty(paymentId)) c.Session.Vars["nike.paymentId"] = paymentId!;

        return StepOutcome.Success();
    }

    /// <summary>
    /// The second half of the decoded chain (<c>sub_140B35420</c>'s resume state): the frozen
    /// eshopworld panel read <c>https://payments-panel.production.eshopworld.com/api/v2/PaymentMethods?paymentId={id}</c>
    /// (0x147078698 + ctx field 53), again a GET. Its answer is the payment-methods list and the
    /// token the checkout POST's <c>paymentToken</c> carries (ctx field 29) —
    /// <see cref="SubmitOrderAsync"/> sends it, so this step stores it on the session.
    /// </summary>
    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return StepOutcome.Fail("nike: no card");

        if (!c.Session.Vars.TryGetValue("nike.paymentId", out var paymentId) ||
            string.IsNullOrEmpty(paymentId))
        {
            // The chain's first half has not run — run it, as the decoded machine does, before
            // its own half. One state machine, two GETs, in the image's own order.
            var first = await GetPaymentMethodsAsync(c, ct).ConfigureAwait(false);
            if (!first.Ok) return first;
            paymentId = c.Session.Vars.TryGetValue("nike.paymentId", out var id) ? id : null;
        }

        var methodsPrefix = c.Session.Vars.TryGetValue("nike.paymentMethodsUrl", out var methodsOverride) &&
                           !string.IsNullOrEmpty(methodsOverride)
            ? methodsOverride
            : "https://payments-panel.production.eshopworld.com/api/v2/PaymentMethods";
        var url = methodsPrefix.TrimEnd('/') + "?paymentId=" +
                  Uri.EscapeDataString(paymentId ?? string.Empty);
        var res = await GetAsync(c, url, "nike-payment-methods", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("nike: payment-methods unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"nike payment-methods HTTP {res.StatusCode}", retryable: true);

        // The token is the contract this step exists to feed: ctx field 29 in the checkout body.
        c.Session.Vars["nike.methodsBody"] = res.Body ?? string.Empty;
        var token = TryRead(res.Body, "paymentToken") ?? TryRead(res.Body, "token");
        if (string.IsNullOrEmpty(token))
            return StepOutcome.Fail("nike: payment-methods answer carried no token", retryable: false);
        c.Session.PaymentToken = token;

        return StepOutcome.Success();
    }

    // R1013: the card-attaching half used to live here as a private AttachCardAsync, kept "for when the address is
    // established". Published, and buy/orders/v2 was still in the artifact afterwards -- so the string pool keeps
    // literals from code nothing calls. Keeping the dead method therefore kept the two non-existent endpoints alive in
    // the binary, which is the opposite of what leaving evidence was for. The body is recorded in the round's dossier
    // instead; a comment cannot be compiled.

    /// <summary>
    /// The order submit, decompiled end to end (<c>sub_140B248A0</c>, reached from the frozen
    /// <c>checkouts/v3</c> literal at <c>0x147053d8c</c>).
    ///
    /// <para>
    /// The original reports the progress string <c>Submit order</c> (0x146EA00F0, through
    /// sub_140F9EDF0 before and sub_140F9EE50 after) around one POST to
    /// <c>buy/checkouts/v3/{market}</c> whose <c>request</c> body is the preview shape plus
    /// <c>paymentToken</c>, a <c>totals</c> block, and the checkout-only item decorations. No
    /// guest-proxy order route runs here — <c>gs/checkout-api … v5/Order/</c>
    /// (<see cref="NikeEndpoints.OrderV5"/>) belongs to the GS surface, so the constant stays
    /// in <see cref="NikeEndpoints"/> unused by this flow.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.VariantId)) return StepOutcome.Fail("nike: no sku id to submit");

        var body = new JObject { ["request"] = BuildBuyRequest(c, checkout: true) };
        var res = await PostJsonAsync(c, NikeEndpoints.Checkouts + CountryCode,
            body.ToString(Newtonsoft.Json.Formatting.None), "nike-submit-order", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("nike order submit failed", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("nike order blocked (kasada)", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"nike order HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["nike.checkout"] = res.Body ?? string.Empty;
        var checkoutJob = TryRead(res.Body, "id");
        if (!string.IsNullOrEmpty(checkoutJob)) c.Session.Vars["nike.checkoutJob"] = checkoutJob;

        // The original hands the response to the transport's mapper and reports Submit order
        // done; the order number surfaces through the checkout job. Read it when the response
        // already carries one, and leave the session's value alone otherwise.
        var number = TryRead(res.Body, "orderNumber");
        if (!string.IsNullOrEmpty(number)) c.Session.OrderNumber = number;

        return StepOutcome.Success();
    }

    // ── buy API request assembly (decompiled from sub_140B1DCC0 / sub_140B248A0) ──────────

    /// <summary>
    /// The buy-API request object both POSTs share, assembled the way the two decompiled
    /// builders assemble it. The preview (<c>sub_140B1DCC0</c>) and the checkout
    /// (<c>sub_140B248A0</c>) differ exactly where the pseudocode shows: the checkout reads its
    /// email first, adds <c>paymentToken</c> and a <c>totals</c> block, sends empty promotion
    /// arrays unless a discount code exists, and decorates the item with
    /// <c>priceId</c>/<c>priceSnapshotId</c> plus a <c>taxes</c> slot.
    /// </summary>
    internal JObject BuildBuyRequest(FlowContext c, bool checkout)
    {
        var ship = c.Shipping!;
        var profile = c.ProfileData;
        var discount = DiscountCode(c);

        var request = new JObject();
        if (checkout) request["email"] = profile?.Email;   // checkout reads email first (sub_140B248A0)
        request["country"] = ship.Country;
        request["currency"] = CurrencyFor(CountryCode);
        request["locale"] = c.Session.Vars.TryGetValue("nike.locale", out var loc) && !string.IsNullOrEmpty(loc)
            ? loc
            : $"{Language}_{CountryCode}";
        request["channel"] = "NIKECOM";   // frozen literal 0x146E11460
        request["items"] = new JArray(BuildBuyItem(c, checkout, discount));

        if (checkout)
        {
            // ctx field 29 — whatever the payment step produced; the original does not gate on it.
            request["paymentToken"] = c.Session.PaymentToken;
            // The checkout leaves the promotion arrays empty unless a discount code exists (the
            // marker-only arrays of sub_140B248A0 are serializer metadata, not wire elements).
            request["promotionCodes"] = discount is null
                ? new JArray()
                : new JArray(new JValue(discount));
            request["totals"] = BuildTotals();
        }
        else
        {
            // The preview always sends the code cell, null when the task has none.
            request["promotionCodes"] = new JArray(
                discount is null ? (JToken)JValue.CreateNull() : new JValue(discount));
            request["email"] = profile?.Email;   // preview reads email last (sub_140B1DCC0)
        }

        return request;
    }

    /// <summary>
    /// One item of the buy request. <c>id</c> and <c>skuId</c> are two distinct context fields
    /// in the original (ctx 19 and 17); both trace to the selected sku and their exact feeders
    /// are not yet decoded, so the replica sends the sku id in both slots (Inference).
    /// </summary>
    internal JObject BuildBuyItem(FlowContext c, bool checkout, string? discount)
    {
        var ship = c.Shipping!;
        var profile = c.ProfileData;

        string? productId = null, priceId = null, priceSnapshotId = null;
        if (c.Session.Vars.TryGetValue("thread", out var threadJson))
        {
            try
            {
                var first = (JObject.Parse(threadJson)["productInfo"] as JArray)?.FirstOrDefault();
                productId = first?["merchProduct"]?["id"]?.ToString();
                // merchPrice carries the price ids the checkout body asks for; the original
                // reads them from fields its own feed step filled (ctx 30 / 31).
                priceId = first?["merchPrice"]?["priceId"]?.ToString();
                priceSnapshotId = first?["merchPrice"]?["priceSnapshotId"]?.ToString();
            }
            catch
            {
                // A thread we cannot re-read leaves the ids null — the original's feed step
                // is the next probe, and a missing id must not take the whole step down.
            }
        }

        var item = new JObject
        {
            ["id"] = c.Session.VariantId,
            ["skuId"] = c.Session.VariantId,
            ["productId"] = productId,
            ["offers"] = new JArray(),
        };

        var priceInfo = new JObject
        {
            ["price"] = JValue.CreateNull(),
            ["fullPrice"] = JValue.CreateNull(),
            ["subtotal"] = JValue.CreateNull(),
            ["discount"] = 0,
            ["valueAddedServices"] = 0,
            ["taxTotal"] = 0,
            ["total"] = JValue.CreateNull(),
            ["fullPriceTotal"] = JValue.CreateNull(),
        };
        if (checkout)
        {
            priceInfo["priceId"] = priceId;
            priceInfo["priceSnapshotId"] = priceSnapshotId;
        }

        var itemCosts = new JObject { ["priceInfo"] = priceInfo };
        if (checkout) itemCosts["taxes"] = new JArray();
        itemCosts["promotionDiscounts"] = checkout
            ? (discount is null
                ? new JArray()
                : new JArray(new JObject { ["code"] = discount }))
            : new JArray(new JObject
            {
                ["code"] = discount is null ? (JToken)JValue.CreateNull() : new JValue(discount),
            });
        item["itemCosts"] = itemCosts;

        item["quantity"] = c.Session.Quantity;

        var postal = new JObject
        {
            ["country"] = ship.Country,
            ["address1"] = ship.Address1 ?? string.Empty,
            ["address2"] = ship.Address2 ?? string.Empty,
            ["postalCode"] = ship.ZipCode ?? string.Empty,
            ["city"] = ship.City ?? string.Empty,
            ["state"] = NikeStateValue(ship.State, ship.Country),
        };

        item["fulfillmentDetails"] = new JObject
        {
            ["type"] = "SHIP",   // frozen literal 0x146E747F0
            ["getBy"] = c.Session.Vars.TryGetValue("nike.getBy", out var getBy) ? getBy : null,
            ["location"] = new JObject
            {
                ["id"] = c.Session.Vars.TryGetValue("nike.locationId", out var locId) ? locId : null,
                ["postalAddress"] = postal,
                ["type"] = "address/shipping",   // frozen literal 0x146F6EAB0
            },
        };

        item["valueAddedServices"] = new JArray();

        var recipient = new JObject
        {
            ["firstName"] = ship.FirstName ?? string.Empty,
            ["lastName"] = ship.LastName ?? string.Empty,
        };

        if (checkout && CountryCode == "JP")
        {
            // The JP decoration from sub_140B248A0's tail: when the task's channel string is
            // the interned 'Nike JP' (0x146E173E8), the recipient gains the kana names the
            // profile carries (kana_first_name / kana_last_name keys, empty-string sentinel
            // 0x146A622F8 when absent) and the postal address gains address3 = address2.
            recipient["altFirstName"] = profile?.JapaneseName ?? string.Empty;
            recipient["altLastName"] = profile?.JapaneseSurname ?? string.Empty;
            postal["address3"] = ship.Address2 ?? string.Empty;
        }

        item["recipient"] = recipient;
        item["contactInfo"] = new JObject
        {
            ["phoneNumber"] = profile?.Phone ?? string.Empty,
            ["email"] = profile?.Email ?? string.Empty,
        };

        return item;
    }

    /// <summary>
    /// The <c>totals</c> block, checkout only, exactly as sub_140B248A0 builds it: null
    /// placeholders where the server computes, zeroes and <c>NOT_CALCULATED</c> (0x146E11E58)
    /// where the client asserts nothing yet.
    /// </summary>
    private static JObject BuildTotals()
    {
        return new JObject
        {
            ["total"] = JValue.CreateNull(),
            ["items"] = new JObject
            {
                ["total"] = JValue.CreateNull(),
                ["details"] = new JObject { ["price"] = JValue.CreateNull(), ["discount"] = 0 },
            },
            ["taxes"] = new JObject
            {
                ["total"] = 0,
                ["details"] = new JObject
                {
                    ["items"] = new JObject { ["tax"] = 0, ["type"] = "NOT_CALCULATED" },
                    ["shipping"] = new JObject { ["type"] = "NOT_CALCULATED" },
                    ["valueAddedServices"] = new JObject { ["tax"] = 0, ["type"] = "NOT_CALCULATED" },
                    ["fulfillment"] = new JObject { ["tax"] = 0, ["type"] = "NOT_CALCULATED" },
                },
            },
            ["valueAddedServices"] = new JObject
            {
                ["total"] = 0,
                ["details"] = new JObject { ["price"] = 0, ["discount"] = 0 },
            },
            ["fulfillment"] = new JObject
            {
                ["total"] = JValue.CreateNull(),
                ["details"] = new JObject { ["price"] = JValue.CreateNull(), ["discount"] = 0 },
            },
        };
    }

    /// <summary>
    /// The state the buy API receives, with the sentinel branch both builders carry: when the
    /// profile's state equals one of two interned literals — <c>ASTLA</c> (0x146B34B08) or
    /// <c>CA</c> (0x146B655C8), compared by reference and again by value — the original sends
    /// <c>{country}-{state}</c>; otherwise the raw state field.
    /// </summary>
    private static string? NikeStateValue(string? state, string? country)
    {
        return state == "ASTLA" || state == "CA"
            ? string.Concat(country, "-", state)
            : state;
    }

    /// <summary>
    /// The task's promotion code. The original reads it out of the task's settings map under
    /// the key <c>discount_code</c> (frozen literal 0x147006180, via sub_140B104F0); the
    /// replica reads the same key from the session vars the task config seeds.
    /// </summary>
    private static string? DiscountCode(FlowContext c) =>
        c.Session.Vars.TryGetValue("discount_code", out var code) && !string.IsNullOrEmpty(code)
            ? code
            : null;

    /// <summary>
    /// Inference: the ISO-4217 currency for each of the forty-two marketplaces. The original
    /// converts an int enum the task config holds (sub_141CEDAC0) whose table is not yet
    /// decoded; the wire needs the string either way, and the marketplace table is the
    /// standard one Nike publishes.
    /// </summary>
    private static string CurrencyFor(string country) =>
        MarketplaceCurrency.TryGetValue(country, out var cur) ? cur : "USD";

    private static readonly Dictionary<string, string> MarketplaceCurrency = new()
    {
        ["AT"] = "EUR", ["AU"] = "AUD", ["BE"] = "EUR", ["BG"] = "EUR", ["CH"] = "CHF",
        ["CZ"] = "CZK", ["DE"] = "EUR", ["DK"] = "DKK", ["ES"] = "EUR", ["FI"] = "EUR",
        ["FR"] = "EUR", ["GB"] = "GBP", ["GR"] = "EUR", ["GS"] = "USD", ["HR"] = "EUR",
        ["HU"] = "HUF", ["IE"] = "EUR", ["IL"] = "ILS", ["IN"] = "INR", ["IT"] = "EUR",
        ["JP"] = "JPY", ["LU"] = "EUR", ["MX"] = "MXN", ["MY"] = "MYR", ["NL"] = "EUR",
        ["NO"] = "NOK", ["NZ"] = "NZD", ["PH"] = "PHP", ["PL"] = "PLN", ["PT"] = "EUR",
        ["RO"] = "RON", ["SE"] = "SEK", ["SG"] = "SGD", ["SI"] = "EUR", ["SK"] = "EUR",
        ["TH"] = "THB", ["TR"] = "TRY", ["TW"] = "TWD", ["US"] = "USD", ["VN"] = "VND",
        ["ZA"] = "ZAR",
    };

    // ── helpers ──────────────────────────────────────────────────────────────

    /// <summary>
    /// The cart endpoint. <strong>Not the one the original uses.</strong>
    ///
    /// Round 48 read the string table of <c>Cybersole.exe</c>; the entire Nike purchase surface
    /// is five URLs:
    ///
    ///   POST api.nike.com/buy/checkout_previews/v3/
    ///   POST api.nike.com/buy/checkout_previews_jobs/v3/
    ///   POST api.nike.com/buy/checkouts/v3/
    ///   POST api.nike.com/buy/checkouts_jobs/v3/
    ///   GET  api.nike.com/deliver/available_gtins/v3
    ///
    /// ``buy/carts/v2``, ``buy/orders/v2`` and the string ``SNKRS`` appear nowhere in it.
    /// ``buy/carts/v2`` is a real Nike route — SNKRS used it — so this is not invented; it is
    /// simply not the route the original takes.
    ///
    /// Not changed, deliberately. The original's checkout steps share those five URLs, and
    /// R1076 settled the question this note used to leave open: the delivery write rides the
    /// <c>checkout_previews/v3</c> POST body and the order submit is the <c>checkouts/v3</c>
    /// POST (sub_140B1DCC0 / sub_140B248A0), so the cart surface this method models is a
    /// different route family, kept because the task config still speaks it.
    ///
    /// See docs/NIKE_PARITY.md — it lists the fourteen steps, which of them are missing here,
    /// and why closing the gap needs ``auto_analysis_ready``.
    /// </summary>
    private string CartUrl() =>
        $"https://api.nike.com/buy/carts/v2/{CountryCode}/Nike/SNKRS?format=simplified";  // inferred: no image evidence (R294)

    private static string? StyleColorOf(string url)
    {
        var m = Regex.Match(url, @"/([A-Z]{2}\d{4}-\d{3})");
        if (m.Success) return m.Groups[1].Value;
        m = Regex.Match(url, @"styleColor=([A-Za-z0-9\-]+)");
        return m.Success ? m.Groups[1].Value : null;
    }

    private static string? WantedSize(FlowContext c)
    {
        if (c.Product?.Sizes.Count > 0) return c.Product.Sizes[0];
        if (c.Session.Vars.TryGetValue("size", out var s) && !string.IsNullOrWhiteSpace(s)) return s;
        return null;
    }

    private static string? SkuLabel(JToken sku)
    {
        var nikeSize = sku["nikeSize"]?.ToString();
        if (!string.IsNullOrEmpty(nikeSize)) return nikeSize;

        var cs = sku["countrySpecifications"] as JArray;
        var localized = cs?.FirstOrDefault()?["localizedSize"]?.ToString();
        return string.IsNullOrEmpty(localized) ? null : localized;
    }


}

