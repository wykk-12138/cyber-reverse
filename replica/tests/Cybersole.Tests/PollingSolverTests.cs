using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 144: the polling road, made real.
///
/// <para>
/// R143 found <c>PollCaptchaAsync</c> in the image and drew the consequence: a service accepts a job and
/// answers later, so an inline await cannot tell "refused" from "not ready yet". This round adds the
/// decorator that can, and pins the three properties that matter — it polls, it is bounded, and when it
/// gives up it says how hard it tried.
/// </para>
///
/// <para>
/// The intervals here are milliseconds, so the test finishes instantly and no clock is faked.
/// </para>
/// </summary>
public sealed class PollingSolverTests
{
    private readonly ITestOutputHelper _out;

    public PollingSolverTests(ITestOutputHelper output) => _out = output;

    /// <summary>A probe that answers on the third look produces a token, and says how many looks.</summary>
    [Fact]
    public async Task ATokenOnTheThirdLookIsFound()
    {
        var looks = 0;

        var solver = new PollingSolver(_ =>
        {
            looks++;
            return Task.FromResult<string?>(looks >= 3 ? "token-after-3" : null);
        }, interval: TimeSpan.FromMilliseconds(1), attempts: 10);

        var token = await solver.GetAsync();

        Assert.True(token.Usable);
        Assert.Equal("token-after-3", token.Token);
        Assert.Equal(3, looks);
        Assert.Contains("Polled 3 time(s)", token.Status);

        _out.WriteLine(token.Status);
    }

    /// <summary>A probe that never answers gives up after exactly the attempt budget.</summary>
    [Fact]
    public async Task AProbeThatNeverAnswersGivesUpOnBudget()
    {
        var looks = 0;

        var solver = new PollingSolver(_ =>
        {
            looks++;
            return Task.FromResult<string?>(null);
        }, interval: TimeSpan.FromMilliseconds(1), attempts: 5);

        var token = await solver.GetAsync();

        Assert.False(token.Usable);
        Assert.Equal(5, looks);
        Assert.Contains("Polled 5 time(s)", token.Status);
        Assert.Contains("gave up", token.Status);

        _out.WriteLine(token.Status);
    }

    /// <summary>Cancelling stops the poll instead of burning the budget.</summary>
    [Fact]
    public async Task CancellingStopsThePoll()
    {
        using var cts = new CancellationTokenSource();
        var looks = 0;

        var solver = new PollingSolver(_ =>
        {
            looks++;
            if (looks == 2) cts.Cancel();
            return Task.FromResult<string?>(null);
        }, interval: TimeSpan.FromMilliseconds(1), attempts: 50);

        await Assert.ThrowsAnyAsync<OperationCanceledException>(() => solver.GetAsync(cts.Token));

        Assert.True(looks <= 3, $"looked {looks} times after cancellation");
        _out.WriteLine($"stopped after {looks} look(s)");
    }

    /// <summary>The budget and interval are readable, so a caller can report them.</summary>
    [Fact]
    public void TheBudgetIsReadable()
    {
        var solver = new PollingSolver(_ => Task.FromResult<string?>(null),
            interval: TimeSpan.FromSeconds(2), attempts: 7);

        Assert.Equal(7, solver.Attempts);
        Assert.Equal(TimeSpan.FromSeconds(2), solver.Interval);
        Assert.Contains("7 time(s)", solver.GiveUpStatus);

        _out.WriteLine(solver.GiveUpStatus);
    }

    /// <summary>The decorator is vendor-agnostic: the mode is whatever the strategy says.</summary>
    [Fact]
    public async Task TheModeComesFromTheStrategy()
    {
        var api = new PollingSolver(_ => Task.FromResult<string?>("t"),
            mode: KasadaStrategy.Mode.Api, interval: TimeSpan.FromMilliseconds(1));
        var fallback = new PollingSolver(_ => Task.FromResult<string?>("t"),
            mode: KasadaStrategy.Mode.MobileFallback, interval: TimeSpan.FromMilliseconds(1));

        Assert.Equal(KasadaStrategy.Mode.Api, (await api.GetAsync()).Mode);
        Assert.Equal(KasadaStrategy.Mode.MobileFallback, (await fallback.GetAsync()).Mode);
    }

    /// <summary>The fact this round implements, stated where a test can hold it.</summary>
    [Fact]
    public void ThePollingFactIsRecorded()
    {
        Assert.Single(WallSolving.Polling);
        Assert.Equal("PollCaptchaAsync", WallSolving.Polling[0]);

        Assert.Contains("answers later", WallSolving.PollingConsequence);
        _out.WriteLine(WallSolving.PollingConsequence);
    }
}
