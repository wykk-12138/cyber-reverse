using System.IO;
using System.Linq;
using System.Text.Json;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R232: <c>MainWindow</c>'s bound vocabulary. The original binds
/// <c>Clock, Exit, Minimise, Navigate, OpenMonitor, OpenNotifications, OpenProfile</c> on the shell; the replica had
/// some of the work inside inline toolbar lambdas and none of the names.
///
/// <para>
/// Two of the three "open" commands also <b>revived dead windows</b>: <c>NotificationView</c> and <c>UserView</c> were
/// declared and never constructed, so they sat in the unreachable baseline. Opening them from a bound command is what
/// the original does with them, and it took the unreachable count from 35 to 33.
/// </para>
/// </summary>
public sealed class MainWindowCommandTests
{
    private readonly ITestOutputHelper _out;
    public MainWindowCommandTests(ITestOutputHelper output) => _out = output;

    private static string Shell() => File.ReadAllText(Path.Combine(Root(),
        "src", "Cybersole.Ui", "Views", "MainWindow.cs"));

    [Fact]
    public void EveryBoundMemberExistsOnTheShell()
    {
        var source = Shell();

        foreach (var (signature, name) in new[]
                 {
                     ("public bool Navigate(string? tab)", "Navigate"),
                     ("public string Clock =>", "Clock"),
                 })
        {
            var present = source.Contains(signature, System.StringComparison.Ordinal);
            _out.WriteLine($"{name}: {(present ? "present" : "MISSING")}");
            Assert.True(present, "MainWindow does not expose " + name);
        }

        // R498: these five are ICommand properties now (the binding table asks for properties, not methods).
        // A `public void X()` would still satisfy the check.
        foreach (var name in new[] { "OpenMonitor", "OpenNotifications", "OpenProfile", "Minimise", "Exit" })
        {
            var present = source.Contains("public void " + name + "(", System.StringComparison.Ordinal)
                          || source.Contains("public ICommand " + name, System.StringComparison.Ordinal);
            _out.WriteLine($"{name}: {(present ? "present" : "MISSING")}");
            Assert.True(present, "MainWindow does not expose " + name);
        }
    }

    [Fact]
    public void NavigateUsesTheSameSixNamesTheTabsCarry()
    {
        var source = Shell();

        // the tab headers are the vocabulary Navigate matches against
        foreach (var tab in new[] { "Home", "Tasks", "Proxies", "Billing", "Accounts", "Settings" })
            Assert.Contains($"Header = \"{tab}\"", source, System.StringComparison.Ordinal);

        // and it reports "no such tab" instead of silently doing nothing
        Assert.Contains("return false;", source);
        Assert.Contains("StringComparison.OrdinalIgnoreCase", source);
    }

    [Fact]
    public void TheTwoRevivedWindowsAreNoLongerInTheUnreachableBaseline()
    {
        var baseline = File.ReadAllText(Path.Combine(Root(),
            "tests", "Cybersole.Tests", "UnreachedUiTypesTests.cs"));

        _out.WriteLine("NotificationView in baseline: " + baseline.Contains("\"NotificationView\""));
        Assert.DoesNotContain("\"NotificationView\"", baseline);
        Assert.DoesNotContain("\"UserView\"", baseline);

        // both are now constructed by the shell
        Assert.Contains("new NotificationView(_vm.Services).Show(this)", Shell());
        Assert.Contains("new UserView(_vm.Services).Show(this)", Shell());
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }
}
