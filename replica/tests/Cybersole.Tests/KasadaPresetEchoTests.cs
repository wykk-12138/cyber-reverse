using System.Text.Json;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: presetting a response makes the sensor read a token back, and a run that only reads its
/// own input back looks exactly like a run that computed one. Measured on the live script: presetting
/// x-kpsdk-ct to a marker makes Solve return that marker verbatim. These cases pin that an echo is refused,
/// because reporting it as a result would be the most comfortable possible lie.
/// </summary>
public sealed class KasadaPresetEchoTests
{
    private static string Payload()
    {
        var dir = AppContext.BaseDirectory;
        while (dir is not null && !Directory.Exists(Path.Combine(dir, "fixtures")))
            dir = Directory.GetParent(dir)?.FullName;
        Assert.NotNull(dir);
        return File.ReadAllText(Path.Combine(dir!, "fixtures", "nike-p.js"));
    }

    [Fact]
    public void ATokenThatWasInjectedIsNotReportedAsComputed()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            ResourceAddress = "https://www.nike.com/",
        };

        var preset = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["x-kpsdk-ct"] = "INJECTED-MARKER-0123456789",
            ["x-kpsdk-h"] = "01",
            ["x-kpsdk-fc"] = "1",
        };
        solver.PresetResponses["mfc"] = preset;

        var result = solver.Solve(Payload());

        // The sensor may well hand the value back; that is caching, not computing.
        Assert.False(result.Ok);
        Assert.Contains("injected", result.Error ?? "", StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void PresetsWithNoTokenStillFailForTheOriginalReason()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            ResourceAddress = "https://www.nike.com/",
        };

        // A preset that carries no token leaves nothing to echo, so the failure must stay the honest one.
        solver.PresetResponses["mfc"] = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["x-kpsdk-h"] = "01",
            ["x-kpsdk-fc"] = "1",
        };

        var result = solver.Solve(Payload());

        Assert.False(result.Ok);
        Assert.Contains("no kasada client token", result.Error ?? "", StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void WithoutPresetsNothingIsInjectedAndTheGuardStaysQuiet()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" });
        var result = solver.Solve(Payload());

        // No transport and no preset: the failure is neither an echo nor a success, and it must not claim
        // to be an echo either.
        Assert.False(result.Ok);
        Assert.DoesNotContain("injected", result.Error ?? "", StringComparison.OrdinalIgnoreCase);
    }
}
