using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R218: the Tasks table's column proportions. Measured by reading the header label left edges off the running build at
/// two window widths and normalising:
///
/// <code>
///   width 1568:  Site 204  Product 384  Profile 191  Proxies 168
///   width 1375:  Site 165  Product 311  Profile 155  Proxies 136
///   ratio       :  1.21       2.29         1.14        1.00
/// </code>
///
/// <para>
/// The replica shipped 1.3 / 2.2 / 1.2 / 1.2 — Site and Proxies were both about 10% off, and nothing in the code said
/// the numbers were guesses. The last column is deliberately not asserted: with no rows it absorbs the remainder, so
/// its measured width is leftover space rather than a design value.
/// </para>
/// </summary>
public sealed class TaskGridColumnTests
{
    private readonly ITestOutputHelper _out;
    public TaskGridColumnTests(ITestOutputHelper output) => _out = output;

    private static string Grid() => File.ReadAllText(Path.Combine(Root(),
        "src", "Cybersole.Ui", "Views", "Tasks", "TaskGrid.cs"));

    [Fact]
    public void TheFourLeadingProportionsAreTheMeasuredOnes()
    {
        var match = Regex.Match(Grid(), @"RowColumns = ""34,(.+?),90"";");
        Assert.True(match.Success, "RowColumns template not found");

        var parts = match.Groups[1].Value.Split(',')
            .Select(p => p.Trim())
            .ToList();

        _out.WriteLine(string.Join(" | ", parts));
        Assert.Equal(5, parts.Count);

        // Site, Product, Profile, Proxies — the measured ratios, in order
        Assert.Equal("1.21*", parts[0]);
        Assert.Equal("2.29*", parts[1]);
        Assert.Equal("1.14*", parts[2]);
        Assert.Equal("1.0*", parts[3]);
    }

    [Fact]
    public void TheLastColumnStaysAnEstimateAndTheCodeSaysSo()
    {
        var source = Grid();

        // the reason Status cannot be measured from an empty table is written where the number lives
        Assert.Contains("absorbs the remainder", source);
        Assert.Contains("cannot be inferred", source);
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }
}
