using Cybersole.Core.Models;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 56: the proxies page became a table, and <c>ProxyLines</c> became an orphan in the same
/// edit — the exact repeat of what R55 caught on the accounts page one round earlier.
///
/// Twice now, replacing a string list with a view left the list being written for nobody. These
/// tests pin the two halves of the fix: the list is gone, and the signal that replaced it is
/// actually subscribed.
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class ProxyTableTests
{
    private readonly ITestOutputHelper _out;

    public ProxyTableTests(ITestOutputHelper output) => _out = output;

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }

    private static string Src(params string[] parts) =>
        Path.Combine(new[] { RepoRoot() }.Concat(parts).ToArray());

    private static string AllUiSource()
    {
        var ui = Src("src", "Cybersole.Ui");
        return string.Join("\n", Directory
            .EnumerateFiles(ui, "*.cs", SearchOption.AllDirectories)
            .Where(f => !f.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}"))
            .Select(File.ReadAllText));
    }

    /// <summary>
    /// Neither orphaned list should come back. If a future edit reintroduces one, it must bring a
    /// reader with it — and this test is where that gets noticed.
    /// </summary>
    [Theory]
    [InlineData("AccountLines")]
    [InlineData("ProxyLines")]
    public void TheOrphanedStringListsStayGone(string name)
    {
        var all = AllUiSource();

        var declared = all.Contains($"ObservableCollection<string> {name}", StringComparison.Ordinal);
        var populated = all.Contains($"{name}.Add(", StringComparison.Ordinal);

        _out.WriteLine($"{name}: declared={declared} populated={populated}");
        Assert.False(declared, $"{name} is back — was it given a reader, or is it an orphan again?");
        Assert.False(populated, $"{name}.Add(...) is back with no list to add to");
    }

    /// <summary>
    /// <c>ProxiesChanged</c> exists because three call sites need to tell the view to rebuild.
    /// R180 found an event that was declared, raised, and never subscribed; the assertion is that
    /// the subscriber exists, not that the event does.
    /// </summary>
    [Fact]
    public void TheProxyTableRebuildsOnChange()
    {
        var all = AllUiSource();

        var raised = all.Contains("ProxiesChanged?.Invoke", StringComparison.Ordinal);
        var subscribed = all.Contains("ProxiesChanged +=", StringComparison.Ordinal);
        var fills = all.Contains("Reload()", StringComparison.Ordinal);

        _out.WriteLine($"raised={raised} subscribed={subscribed} fills={fills}");

        Assert.True(raised, "RefreshProxies no longer raises anything");
        Assert.True(subscribed,
            "ProxiesChanged is raised but never subscribed — this is the round-180 defect: " +
            "the proxy table would never refresh after an import or a test run");
        Assert.True(fills, "the subscriber does not rebuild the page");
    }

    /// <summary>
    /// The table shows the columns the locale names. Proxies.Column.IP / .Port / .Username /
    /// .Status all exist, so a table that drops one is showing less than the original.
    /// </summary>
    [Theory]
    [InlineData("IP")]
    [InlineData("Port")]
    [InlineData("Username")]
    [InlineData("Status")]
    public void TheProxyTableHasTheLocaleColumns(string column)
    {
        var view = File.ReadAllText(Src("src", "Cybersole.Ui", "Views", "Proxies", "ProxyGrid.cs"));
        var locale = File.ReadAllText(
            Src("src", "Cybersole.Core", "Locales", "Cybersole.Locales.en.json"));

        var inLocale = locale.Contains($"\"Proxies.Column.{column}\"", StringComparison.Ordinal);
        var inView = view.Contains($"\"{column}\"", StringComparison.Ordinal);

        _out.WriteLine($"{column}: locale={inLocale} header={inView}");
        Assert.True(inLocale, $"Proxies.Column.{column} is gone from the locale");
        Assert.True(inView, $"ProxyGrid has no {column} column header");
    }

    /// <summary>
    /// A proxy row must not print credentials. The context menu copies them deliberately; the
    /// table itself shows host, port, user and status.
    /// </summary>
    [Fact]
    public void TheProxyTableDoesNotPrintPasswords()
    {
        var view = File.ReadAllText(Src("src", "Cybersole.Ui", "Views", "Proxies", "ProxyGrid.cs"));

        // AddCell(row, …, proxy.Password) would put the secret in a column.
        var leaksPassword = view.Contains("AddCell(row, 2, proxy.Password", StringComparison.Ordinal)
                            || view.Contains("proxy.Password!", StringComparison.Ordinal);

        _out.WriteLine($"leaks-password={leaksPassword}");
        Assert.False(leaksPassword, "ProxyGrid renders the password — it belongs behind Copy Credentials");
    }
}
