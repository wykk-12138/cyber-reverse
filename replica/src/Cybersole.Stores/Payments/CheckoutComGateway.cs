using System.Text;
using System.Text.RegularExpressions;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Checkout.com (<c>api.checkout.com</c> / <c>authentication-devices.checkout.com</c>) gateway and
/// 3-D Secure state machine covering the four IDA-verified paths in Dossier 2B:
/// (1) Shopify Offsite (<c>pay.checkout.com</c> -> <c>/tokens</c> -> <c>/payment-sessions/{id}/submit</c> -> 3DS),
/// (2) Gateway Dispatcher (<c>api.checkout.com/sessions-interceptor/...</c>),
/// (3) NIKE-GS / ESW (<c>authentication-devices.checkout.com</c> 3DS2 + 3DS1 PaReq fallback), and
/// (4) Mollie card-token &amp; challenge notification (<c>api.cc.mollie.com</c> + <c>/sessions-interceptor/challenge-notification</c>).
///
/// <para>
/// <b>Verified (<c>0x1408A34F0</c>)</b>: the issuer ACS dispatcher routes all twenty-eight names in
/// <see cref="AcsHosts"/> across nineteen headless issuer handlers (<see cref="CheckoutComAcsHandlers"/>,
/// <c>01_apata</c>.. <c>19_cardinal</c>) plus interactive fallback <c>20_fallback</c> (<c>0x144BDBD70</c>),
/// logging <c>"Starting 3DS: &lt;host&gt;"</c> and temporarily swapping the transport profile to
/// <c>chrome_131</c>. Caller-supplied challenge forms (<c>checkoutcom.challengeForm</c> / <c>payload</c>)
/// continue to take precedence when present.
/// </para>
///
/// <para>
/// <b>Remaining unknowns</b>: caller-side <c>AllowAutoRedirect</c> initialization before <c>0x1408A34F0</c>,
/// Capital One's <c>0x140F97CA0</c> signal source, Marqeta's <c>0x140F9FBB0</c> poll delay, Cardinal's
/// boxed <c>Screen.Ratio</c> double (<c>sub_141AAF850</c>), Soldo's downstream multipart header binding,
/// and the interactive WebView controller (<c>0x1408A7560</c>/<c>0x1408A7EE0</c>).
/// </para>
/// </summary>
public sealed class CheckoutComGateway : IPaymentGateway
{
    public const string DefaultApiHost = "https://api.checkout.com";
    public const string DefaultAuthDevicesHost = "https://authentication-devices.checkout.com";
    public const string MollieCardTokensUrl = "https://api.cc.mollie.com/v1/card-tokens";

    public const string TokensPath = "/tokens";
    public const string PaymentSessionsPrefix = "/payment-sessions/";
    public const string MethodNotificationPath = "/sessions-interceptor/3ds-method-notification";
    public const string HostedChallengeNotificationPath = "/sessions-interceptor/hosted-challenge-notification";
    public const string ChallengeNotificationPath = "/sessions-interceptor/challenge-notification";

    public string Id => "checkoutcom";
    public string Name => "Checkout.com";

    private static string ApiHost(FlowContext c) =>
        c.Session.Vars.TryGetValue("checkoutcom.apiHost", out var v) && !string.IsNullOrEmpty(v)
            ? v.TrimEnd('/')
            : DefaultApiHost;

    private static string AuthDevicesHost(FlowContext c) =>
        c.Session.Vars.TryGetValue("checkoutcom.authDevicesHost", out var v) && !string.IsNullOrEmpty(v)
            ? v.TrimEnd('/')
            : DefaultAuthDevicesHost;

    /// <summary>
    /// Bootstraps a Shopify Offsite (<c>pay.checkout.com</c>) page by parsing
    /// <c>&lt;script id="__NEXT_DATA__"&gt;.props.pageProps.paymentPageContextSerialized</c>
    /// for <c>pk</c> and <c>payment_session.id</c>.
    /// </summary>
    public async Task<PaymentResult> BootstrapOffsiteAsync(FlowContext c, string offsiteUrl, CancellationToken ct)
    {
        var res = await ThreeDsTransportHelpers.GetRawAsync(c, offsiteUrl, null, "cko-offsite-bootstrap", ct)
            .ConfigureAwait(false);
        if (res is null || !res.IsSuccess)
            return PaymentResult.Fail("checkoutcom: offsite bootstrap failed");

        var nextDataText = HtmlFormDom.ExtractElementText(res.Body, "script#__NEXT_DATA__");
        if (string.IsNullOrEmpty(nextDataText))
            return PaymentResult.Fail("checkoutcom: __NEXT_DATA__ missing");

        var nextJson = ThreeDsTransportHelpers.TryParseJson(nextDataText);
        var serializedToken = nextJson?["props"]?["pageProps"]?["paymentPageContextSerialized"];
        JObject? pageContext = serializedToken?.Type == JTokenType.String
            ? ThreeDsTransportHelpers.TryParseJson(serializedToken.Value<string>())
            : serializedToken as JObject;

        if (pageContext is null)
            return PaymentResult.Fail("checkoutcom: paymentPageContextSerialized missing");

        var pk = pageContext["pk"]?.ToString();
        var sessionId = pageContext["payment_session"]?["id"]?.ToString();
        if (string.IsNullOrEmpty(pk) || string.IsNullOrEmpty(sessionId))
            return PaymentResult.Fail("checkoutcom: missing pk or payment_session.id");

        c.Session.Vars["checkoutcom.pk"] = pk!;
        c.Session.Vars["checkoutcom.paymentSessionId"] = sessionId!;
        return PaymentResult.Success(sessionId);
    }

    public async Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return PaymentResult.Fail("checkoutcom: no card");

        if ((string.IsNullOrEmpty(c.Session.Vars.GetValueOrDefault("checkoutcom.pk")) ||
             string.IsNullOrEmpty(c.Session.Vars.GetValueOrDefault("checkoutcom.paymentSessionId"))) &&
            c.Session.Vars.TryGetValue("checkoutcom.offsiteUrl", out var offsiteUrl) &&
            !string.IsNullOrEmpty(offsiteUrl))
        {
            var boot = await BootstrapOffsiteAsync(c, offsiteUrl!, ct).ConfigureAwait(false);
            if (!boot.Ok) return boot;
        }

        var pk = c.Session.Vars.GetValueOrDefault("checkoutcom.pk");
        if (string.IsNullOrEmpty(pk))
            return PaymentResult.Fail("checkoutcom: missing public key");

        c.Emit("Creating token", "StatusInfo");

        var number = card.Number.Replace(" ", string.Empty);
        var holderName = card.Name;
        if (string.IsNullOrWhiteSpace(holderName))
            holderName = $"{c.ProfileData?.FirstName} {c.ProfileData?.LastName}".Trim();

        var body = new JObject
        {
            ["type"] = "card",
            ["number"] = number,
            ["expiry_month"] = card.Month ?? string.Empty,
            ["expiry_year"] = card.Year ?? string.Empty,
            ["cvv"] = card.Cvv ?? string.Empty,
            ["name"] = holderName,
            ["phone"] = new JObject(),
            ["preferred_scheme"] = string.Empty,
            ["requestSource"] = "JS",
        };

        var headers = new Dictionary<string, string>
        {
            ["Authorization"] = pk!,
        };

        var res = await ThreeDsTransportHelpers.PostJsonRawAsync(
            c, ApiHost(c) + TokensPath, body.ToString(Formatting.None), headers, "cko-token", ct)
            .ConfigureAwait(false);

        if (res is null || (res.StatusCode != 201 && !res.IsSuccess))
            return PaymentResult.Fail("checkoutcom: token creation failed");

        var json = ThreeDsTransportHelpers.TryParseJson(res.Body);
        var token = json?["token"]?.ToString();
        if (string.IsNullOrEmpty(token))
            return PaymentResult.Fail("checkoutcom: no token in response");

        c.Session.PaymentToken = token;
        c.Session.Vars["checkoutcom.token"] = token!;
        c.Session.Vars["checkoutcom.bin"] = number.Length >= 6 ? number[..Math.Min(8, number.Length)] : number;
        return PaymentResult.Success(token);
    }

    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.Vars.GetValueOrDefault("checkoutcom.token")))
        {
            var tok = await TokenizeAsync(c, ct).ConfigureAwait(false);
            if (!tok.Ok) return tok;
        }

        var pk = c.Session.Vars.GetValueOrDefault("checkoutcom.pk");
        var sessionId = c.Session.Vars.GetValueOrDefault("checkoutcom.paymentSessionId");
        var token = c.Session.Vars.GetValueOrDefault("checkoutcom.token") ?? c.Session.PaymentToken;
        if (string.IsNullOrEmpty(pk) || string.IsNullOrEmpty(sessionId) || string.IsNullOrEmpty(token))
            return PaymentResult.Fail("checkoutcom: missing pk, payment_session.id, or token");

        var bin = c.Session.Vars.GetValueOrDefault("checkoutcom.bin");
        if (string.IsNullOrEmpty(bin) && !string.IsNullOrEmpty(c.Card?.Number))
        {
            var num = c.Card.Number.Replace(" ", string.Empty);
            bin = num.Length >= 6 ? num[..Math.Min(8, num.Length)] : num;
        }

        var body = new JObject
        {
            ["type"] = "card",
            ["card_metadata"] = new JObject { ["bin"] = bin ?? string.Empty },
            ["source"] = new JObject { ["token"] = token },
        };

        var url = $"{ApiHost(c)}{PaymentSessionsPrefix}{Uri.EscapeDataString(sessionId!)}/submit";
        var res = await ThreeDsTransportHelpers.PostJsonRawAsync(
            c, url, body.ToString(Formatting.None),
            new Dictionary<string, string> { ["Authorization"] = pk! },
            "cko-session-submit", ct).ConfigureAwait(false);

        if (res is null || (res.StatusCode is not (200 or 201 or 202)))
            return PaymentResult.Fail("checkoutcom: payment-session submit failed");

        var json = ThreeDsTransportHelpers.TryParseJson(res.Body);
        var status = json?["status"]?.ToString();
        c.Session.Vars["checkoutcom.status"] = status ?? string.Empty;

        if (string.Equals(status, "Action Required", StringComparison.OrdinalIgnoreCase))
        {
            var actionUrl = json?["action"]?["url"]?.ToString();
            if (string.IsNullOrEmpty(actionUrl))
                return PaymentResult.Fail("Payment Unsupported");

            c.Session.ThreeDsUrl = actionUrl;
            c.Session.Vars["checkoutcom.actionUrl"] = actionUrl!;
            return PaymentResult.Action(actionUrl!, sessionId!);
        }

        if (string.Equals(status, "Approved", StringComparison.OrdinalIgnoreCase) ||
            string.Equals(status, "Authorized", StringComparison.OrdinalIgnoreCase) ||
            string.Equals(status, "Captured", StringComparison.OrdinalIgnoreCase) ||
            string.Equals(status, "Succeeded", StringComparison.OrdinalIgnoreCase))
        {
            return PaymentResult.Success(json?["id"]?.ToString() ?? sessionId);
        }

        c.Emit("Payment Unsupported", "error");
        return PaymentResult.Fail("Payment Unsupported");
    }

    /// <summary>
    /// Execute the issuer-specific 3-D Secure ACS handler (<c>0x1408A34F0</c>) via
    /// <see cref="CheckoutComAcsHandlers.ExecuteAsync"/>.
    /// </summary>
    public Task<AcsChallengeResult> ResolveAcsChallengeAsync(
        FlowContext c,
        string acsUrl,
        IDictionary<string, string>? initialForm = null,
        bool stripThreeDsSessionData = false,
        CancellationToken ct = default) =>
        CheckoutComAcsHandlers.ExecuteAsync(c, acsUrl, initialForm, stripThreeDsSessionData, ct);

    public async Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct)
    {
        var actionUrl = c.Session.Vars.GetValueOrDefault("checkoutcom.actionUrl") ?? c.Session.ThreeDsUrl;
        if (string.IsNullOrEmpty(actionUrl) && Uri.TryCreate(payload, UriKind.Absolute, out _))
            actionUrl = payload;

        if (string.IsNullOrEmpty(actionUrl))
            actionUrl = c.Session.Vars.GetValueOrDefault("checkoutcom.acsChallengeUrl");

        if (string.IsNullOrEmpty(actionUrl))
            return PaymentResult.Fail("checkoutcom: missing 3DS action url");

        var mode = c.Session.Vars.GetValueOrDefault("checkoutcom.mode");
        if (string.Equals(mode, "acs", StringComparison.OrdinalIgnoreCase) ||
            c.Session.Vars.ContainsKey("checkoutcom.acsChallengeUrl") ||
            (AcsHosts.IsKnown(actionUrl) &&
             !actionUrl!.Contains("/sessions-interceptor/", StringComparison.OrdinalIgnoreCase) &&
             !string.Equals(mode, "esw", StringComparison.OrdinalIgnoreCase) &&
             !string.Equals(mode, "nike-gs", StringComparison.OrdinalIgnoreCase) &&
             string.IsNullOrWhiteSpace(payload) &&
             !c.Session.Vars.ContainsKey("checkoutcom.challengeForm")))
        {
            var initialForm = ParseChallengeFormResult(c, payload) ?? ParseAcsInitialFormVar(c);
            var strip = string.Equals(c.Session.Vars.GetValueOrDefault("checkoutcom.stripThreeDsSessionData"), "true",
                StringComparison.OrdinalIgnoreCase);
            var acs = await ResolveAcsChallengeAsync(c, actionUrl!, initialForm, strip, ct).ConfigureAwait(false);
            if (acs.RequiresInteractiveVerification)
                return PaymentResult.Action(actionUrl!, acs.StatusCategory ?? "3DS verification required");
            if (!acs.Ok)
                return PaymentResult.Fail(acs.Error ?? "Payment failed (3DS)");

            var res = PaymentResult.Success(acs.ActionUrl ?? actionUrl);
            foreach (var kv in acs.Values)
                res.Fields[kv.Key] = kv.Value;
            return res;
        }

        if (string.Equals(mode, "esw", StringComparison.OrdinalIgnoreCase) ||
            string.Equals(mode, "nike-gs", StringComparison.OrdinalIgnoreCase))
        {
            return await ResolveEswThreeDsAsync(c, actionUrl!, payload, ct).ConfigureAwait(false);
        }

        if (string.Equals(mode, "interceptor", StringComparison.OrdinalIgnoreCase) ||
            (actionUrl!.Contains("/sessions-interceptor/", StringComparison.OrdinalIgnoreCase) &&
             actionUrl.Contains("api.checkout.com", StringComparison.OrdinalIgnoreCase)))
        {
            return await CompleteInterceptorFlowAsync(c, actionUrl!, payload, ct).ConfigureAwait(false);
        }

        return await CompleteShopifyOffsiteThreeDsAsync(c, actionUrl!, payload, ct).ConfigureAwait(false);
    }

    /// <summary>
    /// Path 1 completion: <c>GET {action.url}</c> -> <c>POST {action.url}/device-information</c> ->
    /// parse <c>CKO3DS.challenge.get3ds2FullRedirectChallenge</c> -> <c>hosted-challenge-notification</c> ->
    /// <c>/processing?s=</c> -> <c>/long-verify</c> -> <c>GET {redirect_to_url}</c>.
    /// </summary>
    private async Task<PaymentResult> CompleteShopifyOffsiteThreeDsAsync(
        FlowContext c, string actionUrl, string payload, CancellationToken ct)
    {
        var pageRes = await ThreeDsTransportHelpers.GetRawAsync(c, actionUrl, null, "cko-3ds-page", ct)
            .ConfigureAwait(false);
        if (pageRes is null || !pageRes.IsSuccess)
            return PaymentResult.Fail("Payment failed (3DS)");

        var txId = ExtractTransactionId(pageRes.Body);
        if (string.IsNullOrEmpty(txId))
            return PaymentResult.Fail("Payment failed (3DS)");

        var deviceForm = BuildDeviceInfoForm(c, txId!, colorDepth: "24", iframePaymentAllowed: null);
        var devRes = await ThreeDsTransportHelpers.PostFormRawAsync(
            c, actionUrl.TrimEnd('/') + "/device-information", deviceForm, null, "cko-3ds-device", ct)
            .ConfigureAwait(false);
        if (devRes is null || !devRes.IsSuccess)
            return PaymentResult.Fail("Payment failed (3DS)");

        var challengeJson = ExtractChallengePayload(devRes.Body);
        if (!string.IsNullOrEmpty(challengeJson))
            c.Session.Vars["checkoutcom.creq"] = ThreeDsTransportHelpers.Base64UrlEncode(challengeJson!);

        var challengeResult = ParseChallengeFormResult(c, payload);
        if ((challengeResult is null || challengeResult.Count == 0) &&
            TryBuildAcsChallengeFromPayload(c, challengeJson, out var acsTarget, out var acsInitialForm))
        {
            var acs = await ResolveAcsChallengeAsync(c, acsTarget!, acsInitialForm, ct: ct).ConfigureAwait(false);
            if (acs.RequiresInteractiveVerification)
                return PaymentResult.Action(acsTarget!, acs.StatusCategory ?? "3DS verification required");
            if (acs.Ok && acs.Values.Count > 0)
                challengeResult = acs.Values;
        }
        if (challengeResult is null || challengeResult.Count == 0)
        {
            c.Emit("Payment failed (3DS)", "error");
            return PaymentResult.Fail("Payment failed (3DS)");
        }

        var notifyUrl = AuthDevicesHost(c) + HostedChallengeNotificationPath;
        var notifyRes = await ThreeDsTransportHelpers.PostFormRawAsync(
            c, notifyUrl, challengeResult, null, "cko-hosted-notify", ct).ConfigureAwait(false);
        if (notifyRes is null)
            return PaymentResult.Fail("Payment failed (3DS)");

        var sessionQuery = ExtractSessionToken(c, challengeResult, notifyRes.Body);
        var procUrl = actionUrl.TrimEnd('/') + "/processing" +
                      (string.IsNullOrEmpty(sessionQuery) ? string.Empty : "?s=" + Uri.EscapeDataString(sessionQuery!));
        await ThreeDsTransportHelpers.GetRawAsync(c, procUrl, null, "cko-processing", ct).ConfigureAwait(false);

        var verifyUrl = actionUrl.TrimEnd('/') + "/long-verify";
        var verifyRes = await ThreeDsTransportHelpers.GetRawAsync(
            c, verifyUrl, null, "cko-long-verify", ct, followRedirects: false).ConfigureAwait(false);
        if (verifyRes is null)
            return PaymentResult.Fail("Payment failed (3DS)");

        var redirectTarget = ExtractVerifyRedirect(verifyRes);
        if (string.IsNullOrEmpty(redirectTarget))
            return PaymentResult.Fail("Payment failed (3DS)");

        var finalRes = await ThreeDsTransportHelpers.GetRawAsync(c, redirectTarget!, null, "cko-final-redirect", ct)
            .ConfigureAwait(false);
        var replaceUrl = ExtractTopLocationReplace(finalRes?.Body);
        var landed = !string.IsNullOrEmpty(replaceUrl) ? replaceUrl! : (finalRes?.Url.ToString() ?? redirectTarget!);
        c.Session.Vars["checkoutcom.redirectUrl"] = landed;
        return PaymentResult.Success(landed);
    }

    /// <summary>
    /// Path 2 completion: Gateway Dispatcher (<c>/sessions-interceptor/{id}</c>).
    /// </summary>
    private async Task<PaymentResult> CompleteInterceptorFlowAsync(
        FlowContext c, string url, string payload, CancellationToken ct)
    {
        var idMatch = Regex.Match(url, @"/sessions-interceptor/([^/?#]+)", RegexOptions.IgnoreCase);
        var interceptorId = idMatch.Success ? idMatch.Groups[1].Value : c.Session.Vars.GetValueOrDefault("checkoutcom.interceptorId");
        if (string.IsNullOrEmpty(interceptorId))
            return PaymentResult.Fail("checkoutcom: interceptor id not found");

        var pageRes = await ThreeDsTransportHelpers.GetRawAsync(c, url, null, "cko-int-page", ct)
            .ConfigureAwait(false);
        if (pageRes is null || !pageRes.IsSuccess)
            return PaymentResult.Fail("Payment failed (3DS)");

        var txId = ExtractTransactionId(pageRes.Body);
        if (string.IsNullOrEmpty(txId))
            return PaymentResult.Fail("Payment failed (3DS)");

        var apiHost = c.Session.Vars.TryGetValue("checkoutcom.apiHost", out var h) && !string.IsNullOrEmpty(h)
            ? h.TrimEnd('/')
            : ThreeDsTransportHelpers.OriginOf(url);

        var methodPayload = new JObject { ["threeDSServerTransID"] = txId }.ToString(Formatting.None);
        var methodRes = await ThreeDsTransportHelpers.PostFormRawAsync(
            c,
            apiHost + MethodNotificationPath,
            new Dictionary<string, string>
            {
                ["threeDSMethodData"] = Convert.ToBase64String(Encoding.UTF8.GetBytes(methodPayload)),
            },
            null,
            "cko-int-method-notify",
            ct).ConfigureAwait(false);
        if (methodRes is null)
            return PaymentResult.Fail("Payment failed (3DS)");

        var deviceForm = BuildDeviceInfoForm(c, txId!, colorDepth: "24", iframePaymentAllowed: "false");
        var devUrl = $"{apiHost}/sessions-interceptor/{Uri.EscapeDataString(interceptorId!)}/device-information";
        var devRes = await ThreeDsTransportHelpers.PostFormRawAsync(
            c, devUrl, deviceForm, null, "cko-int-device-info", ct).ConfigureAwait(false);
        if (devRes is null || !devRes.IsSuccess)
            return PaymentResult.Fail("Payment failed (3DS)");

        var challengeJson = ExtractChallengePayload(devRes.Body);
        if (!string.IsNullOrEmpty(challengeJson))
            c.Session.Vars["checkoutcom.creq"] = ThreeDsTransportHelpers.Base64UrlEncode(challengeJson!);

        var challengeResult = ParseChallengeFormResult(c, payload);
        if ((challengeResult is null || challengeResult.Count == 0) &&
            TryBuildAcsChallengeFromPayload(c, challengeJson, out var acsTarget, out var acsInitialForm))
        {
            var acs = await ResolveAcsChallengeAsync(c, acsTarget!, acsInitialForm, ct: ct).ConfigureAwait(false);
            if (acs.RequiresInteractiveVerification)
                return PaymentResult.Action(acsTarget!, acs.StatusCategory ?? "3DS verification required");
            if (acs.Ok && acs.Values.Count > 0)
                challengeResult = acs.Values;
        }
        if (challengeResult is null || challengeResult.Count == 0)
            return PaymentResult.Fail("Payment failed (3DS)");

        var notifyRes = await ThreeDsTransportHelpers.PostFormRawAsync(
            c, apiHost + HostedChallengeNotificationPath, challengeResult, null, "cko-int-hosted-notify", ct)
            .ConfigureAwait(false);
        if (notifyRes is null)
            return PaymentResult.Fail("Payment failed (3DS)");

        var redirectUrl = ExtractVerifyRedirect(notifyRes) ?? ThreeDsTransportHelpers.TryParseJson(notifyRes.Body)?["redirect_to_url"]?.ToString();
        if (!string.IsNullOrEmpty(redirectUrl))
        {
            await ThreeDsTransportHelpers.GetRawAsync(c, redirectUrl!, null, "cko-int-redirect", ct).ConfigureAwait(false);
            c.Session.Vars["checkoutcom.redirectUrl"] = redirectUrl!;
            return PaymentResult.Success(redirectUrl);
        }

        return PaymentResult.Success(interceptorId);
    }

    /// <summary>
    /// Path 3 (<c>NIKE-GS</c> / ESW): for <c>authentication-devices.checkout.com</c>, runs 3DS2 with
    /// <c>browserColorDepth = "32"</c> and <c>iframePaymentAllowed = "true"</c>, or falls back to
    /// 3DS1 <c>PaReq</c>/<c>merchantData</c>/<c>termUrl</c>.
    /// </summary>
    public async Task<PaymentResult> ResolveEswThreeDsAsync(
        FlowContext c, string redirectUrl, string payload, CancellationToken ct)
    {
        // R1303: 0x1408A34F0 opens every issuer hop by logging "Starting 3DS: <host>" under the "3DS"
        // category and re-fingerprinting the transport to chrome_131, then restores the profile it saved.
        // The log is unconditional there -- it happens before the host switch -- so it is unconditional
        // here too, and acsKnown records whether the switch had a case for it. The profile is per request
        // rather than saved and written back, which is the same swap without mutating the context.
        c.Emit(AcsHosts.Describe(redirectUrl), AcsHosts.LogCategory);
        c.Session.Vars["checkoutcom.acsHost"] = AcsHosts.HostOf(redirectUrl);
        c.Session.Vars["checkoutcom.acsKnown"] = AcsHosts.IsKnown(redirectUrl) ? "true" : "false";
        var hopProfile = AcsHosts.ProfileFor(redirectUrl, c.BrowserProfile);

        var pageRes = await ThreeDsTransportHelpers
            .GetRawAsync(c, redirectUrl, null, "cko-esw-page", ct, profile: hopProfile)
            .ConfigureAwait(false);
        if (pageRes is null || !pageRes.IsSuccess)
            return PaymentResult.Fail("Payment failed (3DS)");

        var txId = ExtractTransactionId(pageRes.Body);
        if (string.IsNullOrEmpty(txId))
        {
            var (_, inputs) = ThreeDsTransportHelpers.ExtractForm(pageRes.Body);
            if (inputs.ContainsKey("PaReq") || inputs.ContainsKey("MD"))
            {
                c.Session.Vars["checkoutcom.3ds1.paReq"] = inputs.GetValueOrDefault("PaReq") ?? string.Empty;
                c.Session.Vars["checkoutcom.3ds1.md"] = inputs.GetValueOrDefault("MD") ?? inputs.GetValueOrDefault("merchantData") ?? string.Empty;
                c.Session.Vars["checkoutcom.3ds1.termUrl"] = inputs.GetValueOrDefault("TermUrl") ?? inputs.GetValueOrDefault("termUrl") ?? string.Empty;
                return PaymentResult.Success("3ds1");
            }
            return PaymentResult.Fail("Payment failed (3DS)");
        }

        var deviceForm = BuildDeviceInfoForm(c, txId!, colorDepth: "32", iframePaymentAllowed: "true");
        var devRes = await ThreeDsTransportHelpers.PostFormRawAsync(
            c, redirectUrl.TrimEnd('/') + "/device-information", deviceForm, null, "cko-esw-device", ct)
            .ConfigureAwait(false);
        if (devRes is null || !devRes.IsSuccess)
            return PaymentResult.Fail("Payment failed (3DS)");

        var challengeResult = ParseChallengeFormResult(c, payload);
        if ((challengeResult is null || challengeResult.Count == 0) &&
            TryBuildAcsChallengeFromPayload(c, ExtractChallengePayload(devRes.Body), out var acsTarget, out var acsInitialForm))
        {
            var acs = await ResolveAcsChallengeAsync(c, acsTarget!, acsInitialForm, ct: ct).ConfigureAwait(false);
            if (acs.RequiresInteractiveVerification)
                return PaymentResult.Action(acsTarget!, acs.StatusCategory ?? "3DS verification required");
            if (acs.Ok && acs.Values.Count > 0)
                challengeResult = acs.Values;
        }
        if (challengeResult is null || challengeResult.Count == 0)
            return PaymentResult.Fail("Payment failed (3DS)");

        var sessionQuery = ExtractSessionToken(c, challengeResult, devRes.Body);
        var notifyUrl = AuthDevicesHost(c) + HostedChallengeNotificationPath +
                        (string.IsNullOrEmpty(sessionQuery) ? string.Empty : "?s=" + Uri.EscapeDataString(sessionQuery!));
        var notifyRes = await ThreeDsTransportHelpers.PostFormRawAsync(
            c, notifyUrl, challengeResult, null, "cko-esw-notify", ct, followRedirects: false)
            .ConfigureAwait(false);
        if (notifyRes is null)
            return PaymentResult.Fail("Payment failed (3DS)");

        var procUrl = redirectUrl.TrimEnd('/') + "/processing" +
                      (string.IsNullOrEmpty(sessionQuery) ? string.Empty : "?s=" + Uri.EscapeDataString(sessionQuery!));
        await ThreeDsTransportHelpers.GetRawAsync(c, procUrl, null, "cko-esw-proc", ct).ConfigureAwait(false);

        var verifyRes = await ThreeDsTransportHelpers.GetRawAsync(
            c, redirectUrl.TrimEnd('/') + "/long-verify", null, "cko-esw-verify", ct, followRedirects: false)
            .ConfigureAwait(false);
        var finalTarget = verifyRes is null ? null : ExtractVerifyRedirect(verifyRes);
        if (string.IsNullOrEmpty(finalTarget))
            return PaymentResult.Fail("Payment failed (3DS)");

        c.Session.Vars["checkoutcom.redirectUrl"] = finalTarget!;
        return PaymentResult.Success(finalTarget);
    }

    /// <summary>
    /// Path 4 (Mollie): tokenizes card at <c>api.cc.mollie.com/v1/card-tokens</c> and posts challenge
    /// notifications to <c>api.checkout.com/sessions-interceptor/challenge-notification</c>.
    /// </summary>
    public static async Task<PaymentResult> NotifyMollieChallengeAsync(
        FlowContext c,
        IDictionary<string, string> challengeForm,
        CancellationToken ct)
    {
        var host = c.Session.Vars.TryGetValue("checkoutcom.apiHost", out var h) && !string.IsNullOrEmpty(h)
            ? h.TrimEnd('/')
            : DefaultApiHost;
        var res = await ThreeDsTransportHelpers.PostFormRawAsync(
            c, host + ChallengeNotificationPath, challengeForm, null, "mollie-cko-challenge", ct)
            .ConfigureAwait(false);
        return res is not null && res.IsSuccess
            ? PaymentResult.Success(res.Body)
            : PaymentResult.Fail("mollie: checkout.com challenge notification failed");
    }

    internal static Dictionary<string, string> BuildDeviceInfoForm(
        FlowContext c,
        string threeDsServerTransId,
        string colorDepth,
        string? iframePaymentAllowed)
    {
        var form = new Dictionary<string, string>
        {
            ["threeDSServerTransID"] = threeDsServerTransId,
            ["threeDSCompInd"] = "Y",
            ["browserScreenWidth"] = "1920",
            ["browserScreenHeight"] = "1080",
            ["browserColorDepth"] = colorDepth,
            ["browserUserAgent"] = c.Session.UserAgent ?? "Mozilla/5.0",
            ["browserLanguage"] = "en-US",
            ["browserJavaEnabled"] = "false",
            ["browserTZ"] = "-120",
        };
        if (!string.IsNullOrEmpty(iframePaymentAllowed))
            form["iframePaymentAllowed"] = iframePaymentAllowed!;
        return form;
    }

    internal static string? ExtractTransactionId(string? html)
    {
        if (string.IsNullOrEmpty(html)) return null;
        var m = Regex.Match(html, @"transactionId\s*:\s*'([^']+)'", RegexOptions.IgnoreCase);
        return m.Success ? m.Groups[1].Value : null;
    }

    internal static string? ExtractChallengePayload(string? html)
    {
        if (string.IsNullOrEmpty(html)) return null;
        var m = Regex.Match(html, @"CKO3DS\.challenge\.get3ds2FullRedirectChallenge\(\s*'([^']+)'\s*\)",
            RegexOptions.IgnoreCase);
        return m.Success ? m.Groups[1].Value : null;
    }

    internal static string? ExtractTopLocationReplace(string? html)
    {
        if (string.IsNullOrEmpty(html)) return null;
        var m = Regex.Match(html, @"window\.top\.location\.replace\(\s*'([^']+)'\s*\)", RegexOptions.IgnoreCase);
        return m.Success ? m.Groups[1].Value : null;
    }

    private static Dictionary<string, string>? ParseChallengeFormResult(FlowContext c, string payload)
    {
        var raw = !string.IsNullOrWhiteSpace(payload)
            ? payload
            : c.Session.Vars.GetValueOrDefault("checkoutcom.challengeForm");
        if (string.IsNullOrWhiteSpace(raw)) return null;

        var json = ThreeDsTransportHelpers.TryParseJson(raw);
        if (json is not null)
        {
            var dict = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            foreach (var prop in json.Properties())
                dict[prop.Name] = prop.Value?.ToString() ?? string.Empty;
            return dict;
        }

        return new Dictionary<string, string> { ["cres"] = raw! };
    }

    private static string? ExtractSessionToken(FlowContext c, IDictionary<string, string> form, string? body)
    {
        if (c.Session.Vars.TryGetValue("checkoutcom.s", out var s) && !string.IsNullOrEmpty(s))
            return s;
        if (form.TryGetValue("s", out var fs) && !string.IsNullOrEmpty(fs))
            return fs;
        if (!string.IsNullOrEmpty(body))
        {
            var m = Regex.Match(body, @"[?&]s=([A-Za-z0-9_\-]+)");
            if (m.Success) return m.Groups[1].Value;
        }
        return null;
    }

    private static string? ExtractVerifyRedirect(NetResponse res)
    {
        var json = ThreeDsTransportHelpers.TryParseJson(res.Body);
        if (json is not null &&
            string.Equals(json["action"]?.ToString(), "Redirect", StringComparison.OrdinalIgnoreCase))
        {
            var target = json["redirect_to_url"]?.ToString();
            if (!string.IsNullOrEmpty(target)) return target;
        }

        if (res.StatusCode is 301 or 302 or 303 or 307 or 308 &&
            res.Headers.TryGetValue("Location", out var loc) &&
            !string.IsNullOrEmpty(loc))
        {
            return loc;
        }

        return null;
    }

    private static Dictionary<string, string>? ParseAcsInitialFormVar(FlowContext c)
    {
        if (!c.Session.Vars.TryGetValue("checkoutcom.acsForm", out var raw) || string.IsNullOrWhiteSpace(raw))
            return null;
        var json = ThreeDsTransportHelpers.TryParseJson(raw);
        if (json is null) return null;
        var dict = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        foreach (var prop in json.Properties())
            dict[prop.Name] = prop.Value?.ToString() ?? string.Empty;
        return dict;
    }

    private static bool TryBuildAcsChallengeFromPayload(
        FlowContext c,
        string? challengeJson,
        out string? acsUrl,
        out Dictionary<string, string> initialForm)
    {
        initialForm = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        acsUrl = c.Session.Vars.GetValueOrDefault("checkoutcom.acsUrl");

        var parsed = ThreeDsTransportHelpers.TryParseJson(challengeJson);
        if (parsed is not null)
        {
            acsUrl ??= parsed["acsURL"]?.ToString() ?? parsed["acsUrl"]?.ToString() ?? parsed["url"]?.ToString();
            var creq = parsed["creq"]?.ToString() ?? c.Session.Vars.GetValueOrDefault("checkoutcom.creq");
            if (!string.IsNullOrEmpty(creq)) initialForm["creq"] = creq!;
            var sess = parsed["threeDSSessionData"]?.ToString();
            if (!string.IsNullOrEmpty(sess)) initialForm["threeDSSessionData"] = sess!;
        }

        var fromVar = ParseAcsInitialFormVar(c);
        if (fromVar is not null)
        {
            foreach (var kv in fromVar) initialForm[kv.Key] = kv.Value;
        }

        return !string.IsNullOrEmpty(acsUrl);
    }
}
