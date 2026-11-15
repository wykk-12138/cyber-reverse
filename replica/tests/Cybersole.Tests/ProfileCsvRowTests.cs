using System.Collections.Generic;
using Cybersole.Ui.Views.Profiles.Modals;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R314: the five acceptance points from <c>docs/CONTROL_DESIGN_ProfileCsvRow.md</c>, as pure logic.
///
/// <para>
/// The image binds Number / FullySelected / RowStatus / RowError on Cybersole.Ui.Views.Profiles.Modals.ProfileCsvRow.
/// The point of the row is that the editor can say which line is wrong instead of only how many parsed, so the tests are
/// about the classification, not about layout.
/// </para>
/// </summary>
public sealed class ProfileCsvRowTests
{
    private readonly ITestOutputHelper _out;
    public ProfileCsvRowTests(ITestOutputHelper output) => _out = output;

    private static readonly Dictionary<string, int> Map = new()
    {
        ["First name"] = 0,
        ["Last name"] = 1,
        ["Address 1"] = 2,
    };

    [Fact]
    public void AFullRowIsFullySelectedAndHasNoError()
    {
        var row = new ProfileCsvRow(1, new[] { "Ada", "Lovelace", "12 St James's Sq" }, Map);
        _out.WriteLine(row.ToString());

        Assert.True(row.FullySelected);
        Assert.Equal(string.Empty, row.RowError);
        Assert.Contains("Ready", row.RowStatus);
    }

    [Fact]
    public void AMissingColumnNamesIt()
    {
        var row = new ProfileCsvRow(2, new[] { "Ada", "Lovelace", "" }, Map);
        _out.WriteLine(row.ToString());

        Assert.False(row.FullySelected);
        Assert.Contains("Address 1", row.RowError);
        Assert.Contains("2 of 3", row.RowStatus);
    }

    [Fact]
    public void AnEmptyRowSaysSo()
    {
        var row = new ProfileCsvRow(3, new[] { "", "  " }, Map);
        _out.WriteLine(row.ToString());

        Assert.False(row.FullySelected);
        Assert.Equal("Row is empty", row.RowError);
        Assert.Equal("Empty", row.RowStatus);
    }

    [Fact]
    public void TheNumberIsTheLineItCameFrom()
    {
        Assert.Equal(7, new ProfileCsvRow(7, new[] { "a", "b", "c" }, Map).Number);
    }

    [Fact]
    public void AnIndexOutsideTheRowCountsAsMissing()
    {
        var map = new Dictionary<string, int> { ["First name"] = 0, ["Phone"] = 9 };
        var row = new ProfileCsvRow(4, new[] { "Ada" }, map);
        _out.WriteLine(row.ToString());

        Assert.False(row.FullySelected);
        Assert.Contains("Phone", row.RowError);
    }
}
