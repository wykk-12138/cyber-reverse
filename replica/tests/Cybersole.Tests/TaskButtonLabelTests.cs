using System;
using System.Collections.Generic;
using Cybersole.Core.Reporting;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Behaviour probes for <see cref="TaskButtonLabel"/>, which reimplements <c>sub_140594500</c>.
///
/// The four branch texts come from the shipped catalogue; the branch that each input takes comes from the
/// decompiled comparisons. The one that matters is <see cref="AZeroCountTakesDifferentArmsInEachMode"/>: the save
/// arm tests <c>count == 1</c> and the create arm tests <c>count &gt;= 2</c>, so zero lands on the plural in one mode
/// and the singular in the other. An implementation that "tidies" that into <c>count &gt; 1</c> both ways produces the
/// right answer for every realistic input and the wrong one here.
/// </summary>
public class TaskButtonLabelTests
{
    private readonly ITestOutputHelper _out;

    public TaskButtonLabelTests(ITestOutputHelper output) => _out = output;

    private static readonly Dictionary<string, string> Copy = new(StringComparer.Ordinal)
    {
        ["TaskCreator.Button.CreateTask"] = "Create Task",
        ["TaskCreator.Button.CreateTasksFormat"] = "Create {0} Tasks",
        ["TaskCreator.Button.SaveTask"] = "Save Task",
        ["TaskCreator.Button.SaveTasksFormat"] = "Save {0} Tasks",
    };

    private static string Describe(bool saving, int count) => TaskButtonLabel.Describe(saving, count, k => Copy[k]);

    [Theory]
    [InlineData(false, 0, "Create Task")]      // create + zero: the create arm tests >= 2, so zero is singular
    [InlineData(false, 1, "Create Task")]
    [InlineData(false, 2, "Create 2 Tasks")]
    [InlineData(false, 7, "Create 7 Tasks")]
    public void CreateMode(bool saving, int count, string expected)
    {
        _out.WriteLine("create count=" + count);
        Assert.Equal(expected, Describe(saving, count));
    }

    [Theory]
    [InlineData(true, 0, "Save 0 Tasks")]      // save + zero: the save arm tests == 1, so zero is plural
    [InlineData(true, 1, "Save Task")]
    [InlineData(true, 2, "Save 2 Tasks")]
    [InlineData(true, 7, "Save 7 Tasks")]
    public void SaveMode(bool saving, int count, string expected)
    {
        _out.WriteLine("save count=" + count);
        Assert.Equal(expected, Describe(saving, count));
    }

    [Fact]
    /// The asymmetry the decompilation shows. A tidier-looking implementation gets this wrong.
    public void AZeroCountTakesDifferentArmsInEachMode()
    {
        Assert.Equal("Save 0 Tasks", Describe(saving: true, count: 0));
        Assert.Equal("Create Task", Describe(saving: false, count: 0));
    }

    [Fact]
    // The single-task texts carry no placeholder, so they must not go through string.Format.
    public void TheSingleTaskLabelsAreReturnedVerbatim()
    {
        Assert.Equal("Save Task", Describe(true, 1));
        Assert.Equal("Create Task", Describe(false, 1));
    }

    [Theory]
    [InlineData(-1)]
    [InlineData(-5)]
    // Nothing in the decompiled chain guards the sign. Save mode tests == 1 so a negative takes the plural; create
    // mode tests >= 2 so a negative takes the singular. Recorded because it is what the code does, not because a
    // negative count is meaningful.
    public void ANegativeCountFollowsTheSameComparisons(int count)
    {
        Assert.Equal(count == 1 ? "Save Task" : "Save " + count + " Tasks", Describe(true, count));
        Assert.Equal(count >= 2 ? "Create " + count + " Tasks" : "Create Task", Describe(false, count));
    }
}
