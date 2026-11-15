using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 88: the seven Nike identifiers the image carries, and the four headers the replica never
/// sent.
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
/// docs/NIKE_PARITY.md said "four Nike headers unset"; the image says four headers, one Kasada
/// version header and two cookies. The replica sent none of the seven.
/// </para>
///
/// <para>
/// The mechanism sends a header only when the flow has actually observed its value — no defaults are
/// invented. That distinction matters: a header with a made-up value tells Kasada the client is
/// lying, which is worse than a client that simply does not send it.
/// </para>
/// </summary>
public sealed class NikeHeaderTests
{
    private readonly ITestOutputHelper _out;

    public NikeHeaderTests(ITestOutputHelper output) => _out = output;

    /// <summary>Seven identifiers, spelled exactly as the image spells them.</summary>
    [Fact]
    public void TheImageCarriesSevenIdentifiers()
    {
        _out.WriteLine(string.Join(" | ", NikeHeaders.All));

        Assert.Equal(7, NikeHeaders.All.Count);
        Assert.Equal(new[]
        {
            "NIKE-GS",
            "NIKE-SESSION",
            "Nike-Kasada-Version",
            "nike-api-caller-id",
            "x-nike-ux-id",
            "x-nike-visitid",
            "x-nike-visitorid",
        }, NikeHeaders.All);
    }

    /// <summary>Five of them go out as headers; the other two are cookie names.</summary>
    [Fact]
    public void FiveAreHeadersAndTwoAreCookies()
    {
        _out.WriteLine("headers: " + string.Join(", ", NikeHeaders.FromSessionVar.Values));
        _out.WriteLine("cookies: " + string.Join(", ", NikeHeaders.Cookies));

        Assert.Equal(5, NikeHeaders.FromSessionVar.Count);
        Assert.Equal(2, NikeHeaders.Cookies.Count);

        Assert.Contains(NikeHeaders.ApiCallerId, NikeHeaders.FromSessionVar.Values);
        Assert.Contains(NikeHeaders.VisitorId, NikeHeaders.FromSessionVar.Values);
        Assert.Contains(NikeHeaders.Session, NikeHeaders.Cookies);
        Assert.Contains(NikeHeaders.Gs, NikeHeaders.Cookies);

        // the union is the seven, with no overlap
        var union = NikeHeaders.FromSessionVar.Values.Concat(NikeHeaders.Cookies).ToList();
        Assert.Equal(7, union.Count);
        Assert.Equal(7, union.Distinct().Count());
    }

    /// <summary>Only known values are applied — nothing is defaulted.</summary>
    [Fact]
    public void OnlyKnownValuesReachTheHeaders()
    {
        var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

        // nothing known
        Assert.Equal(0, NikeHeaders.Apply(new Dictionary<string, string>(), headers));
        Assert.Empty(headers);

        // two known
        var vars = new Dictionary<string, string>
        {
            ["nike.apiCallerId"] = "abc-123",
            ["nike.visitorId"] = "9f9f",
            ["nike.uxId"] = "",          // empty means "not observed"
        };

        var applied = NikeHeaders.Apply(vars, headers);

        _out.WriteLine($"applied={applied} headers={string.Join(",", headers.Keys)}");

        Assert.Equal(2, applied);
        Assert.Equal("abc-123", headers["nike-api-caller-id"]);
        Assert.Equal("9f9f", headers["x-nike-visitorid"]);
        Assert.False(headers.ContainsKey("x-nike-ux-id"));
    }

    /// <summary>A null session-var bag is not an error; it is simply nothing to send.</summary>
    [Fact]
    public void ANullBagAppliesNothing()
    {
        var headers = new Dictionary<string, string>();
        Assert.Equal(0, NikeHeaders.Apply(null, headers));
        Assert.Empty(headers);
    }
}
