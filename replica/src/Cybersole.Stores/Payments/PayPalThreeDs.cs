using System.Net.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// PayPal 3-D Secure — the challenge layer a PayPal payment runs when the bank asks for it,
/// decompiled end to end across R1078–R1086.
///
/// <para>
/// <b>The request template</b> (every stage, both dialects — sub_141102970 normal /
/// sub_141105A80 hosted, and the nine builders' twins): a PUT to the frozen
/// <c>https://www.paypal.com/graphql/</c> literal (0x147097e78, send step sub_14110D670) with a
/// thirty-second budget (+236 = 30000), a white <c>StatusInfo</c> wall, and the dispatch
/// <b>200 → success continuation, 403 and 429 → one shared retry closure</b>. The headers are
/// PayPal's own web-client fingerprint — <c>x-app-name: checkoutuinodeweb_hermione</c>
/// (0x146fc7338), <c>x-paypal-internal-euat</c>, <c>paypal-client-metadata-id</c>, the
/// sec-fetch family on the normal dialect, <c>x-requested-with</c>/<c>x-locale</c>/
/// <c>x-country</c>/<c>priority</c> on the hosted one.
/// </para>
///
/// <para>
/// <b>The payloads are persisted graphql operations</b> (R1083/R1085): each request body is
/// <c>{"operationName": N, "variables": {...}}</c> — the queries live server-side and are
/// referenced by name. The machine drives, in order: the contingency read (the submit stage),
/// <c>GetThreeDsJwtQuery</c>, the challenge window, <c>ThreeDsAuthenticateMutation</c>,
/// <c>ThreeDsLookUpMutation</c>, and <c>ResolveThreeDsContingency</c> with the six variables
/// token / authId / referenceId / creditCardId / status / experiences.
/// </para>
///
/// <para>
/// <b>The challenge window</b> (R1084/R1085): the response's contingency carries the bank's
/// redirect; the original opens a <c>500x600</c> window whose page is the frozen
/// <c>https://www.paypal.com/checkoutweb/processThreedsConfirmation</c> (0x147097d08), and the
/// window's post-back form carries exactly two fields, <c>JWT</c> (0x146dd3a08) and
/// <c>MD</c> (0x146df88d0). The resolver variables are read back through both a JSON needle
/// (<c>"referenceId":"</c>, via sub_140940820 / sub_140D91B40) and the challenge page's hidden
/// input (<c>input[id='referenceId']</c>, via sub_14092F630) — two sources, one value.
/// </para>
///
/// <para>
/// The four machine states the image names — <c>Submit3DS · Process3DS · Waiting3DS ·
/// Complete3DS</c> — map onto this class as: <see cref="RunAsync"/> (submit + contingency read +
/// JWT query, stopping at the window because the window is host-driven), and
/// <see cref="ContinueAsync"/> (authenticate + lookup + resolve once the window answered).
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

    /// <summary>The challenge window's page, a frozen literal (0x147097d08).</summary>
    public const string ChallengeWindowUrl = "https://www.paypal.com/checkoutweb/processThreedsConfirmation";

    /// <summary>The challenge window's width, from the frozen <c>_500_x_600</c> size (0x146f5ff08).</summary>
    public const int ChallengeWindowWidth = 500;

    /// <summary>The challenge window's height.</summary>
    public const int ChallengeWindowHeight = 600;

    /// <summary>The window's first post-back field (0x146dd3a08).</summary>
    public const string JwtFormField = "JWT";

    /// <summary>The window's second post-back field (0x146df88d0).</summary>
    public const string MdFormField = "MD";

    /// <summary>The graphql persisted-operation names, decoded from the solver bodies.</summary>
    public const string JwtQueryOperation = "GetThreeDsJwtQuery";               // 0x146da0cf0
    public const string AuthenticateOperation = "ThreeDsAuthenticateMutation"; // 0x146eef8a0
    public const string LookUpOperation = "ThreeDsLookUpMutation";             // 0x146eef8f0
    public const string ResolveOperation = "ResolveThreeDsContingency";         // the six-variable resolver

    /// <summary>The resolver's status values, carried in the <c>status</c> variable.</summary>
    public const string ResolveStatusSucceeded = "SUCCESS";
    public const string ResolveStatusFailed = "FAILED";

    /// <summary>The four state-machine names the image carries for the 3DS challenge.</summary>
    public enum ThreeDsState { Submit3DS, Process3DS, Waiting3DS, Complete3DS }

    /// <summary>
    /// The nine observable stages' own labels, every one confirmed by decompile (R1081/R1082):
    /// the label objects are exactly the pool listing's chars-12 addresses — (1) 0x146e93fa8,
    /// (2) 0x146e93ff0, (2.1) 0x146e94038, (3) 0x146e94080, (4) 0x146e940c8, (5) 0x146e94110,
    /// (6) 0x146e94158, (7) 0x146e941a0, (8) 0x146e941e8. Each stage's builder is the same
    /// request template — same header dialects, same 30s budget, same 200/403/429 dispatch.
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

    /// <summary>
    /// True when this class can drive the named stage. R1086: the machine runs the stages through
    /// the shared graphql helper, so the answer is the label map itself — the map is closed at
    /// nine, and a stage outside it does not exist in the image.
    /// </summary>
    public static bool StageIsDecoded(string? stage) =>
        !string.IsNullOrEmpty(stage) && StageLabels.ContainsKey(stage);

    /// <summary>
    /// One stage request's inputs — the fields the builders read off their payment context.
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

        /// <summary>The buyer token the resolver's <c>token</c> variable carries.</summary>
        public string? Token { get; init; }

        /// <summary>The checkout amount, formatted <c>{0:0.00}</c> (0x147193208) for the variables.</summary>
        public decimal Amount { get; init; }
    }

    /// <summary>
    /// What the contingency read found in the submit response — the fields the case bodies'
    /// needles pull out of <c>paymentContingencies</c> (jwtSpecification / referenceId / the
    /// card) plus the bank's redirect the window follows.
    /// </summary>
    public sealed class ContingencySnapshot
    {
        /// <summary>threeDomainSecure.status — empty when no challenge is asked for.</summary>
        public string? Status { get; init; }

        /// <summary>threeDomainSecure.redirectUrl.href — the bank's challenge page.</summary>
        public string? RedirectUrl { get; init; }

        /// <summary>threeDomainSecure.method.</summary>
        public string? Method { get; init; }

        /// <summary>threeDomainSecure.parameter.</summary>
        public string? Parameter { get; init; }

        /// <summary>threeDSContingencyData … contingencyContext.jwtSpecification.jwtIssuer.</summary>
        public string? JwtIssuer { get; init; }

        /// <summary>… jwtSpecification.jwtOrgUnitId.</summary>
        public string? JwtOrgUnitId { get; init; }

        /// <summary>The referenceId both sources agree on (response JSON / challenge-page hidden input).</summary>
        public string? ReferenceId { get; init; }

        /// <summary>threeDSContingencyData … resolution.paymentCard.id — the resolver's creditCardId.</summary>
        public string? CreditCardId { get; init; }

        /// <summary>True when the response asks for a challenge at all.</summary>
        public bool RequiresChallenge =>
            !string.IsNullOrEmpty(Status) && !string.IsNullOrEmpty(RedirectUrl);
    }

    /// <summary>What a machine step reports back.</summary>
    public sealed class StageOutcome
    {
        public bool Ok { get; init; }
        public bool Retryable { get; init; }
        public int Status { get; init; }
        public string? Body { get; init; }
        public string? Error { get; init; }

        /// <summary>The machine reached the challenge window — the host drives it from here.</summary>
        public bool AwaitingChallenge { get; init; }

        /// <summary>The snapshot parsed from the submit response, when one was read.</summary>
        public ContingencySnapshot? Contingency { get; init; }

        public static StageOutcome Success(int status, string? body) =>
            new() { Ok = true, Status = status, Body = body };

        public static StageOutcome Retry(int status) =>
            new() { Retryable = true, Status = status, Error = "paypal 3ds: HTTP " + status };

        public static StageOutcome Failed(int status) =>
            new() { Status = status, Error = "paypal 3ds: HTTP " + status };

        /// <summary>The machine stopped at the window — a real state, not an error.</summary>
        public static StageOutcome Challenge(ContingencySnapshot snapshot) =>
            new() { AwaitingChallenge = true, Contingency = snapshot,
                    Error = "paypal 3ds: challenge window required (" + snapshot.RedirectUrl + ")" };
    }

    /// <summary>The stage text selector both builders apply to the ctx+144 flag.</summary>
    public static string StatusText(bool challengeActive) =>
        challengeActive ? ProcessingStatus : SolvingStatus;

    /// <summary>
    /// The normal dialect's header wall, in the builder's own order (sub_141102970).
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

    /// <summary>The hosted dialect's header wall (sub_141105A80).</summary>
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
    /// One persisted-graphql stage request — the shape every decoded builder sends (R1085's
    /// case bodies: the body is <c>{"operationName": N, "variables": {...}}</c>, the queries live
    /// server-side under their names). The wall, the budget and the dispatch are the builders' own.
    /// </summary>
    public static async Task<StageOutcome> GqlAsync(FlowContext c, StageInput input, string operationName,
        JObject variables, CancellationToken ct, string? url = null)
    {
        c.Emit(StatusText(input.ChallengeActive), "StatusInfo");

        var options = c.Options("paypal-3ds");
        options.Timeout = TimeSpan.FromMilliseconds(StageTimeoutMs);
        foreach (var h in (input.Hosted ? HostedHeaders(input) : NormalHeaders(input)))
            options.Headers[h.Key] = h.Value;

        var body = new JObject
        {
            ["operationName"] = operationName,
            ["variables"] = variables,
        };
        options.Content = new StringContent(body.ToString(Newtonsoft.Json.Formatting.None),
            System.Text.Encoding.UTF8, "application/json");

        // The frozen literal is the target; the session var is the replica's standard test/config
        // seam (StoreFlow's checkStockUrl convention), so the gateway can drive the resolver
        // against a configured endpoint without the frozen URL being mutable in the protocol.
        var target = url
                     ?? (c.Session.Vars.TryGetValue("paypal3ds.graphqlUrl", out var gqlOverride) &&
                         !string.IsNullOrEmpty(gqlOverride)
                         ? gqlOverride
                         : GraphqlUrl);

        var res = await c.Http.SendAsync(HttpMethod.Put, target, options, ct).ConfigureAwait(false);
        c.Session.AbsorbCookies(res.Cookies);

        // The dispatch the builders register: 200 reaches the success continuation, and
        // 403 and 429 share one retry closure. Everything else is unhandled — a fail, not a retry.
        if (res.StatusCode == 200) return StageOutcome.Success(200, res.Body);
        if (res.StatusCode is 403 or 429) return StageOutcome.Retry(res.StatusCode);
        return StageOutcome.Failed(res.StatusCode);
    }

    /// <summary>
    /// Reads the contingency out of a submit response — the needles the case bodies pull
    /// (jwtSpecification / referenceId / the card's id), plus the bank's redirect the window follows.
    /// </summary>
    public static ContingencySnapshot ReadContingency(string? body)
    {
        JObject root;
        try { root = JObject.Parse(body ?? "{}"); }
        catch { return new ContingencySnapshot(); }

        string? Dig(params string[] path)
        {
            JToken? t = root;
            foreach (var p in path) t = t?[p];
            return t?.Type == JTokenType.Null ? null : t?.ToString();
        }

        return new ContingencySnapshot
        {
            Status = Dig("data", "paymentContingencies", "threeDomainSecure", "status")
                     ?? Dig("paymentContingencies", "threeDomainSecure", "status"),
            RedirectUrl = Dig("data", "paymentContingencies", "threeDomainSecure", "redirectUrl", "href")
                          ?? Dig("paymentContingencies", "threeDomainSecure", "redirectUrl", "href"),
            Method = Dig("data", "paymentContingencies", "threeDomainSecure", "method")
                     ?? Dig("paymentContingencies", "threeDomainSecure", "method"),
            Parameter = Dig("data", "paymentContingencies", "threeDomainSecure", "parameter")
                        ?? Dig("paymentContingencies", "threeDomainSecure", "parameter"),
            JwtIssuer = Dig("data", "paymentContingencies", "threeDSContingencyData", "resolution",
                            "contingencyContext", "jwtSpecification", "jwtIssuer")
                        ?? Dig("paymentContingencies", "threeDSContingencyData", "resolution",
                               "contingencyContext", "jwtSpecification", "jwtIssuer"),
            JwtOrgUnitId = Dig("data", "paymentContingencies", "threeDSContingencyData", "resolution",
                               "contingencyContext", "jwtSpecification", "jwtOrgUnitId")
                           ?? Dig("paymentContingencies", "threeDSContingencyData", "resolution",
                                  "contingencyContext", "jwtSpecification", "jwtOrgUnitId"),
            ReferenceId = Dig("data", "paymentContingencies", "threeDSContingencyData", "resolution",
                              "contingencyContext", "referenceId")
                          ?? Dig("paymentContingencies", "threeDSContingencyData", "resolution",
                                 "contingencyContext", "referenceId"),
            CreditCardId = Dig("data", "paymentContingencies", "threeDSContingencyData", "resolution",
                               "paymentCard", "id")
                           ?? Dig("paymentContingencies", "threeDSContingencyData", "resolution",
                                  "paymentCard", "id"),
        };
    }

    /// <summary>
    /// Submit3DS → the machine's synchronous reach: the submit stage reads the contingency, and a
    /// response that asks for a challenge fetches the JWT for the window before handing the
    /// window over to the host — the original's own stopping point (the window is driven by the
    /// offscreen browser pool, not by this state machine).
    /// </summary>
    public async Task<StageOutcome> RunAsync(FlowContext c, StageInput input, CancellationToken ct,
        string? url = null)
    {
        var submit = await SubmitAsync(c, input, ct, url).ConfigureAwait(false);
        if (!submit.Ok) return submit;
        c.Session.Vars["paypal3ds.state"] = nameof(ThreeDsState.Process3DS);

        var snapshot = ReadContingency(submit.Body);
        if (!snapshot.RequiresChallenge)
        {
            // No challenge asked for: the payment state is the response's, and the machine is done.
            c.Session.Vars["paypal3ds.state"] = nameof(ThreeDsState.Complete3DS);
            return StageOutcome.Success(submit.Status, submit.Body);
        }

        // Process3DS: the JWT the window's post-back carries. The case bodies' variables read
        // the amount formatted {0:0.00} beside the contingency fields.
        var jwtVariables = new JObject
        {
            ["amount"] = input.Amount.ToString("0.00"),
            ["jwtIssuer"] = snapshot.JwtIssuer,
            ["jwtOrgUnitId"] = snapshot.JwtOrgUnitId,
            ["referenceId"] = snapshot.ReferenceId,
        };
        var jwt = await GqlAsync(c, input, JwtQueryOperation, jwtVariables, ct, url).ConfigureAwait(false);
        if (!jwt.Ok) return jwt;
        c.Session.Vars["paypal3ds.jwt"] = jwt.Body ?? string.Empty;

        // Waiting3DS: the window itself. Its page, size and post-back fields are the decoded
        // constants — the host drives the browser; what it posts back is JWT and MD. The machine
        // state and the resolver's inputs persist on the session so the gateway's action
        // completion (CompleteActionAsync) can rebuild the snapshot and drive ContinueAsync.
        c.Session.Vars["paypal3ds.redirectUrl"] = snapshot.RedirectUrl ?? string.Empty;
        c.Session.Vars["paypal3ds.referenceId"] = snapshot.ReferenceId ?? string.Empty;
        c.Session.Vars["paypal3ds.creditCardId"] = snapshot.CreditCardId ?? string.Empty;
        c.Session.Vars["paypal3ds.euat"] = input.Euat ?? string.Empty;
        c.Session.Vars["paypal3ds.hosted"] = input.Hosted ? "1" : "0";
        c.Session.Vars["paypal3ds.token"] = input.Token ?? string.Empty;
        c.Session.Vars["paypal3ds.state"] = nameof(ThreeDsState.Waiting3DS);
        return StageOutcome.Challenge(snapshot);
    }

    /// <summary>
    /// Completes the machine after the challenge window answered — ThreeDsAuthenticateMutation,
    /// ThreeDsLookUpMutation, then ResolveThreeDsContingency with the six variables
    /// (token / authId / referenceId / creditCardId / status / experiences).
    /// </summary>
    public async Task<StageOutcome> ContinueAsync(FlowContext c, StageInput input, ContingencySnapshot snapshot,
        string authId, string status, CancellationToken ct, string? url = null)
    {
        c.Session.Vars["paypal3ds.state"] = nameof(ThreeDsState.Process3DS);

        var authVariables = new JObject
        {
            ["authId"] = authId,
            ["referenceId"] = snapshot.ReferenceId,
            ["creditCardId"] = snapshot.CreditCardId,
        };
        var auth = await GqlAsync(c, input, AuthenticateOperation, authVariables, ct, url).ConfigureAwait(false);
        if (!auth.Ok) return auth;

        var lookVariables = new JObject
        {
            ["referenceId"] = snapshot.ReferenceId,
            ["creditCardId"] = snapshot.CreditCardId,
        };
        var look = await GqlAsync(c, input, LookUpOperation, lookVariables, ct, url).ConfigureAwait(false);
        if (!look.Ok) return look;

        var resolveVariables = new JObject
        {
            ["token"] = input.Token,
            ["authId"] = authId,
            ["referenceId"] = snapshot.ReferenceId,
            ["creditCardId"] = snapshot.CreditCardId,
            ["status"] = status,
            ["experiences"] = new JArray("HERMES", "EXPRESS_CHECKOUT"),   // the decoded dialect set
        };
        var resolve = await GqlAsync(c, input, ResolveOperation, resolveVariables, ct, url).ConfigureAwait(false);
        if (!resolve.Ok) return resolve;

        c.Session.Vars["paypal3ds.state"] = nameof(ThreeDsState.Complete3DS);
        return StageOutcome.Success(resolve.Status, resolve.Body);
    }

    /// <summary>
    /// Stage 1, both dialects: the white StatusInfo wall, the thirty-second budget, the exact
    /// header dialect, and the PUT to PayPal's graphql surface with the caller's operation.
    /// The original's submit carried the first persisted operation; the helper above is the
    /// general form, and this step keeps its named place in the four-state machine.
    /// </summary>
    public static async Task<StageOutcome> SubmitAsync(FlowContext c, StageInput input, CancellationToken ct,
        string? url = null)
    {
        var submitVariables = new JObject
        {
            ["token"] = input.Token,
            ["amount"] = input.Amount.ToString("0.00"),
        };
        return await GqlAsync(c, input, JwtQueryOperation, submitVariables, ct, url).ConfigureAwait(false);
    }
}
