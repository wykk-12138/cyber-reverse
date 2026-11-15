using Cybersole.Core.Store;
using Cybersole.Services;
using Xunit;

namespace Cybersole.Tests;

public class CheckoutStatsTests
{
    private static CheckoutEvent Evt(bool success, string store = "shopify", string price = "120.00")
        => new(store, "Product", "10", price, success, success ? "A1" : null, "Profile");

    [Fact]
    public void Records_Totals_And_Per_Store_Breakdown()
    {
        var bus = new EventBus();
        using var stats = new CheckoutStats(bus);

        bus.RaiseCheckout(Evt(true, "shopify"));
        bus.RaiseCheckout(Evt(false, "shopify"));
        bus.RaiseCheckout(Evt(true, "nike"));

        Assert.Equal(3, stats.Total);
        Assert.Equal(2, stats.Success);
        Assert.Equal(1, stats.Failed);
        var shopify = stats.ByStore["shopify"];
        var nike = stats.ByStore["nike"];
        Assert.Equal(1, shopify.Success);
        Assert.Equal(1, shopify.Failed);
        Assert.Equal(1, nike.Success);
        Assert.Equal(0, nike.Failed);
    }

    [Fact]
    public void Spent_Only_Counts_Successful_Checkouts()
    {
        var bus = new EventBus();
        using var stats = new CheckoutStats(bus);

        bus.RaiseCheckout(Evt(true, price: "199.99"));
        bus.RaiseCheckout(Evt(false, price: "999.00"));

        Assert.Equal(199.99m, stats.Spent, 2);
    }

    [Fact]
    public void SuccessRate_Is_Zero_Without_Events()
    {
        var bus = new EventBus();
        using var stats = new CheckoutStats(bus);
        Assert.Equal(0, stats.SuccessRate);
    }

    [Fact]
    public void Raises_Changed_On_Each_Checkout()
    {
        var bus = new EventBus();
        using var stats = new CheckoutStats(bus);
        var count = 0;
        stats.Changed += (_, _) => count++;

        bus.RaiseCheckout(Evt(true));
        bus.RaiseCheckout(Evt(false));

        Assert.Equal(2, count);
    }

    [Fact]
    public void Unsubscribes_On_Dispose()
    {
        var bus = new EventBus();
        var stats = new CheckoutStats(bus);
        stats.Dispose();

        bus.RaiseCheckout(Evt(true));

        Assert.Equal(0, stats.Total);
    }
}
