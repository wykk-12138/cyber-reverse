using Cybersole.Services;
using Xunit;

namespace Cybersole.Tests;

public class ConcurrencyGateTests
{
    [Fact]
    public async Task Never_Exceeds_Capacity()
    {
        var gate = new ConcurrencyGate(2);
        var peak = 0;
        var running = 0;
        var tasks = new List<Task>();

        for (var i = 0; i < 10; i++)
        {
            tasks.Add(Task.Run(async () =>
            {
                using var lease = await gate.EnterAsync();
                var now = Interlocked.Increment(ref running);
                InterlockedMax(ref peak, now);
                await Task.Delay(20);
                Interlocked.Decrement(ref running);
            }));
        }

        await Task.WhenAll(tasks);

        Assert.True(peak <= 2, $"peak concurrency was {peak}");
        Assert.Equal(0, gate.InFlight);
        Assert.True(gate.MaxObserved <= 2);
    }

    [Fact]
    public async Task Serialises_When_Capacity_Is_One()
    {
        var gate = new ConcurrencyGate(1);
        var order = new List<int>();

        var tasks = Enumerable.Range(0, 5).Select(i => Task.Run(async () =>
        {
            using var lease = await gate.EnterAsync();
            lock (order) order.Add(i);
            await Task.Delay(10);
        })).ToArray();

        await Task.WhenAll(tasks);

        Assert.Equal(5, order.Count);
        Assert.Equal(1, gate.MaxObserved);
    }

    [Fact]
    public async Task Lease_Is_Idempotent_On_Dispose()
    {
        var gate = new ConcurrencyGate(1);
        var lease = await gate.EnterAsync();
        lease.Dispose();
        lease.Dispose();

        Assert.Equal(0, gate.InFlight);

        using var again = await gate.EnterAsync().WaitAsync(TimeSpan.FromSeconds(2));
        Assert.Equal(1, gate.InFlight);
    }

    [Fact]
    public async Task Cancellation_While_Waiting_Throws()
    {
        var gate = new ConcurrencyGate(1);
        using var first = await gate.EnterAsync();

        using var cts = new CancellationTokenSource(50);
        await Assert.ThrowsAnyAsync<OperationCanceledException>(
            async () => await gate.EnterAsync(cts.Token));

        Assert.Equal(1, gate.InFlight);
    }

    [Fact]
    public void Minimum_Capacity_Is_One()
    {
        var gate = new ConcurrencyGate(0);
        Assert.Equal(1, gate.Capacity);
    }

    private static void InterlockedMax(ref int target, int value)
    {
        int observed;
        do
        {
            observed = Volatile.Read(ref target);
            if (value <= observed) return;
        }
        while (Interlocked.CompareExchange(ref target, value, observed) != observed);
    }
}
