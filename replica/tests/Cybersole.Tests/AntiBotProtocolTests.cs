using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 106: the protocol layer — what the image actually puts on the wire for each anti-bot
/// system.
///
/// <para>
/// R105 named the vendors. This names the headers and cookies: nine <c>x-kpsdk-*</c> Kasada headers,
/// the Akamai / DataDome / Cloudflare / Kasada cookie families, Queue-it's hosts and its
/// <c>queue-it-set-cookie</c>, and TrustDecision's two scripts with their per-region fingerprint ids.
/// </para>
///
/// <para>
/// PerimeterX is the deliberate gap: the image names the vendor and a <c>PerimeterX-Token</c> header,
/// but no <c>_px</c> cookie anywhere. Recording nothing for it is more honest than filling it from
/// what PerimeterX usually sets — this session has already been burned five times by exactly that
/// habit.
/// </para>
/// </summary>
public sealed class AntiBotProtocolTests
{
    private readonly ITestOutputHelper _out;

    public AntiBotProtocolTests(ITestOutputHelper output) => _out = output;

    /// <summary>Nine Kasada headers, all distinct, all prefixed.</summary>
    [Fact]
    public void KasadaHasNineHeaders()
    {
        _out.WriteLine(string.Join(" ", AntiBotProtocol.KasadaHeaders));

        Assert.Equal(9, AntiBotProtocol.KasadaHeaders.Count);
        Assert.Equal(9, AntiBotProtocol.KasadaHeaders.Distinct().Count());
        Assert.All(AntiBotProtocol.KasadaHeaders, h => Assert.StartsWith("x-kpsdk-", h));

        Assert.True(AntiBotProtocol.IsKasadaHeader("x-kpsdk-ct"));
        Assert.False(AntiBotProtocol.IsKasadaHeader("x-kpsdk-zz"));
        Assert.False(AntiBotProtocol.IsKasadaHeader(null));
    }

    /// <summary>Four vendors have a cookie family; PerimeterX deliberately does not.</summary>
    [Fact]
    public void SixVendorsHaveCookieFamilies()   // R944: PerimeterX is the fifth; Queue-it and TrustDecision are covered by routes and scripts, not cookies
    {
        var vendors = AntiBotProtocol.VendorsWithCookies().OrderBy(v => v).ToList();
        _out.WriteLine(string.Join(", ", vendors));

        // R1052: six -- Vercel's _vcrcs joins the cookie families.
        Assert.Equal(6, vendors.Count);
        Assert.Equal(new[] { "Akamai", "Cloudflare", "DataDome", "Kasada", "PerimeterX", "Vercel" }, vendors);   // R944

        Assert.Equal(new[] { "_abck", "ak_bmsc" }, AntiBotProtocol.CookiesFor("Akamai"));
        Assert.Equal(new[] { "datadome" }, AntiBotProtocol.CookiesFor("DataDome"));
        Assert.Equal(new[] { "cf_clearance" }, AntiBotProtocol.CookiesFor("Cloudflare"));
        Assert.Equal(new[] { "kpsdk" }, AntiBotProtocol.CookiesFor("Kasada"));

        // R944: these two lines asserted that the image names no cookie for PerimeterX, and it does -- _px3. This was
        // the false absence that used to be recorded three times overTests, and here. Three copies is why it was
        // never checked; a claim repeated looks like a fact corroborated.
        Assert.True(AntiBotVendors.Knows("PerimeterX"));
        Assert.NotNull(AntiBotProtocol.CookiesFor("PerimeterX"));
        Assert.Contains("_px3", AntiBotProtocol.CookiesFor("PerimeterX")!);
    }

    /// <summary>Queue-it's hosts and the cookie it sets.</summary>
    [Fact]
    public void QueueItHostsAndCookieAreRecorded()
    {
        _out.WriteLine(string.Join(", ", AntiBotProtocol.QueueIt));

        Assert.Contains("queue-it.net", AntiBotProtocol.QueueIt);
        Assert.Contains(".queue-it.net", AntiBotProtocol.QueueIt);
        Assert.Contains("panini.queue-it.net", AntiBotProtocol.QueueIt);
        Assert.Contains("queue-it-set-cookie", AntiBotProtocol.QueueIt);
        Assert.Equal(4, AntiBotProtocol.QueueIt.Count);
    }

    /// <summary>TrustDecision's two scripts and two per-region ids.</summary>
    [Fact]
    public void TrustDecisionScriptsAndRegionsAreRecorded()
    {
        _out.WriteLine(string.Join(", ", AntiBotProtocol.TrustDecisionScripts));

        Assert.Contains("trustdevice.js", AntiBotProtocol.TrustDecisionScripts);
        Assert.Contains("trustdevice-botd.js", AntiBotProtocol.TrustDecisionScripts);
        Assert.Contains("tdfp/de/e6058883d38c943d575ef00c0bc08768/fm.js",
            AntiBotProtocol.TrustDecisionScripts);
        Assert.Contains("tdfp/sg/755d8ba834619d71d88664d0a36c81ce/fm.js",
            AntiBotProtocol.TrustDecisionScripts);

        // the region ids are hashes, not versions — two distinct ones
        var regions = AntiBotProtocol.TrustDecisionScripts
            .Where(s => s.Contains("/fm.js", System.StringComparison.Ordinal))
            .Select(s => s.Split('/')[1])
            .Distinct()
            .ToList();
        Assert.Equal(new[] { "de", "sg" }, regions);
    }

    /// <summary>
    /// The protocol layer only covers vendors R105 already established — it never invents a vendor.
    /// </summary>
    [Fact]
    public void EveryProtocolVendorIsAKnownVendor()
    {
        foreach (var vendor in AntiBotProtocol.VendorsWithCookies())
            Assert.True(AntiBotVendors.Knows(vendor), vendor);

        _out.WriteLine($"{AntiBotProtocol.VendorsWithCookies().Count} of " +
                       $"{AntiBotVendors.All.Count} vendors have a cookie family");
    }
}
