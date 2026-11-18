using System.Net.Http;
using Cybersole.Stores.Flows;

namespace Cybersole.Stores.Payments;

/// <summary>
/// PayPal 3-D Secure — the challenge layer a PayPal payment runs when the bank asks for it.
///
/// <para>
/// <b>R1078 decompiled stage 1 of both paths.</b> The two request builders are the only xrefs of
/// the <c>Solving PayPal 3DS</c> stage string (obj 0x146e93fa8 = chars 0x146e93fb4 - 12):
/// <c>sub_141102970</c> (normal, 927 B) and <c>sub_141105A80</c> (hosted, 1,047 B) — the
/// <c>&lt;SolvePayPal3DS&gt;</c> and <c>&lt;SolvePayPalHosted3DS&gt;</c> bodies. The send step
/// <c>sub_14110D670</c> sets the URL to the frozen <c>https://www.paypal.com/graphql/</c>
/// (0x147097e78) and fires the 4-arg payload send <c>sub_1408B6310</c> — the +24 verb slot, PUT.
/// </para>
///
/// <para>
/// Each builder registers a white <c>StatusInfo</c> wall, pins a thirty-second budget
/// (+236 = 30000), assembles its header wall, and dispatches on the answer: <b>200</b> to the
/// success continuation, <b>403 and 429</b> to one shared retry closure. The nine observable
/// stages report through this family — the map, one decompile per stage, is named in
/// <see cref="RunAsync"/>: (1) sub_141102970/sub_141105A80 · (2) sub_141103410 +
/// sub_141107DA0 + sub_141108170 · (2.1) sub_141103800 · (3) sub_141103BF0/sub_141105EF0 ·
/// (4) sub_1411090C0 · (5) sub_141109550 · (6) sub_141109910/sub_141109CF0 ·
/// (7) sub_14110A080 · (8) sub_141106360.
/// </para>
/// </summary>
public sealed class PayPalThreeDs
{
    /// <summary>The stage target, a frozen literal (0x147097e78): PayPal's own graphql surface.</summary>
    public const string GraphqlUrl = "https://www.paypal.com/graphql/";

    /// <summary>PayPal's web client id (0x146fc7338) — hermione is its checkout UI node's own name.</summary>
    public const string AppName = "checkoutuinodeweb_hermione";

    /// <summary>
    /// Stage 1's wall text (0x146e93fa8 = chars 0x146e93fb4 - 12). R1081 correction: the frozen
    /// literal carries the stage suffix — an earlier version read the doc's shorthand without the
    /// "(1)" and pinned that; the pool listing was the authority all along.
    /// </summary>
    public const string SolvingStatus = "Solving PayPal 3DS (1)";

    /// <summary>Stage text when the challenge flag is on (0x146e4a918) — the image's own spelling, kept.</summary>
    public const string ProcessingStatus = "Proccesing 3D Secure";

    /// <summary>The budget both builders pin (+236), in milliseconds.</summary>
    public const int StageTimeoutMs = 30000;

    /// <summary>The four state-machine names the image carries for the 3DS challenge.</summary>
    public enum ThreeDsState { Submit3DS, Process3DS, Waiting3DS, Complete3DS }

    /// <summary>
    /// One stage request's inputs — the fields the builders read off their payment context.
    /// The payload itself is built by the stage that runs before this one, exactly as the
    /// original's send step reads it from its state field (a1[2]); it is not invented here.
    /// </summary>
    public sealed class StageInput
    {
        /// <summary>The flag at ctx+144 that selects the stage text in both builders.</summary>
        public bool ChallengeActive { get; init; }

        /// <summary>Which of the two builder twins runs — the normal or the hosted dialect.</summary>
        public bool Hosted { get; init; }

        /// <summary>x-paypal-internal-euat — the normal path reads ctx[2], the hosted ctx[3].</summary>
        public string? Euat { get; init; }

        /// <summary>paypal-client-metadata-id (ctx+24); the hosted dialect also echoes it as paypal-client-context.</summary>
        public string? MetadataId { get; init; }

        /// <summary>Hosted only: x-country (ctx[4]).</summary>
        public string? Country { get; init; }

        /// <summary>Hosted only: x-app-name comes from the context (ctx[2]) instead of the literal.</summary>
        public string? HostedAppName { get; init; }

        /// <summary>Hosted only: referer comes from the context (ctx[5]); the normal path sends the paypal origin.</summary>
        public string? HostedReferer { get; init; }

        /// <summary>The global config's user agent, both paths.</summary>
        public string? UserAgent { get; init; }

        /// <summary>sec-ch-ua, generated (sub_140f9a950).</summary>
        public string? SecChUa { get; init; }

        /// <summary>sec-ch-ua-platform, generated (sub_140f9bce0).</summary>
        public string? SecChUaPlatform { get; init; }

        /// <summary>The GraphQL operation the previous stage assembled.</summary>
        public string Payload { get; init; } = "{}";
    }

    /// <summary>What the registered status dispatch does with each answer.</summary>
    public sealed class StageOutcome
    {
        public bool Ok { get; init; }
        public bool Retryable { get; init; }
        public int Status { get; init; }
        public string? Body { get; init; }
        public string? Error { get; init; }

        public static StageOutcome Success(int status, string? body) =>
            new() { Ok = true, Status = status, Body = body };

        public static StageOutcome Retry(int status) =>
            new() { Retryable = true, Status = status, Error = "paypal 3ds: HTTP " + status };

        public static StageOutcome Failed(int status) =>
            new() { Status = status, Error = "paypal 3ds: HTTP " + status };

        /// <summary>A machine stop whose reason is not an HTTP answer — a not-yet-decoded stage.</summary>
        public static StageOutcome Pending(string reason) => new() { Error = reason };
    }

    /// <summary>The stage text selector both builders apply to the ctx+144 flag.</summary>
    public static string StatusText(bool challengeActive) =>
        challengeActive ? ProcessingStatus : SolvingStatus;

    /// <summary>
    /// The nine observable stages' own labels, every one confirmed by decompile (R1081/R1082):
    /// the label objects are exactly the pool listing's chars-12 addresses — (1) 0x146e93fa8,
    /// (2) 0x146e93ff0, (2.1) 0x146e94038, (3) 0x146e94080, (4) 0x146e940c8, (5) 0x146e94110,
    /// (6) 0x146e94158, (7) 0x146e941a0, (8) 0x146e941e8. Each stage's builder is the same
    /// request template — same header dialects, same 30s budget, same 200/403/429 dispatch —
    /// differing only in the label, the success-continuation slot and the payload it carries:
    /// (1) sub_141102970/105A80 resumes a1[4]/a1[9], (2) sub_141103410 (+hosted twins
    /// sub_141107DA0/sub_141108170) a1[7], (2.1) sub_141103800 a1[8], (3) sub_141103BF0 a
    /// shared closure at qword_1472C7328+120, (4) sub_1411090C0 a1+80, (5) sub_141109550
    /// a1+88, (6) sub_141109910 a1[12], (7) sub_14110A080 a1+104, (8) sub_141106360 a1[11].
    /// Stages 4-8 run the hosted dialect; their per-stage graphql payloads remain
    /// caller-supplied — the payload builders are the next probe.
    /// </summary>
    public static readonly IReadOnlyDictionary<string, string> StageLabels =
        new Dictionary<string, string>
        {
            ["1"] = SolvingStatus,
            ["2"] = "Solving PayPal 3DS (2)",
            ["2.1"] = "Solving PayPal 3DS (2.1)",
            ["3"] = "Solving PayPal 3DS (3)",
            ["4"] = "Solving PayPal 3DS (4)",
            ["5"] = "Solving PayPal 3DS (5)",
            ["6"] = "Solving PayPal 3DS (6)",
            ["7"] = "Solving PayPal 3DS (7)",
            ["8"] = "Solving PayPal 3DS (8)",
        };

    /// <summary>True when the stage's request body is one this workspace has decoded.</summary>
    public static bool StageIsDecoded(string stage) => StageLabels.ContainsKey(stage);

    /// <summary>
    /// The normal dialect's header wall, in the builder's own order (sub_141102970).
    /// The original also pins a null cookie header — "no cookie sent", which is the same wire
    /// as not setting one, so it is omitted rather than sent empty.
    /// </summary>
    public static IReadOnlyDictionary<string, string> NormalHeaders(StageInput i) => new Dictionary<string, string>
    {
        ["sec-ch-ua"] = i.SecChUa ?? string.Empty,
        ["x-paypal-internal-euat"] = i.Euat ?? string.Empty,
        ["paypal-client-metadata-id"] = i.MetadataId ?? string.Empty,
        ["sec-ch-ua-mobile"] = "?0",
        ["user-agent"] = i.UserAgent ?? string.Empty,
        ["content-type"] = "application/json",
        ["accept"] = "*/*",
        ["x-app-name"] = AppName,
        ["sec-ch-ua-platform"] = i.SecChUaPlatform ?? string.Empty,
        ["origin"] = "https://www.paypal.com",
        ["sec-fetch-site"] = "same-origin",
        ["sec-fetch-mode"] = "cors",
        ["sec-fetch-dest"] = "empty",
        ["referer"] = "https://www.paypal.com",
        ["Accept-Encoding"] = "gzip, deflate",
        ["Accept-Language"] = "en-GB",
    };

    /// <summary>
    /// The hosted dialect's header wall (sub_141105A80): x-requested-with/x-locale/priority/x-country
    /// appear, the sec-fetch family does not, and the app name and referer come from the context.
    /// The original also pins a placeholder content-length of 0 that its transport overwrites with
    /// the real length — this replica lets its transport do the same rather than send a wrong one.
    /// </summary>
    public static IReadOnlyDictionary<string, string> HostedHeaders(StageInput i) => new Dictionary<string, string>
    {
        ["sec-ch-ua-platform"] = i.SecChUaPlatform ?? string.Empty,
        ["sec-ch-ua"] = i.SecChUa ?? string.Empty,
        ["sec-ch-ua-mobile"] = "?0",
        ["x-requested-with"] = "fetch",
        ["accept"] = "*/*",
        ["content-type"] = "application/json",
        ["x-locale"] = "en_US",
        ["paypal-client-context"] = i.MetadataId ?? string.Empty,
        ["x-app-name"] = i.HostedAppName ?? string.Empty,
        ["x-paypal-internal-euat"] = i.Euat ?? string.Empty,
        ["paypal-client-metadata-id"] = i.MetadataId ?? string.Empty,
        ["user-agent"] = i.UserAgent ?? string.Empty,
        ["x-country"] = i.Country ?? string.Empty,
        ["referer"] = i.HostedReferer ?? string.Empty,
        ["accept-encoding"] = "gzip, deflate, br, zstd",
        ["accept-language"] = "en-US,en;q=0.9",
        ["priority"] = "u=1, i",
    };

    /// <summary>
    /// Stage 1, both paths: the white StatusInfo wall, the thirty-second budget, the exact header
    /// dialect, and the PUT to PayPal's graphql surface with the previous stage's payload.
    /// </summary>
    public static async Task<StageOutcome> SubmitAsync(FlowContext c, StageInput input, CancellationToken ct,
        string? url = null)
    {
        // The wall registration both builders make: (status text, "white", "StatusInfo", null).
        c.Emit(StatusText(input.ChallengeActive), "StatusInfo");

        var options = c.Options("paypal-3ds");
        options.Timeout = TimeSpan.FromMilliseconds(StageTimeoutMs);
        foreach (var h in (input.Hosted ? HostedHeaders(input) : NormalHeaders(input)))
            options.Headers[h.Key] = h.Value;

        options.Content = new StringContent(input.Payload, System.Text.Encoding.UTF8, "application/json");
        var res = await c.Http.SendAsync(HttpMethod.Put, url ?? GraphqlUrl, options, ct).ConfigureAwait(false);
        c.Session.AbsorbCookies(res.Cookies);

        // The status dispatch the builders register: 200 reaches the success continuation, and
        // 403 and 429 share one retry closure. Everything else is unhandled — a fail, not a retry.
        if (res.StatusCode == 200) return StageOutcome.Success(200, res.Body);
        if (res.StatusCode is 403 or 429) return StageOutcome.Retry(res.StatusCode);
        return StageOutcome.Failed(res.StatusCode);
    }

    /// <summary>
    /// The four-state machine the image names (Submit3DS → Process3DS → Waiting3DS → Complete3DS).
    /// Submit runs; the machine stops where the workspace's knowledge does — all nine stage
    /// builders are decoded (labels, dialects, continuation slots), but the per-stage graphql
    /// payloads they PUT are assembled by callers this workspace has not decoded, and inventing
    /// operations would be a guess dressed as a protocol.
    /// </summary>
    public async Task<StageOutcome> RunAsync(FlowContext c, StageInput input, CancellationToken ct,
        string? url = null)
    {
        var submit = await SubmitAsync(c, input, ct, url).ConfigureAwait(false);
        if (!submit.Ok) return submit;
        c.Session.Vars["paypal3ds.state"] = nameof(ThreeDsState.Process3DS);

        // Process3DS and beyond run stages (2)-(8) through the decoded builders. R1083 identified
        // the payloads: they are FROZEN graphql literals, not opaque caller magic — the
        // threeDomainSecure family at 0x1470cc8cc..0x14712190c (ApproveOnboardPaymentMutation,
        // CurrencyConversion, OnboardGuestMutation, approveMemberPayment, PayWithQuery, and
        // ResolveThreeDsContingency x2 — the resolution operation with token/authId/referenceId/
        // creditCardId/status/experiences variables). The variant-B resolver (0x1470dc9bc) is
        // assembled by the hosted solver sub_141113680 itself — the 11-case state machine R1078
        // located; the variant-A resolver (0x1470d7974) by the normal solver sub_14110FDB0.
        // What remains unknown is the per-case variable binding (which case sets which
        // authId/referenceId/status), so the runnable edge stays at Submit until a case body
        // is decoded.
        return StageOutcome.Pending(
            "paypal 3ds: all nine stage builders decoded; payloads identified as the frozen " +
            "threeDomainSecure graphql family (ResolveThreeDsContingency drives the resolver " +
            "stages, assembled by the solver bodies sub_14110FDB0/sub_141113680); the per-case " +
            "variable bindings remain to be decoded -- Submit runs, the rest waits on those");
    }
}
