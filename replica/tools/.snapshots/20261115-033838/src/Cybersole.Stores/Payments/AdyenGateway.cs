using System.Text;
using System.Text.RegularExpressions;
using Cybersole.Stores.Flows;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Adyen Checkout integration with the four 3-D Secure lookups the binary runs:
/// <c>_threeDsLookUpQuery</c>, <c>_threeDsJwtQuery</c>, <c>_threeDsAuthenticateQuery</c> and
/// <c>_resolveThreeDsContingencyQuery</c>.
///
/// Two hosts are involved: the merchant's own `/v{NN}/payments` endpoints and the
/// shopper-side host <c>checkoutshopper-live.adyen.com</c> where the 3DS2 challenge runs.
/// </summary>
public sealed class AdyenGateway : IPaymentGateway
{
    public string Id => "adyen";
    public string Name => "Adyen";

    private const string ShopperHost = "https://checkoutshopper-live.adyen.com";
    public const string ApiVersion = "v68";

    public async Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct)
    {
        // Adyen has no separate tokenisation step for card fields — the encrypted blob is
        // produced by the shopper component, so tokenisation is a pass-through that only
        // records what will be sent on /payments.
        var card = c.Card;
        if (card?.Number is null) return PaymentResult.Fail("adyen: no card");
        if (string.IsNullOrEmpty(c.Session.PaymentMethodId))
            c.Session.PaymentMethodId = "scheme";

        return PaymentResult.Success();
    }

    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return PaymentResult.Fail("adyen: no card");

        c.Session.Vars["adyen.merchantAccount"] =
            c.Session.Vars.TryGetValue("adyen.merchantAccount", out var ma) ? ma : "CybersoleECOM";

        var body = new JObject
        {
            ["paymentMethod"] = new JObject
            {
                ["type"] = c.Session.PaymentMethodId ?? "scheme",
                ["encryptedCardNumber"] = Encrypt(card.Number),
                ["encryptedExpiryMonth"] = Encrypt(card.Month ?? string.Empty),
                ["encryptedExpiryYear"] = Encrypt(card.Year ?? string.Empty),
                ["encryptedSecurityCode"] = Encrypt(card.Cvv ?? string.Empty),
                ["holderName"] = card.Name ?? c.ProfileData?.Display,
            },
            ["amount"] = new JObject
            {
                ["value"] = AmountMinor(c),
                ["currency"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "USD",
            },
            ["reference"] = c.Session.CheckoutToken ?? Guid.NewGuid().ToString("N")[..12],
            ["merchantAccount"] = c.Session.Vars["adyen.merchantAccount"],
            ["channel"] = "web",
            ["returnUrl"] = c.Session.CheckoutUrl ?? c.Url,
            // R133: the browser profile comes from the same fingerprint the page reported. These were
            // hardcoded to 24 / 1080 / 1920 / offset 0, which is the one thing a 3-D Secure risk engine
            // checks first: a payment whose screen disagrees with the browser that made it is rejected
            // in a way that looks exactly like a declined card.
            ["browserInfo"] = BrowserInfo(c),
            ["threeDS2RequestData"] = new JObject
            {
                ["threeDSCompInd"] = Scripts.DlpaProfile.From(FingerprintFor(c), TimeZoneOffset(c)).ThreeDsCompInd,
            },
        };

        var res = await PostAsync(c, PaymentsUrl(c), body, "adyen-payments", ct)
            .ConfigureAwait(false);
        if (res is null) return PaymentResult.Fail("adyen: payments call failed");

        var root = res;
        var resultCode = root["resultCode"]?.ToString();
        c.Session.Vars["adyen.resultCode"] = resultCode ?? string.Empty;
        c.Session.Vars["adyen.pspReference"] = root["pspReference"]?.ToString() ?? string.Empty;

        var action = root["action"];
        if (action is not null)
        {
            var type = action["type"]?.ToString();
            c.Session.Vars["adyen.actionType"] = type ?? string.Empty;

            if (string.Equals(type, "threeDS2", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(type, "threeDS2Challenge", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(type, "threeDS2Fingerprint", StringComparison.OrdinalIgnoreCase))
            {
                var paymentData = action["paymentData"]?.ToString();
                if (string.IsNullOrEmpty(paymentData))
                    return PaymentResult.Fail("adyen: 3DS action without paymentData");

                var jwt = DecodeJwt(paymentData!);
                if (jwt is not null)
                {
                    c.Session.Vars["adyen.acsTransId"] = jwt["acsTransID"]?.ToString() ?? string.Empty;
                    c.Session.Vars["adyen.threeDSMethodUrl"] = jwt["threeDSMethodURL"]?.ToString() ?? string.Empty;
                    c.Session.Vars["adyen.messageVersion"] = jwt["messageVersion"]?.ToString() ?? string.Empty;
                }

                c.Session.Vars["adyen.paymentData"] = paymentData!;
                return PaymentResult.Action(action["url"]?.ToString() ?? ShopperHost, paymentData!);
            }

            if (string.Equals(type, "redirect", StringComparison.OrdinalIgnoreCase))
            {
                c.Session.Vars["adyen.redirect"] = action["url"]?.ToString() ?? string.Empty;
                return PaymentResult.Action(action["url"]?.ToString() ?? string.Empty,
                    action["paymentData"]?.ToString() ?? string.Empty);
            }
        }

        if (string.Equals(resultCode, "Authorised", StringComparison.OrdinalIgnoreCase))
            return PaymentResult.Success(root["pspReference"]?.ToString());

        return PaymentResult.Fail($"adyen: resultCode {resultCode}");
    }

    // 鈹€鈹€ the four 3-D Secure queries 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    /// <summary>
    /// <c>_threeDsLookUpQuery</c> — ask the shopper host which 3DS version/method the
    /// card supports before the payment is issued.
    /// </summary>
    public async Task<PaymentResult> LookUpAsync(FlowContext c, CancellationToken ct)
    {
        var body = new JObject
        {
            ["paymentMethod"] = new JObject { ["type"] = c.Session.PaymentMethodId ?? "scheme" },
            ["amount"] = new JObject
            {
                ["value"] = AmountMinor(c),
                ["currency"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "USD",
            },
        };

        var res = await PostAsync(c,
            $"{ShopperHost}/checkoutshopper/v1/threeDS2/deviceSupport", body, "adyen-3ds-lookup", ct)
            .ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("adyen: 3DS lookup failed");

        c.Session.Vars["adyen.deviceSupport"] = res["supportedVersions"]?.ToString() ?? string.Empty;
        c.Session.Vars["adyen.supported"] = res["supported"]?.ToString() ?? "true";
        return PaymentResult.Success();
    }

    /// <summary>
    /// <c>GetThreeDsJwtQuery</c> / <c>_threeDsJwtQuery</c> — decode the base64url JWT that
    /// Adyen hands back so the ACS endpoints are known before the challenge runs.
    /// </summary>
    public PaymentResult GetJwt(FlowContext c, string paymentData)
    {
        var jwt = DecodeJwt(paymentData);
        if (jwt is null) return PaymentResult.Fail("adyen: paymentData is not a JWT");

        foreach (var key in new[] { "ACSURL", "acsURL", "threeDSMethodURL", "acsTransID", "messageVersion", "threeDSServerTransID" })
        {
            if (jwt[key] is { } v) c.Session.Vars["adyen.jwt." + key] = v.ToString();
        }

        return PaymentResult.Success();
    }

    /// <summary>
    /// <c>_threeDsAuthenticateQuery</c> — post the fingerprint/challenge result back to the
    /// shopper host and capture <c>transStatus</c>.
    /// </summary>
    public async Task<PaymentResult> AuthenticateAsync(FlowContext c, string threeDsResult,
        CancellationToken ct)
    {
        var body = new JObject
        {
            ["threeDSResult"] = threeDsResult,
            ["paymentData"] = c.Session.Vars.TryGetValue("adyen.paymentData", out var pd) ? pd : null,
        };

        var res = await PostAsync(c,
            $"{ShopperHost}/checkoutshopper/v1/threeDS2/authenticate", body, "adyen-3ds-auth", ct)
            .ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("adyen: 3DS authenticate failed");

        c.Session.Vars["adyen.transStatus"] = res["transStatus"]?.ToString() ?? string.Empty;
        c.Session.Vars["adyen.authenticated"] =
            string.Equals(res["transStatus"]?.ToString(), "Y", StringComparison.OrdinalIgnoreCase)
                ? "true" : "false";

        return PaymentResult.Success(res["transStatus"]?.ToString());
    }

    /// <summary>
    /// <c>_resolveThreeDsContingencyQuery</c> — when the issuer returns <c>C</c> or the
    /// challenge cannot run, resolve the contingency (frictionless fallback / exemption).
    /// </summary>
    public async Task<PaymentResult> ResolveContingencyAsync(FlowContext c, CancellationToken ct)
    {
        var body = new JObject
        {
            ["paymentData"] = c.Session.Vars.TryGetValue("adyen.paymentData", out var pd) ? pd : null,
            ["threeDSServerTransID"] = c.Session.Vars.TryGetValue("adyen.threeDSServerTransID", out var t) ? t : null,
            ["transStatus"] = c.Session.Vars.TryGetValue("adyen.transStatus", out var s) ? s : null,
        };

        var res = await PostAsync(c,
            $"{ShopperHost}/checkoutshopper/v1/threeDS2/contingency", body, "adyen-3ds-contingency", ct)
            .ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("adyen: contingency resolution failed");

        c.Session.Vars["adyen.contingency"] = res["result"]?.ToString() ?? string.Empty;
        return PaymentResult.Success(res["result"]?.ToString());
    }

    /// <summary><c>Adyen-PaymentsDetails</c> — finish the payment after 3DS / redirect.</summary>
    public async Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload,
        CancellationToken ct)
    {
        var details = new JObject
        {
            ["details"] = new JObject { ["threeDSResult"] = payload },
            ["paymentData"] = c.Session.Vars.TryGetValue("adyen.paymentData", out var pd) ? pd : null,
        };

        var res = await PostAsync(c, PaymentsDetailsUrl(c), details, "adyen-details", ct)
            .ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("adyen: payments/details failed");

        var code = res["resultCode"]?.ToString();
        if (string.Equals(code, "Authorised", StringComparison.OrdinalIgnoreCase))
            return PaymentResult.Success(res["pspReference"]?.ToString());

        return PaymentResult.Fail($"adyen details: resultCode {code}");
    }

    /// <summary><c>Adyen-Authorize3DS2</c> — explicit challenge submission path.</summary>
    public async Task<PaymentResult> Authorize3DS2Async(FlowContext c, string challengeResponse,
        CancellationToken ct)
    {
        var jwt = c.Session.Vars.TryGetValue("adyen.paymentData", out var pd) ? pd : null;
        var acsTransId = c.Session.Vars.TryGetValue("adyen.acsTransId", out var a) ? a : string.Empty;

        var body = new JObject
        {
            ["transStatus"] = "Y",
            ["threeDSCompInd"] = "Y",
            ["acsTransID"] = acsTransId,
            ["challengeResponse"] = challengeResponse,
            ["paymentData"] = jwt,
        };

        var res = await PostAsync(c,
            $"{ShopperHost}/checkoutshopper/v1/threeDS2/challenge", body, "adyen-3ds-challenge", ct)
            .ConfigureAwait(false);

        if (res is null) return PaymentResult.Fail("adyen: challenge submission failed");
        return PaymentResult.Success(res["transStatus"]?.ToString());
    }

    /// <summary><c>Adyen-PaymentFromComponent</c> — the drop-in component posts the state blob.</summary>
    public async Task<PaymentResult> PaymentFromComponentAsync(FlowContext c, string stateData,
        CancellationToken ct)
    {
        var body = new JObject
        {
            ["stateData"] = stateData,
            ["paymentMethod"] = new JObject { ["type"] = c.Session.PaymentMethodId ?? "scheme" },
        };

        var res = await PostAsync(c, PaymentsUrl(c), body, "adyen-component", ct).ConfigureAwait(false);
        if (res is null) return PaymentResult.Fail("adyen: component submission failed");

        var code = res["resultCode"]?.ToString();
        return string.Equals(code, "Authorised", StringComparison.OrdinalIgnoreCase)
            ? PaymentResult.Success(res["pspReference"]?.ToString())
            : PaymentResult.Fail($"adyen component: resultCode {code}");
    }

    // 鈹€鈹€ helpers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
    private static string PaymentsUrl(FlowContext c)
    {
        var origin = c.Session.Vars.TryGetValue("adyen.apiOrigin", out var o) && !string.IsNullOrEmpty(o)
            ? o
            : Origin(c.Url);
        return $"{origin}/{ApiVersion}/payments";
    }

    private static string PaymentsDetailsUrl(FlowContext c)
    {
        var origin = c.Session.Vars.TryGetValue("adyen.apiOrigin", out var o) && !string.IsNullOrEmpty(o)
            ? o
            : Origin(c.Url);
        return $"{origin}/{ApiVersion}/payments/details";
    }

    private static string Origin(string url)
    {
        var u = new Uri(url);
        return u.GetLeftPart(UriPartial.Authority);
    }

    private static string AmountMinor(FlowContext c)
    {
        var raw = c.Session.Vars.TryGetValue("total", out var t) ? t : c.Product?.Price ?? "0";
        var cleaned = Regex.Replace(raw, @"[^\d.]", string.Empty);
        if (!decimal.TryParse(cleaned, System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var value))
            value = 0;
        return ((long)Math.Round(value * 100)).ToString();
    }

    /// <summary>Adyen encrypted field placeholder — the shopper key is store-specific.</summary>
    private static string Encrypt(string value)
    {
        var key = "adyen-shopper-key";
        var bytes = Encoding.UTF8.GetBytes(value);
        var keyBytes = Encoding.UTF8.GetBytes(key);
        for (var i = 0; i < bytes.Length; i++) bytes[i] ^= keyBytes[i % keyBytes.Length];
        return "adyenjs_" + Convert.ToBase64String(bytes);
    }

    public static JObject? DecodeJwt(string token)
    {
        var parts = token.Split('.');
        if (parts.Length < 2) return null;

        try
        {
            var payload = parts[1].Replace('-', '+').Replace('_', '/');
            switch (payload.Length % 4)
            {
                case 2: payload += "=="; break;
                case 3: payload += "="; break;
            }
            var json = Encoding.UTF8.GetString(Convert.FromBase64String(payload));
            return JObject.Parse(json);
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static async Task<JObject?> PostAsync(FlowContext c, string url, JObject body, string tag,
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

    /// <summary>
    /// The fingerprint this session's browser reports. Taken from the flow's profile key when the
    /// browser bridge set one, otherwise derived from the User-Agent — never invented per call.
    /// </summary>
    private static Scripts.BrowserFingerprint FingerprintFor(FlowContext c) =>
        Scripts.BrowserIdentity.Fingerprint(c.Session);

    /// <summary>Minutes east of UTC, from the session when the browser reported one.</summary>
    private static int TimeZoneOffset(FlowContext c) =>
        Scripts.BrowserIdentity.TimeZoneOffset(c.Session);

    /// <summary>
    /// Adyen's <c>browserInfo</c>, derived from the fingerprint so it cannot contradict the page.
    /// The DLPA profile is the same device seen by the scheme, which is why both are built here.
    /// </summary>
    private static JObject BrowserInfo(FlowContext c)
    {
        var fingerprint = FingerprintFor(c);
        var dlpa = Scripts.DlpaProfile.From(fingerprint, TimeZoneOffset(c), c.Session.UserAgent);

        return new JObject
        {
            ["userAgent"] = c.Session.UserAgent ?? "Mozilla/5.0",
            ["acceptHeader"] = "*/*",
            ["language"] = dlpa.BrowserLanguage,
            ["colorDepth"] = fingerprint.ColorDepth,
            ["screenHeight"] = fingerprint.ScreenHeight,
            ["screenWidth"] = fingerprint.ScreenWidth,
            ["timeZoneOffset"] = TimeZoneOffset(c),
            ["javaEnabled"] = false,
        };
    }

}
