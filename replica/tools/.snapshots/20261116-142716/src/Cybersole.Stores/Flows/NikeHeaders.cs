using Cybersole.Stores.Flows;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The seven Nike-specific identifiers the 5.18.32 image contains, read out in R88 with
/// <c>find_regex "nike-[a-z-]+"</c> (plus the two upper-case spellings it also matched, checked by
/// hand):
///
/// <code>
/// nike-api-caller-id     0x1470e4b84
/// x-nike-ux-id           0x14716b6d4
/// x-nike-visitid         0x14716b704
/// x-nike-visitorid       0x14716b73c
/// Nike-Kasada-Version    0x146dfbbd4
/// NIKE-SESSION           0x146df5874
/// NIKE-GS                0x146df584c
/// </code>
///
/// <para>
/// The replica sent <b>none</b> of them: docs/NIKE_PARITY.md listed "four Nike headers unset", and
/// the truth is seven identifiers, four of which are headers on every API call.
/// </para>
///
/// <para>
/// <b>No values are invented here.</b> Each name maps to a session var the flow fills from what the
/// site itself hands back; a header is only sent when its value is known. A header with a made-up
/// value is worse than a missing one — it tells Kasada the client is lying rather than absent.
/// </para>
/// </summary>
public static class NikeHeaders
{
    public const string ApiCallerId = "nike-api-caller-id";
    public const string UxId = "x-nike-ux-id";
    public const string VisitId = "x-nike-visitid";
    public const string VisitorId = "x-nike-visitorid";
    public const string KasadaVersion = "Nike-Kasada-Version";
    public const string Session = "NIKE-SESSION";
    public const string Gs = "NIKE-GS";

    /// <summary>Session var key → header name, for the five that are request headers.</summary>
    public static readonly IReadOnlyDictionary<string, string> FromSessionVar =
        new Dictionary<string, string>(StringComparer.Ordinal)
        {
            ["nike.apiCallerId"] = ApiCallerId,
            ["nike.uxId"] = UxId,
            ["nike.visitId"] = VisitId,
            ["nike.visitorId"] = VisitorId,
            ["nike.kasadaVersion"] = KasadaVersion,
        };

    /// <summary>The two that are cookie names rather than headers.</summary>
    public static readonly IReadOnlyList<string> Cookies = new[] { Session, Gs };

    // ---- the VALUES (R202) ---------------------------------------------------------------------------
    //
    // R88 read the header NAMES out of the image and left the values to the session, "because a header with a made-up
    // value is worse than a missing one". That was right, and it stayed incomplete: nothing ever filled
    // `nike.apiCallerId`, so the header never went out at all. The image does carry the values, and the composed iOS
    // one pins the format:

    /// <summary>One caller id with the address it was read at.</summary>
    public sealed record CallerId(string Id, string Address, string What);

    /// <summary>The composed iOS value, verbatim: `nike:<callerId>:<os>:<osVersion>` (0x07100354).</summary>
    public const string IosComposedExample = "nike:com.nike.commerce.omega.ios:ios:26.8";

    /// <summary>The four caller ids the image contains, in address order.</summary>
    public static readonly IReadOnlyList<CallerId> CallerIds = new[]
    {
        new CallerId("com.nike.commerce.checkout.web", "0x06fd2aa4", "the web checkout client"),
        new CallerId("com.nike.commerce.nikedotcom.web", "0x06fd2afc", "the nike.com web client"),
        new CallerId("com.nike.unite", "0x06fd2b54", "Nike's identity/unite client"),
        // the iOS id has no standalone literal: it exists only inside the composed value, so that is what is recorded
        new CallerId(IosComposedExample, "0x07100354", "the iOS checkout app, composed"),
    };

    /// <summary>The app marker that belongs to the Android build.</summary>
    public const string AndroidMarker = "nike_android_mobile";

    /// <summary>
    /// The value this flow sends: the WEB checkout client. The image's only composed value is the iOS app's, and
    /// sending that from a browser flow would claim to be an app the session is not — the ids are all in the image,
    /// the choice of which one belongs to a browser is the inference, and it is recorded as one.
    /// </summary>
    public const string WebCallerId = "com.nike.commerce.checkout.web";

    /// <summary>The format the image composes its own value in: <c>nike:&lt;callerId&gt;:&lt;os&gt;:&lt;osVersion&gt;</c>.</summary>
    public static string ComposeCallerId(string callerId, string os, string osVersion) =>
        "nike:" + callerId + ":" + os + ":" + osVersion;

    /// <summary>All seven identifiers, in the image's address order.</summary>
    public static readonly IReadOnlyList<string> All = new[]
    {
        Gs, Session, KasadaVersion, ApiCallerId, UxId, VisitId, VisitorId,
    };

    /// <summary>
    /// Copies whichever of the five headers the session actually knows into
    /// <paramref name="headers"/>. Returns the number set, so a caller can log "0 headers, the page
    /// handed back none" instead of pretending.
    /// </summary>
    public static int Apply(IDictionary<string, string>? sessionVars,
        IDictionary<string, string> headers)
    {
        if (sessionVars is null) return 0;

        var applied = 0;
        foreach (var (varKey, header) in FromSessionVar)
        {
            if (!sessionVars.TryGetValue(varKey, out var value)) continue;
            if (string.IsNullOrWhiteSpace(value)) continue;

            headers[header] = value;
            applied++;
        }

        return applied;
    }
}
