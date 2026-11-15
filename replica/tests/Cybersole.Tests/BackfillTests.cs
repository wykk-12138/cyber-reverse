using Cybersole.Core.Models;
using Cybersole.Core.Store;
using Cybersole.Ui.Views.Analytics;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R10 back-fills: the cartesian task builder, real RunOnce/RunInterval throttling, and
/// period slicing for the analytics page.
/// </summary>
public class TaskCombinationTests
{
    private static TaskCombinationRequest Request(params string[] sizes) => new()
    {
        Store = "Nike",
        Url = "https://www.nike.com/launch/t/air-max",
        Sizes = sizes.ToList(),
        Profiles = new List<string> { "profile-1", "profile-2" },
        ProxyGroupIds = new List<string> { "pg-1", "pg-2" },
    };

    [Fact]
    public void MultipliesSizesByProfiles()
    {
        var tasks = TaskCombinationBuilder.Build(Request("9", "10", "10.5"));
        Assert.Equal(6, tasks.Count);
    }

    [Fact]
    public void SingleSizeSingleProfileMakesOneTask()
    {
        var request = new TaskCombinationRequest
        {
            Store = "Nike",
            Sizes = new List<string> { "10" },
            Profiles = new List<string> { "p1" },
        };

        var tasks = TaskCombinationBuilder.Build(request);
        Assert.Single(tasks);
        Assert.Equal("Nike", tasks[0].Store);
        Assert.Equal("10", tasks[0].Product.Sizes[0]);
        Assert.Equal("p1", tasks[0].ProfileId);
    }

    [Fact]
    public void EmptySelectionsCollapseToOneDefault()
    {
        var tasks = TaskCombinationBuilder.Build(new TaskCombinationRequest { Store = "Nike" });
        Assert.Single(tasks);
        Assert.Null(tasks[0].ProfileId);
        Assert.Empty(tasks[0].Product.Sizes);
    }

    [Fact]
    public void MultiCartRepeatsQuantityPerProfile()
    {
        var request = Request("10");
        request = new TaskCombinationRequest
        {
            Store = request.Store,
            Url = request.Url,
            Sizes = request.Sizes,
            Profiles = new List<string> { "p1" },
            QuantityPerProfile = 3,
            MultiCart = true,
        };

        var tasks = TaskCombinationBuilder.Build(request);
        Assert.Equal(3, tasks.Count);
    }

    [Fact]
    public void WithoutMultiCartQuantityPerProfileIsIgnored()
    {
        var request = new TaskCombinationRequest
        {
            Store = "Nike",
            Sizes = new List<string> { "10" },
            Profiles = new List<string> { "p1" },
            QuantityPerProfile = 5,
            MultiCart = false,
        };

        Assert.Single(TaskCombinationBuilder.Build(request));
    }

    [Fact]
    public void ProxyGroupsAreDistributedRoundRobin()
    {
        var request = new TaskCombinationRequest
        {
            Store = "Nike",
            Sizes = new List<string> { "9", "10", "11", "12" },
            Profiles = new List<string> { "p1" },
            ProxyGroupIds = new List<string> { "pg-1", "pg-2" },
        };

        var tasks = TaskCombinationBuilder.Build(request);
        Assert.Equal(4, tasks.Count);
        Assert.Equal(new[] { "pg-1", "pg-2", "pg-1", "pg-2" },
            tasks.Select(t => t.ProxyGroupId).ToArray());
    }

    [Fact]
    public void NamesAreDistinctAndCarryTheSize()
    {
        var tasks = TaskCombinationBuilder.Build(Request("9", "10", "10.5"));
        var names = tasks.Select(t => t.Name).ToList();

        Assert.Equal(names.Count, names.Distinct().Count());
        Assert.Contains("9", names[0]);
        // sizes are the outer loop, profiles the inner one: index 4 is (10.5, profile-1)
        Assert.Contains("10.5", names[4]);
    }

    [Fact]
    public void CountMatchesBuild()
    {
        var request = Request("9", "10", "10.5");
        Assert.Equal(TaskCombinationBuilder.Build(request).Count, TaskCombinationBuilder.Count(request));
    }

    [Fact]
    public void CeilingPreventsRunawaySelections()
    {
        var request = new TaskCombinationRequest
        {
            Store = "Nike",
            Sizes = Enumerable.Range(1, 100).Select(i => i.ToString()).ToList(),
            Profiles = Enumerable.Range(1, 100).Select(i => "p" + i).ToList(),
        };

        Assert.Equal(TaskCombinationBuilder.MaxTasks, TaskCombinationBuilder.Count(request));
        Assert.Equal(TaskCombinationBuilder.MaxTasks, TaskCombinationBuilder.Build(request).Count);
    }

    [Fact]
    public void OptionalTimingFieldsPropagate()
    {
        var start = DateTime.UtcNow.AddMinutes(5);
        var request = new TaskCombinationRequest
        {
            Store = "Nike",
            Sizes = new List<string> { "10" },
            Profiles = new List<string> { "p1" },
            MonitorDelay = 750,
            RetryDelay = 1500,
            Timeout = 30,
            MonitorMode = true,
            PriceCheck = true,
            StartTime = start,
            CheckoutDelay = 250,
        };

        var task = TaskCombinationBuilder.Build(request)[0];
        Assert.Equal(750, task.MonitorDelay);
        Assert.Equal(1500, task.RetryDelay);
        Assert.Equal(30, task.Timeout);
        Assert.True(task.MonitorMode);
        Assert.True(task.Product.PriceCheck);
        Assert.Equal(start, task.StartTime);
        Assert.Equal(250, task.CheckoutDelay);
    }
}

public class SmartActionThrottleTests
{
    [Fact]
    public void RunOnceStopsAfterTheFirstRun()
    {
        using var services = TestServices.Create();
        var rule = new SmartAction { RunOnce = true };

        Assert.True(services.SmartActions.ShouldRun(rule));

        rule.LastRun = DateTime.UtcNow;
        Assert.False(services.SmartActions.ShouldRun(rule));
    }

    [Fact]
    public void RunIntervalBlocksUntilTheGapElapses()
    {
        using var services = TestServices.Create();
        var now = DateTime.UtcNow;
        var rule = new SmartAction
        {
            RunInterval = TimeSpan.FromSeconds(30),
            LastRun = now,
        };

        Assert.False(services.SmartActions.ShouldRun(rule, now.AddSeconds(10)));
        Assert.False(services.SmartActions.ShouldRun(rule, now.AddSeconds(29)));
        Assert.True(services.SmartActions.ShouldRun(rule, now.AddSeconds(31)));
    }

    [Fact]
    public void NoSchedulingFieldsMeansAlwaysRunnable()
    {
        using var services = TestServices.Create();
        Assert.True(services.SmartActions.ShouldRun(new SmartAction()));
    }
}

public class CheckoutStatsPeriodTests
{
    private static CheckoutEvent Evt(string store, string price, bool ok) =>
        new(store, "product", "10", price, ok, ok ? "A1" : null, "p1");

    [Fact]
    public void SummarizeCountsOnlyTheWindow()
    {
        using var services = TestServices.Create();

        // The stats service loads whatever history already exists on disk, so the window is
        // pinned to the exact instant of the two events instead of "the last 10 minutes".
        var from = DateTimeOffset.UtcNow;
        services.Bus.RaiseCheckout(Evt("nike", "150.00", true));
        services.Bus.RaiseCheckout(Evt("nike", "90.00", false));
        var to = DateTimeOffset.UtcNow.AddSeconds(1);

        var (total, success, failed, spent) = services.Stats.Summarize(from, to);

        Assert.Equal(2, total);
        Assert.Equal(1, success);
        Assert.Equal(1, failed);
        Assert.Equal(150.00m, spent);
    }

    [Fact]
    public void SummarizeIgnoresEventsOutsideTheWindow()
    {
        using var services = TestServices.Create();
        services.Bus.RaiseCheckout(Evt("nike", "150.00", true));

        var past = DateTimeOffset.UtcNow.AddDays(-2);
        var (total, _, _, _) = services.Stats.Summarize(past.AddHours(-1), past);

        Assert.Equal(0, total);
    }

    [Fact]
    public void ByStoreInPeriodGroupsPerStore()
    {
        using var services = TestServices.Create();

        var from = DateTimeOffset.UtcNow;
        services.Bus.RaiseCheckout(Evt("nike", "150.00", true));
        services.Bus.RaiseCheckout(Evt("nike", "150.00", false));
        services.Bus.RaiseCheckout(Evt("footlocker", "120.00", true));
        var to = DateTimeOffset.UtcNow.AddSeconds(1);

        var byStore = services.Stats.ByStoreInPeriod(from, to);

        Assert.Equal(1, byStore["nike"].Success);
        Assert.Equal(1, byStore["nike"].Failed);
        Assert.Equal(1, byStore["footlocker"].Success);
    }

    [Fact]
    public void BucketsAreNewestFirstAndSized()
    {
        using var services = TestServices.Create();
        services.Bus.RaiseCheckout(Evt("nike", "150.00", true));

        var buckets = services.Stats.Buckets(TimeSpan.FromMinutes(30), 6);
        Assert.Equal(6, buckets.Count);

        // newest bucket comes first and its window is in the past hour
        Assert.True(buckets[0].To >= buckets[0].From);
        Assert.True(buckets[0].To <= DateTimeOffset.UtcNow.AddSeconds(1));
        Assert.True(buckets[1].To <= buckets[0].From.AddSeconds(1));
    }

    /// <summary>
    /// R205: the period is a four-way selector, not a Previous/Next window — measured from the running build, where
    /// Today/Week/Month/Year sit above the checkout count and the two arrow buttons belong to the release carousel.
    /// </summary>
    [Fact]
    public void AnalyticsViewPeriodFollowsTheFourWaySelector()
    {
        using var services = TestServices.Create();
        var view = new AnalyticsView(services);

        // "Today" is the default and the window starts at one day, not one hour
        Assert.Equal("Today", view.SelectedPeriod);
        Assert.Equal(TimeSpan.FromDays(1), view.CurrentPeriod.To - view.CurrentPeriod.From);

        view.SetPeriod("Week");
        Assert.Equal(TimeSpan.FromDays(7), view.CurrentPeriod.To - view.CurrentPeriod.From);

        view.SetPeriod("Month");
        Assert.Equal(TimeSpan.FromDays(30), view.CurrentPeriod.To - view.CurrentPeriod.From);

        view.SetPeriod("Year");
        Assert.Equal(TimeSpan.FromDays(365), view.CurrentPeriod.To - view.CurrentPeriod.From);

        // an unknown name is ignored rather than narrowing the window to nothing
        view.SetPeriod("Yesterday");
        Assert.Equal("Year", view.SelectedPeriod);
    }
}
