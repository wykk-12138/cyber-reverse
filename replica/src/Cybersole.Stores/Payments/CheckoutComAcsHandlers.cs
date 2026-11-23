using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Net.WebSockets;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Outcome of running a decoded Checkout.com / Adyen issuer ACS handler (<c>0x1408A34F0</c>).
/// Mirrors <c>AcsResult</c> (<c>0x144C95D58</c>) plus interactive fallback metadata (<c>20_fallback</c>).
/// </summary>
public sealed class AcsChallengeResult
{
    public bool Ok { get; init; }
    public bool RequiresInteractiveVerification { get; init; }
    public string Cluster { get; init; } = string.Empty;
    public string? ActionUrl { get; init; }
    public Dictionary<string, string> Values { get; init; } = new(StringComparer.OrdinalIgnoreCase);
    public string? Error { get; init; }
    public string? StatusText { get; init; }
    public string? StatusCategory { get; init; }
}

/// <summary>
/// Per-issuer 3-D Secure ACS challenge state machines dispatched by <c>0x1408A34F0</c>
/// (<c>01_apata</c> through <c>19_cardinal</c> covering all 28 hosts in <see cref="AcsHosts.Known"/>,
/// plus <c>20_fallback</c> for interactive verification).
/// </summary>
public static class CheckoutComAcsHandlers
{
    private const int DefaultMaxPollAttempts = 60;
    private const string SoldoMultipartBoundary = "T21mAUisfuWtVfY8";

    /// <summary>
    /// Map an ACS host or URL to its decoded handler cluster id (<c>01_apata</c>.. <c>19_cardinal</c>,
    /// or <c>20_fallback</c> for any unrecognised host).
    /// </summary>
    public static string ClusterForHost(string? urlOrHost) =>
        AcsHosts.HostOf(urlOrHost) switch
        {
            "acs.apata.io" or "acs-challenge.apata.io" => "01_apata",
            "acs2.edb.com" => "02_edb",
            "3ds.soldo.com" => "03_soldo",
            "acs.touch.tech" => "04_touchtech",
            "cacs.icard.com" or "cacs-v2.icard.com" => "05_icard",
            "acs.revolut.com" or "poseidon.revolut.com" => "06_revolut",
            "3dsecure.zen.com" => "07_zen",
            "verify.monzo.com" => "08_monzo",
            "3dsecure.mbank.cz" => "09_mbank",
            "secure4.arcot.com" => "10_arcot",
            "acs.capitalone.com" => "11_capitalone",
            "acs1.3ds.modirum.com" or "acs2.3ds.modirum.com"
                or "acs1.mpts.modirum.com" or "acs2.mpts.modirum.com" => "12_modirum",
            "api.secure-code.bunq.com" or "api.id.mastercard.bunq.com" => "13_bunq",
            "3dsecure.starlingbank.com" => "14_starling",
            "3ds-a.live.ext.prod.enfuce.com" or "3ds-b.live.ext.prod.enfuce.com" => "15_enfuce",
            "authentication-acs.marqeta.com" => "16_marqeta",
            "acs-safekey.americanexpress.com" => "17_amex",
            "idcheck.acs.touchtechpayments.com" or "verifiedbyvisa.acs.touchtechpayments.com" => "18_touchtechpayments",
            "authentication.cardinalcommerce.com" => "19_cardinal",
            _ => "20_fallback",
        };

    /// <summary>
    /// Dispatch an ACS challenge hop to its decoded cluster handler, matching <c>0x1408A34F0</c>.
    /// </summary>
    public static async Task<AcsChallengeResult> ExecuteAsync(
        FlowContext c,
        string acsUrl,
        IDictionary<string, string>? initialForm = null,
        bool stripThreeDsSessionData = false,
        CancellationToken ct = default,
        Func<string, string, CancellationToken, Task<string?>>? webSocketClient = null)
    {
        var urlHost = AcsHosts.HostOf(acsUrl);
        var overrideHost = AcsHosts.HostOf(c.Session.Vars.GetValueOrDefault("checkoutcom.acsHost"));
        var effectiveHost = AcsHosts.IsKnown(urlHost)
            ? urlHost
            : (!string.IsNullOrEmpty(overrideHost) && AcsHosts.IsKnown(overrideHost) ? overrideHost : urlHost);

        c.Emit(AcsHosts.LogPrefix + effectiveHost, AcsHosts.LogCategory);
        c.Session.Vars["checkoutcom.acsHost"] = effectiveHost;
        c.Session.Vars["checkoutcom.acsKnown"] = AcsHosts.IsKnown(effectiveHost) ? "true" : "false";

        var cluster = ClusterForHost(effectiveHost);
        c.Session.Vars["checkoutcom.acsCluster"] = cluster;

        var form = initialForm is null
            ? new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            : new Dictionary<string, string>(initialForm, StringComparer.OrdinalIgnoreCase);

        var profile = AcsHosts.ProfileFor(effectiveHost, c.BrowserProfile);
        var ctx = new AcsContext(c, acsUrl, effectiveHost, cluster, form, stripThreeDsSessionData, profile, webSocketClient);

        return cluster switch
        {
            "01_apata" => await HandleApataAsync(ctx, ct).ConfigureAwait(false),
            "02_edb" => await HandleEdbAsync(ctx, ct).ConfigureAwait(false),
            "03_soldo" => await HandleSoldoAsync(ctx, ct).ConfigureAwait(false),
            "04_touchtech" => await HandleTouchtechAsync(ctx, ct).ConfigureAwait(false),
            "05_icard" => await HandleIcardAsync(ctx, ct).ConfigureAwait(false),
            "06_revolut" => await HandleRevolutAsync(ctx, ct).ConfigureAwait(false),
            "07_zen" => await HandleZenAsync(ctx, ct).ConfigureAwait(false),
            "08_monzo" => await HandleMonzoAsync(ctx, ct).ConfigureAwait(false),
            "09_mbank" => await HandleMbankAsync(ctx, ct).ConfigureAwait(false),
            "10_arcot" => await HandleArcotAsync(ctx, ct).ConfigureAwait(false),
            "11_capitalone" => await HandleCapitalOneAsync(ctx, ct).ConfigureAwait(false),
            "12_modirum" => await HandleModirumAsync(ctx, ct).ConfigureAwait(false),
            "13_bunq" => await HandleBunqAsync(ctx, ct).ConfigureAwait(false),
            "14_starling" => await HandleStarlingAsync(ctx, ct).ConfigureAwait(false),
            "15_enfuce" => await HandleEnfuceAsync(ctx, ct).ConfigureAwait(false),
            "16_marqeta" => await HandleMarqetaAsync(ctx, ct).ConfigureAwait(false),
            "17_amex" => await HandleAmexAsync(ctx, ct).ConfigureAwait(false),
            "18_touchtechpayments" => await HandleTouchtechPaymentsAsync(ctx, ct).ConfigureAwait(false),
            "19_cardinal" => await HandleCardinalAsync(ctx, ct).ConfigureAwait(false),
            _ => FallbackResult(c, cluster),
        };
    }

    // -------------------------------------------------------------------------
    // 01_apata: acs.apata.io, acs-challenge.apata.io (0x140899160)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleApataAsync(AcsContext a, CancellationToken ct)
    {
        if (a.StripThreeDsSessionData)
            a.InitialForm.Remove("threeDSSessionData");

        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var target = a.EntryUrl;
        HttpContent content = BuildFormContent(a.InitialForm);
        string? pollToken = null;
        Dictionary<string, string>? challengeInputs = null;

        NetResponse? res = null;
        for (var hop = 0; hop < 5; hop++)
        {
            res = await a.PostAsync(target, content, null, "acs-apata-step1", ct).ConfigureAwait(false);
            if (res is null || !res.IsSuccess)
                return a.Fail("apata: initial ACS post failed");

            var body = res.Body ?? string.Empty;
            if (body.Contains("How would you like to approve this payment", StringComparison.Ordinal))
            {
                var form = FindFirstForm(body);
                var txId = ReadInputValue(body, "transactionId") ?? string.Empty;
                var appVal = HtmlFormDom.ExtractElementAttribute(
                                 body, "button[id*='app' i], label[id*='app' i]", "value")
                             ?? "0";
                target = ResolveAction(res.Url.ToString(), form.Action) ?? target;
                var approveJson = new JObject
                {
                    ["action"] = "SUBMIT",
                    ["transactionId"] = txId,
                    ["answer"] = appVal,
                }.ToString(Formatting.None);
                content = new StringContent(approveJson, Encoding.UTF8, "application/json");
                continue;
            }

            var redirectForm = FindFormByIdOrName(body, id: "redirect-form");
            if (redirectForm.Found)
            {
                return a.Success(
                    ResolveAction(res.Url.ToString(), redirectForm.Action),
                    redirectForm.Inputs);
            }

            var challengeForm = FindFormByIdOrName(body, id: "challenge_form", name: "challenge_form");
            if (!challengeForm.Found) challengeForm = FindFirstForm(body);
            challengeInputs = challengeForm.Inputs;

            var pollMatch = Regex.Match(body, "\"?pollToken\"?\\s?[:|=]\\s?\"(.*?)\"");
            pollToken = pollMatch.Success ? pollMatch.Groups[1].Value : null;
            break;
        }

        a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
        var pollUrl = "https://acs-challenge.apata.io/v1/PollTransaction";
        var pollBody = new JObject { ["pollToken"] = pollToken ?? string.Empty }.ToString(Formatting.None);
        for (var attempt = 0; attempt < a.MaxPolls; attempt++)
        {
            var pollRes = await a.PostJsonAsync(pollUrl, pollBody, null, "acs-apata-poll", ct).ConfigureAwait(false);
            if (pollRes is null || !pollRes.IsSuccess)
                return a.Fail("apata: PollTransaction failed");

            var state = ThreeDsTransportHelpers.TryParseJson(pollRes.Body)?["state"]?.ToString();
            if (string.Equals(state, "COMPLETED", StringComparison.Ordinal))
                break;

            await a.DelayAsync(500, ct).ConfigureAwait(false);
        }

        a.Flow.Emit("Completing 3D Secure", "StatusInfo");
        var finalRes = await a.PostFormAsync(
            "https://acs-challenge.apata.io/v1/BrowserCReqAction",
            challengeInputs ?? new Dictionary<string, string>(),
            null,
            "acs-apata-complete",
            ct).ConfigureAwait(false);
        if (finalRes is null || !finalRes.IsSuccess)
            return a.Fail("apata: BrowserCReqAction failed");

        var finalForm = FindFirstForm(finalRes.Body);
        return a.Success(
            ResolveAction(finalRes.Url.ToString(), finalForm.Action),
            finalForm.Inputs);
    }

    // -------------------------------------------------------------------------
    // 02_edb: acs2.edb.com (0x1408A6F00)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleEdbAsync(AcsContext a, CancellationToken ct)
    {
        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var target = a.EntryUrl;
        HttpContent? content = BuildFormContent(a.InitialForm);
        string? collectUrl = null;

        for (var hop = 0; hop < 12; hop++)
        {
            var res = await a.PostAsync(target, content, null, "acs-edb-step1", ct).ConfigureAwait(false);
            if (res is null || !res.IsSuccess)
                return a.Fail("edb: step 1 request failed");

            var form = FindFirstForm(res.Body);
            if (!form.Found)
            {
                await a.DelayAsync(500, ct).ConfigureAwait(false);
                continue;
            }

            switch (form.Name)
            {
                case "postform":
                    target = ResolveAction(res.Url.ToString(), form.Action) ?? target;
                    content = BuildFormContent(form.Inputs);
                    continue;

                case "myForm":
                    target = "https://secure.edb.com" + (form.Action ?? string.Empty) + "?fp=583237862";
                    content = BuildFormContent(new Dictionary<string, string> { ["fingprnt"] = "583237862" });
                    continue;

                case "externalPre":
                    target = "https://secure.edb.com" + (form.Action ?? string.Empty);
                    content = null;
                    continue;

                case "externalCollect":
                    collectUrl = "https://secure.edb.com" + (form.Action ?? string.Empty);
                    break;

                default:
                    await a.DelayAsync(500, ct).ConfigureAwait(false);
                    continue;
            }

            if (collectUrl is not null) break;
        }

        if (string.IsNullOrEmpty(collectUrl))
            return a.Fail("edb: externalCollect form not reached");

        a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
        string? toAcsAction = null;
        Dictionary<string, string>? toAcsInputs = null;
        for (var attempt = 0; attempt < a.MaxPolls; attempt++)
        {
            var collectRes = await a.PostAsync(collectUrl!, null, null, "acs-edb-collect", ct).ConfigureAwait(false);
            if (collectRes is null || !collectRes.IsSuccess)
                return a.Fail("edb: externalCollect failed");

            var toAcsForm = FindFormByIdOrName(collectRes.Body, id: "toACSForm");
            if (toAcsForm.Found)
            {
                toAcsAction = ResolveAction(collectRes.Url.ToString(), toAcsForm.Action) ?? collectUrl;
                toAcsInputs = toAcsForm.Inputs;
                break;
            }

            await a.DelayAsync(1000, ct).ConfigureAwait(false);
        }

        if (toAcsAction is null || toAcsInputs is null)
            return a.Fail("edb: #toACSForm timed out");

        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        for (var attempt = 0; attempt < a.MaxPolls; attempt++)
        {
            var paresRes = await a.PostFormAsync(toAcsAction, toAcsInputs, null, "acs-edb-pares", ct).ConfigureAwait(false);
            if (paresRes is null || !paresRes.IsSuccess)
                return a.Fail("edb: PAResForm request failed");

            var paresForm = FindFormByIdOrName(paresRes.Body, name: "PAResForm");
            if (paresForm.Found)
                return a.Success(null, paresForm.Inputs);

            await a.DelayAsync(1000, ct).ConfigureAwait(false);
        }

        return a.Fail("edb: PAResForm timed out");
    }

    // -------------------------------------------------------------------------
    // 03_soldo: 3ds.soldo.com (0x1408AEE80)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleSoldoAsync(AcsContext a, CancellationToken ct)
    {
        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1Res = await a.PostFormAsync(a.EntryUrl, a.InitialForm, null, "acs-soldo-step1", ct).ConfigureAwait(false);
        if (step1Res is null || !step1Res.IsSuccess)
            return a.Fail("soldo: step 1 failed");

        var form = FindFirstForm(step1Res.Body);
        var currentFields = form.Inputs;
        var v2FormUrl = "https://" + a.OriginalAuthorityOrHost + "//v2Form";

        a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
        for (var attempt = 0; attempt < a.MaxPolls; attempt++)
        {
            var content = BuildPercentEncodedWebKitMultipart(currentFields, SoldoMultipartBoundary);
            var pollRes = await a.PostAsync(v2FormUrl, content, null, "acs-soldo-v2form", ct).ConfigureAwait(false);
            if (pollRes is null || !pollRes.IsSuccess)
                return a.Fail("soldo: //v2Form failed");

            var nextForm = FindFirstForm(pollRes.Body);
            currentFields = nextForm.Inputs;
            if (currentFields.ContainsKey("cres"))
                return a.Success(null, currentFields);

            await a.DelayAsync(1000, ct).ConfigureAwait(false);
        }

        return a.Fail("soldo: cres timed out");
    }

    internal static ByteArrayContent BuildPercentEncodedWebKitMultipart(
        IDictionary<string, string> fields,
        string boundarySuffix = SoldoMultipartBoundary)
    {
        var fullBoundary = "----WebKitFormBoundary" + boundarySuffix;
        var sb = new StringBuilder();
        var first = true;
        foreach (var kv in fields)
        {
            if (!first) sb.Append("\r\n");
            first = false;
            sb.Append("--").Append(fullBoundary).Append("\r\n");
            sb.Append("Content-Disposition: form-data; name=\"")
              .Append(Uri.EscapeDataString(kv.Key))
              .Append("\"\r\n\r\n");
            sb.Append(Uri.EscapeDataString(kv.Value ?? string.Empty));
        }
        sb.Append("\r\n--").Append(fullBoundary).Append("--\r\n");

        var content = new ByteArrayContent(Encoding.UTF8.GetBytes(sb.ToString()));
        content.Headers.Remove("Content-Type");
        content.Headers.TryAddWithoutValidation("Content-Type", "multipart/form-data; boundary=" + fullBoundary);
        return content;
    }

    // -------------------------------------------------------------------------
    // 04_touchtech: acs.touch.tech (0x1408B25B0)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleTouchtechAsync(AcsContext a, CancellationToken ct)
    {
        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1 = await a.PostFormAsync(a.EntryUrl, a.InitialForm, null, "acs-touchtech-step1", ct).ConfigureAwait(false);
        if (step1 is null || !step1.IsSuccess)
            return a.Fail("touchtech: step 1 failed");

        var body = step1.Body ?? string.Empty;
        if (body.Contains("redirect()", StringComparison.Ordinal))
        {
            return ExtractInlineTouchtechRedirect(a, body);
        }

        var token = Between(body, "token: '", "'");
        var title = ExtractHtmlTitle(body).ToLowerInvariant();
        var flag = false;

        if (title.Contains("wise", StringComparison.Ordinal) ||
            (title.Contains("3d-secure", StringComparison.Ordinal) && body.Contains("DELEGATED", StringComparison.Ordinal)))
        {
            var selectUrl = $"https://acs.touch.tech/v1/transactions/{token}/challenge/select";
            var selectBody = new JObject
            {
                ["transactionToken"] = token,
                ["challengeMethod"] = "DELEGATED",
            }.ToString(Formatting.None);

            for (var i = 0; i < 3; i++)
            {
                var selRes = await a.PostJsonAsync(selectUrl, selectBody, null, "acs-touchtech-select", ct).ConfigureAwait(false);
                if (selRes is null) return a.Fail("touchtech: select unreachable");
                if (selRes.StatusCode == 400)
                {
                    flag = true;
                    break;
                }
                if (selRes.IsSuccess)
                {
                    var st = ThreeDsTransportHelpers.TryParseJson(selRes.Body)?["status"]?.ToString();
                    if (string.Equals(st, "ok", StringComparison.OrdinalIgnoreCase))
                        break;
                }
            }
        }

        if (body.Contains("Monese", StringComparison.Ordinal) || flag)
            return FallbackResult(a.Flow, a.Cluster);

        a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
        var pollUrl = $"https://acs.touch.tech/v1/transactions/{token}/challenge?retryCounter=0";
        var pollHeaders = new Dictionary<string, string>
        {
            ["Content-Type"] = "application/json",
            ["Accept"] = "*/*",
            ["Referer"] = "https://acs.touch.tech/v1/emv3ds/challenge",
        };
        for (var attempt = 0; attempt < a.MaxPolls; attempt++)
        {
            var pollRes = await a.GetAsync(pollUrl, pollHeaders, "acs-touchtech-poll", ct).ConfigureAwait(false);
            if (pollRes is null || !pollRes.IsSuccess)
                return a.Fail("touchtech: challenge poll failed");

            var st = ThreeDsTransportHelpers.TryParseJson(pollRes.Body)?["status"]?.ToString();
            if (st is "blocked" or "declined" or "failure" or "expired" or "authenticated")
                break;

            await a.DelayAsync(500, ct).ConfigureAwait(false);
        }

        a.Flow.Emit("Completing 3D Secure", "StatusInfo");
        var contRes = await a.PostAsync(
            $"https://acs.touch.tech/v1/{token}/continue",
            null,
            null,
            "acs-touchtech-continue",
            ct).ConfigureAwait(false);
        if (contRes is null || !contRes.IsSuccess)
            return a.Fail("touchtech: continue failed");

        var form = FindFirstForm(contRes.Body);
        return a.Success(null, form.Inputs);
    }

    private static AcsChallengeResult ExtractInlineTouchtechRedirect(AcsContext a, string body)
    {
        var pares = Between(body, "var pares = \"", "\"");
        var b64 = Between(body, "atob(\"", "\"");
        var md = string.Empty;
        if (!string.IsNullOrEmpty(b64))
        {
            try
            {
                var decoded = Encoding.UTF8.GetString(DecodeBase64Flexible(b64));
                md = ThreeDsTransportHelpers.TryParseJson(decoded)?["md"]?.ToString() ?? string.Empty;
            }
            catch { /* keep empty md if invalid base64 */ }
        }

        return a.Success(null, new Dictionary<string, string>
        {
            ["PaRes"] = pares,
            ["MD"] = md,
        });
    }

    // -------------------------------------------------------------------------
    // 05_icard: cacs.icard.com (0), cacs-v2.icard.com (1) (0x1408A5480)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleIcardAsync(AcsContext a, CancellationToken ct)
    {
        var isV2 = a.EffectiveHost.Contains("cacs-v2", StringComparison.OrdinalIgnoreCase);

        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1 = await a.PostFormAsync(
            a.EntryUrl,
            a.InitialForm,
            null,
            "acs-icard-step1",
            ct,
            followRedirects: false).ConfigureAwait(false);
        if (step1 is null)
            return a.Fail("icard: step 1 unreachable");

        if (step1.StatusCode == 200)
        {
            var form1 = FindFormByIdOrName(step1.Body, id: "PAResForm1");
            if (form1.Found)
                return a.Success(null, form1.Inputs);

            a.Flow.Emit("Invalid 3DS (iCard)", "error");
            return a.Fail("Invalid 3DS (iCard)");
        }

        if (!step1.Headers.TryGetValue("Location", out var loc) || string.IsNullOrEmpty(loc))
            return a.Fail($"icard: unexpected status {step1.StatusCode} without Location");

        var nextUrl = Uri.TryCreate(loc, UriKind.Absolute, out _)
            ? loc
            : "https://" + a.OriginalAuthorityOrHost + loc;
        var acctId = loc.Split('?', 2)[0].TrimEnd('/').Split('/').LastOrDefault() ?? string.Empty;

        var step2 = await a.GetAsync(nextUrl, null, "acs-icard-step2", ct).ConfigureAwait(false);
        if (step2 is null || !step2.IsSuccess)
            return a.Fail("icard: step 2 failed");

        if ((step2.Body ?? string.Empty).Contains("confirm-otp", StringComparison.OrdinalIgnoreCase))
            return FallbackResult(a.Flow, a.Cluster);

        a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
        var checkPushUrl = $"https://{a.OriginalAuthorityOrHost}/{(isV2 ? "ProcessV2" : "Process")}/CheckPush";
        var acctJson = new JObject { ["acctID"] = acctId }.ToString(Formatting.None);
        for (var attempt = 0; attempt < a.MaxPolls; attempt++)
        {
            var pushRes = await a.PostJsonAsync(
                checkPushUrl,
                acctJson,
                null,
                "acs-icard-checkpush",
                ct,
                timeoutMs: 40000).ConfigureAwait(false);
            if (pushRes is null || !pushRes.IsSuccess)
                return a.Fail("icard: CheckPush failed");

            var code = ThreeDsTransportHelpers.TryParseJson(pushRes.Body)?["responseCode"]?.ToString();
            if (code == "0") break;
            if (code == "1")
            {
                a.Flow.Emit("3D Verification Rejected", "error");
                return a.Fail("3D Verification Rejected");
            }

            await a.DelayAsync(500, ct).ConfigureAwait(false);
        }

        a.Flow.Emit("Completing 3D Secure", "StatusInfo");
        var suRes = await a.PostJsonAsync(
            $"https://{a.OriginalAuthorityOrHost}/Process/SendSURes",
            acctJson,
            null,
            "acs-icard-sures",
            ct,
            timeoutMs: 40000).ConfigureAwait(false);
        if (suRes is null || !suRes.IsSuccess)
            return a.Fail("icard: SendSURes failed");

        var finalForm = FindFormByIdOrName(suRes.Body, id: "PAResForm1");
        return a.Success(null, finalForm.Inputs);
    }

    // -------------------------------------------------------------------------
    // 06_revolut: acs.revolut.com, poseidon.revolut.com (0x1408ADCA0)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleRevolutAsync(AcsContext a, CancellationToken ct)
    {
        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1 = await a.PostFormAsync(a.EntryUrl, a.InitialForm, null, "acs-revolut-step1", ct).ConfigureAwait(false);
        if (step1 is null || !step1.IsSuccess)
            return a.Fail("revolut: step 1 failed");

        var body = step1.Body ?? string.Empty;
        var cfg = Between(body, "config.transaction = ", ";");
        if (string.IsNullOrEmpty(cfg)) cfg = body;

        var pollUri = Between(cfg, "transactionInfoURL: '", "',");
        if (string.IsNullOrEmpty(pollUri))
            pollUri = Regex.Match(cfg, @"transactionInfoURL\s*:\s*'([^']+)'").Groups[1].Value;

        var submitUri = Between(cfg, "confirmTransactionURL: '", "',");
        if (string.IsNullOrEmpty(submitUri))
            submitUri = Regex.Match(cfg, @"confirmTransactionURL\s*:\s*'([^']+)'").Groups[1].Value;

        if (string.IsNullOrEmpty(pollUri) || string.IsNullOrEmpty(submitUri))
        {
            a.Flow.Emit("3D Verification Failed", "REVOLUT");
            return a.Fail("3D Verification Failed");
        }

        pollUri = ResolveAction(step1.Url.ToString(), pollUri)!;
        submitUri = ResolveAction(step1.Url.ToString(), submitUri)!;

        a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
        for (var attempt = 0; attempt < a.MaxPolls; attempt++)
        {
            var pollRes = await a.GetAsync(pollUri, null, "acs-revolut-poll", ct).ConfigureAwait(false);
            if (pollRes is null || !pollRes.IsSuccess)
                return a.Fail("revolut: poll failed");

            var st = ThreeDsTransportHelpers.TryParseJson(pollRes.Body)?["status"]?.ToString();
            if (st is "DECLINED" or "REJECTED" or "REJECTED_PENDING_RESPONSE" or "FAILED" or "EXPIRED" or "AUTHENTICATED")
                break;

            await a.DelayAsync(500, ct).ConfigureAwait(false);
        }

        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var confirmJson = new JObject { ["reason"] = "AUTHENTICATED" }.ToString(Formatting.None);
        for (var attempt = 0; attempt < a.MaxPolls; attempt++)
        {
            var confRes = await a.PostJsonAsync(submitUri, confirmJson, null, "acs-revolut-confirm", ct).ConfigureAwait(false);
            if (confRes is null)
                return a.Fail("revolut: confirm unreachable");

            if (confRes.StatusCode == 205)
            {
                await a.DelayAsync(500, ct).ConfigureAwait(false);
                continue;
            }

            if (!confRes.IsSuccess)
                return a.Fail($"revolut: confirm HTTP {confRes.StatusCode}");

            var form = FindFormByIdOrName(confRes.Body, id: "poseidonForm");
            return a.Success(ResolveAction(confRes.Url.ToString(), form.Action), form.Inputs);
        }

        return a.Fail("revolut: confirm timed out");
    }

    // -------------------------------------------------------------------------
    // 07_zen: 3dsecure.zen.com (0x1408B3BD0)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleZenAsync(AcsContext a, CancellationToken ct)
    {
        a.InitialForm.Remove("threeDSSessionData");
        if (a.InitialForm.TryGetValue("creq", out var creq) && !string.IsNullOrEmpty(creq))
            a.InitialForm["creq"] = creq.TrimEnd('=');

        var step1Headers = BuildChrome131OverrideHeaders(a.Profile);
        step1Headers["origin"] = "https://" + a.OriginalAuthorityOrHost;
        step1Headers["referer"] = "https://" + a.OriginalAuthorityOrHost + "/";
        step1Headers["sec-fetch-dest"] = "iframe";
        step1Headers["sec-fetch-site"] = "cross-site";
        step1Headers["sec-fetch-storage-access"] = "active";
        step1Headers["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8";

        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1 = await a.PostFormAsync(
            a.EntryUrl,
            a.InitialForm,
            step1Headers,
            "acs-zen-step1",
            ct,
            overrideHeaders: true).ConfigureAwait(false);
        if (step1 is null || !step1.IsSuccess)
            return a.Fail("zen: step 1 failed");

        var challengeForm1 = FindFormByIdOrName(step1.Body, id: "challenge-form");
        var sessionId = challengeForm1.Inputs.GetValueOrDefault("SESSIONID") ?? ReadInputValue(step1.Body, "SESSIONID") ?? string.Empty;
        var viewState = challengeForm1.Inputs.GetValueOrDefault("javax.faces.ViewState") ?? ReadInputValue(step1.Body, "javax.faces.ViewState") ?? string.Empty;

        var step2Headers = BuildChrome131OverrideHeaders(a.Profile);
        step2Headers["faces-request"] = "partial/ajax";
        step2Headers["origin"] = "https://3dsecure.zen.com";
        step2Headers["referer"] = "https://3dsecure.zen.com/v2/brw/index.xhtml";
        step2Headers["sec-fetch-dest"] = "iframe";
        step2Headers["sec-fetch-site"] = "same-origin";
        step2Headers["accept"] = "*/*";

        var step2Body = new Dictionary<string, string>
        {
            ["challenge-form"] = "challenge-form",
            ["SESSIONID"] = sessionId,
            ["javax.faces.ViewState"] = viewState,
            ["javax.faces.source"] = "mobile:j_idt197",
            ["javax.faces.partial.event"] = "click",
            ["javax.faces.partial.execute"] = "mobile:j_idt197 mobile:j_idt197",
            ["javax.faces.partial.render"] = "mobile:buttons",
            ["javax.faces.behavior.event"] = "action",
            ["javax.faces.partial.ajax"] = "true",
        };

        a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
        for (var attempt = 0; attempt < a.MaxPolls; attempt++)
        {
            var pollRes = await a.PostFormAsync(
                a.EntryUrl,
                step2Body,
                step2Headers,
                "acs-zen-step2",
                ct,
                overrideHeaders: true).ConfigureAwait(false);
            if (pollRes is null || !pollRes.IsSuccess)
                return a.Fail("zen: step 2 failed");

            var body = pollRes.Body ?? string.Empty;
            if (body.Contains("auth-complete", StringComparison.OrdinalIgnoreCase))
            {
                step2Headers.Remove("faces-request");
                step2Body = new Dictionary<string, string>
                {
                    ["challenge-form"] = "challenge-form",
                    ["mobile:j_idt198"] = "Continue",
                    ["SESSIONID"] = sessionId,
                    ["javax.faces.ViewState"] = viewState,
                };
                continue;
            }

            var finalForm = FindFormByIdOrName(body, id: "challenge-form");
            if (finalForm.Found && finalForm.Inputs.TryGetValue("cres", out var cres))
            {
                return a.Success(
                    ResolveAction(pollRes.Url.ToString(), finalForm.Action),
                    new Dictionary<string, string> { ["cres"] = cres });
            }

            await a.DelayAsync(1500, ct).ConfigureAwait(false);
        }

        return a.Fail("zen: auth-complete timed out");
    }

    // -------------------------------------------------------------------------
    // 08_monzo: verify.monzo.com (0x1408AC580)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleMonzoAsync(AcsContext a, CancellationToken ct)
    {
        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        string? location = null;
        for (var attempt = 0; attempt < 5; attempt++)
        {
            var step1 = await a.PostFormAsync(
                a.EntryUrl,
                a.InitialForm,
                null,
                "acs-monzo-step1",
                ct,
                followRedirects: false).ConfigureAwait(false);
            if (step1 is null)
                return a.Fail("monzo: step 1 unreachable");

            if (step1.StatusCode == 200)
            {
                if ((step1.Body ?? string.Empty).Contains("Confirmation Failed", StringComparison.OrdinalIgnoreCase))
                {
                    a.Flow.Emit("3DS Confirmation Failed", "error");
                    return a.Fail("3DS Confirmation Failed");
                }

                await a.DelayAsync(500, ct).ConfigureAwait(false);
                continue;
            }

            if (step1.Headers.TryGetValue("Location", out var loc) && !string.IsNullOrEmpty(loc))
            {
                location = loc;
                break;
            }

            return a.Fail($"monzo: unexpected status {step1.StatusCode}");
        }

        if (string.IsNullOrEmpty(location))
            return a.Fail("monzo: missing 303 Location");

        if (location!.Contains("3ds2", StringComparison.OrdinalIgnoreCase))
        {
            var q = location.Contains('?') ? location.Split('?', 2)[1] : string.Empty;
            var pollUrl = "https://verify.monzo.com/3ds2/challenge/poll" + (string.IsNullOrEmpty(q) ? string.Empty : "?" + q);

            a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
            for (var attempt = 0; attempt < a.MaxPolls; attempt++)
            {
                var pollRes = await a.GetAsync(pollUrl, null, "acs-monzo-poll2", ct).ConfigureAwait(false);
                if (pollRes is null || !pollRes.IsSuccess)
                    return a.Fail("monzo: 3ds2 poll failed");

                if (ThreeDsTransportHelpers.TryParseJson(pollRes.Body)?["completed"]?.ToObject<bool?>() == true)
                    break;

                await a.DelayAsync(500, ct).ConfigureAwait(false);
            }

            a.Flow.Emit("Completing 3D Secure", "StatusInfo");
            var finalUrl = "https://verify.monzo.com/3ds2/challenge" + (string.IsNullOrEmpty(q) ? string.Empty : "?" + q);
            var finalRes = await a.GetAsync(finalUrl, null, "acs-monzo-final2", ct).ConfigureAwait(false);
            if (finalRes is null || !finalRes.IsSuccess)
                return a.Fail("monzo: 3ds2 challenge page failed");

            var cres = ReadInputValue(finalRes.Body, "cres");
            if (string.IsNullOrEmpty(cres))
            {
                a.Flow.Emit("3DS Error (Monzo)", "error");
                return a.Fail("3DS Error (Monzo)");
            }

            string? absAction = null;
            foreach (var form in FindAllForms(finalRes.Body))
            {
                if (!string.IsNullOrEmpty(form.Action) &&
                    Uri.TryCreate(form.Action, UriKind.Absolute, out var absUri))
                {
                    absAction = absUri.ToString();
                    break;
                }
            }

            var outValues = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase) { ["cres"] = cres! };
            if (a.InitialForm.TryGetValue("threeDSSessionData", out var sessData))
                outValues["threeDSSessionData"] = sessData;
            return a.Success(absAction, outValues);
        }
        else
        {
            var id = location.Split('?', 2)[0].TrimEnd('/').Split('/').LastOrDefault() ?? string.Empty;

            a.Flow.Emit("Processing 3D Secure", "StatusInfo");
            var pendingRes = await a.GetAsync(
                $"https://verify.monzo.com/3ds/v2/challenge-pending/{id}",
                null,
                "acs-monzo-pending1",
                ct).ConfigureAwait(false);
            if (pendingRes is null || !pendingRes.IsSuccess)
                return a.Fail("monzo: challenge-pending failed");

            var mcid = ReadInputValue(pendingRes.Body, "messageCorrelationId");
            if (string.IsNullOrEmpty(mcid))
            {
                a.Flow.Emit("3DS Error (Monzo)", "error");
                return a.Fail("3DS Error (Monzo)");
            }

            var escapedMcid = Uri.EscapeDataString(mcid!);
            a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
            var pollUrl = $"https://verify.monzo.com/3ds/poll-challenge?messageCorrelationID={escapedMcid}";
            for (var attempt = 0; attempt < a.MaxPolls; attempt++)
            {
                var pollRes = await a.GetAsync(pollUrl, null, "acs-monzo-poll1", ct).ConfigureAwait(false);
                if (pollRes is null || !pollRes.IsSuccess)
                    return a.Fail("monzo: poll-challenge failed");

                if (ThreeDsTransportHelpers.TryParseJson(pollRes.Body)?["completed"]?.ToObject<bool?>() == true)
                    break;

                await a.DelayAsync(500, ct).ConfigureAwait(false);
            }

            a.Flow.Emit("Completing 3D Secure", "StatusInfo");
            var completeRes = await a.GetAsync(
                $"https://verify.monzo.com/3ds/v2/challenge-complete/{id}",
                null,
                "acs-monzo-complete1",
                ct).ConfigureAwait(false);
            if (completeRes is null || !completeRes.IsSuccess)
                return a.Fail("monzo: challenge-complete failed");

            var pares = ReadInputValue(completeRes.Body, "PaRes");
            if (string.IsNullOrEmpty(pares))
            {
                a.Flow.Emit("3DS Error (Monzo)", "error");
                return a.Fail("3DS Error (Monzo)");
            }

            var outValues = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase) { ["PaRes"] = pares! };
            if (a.InitialForm.TryGetValue("MD", out var md))
                outValues["MD"] = md;
            return a.Success(null, outValues);
        }
    }

    // -------------------------------------------------------------------------
    // 09_mbank: 3dsecure.mbank.cz (0x1408A99F0)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleMbankAsync(AcsContext a, CancellationToken ct)
    {
        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1 = await a.PostFormAsync(a.EntryUrl, a.InitialForm, null, "acs-mbank-step1", ct).ConfigureAwait(false);
        if (step1 is null || !step1.IsSuccess)
            return a.Fail("mbank: step 1 failed");

        var sessionId = ReadInputValue(step1.Body, "SESSIONID") ?? string.Empty;
        var viewState = ReadInputValueById(step1.Body, "j_id1:javax.faces.ViewState:0")
                        ?? ReadInputValue(step1.Body, "javax.faces.ViewState")
                        ?? string.Empty;

        const string endpoint = "https://3dsecure.mbank.cz/v2/brw/index.xhtml";
        var pollForm = new Dictionary<string, string>
        {
            ["challenge-form"] = "challenge-form",
            ["SESSIONID"] = sessionId,
            ["javax.faces.ViewState"] = viewState,
            ["javax.faces.source"] = "mobile:j_idt160",
            ["javax.faces.partial.event"] = "click",
            ["javax.faces.partial.execute"] = "mobile:j_idt160 mobile:j_idt160",
            ["javax.faces.partial.render"] = "mobile:auto-submit-buttons",
            ["javax.faces.behavior.event"] = "action",
            ["javax.faces.partial.ajax"] = "true",
        };
        var pollHeaders = new Dictionary<string, string>
        {
            ["Faces-Request"] = "partial/ajax",
        };

        a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
        for (var attempt = 0; attempt < a.MaxPolls; attempt++)
        {
            var pollRes = await a.PostFormAsync(endpoint, pollForm, pollHeaders, "acs-mbank-step2", ct).ConfigureAwait(false);
            if (pollRes is null || !pollRes.IsSuccess)
                return a.Fail("mbank: step 2 failed");

            if (!(pollRes.Body ?? string.Empty).Contains("onclick", StringComparison.OrdinalIgnoreCase))
                break;

            await a.DelayAsync(500, ct).ConfigureAwait(false);
        }

        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var confirmForm = new Dictionary<string, string>
        {
            ["challenge-form"] = "challenge-form",
            ["mobile:j_idt161"] = "Confirm",
            ["SESSIONID"] = sessionId,
            ["javax.faces.ViewState"] = viewState,
        };
        var confirmRes = await a.PostFormAsync(endpoint, confirmForm, null, "acs-mbank-step3", ct).ConfigureAwait(false);
        if (confirmRes is null || !confirmRes.IsSuccess)
            return a.Fail("mbank: step 3 failed");

        var finalForm = FindFormByIdOrName(confirmRes.Body, id: "challenge-form");
        return a.Success(null, finalForm.Inputs);
    }

    // -------------------------------------------------------------------------
    // 10_arcot: secure4.arcot.com (0x14089AC30)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleArcotAsync(AcsContext a, CancellationToken ct)
    {
        var headers1 = BuildChrome131OverrideHeaders(a.Profile);
        headers1["cache-control"] = "max-age=0";
        headers1["upgrade-insecure-requests"] = "1";
        headers1["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8";
        headers1["sec-fetch-site"] = "cross-site";
        headers1["sec-fetch-mode"] = "navigate";
        headers1["sec-fetch-dest"] = "iframe";
        headers1["priority"] = "u=0, i";

        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1 = await a.PostFormAsync(
            a.EntryUrl,
            a.InitialForm,
            headers1,
            "acs-arcot-step1",
            ct,
            overrideHeaders: true).ConfigureAwait(false);
        if (step1 is null || !step1.IsSuccess)
            return a.Fail("arcot: step 1 failed");

        var body1 = step1.Body ?? string.Empty;
        var cresImmediate = FindFormByIdOrName(body1, id: "cres_form");
        if (cresImmediate.Found)
            return a.Success(ResolveAction(step1.Url.ToString(), cresImmediate.Action), cresImmediate.Inputs);

        var landingForm = FindFormByIdOrName(body1, id: "landingForm");
        if (!landingForm.Found || !body1.Contains("data-tykey='BANKAPP'", StringComparison.OrdinalIgnoreCase) &&
            !body1.Contains("data-tykey=\"BANKAPP\"", StringComparison.OrdinalIgnoreCase))
        {
            return FallbackResult(a.Flow, a.Cluster);
        }

        var landingAction = ResolveAction(step1.Url.ToString(), landingForm.Action) ?? step1.Url.ToString();
        var landingInputs = new Dictionary<string, string>(landingForm.Inputs, StringComparer.OrdinalIgnoreCase)
        {
            ["selected_option"] = "BANKAPP",
        };

        var headers1b = BuildChrome131OverrideHeaders(a.Profile);
        headers1b["cache-control"] = "max-age=0";
        headers1b["origin"] = "https://" + a.OriginalAuthorityOrHost;
        headers1b["referer"] = step1.Url.ToString();
        headers1b["upgrade-insecure-requests"] = "1";
        headers1b["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8";
        headers1b["sec-fetch-site"] = "same-origin";
        headers1b["sec-fetch-mode"] = "navigate";
        headers1b["sec-fetch-user"] = "?1";
        headers1b["sec-fetch-dest"] = "iframe";
        headers1b["priority"] = "u=1, i";

        var step1b = await a.PostFormAsync(
            landingAction,
            landingInputs,
            headers1b,
            "acs-arcot-step1b",
            ct,
            overrideHeaders: true).ConfigureAwait(false);
        if (step1b is null || !step1b.IsSuccess)
            return a.Fail("arcot: landingForm submit failed");

        var body1b = step1b.Body ?? string.Empty;
        var verifyForm = FindFormByIdOrName(body1b, id: "verify_form", name: "verify_form");
        var cbsUrl = MatchJsVar(body1b, "cbsUrl");
        var cbsTxnId = MatchJsVar(body1b, "cbsTxnId");
        if (!verifyForm.Found || string.IsNullOrEmpty(cbsUrl) || string.IsNullOrEmpty(cbsTxnId))
            return FallbackResult(a.Flow, a.Cluster);

        var freqSec = int.TryParse(MatchJsVar(body1b, "cbsPollingFreq"), out var parsedFreq) && parsedFreq > 0 ? parsedFreq : 5;
        var attempts = int.TryParse(MatchJsVar(body1b, "cbsPollingRetryAttempts"), out var parsedAttempts) && parsedAttempts > 0 ? parsedAttempts : 48;
        var displayMsgFlag = MatchJsVar(body1b, "displayMsgFlag");

        var resolvedCbsUrl = ResolveAction(step1b.Url.ToString(), cbsUrl)!;
        var cbsBody = new JObject
        {
            ["transaction_id"] = cbsTxnId,
            ["transaction_type"] = "OOB",
        }.ToString(Formatting.None);

        var headers2 = BuildChrome131OverrideHeaders(a.Profile);
        headers2["origin"] = "https://" + a.OriginalAuthorityOrHost;
        headers2["referer"] = step1b.Url.ToString();
        headers2["accept"] = "*/*";
        headers2["sec-fetch-site"] = "same-origin";
        headers2["sec-fetch-mode"] = "cors";
        headers2["sec-fetch-dest"] = "empty";
        headers2["priority"] = "u=1, i";

        a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
        for (var attempt = 0; attempt < attempts; attempt++)
        {
            var pollRes = await a.PostJsonAsync(
                resolvedCbsUrl,
                cbsBody,
                headers2,
                "acs-arcot-cbs",
                ct,
                overrideHeaders: true).ConfigureAwait(false);

            if (pollRes is { IsSuccess: true })
            {
                var j = ThreeDsTransportHelpers.TryParseJson(pollRes.Body);
                var st = j?["status"]?.ToString() ?? j?["transaction_status"]?.ToString();
                if (st is "COMPLETE" or "TIMEDOUT" or "FAILED" or "CANCELLED")
                    break;
            }

            await a.DelayAsync(freqSec * 1000, ct).ConfigureAwait(false);
        }

        if (!string.Equals(displayMsgFlag, "false", StringComparison.OrdinalIgnoreCase))
            await a.DelayAsync(5000, ct).ConfigureAwait(false);

        a.Flow.Emit("Completing 3D Secure", "StatusInfo");
        var verifyUrl = ResolveAction(step1b.Url.ToString(), verifyForm.Action) ?? step1b.Url.ToString();
        var headers3 = BuildChrome131OverrideHeaders(a.Profile);
        headers3["origin"] = "https://" + a.OriginalAuthorityOrHost;
        headers3["referer"] = step1b.Url.ToString();
        headers3["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8";
        headers3["sec-fetch-site"] = "same-origin";
        headers3["sec-fetch-mode"] = "navigate";
        headers3["sec-fetch-dest"] = "iframe";
        headers3["priority"] = "u=1, i";

        var step3 = await a.PostFormAsync(
            verifyUrl,
            verifyForm.Inputs,
            headers3,
            "acs-arcot-verify",
            ct,
            overrideHeaders: true).ConfigureAwait(false);
        if (step3 is null || !step3.IsSuccess)
            return a.Fail("arcot: verify_form post failed");

        var finalForm = FindFormByIdOrName(step3.Body, id: "cres_form");
        if (!finalForm.Found)
            finalForm = FindFormContainingInput(step3.Body, "cres");
        if (!finalForm.Found)
        {
            a.Flow.Emit("3DS Error (Arcot)", "error");
            return a.Fail("3DS Error (Arcot)");
        }

        return a.Success(ResolveAction(step3.Url.ToString(), finalForm.Action), finalForm.Inputs);
    }

    // -------------------------------------------------------------------------
    // 11_capitalone: acs.capitalone.com (0x14089D2B0)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleCapitalOneAsync(AcsContext a, CancellationToken ct)
    {
        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1 = await a.PostFormAsync(a.EntryUrl, a.InitialForm, null, "acs-cap1-step1", ct).ConfigureAwait(false);
        if (step1 is null || !step1.IsSuccess)
            return a.Fail("capitalone: step 1 failed");

        a.Flow.Emit("Pending 3DS Task", "StatusInfo");

        var creqB64 = a.InitialForm.GetValueOrDefault("creq") ?? string.Empty;
        JObject creqJson;
        try
        {
            var decoded = Encoding.UTF8.GetString(DecodeBase64Flexible(creqB64));
            creqJson = JObject.Parse(decoded);
        }
        catch
        {
            creqJson = new JObject();
        }
        creqJson["authMethodSelected"] = "MAV";

        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step2 = await a.PostJsonAsync(
            a.EntryUrl,
            creqJson.ToString(Formatting.None),
            null,
            "acs-cap1-step2",
            ct).ConfigureAwait(false);
        if (step2 is null || !step2.IsSuccess)
            return a.Fail("capitalone: step 2 failed");

        var taskRefId = ThreeDsTransportHelpers.TryParseJson(step2.Body)?["taskReferenceId"]?.ToString() ?? string.Empty;

        a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
        var sseUrl = $"https://verified.capitalone.com/sse/mav/{Uri.EscapeDataString(taskRefId)}";
        var sseTimeoutMs = int.TryParse(a.Flow.Session.Vars.GetValueOrDefault("checkoutcom.capitalOneSseTimeoutMs"), out var stMs) && stMs > 0
            ? stMs
            : 600;
        var sseHeaders = new Dictionary<string, string>
        {
            ["Accept"] = "text/event-stream",
            ["Origin"] = "https://acs.capitalone.com",
        };
        await a.GetAsync(sseUrl, sseHeaders, "acs-cap1-sse", ct, timeoutMs: sseTimeoutMs, retries: 0, ignoreTimeout: true)
            .ConfigureAwait(false);

        creqJson["challengeHTMLDataEntry"] = string.Empty;
        var validateUrl = a.EntryUrl.Replace("/stepup", "/validate", StringComparison.OrdinalIgnoreCase);
        var validateHeaders = new Dictionary<string, string>
        {
            ["Accept"] = "*/*",
            ["Origin"] = "https://acs.capitalone.com",
        };
        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step4 = await a.PostJsonAsync(
            validateUrl,
            creqJson.ToString(Formatting.None),
            validateHeaders,
            "acs-cap1-validate",
            ct).ConfigureAwait(false);
        if (step4 is null || !step4.IsSuccess)
            return a.Fail("capitalone: validate failed");

        var valJson = ThreeDsTransportHelpers.TryParseJson(step4.Body);
        var state = valJson?["transactionState"]?.ToString();
        if (string.Equals(state, "VALIDATION_SUCCEEDED", StringComparison.Ordinal))
        {
            var notifUrl = valJson?["notificationUrl"]?.ToString()
                           ?? valJson?["NotificationUrl"]?.ToString()
                           ?? valJson?["acsURL"]?.ToString();
            var encodedResp = valJson?["encodedResponse"]?.ToString()
                              ?? valJson?["cres"]?.ToString()
                              ?? string.Empty;
            return a.Success(notifUrl, new Dictionary<string, string> { ["cres"] = encodedResp });
        }

        a.Flow.Emit("3DS Rejected", "error");
        return a.Fail("3DS Rejected");
    }

    // -------------------------------------------------------------------------
    // 12_modirum: acs1/2.3ds.modirum.com, acs1/2.mpts.modirum.com (0x1408AAC40)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleModirumAsync(AcsContext a, CancellationToken ct)
    {
        if (a.StripThreeDsSessionData)
            a.InitialForm.Remove("threeDSSessionData");
        if (a.InitialForm.TryGetValue("creq", out var creq) && creq.StartsWith("ey", StringComparison.Ordinal))
            a.InitialForm["creq"] = creq.Replace('+', '-').Replace('/', '_').TrimEnd('=');

        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1 = await a.PostFormAsync(a.EntryUrl, a.InitialForm, null, "acs-modirum-step1", ct).ConfigureAwait(false);
        if (step1 is null || !step1.IsSuccess)
            return a.Fail("modirum: step 1 failed");

        var cresDirect = FindFormByIdOrName(step1.Body, name: "CResForm");
        if (cresDirect.Found)
            return a.Success(null, cresDirect.Inputs);

        var firstForm = FindFirstForm(step1.Body);
        var actionUrl = ResolveAction(step1.Url.ToString(), firstForm.Action) ?? step1.Url.ToString();

        var isMpts = a.EntryUrl.Contains("mpts", StringComparison.OrdinalIgnoreCase) ||
                     a.EffectiveHost.Contains("mpts", StringComparison.OrdinalIgnoreCase);

        var nextBody = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        if (isMpts)
        {
            a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
            var mptsPollUrl = actionUrl + (actionUrl.Contains('?') ? "&" : "?") + "polling=true";
            for (var attempt = 0; attempt < a.MaxPolls; attempt++)
            {
                var mRes = await a.PostFormAsync(mptsPollUrl, new Dictionary<string, string>(), null, "acs-modirum-mpts", ct)
                    .ConfigureAwait(false);
                if (mRes is null || !mRes.IsSuccess)
                    return a.Fail("modirum: mpts polling failed");

                if (!string.Equals((mRes.Body ?? string.Empty).Trim(), "VERIFICATION_PENDING", StringComparison.Ordinal))
                {
                    nextBody["continue"] = "continue";
                    break;
                }

                await a.DelayAsync(500, ct).ConfigureAwait(false);
            }
        }

        a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
        for (var attempt = 0; attempt < a.MaxPolls; attempt++)
        {
            var pollRes = await a.PostFormAsync(actionUrl, nextBody, null, "acs-modirum-poll", ct).ConfigureAwait(false);
            if (pollRes is null || !pollRes.IsSuccess)
                return a.Fail("modirum: final poll failed");

            var paresForm = FindFormByIdOrName(pollRes.Body, name: "PAResForm");
            if (paresForm.Found)
                return a.Success(null, paresForm.Inputs);

            var cresForm = FindFormByIdOrName(pollRes.Body, name: "CResForm");
            if (cresForm.Found)
                return a.Success(null, cresForm.Inputs);

            await a.DelayAsync(5000, ct).ConfigureAwait(false);
        }

        return a.Fail("modirum: form poll timed out");
    }

    // -------------------------------------------------------------------------
    // 13_bunq: api.secure-code.bunq.com (0), api.id.mastercard.bunq.com (1) (0x14089C3B0)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleBunqAsync(AcsContext a, CancellationToken ct)
    {
        var is3ds2 = a.EffectiveHost.Contains("mastercard", StringComparison.OrdinalIgnoreCase);

        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1 = await a.PostFormAsync(a.EntryUrl, a.InitialForm, null, "acs-bunq-step1", ct).ConfigureAwait(false);
        if (step1 is null || !step1.IsSuccess)
            return a.Fail("bunq: step 1 failed");

        var marker = is3ds2 ? "challenge-request/" : "secure-code/";
        var token = Between(step1.Body ?? string.Empty, marker, "\"");
        if (string.IsNullOrEmpty(token))
            return a.Fail($"bunq: token after '{marker}' missing");

        var pollUrl = is3ds2
            ? $"https://api.id.mastercard.bunq.com/v1/challenge-request/{token}"
            : $"https://api.secure-code.bunq.com/v1/secure-code/{token}";
        var key = is3ds2 ? "MasterCardIdentityCheckChallengeRequest" : "MasterCardSecureCode";

        a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
        for (var attempt = 0; attempt < a.MaxPolls; attempt++)
        {
            var pollRes = await a.GetAsync(pollUrl, null, "acs-bunq-poll", ct).ConfigureAwait(false);
            if (pollRes is null || !pollRes.IsSuccess)
                return a.Fail("bunq: poll failed");

            var obj = ThreeDsTransportHelpers.TryParseJson(pollRes.Body)?["Response"]?[0]?[key] as JObject;
            var status = obj?["status"]?.ToString();

            if (status is "REJECTED" or "REJECTED_PENDING_RESPONSE")
            {
                a.Flow.Emit("3D Verification Rejected", "error");
                return a.Fail("3D Verification Rejected");
            }
            if (status == "FAILED")
            {
                a.Flow.Emit("3D Verification Failed", "error");
                return a.Fail("3D Verification Failed");
            }
            if (status == "EXPIRED")
            {
                a.Flow.Emit("3D Verification Expired", "error");
                return a.Fail("3D Verification Expired");
            }
            if (status == "ACCEPTED")
            {
                var returnUrl = obj?["return_url"]?.ToString();
                if (is3ds2)
                {
                    return a.Success(returnUrl, new Dictionary<string, string>
                    {
                        ["cres"] = obj?["challenge_result"]?.ToString() ?? string.Empty,
                        ["threeDSSessionData"] = obj?["session_data"]?.ToString() ?? string.Empty,
                    });
                }

                return a.Success(returnUrl, new Dictionary<string, string>
                {
                    ["MD"] = obj?["merchant_data"]?.ToString() ?? string.Empty,
                    ["PaRes"] = obj?["authentication_response"]?.ToString() ?? string.Empty,
                });
            }

            await a.DelayAsync(500, ct).ConfigureAwait(false);
        }

        return a.Fail("bunq: poll timed out");
    }

    // -------------------------------------------------------------------------
    // 14_starling: 3dsecure.starlingbank.com (0x1408AFA50)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleStarlingAsync(AcsContext a, CancellationToken ct)
    {
        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1 = await a.PostFormAsync(a.EntryUrl, a.InitialForm, null, "acs-starling-step1", ct).ConfigureAwait(false);
        if (step1 is null || !step1.IsSuccess)
            return a.Fail("starling: step 1 failed");

        var transId = ReadInputValueById(step1.Body, "3ds-server-trans-id");
        if (string.IsNullOrEmpty(transId))
            return FallbackResult(a.Flow, a.Cluster);

        a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
        var statusUrl = $"https://3dsecure.starlingbank.com/3ds/v2/challenge-browser/status?threeDSServerTransID={Uri.EscapeDataString(transId!)}";
        for (var attempt = 0; attempt < a.MaxPolls; attempt++)
        {
            var statusRes = await a.GetAsync(statusUrl, null, "acs-starling-status", ct).ConfigureAwait(false);
            if (statusRes is null || !statusRes.IsSuccess)
                return a.Fail("starling: status poll failed");

            if ((statusRes.Body ?? string.Empty).Contains("READY_TO_SUBMIT", StringComparison.OrdinalIgnoreCase))
                break;

            await a.DelayAsync(500, ct).ConfigureAwait(false);
        }

        var attemptBody = new JObject { ["threeDSServerTransID"] = transId }.ToString(Formatting.None);
        var attemptRes = await a.PostJsonAsync(
            "https://3dsecure.starlingbank.com/3ds/v2/challenge-browser/attempt",
            attemptBody,
            null,
            "acs-starling-attempt",
            ct).ConfigureAwait(false);
        if (attemptRes is null || !attemptRes.IsSuccess)
            return a.Fail("starling: attempt failed");

        var finalForm = FindFirstFormWithAction(attemptRes.Body);
        if (!finalForm.Found)
        {
            a.Flow.Emit("3DS Error (Starling)", "error");
            return a.Fail("3DS Error (Starling)");
        }

        return a.Success(ResolveAction(attemptRes.Url.ToString(), finalForm.Action), finalForm.Inputs);
    }

    // -------------------------------------------------------------------------
    // 15_enfuce: 3ds-a/b.live.ext.prod.enfuce.com (0x1408A2360)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleEnfuceAsync(AcsContext a, CancellationToken ct)
    {
        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1 = await a.PostFormAsync(a.EntryUrl, a.InitialForm, null, "acs-enfuce-step1", ct).ConfigureAwait(false);
        if (step1 is null || !step1.IsSuccess)
            return a.Fail("enfuce: step 1 failed");

        var wsUrl = Between(step1.Body ?? string.Empty, "new WebSocket(\"", "\"");
        if (string.IsNullOrEmpty(wsUrl))
            wsUrl = Between(step1.Body ?? string.Empty, "new WebSocket('", "'");
        if (string.IsNullOrEmpty(wsUrl))
            return a.Fail("enfuce: WebSocket URL missing");

        var jsessionid = wsUrl.Split('?', 2)[0].TrimEnd('/').Split('/').LastOrDefault() ?? string.Empty;

        string? wsMessage;
        if (a.WebSocketClient is not null)
        {
            wsMessage = await a.WebSocketClient(wsUrl, jsessionid, ct).ConfigureAwait(false);
        }
        else
        {
            wsMessage = await AwaitEnfuceWebSocketAsync(wsUrl, jsessionid, ct).ConfigureAwait(false);
        }

        if (!string.Equals(wsMessage, "OK", StringComparison.Ordinal))
        {
            a.Flow.Emit("3D Verification Expired", "error");
            return a.Fail("3D Verification Expired");
        }

        var wsUri = new Uri(wsUrl, UriKind.Absolute);
        var dispatcherScheme = wsUri.Scheme.Equals("ws", StringComparison.OrdinalIgnoreCase) ? "http" : "https";
        var dispatcherUrl = $"{dispatcherScheme}://{wsUri.Authority}/acs/challengedispatcher";

        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var dispBody = new JObject
        {
            ["PASSWORD"] = string.Empty,
            ["formaction"] = "pa.submit",
            ["jsessionid"] = jsessionid,
        }.ToString(Formatting.None);

        var dispRes = await a.PostJsonAsync(dispatcherUrl, dispBody, null, "acs-enfuce-dispatch", ct).ConfigureAwait(false);
        if (dispRes is null || !dispRes.IsSuccess)
            return a.Fail("enfuce: challengedispatcher failed");

        var cresForm = FindFormByIdOrName(dispRes.Body, name: "CResForm");
        return a.Success(null, cresForm.Inputs);
    }

    private static async Task<string?> AwaitEnfuceWebSocketAsync(string wsUrl, string jsessionid, CancellationToken ct)
    {
        using var ws = new ClientWebSocket();
        await ws.ConnectAsync(new Uri(wsUrl, UriKind.Absolute), ct).ConfigureAwait(false);
        var outBytes = Encoding.UTF8.GetBytes(jsessionid);
        await ws.SendAsync(outBytes, WebSocketMessageType.Text, endOfMessage: true, ct).ConfigureAwait(false);

        var buf = new byte[256];
        var offset = 0;
        while (ws.State == WebSocketState.Open && offset < buf.Length)
        {
            var stride = Math.Min(64, buf.Length - offset);
            var recv = await ws.ReceiveAsync(buf.AsMemory(offset, stride), ct).ConfigureAwait(false);
            if (recv.MessageType == WebSocketMessageType.Close)
                break;

            offset += recv.Count;
            if (recv.EndOfMessage)
            {
                var msg = Encoding.UTF8.GetString(buf, 0, offset);
                if (string.Equals(msg, "OK", StringComparison.Ordinal))
                {
                    try
                    {
                        await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "CLOSE", ct).ConfigureAwait(false);
                    }
                    catch { /* peer may close first */ }
                    return msg;
                }
                offset = 0;
            }
        }

        return null;
    }

    // -------------------------------------------------------------------------
    // 16_marqeta: authentication-acs.marqeta.com (0x1408A8C50)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleMarqetaAsync(AcsContext a, CancellationToken ct)
    {
        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1 = await a.PostFormAsync(a.EntryUrl, a.InitialForm, null, "acs-marqeta-step1", ct).ConfigureAwait(false);
        if (step1 is null || !step1.IsSuccess)
            return a.Fail("marqeta: step 1 failed");

        var body1 = step1.Body ?? string.Empty;
        var mainForm = FindFormByIdOrName(body1, id: "MainForm");
        if (!mainForm.Found) mainForm = FindFirstForm(body1);

        var formInputs = new Dictionary<string, string>(mainForm.Inputs, StringComparer.OrdinalIgnoreCase);
        formInputs.Remove("submit");

        var pollMatch = Regex.Match(body1, @"oobPollUrl\s*=\s*[""']([^""']+)[""']");
        if (!pollMatch.Success || string.IsNullOrEmpty(pollMatch.Groups[1].Value))
        {
            a.Flow.Emit("3DS Error (Marqeta)", "error");
            return a.Fail("3DS Error (Marqeta)");
        }

        var oobPollUrl = ResolveAction(step1.Url.ToString(), pollMatch.Groups[1].Value)!;
        var origin = new Uri(step1.Url.ToString()).GetLeftPart(UriPartial.Authority);

        a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
        var pollHeaders = new Dictionary<string, string>
        {
            ["Accept"] = "*/*",
            ["Origin"] = origin,
        };
        for (var attempt = 0; attempt < a.MaxPolls; attempt++)
        {
            var pollRes = await a.GetAsync(oobPollUrl, pollHeaders, "acs-marqeta-poll", ct, retries: 0).ConfigureAwait(false);
            if (pollRes is { StatusCode: 200 })
                break;

            await a.DelayAsync(500, ct).ConfigureAwait(false);
        }

        formInputs["autoSubmit"] = "true";
        var formAction = ResolveAction(step1.Url.ToString(), mainForm.Action) ?? step1.Url.ToString();
        var step3Headers = new Dictionary<string, string>
        {
            ["Origin"] = origin,
            ["Referer"] = step1.Url.ToString(),
        };

        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step3 = await a.PostFormAsync(formAction, formInputs, step3Headers, "acs-marqeta-step3", ct).ConfigureAwait(false);
        if (step3 is null || !step3.IsSuccess)
            return a.Fail("marqeta: step 3 failed");

        var cresForm = FindFormByIdOrName(step3.Body, id: "CResForm");
        if (!cresForm.Found) cresForm = FindFormContainingInput(step3.Body, "cres");
        var resolvedFinalAction = ResolveAction(step3.Url.ToString(), cresForm.Action);
        if (!cresForm.Found || string.IsNullOrEmpty(resolvedFinalAction) ||
            !Uri.TryCreate(resolvedFinalAction, UriKind.Absolute, out _))
        {
            a.Flow.Emit("3DS Error (Marqeta)", "error");
            return a.Fail("3DS Error (Marqeta)");
        }

        return a.Success(resolvedFinalAction, cresForm.Inputs);
    }

    // -------------------------------------------------------------------------
    // 17_amex: acs-safekey.americanexpress.com (0x140897E10)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleAmexAsync(AcsContext a, CancellationToken ct)
    {
        if (a.InitialForm.ContainsKey("creq"))
            return FallbackResult(a.Flow, a.Cluster);

        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1 = await a.PostFormAsync(a.EntryUrl, a.InitialForm, null, "acs-amex-step1", ct).ConfigureAwait(false);
        if (step1 is null || !step1.IsSuccess)
            return a.Fail("amex: step 1 failed");

        var form1 = FindFirstForm(step1.Body);
        var dict = new Dictionary<string, string>(form1.Inputs, StringComparer.OrdinalIgnoreCase);
        var savedMd = dict.GetValueOrDefault("MD") ?? a.InitialForm.GetValueOrDefault("MD") ?? string.Empty;

        var payAuthBody = new JObject
        {
            ["paReq"] = dict.GetValueOrDefault("PaReq") ?? a.InitialForm.GetValueOrDefault("PaReq") ?? string.Empty,
        }.ToString(Formatting.None);
        var step2 = await a.PostJsonAsync(
            "https://acs-safekey.americanexpress.com/GravityACS/payauth",
            payAuthBody,
            null,
            "acs-amex-payauth",
            ct).ConfigureAwait(false);
        if (step2 is null || !step2.IsSuccess)
            return a.Fail("amex: GravityACS/payauth failed");

        var sessionData = ThreeDsTransportHelpers.TryParseJson(step2.Body)?["sessionData"]?.ToString();
        if (!string.IsNullOrEmpty(sessionData))
            dict["sessionData"] = sessionData!;

        var step3 = await a.PostFormAsync(
            "https://acs-safekey.americanexpress.com/GravityACS/response",
            dict,
            null,
            "acs-amex-response",
            ct).ConfigureAwait(false);
        if (step3 is null || !step3.IsSuccess)
            return a.Fail("amex: GravityACS/response failed");

        var finalForm = FindFirstForm(step3.Body);
        var values = new Dictionary<string, string>(finalForm.Inputs, StringComparer.OrdinalIgnoreCase);
        if (!string.IsNullOrEmpty(savedMd))
            values["MD"] = savedMd;

        return a.Success(null, values);
    }

    // -------------------------------------------------------------------------
    // 18_touchtechpayments: idcheck.acs.touchtechpayments.com, verifiedbyvisa.acs.touchtechpayments.com (0x1408B0CF0)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleTouchtechPaymentsAsync(AcsContext a, CancellationToken ct)
    {
        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1 = await a.PostFormAsync(a.EntryUrl, a.InitialForm, null, "acs-ttp-step1", ct).ConfigureAwait(false);
        if (step1 is null || !step1.IsSuccess)
            return a.Fail("touchtechpayments: step 1 failed");

        var body = step1.Body ?? string.Empty;
        if (body.Contains("redirect()", StringComparison.Ordinal))
            return ExtractInlineTouchtechRedirect(a, body);

        var token = Between(body, "token: \"", "\"");
        var title = ExtractHtmlTitle(body).ToLowerInvariant();
        var flag = false;

        if (title.Contains("wise", StringComparison.Ordinal) || title.Contains("3d-secure", StringComparison.Ordinal))
        {
            var selectBody = new JObject
            {
                ["transactionToken"] = token,
                ["challengeMethod"] = "delegate-sca",
            }.ToString(Formatting.None);

            for (var i = 0; i < 3; i++)
            {
                var selRes = await a.PostJsonAsync(
                    "https://retry.touchtechpayments.com/api/v1/:select",
                    selectBody,
                    null,
                    "acs-ttp-select",
                    ct).ConfigureAwait(false);
                if (selRes is null) return a.Fail("touchtechpayments: select unreachable");
                if (selRes.StatusCode == 400)
                {
                    flag = true;
                    break;
                }
                if (selRes.IsSuccess &&
                    string.Equals(ThreeDsTransportHelpers.TryParseJson(selRes.Body)?["status"]?.ToString(), "ok",
                        StringComparison.OrdinalIgnoreCase))
                {
                    break;
                }
            }
        }

        if ((body.Contains("Monese", StringComparison.Ordinal) || flag) && !title.Contains("revolut", StringComparison.Ordinal))
            return FallbackResult(a.Flow, a.Cluster);

        a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
        var pollJson = new JObject { ["transToken"] = token }.ToString(Formatting.None);
        string? authToken = null;
        for (var attempt = 0; attempt < a.MaxPolls; attempt++)
        {
            var pollRes = await a.PostJsonAsync(
                "https://poll.touchtechpayments.com/poll",
                pollJson,
                null,
                "acs-ttp-poll",
                ct).ConfigureAwait(false);
            if (pollRes is null || !pollRes.IsSuccess)
                return a.Fail("touchtechpayments: poll failed");

            var j = ThreeDsTransportHelpers.TryParseJson(pollRes.Body);
            var st = j?["status"]?.ToString();
            if (st is "blocked" or "declined" or "failure" or "expired")
                return a.Fail($"touchtechpayments: {st}");

            if (st == "success")
            {
                authToken = j?["authToken"]?.ToString();
                break;
            }

            await a.DelayAsync(500, ct).ConfigureAwait(false);
        }

        a.Flow.Emit("Completing 3D Secure", "StatusInfo");
        var confirmJson = new JObject
        {
            ["transToken"] = token,
            ["authToken"] = authToken ?? string.Empty,
        }.ToString(Formatting.None);
        var confirmRes = await a.PostJsonAsync(
            "https://macs.touchtechpayments.com/v1/confirmTransaction",
            confirmJson,
            null,
            "acs-ttp-confirm",
            ct).ConfigureAwait(false);
        if (confirmRes is null || !confirmRes.IsSuccess)
            return a.Fail("touchtechpayments: confirmTransaction failed");

        var pares = ThreeDsTransportHelpers.TryParseJson(confirmRes.Body)?["Response"]?.ToString() ?? string.Empty;
        return a.Success(null, new Dictionary<string, string>
        {
            ["MD"] = a.InitialForm.GetValueOrDefault("MD") ?? string.Empty,
            ["PaRes"] = pares,
        });
    }

    // -------------------------------------------------------------------------
    // 19_cardinal: authentication.cardinalcommerce.com (0x14089F170)
    // -------------------------------------------------------------------------
    private static async Task<AcsChallengeResult> HandleCardinalAsync(AcsContext a, CancellationToken ct)
    {
        a.Flow.Emit("Processing 3D Secure", "StatusInfo");
        var step1 = await a.PostFormAsync(a.EntryUrl, a.InitialForm, null, "acs-cardinal-step1", ct).ConfigureAwait(false);
        if (step1 is null || !step1.IsSuccess)
            return a.Fail("cardinal-acs: step 1 failed");

        var oobForm = FindFormByIdOrName(step1.Body, id: "ValidateOutOfBandCredentialForm");
        var riskForm = FindFormByActionContains(step1.Body, "/Api/NextStep/ProcessRisk");

        if (riskForm.Found && riskForm.Inputs.Count > 0)
        {
            var txId = riskForm.Inputs.GetValueOrDefault("TransactionId") ?? string.Empty;
            var issuerId = riskForm.Inputs.GetValueOrDefault("IssuerId") ?? string.Empty;

            var saveHeaders = new Dictionary<string, string>
            {
                ["X-Requested-With"] = "XMLHttpRequest",
                ["X-HTTP-Method-Override"] = "FORM",
            };
            var saveBody = BuildCardinalSaveBrowserData(txId);
            await a.PostJsonAsync(
                "https://geoissuer.cardinalcommerce.com/DeviceFingerprintWeb/V2/Browser/SaveBrowserData",
                saveBody.ToString(Formatting.None),
                saveHeaders,
                "acs-cardinal-savebrowser",
                ct).ConfigureAwait(false);

            var riskRes = await a.PostFormAsync(
                "https://authentication.cardinalcommerce.com/Api/NextStep/ProcessRisk",
                riskForm.Inputs,
                null,
                "acs-cardinal-processrisk",
                ct).ConfigureAwait(false);
            if (riskRes is null || !riskRes.IsSuccess)
                return a.Fail("cardinal-acs: ProcessRisk failed");

            var termBody = new JObject
            {
                ["TransactionId"] = txId,
                ["IssuerId"] = issuerId,
            }.ToString(Formatting.None);
            var termRes = await a.PostJsonAsync(
                "https://authentication.cardinalcommerce.com/api/nextstep/term",
                termBody,
                null,
                "acs-cardinal-term1",
                ct).ConfigureAwait(false);
            if (termRes is null || !termRes.IsSuccess)
                return a.Fail("cardinal-acs: api/nextstep/term failed");

            var payload = ThreeDsTransportHelpers.TryParseJson(termRes.Body)?["Payload"];
            return a.Success(null, new Dictionary<string, string>
            {
                ["MD"] = payload?["MD"]?.ToString() ?? string.Empty,
                ["PaRes"] = payload?["PARes"]?.ToString() ?? string.Empty,
            });
        }

        if (oobForm.Found && oobForm.Inputs.Count > 0)
        {
            var oobInputs = new Dictionary<string, string>(oobForm.Inputs, StringComparer.OrdinalIgnoreCase);
            oobInputs.Remove("ValidateReloadEnabled");
            oobInputs["MessageVersion"] = "2";
            oobInputs["Type"] = "BIOMETRIC";
            oobInputs["Origin"] = "JAVASCRIPT_POLLING";

            a.Flow.Emit("Waiting for 3D verification", "StatusInfo");
            for (var attempt = 0; attempt < a.MaxPolls; attempt++)
            {
                var oobRes = await a.PostFormAsync(
                    "https://authentication.cardinalcommerce.com/Api/OutOfBand/ValidateOutOfBandCredential",
                    oobInputs,
                    null,
                    "acs-cardinal-oob",
                    ct).ConfigureAwait(false);
                if (oobRes is null || !oobRes.IsSuccess)
                    return a.Fail("cardinal-acs: ValidateOutOfBandCredential failed");

                var nextStep = ThreeDsTransportHelpers.TryParseJson(oobRes.Body)?["NextStep"]?.ToString();
                if (string.Equals(nextStep, "ERROR", StringComparison.OrdinalIgnoreCase))
                {
                    a.Flow.Emit("3DS Rejected", "error");
                    return a.Fail("3DS Rejected");
                }
                if (!string.Equals(nextStep, "PENDING", StringComparison.OrdinalIgnoreCase))
                    break;

                await a.DelayAsync(1000, ct).ConfigureAwait(false);
            }

            a.Flow.Emit("Processing 3D Secure", "StatusInfo");
            var termBody = new JObject
            {
                ["TransactionId"] = oobInputs.GetValueOrDefault("TransactionId") ?? string.Empty,
                ["IssuerId"] = oobInputs.GetValueOrDefault("IssuerId") ?? string.Empty,
            }.ToString(Formatting.None);
            var termRes = await a.PostJsonAsync(
                "https://authentication.cardinalcommerce.com/api/2_1_0/nextstep/term",
                termBody,
                null,
                "acs-cardinal-term2",
                ct).ConfigureAwait(false);
            if (termRes is null || !termRes.IsSuccess)
                return a.Fail("cardinal-acs: api/2_1_0/nextstep/term failed");

            var payload = ThreeDsTransportHelpers.TryParseJson(termRes.Body)?["Payload"];
            var notifUrl = payload?["NotificationUrl"]?.ToString();
            return a.Success(notifUrl, new Dictionary<string, string>
            {
                ["cres"] = payload?["CRes"]?.ToString() ?? string.Empty,
                ["threeDSSessionData"] = payload?["ThreeDSSessionData"]?.ToString() ?? string.Empty,
            });
        }

        return FallbackResult(a.Flow, a.Cluster);
    }

    internal static JObject BuildCardinalSaveBrowserData(string referenceId) => new()
    {
        ["BinConfigIdentifiers"] = JValue.CreateNull(),
        ["BinSessionId"] = JValue.CreateNull(),
        ["CallSignEnabled"] = JValue.CreateNull(),
        ["Cookies"] = new JObject
        {
            ["Extended"] = true,
            ["LocalStorage"] = true,
            ["SessionStorage"] = true,
        },
        ["DeviceChannel"] = "Browser",
        ["Extended"] = new JObject
        {
            ["Browser"] = new JObject
            {
                ["Adblock"] = false,
                ["AvailableJsFonts"] = new JArray(
                    "Arial", "Arial Hebrew", "Arial Rounded MT Bold", "Courier", "Courier New",
                    "Georgia", "Helvetica", "Helvetica Neue", "Palatino", "Times",
                    "Times New Roman", "Trebuchet MS", "Verdana"),
                ["DoNotTrack"] = "unknown",
                ["JavaEnabled"] = false,
            },
            ["Device"] = new JObject
            {
                ["ColorDepth"] = 24,
                ["Cpu"] = "unknown",
                ["Platform"] = "Win32",
                ["TouchSupport"] = new JObject
                {
                    ["MaxTouchPoints"] = 0,
                    ["OnTouchStartAvailable"] = false,
                    ["TouchEventCreationSuccessful"] = false,
                },
            },
        },
        ["Fingerprint"] = "1e7e2de356989ef2983429f5e0e41660",
        ["FingerprintDetails"] = new JObject { ["Version"] = "1.5.1" },
        ["FingerprintingTime"] = Random.Shared.Next(50, 75),
        ["Language"] = "en-us",
        ["Latitude"] = JValue.CreateNull(),
        ["Longitude"] = JValue.CreateNull(),
        ["OrgUnitId"] = "5d9e42a04901d560f078435d",
        ["Origin"] = "Unknown",
        ["Plugins"] = new JArray(
            "PDF Viewer", "Chrome PDF Viewer", "Chromium PDF Viewer",
            "Microsoft Edge PDF Viewer", "WebKit built-in PDF"),
        ["ReferenceId"] = referenceId,
        ["Referrer"] = "https://authentication.cardinalcommerce.com/",
        ["Screen"] = new JObject
        {
            ["FakedResolution"] = false,
            ["Ratio"] = 1.0,
            ["Resolution"] = "896x414",
            ["UsableResolution"] = "896x414",
            ["CCAScreenSize"] = "02",
        },
        ["ThreatMetrixEnabled"] = "true",
        ["ThreatMetrixEventType"] = "PAYMENT",
        ["ThreeDSServerTransId"] = JValue.CreateNull(),
        ["TimeOffset"] = -60,
        ["UserAgent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        ["UserAgentDetails"] = new JObject
        {
            ["FakedOS"] = false,
            ["FakedBrowser"] = false,
        },
    };

    // -------------------------------------------------------------------------
    // 20_fallback: 0x144BDBD70 interactive verification required
    // -------------------------------------------------------------------------
    private static AcsChallengeResult FallbackResult(FlowContext c, string cluster)
    {
        c.Emit("Click to finalize 3DS", "StatusInfo");
        c.Emit("A task is waiting for 3DS verification!", "3DS verification required");
        c.Session.Vars["checkoutcom.interactive3ds"] = "true";
        return new AcsChallengeResult
        {
            Ok = false,
            RequiresInteractiveVerification = true,
            Cluster = cluster,
            StatusText = "Click to finalize 3DS",
            StatusCategory = "3DS verification required",
            Error = "3DS verification required",
        };
    }

    // -------------------------------------------------------------------------
    // Shared Context, HTTP Transport, Host Rewrite, Form & String Parsers
    // -------------------------------------------------------------------------
    private sealed class AcsContext
    {
        public FlowContext Flow { get; }
        public string EntryUrl { get; }
        public string EffectiveHost { get; }
        public string Cluster { get; }
        public Dictionary<string, string> InitialForm { get; }
        public bool StripThreeDsSessionData { get; }
        public TlsProfile Profile { get; }
        public Func<string, string, CancellationToken, Task<string?>>? WebSocketClient { get; }
        public int MaxPolls { get; }
        public string OriginalAuthorityOrHost { get; }

        public AcsContext(
            FlowContext flow,
            string entryUrl,
            string effectiveHost,
            string cluster,
            Dictionary<string, string> initialForm,
            bool stripThreeDsSessionData,
            TlsProfile profile,
            Func<string, string, CancellationToken, Task<string?>>? webSocketClient)
        {
            Flow = flow;
            EntryUrl = entryUrl;
            EffectiveHost = effectiveHost;
            Cluster = cluster;
            InitialForm = initialForm;
            StripThreeDsSessionData = stripThreeDsSessionData;
            Profile = profile;
            WebSocketClient = webSocketClient;
            MaxPolls = int.TryParse(flow.Session.Vars.GetValueOrDefault("checkoutcom.acsMaxPolls"), out var mp) && mp > 0
                ? mp
                : DefaultMaxPollAttempts;
            OriginalAuthorityOrHost = !string.IsNullOrEmpty(effectiveHost)
                ? effectiveHost
                : (Uri.TryCreate(entryUrl, UriKind.Absolute, out var eu) ? eu.Authority : string.Empty);
        }

        public string RewriteUrl(string rawUrl)
        {
            if (string.IsNullOrEmpty(rawUrl)) return rawUrl;
            if (!Uri.TryCreate(rawUrl, UriKind.Absolute, out var uri))
                return rawUrl;

            var hostKey = "checkoutcom.acsHost." + uri.Host;
            string? targetBase = null;
            if (Flow.Session.Vars.TryGetValue(hostKey, out var perHost) && !string.IsNullOrEmpty(perHost))
                targetBase = perHost;
            else if (Flow.Session.Vars.TryGetValue("checkoutcom.acsBaseUrl", out var globalBase) && !string.IsNullOrEmpty(globalBase))
                targetBase = globalBase;
            else if (Uri.TryCreate(EntryUrl, UriKind.Absolute, out var entryUri) && entryUri.IsLoopback && !uri.IsLoopback)
                targetBase = entryUri.GetLeftPart(UriPartial.Authority);

            if (string.IsNullOrEmpty(targetBase))
                return rawUrl;

            // Preserve PathAndQuery literally (including double slashes like //v2Form for 03_soldo)
            var schemeEnd = rawUrl.IndexOf("://", StringComparison.Ordinal);
            var afterScheme = rawUrl[(schemeEnd + 3)..];
            var slashIdx = afterScheme.IndexOf('/');
            var pathAndQuery = slashIdx >= 0 ? afterScheme[slashIdx..] : string.Empty;
            return targetBase!.TrimEnd('/') + pathAndQuery;
        }

        public Task DelayAsync(int defaultMs, CancellationToken ct)
        {
            var ms = defaultMs;
            if (Flow.Session.Vars.TryGetValue("checkoutcom.acsPollMs", out var raw) &&
                int.TryParse(raw, NumberStyles.Integer, CultureInfo.InvariantCulture, out var overrideMs) &&
                overrideMs >= 0)
            {
                ms = overrideMs;
            }
            return ms == 0 ? Task.CompletedTask : Task.Delay(ms, ct);
        }

        public Task<NetResponse?> GetAsync(
            string url,
            IDictionary<string, string>? headers,
            string tag,
            CancellationToken ct,
            bool followRedirects = true,
            bool overrideHeaders = false,
            int timeoutMs = 0,
            int? retries = null,
            bool ignoreTimeout = false) =>
            SendAsync(HttpMethod.Get, url, null, headers, tag, ct, followRedirects, overrideHeaders, timeoutMs, retries, ignoreTimeout);

        public Task<NetResponse?> PostFormAsync(
            string url,
            IDictionary<string, string> form,
            IDictionary<string, string>? headers,
            string tag,
            CancellationToken ct,
            bool followRedirects = true,
            bool overrideHeaders = false,
            int timeoutMs = 0) =>
            SendAsync(HttpMethod.Post, url, BuildFormContent(form), headers, tag, ct, followRedirects, overrideHeaders, timeoutMs);

        public Task<NetResponse?> PostJsonAsync(
            string url,
            string json,
            IDictionary<string, string>? headers,
            string tag,
            CancellationToken ct,
            bool followRedirects = true,
            bool overrideHeaders = false,
            int timeoutMs = 0) =>
            SendAsync(HttpMethod.Post, url, new StringContent(json, Encoding.UTF8, "application/json"), headers, tag, ct, followRedirects, overrideHeaders, timeoutMs);

        public Task<NetResponse?> PostAsync(
            string url,
            HttpContent? content,
            IDictionary<string, string>? headers,
            string tag,
            CancellationToken ct,
            bool followRedirects = true,
            bool overrideHeaders = false,
            int timeoutMs = 0) =>
            SendAsync(HttpMethod.Post, url, content, headers, tag, ct, followRedirects, overrideHeaders, timeoutMs);

        private async Task<NetResponse?> SendAsync(
            HttpMethod method,
            string url,
            HttpContent? content,
            IDictionary<string, string>? headers,
            string tag,
            CancellationToken ct,
            bool followRedirects,
            bool overrideHeaders,
            int timeoutMs,
            int? retries = null,
            bool ignoreTimeout = false)
        {
            var effectiveUrl = RewriteUrl(url);
            try
            {
                var opts = Flow.Options(tag);
                opts.Profile = Profile;
                opts.FollowRedirects = followRedirects;
                opts.OverrideHeaders = overrideHeaders;
                opts.Content = content;
                if (timeoutMs > 0) opts.Timeout = TimeSpan.FromMilliseconds(timeoutMs);
                if (retries is { } r) opts.Retries = r;

                if (!overrideHeaders)
                {
                    opts.Headers.TryAdd("Accept-Encoding", "gzip, deflate, br");
                    opts.Headers.TryAdd("Accept-Language", "en-GB");
                }

                if (headers is not null)
                {
                    foreach (var kv in headers)
                        opts.Headers[kv.Key] = kv.Value;
                }

                var res = await Flow.Http.SendAsync(method, effectiveUrl, opts, ct).ConfigureAwait(false);
                Flow.Session.AbsorbCookies(res.Cookies);
                Flow.Session.Vars["lastStatus"] = res.StatusCode.ToString(CultureInfo.InvariantCulture);
                Flow.Session.Vars["lastUrl"] = res.Url.ToString();
                return res;
            }
            catch (Exception ex) when (ignoreTimeout && !ct.IsCancellationRequested)
            {
                Flow.Emit($"{tag}: {ex.Message}", "StatusInfo");
                return null;
            }
            catch (Exception ex)
            {
                Flow.Emit($"{tag}: {ex.Message}", "error");
                return null;
            }
        }

        public AcsChallengeResult Success(string? actionUrl, Dictionary<string, string> values) => new()
        {
            Ok = true,
            Cluster = Cluster,
            ActionUrl = actionUrl,
            Values = values,
        };

        public AcsChallengeResult Fail(string error) => new()
        {
            Ok = false,
            Cluster = Cluster,
            Error = error,
        };
    }

    private static FormUrlEncodedContent BuildFormContent(IDictionary<string, string> form) =>
        new(form.Select(kv => new KeyValuePair<string, string>(kv.Key, kv.Value ?? string.Empty)));

    private static Dictionary<string, string> BuildChrome131OverrideHeaders(TlsProfile profile) =>
        new(StringComparer.OrdinalIgnoreCase)
        {
            ["user-agent"] = profile.UserAgent,
            ["sec-ch-ua"] = profile.SecChUa,
            ["sec-ch-ua-mobile"] = profile.SecChUaMobile,
            ["sec-ch-ua-platform"] = profile.SecChUaPlatform,
            ["accept-encoding"] = "gzip, deflate, br, zstd",
            ["accept-language"] = "en-US,en;q=0.9",
        };

    private readonly record struct ParsedForm(
        bool Found,
        string? Id,
        string? Name,
        string? Action,
        Dictionary<string, string> Inputs);

    private static List<ParsedForm> FindAllForms(string? html)
    {
        var forms = HtmlFormDom.ExtractAllForms(html);
        var list = new List<ParsedForm>(forms.Count);
        foreach (var f in forms)
            list.Add(new ParsedForm(true, f.Id, f.Name, f.Action, f.Inputs));
        return list;
    }

    private static ParsedForm FindFirstForm(string? html)
    {
        var form = HtmlFormDom.ExtractFormInfo(html);
        return form is null ? default : new ParsedForm(true, form.Id, form.Name, form.Action, form.Inputs);
    }

    private static ParsedForm FindFirstFormWithAction(string? html)
    {
        foreach (var f in FindAllForms(html))
        {
            if (!string.IsNullOrEmpty(f.Action)) return f;
        }
        return default;
    }

    private static ParsedForm FindFormByIdOrName(string? html, string? id = null, string? name = null)
    {
        var form = HtmlFormDom.ExtractFormInfo(html, formName: name, formId: id, matchAnyIdOrName: true);
        return form is null ? default : new ParsedForm(true, form.Id, form.Name, form.Action, form.Inputs);
    }

    private static ParsedForm FindFormByActionContains(string? html, string fragment)
    {
        foreach (var f in FindAllForms(html))
        {
            if (!string.IsNullOrEmpty(f.Action) &&
                f.Action.Contains(fragment, StringComparison.OrdinalIgnoreCase))
                return f;
        }
        return default;
    }

    private static ParsedForm FindFormContainingInput(string? html, string inputName)
    {
        foreach (var f in FindAllForms(html))
        {
            if (f.Inputs.ContainsKey(inputName))
                return f;
        }
        return default;
    }

    private static string? ReadInputValue(string? html, string name) =>
        HtmlFormDom.ExtractInputs(html).GetValueOrDefault(name);

    private static string? ReadInputValueById(string? html, string id) =>
        HtmlFormDom.ExtractElementAttributeById(html, id, "value");

    private static string? ResolveAction(string currentUrl, string? action)
    {
        if (string.IsNullOrWhiteSpace(action)) return null;
        return ThreeDsTransportHelpers.ResolveUrl(currentUrl, action!);
    }

    private static string Between(string text, string start, string end)
    {
        if (string.IsNullOrEmpty(text)) return string.Empty;
        var i = text.IndexOf(start, StringComparison.Ordinal);
        if (i < 0) return string.Empty;
        i += start.Length;
        var j = text.IndexOf(end, i, StringComparison.Ordinal);
        return j < 0 ? string.Empty : text[i..j];
    }

    private static string ExtractHtmlTitle(string? html) =>
        HtmlFormDom.ExtractTitle(html) ?? string.Empty;

    private static string? MatchJsVar(string html, string varName)
    {
        if (string.IsNullOrEmpty(html)) return null;
        var m = Regex.Match(
            html,
            $@"\b{Regex.Escape(varName)}\s*[:=]\s*(?:""([^""]*)""|'([^']*)'|([^\s;,\r\n\}}]+))");
        if (!m.Success) return null;
        return m.Groups[1].Success ? m.Groups[1].Value.Trim()
            : m.Groups[2].Success ? m.Groups[2].Value.Trim()
            : m.Groups[3].Value.Trim();
    }

    private static byte[] DecodeBase64Flexible(string raw)
    {
        var padded = raw.Trim().Replace('-', '+').Replace('_', '/');
        var mod = padded.Length % 4;
        if (mod == 2) padded += "==";
        else if (mod == 3) padded += "=";
        return Convert.FromBase64String(padded);
    }
}
