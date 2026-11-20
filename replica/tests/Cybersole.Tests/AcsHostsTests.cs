using System.Linq;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1303: the issuer ACS host table decoded from <c>0x1408A34F0</c>.
///
/// <para>
/// The strongest assertion here is the one that needs no trust: the switch's eighteen <c>case</c> values
/// are string <i>lengths</i> (0xC, 0xD, 0xE, 0xF, 0x10, 0x11, 0x12, 0x14, 0x15, 0x16, 0x18, 0x19, 0x1A,
/// 0x1E, 0x1F, 0x21, 0x23, 0x28), and the names were read separately out of the frozen string objects
/// the same function compares against. Two independent sources agree on the same eighteen lengths only if
/// both decodes are right, so <see cref="TheCaseLengthsAreTheOnesTheDecompilerPrinted"/> is the
/// cross-check rather than a restatement.
/// </para>
/// </summary>
public sealed class AcsHostsTests
{
    [Fact]
    public void TheTableHoldsTheHostsTheSwitchCompares()
    {
        Assert.Equal(28, AcsHosts.Known.Count);
        Assert.Equal(AcsHosts.Known.Count, AcsHosts.Known.Distinct().Count());

        // The first and last names the switch can reach, plus the families that come in pairs.
        Assert.Contains("acs.apata.io", AcsHosts.Known);                       // 0x146F6D6A8, 12 chars
        Assert.Contains("verifiedbyvisa.acs.touchtechpayments.com", AcsHosts.Known); // 0x14717E440, 40
        Assert.Contains("3ds-a.live.ext.prod.enfuce.com", AcsHosts.Known);
        Assert.Contains("3ds-b.live.ext.prod.enfuce.com", AcsHosts.Known);
        Assert.Contains("acs1.3ds.modirum.com", AcsHosts.Known);
        Assert.Contains("acs2.mpts.modirum.com", AcsHosts.Known);
        Assert.Contains("authentication.cardinalcommerce.com", AcsHosts.Known);
        Assert.Contains("secure4.arcot.com", AcsHosts.Known);
    }

    [Fact]
    public void TheCaseLengthsAreTheOnesTheDecompilerPrinted()
    {
        var printed = new[] { 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 24, 25, 26, 30, 31, 33, 35, 40 };
        Assert.Equal(printed, AcsHosts.CaseLengths);

        // Every name has to land on a case, or 0x1408A34F0 would fall through to the generic handler.
        foreach (var host in AcsHosts.Known)
            Assert.Contains(host.Length, printed);
    }

    [Fact]
    public void HostOfKeepsOnlyTheHost()
    {
        Assert.Equal("acs.apata.io", AcsHosts.HostOf("https://acs.apata.io/v1/challenge?x=1"));
        Assert.Equal("acs.apata.io", AcsHosts.HostOf("HTTPS://ACS.APATA.IO"));
        Assert.Equal("acs.apata.io", AcsHosts.HostOf("acs.apata.io:443"));
        Assert.Equal("acs.apata.io", AcsHosts.HostOf("acs.apata.io."));
        Assert.Equal("acs.apata.io", AcsHosts.HostOf("https://user:pw@acs.apata.io/x"));
        Assert.Equal(string.Empty, AcsHosts.HostOf(null));
    }

    [Fact]
    public void AKnownHostRunsOnTheImagesProfileAndAnUnknownOneKeepsWhatsThere()
    {
        Assert.Equal("chrome_131", AcsHosts.TransportProfileName);
        Assert.Same(TlsProfile.Chrome, AcsHosts.ProfileFor("https://acs.apata.io/x", TlsProfile.Firefox));
        Assert.Same(TlsProfile.Firefox, AcsHosts.ProfileFor("https://example.test/x", TlsProfile.Firefox));
    }

    [Fact]
    public void TheLogLineIsTheOneTheDispatcherWrites()
    {
        Assert.Equal("Starting 3DS: acs.revolut.com",
            AcsHosts.Describe("https://acs.revolut.com/acs/challenge"));
        Assert.Equal("3DS", AcsHosts.LogCategory);
    }

    /// <summary>
    /// The emit happens before the host switch in the image, so it happens even when the page cannot be
    /// read: the event names the hop whether or not the hop is one the dispatcher understands.
    /// </summary>
    [Fact]
    public async Task TheHopIsLoggedBeforeThePageIsEvenFetched()
    {
        using var server = new TinyServer((_, _) => (404, "nope"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/checkout" };

        var result = await new CheckoutComGateway()
            .ResolveEswThreeDsAsync(ctx, server.BaseUrl + "/challenge", "{}", default);

        Assert.False(result.Ok);
        Assert.Contains(ctx.Events,
            e => e.Name == "Starting 3DS: 127.0.0.1" && e.Type == "3DS");
        Assert.Equal("127.0.0.1", ctx.Session.Vars["checkoutcom.acsHost"]);
        Assert.Equal("false", ctx.Session.Vars["checkoutcom.acsKnown"]);
    }
}
