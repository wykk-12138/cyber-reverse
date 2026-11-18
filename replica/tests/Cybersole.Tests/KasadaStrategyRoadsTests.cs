using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: the strategy runner shipped four roads and none of them could work in a default build —
/// the API road had no endpoint, the browser road was passed a null browser, and the two named fallbacks
/// only ever reported a name. Every store except Nike therefore failed its Kasada step and carried on
/// without a token. These cases pin that the road list reflects what was actually supplied, and that the
/// script road exists at all.
/// </summary>
public sealed class KasadaStrategyRoadsTests
{
    [Fact]
    public void ADefaultRunnerStillDeclaresAllFourModes()
    {
        var runner = KasadaStrategyRunner.Default();

        // The image declares four interchangeable modes and the runner reports each road's own status so a
        // failure is explainable. Dropping a road would hide the reason instead of reporting it.
        Assert.Equal(new[]
        {
            KasadaStrategy.Mode.Api, KasadaStrategy.Mode.Local,
            KasadaStrategy.Mode.Fallback, KasadaStrategy.Mode.MobileFallback,
        }, runner.Order);
    }

    [Fact]
    public async Task ADefaultRunnerCannotProduceATokenWhenNothingWasSupplied()
    {
        var runner = KasadaStrategyRunner.Default();

        // Declaring four roads is not the same as any of them working: with no endpoint, no browser and
        // no script, every road answers with its own failure status.
        var token = await runner.GetAsync("http://127.0.0.1:1/");
        Assert.False(token.Usable);
    }

    [Fact]
    public void SuppliedRoadsAppearInTheOrderTheyAreTried()
    {
        using var http = new Cybersole.Http.NetClient();
        var runner = KasadaStrategyRunner.Default(script: new ScriptKasadaSolver(http));

        Assert.Contains(KasadaStrategy.Mode.Local, runner.Order);

        // The script road is tried before the name-only fallbacks, otherwise a real answer would never be
        // reached while a placeholder status was reported instead.
        var local = runner.Order.ToList().IndexOf(KasadaStrategy.Mode.Local);
        var fallback = runner.Order.ToList().IndexOf(KasadaStrategy.Mode.Fallback);
        Assert.True(local < fallback, $"Local at {local}, Fallback at {fallback}");
    }

    [Fact]
    public async Task TheScriptRoadFailsCleanlyOnAnUnreachablePage()
    {
        using var http = new Cybersole.Http.NetClient();
        var road = new ScriptKasadaSolver(http);

        // No live page, so this cannot produce a token — but it must say so as a status, not by throwing
        // at the flow, because the runner tries the next road after it.
        var token = await road.GetAsync("http://127.0.0.1:1/");

        Assert.False(token.Usable);
        Assert.Equal(KasadaStrategy.Mode.Local, token.Mode);
        Assert.False(string.IsNullOrEmpty(token.Status));
    }

    [Fact]
    public async Task AnEmptyPageUrlIsRejectedWithoutAnyNetworkWork()
    {
        using var http = new Cybersole.Http.NetClient();
        var road = new ScriptKasadaSolver(http);

        var token = await road.GetAsync("");

        Assert.False(token.Usable);
        Assert.Equal(KasadaStrategy.Mode.Local, token.Mode);
    }
}
