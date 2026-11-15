using Cybersole.Core.Store;
using Xunit;

namespace Cybersole.Tests;

public class EventBusLimitsTests
{
    [Fact]
    public void Line_Cap_Drops_Oldest()
    {
        var bus = new EventBus { MaxHistory = 5, MaxRetention = TimeSpan.Zero };
        for (var i = 0; i < 20; i++) bus.Info("test", $"line {i}");

        Assert.Equal(5, bus.History.Count);
        Assert.Contains(bus.History, e => e.Message == "line 19");
        Assert.DoesNotContain(bus.History, e => e.Message == "line 14");
    }

    [Fact]
    public void Size_Budget_Trims_By_Characters()
    {
        var bus = new EventBus
        {
            MaxHistory = 1000,
            MaxRetention = TimeSpan.Zero,
            MaxTotalChars = 100,     // ~10 messages of 10 chars
            MaxEntryLength = 1000,
        };

        for (var i = 0; i < 50; i++) bus.Info("test", "0123456789");

        Assert.True(bus.History.Count * 10 <= 100 + 10, $"kept {bus.History.Count} entries");
    }

    [Fact]
    public void Retention_Window_Drops_Old_Entries()
    {
        var bus = new EventBus
        {
            MaxHistory = 1000,
            MaxTotalChars = int.MaxValue,
            MaxRetention = TimeSpan.FromMilliseconds(120),
        };

        bus.Info("test", "old");
        Thread.Sleep(200);
        bus.Info("test", "new");

        var messages = bus.History.Select(e => e.Message).ToList();
        Assert.Contains("new", messages);
        Assert.DoesNotContain("old", messages);
    }

    [Fact]
    public void Long_Messages_Are_Truncated()
    {
        var bus = new EventBus { MaxEntryLength = 50, MaxRetention = TimeSpan.Zero };
        bus.Info("test", new string('x', 500));

        var entry = Assert.Single(bus.History);
        Assert.StartsWith(new string('x', 50), entry.Message);
        Assert.EndsWith("…(+450)", entry.Message);
    }

    [Fact]
    public void Defaults_Are_Sane()
    {
        var bus = new EventBus();
        Assert.Equal(20000, bus.MaxHistory);
        Assert.Equal(50 * 1024 * 1024, bus.MaxTotalChars);
        Assert.Equal(TimeSpan.FromDays(1), bus.MaxRetention);
        Assert.Equal(8000, bus.MaxEntryLength);
    }
}
