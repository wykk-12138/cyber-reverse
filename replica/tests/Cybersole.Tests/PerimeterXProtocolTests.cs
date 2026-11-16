using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// PerimeterX, the seventh anti-bot vendor, and the comment that had asserted its cookie was absent.
///
/// <para>
/// R944. Going to the risk-control priority, all four remaining vendors turned out to be present in the image — Kasada,
/// DataDome, PerimeterX and Queue-it — and six of the seven were already covered by AntiBotProtocol. PerimeterX was the
/// exception, and the reason was written down: the image names the vendor and a token but no _px cookie, so it was
/// "deliberately absent rather than filled in from memory". One search disproved that. _px3 is present, one match. The
/// comment had asserted an absence it never checked, and asserting it kept anyone from looking.
/// </para>
/// </summary>
public class PerimeterXProtocolTests
{
    /// <summary>
    /// Five vendors have a cookie family, and PerimeterX is now one of them. Not seven: Queue-it and TrustDecision are
    /// covered by other means -- join routes for the first, script names for the second -- so counting them here would be
    /// asserting a cookie they do not have.
    /// </summary>
    [Fact]
    public void FiveVendorsHaveCookiesAndPerimeterXIsOne()
    {
        var vendors = AntiBotProtocol.VendorsWithCookies();

        Assert.Equal(5, vendors.Count);
        Assert.Contains("PerimeterX", vendors);
        Assert.Contains("Kasada", vendors);
        Assert.Contains("Cloudflare", vendors);
        Assert.Contains("DataDome", vendors);
        Assert.Contains("Akamai", vendors);
    }

    /// <summary>The cookie the image carries, which the old comment said did not exist.</summary>
    [Fact]
    public void TheCookieIsPx3()
    {
        Assert.Equal("_px3", AntiBotProtocol.PerimeterX.Cookie);
        Assert.Contains("_px3", AntiBotProtocol.CookiesFor("PerimeterX")!);
    }

    /// <summary>
    /// Two visitor identifiers differing by one underscore. Kept apart because the image has both and nothing says they
    /// hold the same value -- collapsing them would be a guess dressed as tidying.
    /// </summary>
    [Fact]
    public void TheTwoVisitorIdsAreKeptApart()
    {
        var ids = AntiBotProtocol.PerimeterX.VisitorIds;

        Assert.Equal(new[] { "__pxvid", "_pxvid" }, ids);
        Assert.Equal(2, ids.Distinct().Count());
        Assert.Contains("__pxvid", AntiBotProtocol.CookiesFor("PerimeterX")!);
        Assert.Contains("_pxvid", AntiBotProtocol.CookiesFor("PerimeterX")!);
    }

    /// <summary>The header and handler names, in the capitalisation the image carries.</summary>
    [Fact]
    public void TheHeaderAndHandlerKeepTheirCapitalisation()
    {
        Assert.Equal("PerimeterX-Token", AntiBotProtocol.PerimeterX.TokenHeader);
        Assert.Equal("PerimeterXHandler", AntiBotProtocol.PerimeterX.Handler);
    }

    /// <summary>
    /// Two message strings are recorded verbatim and not interpreted. The rotating-proxy one is the original's advice,
    /// which is a fact about the original rather than about the vendor's protocol.
    /// </summary>
    [Fact]
    public void TheMessagesAreVerbatim()
    {
        var messages = AntiBotProtocol.PerimeterX.Messages;

        Assert.Contains("Solving PerimeterX", messages);
        Assert.Contains("PerimeterX block (Rotating proxy)", messages);
    }

    /// <summary>
    /// The correction itself is pinned: the source must no longer claim PerimeterX lacks a cookie, and must say why the
    /// claim survived.
    /// </summary>
    [Fact]
    public void TheFalseAbsenceClaimIsGone()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "AntiBotProtocol.cs"));

        Assert.DoesNotContain("PerimeterX\n    /// is the exception", doc);
        Assert.DoesNotContain("but no <c>_px</c> cookie", doc);
        Assert.Contains("asserted an absence it had never checked", doc);
    }

    /// <summary>The other six are untouched, so the addition did not disturb what was already verified.</summary>
    [Fact]
    public void TheOtherSixAreUnchanged()
    {
        Assert.Equal(new[] { "_abck", "ak_bmsc" }, AntiBotProtocol.CookiesFor("Akamai"));
        Assert.Equal(new[] { "datadome" }, AntiBotProtocol.CookiesFor("DataDome"));
        Assert.Equal(new[] { "cf_clearance" }, AntiBotProtocol.CookiesFor("Cloudflare"));
        Assert.Equal(new[] { "kpsdk" }, AntiBotProtocol.CookiesFor("Kasada"));
        Assert.Null(AntiBotProtocol.CookiesFor("NoSuchVendor"));
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(System.IO.Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}