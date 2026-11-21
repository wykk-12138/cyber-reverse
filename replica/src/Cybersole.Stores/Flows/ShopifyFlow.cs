using System.Text.RegularExpressions;
using Cybersole.Http;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Shopify flow — the widest-coverage module in the app (one flow serves every
/// <c>*.myshopify.com</c> fronted brand).
///
/// Walked in the order the binary uses: product JSON → cart/add → cart.js →
/// checkout token → email/shipping/rates/billing → payment → complete.
/// </summary>
public class ShopifyFlow : StoreFlow
{
    private readonly string _id;
    private readonly string _name;
    private readonly IReadOnlyList<string> _domains;

    /// <summary>Generic Shopify flow for any *.myshopify.com storefront.</summary>
    public ShopifyFlow() : this("shopify", "Shopify", new[] { "myshopify.com", "shopify.com" })
    {
    }

    /// <summary>
    /// Brand-specific alias. Shopify powers most streetwear retailers, so instead of
    /// duplicating thirty flows each brand is a thin parameterisation of this one.
    /// </summary>
    public ShopifyFlow(string id, string name, IReadOnlyList<string> domains)
    {
        _id = id;
        _name = name;
        _domains = domains;
    }

    public override string Id => _id;
    public override string Name => _name;
    public override IReadOnlyList<string> Domains => _domains;

    // 鈹€鈹€ session 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/", "shopify-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("shopify home unreachable", retryable: true);

        c.Session.Vars["shop"] = Regex.Match(res.Body, @"Shopify\.shop\s*=\s*""([^""]+)""").Groups[1].Value;
        c.Session.Vars["currency"] = Regex.Match(res.Body, @"Shopify\.currency\s*=\s*\{[^}]*""active""\s*:\s*""([^""]+)""").Groups[1].Value;

        var csrf = Regex.Match(res.Body, @"name=""authenticity_token""\s+value=""([^""]+)""");
        if (csrf.Success) c.Session.CsrfToken = csrf.Groups[1].Value;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCsrfAsync(FlowContext c, CancellationToken ct)
    {
        // R823: no fabricated fallback. GetHomeAsync already extracts name="authenticity_token" from the page when the
        // page carries one; if it did not, inventing a GUID here would put a token in the session that this server never
        // issued, and every request carrying it would be rejected as invalid rather than recognised as tokenless.
        // Shopify's cart endpoints do not require one at all, so an absent token is the truthful state.
        return StepOutcome.Success();
    }

    // 鈹€鈹€ product 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
    public const string ToppsCdnPrefix = "https://cdn.cybersole.io/variants/topps-";

    public static readonly IReadOnlyDictionary<string, string> ConvenienceStores =
        new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["Seven-Eleven"] = "seven-eleven",
            ["Lawson"] = "lawson",
            ["Family Mart"] = "family-mart",
            ["Ministop"] = "ministop",
            ["Daily Yamazaki"] = "daily-yamazaki",
            ["Seicomart"] = "seicomart",
        };

    public override async Task<StepOutcome> FindProductFlowAsync(FlowContext c, CancellationToken ct)
    {
        if (IsToppsHost(c.Url) ||
            string.Equals(c.Session.Vars.GetValueOrDefault("shopify.useToppsCdn"), "true",
                StringComparison.OrdinalIgnoreCase))
        {
            return await FindProductCdnAsync(c, ct).ConfigureAwait(false);
        }

        return await base.FindProductFlowAsync(c, ct).ConfigureAwait(false);
    }

    private static bool IsToppsHost(string? url) =>
        !string.IsNullOrEmpty(url) &&
        Uri.TryCreate(url, UriKind.Absolute, out var u) &&
        (u.Host.EndsWith("topps.com", StringComparison.OrdinalIgnoreCase) ||
         u.Host.StartsWith("topps-", StringComparison.OrdinalIgnoreCase));

    /// <summary>
    /// <c>FindProductCDN</c> (<c>0x1433a0f45 &lt;FindProductCDN&gt;d__25</c>, <c>0x140c986f0 -> 0x140c9e420</c>):
    /// splits task input by <c>' '</c>, lowercases the first token, and fetches
    /// <c>GET https://cdn.cybersole.io/variants/topps-{firstTokenLower}.json</c>.
    ///
    /// <para>
    /// Note: <c>https://cdn.cybersole.io/data/products.json</c> belongs to the separate Cybersole test/benchmark
    /// module (<c>0x140d5a380</c>), NOT Topps CDN.
    /// </para>
    ///
    /// <para>
    /// <b>R1305 replaced the Unknown with a shape.</b> <c>off_1449B8EB0</c> is a JSON type handle, not a
    /// string table; the properties came out of the reflection metadata the image still ships, and they
    /// are <c>ToppsCommerceProduct</c> with <c>PriceAmount</c>, <c>ProductImage</c>, <c>ProductVariant</c>,
    /// <c>SelectedOption</c>, <c>VariantImage</c>, <c>ToppsCommerceProductUrl</c> and <c>JToken</c> —
    /// see <see cref="ToppsCdn"/>, which parses the list and matches keys case-insensitively because the
    /// serialised casing was not recovered. <c>topps.schema</c> now records which shape was recognised.
    /// </para>
    /// </summary>
    public async Task<StepOutcome> FindProductCdnAsync(FlowContext c, CancellationToken ct)
    {
        var rawInput = c.Session.Vars.GetValueOrDefault("topps.input");
        if (string.IsNullOrWhiteSpace(rawInput))
            rawInput = c.Product?.Name;
        if (string.IsNullOrWhiteSpace(rawInput))
            rawInput = ProductHandle(c.Url) ?? c.Url;

        var firstToken = rawInput!
            .Split(' ', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .FirstOrDefault() ?? string.Empty;
        var tokenLower = firstToken.ToLowerInvariant();
        if (string.IsNullOrEmpty(tokenLower))
            return StepOutcome.Fail("topps cdn: empty task input");

        var url = c.Session.Vars.TryGetValue("topps.cdnOrigin", out var cdnOrigin) && !string.IsNullOrEmpty(cdnOrigin)
            ? cdnOrigin.TrimEnd('/') + "/variants/topps-" + Uri.EscapeDataString(tokenLower) + ".json"
            : ToppsCdnPrefix + Uri.EscapeDataString(tokenLower) + ".json";

        c.Emit("Finding product (Topps CDN)", "StatusInfo");
        var res = await GetAsync(c, url, "topps-cdn", ct).ConfigureAwait(false);
        if (res is null)
            return StepOutcome.Fail("topps cdn unreachable", retryable: true);

        var retryEnabled = !string.Equals(c.Session.Vars.GetValueOrDefault("topps.retry"), "false",
            StringComparison.OrdinalIgnoreCase);

        if (res.StatusCode == 404)
            return StepOutcome.Fail("topps cdn: 404 variant list not live", retryable: retryEnabled);

        if (!res.IsSuccess)
            return StepOutcome.Fail($"topps cdn HTTP {res.StatusCode}", retryable: retryEnabled);

        c.Session.Vars["raw"] = res.Body ?? string.Empty;
        c.Session.Vars["topps.cdnResponse"] = res.Body ?? string.Empty;

        // R1305: the payload's shape is known now — a list of ToppsCommerceProduct with seven properties
        // (see ToppsCdn). What is not known is whether the keys are PascalCase or camelCase, so the reader
        // matches case-insensitively and the schema label says which shape was recognised rather than
        // claiming the casing.
        var toppsProducts = ToppsCdn.Parse(res.Body);
        if (toppsProducts.Count > 0)
        {
            c.Session.Vars["topps.schema"] = "ToppsCommerceProduct";
            c.Session.Vars["topps.count"] = toppsProducts.Count.ToString();
            c.Session.Vars["topps.products"] = Newtonsoft.Json.JsonConvert.SerializeObject(toppsProducts);
            var firstUrl = toppsProducts.FirstOrDefault(p => !string.IsNullOrEmpty(p.ToppsCommerceProductUrl));
            if (firstUrl is not null)
                c.Session.Vars["topps.productUrl"] = firstUrl.ToppsCommerceProductUrl;
        }
        else
        {
            c.Session.Vars["topps.schema"] = "unknown";
        }

        try
        {
            var token = JToken.Parse(res.Body ?? string.Empty);
            if (token is JObject obj)
            {
                var title = obj["title"]?.ToString();
                if (!string.IsNullOrEmpty(title)) c.Session.Vars["product"] = title!;
                var handle = obj["handle"]?.ToString();
                if (!string.IsNullOrEmpty(handle)) c.Session.Vars["handle"] = handle!;
                var unitPrice = obj["unitPrice"]?.ToString() ?? obj["price"]?.ToString();
                if (!string.IsNullOrEmpty(unitPrice)) c.Session.Vars["price"] = unitPrice!;
            }
        }
        catch (Newtonsoft.Json.JsonException ex)
        {
            return StepOutcome.Fail("topps cdn invalid json: " + ex.Message, retryable: retryEnabled);
        }

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var handle = ProductHandle(c.Url);
        if (handle is null) return StepOutcome.Fail("shopify: cannot resolve product handle from url");

        var url = Origin(c.Url) + "/products/" + handle + ".js";
        var res = await GetAsync(c, url, "shopify-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("shopify product request failed", retryable: true);
        if (res.StatusCode == 404) return StepOutcome.Fail("shopify: product 404");

        var body = res.Body;
        c.Session.Vars["raw"] = body;

        JObject root;
        try { root = JObject.Parse(body); }
        catch (Exception ex) { return StepOutcome.Fail("shopify product json: " + ex.Message); }

        c.Session.Vars["product"] = root["title"]?.ToString() ?? string.Empty;
        c.Session.Vars["handle"] = handle;

        var image = (root["images"] as JArray)?.FirstOrDefault()?.ToString();
        if (!string.IsNullOrEmpty(image))
            c.Session.Vars["image"] = image!.StartsWith("//") ? "https:" + image : image;

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.Vars.TryGetValue("raw", out var raw) || string.IsNullOrWhiteSpace(raw))
            return StepOutcome.Fail("shopify: no product payload");

        var root = JObject.Parse(raw);
        var variants = root["variants"] as JArray;
        if (variants is null || variants.Count == 0) return StepOutcome.Fail("shopify: product has no variants");

        var wanted = WantedSize(c);
        JToken? chosen = null;
        var availableIds = new List<string>();
        var sizes = new List<string>();

        foreach (var v in variants)
        {
            var label = (v["public_title"]?.ToString() ?? v["title"]?.ToString() ?? "").Trim();
            if (label.Length > 0 && !sizes.Contains(label)) sizes.Add(label);

            var available = v["available"]?.ToObject<bool?>() ?? false;
            if (available)
            {
                availableIds.Add(v["id"]?.ToString() ?? string.Empty);
                if (wanted is null ||
                    string.Equals(label, wanted, StringComparison.OrdinalIgnoreCase))
                    chosen ??= v;
            }

            if (chosen is null && wanted is null) chosen = v;
        }

        if (chosen is null) return StepOutcome.Fail("shopify: requested size unavailable");

        c.Session.VariantId = chosen["id"]?.ToString();
        c.Session.VariantTitle = chosen["public_title"]?.ToString() ?? chosen["title"]?.ToString();
        c.Session.Vars["price"] = chosen["price"]?.ToString() ?? root["price"]?.ToString() ?? string.Empty;
        c.Session.Vars["sizes"] = string.Join('|', sizes);
        c.Session.Vars["availableVariants"] = string.Join('|', availableIds);
        return StepOutcome.Success();
    }

    /// <summary>
    /// <c>CheckPriceLimit</c> / <c>CheckPriceLimitApp</c> (<c>0x143373f5f</c>, <c>0x140cf4a20</c>,
    /// <c>0x140d1c1a0</c>, <c>0x140d17860</c>): validates input mode, queries Storefront GraphQL
    /// (<c>POST /api/2020-04/graphql.json</c> with <c>Content-Type: application/graphql</c> and iOS Mobile Buy SDK
    /// headers) when in App/Storefront/ShopApp mode with a token, and checks min/max bounds.
    /// </summary>
    public override async Task<StepOutcome> CheckPriceLimitAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Product?.PriceCheck != true) return StepOutcome.Success();

        var handle = ProductHandle(c.Url) ?? c.Session.Vars.GetValueOrDefault("handle");
        if (string.IsNullOrWhiteSpace(c.Url) ||
            c.Url.Contains("/cart/", StringComparison.OrdinalIgnoreCase) ||
            (string.IsNullOrWhiteSpace(handle) && string.IsNullOrWhiteSpace(c.Product?.Name)))
        {
            c.Emit("Price limit requires keyword or URL input", "error");
            return StepOutcome.Fail("Price limit requires keyword or URL input", retryable: false);
        }

        if (IsAppPriceLimitMode(c) &&
            c.Session.Vars.TryGetValue(GraphQlTokenVar, out var storefrontToken) &&
            !string.IsNullOrWhiteSpace(storefrontToken) &&
            !string.IsNullOrWhiteSpace(handle))
        {
            return await CheckPriceLimitAppAsync(c, storefrontToken!, handle!, ct).ConfigureAwait(false);
        }

        if (decimal.TryParse(c.Session.Vars.GetValueOrDefault("price"),
                System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var actual))
        {
            return EvaluatePriceBounds(c, actual);
        }

        return StepOutcome.Success();
    }

    private static bool IsAppPriceLimitMode(FlowContext c)
    {
        if (string.Equals(c.Session.Vars.GetValueOrDefault("shopify.appPriceCheck"), "true",
                StringComparison.OrdinalIgnoreCase))
            return true;

        var mode = c.Session.Vars.GetValueOrDefault("shopify.mode");
        if (string.Equals(mode, "app", StringComparison.OrdinalIgnoreCase) ||
            string.Equals(mode, "app preload", StringComparison.OrdinalIgnoreCase) ||
            string.Equals(mode, "shop app", StringComparison.OrdinalIgnoreCase) ||
            string.Equals(mode, "storefront", StringComparison.OrdinalIgnoreCase))
            return true;

        if (string.Equals(c.Session.Vars.GetValueOrDefault("shopify.forceApp"), "1",
                StringComparison.OrdinalIgnoreCase) &&
            !string.Equals(c.Session.Vars.GetValueOrDefault("shopify.paymentMethod"), "Google Pay",
                StringComparison.OrdinalIgnoreCase))
            return true;

        return false;
    }

    /// <summary>
    /// <c>CheckPriceLimitApp</c> (<c>0x140d1c1a0 -> 0x140d17860 -> 0x140d17980</c>):
    /// <c>POST https://{host}/api/2020-04/graphql.json</c> (<c>Content-Type: application/graphql</c>)
    /// with Mobile Buy SDK iOS <c>3.7.1</c> headers, optional <c>@inContext(country: ...)</c>,
    /// and min/max price verification against the selected variant.
    /// </summary>
    public async Task<StepOutcome> CheckPriceLimitAppAsync(
        FlowContext c, string storefrontToken, string handle, CancellationToken ct)
    {
        var appContext = c.Session.Vars.GetValueOrDefault("shopify.appContext");
        var contextDirective = string.IsNullOrWhiteSpace(appContext)
            ? string.Empty
            : $" @inContext(country: {appContext.Trim()})";
        var query = $"query{contextDirective} {{ product(handle:\"{handle}\") {{ variants(first: 250) {{ edges {{ node {{ id priceV2 {{ amount currencyCode }} }} }} }} }} }}";

        var url = Origin(c.Url) + "/api/2020-04/graphql.json";
        var headers = new Dictionary<string, string>
        {
            [ShopifyHeaders.StorefrontAccessToken] = storefrontToken,
            ["X-SDK-Variant"] = "ios",
            ["X-SDK-Version"] = "3.7.1",
            ["User-Agent"] = "Mobile Buy SDK iOS/3.7.1/com.tapcart.hoyJaSjQM2",
        };

        var res = await Cybersole.Stores.Payments.ThreeDsTransportHelpers.PostJsonRawAsync(
            c, url, query, headers, "shopify-price-limit-app", ct, "application/graphql")
            .ConfigureAwait(false);

        if (res is null || !res.IsSuccess)
            return StepOutcome.Fail($"shopify price limit app HTTP {res?.StatusCode ?? 0}", retryable: true);

        JObject root;
        try { root = JObject.Parse(res.Body ?? string.Empty); }
        catch (Newtonsoft.Json.JsonException ex)
        {
            return StepOutcome.Fail("shopify price limit json: " + ex.Message, retryable: true);
        }

        var edges = root["data"]?["product"]?["variants"]?["edges"] as JArray;
        if (edges is null || edges.Count == 0)
            return StepOutcome.Fail("shopify price limit: no variants", retryable: true);

        JToken? matchedNode = null;
        var wantedVariant = c.Session.VariantId;
        foreach (var edge in edges)
        {
            var node = edge["node"];
            if (node is null) continue;
            var fullId = node["id"]?.ToString() ?? string.Empty;
            var trailingId = fullId.Contains('/') ? fullId[(fullId.LastIndexOf('/') + 1)..] : fullId;
            if (!string.IsNullOrEmpty(wantedVariant) &&
                (string.Equals(trailingId, wantedVariant, StringComparison.OrdinalIgnoreCase) ||
                 string.Equals(fullId, wantedVariant, StringComparison.OrdinalIgnoreCase)))
            {
                matchedNode = node;
                break;
            }
            matchedNode ??= node;
        }

        var amountStr = matchedNode?["priceV2"]?["amount"]?.ToString();
        var currency = matchedNode?["priceV2"]?["currencyCode"]?.ToString();
        if (!string.IsNullOrEmpty(amountStr)) c.Session.Vars["price"] = amountStr!;
        if (!string.IsNullOrEmpty(currency)) c.Session.Vars["currency"] = currency!;

        if (!decimal.TryParse(amountStr, System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var price))
            return StepOutcome.Fail("shopify price limit: unparseable amount", retryable: true);

        return EvaluatePriceBounds(c, price);
    }

    private static StepOutcome EvaluatePriceBounds(FlowContext c, decimal price)
    {
        var maxEnabled = !string.IsNullOrWhiteSpace(c.Product?.Price);
        var minEnabled = string.Equals(c.Session.Vars.GetValueOrDefault("shopify.minPriceEnabled"), "true",
            StringComparison.OrdinalIgnoreCase);

        if (minEnabled &&
            decimal.TryParse(c.Session.Vars.GetValueOrDefault("shopify.minPrice"),
                System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var min) &&
            price < min)
        {
            c.Emit("Price exceeded", "error");
            return StepOutcome.Fail("Price exceeded", retryable: true);
        }

        if (maxEnabled &&
            decimal.TryParse(c.Product?.Price,
                System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var max) &&
            price > max)
        {
            c.Emit("Price exceeded", "error");
            return StepOutcome.Fail("Price exceeded", retryable: true);
        }

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.Vars.TryGetValue("raw", out var raw) || string.IsNullOrWhiteSpace(raw))
            return StepOutcome.Fail("shopify: no product payload");

        var root = JObject.Parse(raw);
        var variants = root["variants"] as JArray;
        var anyAvailable = variants is not null &&
                           variants.Any(v => v["available"]?.ToObject<bool?>() == true);

        c.Session.Vars["available"] = anyAvailable ? "true" : "false";
        return StepOutcome.Success();
    }

    // 鈹€鈹€ cart 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.VariantId)) return StepOutcome.Fail("shopify: no variant to add");

        var payload = new JObject
        {
            ["id"] = long.TryParse(c.Session.VariantId, out var id) ? id : c.Session.VariantId,
            ["quantity"] = c.Session.Quantity,
        };

        // R1253: the image carries cart/add.js as a token without the leading slash, so this URL is the origin plus
        // an attested token rather than an invented path. Same for cart/update.js below.
        var res = await PostJsonAsync(c, Origin(c.Url) + "/cart/add.js",
            payload.ToString(Newtonsoft.Json.Formatting.None), "shopify-cart-add", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("shopify add to cart failed", retryable: true);
        if (res.StatusCode is 422 or 404) return StepOutcome.Fail("shopify: variant sold out");
        if (!res.IsSuccess) return StepOutcome.Fail($"shopify cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        // R98: the image carries a Storefront GraphQL cart read (a 354-character selection set with
        // checkoutUrl, totals and up to 250 lines) as well as the plain /cart.js read. A storefront
        // hands out a token to a headless store; without one there is nothing to query, so the
        // fallback is the path this flow already used.
        if (c.Session.Vars.TryGetValue(GraphQlTokenVar, out var token) && !string.IsNullOrWhiteSpace(token)
            && c.Session.Vars.TryGetValue(GraphQlCartVar, out var cartId) && !string.IsNullOrWhiteSpace(cartId))
        {
            var graph = await GetCartViaGraphQlAsync(c, token, cartId, ct).ConfigureAwait(false);
            if (graph is not null) return graph.Value;
        }

        var res = await GetAsync(c, Origin(c.Url) + "/cart.js", "shopify-cart-get", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("shopify cart fetch failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"shopify cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        var total = JObject.Parse(res.Body)["total_price"]?.ToString();
        if (total is not null) c.Session.Vars["total"] = total;
        return StepOutcome.Success();
    }

    /// <summary>Session var holding a Storefront access token, when the store hands one out.</summary>
    public const string GraphQlTokenVar = "shopify.storefrontToken";

    /// <summary>Session var holding the GraphQL cart id (<c>gid://shopify/Cart/…</c>).</summary>
    public const string GraphQlCartVar = "shopify.cartId";

    /// <summary>
    /// Reads the cart through the Storefront GraphQL endpoint using the image's own selection set.
    /// Returns null when the call fails, so the caller falls back to <c>/cart.js</c> rather than
    /// reporting a checkout failure for a capability the store may simply not offer.
    /// </summary>
    private async Task<StepOutcome?> GetCartViaGraphQlAsync(
        FlowContext c, string token, string cartId, CancellationToken ct)
    {
        var document = ShopifyGraphQl.CartQueryDocument(
            "query Cart($cartId: ID!) { cart(id: $cartId) ");

        var payload = new JObject
        {
            ["query"] = document,
            ["variables"] = new JObject { ["cartId"] = cartId },
        };

        var url = ShopifyGraphQl.Endpoint(new Uri(c.Url).Host,
            c.Session.Vars.TryGetValue("shopify.apiVersion", out var version) && !string.IsNullOrWhiteSpace(version)
                ? version
                : "2025-04");

        // R203: the name comes from ShopifyHeaders, where the image spells it twice (0x06f2cb4c upper, 0x07187b04 lower).
        c.Session.Headers[ShopifyHeaders.StorefrontAccessToken] = token;

        var res = await PostJsonAsync(c, url, payload.ToString(Newtonsoft.Json.Formatting.None),
            "shopify-cart-graphql", ct).ConfigureAwait(false);

        if (res is null || !res.IsSuccess) return null;

        var checkoutUrl = ShopifyGraphQl.ParseCheckoutUrl(res.Body);
        if (checkoutUrl is not null) c.Session.Vars["checkoutUrl"] = checkoutUrl;

        // R1331: cartLinesUpdate is keyed by line id, and the read already receives it (lines.nodes[].id) —
        // keeping it is what lets the edit take the structured path instead of the REST one.
        try
        {
            var lineId = JObject.Parse(res.Body)?["data"]?["cart"]?["lines"]?["nodes"] is JArray nodes && nodes.Count > 0
                ? nodes[0]?["id"]?.ToString()
                : null;
            if (!string.IsNullOrEmpty(lineId)) c.Session.Vars["shopify.lineId"] = lineId!;
        }
        catch (Newtonsoft.Json.JsonException)
        {
            // A reply that is not the shape we expect just means no line id; the REST edit still works.
        }

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> EditLineAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Quantity <= 1) return StepOutcome.Success();

        // R1331: the observed cartLinesUpdate mutation, when the read has supplied a cart id, a line id and a
        // storefront token. The REST call below is what this step did before and still does without them.
        var token = c.Session.Vars.GetValueOrDefault(GraphQlTokenVar);
        var graphQlCart = c.Session.Vars.GetValueOrDefault(GraphQlCartVar);
        var lineId = c.Session.Vars.GetValueOrDefault("shopify.lineId");
        if (!string.IsNullOrEmpty(token) && !string.IsNullOrEmpty(graphQlCart) && !string.IsNullOrEmpty(lineId))
        {
            var editPayload = new JObject
            {
                ["query"] = ShopifyGraphQl.CartLinesUpdate,
                ["variables"] = new JObject
                {
                    ["cartId"] = graphQlCart,
                    ["lines"] = new JArray { new JObject { ["id"] = lineId, ["quantity"] = c.Session.Quantity } },
                },
            };

            // R1331: the composed endpoint is https, so a capture or a test cannot point it elsewhere. The
            // session override replaces it outright; the default is unchanged.
            var editUrl = c.Session.Vars.GetValueOrDefault("shopify.graphqlBase");
            if (string.IsNullOrEmpty(editUrl))
                editUrl = ShopifyGraphQl.Endpoint(new Uri(c.Url).Host,
                    c.Session.Vars.TryGetValue("shopify.apiVersion", out var editVersion) &&
                    !string.IsNullOrWhiteSpace(editVersion) ? editVersion : "2025-04");

            c.Session.Headers[ShopifyHeaders.StorefrontAccessToken] = token;
            var edited = await PostJsonAsync(c, editUrl,
                editPayload.ToString(Newtonsoft.Json.Formatting.None), "shopify-cart-lines", ct)
                .ConfigureAwait(false);

            if (edited is { IsSuccess: true })
            {
                c.Session.Vars["cart"] = edited.Body;
                return StepOutcome.Success();
            }

            return StepOutcome.Fail($"shopify cart line update HTTP {edited?.StatusCode}", retryable: true);
        }

        var payload = new JObject { ["line"] = 1, ["quantity"] = c.Session.Quantity };
        // R1253: cart/update.js is likewise an attested token (no leading slash in the image).
        var res = await PostJsonAsync(c, Origin(c.Url) + "/cart/update.js",
            payload.ToString(Newtonsoft.Json.Formatting.None), "shopify-cart-change", ct)
            .ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail($"shopify cart change HTTP {res?.StatusCode}", retryable: true);
    }

    // 鈹€鈹€ checkout 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
    public override async Task<StepOutcome> InitiateCheckoutAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/checkout", ShopifyHeaders.CheckoutClientTag, ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("shopify checkout init failed", retryable: true);

        var token = CheckoutTokenOf(res.Url.ToString()) ?? CheckoutTokenOf(res.Body);
        if (token is null) return StepOutcome.Fail("shopify: no checkout token");

        c.Session.CheckoutToken = token;
        c.Session.CheckoutUrl = Origin(c.Url) + "/checkouts/" + token;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.CheckoutToken))
        {
            var init = await InitiateCheckoutAsync(c, ct).ConfigureAwait(false);
            if (!init.Ok) return init;
        }

        var res = await GetAsync(c, c.Session.CheckoutUrl!, ShopifyHeaders.CheckoutSourceTag, ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("shopify checkout fetch failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"shopify checkout HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["checkout"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitEmailAsync(FlowContext c, CancellationToken ct)
    {
        var email = c.ProfileData?.Email ?? c.Account?.Email;
        if (string.IsNullOrEmpty(email)) return StepOutcome.Fail("shopify: profile has no email");

        var payload = new JObject
        {
            ["checkout"] = new JObject { ["email"] = email },
        };

        var res = await PostJsonAsync(c, CheckoutEndpoint(c),
            payload.ToString(Newtonsoft.Json.Formatting.None), "shopify-email", ct)
            .ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail($"shopify email HTTP {res?.StatusCode}", retryable: true);
    }

    public override async Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct)
    {
        var ship = c.Shipping ?? AddressFromProfile(c);
        if (ship is null) return StepOutcome.Fail("shopify: no shipping address");

        var payload = new JObject
        {
            ["checkout"] = new JObject
            {
                ["shipping_address"] = new JObject
                {
                    ["first_name"] = ship.FirstName,
                    ["last_name"] = ship.LastName,
                    ["address1"] = ship.Address1,
                    ["address2"] = ship.Address2,
                    ["city"] = ship.City,
                    ["province"] = ship.State,
                    ["country"] = ship.Country,
                    ["zip"] = ship.ZipCode,
                    ["phone"] = c.ProfileData?.Phone,
                },
            },
        };

        // A shipping_line needs a handle, and the handle only exists after GetShippingRates has
        // read the rate list. The step order is SubmitShipping -> GetShippingRates ->
        // SubmitShipping, so the first call has no handle and the second one does.
        if (c.Session.Vars.TryGetValue("shippingRateHandle", out var handle) && handle.Length > 0)
        {
            ((JObject)payload["checkout"]!)["shipping_line"] = new JObject
            {
                ["handle"] = handle,
            };
        }

        var res = await PostJsonAsync(c, CheckoutEndpoint(c),
            payload.ToString(Newtonsoft.Json.Formatting.None), "shopify-shipping", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("shopify shipping failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"shopify shipping HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["shipping"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// One entry of Shopify's shipping_rates reply.
    /// </summary>
    public readonly record struct RateOption(string Name, string Handle, string Price);

    /// <summary>
    /// Choose a rate from a shipping_rates body.
    ///
    /// <paramref name="preference"/> comes from TaskGroup.ShippingRate, whose comment says
    /// "Preferred shipping method/price for this group" — so it may be either. The order is:
    /// exact name, name containing the preference (case-insensitive), then exact price. A null or
    /// blank preference selects nothing, which leaves the old behaviour untouched and is why this
    /// change cannot regress a group that never set the field.
    /// </summary>
    public static RateOption? PickRate(string body, string? preference)
    {
        if (string.IsNullOrWhiteSpace(preference)) return null;

        var options = new List<RateOption>();
        try
        {
            var root = JObject.Parse(body);
            if (root["shipping_rates"] is JArray array)
            {
                foreach (var item in array.OfType<JObject>())
                {
                    var name = item["name"]?.ToString() ?? string.Empty;
                    var handle = item["handle"]?.ToString() ?? string.Empty;
                    var price = item["price"]?.ToString() ?? string.Empty;
                    if (handle.Length > 0) options.Add(new RateOption(name, handle, price));
                }
            }
        }
        catch (Newtonsoft.Json.JsonException)
        {
            return null;
        }

        var want = preference.Trim();

        var exact = options.FirstOrDefault(o =>
            string.Equals(o.Name, want, StringComparison.OrdinalIgnoreCase));
        if (exact.Handle is not null) return exact;

        var contains = options.FirstOrDefault(o =>
            o.Name.Contains(want, StringComparison.OrdinalIgnoreCase));
        if (contains.Handle is not null) return contains;

        var byPrice = options.FirstOrDefault(o =>
            string.Equals(o.Price, want, StringComparison.Ordinal));
        if (byPrice.Handle is not null) return byPrice;

        return null;
    }

    public override async Task<StepOutcome> GetShippingRatesAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Session.CheckoutUrl + "/shipping_rates", "shopify-rates", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("shopify rates failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"shopify rates HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["rates"] = res.Body;
        var cheapest = Regex.Match(res.Body, @"""price""\s*:\s*""?([\d.]+)""?");
        if (cheapest.Success) c.Session.Vars["shippingPrice"] = cheapest.Groups[1].Value;

        // The body lists every rate; only the first price was kept before, and no handle was
        // remembered, so nothing downstream could choose one. Parse them all and, when the task
        // group asked for a particular method or price, remember its handle for SubmitShipping.
        //
        // TaskGroup.ShippingRate is a string, and the field's comment says "method/price", so the
        // match accepts either: an exact name, a name contained in the rate's name, or a price
        // equal to it. No preference means no selection, and the original behaviour stands.
        c.Session.Vars.TryGetValue("shippingRate", out var preferred);
        var picked = PickRate(res.Body, preferred);
        if (picked is not null)
        {
            c.Session.Vars["shippingRateHandle"] = picked.Value.Handle;
            c.Session.Vars["shippingRateName"] = picked.Value.Name;
        }

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitBillingAsync(FlowContext c, CancellationToken ct)
    {
        var bill = c.Billing ?? c.Shipping ?? AddressFromProfile(c);
        if (bill is null) return StepOutcome.Fail("shopify: no billing address");

        c.Session.Vars["billing1"] = bill.Address1 ?? string.Empty;
        c.Session.Vars["billingZip"] = bill.ZipCode ?? string.Empty;

        // R1332: this step used to return Success here without sending anything, so a run log said billing was
        // done while the checkout had not been touched — the failure then surfaced as a payment error with no
        // cause attached. The endpoint is not captured, and inventing one is worse than saying so: the address
        // is recorded for a consumer that does have it, and the step reports what it did not do.
        c.Session.Vars["shopify.billingSubmitted"] = "false";
        c.Emit("shopify: billing address recorded but no billing request was made — the checkout billing " +
               "endpoint is not captured, so nothing was submitted", "StatusInfo");
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Vars.ContainsKey("convenienceStore") ||
            string.Equals(c.Session.Vars.GetValueOrDefault("shopify.paymentType"), "Convenience Store",
                StringComparison.OrdinalIgnoreCase))
        {
            return await CompleteConvenienceStoreAsync(c, ct).ConfigureAwait(false);
        }

        if (c.Session.Vars.ContainsKey("checkoutcom.offsiteUrl") ||
            string.Equals(c.Session.Vars.GetValueOrDefault(PaymentGatewayNameKey), "checkoutcom",
                StringComparison.OrdinalIgnoreCase) ||
            (c.Session.CheckoutUrl?.Contains("pay.checkout.com", StringComparison.OrdinalIgnoreCase) ?? false))
        {
            if (Cybersole.Stores.Payments.PaymentGatewayRegistry.Default.Resolve("checkoutcom") is not
                Cybersole.Stores.Payments.CheckoutComGateway cko)
                return StepOutcome.Fail("shopify: checkoutcom gateway unavailable");

            var auth = await cko.AuthorizeAsync(c, ct).ConfigureAwait(false);
            if (auth.RequiresAction)
            {
                c.Session.Vars[PaymentGatewayNameKey] = "checkoutcom";
                c.Session.Vars["paymentStatus"] = "requires_action";
                if (!string.IsNullOrEmpty(auth.ThreeDsUrl))
                    c.Session.Vars["threeDsUrl"] = auth.ThreeDsUrl!;
                if (string.Equals(c.Session.Vars.GetValueOrDefault("shopify.autoContinue3ds"), "true",
                        StringComparison.OrdinalIgnoreCase))
                {
                    var done = await cko.CompleteActionAsync(
                        c, c.Session.Vars.GetValueOrDefault("threeDsPayload") ?? string.Empty, ct)
                        .ConfigureAwait(false);
                    return done.Ok
                        ? StepOutcome.Success()
                        : StepOutcome.Fail(done.Error ?? "Payment failed (3DS)", retryable: true);
                }
                return StepOutcome.Success();
            }

            return auth.Ok
                ? StepOutcome.Success()
                : StepOutcome.Fail(auth.Error ?? "checkoutcom payment failed", retryable: false);
        }

        var card = c.Card;
        if (card?.Number is null) return StepOutcome.Fail("shopify: profile has no card");

        var payload = new JObject
        {
            ["checkout"] = new JObject
            {
                ["payment_gateway"] = new JObject
                {
                    ["payment"] = new JObject
                    {
                        ["amount"] = c.Session.Vars.TryGetValue("total", out var t) ? t : "0",
                        ["unique_token"] = Guid.NewGuid().ToString("N"),
                        ["payment_method"] = new JObject
                        {
                            ["credit_card"] = new JObject
                            {
                                ["number"] = card.Number,
                                ["month"] = card.Month,
                                ["year"] = card.Year,
                                ["verification_value"] = card.Cvv,
                                ["name"] = card.Name ?? c.ProfileData?.Display,
                            },
                        },
                    },
                },
            },
        };

        var res = await PostJsonAsync(c, CheckoutEndpoint(c, "/payments"),
            payload.ToString(Newtonsoft.Json.Formatting.None), "shopify-payment", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("shopify payment failed", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail($"shopify payment HTTP {res.StatusCode}: {Truncate(res.Body)}");

        c.Session.PaymentToken = Regex.Match(res.Body, @"""id""\s*:\s*""([^""]+)""").Groups[1].Value;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.CheckoutToken)) return StepOutcome.Fail("shopify: no checkout token");

        var res = await PostJsonAsync(c, CheckoutEndpoint(c, "/complete"),
            "{}", "shopify-complete", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("shopify complete failed", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail($"shopify complete HTTP {res.StatusCode}: {Truncate(res.Body)}");

        var body = JObject.Parse(res.Body);
        c.Session.OrderId = body["id"]?.ToString();
        c.Session.OrderNumber = body["order_id"]?.ToString()
                                ?? body["order_number"]?.ToString()
                                ?? body["name"]?.ToString();
        c.Session.TrackingUrl = body["order_status_url"]?.ToString();
        return string.IsNullOrEmpty(c.Session.OrderNumber) && string.IsNullOrEmpty(c.Session.OrderId)
            ? StepOutcome.Fail("shopify: complete returned no order")
            : StepOutcome.Success();
    }

    // ── recovered steps with real bodies ──────────────────────────────────────

    /// <summary>
    /// Shopify keeps the cart token in <c>_secure_session_id</c> and the checkout token in the
    /// permalink; the structure token is what the checkout form posts back.
    /// </summary>
    public override async Task<StepOutcome> GetStructureTokenAsync(FlowContext c,
        CancellationToken ct)
    {
        await Task.CompletedTask.ConfigureAwait(false);

        if (c.Session.Cookies.TryGetValue("_secure_session_id", out var secure))
        {
            c.Session.Vars["structureToken"] = secure;
            return StepOutcome.Success();
        }

        if (!string.IsNullOrEmpty(c.Session.CheckoutToken))
        {
            c.Session.Vars["structureToken"] = c.Session.CheckoutToken!;
            return StepOutcome.Success();
        }

        return StepOutcome.Fail("shopify: no structure token yet", retryable: true);
    }

    /// <summary>Build the checkout URL the payment step will post to.</summary>
    public override async Task<StepOutcome> BuildDestinationAsync(FlowContext c,
        CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.CheckoutToken))
        {
            var init = await InitiateCheckoutAsync(c, ct).ConfigureAwait(false);
            if (!init.Ok) return init;
        }

        c.Session.Vars["destination"] = Origin(c.Url) + "/checkouts/" + c.Session.CheckoutToken;
        return StepOutcome.Success();
    }

    /// <summary>
    /// Shopify's cart/checkout forms take a fixed field set; Fill stages every value before
    /// the individual submits run so a failure names one step, not "checkout failed".
    /// </summary>
    public override async Task<StepOutcome> FillAsync(FlowContext c, CancellationToken ct)
    {
        await Task.CompletedTask.ConfigureAwait(false);

        var profile = c.ProfileData;
        if (profile is null) return StepOutcome.Fail("shopify: no profile to fill from");

        var fields = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["checkout[email]"] = profile.Email ?? string.Empty,
            ["checkout[shipping_address][first_name]"] = profile.FirstName ?? string.Empty,
            ["checkout[shipping_address][last_name]"] = profile.LastName ?? string.Empty,
            ["checkout[shipping_address][address1]"] = profile.Address1 ?? string.Empty,
            ["checkout[shipping_address][address2]"] = profile.Address2 ?? string.Empty,
            ["checkout[shipping_address][city]"] = profile.City ?? string.Empty,
            ["checkout[shipping_address][province]"] = profile.State ?? string.Empty,
            ["checkout[shipping_address][zip]"] = profile.Zip ?? string.Empty,
            ["checkout[shipping_address][country]"] = profile.Country ?? string.Empty,
            ["checkout[shipping_address][phone]"] = profile.Phone ?? string.Empty,
        };

        if (c.Card is { Number: not null } card)
        {
            fields["checkout[credit_card][number]"] = card.Number;
            fields["checkout[credit_card][month]"] = card.Month ?? string.Empty;
            fields["checkout[credit_card][year]"] = card.Year ?? string.Empty;
            fields["checkout[credit_card][verification_value]"] = card.Cvv ?? string.Empty;
            fields["checkout[credit_card][name]"] = card.Name ?? profile.Display;
        }

        foreach (var kv in fields) c.Session.Vars["fill." + kv.Key] = kv.Value;
        c.Session.Vars["fill.count"] = fields.Count.ToString();
        return StepOutcome.Success();
    }

    /// <summary>Extract the order identity from whatever the complete call returned.</summary>
    public override async Task<StepOutcome> ProcessResponseAsync(FlowContext c,
        CancellationToken ct)
    {
        await Task.CompletedTask.ConfigureAwait(false);

        if (!c.Session.Vars.TryGetValue("checkout", out var body) || string.IsNullOrWhiteSpace(body))
            return StepOutcome.Fail("shopify: no checkout payload to process");

        var order = System.Text.RegularExpressions.Regex.Match(
            body, "\"order_id\"\\s*:\\s*\"?([A-Za-z0-9\\-]+)\"?");
        if (order.Success) c.Session.OrderNumber = order.Groups[1].Value;

        var name = System.Text.RegularExpressions.Regex.Match(
            body, "\"name\"\\s*:\\s*\"(#?[A-Za-z0-9\\-]+)\"");
        if (name.Success && string.IsNullOrEmpty(c.Session.OrderNumber))
            c.Session.OrderNumber = name.Groups[1].Value;

        var tracking = System.Text.RegularExpressions.Regex.Match(
            body, "\"order_status_url\"\\s*:\\s*\"([^\"]+)\"");
        if (tracking.Success) c.Session.TrackingUrl = tracking.Groups[1].Value;

        return string.IsNullOrEmpty(c.Session.OrderNumber) && string.IsNullOrEmpty(c.Session.OrderId)
            ? StepOutcome.Fail("shopify: response carried no order identity")
            : StepOutcome.Success();
    }


    // 鈹€鈹€ helpers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
    /// <summary>
    /// Completes Shopify Offsite Convenience Store payments recovered in Dossier 2B §4:
    /// (1) <c>komoju.com</c> (<c>0x140d98f60</c>): GET page -> <c>meta[name='csrf-token']</c> -> POST JSON
    /// <c>{"authenticity_token", "payment_details":{"type":"konbini","email","store","given_name"}}</c>;
    /// (2) WebCVS Konbini (<c>0x140dcecf0</c>): <c>form[name='toShopify']</c> or
    /// <c>form[name='webcvsFepChargePaymentInfoEntryActionForm']</c> with <c>shift_jis</c> form fields.
    ///
    /// <para>
    /// <b>R1304 corrected the Unknown here.</b> There is no <c>formUrl</c> suffix expression inside
    /// <c>0x140d98f60</c>: that function builds exactly the body above and hands it to the sender with a URL
    /// taken from its state machine's context (<c>*(*(v3+16)+16)</c>), so the target is chosen by its caller
    /// and not composed there. The claim about a <c>[1..56]</c> slice is retracted.
    /// </para>
    ///
    /// <para>
    /// <b>Unknown</b>: which URL the konbini body goes to. The sibling card machine
    /// (<c>0x140D994D0</c>) does name one — <c>https://komoju.com/gpayments_offsite/auth</c>, now
    /// <see cref="Cybersole.Stores.Payments.KomojuGateway.AuthUrl"/> — but it posts a different body
    /// (<c>browser_info</c>/<c>uuid</c>/<c>token</c>), so reusing it here would be a guess. Until a capture or
    /// a caller decode supplies it, the value still comes from <c>komoju.formUrl</c> or the page's
    /// <c>&lt;form action&gt;</c>.
    /// </para>
    /// </summary>
    public async Task<StepOutcome> CompleteConvenienceStoreAsync(FlowContext c, CancellationToken ct)
    {
        var requestedStore = c.Session.Vars.GetValueOrDefault("convenienceStore") ?? "Seven-Eleven";
        var mappedStore = ConvenienceStores.TryGetValue(requestedStore, out var mapped)
            ? mapped
            : requestedStore.ToLowerInvariant().Replace(' ', '-');

        var offsiteUrl = c.Session.Vars.GetValueOrDefault("offsiteUrl") ?? c.Session.CheckoutUrl ?? c.Url;
        var pageRes = await Cybersole.Stores.Payments.ThreeDsTransportHelpers.GetRawAsync(
            c, offsiteUrl, null, "shopify-konbini-get", ct).ConfigureAwait(false);
        if (pageRes is null || !pageRes.IsSuccess)
            return StepOutcome.Fail("shopify konbini: offsite page unreachable", retryable: true);

        var body = pageRes.Body ?? string.Empty;
        var currentUrl = pageRes.Url.ToString();

        if (offsiteUrl.Contains("komoju", StringComparison.OrdinalIgnoreCase) ||
            string.Equals(c.Session.Vars.GetValueOrDefault("shopify.offsiteKind"), "komoju",
                StringComparison.OrdinalIgnoreCase))
        {
            var csrf = Cybersole.Stores.Payments.ThreeDsTransportHelpers.ReadMetaContent(body, "csrf-token");
            if (string.IsNullOrEmpty(csrf))
                return StepOutcome.Fail("komoju: missing csrf-token meta");

            var (formAction, _) = Cybersole.Stores.Payments.ThreeDsTransportHelpers.ExtractForm(body);
            var formUrl = c.Session.Vars.GetValueOrDefault("komoju.formUrl")
                          ?? (string.IsNullOrEmpty(formAction)
                              ? null
                              : Cybersole.Stores.Payments.ThreeDsTransportHelpers.ResolveUrl(currentUrl, formAction!));
            if (string.IsNullOrEmpty(formUrl))
            {
                return StepOutcome.Fail(
                    "komoju: formUrl unknown — exact suffix expression in 0x140d98f60 [1..56] was not statically recovered and page carried no form action");
            }

            var payload = new JObject
            {
                ["authenticity_token"] = csrf,
                ["payment_details"] = new JObject
                {
                    ["type"] = "konbini",
                    ["email"] = c.ProfileData?.Email ?? c.Account?.Email ?? string.Empty,
                    ["store"] = mappedStore,
                    ["given_name"] = c.Billing?.FirstName ?? c.Shipping?.FirstName ?? c.ProfileData?.FirstName ?? string.Empty,
                },
            };

            var komojuOrigin = "https://komoju.com";
            var komojuRes = await Cybersole.Stores.Payments.ThreeDsTransportHelpers.PostJsonRawAsync(
                c,
                formUrl!,
                payload.ToString(Newtonsoft.Json.Formatting.None),
                new Dictionary<string, string>
                {
                    ["Origin"] = komojuOrigin,
                    ["Referer"] = komojuOrigin,
                },
                "shopify-komoju-post",
                ct).ConfigureAwait(false);

            return komojuRes is not null && komojuRes.IsSuccess
                ? StepOutcome.Success()
                : StepOutcome.Fail($"komoju HTTP {komojuRes?.StatusCode ?? 0}", retryable: true);
        }

        // WebCVS Konbini (0x140dce6b0 -> 0x140dcecf0)
        var (toShopifyAction, toShopifyInputs) = Cybersole.Stores.Payments.ThreeDsTransportHelpers.ExtractForm(
            body, "toShopify");
        if (!string.IsNullOrEmpty(toShopifyAction))
        {
            var fwdUrl = Cybersole.Stores.Payments.ThreeDsTransportHelpers.ResolveUrl(currentUrl, toShopifyAction!);
            var fwdRes = await Cybersole.Stores.Payments.ThreeDsTransportHelpers.PostFormRawAsync(
                c, fwdUrl, toShopifyInputs, null, "shopify-webcvs-forward", ct).ConfigureAwait(false);
            return fwdRes is not null && fwdRes.IsSuccess
                ? StepOutcome.Success()
                : StepOutcome.Fail($"webcvs forward HTTP {fwdRes?.StatusCode ?? 0}", retryable: true);
        }

        var (entryAction, entryInputs) = Cybersole.Stores.Payments.ThreeDsTransportHelpers.ExtractForm(
            body, "webcvsFepChargePaymentInfoEntryActionForm");
        if (string.IsNullOrEmpty(entryAction))
            return StepOutcome.Fail("webcvs: entry form not found");

        var webCvsType = mappedStore switch
        {
            "seven-eleven" => "001",
            "lawson" => "002",
            "family-mart" => "016",
            "ministop" => "005",
            "seicomart" => "018",
            _ => "001",
        };
        var isMajorThree = webCvsType is "001" or "002" or "016";

        var emailAddr = c.ProfileData?.Email ?? c.Account?.Email ?? string.Empty;
        var bill = c.Billing ?? c.Shipping;
        var webCvsForm = new Dictionary<string, string>
        {
            ["org.apache.struts.taglib.html.TOKEN"] =
                entryInputs.GetValueOrDefault("org.apache.struts.taglib.html.TOKEN") ?? string.Empty,
            ["webCvsType"] = webCvsType,
            ["webCvsType1"] = isMajorThree ? webCvsType : "999",
            ["webCvsType2"] = isMajorThree ? string.Empty : webCvsType,
            ["lastName"] = bill?.LastName ?? c.ProfileData?.LastName ?? string.Empty,
            ["firstName"] = bill?.FirstName ?? c.ProfileData?.FirstName ?? string.Empty,
            ["lastNameKana"] = string.Empty,
            ["firstNameKana"] = string.Empty,
            ["telephoneNumber"] = c.ProfileData?.Phone ?? string.Empty,
            ["emailAddress"] = emailAddr,
            ["confirmEmailAddress"] = emailAddr,
            ["zipCode1"] = "000",
            ["zipCode2"] = "0000",
            ["address1"] = string.Empty,
            ["address2"] = string.Empty,
            ["address3"] = string.Empty,
        };

        System.Text.Encoding.RegisterProvider(System.Text.CodePagesEncodingProvider.Instance);
        var shiftJis = System.Text.Encoding.GetEncoding("shift_jis");
        var entryUrl = Cybersole.Stores.Payments.ThreeDsTransportHelpers.ResolveUrl(currentUrl, entryAction!);
        var entryRes = await Cybersole.Stores.Payments.ThreeDsTransportHelpers.PostFormRawAsync(
            c, entryUrl, webCvsForm, null, "shopify-webcvs-submit", ct, encoding: shiftJis).ConfigureAwait(false);

        return entryRes is not null && entryRes.IsSuccess
            ? StepOutcome.Success()
            : StepOutcome.Fail($"webcvs HTTP {entryRes?.StatusCode ?? 0}", retryable: true);
    }

    private static string CheckoutEndpoint(FlowContext c, string? suffix = null)
    {
        var baseUrl = c.Session.CheckoutUrl;
        if (string.IsNullOrEmpty(baseUrl))
            baseUrl = Origin(c.Url) + "/checkouts/" + (c.Session.CheckoutToken ?? string.Empty);
        return string.IsNullOrEmpty(suffix) ? baseUrl! : baseUrl + suffix;
    }

    private static string? ProductHandle(string url)
    {
        var m = Regex.Match(url, @"/products/([A-Za-z0-9_\-%.]+)");
        if (m.Success) return m.Groups[1].Value;
        var u = new Uri(url);
        var last = u.AbsolutePath.Trim('/').Split('/').LastOrDefault();
        return string.IsNullOrWhiteSpace(last) ? null : last;
    }

    private static string? WantedSize(FlowContext c)
    {
        if (c.Product?.Sizes.Count > 0) return c.Product.Sizes[0];
        if (c.Session.Vars.TryGetValue("size", out var s) && !string.IsNullOrWhiteSpace(s)) return s;
        return null;
    }

    private static string? CheckoutTokenOf(string text)
    {
        var m = Regex.Match(text, @"checkouts/(?:cn/)?([A-Za-z0-9]{20,})");
        if (m.Success) return m.Groups[1].Value;
        m = Regex.Match(text, @"""token""\s*:\s*""([A-Za-z0-9]{20,})""");
        return m.Success ? m.Groups[1].Value : null;
    }

    private static Cybersole.Core.Models.Address? AddressFromProfile(FlowContext c)
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

    private static string Truncate(string s) => s.Length <= 160 ? s : s[..160];
}
