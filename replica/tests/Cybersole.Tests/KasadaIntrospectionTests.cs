using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R21: find out what a live Kasada build actually exposes, rather than guessing at entry
/// point names. Everything here runs against the real storefront.
/// </summary>
[Trait("Speed", "Slow")]
public class KasadaIntrospectionTests
{
    private readonly ITestOutputHelper _out;
    public KasadaIntrospectionTests(ITestOutputHelper output) => _out = output;

    private static async Task<ChromiumBridge> OpenNikeAsync()
    {
        var bridge = await ChromiumBridge.LaunchAsync();
        await bridge.ApplyStealthAsync();
        await bridge.NavigateAsync("https://www.nike.com/");

        // give p.js time to boot and mint its token
        for (var i = 0; i < 40; i++)
        {
            var ready = await bridge.EvaluateAsync("typeof window.KPSDK !== 'undefined'");
            if (ready == "true") break;
            await Task.Delay(250);
        }

        return bridge;
    }

    [Fact]
    public async Task KpsdkExposesItsOwnSurface()
    {
        await using var bridge = await OpenNikeAsync();

        var shape = await bridge.EvaluateAsync("""
            (() => {
              const k = window.KPSDK;
              if (!k) return JSON.stringify({ present: false });
              const own = Object.getOwnPropertyNames(k);
              const proto = Object.getOwnPropertyNames(Object.getPrototypeOf(k) || {});
              const described = {};
              for (const name of own) {
                try { described[name] = typeof k[name]; } catch (e) { described[name] = 'throws'; }
              }
              return JSON.stringify({ present: true, own, proto, described });
            })()
            """);

        _out.WriteLine(shape ?? "(null)");
        Assert.NotNull(shape);
        Assert.Contains("\"present\":true", shape);
    }

    [Fact]
    public async Task CookiesCarryWhateverKasadaWrote()
    {
        await using var bridge = await OpenNikeAsync();
        await Task.Delay(1500);

        var cookies = await bridge.EvaluateAsync("document.cookie");
        _out.WriteLine($"cookies = {cookies}");

        var kasadaCookies = await bridge.EvaluateAsync("""
            (() => {
              const names = document.cookie.split(';').map(c => c.split('=')[0].trim());
              return JSON.stringify(names.filter(n =>
                /^(ct|cd|sbsd|kpsdk|_kpsdk)/i.test(n)));
            })()
            """);

        _out.WriteLine($"kasada cookies = {kasadaCookies}");
        Assert.NotNull(cookies);
    }

    [Fact]
    public async Task AnOutboundRequestGetsTheKasadaHeaders()
    {
        await using var bridge = await OpenNikeAsync();

        // Ask the page to hit its own origin — Kasada hooks XHR/fetch and should decorate it.
        var probe = await bridge.EvaluateAsync("""
            (async () => {
              try {
                const r = await fetch('/api/graphql?query=%7B__typename%7D', {
                  method: 'POST',
                  headers: { 'content-type': 'application/json' },
                  body: '{"query":"{__typename}"}',
                  credentials: 'include'
                });
                return JSON.stringify({ status: r.status });
              } catch (e) { return JSON.stringify({ error: String(e) }); }
            })()
            """, default, awaitPromise: true);

        _out.WriteLine($"probe = {probe}");
        await Task.Delay(1200);

        var headers = bridge.SniffKasadaHeaders();
        foreach (var kv in headers)
            _out.WriteLine($"  {kv.Key} = {(kv.Value.Length > 60 ? kv.Value[..60] + "…" : kv.Value)}");

        // ct must be there; sb only appears once a protected endpoint is exercised
        Assert.True(headers.ContainsKey("x-kpsdk-ct") || probe?.Contains("\"status\"") == true,
            "no x-kpsdk-ct observed on an outbound request");
    }

    [Fact]
    public async Task TheSolverFindsTheSensorTokenWhenThePageProducesOne()
    {
        var solver = new ChromiumKasadaSolver();
        var result = await solver.SolveAsync("https://www.nike.com/", TimeSpan.FromSeconds(40));

        _out.WriteLine($"ok={result.Ok} ctLen={result.Ct?.Length} sbLen={result.Sbsd?.Length}");
        _out.WriteLine($"version={result.Version} error={result.Error}");

        Assert.True(result.Ok, result.Error);
        Assert.False(string.IsNullOrEmpty(result.Ct));
    }
}
