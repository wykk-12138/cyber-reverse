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

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> EditLineAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Quantity <= 1) return StepOutcome.Success();

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
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
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
