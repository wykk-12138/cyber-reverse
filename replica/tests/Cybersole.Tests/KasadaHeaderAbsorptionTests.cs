using System.Text.Json;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: the original keeps one host-side field per Kasada header (_kasadaCt, _kasadaDt,
/// _kasadaIm, _kasadaDv, _kasadaSt, _kasadaRst, _kasadaFc, _kasadaH, plus _kasadaWorkTime — addresses in
/// docs/KASADA/11 5.69), because the gate reads them together. Shipping only x-kpsdk-ct and dropping the
/// rest produces a request the site can tell from a real one. These cases pin that every x-kpsdk-* header
/// the transport observed ends up on the result.
/// </summary>
public sealed class KasadaHeaderAbsorptionTests
{
    private static string Payload()
    {
        var dir = AppContext.BaseDirectory;
        while (dir is not null && !Directory.Exists(Path.Combine(dir, "fixtures")))
            dir = Directory.GetParent(dir)?.FullName;
        Assert.NotNull(dir);
        return File.ReadAllText(Path.Combine(dir!, "fixtures", "nike-p.js"));
    }

    /// <summary>Answers /mfc and /r the way a real deployment does: several x-kpsdk headers at once.</summary>
    private static Func<string, string, string, string, string?> Answer() =>
        (url, method, headersJson, body) =>
        {
            var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            if (url.EndsWith("/mfc", StringComparison.Ordinal))
            {
                headers["x-kpsdk-h"] = "01";
                headers["x-kpsdk-fc"] = "1";
                headers["x-kpsdk-im"] = "im-from-mfc";
            }
            else if (url.EndsWith("/r", StringComparison.Ordinal))
            {
                headers["x-kpsdk-ct"] = "CT-ABSORB-TEST-0123456789";
                headers["x-kpsdk-cd"] = "cd-from-r";
                headers["x-kpsdk-dt"] = "dt-from-r";
                headers["x-kpsdk-st"] = "st-from-r";
            }
            return JsonSerializer.Serialize(new { status = 200, headers, body = "" });
        };

    [Fact]
    public void EveryResponseHeaderReachesTheResult()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            ResourceAddress = "https://www.nike.com/",
            Transport = Answer(),
        };

        var result = solver.Solve(Payload());

        foreach (var name in new[] { "x-kpsdk-ct", "x-kpsdk-h", "x-kpsdk-fc", "x-kpsdk-im", "x-kpsdk-cd", "x-kpsdk-dt", "x-kpsdk-st" })
            Assert.True(result.Headers.ContainsKey(name), $"missing {name}");
    }

    [Fact]
    public void TheObservedHeadersSurviveInspection()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            ResourceAddress = "https://www.nike.com/",
            Transport = Answer(),
        };

        var result = solver.Solve(Payload());

        // Header lookup is case-insensitive, because HTTP header names are.
        Assert.Equal("CT-ABSORB-TEST-0123456789", result.Headers["X-KPSDK-CT"]);
        Assert.Equal("cd-from-r", result.ClientData);
        Assert.Equal("dt-from-r", result.Dt);
        Assert.Equal("st-from-r", result.St);
        Assert.Equal("01", result.H);
        Assert.Equal("im-from-mfc", result.Im);
    }

    [Fact]
    public void HeadersTheTransportNeverSawAreNotInvented()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            ResourceAddress = "https://www.nike.com/",
            Transport = Answer(),
        };

        var result = solver.Solve(Payload());

        // dv and rst were never sent. A gate that receives an empty header is different from one that
        // receives no header at all, so absence must stay absence.
        Assert.False(result.Headers.ContainsKey("x-kpsdk-dv"));
        Assert.False(result.Headers.ContainsKey("x-kpsdk-rst"));
        Assert.Null(result.Dv);
        Assert.Null(result.Rst);
    }
}
