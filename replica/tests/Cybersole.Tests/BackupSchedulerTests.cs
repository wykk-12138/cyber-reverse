using Cybersole.Services;
using Xunit;

namespace Cybersole.Tests;

public class BackupSchedulerTests
{
    [Fact]
    public async Task Runs_On_Interval()
    {
        var count = 0;
        using var scheduler = new BackupScheduler(TimeSpan.FromMilliseconds(40), () => Interlocked.Increment(ref count));

        await Task.Delay(300);

        Assert.True(scheduler.Runs >= 2, $"ran {scheduler.Runs} times");
        Assert.True(scheduler.IsEnabled);
    }

    [Fact]
    public void Zero_Interval_Disables_Scheduling()
    {
        using var scheduler = new BackupScheduler(TimeSpan.Zero, () => { });
        Assert.False(scheduler.IsEnabled);
        Assert.Equal(0, scheduler.Runs);
    }

    [Fact]
    public void Absurd_Interval_Is_Rejected()
    {
        using var scheduler = new BackupScheduler(TimeSpan.FromDays(30), () => { });
        Assert.False(scheduler.IsEnabled);
    }

    [Fact]
    public async Task Swallows_Callback_Exceptions()
    {
        var runs = 0;
        using var scheduler = new BackupScheduler(TimeSpan.FromMilliseconds(40), () =>
        {
            Interlocked.Increment(ref runs);
            throw new InvalidOperationException("disk full");
        });

        await Task.Delay(250);

        Assert.True(runs >= 2, "the timer thread must survive a throwing callback");
    }

    [Fact]
    public async Task Stops_After_Dispose()
    {
        var runs = 0;
        var scheduler = new BackupScheduler(TimeSpan.FromMilliseconds(30), () => Interlocked.Increment(ref runs));
        await Task.Delay(150);

        scheduler.Dispose();
        var snapshot = Volatile.Read(ref runs);
        await Task.Delay(200);

        Assert.InRange(Volatile.Read(ref runs), snapshot, snapshot + 1); // one straggler at most
    }
}
