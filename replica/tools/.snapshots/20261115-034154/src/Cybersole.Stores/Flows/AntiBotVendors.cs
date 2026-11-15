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

    public static readonly IReadOnlyList<Vendor> All = new[]
    {
        new Vendor("DataDome", new[]
        {
            DataDomeSdk, DataDomeRelay, DataDomeSensor,
            "DataDomeKey", "DataDomeChallenge", "DatadomeSliderTask",
        }),
        new Vendor("PerimeterX", new[]
        {
            "PerimeterX", "PerimeterX-Token", "PerimeterXHandler", "_pxHandler",
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
