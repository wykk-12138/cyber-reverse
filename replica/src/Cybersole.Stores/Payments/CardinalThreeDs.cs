using System.Text;
using System.Text.RegularExpressions;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Cardinal Commerce 3-D Secure / SongbirdJS / CruiseAPI state machine
/// (<c>CardinalInit</c>, <c>CardinalContinue</c>, <c>geo.cardinalcommerce.com</c> device
/// fingerprinting, and <c>V2/Cruise/StepUp</c> + <c>V1/Cruise/TermRedirection</c>),
/// recovered from <c>0x14338294f</c> and <c>0x14092df10..0x140942cc0</c>.
/// </summary>
public sealed class CardinalThreeDs
{
    public const string CentinelHost = "https://centinelapi.cardinalcommerce.com";
    public const string TrustedHost = "https://client.cardinaltrusted.com";
    public const string GeoHost = "https://geo.cardinalcommerce.com";
    public const string CybersourceOrigin = "https://secureacceptance.cybersource.com";

    public const string CentinelInitPath = "/V1/Order/JWT/Init";
    public const string CentinelContinuePath = "/V1/Order/JWT/Continue";
    public const string TrustedInitPath = "/centinelapi/V1/Order/JWT/Init";
    public const string TrustedContinuePath = "/centinelapi/V1/Order/JWT/Continue";
    public const string CruiseStepUpPath = "/V2/Cruise/StepUp";
    public const string CruiseTermRedirectionPath = "/V1/Cruise/TermRedirection";

    public enum CardinalVariant
    {
        /// <summary><c>centinelapi.cardinalcommerce.com</c> (SongbirdJS 1.35.0 — Demandware, Paynamics, PayPal, PayMongo, iPay88, Xendit, FEP/SPS).</summary>
        Centinel = 0,

        /// <summary><c>client.cardinaltrusted.com</c> (SongbirdJS 2.1.0 — Warhammer, AO.com).</summary>
        CardinalTrusted = 1,
    }

    private static string ResolveCentinelHost(FlowContext c) =>
        c.Session.Vars.TryGetValue("cardinal.centinelHost", out var h) && !string.IsNullOrEmpty(h)
            ? h.TrimEnd('/')
            : CentinelHost;

    private static string ResolveTrustedHost(FlowContext c) =>
        c.Session.Vars.TryGetValue("cardinal.trustedHost", out var h) && !string.IsNullOrEmpty(h)
            ? h.TrimEnd('/')
            : TrustedHost;

    private static string ResolveGeoHost(FlowContext c) =>
        c.Session.Vars.TryGetValue("cardinal.geoHost", out var h) && !string.IsNullOrEmpty(h)
            ? h.TrimEnd('/')
            : GeoHost;

    private static string EnsureTid(FlowContext c)
    {
        if (c.Session.Vars.TryGetValue("cardinal.tid", out var tid) && !string.IsNullOrEmpty(tid))
            return tid;
        tid = "Tid-" + Guid.NewGuid().ToString("D");
        c.Session.Vars["cardinal.tid"] = tid;
        return tid;
    }

    /// <summary>
    /// <c>CardinalInit</c> (<c>0x140933e70</c> for Centinel; <c>0x1409423b0</c> for CardinalTrusted).
    /// Posts the SongbirdJS init payload and extracts <c>CardinalJWT</c> and <c>ConsumerSessionId</c>.
    /// </summary>
    public async Task<PaymentResult> InitAsync(
        FlowContext c,
        string serverJwt,
        CardinalVariant variant = CardinalVariant.Centinel,
        CancellationToken ct = default)
    {
        if (string.IsNullOrEmpty(serverJwt))
            return PaymentResult.Fail("cardinal: missing ServerJWT");

        c.Emit("Submitting Cardinal (I)", "StatusInfo");

        var tid = EnsureTid(c);
        var hostOrigin = ThreeDsTransportHelpers.OriginOf(c.Url);

        string url;
        Dictionary<string, string> headers;
        JObject body;

        if (variant == CardinalVariant.CardinalTrusted)
        {
            url = ResolveTrustedHost(c) + TrustedInitPath;
            headers = new Dictionary<string, string>
            {
                ["x-cardinal-tid"] = tid,
                ["origin"] = c.Session.Vars.GetValueOrDefault("cardinal.origin") ?? CybersourceOrigin,
                ["referer"] = c.Session.Vars.GetValueOrDefault("cardinal.referer") ?? CybersourceOrigin,
            };
            body = new JObject
            {
                ["SupportsAlternativePayments"] = new JObject { ["cca"] = true },
                ["Client"] = new JObject { ["Agent"] = "SongbirdJS", ["Version"] = "2.1.0" },
                ["ConsumerSessionId"] = JValue.CreateNull(),
                ["ServerJWT"] = serverJwt,
            };
        }
        else
        {
            var consumerSessionId = c.Session.Vars.TryGetValue("cardinal.consumerSessionId", out var csid) &&
                                    !string.IsNullOrEmpty(csid)
                ? csid
                : "0_" + Guid.NewGuid().ToString("D");
            c.Session.Vars["cardinal.consumerSessionId"] = consumerSessionId;

            url = ResolveCentinelHost(c) + CentinelInitPath;
            headers = new Dictionary<string, string>
            {
                ["x-cardinal-tid"] = tid,
                ["origin"] = c.Session.Vars.GetValueOrDefault("cardinal.origin") ?? hostOrigin,
            };
            body = new JObject
            {
                ["BrowserPayload"] = new JObject
                {
                    ["Order"] = new JObject
                    {
                        ["OrderDetails"] = new JObject(),
                        ["Consumer"] = new JObject
                        {
                            ["BillingAddress"] = new JObject(),
                            ["ShippingAddress"] = new JObject(),
                            ["Account"] = new JObject(),
                        },
                        ["Cart"] = new JArray(),
                        ["Token"] = new JObject(),
                        ["Authorization"] = new JObject(),
                        ["Options"] = new JObject(),
                        ["CCAExtension"] = new JObject(),
                    },
                    ["SupportsAlternativePayments"] = new JObject
                    {
                        ["cca"] = true,
                        ["hostedFields"] = false,
                        ["applepay"] = false,
                        ["discoverwallet"] = false,
                        ["wallet"] = false,
                        ["paypal"] = false,
                        ["visacheckout"] = false,
                    },
                },
                ["Client"] = new JObject { ["Agent"] = "SongbirdJS", ["Version"] = "1.35.0" },
                ["ConsumerSessionId"] = consumerSessionId,
                ["ServerJWT"] = serverJwt,
            };
        }

        c.Session.Vars["cardinal.serverJwt"] = serverJwt;
        var res = await ThreeDsTransportHelpers.PostJsonRawAsync(
            c, url, body.ToString(Formatting.None), headers, "cardinal-init", ct,
            "application/json;charset=UTF-8").ConfigureAwait(false);

        if (res is null || !res.IsSuccess)
            return PaymentResult.Fail(res is null ? "3DS init failed" : $"3DS init failed (HTTP {res.StatusCode})");

        var json = ThreeDsTransportHelpers.TryParseJson(res.Body);
        var cardinalJwt = json?["CardinalJWT"]?.ToString();
        if (string.IsNullOrEmpty(cardinalJwt))
            return PaymentResult.Fail("cardinal: missing CardinalJWT in init response");

        c.Session.Vars["cardinal.jwt"] = cardinalJwt!;
        var decoded = ThreeDsTransportHelpers.DecodeJwtPayload(cardinalJwt);
        if (decoded is not null)
        {
            var decodedCsid = decoded["ConsumerSessionId"]?.ToString();
            if (!string.IsNullOrEmpty(decodedCsid))
            {
                c.Session.Vars["cardinal.consumerSessionId"] = decodedCsid!;
                c.Session.Vars["cardinal.dfReferenceId"] = decodedCsid!;
            }
            var refId = decoded["ReferenceId"]?.ToString();
            if (!string.IsNullOrEmpty(refId))
                c.Session.Vars["cardinal.dfReferenceId"] = refId!;
            var payloadObj = decoded["Payload"];
            if (payloadObj is not null)
            {
                var stepUpUrl = payloadObj["StepUpUrl"]?.ToString() ?? payloadObj["ACSUrl"]?.ToString();
                if (!string.IsNullOrEmpty(stepUpUrl))
                    c.Session.Vars["cardinal.stepUpUrl"] = stepUpUrl!;
            }
        }

        if (!c.Session.Vars.ContainsKey("cardinal.dfReferenceId") &&
            c.Session.Vars.TryGetValue("cardinal.consumerSessionId", out var savedCsid))
        {
            c.Session.Vars["cardinal.dfReferenceId"] = savedCsid;
        }

        var result = PaymentResult.Success(c.Session.Vars.GetValueOrDefault("cardinal.dfReferenceId") ?? tid);
        result.Fields["CardinalJWT"] = cardinalJwt!;
        if (c.Session.Vars.TryGetValue("cardinal.consumerSessionId", out var finalCsid))
            result.Fields["ConsumerSessionId"] = finalCsid;
        return result;
    }

    /// <summary>
    /// <c>CardinalContinue</c> (<c>0x140933640</c> for Centinel; <c>0x140941ae0</c> for CardinalTrusted).
    /// Submits <c>PaymentType: "CCA"</c> and <c>OrderDetails.TransactionId</c>.
    /// </summary>
    public async Task<PaymentResult> ContinueAsync(
        FlowContext c,
        string transactionId,
        string? serverJwt = null,
        CardinalVariant variant = CardinalVariant.Centinel,
        CancellationToken ct = default)
    {
        var jwt = !string.IsNullOrEmpty(serverJwt)
            ? serverJwt!
            : c.Session.Vars.GetValueOrDefault("cardinal.serverJwt") ?? string.Empty;
        if (string.IsNullOrEmpty(jwt))
            return PaymentResult.Fail("cardinal: missing ServerJWT for continue");

        c.Emit("Submitting Cardinal (C)", "StatusInfo");

        var tid = EnsureTid(c);
        var hostOrigin = ThreeDsTransportHelpers.OriginOf(c.Url);
        var consumerSessionId = c.Session.Vars.GetValueOrDefault("cardinal.consumerSessionId");

        string url;
        Dictionary<string, string> headers;
        JObject body;

        if (variant == CardinalVariant.CardinalTrusted)
        {
            url = ResolveTrustedHost(c) + TrustedContinuePath;
            headers = new Dictionary<string, string>
            {
                ["x-cardinal-tid"] = tid,
                ["origin"] = c.Session.Vars.GetValueOrDefault("cardinal.origin") ?? CybersourceOrigin,
                ["referer"] = c.Session.Vars.GetValueOrDefault("cardinal.referer") ?? CybersourceOrigin,
                ["sec-fetch-site"] = "same-origin",
            };
            body = new JObject
            {
                ["PaymentType"] = "CCA",
                ["OrderDetails"] = new JObject { ["TransactionId"] = transactionId },
                ["ConsumerSessionId"] = consumerSessionId,
                ["ServerJWT"] = jwt,
            };
        }
        else
        {
            url = ResolveCentinelHost(c) + CentinelContinuePath;
            headers = new Dictionary<string, string>
            {
                ["x-cardinal-tid"] = tid,
                ["origin"] = c.Session.Vars.GetValueOrDefault("cardinal.origin") ?? hostOrigin,
                ["sec-fetch-site"] = "same-origin",
            };
            body = new JObject
            {
                ["BrowserPayload"] = new JObject
                {
                    ["Order"] = new JObject
                    {
                        ["OrderDetails"] = new JObject { ["TransactionId"] = transactionId },
                    },
                    ["PaymentType"] = "CCA",
                    ["SupportsAlternativePayments"] = new JObject
                    {
                        ["cca"] = true,
                        ["hostedFields"] = false,
                        ["applepay"] = false,
                        ["discoverwallet"] = false,
                        ["wallet"] = false,
                        ["paypal"] = false,
                        ["visacheckout"] = false,
                    },
                },
                ["Client"] = new JObject { ["Agent"] = "SongbirdJS", ["Version"] = "1.35.0" },
                ["ConsumerSessionId"] = consumerSessionId,
                ["ServerJWT"] = jwt,
                ["PaymentType"] = "CCA",
                ["OrderDetails"] = new JObject { ["TransactionId"] = transactionId },
            };
        }

        var res = await ThreeDsTransportHelpers.PostJsonRawAsync(
            c, url, body.ToString(Formatting.None), headers, "cardinal-continue", ct,
            "application/json;charset=UTF-8").ConfigureAwait(false);

        if (res is null || !res.IsSuccess)
            return PaymentResult.Fail(res is null ? "cardinal: continue failed" : $"cardinal: continue HTTP {res.StatusCode}");

        c.Session.Vars["cardinal.continueBody"] = res.Body;
        var json = ThreeDsTransportHelpers.TryParseJson(res.Body);
        var nextJwt = json?["CardinalJWT"]?.ToString();
        if (!string.IsNullOrEmpty(nextJwt))
            c.Session.Vars["cardinal.jwt"] = nextJwt!;

        var stepUpUrl = json?["StepUpUrl"]?.ToString() ?? json?["AcsUrl"]?.ToString();
        if (!string.IsNullOrEmpty(stepUpUrl))
            return PaymentResult.Action(stepUpUrl!, nextJwt ?? transactionId);

        return PaymentResult.Success(nextJwt ?? transactionId);
    }

    /// <summary>
    /// <c>geo.cardinalcommerce.com/DeviceFingerprintWeb/V2/Browser/Render</c> (<c>0x140937e70</c>) +
    /// <c>SaveBrowserData</c> (<c>0x140935560</c>) + <c>Notification</c> (<c>0x140934970</c>).
    /// </summary>
    public async Task<PaymentResult> CollectDeviceFingerprintAsync(
        FlowContext c,
        string orgUnitId,
        string referenceId,
        string? binSessionId = null,
        string? methodUrl = null,
        CancellationToken ct = default)
    {
        var geoHost = ResolveGeoHost(c);
        var hostOrigin = c.Session.Vars.GetValueOrDefault("cardinal.origin") ?? ThreeDsTransportHelpers.OriginOf(c.Url);
        var renderUrl = $"{geoHost}/DeviceFingerprintWeb/V2/Browser/Render" +
                        $"?threatmetrix=true&alias=Default&orgUnitId={Uri.EscapeDataString(orgUnitId)}" +
                        $"&tmEventType=PAYMENT&referenceId={Uri.EscapeDataString(referenceId)}" +
                        $"&geolocation=false&origin={Uri.EscapeDataString(hostOrigin)}";

        var collectReferer = $"{hostOrigin}/V1/Cruise/Collect";
        var renderHeaders = new Dictionary<string, string> { ["referer"] = collectReferer };
        var renderRes = await ThreeDsTransportHelpers.GetRawAsync(c, renderUrl, renderHeaders, "cardinal-df-render", ct)
            .ConfigureAwait(false);
        if (renderRes is null || !renderRes.IsSuccess)
            return PaymentResult.Fail("cardinal: device fingerprint render failed");

        var fp = Scripts.BrowserIdentity.Fingerprint(c.Session);
        var ua = c.Session.UserAgent ?? "Mozilla/5.0";
        var tz = Scripts.BrowserIdentity.TimeZoneOffset(c.Session);
        var effectiveBinSessionId = binSessionId ?? referenceId;

        var saveBody = new JObject
        {
            ["BinConfigIdentifiers"] = new JArray(),
            ["Cookies"] = new JObject(),
            ["DeviceChannel"] = "Browser",
            ["Extended"] = new JObject { ["Device"] = new JObject() },
            ["Fingerprint"] = c.Session.Vars.GetValueOrDefault("cardinal.fingerprint") ?? string.Empty,
            ["FingerprintingTime"] = 120,
            ["FingerprintDetails"] = new JObject { ["Version"] = "1.5.1" },
            ["Plugins"] = new JArray(),
            ["Screen"] = new JObject
            {
                ["FakedResolution"] = false,
                ["Ratio"] = 1,
                ["Resolution"] = $"{fp.ScreenWidth}x{fp.ScreenHeight}",
                ["UsableResolution"] = $"{fp.ScreenWidth}x{fp.ScreenHeight}",
                ["CCAScreenSize"] = "02",
            },
            ["ThreatMetrixEnabled"] = true,
            ["ThreatMetrixEventType"] = "PAYMENT",
            ["ThreatMetrixAlias"] = "Default",
            ["TimeOffset"] = tz,
            ["UserAgent"] = ua,
            ["UserAgentDetails"] = new JObject
            {
                ["FakedOS"] = false,
                ["FakedBrowser"] = false,
            },
            ["BinSessionId"] = effectiveBinSessionId,
            ["Referrer"] = hostOrigin + "/",
        };
        if (!string.IsNullOrEmpty(methodUrl))
            saveBody["MethodUrls"] = new JArray(methodUrl);

        var saveTarget = !string.IsNullOrEmpty(methodUrl)
            ? (methodUrl!.EndsWith("/SaveBrowserData", StringComparison.OrdinalIgnoreCase)
                ? methodUrl
                : methodUrl.TrimEnd('/') + "/SaveBrowserData")
            : $"{geoHost}/DeviceFingerprintWeb/V2/Browser/SaveBrowserData";

        var saveHeaders = new Dictionary<string, string> { ["referer"] = collectReferer };
        var saveRes = await ThreeDsTransportHelpers.PostJsonRawAsync(
            c, saveTarget, saveBody.ToString(Formatting.None), saveHeaders, "cardinal-df-save", ct)
            .ConfigureAwait(false);
        if (saveRes is null || !saveRes.IsSuccess)
            return PaymentResult.Fail("cardinal: SaveBrowserData failed");

        var notifyUrl = $"{geoHost}/DeviceFingerprintWeb/V2/Browser/Notification" +
                        $"?binSessionId={Uri.EscapeDataString(effectiveBinSessionId)}" +
                        $"&referenceId={Uri.EscapeDataString(referenceId)}";
        var methodPayload = new JObject { ["threeDSServerTransID"] = effectiveBinSessionId }.ToString(Formatting.None);
        var encodedMethod = Convert.ToBase64String(Encoding.UTF8.GetBytes(methodPayload));
        var notifyRes = await ThreeDsTransportHelpers.PostFormRawAsync(
            c,
            notifyUrl,
            new Dictionary<string, string> { ["threeDSMethodData"] = encodedMethod },
            new Dictionary<string, string> { ["referer"] = collectReferer },
            "cardinal-df-notify",
            ct).ConfigureAwait(false);

        if (notifyRes is null || !notifyRes.IsSuccess)
            return PaymentResult.Fail("cardinal: device fingerprint notification failed");

        c.Session.Vars["cardinal.dfReferenceId"] = referenceId;
        return PaymentResult.Success(referenceId);
    }

    /// <summary>
    /// <c>Cruise/StepUp</c> (<c>0x14092e630 -> 0x140934ea0 -> 0x1409331c0/0x140932550</c>) and
    /// <c>V1/Cruise/TermRedirection</c>.
    /// </summary>
    public async Task<PaymentResult> StepUpAsync(
        FlowContext c,
        string jwt,
        string? stepUpUrl = null,
        CancellationToken ct = default)
    {
        if (string.IsNullOrEmpty(jwt))
            return PaymentResult.Fail("cardinal: missing StepUp JWT");

        var target = !string.IsNullOrEmpty(stepUpUrl)
            ? stepUpUrl!
            : c.Session.Vars.GetValueOrDefault("cardinal.stepUpUrl") ?? (ResolveCentinelHost(c) + CruiseStepUpPath);

        var res = await ThreeDsTransportHelpers.PostFormRawAsync(
            c,
            target,
            new Dictionary<string, string> { ["JWT"] = jwt },
            null,
            "cardinal-stepup",
            ct).ConfigureAwait(false);

        if (res is null || !res.IsSuccess)
            return PaymentResult.Fail("cardinal: Cruise/StepUp failed");

        var baseUrl = ThreeDsTransportHelpers.OriginOf(target);
        var currentBody = res.Body ?? string.Empty;
        var currentUrl = res.Url.ToString();

        for (var hop = 0; hop < 4; hop++)
        {
            var cardinalJwt = ExtractCardinalJwt(currentBody);
            if (!string.IsNullOrEmpty(cardinalJwt))
            {
                var termUrl = ResolveCentinelHost(c) + CruiseTermRedirectionPath;
                if (Uri.TryCreate(currentUrl, UriKind.Absolute, out var cu) &&
                    !string.Equals(cu.Host, new Uri(CentinelHost).Host, StringComparison.OrdinalIgnoreCase))
                {
                    termUrl = ThreeDsTransportHelpers.OriginOf(currentUrl) + CruiseTermRedirectionPath;
                }

                var mcsId = c.Session.Vars.GetValueOrDefault("cardinal.mcsId")
                            ?? ExtractInputValue(currentBody, "McsId")
                            ?? string.Empty;

                var termBody = new JObject
                {
                    ["McsId"] = mcsId,
                    ["CardinalJWT"] = cardinalJwt,
                    ["Error"] = string.Empty,
                };

                var termRes = await ThreeDsTransportHelpers.PostJsonRawAsync(
                    c, termUrl, termBody.ToString(Formatting.None), null, "cardinal-term-redirect", ct)
                    .ConfigureAwait(false);
                if (termRes is null || !termRes.IsSuccess)
                    return PaymentResult.Fail("cardinal: TermRedirection failed");

                var termJson = ThreeDsTransportHelpers.TryParseJson(termRes.Body);
                var resultJwt = termJson?["CardinalJWT"]?.ToString()
                                ?? termJson?["jwt"]?.ToString()
                                ?? cardinalJwt!;
                c.Session.Vars["cardinal.resultJwt"] = resultJwt;
                return PaymentResult.Success(resultJwt);
            }

            var (redirectAction, redirectInputs) = ThreeDsTransportHelpers.ExtractForm(currentBody, "Redirect");
            if (string.IsNullOrEmpty(redirectAction))
                (redirectAction, redirectInputs) = ThreeDsTransportHelpers.ExtractForm(currentBody);

            if (string.IsNullOrEmpty(redirectAction))
                break;

            var nextUrl = ThreeDsTransportHelpers.ResolveUrl(currentUrl, redirectAction!);
            var formRes = await ThreeDsTransportHelpers.PostFormRawAsync(
                c, nextUrl, redirectInputs, null, "cardinal-stepup-form", ct).ConfigureAwait(false);
            if (formRes is null)
                return PaymentResult.Fail("cardinal: step-up form post failed");

            currentBody = formRes.Body ?? string.Empty;
            currentUrl = formRes.Url.ToString();
            if (nextUrl == baseUrl) break;
        }

        if (c.Session.Vars.TryGetValue("cardinal.resultJwt", out var savedResult) && !string.IsNullOrEmpty(savedResult))
            return PaymentResult.Success(savedResult);

        var (pendingAction, _) = ThreeDsTransportHelpers.ExtractForm(currentBody);
        if (!string.IsNullOrEmpty(pendingAction))
            return PaymentResult.Action(ThreeDsTransportHelpers.ResolveUrl(currentUrl, pendingAction!), jwt);

        return PaymentResult.Fail("3DS result missing");
    }

    private static string? ExtractCardinalJwt(string body)
    {
        if (string.IsNullOrEmpty(body)) return null;
        var json = ThreeDsTransportHelpers.TryParseJson(body);
        var fromJson = json?["CardinalJWT"]?.ToString();
        if (!string.IsNullOrEmpty(fromJson)) return fromJson;

        var fromInput = ExtractInputValue(body, "CardinalJWT");
        if (!string.IsNullOrEmpty(fromInput)) return fromInput;

        var m = Regex.Match(body, @"""CardinalJWT""\s*:\s*""([^""]+)""");
        return m.Success ? m.Groups[1].Value : null;
    }

    private static string? ExtractInputValue(string html, string name)
    {
        var (_, inputs) = ThreeDsTransportHelpers.ExtractForm(html);
        return inputs.TryGetValue(name, out var val) && !string.IsNullOrEmpty(val) ? val : null;
    }
}
