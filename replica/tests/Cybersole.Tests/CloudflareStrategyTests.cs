using System.Threading;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 139: Cloudflare's ladder, which the image states in one sentence —
/// <c>Cloudflare solver refused the token, solving in-bot</c> — and which turns out to be the same
/// strategy as Kasada's.
///
/// <para>
/// Service first, then in-bot. A refusal is not an error: it is the reason to fall through, so the
/// runner reports the sentence as a status rather than failing. The service host exists
/// (<c>cf-solver.cybersole.io</c>, from the fifteen), the protocol does not, so the call is injected.
/// </para>
/// </summary>
public sealed class CloudflareStrategyTests
{
    private readonly ITestOutputHelper _out;

    public CloudflareStrategyTests(ITestOutputHelper output) => _out = output;

    /// <summary>Two modes, and the service host is one of the fifteen.</summary>
    [Fact]
    public void ThereAreTwoModesAndTheHostIsReal()
    {
        Assert.Equal(2, System.Enum.GetValues<CloudflareStrategy.Mode>().Length);
        Assert.True(CybersoleHosts.IsKnown(CloudflareStrategy.ServiceHost));
        Assert.True(CybersoleHosts.IsSolverHost(CloudflareStrategy.ServiceHost));
        Assert.Equal("Cloudflare", CybersoleHosts.WallFor(CloudflareStrategy.ServiceHost));

        _out.WriteLine(CloudflareStrategy.ServiceHost);
    }

    /// <summary>A working service wins and the in-bot road is never asked.</summary>
    [Fact]
    public async Task TheServiceWinsWhenItAnswers()
    {
        var askedInBot = false;

        var runner = CloudflareStrategyRunner.Default(
            serviceCall: (_, _, _) => Task.FromResult<string?>("cf-from-service"),
            inBotSolve: (_, _) =>
            {
                askedInBot = true;
                return Task.FromResult<string?>("cf-from-bot");
            });

        var (token, status) = await runner.GetAsync("https://example.test");

        Assert.Equal("cf-from-service", token);
        Assert.False(askedInBot);
        _out.WriteLine(status);
    }

    /// <summary>A refusal falls through to in-bot, and the status is the image's sentence.</summary>
    [Fact]
    public async Task ARefusalFallsThroughToInBot()
    {
        var runner = CloudflareStrategyRunner.Default(
            serviceCall: (_, _, _) => Task.FromResult<string?>(null),
            inBotSolve: (_, _) => Task.FromResult<string?>("cf-from-bot"));

        var (token, status) = await runner.GetAsync("https://example.test");

        Assert.Equal("cf-from-bot", token);
        Assert.Equal("Cloudflare solver refused the token, solving in-bot", status);
        Assert.Equal(CloudflareStrategy.Mode.Service, CloudflareStrategy.ModeFor(status));
    }

    /// <summary>Both roads empty still reports the sentence, with no token.</summary>
    [Fact]
    public async Task NeitherRoadLeavesTheSentenceAndNoToken()
    {
        var runner = CloudflareStrategyRunner.Default();

        var (token, status) = await runner.GetAsync("https://example.test");

        Assert.Empty(token);
        Assert.Equal(CloudflareStrategy.RefusedMessage, status);
    }

    /// <summary>The order is service → in-bot, which is the whole content of the strategy.</summary>
    [Fact]
    public void TheOrderIsServiceThenInBot()
    {
        var runner = CloudflareStrategyRunner.Default();

        Assert.Equal(new[] { CloudflareStrategy.Mode.Service, CloudflareStrategy.Mode.InBot },
            runner.Order);

        Assert.True(CloudflareStrategy.IsService(CloudflareStrategy.Mode.Service));
        Assert.False(CloudflareStrategy.IsService(CloudflareStrategy.Mode.InBot));
    }

    /// <summary>The clearance cookie is the one the protocol table already carries.</summary>
    [Fact]
    public void TheClearanceCookieIsTheOneTheProtocolTableHas()
    {
        Assert.Equal("cf_clearance", CloudflareStrategy.ClearanceCookie);
        Assert.Contains(CloudflareStrategy.ClearanceCookie, Cybersole.Stores.Flows.AntiBotProtocol.CookiesFor("Cloudflare")!);

        // and the registry the page renders is recorded
        Assert.Equal(6, CloudflareStrategy.RegistryNames.Count);
        foreach (var name in CloudflareStrategy.RegistryNames) _out.WriteLine(name);
    }

    /// <summary>The two strategies are the same shape — that is the finding.</summary>
    [Fact]
    public void CloudflareAndKasadaHaveTheSameShape()
    {
        // both have a service road and a local road
        Assert.True(Cybersole.Stores.Scripts.KasadaStrategy.IsUsable(KasadaStrategy.Mode.Api));
        Assert.True(Cybersole.Stores.Scripts.KasadaStrategy.IsUsable(KasadaStrategy.Mode.Local));

        Assert.Equal(2, System.Enum.GetValues<CloudflareStrategy.Mode>().Length);
        Assert.Equal(4, System.Enum.GetValues<KasadaStrategy.Mode>().Length);

        // Kasada has two extra roads because it has two fallbacks; the ladder below them is identical
        var kasadaOrder = KasadaStrategyRunner.Default().Order;
        var cloudflareOrder = CloudflareStrategyRunner.Default().Order;

        Assert.Equal(KasadaStrategy.Mode.Api, kasadaOrder[0]);
        Assert.Equal(CloudflareStrategy.Mode.Service, cloudflareOrder[0]);

        _out.WriteLine("service road first, local road second — both strategies");
    }
}
