using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R29: the hand-written TLS stack must degrade instead of failing the caller.
///
/// R27 pinned the defect (nike.com answers `bad_record_mac`). Rather than leave a landmine,
/// OwnTls now falls back to the system stack once and says so.
/// </summary>
[Trait("Speed", "Slow")]
public class OwnTlsFallbackTests
{
    private readonly ITestOutputHelper _out;
    public OwnTlsFallbackTests(ITestOutputHelper output) => _out = output;

    private const string Url = "https://www.nike.com/";

    [Fact]
    public async Task AHundredTimesCallerStillGetsAResponse()
    {
        using var client = new NetClient { Transport = TransportMode.OwnTls };

        var res = await client.GetAsync(Url, new RequestOptions
        {
            Timeout = TimeSpan.FromSeconds(25),
            Retries = 1,
            Tag = "fallback",
        });

        _out.WriteLine($"status={res.StatusCode} bytes={res.Bytes} protocol={res.Protocol}");
        _out.WriteLine($"fellBack={client.FellBackFromOwnTls} count={client.OwnTlsFallbackCount}");

        // Whatever the transport ends up being, the request must succeed.
        Assert.True(res.IsSuccess, $"request failed entirely: HTTP {res.StatusCode}");

        // The transport must have been SwitchedForUs rather than silently left broken.
        Assert.True(client.FellBackFromOwnTls,
            "OwnTls was expected to be rejected by this host and fall back");
        Assert.True(client.OwnTlsFallbackCount >= 1);
    }

    [Fact]
    public async Task TheFallbackIsOneShotPerClient()
    {
        using var client = new NetClient { Transport = TransportMode.OwnTls };

        var first = await client.GetAsync(Url, new RequestOptions
        {
            Timeout = TimeSpan.FromSeconds(25),
            Retries = 0,
            Tag = "fallback-1",
        });
        Assert.True(first.IsSuccess);

        var countAfterFirst = client.OwnTlsFallbackCount;

        var second = await client.GetAsync(Url, new RequestOptions
        {
            Timeout = TimeSpan.FromSeconds(25),
            Retries = 0,
            Tag = "fallback-2",
        });
        Assert.True(second.IsSuccess);

        _out.WriteLine($"count after first={countAfterFirst} after second={client.OwnTlsFallbackCount}");

        // Once it has moved to the system stack it stays there — no repeated negotiation.
        Assert.Equal(countAfterFirst, client.OwnTlsFallbackCount);
    }

    [Fact]
    public void ResettingClearsTheBookkeeping()
    {
        using var client = new NetClient { Transport = TransportMode.OwnTls };
        client.ResetOwnTlsFallback();

        Assert.False(client.FellBackFromOwnTls);
        Assert.Equal(0, client.OwnTlsFallbackCount);
    }

    [Fact]
    public async Task TheDefaultTransportIsUnaffected()
    {
        using var client = new NetClient();   // SChannel by default
        var res = await client.GetAsync(Url, new RequestOptions
        {
            Timeout = TimeSpan.FromSeconds(25),
            Retries = 0,
            Tag = "default",
        });

        _out.WriteLine($"default status={res.StatusCode} fellBack={client.FellBackFromOwnTls}");

        Assert.True(res.IsSuccess);
        Assert.False(client.FellBackFromOwnTls);
        Assert.Equal(0, client.OwnTlsFallbackCount);
    }
}
