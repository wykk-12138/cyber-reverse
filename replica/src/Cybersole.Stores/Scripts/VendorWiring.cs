using System.Collections.Generic;
using System.Linq;
using Cybersole.Stores.Flows;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The six walls the flow detects, audited in one place for the defect R140 named:
/// <b>detection exists, storage exists, the call between them does not</b>.
///
/// <para>
/// <see cref="StoreFlow.DetectAsync"/> recognises cloudflare, kasada, imperva, datadome, perimeterx and
/// queue-it by a body marker or the <c>server</c> header. <see cref="AntiBotProtocol.Cookies"/> names
/// the cookie four of them set. What matters for a replica is the third column — whether anything
/// actually asks a solver for a token and writes it back — and before R140 that column was empty for
/// all six.
/// </para>
///
/// <code>
/// vendor        marker (detect)              cookie            call wired
/// cloudflare    cf-chl / server:cloudflare   cf_clearance      yes  (R140)
/// kasada        kpsdk                       kpsdk             yes  (R141, this round)
/// imperva       _Incapsula_Resource         none named        no   — no cookie, no solver
/// datadome      datadome                    datadome          no   — host recorded, protocol not
/// perimeterx    px-captcha                  none named        no   — deliberately blank
/// queue-it      queue-it                    queue-it-set-cookie  no — queue, not a solver
/// </code>
///
/// <para>
/// The four gaps are not the same kind of gap, and saying which kind each is makes them actionable:
/// DataDome has a host and no protocol (like Cloudflare before R140), PerimeterX has neither, Imperva's
/// cookie family is not in the image at all, and Queue-it is a queue rather than a challenge — the right
/// handling there is to wait, not to solve.
/// </para>
/// </summary>
public static class VendorWiring
{
    /// <summary>What state a vendor's call chain is in.</summary>
    public enum State
    {
        /// <summary>Detect → solve → store all exist.</summary>
        Wired,
        /// <summary>Host known, protocol unknown — a call can be injected but not written.</summary>
        HostWithoutProtocol,
        /// <summary>Detected, and the image names neither a cookie nor a solver.</summary>
        DetectedOnly,
        /// <summary>Not a challenge at all — waiting is the correct handling.</summary>
        NotAChallenge,
        /// <summary>
        /// The original solves this vendor and this workspace has not written the call yet. R995 added this because the
        /// four states above could not say it, and DataDome had been mislabelled as a result.
        ///
        /// <para>
        /// The distinction from <see cref="HostWithoutProtocol"/> is one of attribution, and it is the whole point. That
        /// state says the protocol does not exist. This one says the protocol exists in the image and the gap is in these
        /// notes — which is what <see cref="WallSolving.DataDomeCorrection"/> recorded at R141 when it found
        /// <c>SolveBotD</c>, DataDome's own challenge script, named by a method in the original.
        /// </para>
        /// </summary>
        OriginalSolvesProtocolUnrecorded,
    }

    /// <summary>One row of the audit.</summary>
    public sealed record Row(string Vendor, string Marker, string? Cookie, State State, string Note);

    /// <summary>The audit, in the order <c>DetectAsync</c> tests its markers.</summary>
    public static readonly IReadOnlyList<Row> Rows = new[]
    {
        new Row("cloudflare", "cf-chl / server: cloudflare", "cf_clearance", State.Wired,
            "R140: CloudflareClearance runs the service→in-bot ladder and writes the cookie"),

        new Row("kasada", "kpsdk", "kpsdk", State.Wired,
            "R141: KasadaClearance runs the four-road strategy and writes the token"),

        new Row("imperva", "_Incapsula_Resource", null, State.DetectedOnly,
            "the image names no Imperva cookie and no Imperva host"),

        new Row("datadome", "datadome", "datadome", State.OriginalSolvesProtocolUnrecorded,
            "R995 corrects this row. R141 already found SolveBotD -- DataDome's own challenge script, named by a method in "
            + "the original -- and WallSolving.DataDomeCorrection records the consequence: the original does solve DataDome "
            + "and the missing protocol is this workspace's gap. The image also names the whole chain: api-sdk.datadome.co/sdk/, "
            + "datadome.cybersole.io/sensor, DataDomeKey, DatadomeSliderTask, and GenerateSensor / SubmitSensor / GetSensorData "
            + "as three state machines. What is missing is the call, not the knowledge."),

        new Row("perimeterx", "px-captcha", null, State.DetectedOnly,
            "deliberately blank: a token header exists, no _px cookie does"),

        new Row("queue-it", "queue-it", "queue-it-set-cookie", State.NotAChallenge,
            "a queue, not a wall: the correct handling is to wait, not to solve"),
    };

    /// <summary>Vendors whose call chain is complete.</summary>
    public static IReadOnlyList<string> Wired =>
        Rows.Where(r => r.State == State.Wired).Select(r => r.Vendor).ToList();

    /// <summary>Vendors that are detected and do nothing about it.</summary>
    public static IReadOnlyList<string> Gaps =>
        Rows.Where(r => r.State != State.Wired).Select(r => r.Vendor).ToList();

    /// <summary>The row for a vendor, or null.</summary>
    public static Row? For(string? vendor) =>
        string.IsNullOrEmpty(vendor)
            ? null
            : Rows.FirstOrDefault(r => string.Equals(r.Vendor, vendor,
                System.StringComparison.OrdinalIgnoreCase));

    /// <summary>
    /// True when the detector recognises the vendor — the marker column, read back from the flow's own
    /// list so the audit cannot drift from the code it audits.
    /// </summary>
    public static bool IsDetected(string? vendor) =>
        !string.IsNullOrEmpty(vendor)
        && Rows.Any(r => string.Equals(r.Vendor, vendor, System.StringComparison.OrdinalIgnoreCase));

    /// <summary>The rule this round states, for a test to hold down.</summary>
    public const string AuditRule =
        "detection and storage are cheap and were already present; the call between them is the work";
}
