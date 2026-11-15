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
}
