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

        // 2. Fall back to the script engine. Expected to fail on current builds, but a build
        //    that exposes ct() directly would still work here.
        if (!c.Session.Vars.TryGetValue("kasada.script", out var script) || string.IsNullOrEmpty(script))
            return StepOutcome.Fail("nike: no kasada script loaded");

        using var solver = new KasadaSolver(new BrowserShim
        {
            Href = c.Session.Vars.TryGetValue("kasada.scriptUrl", out var u) ? u : c.Url,
            Cookie = c.Session.CookieHeader(),
        });

        var result = solver.Solve(script);
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
    /// Nike's checkout API takes the delivery block as a PUT on the order. The region segment
    /// (the "US" in the path) is the same one <see cref="SubmitOrderAsync"/> uses.
    /// </summary>
    public override async Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.CartId))
            return StepOutcome.Fail("nike: no order to attach a delivery to");

        var ship = c.Shipping;
        if (ship is null) return StepOutcome.Fail("nike: no shipping address");

        var payload = new JObject
        {
            ["deliveryType"] = "SHIP_AND_HANDLE",
            ["address"] = new JObject
            {
                ["address1"] = ship.Address1 ?? string.Empty,
                ["address2"] = ship.Address2 ?? string.Empty,
                ["city"] = ship.City ?? string.Empty,
                ["state"] = ship.State ?? string.Empty,
                ["postalCode"] = ship.ZipCode ?? string.Empty,
                ["country"] = ship.Country ?? "US",
            },
            ["phoneNumber"] = c.ProfileData?.Phone ?? string.Empty,
            ["recipient"] = new JObject
            {
                ["firstName"] = ship.FirstName ?? string.Empty,
                ["lastName"] = ship.LastName ?? string.Empty,
            },
        };

        // R1014: this PUT to buy/orders/v2/US/{cart}/delivery until R1013, and to NikeEndpoints.Checkouts after it. Both
        // were wrong in the same way, and the second was worse.
        //
        // buy/orders/v2 is in the image zero times -- there is no cart endpoint and no order endpoint, only
        // checkout_previews/v3, its jobs, checkouts/v3 and checkouts_jobs/v3. So the old address could only 404, and it
        // said so. R1013 replaced it with checkouts/v3 on the strength of a header sentence -- "the resource every step
        // writes to" -- which is true and does not settle which resource carries a delivery write. CartUrl()'s own note
        // had already ruled on exactly this move: "there is no way to tell which of checkouts/v3 and checkout_previews/v3
        // carries the add. Swapping one guess for another would move the failure, not remove it."
        //
        // A swapped guess is worse than the 404 because it comes back with 200 or with an error about the payload, and
        // then the message no longer points at the address. So this reports instead, and the three candidates are named
        // in the text so the next attempt starts from them rather than from scratch.
        _ = payload;  // built below and unused until the resource is established
        return StepOutcome.Fail(
            "nike: delivery endpoint not captured -- buy/orders/v2 is in the image zero times; the buy surface is "
            + "checkout_previews/v3 and checkouts/v3 with their jobs, and which one takes a delivery write is not "
            + "established", retryable: false);
    }

    /// <summary>
    /// Step <c>GetPaymentMethods</c>, ordinal 57, which sits between <c>GetShopperIp</c> and
    /// <c>SubmitOrder</c> in the image's sequence (<c>StoreFlowSteps.Nike</c>, source Literal).
    ///
    /// <para>
    /// <b>R1012: this is the first override of this step anywhere in the replica.</b> R1008 found that
    /// <c>StoreFlow.GetPaymentMethodsAsync</c> had none, and R963 established that an unoverridden base method is
    /// trimmed -- so the step existed in no artifact and read <c>Vars["paymentMethodsUrl"]</c>, a key name that is
    /// absent from the image in both encodings. An override both gives the step a caller and lets the address come
    /// from the image instead of from a session variable nobody sets.
    /// </para>
    ///
    /// <para>
    /// The address is <see cref="NikeEndpoints.Checkouts"/>, which the image carries at <c>0x147053d8c</c> and which
    /// <c>NikeEndpoints</c>' header describes as the single resource every checkout step writes to. Nike's own
    /// <c>GetPaymentMethods</c> is a read of the checkout, not a separate route -- the image names no
    /// payment-methods path for this host at all, so inventing one would be the join-two-fragments mistake.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> GetPaymentMethodsAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.CartId))
            return StepOutcome.Fail("nike: no checkout to read payment methods from", retryable: true);

        // R1014: R1012 read this from NikeEndpoints.Checkouts, on the same header sentence the delivery step used, and
        // for the same insufficient reason -- the image says every step writes to one checkout resource but not which
        // step writes what, and it names no payment-methods route for this host at all. Reading a guess is worse than
        // saying nothing, because a read that returns the checkout's JSON parses to "no methods offered" and reads like
        // a shop that refuses cards.
        //
        // What stays is the part that was never a guess: the step has an override, so it is no longer trimmed (R963),
        // and it names the candidate resources so the next attempt has somewhere to start.
        return StepOutcome.Fail(
            "nike: payment-methods endpoint not captured -- the image names no such route for this host; the buy "
            + "surface is checkout_previews/v3 and checkouts/v3 with their jobs, and which one carries the list is not "
            + "established", retryable: false);
    }

    /// <summary>
    /// Payment goes through two calls: InitiatePayment hands back a token, then the payment
    /// block is PUT onto the order. Kasada guards both, which is why the sensor has to be
    /// submitted earlier in the flow.
    /// </summary>
    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.CartId))
            return StepOutcome.Fail("nike: no order to pay for");

        var card = c.Card;
        if (card?.Number is null) return StepOutcome.Fail("nike: no card");

        // R1011: this step used to POST to buy/orders/v2/.../initiatePayment and PUT to .../payment. Neither family
        // exists. `NikeEndpoints`' own header has said so since R87 -- it records that the replica was calling two URL
        // families the binary does not contain -- and the two literals survived anyway, inside an override, which means
        // they are compiled into the artifact and would go out on the wire.
        //
        // What the image does name, in address order:
        //   0x147053d8c  https://api.nike.com/buy/checkouts/v3/                     one resource every step writes to
        //   0x147053c94  https://api.nike.com/buy/checkout_previews/v3/             the preview half
        //   0x146ab768c  /rpc/payment/pay/initiatePayment                           an RPC form, host not paired
        //   0x146aafe84  /InitiatePayment                                           a controller name
        //
        // So the operation is real and its address is not established: the RPC path has no host literal beside it, and
        // pairing it with api.nike.com would be the join-two-seen-fragments mistake `EndpointProvenanceTests` was
        // written to stop. Reporting that is worth more than sending a request that can only 404 -- the old code turned
        // a missing endpoint into "nike initiatePayment HTTP 404", which reads like the store refusing us.
        return StepOutcome.Fail(
            "nike: payment endpoint not captured -- the image names /rpc/payment/pay/initiatePayment without a host "
            + "and buy/checkouts/v3 as the resource, while buy/orders/v2 (what this step used) is in it zero times",
            retryable: false);
    }

    // R1013: the card-attaching half used to live here as a private AttachCardAsync, kept "for when the address is
    // established". Published, and buy/orders/v2 was still in the artifact afterwards -- so the string pool keeps
    // literals from code nothing calls. Keeping the dead method therefore kept the two non-existent endpoints alive in
    // the binary, which is the opposite of what leaving evidence was for. The body is recorded in the round's dossier
    // instead; a comment cannot be compiled.

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.CartId)) return StepOutcome.Fail("nike: no cart to submit");

        var order = TryRead(c.Session.Vars.TryGetValue("cart", out var cart) ? cart : "{}", "orderNumber");
        if (order is not null)
        {
            c.Session.OrderNumber = order;
            return StepOutcome.Success();
        }

        // R129: this used to post to a hand-built `api.nike.com/buy/orders/v2/US/{id}/submit` — the
        // R87 invention. The image's only order endpoint is NikeEndpoints.OrderV5, on the guest-checkout
        // proxy host, so the cart id travels in the body instead of the path.
        var payload = new JObject
        {
            ["cartId"] = c.Session.CartId,
            ["country"] = CountryCode,
        };

        var res = await PostJsonAsync(c, NikeEndpoints.OrderV5,
            payload.ToString(Newtonsoft.Json.Formatting.None), "nike-order", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("nike order submit failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"nike order HTTP {res.StatusCode}", retryable: true);

        var body = JObject.Parse(res.Body);
        c.Session.OrderNumber = body["orderNumber"]?.ToString() ?? body["id"]?.ToString();
        c.Session.OrderId = body["id"]?.ToString();
        return string.IsNullOrEmpty(c.Session.OrderNumber)
            ? StepOutcome.Fail("nike: order response had no number")
            : StepOutcome.Success();
    }

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
    /// Not changed, deliberately. The original's fourteen checkout steps share those five URLs,
    /// which means most of them write to one checkout resource rather than hitting fourteen
    /// endpoints; without the decompiled step bodies there is no way to tell which of
    /// ``checkouts/v3`` and ``checkout_previews/v3`` carries the add. Swapping one guess for
    /// another would move the failure, not remove it.
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

