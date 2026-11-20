using Cybersole.Core.Models;
using Cybersole.Core.Store;
using Cybersole.Services;
using Xunit;

namespace Cybersole.Tests;

public class SmartActionTests
{
    private static CheckoutEvent Evt(bool success = true, string store = "shopify", string price = "180.00")
        => new(store, "Air Max 1", "10", price, success, success ? "A123" : null, "Profile 1");

    [Fact]
    public void Matches_Without_Filters_Always_True()
    {
        var engine = CreateEngine(out _);
        var rule = new SmartAction();
        Assert.True(engine.Matches(rule, Evt()));
    }

    [Fact]
    public void Matches_Respects_Store_Filter()
    {
        var engine = CreateEngine(out _);
        var rule = new SmartAction { StoreFilter = "nike" };
        Assert.False(engine.Matches(rule, Evt(store: "shopify")));
        Assert.True(engine.Matches(rule, Evt(store: "nike")));
    }

    [Fact]
    public void Matches_Respects_MinPrice()
    {
        var engine = CreateEngine(out _);
        var rule = new SmartAction { MinPrice = 200m };
        Assert.False(engine.Matches(rule, Evt(price: "180.00")));
        Assert.True(engine.Matches(rule, Evt(price: "250.00")));
    }

    [Fact]
    public async Task Execute_Notification_Records_History()
    {
        var engine = CreateEngine(out var bus);
        var rule = new SmartAction
        {
            Name = "notify-me",
            Kind = SmartActionKind.Notification,
            Trigger = SmartTrigger.CheckoutSuccess,
        };

        await engine.ExecuteAsync(rule, Evt());
        Assert.Single(engine.History);
        Assert.True(engine.History[0].Executed);
        Assert.Equal("notify-me", engine.History[0].RuleName);
    }

    [Fact]
    public async Task Execute_Webhook_With_Empty_Target_Records_Failure()
    {
        var engine = CreateEngine(out _);
        var rule = new SmartAction { Name = "bad-hook", Kind = SmartActionKind.Webhook, Target = "" };

        await engine.ExecuteAsync(rule, Evt());
        Assert.Single(engine.History);
        Assert.False(engine.History[0].Executed);
        Assert.NotNull(engine.History[0].Error);
    }

    [Fact]
    public void Checkout_Event_Triggers_Matching_Rules()
    {
        var engine = CreateEngine(out var bus, cfg =>
        {
            cfg.SmartActions.Actions.Add(new SmartAction
            {
                Name = "on-success",
                Trigger = SmartTrigger.CheckoutSuccess,
                Kind = SmartActionKind.Notification,
            });
            cfg.SmartActions.Actions.Add(new SmartAction
            {
                Name = "on-decline",
                Trigger = SmartTrigger.Decline,
                Kind = SmartActionKind.Notification,
            });
        });

        bus.RaiseCheckout(Evt(success: true));
        Thread.Sleep(150); // fire-and-forget execution
        Assert.Contains(engine.History, h => h.RuleName == "on-success");
        Assert.DoesNotContain(engine.History, h => h.RuleName == "on-decline");
    }

    [Fact]
    public void SmartAction_Logs_Is_Settable_And_RoundTrips()
    {
        var rule = new SmartAction
        {
            Name = "with-logs",
            Logs = new List<string> { "line-1", "line-2" },
        };

        var json = Cybersole.Core.Store.Json.Serialize(rule);
        var restored = Cybersole.Core.Store.Json.Deserialize<SmartAction>(json);

        Assert.NotNull(restored);
        Assert.Equal(new[] { "line-1", "line-2" }, restored!.Logs);
    }

    private static SmartActionEngine CreateEngine(out EventBus bus, Action<ConfigurationStore>? setup = null)
    {
        bus = new EventBus();
        var config = new ConfigurationStore();
        config.Load();
        setup?.Invoke(config);
        var http = new Cybersole.Http.NetClient();
        var notify = new NotificationService(bus, config.Settings, http);
        return new SmartActionEngine(config, bus, notify, http);
    }
}
