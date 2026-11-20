using System.Text.RegularExpressions;
using Cybersole.Http;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Salesforce Commerce Cloud (Demandware) storefronts.
///
/// The Accounts page of the running 5.18.32 build lists this platform twice —
/// "Demandware" and "Demandware (Funko)" — because a single site id is bound per tenant.
/// One implementation therefore serves both entries: everything below is parameterised on
/// <c>SiteId</c> rather than on the host.
///
/// Endpoint shape (SFCC storefront controllers):
///   GET  /on/demandware.store/Sites-{site}-Site/{locale}/Product-Show?pid={pid}
///   POST /on/demandware.store/Sites-{site}-Site/{locale}/Cart-AddProduct
///   GET  /on/demandware.store/Sites-{site}-Site/{locale}/Cart-Show
///   GET  /on/demandware.store/Sites-{site}-Site/{locale}/Checkout-Begin
///   POST /on/demandware.store/Sites-{site}-Site/{locale}/Checkout-Submit
/// </summary>
public class DemandwareFlow : StoreFlow
{
    private readonly string _site;
    private readonly string _locale;

    public DemandwareFlow(string id, string name, string[] domains, string siteId,
        string locale = "en_US")
    {
        Id = id;
        Name = name;
        Domains = domains;
        _site = siteId;
        _locale = locale;
    }

    public override string Id { get; }
    public override string Name { get; }
    public override IReadOnlyList<string> Domains { get; }

    /// <summary>The SFCC site id, as it appears in the controller path.</summary>
    public string SiteId => _site;

    /// <summary>The SFCC locale segment, e.g. en_US.</summary>
    public string Locale => _locale;

    protected string Controller(FlowContext c, string name)
    {
        var siteSegment = _site.EndsWith("-Site", StringComparison.Ordinal) ? _site : _site + "-Site";
        return $"{Origin(c.Url)}/on/demandware.store/Sites-{siteSegment}/{_locale}/{name}";
    }

    /// <summary>
    /// The three PayPal controller actions the image carries (R1162). All three are SFCC storefront
    /// controllers, so they compose with <see cref="Controller"/> exactly like Product-Show does —
    /// they are not gateway API calls and do not belong with the payment gateways.
    ///
    /// <para>
    /// <c>GetPurchaseUnit</c> (0x146ab044c) is the one with an observed verb: in <c>sub_140a50cd0</c> the
    /// path is appended to a builder at line 172 and the request that follows at line 179 goes through
    /// verb slot <c>sub_1408B61E0</c> (+8 = GET), with three arguments — a GET and therefore no body.
    /// </para>
    /// <para>
    /// The other two paths are frozen literals too — <c>/Paypal-GetPaypalOrderId?csrf_token=</c>
    /// (0x146ab03ec) and <c>/Paypal-GetOrderDetails?orderId=</c> (0x146ab0394) — but neither is
    /// referenced from that function, so their verbs are <b>Unknown</b> and nothing here sends them.
    /// </para>
    /// </summary>
    /// <summary>
    /// The two query prefixes. The controller names themselves live in <see cref="DemandwareControllers"/>
    /// with every other controller name (R1169); only the query shape belongs here.
    /// </summary>
    public const string PaypalGetPaypalOrderIdQuery = "?csrf_token=";
    public const string PaypalGetOrderDetailsQuery = "?orderId=";

    /// <summary>
    /// Reads the PayPal purchase unit for the current cart. The image does this with a GET on the
    /// controller path (see <see cref="PaypalGetPurchaseUnit"/>), and the answer is kept for the
    /// gateway call that follows it in the same machine.
    ///
    /// <para>
    /// R1170 walked the caller chain, because for three rounds the honest note here was "nothing calls
    /// this": the controller machine 0x140a50cd0 is awaited from a state machine, which is started by
    /// the async method 0x140a45380, and that method has exactly one caller — <b>0x140a530f0</b>, a
    /// 438-line routine. The same routine also awaits the order-details method 0x140a453d0. So these
    /// two calls sit together inside one step; the order-id lookup, whose async method 0x140a27e50 is
    /// awaited from a <i>different</i> routine (0x140a32f30, 574 lines), does not.
    /// </para>
    /// </summary>
    public async Task<StepOutcome> PaypalPurchaseUnitAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Controller(c, DemandwareControllers.PaypalGetPurchaseUnit),
            Tag() + "-paypal-purchase-unit", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("demandware paypal: purchase unit unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"demandware paypal: purchase unit HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["paypal.purchaseUnit"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// The order-id lookup. R1164 closed the gap R1163 left open: the containing function
    /// (0x140a31e40) appends the controller path at line 118, the <c>?csrf_token=</c> prefix at 124 (or
    /// 129 on the grow path), then the token itself at 138; line 141 calls <c>sub_141DC7870(&amp;v23)</c>
    /// — which materialises that builder — and line 143 hands the resulting string to the options object,
    /// which is the second argument of the GET at line 146. So the request does carry this URL, and the
    /// append order is path, query prefix, token: the same order this method composes.
    ///
    /// <para>The caller passes the token rather than this method inventing a session key for it.</para>
    /// </summary>
    public async Task<StepOutcome> PaypalOrderIdAsync(FlowContext c, string csrfToken,
        CancellationToken ct)
    {
        var res = await GetAsync(c,
            Controller(c, DemandwareControllers.PaypalGetPaypalOrderId) + PaypalGetPaypalOrderIdQuery + csrfToken,
            Tag() + "-paypal-order-id", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("demandware paypal: order id unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"demandware paypal: order id HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["paypal.orderId"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// The order-details lookup, traced the same way in R1164: function 0x140a51e20 appends the path at
    /// 121, appends the order id at 131, materialises the builder at 134 via
    /// <c>sub_141DC7870(&amp;v21)</c>, and the GET at 139 takes the options object that string was
    /// placed into — so this URL is the one requested.
    /// </summary>
    public async Task<StepOutcome> PaypalOrderDetailsAsync(FlowContext c, string orderId,
        CancellationToken ct)
    {
        var res = await GetAsync(c,
            Controller(c, DemandwareControllers.PaypalGetOrderDetails) + PaypalGetOrderDetailsQuery + orderId,
            Tag() + "-paypal-order-details", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("demandware paypal: order details unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"demandware paypal: order details HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["paypal.orderDetails"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/", Tag() + "-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("demandware home unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"demandware home HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["home"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        // SFCC exposes the product id either in the URL (…-{pid}.html) or in a ?pid= query.
        var pid = ProductIdOf(c.Url);
        if (pid is null) return StepOutcome.Fail("demandware: no product id in url");

        var res = await GetAsync(c, Controller(c, "Product-Show") + "?pid=" + pid,
            Tag() + "-product", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("demandware product unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"demandware product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;
        c.Session.Vars["productId"] = pid;

        var name = Regex.Match(res.Body, @"<title>([^<|]+)").Groups[1].Value.Trim();
        if (!string.IsNullOrEmpty(name)) c.Session.Vars["product"] = name;

        var price = Regex.Match(res.Body,
            @"""price""\s*:\s*\{?\s*""sales""\s*:\s*\{?\s*""value""\s*:\s*([\d.]+)").Groups[1].Value;
        if (string.IsNullOrEmpty(price))
            price = Regex.Match(res.Body, @"data-price=""([\d.]+)""").Groups[1].Value;
        if (!string.IsNullOrEmpty(price)) c.Session.Vars["price"] = price;

        return string.IsNullOrEmpty(name)
            ? StepOutcome.Fail("demandware: product page carried no title", retryable: true)
            : StepOutcome.Success();
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        var wanted = c.Product?.Sizes.FirstOrDefault();

        // SFCC renders one swatch per variation with data-attr-value holding the pid.
        var candidates = Regex.Matches(body,
            @"""pid""\s*:\s*""([A-Za-z0-9_\-]+)""[^}]*?""(?:variationValue|size)""\s*:\s*""([^""]+)""");

        string? chosenId = null;
        string? chosenSize = null;

        foreach (Match m in candidates)
        {
            var id = m.Groups[1].Value;
            var size = m.Groups[2].Value;

            if (chosenId is null) { chosenId = id; chosenSize = size; }

            if (wanted is not null && size.Contains(wanted, StringComparison.OrdinalIgnoreCase))
            {
                chosenId = id;
                chosenSize = size;
                break;
            }
        }

        if (chosenId is null)
        {
            // fall back to the page's default variation
            var fallback = Regex.Match(body, @"""pid""\s*:\s*""([A-Za-z0-9_\-]+)""");
            if (!fallback.Success) return Task.FromResult(StepOutcome.Fail("demandware: no variation in page"));
            chosenId = fallback.Groups[1].Value;
        }

        c.Session.VariantId = chosenId;
        c.Session.Vars["variant"] = chosenId;
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

        var blocked = body.Contains("out of stock", StringComparison.OrdinalIgnoreCase) ||
                      body.Contains(@"""availability"":""outOfStock""", StringComparison.OrdinalIgnoreCase) ||
                      body.Contains(@"""available"":false", StringComparison.OrdinalIgnoreCase);

        c.Session.Vars["available"] = blocked ? "false" : "true";

        var sizes = new List<string>();
        foreach (Match m in Regex.Matches(body, @"""variationValue""\s*:\s*""([^""]{1,10})"""))
        {
            var s = m.Groups[1].Value.Trim();
            if (s.Length > 0 && !sizes.Contains(s)) sizes.Add(s);
        }

        if (sizes.Count > 0) c.Session.Vars["sizes"] = string.Join(',', sizes);

        return Task.FromResult(StepOutcome.Success());
    }

    /// <summary>Session var holding an SCAPI OAuth bearer token, when the store runs headless.</summary>
    public const string ScapiTokenVar = "scapi.token";

    /// <summary>Session var holding the SCAPI basket id returned by <c>createBasket</c>.</summary>
    public const string ScapiBasketVar = "scapi.basketId";

    /// <summary>The SCAPI organisation id, which every basket call needs.</summary>
    public const string ScapiOrgVar = "scapi.organizationId";

    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.VariantId))
            return StepOutcome.Fail("demandware: no pid to add");

        // R107: the image drives SFCC two ways. When the store hands out an SCAPI token the basket
        // calls go through /scapi/ShopperBaskets/*; otherwise the classic demandware.store
        // controller is the path this flow always used. Both are real; a store runs one or the other.
        if (c.Session.Vars.TryGetValue(ScapiTokenVar, out var token) && !string.IsNullOrWhiteSpace(token))
        {
            var scapi = await AddToCartViaScapiAsync(c, token, ct).ConfigureAwait(false);
            if (scapi is not null) return scapi.Value;
        }

        var form = new Dictionary<string, string>
        {
            ["pid"] = c.Session.VariantId!,
            ["quantity"] = c.Session.Quantity.ToString(),
        };

        var res = await PostFormAsync(c, Controller(c, DemandwareControllers.CartAddProduct), form,
            Tag() + "-add", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("demandware add failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"demandware add HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// The SCAPI half of <see cref="AddToCartAsync"/>: create a basket if there is none, then add the
    /// item. Returns null on any failure so the caller falls back to the classic controller rather
    /// than reporting a checkout failure for a capability the store may not offer.
    /// </summary>
    private async Task<StepOutcome?> AddToCartViaScapiAsync(
        FlowContext c, string token, CancellationToken ct)
    {
        var origin = Origin(c.Url);
        c.Session.Headers["Authorization"] = "Bearer " + token;
        try
        {
            if (!c.Session.Vars.TryGetValue(ScapiBasketVar, out var basketId) || string.IsNullOrWhiteSpace(basketId))
            {
                var created = await PostJsonAsync(c, origin + ScapiEndpoints.CreateBasket, "{}",
                    Tag() + "-scapi-create", ct).ConfigureAwait(false);

                if (created is null || !created.IsSuccess) return null;

                basketId = Newtonsoft.Json.Linq.JObject.Parse(created.Body)["basketId"]?.ToString();
                if (string.IsNullOrWhiteSpace(basketId)) return null;

                c.Session.Vars[ScapiBasketVar] = basketId!;
            }

            var org = c.Session.Vars.TryGetValue(ScapiOrgVar, out var organization) ? organization : string.Empty;

            var body = new Newtonsoft.Json.Linq.JObject
            {
                ["productId"] = c.Session.VariantId,
                ["quantity"] = c.Session.Quantity,
            };

            var url = origin + ScapiEndpoints.AddItemToBasket + "?siteId=" + Uri.EscapeDataString(SiteId);  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R298)

            var added = await PostJsonAsync(c, url, body.ToString(Newtonsoft.Json.Formatting.None),
                Tag() + "-scapi-add", ct).ConfigureAwait(false);

            if (added is null || !added.IsSuccess) return null;

            c.Session.Vars["cart"] = added.Body;
            if (!string.IsNullOrEmpty(org)) c.Session.Vars["scapi.org"] = org;
            return StepOutcome.Success();
        }
        finally
        {
            c.Session.Headers.Remove("Authorization");
        }
    }

    /// <summary>
    /// The <c>siteId</c> an SCAPI call needs — the same site id the flow already carries
    /// (<c>Sites-{site}-Site</c>), not a separate value, so it reuses <c>SiteId</c>.
    /// </summary>

    /// <summary>
    /// Enters a Demandware draw. The image carries the three pieces this needs: the
    /// <c>SaleRegistration-Config</c> / <c>SaleRegistration-SignupSubmit</c> controllers a sale
    /// registration also uses, the <c>panagora-raffle-data</c> script the page carries its payload
    /// in, and <c>Already Entered Draw</c> as the duplicate-entry answer.
    ///
    /// <para>
    /// A page with no raffle payload is <b>not</b> a failure: most Demandware stores are not running
    /// a draw, and turning that into an error would fail every normal checkout that never asked for
    /// one. It records <c>raffle=absent</c> and succeeds.
    /// </para>
    /// </summary>
    public async Task<StepOutcome> EnterRaffleAsync(FlowContext c, CancellationToken ct)
    {
        var page = await GetAsync(c, Origin(c.Url) + DemandwareRaffle.EntryPage,
            Tag() + "-raffle-page", ct).ConfigureAwait(false);

        if (page is null) return StepOutcome.Fail("raffle page unreachable", retryable: true);

        var payload = DemandwareRaffle.ExtractData(page.Body);
        if (payload is null)
        {
            c.Session.Vars["raffle"] = "absent";
            return StepOutcome.Success();
        }

        c.Session.Vars["raffle"] = "present";
        c.Session.Vars["raffle.data"] = payload;

        var id = DemandwareRaffle.ExtractId(page.Body);
        if (id is not null) c.Session.Vars["raffle.id"] = id;

        var config = await GetAsync(c, Controller(c, DemandwareControllers.SaleConfig),
            Tag() + "-raffle-config", ct).ConfigureAwait(false);

        if (config is not null && !config.IsSuccess)
            return StepOutcome.Fail($"raffle config HTTP {config.StatusCode}", retryable: true);

        var form = new Dictionary<string, string>
        {
            ["raffleId"] = id ?? string.Empty,
            ["email"] = c.Session.Vars.TryGetValue("email", out var email) ? email : string.Empty,
        };

        var submit = await PostFormAsync(c, Controller(c, DemandwareControllers.SaleSignupSubmit),
            form, Tag() + "-raffle-submit", ct).ConfigureAwait(false);

        if (submit is null) return StepOutcome.Fail("raffle submit failed", retryable: true);

        if (DemandwareRaffle.IsAlreadyEntered(submit.Body))
        {
            c.Session.Vars["raffle.status"] = "already-entered";
            return StepOutcome.Success();
        }

        if (!submit.IsSuccess)
            return StepOutcome.Fail($"raffle submit HTTP {submit.StatusCode}", retryable: true);

        c.Session.Vars["raffle.status"] = "entered";
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Controller(c, DemandwareControllers.CartGet), Tag() + "-cart", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("demandware cart unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"demandware cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;

        var total = Regex.Match(res.Body, @"""grandTotal""\s*:\s*""?([\d.,]+)""?").Groups[1].Value;
        if (!string.IsNullOrEmpty(total)) c.Session.Vars["total"] = total;

        var empty = res.Body.Contains("cart-empty", StringComparison.OrdinalIgnoreCase);
        return empty ? StepOutcome.Fail("demandware: cart is empty") : StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Controller(c, DemandwareControllers.CheckoutBegin), Tag() + "-checkout", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("demandware checkout unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"demandware checkout HTTP {res.StatusCode}", retryable: true);

        c.Session.CheckoutUrl = res.Url.ToString();
        c.Session.Vars["checkout"] = res.Body;

        var csrf = Regex.Match(res.Body,
            @"name=""(?:csrf_token|dwfrm_security_token)""\s+value=""([^""]+)""").Groups[1].Value;
        if (!string.IsNullOrEmpty(csrf)) c.Session.CsrfToken = csrf;

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct)
    {
        var ship = c.Shipping;
        if (ship is null) return StepOutcome.Fail("demandware: no shipping address");

        // SFCC posts the whole address as dwfrm_shipping_* fields on Shipping-Show.
        // R1282: the address is projected through the image's own model (Cybersole.Models.Address) so the state is a
        // State rather than a bare string — the descriptor run at 0x143211f9d is what says Address.State is a State.
        var address = new Cybersole.Models.Address(
            ship.FirstName, ship.LastName, ship.Address1, null, ship.City, ship.ZipCode, null,
            string.IsNullOrEmpty(ship.State) ? null : new Cybersole.Models.State(ship.State!),
            null);

        var form = new Dictionary<string, string>
        {
            ["dwfrm_shipping_shippingAddress_addressFields_firstName"] = address.FirstName ?? string.Empty,
            ["dwfrm_shipping_shippingAddress_addressFields_lastName"] = address.LastName ?? string.Empty,
            ["dwfrm_shipping_shippingAddress_addressFields_address1"] = address.Address1 ?? string.Empty,
            ["dwfrm_shipping_shippingAddress_addressFields_city"] = address.City ?? string.Empty,
            ["dwfrm_shipping_shippingAddress_addressFields_states_stateCode"] = address.State?.Name ?? string.Empty,
            ["dwfrm_shipping_shippingAddress_addressFields_postalCode"] = address.ZipCode ?? string.Empty,
            ["dwfrm_shipping_shippingAddress_addressFields_country"] = ship.Country ?? "US",
        };

        if (!string.IsNullOrEmpty(c.Session.CsrfToken))
            form["csrf_token"] = c.Session.CsrfToken!;

        var res = await PostFormAsync(c, Controller(c, DemandwareControllers.SubmitShipping), form,
            Tag() + "-shipping", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("demandware shipping failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"demandware shipping HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["shipping"] = res.Body;

        // A shipping method has to be chosen before payment; pick the first offered.
        var method = Regex.Match(res.Body, @"value=""([A-Za-z0-9_\-]+)""[^>]*name=""dwfrm_shipping_shippingMethodID""");
        if (!method.Success)
            method = Regex.Match(res.Body, @"name=""dwfrm_shipping_shippingMethodID""[^>]*value=""([A-Za-z0-9_\-]+)""");
        if (method.Success) c.Session.Vars["shippingMethod"] = method.Groups[1].Value;

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return StepOutcome.Fail("demandware: no card");

        // SFCC never takes the PAN through the storefront form on a live tenant — it expects a
        // token from the payment provider. Record the intent and post what the form accepts so
        // the step is honest about what it can and cannot do.
        var form = new Dictionary<string, string>
        {
            ["dwfrm_billing_paymentMethod"] = c.Session.Vars.TryGetValue("paymentMethod", out var pm)
                ? pm
                : "CREDIT_CARD",
            ["dwfrm_billing_creditCardFields_cardType"] =
                card.Number.StartsWith('4') ? "Visa"
                : card.Number.StartsWith("5") ? "Master"
                : "Amex",
            ["dwfrm_billing_creditCardFields_cardNumber"] = card.Number,
            ["dwfrm_billing_creditCardFields_expirationMonth"] = card.Month ?? string.Empty,
            ["dwfrm_billing_creditCardFields_expirationYear"] = card.Year ?? string.Empty,
            ["dwfrm_billing_creditCardFields_securityCode"] = card.Cvv ?? string.Empty,
        };

        if (!string.IsNullOrEmpty(c.Session.CsrfToken))
            form["csrf_token"] = c.Session.CsrfToken!;

        var res = await PostFormAsync(c, Controller(c, DemandwareControllers.SubmitPayment), form,
            Tag() + "-payment", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("demandware payment failed", retryable: true);

        var status = res.StatusCode;
        c.Session.Vars["paymentStatus"] = res.IsSuccess ? "authorised" : $"http_{status}";

        return res.IsSuccess
            ? StepOutcome.Success()
            : StepOutcome.Fail($"demandware payment HTTP {status}", retryable: status >= 500);
    }

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Vars.TryGetValue("cardinal.serverJwt", out var serverJwt) &&
            !string.IsNullOrEmpty(serverJwt) &&
            !c.Session.Vars.ContainsKey("cardinal.dfReferenceId"))
        {
            var init = await new Cybersole.Stores.Payments.CardinalThreeDs()
                .InitAsync(c, serverJwt, Cybersole.Stores.Payments.CardinalThreeDs.CardinalVariant.Centinel, ct)
                .ConfigureAwait(false);
            if (!init.Ok) return StepOutcome.Fail(init.Error ?? "demandware: cardinal init failed", retryable: true);
        }

        var form = new Dictionary<string, string>
        {
            ["dwfrm_billing_paymentMethod"] = c.Session.Vars.TryGetValue("paymentMethod", out var pm)
                ? pm
                : "CREDIT_CARD",
        };
        if (!string.IsNullOrEmpty(c.Session.CsrfToken))
            form["csrf_token"] = c.Session.CsrfToken!;

        var hasDf = c.Session.Vars.TryGetValue("cardinal.dfReferenceId", out var dfRef);
        var useDfQuery = hasDf ||
                         string.Equals(c.Session.Vars.GetValueOrDefault("demandware.useDfQuery"), "true",
                             StringComparison.OrdinalIgnoreCase);
        var orderController = useDfQuery
            ? DemandwareControllers.PlaceOrderPathWith(dfRef).TrimStart('/')
            : DemandwareControllers.PlaceOrder;

        var res = await PostFormAsync(c, Controller(c, orderController), form,
            Tag() + "-order", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("demandware order failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"demandware order HTTP {res.StatusCode}", retryable: true);

        var order = Regex.Match(res.Body,
            @"""orderNo""\s*:\s*""([A-Za-z0-9\-]+)""").Groups[1].Value;
        if (string.IsNullOrEmpty(order))
            order = Regex.Match(res.Body, @"order-confirmation[^?]*\?orderID=([A-Za-z0-9\-]+)")  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R298)
                .Groups[1].Value;

        if (string.IsNullOrEmpty(order))
            return StepOutcome.Fail("demandware: no order number returned");

        c.Session.OrderNumber = order;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> Process3DSAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Vars.TryGetValue("cardinal.serverJwt", out var jwt) && !string.IsNullOrEmpty(jwt))
        {
            var cardinal = new Cybersole.Stores.Payments.CardinalThreeDs();
            var init = await cardinal.InitAsync(
                c, jwt, Cybersole.Stores.Payments.CardinalThreeDs.CardinalVariant.Centinel, ct)
                .ConfigureAwait(false);
            if (!init.Ok) return StepOutcome.Fail(init.Error ?? "cardinal init failed", retryable: true);

            if (c.Session.Vars.TryGetValue("cardinal.orgUnitId", out var orgUnitId) && !string.IsNullOrEmpty(orgUnitId))
            {
                var refId = c.Session.Vars.GetValueOrDefault("cardinal.dfReferenceId")
                            ?? c.Session.Vars.GetValueOrDefault("cardinal.consumerSessionId")
                            ?? string.Empty;
                var fp = await cardinal.CollectDeviceFingerprintAsync(
                    c,
                    orgUnitId!,
                    refId,
                    c.Session.Vars.GetValueOrDefault("cardinal.binSessionId"),
                    c.Session.Vars.GetValueOrDefault("cardinal.methodUrl"),
                    ct).ConfigureAwait(false);
                if (!fp.Ok) return StepOutcome.Fail(fp.Error ?? "cardinal device fingerprint failed", retryable: true);
            }

            var txId = c.Session.Vars.GetValueOrDefault("cardinal.transactionId") ?? c.Session.OrderId;
            if (!string.IsNullOrEmpty(txId))
            {
                var cont = await cardinal.ContinueAsync(
                    c, txId!, jwt, Cybersole.Stores.Payments.CardinalThreeDs.CardinalVariant.Centinel, ct)
                    .ConfigureAwait(false);
                if (!cont.Ok) return StepOutcome.Fail(cont.Error ?? "cardinal continue failed", retryable: true);
            }

            return StepOutcome.Success();
        }

        return await base.Process3DSAsync(c, ct).ConfigureAwait(false);
    }

    /// <summary>SFCC product pages end in <c>…-{pid}.html</c> or carry a <c>pid</c> query.</summary>
    private static string? ProductIdOf(string url)
    {
        var query = Regex.Match(url, @"[?&]pid=([A-Za-z0-9_\-]+)");
        if (query.Success) return query.Groups[1].Value;

        var path = Regex.Match(url, @"-([A-Za-z0-9]{4,})\.html");
        return path.Success ? path.Groups[1].Value : null;
    }
}

/// <summary>Funko runs on Demandware with its own site id.</summary>
/// <summary>
/// Funko — Demandware, US storefront.
///
/// The site id was wrong: the flow declared <c>Funko-Site</c>, but every controller the real
/// storefront calls is under <c>Sites-FunkoUS-Site</c>:
///
///   /on/demandware.store/Sites-FunkoUS-Site/en_US/__Analytics-Start
///   /on/demandware.static/Sites-FunkoUS-Site/-/default/dw43a14dfa/...
///
/// A wrong site id is the quietest possible failure: the host is right, the platform is right,
/// and every controller request 404s. Verified against a live capture.
/// </summary>
public sealed class FunkoFlow : DemandwareFlow
{
    public FunkoFlow() : base("funko", "Demandware (Funko)", new[] { "funko.com" },
        "FunkoUS-Site", "en_US")
    {
    }

    private string AccountUrl(FlowContext c)
    {
        var prefix = c.Session.Vars.TryGetValue("funko.accountPrefix", out var p) && !string.IsNullOrEmpty(p)
            ? "/" + p.Trim('/')
            : string.Empty;
        return Origin(c.Url) + prefix + "/account";
    }

    /// <summary>
    /// <c>CheckFanRewardState</c> (<c>0x140a0fc40</c>): <c>GET {baseUrl}{prefix}/account</c>,
    /// inspects DOM <c>.crowd-twist-points</c> to report <c>"Already signed up"</c>.
    /// </summary>
    public async Task<StepOutcome> CheckFanRewardStateAsync(FlowContext c, CancellationToken ct)
    {
        c.Emit("Checking account", "StatusInfo");
        var res = await GetAsync(c, AccountUrl(c), Tag() + "-fan-state", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("funko: account unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"funko: account HTTP {res.StatusCode}", retryable: true);

        var body = res.Body ?? string.Empty;
        if (Regex.IsMatch(body, @"class\s*=\s*[""'][^""']*\bcrowd-twist-points\b[^""']*[""']", RegexOptions.IgnoreCase))
        {
            c.Session.Vars["fanRewards.state"] = "already_signed_up";
            c.Emit("Already signed up", "StatusInfo");
            return StepOutcome.Success();
        }

        c.Session.Vars["fanRewards.state"] = "not_signed_up";
        return StepOutcome.Success();
    }

    /// <summary>
    /// Funko <c>CheckBalance</c> (<c>0x140a13670</c>, mode enum <c>2 = "check balance"</c>):
    /// <c>GET {baseUrl}{prefix}/account</c>, reads <c>[class*='points-value']</c> -> <c>"{pts} pts"</c>.
    /// </summary>
    public async Task<StepOutcome> CheckFanRewardBalanceAsync(FlowContext c, CancellationToken ct)
    {
        c.Emit("Checking Balance", "StatusInfo");
        var res = await GetAsync(c, AccountUrl(c), Tag() + "-fan-balance", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("funko: balance unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"funko: balance HTTP {res.StatusCode}", retryable: true);

        var m = Regex.Match(res.Body ?? string.Empty,
            @"<[^>]*class\s*=\s*[""'][^""']*points-value[^""']*[""'][^>]*>(.*?)</[^>]+>",
            RegexOptions.IgnoreCase | RegexOptions.Singleline);
        if (m.Success)
        {
            var pts = Regex.Replace(m.Groups[1].Value, "<[^>]+>", string.Empty).Trim();
            if (!string.IsNullOrEmpty(pts))
            {
                var formatted = $"{pts} pts";
                c.Session.Vars["fanRewards.balance"] = formatted;
                c.Emit(formatted, "StatusInfo");
                return StepOutcome.Success();
            }
        }

        c.Emit("Invalid Account", "error");
        return StepOutcome.Fail("Invalid Account");
    }

    /// <summary>
    /// <c>SignUpFanRewards</c> (<c>0x140a19360</c>, mode enum <c>5 = "fan rewards signup"</c>):
    /// <c>POST {baseUrl}/on/demandware.store/Sites-FunkoUS-Site/{Locale}/CrowdTwist-Register</c>
    /// with <c>Referer: {baseUrl}/fanrewards-join/</c>, <c>Origin</c>, <c>X-Requested-With: XMLHttpRequest</c>,
    /// empty body, checking JSON <c>"success"</c> boolean.
    /// </summary>
    public async Task<StepOutcome> SignUpFanRewardsAsync(FlowContext c, CancellationToken ct)
    {
        c.Emit("Signing up", "StatusInfo");
        var origin = Origin(c.Url);
        var url = Controller(c, DemandwareControllers.CrowdTwistRegister);
        var headers = new Dictionary<string, string>
        {
            ["Referer"] = origin + "/fanrewards-join/",
            ["Origin"] = origin,
            ["X-Requested-With"] = "XMLHttpRequest",
        };

        var options = c.Options(Tag() + "-fan-signup");
        foreach (var kv in headers) options.Headers[kv.Key] = kv.Value;
        options.Content = new StringContent(string.Empty, System.Text.Encoding.UTF8, "application/x-www-form-urlencoded");

        NetResponse res;
        try
        {
            res = await c.Http.SendAsync(HttpMethod.Post, url, options, ct).ConfigureAwait(false);
            c.Session.AbsorbCookies(res.Cookies);
            c.Session.Vars["lastStatus"] = res.StatusCode.ToString();
            c.Session.Vars["lastUrl"] = res.Url.ToString();
        }
        catch (Exception ex)
        {
            c.Emit($"funko signup: {ex.Message}", "error");
            return StepOutcome.Fail("funko: rewards signup unreachable", retryable: true);
        }

        if (res.IsSuccess)
        {
            try
            {
                var ok = Newtonsoft.Json.Linq.JObject.Parse(res.Body)["success"]?.ToObject<bool?>() == true;
                if (ok)
                {
                    c.Session.Vars["fanRewards.signup"] = "registered";
                    c.Emit("Successfully Registered (Rewards)", "StatusInfo");
                    return StepOutcome.Success();
                }
            }
            catch { /* fall through to Signup Failed */ }
        }

        c.Session.Vars["fanRewards.signup"] = "failed";
        c.Emit("Signup Failed", "error");
        return StepOutcome.Fail("Signup Failed");
    }

    public override async Task<StepOutcome> CheckLoginAsync(FlowContext c, CancellationToken ct)
    {
        var mode = c.Session.Vars.GetValueOrDefault("funko.mode");
        if (string.Equals(mode, "check balance", StringComparison.OrdinalIgnoreCase))
            return await CheckFanRewardBalanceAsync(c, ct).ConfigureAwait(false);

        if (string.Equals(mode, "fan rewards state", StringComparison.OrdinalIgnoreCase))
            return await CheckFanRewardStateAsync(c, ct).ConfigureAwait(false);

        if (string.Equals(mode, "fan rewards signup", StringComparison.OrdinalIgnoreCase))
        {
            var state = await CheckFanRewardStateAsync(c, ct).ConfigureAwait(false);
            if (!state.Ok) return state;
            if (string.Equals(c.Session.Vars.GetValueOrDefault("fanRewards.state"), "already_signed_up",
                    StringComparison.Ordinal))
                return StepOutcome.Success();
            return await SignUpFanRewardsAsync(c, ct).ConfigureAwait(false);
        }

        return await base.CheckLoginAsync(c, ct).ConfigureAwait(false);
    }

    public override async Task<StepOutcome> SignUpAsync(FlowContext c, CancellationToken ct)
    {
        var state = await CheckFanRewardStateAsync(c, ct).ConfigureAwait(false);
        if (!state.Ok) return state;
        if (string.Equals(c.Session.Vars.GetValueOrDefault("fanRewards.state"), "already_signed_up",
                StringComparison.Ordinal))
            return StepOutcome.Success();
        return await SignUpFanRewardsAsync(c, ct).ConfigureAwait(false);
    }
}
