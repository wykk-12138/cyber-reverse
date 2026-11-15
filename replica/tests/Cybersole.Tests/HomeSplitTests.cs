using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R221: the Home page's two-pane split. Measured on the running build at two window widths by reading the panel
/// borders off the screen:
///
/// <code>
///   window 1568:  Checkouts 973 px   gutter 23   Checkout Feed 521 px    ratio 1.865
///   window 1375:  Checkouts 845 px   gutter 29   Checkout Feed 453 px    ratio 1.867
/// </code>
///
/// <para>
/// Same proportion at both widths → star sizing, at about 1.87 : 1 with a 24 px gutter. The replica shipped
/// <c>"2*,8,1*"</c>: the checkout panel was ~7% too wide and the gutter too thin, and nothing in the file said the
/// numbers were a guess.
/// </para>
/// </summary>
public sealed class HomeSplitTests
{
    private readonly ITestOutputHelper _out;
    public HomeSplitTests(ITestOutputHelper output) => _out = output;

    private static string Analytics() => File.ReadAllText(Path.Combine(Root(),
        "src", "Cybersole.Ui", "Views", "Analytics", "AnalyticsViews.cs"));

    [Fact]
    public void TheTwoPanesAreTheMeasuredRatio()
    {
        var match = Regex.Match(Analytics(), @"ColumnDefinitions = new ColumnDefinitions\(""(?<v>[^""]+)""\)");
        Assert.True(match.Success, "Home grid template not found");

        var parts = match.Groups["v"].Value.Split(',');
        _out.WriteLine(string.Join(" | ", parts));
        Assert.Equal(3, parts.Length);

        Assert.Equal("1.87*", parts[0].Trim());
        Assert.Equal("24", parts[1].Trim());
        Assert.Equal("1*", parts[2].Trim());
    }

    [Fact]
    public void TheMeasurementIsWrittenNextToTheNumber()
    {
        var source = Analytics();

        // a future reader must be able to tell these numbers from the ones that were invented
        Assert.Contains("measured at two window widths", source);
        Assert.Contains("1.865", source);
        Assert.Contains("1.867", source);
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }
}
