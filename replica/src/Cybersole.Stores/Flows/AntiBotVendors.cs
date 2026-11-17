using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The anti-bot vendors the 5.18.32 image knows about, read out in R105.
///
/// <para>
/// Every entry below is backed by a literal in the image. The interesting one is DataDome: the
/// image does not talk to <c>api-sdk.datadome.co</c> directly for sensors — it talks to
/// <c>datadome.cybersole.io/sensor</c>, a <b>first-party host</b>. That is a relay: the tool runs its
/// own sensor endpoint so the request looks like it comes from its own domain.
/// </para>
///
/// <code>
/// DataDome      api-sdk.datadome.co/sdk/   datadome.cybersole.io/   …/sensor
///               DataDomeKey  DataDomeChallenge  DatadomeSliderTask
/// PerimeterX    PerimeterX  PerimeterX-Token  PerimeterXHandler  _pxHandler
/// Akamai        AkamaiGHost  AkamaiQueueName  pollToken
/// Kasada        GetKasada  Kasada  KasadaCt  &lt;Store&gt;-Kasada-Version  (per store!)
/// TrustDecision static.trustdecision.com/{fra,sg}/botd.js   …/tdfp
/// Cloudflare    Turnstile  .cf-turnstile  __cf_chl_tk  LoopTurnstile
/// captcha tasks AntiTurnstileTaskProxyLess          (a solver-service task name)
/// Forter        cdn3.forter.com/events  cdn123.forter.com/?u=  .cdn.forter.com/prop.json
///               forter.cybersole.workers.dev/   forterToken  ForterEnvelope  ForterEventsEncoder
/// </code>
///
/// <para>
/// The per-store Kasada version headers are the detail a single global version would get wrong:
/// Converse, Crocs EU, Crocs JP, Crocs and Footsites each carry their own
/// <c>&lt;Store&gt;-Kasada-Version</c> literal.
/// </para>
/// </summary>
public static class AntiBotVendors
{
    /// <summary>One vendor, with the literals that prove the image handles it.</summary>
    public sealed record Vendor(string Name, IReadOnlyList<string> Evidence);

    /// <summary>The DataDome relay host — first-party, not the vendor's own domain.</summary>
    public const string DataDomeRelay = "datadome.cybersole.io/";

    /// <summary>The DataDome sensor path the relay serves.</summary>
    public const string DataDomeSensor = "datadome.cybersole.io/sensor";

    /// <summary>DataDome's own SDK host, which the image also names.</summary>
    public const string DataDomeSdk = "api-sdk.datadome.co/sdk/";

    /// <summary>
    /// The Forter relay host. R762: Forter gets the same treatment as DataDome -- the image names
    /// <c>forter.cybersole.workers.dev/</c> alongside Forter's own <c>cdn0/3/6.forter.com</c> hosts, so the tool
    /// fronts the vendor from its own Worker rather than posting to the vendor directly.
    /// </summary>
    public const string ForterRelay = "forter.cybersole.workers.dev/";

    /// <summary>Forter's event upload endpoint, the one the sensor is posted to.</summary>
    public const string ForterEvents = "https://cdn3.forter.com/events";

    /// <summary>
    /// Riskified's three hosts. R807.
    ///
    /// <para>
    /// <b>Observation:</b> the image names <c>https://beacon.riskified.com/?shop=</c>,
    /// <c>https://c.riskified.com/v2/client_infos</c> and <c>https://img.riskified.com/img/image-l.gif?t=</c>. The three
    /// serve different jobs -- a beacon, a client-info post, and a tracking pixel -- which is why they are kept apart
    /// rather than collapsed into one host.
    /// </para>
    /// </summary>
    public const string RiskifiedBeacon = "https://beacon.riskified.com/?shop=";

    /// <inheritdoc cref="RiskifiedBeacon"/>
    public const string RiskifiedClientInfo = "https://c.riskified.com/v2/client_infos";

    /// <inheritdoc cref="RiskifiedBeacon"/>
    public const string RiskifiedPixel = "https://img.riskified.com/img/image-l.gif?t=";

    /// <summary>
    /// Riskified's cookie names, verbatim from the image. R807.
    ///
    /// <para>
    /// <c>_riskified</c>, <c>_riskifiedId</c> and <c>_riskifiedToken</c> are three distinct cookies rather than one
    /// family, and <c>FNL_RISKIFIED_ID=([^;]+)</c> is a regex the image uses to pull the id out of a cookie header --
    /// so it is recorded as the extraction pattern it is, not as a cookie name.
    /// </para>
    /// </summary>
    public const string RiskifiedLegacyCookie = "_riskified";

    /// <inheritdoc cref="RiskifiedLegacyCookie"/>
    public const string RiskifiedIdCookie = "_riskifiedId";

    /// <inheritdoc cref="RiskifiedLegacyCookie"/>
    public const string RiskifiedTokenCookie = "_riskifiedToken";

    /// <summary>The shop identifier cookie the beacon carries.</summary>
    public const string RiskifiedShopCookie = "riskified_cookie";

    /// <summary>
    /// Signifyd's two endpoints live on the Scheels frontastic hub. R807, deduplicated R808.
    ///
    /// <para>
    /// <b>Observation:</b> the image carries <c>sendSignifydStepUpCode</c> and
    /// <c>completeSignifydStepUpCheckout</c> as frontastic cart actions, with <c>HandleSignifydStepUp</c>,
    /// <c>GetSignifydCode</c> and <c>CompleteSignifydStepUp</c> as the state machine around them, and
    /// <c>requiresSignifydStepUp</c> as the flag that starts it. That is a code-verification step-up, not a passive
    /// sensor, which is why Signifyd is a handled vendor rather than a named one.
    /// </para>
    ///
    /// <para>
    /// R807 wrote both URLs out as literals here. R808 found that <see cref="ScheelsFrontastic"/> had carried them
    /// since R103, so this now references that class rather than repeating the strings. Two hard-coded copies of one
    /// URL is the kind of duplication that drifts.
    /// </para>
    /// </summary>
    public const string SignifydSendCode = RetailApiFamilies.ScheelsFrontastic.SignifydStepUpCode;

    /// <inheritdoc cref="SignifydSendCode"/>
    public const string SignifydCompleteStepUp = RetailApiFamilies.ScheelsFrontastic.CompleteSignifydStepUp;

    public static readonly IReadOnlyList<Vendor> All = new[]
    {
        new Vendor("DataDome", new[]
        {
            DataDomeSdk, DataDomeRelay, DataDomeSensor,
            "DataDomeKey", "DataDomeChallenge", "DatadomeSliderTask",
        }),
        // R1023 adds the fifth literal, which R1022's note had left out because the query stopped at four matches of the
        // display name. "Solving PerimeterX" (0x146e9423c) is present progressive: the original has a solving action for
        // this vendor. That retracts R1022's guess that routing around a block was its whole response -- both literals
        // are in the artifact, "PerimeterX block (Rotating proxy)" and "Solving PerimeterX", so the two paths coexist
        // rather than one replacing the other, which is the same shape as R772's two surfaces.
        //
        // It is still not a page-level string, so Gap.NoPageMarker stands: it is a line of the workspace's own output,
        // not something a store serves. What it does settle is that this vendor is handled, not merely detected.
        new Vendor("PerimeterX", new[]
        {
            "PerimeterX", "PerimeterX-Token", "PerimeterXHandler", "_pxHandler", "Solving PerimeterX",
        }),
        new Vendor("Akamai", new[]
        {
            "AkamaiGHost", "AkamaiQueueName", "pollToken",
        }),
        new Vendor("Kasada", new[]
        {
            "GetKasada", "Kasada", "KasadaCt", "Nike-Kasada-Version",
        }),
        new Vendor("TrustDecision", new[]
        {
            "static.trustdecision.com/fra/botd.js",
            "static.trustdecision.com/sg/botd.js",
            "static.trustdecision.com/tdfp",
        }),
        new Vendor("Cloudflare", new[]
        {
            "Turnstile", ".cf-turnstile", "__cf_chl_tk", "LoopTurnstile",
        }),
        new Vendor("Forter", new[]
        {
            ForterEvents, "https://cdn123.forter.com/?u=", ".cdn.forter.com/prop.json", ForterRelay,
            "forterToken", "forterCookieToken", "CheckoutData.ForterToken", "BuildForterSessionId",
            "ForterEnvelope", "ForterEventsEncoder",
        }),
        new Vendor("Signifyd", new[]
        {
            "HandleSignifydStepUp", "SendSignifydStepUpCode", "CompleteSignifydStepUp",
            "GetSignifydCode", "requiresSignifydStepUp", "_signifydStepUpDone",
            SignifydSendCode, SignifydCompleteStepUp,
        }),
        // R1052: handled rather than merely named, on the criterion NamedButNotHandled states -- Riskified sits there
        // because Build/Handle/Get are absent for it, unlike BuildForterSessionId or GetKasada. Both below have handler
        // names, BotDeflector three bodies and Vercel a solver type plus a handler.
        new Vendor("BotDeflector", new[]
        {
            "BotDeflector", "SubmitBotDeflectorChallenge", "SolveBotDeflectorPow", "SolveBotDeflectorIcons",
            "_botDeflectorFingerprint", "Solving BotDeflector icons", "Solving BotDeflector proof of work",
        }),
        new Vendor("Vercel", new[]
        {
            "VercelBotIdSolver", "VercelChallengeHandler", "VercelChallengeToken",
            "x-vercel-challenge-token", "x-vercel-challenge-solution", "x-vercel-challenge-version",
            "/.well-known/vercel/security/request-challenge", "_vcrcs", "SupportedVersion",
        }),
    };

    /// <summary>
    /// Vendors the image names but does not handle. R807.
    ///
    /// <para>
    /// Riskified has three hosts and four cookie names in the pool, and no handler: <c>BuildRiskified</c>,
    /// <c>HandleRiskified</c> and <c>GetRiskified</c> are all absent, unlike <c>BuildForterSessionId</c> or
    /// <c>GetKasada</c> for the vendors in <see cref="All"/>. So it is recorded as named-and-nothing-more rather than
    /// counted among the handled ones.
    /// </para>
    ///
    /// <para>
    /// The distinction matters because <see cref="All"/> is what the anti-bot layer claims to defend against. A host
    /// string proves the original knew the vendor existed; it does not prove the original did anything about it.
    /// </para>
    /// </summary>
    public static readonly IReadOnlyList<Vendor> NamedButNotHandled = new[]
    {
        new Vendor("Riskified", new[]
        {
            RiskifiedBeacon, RiskifiedClientInfo, RiskifiedPixel,
            RiskifiedIdCookie, RiskifiedTokenCookie, RiskifiedLegacyCookie, RiskifiedShopCookie,
        }),
    };

    /// <summary>
    /// The per-store Kasada version headers, verbatim. A single shared version would be wrong for at
    /// least four of these five stores.
    /// </summary>
    public static readonly IReadOnlyList<string> KasadaVersionHeaders = new[]
    {
        "Converse-Kasada-Version",
        "Crocs-EU-Kasada-Version",
        "Crocs-JP-Kasada-Version",
        "Crocs-Kasada-Version",
        "Footsites-Kasada-Version",
    };

    /// <summary>A solver-service task name the image carries, verbatim.</summary>
    public const string TurnstileTaskName = "AntiTurnstileTaskProxyLess";

    /// <summary>True when the image handles the named vendor.</summary>
    public static bool Knows(string? vendor) =>
        !string.IsNullOrEmpty(vendor) &&
        All.Any(v => string.Equals(v.Name, vendor, System.StringComparison.OrdinalIgnoreCase));

    /// <summary>Every evidence literal across every vendor.</summary>
    public static IReadOnlyList<string> Evidence() => All.SelectMany(v => v.Evidence).ToList();
}
