using System.Linq;
using Cybersole.Ui.Views.Analytics;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R205: the Home page, pinned to what the running build actually draws (snapshot s00000001, pid 189264,
/// window_id 10094414, image sha256:19844997c25be7857e146c866e84421f098304f61b31ffb48246f51d90289c44).
/// </summary>
public sealed class HomePageParityTests
{
    private readonly ITestOutputHelper _out;
    public HomePageParityTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheSegmentsAndPeriodsAreTheWindowsOwn()
    {
        // the two segments above the count, and the four periods beside them — read off the window, in that order
        Assert.Equal(new[] { "Checkouts", "Spend" }, AnalyticsView.Segments);
        Assert.Equal(new[] { "Today", "Week", "Month", "Year" }, AnalyticsView.Periods);
    }

    [Fact]
    public void TheThreeEmptyStatesAreVerbatim()
    {
        Assert.Equal("Nothing to see here", AnalyticsView.EmptyHeadline);
        Assert.Equal("You haven't made any checkouts for this period", AnalyticsView.EmptyPeriodBody);
        Assert.Equal("You haven't made any checkouts yet", AnalyticsView.EmptyFeedBody);

        // the apostrophes are the plain ASCII ones the window draws, not typographic quotes
        Assert.DoesNotContain('\u2019', AnalyticsView.EmptyPeriodBody);
        Assert.DoesNotContain('\u2019', AnalyticsView.EmptyFeedBody);
    }

    [Fact]
    public void ThePagerBelongsToTheReleasesNotThePeriod()
    {
        using var services = TestServices.Create();
        var view = new AnalyticsView(services);

        var before = view.CurrentPeriod;
        // R500: MoveNext / MovePrevious are ICommand properties now (the binding table asks for properties).
        view.MoveNext.Execute(null);
        view.MovePrevious.Execute(null);

        // moving the carousel must not move the time window: that was the mistake this round corrected
        Assert.Equal(before.From, view.CurrentPeriod.From);
        Assert.Equal(before.To, view.CurrentPeriod.To);

        // and the page never leaves 1..ReleasePages
        Assert.InRange(view.ReleasePage, 1, view.ReleasePages);
    }

    [Fact]
    public void TheSpendSegmentSaysMoneySpentAndPrintsADollarFigure()
    {
        // R335: measured on the running build — the caption is "Money Spent" (capital S) and the figure is "$0".
        Assert.Equal("Checkouts", AnalyticsView.SegmentCaption(0));
        Assert.Equal("Money Spent", AnalyticsView.SegmentCaption(1));
        Assert.Equal("$0", AnalyticsView.SpendFigure(0m));
    }

    [Fact]
    public void AnEmptyCarouselReadsZeroOfZeroAndSaysThereAreNoReleases()
    {
        // R334: measured on the running build with no data — "Releases < 0 / 0 >" and a two-line empty state.
        Assert.Equal("0 / 0", AnalyticsView.PagerCaption(1, 0));
        Assert.Equal("2 / 3", AnalyticsView.PagerCaption(2, 3));
        Assert.Equal("There are no upcoming releases", AnalyticsView.EmptyReleasesBody);
    }

    [Fact]
    public void TheFourChartsFromTheDecompiledClassSurvive()
    {
        // the source is the primary reference: ChangeChart takes four kinds, and the window shows two of them as
        // segments. Neither fact may delete the other.
        var field = typeof(AnalyticsView).GetField("Charts",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static);
        Assert.NotNull(field);
        var charts = (string[])field!.GetValue(null)!;

        Assert.Equal(4, charts.Length);
        _out.WriteLine(string.Join(", ", charts));
    }
}
