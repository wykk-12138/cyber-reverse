using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Magento-style storefront (End Clothing, Offspring, Footpatrol, Size?, …).
///
/// Magento exposes a guest-cart REST surface that the binary targets directly:
/// <c>/rest/V1/guest-carts/{mask}/items</c>, <c>/estimate-shipping-methods</c>,
/// <c>/shipping-information</c>, <c>/payment-information</c>, <c>/order</c>.
/// </summary>
public class MagentoFlow : StoreFlow
{
    private readonly string _id;
    private readonly string _name;
    private readonly IReadOnlyList<string> _domains;
    private readonly string _apiHost;

    public MagentoFlow(string id, string name, IReadOnlyList<string> domains, string? apiHost = null)
    {
        _id = id;
        _name = name;
        _domains = domains;
        _apiHost = apiHost ?? string.Empty;
    }

    public override string Id => _id;
    public override string Name => _name;
    public override IReadOnlyList<string> Domains => _domains;

    protected string ApiOrigin(FlowContext c) =>
        string.IsNullOrEmpty(_apiHost) ? Origin(c.Url) : "https://" + _apiHost;

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/", "magento-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("magento home unreachable", retryable: true);

        c.Session.Vars["home"] = res.Body;
        var formKey = Regex.Match(res.Body, @"name=""form_key""[^>]*value=""([^""]+)""|""form_key""\s*:\s*""([^""]+)""");
        var key = formKey.Groups[1].Success ? formKey.Groups[1].Value : formKey.Groups[2].Value;
        if (!string.IsNullOrEmpty(key)) c.Session.CsrfToken = key;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCsrfAsync(FlowContext c, CancellationToken ct)
    {
        if (!string.IsNullOrEmpty(c.Session.CsrfToken)) return StepOutcome.Success();

        // R823: Magento sends this value as ["CSRFToken"], so a fabricated one guaranteed an "invalid form key" answer
        // that looked like a protocol mismatch. GetHomeAsync extracts form_key when the page carries it; when it does
        // not, the session stays tokenless and the submission reports a missing key, which is the true condition.
        c.Session.Headers["X-Requested-With"] = "XMLHttpRequest";
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "magento-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("magento product unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"magento product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;
        c.Session.Vars["product"] = Regex.Match(res.Body,
            @"<span[^>]*itemprop=""name""[^>]*>([^<]+)<").Groups[1].Value is { Length: > 0 } n
            ? n
            : Regex.Match(res.Body, @"<title>([^<|]+)").Groups[1].Value;
        c.Session.Vars["price"] = Regex.Match(res.Body,
            @"""price""\s*:\s*""?([\d.]+)""?").Groups[1].Value;
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        if (string.IsNullOrWhiteSpace(body)) return Task.FromResult(StepOutcome.Fail("magento: no product page"));

        var wanted = c.Product?.Sizes.FirstOrDefault() ??
                     (c.Session.Vars.TryGetValue("size", out var s) && !string.IsNullOrWhiteSpace(s) ? s : null);

        // Magento 2 puts the full SKU matrix in a JSON blob.
        var jsonBlob = Regex.Match(body, @"""jsonConfig""\s*:\s*(\{.*?\})\s*,\s*""", RegexOptions.Singleline);
        var sizes = new List<string>();
        string? chosenSku = null;

        if (jsonBlob.Success)
        {
            try
            {
                var cfg = JObject.Parse(jsonBlob.Groups[1].Value);
                foreach (var attr in cfg["attributes"]?.Children() ?? Enumerable.Empty<JToken>())
                {
                    foreach (var opt in attr.Children())
                    {
                        var label = opt["label"]?.ToString();
                        var products = opt["products"] as JArray;
                        if (string.IsNullOrEmpty(label) || products is null) continue;
                        if (!sizes.Contains(label!)) sizes.Add(label!);
                        if (wanted is null || string.Equals(label, wanted, StringComparison.OrdinalIgnoreCase))
                            chosenSku = products.FirstOrDefault()?.ToString();
                        if (wanted is not null && chosenSku is not null) break;
                    }
                }
            }
            catch (Exception)
            {
                // fall through to regex
            }
        }

        if (chosenSku is null)
        {
            var m = Regex.Match(body, @"""sku""\s*:\s*""([^""]+)""");
            chosenSku = m.Success ? m.Groups[1].Value : null;
        }

        if (chosenSku is null) return Task.FromResult(StepOutcome.Fail("magento: no sku"));

        c.Session.VariantId = chosenSku;
        c.Session.VariantTitle = wanted;
        c.Session.Vars["sizes"] = string.Join('|', sizes);
        return Task.FromResult(StepOutcome.Success());
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        var outOfStock = body.Contains("out of stock", StringComparison.OrdinalIgnoreCase) ||
                         body.Contains("soldout", StringComparison.OrdinalIgnoreCase);
        c.Session.Vars["available"] = outOfStock ? "false" : "true";
        return Task.FromResult(StepOutcome.Success());
    }

    public override async Task<StepOutcome> CreateCartAsync(FlowContext c, CancellationToken ct)
    {
        var res = await PostJsonAsync(c, $"{ApiOrigin(c)}/rest/V1/guest-carts",
            "{}", "magento-cart-create", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("magento cart create failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"magento cart HTTP {res.StatusCode}", retryable: true);

        c.Session.CartId = res.Body.Trim('"', '\r', '\n', ' ');
        return string.IsNullOrEmpty(c.Session.CartId)
            ? StepOutcome.Fail("magento: no cart mask")
            : StepOutcome.Success();
    }

    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.VariantId)) return StepOutcome.Fail("magento: no sku");
        if (string.IsNullOrEmpty(c.Session.CartId)) c.Session.CartId = Guid.NewGuid().ToString("N");

        var body = new JObject
        {
            ["cartItem"] = new JObject
            {
                ["sku"] = c.Session.VariantId,
                ["qty"] = c.Session.Quantity,
                ["quote_id"] = c.Session.CartId,
            },
        };

        var res = await PostJsonAsync(c,
            $"{ApiOrigin(c)}/rest/V1/guest-carts/{c.Session.CartId}/items",
            body.ToString(Newtonsoft.Json.Formatting.None), "magento-cart-add", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("magento add to cart failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"magento cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// Magento 2 exposes a dedicated basket for EU storefronts. It behaves like the guest
    /// cart but keeps its own mask, so the flow tracks both ids.
    /// </summary>
    public override async Task<StepOutcome> CreateBasketAsync(FlowContext c,
        CancellationToken ct)
    {
        var res = await PostJsonAsync(c, ApiOrigin(c) + "/rest/V2/carts/mine",
            "{}", "magento-basket-create", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("magento basket create failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"magento basket HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["basketId"] = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"id\"\\s*:\\s*\"?([A-Za-z0-9\\-]+)\"?").Groups[1].Value;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetBasketAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, ApiOrigin(c) + "/rest/V1/carts/mine", "magento-basket-get", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("magento basket fetch failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"magento basket HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["basket"] = res.Body;
        var root = Newtonsoft.Json.Linq.JObject.Parse(res.Body);
        if (root["items"] is not Newtonsoft.Json.Linq.JArray { Count: > 0 })
            return StepOutcome.Fail("magento: basket empty");
        return StepOutcome.Success();
    }


    /// <summary>
    /// Magento 2's checkout is a single-page app whose data comes from the REST totals
    /// endpoint. Fetching the page alone yields an empty shell, so both are pulled — the page
    /// for the CSRF/session it establishes, the totals for anything worth reading.
    /// </summary>
    public override async Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct)
    {
        var page = await GetAsync(c, Origin(c.Url) + "/checkout/#payment",
            Tag() + "-checkout-page", ct).ConfigureAwait(false);

        if (page is null) return StepOutcome.Fail("magento checkout unreachable", retryable: true);
        if (!page.IsSuccess) return StepOutcome.Fail($"magento checkout HTTP {page.StatusCode}", retryable: true);

        c.Session.CheckoutUrl = page.Url.ToString();
        c.Session.Vars["checkoutPage"] = page.Body;

        var totals = await GetAsync(c, ApiOrigin(c) + "/rest/V1/carts/mine/totals",  // inferred: no image evidence (R294)
            Tag() + "-checkout-totals", ct).ConfigureAwait(false);

        if (totals is { IsSuccess: true })
        {
            c.Session.Vars["checkout"] = totals.Body;

            var grand = System.Text.RegularExpressions.Regex
                .Match(totals.Body, "\"grand_total\"\\s*:\\s*\"?(\\d+(?:\\.\\d+)?)\"?")
                .Groups[1].Value;
            if (!string.IsNullOrEmpty(grand)) c.Session.Vars["total"] = grand;

            var currency = System.Text.RegularExpressions.Regex
                .Match(totals.Body, "\"quote_currency_code\"\\s*:\\s*\"([^\"]+)\"")
                .Groups[1].Value;
            if (!string.IsNullOrEmpty(currency)) c.Session.Vars["currency"] = currency;

            // An empty quote means the cart did not survive, which is worth failing on now
            // rather than at the payment step.
            var items = System.Text.RegularExpressions.Regex
                .Matches(totals.Body, "\"item_id\"").Count;
            c.Session.Vars["checkoutItems"] = items.ToString();
            if (items == 0) return StepOutcome.Fail("magento: checkout quote is empty", retryable: true);
        }

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, $"{ApiOrigin(c)}/rest/V1/guest-carts/{c.Session.CartId}",
            "magento-cart-get", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("magento cart fetch failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"magento cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        var root = JObject.Parse(res.Body);
        if (root["items"] is not JArray { Count: > 0 }) return StepOutcome.Fail("magento: cart empty");
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> EditLineAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Quantity <= 1) return StepOutcome.Success();

        var body = new JObject
        {
            ["cartItem"] = new JObject { ["qty"] = c.Session.Quantity, ["quote_id"] = c.Session.CartId },
        };

        var res = await PostJsonAsync(c,
            $"{ApiOrigin(c)}/rest/V1/guest-carts/{c.Session.CartId}/items",
            body.ToString(Newtonsoft.Json.Formatting.None), "magento-cart-edit", ct).ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail($"magento edit HTTP {res?.StatusCode}", retryable: true);
    }

    public override Task<StepOutcome> InitiateCheckoutAsync(FlowContext c, CancellationToken ct)
    {
        c.Session.CheckoutUrl = $"{ApiOrigin(c)}/rest/V1/guest-carts/{c.Session.CartId}";
        c.Session.CheckoutToken = c.Session.CartId;
        return Task.FromResult(StepOutcome.Success());
    }

    public override async Task<StepOutcome> SubmitEmailAsync(FlowContext c, CancellationToken ct)
    {
        var email = c.ProfileData?.Email ?? c.Account?.Email;
        if (string.IsNullOrEmpty(email)) return StepOutcome.Fail("magento: no email");

        var body = new JObject
        {
            ["addressInformation"] = new JObject
            {
                ["shippingAddress"] = new JObject { ["email"] = email },
                ["billingAddress"] = new JObject { ["email"] = email },
                ["shipping_method_code"] = "flatrate",
                ["shipping_carrier_code"] = "flatrate",
            },
        };

        var res = await PostJsonAsync(c,
            $"{ApiOrigin(c)}/rest/V1/guest-carts/{c.Session.CartId}/shipping-information",
            body.ToString(Newtonsoft.Json.Formatting.None), "magento-email", ct).ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail($"magento email HTTP {res?.StatusCode}", retryable: true);
    }

    public override async Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct)
    {
        var ship = c.Shipping ?? FootsitesFlow.AddressFromProfile(c);
        if (ship is null) return StepOutcome.Fail("magento: no shipping address");

        var address = new JObject
        {
            ["region"] = ship.State,
            ["region_id"] = 0,
            ["country_id"] = ship.Country,
            ["street"] = new JArray(ship.Address1 ?? string.Empty, ship.Address2 ?? string.Empty),
            ["postcode"] = ship.ZipCode,
            ["city"] = ship.City,
            ["firstname"] = ship.FirstName,
            ["lastname"] = ship.LastName,
            ["email"] = c.ProfileData?.Email ?? c.Account?.Email,
            ["telephone"] = c.ProfileData?.Phone,
        };

        var body = new JObject
        {
            ["addressInformation"] = new JObject
            {
                ["shipping_address"] = address,
                ["billing_address"] = address.DeepClone(),
                ["shipping_carrier_code"] = "flatrate",
                ["shipping_method_code"] = "flatrate",
            },
        };

        var res = await PostJsonAsync(c,
            $"{ApiOrigin(c)}/rest/V1/guest-carts/{c.Session.CartId}/shipping-information",
            body.ToString(Newtonsoft.Json.Formatting.None), "magento-shipping", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("magento shipping failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"magento shipping HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["shipping"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetShippingRatesAsync(FlowContext c, CancellationToken ct)
    {
        var body = new JObject
        {
            ["address"] = new JObject
            {
                ["country_id"] = c.ProfileData?.Country ?? "GB",
                ["postcode"] = c.ProfileData?.Zip,
            },
        };

        var res = await PostJsonAsync(c,
            $"{ApiOrigin(c)}/rest/V1/guest-carts/{c.Session.CartId}/estimate-shipping-methods",
            body.ToString(Newtonsoft.Json.Formatting.None), "magento-rates", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("magento rates failed", retryable: true);
        c.Session.Vars["rates"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return StepOutcome.Fail("magento: no card");

        var body = new JObject
        {
            ["paymentMethod"] = new JObject
            {
                ["method"] = "checkmo",
                ["additional_data"] = new JObject
                {
                    ["cc_number"] = card.Number,
                    ["cc_exp_month"] = card.Month,
                    ["cc_exp_year"] = card.Year,
                    ["cc_cid"] = card.Cvv,
                },
            },
            ["billingAddress"] = new JObject
            {
                ["email"] = c.ProfileData?.Email,
                ["countryId"] = c.ProfileData?.Country,
                ["postcode"] = c.ProfileData?.Zip,
            },
        };

        var res = await PostJsonAsync(c,
            $"{ApiOrigin(c)}/rest/V1/guest-carts/{c.Session.CartId}/payment-information",
            body.ToString(Newtonsoft.Json.Formatting.None), "magento-payment", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("magento payment failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"magento payment HTTP {res.StatusCode}", retryable: true);

        c.Session.OrderNumber = res.Body.Trim('"', '\r', '\n', ' ');
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        if (!string.IsNullOrEmpty(c.Session.OrderNumber)) return StepOutcome.Success();

        var res = await PostJsonAsync(c,
            $"{ApiOrigin(c)}/rest/V1/guest-carts/{c.Session.CartId}/order",
            "{}", "magento-order", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("magento order failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"magento order HTTP {res.StatusCode}", retryable: true);

        c.Session.OrderNumber = res.Body.Trim('"', '\r', '\n', ' ');
        return StepOutcome.Success();
    }
}

/// <summary>
/// END. — the running 5.18.32 build lists this under <c>Type = Shopify</c> (Store name "END."),
/// not under Magento. The replica used to model it as Magento with a split api2 endpoint,
/// which is what the site used years ago; the GUI is the newer truth.
/// </summary>
public sealed class EndClothingFlow : ShopifyFlow
{
    public EndClothingFlow() : base("endclothing", "END.",
        new[] { "endclothing.com", "endclothing.co.uk" })
    {
    }
}

/// <summary>Offspring — Magento 1 style, no guest-cart REST; falls back to form checkout.</summary>
public sealed class OffspringFlow : MagentoFlow
{
    public OffspringFlow() : base("offspring", "Offspring",
        new[] { "offspring.co.uk", "offspring.com" })
    {
    }
}

/// <summary>
/// Footpatrol — Shopify, part of the JD Sports group.
///
/// Registered against MagentoFlow until a live probe showed otherwise: the storefront carries
/// cdn.shopify.com / shopify-section / Shopify.theme, and /cart.js answers
/// <c>{"token":"d1bee53c…","note":null,"attributes":{…}}</c> — a Shopify cart object.
/// No Magento REST surface answered at all (/rest/V1/store/storeConfigs is 404).
///
/// <para>
/// The .com host comes first because .co.uk no longer resolves: a reachability sweep found
/// <c>https://footpatrol.co.uk/</c> failing DNS while <c>https://www.footpatrol.com/</c> answers
/// 200 with 892 KB. Domains.First() is what the sweep and the router both use, so putting a
/// dead host first made a working module report as unreachable.
/// </para>
/// </summary>
public sealed class FootpatrolFlow : ShopifyFlow
{
    public FootpatrolFlow() : base("footpatrol", "Footpatrol",
        new[] { "footpatrol.com", "footpatrol.co.uk" })
    {
    }
}

/// <summary>
/// Size? — Shopify, JD Sports group.
///
/// Same story as Footpatrol: /cart.js returns a Shopify cart token
/// (<c>{"token":"50e1612e…"}</c>) and the page carries Shopify theme markers. The Magento
/// registration was wrong.
///
/// The queue gate is kept: Size? still puts hot launches behind a waiting room, and the
/// storefront URL changes while queued regardless of which platform is underneath.
/// </summary>
public sealed class SizeFlow : ShopifyFlow
{
    public SizeFlow() : base("size", "Size?", new[] { "size.co.uk", "sizeofficial.com" })
    {
    }

    public override async Task<StepOutcome> PollQueueAsync(FlowContext c, CancellationToken ct)
    {
        for (var i = 0; i < 8; i++)
        {
            ct.ThrowIfCancellationRequested();
            var res = await GetAsync(c, Origin(c.Url) + "/", "size-queue", ct).ConfigureAwait(false);
            if (res is null) return StepOutcome.Fail("size queue unreachable", retryable: true);

            if (res.IsSuccess && !res.Url.ToString().Contains("queue", StringComparison.OrdinalIgnoreCase))
            {
                c.Session.Vars["queue"] = "passed";
                return StepOutcome.Success();
            }
            await Task.Delay(TimeSpan.FromMilliseconds(250), ct).ConfigureAwait(false);
        }
        return StepOutcome.Fail("size: still queued", retryable: true);
    }
}

/// <summary>
/// JD Sports — Akamai + queue-it in front, Magento behind. Login is mandatory for
/// checkout, so the flow runs the account steps before the cart steps.
/// </summary>
public sealed class JdSportsFlow : MagentoFlow
{
    public JdSportsFlow() : base("jdsports", "JD Sports",
        new[] { "jdsports.co.uk", "jdsports.com", "jdsports.ie", "jdsports.fr", "jdsports.nl" })
    {
    }

    public override bool RequiresAccount => true;

    public override async Task<StepOutcome> LoginAsync(FlowContext c, CancellationToken ct)
    {
        var account = c.Account;
        if (account is null || string.IsNullOrEmpty(account.Email))
            return StepOutcome.Fail("jdsports: no account configured");

        var form = new Dictionary<string, string>
        {
            ["j_username"] = account.Email,
            ["j_password"] = account.Password ?? string.Empty,
            ["CSRFToken"] = c.Session.CsrfToken ?? string.Empty,
        };

        var res = await PostFormAsync(c, Origin(c.Url) + "/account/login",
            form, "jdsports-login", ct).ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail($"jdsports login HTTP {res?.StatusCode}");
    }

    public override async Task<StepOutcome> CheckLoginAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/account", "jdsports-account", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jdsports account unreachable", retryable: true);

        return res.Url.ToString().Contains("login", StringComparison.OrdinalIgnoreCase)
            ? StepOutcome.Fail("jdsports: not logged in")
            : StepOutcome.Success();
    }

    public override async Task<StepOutcome> SendTwoFactorAsync(FlowContext c, CancellationToken ct)
    {
        var code = c.Session.Vars.TryGetValue("otp", out var otp) ? otp : null;
        if (string.IsNullOrEmpty(code)) return StepOutcome.Fail("jdsports: no OTP available");

        var res = await PostFormAsync(c, Origin(c.Url) + "/account/verify",  // inferred: no image evidence (R294)
            new Dictionary<string, string> { ["code"] = code! }, "jdsports-2fa", ct)
            .ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail("jdsports: 2FA rejected");
    }
}

/// <summary>
/// John Lewis — separate checkout host, no REST guest cart. The flow rides the
/// <c>checkout.johnlewis.com</c> basket endpoints.
/// </summary>
public sealed class JohnLewisFlow : StoreFlow
{
    public override string Id => "johnlewis";
    public override string Name => "John Lewis";
    public override IReadOnlyList<string> Domains => new[] { "johnlewis.com", "checkout.johnlewis.com" };

    /// <summary>
    /// John Lewis's own order — the image's nineteen steps, from one adjacent run of compiler ordinals (R112).
    ///
    /// <para>
    /// R869. This flow has more steps than its twelve BFF endpoints have names, which R118 recorded as a reading in
    /// itself: the step list is the client's phases while the endpoints are the server's resources, so
    /// <c>v2/sessions/web/handover</c> serves both WebHandOver and SessionHandover. Declaring the sequence keeps that
    /// distinction where it belongs — in the order the client runs, not in how many URLs exist.
    /// </para>
    /// </summary>
    public override IReadOnlyList<string> StepSequence => StoreFlowSteps.JohnLewis.Names;

    /// <summary>
    /// John Lewis runs its own checkout under /checkout/registration rather than Magento's
    /// SPA, and the order summary rides along in the same response.
    /// </summary>
    public override async Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, CheckoutHost + "/checkout/registration",
            Tag() + "-jl-checkout", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("jl checkout unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"jl checkout HTTP {res.StatusCode}", retryable: true);

        c.Session.CheckoutUrl = res.Url.ToString();
        c.Session.Vars["checkout"] = res.Body;

        var total = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"orderTotal\"\\s*:\\s*\"?([\\d.]+)\"?").Groups[1].Value;
        if (!string.IsNullOrEmpty(total)) c.Session.Vars["total"] = total;

        var orderId = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"orderId\"\\s*:\\s*\"?([A-Za-z0-9\\-]+)\"?").Groups[1].Value;
        if (!string.IsNullOrEmpty(orderId)) c.Session.OrderId = orderId;

        return StepOutcome.Success();
    }


    private const string CheckoutHost = "https://checkout.johnlewis.com";

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/", "jl-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jl home unreachable", retryable: true);
        c.Session.Vars["home"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "jl-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jl product unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"jl product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;
        c.Session.Vars["product"] = ExtractProductName(res.Body);
        c.Session.Vars["price"] = ExtractPrice(res.Body);
        return StepOutcome.Success();
    }

    /// <summary>
    /// The product name. <c>&lt;title&gt;</c> is unusable here: on John Lewis it belongs to a
    /// footer widget and reads "Store Finder". The <c>&lt;h1&gt;</c> carries the real title.
    /// </summary>
    public static string ExtractProductName(string body)
    {
        var m = Regex.Match(body, @"<h1[^>]*>([^<]+)<");
        return Regex.Replace(m.Groups[1].Value, @"\s+", " ").Trim();
    }

    /// <summary>
    /// The product price.
    ///
    /// <c>£([\d.,]+)</c> over the whole document is wrong: the meta description contains
    /// "Free Delivery on orders over £50.", so the first match is a delivery threshold that
    /// looks exactly like a price — verified against a live page where the real figure was
    /// £12.75. Structured data does not help either; the ld+json blocks carry name and brand
    /// but no price.
    ///
    /// So: prefer an element the site itself marks as a price, then a declared meta price, and
    /// otherwise return nothing rather than a plausible wrong number.
    /// </summary>
    public static string ExtractPrice(string body)
    {
        var marked = Regex.Match(body,
            "data-test-id=\"[^\"]*price[^\"]*\"[^>]*>\\s*£?\\s*([\\d,]+\\.\\d{2})");
        if (marked.Success) return Clean(marked.Groups[1].Value);

        var byClass = Regex.Match(body,
            "class=\"[^\"]*\\bprice\\b[^\"]*\"[^>]*>\\s*£?\\s*([\\d,]+\\.\\d{2})");
        if (byClass.Success) return Clean(byClass.Groups[1].Value);

        var declared = Regex.Match(body,
            "(?:product:price:amount|og:price:amount)\"\\s+content=\"([\\d.]+)\"");
        if (declared.Success) return Clean(declared.Groups[1].Value);

        return string.Empty;
    }

    private static string Clean(string raw) => raw.Replace(",", string.Empty).Trim();

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        var sku = Regex.Match(body, @"""productId""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (string.IsNullOrEmpty(sku))
            sku = Regex.Match(body, @"""sku""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (string.IsNullOrEmpty(sku)) return Task.FromResult(StepOutcome.Fail("jl: no product id"));

        var sizes = Regex.Matches(body, @"""size""\s*:\s*""([^""]+)""")
            .Select(m => m.Groups[1].Value).Distinct().ToList();

        c.Session.VariantId = sku;
        c.Session.Vars["sizes"] = string.Join('|', sizes);
        return Task.FromResult(StepOutcome.Success());
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        var unavailable = body.Contains("outOfStock", StringComparison.OrdinalIgnoreCase) ||
                          body.Contains("Out of stock", StringComparison.OrdinalIgnoreCase);
        c.Session.Vars["available"] = unavailable ? "false" : "true";
        return Task.FromResult(StepOutcome.Success());
    }

    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        var payload = new JObject
        {
            ["skuId"] = c.Session.VariantId,
            ["quantity"] = c.Session.Quantity,
        };

        var res = await PostJsonAsync(c, $"{CheckoutHost}/api/basket/items",
            payload.ToString(Newtonsoft.Json.Formatting.None), "jl-basket-add", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("jl basket add failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"jl basket HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["basket"] = res.Body;
        c.Session.CartId = Regex.Match(res.Body, @"""basketId""\s*:\s*""([^""]+)""").Groups[1].Value;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, $"{CheckoutHost}/api/basket", "jl-basket-get", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jl basket fetch failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"jl basket HTTP {res.StatusCode}", retryable: true);
        c.Session.Vars["basket"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> InitiateCheckoutAsync(FlowContext c, CancellationToken ct)
    {
        c.Session.CheckoutUrl = $"{CheckoutHost}/checkout";
        var res = await GetAsync(c, c.Session.CheckoutUrl!, "jl-checkout", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jl checkout unreachable", retryable: true);
        c.Session.Vars["checkout"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// <c>SubmitShipping</c> — the PUT to <c>v4/orderforms/deliveries/delivery-address</c> that carries
    /// the shipping address itself.
    ///
    /// <para>
    /// R1136 reassigned this step. R1133 pointed both of the image's delivery step names at the
    /// body-less <c>deliveries</c> PUT, which left <c>delivery-address</c> named by no step at all —
    /// and there are two names and two endpoints, one carrying an address and one carrying nothing.
    /// The pairing here is <b>inferred</b> from that 1:1 shape and the two names (submit the shipping
    /// address; create the delivery), not from request capture, so it is recorded as an inference.
    /// </para>
    ///
    /// <para>
    /// The body is read off <c>sub_140A43A80</c> (R1134): eleven keys in three levels, with
    /// <c>addressee</c> wrapping the names, <c>address</c> wrapping the four street fields and
    /// <c>contact</c> wrapping the phone number, all under a single root key <c>addressDetails</c>.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct)
    {
        var ship = c.Shipping ?? FootsitesFlow.AddressFromProfile(c);
        if (ship is null) return StepOutcome.Fail("jl: no shipping address");

        string V(string key, string? fallback) =>
            c.Session.Vars.TryGetValue(key, out var v) && !string.IsNullOrEmpty(v)
                ? v!
                : (fallback ?? string.Empty);

        var body = new JObject
        {
            ["addressDetails"] = new JObject
            {
                ["addressee"] = new JObject
                {
                    ["firstName"] = V("jl.firstName", ship.FirstName),
                    ["lastName"] = V("jl.lastName", ship.LastName),
                },
                ["address"] = new JObject
                {
                    ["addressLine1"] = V("jl.addressLine1", ship.Address1),
                    ["townOrCity"] = V("jl.townOrCity", ship.City),
                    ["postcode"] = V("jl.postcode", ship.ZipCode),
                    ["countryCode"] = V("jl.countryCode", ship.Country),
                },
                ["contact"] = new JObject
                {
                    ["phoneNumber"] = V("jl.phoneNumber", c.ProfileData?.Phone),
                },
            },
        }.ToString(Newtonsoft.Json.Formatting.None);

        var url = c.Session.Vars.TryGetValue("jl.deliveryAddressUrl", out var over) &&
                  !string.IsNullOrEmpty(over)
            ? over.TrimEnd('/')
            : RetailApiFamilies.JohnLewisBff.DeliveryAddressV4;

        var res = await SendJsonAsync(c, HttpMethod.Put, url, body, "jl-delivery-address", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jl delivery address unreachable", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail($"jl delivery address HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["jl.deliveryAddressBody"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetShippingRatesAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, $"{CheckoutHost}/api/delivery/options", "jl-rates", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jl rates failed", retryable: true);
        c.Session.Vars["rates"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return StepOutcome.Fail("jl: no card");

        var payload = new JObject
        {
            ["card"] = new JObject
            {
                ["number"] = card.Number,
                ["expiryMonth"] = card.Month,
                ["expiryYear"] = card.Year,
                ["cv2"] = card.Cvv,
                ["nameOnCard"] = card.Name ?? c.ProfileData?.Display,
            },
        };

        var res = await PostJsonAsync(c, $"{CheckoutHost}/api/payment",
            payload.ToString(Newtonsoft.Json.Formatting.None), "jl-payment", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("jl payment failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"jl payment HTTP {res.StatusCode}", retryable: true);

        c.Session.PaymentToken = Regex.Match(res.Body, @"""token""\s*:\s*""([^""]+)""").Groups[1].Value;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        var res = await PostJsonAsync(c, $"{CheckoutHost}/api/order", "{}", "jl-order", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("jl order failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"jl order HTTP {res.StatusCode}", retryable: true);

        var root = JObject.Parse(res.Body);
        c.Session.OrderNumber = root["orderNumber"]?.ToString() ?? root["orderId"]?.ToString();
        return string.IsNullOrEmpty(c.Session.OrderNumber)
            ? StepOutcome.Fail("jl: order response had no number")
            : StepOutcome.Success();
    }

    /// <summary>
    /// <c>SubmitOrderStripe</c> — the JL flow's Stripe payment submit, decoded R1089 from
    /// <c>sub_140a42bc0</c> (the five-state payments machine that PUTs the BFF's
    /// <c>v2/orderforms/payments</c>, 0x14705d744).
    ///
    /// <para>
    /// The request is a PUT carrying two query parameters the machine assembles from its payment
    /// context: <c>methodId</c> (0x1470c29a0, the context's field 23) and
    /// <c>setupFutureUsage</c> (0x147159a48 — the same parameter name PopMart's desk pay sends,
    /// R1087). The response path then gates on the selected method reading
    /// <b>CREDITCARD</b> before its four-request continuation runs
    /// (<c>sub_140a371e0</c> → <c>sub_140a370f0</c> → <c>sub_140a37140</c> → <c>sub_140a37190</c>,
    /// trampolines into async machines whose bodies are the next probe) — which is the
    /// <c>HandleRequiresAction</c> / <c>GetStripePaymentIntent</c> pair the step map already
    /// records as Stripe-direct.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> SubmitOrderStripeAsync(FlowContext c, CancellationToken ct)
    {
        // The payment context's method id — the decoded machine reads its field 23.
        var methodId = c.Session.Vars.GetValueOrDefault("jl.methodId")
                       ?? c.Session.Vars.GetValueOrDefault("paymentMethodId");
        if (string.IsNullOrEmpty(methodId))
            return StepOutcome.Fail("jl: no payment method id to submit with", retryable: true);

        // The frozen BFF host, with the standard session seam (the checkStockUrl convention)
        // so a configured endpoint can front it.
        var paymentsBase = c.Session.Vars.TryGetValue("jl.paymentsUrl", out var paymentsOverride) &&
                           !string.IsNullOrEmpty(paymentsOverride)
            ? paymentsOverride.TrimEnd('/')
            : CheckoutHost + "/bff/v2/orderforms/payments";
        var url = paymentsBase + "?methodId=" +
                  Uri.EscapeDataString(methodId) + "&setupFutureUsage=false";

        var res = await SendJsonAsync(c, HttpMethod.Put, url, "{}", "jl-payments-stripe", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jl payments unreachable", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail($"jl payments HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["jl.paymentsBody"] = res.Body;

        // The machine's CREDITCARD gate: the method the context selected decides whether the
        // four-request Stripe-direct continuation runs. When it does, its requests are the
        // flow's HandleRequiresAction / GetStripePaymentIntent steps — already declared in the
        // step sequence, and not yet decoded from their trampolines (the named continuation).
        var selected = c.Session.Vars.GetValueOrDefault("jl.paymentMethod");
        if (string.Equals(selected, "CREDITCARD", StringComparison.OrdinalIgnoreCase) &&
            string.IsNullOrEmpty(c.Card?.Number))
            return StepOutcome.Fail("jl: credit card method selected but no card loaded");

        return StepOutcome.Success();
    }

    /// <summary>John Lewis's frozen Stripe account id (0x146f6d140) — the integration's own constant.</summary>
    public const string StripeAccount = "acct_1S0JRiIiwyy5Cf6X";

    /// <summary>
    /// <c>GetPaymentPage</c> — reads John Lewis's payment page before the method is submitted.
    ///
    /// <para>
    /// R1127: the step map pairs this step with <c>v2/orderforms/payment-page</c>, and the image calls
    /// that URL with <b>two</b> verbs — a GET at site 0x140a3ff44 (verb slot 0x1408b61e0, called at
    /// 0x140a3ff75) and a PUT at 0x140a4003b (slot 0x1408b6310, called at 0x140a4006f). The read is
    /// the one this step is named for, so the GET is what runs here; the base class was answering on
    /// <c>Origin + "/payments"</c>, which is not a John Lewis URL at all.
    /// </para>
    ///
    /// <para>
    /// The answer is kept under both <c>jl.paymentPageBody</c> (this flow's key) and the base
    /// class's <c>paymentPage</c>, so a later step reading either spelling still finds it.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> GetPaymentPageAsync(FlowContext c, CancellationToken ct)
    {
        var url = c.Session.Vars.TryGetValue("jl.paymentPageUrl", out var over) &&
                  !string.IsNullOrEmpty(over)
            ? over.TrimEnd('/')
            : RetailApiFamilies.JohnLewisBff.PaymentPageV2;

        var res = await GetAsync(c, url, "jl-payment-page", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jl payment page unreachable", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail($"jl payment page HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["jl.paymentPageBody"] = res.Body;
        c.Session.Vars["paymentPage"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// <c>SubmitBillingAddress</c> — the POST to <c>v1/orderforms/payments/billing-address</c>.
    ///
    /// <para>
    /// R1128: the body's shape is <b>read off the machine</b>, not assumed. In <c>sub_140A424B0</c> the
    /// key order is: a nested object built with <c>firstName</c> + <c>lastName</c> is stored under
    /// <c>addressee</c>; a second nested object built with <c>addressLine1</c> + <c>townOrCity</c> +
    /// <c>postcode</c> + <c>countryCode</c> is stored under <c>address</c>; then <c>phoneNumber</c> goes
    /// on the root. So the request is
    /// <c>{"addressee":{firstName,lastName},"address":{addressLine1,townOrCity,postcode,countryCode},"phoneNumber":…}</c>
    /// — <b>not</b> a flat object, which is what the key list alone would suggest.
    /// </para>
    ///
    /// <para>
    /// The values come from the task's own address (the image reads its profile object; the fields that
    /// map one-to-one are taken from the address, the three with no counterpart there come from session
    /// vars so the caller decides). The step still records the base class's four session keys.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> SubmitBillingAddressAsync(FlowContext c, CancellationToken ct)
    {
        var bill = c.Billing ?? c.Shipping;
        if (bill is null) return StepOutcome.Fail("jl: no billing address to submit");

        string V(string key, string? fallback) =>
            c.Session.Vars.TryGetValue(key, out var v) && !string.IsNullOrEmpty(v)
                ? v!
                : (fallback ?? string.Empty);

        var addressee = new JObject
        {
            ["firstName"] = V("jl.firstName", null),
            ["lastName"] = V("jl.lastName", null),
        };
        var address = new JObject
        {
            ["addressLine1"] = V("jl.addressLine1", bill.Address1),
            ["townOrCity"] = V("jl.townOrCity", bill.City),
            ["postcode"] = V("jl.postcode", bill.ZipCode),
            ["countryCode"] = V("jl.countryCode", bill.Country),
        };
        var body = new JObject
        {
            ["addressee"] = addressee,
            ["address"] = address,
            ["phoneNumber"] = V("jl.phoneNumber", null),
        }.ToString(Newtonsoft.Json.Formatting.None);

        var url = c.Session.Vars.TryGetValue("jl.billingAddressUrl", out var over) &&
                  !string.IsNullOrEmpty(over)
            ? over.TrimEnd('/')
            : RetailApiFamilies.JohnLewisBff.BillingAddressV1;

        var res = await SendJsonAsync(c, HttpMethod.Post, url, body, "jl-billing-address", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jl billing address unreachable", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail($"jl billing address HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["jl.billingAddressBody"] = res.Body;
        c.Session.Vars["billing.address1"] = bill.Address1 ?? string.Empty;
        c.Session.Vars["billing.city"] = bill.City ?? string.Empty;
        c.Session.Vars["billing.zip"] = bill.ZipCode ?? string.Empty;
        c.Session.Vars["billing.country"] = bill.Country ?? string.Empty;
        return StepOutcome.Success();
    }

    /// <summary>
    /// <c>WebHandOver</c> / <c>SessionHandover</c> — the PUT to <c>v2/sessions/web/handover</c> that
    /// hands the basket to the checkout backend. Both of the image's step names (ordinals 23 and 24)
    /// hit this one endpoint, which is why one core serves both.
    ///
    /// <para>
    /// R1130: the body's <b>shape</b> is read off <c>sub_140A410E0</c>. The three <c>time*</c> keys are
    /// set on the inner object built from <c>unk_144DFD730</c> (variable <c>v20</c>), and then
    /// <c>timestamps</c> is set to that very object; <c>express</c>, <c>basketId</c> and
    /// <c>discountsInBasketUIEnabled</c> are set on the root. So:
    /// <c>{express, basketId, discountsInBasketUIEnabled, timestamps:{timeContinueToCheckoutClicked,
    /// timeToCheckoutSpinner, timeToReactLoaded}}</c>.
    /// </para>
    ///
    /// <para>
    /// The <b>types</b> are not in that evidence: the machine builds <c>basketId</c> through the same
    /// token helper the billing address uses for its strings, while the three stamps are computed
    /// values, so this sends <c>basketId</c> as a string, the two flags as booleans and the three
    /// stamps as numbers. That reading is an inference from how the values are produced, and it is
    /// recorded here rather than buried, because a type that is wrong fails at the server.
    /// </para>
    /// </summary>
    public override Task<StepOutcome> WebHandOverAsync(FlowContext c, CancellationToken ct)
        => HandOverAsync(c, ct);

    /// <inheritdoc/>
    public override Task<StepOutcome> SessionHandoverAsync(FlowContext c, CancellationToken ct)
        => HandOverAsync(c, ct);

    private async Task<StepOutcome> HandOverAsync(FlowContext c, CancellationToken ct)
    {
        string V(string key, string fallback) =>
            c.Session.Vars.TryGetValue(key, out var v) && !string.IsNullOrEmpty(v) ? v! : fallback;

        static long Ticks(string raw) =>
            long.TryParse(raw, out var n) ? n : 0L;

        static bool Flag(string raw) =>
            string.Equals(raw, "true", StringComparison.OrdinalIgnoreCase);

        var body = new JObject
        {
            ["express"] = Flag(V("jl.express", "false")),
            ["basketId"] = V("jl.basketId", string.Empty),
            ["discountsInBasketUIEnabled"] = Flag(V("jl.discountsInBasketUIEnabled", "false")),
            ["timestamps"] = new JObject
            {
                ["timeContinueToCheckoutClicked"] = Ticks(V("jl.timeContinueToCheckoutClicked", "0")),
                ["timeToCheckoutSpinner"] = Ticks(V("jl.timeToCheckoutSpinner", "0")),
                ["timeToReactLoaded"] = Ticks(V("jl.timeToReactLoaded", "0")),
            },
        }.ToString(Newtonsoft.Json.Formatting.None);

        var url = c.Session.Vars.TryGetValue("jl.handoverUrl", out var over) && !string.IsNullOrEmpty(over)
            ? over.TrimEnd('/')
            : RetailApiFamilies.JohnLewisBff.SessionHandoverV2;

        var res = await SendJsonAsync(c, HttpMethod.Put, url, body, "jl-handover", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jl handover unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"jl handover HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["jl.handoverBody"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// <c>GuestCallback</c> — the PUT to <c>v4/callback/guest</c> whose body is a single
    /// <c>email</c> key.
    ///
    /// <para>
    /// R1131: read off <c>sub_140A407A0</c>. That function touches <b>two</b> URLs, and they are not
    /// interchangeable: <c>…/callback/login/guest?email=</c> (0x14705dcd8) is passed to
    /// <c>sub_141CF6230</c>, while the PUT's URL argument is built from
    /// <c>…/bff/v4/callback/guest</c> (0x14705da88); the body object gets one key, <c>email</c>
    /// (0x14701ac58). So the request is <c>PUT …/bff/v4/callback/guest {"email": …}</c>, and the other
    /// URL belongs to something else in the same function that this step does not perform.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> GuestCallbackAsync(FlowContext c, CancellationToken ct)
    {
        var email = c.Session.Vars.TryGetValue("jl.email", out var own) && !string.IsNullOrEmpty(own)
            ? own!
            : c.Session.Vars.TryGetValue("email", out var shared) ? shared! : string.Empty;
        if (string.IsNullOrEmpty(email))
            return StepOutcome.Fail("jl: no email for the guest callback");

        var body = new JObject { ["email"] = email }.ToString(Newtonsoft.Json.Formatting.None);

        var url = c.Session.Vars.TryGetValue("jl.guestCallbackUrl", out var over) &&
                  !string.IsNullOrEmpty(over)
            ? over.TrimEnd('/')
            : RetailApiFamilies.JohnLewisBff.GuestCallbackV4;

        var res = await SendJsonAsync(c, HttpMethod.Put, url, body, "jl-guest-callback", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jl guest callback unreachable", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail($"jl guest callback HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["jl.guestCallbackBody"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// <c>SubmitShipping</c> / <c>CreateDelivery</c> — the <b>body-less</b> PUT to
    /// <c>v4/orderforms/deliveries</c> that confirms the delivery form the previous steps filled in.
    ///
    /// <para>
    /// R1133: R1129 recorded this function as "no body keys", and that was the right reading of the
    /// wrong thing — it is not that the keys live elsewhere, it is that <b>there is no body</b>. In
    /// <c>sub_140A3F590</c> the verb call is <c>sub_1408B6310(v2, v3, 0, v4)</c>: the third argument,
    /// where every other BFF call passes its body object, is the literal <c>0</c>. The address fields
    /// go to a different endpoint (<c>v4/orderforms/deliveries/delivery-address</c>, also a PUT), which
    /// is what makes this one a confirmation rather than a submission.
    /// </para>
    /// </summary>
    public override Task<StepOutcome> CreateDeliveryAsync(FlowContext c, CancellationToken ct)
        => ConfirmDeliveryFormAsync(c, ct);

    private async Task<StepOutcome> ConfirmDeliveryFormAsync(FlowContext c, CancellationToken ct)
    {
        var url = c.Session.Vars.TryGetValue("jl.deliveriesUrl", out var over) && !string.IsNullOrEmpty(over)
            ? over.TrimEnd('/')
            : RetailApiFamilies.JohnLewisBff.DeliveriesV4;

        // No Content: the machine passes 0 for the body, so sending "{}" would be a different request.
        var options = c.Options("jl-deliveries");
        var res = await c.Http.SendAsync(HttpMethod.Put, url, options, ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jl deliveries unreachable", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail($"jl deliveries HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["jl.deliveriesBody"] = res.Body ?? string.Empty;
        return StepOutcome.Success();
    }

    /// <summary>
    /// <c>DeliveryPage</c> — the <b>body-less</b> PUT to <c>v3/orderforms/delivery-page</c>.
    ///
    /// <para>
    /// R1134: <c>sub_140A3F750</c> references exactly one literal — its own URL (0x14705d960) — and its
    /// verb call is <c>sub_1408B6310(v2, v3, 0, v4)</c> with the literal <c>0</c> where a body would go.
    /// So this step is a touch on the page, not a submission; the address itself travels to
    /// <c>v4/orderforms/deliveries/delivery-address</c>, whose body is evidenced separately (11 keys
    /// under <c>addressDetails</c>) but which has no step name of its own in the image's list.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> DeliveryPageAsync(FlowContext c, CancellationToken ct)
    {
        var url = c.Session.Vars.TryGetValue("jl.deliveryPageUrl", out var over) &&
                  !string.IsNullOrEmpty(over)
            ? over.TrimEnd('/')
            : RetailApiFamilies.JohnLewisBff.DeliveryPageV3;

        var options = c.Options("jl-delivery-page");
        var res = await c.Http.SendAsync(HttpMethod.Put, url, options, ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jl delivery page unreachable", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail($"jl delivery page HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["jl.deliveryPageBody"] = res.Body ?? string.Empty;
        return StepOutcome.Success();
    }

    /// <summary>
    /// <c>SubmitDeliveryMethod</c> — the POST to <c>v3/orderforms/deliveries/details</c> that picks one
    /// fulfilment offer.
    ///
    /// <para>
    /// R1135: the body's shape is read off <c>sub_140A428D0</c> (R1128): <c>deliveryId</c> and an inner
    /// object holding <c>fulfilmentOfferId</c> under <c>fulfilment</c> are built first, that pair goes
    /// into a <b>single-element array</b> (<c>sub_141FD0AA0(v10, &amp;v19)</c> with the count set to 1),
    /// and the array is stored under <c>deliveries</c>. So the request is
    /// <c>{"deliveries":[{"deliveryId":…,"fulfilment":{"fulfilmentOfferId":…}}]}</c> — the array is the
    /// part a flat reading gets wrong.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> SubmitDeliveryMethodAsync(FlowContext c, CancellationToken ct)
    {
        var deliveryId = c.Session.Vars.TryGetValue("jl.deliveryId", out var d) ? d : string.Empty;
        if (string.IsNullOrEmpty(deliveryId))
            return StepOutcome.Fail("jl: no deliveryId to submit a method for");

        var offerId = c.Session.Vars.TryGetValue("jl.fulfilmentOfferId", out var f) ? f : string.Empty;

        var body = new JObject
        {
            ["deliveries"] = new JArray
            {
                new JObject
                {
                    ["deliveryId"] = deliveryId,
                    ["fulfilment"] = new JObject { ["fulfilmentOfferId"] = offerId },
                },
            },
        }.ToString(Newtonsoft.Json.Formatting.None);

        var url = c.Session.Vars.TryGetValue("jl.deliveryDetailsUrl", out var over) &&
                  !string.IsNullOrEmpty(over)
            ? over.TrimEnd('/')
            : RetailApiFamilies.JohnLewisBff.DeliveryDetailsV3;

        var res = await SendJsonAsync(c, HttpMethod.Post, url, body, "jl-delivery-details", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jl delivery details unreachable", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail($"jl delivery details HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["jl.deliveryDetailsBody"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// <c>GetStripePaymentIntent</c> — the intent read, decoded R1090 from <c>sub_140a40a30</c>'s
    /// needle chain: <c>next_action</c> → <c>use_stripe_sdk</c> → <c>type</c>, gated on
    /// <b>stripe_3ds2_fingerprint</b> (0x147165bf0), with <c>three_d_secure_2_source</c>
    /// (0x14716d850) the source the continuation keys on and <c>_secret_</c> (0x146f64778) the
    /// needle the client secret is split out with. The fetch itself rides the same
    /// Stripe-direct surface the step map records — its request body lives behind the
    /// <c>sub_140a37540</c> trampoline and is the named continuation for the next probe.
    /// </summary>
    public override Task<StepOutcome> GetStripePaymentIntentAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.GetValueOrDefault("jl.paymentsBody");
        if (string.IsNullOrEmpty(body))
            return Task.FromResult(StepOutcome.Fail("jl: no payments answer to read the intent from",
                retryable: true));

        JObject root;
        try { root = JObject.Parse(body); }
        catch { return Task.FromResult(StepOutcome.Fail("jl: payments answer was not JSON")); }

        var sdk = root["next_action"]?["use_stripe_sdk"];
        var type = sdk?["type"]?.ToString();
        var source = sdk?["three_d_secure_2_source"]?.ToString();

        if (string.IsNullOrEmpty(source))
        {
            // The machine's own stop line (0x146e4afb8): a payments answer without a 3DS source
            // needs no authentication, and the original says exactly that on its STRIPE channel.
            c.Emit("Process: no 3DS source after GetPaymentIntent - no authentication required",
                "STRIPE");
            return Task.FromResult(StepOutcome.Success());
        }

        c.Session.Vars["jl.stripeSdkType"] = type ?? string.Empty;
        c.Session.Vars["jl.threeDs2Source"] = source;
        // The intent id the process wall names — the payments answer's own id-shaped field.
        c.Session.Vars["jl.stripeIntentId"] =
            root["paymentIntentId"]?.ToString() ?? root["id"]?.ToString() ?? string.Empty;
        // The '_secret_' needle: the sdk block's source string carries the secret after it.
        c.Session.Vars["jl.stripeSecret"] = source.Contains("_secret_")
            ? source[(source.IndexOf("_secret_", StringComparison.Ordinal) + "_secret_".Length)..]
            : string.Empty;

        return Task.FromResult(StepOutcome.Success());
    }

    /// <summary>
    /// <c>HandleRequiresAction</c> — the machine's fingerprint gate: when the sdk block's type is
    /// <b>stripe_3ds2_fingerprint</b> the continuation builder runs with John Lewis's frozen
    /// Stripe account (<c>acct_1S0JRiIiwyy5Cf6X</c>) and the BFF host
    /// (<c>checkout.johnlewis.com</c>, 0x14705d5a8) — <c>sub_141141680</c>'s request is the
    /// named continuation; the gate itself is fully decoded.
    ///
    /// <para>
    /// R1091: the continuation's own process wall is decoded too
    /// (<c>sub_141146510</c>, 295 lines): it emits
    /// <c>Process start: payment_intent={id} merchant={account} source={source}</c>
    /// on the <b>STRIPE</b> channel (0x146e76110) before its request chain runs
    /// (<c>sub_141141870</c> → <c>sub_141141910</c> → <c>sub_1411419b0</c> →
    /// <c>sub_141141a00</c>), closes with <c>Process complete</c> (0x146e4aa00), and its stop
    /// paths have their own lines — <c>stopping after fingerprint (alive=, hasForm=)</c>
    /// (0x146e4b068) and the no-source line the intent read emits.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> HandleRequiresActionAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.Vars.TryGetValue("jl.threeDs2Source", out var source) ||
            string.IsNullOrEmpty(source))
            return StepOutcome.Success();   // nothing to act on

        var type = c.Session.Vars.GetValueOrDefault("jl.stripeSdkType");
        if (!string.Equals(type, "stripe_3ds2_fingerprint", StringComparison.Ordinal))
            return StepOutcome.Success();   // not the fingerprint action

        // The gate passed: the source is staged for the account-keyed continuation, and the
        // account the builder swears by goes out with it — the frozen literal, not a guess.
        c.Session.Vars["jl.stripeAccount"] = StripeAccount;

        // The continuation's own process wall, verbatim — the STRIPE channel's opening line
        // with the intent, the frozen merchant account, and the staged source.
        var intentId = c.Session.Vars.GetValueOrDefault("jl.stripeIntentId");
        c.Emit("Process start: payment_intent=" + intentId + " merchant=" + StripeAccount +
               " source=" + source, "STRIPE");

        // R1092: the chain's first request, decoded from sub_141144fc0 — a GET of the hosted
        // challenge page on Stripe's hooks surface, the five composed segments verbatim:
        // merchant (the frozen account), payment_intent, its client secret, the publishable
        // key, and the source. The answer's return URL is the machine's own report line.
        var secret = c.Session.Vars.GetValueOrDefault("jl.stripeSecret");
        var publishable = c.Session.Vars.GetValueOrDefault("stripe.publishableKey");
        var hooksBase = c.Session.Vars.TryGetValue("stripe.hooksUrl", out var h) &&
                        !string.IsNullOrEmpty(h)
            ? h.TrimEnd('/')
            : "https://hooks.stripe.com";
        var hosted = hooksBase + "/3d_secure_2/hosted?merchant=" + StripeAccount +
                    "&payment_intent=" + Uri.EscapeDataString(intentId ?? string.Empty) +
                    "&payment_intent_client_secret=" + Uri.EscapeDataString(secret) +
                    "&publishable_key=" + Uri.EscapeDataString(publishable ?? string.Empty) +
                    "&source=" + Uri.EscapeDataString(source);

        var res = await GetAsync(c, hosted, "jl-stripe-hosted", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("jl: hosted page unreachable", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail($"jl hosted page HTTP {res.StatusCode}", retryable: true);

        // The machine's report line (0x146d9eb30): the hosted page's return URL.
        var returnUrl = System.Text.RegularExpressions.Regex.Match(
            res.Body, "\"returnUrl\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;
        if (!string.IsNullOrEmpty(returnUrl)) c.Session.Vars["jl.hostedReturnUrl"] = returnUrl;
        c.Emit("GetHostedPage: returnUrl=" + (string.IsNullOrEmpty(returnUrl) ? res.Url.ToString() : returnUrl),
            "STRIPE");

        // R1093: the chain's second request, decoded from sub_1411458f0 — the intent confirm as
        // a GET on the v1 surface with the JL variant's own segments: is_stripe_sdk=true
        // (0x146b28808), the client secret, the publishable key, and the frozen account riding
        // the dedicated _stripe_account segment (0x146a7afd8).
        var apiUrl = c.Session.Vars.TryGetValue("stripe.apiUrl", out var apiOverride) &&
                     !string.IsNullOrEmpty(apiOverride)
            ? apiOverride.TrimEnd('/')
            : "https://api.stripe.com";
        var confirmUrl = apiUrl + "/v1/payment_intents/" + Uri.EscapeDataString(intentId ?? string.Empty) +
                         "?is_stripe_sdk=true" +
                         "&client_secret=" + Uri.EscapeDataString(secret) +
                         "&key=" + Uri.EscapeDataString(publishable ?? string.Empty) +
                         "&_stripe_account=" + StripeAccount;

        var confirm = await GetAsync(c, confirmUrl, "jl-stripe-intent", ct).ConfigureAwait(false);
        if (confirm is null) return StepOutcome.Fail("jl: intent confirm unreachable", retryable: true);
        if (!confirm.IsSuccess)
            return StepOutcome.Fail($"jl intent confirm HTTP {confirm.StatusCode}", retryable: true);

        // R1094: the chain's fingerprint submit, decoded from sub_1411474a0 (477 lines) — a PUT
        // of the 3ds2 authenticate form on the same frozen endpoint R1088's Stripe gateway uses
        // (0x147054e20). The form is the twelve-key browser fingerprint object plus the
        // one_click_authn_device_support family, and here the family is NOT hard-coded: the
        // machine drives it from its has-form flag — hosted and webauthn_eligible are always
        // "true", same_origin_frame / spc_eligible / publickey_credentials_get_allowed follow the
        // flag, and without a form the block also carries fingerprintOutcome=not_supported and
        // frontend_execution. key (0x1470ae940) and _stripe_account (0x146f649d0) close it.
        var hasForm = !string.IsNullOrEmpty(c.Session.Vars.GetValueOrDefault("jl.finalCres"));
        var flag = hasForm ? "true" : "false";

        var browser = new JObject
        {
            ["fingerprintAttempted"] = true,                          // 0x147034f20
            ["fingerprintData"] = null,                               // 0x147034f60
            ["challengeWindowSize"] = "Y",                            // 0x146fc5498 / 0x146f33988
            ["threeDSCompInd"] = "Y",                                 // 0x14716d1e0
            ["browserJavaEnabled"] = false,                           // 0x146f9c698
            ["browserJavascriptEnabled"] = true,                      // 0x146f9c6d8
            ["browserLanguage"] = "en-US",                            // 0x146f9c750 / 0x14701be60
            ["browserColorDepth"] = "24",                             // 0x146f9c110 / 0x146ae23f8
            ["browserScreenHeight"] = "1080",                         // 0x146f9c788 / 0x146ad59e8
            ["browserScreenWidth"] = "1920",                          // 0x146f9c7c8 / 0x146adcfa8
            ["browserTZ"] = "-120",                                   // 0x146f9c808 / 0x146aa3188
            ["browserUserAgent"] = c.Session.UserAgent ?? string.Empty, // 0x146f9c830
        };

        var fingerprint = new Dictionary<string, string>
        {
            ["source"] = source,                                       // 0x147160de0
            ["browser"] = browser.ToString(Newtonsoft.Json.Formatting.None), // 0x146f9c058
            ["one_click_authn_device_support[hosted]"] = "true",        // 0x1471082a8 → true
            ["one_click_authn_device_support[same_origin_frame]"] = flag,   // 0x1471083a8
            ["one_click_authn_device_support[spc_eligible]"] = flag,        // 0x147108420
            ["one_click_authn_device_support[webauthn_eligible]"] = "true", // 0x147108490 → true
            ["one_click_authn_device_support[publickey_credentials_get_allowed]"] = flag,
            ["key"] = publishable ?? string.Empty,                     // 0x1470ae940
            ["_stripe_account"] = StripeAccount,                       // 0x146f649d0
        };
        if (!hasForm)
        {
            fingerprint["fingerprintOutcome"] = "not_supported";       // 0x147103b28 / 0x147034fd0
            fingerprint["frontend_execution"] = StripeAccount;         // 0x14703b548 (derived value)
        }

        // The machine's own report line (0x146ea0348 + 0x146a87ad8 + 0x146a689f8).
        c.Emit("SubmitFingerprint: methodUrl='" + apiUrl + "/v1/3ds2/authenticate" +
               "' fingerprintAvailable=" + flag +
               " body=" + fingerprint["browser"], "STRIPE");

        var authForm = new System.Net.Http.FormUrlEncodedContent(fingerprint);
        var authReq = await c.Http.SendAsync(HttpMethod.Put, apiUrl + "/v1/3ds2/authenticate",
            JlFormOptions(c, authForm, "jl-3ds2-auth"), ct).ConfigureAwait(false);
        c.Session.AbsorbCookies(authReq.Cookies);
        if (authReq.StatusCode < 200 || authReq.StatusCode >= 300)
            return StepOutcome.Fail($"jl 3ds2 authenticate HTTP {authReq.StatusCode}", retryable: true);

        // R1094: the chain's last request, decoded from sub_141144c20 (113 lines) — first the
        // notify hop with the server transaction id (report line 0x146b9a028, URL
        // 0x14706b908 + account + '/' + transaction id), then the completion PUT of
        // challenge_complete (0x147054e90) carrying source / final_cres / key / _stripe_account.
        var txnId = c.Session.Vars.GetValueOrDefault("jl.threeDsServerTransId") ?? string.Empty;
        c.Emit("CompletePayment: notify serverTransactionId=" + txnId, "STRIPE");

        var hooksBase2 = c.Session.Vars.TryGetValue("stripe.hooksUrl", out var h2) &&
                         !string.IsNullOrEmpty(h2)
            ? h2.TrimEnd('/')
            : "https://hooks.stripe.com";
        var notifyUrl = hooksBase2 + "/3d_secure_2/notify/" + StripeAccount + "/" +
                        Uri.EscapeDataString(txnId);
        var notifyReq = await c.Http.SendAsync(HttpMethod.Put, notifyUrl,
            JlFormOptions(c, new System.Net.Http.FormUrlEncodedContent(new Dictionary<string, string>
            {
                ["source"] = source,
            }), "jl-3ds2-notify"), ct).ConfigureAwait(false);
        c.Session.AbsorbCookies(notifyReq.Cookies);
        if (notifyReq.StatusCode < 200 || notifyReq.StatusCode >= 300)
            return StepOutcome.Fail($"jl 3ds2 notify HTTP {notifyReq.StatusCode}", retryable: true);

        var completeForm = new Dictionary<string, string>
        {
            ["source"] = source,
            ["final_cres"] = c.Session.Vars.GetValueOrDefault("jl.finalCres") ?? string.Empty,
            ["key"] = publishable ?? string.Empty,
            ["_stripe_account"] = StripeAccount,
        };
        var completeReq = await c.Http.SendAsync(HttpMethod.Put, apiUrl + "/v1/3ds2/challenge_complete",
            JlFormOptions(c, new System.Net.Http.FormUrlEncodedContent(completeForm), "jl-3ds2-complete"),
            ct).ConfigureAwait(false);
        c.Session.AbsorbCookies(completeReq.Cookies);
        if (completeReq.StatusCode < 200 || completeReq.StatusCode >= 300)
            return StepOutcome.Fail($"jl 3ds2 challenge_complete HTTP {completeReq.StatusCode}", retryable: true);

        // The chain's closing line, verbatim (0x146e4aa00).
        c.Emit("Process complete", "STRIPE");
        return StepOutcome.Success();
    }

    /// <summary>
    /// The form body with its per-request options — the same shape NetClient's PostFormAsync
    /// builds, exposed here because the 3DS2 hops are PUTs and PostFormAsync is POST-only.
    /// </summary>
    private static Cybersole.Http.RequestOptions JlFormOptions(FlowContext c,
        System.Net.Http.HttpContent content, string tag)
    {
        var options = c.Options(tag);
        options.Content = content;
        return options;
    }
}

/// <summary>Kith — Shopify storefront plus a drop scheduler.</summary>
public sealed class KithFlow : ShopifyFlow
{
    public KithFlow() : base("kith", "Kith", new[] { "kith.com", "kithnyc.com" })
    {
    }

    public override async Task<StepOutcome> WaitForReleaseAsync(FlowContext c, CancellationToken ct)
    {
        var at = c.Session.Vars.TryGetValue("release", out var r) ? r : null;
        if (string.IsNullOrEmpty(at) || !DateTimeOffset.TryParse(at, out var when))
            return StepOutcome.Success();

        var wait = when - DateTimeOffset.UtcNow;
        if (wait > TimeSpan.Zero && wait < TimeSpan.FromMinutes(30))
            await Task.Delay(wait, ct).ConfigureAwait(false);
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> PollReleaseAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/collections/new-releases",  // inferred: no image evidence (R294)
            "kith-releases", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("kith releases unreachable", retryable: true);

        c.Session.Vars["releases"] = res.Body;
        var count = Regex.Matches(res.Body, @"/products/([A-Za-z0-9_\-]+)").Count;
        c.Session.Vars["releaseCount"] = count.ToString();
        return StepOutcome.Success();
    }
}

/// <summary>
/// Sneakersnstuff — Shopify, EU storefronts.
///
/// Only sneakersnstuff.com is claimed. <c>sns.com</c> used to redirect here but now belongs to
/// an unrelated managed-services company (it resolves to thrivenextgen.com), so claiming it
/// would hand a completely different site's URLs to this flow. A wrong claim is worse than a
/// missing one: it fails silently, in the wrong place.
/// </summary>
public sealed class SnsFlow : ShopifyFlow
{
    public SnsFlow() : base("sns", "Sneakersnstuff", new[] { "sneakersnstuff.com" })
    {
    }
}

/// <summary>Notre — Shopify, single storefront.</summary>
public sealed class NotreFlow : ShopifyFlow
{
    public NotreFlow() : base("notre", "Notre", new[] { "notre-shop.com" })
    {
    }
}
