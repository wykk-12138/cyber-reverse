using Avalonia.Controls;
using Cybersole.Ui.Views;
using Cybersole.Ui.Views.Analytics;
using Xunit;

namespace Cybersole.Tests;

/// <summary>R15: the analytics chart's timeline mode.</summary>
public class ChartTimelineTests
{
    [Fact]
    public void ChartStartsInPerStoreMode()
    {
        var chart = new StoreBarChart();
        Assert.False(chart.IsTimeline);
    }

    [Fact]
    public void UpdateTimelineSwitchesTheMode()
    {
        var chart = new StoreBarChart();
        chart.UpdateTimeline(new List<(DateTimeOffset, DateTimeOffset, int, int)>
        {
            (DateTimeOffset.UtcNow.AddHours(-1), DateTimeOffset.UtcNow, 5, 3),
        });

        Assert.True(chart.IsTimeline);
    }

    [Fact]
    public void UpdateSwitchesBackToPerStore()
    {
        var chart = new StoreBarChart();
        chart.UpdateTimeline(new List<(DateTimeOffset, DateTimeOffset, int, int)>
        {
            (DateTimeOffset.UtcNow.AddHours(-1), DateTimeOffset.UtcNow, 5, 3),
        });
        chart.Update(new Dictionary<string, (int, int)> { ["nike"] = (1, 0) });

        Assert.False(chart.IsTimeline);
    }

    [Fact]
    public void EmptyTimelineIsAcceptedWithoutThrowing()
    {
        var chart = new StoreBarChart();
        chart.UpdateTimeline(Array.Empty<(DateTimeOffset, DateTimeOffset, int, int)>());
        Assert.True(chart.IsTimeline);
    }

    [Fact]
    public void AnalyticsViewOffersFourCharts()
    {
        using var services = TestServices.Create();
        var view = new AnalyticsView(services);
        Assert.IsAssignableFrom<UserControl>(view);

        var field = typeof(AnalyticsView).GetField("Charts",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static);
        Assert.NotNull(field);

        var charts = field!.GetValue(null) as System.Collections.IEnumerable;
        Assert.NotNull(charts);

        var names = charts!.Cast<object>().Select(o => o?.ToString() ?? string.Empty).ToList();
        Assert.Equal(4, names.Count);
        Assert.Contains(names, c => c.Contains("Timeline", StringComparison.OrdinalIgnoreCase));
    }

    [Fact]
    public void BucketsFeedTheTimelineWithTwelveSlots()
    {
        using var services = TestServices.Create();
        var buckets = services.Stats.Buckets(TimeSpan.FromHours(1), 12);
        Assert.Equal(12, buckets.Count);

        var chart = new StoreBarChart();
        chart.UpdateTimeline(buckets);
        Assert.True(chart.IsTimeline);
    }
}
