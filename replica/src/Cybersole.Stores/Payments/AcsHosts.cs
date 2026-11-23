using System;
using System.Collections.Generic;
using System.Linq;
using Cybersole.Http;

namespace Cybersole.Stores.Payments;

/// <summary>
/// The issuer ACS hosts the 3-D Secure dispatcher recognises, decoded from <c>0x1408A34F0</c> (R1303).
///
/// <para>
/// That function opens with a category-<c>"3DS"</c> log of <c>"Starting 3DS: " + host</c>
/// (0x146AECBA0 and 0x146E9A430), overwrites the transport profile field with the frozen
/// <c>"chrome_131"</c> (0x146FC83D8), switches on the host string's length and content, builds the
/// matching per-issuer handler, then writes the previous profile back from the two slots it saved it
/// in. So the hop to an issuer is a temporary re-fingerprint, and knowing the host is what decides
/// whether the hop is one it understands.
/// </para>
///
/// <para>
/// The names below are the frozen <c>System.String</c> objects that switch compares against, read one
/// by one (<c>off_146F6D6A8</c> is <c>acs.apata.io</c>, <c>off_14717E440</c> is
/// <c>verifiedbyvisa.acs.touchtechpayments.com</c>, and so on). The length cases the decompiler prints
/// (0xC, 0xD, 0xE, 0xF, 0x10 … 0x28) are the lengths of these names — eighteen of them, several
/// carrying two hosts.
/// </para>
///
/// <para>
/// <b>Verified (<c>0x1408A34F0</c>)</b>: the switch dispatches these twenty-eight hosts across nineteen
/// headless issuer clusters (<see cref="CheckoutComAcsHandlers"/>, clusters <c>01_apata</c> through
/// <c>19_cardinal</c>) plus one shared interactive verification fallback (<c>20_fallback</c>,
/// <c>0x144BDBD70</c>) for unrecognised hosts or runtime escalations (OTP, Monese, Amex 3DS2, etc.).
/// </para>
///
/// <para>
/// <b>Remaining cross-cutting unknowns</b>: caller-side <c>AllowAutoRedirect</c> (<c>client+80</c>)
/// initialization before entering <c>0x1408A34F0</c>; Capital One's external signal <c>0x140F97CA0</c>;
/// Marqeta's exact poll delay helper <c>0x140F9FBB0</c>; Cardinal's exact boxed <c>Screen.Ratio</c>
/// constant (<c>sub_141AAF850</c>); Soldo's downstream <c>Content-Type</c> wire binding; and the
/// interactive WebView controller (<c>0x1408A7560</c>/<c>0x1408A7EE0</c>).
/// </para>
/// </summary>
public static class AcsHosts
{
    /// <summary>The profile the image re-fingerprints to for the issuer hop (0x146FC83D8), verbatim.</summary>
    public const string TransportProfileName = "chrome_131";

    /// <summary>The log category and prefix the dispatcher opens with (0x146AECBA0, 0x146E9A430).</summary>
    public const string LogCategory = "3DS";
    public const string LogPrefix = "Starting 3DS: ";

    /// <summary>
    /// Every host <c>0x1408A34F0</c> compares against, in name order. Two of them are the <c>-a</c> and
    /// <c>-b</c> halves of one Enfuce deployment, four are Modirum MTPS/3DS pairs, and
    /// <c>verifiedbyvisa.acs.touchtechpayments.com</c> (40 characters) is the longest string the switch
    /// has a case for.
    /// </summary>
    public static IReadOnlyList<string> Known { get; } = new[]
    {
        "3ds-a.live.ext.prod.enfuce.com",
        "3ds-b.live.ext.prod.enfuce.com",
        "3ds.soldo.com",
        "3dsecure.mbank.cz",
        "3dsecure.starlingbank.com",
        "3dsecure.zen.com",
        "acs-challenge.apata.io",
        "acs-safekey.americanexpress.com",
        "acs.apata.io",
        "acs.capitalone.com",
        "acs.revolut.com",
        "acs.touch.tech",
        "acs1.3ds.modirum.com",
        "acs1.mpts.modirum.com",
        "acs2.3ds.modirum.com",
        "acs2.edb.com",
        "acs2.mpts.modirum.com",
        "api.id.mastercard.bunq.com",
        "api.secure-code.bunq.com",
        "authentication-acs.marqeta.com",
        "authentication.cardinalcommerce.com",
        "cacs-v2.icard.com",
        "cacs.icard.com",
        "idcheck.acs.touchtechpayments.com",
        "poseidon.revolut.com",
        "secure4.arcot.com",
        "verifiedbyvisa.acs.touchtechpayments.com",
        "verify.monzo.com",
    };

    private static readonly HashSet<string> Lookup =
        new(Known, StringComparer.OrdinalIgnoreCase);

    /// <summary>
    /// The host part of a URL, or the argument itself when it is already a host: scheme, user info,
    /// port, path, query, fragment and a trailing root dot are all dropped, and the answer is
    /// lower-cased. The switch compares lower-case literals, and a challenge action URL arrives in
    /// whatever case the issuer wrote.
    /// </summary>
    public static string HostOf(string? urlOrHost)
    {
        var text = (urlOrHost ?? string.Empty).Trim();
        if (text.Length == 0) return string.Empty;

        var scheme = text.IndexOf("://", StringComparison.Ordinal);
        if (scheme >= 0) text = text[(scheme + 3)..];

        var cut = text.IndexOfAny(new[] { '/', '?', '#' });
        if (cut >= 0) text = text[..cut];

        var at = text.LastIndexOf('@');
        if (at >= 0) text = text[(at + 1)..];

        var colon = text.IndexOf(':');
        if (colon >= 0) text = text[..colon];

        return text.TrimEnd('.').ToLowerInvariant();
    }

    /// <summary>Whether <c>0x1408A34F0</c> has a case for this hop's host.</summary>
    public static bool IsKnown(string? urlOrHost) => Lookup.Contains(HostOf(urlOrHost));

    /// <summary>
    /// The profile a hop to this host runs under: the image's <c>chrome_131</c> for a host it
    /// recognises, and the profile the request already had for one it does not — the dispatcher only
    /// overwrites the field inside the branches, and restores it either way.
    /// </summary>
    public static TlsProfile ProfileFor(string? urlOrHost, TlsProfile current) =>
        IsKnown(urlOrHost) ? TlsProfile.ByName(TransportProfileName) : current;

    /// <summary>The log line the dispatcher opens with, so a hop reads the same in the event list.</summary>
    public static string Describe(string? urlOrHost) => LogPrefix + HostOf(urlOrHost);

    /// <summary>
    /// The length cases the switch carries, kept with the names they belong to so the two can be
    /// re-derived: eighteen lengths from 12 to 40, which is what the decompiler's <c>case</c> values
    /// say, and what a name added to <see cref="Known"/> must land on to be reachable at all.
    /// </summary>
    public static IReadOnlyList<int> CaseLengths { get; } =
        Known.Select(h => h.Length).Distinct().OrderBy(n => n).ToList();
}
