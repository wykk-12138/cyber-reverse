using System;
using Cybersole.Stores;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1235: the Waitwhile queue surface, decoded from four functions the replica had never mentioned.
///
/// <para>
/// Before this round <c>waitwhile</c> returned no match anywhere under <c>replica/src</c> or <c>replica/tests</c>,
/// while the image carries three hosts and a slot query for it. The three host constants and the query are observed
/// literals; the fixed ceiling of 150 and the start-of-day suffix are read straight off the literals rather than
/// chosen, which is why the builder takes only the location and the two dates.
/// </para>
/// </summary>
public sealed class WaitwhileQueueTests
{
    [Fact]
    public void TheSlotUrlIsTheImagesOwnShape()
    {
        var url = WaitwhileQueue.FirstAvailableSlotsUrl("loc_1",
            new DateTime(2026, 11, 20), new DateTime(2026, 11, 27));

        Assert.Equal(
            "https://api.waitwhile.com/v2/public/visits/loc_1" +
            "/first-available-slots?fromDate=2026-11-20T00:00&toDate=2026-11-27T00:00&maxNumSlots=150",
            url);
    }

    [Fact]
    public void TheThreeHostsAreTheImagesOwn()
    {
        Assert.Equal("https://api.waitwhile.com/v2/public/visits/", WaitwhileQueue.VisitsHost);
        Assert.Equal("https://api.waitwhile.com/v2/public/locations/", WaitwhileQueue.LocationsHost);
        Assert.Equal("https://api.waitwhile.com/v2/public/data-fields/", WaitwhileQueue.DataFieldsHost);
    }

    [Fact]
    public void BothBoundsAreStartOfDayBecauseTheSuffixIsALiteral()
    {
        Assert.Equal("2026-01-02T00:00", WaitwhileQueue.Day(new DateTime(2026, 1, 2, 17, 45, 0)));
    }

    [Fact]
    public void TheCeilingIsTheLiteralNotACallerChoice()
    {
        Assert.Equal(150, WaitwhileQueue.MaxSlots);
    }

    [Fact]
    public void TheLocationIdIsEscaped()
    {
        Assert.Contains("/a%2Fb/first-available-slots",
            WaitwhileQueue.FirstAvailableSlotsUrl("a/b", DateTime.Today, DateTime.Today));
    }
}
