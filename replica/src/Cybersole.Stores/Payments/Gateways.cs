using System.Text.RegularExpressions;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

internal static class GatewayHttp
{
    public static async Task<JObject?> GetAsync(FlowContext c, string url, string tag,
        CancellationToken ct)
    {
        try
        {
            var res = await c.Http.GetAsync(url, c.Options(tag), ct).ConfigureAwait(false);
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

    /// <summary>
    /// The basil pin (0x146ADFC60). It is the version the challenge surface uses and, as of R1245, also the second
    /// pin observed on the payment-intents retrieve (<c>sub_14095B6C0</c>), so the same value serves two shapes.
    /// </summary>
    public const string ChallengeVersion = "2025-08-27.basil";

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

    /// <summary>Stripe's setup-intent confirm endpoint (0x147054fe0, with the /confirm suffix at 0x146ab3a08).</summary>
    public const string SetupIntentPath = "/v1/setup_intents/";

    /// <summary>The suffix appended to the setup-intent id (0x146ab3a08).</summary>
    public const string SetupConfirmSuffix = "/confirm";

    /// <summary>
    /// The card-element user agent the setup-intent confirm sends (0x1471654a0) — verbatim, and different from
    /// <see cref="PaymentUserAgent"/>: the payment-method create swears by payment-element/autopm, this one by
    /// card-element. Two surfaces, two frozen strings.
    /// </summary>
    public const string CardElementUserAgent = "stripe.js/035decdc6c; stripe-js-v3/035decdc6c; card-element";

    /// <summary>
    /// The setup-intent confirm's URL: the frozen prefix, the intent id, then <c>/confirm</c> (sub_140BE0F80).
    /// </summary>
    public static string SetupConfirmUrl(string setupIntentId) =>
        ApiHost + SetupIntentPath + Uri.EscapeDataString(setupIntentId ?? string.Empty) + SetupConfirmSuffix;

    /// <summary>The third frozen API version in the image: the payment-intent retrieve's (0x146ADFC98).</summary>
    public const string IntentVersion = "2025-09-30.clover";

    /// <summary>
    /// The confirmation user agent of <c>sub_140B58D60</c> (0x1471659D8) — the third distinct one in the image,
    /// and again a different hash from the other two surfaces.
    /// </summary>
    public const string PayPalConfirmUserAgent =
        "stripe.js/d6356e1526; stripe-js-v3/d6356e1526; payment-element";

    /// <summary>The mandate acceptance type the PayPal confirm sends (0x1471085E8).</summary>
    public const string MandateAcceptanceType = "online";

    /// <summary>The payment-intent confirm suffix (0x146AB3A08), shared literal with the setup-intent one.</summary>
    public static string PaymentIntentConfirmUrl(string intentId) =>
        ApiHost + "/v1/payment_intents/" + Uri.EscapeDataString(intentId ?? string.Empty) + "/confirm";

    /// <summary>
    /// The PayPal-through-Stripe payment-intent confirm built by <c>sub_140B58D60</c> (2,516 bytes, 345 lines),
    /// statically wired to Highsnobiety (<c>sub_140b578c0</c>).
    ///
    /// <para>
    /// <b>Observed</b>: <c>payment_method_data[type]</c> with the value <c>paypal</c> (0x147110A68),
    /// <c>expected_payment_method_type</c> (0x147020F28), <c>return_url</c> (0x14714DB90),
    /// <c>mandate_data[customer_acceptance][type]</c> (0x1470BE0C0) with <c>online</c> (0x1471085E8),
    /// <c>mandate_data[customer_acceptance][online][infer_from_client]</c> (0x1470BE030), the
    /// <c>payment_method_data[billing_details][address][country|postal_code]</c> pair (0x14710F958/F9E0),
    /// the nine client-side stamps (<c>guid</c>, <c>muid</c>, <c>sid</c>, <c>referrer</c>, <c>time_on_page</c>,
    /// <c>payment_user_agent</c>, and the six <c>client_attribution_metadata</c> keys),
    /// <c>radar_options[hcaptcha_token]</c> (0x147148170), and the standalone literals <c>NA</c> (0x146E10B68),
    /// <c>standard</c> (0x1471628B0), <c>2021</c> and <c>elements</c>.
    /// </para>
    ///
    /// <para>
    /// <b>Unknown</b>: which key the function's <c>true</c> literal (0x147173DE8) is assigned to. It is present
    /// in the constant set, and <c>infer_from_client</c> is the only flag-shaped slot here, but the decompiler does
    /// not pair them, so <paramref name="inferFromClient"/> is a parameter rather than a default. Likewise the
    /// two <c>client_attribution_metadata[*_flow]</c> values: the keys are observable, their contents are not.
    /// </para>
    /// </summary>
    public static Dictionary<string, string> PayPalConfirmForm(
        string paypalVaultId,
        string clientSecret,
        string publishableKey,
        string returnUrl,
        string inferFromClient,
        string? hcaptchaToken = null,
        string country = "BE",
        string postalCode = "1000")
    {
        var form = new Dictionary<string, string>
        {
            ["client_secret"] = clientSecret,
            ["key"] = publishableKey,
            ["return_url"] = returnUrl,
            ["expected_payment_method_type"] = "paypal",
            ["payment_method_data[type]"] = "paypal",
            ["payment_method_data[payment_user_agent]"] = PayPalConfirmUserAgent,
            ["payment_method_data[time_on_page]"] = TimeOnPage,
            ["payment_method_data[billing_details][address][country]"] = country,
            ["payment_method_data[billing_details][address][postal_code]"] = postalCode,
            ["mandate_data[customer_acceptance][type]"] = MandateAcceptanceType,
            ["mandate_data[customer_acceptance][online][infer_from_client]"] = inferFromClient,
            ["client_attribution_metadata[merchant_integration_source]"] = "elements",
            ["client_attribution_metadata[merchant_integration_version]"] = "2021",
            ["payment_method_data[client_attribution_metadata][merchant_integration_source]"] = "elements",
            ["payment_method_data[client_attribution_metadata][merchant_integration_version]"] = "2021",
            ["payment_method_data[client_attribution_metadata][payment_method_selection_flow]"] = "automatic",
        };
        if (!string.IsNullOrEmpty(paypalVaultId))
            form["payment_method"] = paypalVaultId;
        if (!string.IsNullOrEmpty(hcaptchaToken))
            form["radar_options[hcaptcha_token]"] = hcaptchaToken!;
        return form;
    }

    /// <summary>
    /// The payment-intent retrieve built by <c>sub_140A40170</c> (1,472 bytes) — John Lewis (<c>sub_140a40a30</c>),
    /// distinct from Casio's basil-pinned retrieve (<c>sub_14095B6C0</c>).
    ///
    /// <para>
    /// <b>Observed</b>: the function loads <c>https://api.stripe.com/v1/payment_intents/</c> (0x147054F08),
    /// <c>?is_stripe_sdk=false&amp;client_secret=</c> (0x146B287A8), <c>&amp;key=</c> (0x146A84588),
    /// <c>&amp;_stripe_version=</c> (0x146A7B010) with <c>2025-09-30.clover</c> (0x146ADFC98),
    /// <c>&amp;_stripe_account=</c> (0x146A7AFD8) and the account id <c>acct_1S0JRiIiwyy5Cf6X</c> (0x146F6D140).
    /// </para>
    ///
    /// <para>
    /// It differs from the John Lewis confirm that <c>MagentoFlow</c> already builds from
    /// <c>sub_1411458f0</c> in two ways: that one sends <c>is_stripe_sdk=true</c> and no version fragment, this one
    /// sends <c>false</c> and pins clover. Two builders, two shapes — the same lesson as the two user agents.
    /// </para>
    ///
    /// <para>
    /// <b>Unknown</b>: the order of the fragments after the first. Only <c>?is_stripe_sdk=false&amp;client_secret=</c>
    /// is known to open the query, because it is a single literal with the <c>?</c> in it; the other three are
    /// separate strings whose concatenation order the decompiler does not settle. Callers that assert on the URL
    /// should compare fragments, not the whole string.
    /// </para>
    /// </summary>
    public static string PaymentIntentRetrieveUrl(string intentId, string clientSecret, string publishableKey,
        string? stripeAccount = null, string? version = null) =>
        ApiHost + "/v1/payment_intents/" + Uri.EscapeDataString(intentId ?? string.Empty) +
        "?is_stripe_sdk=false" +
        "&client_secret=" + Uri.EscapeDataString(clientSecret ?? string.Empty) +
        "&key=" + Uri.EscapeDataString(publishableKey ?? string.Empty) +
        "&_stripe_version=" + Uri.EscapeDataString(version ?? IntentVersion) +
        "&_stripe_account=" + Uri.EscapeDataString(stripeAccount ?? string.Empty);

    /// <summary>
    /// The second pin for that same retrieve: <c>sub_14095B6C0</c> (1,271 bytes) builds the identical URL with
    /// <c>2025-08-27.basil</c> (0x146ADFC60) where <see cref="PaymentIntentRetrieveUrl"/> pins clover.
    ///
    /// <para>
    /// Its whole constant set is the five literals already known —
    /// <c>https://api.stripe.com/v1/payment_intents/</c>, <c>?is_stripe_sdk=false&amp;client_secret=</c>,
    /// <c>&amp;key=</c>, <c>&amp;_stripe_version=</c> and basil — so the shape is not a sixth thing to implement, it
    /// is the same four fragments with a different version value. That is why this is an overload and not a new
    /// builder: two versions of one request is a parameter, not two protocols.
    /// </para>
    ///
    /// <para>
    /// <b>Observed</b>: static thunk wiring confirms <c>sub_14095B6C0</c> belongs to Casio
    /// (<c>sub_14095c980</c>, <c>/stripe/payments/get_requires_action?orderId=</c>, paired with Casio's
    /// <c>PaymentMethodCreate</c> in <c>sub_140959320</c>), whereas <c>sub_140A40170</c> (<c>clover</c> +
    /// <c>acct_1S0JRiIiwyy5Cf6X</c>) belongs to John Lewis (<c>sub_140a40a30</c>), and the <c>0x147228EF8</c> /
    /// <c>0x1472279C8</c> pointers are <c>AsyncStateMachineBox</c> <c>ContextCallback</c> boxes rather than an
    /// indirect dispatch table.
    /// </para>
    /// </summary>
    public static string PaymentIntentRetrieveUrlBasil(string intentId, string clientSecret,
        string publishableKey, string? stripeAccount = null) =>
        PaymentIntentRetrieveUrl(intentId, clientSecret, publishableKey, stripeAccount, ChallengeVersion);

    /// <summary>
    /// The setup-intent retrieve URL (sub_141145DB0, 1,138 bytes): the same frozen prefix and id, then the query
    /// the image builds from three more literals — <c>?is_stripe_sdk=true&amp;client_secret=</c> at 0x146B28808,
    /// <c>&amp;key=</c> at 0x146A84588 and <c>&amp;_stripe_account=</c> at 0x146A7AFD8.
    ///
    /// <para>
    /// <b>Observed</b>: invoked from the shared Stripe <c>ProcessSetup</c> path (<c>sub_141146ce0</c> &lt;-
    /// <c>sub_140dd4f20</c> for <c>SHOPIFY-PAYMENT</c> / <c>PAYMENT-PARTNERS</c>), while its payment-intent sibling
    /// (<c>sub_1411458f0</c> via <c>STRIPE.Process</c> <c>sub_141146510</c>) serves Casio, John Lewis, HBX,
    /// Sportsshoes and <c>sub_140dd4f20</c>. What it produces is a GET of the intent, not a form post.
    /// </para>
    /// </summary>
    public static string SetupIntentRetrieveUrl(string setupIntentId, string clientSecret, string publishableKey,
        string? stripeAccount = null) =>
        ApiHost + SetupIntentPath + Uri.EscapeDataString(setupIntentId ?? string.Empty) +
        "?is_stripe_sdk=true" +
        "&client_secret=" + Uri.EscapeDataString(clientSecret ?? string.Empty) +
        "&key=" + Uri.EscapeDataString(publishableKey ?? string.Empty) +
        "&_stripe_account=" + Uri.EscapeDataString(stripeAccount ?? string.Empty);

    /// <summary>
    /// The setup-intent confirm form (sub_140BE0F80, 2,844 bytes), statically wired to Above The Clouds
    /// (<c>sub_140be2a10</c>, <c>abovetheclouds.nodnod.digital/stripe/create-setup-intent</c>).
    ///
    /// <para>
    /// <b>Observed</b>: every key below is a frozen literal loaded by that function — the
    /// <c>payment_method_data[...]</c> family at 0x14710FAE0..0x1471102C8, <c>expected_payment_method_type</c>
    /// at 0x147020F28, <c>use_stripe_sdk</c> at 0x147179510 with its value <c>true</c> at 0x147173DE8,
    /// <c>client_secret</c> at 0x146FCB508, <c>key</c> at 0x1470AE940, <c>radar_options[hcaptcha_token]</c> at
    /// 0x147148170, <c>card</c> at 0x146FBFC90, and the cdns host at 0x147057F10.
    /// <b>Unknown</b>: what the original puts in <c>pasted_fields</c>, <c>time_on_page</c> and <c>referrer</c> at
    /// runtime — the literals name the fields, not the values.
    /// </para>
    /// </summary>
    public static Dictionary<string, string> SetupConfirmForm(
        string setupIntentId,
        string clientSecret,
        string publishableKey,
        CardDetails card,
        string? hcaptchaToken = null,
        string expectedPaymentMethodType = "card",
        string integrationSource = "elements",
        string integrationVersion = "2017")
    {
        var form = new Dictionary<string, string>
        {
            ["client_secret"] = clientSecret,
            ["key"] = publishableKey,
            ["use_stripe_sdk"] = "true",
            ["expected_payment_method_type"] = expectedPaymentMethodType,
            ["payment_method_data[type]"] = "card",
            ["payment_method_data[card][number]"] = card.Number,
            ["payment_method_data[card][cvc]"] = card.Cvc,
            ["payment_method_data[card][exp_month]"] = card.ExpMonth,
            ["payment_method_data[card][exp_year]"] = card.ExpYear,
            ["payment_method_data[payment_user_agent]"] = CardElementUserAgent,
            ["payment_method_data[time_on_page]"] = TimeOnPage,
            ["client_attribution_metadata[merchant_integration_source]"] = integrationSource,
            ["client_attribution_metadata[merchant_integration_version]"] = integrationVersion,
            ["payment_method_data[client_attribution_metadata][merchant_integration_source]"] = integrationSource,
            ["payment_method_data[client_attribution_metadata][merchant_integration_version]"] = integrationVersion,
        };
        if (!string.IsNullOrEmpty(hcaptchaToken))
            form["radar_options[hcaptcha_token]"] = hcaptchaToken!;
        return form;
    }

    /// <summary>The card the setup-intent confirm submits (cryptogram-free; the hosted fields fill these).</summary>
    public readonly record struct CardDetails(string Number, string Cvc, string ExpMonth, string ExpYear);

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

    private static string ResolveApiHost(FlowContext c, string url) =>
        url.StartsWith(ApiHost, StringComparison.OrdinalIgnoreCase)
            ? ApiUrl(c) + url[ApiHost.Length..]
            : url;

    // ── R1302: the store-side Stripe configuration fetch ────────────────────────────────────────────
    //
    // This is the step R1301 recovered from 0x14094C210 while disproving that it was Unzer's. The whole
    // chain is: the async machine sub_14095B4E0 composes the URL, wraps 0x14094C210 in a delegate,
    // sub_1408B61E0 invokes that delegate on the request object it just built and then sub_1408B5EB0
    // sends it -- so 0x14094C210 configures the outgoing request, it is not a response callback.

    /// <summary>
    /// The Magento Stripe module's configuration path (0x146AB93D0) — and its query is a cache buster,
    /// not a parameter name: the image concatenates the tick straight onto the <c>=</c>.
    /// </summary>
    public const string StoreConfigPath = "/stripe/payments/get_stripe_configuration?_=";

    /// <summary>
    /// The origin the image composes the config URL from, verbatim (0x147090DF0). It is the Casio
    /// storefront because <c>sub_140947750</c> concatenates this literal, the store code and
    /// <see cref="MagentoRestPrefix"/> — the same Magento REST root <c>Sub_140959320</c>'s
    /// <c>PaymentMethodCreate</c> sits behind.
    /// </summary>
    public const string DefaultStoreOrigin = "https://www.casio.com/";

    /// <summary>The REST root between the store code and the path (0x146AB7298).</summary>
    public const string MagentoRestPrefix = "/rest/V1";

    /// <summary>
    /// The config URL as <c>sub_140947750</c> + <c>sub_14094A600</c> build it: origin, store code,
    /// <c>/rest/V1</c>, the path, then the millisecond tick. A trailing slash on the origin is tolerated
    /// because the frozen literal has one and a configured host usually does not.
    /// </summary>
    public static string StoreConfigUrl(string? storeOrigin, string? storeCode, long tick)
    {
        var declared = string.IsNullOrEmpty(storeOrigin) ? DefaultStoreOrigin : storeOrigin!;
        var origin = declared.TrimEnd('/') + "/";
        var code = (storeCode ?? string.Empty).Trim('/');
        var root = code.Length == 0 ? origin.TrimEnd('/') : origin + code;
        return root + MagentoRestPrefix + StoreConfigPath + tick.ToString(System.Globalization.CultureInfo.InvariantCulture);
    }

    /// <summary>
    /// The fifteen-entry browser template <c>0x14094C210</c> installs at <c>a2+80</c>, minus the three
    /// entries the image computes at build time (<c>user-agent</c>, <c>sec-ch-ua</c> and
    /// <c>sec-ch-ua-platform</c> — <c>sub_140F9BCE0</c> / <c>sub_140F9A950</c> / the session UA) and the
    /// one it leaves null (<c>cookie</c>).
    ///
    /// <para>
    /// The three computed entries are carried by the request's TLS profile here, which is where the
    /// replica's own fingerprint lives, and the cookie entry by the session's jar — so they are absent
    /// from this dictionary rather than re-invented in it.
    /// </para>
    ///
    /// <para>
    /// <b>Unknown</b>: <c>0x14094C210</c> also writes <c>"Akamai"</c> = <c>"1"</c> into <c>a2+112</c>,
    /// a field that is not the header dictionary at <c>a2+80</c>, and sets the byte at <c>a2+226</c> to
    /// one. Whether that pair is a cookie, a header of another collection, or a request flag is not
    /// established, so neither is emitted — an <c>Akamai</c> header on a request to an Akamai-fronted
    /// host would be a wire-level guess, not a replication.
    /// </para>
    /// </summary>
    public static Dictionary<string, string> StoreConfigHeaders(FlowContext c) =>
        new()
        {
            ["x-requested-with"] = "XMLHttpRequest",
            ["accept"] = "*/*",
            ["content-type"] = "application/json",
            ["sec-ch-ua-mobile"] = "?0",
            ["sec-fetch-site"] = "same-origin",
            ["sec-fetch-mode"] = "cors",
            ["sec-fetch-dest"] = "empty",
            ["accept-encoding"] = "gzip, deflate, br, zstd",
            ["accept-language"] = "en-US,en;q=0.9",
            ["priority"] = "u=1, i",
            ["referer"] = c.Session.Vars.GetValueOrDefault("stripe.storeReferer") ?? c.Url ?? string.Empty,
        };

    /// <summary>
    /// Fetch the store's Stripe configuration and take its <c>apiKey</c> as the publishable key —
    /// <c>0x14094C210</c> for the request side, <c>sub_14095B4E0</c> for the URL.
    ///
    /// <para>
    /// <b>Observed</b>: the status pair the caller's status object carries — <c>"Preparing payment"</c>
    /// (0x146E49298) with colour <c>"white"</c> (0x147184330) and kind <c>"StatusInfo"</c>
    /// (0x146E9B830), and on the failure branch <c>"Error preparing payment"</c> (0x146D0F904). The
    /// endpoint answers with <c>{"apiKey": "pk_…"}</c>.
    /// </para>
    ///
    /// <para>
    /// <b>Inference</b>: that this response's <c>apiKey</c> is the value later handed to
    /// <c>api.stripe.com</c> as <c>key</c>. The endpoint is Magento's Stripe module configuration and
    /// that module returns exactly this field, but the reader of the literal inside the image is not on
    /// this chain: <c>0x146F7544C</c>'s four referencing functions are <c>sub_14094DEB0</c>,
    /// <c>sub_1409F2A60</c>, <c>sub_140ECF2B0</c> and <c>sub_14117B6C0</c>, none of them in
    /// <c>0x14095xxxx</c>. Storing it under <c>stripe.publishableKey</c> is therefore the replica's
    /// choice, named here so a later round can move it if the reader turns up somewhere else.
    /// </para>
    /// </summary>
    public async Task<PaymentResult> FetchConfigurationAsync(FlowContext c, CancellationToken ct)
    {
        var url = StoreConfigUrl(
            c.Session.Vars.GetValueOrDefault("stripe.storeOrigin"),
            c.Session.Vars.GetValueOrDefault("stripe.storeCode"),
            DateTimeOffset.UtcNow.ToUnixTimeMilliseconds());

        c.Emit("Preparing payment", "StatusInfo");
        var res = await ThreeDsTransportHelpers
            .GetRawAsync(c, url, StoreConfigHeaders(c), "stripe-store-config", ct)
            .ConfigureAwait(false);

        var apiKey = ThreeDsTransportHelpers.TryParseJson(res?.Body)?["apiKey"]?.ToString();
        if (string.IsNullOrEmpty(apiKey))
        {
            c.Emit("Error preparing payment", "error");
            return PaymentResult.Fail("Error preparing payment");
        }

        c.Session.Vars["stripe.publishableKey"] = apiKey!;
        c.Session.Vars["stripe.storeConfig"] = res!.Body ?? string.Empty;
        return PaymentResult.Success(apiKey);
    }

    /// <summary>Execute a PaymentIntent retrieve via GET (<see cref="PaymentIntentRetrieveUrl"/> / <see cref="PaymentIntentRetrieveUrlBasil"/>).</summary>
    public async Task<PaymentResult> RetrievePaymentIntentAsync(
        FlowContext c,
        string intentId,
        string clientSecret,
        string publishableKey,
        string? stripeAccount = null,
        string? version = null,
        CancellationToken ct = default)
    {
        var url = ResolveApiHost(c, PaymentIntentRetrieveUrl(intentId, clientSecret, publishableKey, stripeAccount, version));
        var res = await GatewayHttp.GetAsync(c, url, "stripe-pi-retrieve", ct).ConfigureAwait(false);
        return InterpretIntentResponse(c, res, "stripe-pi-retrieve", "stripe: payment_intent retrieve failed", "stripe.intentId");
    }

    /// <summary>Execute a SetupIntent retrieve via GET (<see cref="SetupIntentRetrieveUrl"/>).</summary>
    public async Task<PaymentResult> RetrieveSetupIntentAsync(
        FlowContext c,
        string setupIntentId,
        string clientSecret,
        string publishableKey,
        string? stripeAccount = null,
        CancellationToken ct = default)
    {
        var url = ResolveApiHost(c, SetupIntentRetrieveUrl(setupIntentId, clientSecret, publishableKey, stripeAccount));
        var res = await GatewayHttp.GetAsync(c, url, "stripe-si-retrieve", ct).ConfigureAwait(false);
        return InterpretIntentResponse(c, res, "stripe-si-retrieve", "stripe: setup_intent retrieve failed", "stripe.setupIntentId");
    }

    /// <summary>Execute a SetupIntent confirm POST using <see cref="SetupConfirmForm"/> (<c>sub_140BE0F80</c>).</summary>
    public async Task<PaymentResult> ConfirmSetupIntentAsync(
        FlowContext c,
        string setupIntentId,
        string clientSecret,
        string publishableKey,
        CardDetails card,
        string? hcaptchaToken = null,
        string expectedPaymentMethodType = "card",
        string integrationSource = "elements",
        string integrationVersion = "2017",
        CancellationToken ct = default)
    {
        var form = SetupConfirmForm(setupIntentId, clientSecret, publishableKey, card,
            hcaptchaToken, expectedPaymentMethodType, integrationSource, integrationVersion);
        var res = await GatewayHttp.PostFormAsync(c, ResolveApiHost(c, SetupConfirmUrl(setupIntentId)),
            form, "stripe-si-confirm", ct).ConfigureAwait(false);
        return InterpretIntentResponse(c, res, "stripe-si-confirm", "stripe: setup_intent confirm failed", "stripe.setupIntentId");
    }

    /// <summary>Execute a PayPal-on-Stripe PaymentIntent confirm POST using <see cref="PayPalConfirmForm"/> (<c>sub_140B58D60</c>).</summary>
    public async Task<PaymentResult> ConfirmPayPalIntentAsync(
        FlowContext c,
        string intentId,
        string paypalVaultId,
        string clientSecret,
        string publishableKey,
        string returnUrl,
        string inferFromClient,
        string? hcaptchaToken = null,
        string country = "BE",
        string postalCode = "1000",
        CancellationToken ct = default)
    {
        var form = PayPalConfirmForm(paypalVaultId, clientSecret, publishableKey, returnUrl,
            inferFromClient, hcaptchaToken, country, postalCode);
        var res = await GatewayHttp.PostFormAsync(c, ResolveApiHost(c, PaymentIntentConfirmUrl(intentId)),
            form, "stripe-paypal-confirm", ct).ConfigureAwait(false);
        return InterpretIntentResponse(c, res, "stripe-paypal-confirm", "stripe: paypal confirm failed", "stripe.intentId");
    }

    private static PaymentResult InterpretIntentResponse(
        FlowContext c, Newtonsoft.Json.Linq.JObject? res, string op, string nullError, string idVarKey)
    {
        if (res is null) return PaymentResult.Fail(nullError);

        var id = res["id"]?.ToString();
        if (!string.IsNullOrEmpty(id)) c.Session.Vars[idVarKey] = id!;
        var status = res["status"]?.ToString();
        if (!string.IsNullOrEmpty(status)) c.Session.Vars["stripe.status"] = status!;

        if (string.Equals(status, "succeeded", StringComparison.OrdinalIgnoreCase))
            return PaymentResult.Success(id);

        if (string.Equals(status, "requires_action", StringComparison.OrdinalIgnoreCase))
        {
            var threeDs2Source = res["source"]?.ToString()
                                 ?? res["next_action"]?["source"]?.ToString();
            var url3ds = res["next_action"]?["redirect_to_url"]?["url"]?.ToString() ?? string.Empty;
            if (!string.IsNullOrEmpty(threeDs2Source) && threeDs2Source.StartsWith("src_",
                    StringComparison.OrdinalIgnoreCase))
                c.Session.Vars["stripe.threeDs2Source"] = threeDs2Source!;
            return PaymentResult.Action(url3ds, res["client_secret"]?.ToString() ?? string.Empty);
        }

        return PaymentResult.Fail($"{op}: status {status}");
    }

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
        // R1302: the store's own configuration comes first when the flow declared the Magento Stripe
        // surface and no key is loaded yet. That is the condition sub_140F9E790 tests inside the image —
        // it returns the session flag at +120 only while the counter at +32 is zero, i.e. "fetch the
        // config unless it is already there" — and the key it produces is what every call below sends as
        // form["key"], so an empty one would have gone out as key= and failed at Stripe rather than here.
        // Declaring the store (stripe.storeCode / stripe.storeOrigin) is this replica's stand-in for that
        // flag: without it a flow keeps supplying its own publishable key and no request is made.
        var declaredStore = !string.IsNullOrEmpty(c.Session.Vars.GetValueOrDefault("stripe.storeCode")) ||
                            !string.IsNullOrEmpty(c.Session.Vars.GetValueOrDefault("stripe.storeOrigin"));
        if (declaredStore && string.IsNullOrEmpty(PublishableKey(c)))
        {
            var configured = await FetchConfigurationAsync(c, ct).ConfigureAwait(false);
            if (!configured.Ok) return configured;
        }

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

        // R1282: the wall. The image runs the orange-wall confirm as its own step inside billing — sub_140BE31F0
        // emits "Solving Stripe challenge", awaits the captcha token, then PUTs the five fields — and what puts it
        // on that path is the answer carrying CAPTCHA_REQUIRED (0x146B65A14). It is checked before requires_action
        // because a challenged intent also reports that status: the wall, not the 3DS route, is what comes first.
        if (res.ToString().Contains(StripeChallenge.ChallengeRequiredMarker, StringComparison.Ordinal))
        {
            if (string.IsNullOrEmpty(c.Session.Vars.GetValueOrDefault("stripe.challengeToken")))
                return PaymentResult.Fail("stripe: challenged, no captcha token");

            var challenge = await ConfirmChallengeAsync(c, ct).ConfigureAwait(false);
            if (!challenge.Ok) return PaymentResult.Fail("stripe: challenge confirm failed");

            var retry = await GatewayHttp.PostFormAsync(c, url, form, "stripe-intent-retry", ct)
                .ConfigureAwait(false);
            if (retry is null) return PaymentResult.Fail("stripe: intent retry failed");

            c.Session.Vars["stripe.intentId"] = retry["id"]?.ToString() ?? string.Empty;
            var retryStatus = retry["status"]?.ToString();
            c.Session.Vars["stripe.status"] = retryStatus ?? string.Empty;
            if (string.Equals(retryStatus, "succeeded", StringComparison.OrdinalIgnoreCase))
                return PaymentResult.Success(retry["id"]?.ToString());

        }

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

    /// <summary>
    /// The orange-wall confirm on the main chain: reads the token the captcha surface handed back and runs
    /// <see cref="StripeChallenge.ConfirmAsync"/> against the per-order path the flow recorded.
    ///
    /// <para>
    /// The host goes through <see cref="ApiUrl"/>, so a configured endpoint can front the API — the same seam the
    /// intent calls already use. Before R1282 nothing in src called the confirm step at all.
    /// </para>
    /// </summary>
    public static async Task<StripeChallenge.ChallengeOutcome> ConfirmChallengeAsync(FlowContext c,
        CancellationToken ct)
    {
        var input = new StripeChallenge.ChallengeInput
        {
            CaptchaToken = c.Session.Vars.GetValueOrDefault("stripe.challengeToken"),
            ClientSecret = c.Session.Vars.GetValueOrDefault("stripe.clientSecret"),
            PublishableKey = PublishableKey(c),
            Path = c.Session.Vars.GetValueOrDefault("stripe.challengePath"),
        };

        // ConfirmAsync's url parameter replaces host+path wholesale, so the per-order path is appended here: the
        // seam moves the host, it does not drop the path the flow recorded.
        var target = ApiUrl(c) + (input.Path ?? string.Empty);
        return await StripeChallenge.ConfirmAsync(c, input, ct, target).ConfigureAwait(false);
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

/// <summary>
/// Unzer — <c>api.unzer.com</c> charge flow, Casio Magento 2 <c>unzer_cards</c> checkout, and
/// <c>ContinueUnzerThreeDs</c> / <c>RunUnzerThreeDs</c> state machine (<c>0x143383aa9</c>, <c>0x140960560</c>).
///
/// <para>
/// <b>R1302: this class no longer claims <c>0x14094c210</c>.</b> That function was labelled the Unzer
/// prepare sub-path with the sub-path itself unknown; decompiling it shows the opposite — it is the
/// request configuration for the Magento Stripe module's configuration fetch, whose URL
/// <c>sub_14095B4E0</c> composes from <c>https://www.casio.com/</c>, the store code and
/// <c>/rest/V1/stripe/payments/get_stripe_configuration?_=</c>. It lives on
/// <see cref="StripeGateway.FetchConfigurationAsync"/> now, and the step below is gone with it: its
/// <c>unzer.prepareUrl</c> requirement was a seam for a URL no evidence ever produced.
/// </para>
///
/// <para>
/// <b>Unknown</b>: (1) exact terminal exclusion set in <c>qword_1472c65a0+8</c>;
/// (2) exact URL predicate inside <c>0x14094a870</c> gating <c>RunUnzerThreeDs</c>.
/// </para>
/// </summary>
public sealed class UnzerGateway : IPaymentGateway
{
    public const string DefaultApiHost = "https://api.unzer.com";
    public const string SdkTypeHeader = "unzercorp/connectivity-v2-card-ui";
    public const string SdkVersionHeader = "0.22.0";
    public const string StaticOrigin = "https://static-cc.unzer.com";
    private const int MaxThreeDsHops = 6;

    public string Id => "unzer";
    public string Name => "Unzer";

    private static string ApiHost(FlowContext c) =>
        c.Session.Vars.TryGetValue("unzer.apiUrl", out var u) && !string.IsNullOrEmpty(u)
            ? u.TrimEnd('/')
            : DefaultApiHost;

    private static string StoreOrigin(FlowContext c) =>
        c.Session.Vars.TryGetValue("unzer.storeOrigin", out var o) && !string.IsNullOrEmpty(o)
            ? o.TrimEnd('/')
            : (!string.IsNullOrEmpty(c.Url) ? GatewayHttp.OriginOf(c.Url) : "https://www.casio.com");

    private static string StoreBase(FlowContext c)
    {
        var origin = StoreOrigin(c);
        var code = c.Session.Vars.TryGetValue("unzer.storeCode", out var sc) && !string.IsNullOrEmpty(sc)
            ? sc.Trim('/')
            : (c.Session.Vars.TryGetValue("CasioRegion", out var cr) && !string.IsNullOrEmpty(cr)
                ? cr.Trim('/')
                : string.Empty);
        return string.IsNullOrEmpty(code) ? origin : $"{origin}/{code}";
    }

    private static string CartScopeSegment(FlowContext c)
    {
        var isGuest = c.Session.Vars.TryGetValue("unzer.guest", out var g)
            ? string.Equals(g, "true", StringComparison.OrdinalIgnoreCase)
            : !string.IsNullOrEmpty(c.Session.CartId) &&
              !string.Equals(c.Session.Vars.GetValueOrDefault("unzer.authenticated"), "true", StringComparison.OrdinalIgnoreCase);
        return isGuest
            ? $"guest-carts/{Uri.EscapeDataString(c.Session.CartId ?? string.Empty)}"
            : "carts/mine";
    }

    /// <summary>
    /// <c>Set unzer payment</c> (<c>0x14094a660 -> 0x14095f480</c>):
    /// <c>POST /{store}/rest/V1/{carts/mine|guest-carts/{cartId}}/set-payment-information</c>.
    /// </summary>
    public async Task<PaymentResult> SetUnzerPaymentAsync(FlowContext c, CancellationToken ct)
    {
        c.Emit("Set unzer payment", "StatusInfo");
        var email = c.ProfileData?.Email ?? c.Account?.Email ?? c.Session.Vars.GetValueOrDefault("email") ?? string.Empty;
        var body = new JObject
        {
            ["cartId"] = c.Session.CartId ?? string.Empty,
            ["email"] = email,
            ["paymentMethod"] = new JObject { ["method"] = "unzer_cards" },
        };

        var url = $"{StoreBase(c)}/rest/V1/{CartScopeSegment(c)}/set-payment-information";
        var res = await ThreeDsTransportHelpers.PostJsonRawAsync(
            c, url, body.ToString(Formatting.None),
            new Dictionary<string, string> { ["X-Requested-With"] = "XMLHttpRequest" },
            "unzer-set-payment", ct).ConfigureAwait(false);

        return res is not null && res.IsSuccess
            ? PaymentResult.Success(res.Body)
            : PaymentResult.Fail($"unzer: set-payment-information failed ({res?.StatusCode ?? 0})");
    }

    public async Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return PaymentResult.Fail("unzer: no card");

        var publicKey = c.Session.Vars.GetValueOrDefault("unzer.publicKey");
        if (string.IsNullOrEmpty(publicKey))
        {
            c.Emit("Missing Unzer public key", "error");
            return PaymentResult.Fail("Missing Unzer public key");
        }

        c.Emit("Tokenizing card", "StatusInfo");

        var month = (card.Month ?? string.Empty).PadLeft(2, '0');
        var rawYear = card.Year ?? string.Empty;
        var yy = rawYear.Length == 4 ? rawYear[2..] : rawYear;
        var holder = !string.IsNullOrWhiteSpace(card.Name)
            ? card.Name!
            : $"{c.Billing?.FirstName ?? c.Shipping?.FirstName ?? c.ProfileData?.FirstName} {c.Billing?.LastName ?? c.Shipping?.LastName ?? c.ProfileData?.LastName}".Trim();

        var body = new JObject
        {
            ["number"] = card.Number.Replace(" ", string.Empty),
            ["cvc"] = card.Cvv ?? string.Empty,
            ["expiryDate"] = $"{month}/{yy}",
            ["cardHolder"] = holder,
        };

        var basicAuth = Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(publicKey + ":"));
        var headers = new Dictionary<string, string>
        {
            ["authorization"] = "Basic " + basicAuth,
            ["origin"] = StaticOrigin,
            ["accept-language"] = "de-DE",
            ["sdk-type"] = SdkTypeHeader,
            ["sdk-version"] = SdkVersionHeader,
            ["sec-fetch-site"] = "same-site",
        };

        var res = await ThreeDsTransportHelpers.PostJsonRawAsync(
            c, $"{ApiHost(c)}/v1/types/card", body.ToString(Formatting.None), headers, "unzer-card", ct)
            .ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("unzer: card type failed");
        if (res.StatusCode == 400)
        {
            c.Emit("Unzer tokenize bad request: " + (res.Body ?? string.Empty), "error");
            return PaymentResult.Fail("Invalid card");
        }
        if (res.StatusCode is not (200 or 201) && !res.IsSuccess)
            return PaymentResult.Fail($"unzer: card type HTTP {res.StatusCode}");

        var json = ThreeDsTransportHelpers.TryParseJson(res.Body);
        var id = json?["id"]?.ToString();
        if (string.IsNullOrEmpty(id)) return PaymentResult.Fail("unzer: no type id");

        c.Session.PaymentMethodId = id;
        c.Session.Vars["unzer.resourceId"] = id!;
        return PaymentResult.Success(id);
    }

    /// <summary>
    /// <c>Submit order</c> (<c>0x14094a700 -> 0x140963c40</c>):
    /// <c>POST /{store}/rest/V1/{carts/mine|guest-carts/{cartId}}/payment-information</c>.
    /// </summary>
    public async Task<PaymentResult> SubmitUnzerOrderAsync(FlowContext c, CancellationToken ct)
    {
        var cartId = c.Session.CartId;
        var resourceId = c.Session.Vars.GetValueOrDefault("unzer.resourceId") ?? c.Session.PaymentMethodId;
        if (string.IsNullOrEmpty(cartId) || string.IsNullOrEmpty(resourceId))
            return PaymentResult.Fail("unzer: missing cartId or resourceId");

        c.Emit("Submit order", "StatusInfo");

        var bill = c.Billing ?? c.Shipping;
        var email = c.ProfileData?.Email ?? c.Account?.Email ?? c.Session.Vars.GetValueOrDefault("email") ?? string.Empty;
        var addr1 = bill?.Address1 ?? c.ProfileData?.Address1 ?? string.Empty;
        var addr2 = bill?.Address2 ?? c.ProfileData?.Address2 ?? string.Empty;
        var storeOrigin = StoreOrigin(c);

        var extensionAttributes = new JObject
        {
            ["agreement_ids"] = new JArray(c.Session.Vars.GetValueOrDefault("unzer.agreementId") ?? "1"),
        };
        if (string.Equals(c.Session.Vars.GetValueOrDefault("unzer.policyAgreed"), "true", StringComparison.OrdinalIgnoreCase))
            extensionAttributes["is_policy_agreed"] = true;

        var billingAddress = new JObject
        {
            ["countryId"] = bill?.Country ?? c.ProfileData?.Country ?? string.Empty,
            ["email"] = email,
            ["regionCode"] = bill?.State ?? c.ProfileData?.State ?? string.Empty,
            ["region"] = bill?.State ?? c.ProfileData?.State ?? string.Empty,
            ["street"] = new JArray(addr1, addr2),
            ["company"] = string.Empty,
            ["telephone"] = c.ProfileData?.Phone ?? string.Empty,
            ["postcode"] = bill?.ZipCode ?? c.ProfileData?.Zip ?? string.Empty,
            ["city"] = bill?.City ?? c.ProfileData?.City ?? string.Empty,
            ["firstname"] = bill?.FirstName ?? c.ProfileData?.FirstName ?? string.Empty,
            ["lastname"] = bill?.LastName ?? c.ProfileData?.LastName ?? string.Empty,
            ["saveInAddressBook"] = JValue.CreateNull(),
        };

        var body = new JObject
        {
            ["cartId"] = cartId,
            ["billingAddress"] = billingAddress,
            ["email"] = email,
            ["paymentMethod"] = new JObject
            {
                ["method"] = "unzer_cards",
                ["po_number"] = JValue.CreateNull(),
                ["additional_data"] = new JObject
                {
                    ["customer_id"] = JValue.CreateNull(),
                    ["resource_id"] = resourceId,
                    ["birthDate"] = JValue.CreateNull(),
                    ["customer_type"] = "b2c",
                },
                ["extension_attributes"] = extensionAttributes,
            },
        };

        var headers = new Dictionary<string, string>
        {
            ["x-requested-with"] = "XMLHttpRequest",
            ["origin"] = storeOrigin,
            ["sec-fetch-site"] = "same-origin",
            ["sec-fetch-mode"] = "cors",
            ["sec-fetch-dest"] = "empty",
            ["referer"] = c.Session.Vars.GetValueOrDefault("unzer.referer") ?? c.Url,
            ["accept"] = "*/*",
            ["accept-language"] = "en-US,en;q=0.9",
            ["priority"] = "u=1, i",
        };

        var url = $"{StoreBase(c)}/rest/V1/{CartScopeSegment(c)}/payment-information";
        var res = await ThreeDsTransportHelpers.PostJsonRawAsync(
            c, url, body.ToString(Formatting.None), headers, "unzer-order", ct).ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("Error submitting order");
        if (res.StatusCode == 400)
        {
            c.Emit("Unzer order bad request: " + (res.Body ?? string.Empty), "error");
            return PaymentResult.Fail("Error submitting order");
        }
        if (!res.IsSuccess) return PaymentResult.Fail($"unzer: order HTTP {res.StatusCode}");

        var orderId = (res.Body ?? string.Empty).Trim('"', '\r', '\n', ' ');
        c.Session.OrderId = orderId;
        c.Session.OrderNumber = orderId;
        c.Session.Vars["unzer.orderId"] = orderId;
        c.Session.Vars["unzer.requiresRedirect"] = "true";
        c.Session.Vars["unzer.state"] = "Waiting3DS";

        var redirectUrl = $"{StoreBase(c)}/unzer/payment/redirect";
        c.Session.ThreeDsUrl = redirectUrl;
        return PaymentResult.Action(redirectUrl, orderId);
    }

    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.PaymentMethodId))
        {
            var t = await TokenizeAsync(c, ct).ConfigureAwait(false);
            if (!t.Ok) return t;
        }

        if (string.Equals(c.Session.Vars.GetValueOrDefault("unzer.flow"), "casio", StringComparison.OrdinalIgnoreCase) ||
            (!string.IsNullOrEmpty(c.Session.CartId) &&
             (c.Session.Vars.ContainsKey("unzer.storeOrigin") ||
              c.Session.Vars.ContainsKey("unzer.storeCode") ||
              c.Url.Contains("casio.com", StringComparison.OrdinalIgnoreCase))))
        {
            var set = await SetUnzerPaymentAsync(c, ct).ConfigureAwait(false);
            if (!set.Ok) return set;
            return await SubmitUnzerOrderAsync(c, ct).ConfigureAwait(false);
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

        var headers = new Dictionary<string, string>();
        if (c.Session.Vars.TryGetValue("unzer.publicKey", out var pk) && !string.IsNullOrEmpty(pk))
            headers["authorization"] = "Basic " + Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(pk + ":"));

        var res = await ThreeDsTransportHelpers.PostJsonRawAsync(
            c, $"{ApiHost(c)}/v1/payments/charges", body.ToString(Formatting.None), headers,
            "unzer-charge", ct).ConfigureAwait(false);

        if (res is null || !res.IsSuccess) return PaymentResult.Fail("unzer: charge failed");

        var json = ThreeDsTransportHelpers.TryParseJson(res.Body);
        if (json is null) return PaymentResult.Fail("unzer: charge response invalid");

        var id = json["id"]?.ToString();
        c.Session.Vars["unzer.paymentId"] = id ?? string.Empty;
        var redirectUrl = json["redirectUrl"]?.ToString();
        var status = json["status"]?.ToString();

        if (!string.IsNullOrEmpty(redirectUrl) &&
            !string.Equals(status, "success", StringComparison.OrdinalIgnoreCase))
        {
            c.Session.ThreeDsUrl = redirectUrl;
            c.Session.Vars["unzer.state"] = "Waiting3DS";
            return PaymentResult.Action(redirectUrl!, id ?? string.Empty);
        }

        return string.Equals(status, "success", StringComparison.OrdinalIgnoreCase)
            ? PaymentResult.Success(id)
            : PaymentResult.Fail($"unzer: status {status}");
    }

    /// <summary>
    /// <c>ContinueUnzerThreeDs</c> (<c>0x143383aa9</c>, <c>0x14094a760 -> 0x14095d270</c>):
    /// GETs <c>/{store}/unzer/payment/redirect</c>, extracts <c>form[action]</c> + inputs, runs
    /// <see cref="RunUnzerThreeDsAsync"/> when the action targets Unzer 3DS, follows up to 6 redirect hops,
    /// and verifies <c>/{store}/unzer/payment/callback/</c> (<c>checkout/onepage/success</c> / <c>/checkout/success</c>).
    /// </summary>
    public async Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct)
    {
        var redirectUrl = !string.IsNullOrWhiteSpace(payload) &&
                          (Uri.TryCreate(payload, UriKind.Absolute, out _) || payload.StartsWith('/'))
            ? ThreeDsTransportHelpers.ResolveUrl(StoreBase(c) + "/", payload)
            : c.Session.Vars.GetValueOrDefault("threeDsUrl")
              ?? c.Session.ThreeDsUrl
              ?? $"{StoreBase(c)}/unzer/payment/redirect";

        var redirectRes = await FollowRedirectsAsync(c, redirectUrl, "unzer-redirect", ct).ConfigureAwait(false);
        if (redirectRes is null)
            return PaymentResult.Fail("Error verifying payment");

        var landedUrl = redirectRes.Url.ToString();
        var (formAction, formInputs) = ThreeDsTransportHelpers.ExtractForm(redirectRes.Body);

        if (!string.IsNullOrEmpty(formAction))
        {
            var actionUri = ThreeDsTransportHelpers.ResolveUrl(landedUrl, formAction!);
            if (IsUnzerThreeDsAction(c, actionUri))
            {
                var threeDs = await RunUnzerThreeDsAsync(c, actionUri, formInputs, ct).ConfigureAwait(false);
                if (!threeDs.Ok) return threeDs;
                landedUrl = c.Session.Vars.GetValueOrDefault("unzer.landedUrl") ?? landedUrl;
            }
            else
            {
                var postRes = await ThreeDsTransportHelpers.PostFormRawAsync(
                    c, actionUri, formInputs, null, "unzer-form-hop", ct, followRedirects: false)
                    .ConfigureAwait(false);
                if (postRes is not null)
                {
                    var hopped = await FollowResponseHopsAsync(c, postRes, "unzer-form-redirect", ct)
                        .ConfigureAwait(false);
                    landedUrl = hopped.Url.ToString();
                }
            }
        }
        else if (!IsTerminalUrl(landedUrl))
        {
            c.Emit("Unzer redirect had no form: " + landedUrl, "StatusInfo");
        }

        if (!IsTerminalUrl(landedUrl))
        {
            var callbackUrl = $"{StoreBase(c)}/unzer/payment/callback/";
            var cbRes = await FollowRedirectsAsync(c, callbackUrl, "unzer-callback", ct).ConfigureAwait(false);
            if (cbRes is null)
                return PaymentResult.Fail("Error verifying payment");
            landedUrl = cbRes.Url.ToString();
        }

        c.Session.Vars["unzer.landedUrl"] = landedUrl;
        if (IsSuccessLanding(landedUrl))
        {
            c.Session.Vars["unzer.state"] = "Complete3DS";
            return PaymentResult.Success(c.Session.OrderId ?? c.Session.Vars.GetValueOrDefault("unzer.paymentId") ?? landedUrl);
        }

        if (landedUrl.Contains("checkout/cart", StringComparison.OrdinalIgnoreCase))
        {
            c.Emit("Unzer returned to cart: " + landedUrl, "error");
            return PaymentResult.Fail("Unzer returned to cart: " + landedUrl);
        }

        c.Emit("Unzer callback landed on " + landedUrl, "error");
        return PaymentResult.Fail("Error verifying payment");
    }

    /// <summary>
    /// <c>RunUnzerThreeDs</c> (<c>0x14094a7b0 -> 0x14095e0f0</c>): GETs <paramref name="actionUri"/>,
    /// parses <c>#threeds-method-data</c> (<c>data-notification-url</c>, <c>data-continue-url</c>,
    /// <c>data-server-trans-id</c>), POSTs Base64Url <c>threeDSMethodData</c> when notification URL is present,
    /// rewrites <c>/continue/</c> -> <c>/receiver/</c>, and walks up to 6 hops.
    /// </summary>
    public async Task<PaymentResult> RunUnzerThreeDsAsync(
        FlowContext c,
        string actionUri,
        IDictionary<string, string>? formInputs,
        CancellationToken ct)
    {
        var pageRes = await FollowRedirectsAsync(c, actionUri, "unzer-3ds-action", ct).ConfigureAwait(false);
        if (pageRes is null)
            return PaymentResult.Fail("Error verifying payment");

        var currentUrl = pageRes.Url.ToString();
        var methodAttrs = ThreeDsTransportHelpers.ReadElementAttributesById(pageRes.Body, "threeds-method-data");
        string? continueUrl = null;

        if (!string.IsNullOrEmpty(methodAttrs))
        {
            var notifyUrl = ThreeDsTransportHelpers.ReadAttr(methodAttrs!, "data-notification-url");
            var rawContinue = ThreeDsTransportHelpers.ReadAttr(methodAttrs!, "data-continue-url");
            var serverTransId = ThreeDsTransportHelpers.ReadAttr(methodAttrs!, "data-server-trans-id") ?? string.Empty;

            if (!string.IsNullOrEmpty(notifyUrl))
            {
                var methodJson = new JObject { ["threeDSServerTransID"] = serverTransId }.ToString(Formatting.None);
                var encoded = ThreeDsTransportHelpers.Base64UrlEncode(methodJson);
                var resolvedNotify = ThreeDsTransportHelpers.ResolveUrl(currentUrl, notifyUrl!);
                await ThreeDsTransportHelpers.PostFormRawAsync(
                    c, resolvedNotify,
                    new Dictionary<string, string> { ["threeDSMethodData"] = encoded },
                    null, "unzer-3ds-method-notify", ct).ConfigureAwait(false);
            }

            if (!string.IsNullOrEmpty(rawContinue))
                continueUrl = rawContinue!.Replace("/continue/", "/receiver/", StringComparison.OrdinalIgnoreCase);
        }

        if (!string.IsNullOrEmpty(continueUrl))
        {
            var resolvedContinue = ThreeDsTransportHelpers.ResolveUrl(currentUrl, continueUrl!);
            NetResponse? contRes;
            var cres = c.Session.Vars.GetValueOrDefault("unzer.cres");
            if (!string.IsNullOrEmpty(cres))
            {
                contRes = await ThreeDsTransportHelpers.PostFormRawAsync(
                    c, resolvedContinue,
                    new Dictionary<string, string> { ["cres"] = cres! },
                    null, "unzer-3ds-continue-post", ct, followRedirects: false).ConfigureAwait(false);
            }
            else
            {
                contRes = await ThreeDsTransportHelpers.GetRawAsync(
                    c, resolvedContinue, null, "unzer-3ds-continue", ct, followRedirects: false)
                    .ConfigureAwait(false);
            }

            if (contRes is not null)
            {
                var hopped = await FollowResponseHopsAsync(c, contRes, "unzer-3ds-hop", ct).ConfigureAwait(false);
                currentUrl = hopped.Url.ToString();
            }
        }
        else if (formInputs is not null && formInputs.Count > 0 && !IsTerminalUrl(currentUrl))
        {
            var postRes = await ThreeDsTransportHelpers.PostFormRawAsync(
                c, currentUrl, formInputs, null, "unzer-3ds-form", ct, followRedirects: false)
                .ConfigureAwait(false);
            if (postRes is not null)
            {
                var hopped = await FollowResponseHopsAsync(c, postRes, "unzer-3ds-form-hop", ct).ConfigureAwait(false);
                currentUrl = hopped.Url.ToString();
            }
        }

        c.Session.Vars["unzer.landedUrl"] = currentUrl;
        return PaymentResult.Success(currentUrl);
    }

    private static bool IsUnzerThreeDsAction(FlowContext c, string actionUri)
    {
        if (string.Equals(c.Session.Vars.GetValueOrDefault("unzer.forceThreeDs"), "true", StringComparison.OrdinalIgnoreCase))
            return true;
        // Unknown: exact URL predicate inside 0x14094a870 was not dumped statically.
        return actionUri.Contains("unzer", StringComparison.OrdinalIgnoreCase) ||
               actionUri.Contains("threeds", StringComparison.OrdinalIgnoreCase) ||
               actionUri.Contains("3ds", StringComparison.OrdinalIgnoreCase);
    }

    private static bool IsSuccessLanding(string url) =>
        url.Contains("checkout/onepage/success", StringComparison.OrdinalIgnoreCase) ||
        url.Contains("/checkout/success", StringComparison.OrdinalIgnoreCase);

    private static bool IsTerminalUrl(string url) =>
        IsSuccessLanding(url) || url.Contains("checkout/cart", StringComparison.OrdinalIgnoreCase);

    private static async Task<NetResponse?> FollowRedirectsAsync(
        FlowContext c, string url, string tag, CancellationToken ct)
    {
        var initial = await ThreeDsTransportHelpers.GetRawAsync(c, url, null, tag, ct, followRedirects: false)
            .ConfigureAwait(false);
        if (initial is null) return null;
        return await FollowResponseHopsAsync(c, initial, tag, ct).ConfigureAwait(false);
    }

    private static async Task<NetResponse> FollowResponseHopsAsync(
        FlowContext c, NetResponse current, string tag, CancellationToken ct)
    {
        for (var hop = 0; hop < MaxThreeDsHops; hop++)
        {
            if (current.StatusCode is not (301 or 302 or 303 or 307 or 308))
                break;
            if (!current.Headers.TryGetValue("Location", out var loc) || string.IsNullOrEmpty(loc))
                break;

            var nextUrl = ThreeDsTransportHelpers.ResolveUrl(current.Url.ToString(), loc);
            var next = await ThreeDsTransportHelpers.GetRawAsync(c, nextUrl, null, tag, ct, followRedirects: false)
                .ConfigureAwait(false);
            if (next is null) break;
            current = next;
        }
        return current;
    }
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
    /// <summary>
    /// <b>Not attested in the image.</b> R1246 searched the binary for <c>api.omise.co</c> and found nothing; the
    /// three Omise literals it does carry all sit on <see cref="CheckoutHost"/>. This constant is kept rather than
    /// removed because deleting a tokenising host is a product decision, but a later round should either find the
    /// evidence for it or replace it with whatever the image actually posts to — the honest state is "unevidenced",
    /// not "verified".
    /// </summary>
    private const string ApiHost = "https://api.omise.co";

    public const string CheckoutHost = "https://checkout-page.omise.co";

    /// <summary>The hosted checkout root, verbatim (0x14705CD0C) — with the trailing slash the image carries.</summary>
    public const string CheckoutPageUrl = "https://checkout-page.omise.co/";

    /// <summary>
    /// The sessions endpoint (0x14705CDD4). It had no presence in the replica before R1246, while the image carries it
    /// together with <c>https://checkout-page.omise.co/api/payment</c> (0x14705CD64) — the latter was already used at
    /// <c>MagentoFlow:838</c>, so only the sessions path was missing.
    /// </summary>
    public const string SessionsPath = "/api/sessions/";

    /// <summary><c>{CheckoutHost}/api/sessions/{id}</c>.</summary>
    public static string SessionsUrl(string sessionId) =>
        CheckoutHost + SessionsPath + Uri.EscapeDataString(sessionId ?? string.Empty);

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

    public async Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct)
    {
        if (c is not null &&
            (c.Session.Vars.ContainsKey("cardinal.serverJwt") ||
             c.Session.Vars.ContainsKey("cardinal.dfReferenceId") ||
             (!string.IsNullOrEmpty(payload) && payload.Contains('.'))))
        {
            var cardinal = new CardinalThreeDs();
            var serverJwt = c.Session.Vars.GetValueOrDefault("cardinal.serverJwt") ?? payload;
            var init = await cardinal.InitAsync(c, serverJwt, CardinalThreeDs.CardinalVariant.Centinel, ct)
                .ConfigureAwait(false);
            if (!init.Ok) return init;

            var txId = c.Session.Vars.GetValueOrDefault("cardinal.transactionId")
                       ?? c.Session.OrderId
                       ?? c.Session.Vars.GetValueOrDefault("paynamics.transactionId")
                       ?? string.Empty;
            if (!string.IsNullOrEmpty(txId))
                return await cardinal.ContinueAsync(c, txId, serverJwt, CardinalThreeDs.CardinalVariant.Centinel, ct)
                    .ConfigureAwait(false);

            return init;
        }

        return PaymentResult.Success(payload);
    }
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

    public async Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct)
    {
        if (c is null ||
            (!c.Session.Vars.ContainsKey("mollie.cardTokensUrl") &&
             !string.Equals(c.Session.Vars.GetValueOrDefault("mollie.mode"), "checkoutcom", StringComparison.OrdinalIgnoreCase)))
        {
            return PaymentResult.Fail(
                "mollie: tokenise endpoint not captured — the image names only /api/v1/public/core/payments/poll");
        }

        var card = c.Card;
        if (card?.Number is null) return PaymentResult.Fail("mollie: no card");

        var url = c.Session.Vars.GetValueOrDefault("mollie.cardTokensUrl") ?? CheckoutComGateway.MollieCardTokensUrl;
        var body = new JObject
        {
            ["cardNumber"] = card.Number.Replace(" ", string.Empty),
            ["expiryDate"] = $"{card.Month}/{card.Year}",
            ["cvv"] = card.Cvv ?? string.Empty,
            ["cardHolder"] = card.Name ?? c.ProfileData?.Display ?? string.Empty,
        };

        var res = await GatewayHttp.PostAsync(c, url, body, "mollie-card-tokens", ct).ConfigureAwait(false);
        var token = res?["cardToken"]?.ToString() ?? res?["token"]?.ToString() ?? res?["id"]?.ToString();
        if (string.IsNullOrEmpty(token)) return PaymentResult.Fail("mollie: card-tokens failed");

        c.Session.PaymentToken = token;
        return PaymentResult.Success(token);
    }

    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        var apiHost = c.Session.Vars.TryGetValue("mollie.apiHost", out var h) && !string.IsNullOrEmpty(h)
            ? h.TrimEnd('/')
            : ApiHost;
        var body = new JObject
        {
            ["amount"] = GatewayHttp.MinorUnits(c),
            ["currency"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "EUR",
        };

        var res = await GatewayHttp.PostAsync(c, $"{apiHost}/api/v1/public/core/payments/poll", body,
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

    public async Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct)
    {
        if (c is not null &&
            (c.Session.Vars.ContainsKey("checkoutcom.challengeForm") ||
             string.Equals(c.Session.Vars.GetValueOrDefault("mollie.mode"), "checkoutcom", StringComparison.OrdinalIgnoreCase)))
        {
            var form = new Dictionary<string, string>();
            var parsed = ThreeDsTransportHelpers.TryParseJson(payload);
            if (parsed is not null)
            {
                foreach (var p in parsed.Properties())
                    form[p.Name] = p.Value?.ToString() ?? string.Empty;
            }
            else if (!string.IsNullOrEmpty(payload))
            {
                form["cres"] = payload;
            }

            var notified = await CheckoutComGateway.NotifyMollieChallengeAsync(c, form, ct).ConfigureAwait(false);
            if (!notified.Ok) return notified;
        }

        return await AuthorizeAsync(c, ct).ConfigureAwait(false);
    }
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

    /// <summary>
    /// Midtrans' 3DS result completion (0x147053AE8): the endpoint the image posts the challenge outcome to.
    ///
    /// <para>
    /// <b>Observed</b> in <c>sub_140DA0380</c> (3,886 bytes), whose constant set is this endpoint together with
    /// <c>/v2/3ds/callback/</c> (0x146AB9A40), <c>/charge</c> (0x146AB2DC0), <c>ThreeDSServerTransID</c>
    /// (0x146EEF768), <c>BrowserInfo</c> (0x146B62F30), <c>DeviceChannel</c> (0x146BBD1C8), the seven
    /// <c>browser*</c> fields, <c>card_token</c> (0x146FC0B88), <c>credit_card</c> (0x146FD9158),
    /// <c>customer_details</c> (0x146FDBC40) with <c>full_name</c> and <c>email</c>, and the literals
    /// <c>3ds</c> (0x146AEE028) and <c>02</c> (0x146ABD328).
    /// </para>
    ///
    /// <para>
    /// <b>Unknown</b>: whether the browser block travels nested under <c>BrowserInfo</c> or flattened, and which
    /// slot the <c>02</c> literal fills. The names are observable; the JSON shape is not, so the builder returns
    /// the browser block separately rather than inventing a nesting.
    /// </para>
    /// </summary>
    public const string ResultCompletionUrlPrefix = "https://api.midtrans.com/v2/3ds/result-completion/";

    /// <summary>The 3DS callback path in the same function's constant set (0x146AB9A40).</summary>
    public const string ThreeDsCallbackPath = "/v2/3ds/callback/";

    /// <summary>Channel and type literals the same function loads (0x146AEE028 / 0x146ABD328).</summary>
    public const string ThreeDsTypeLiteral = "3ds";

    /// <summary>The result completion URL for one transaction (sub_140DA0380, 0x147053AE8).</summary>
    public static string ResultCompletionUrl(string transactionId) =>
        ResultCompletionUrlPrefix + Uri.EscapeDataString(transactionId ?? string.Empty);

    /// <summary>
    /// The browser block the 3DS result completion carries. The seven keys are the image's own literals; the
    /// values are the same frozen fingerprint the 3DS2 authenticate form uses, because the image loads the same
    /// string objects in both functions (compare <see cref="StripeGateway.BrowserFingerprint"/>).
    /// </summary>
    public static Dictionary<string, string> ThreeDsBrowserBlock(string userAgent) =>
        new()
        {
            ["browserColorDepth"] = "24",
            ["browserJavaEnabled"] = "false",
            ["browserLanguage"] = "en-US",
            ["browserScreenHeight"] = "1080",
            ["browserScreenWidth"] = "1920",
            ["browserTZ"] = "-120",
            ["browserUserAgent"] = userAgent ?? string.Empty,
        };

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
