using System.IO;
using System.Linq;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R217: the original's top-level window inventory, measured by polling the running process's window rects from the
/// moment of launch. Four windows plus the splash, and three of them share one frame:
///
/// <code>
/// vis   1429x892 at 310,110   'Cybersole'   the shell (resizable)
/// vis   1536x814 at  26, 26   'Login'
/// vis   1536x814 at  77, 77   'Solver'      created hidden up front
/// vis   1536x814 at 102,102   'Monitor'     created hidden up front
/// vis    529x630 at   …       'Cybersole'   the splash, before the shell opens
/// </code>
///
/// <para>
/// No amount of decompilation gave these numbers; they come from asking the running build. Every size the replica had
/// was invented, which is exactly the failure mode this test pins down: <b>a window size with no evidence is a guess,
/// and a guess with a comment that says "measured" is worse than a guess</b>.
/// </para>
/// </summary>
public sealed class WindowGeometryTests
{
    private readonly ITestOutputHelper _out;
    public WindowGeometryTests(ITestOutputHelper output) => _out = output;

    private static string Ui(string relative) =>
        File.ReadAllText(Path.Combine(Root(), "src", "Cybersole.Ui", "Views",
            relative.Replace('/', Path.DirectorySeparatorChar)));

    [Theory]
    [InlineData("MonitorWindow.cs", "Monitor")]
    [InlineData("SolverWindow.cs", "Solver")]
    public void ThePanelWindowsShareOneFrame(string file, string title)
    {
        var source = Ui(file);

        _out.WriteLine(file);
        Assert.Contains($"Title = \"{title}\";", source);
        Assert.Contains("Width = 1536;", source);
        Assert.Contains("Height = 814;", source);
    }

    [Fact]
    public void TheSplashIsTheMeasuredPortraitFrame()
    {
        var source = Ui("Auth/SplashWindow.cs");

        Assert.Contains("Width = 529;", source);
        Assert.Contains("Height = 630;", source);

        // and its title is the shell's own, which is why the window inventory shows two "Cybersole" windows
        Assert.Contains("Title = \"Cybersole\";", source);
    }

    [Fact]
    public void TheLoginIsHostedAtTheMeasuredFrameAndTitle()
    {
        var modal = Ui("Modals/CommonModals.cs");

        // measured: a window titled "Login", 1536x814 — not a 520x460 card called "Sign in"
        Assert.Contains("\"Login\", login, 1536, 814", modal);
        Assert.DoesNotContain("\"Sign in\", login", modal);
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }
}
