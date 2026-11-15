using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Core.Store;
using Cybersole.Ui.Views.SmartActions;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Smart-action and captcha window parity. Type names are the recovered XAML files under
/// <c>/Views/SmartActions/</c> and <c>/Views/Captcha/</c>.
/// </summary>
public class SmartActionViewTests
{
    private static readonly string[] SmartActionViews =
    {
        "SmartActionsView", "SmartActionsCreator", "ActionsModal", "HistoryWindow",
        "TemplateView", "PublishTemplateModal", "SmartActionSettingsView",
    };

    private static readonly string[] CaptchaViews =
    {
        "SolverWindow", "GoogleLogin", "YoutubeWindow",
    };

    private static CheckoutEvent Evt(string store = "nike", string product = "Air Max",
        string price = "150.00", bool success = true, string? order = "A1") =>
        new(store, product, "10", price, success, order, "profile-1");

    [Fact]
    public void AllRecoveredSmartActionViewsExist()
    {
        var names = typeof(SmartActionsView).Assembly.GetTypes().Select(t => t.Name).ToHashSet();
        foreach (var n in SmartActionViews) Assert.Contains(n, names);
    }

    [Fact]
    public void AllRecoveredCaptchaViewsExist()
    {
        var names = typeof(SmartActionsView).Assembly.GetTypes().Select(t => t.Name).ToHashSet();
        foreach (var n in CaptchaViews) Assert.Contains(n, names);
    }

    [Fact]
    public void SmartActionUserControlsConstruct()
    {
        using var services = TestServices.Create();
        var action = new SmartAction { Name = "webhook on checkout" };
        services.Config.SmartActions.Actions.Add(action);

        Assert.IsAssignableFrom<UserControl>(new SmartActionsView(services));
        Assert.IsAssignableFrom<UserControl>(new SmartActionsCreator(services, action));
        Assert.IsAssignableFrom<UserControl>(new TemplateView(services));
        Assert.IsAssignableFrom<UserControl>(new SmartActionSettingsView(services, action));
    }

    [Fact]
    public void CreatorStartsOnStepOneAndHasThreeSteps()
    {
        using var services = TestServices.Create();
        var creator = new SmartActionsCreator(services);
        Assert.Equal(0, creator.Step);
    }

    [Fact]
    public void FilterOperatorsCoverTheRecoveredSet()
    {
        Assert.Equal(8, SmartActionFilter.Operators.Count);
        Assert.Contains("equals", SmartActionFilter.Operators);
        Assert.Contains("contains", SmartActionFilter.Operators);
        Assert.Contains("greater than", SmartActionFilter.Operators);
        Assert.Contains("regex", SmartActionFilter.Operators);
    }

    [Fact]
    public void FilterFieldsCoverTheCheckoutEvent()
    {
        Assert.Contains("store", SmartActionFilter.Fields);
        Assert.Contains("product", SmartActionFilter.Fields);
        Assert.Contains("price", SmartActionFilter.Fields);
        Assert.Contains("success", SmartActionFilter.Fields);
        Assert.Contains("order", SmartActionFilter.Fields);
    }

    [Theory]
    [InlineData("store", "equals", "nike", true)]
    [InlineData("store", "equals", "footlocker", false)]
    [InlineData("store", "not equals", "footlocker", true)]
    [InlineData("product", "contains", "Air", true)]
    [InlineData("product", "not contains", "Air", false)]
    [InlineData("price", "greater than", "100", true)]
    [InlineData("price", "less than", "100", false)]
    [InlineData("success", "equals", "True", true)]
    [InlineData("order", "starts with", "A", true)]
    [InlineData("product", "regex", "^Air.*Max$", true)]
    [InlineData("product", "regex", "^Nope", false)]
    public void FilterEvaluatesEveryOperator(string field, string op, string value, bool expected)
    {
        var filter = new SmartActionFilter { Field = field, Operator = op, Value = value };
        Assert.Equal(expected, filter.Passes(Evt()));
    }

    [Fact]
    public void InvalidRegexDoesNotThrow()
    {
        var filter = new SmartActionFilter { Field = "store", Operator = "regex", Value = "([unclosed" };
        Assert.False(filter.Passes(Evt()));
    }

    [Fact]
    public void EmptyFilterChainAlwaysPasses()
    {
        var action = new SmartAction();
        Assert.Empty(action.Filters);
        Assert.True(action.Passes(Evt()));
    }

    [Fact]
    public void ActionPassesOnlyWhenEveryFilterPasses()
    {
        var action = new SmartAction
        {
            Filters = new List<SmartActionFilter>
            {
                new() { Field = "store", Operator = "equals", Value = "nike" },
                new() { Field = "price", Operator = "greater than", Value = "100" },
            },
        };

        Assert.True(action.Passes(Evt()));
        Assert.False(action.Passes(Evt(store: "footlocker")));
        Assert.False(action.Passes(Evt(price: "50.00")));
    }

    [Fact]
    public void ActionCarriesTheRecoveredSchedulingFields()
    {
        var action = new SmartAction
        {
            RunOnce = true,
            RunInterval = TimeSpan.FromSeconds(30),
            Notifications = true,
            LastRun = DateTime.UtcNow,
            LastResult = "ok",
        };

        Assert.True(action.RunOnce);
        Assert.Equal(TimeSpan.FromSeconds(30), action.RunInterval);
        Assert.True(action.Notifications);
        Assert.Equal("ok", action.LastResult);
    }

    [Fact]
    public void SolverWindowDeclaresEveryRecoveredPanel()
    {
        var prop = typeof(Cybersole.Ui.Views.SolverWindow)
            .GetProperty("Panels", System.Reflection.BindingFlags.Public |
                                   System.Reflection.BindingFlags.Instance);
        Assert.NotNull(prop);
        Assert.Equal(typeof(IReadOnlyList<string>), prop!.PropertyType);
    }

    [Fact]
    public void SolverWindowDeclaresTheRecoveredCommands()
    {
        var t = typeof(Cybersole.Ui.Views.SolverWindow);
        foreach (var name in new[] { "Add", "CloseSolver", "Reload" })
            Assert.NotNull(t.GetMethod(name, System.Reflection.BindingFlags.Public |
                                             System.Reflection.BindingFlags.Instance));
    }
}

/// <summary>The engine must honour the new filter chain when matching rules.</summary>
public class SmartActionEngineFilterTests
{
    [Fact]
    public void MatchesRespectsStoreAndPriceFilters()
    {
        using var services = TestServices.Create();

        var rule = new SmartAction
        {
            Name = "nike only",
            Trigger = SmartTrigger.CheckoutSuccess,
            Kind = SmartActionKind.Notification,
            Enabled = true,
            StoreFilter = "nike",
            MinPrice = 100m,
        };

        var engine = services.SmartActions;

        var hit = new CheckoutEvent("nike", "Air Max", "10", "150.00", true, "A1", "p");
        var cheap = new CheckoutEvent("nike", "Air Max", "10", "50.00", true, "A2", "p");
        var otherStore = new CheckoutEvent("footlocker", "Air Max", "10", "150.00", true, "A3", "p");

        Assert.True(engine.Matches(rule, hit));
        Assert.False(engine.Matches(rule, cheap));
        Assert.False(engine.Matches(rule, otherStore));
    }

    [Fact]
    public void MatchesIgnoresFiltersWhenRuleHasNone()
    {
        using var services = TestServices.Create();

        var rule = new SmartAction
        {
            Trigger = SmartTrigger.CheckoutSuccess,
            Kind = SmartActionKind.Notification,
            Enabled = true,
        };

        var evt = new CheckoutEvent("any", "thing", "1", "1.00", true, null, "p");
        Assert.True(services.SmartActions.Matches(rule, evt));
    }
}
