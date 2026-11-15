using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The pruning list and the credentials shim, both read verbatim in R163 — and the correction the first one
/// forces on R156.
///
/// <para>
/// The image's mobile script says, right after it installs the navigator:
/// </para>
///
/// <code>
/// // Actually removed, not hidden behind a trap. Blink exposes a pile of interfaces WebKit has
/// // never shipped -- userAgentData, getBattery, connection, bluetooth, usb, hid, serial, xr,
/// // deviceMemory -- and browserleaks reads every one of them straight off navigator.
/// NAV_PRUNE …
/// </code>
///
/// <para>
/// <b>R156 installed <c>connection</c> for every profile.</b> For an Apple profile that is backwards: the member
/// has to be <i>absent</i>, because WebKit never shipped it. The desktop payload sample does read
/// <c>navigator.connection</c>, so the correct rule is the one this session keeps rediscovering — the same member is
/// installed for one claim and deleted for another.
/// </para>
///
/// <para>
/// The credentials shim is the other half: four entries with the triple, <c>get</c>/<c>create</c> at length 1,
/// <c>preventSilentAccess</c> at 0, <c>store</c> at 1. Their <c>src</c> is a real WebAuthn implementation — a virtual
/// authenticator answering a 3-D Secure challenge — which this workspace has <b>not</b> built. The shape is recorded;
/// the implementation is an open item, stated as one.
/// </para>
/// </summary>
public static class NavPrune
{
    /// <summary>
    /// The Blink-only members an Apple profile must not expose — kept as the <i>reason</i> the allowlist exists,
    /// and as the names to check in a test, even though the mechanism is now whitelist-based (R169).
    /// </summary>
    public static readonly IReadOnlyList<string> BlinkOnly = new[]
    {
        "userAgentData", "getBattery", "connection", "bluetooth", "usb", "hid", "serial", "xr",
        "deviceMemory",
    };

    /// <summary>True when the profile's claim requires pruning.</summary>
    public static bool ShouldPrune(string? userAgent) => MobileSurface.IsAppleUserAgent(userAgent);

    /// <summary>
    /// The allowlist the image's <c>NAV_PRUNE</c> deletes against: every own name on
    /// <c>Navigator.prototype</c> that is <b>not</b> in it is removed (R169).
    ///
    /// <para>
    /// R163 wrote this as a nine-name blacklist. The capture is a whitelist — <c>NAV_KEYS</c> has fifty-one entries and
    /// the loop is <c>if (!NAV_KEYS.has(key) &amp;&amp; key !== 'constructor') delete proto[key]</c>. The difference
    /// matters: a blacklist has to be extended every time the engine ships a new interface, and a whitelist cannot fall
    /// behind.
    /// </para>
    /// </summary>
    public static IReadOnlyList<string> AllowList =>
        MobileNavigator.NavOrder.Append("plugins").Append("mimeTypes").ToList();

    /// <summary>
    /// Delete every own property of the navigator prototype that is not on the allowlist. Deleting is the point: a trap
    /// that throws is still a property, and <c>for in</c> still walks it.
    /// </summary>
    public static string BodyJs()
    {
        var allowed = string.Join(", ", AllowList.Select(n => "'" + n + "'"));

        return """
               // ---- pruning (R163, whitelist since R169) ----------------------------------------
               // Deleted, not trapped: browserleaks reads these straight off navigator, and a property that
               // answers "no" is not the same as a property that is not there. The image prunes against an
               // allowlist, so an interface Blink ships tomorrow is removed without anyone editing this list.
               try {
                 const keep = new Set([__ALLOWED__]);
                 const sweep = (target) => {
                   if (!target) return;
                   // R187: the reference captured at the top (`nativeOwnNames`, 0x03d20953 in the target), not the
                   // live builtin — the key-order wrapper is installed above this prune in the target's own script.
                   const own = G.__nativeOwnNames || Object.getOwnPropertyNames;
                   own(target).forEach((key) => {
                     if (!keep.has(key) && key !== 'constructor') {
                       try { delete target[key]; } catch (e) {}
                     }
                   });
                 };

                 // The image sweeps the prototype, because it installs everything there. This replica's own
                 // scripts still put a few members on the instance (deviceMemory among them), so the sweep
                 // runs over both — a superset of the same rule, and the measurement says why: without it an
                 // iPhone profile still answered navigator.deviceMemory.
                 sweep(G.Navigator && G.Navigator.prototype);
                 sweep(G.navigator);
               } catch (e) {}
               """.Replace("__ALLOWED__", allowed);
    }

    /// <summary>The credentials shim's four entries, exactly as the image records them.</summary>
    public static readonly IReadOnlyList<CredentialsShim> Credentials = new[]
    {
        new CredentialsShim("get", 1, false),
        new CredentialsShim("create", 1, false),
        new CredentialsShim("preventSilentAccess", 0, false),
        new CredentialsShim("store", 1, false),
    };

    /// <summary>One shim entry: what it is called, its arity, and whether this workspace has it.</summary>
    public sealed record CredentialsShim(string Name, int Length, bool Implemented);

    /// <summary>
    /// The open item, in the image's own terms: its <c>get</c> body calls <c>he(e, true)</c> after a challenge, and its
    /// <c>create</c> calls <c>ge(e)</c> — a virtual authenticator. Building that is a separate piece of work.
    /// </summary>
    public const string CredentialsOpenItem =
        "the image's credentials.get/create are a working WebAuthn shim (virtual authenticator for 3-D Secure "
        + "challenges); this workspace records the shape and has not built the authenticator";

    /// <summary>
    /// The <c>audioSession</c> shim, verbatim from the image (R169).
    ///
    /// <code>
    /// // iOS exposes navigator.audioSession, which Blink has no equivalent for, so the prune above cannot restore
    /// // it -- it was never there. hCaptcha serialises each navigator member with JSON.stringify, and on the device
    /// // this one comes back as {} exactly like gpu and clipboard do, so a bare object with the right toStringTag
    /// // reproduces what it reads.
    /// const session = {};
    /// Object.defineProperty(session, Symbol.toStringTag, { value: 'AudioSession', configurable: true });
    /// Object.defineProperty(session, 'type', { value: 'auto', enumerable: false, configurable: true });
    /// value(proto, 'audioSession', session);
    /// </code>
    ///
    /// <para>
    /// A shim does not have to simulate the API; it has to reproduce what the reader serialises. hCaptcha calls
    /// <c>JSON.stringify</c> on each member, and an object with a <c>toStringTag</c> and no enumerable data stringifies to
    /// <c>{}</c> — which is what a real iPhone answers for this member, and for <c>gpu</c> and <c>clipboard</c> too.
    /// </para>
    /// </summary>
    public static string AudioSessionBodyJs()
    {
        return """
               // ---- audioSession (R169) --------------------------------------------------------
               // Not a simulation: JSON.stringify on a bare object with the right toStringTag and no enumerable
               // data answers "{}", which is what the device answers for this member.
               try {
                 const proto = G.Navigator && G.Navigator.prototype;
                 if (proto && !('audioSession' in proto)) {
                   const session = {};
                   Object.defineProperty(session, Symbol.toStringTag,
                     { value: 'AudioSession', configurable: true });
                   Object.defineProperty(session, 'type',
                     { value: 'auto', enumerable: false, configurable: true });
                   Object.defineProperty(proto, 'audioSession',
                     { value: session, writable: true, configurable: true, enumerable: true });
                 }
               } catch (e) {}
               """;
    }

    /// <summary>The tag and the default type the shim carries.</summary>
    public const string AudioSessionTag = "AudioSession";

    /// <inheritdoc cref="AudioSessionTag"/>
    public const string AudioSessionType = "auto";

    /// <summary>
    /// <c>navigator.plugins</c> and <c>mimeTypes</c> are left native, and the image says why: Blink's lists are the
    /// spec's five PDF viewers and two PDF mime types, which is exactly what the iPhone reports (R169).
    /// </summary>
    public const string PluginsAreNative =
        "Blink's lists are the spec's five PDF viewers and two PDF mime types — the same five internal-pdf-viewer "
        + "entries and the same two lengths an iPhone reports; an override used to empty both, on the mistaken belief "
        + "that WebKit's lists are empty, so every bot payload carried plugins: []";

    /// <summary>The lengths a device collector reads off the native lists.</summary>
    public const int NativePluginCount = 5;

    /// <inheritdoc cref="NativePluginCount"/>
    public const int NativeMimeTypeCount = 2;

    /// <summary>The shape rule this round adds.</summary>
    public const string Rule =
        "the same member is installed for one claim and deleted for another: a desktop profile reads "
        + "navigator.connection, an iPhone profile must not have it at all";
}
