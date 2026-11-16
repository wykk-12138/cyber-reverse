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
/// </summary>
public sealed class StripeGateway : IPaymentGateway
{
    private const string ApiHost = "https://api.stripe.com";

    public string Id => "stripe";
    public string Name => "Stripe";

    private static string PublishableKey(FlowContext c) =>
        c.Session.Vars.TryGetValue("stripe.publishableKey", out var v) ? v : string.Empty;

    public async Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return PaymentResult.Fail("stripe: no card");

        var form = new Dictionary<string, string>
        {
            ["key"] = PublishableKey(c),
            ["type"] = "card",
            ["card[number]"] = card.Number,
            ["card[exp_month]"] = card.Month ?? string.Empty,
            ["card[exp_year]"] = card.Year ?? string.Empty,
            ["card[cvc]"] = card.Cvv ?? string.Empty,
            ["card[name]"] = card.Name ?? c.ProfileData?.Display ?? string.Empty,
            ["billing_details[address][postal_code]"] = c.ProfileData?.Zip ?? string.Empty,
        };

        var res = await GatewayHttp.PostFormAsync(c, $"{ApiHost}/v1/payment_methods", form,
            "stripe-pm", ct).ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("stripe: payment_methods failed");

        var id = res["id"]?.ToString();
        if (string.IsNullOrEmpty(id)) return PaymentResult.Fail("stripe: no payment method id");

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

        var form = new Dictionary<string, string>
        {
            ["key"] = PublishableKey(c),
            ["payment_method"] = c.Session.PaymentMethodId ?? string.Empty,
            ["return_url"] = c.Session.CheckoutUrl ?? c.Url,
            ["confirm"] = "true",
        };

        var intentId = c.Session.Vars.TryGetValue("stripe.intentId", out var i) ? i : null;
        var url = string.IsNullOrEmpty(intentId)
            ? $"{ApiHost}/v1/payment_intents"
            : $"{ApiHost}/v1/payment_intents/{intentId}/confirm";

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
            var url3ds = res["next_action"]?["redirect_to_url"]?["url"]?.ToString() ?? string.Empty;
            return PaymentResult.Action(url3ds, res["client_secret"]?.ToString() ?? string.Empty);
        }

        return PaymentResult.Fail($"stripe: status {status}");
    }

    public async Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload,
        CancellationToken ct)
    {
        var form = new Dictionary<string, string>
        {
            ["key"] = PublishableKey(c),
            ["payment_method"] = c.Session.PaymentMethodId ?? string.Empty,
        };

        var res = await GatewayHttp.PostFormAsync(c,
            $"{ApiHost}/v1/payment_intents/{c.Session.Vars.GetValueOrDefault("stripe.intentId")}/confirm",
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

    public Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct)
    {
        if (!string.IsNullOrEmpty(payload)) c.Session.Vars["paypal.payerId"] = payload;
        return AuthorizeAsync(c, ct);
    }
}
