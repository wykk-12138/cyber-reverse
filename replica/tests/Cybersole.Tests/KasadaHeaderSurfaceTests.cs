using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R21: what a live Kasada request actually carries, and what the solver now returns.
/// </summary>
[Trait("Speed", "Slow")]
public class KasadaHeaderSurfaceTests
{
    private readonly ITestOutputHelper _out;
    public KasadaHeaderSurfaceTests(ITestOutputHelper output) => _out = output;

    private static string Shorten(string value) =>
        value.Length > 70 ? value[..70] + "..." : value;

    [Fact]
    public async Task TheSolverReturnsTheWholeHeaderFamily()
    {
        var solver = new ChromiumKasadaSolver();

        // The trigger endpoint just has to be on the protected origin; a 404 still gets
        // decorated by the script, which is all we need to observe the headers.
        var result = await solver.SolveAsync(
            "https://www.nike.com/",
            TimeSpan.FromSeconds(40),
            "https://www.nike.com/api/graphql?query=%7B__typename%7D");

        _out.WriteLine($"ok={result.Ok} error={result.Error}");
        foreach (var kv in result.KasadaHeaders)
            _out.WriteLine($"  {kv.Key} = {Shorten(kv.Value)}");

        Assert.True(result.Ok, result.Error);
        Assert.False(string.IsNullOrEmpty(result.Ct));
        Assert.Contains("x-kpsdk-ct", result.KasadaHeaders.Keys);
    }

    [Fact]
    public async Task ClientDataIsSurfacedWhenTheWireCarriesIt()
    {
        var solver = new ChromiumKasadaSolver();
        var result = await solver.SolveAsync("https://www.nike.com/", TimeSpan.FromSeconds(40));

        _out.WriteLine($"clientData = {Shorten(result.ClientData ?? "(none)")}");

        if (result.ClientData is not null)
        {
            Assert.Contains("workTime", result.ClientData);
            Assert.Contains("{", result.ClientData);
        }
    }

    [Fact]
    public void KasadaHeadersOnlyContainsKasadaHeaders()
    {
        var result = new KasadaResult { Ok = true };
        result.Headers["x-kpsdk-ct"] = "a";
        result.Headers["x-kpsdk-v"] = "b";
        result.Headers["Content-Type"] = "c";

        Assert.Equal(2, result.KasadaHeaders.Count);
        Assert.DoesNotContain("Content-Type", result.KasadaHeaders.Keys);
    }

    [Fact]
    public void ClientDataReadsFromTheHeaderBag()
    {
        var result = new KasadaResult { Ok = true };
        result.Headers["x-kpsdk-cd"] = "{\"workTime\":1}";

        Assert.Equal("{\"workTime\":1}", result.ClientData);
    }
}
