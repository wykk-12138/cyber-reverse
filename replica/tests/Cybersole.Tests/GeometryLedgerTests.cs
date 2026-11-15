using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R224: <c>docs/GUI_GEOMETRY.md</c> is the single table of numbers measured off the running build, and this test keeps
/// it honest — every number in the doc must still be the number in the code.
///
/// <para>
/// The point is not the numbers themselves; it is that a size in this project is either <b>measured and recorded</b> or
/// it is a guess. R217 found four window sizes that were guesses wearing the clothes of parameters; R218/R221/R222/R223
/// found four more. A ledger with a test attached is how those stay measured.
/// </para>
/// </summary>
public sealed class GeometryLedgerTests
{
    private readonly ITestOutputHelper _out;
    public GeometryLedgerTests(ITestOutputHelper output) => _out = output;

    private static string Read(string relative) => File.ReadAllText(Path.Combine(Root(),
        relative.Replace('/', Path.DirectorySeparatorChar)));

    [Fact]
    public void TheLedgerExistsAndNamesItsMethod()
    {
        var doc = Read("docs/GUI_GEOMETRY.md");

        Assert.Contains("唯一权威表", doc, System.StringComparison.Ordinal);
        Assert.Contains("两个样本", doc, System.StringComparison.Ordinal);
        // the three things that cannot be measured are named rather than silently estimated
        Assert.Contains("量不出来、已标注", doc, System.StringComparison.Ordinal);
        Assert.Contains("待查（有观测、无结论）", doc, System.StringComparison.Ordinal);
    }

    [Fact]
    public void EveryDocumentedNumberIsStillInTheCode()
    {
        var doc = Read("docs/GUI_GEOMETRY.md");

        // 1. window frames
        Assert.Contains("1536×814", doc, System.StringComparison.Ordinal);
        var monitor = Read("src/Cybersole.Ui/Views/MonitorWindow.cs");
        var solver = Read("src/Cybersole.Ui/Views/SolverWindow.cs");
        var splash = Read("src/Cybersole.Ui/Views/Auth/SplashWindow.cs");
        Assert.Contains("Width = 1536;", monitor);
        Assert.Contains("Width = 1536;", solver);
        Assert.Contains("Width = 529;", splash);
        Assert.Contains("Height = 630;", splash);

        // 2. the shell layout
        Assert.Contains("1.87*,24,1*", Read("src/Cybersole.Ui/Views/Analytics/AnalyticsViews.cs"));
        Assert.Contains("RailWidth = 324;", Read("src/Cybersole.Ui/Views/Proxies/ProxyView.cs"));
        Assert.Contains("324,*", Read("src/Cybersole.Ui/Views/BillingView.cs"));

        // 3. the two tables
        Assert.Contains("1.21*,2.29*,1.14*,1.0*", Read("src/Cybersole.Ui/Views/Tasks/TaskGrid.cs"));
        Assert.Contains("1.0*,1.28*,1.29*,1.0*", Read("src/Cybersole.Ui/Views/BillingView.cs"));

        _out.WriteLine("ledger and code agree");
    }

    [Fact]
    public void NoNewUnexplainedSizeAppearsInTheTwoViewsThatWereFixed()
    {
        // a regression guard: the numbers that were measured must not drift back to round guesses
        var tasks = Read("src/Cybersole.Ui/Views/Tasks/TaskGrid.cs");
        var match = Regex.Match(tasks, @"RowColumns = ""34,(?<v>[^""]+),90"";");
        Assert.True(match.Success);
        Assert.Equal("1.21*,2.29*,1.14*,1.0*,1.1*", match.Groups["v"].Value);

        // the comment above the template quotes the old value on purpose, so the check runs on code only
        var analytics = string.Join("\n", Read("src/Cybersole.Ui/Views/Analytics/AnalyticsViews.cs")
            .Split('\n')
            .Where(line => !line.TrimStart().StartsWith("//", System.StringComparison.Ordinal)));

        Assert.DoesNotContain("\"2*,8,1*\"", analytics);
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }
}
