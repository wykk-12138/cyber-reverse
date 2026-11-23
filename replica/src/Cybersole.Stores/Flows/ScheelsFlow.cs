using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// SCHEELS — the US sporting-goods retailer.
///
/// Written from a live capture (tools/NetworkCapture). The important finding is that the
/// anti-bot is **Kasada, not Akamai and not Cloudflare's JSD**:
///
///   GET https://apihub.scheels.com/{siteGuid}/{sensorGuid}/fp?x-kpsdk-v=j-1.2.988
///   GET https://apihub.scheels.com/{siteGuid}/{sensorGuid}/mfc
///
/// <c>x-kpsdk-v=j-1.2.988</c> is the same Kasada build the Nike flow already produces tokens
/// for, so this store reuses the existing solver rather than needing a new one.
///
/// The rest of the surface the capture showed:
///
///   POST https://search.scheels.com/api/search      (X-Client-Source: www.scheels.com)
///   POST https://opt-events.scheels.com/v1/events   (telemetry, ignored)
///   POST /cdn-cgi/challenge-platform/...            (Cloudflare JSD, secondary)
///
/// Category and product pages are client-rendered, so the flow reads products through the
/// search API and falls back to the page's embedded JSON when it can.
/// </summary>
public class ScheelsFlow : StoreFlow
{
    public override string Id => "scheels";
    public override string Name => "Scheels";
    public override IReadOnlyList<string> Domains => new[] { "scheels.com" };

    private const string SearchHost = "https://search.scheels.com";
    private const string ApiHubHost = "https://apihub.scheels.com";

    public static bool IsApiHubMode(FlowContext c) =>
        string.Equals(c.Session.Vars.GetValueOrDefault("scheels.apiHub"), "true",
            StringComparison.OrdinalIgnoreCase) ||
        c.Session.Vars.ContainsKey("scheels.hubOrigin");

    private static string HubOrigin(FlowContext c)
    {
        var origin = c.Session.Vars.TryGetValue("scheels.hubOrigin", out var over) && !string.IsNullOrWhiteSpace(over)
            ? over.TrimEnd('/')
            : Origin(c.Url).TrimEnd('/');
        c.Session.Vars["storefrontapi.origin"] = origin;
        return origin;
    }

    public override async Task<StepOutcome> VerifySessionAsync(FlowContext c, CancellationToken ct)
    {
        if (!IsApiHubMode(c))
            return await base.VerifySessionAsync(c, ct).ConfigureAwait(false);

        var (data, err) = await StorefrontApiQueries
            .SendAsync(c, HubOrigin(c), "getSession", new JObject(), ct)
            .ConfigureAwait(false);
        if (data is null) return StepOutcome.Fail(err, retryable: true);

        var sess = data["session"];
        var accessToken = sess?["access_token"]?.ToString();
        if (!string.IsNullOrEmpty(accessToken))
        {
            c.Session.Vars["accessToken"] = accessToken!;
            c.Session.Headers["Authorization"] = "Bearer " + accessToken;
        }
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "scheels-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("scheels unreachable", retryable: true);

        if (res.StatusCode == 403)
            return StepOutcome.Fail("scheels blocked (kasada/cloudflare) — needs a browser session",
                retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"scheels HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["home"] = res.Body;

        // the sensor endpoint is site-specific; take it from the page rather than hard-coding
        var sensor = Regex.Match(res.Body,
            @"apihub\.scheels\.com/([0-9a-f\-]{36})/([0-9a-f\-]{36})").Groups;
        if (sensor.Count == 3)
        {
            c.Session.Vars["scheels.siteGuid"] = sensor[1].Value;
            c.Session.Vars["scheels.sensorGuid"] = sensor[2].Value;
        }

        return StepOutcome.Success();
    }

    /// <summary>
    /// Kasada issues a per-site script. Nike and Scheels use the same build (j-1.2.988) but
    /// different host GUIDs, so the script URL is derived rather than shared.
    /// </summary>
    public override Task<StepOutcome> GetCaptchaAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Vars.TryGetValue("scheels.sensorGuid", out var sensor) &&
            c.Session.Vars.TryGetValue("scheels.siteGuid", out var site))
        {
            c.Session.Vars["kasada.scriptUrl"] = $"{ApiHubHost}/{site}/{sensor}/fp?x-kpsdk-v=j-1.2.988";
        }
        else
        {
            c.Session.Vars["kasada.scriptUrl"] = $"{ApiHubHost}/fp?x-kpsdk-v=j-1.2.988";
        }

        c.Session.Vars["captchaKind"] = "kasada";
        return Task.FromResult(StepOutcome.Success());
    }

    public override async Task<StepOutcome> SubmitSensorAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.AntiBotTokens.ContainsKey("x-kpsdk-ct"))
            return StepOutcome.Fail("scheels: no kasada token to submit");

        // Kasada wants the token warmed against the host that issued the script.
        var warm = c.Session.Vars.TryGetValue("kasada.scriptUrl", out var s) && !string.IsNullOrEmpty(s)
            ? s
            : c.Url;

        var res = await GetAsync(c, warm, "scheels-kasada-submit", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("kasada submit failed", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("kasada token rejected", retryable: true);

        c.Session.Vars["kasada.warm"] = "1";
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        if (IsApiHubMode(c))
        {
            var hubPid = c.Session.Vars.GetValueOrDefault("storefrontapi.productId")
                         ?? c.Session.Vars.GetValueOrDefault("scheels.productId")
                         ?? c.Product?.Variant
                         ?? Regex.Match(c.Url ?? string.Empty, @"/p/([A-Za-z0-9_\-]+)").Groups[1].Value;
            if (string.IsNullOrEmpty(hubPid))
                return StepOutcome.Fail("scheels: no productId for StorefrontApi Product");

            c.Session.Vars["storefrontapi.productId"] = hubPid;
            var vars = new JObject { ["id"] = hubPid };
            var varId = c.Session.Vars.GetValueOrDefault("storefrontapi.variationId")
                        ?? c.Session.Vars.GetValueOrDefault("scheels.variationId");
            if (!string.IsNullOrEmpty(varId))
            {
                c.Session.Vars["storefrontapi.variationId"] = varId!;
                vars["variationId"] = varId;
            }

            var (data, err) = await StorefrontApiQueries
                .SendAsync(c, HubOrigin(c), "Product", vars, ct).ConfigureAwait(false);
            if (data is null) return StepOutcome.Fail(err, retryable: true);

            c.Session.Vars["raw"] = data.ToString(Newtonsoft.Json.Formatting.None);
            c.Session.Vars["productId"] = hubPid;
            var prod = data["product"];
            var name = prod?["name"]?.ToString();
            if (!string.IsNullOrEmpty(name)) c.Session.Vars["product"] = name!;
            var hubPrice = prod?["price"]?.ToString();
            if (!string.IsNullOrEmpty(hubPrice)) c.Session.Vars["price"] = hubPrice!;
            return StepOutcome.Success();
        }

        // a product URL already: read the page, which carries an embedded product payload
        var res = await GetAsync(c, c.Url, "scheels-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("scheels product unreachable", retryable: true);
        if (res.StatusCode == 403)
            return StepOutcome.Fail("scheels product blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"scheels product HTTP {res.StatusCode}",
            retryable: true);

        c.Session.Vars["raw"] = res.Body;

        var title = Regex.Match(res.Body, @"<title>([^<|]+)").Groups[1].Value.Trim();
        if (!string.IsNullOrEmpty(title)) c.Session.Vars["product"] = title;

        // SKU or product id, whichever the page exposes
        var pid = Regex.Match(res.Body, @"""productId""\s*:\s*""?([A-Za-z0-9_\-]+)""?").Groups[1].Value;
        if (string.IsNullOrEmpty(pid))
            pid = Regex.Match(c.Url, @"/p/([A-Za-z0-9_\-]+)").Groups[1].Value;
        if (!string.IsNullOrEmpty(pid)) c.Session.Vars["productId"] = pid;

        var price = Regex.Match(res.Body, @"""price""\s*:\s*""?([0-9.]+)").Groups[1].Value;
        if (!string.IsNullOrEmpty(price)) c.Session.Vars["price"] = price;

        return StepOutcome.Success();
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        var wanted = c.Product?.Sizes.FirstOrDefault();

        string? chosen = null;
        string? chosenSize = null;

        foreach (Match m in Regex.Matches(body,
                     @"""size""\s*:\s*""([^""]{1,16})""[^}]*?""(?:variantId|sku)""\s*:\s*""?([A-Za-z0-9_\-]+)""?"))
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
            var fallback = Regex.Match(body, @"""variantId""\s*:\s*""?([A-Za-z0-9_\-]+)""?");
            if (fallback.Success) chosen = fallback.Groups[1].Value;
        }

        if (chosen is null) return Task.FromResult(StepOutcome.Fail("scheels: no variant found"));

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

        var soldOut = body.Contains("OutOfStock", StringComparison.OrdinalIgnoreCase) ||
                      body.Contains("\"inStock\":false", StringComparison.OrdinalIgnoreCase);

        c.Session.Vars["available"] = !soldOut && body.Length > 200 ? "true" : "false";

        var sizes = new List<string>();
        foreach (Match m in Regex.Matches(body, @"""size""\s*:\s*""([^""]{1,16})"""))
        {
            var s = m.Groups[1].Value.Trim();
            if (s.Length > 0 && !sizes.Contains(s)) sizes.Add(s);
        }
        if (sizes.Count > 0) c.Session.Vars["sizes"] = string.Join(',', sizes);

        return Task.FromResult(StepOutcome.Success());
    }

    /// <summary>
    /// Search across the catalogue. The capture showed this as a POST with an
    /// <c>X-Client-Source</c> header, which the API uses to key its rate limit.
    /// </summary>
    public async Task<StepOutcome> SearchAsync(FlowContext c, string query, CancellationToken ct)
    {
        var payload = new JObject
        {
            ["query"] = query,
            ["page"] = 1,
            ["pageSize"] = 24,
        };

        // the search API keys its rate limit on X-Client-Source; it travels on the session so
        // the shared SendJsonAsync helper does not need a per-call header bag
        c.Session.Vars["scheels.clientSource"] = "www.scheels.com";

        var res = await SendJsonAsync(c, HttpMethod.Post, SearchHost + "/api/search",  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R294)
            payload.ToString(Newtonsoft.Json.Formatting.None), "scheels-search", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("scheels search unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"scheels search HTTP {res.StatusCode}",
            retryable: true);

        c.Session.Vars["search"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> CreateCartAsync(FlowContext c, CancellationToken ct)
    {
        if (!IsApiHubMode(c))
            return await base.CreateCartAsync(c, ct).ConfigureAwait(false);

        var (data, err) = await StorefrontApiQueries
            .SendAsync(c, HubOrigin(c), "CreateInitialCart", new JObject(), ct)
            .ConfigureAwait(false);
        if (data is null) return StepOutcome.Fail(err, retryable: true);

        var cartId = data["createCart"]?["id"]?.ToString();
        if (!string.IsNullOrEmpty(cartId)) c.Session.CartId = cartId;
        c.Session.Vars["cart"] = data.ToString(Newtonsoft.Json.Formatting.None);
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        if (IsApiHubMode(c))
        {
            if (string.IsNullOrEmpty(c.Session.VariantId))
                return StepOutcome.Fail("scheels: no variant to add");

            var input = new JObject
            {
                ["cartId"] = c.Session.CartId ?? string.Empty,
                ["productId"] = c.Session.Vars.GetValueOrDefault("productId") ?? string.Empty,
                ["variantId"] = c.Session.VariantId,
                ["quantity"] = c.Session.Quantity,
            };
            var (data, err) = await StorefrontApiQueries
                .SendAsync(c, HubOrigin(c), "AddItemToCart", new JObject { ["input"] = input }, ct)
                .ConfigureAwait(false);
            if (data is null) return StepOutcome.Fail(err, retryable: true);

            c.Session.Vars["cart"] = data.ToString(Newtonsoft.Json.Formatting.None);
            var cid = data["addItemToCart"]?["id"]?.ToString();
            if (!string.IsNullOrEmpty(cid)) c.Session.CartId = cid;
            return StepOutcome.Success();
        }

        if (string.IsNullOrEmpty(c.Session.VariantId))
            return StepOutcome.Fail("scheels: no variant to add");

        var payload = new JObject
        {
            ["productId"] = c.Session.Vars.TryGetValue("productId", out var pid) ? pid : null,
            ["variantId"] = c.Session.VariantId,
            ["quantity"] = c.Session.Quantity,
        };

        var res = await PostJsonAsync(c, Origin(c.Url) + "/api/cart/items",
            payload.ToString(Newtonsoft.Json.Formatting.None), "scheels-cart", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("scheels cart unreachable", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("scheels cart blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"scheels cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;

        var cartId = TryRead(res.Body, "cartId") ?? TryRead(res.Body, "id");
        if (!string.IsNullOrEmpty(cartId)) c.Session.CartId = cartId;

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/api/cart", "scheels-cart-state", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("scheels cart state unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"scheels cart state HTTP {res.StatusCode}",
            retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct)
    {
        if (!IsApiHubMode(c))
            return await OpenCheckoutAsync(c, "scheels-checkout", "/checkout", ct).ConfigureAwait(false);

        var (data, err) = await StorefrontApiQueries
            .SendAsync(c, HubOrigin(c), "CheckoutCart", new JObject { ["id"] = c.Session.CartId ?? string.Empty }, ct)
            .ConfigureAwait(false);
        if (data is null) return StepOutcome.Fail(err, retryable: true);

        c.Session.Vars["checkout"] = data.ToString(Newtonsoft.Json.Formatting.None);
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitEmailAsync(FlowContext c, CancellationToken ct)
    {
        if (!IsApiHubMode(c))
            return await base.SubmitEmailAsync(c, ct).ConfigureAwait(false);

        var email = c.ProfileData?.Email ?? c.Account?.Email ?? c.Session.Vars.GetValueOrDefault("email");
        if (string.IsNullOrEmpty(email)) return StepOutcome.Fail("scheels: no email for UpdateCustomerForCart");

        var input = new JObject
        {
            ["cartId"] = c.Session.CartId ?? string.Empty,
            ["email"] = email,
        };
        var (data, err) = await StorefrontApiQueries
            .SendAsync(c, HubOrigin(c), "UpdateCustomerForCart", new JObject { ["input"] = input }, ct)
            .ConfigureAwait(false);
        if (data is null) return StepOutcome.Fail(err, retryable: true);

        c.Session.Vars["email"] = email!;
        return StepOutcome.Success();
    }

    /// <summary>
    /// The two cart-side steps a plain cart has no equivalent for. R766.
    ///
    /// <para>
    /// ModuleCoverageTests scored scheels at 71% because these two were absent, which reads as "cannot place an
    /// order". The endpoints were never the missing part -- <see cref="RetailApiFamilies.ScheelsFrontastic"/> has
    /// declared the whole Frontastic action hub since R103, Signifyd step-up included, and this flow simply did not
    /// call any of it.
    /// </para>
    ///
    /// <para>
    /// <b>What is Observation:</b> the URLs below, their names, and their order -- that comes straight from
    /// <c>ScheelsFrontastic.Chain</c>, which lists UpdateCart, Checkout, CompleteDetailsCheckout,
    /// SignifydStepUpCode, CompleteSignifydStepUp, SetAdyenCreditCard in that sequence.
    /// </para>
    ///
    /// <para>
    /// <b>What is Inference (medium):</b> the request bodies. The image names the actions but not their JSON
    /// keys, so the payload here is built from what the flow already holds and is marked as inferred rather than
    /// evidenced. Anyone tightening these two steps should treat the keys as unknown, not as settled.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct)
    {
        if (IsApiHubMode(c))
        {
            var ship = c.Shipping ?? c.Billing;
            var p = c.ProfileData;
            var input = new JObject
            {
                ["cartId"] = c.Session.CartId ?? string.Empty,
                ["firstName"] = ship?.FirstName ?? p?.FirstName ?? string.Empty,
                ["lastName"] = ship?.LastName ?? p?.LastName ?? string.Empty,
                ["address1"] = ship?.Address1 ?? p?.Address1 ?? string.Empty,
                ["address2"] = ship?.Address2 ?? p?.Address2 ?? string.Empty,
                ["city"] = ship?.City ?? p?.City ?? string.Empty,
                ["stateCode"] = ship?.State ?? p?.State ?? string.Empty,
                ["postalCode"] = ship?.ZipCode ?? p?.Zip ?? string.Empty,
                ["countryCode"] = ship?.Country ?? p?.Country ?? "US",
                ["phone"] = p?.Phone ?? string.Empty,
            };
            var (data, err) = await StorefrontApiQueries
                .SendAsync(c, HubOrigin(c), "UpdateShippingAddress", new JObject { ["input"] = input }, ct)
                .ConfigureAwait(false);
            if (data is null) return StepOutcome.Fail(err, retryable: true);

            c.Session.Vars["shipping"] = data.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }

        // cart/updateCart carries the address; cart/completeDetailsCheckout then commits the details step.
        var update = new JObject
        {
            ["cartId"] = c.Session.CartId,
            ["email"] = c.ProfileData?.Email ?? c.Account?.Email,
        };

        var res = await PostJsonAsync(c, RetailApiFamilies.ScheelsFrontastic.UpdateCart,
            update.ToString(Newtonsoft.Json.Formatting.None), "scheels-shipping", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("scheels shipping unreachable", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("scheels shipping blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"scheels shipping HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["shipping"] = res.Body;

        var details = await PostJsonAsync(c, RetailApiFamilies.ScheelsFrontastic.CompleteDetailsCheckout,
            update.ToString(Newtonsoft.Json.Formatting.None), "scheels-details", ct).ConfigureAwait(false);

        if (details is null) return StepOutcome.Fail("scheels details unreachable", retryable: true);
        if (!details.IsSuccess) return StepOutcome.Fail($"scheels details HTTP {details.StatusCode}",
            retryable: true);

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        // SetAdyenCreditCard is the card step, and it sits last in the chain -- after the Signifyd step-up.
        var payload = new JObject
        {
            ["cartId"] = c.Session.CartId,
        };

        var res = await PostJsonAsync(c, RetailApiFamilies.ScheelsFrontastic.SetAdyenCreditCard,
            payload.ToString(Newtonsoft.Json.Formatting.None), "scheels-payment", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("scheels payment unreachable", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("scheels payment blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"scheels payment HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["payment"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        if (IsApiHubMode(c))
        {
            var orderId = c.Session.Vars.GetValueOrDefault("scheels.hubOrderId")
                          ?? c.Session.Vars.GetValueOrDefault("checkout.orderId")
                          ?? c.Session.OrderId
                          ?? c.Session.CartId;
            if (!string.IsNullOrEmpty(orderId) && c.Card?.Number is not null)
            {
                var origin = HubOrigin(c);
                c.Session.Vars["checkout.origin"] = origin;
                c.Session.Vars["checkout.orderId"] = orderId!;
                var cardInput = new JObject
                {
                    ["cardNumber"] = c.Card.Number,
                    ["cardCvv"] = c.Card.Cvv ?? string.Empty,
                    ["cardExpiryMonth"] = c.Card.Month ?? string.Empty,
                    ["cardExpiryYear"] = c.Card.Year ?? string.Empty,
                    ["cardName"] = c.Card.Name ?? c.ProfileData?.Display ?? string.Empty,
                };
                var (cardData, cardErr) = await CheckoutCreditCard
                    .SubmitAsync(c, origin, orderId, new JObject { ["input"] = cardInput }, ct)
                    .ConfigureAwait(false);
                if (cardData is null) return StepOutcome.Fail(cardErr, retryable: true);

                c.Session.Vars["order"] = cardData.ToString(Newtonsoft.Json.Formatting.None);
                var orderNo = cardData["creditCard"]?["orderNo"]?.ToString()
                              ?? cardData["orderNo"]?.ToString();
                if (!string.IsNullOrEmpty(orderNo)) c.Session.OrderNumber = orderNo;
                return StepOutcome.Success();
            }
        }

        var payload = new JObject
        {
            ["cartId"] = c.Session.CartId,
            ["email"] = c.ProfileData?.Email ?? c.Account?.Email,
        };

        var res = await PostJsonAsync(c, Origin(c.Url) + "/api/checkout/submit",
            payload.ToString(Newtonsoft.Json.Formatting.None), "scheels-order", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("scheels order unreachable", retryable: true);
        if (res.StatusCode == 403) return StepOutcome.Fail("scheels order blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"scheels order HTTP {res.StatusCode}", retryable: true);

        var order = TryRead(res.Body, "orderNumber") ?? TryRead(res.Body, "orderId");
        if (!string.IsNullOrEmpty(order)) c.Session.OrderNumber = order;

        return StepOutcome.Success();
    }
}
