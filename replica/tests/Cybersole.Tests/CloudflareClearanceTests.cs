using System.Threading.Tasks;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 140: the middle of the Cloudflare path — detect the wall, run the ladder, store the
/// clearance.
///
/// <para>
/// <see cref="StoreFlow.DetectAsync"/> named the vendor and <c>AntiBotProtocol</c> knew the cookie, but
/// nothing asked the strategy for a token or wrote the answer back. This is the same gap R133/R134
/// found on the payment side, and the same fix: one place that reads what the session recorded and one
/// that writes what the next request needs.
/// </para>
///
/// <para>
/// A live fact is recorded with it: <c>cf-solver.cybersole.io</c> answered <b>401</b> when probed, so
/// the host exists and the protocol wants credentials — more than the Kasada road has, whose host is
/// unknown.
/// </para>
/// </summary>
public sealed class CloudflareClearanceTests
{
    private readonly ITestOutputHelper _out;

    public CloudflareClearanceTests(ITestOutputHelper output) => _out = output;

    private static FlowContext Context(string vendor)
    {
        // FlowContext is built by the runner, so the test builds the smallest one it can and sets the
        // two things the helper reads: the vendor the detector recorded, and a URL to solve for.
        var context = new FlowContext { Url = "https://example.test/", Http = null! };
        context.Session.Vars["antibot"] = vendor;
        return context;
    }

    /// <summary>A Cloudflare wall gets a clearance, stored as a var and as the cookie.</summary>
    [Fact]
    public async Task AClearanceIsStoredInBothPlaces()
    {
        var c = Context("cloudflare");
        var runner = CloudflareStrategyRunner.Default(
            serviceCall: (_, _, _) => Task.FromResult<string?>("cf-token"),
            inBotSolve: (_, _) => Task.FromResult<string?>(null));

        var outcome = await CloudflareClearance.ApplyAsync(c, runner, "https://example.test/");

        Assert.True(outcome.Ok);
        Assert.Equal("cf-token", CloudflareClearance.Clearance(c.Session));
        Assert.True(c.Session.Cookies.ContainsKey("cf_clearance"));
        Assert.Equal("cf-token", c.Session.Cookies["cf_clearance"]);

        _out.WriteLine(CloudflareClearance.SolverStatus(c.Session));
    }

    /// <summary>A refusal stores the sentence and no cookie — the flow keeps going.</summary>
    [Fact]
    public async Task ARefusalStoresTheSentenceAndNoCookie()
    {
        var c = Context("cloudflare");
        var runner = CloudflareStrategyRunner.Default();

        var outcome = await CloudflareClearance.ApplyAsync(c, runner, "https://example.test/");

        Assert.True(outcome.Ok);
        Assert.Equal(CloudflareStrategy.RefusedMessage, CloudflareClearance.SolverStatus(c.Session));
        Assert.Null(CloudflareClearance.Clearance(c.Session));
        Assert.False(c.Session.Cookies.ContainsKey("cf_clearance"));
    }

    /// <summary>Another vendor's wall is left alone.</summary>
    [Fact]
    public async Task AnotherVendorsWallIsLeftAlone()
    {
        foreach (var vendor in new[] { "kasada", "datadome", "none", "" })
        {
            var c = Context(vendor);
            var runner = CloudflareStrategyRunner.Default(
                serviceCall: (_, _, _) => Task.FromResult<string?>("should-not-be-asked"),
                inBotSolve: (_, _) => Task.FromResult<string?>(null));

            await CloudflareClearance.ApplyAsync(c, runner, "https://example.test/");

            Assert.Null(CloudflareClearance.SolverStatus(c.Session));
            Assert.Null(CloudflareClearance.Clearance(c.Session));
        }

        _out.WriteLine("only the Cloudflare wall is this helper's business");
    }

    /// <summary>The observed 401 is recorded, with what it means.</summary>
    [Fact]
    public void TheObserved401IsRecorded()
    {
        Assert.Equal(401, CloudflareClearance.ServiceStatusObserved);
        Assert.Contains("401", CloudflareClearance.ServiceStatusMeaning);
        Assert.Contains("host is real", CloudflareClearance.ServiceStatusMeaning);
        Assert.Contains("credentials", CloudflareClearance.ServiceStatusMeaning);

        _out.WriteLine(CloudflareClearance.ServiceStatusMeaning);
    }

    /// <summary>Detection and storage were both present before this round — the call was not.</summary>
    [Fact]
    public void TheHelperUsesTheTwoPiecesThatAlreadyExisted()
    {
        // detection: the vendor var StoreFlow.DetectAsync writes
        Assert.Equal("antibot", CloudflareClearance.VendorVar);

        // storage: the cookie name AntiBotProtocol already carried
        var cookies = AntiBotProtocol.CookiesFor("Cloudflare");
        Assert.NotNull(cookies);
        Assert.Contains(CloudflareStrategy.ClearanceCookie, cookies!);

        Assert.Equal(2, CloudflareClearance.Keys.Count);
    }
}
