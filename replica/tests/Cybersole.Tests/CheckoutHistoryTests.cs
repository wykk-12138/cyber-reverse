using Cybersole.Core.Store;
using Cybersole.Services;
using Xunit;

namespace Cybersole.Tests;

public class CheckoutHistoryTests
{
    private static CheckoutEvent Evt(bool success, string store = "shopify", string price = "100.00")
        => new(store, "Product", "10", price, success, success ? "A1" : null, "Profile");

    [Fact]
    public void Flush_Writes_History_And_Load_Restores_Aggregates()
    {
        var dir = Path.Combine(Path.GetTempPath(), "cyb-hist-" + Guid.NewGuid().ToString("N"));
        var path = Path.Combine(dir, "checkoutHistory.json");

        try
        {
            var bus1 = new EventBus();
            var first = new CheckoutStats(bus1, path);
            bus1.RaiseCheckout(Evt(true, "shopify", "250.00"));
            bus1.RaiseCheckout(Evt(false, "nike", "999.00"));
            first.Flush();
            first.Dispose();

            Assert.True(File.Exists(path));

            var bus2 = new EventBus();
            using var second = new CheckoutStats(bus2, path);

            Assert.Equal(2, second.Total);
            Assert.Equal(1, second.Success);
            Assert.Equal(1, second.Failed);
            Assert.Equal(250.00m, second.Spent, 2);
            Assert.Equal(2, second.Events.Count);
        }
        finally
        {
            if (Directory.Exists(dir)) Directory.Delete(dir, true);
        }
    }

    [Fact]
    public void Missing_History_File_Is_Ignored()
    {
        var dir = Path.Combine(Path.GetTempPath(), "cyb-missing-" + Guid.NewGuid().ToString("N"));
        var path = Path.Combine(dir, "h.json");
        var bus = new EventBus();
        using (var stats = new CheckoutStats(bus, path))
        {
            Assert.Equal(0, stats.Total);
        }

        Assert.Equal(0, new CheckoutStats(bus, path).Total);

        // R130: constructing and disposing must not leave a directory behind. The class used to create
        // one and write "[]" into it, which is how fourteen cyb-missing-* shells accumulated in %TEMP%
        // with nothing but an empty array inside.
        Assert.False(Directory.Exists(dir), "an empty, absent history must not be created on dispose");
    }

    [Fact]
    public void Corrupt_History_File_Does_Not_Throw()
    {
        var dir = Path.Combine(Path.GetTempPath(), "cyb-bad-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(dir);
        var path = Path.Combine(dir, "h.json");
        File.WriteAllText(path, "{not json");

        try
        {
            var bus = new EventBus();
            using var stats = new CheckoutStats(bus, path);
            Assert.Equal(0, stats.Total);
        }
        finally
        {
            Directory.Delete(dir, true);
        }
    }

    [Fact]
    public void History_Is_Bounded_To_2000_Entries()
    {
        var bus = new EventBus();
        using var stats = new CheckoutStats(bus);
        for (var i = 0; i < 2100; i++)
            bus.RaiseCheckout(Evt(true));

        Assert.Equal(2100, stats.Total);
        Assert.Equal(2000, stats.Events.Count);
    }
}
