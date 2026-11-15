using System.Collections.Generic;
using Cybersole.Stores.Flows;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The session-level record of which browser a task is using — the other half of R133, where the
/// gateway learned to read these keys but nothing wrote them (R134).
///
/// <para>
/// Three values travel together because they only make sense together:
/// </para>
///
/// <list type="bullet">
/// <item><c>browser.fingerprintKey</c> — the key the fingerprint is derived from. The same key must
/// reach the browser launcher (it picks the profile directory) and the payment gateway (it picks the
/// screen), or the two disagree.</item>
/// <item><c>browser.timezoneOffsetMinutes</c> — what the page reports as
/// <c>new Date().getTimezoneOffset()</c>, in minutes east of UTC.</item>
/// <item><c>browser.fingerprintPayload</c> — <c>fingerprint-v1</c> or
/// <c>fingerprint-v1-sans-ua</c>, decided once here.</item>
/// </list>
///
/// <para>
/// Setting them is one call, and reading them back is one call, so no caller has to remember which
/// spelling of which key it needs.
/// </para>
/// </summary>
public static class BrowserIdentity
{
    public const string FingerprintKeyVar = "browser.fingerprintKey";
    public const string TimeZoneOffsetVar = "browser.timezoneOffsetMinutes";
    public const string PayloadVar = "browser.fingerprintPayload";

    /// <summary>
    /// Record the browser a task is using.
    ///
    /// <para>
    /// <paramref name="userAgentAlreadySent"/> decides the payload variant: a caller that already
    /// sends the UA on every request asks for the version without it, and the same choice is stored so
    /// the payment layer does not have to guess again.
    /// </para>
    /// </summary>
    public static void Record(FlowSession session, string fingerprintKey, int utcOffsetMinutes,
        bool userAgentAlreadySent = false)
    {
        session.Vars[FingerprintKeyVar] = fingerprintKey;
        session.Vars[TimeZoneOffsetVar] = utcOffsetMinutes.ToString(
            System.Globalization.CultureInfo.InvariantCulture);
        session.Vars[PayloadVar] = FingerprintLayers.PayloadFor(userAgentAlreadySent);
    }

    /// <summary>
    /// Record the browser from a launched profile path: the profile is the key, which is what makes
    /// the folder and the fingerprint describe one identity.
    /// </summary>
    public static BrowserFingerprint RecordProfile(FlowSession session, string profilePath,
        int utcOffsetMinutes = 0, bool userAgentAlreadySent = false)
    {
        Record(session, profilePath, utcOffsetMinutes, userAgentAlreadySent);
        return BrowserFingerprint.ForProfile(profilePath);
    }

    /// <summary>The key, or null when nothing recorded one — a flow that never opened a browser.</summary>
    public static string? FingerprintKey(FlowSession session) =>
        session.Vars.TryGetValue(FingerprintKeyVar, out var value) ? value : null;

    /// <summary>The offset, 0 when unknown (which is also what a UTC browser reports).</summary>
    public static int TimeZoneOffset(FlowSession session) =>
        session.Vars.TryGetValue(TimeZoneOffsetVar, out var raw)
        && int.TryParse(raw, System.Globalization.NumberStyles.Integer,
            System.Globalization.CultureInfo.InvariantCulture, out var minutes)
            ? minutes
            : 0;

    /// <summary>The payload variant, defaulting to the full one.</summary>
    public static string Payload(FlowSession session) =>
        session.Vars.TryGetValue(PayloadVar, out var value) && value.Length > 0
            ? value
            : FingerprintLayers.PayloadV1;

    /// <summary>True when this session's payload omits the User-Agent.</summary>
    public static bool IsSansUserAgent(FlowSession session) =>
        Payload(session) == FingerprintLayers.PayloadV1SansUa;

    /// <summary>
    /// The fingerprint for this session: from the recorded key when there is one, otherwise from the
    /// User-Agent, otherwise a stable default. Never random — two calls in one session must agree.
    /// </summary>
    public static BrowserFingerprint Fingerprint(FlowSession session) =>
        BrowserFingerprint.ForProfile(FingerprintKey(session) ?? session.UserAgent ?? "unknown");

    /// <summary>Every key this class writes, for a test to enumerate.</summary>
    public static IReadOnlyList<string> Keys = new[] { FingerprintKeyVar, TimeZoneOffsetVar, PayloadVar };
}
