using System.Text.Json;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: Nike's current sensor exposes only configure/isReady — there is no ct() entry point
/// to probe — so the clearance token has to come off the sensor's own interrogation traffic. These cases
/// pin that contract end to end: with a resourceAddress the payload issues GET /mfc then POST /r, and the
/// host reads x-kpsdk-ct out of the /r response. Measured evidence for each step is in
/// docs/KASADA/11-jint-runtime.md sections 5.41 (resourceAddress), 5.56 (/mfc header check) and 5.61
/// (the payload settles on "Configured" and never reads the token back itself).
/// </summary>
public sealed class KasadaInterrogationTransportTests
{
    private static string Payload()
    {
        var dir = AppContext.BaseDirectory;
        while (dir is not null && !Directory.Exists(Path.Combine(dir, "fixtures")))
            dir = Directory.GetParent(dir)?.FullName;
        Assert.NotNull(dir);
        return File.ReadAllText(Path.Combine(dir!, "fixtures", "nike-p.js"));
    }

    /// <summary>A transport that answers the two endpoints the sensor calls, and records the calls.</summary>
    private static Func<string, string, string, string, string?> Answer(
        out List<(string Method, string Url, int BodyLength)> calls,
        string ct = "CT-FROM-RESPONSE-0123456789")
    {
        var log = new List<(string, string, int)>();
        calls = log;
        return (url, method, headersJson, body) =>
        {
            log.Add((method, url, body.Length));
            var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            if (url.EndsWith("/mfc", StringComparison.Ordinal))
            {
                // Without these two the payload throws "/mfc response was missing one or more headers".
                headers["x-kpsdk-h"] = "01";
                headers["x-kpsdk-fc"] = "1";
            }
            else if (url.EndsWith("/r", StringComparison.Ordinal))
            {
                headers["x-kpsdk-ct"] = ct;
                headers["x-kpsdk-v"] = "j-1.2.988";
            }
            return JsonSerializer.Serialize(new { status = 200, headers, body = "" });
        };
    }

    [Fact]
    public void TheSensorInterrogatesItsEndpointsAndTheTokenComesOffTheResponse()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            ResourceAddress = "https://www.nike.com/",
            Transport = Answer(out var calls),
        };

        var result = solver.Solve(Payload());

        Assert.True(result.ScriptExecuted);
        Assert.True(result.Ok, result.Error);
        Assert.Equal("CT-FROM-RESPONSE-0123456789", result.Ct);

        // The order is the payload's own: /mfc fetches remote configuration, /r carries the interrogation.
        Assert.Contains(calls, c => c.Method == "GET" && c.Url.EndsWith("/mfc"));
        Assert.Contains(calls, c => c.Method == "POST" && c.Url.EndsWith("/r"));

        // The interrogation body is built by the script, so it must not be empty: an empty POST would mean
        // the payload skipped its encoding step and any token we then read would be unrelated to it.
        var interrogation = calls.Single(c => c.Url.EndsWith("/r"));
        Assert.True(interrogation.BodyLength > 100,
            $"interrogation body was {interrogation.BodyLength} bytes");
    }

    [Fact]
    public void WithoutAResourceAddressNothingIsInterrogated()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            Transport = Answer(out var calls),
        };

        var result = solver.Solve(Payload());

        // The payload loads fine, but with no resourceAddress it has nothing to interrogate.
        Assert.True(result.ScriptExecuted);
        Assert.Empty(calls);
        Assert.False(result.Ok);
        Assert.Null(result.Ct);
    }

    [Fact]
    public void WithoutATransportTheRunStaysOfflineAndReportsNoToken()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            ResourceAddress = "https://www.nike.com/",
        };

        var result = solver.Solve(Payload());

        Assert.True(result.ScriptExecuted);
        Assert.Null(result.Ct);
        Assert.False(result.Ok);
    }
}
