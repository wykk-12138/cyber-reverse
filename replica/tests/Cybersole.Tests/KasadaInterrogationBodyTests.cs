using System.Text.Json;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: the image has a separate KasadaCdSolver (0x143321dfa) for the client-data header, and
/// the replica's older approach was to call an entry point on the script — which does not exist on NFL's
/// current build any more than ct() does (docs/KASADA/11 5.23). The sensor composes that material itself
/// and only the host gets to see it, so the honest way to have it is to capture the interrogation body the
/// sensor built. These cases pin that it is captured, complete, and not a stub.
/// </summary>
public sealed class KasadaInterrogationBodyTests
{
    private static string Payload()
    {
        var dir = AppContext.BaseDirectory;
        while (dir is not null && !Directory.Exists(Path.Combine(dir, "fixtures")))
            dir = Directory.GetParent(dir)?.FullName;
        Assert.NotNull(dir);
        return File.ReadAllText(Path.Combine(dir!, "fixtures", "nike-p.js"));
    }

    private static Func<string, string, string, string, string?> Answer() =>
        (url, method, headersJson, body) =>
        {
            var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            if (url.EndsWith("/mfc", StringComparison.Ordinal))
            {
                headers["x-kpsdk-h"] = "01";
                headers["x-kpsdk-fc"] = "1";
            }
            else if (url.EndsWith("/r", StringComparison.Ordinal))
            {
                headers["x-kpsdk-ct"] = "CT-FOR-BODY-TEST-0123456789";
            }
            return JsonSerializer.Serialize(new { status = 200, headers, body = "" });
        };

    [Fact]
    public void TheBodyTheSensorBuiltIsCapturedWhole()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            ResourceAddress = "https://www.nike.com/",
            Transport = Answer(),
        };

        var result = solver.Solve(Payload());

        Assert.NotNull(result.InterrogationBody);

        // The sensor's own encoding is not a short marker: a truncated capture would look like success
        // while being useless for anything that replays it.
        Assert.True(result.InterrogationBody!.Length > 200,
            $"captured body was {result.InterrogationBody.Length} chars");

        // Opaque encoded text, not JSON: a body that still looks like structured data means the sensor's
        // encoding step never ran and we captured the plaintext input instead.
        Assert.DoesNotContain("{", result.InterrogationBody, StringComparison.Ordinal);
        Assert.DoesNotContain("probe", result.InterrogationBody, StringComparison.Ordinal);
    }

    [Fact]
    public void TheBodyIsStableWhenEveryInputIsHeldConstant()
    {
        string Body()
        {
            using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
            {
                ResourceAddress = "https://www.nike.com/",
                Transport = Answer(),
            };
            return solver.Solve(Payload()).InterrogationBody ?? "";
        }

        // Measured, not assumed: three runs under an identical shim produce the identical body. That is
        // the correct behaviour for a deterministic encoder — the variation a real page shows comes from
        // its clock and fingerprint inputs, not from a random source inside the encoding itself. Pinning
        // it here means a future change that starts injecting randomness is a deliberate decision rather
        // than a silent drift.
        var bodies = Enumerable.Range(0, 3).Select(_ => Body()).Where(b => b.Length > 0).ToList();
        Assert.Equal(3, bodies.Count);
        Assert.Single(bodies.Distinct());
    }

    [Fact]
    public void NoTransportMeansNoBodyToReport()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            ResourceAddress = "https://www.nike.com/",
        };

        var result = solver.Solve(Payload());

        Assert.Null(result.InterrogationBody);
    }
}
