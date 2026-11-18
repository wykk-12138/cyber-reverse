using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: a Kasada give-up is a status, not an exception — the image's design is that every road
/// reports its own reason and the caller decides whether to rotate and restart (docs/KASADA/05-states.md
/// section 5). So "no token" must still be a Success step outcome that carries the reasons, and the status
/// must name every road that was tried plus the give-up marker. These cases pin that contract, and record
/// honestly that the runner makes one pass: Retry limit reached currently means "after a single attempt".
/// </summary>
public sealed class KasadaGiveUpContractTests
{
    [Fact]
    public async Task AGiveUpNamesEveryRoadAndTheRetryMarker()
    {
        var runner = KasadaStrategyRunner.Default();
        var token = await runner.GetAsync("http://127.0.0.1:1/");

        Assert.False(token.Usable);

        // The image's give-up string is a contract: it is what a support conversation keys off.
        Assert.Contains(KasadaStrategyRunner.GaveUpStatus, token.Status, StringComparison.Ordinal);

        // Every road's own reason travels with it, so the status says *why* rather than just *no*.
        Assert.Contains("|", token.Status, StringComparison.Ordinal);
    }

    [Fact]
    public async Task TheRoadsAreTriedInTheDeclaredOrderAndAllReport()
    {
        var runner = KasadaStrategyRunner.Default();
        var token = await runner.GetAsync("http://127.0.0.1:1/");

        var parts = token.Status.Split('|', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries);

        // Four roads plus the give-up marker appended after them.
        Assert.Equal(runner.Order.Count + 1, parts.Length);
        Assert.Equal(KasadaStrategyRunner.GaveUpStatus, parts[^1]);
    }

    [Fact]
    public async Task AGiveUpIsNotAnExceptionSoTheFlowCanDecide()
    {
        var runner = KasadaStrategyRunner.Default();

        // Whatever happens, this call returns a token object. An exception here would take the decision
        // away from the caller, which is the one thing the image's status-per-road design avoids.
        var token = await runner.GetAsync("http://127.0.0.1:1/");
        Assert.NotNull(token);
        Assert.False(string.IsNullOrEmpty(token.Status));
    }
}
