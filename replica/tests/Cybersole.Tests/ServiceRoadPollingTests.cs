using System;
using System.IO;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 145: the polling decorator reaches the two service roads.
///
/// <para>
/// R144 built the poller; it did not connect to anything. Both service solvers now accept a poller
/// instead of a one-shot call, which is what the image's <c>PollCaptchaAsync</c> implies: a service that
/// hands out tokens asynchronously answers "not ready" for the first few looks by design, and a
/// one-shot call cannot tell that from a refusal.
/// </para>
///
/// <para>
/// The polling constructors keep the endpoint out of the picture on purpose — a poller is given a probe,
/// not an address, so the unconfigured-API rule of R137 still holds: no address, no invented host.
/// </para>
/// </summary>
public sealed class ServiceRoadPollingTests
{
    private readonly ITestOutputHelper _out;

    public ServiceRoadPollingTests(ITestOutputHelper output) => _out = output;

    /// <summary>Both service roads can poll, and say so.</summary>
    [Fact]
    public void BothServiceRoadsCanPoll()
    {
        var kasada = ApiKasadaSolver.Polling(_ => Task.FromResult<string?>("t"),
            TimeSpan.FromMilliseconds(1));
        var cloudflare = ServiceCloudflareSolver.Polling(_ => Task.FromResult<string?>("c"),
            TimeSpan.FromMilliseconds(1));

        Assert.True(kasada.IsPolling);
        Assert.True(cloudflare.IsPolling);
        Assert.True(kasada.IsConfigured);
        Assert.True(cloudflare.IsConfigured);

        // and the one-shot form still exists
        Assert.False(new ApiKasadaSolver().IsPolling);
        Assert.False(new ServiceCloudflareSolver().IsPolling);
    }

    /// <summary>A poll that answers later produces a token, and its status says how many looks.</summary>
    [Fact]
    public async Task ALateAnswerStillProducesAToken()
    {
        var looks = 0;

        var solver = ApiKasadaSolver.Polling(_ =>
        {
            looks++;
            return Task.FromResult<string?>(looks >= 3 ? "late-token" : null);
        }, TimeSpan.FromMilliseconds(1), attempts: 10);

        var token = await solver.GetAsync("https://example.test/");

        Assert.True(token.Usable);
        Assert.Equal("late-token", token.Token);
        Assert.Equal(KasadaStrategy.Mode.Api, token.Mode);
        Assert.Contains("Polled 3 time(s)", token.Status);

        _out.WriteLine(token.Status);
    }

    /// <summary>The Cloudflare service road returns the token through its string-shaped interface.</summary>
    [Fact]
    public async Task TheCloudflareRoadReturnsThePolledToken()
    {
        var looks = 0;

        var solver = ServiceCloudflareSolver.Polling(_ =>
        {
            looks++;
            return Task.FromResult<string?>(looks >= 2 ? "cf-late" : null);
        }, TimeSpan.FromMilliseconds(1), attempts: 5);

        var token = await solver.GetClearanceAsync("https://example.test/");

        Assert.Equal("cf-late", token);
        Assert.Equal(2, looks);
    }

    /// <summary>A poll that never answers leaves the road empty, and the ladder falls through.</summary>
    [Fact]
    public async Task AnEmptyPollFallsThroughToInBot()
    {
        var service = ServiceCloudflareSolver.Polling(_ => Task.FromResult<string?>(null),
            TimeSpan.FromMilliseconds(1), attempts: 3);
        var inBot = new InBotCloudflareSolver((_, _) => Task.FromResult<string?>("cf-from-bot"));

        var runner = new CloudflareStrategyRunner(service, inBot);
        var (token, status) = await runner.GetAsync("https://example.test/");

        Assert.Equal("cf-from-bot", token);
        Assert.Equal(CloudflareStrategy.RefusedMessage, status);
    }

    /// <summary>The unconfigured-API rule survives: no address, no invented host.</summary>
    [Fact]
    public async Task NoAddressStillMeansNoHost()
    {
        var unconfigured = new ApiKasadaSolver();
        var token = await unconfigured.GetAsync("https://example.test/");

        Assert.False(token.Usable);
        Assert.Equal("Kasada API down (Contact staff)", token.Status);

        // and the polling form takes a probe rather than an address, so it cannot invent one either
        var source = File.ReadAllText(Path.Combine(RepoRoot(), "src", "Cybersole.Stores",
            "Scripts", "KasadaSolvers.cs"));
        Assert.DoesNotContain("https://api.cybersole.io", source);

        _out.WriteLine("a probe is not an address");
    }

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir!.FullName;
    }
}
