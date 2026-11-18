using System.Text.Json;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: KasadaSolver carries three legacy entry-point probe tables (ct / sb / body). On Nike's
/// current build none of them match — KPSDK exposes only configure and isReady (docs/KASADA/11 5.23) — so a
/// null from those tables means "this probe did not apply", not "the script has no token". These cases pin
/// the real path and, in particular, that EncryptBody no longer returns null on a modern build: it falls
/// back to the material the sensor actually composed.
/// </summary>
public sealed class KasadaLegacyEntryPointTests
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
                headers["x-kpsdk-ct"] = "CT-LEGACY-TEST-0123456789";
            }
            return JsonSerializer.Serialize(new { status = 200, headers, body = "" });
        };

    [Fact]
    public void TheModernBuildExposesNoTokenGetterToProbe()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" });
        solver.Solve(Payload());

        // This is the fact the legacy tables exist to survive, not a bug to paper over.
        Assert.Equal("false", solver.Runtime.TryString("String(!!(window.KPSDK && window.KPSDK.ct))"));
        Assert.Equal("false", solver.Runtime.TryString("String(!!(window.KPSDK && window.KPSDK.sb))"));
        Assert.Equal("configure,isReady",
            solver.Runtime.TryString("Object.keys(window.KPSDK).join(',')"));
    }

    [Fact]
    public void EncryptBodyFallsBackToTheMaterialTheSensorComposed()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            ResourceAddress = "https://www.nike.com/",
            Transport = Answer(),
        };
        var result = solver.Solve(Payload());
        Assert.NotNull(result.InterrogationBody);

        var body = solver.EncryptBody("""{"probe":"payload"}""");

        // Before the fallback this was null on every modern build, which silently turned a protected
        // request into an unprotected one.
        Assert.NotNull(body);
        Assert.Equal(result.InterrogationBody, body);
    }

    [Fact]
    public void EncryptBodyStillReturnsNullWhenNothingHasBeenCaptured()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" });
        solver.Solve(Payload());

        // No transport was installed, so no interrogation body exists and there is nothing honest to
        // return. Answering with the caller's own input would look like encryption and not be any.
        Assert.Null(solver.EncryptBody("""{"probe":"payload"}"""));
    }
}
