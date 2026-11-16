using System;
using System.Collections.Generic;
using Cybersole.Core.Reporting;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Behaviour probes for <see cref="RelativeTime"/>, which reimplements <c>sub_1410E2B60</c>.
///
/// The expectations come from two independent places, and neither is this implementation:
///   * the branch structure read out of the decompilation (whole days, then hours, then minutes, each with a
///     <c>&gt;1</c> and a <c>==1</c> arm, then the fallthrough);
///   * the seven <c>TimeAgo.*</c> strings the shipped catalogue actually contains.
///
/// The boundary cases are the point. A formatter that returns the right text for "5 hours ago" is easy; one that
/// switches arm at the wrong tick is wrong only at the boundary, and the decompiled comparisons are strict
/// (<c>&gt; 1</c> and <c>== 1</c>), so exactly-one-day must take the singular arm and one day plus an hour must not.
/// </summary>
public class RelativeTimeTests
{
    private readonly ITestOutputHelper _out;

    public RelativeTimeTests(ITestOutputHelper output) => _out = output;

    /// <summary>The shipped English catalogue entries this formatter can produce.</summary>
    private static readonly Dictionary<string, string> Copy = new(StringComparer.Ordinal)
    {
        ["TimeAgo.DaysAgoFormat"] = "{0} days ago",
        ["TimeAgo.OneDayAgo"] = "1 day ago",
        ["TimeAgo.HoursAgoFormat"] = "{0} hours ago",
        ["TimeAgo.OneHourAgo"] = "1 hour ago",
        ["TimeAgo.MinutesAgoFormat"] = "{0} mins ago",
        ["TimeAgo.OneMinuteAgo"] = "1 min ago",
        ["TimeAgo.JustNow"] = "just now",
    };

    private static string Describe(TimeSpan elapsed) => RelativeTime.Describe(elapsed, k => Copy[k]);

    [Theory]
    // the fallthrough: less than one whole minute
    [InlineData(0, "just now")]
    [InlineData(1, "just now")]
    [InlineData(59, "just now")]
    // exactly one minute takes the singular arm; the comparison is == 1, not >= 1
    [InlineData(60, "1 min ago")]
    [InlineData(119, "1 min ago")]
    // two whole minutes crosses into the plural arm
    [InlineData(120, "2 mins ago")]
    [InlineData(59 * 60, "59 mins ago")]
    public void MinutesBucket(int seconds, string expected)
    {
        _out.WriteLine("seconds=" + seconds);
        Assert.Equal(expected, Describe(TimeSpan.FromSeconds(seconds)));
    }

    [Theory]
    [InlineData(3600, "1 hour ago")]          // exactly one hour
    [InlineData(7199, "1 hour ago")]          // one hour fifty-nine minutes
    [InlineData(7200, "2 hours ago")]         // two whole hours
    [InlineData(86399, "23 hours ago")]       // one tick short of a day
    public void HoursBucket(int seconds, string expected)
    {
        _out.WriteLine("seconds=" + seconds);
        Assert.Equal(expected, Describe(TimeSpan.FromSeconds(seconds)));
    }

    [Theory]
    [InlineData(86400, "1 day ago")]                  // exactly one day
    [InlineData(2 * 86400 - 1, "1 day ago")]          // one tick short of two days
    [InlineData(2 * 86400, "2 days ago")]             // two whole days
    [InlineData(47 * 3600, "1 day ago")]              // 1d 23h stays in the singular arm
    [InlineData(30 * 86400, "30 days ago")]
    public void DaysBucket(int seconds, string expected)
    {
        _out.WriteLine("seconds=" + seconds);
        Assert.Equal(expected, Describe(TimeSpan.FromSeconds(seconds)));
    }

    [Fact]
    // The decompiled day step truncates, so a duration of 1.9 days reports one day rather than rounding to two.
    public void TheDayStepTruncatesRatherThanRounds()
    {
        Assert.Equal("1 day ago", Describe(TimeSpan.FromHours(45)));
        Assert.Equal("2 days ago", Describe(TimeSpan.FromHours(49)));
    }

    [Fact]
    // v4 is a subtraction of two tick values; nothing in the decompiled chain clamps it, but a negative remaining
    // time is not a duration "ago" and every arm would be taken by the fallthrough anyway.
    public void ANegativeDurationReportsJustNow()
    {
        Assert.Equal("just now", Describe(TimeSpan.FromMinutes(-5)));
    }

    [Fact]
    // A catalogue entry with no placeholder must not throw: the original passes an argument to a format helper, but
    // string.Format would raise on a brace-free template, and a localisation slip should not crash a list column.
    public void ACountedKeyWithoutAPlaceholderReturnsItsTextUnchanged()
    {
        var copy = new Dictionary<string, string>(Copy, StringComparer.Ordinal)
        {
            ["TimeAgo.HoursAgoFormat"] = "hours ago",
        };
        Assert.Equal("hours ago", RelativeTime.Describe(TimeSpan.FromHours(5), k => copy[k]));
    }

    [Fact]
    public void EveryProducedStringComesFromOneOfTheSevenKeys()
    {
        var seen = new HashSet<string>(StringComparer.Ordinal);
        foreach (var seconds in new[] { 0, 60, 120, 3600, 7200, 86400, 172800 })
        {
            var text = Describe(TimeSpan.FromSeconds(seconds));
            Assert.Contains(text, new[]
            {
                "just now", "1 min ago", "2 mins ago", "1 hour ago", "2 hours ago", "1 day ago", "2 days ago",
            });
            seen.Add(text);
        }

        Assert.Equal(7, seen.Count);
    }
}
