using Cybersole.Http;
using Cybersole.Tests.Support;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>Diagnostic: can NetClient talk to a loopback HttpListener at all?</summary>
public class NetClientLoopbackProbeTests
{
    private readonly ITestOutputHelper _out;
    public NetClientLoopbackProbeTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public async Task GetAsyncReachesALoopbackServer()
    {
        using var server = new TinyServer(_ => (200, "{\"ok\":true}"));

        using var http = new NetClient();
        var res = await http.GetAsync(server.BaseUrl + "/",
            new RequestOptions { Timeout = TimeSpan.FromSeconds(5), Retries = 0 });

        _out.WriteLine($"status={res.StatusCode} bytes={res.Bytes} body={res.Body}");
        Assert.Equal(200, res.StatusCode);
        Assert.Contains("ok", res.Body);
    }

    [Fact]
    public void DefaultTransportIsProductionAndOwnTlsIsExperimental()
    {
        using var client = new NetClient();
        Assert.Equal(TransportMode.SChannel, client.Transport);
        Assert.True(client.IsProductionTransport);
        Assert.False(client.IsExperimentalTransport);

        client.Transport = TransportMode.OwnTls;
        Assert.False(client.IsProductionTransport);
        Assert.True(client.IsExperimentalTransport);
    }

    [Fact]
    public async Task OwnTlsFallsBackOneShotToSChannelOnLocalHandshakeFailure()
    {
        // Plain HTTP listener rejects TLS ClientHello immediately, triggering OwnTls -> SChannel fallback offline.
        using var server = new TinyServer(_ => (200, "ok"));
        var httpsUrl = server.BaseUrl.Replace("http://", "https://");

        using var client = new NetClient { Transport = TransportMode.OwnTls };
        await Assert.ThrowsAnyAsync<Exception>(() =>
            client.GetAsync(httpsUrl, new RequestOptions { Timeout = TimeSpan.FromSeconds(2), Retries = 0 }));

        Assert.True(client.FellBackFromOwnTls);
        Assert.Equal(1, client.OwnTlsFallbackCount);
        Assert.False(string.IsNullOrEmpty(client.LastOwnTlsError));
        Assert.Equal(TransportMode.SChannel, client.Transport);
        Assert.True(client.IsProductionTransport);

        client.ResetOwnTlsFallback();
        Assert.False(client.FellBackFromOwnTls);
        Assert.Equal(0, client.OwnTlsFallbackCount);
        Assert.Null(client.LastOwnTlsError);
    }

    [Fact]
    public void SocketsDefaultsAndAsicsChrome150MatchBinaryOptions()
    {
        Assert.Equal(TimeSpan.FromSeconds(30), NetClient.DefaultConnectTimeout);
        Assert.Equal(TimeSpan.FromSeconds(90), NetClient.DefaultPooledConnectionIdleTimeout);

        using var client = new NetClient();
        Assert.Equal(TimeSpan.FromSeconds(30), client.ConnectTimeout);

        Assert.Equal(3, TlsProfile.All.Count);
        Assert.False(TlsProfile.Chrome.SupportsHttp3);
        Assert.True(TlsProfile.Chrome150.SupportsHttp3);
        Assert.Same(TlsProfile.Chrome150, TlsProfile.ByName("chrome_150"));
        Assert.Same(TlsProfile.Chrome, TlsProfile.ByName("chrome_131"));
    }
}
