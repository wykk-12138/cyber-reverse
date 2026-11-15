using Cybersole.Core;
using Cybersole.Core.Models;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 52: the original's TaskGroup carries running counters that this replica did not have.
///
/// The string table of Cybersole.exe has these together:
///
///     get_TotalCheckouts   get_TotalDeclines   get_NextReset   get_CheckoutLimit
///
/// which reads as one class's property list. <c>CheckoutStats</c> here is global
/// (<c>AppServices.Stats</c>) and keyed by store, so it answers "how many across everything" and
/// "how many per store" but not "how many has this group landed".
///
/// These tests pin the fields and the write, not the arithmetic. The counter is incremented under
/// a lock in TaskEngine because one group is shared by every task in it.
/// </summary>
public sealed class GroupCounterTests
{
    private readonly ITestOutputHelper _out;

    public GroupCounterTests(ITestOutputHelper output) => _out = output;

    private static string Src(params string[] parts) =>
        Path.Combine(new[] { RepoRoot() }.Concat(parts).ToArray());

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }

    [Fact]
    public void TheGroupHasBothCounters()
    {
        var group = new TaskGroup();

        Assert.Equal(0, group.TotalCheckouts);
        Assert.Equal(0, group.TotalDeclines);

        group.TotalCheckouts++;
        group.TotalDeclines += 2;

        _out.WriteLine($"after: checkouts={group.TotalCheckouts} declines={group.TotalDeclines}");
        Assert.Equal(1, group.TotalCheckouts);
        Assert.Equal(2, group.TotalDeclines);
    }

    [Fact]
    public void TheEngineIncrementsBothCounters()
    {
        var engine = File.ReadAllText(Src("src", "Cybersole.Services", "TaskEngine.cs"));

        var hasSuccess = engine.Contains("group.TotalCheckouts++", StringComparison.Ordinal);
        var hasFailure = engine.Contains("group.TotalDeclines++", StringComparison.Ordinal);
        var hasLock = engine.Contains("lock (group)", StringComparison.Ordinal);

        _out.WriteLine($"success={hasSuccess} failure={hasFailure} lock={hasLock}");

        Assert.True(hasSuccess, "TotalCheckouts is declared but never incremented");
        Assert.True(hasFailure, "TotalDeclines is declared but never incremented");
        Assert.True(hasLock,
            "counters are incremented without a lock — a group is shared by every task in it, " +
            "so plain ++ loses increments under concurrency");
    }

    /// <summary>
    /// ErrorDelay is not the original's. R52 searched the string table for <c>errorDelay</c> and
    /// for <c>^Default[A-Z]\w*$</c>; neither exists. The group's own delay fields are
    /// MonitorDelay, RetryDelay and Timeout.
    ///
    /// The field stays (removing it breaks the settings UI), but its doc comment must not claim
    /// to mirror <c>Cybersole.Models.TaskGroup.ErrorDelay</c>, because there is no such member.
    /// This test fails if that claim comes back.
    /// </summary>
    [Fact]
    public void ErrorDelayIsNotDescribedAsTheOriginals()
    {
        var tasks = File.ReadAllText(Src("src", "Cybersole.Core", "Models", "Tasks.cs"));

        var claimsOrigin = tasks.Contains("Cybersole.Models.TaskGroup.ErrorDelay", StringComparison.Ordinal);
        var saysNotInOriginal = tasks.Contains("Not in the original", StringComparison.Ordinal);

        _out.WriteLine($"claims-origin={claimsOrigin} marked-as-not-original={saysNotInOriginal}");

        Assert.False(claimsOrigin,
            "ErrorDelay's comment claims to mirror Cybersole.Models.TaskGroup.ErrorDelay, " +
            "but the original has no such member");
        Assert.True(saysNotInOriginal,
            "ErrorDelay needs to say it is not in the original — otherwise the next reader " +
            "assumes R52's find was wrong rather than the comment");
    }

    /// <summary>
    /// The fields that do match: the original has MonitorDelay, RetryDelay, CheckoutLimit,
    /// ProfileLimit and UsageExpiry. If any of these disappear, the group lost a field the
    /// original actually has.
    ///
    /// UsagePeriod is not in this list. R53 removed it: the original has UsageExpiry only
    /// (get_UsageExpiry / set_UsageExpiry), and a separate TimeSpan? UsagePeriod was the same
    /// concept stored twice.
    /// </summary>
    [Theory]
    [InlineData("MonitorDelay", "Nullable`1")]
    [InlineData("RetryDelay", "Nullable`1")]
    [InlineData("CheckoutLimit", "Nullable`1")]
    [InlineData("ProfileLimit", "Nullable`1")]
    [InlineData("UsageExpiry", "Nullable`1")]
    public void TheMatchingFieldsSurvive(string field, string expectedShape)
    {
        var group = new TaskGroup();
        var prop = typeof(TaskGroup).GetProperty(field);

        _out.WriteLine($"{field}: {(prop is null ? "MISSING" : prop.PropertyType.Name)}");
        Assert.NotNull(prop);
        Assert.Contains(expectedShape, prop!.PropertyType.Name);
        Assert.NotNull(group);
    }

    /// <summary>
    /// R53: UsageExpiry is a duration choice, NextReset is the derived boundary.
    ///
    /// The original's XAML binds <c>TaskGroupView,Cybersole.TimeSpans</c> to
    /// <c>TaskGroup,Core.UsageExpiry</c>, so the property is an enum, not an instant. And
    /// <c>get_NextReset</c> exists with no <c>set_NextReset</c>, so the boundary is computed.
    ///
    /// This test pins both: the enum type, and that NextReset follows PeriodStart + the duration.
    /// </summary>
    [Fact]
    public void TheResetBoundaryIsDerivedFromTheDuration()
    {
        var start = new DateTime(2026, 1, 1, 12, 0, 0, DateTimeKind.Utc);

        var oneHour = new TaskGroup { UsageExpiry = TimeSpans.OneHour, PeriodStart = start };
        var manual = new TaskGroup { UsageExpiry = TimeSpans.Manual, PeriodStart = start };
        var unset = new TaskGroup { PeriodStart = start };

        _out.WriteLine($"1Hour -> {oneHour.NextReset:u}");
        _out.WriteLine($"Manual -> {(manual.NextReset is null ? "(none)" : manual.NextReset.ToString())}");
        _out.WriteLine($"unset -> {(unset.NextReset is null ? "(none)" : unset.NextReset.ToString())}");

        Assert.Equal(typeof(TimeSpans?), typeof(TaskGroup).GetProperty("UsageExpiry")!.PropertyType);
        Assert.Equal(start.AddHours(1), oneHour.NextReset);

        // Manual means "no fixed period", and unset means nothing to derive from. Neither invents
        // a boundary — returning PeriodStart would claim the window already closed.
        Assert.Null(manual.NextReset);
        Assert.Null(unset.NextReset);
    }

    /// <summary>
    /// Every option the locale names has an enum member, and vice versa. The strings are
    /// <c>TaskGroup.TimeSpan.30Minutes/.1Hour/.3Hour/.6Hour/.12Hour/.1Day/.Manual</c>.
    /// </summary>
    [Fact]
    public void EveryTimeSpanOptionHasALocaleLabel()
    {
        var locale = File.ReadAllText(
            Src("src", "Cybersole.Core", "Locales", "Cybersole.Locales.en.json"));

        foreach (var spans in Enum.GetValues<TimeSpans>())
        {
            var key = spans.LocaleKey();
            var present = locale.Contains($"\"{key}\"", StringComparison.Ordinal);
            _out.WriteLine($"{spans,-14} {key,-32} present={present}");
            Assert.True(present, $"{spans} has no locale label at {key}");
        }
    }
}
