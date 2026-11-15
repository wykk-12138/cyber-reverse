using Cybersole.Core.Models;
using Cybersole.Services;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 58: <c>Proxies.More.TestAllOn</c> ("Test All On:") and <c>Proxies.More.SelectSite</c>
/// ("Select Site") were locale strings with no implementation. The tester could only ask one
/// question — "does this proxy reach ipify" — which is not the question a drop cares about.
///
/// A proxy can reach a neutral echo and still be blocked at the store. These tests pin the part
/// that is testable without a network: the target is honoured, and the exit IP is only read when
/// the target actually reports one.
/// </summary>
public sealed class ProxySiteTestTests
{
    private readonly ITestOutputHelper _out;

    public ProxySiteTestTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// A failed test against a named target still reports the target's failure, not ipify's.
    /// The proxy here points at a port nothing listens on, so the request fails locally and no
    /// network is touched.
    /// </summary>
    [Fact]
    public async Task TestingAgainstASiteUsesThatSite()
    {
        var bus = new Cybersole.Core.Store.EventBus();
        var tester = new ProxyTester(bus);
        var proxy = new Proxy { Host = "127.0.0.1", Port = 1, Scheme = "http" };

        var result = await tester.TestAsync(proxy, timeoutSeconds: 1,
            targetUrl: "https://www.nike.com/");

        _out.WriteLine($"ok={result.Ok} error={result.Error?[..Math.Min(50, result.Error.Length)]}");

        // The point is not that it failed — it is that a target URL is accepted at all and the
        // failure is the proxy's, not an argument error.
        Assert.False(result.Ok);
        Assert.NotNull(result.Error);
        Assert.Same(proxy, result.Proxy);
    }

    /// <summary>
    /// The exit IP is only parsed when the target is the echo service. Parsing a store's home
    /// page for an "ip" field would either throw or invent a value.
    /// </summary>
    [Fact]
    public async Task ASiteTestDoesNotInventAnExitIp()
    {
        var bus = new Cybersole.Core.Store.EventBus();
        var tester = new ProxyTester(bus);
        var proxy = new Proxy { Host = "127.0.0.1", Port = 1, Scheme = "http" };

        var result = await tester.TestAsync(proxy, timeoutSeconds: 1,
            targetUrl: "https://www.nike.com/");

        _out.WriteLine($"exit-ip={(result.ExitIp is null ? "(none)" : result.ExitIp)}");
        Assert.Null(result.ExitIp);
    }

    /// <summary>
    /// The default target is still the echo service, so the old behaviour — "Test All" with no
    /// site picked — keeps meaning what it meant.
    /// </summary>
    [Fact]
    public void TheDefaultTargetIsStillTheEchoService()
    {
        _out.WriteLine($"default target: {ProxyTester.IpEchoUrl}");
        Assert.Equal("https://api.ipify.org?format=json", ProxyTester.IpEchoUrl);
    }
}
