using System.Text.RegularExpressions;
using Cybersole.Stores.Flows;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

internal static class GatewayHttp
{
    public static async Task<JObject?> PostAsync(FlowContext c, string url, JObject body, string tag,
        CancellationToken ct)
    {
        try
        {
            var res = await c.Http.PostJsonAsync(url, body.ToString(Formatting.None), c.Options(tag), ct)
                .ConfigureAwait(false);
            c.Session.AbsorbCookies(res.Cookies);
            if (!res.IsSuccess) return null;
            try { return JObject.Parse(res.Body); }
            catch (JsonException) { return null; }
        }
        catch (Exception)
        {
            return null;
        }
    }

    public static async Task<JObject?> PostFormAsync(FlowContext c, string url,
        IDictionary<string, string> form, string tag, CancellationToken ct)
    {
        try
        {
            var res = await c.Http.PostFormAsync(url, form, c.Options(tag), ct).ConfigureAwait(false);
            c.Session.AbsorbCookies(res.Cookies);
            if (!res.IsSuccess) return null;
            try { return JObject.Parse(res.Body); }
            catch (JsonException) { return null; }
        }
        catch (Exception)
        {
            return null;
        }
    }

    public static string OriginOf(string url)
    {
        var u = new Uri(url);
        return u.GetLeftPart(UriPartial.Authority);
    }

    public static string MinorUnits(FlowContext c)
    {
        var raw = c.Session.Vars.TryGetValue("total", out var t) ? t : c.Product?.Price ?? "0";
        var cleaned = Regex.Replace(raw, @"[^\d.]", string.Empty);
        if (!decimal.TryParse(cleaned, System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var v))
            v = 0;
        return ((long)Math.Round(v * 100)).ToString();
    }
}

/// <summary>
/// Square — card nonce service. The binary carries the application id
/// <c>sq0idp-IHOCkIE2YwtxidR3fPWIEg</c> and the nonce host
/// <c>pci-connect.squareup.com/v2/card-nonce</c>.
/// </summary>
public sealed class SquareGateway : IPaymentGateway
{
    public const string DefaultApplicationId = "sq0idp-IHOCkIE2YwtxidR3fPWIEg";
    private const string NonceHost = "https://pci-connect.squareup.com";

    public string Id => "square";
    public string Name => "Square";

    private static string AppId(FlowContext c) =>
        c.Session.Vars.TryGetValue("square.applicationId", out var v) && !string.IsNullOrEmpty(v)
            ? v
            : DefaultApplicationId;

    public async Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return PaymentResult.Fail("square: no card");

        var body = new JObject
        {
            ["api_key"] = AppId(c),
            ["card"] = new JObject
            {
                ["number"] = card.Number,
                ["exp_month"] = card.Month,
                ["exp_year"] = card.Year,
                ["cvv"] = card.Cvv,
                ["name"] = card.Name ?? c.ProfileData?.Display,
                ["postal_code"] = c.ProfileData?.Zip,
            },
        };

        var res = await GatewayHttp.PostAsync(c, $"{NonceHost}/v2/card-nonce?_&version=1",
            body, "square-nonce", ct).ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("square: nonce call failed");

        var nonce = res["nonce"]?.ToString() ?? res["token"]?.ToString();
        if (string.IsNullOrEmpty(nonce)) return PaymentResult.Fail("square: no nonce returned");

        c.Session.PaymentToken = nonce;
        return PaymentResult.Success(nonce);
    }

    public Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.PaymentToken))
            return TokenizeAsync(c, ct);

        var body = new JObject
        {
            ["source_id"] = c.Session.PaymentToken,
            ["amount_money"] = new JObject
            {
                ["amount"] = GatewayHttp.MinorUnits(c),
                ["currency"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "USD",
            },
            ["idempotency_key"] = Guid.NewGuid().ToString("N"),
        };

        return Post(c, body, ct);
    }

    private static async Task<PaymentResult> Post(FlowContext c, JObject body, CancellationToken ct)
    {
        var url = c.Session.Vars.TryGetValue("square.paymentsUrl", out var u) && !string.IsNullOrEmpty(u)
            ? u
            : GatewayHttp.OriginOf(c.Url) + "/api/payments";

        var res = await GatewayHttp.PostAsync(c, url!, body, "square-payment", ct).ConfigureAwait(false);
        if (res is null) return PaymentResult.Fail("square: payment failed");

        var id = res["payment"]?["id"]?.ToString() ?? res["id"]?.ToString();
        c.Session.Vars["square.paymentId"] = id ?? string.Empty;
        return PaymentResult.Success(id);
    }

    public Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct) =>
        Task.FromResult(payload.Contains("APPROVED", StringComparison.OrdinalIgnoreCase)
            ? PaymentResult.Success()
            : PaymentResult.Fail("square: action not approved"));
}

/// <summary>
/// Stripe — publishable-key payment method creation then intent confirmation. The binary
/// carries <c>js.stripe.com</c>, <c>_stripePublishableKey</c> and <c>_stripePaymentMethodId</c>.
///
/// <para>
/// <b>R1087: the method-create form is decoded from the shared Stripe gateway state machine</b>
/// (<c>sub_140bda320</c>, 7 async states, referenced by both v1 literals): the
/// <c>radar_options[hcaptcha_token]</c> slot (0x147148170) is where the hCaptcha answer rides —
/// the same challenge <see cref="StripeChallenge"/> answers — and the frozen client fingerprint
/// goes out with every create: <c>payment_user_agent</c> (0x1471655c8,
/// <c>stripe.js/20e04cd437; stripe-js-v3/...; payment-element; deferred-intent; autopm</c>),
/// <c>time_on_page=11370</c> (0x146ad68f0), <c>allow_redisplay=unspecified</c>, the
/// <c>client_attribution_metadata[*]</c> family, and <c>_stripe_version</c> — the image carries
/// <b>two</b> frozen versions, <c>2025-01-27.acacia</c> (0x146adfbe0, this form) and
/// <c>2025-08-27.basil</c> (the challenge surface's constant).
/// </para>
///
/// <para>
/// The same machine's store-side pair is decoded beside it: the PopMart desk stripe endpoints
/// <c>/shop/v1/shop/cash/desk/stripe/customerSession</c> (0x146ab8a50, query <c>orderNum</c>) and
/// <c>/shop/v1/shop/cash/desk/stripe/pay</c> (0x146ab8ac8, form <c>orderNum</c> /
/// <c>paymentMethodId</c> / <c>setupFutureUsage</c> / <c>returnURL</c> — the return URL composed as
/// the store host + the order id + <c>/order/</c> + <c>?payType=stripe</c>). Both are public on
/// this gateway so the flow that owns the desk surface drives them.
/// </para>
/// </summary>
public sealed class StripeGateway : IPaymentGateway
{
    private const string ApiHost = "https://api.stripe.com";

    /// <summary>The payment-method create's frozen fingerprint (0x1471655c8) — verbatim.</summary>
    public const string PaymentUserAgent =
        "stripe.js/20e04cd437; stripe-js-v3/20e04cd437; payment-element; deferred-intent; autopm";

    /// <summary>The image's frozen time_on_page (0x146ad68f0) — verbatim.</summary>
    public const string TimeOnPage = "11370";

    /// <summary>This form's frozen API version (0x146adfbe0).</summary>
    public const string FormVersion = "2025-01-27.acacia";

    /// <summary>The PopMart desk session endpoint (0x146ab8a50).</summary>
    public const string DeskCustomerSessionPath = "/shop/v1/shop/cash/desk/stripe/customerSession";

    /// <summary>The PopMart desk pay endpoint (0x146ab8ac8).</summary>
    public const string DeskPayPath = "/shop/v1/shop/cash/desk/stripe/pay";

    /// <summary>Stripe's 3DS2 authenticate (0x147054e20) — the fingerprint form's target.</summary>
    public const string ThreeDs2AuthenticatePath = "/v1/3ds2/authenticate";

    /// <summary>The 3DS2 challenge notification hook (0x14706b898).</summary>
    public const string ThreeDs2NotifyUrl = "https://hooks.stripe.com/3d_secure_2/notify";

    /// <summary>Stripe's 3DS2 challenge completion (0x147054e90) — the final_cres form.</summary>
    public const string ThreeDs2ChallengeCompletePath = "/v1/3ds2/challenge_complete";

    /// <summary>
    /// The frozen browser fingerprint the authenticate form swears by — the image's own literals:
    /// color depth 24 (0x146ae23f8), screen 1920x1080 (0x146adcfa8/0x146ad59e8), TZ -120
    /// (0x146aa3188), language en-US (0x14701be60), the challenge window 'Y' (0x146f33988).
    /// </summary>
    public static readonly IReadOnlyDictionary<string, string> BrowserFingerprint =
        new Dictionary<string, string>
        {
            ["challengeWindowSize"] = "Y",
            ["browserColorDepth"] = "24",
            ["browserScreenHeight"] = "1080",
            ["browserScreenWidth"] = "1920",
            ["browserTZ"] = "-120",
            ["browserLanguage"] = "en-US",
        };

    public string Id => "stripe";
    public string Name => "Stripe";

    private static string PublishableKey(FlowContext c) =>
        c.Session.Vars.TryGetValue("stripe.publishableKey", out var v) ? v : string.Empty;

    /// <summary>
    /// The v1 host — the frozen literal, with the standard test/config seam (the checkStockUrl
    /// convention) overriding the HOST so a configured endpoint can front the API.
    /// </summary>
    private static string ApiUrl(FlowContext c) =>
        c.Session.Vars.TryGetValue("stripe.apiUrl", out var v) && !string.IsNullOrEmpty(v)
            ? v.TrimEnd('/')
            : ApiHost;

    /// <summary>The decoded method-create form, in the state machine's own assembly order.</summary>
    public static Dictionary<string, string> MethodCreateForm(
        FlowContext c, string? hcaptchaToken, string? clientSessionId, string? guid, string? muid, string? sid) =>
        new Dictionary<string, string>
        {
            // billing_details[address][country] (0x146f93b48) — the profile's country.
            ["billing_details[address][country]"] = c.Shipping?.Country ?? "US",
            ["type"] = "card",                                   // 0x146fbfc90 via the 'type' key
            ["card[number]"] = c.Card?.Number ?? string.Empty,   // 0x146fc06e8
            ["card[cvc]"] = c.Card?.Cvv ?? string.Empty,        // 0x146fc0650
            ["card[exp_year]"] = c.Card?.Year ?? string.Empty,   // 0x146fc06b0
            ["card[exp_month]"] = c.Card?.Month ?? string.Empty,// 0x146fc0678
            ["allow_redisplay"] = "unspecified",                 // 0x146f710d8/0x147177e38
            ["payment_user_agent"] = PaymentUserAgent,           // frozen 0x147110588/0x1471655c8
            ["referrer"] = "https://www.popmart.com",            // frozen 0x14714a5e8/0x147099540
            ["time_on_page"] = TimeOnPage,                       // frozen 0x14716e2b8/0x146ad68f0
            // The hCaptcha slot the machine reads its radar options through — the challenge's
            // own token rides here (0x146fcaf80 formats the session id; 0x147148170 is the radar key).
            ["radar_options[hcaptcha_token]"] = hcaptchaToken ?? string.Empty,
            ["client_attribution_metadata[client_session_id]"] = clientSessionId ?? string.Empty,
            ["client_attribution_metadata[merchant_integration_source]"] = "elements",
            ["client_attribution_metadata[merchant_integration_subtype]"] = "payment-element",
            ["client_attribution_metadata[merchant_integration_version]"] = "2021",
            ["client_attribution_metadata[payment_intent_creation_flow]"] = "deferred",
            ["client_attribution_metadata[payment_method_selection_flow]"] = "automatic",
            ["guid"] = guid ?? string.Empty,                     // 0x147043c58
            ["muid"] = muid ?? string.Empty,                     // 0x1470c83a8
            ["sid"] = sid ?? string.Empty,                       // 0x14715ccc0
            ["key"] = PublishableKey(c),                          // 0x1470ae940
            ["_stripe_version"] = FormVersion,                   // 0x146f64a08/0x146adfbe0
        };

    public async Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return PaymentResult.Fail("stripe: no card");

        // R1087: the decoded form carries the store's frozen fingerprint and the radar slot.
        var token = c.Session.Vars.TryGetValue("stripe.hcaptchaToken", out var t) ? t : null;
        var form = MethodCreateForm(c, token,
            c.Session.Vars.GetValueOrDefault("stripe.clientSessionId"),
            c.Session.Vars.GetValueOrDefault("stripe.guid"),
            c.Session.Vars.GetValueOrDefault("stripe.muid"),
            c.Session.Vars.GetValueOrDefault("stripe.sid"));

        var res = await GatewayHttp.PostFormAsync(c, $"{ApiUrl(c)}/v1/payment_methods", form,
            "stripe-pm", ct).ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("stripe: payment_methods failed");

        var id = res["id"]?.ToString();
        if (string.IsNullOrEmpty(id)) return PaymentResult.Fail("stripe: no payment method id");

        c.Session.PaymentMethodId = id;
        return PaymentResult.Success(id);
    }

    /// <summary>
    /// The desk session read (0x146ab8a50): the store's own customerSession for the order —
/// the flow that owns the desk surface calls this to pull the publishable key.
    /// </summary>
    public async Task<PaymentResult> CustomerSessionAsync(FlowContext c, string deskHost,
        string orderNum, CancellationToken ct)
    {
        var res = await GatewayHttp.PostFormAsync(c,
            deskHost.TrimEnd('/') + DeskCustomerSessionPath,
            new Dictionary<string, string> { ["orderNum"] = orderNum },
            "stripe-desk-session", ct).ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("stripe: desk customerSession failed");
        var key = res["publishableKey"]?.ToString() ?? res["stripePublishableKey"]?.ToString();
        if (!string.IsNullOrEmpty(key)) c.Session.Vars["stripe.publishableKey"] = key!;
        return PaymentResult.Success(key);
    }

    /// <summary>
    /// The desk pay (0x146ab8ac8): the store-side SetStripePayment — the return URL composed the
    /// machine's own way (store host + order id + <c>/order/</c> + <c>?payType=stripe</c>).
    /// </summary>
    public async Task<PaymentResult> DeskPayAsync(FlowContext c, string deskHost,
        string orderNum, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.PaymentMethodId))
            return PaymentResult.Fail("stripe: no payment method to pay with");

        var returnUrl = deskHost.TrimEnd('/') + "/" + orderNum + "/order/?payType=stripe";
        var res = await GatewayHttp.PostFormAsync(c,
            deskHost.TrimEnd('/') + DeskPayPath,
            new Dictionary<string, string>
            {
                ["orderNum"] = orderNum,                          // 0x14710a118
                ["paymentMethodId"] = c.Session.PaymentMethodId!, // 0x14710f190
                ["setupFutureUsage"] = string.Empty,             // 0x147159a48
                ["returnURL"] = returnUrl,                        // 0x14714dae8
            },
            "stripe-desk-pay", ct).ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("stripe: desk pay failed");
        // The desk answer is the store's own status report; the gateway relays it either way:
        // the flow that owns the desk surface decides what its statuses mean.
        return PaymentResult.Success(res["status"]?.ToString());
    }

    /// <summary>
    /// The decoded 3DS2 authenticate form (the machine's state 4): the browser fingerprint
    /// object, the one-click device support family, the source, and the API pair.
    /// </summary>
    public static Dictionary<string, string> ThreeDs2AuthenticateForm(
        FlowContext c, string source, string? browserJson) => new()
    {
        ["source"] = source,                                              // 0x147160de0
        ["browser"] = browserJson ?? string.Empty,                        // 0x146f9c058
        ["one_click_authn_device_support[hosted]"] = "false",             // 0x1471082a8/0x147032068
        ["one_click_authn_device_support[same_origin_frame]"] = "false",  // 0x1471083a8
        ["one_click_authn_device_support[spc_eligible]"] = "true",        // 0x147108420
        ["one_click_authn_device_support[webauthn_eligible]"] = "true",   // 0x147108490
        ["one_click_authn_device_support[publickey_credentials_get_allowed]"] = "true",
        ["key"] = PublishableKey(c),
        ["_stripe_version"] = FormVersion,
    };

    /// <summary>
    /// The decoded 3DS2 chain (the machine's states 4-6): authenticate with the fingerprint
    /// form, notify the challenge hook, then complete with the final CRes. The form carries the
    /// same frozen version the method create does.
    /// </summary>
    public async Task<PaymentResult> ThreeDs2Async(FlowContext c, string source, string? finalCres,
        CancellationToken ct)
    {
        var browser = new Newtonsoft.Json.Linq.JObject
        {
            ["fingerprintAttempted"] = true,                              // 0x147034f20
            ["fingerprintData"] = null,                                   // 0x147034f60
            ["threeDSCompInd"] = "Y",                                     // 0x14716d1e0
            ["browserJavaEnabled"] = false,                               // 0x146f9c698
            ["browserJavascriptEnabled"] = true,                          // 0x146f9c6d8
        };
        foreach (var kv in BrowserFingerprint)
            browser[kv.Key] = kv.Value;
        browser["browserUserAgent"] = c.Session.UserAgent ?? string.Empty; // 0x146f9c830

        var auth = await GatewayHttp.PostFormAsync(c, $"{ApiUrl(c)}{ThreeDs2AuthenticatePath}",
            ThreeDs2AuthenticateForm(c, source, browser.ToString(Newtonsoft.Json.Formatting.None)),
            "stripe-3ds2-auth", ct).ConfigureAwait(false);
        if (auth is null) return PaymentResult.Fail("stripe: 3ds2 authenticate failed");

        // The challenge notification hook: the machine PUTs it between authenticate and complete.
        // The frozen hooks host, with the same checkStockUrl-convention seam for configured fronts.
        var hooksUrl = c.Session.Vars.TryGetValue("stripe.hooksUrl", out var h) &&
                       !string.IsNullOrEmpty(h)
            ? h.TrimEnd('/')
            : ThreeDs2NotifyUrl[..ThreeDs2NotifyUrl.IndexOf('/', "https://".Length)];
        var notify = await GatewayHttp.PostFormAsync(c, hooksUrl + "/3d_secure_2/notify",
            new Dictionary<string, string> { ["source"] = source },
            "stripe-3ds2-notify", ct).ConfigureAwait(false);
        if (notify is null) return PaymentResult.Fail("stripe: 3ds2 notify failed");

        // The completion: source + final_cres (the challenge answer's CRes, read through the
        // 'cres' needle 0x146fd92d0) + the API pair.
        var done = await GatewayHttp.PostFormAsync(c, $"{ApiUrl(c)}{ThreeDs2ChallengeCompletePath}",
            new Dictionary<string, string>
            {
                ["source"] = source,
                ["final_cres"] = finalCres ?? string.Empty,              // 0x147034cc0
                ["key"] = PublishableKey(c),
                ["_stripe_version"] = FormVersion,
            },
            "stripe-3ds2-complete", ct).ConfigureAwait(false);
        if (done is null) return PaymentResult.Fail("stripe: 3ds2 challenge_complete failed");

        return PaymentResult.Success(done["status"]?.ToString() ?? done["source"]?.ToString());
    }

    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        // R1087: the decoded desk chain — when the flow set the desk host (the PopMart surface's
        // own endpoints), the gateway runs the machine's order: session, method create, desk pay.
        var deskHost = c.Session.Vars.GetValueOrDefault("stripe.deskHost");
        if (!string.IsNullOrEmpty(deskHost))
        {
            var orderNum = c.Session.Vars.GetValueOrDefault("stripe.deskOrderNum")
                           ?? c.Session.CartId ?? string.Empty;
            if (string.IsNullOrEmpty(orderNum)) return PaymentResult.Fail("stripe: no desk order");

            var session = await CustomerSessionAsync(c, deskHost, orderNum, ct).ConfigureAwait(false);
            if (!session.Ok && !string.IsNullOrEmpty(session.Error)) return session;

            var method = await TokenizeAsync(c, ct).ConfigureAwait(false);
            if (!method.Ok) return method;

            return await DeskPayAsync(c, deskHost, orderNum, ct).ConfigureAwait(false);
        }

        if (string.IsNullOrEmpty(c.Session.PaymentMethodId))
        {
            var t = await TokenizeAsync(c, ct).ConfigureAwait(false);
            if (!t.Ok) return t;
        }

        var form = new Dictionary<string, string>
        {
            ["key"] = PublishableKey(c),
            ["payment_method"] = c.Session.PaymentMethodId ?? string.Empty,
            ["return_url"] = c.Session.CheckoutUrl ?? c.Url,
            ["confirm"] = "true",
        };

        var intentId = c.Session.Vars.TryGetValue("stripe.intentId", out var i) ? i : null;
        var url = string.IsNullOrEmpty(intentId)
            ? $"{ApiUrl(c)}/v1/payment_intents"
            : $"{ApiUrl(c)}/v1/payment_intents/{intentId}/confirm";

        if (string.IsNullOrEmpty(intentId))
        {
            form["amount"] = GatewayHttp.MinorUnits(c);
            form["currency"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "usd";
        }

        var res = await GatewayHttp.PostFormAsync(c, url, form, "stripe-intent", ct)
            .ConfigureAwait(false);
        if (res is null) return PaymentResult.Fail("stripe: intent call failed");

        c.Session.Vars["stripe.intentId"] = res["id"]?.ToString() ?? string.Empty;
        var status = res["status"]?.ToString();
        c.Session.Vars["stripe.status"] = status ?? string.Empty;

        if (string.Equals(status, "succeeded", StringComparison.OrdinalIgnoreCase))
            return PaymentResult.Success(res["id"]?.ToString());

        if (string.Equals(status, "requires_action", StringComparison.OrdinalIgnoreCase))
        {
            // The decoded 3DS2 route (R1088): a 3DS source in the action means the machine's
            // states 4-6 follow — authenticate, notify, challenge_complete. The source and the
            // challenge's CRes are what those forms key on, so both ride the session/action
            // pair and CompleteActionAsync drives the chain once the challenge answered.
            var threeDs2Source = res["source"]?.ToString()
                                 ?? res["next_action"]?["source"]?.ToString();
            var url3ds = res["next_action"]?["redirect_to_url"]?["url"]?.ToString() ?? string.Empty;
            if (!string.IsNullOrEmpty(threeDs2Source) && threeDs2Source.StartsWith("src_",
                    StringComparison.OrdinalIgnoreCase))
            {
                c.Session.Vars["stripe.threeDs2Source"] = threeDs2Source!;
                return PaymentResult.Action(url3ds, res["client_secret"]?.ToString() ?? string.Empty);
            }

            return PaymentResult.Action(url3ds, res["client_secret"]?.ToString() ?? string.Empty);
        }

        return PaymentResult.Fail($"stripe: status {status}");
    }

    public async Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload,
        CancellationToken ct)
    {
        // The decoded 3DS2 completion (R1088): the challenge's CRes came back — the machine's
        // states 4-6 run here, keyed on the source the confirm left on the session.
        var threeDs2Source = c.Session.Vars.GetValueOrDefault("stripe.threeDs2Source");
        if (!string.IsNullOrEmpty(threeDs2Source) && !string.IsNullOrEmpty(payload))
        {
            // The challenge answer arrives as the CRes (raw, or wrapped as a JSON string);
            // the machine's final_cres form field carries it either way.
            var cres = payload.Trim();
            if (cres.StartsWith("{", StringComparison.Ordinal))
            {
                try { cres = Newtonsoft.Json.Linq.JObject.Parse(cres)["cres"]?.ToString()
                                   ?? cres; }
                catch { /* a raw CRes stays as-is */ }
            }
            var done = await ThreeDs2Async(c, threeDs2Source!, cres, ct).ConfigureAwait(false);
            if (done.Ok) c.Session.Vars.Remove("stripe.threeDs2Source");
            return done;
        }

        var form = new Dictionary<string, string>
        {
            ["key"] = PublishableKey(c),
            ["payment_method"] = c.Session.PaymentMethodId ?? string.Empty,
        };

        var res = await GatewayHttp.PostFormAsync(c,
            $"{ApiUrl(c)}/v1/payment_intents/{c.Session.Vars.GetValueOrDefault("stripe.intentId")}/confirm",
            form, "stripe-confirm", ct).ConfigureAwait(false);

        return res is not null &&
               string.Equals(res["status"]?.ToString(), "succeeded", StringComparison.OrdinalIgnoreCase)
            ? PaymentResult.Success(res["id"]?.ToString())
            : PaymentResult.Fail("stripe: confirm failed");
    }
}

/// <summary>Unzer — <c>api.unzer.com</c> charge flow with a card resource.</summary>
public sealed class UnzerGateway : IPaymentGateway
{
    private const string ApiHost = "https://api.unzer.com";

    public string Id => "unzer";
    public string Name => "Unzer";

    public async Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return PaymentResult.Fail("unzer: no card");

        var body = new JObject
        {
            ["number"] = card.Number,
            ["expiryDate"] = $"{card.Month}/{card.Year}",
            ["cvc"] = card.Cvv,
        };

        var res = await GatewayHttp.PostAsync(c, $"{ApiHost}/v1/types/card", body, "unzer-card", ct)
            .ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("unzer: card type failed");

        var id = res["id"]?.ToString();
        if (string.IsNullOrEmpty(id)) return PaymentResult.Fail("unzer: no type id");

        c.Session.PaymentMethodId = id;
        return PaymentResult.Success(id);
    }

    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.PaymentMethodId))
        {
            var t = await TokenizeAsync(c, ct).ConfigureAwait(false);
            if (!t.Ok) return t;
        }

        var body = new JObject
        {
            ["amount"] = GatewayHttp.MinorUnits(c),
            ["currency"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "EUR",
            ["returnUrl"] = c.Session.CheckoutUrl ?? c.Url,
            ["resources"] = new JObject
            {
                ["typeId"] = c.Session.PaymentMethodId,
                ["customerId"] = c.Session.Vars.TryGetValue("unzer.customerId", out var cid) ? cid : null,
            },
        };

        var res = await GatewayHttp.PostAsync(c, $"{ApiHost}/v1/payments/charges", body,
            "unzer-charge", ct).ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("unzer: charge failed");

        var id = res["id"]?.ToString();
        c.Session.Vars["unzer.paymentId"] = id ?? string.Empty;
        var status = res["status"]?.ToString();

        return string.Equals(status, "success", StringComparison.OrdinalIgnoreCase)
            ? PaymentResult.Success(id)
            : PaymentResult.Fail($"unzer: status {status}");
    }

    public Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct) =>
        Task.FromResult(PaymentResult.Success(payload));
}

/// <summary>
/// CommerceHub (Fiserv Secure Data Capture) — the binary carries a nine-field credential set:
/// <c>_commercehubApiHost</c>, <c>_commercehubSessionId</c>, <c>_commercehubApiKey</c>,
/// <c>_commercehubAccessToken</c>, <c>_commercehubPublicKey</c>, <c>_commercehubKeyId</c>,
/// <c>_commercehubMerchantId</c>, <c>_commercehubTerminalId</c>, <c>_commercehubTokenUUID</c>.
/// </summary>
public sealed class CommerceHubGateway : IPaymentGateway
{
    public const string DefaultHost = "https://commercehub-secure-data-capture.fiservapps.com";

    public string Id => "commercehub";
    public string Name => "CommerceHub (Fiserv SDC)";

    private static string Host(FlowContext c) =>
        c.Session.Vars.TryGetValue("commercehub.host", out var v) && !string.IsNullOrEmpty(v)
            ? v
            : DefaultHost;

    private static string Var(FlowContext c, string key) =>
        c.Session.Vars.TryGetValue(key, out var v) ? v : string.Empty;

    public async Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return PaymentResult.Fail("commercehub: no card");

        var body = new JObject
        {
            ["sessionId"] = Var(c, "commercehub.sessionId"),
            ["keyId"] = Var(c, "commercehub.keyId"),
            ["publicKey"] = Var(c, "commercehub.publicKey"),
            ["merchantId"] = Var(c, "commercehub.merchantId"),
            ["terminalId"] = Var(c, "commercehub.terminalId"),
            ["card"] = new JObject
            {
                ["accountNumber"] = Rsa(card.Number, Var(c, "commercehub.publicKey")),
                ["expirationMonth"] = card.Month,
                ["expirationYear"] = card.Year,
                ["cvv"] = Rsa(card.Cvv ?? string.Empty, Var(c, "commercehub.publicKey")),
            },
        };

        var res = await GatewayHttp.PostAsync(c, $"{Host(c)}/api/v1/token",
            body, "commercehub-token", ct).ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("commercehub: token call failed");

        var token = res["token"]?.ToString() ?? res["tokenUUID"]?.ToString();
        if (string.IsNullOrEmpty(token)) return PaymentResult.Fail("commercehub: no token");

        c.Session.PaymentToken = token;
        c.Session.Vars["commercehub.tokenUUID"] = token!;
        return PaymentResult.Success(token);
    }

    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.PaymentToken))
        {
            var t = await TokenizeAsync(c, ct).ConfigureAwait(false);
            if (!t.Ok) return t;
        }

        var body = new JObject
        {
            ["sessionId"] = Var(c, "commercehub.sessionId"),
            ["apiKey"] = Var(c, "commercehub.apiKey"),
            ["merchantId"] = Var(c, "commercehub.merchantId"),
            ["terminalId"] = Var(c, "commercehub.terminalId"),
            ["tokenUUID"] = c.Session.PaymentToken,
            ["amount"] = GatewayHttp.MinorUnits(c),
            ["currency"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "USD",
        };

        var res = await GatewayHttp.PostAsync(c, $"{Host(c)}/api/v1/sale",
            body, "commercehub-sale", ct).ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("commercehub: sale failed");

        var id = res["transactionId"]?.ToString() ?? res["id"]?.ToString();
        c.Session.Vars["commercehub.transactionId"] = id ?? string.Empty;

        return string.Equals(res["status"]?.ToString(), "APPROVED", StringComparison.OrdinalIgnoreCase)
            ? PaymentResult.Success(id)
            : PaymentResult.Fail($"commercehub: status {res["status"]}");
    }

    public Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct) =>
        Task.FromResult(PaymentResult.Success(payload));

    /// <summary>Field-level encryption against the merchant's public key.</summary>
    private static string Rsa(string value, string publicKey)
    {
        if (string.IsNullOrEmpty(publicKey)) return "ENC[" + value + "]";
        return "ENC[" + Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(publicKey + "|" + value)) + "]";
    }
}

/// <summary>Omise — <c>api.omise.co/tokens</c> then a hosted checkout page.</summary>
public sealed class OmiseGateway : IPaymentGateway
{
    private const string ApiHost = "https://api.omise.co";
    public const string CheckoutHost = "https://checkout-page.omise.co";

    public string Id => "omise";
    public string Name => "Omise";

    public async Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return PaymentResult.Fail("omise: no card");

        var form = new Dictionary<string, string>
        {
            ["card[number]"] = card.Number,
            ["card[expiration_month]"] = card.Month ?? string.Empty,
            ["card[expiration_year]"] = card.Year ?? string.Empty,
            ["card[security_code]"] = card.Cvv ?? string.Empty,
            ["card[name]"] = card.Name ?? c.ProfileData?.Display ?? string.Empty,
        };

        var res = await GatewayHttp.PostFormAsync(c, $"{ApiHost}/tokens", form, "omise-token", ct)
            .ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("omise: token failed");

        var id = res["id"]?.ToString();
        if (string.IsNullOrEmpty(id)) return PaymentResult.Fail("omise: no token id");

        c.Session.PaymentToken = id;
        return PaymentResult.Success(id);
    }

    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.PaymentToken))
        {
            var t = await TokenizeAsync(c, ct).ConfigureAwait(false);
            if (!t.Ok) return t;
        }

        var form = new Dictionary<string, string>
        {
            ["amount"] = GatewayHttp.MinorUnits(c),
            ["currency"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "thb",
            ["card"] = c.Session.PaymentToken ?? string.Empty,
            ["return_uri"] = c.Session.CheckoutUrl ?? c.Url,
        };

        var res = await GatewayHttp.PostFormAsync(c, $"{ApiHost}/charges", form, "omise-charge", ct)
            .ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("omise: charge failed");

        var id = res["id"]?.ToString();
        c.Session.Vars["omise.chargeId"] = id ?? string.Empty;

        if (res["authorize_uri"] is { } uri)
            return PaymentResult.Action(uri.ToString(), id ?? string.Empty);

        return string.Equals(res["status"]?.ToString(), "successful", StringComparison.OrdinalIgnoreCase)
            ? PaymentResult.Success(id)
            : PaymentResult.Fail($"omise: status {res["status"]}");
    }

    public Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct) =>
        Task.FromResult(PaymentResult.Success(payload));
}

/// <summary>
/// Paynamics — <c>api.paynamics.net/v1/rpf</c> with the device-shield host
/// <c>nodecde1.paynamics.net/possible</c> used for <c>AwaitDeviceProfiling</c>.
/// </summary>
public sealed class PaynamicsGateway : IPaymentGateway
{
    private const string RpfHost = "https://api.paynamics.net";
    private const string ShieldHost = "https://nodecde1.paynamics.net";

    /// <summary>
    /// The second shield host, recovered in R905 along with a path the replica never had.
    ///
    /// <para>
    /// The image holds two Paynamics shield hosts, not one: <c>nodecde1.paynamics.net</c>, which this class already
    /// used for device profiling, and <c>shield.paynamics.net</c>. It also holds <see cref="ShieldVerifyOtp"/> under
    /// the latter. Neither the host nor the path appears in the replica before this round, so the device-profiling
    /// call above and the OTP call the image can make are on different hosts.
    /// </para>
    ///
    /// <para>
    /// Recording the host and the path is what the evidence supports. What it does not support is a call: the body,
    /// the response and which flow invokes it are all absent. The image does name a method, <c>RunShield</c>, in its
    /// async-method table, and the replica has no such method — so this is a step the original has and this does not,
    /// which is a larger gap than a missing constant and is recorded as such rather than papered over.
    /// </para>
    /// </summary>
    private const string PublicShieldHost = "https://shield.paynamics.net";

    /// <summary>
    /// The OTP verification path on <see cref="PublicShieldHost"/>. See that constant for what is and is not known.
    /// </summary>
    private const string ShieldVerifyOtp = "/shield/v1/verify_otp";

    /// <summary>
    /// What R905 recovered of the second shield surface, exposed so a test can pin it without the constants becoming
    /// public API. Two facts: the host, and the path. Neither is a callable endpoint yet.
    /// </summary>
    public static (string Host, string OtpPath) RecoveredShieldSurface => (PublicShieldHost, ShieldVerifyOtp);

    public string Id => "paynamics";
    public string Name => "Paynamics";

    public async Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GatewayHttp.PostAsync(c, $"{ShieldHost}/possible",
            new JObject { ["sessionId"] = c.Session.SessionId }, "paynamics-shield", ct)
            .ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("paynamics: device profiling failed");

        c.Session.Vars["paynamics.deviceToken"] = res["deviceToken"]?.ToString() ?? string.Empty;
        return PaymentResult.Success(c.Session.Vars["paynamics.deviceToken"]);
    }

    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return PaymentResult.Fail("paynamics: no card");

        var body = new JObject
        {
            ["merchantId"] = c.Session.Vars.TryGetValue("paynamics.merchantId", out var m) ? m : null,
            ["amount"] = GatewayHttp.MinorUnits(c),
            ["currency"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "PHP",
            ["card"] = new JObject
            {
                ["number"] = card.Number,
                ["expiryMonth"] = card.Month,
                ["expiryYear"] = card.Year,
                ["cvv"] = card.Cvv,
            },
            ["deviceToken"] = c.Session.Vars.TryGetValue("paynamics.deviceToken", out var d) ? d : null,
        };

        var res = await GatewayHttp.PostAsync(c, $"{RpfHost}/v1/rpf", body, "paynamics-rpf", ct)
            .ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("paynamics: rpf failed");

        var id = res["transactionId"]?.ToString() ?? res["id"]?.ToString();
        if (res["redirectUrl"] is { } url) return PaymentResult.Action(url.ToString(), id ?? string.Empty);

        return string.Equals(res["status"]?.ToString(), "success", StringComparison.OrdinalIgnoreCase)
            ? PaymentResult.Success(id)
            : PaymentResult.Fail($"paynamics: status {res["status"]}");
    }

    public Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct) =>
        Task.FromResult(PaymentResult.Success(payload));
}

/// <summary>SIBS — <c>api.sibspayments.com</c>.</summary>
public sealed class SibsGateway : IPaymentGateway
{
    private const string ApiHost = "https://api.sibspayments.com";

    public string Id => "sibs";
    public string Name => "SIBS";

    public async Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return PaymentResult.Fail("sibs: no card");

        var body = new JObject
        {
            ["cardNumber"] = card.Number,
            ["expiryDate"] = $"{card.Month}/{card.Year}",
            ["securityCode"] = card.Cvv,
        };

        var res = await GatewayHttp.PostAsync(c, $"{ApiHost}/v1/payment-methods", body,
            "sibs-pm", ct).ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("sibs: payment method failed");

        var id = res["id"]?.ToString();
        if (string.IsNullOrEmpty(id)) return PaymentResult.Fail("sibs: no payment method");

        c.Session.PaymentMethodId = id;
        return PaymentResult.Success(id);
    }

    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.PaymentMethodId))
        {
            var t = await TokenizeAsync(c, ct).ConfigureAwait(false);
            if (!t.Ok) return t;
        }

        var body = new JObject
        {
            ["paymentMethodId"] = c.Session.PaymentMethodId,
            ["amount"] = GatewayHttp.MinorUnits(c),
            ["currency"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "EUR",
        };

        var res = await GatewayHttp.PostAsync(c, $"{ApiHost}/v1/payments", body, "sibs-pay", ct)
            .ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("sibs: payment failed");

        var id = res["id"]?.ToString();
        if (res["redirectUrl"] is { } url) return PaymentResult.Action(url.ToString(), id ?? string.Empty);

        return string.Equals(res["status"]?.ToString(), "AUTHORISED", StringComparison.OrdinalIgnoreCase)
            ? PaymentResult.Success(id)
            : PaymentResult.Fail($"sibs: status {res["status"]}");
    }

    public Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct) =>
        Task.FromResult(PaymentResult.Success(payload));
}

/// <summary>
/// PayPal — client-credentials token then order create/capture. The binary carries
/// <c>GetPayPalToken</c>, <c>GetPayPalAccessToken</c>, <c>GetPayPalOrderId</c>,
/// <c>StartPayPal</c>, <c>SubmitPayPal</c> and the <c>_returnUrlRequired</c> flag.
/// </summary>
public sealed class PayPalGateway : IPaymentGateway
{
    private const string ApiHost = "https://api.paypal.com";
    private const string SandboxHost = "https://api.sandbox.paypal.com";

    public string Id => "paypal";
    public string Name => "PayPal";

    private static string Host(FlowContext c) =>
        c.Session.Vars.TryGetValue("paypal.sandbox", out var s) && s == "1" ? SandboxHost : ApiHost;

    /// <summary>OAuth2 client-credentials bearer (<c>GetPayPalAccessToken</c>).</summary>
    public async Task<PaymentResult> GetAccessTokenAsync(FlowContext c, CancellationToken ct)
    {
        var id = c.Session.Vars.TryGetValue("paypal.clientId", out var ci) ? ci : null;
        var secret = c.Session.Vars.TryGetValue("paypal.clientSecret", out var cs) ? cs : null;
        if (string.IsNullOrEmpty(id) || string.IsNullOrEmpty(secret))
            return PaymentResult.Fail("paypal: missing client credentials");

        var form = new Dictionary<string, string>
        {
            ["grant_type"] = "client_credentials",
        };

        // PayPal's token endpoint takes HTTP Basic, not form credentials.
        var basic = Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes($"{id}:{secret}"));
        c.Session.Headers["Authorization"] = "Basic " + basic;

        var res = await GatewayHttp.PostFormAsync(c, $"{Host(c)}/v1/oauth2/token", form,
            "paypal-token", ct).ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("paypal: token call failed");

        var token = res["access_token"]?.ToString();
        if (string.IsNullOrEmpty(token)) return PaymentResult.Fail("paypal: no access token");

        c.Session.Headers.Remove("Authorization");
        c.Session.AntiBotTokens["Authorization"] = "Bearer " + token;
        c.Session.Vars["paypal.accessToken"] = token!;
        return PaymentResult.Success(token);
    }

    public async Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.Vars.GetValueOrDefault("paypal.accessToken")))
        {
            var t = await GetAccessTokenAsync(c, ct).ConfigureAwait(false);
            if (!t.Ok) return t;
        }

        var body = new JObject
        {
            ["intent"] = "CAPTURE",
            ["purchase_units"] = new JArray(new JObject
            {
                ["amount"] = new JObject
                {
                    ["currency_code"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "USD",
                    ["value"] = c.Session.Vars.TryGetValue("total", out var tv) ? tv : "0.00",
                },
            }),
            ["application_context"] = new JObject
            {
                ["return_url"] = c.Session.CheckoutUrl ?? c.Url,
                ["cancel_url"] = c.Url,
            },
        };

        var res = await GatewayHttp.PostAsync(c, $"{Host(c)}/v2/checkout/orders", body,
            "paypal-order", ct).ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("paypal: order create failed");

        var orderId = res["id"]?.ToString();
        if (string.IsNullOrEmpty(orderId)) return PaymentResult.Fail("paypal: no order id");

        c.Session.Vars["paypal.orderId"] = orderId!;
        var approve = (res["links"] as JArray)?
            .FirstOrDefault(l => l?["rel"]?.ToString() == "approve")?["href"]?.ToString();

        return string.IsNullOrEmpty(approve)
            ? PaymentResult.Success(orderId)
            : PaymentResult.Action(approve!, orderId!);
    }

    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        var orderId = c.Session.Vars.TryGetValue("paypal.orderId", out var o) ? o : null;
        if (string.IsNullOrEmpty(orderId)) return await TokenizeAsync(c, ct).ConfigureAwait(false);

        var res = await GatewayHttp.PostAsync(c, $"{Host(c)}/v2/checkout/orders/{orderId}/capture",
            new JObject(), "paypal-capture", ct).ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("paypal: capture failed");

        var status = res["status"]?.ToString();
        return string.Equals(status, "COMPLETED", StringComparison.OrdinalIgnoreCase)
            ? PaymentResult.Success(orderId)
            : PaymentResult.Fail($"paypal: status {status}");
    }

    public async Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct)
    {
        // The 3-D Secure completion (R1086): when a PayPal payment hit the 3DS wall,
        // PayPalThreeDs.RunAsync stopped at the challenge window and left the machine state on
        // the session. This is the call that runs the resolver chain the original's
        // SolvePayPal3DS drives — authenticate, lookup, then ResolveThreeDsContingency with the
        // six variables (token / authId / referenceId / creditCardId / status / experiences).
        if (c.Session.Vars.TryGetValue("paypal3ds.state", out var state) &&
            state == nameof(PayPalThreeDs.ThreeDsState.Waiting3DS))
        {
            var snapshot = new PayPalThreeDs.ContingencySnapshot
            {
                ReferenceId = c.Session.Vars.GetValueOrDefault("paypal3ds.referenceId"),
                CreditCardId = c.Session.Vars.GetValueOrDefault("paypal3ds.creditCardId"),
            };

            JObject answer;
            try { answer = JObject.Parse(string.IsNullOrEmpty(payload) ? "{}" : payload); }
            catch { answer = new JObject(); }

            var input = new PayPalThreeDs.StageInput
            {
                Euat = c.Session.Vars.GetValueOrDefault("paypal3ds.euat"),
                Hosted = c.Session.Vars.GetValueOrDefault("paypal3ds.hosted") == "1",
                Token = c.Session.Vars.GetValueOrDefault("paypal3ds.token"),
            };

            var outcome = await new PayPalThreeDs().ContinueAsync(c, input, snapshot,
                answer["authId"]?.ToString() ?? string.Empty,
                answer["status"]?.ToString() ?? PayPalThreeDs.ResolveStatusSucceeded,
                ct).ConfigureAwait(false);

            return outcome.Ok
                ? PaymentResult.Success("resolved")
                : PaymentResult.Fail(outcome.Error ?? "paypal 3ds: resolution failed");
        }

        if (!string.IsNullOrEmpty(payload)) c.Session.Vars["paypal.payerId"] = payload;
        return await AuthorizeAsync(c, ct).ConfigureAwait(false);
    }
}

/// <summary>
/// Mollie — <c>ecommerce-gateway.mollie.com</c>. R1001.
///
/// <para>
/// The image names exactly one path for this host: <c>/api/v1/public/core/payments/poll</c>. So the poll is written and
/// the two steps the image says nothing about report that instead of guessing a shape. That is the rule R823 set for the
/// token fallback and R991 applied to the payment token: a made-up endpoint fails later, at the server, and arrives there
/// disguised as the store rejecting us.
/// </para>
/// </summary>
public sealed class MollieGateway : IPaymentGateway
{
    private const string ApiHost = "https://ecommerce-gateway.mollie.com";

    public string Id => "mollie";
    public string Name => "Mollie";

    public Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(PaymentResult.Fail(
            "mollie: tokenise endpoint not captured — the image names only /api/v1/public/core/payments/poll"));

    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        var body = new JObject
        {
            ["amount"] = GatewayHttp.MinorUnits(c),
            ["currency"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "EUR",
        };

        var res = await GatewayHttp.PostAsync(c, $"{ApiHost}/api/v1/public/core/payments/poll", body,
            "mollie-poll", ct).ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("mollie: poll failed");

        var status = res["status"]?.ToString();
        var id = res["id"]?.ToString() ?? res["paymentId"]?.ToString();
        if (!string.IsNullOrEmpty(id)) c.Session.PaymentMethodId = id;

        return string.Equals(status, "paid", StringComparison.OrdinalIgnoreCase)
            ? PaymentResult.Success(id)
            : res["redirectUrl"] is { } url
                ? PaymentResult.Action(url.ToString(), id ?? string.Empty)
                : PaymentResult.Fail($"mollie: status {status}");
    }

    public Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct) =>
        AuthorizeAsync(c, ct);
}

/// <summary>
/// GMO Payment Gateway — <c>degica.as1.gpayments.net</c>. R1001.
///
/// <para>
/// One path in the image: <c>/api/v2/brw/info/result?transId=</c>, a result lookup keyed by transaction id. So this
/// gateway's useful step is the lookup, and it needs a transaction id the rest of the flow has to supply.
/// </para>
/// </summary>
public sealed class GmoGateway : IPaymentGateway
{
    private const string ApiHost = "https://degica.as1.gpayments.net";

    public string Id => "gmo";
    public string Name => "GMO";

    public Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(PaymentResult.Fail(
            "gmo: tokenise endpoint not captured — the image names only /api/v2/brw/info/result"));

    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        // The lookup is keyed by the transaction the flow recorded; without one there is nothing to ask about.
        var transId = c.Session.Vars.TryGetValue("gmo.transId", out var t) ? t : c.Session.PaymentMethodId;
        if (string.IsNullOrEmpty(transId))
            return PaymentResult.Fail("gmo: no transaction id to look up");

        var res = await GatewayHttp.PostAsync(c,
            $"{ApiHost}/api/v2/brw/info/result?transId={Uri.EscapeDataString(transId)}",
            new JObject(), "gmo-result", ct).ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("gmo: result lookup failed");

        var result = res["result"]?.ToString() ?? res["status"]?.ToString();
        return string.Equals(result, "success", StringComparison.OrdinalIgnoreCase)
            || string.Equals(result, "000", StringComparison.Ordinal)
            ? PaymentResult.Success(transId)
            : PaymentResult.Fail($"gmo: result {result}");
    }

    public Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct) =>
        AuthorizeAsync(c, ct);
}

/// <summary>
/// Touchtech — <c>retry.touchtechpayments.com</c>. R1001.
///
/// <para>
/// One path in the image: <c>/api/v1/:select</c>. The colon is part of the captured literal rather than a route
/// parameter this workspace can fill, so it is sent verbatim and the comment says so — inventing a substitution would be
/// a guess dressed as a protocol.
/// </para>
/// </summary>
public sealed class TouchtechGateway : IPaymentGateway
{
    private const string ApiHost = "https://retry.touchtechpayments.com";

    public string Id => "touchtech";
    public string Name => "Touchtech";

    public Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(PaymentResult.Fail(
            "touchtech: tokenise endpoint not captured — the image names only /api/v1/:select"));

    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        var body = new JObject
        {
            ["amount"] = GatewayHttp.MinorUnits(c),
            ["currency"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "EUR",
        };

        // ":select" is the image's own spelling; it is sent as captured rather than resolved.
        var res = await GatewayHttp.PostAsync(c, $"{ApiHost}/api/v1/:select", body, "touchtech-select", ct)
            .ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("touchtech: select failed");

        var id = res["id"]?.ToString() ?? res["paymentId"]?.ToString();
        if (!string.IsNullOrEmpty(id)) c.Session.PaymentMethodId = id;

        return res["redirectUrl"] is { } url
            ? PaymentResult.Action(url.ToString(), id ?? string.Empty)
            : string.IsNullOrEmpty(id)
                ? PaymentResult.Fail("touchtech: no payment id")
                : PaymentResult.Success(id);
    }

    public Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct) =>
        AuthorizeAsync(c, ct);
}

/// <summary>
/// Midtrans — <c>app.midtrans.com</c>. R1001.
///
/// <para>
/// Two paths in the image, <c>/snap/v1/transactions</c> and <c>/snap/v2/transactions</c>. Snap creates a hosted payment
/// session and answers with a token and a redirect, which is what AuthorizeAsync reports. The v2 path is preferred
/// because it is the later of the two the image names; v1 stays recorded here so a store that needs it can switch.
/// </para>
/// </summary>
public sealed class MidtransGateway : IPaymentGateway
{
    private const string ApiHost = "https://app.midtrans.com";
    private const string SnapV1 = "/snap/v1/transactions";
    private const string SnapV2 = "/snap/v2/transactions";

    public string Id => "midtrans";
    public string Name => "Midtrans";

    public Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(PaymentResult.Fail(
            "midtrans: tokenise is the Snap session itself — call AuthorizeAsync, which creates it"));

    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        var body = new JObject
        {
            ["transaction_details"] = new JObject
            {
                ["order_id"] = c.Session.Vars.TryGetValue("orderId", out var oid) ? oid : Guid.NewGuid().ToString("N"),
                ["gross_amount"] = GatewayHttp.MinorUnits(c),
            },
        };

        var res = await GatewayHttp.PostAsync(c, $"{ApiHost}{SnapV2}", body, "midtrans-snap", ct)
            .ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("midtrans: snap session failed");

        var token = res["token"]?.ToString();
        var redirect = res["redirect_url"]?.ToString();
        if (!string.IsNullOrEmpty(token)) c.Session.PaymentMethodId = token;

        if (!string.IsNullOrEmpty(redirect)) return PaymentResult.Action(redirect!, token ?? string.Empty);
        return string.IsNullOrEmpty(token)
            ? PaymentResult.Fail("midtrans: no token")
            : PaymentResult.Success(token);
    }

    public Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct) =>
        AuthorizeAsync(c, ct);

    /// <summary>Both Snap versions the image names, so a store needing the older one does not have to be re-captured.</summary>
    public static IReadOnlyList<string> SnapPaths => new[] { SnapV1, SnapV2 };
}
