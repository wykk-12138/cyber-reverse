using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Live capture against a real site.
///
/// Skipped by default: a headed Chrome launched from inside the test host does not always get
/// reaped, and the run then hangs instead of failing. Use the recorder directly when you
/// actually want a capture:
///
/// <code>
/// await using var rec = await NetworkRecorder.BeginAsync(headed: true);
/// await rec.VisitAsync("https://www.goat.com/sneakers/...");
/// await rec.WaitAsync(TimeSpan.FromSeconds(8));
/// Console.WriteLine(rec.Describe());
/// </code>
///
/// What a capture produced before the skip went in:
///
///   headless, throwaway profile   403 for both goat.com and scheels.com
///   headed,   profile on disk     200 for both
///
/// So the anti-bot wall is about the headless signature and profile freshness, not about the
/// recorder. Keep this fact when re-enabling: launching headless will look like a broken
/// recorder and is not.
/// </summary>
public class NetworkRecorderLiveTests
{
    private const string SkipReason =
        "manual capture only - a headed browser launched from the test host can hang the run";

    [Fact(Skip = SkipReason)]
    public async Task CapturesTheApiCallsGoatMakesOnAProductPage()
    {
        if (ChromiumBridge.FindBrowser() is null) return;

        await using var rec = await NetworkRecorder.BeginAsync(headed: true);
        await rec.VisitAsync(
            "https://www.goat.com/sneakers/air-jordan-1-retro-high-og-royal-2026-iq5495-005");
        await rec.WaitAsync(TimeSpan.FromSeconds(8));

        var api = rec.ApiCalls.ToList();
        Assert.True(api.Count > 0, "the recorder saw no traffic at all");

        var sawApi = api.Any(c => c.Url!.Contains("/api/", StringComparison.OrdinalIgnoreCase));
        var allBlocked = api.All(c => c.Status == 403);
        Assert.True(sawApi || allBlocked, "unexpected capture shape: " + rec.Describe());

        Console.WriteLine(rec.Describe());
    }

    [Fact(Skip = SkipReason)]
    public async Task CapturesScheelsHomeTraffic()
    {
        if (ChromiumBridge.FindBrowser() is null) return;

        await using var rec = await NetworkRecorder.BeginAsync(headed: true);
        await rec.VisitAsync("https://www.scheels.com/");
        await rec.WaitAsync(TimeSpan.FromSeconds(6));

        Assert.True(rec.ApiCalls.Any(), "the recorder saw no traffic at all");
        Console.WriteLine(rec.Describe());
    }
}
