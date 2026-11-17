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
/// perimeterx    px-captcha (inferred)       none named        no   — _px3 exists; px-captcha does not
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

    /// <summary>
    /// Where a row's detection marker came from. R997 added this because two of the six markers turned out not to be in the
    /// image at all, and the table gave no way to tell.
    ///
    /// <para>
    /// The distinction is criterion (d)'s: every claim carries its authority. <c>kpsdk</c>, <c>queue-it</c> and
    /// <c>datadome</c> are literals the image contains -- seventeen, thirteen and fifteen times respectively. Neither
    /// <c>cf-chl</c> nor <c>_Incapsula_Resource</c> appears anywhere in it, so those two rows describe a detector this
    /// workspace wrote, not one it copied. Cloudflare's happens to work because <c>cf-chl</c> is what a real Cloudflare
    /// challenge page contains -- but that is general knowledge, not evidence from the artifact, and the table should say
    /// so rather than let a Wired row look as though it were transcribed.
    /// </para>
    /// </summary>
    public enum MarkerSource
    {
        /// <summary>The image contains this literal.</summary>
        ImageLiteral,
        /// <summary>This workspace chose this marker; the image does not carry it.</summary>
        Inferred,
    }

    /// <summary>
    /// Why a row's marker is not the image's, when it is not.
    ///
    /// <para>
    /// R1020 splits what one value used to hold. Two rows are <see cref="MarkerSource.Inferred"/> for opposite reasons:
    /// imperva appears in the artifact under none of its six spellings, so there is no vendor to look for; perimeterx is
    /// present, with four cookie-side literals, and simply has nothing page-level to grep for. Reporting both as
    /// "inferred" made a vendor that is missing look like a vendor whose marker this workspace happened to choose, and
    /// the difference decides what the next move is.
    /// </para>
    /// </summary>
    public enum Gap
    {
        /// <summary>The marker is the image's, so there is no gap.</summary>
        None,
        /// <summary>The vendor itself appears nowhere in the artifact, under any spelling.</summary>
        VendorAbsent,
        /// <summary>The vendor is in the artifact, but no page-level literal names it.</summary>
        NoPageMarker,
    }

    /// <summary>One row of the audit.</summary>
    public sealed record Row(string Vendor, string Marker, string? Cookie, State State, string Note,
        MarkerSource MarkerFrom, Gap Gap);

    /// <summary>The audit, in the order <c>DetectAsync</c> tests its markers.</summary>
    public static readonly IReadOnlyList<Row> Rows = new[]
    {
        new Row("cloudflare", "challenge-platform", "cf_clearance", State.Wired,
            "R140: CloudflareClearance runs the service→in-bot ladder and writes the cookie. R1019 moved the marker "
            + "from cf-chl, which the image does not contain, to challenge-platform, which it carries twice as "
            + "/cdn-cgi/challenge-platform/ -- page-level, which is what DetectAsync reads. cf_clearance and __cf_bm "
            + "are in the image too but are cookie names, so they belong in the cookie column where cf_clearance sits.",
            MarkerSource.ImageLiteral, Gap.None),

        new Row("kasada", "kpsdk", "kpsdk", State.Wired,
            "R141: KasadaClearance runs the four-road strategy and writes the token",
            MarkerSource.ImageLiteral, Gap.None),

        // R1024: Akamai was missing from this audit while being the vendor the image documents most thoroughly --
        // analysis/endpoints.md lists twenty-five literals for it. Verified in this round, in address order:
        //
        //   detection   AkamaiGHost (0x146b249dc) · AkamaiQueueName (0x146b24a0c) · AkamaiReferer (0x146b24a44)
        //   solving     "Solving Akamai (" (0x146e77ebc) · "(SBSD)" (0x146e77ef4) · "(SDS)" (0x146e77f34)
        //   failure     "Akamai Failed" · "Akamai Failed (Rotating)" · "Akamai Blocked (IP)" · "Akamai block"
        //   control     SkipAkamai (0x146e7243c) · "Akamai disabled"
        //   internal    GetAkamaiCookie · AkamaiHandler · AkamaiQueueHandler · AkamaiPixel · AkamaiGenerator*
        //
        // So three things are true at once, and the two columns keep them apart on purpose. The marker is image
        // evidence (Gap.None), the original does solve this vendor ("Solving Akamai" with two named modes), and this
        // workspace has no Akamai solver -- its only mentions are failure messages in the fanatics and casio flows. That
        // last one is what DetectedOnly records, and it is a statement about the replica rather than about the image.
        new Row("akamai", "AkamaiGHost", null, State.DetectedOnly,
            "R1024: the image carries twenty-five Akamai literals including a three-stage solver -- \"Solving Akamai (\", "
            + "\"(SBSD)\" and \"(SDS)\" -- plus Blocked/Failed/(Rotating) outcomes and a SkipAkamai control, so the "
            + "original both solves it and can route around it. This replica detects it and has no solver: the name turns "
            + "up in its source only inside fanatics' and casio's 403 messages. DetectedOnly is therefore a statement "
            + "about the replica, not about the artifact.",
            MarkerSource.ImageLiteral, Gap.None),

        new Row("imperva", "_Incapsula_Resource", null, State.DetectedOnly,
            "R1021: two independent sources agree the vendor is absent. None of six spellings is in the artifact "
            + "(_Incapsula_Resource, incap_ses, visid_incap, incapsula, imperva, nlbi_), and AntiBotVendors.All -- eight "
            + "vendors, each carrying the literals that prove it -- does not list Imperva, nor does NamedButNotHandled. "
            + "The branch is kept as an extension so an Imperva wall on a store the original never covered is reported "
            + "rather than swallowed as a product page; it fires only on a page naming the resource.",
            MarkerSource.Inferred, Gap.VendorAbsent),

        new Row("datadome", "datadome", "datadome", State.Wired,
            "R996: DataDomeClearance runs the sensor at datadome.cybersole.io/sensor, narrates the image's four stages "
            + "and writes the datadome cookie. R141's correction stands -- SolveBotD proved the original solves it -- and "
            + "what was missing was the call, which now exists and which SolveDetectedWallAsync dispatches to.",
            MarkerSource.ImageLiteral, Gap.None),

        // R1022: Gap.NoPageMarker now has a second witness. AntiBotVendors has carried a PerimeterX entry since
        // before this audit, and none of its literals is a page-level string (R1023 added a fifth, "Solving PerimeterX",
        // after finding the query behind R1022 had stopped one match short):
        //
        //   PerimeterX        five hits, and what they are is the workspace's own narration -- "PerimeterX block
        //                     (Rotating proxy)" is what Cybersole shows a user, not what a store serves
        //   PerimeterX-Token  a cookie or header name
        //   PerimeterXHandler a class name, i.e. reflection metadata
        //   _pxHandler        a field or method name
        //   Solving PerimeterX  a line of the workspace's own progress output -- and the one that settles the vendor is
        //                     handled rather than only detected, because it is present progressive
        //
        // So the vendor is present and nothing in it can be grepped out of a response body. px-captcha is this
        // workspace's word for the interstitial and the image does not carry it, which is why the row is Inferred and
        // why the gap is NoPageMarker rather than VendorAbsent: the vendor is handled, the page marker is missing.
        new Row("perimeterx", "px-captcha", null, State.DetectedOnly,
            "R998 corrects R997's own row. The cookie evidence is real -- _px3, _pxvid and PerimeterX-Token are image "
            + "literals, and the image carries a PerimeterXHandler plus 'PerimeterX block (Rotating proxy)' -- but the marker "
            + "in this column, px-captcha, appears nowhere in it. R997 labelled the row ImageLiteral by checking the cookie "
            + "column instead of the marker column. R1018 then found R998 had attributed the image's four captcha-delivery "
            + "literals to this vendor when they are DataDome's -- DdInterstitialClient sits beside them -- so DetectAsync "
            + "now routes them to datadome and this row keeps px-captcha as the only marker it can claim, which the image "
            + "does not carry.",
            MarkerSource.Inferred, Gap.NoPageMarker),

        // R1025: this row said NotAChallenge -- "a queue, not a wall: the correct handling is to wait" -- and the image
        // says otherwise in eight places. Verified this round:
        //
        //   "Fetching Queue-it challenge"           the vendor serves a challenge
        //   "Error Solving Queue-it (Softblock)"     the original tries to solve one
        //   "Error Initiliazing Queue-it (Softblock)" and can fail to initialise
        //   "Queue-IT banned, rotating proxy"        it also routes around
        //   "Unsupported Queue-it BotDeflector page" BotDeflector is Queue-it's anti-bot product, by name
        //   /softblock                              an endpoint
        //   /challengeapi/queueitcaptcha/challenge/  a CAPTCHA endpoint
        //   seven X-queueit-challange-* headers      challenge metadata, down to ruleid and rulename
        //
        // So a waiting room and a challenge surface are two things this vendor does, which is R772's shape again. The
        // state becomes DetectedOnly: recognised, with no solver here. What the row had right is that waiting is part
        // of the handling -- it was wrong to conclude that waiting is all of it.
        new Row("queue-it", "queue-it", "queue-it-set-cookie", State.DetectedOnly,
            "R1025: the image carries a challenge surface beside the waiting room -- Fetching Queue-it challenge, "
            + "Solving/Initiliazing Queue-it (Softblock), BotDeflector, /softblock, "
            + "/challengeapi/queueitcaptcha/challenge/ and seven X-queueit-challange-* headers -- so waiting is part of "
            + "the handling rather than all of it. Rows earlier in this file called it NotAChallenge; that was reading "
            + "the waiting room as the whole vendor.",
            MarkerSource.ImageLiteral, Gap.None),
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
