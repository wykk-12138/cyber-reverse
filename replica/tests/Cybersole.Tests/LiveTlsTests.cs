using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Live TLS diagnostics. Skipped unless CYB_LIVE_TLS=1 (the probe needs outbound 443).
/// Run with:  $env:CYB_LIVE_TLS="1"; dotnet test --filter Live_Tls_Probe
/// </summary>
public class LiveTlsTests
{
    private readonly ITestOutputHelper _output;

    public LiveTlsTests(ITestOutputHelper output) => _output = output;

    [Fact]
    public async Task Live_Tls_Probe()
    {
        if (Environment.GetEnvironmentVariable("CYB_LIVE_TLS") != "1")
        {
            _output.WriteLine("skipped (set CYB_LIVE_TLS=1 to run)");
            return;
        }

        var results = await TlsProbe.CompareAsync("api.cybersole.io");
        foreach (var r in results)
        {
            _output.WriteLine(
                $"{r.Host,-24} ok={r.Ok} proto={r.Protocol,-8} cipher={r.CipherSuite,-48} alpn={r.Alpn ?? "-",-8} {r.HandshakeMs}ms {r.Error}");
        }

        Assert.All(results, r => Assert.True(r.Ok || r.Error is not null));
    }
}
