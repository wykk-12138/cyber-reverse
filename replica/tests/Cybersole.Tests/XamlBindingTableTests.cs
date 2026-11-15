using System.IO;
using System.Linq;
using System.Text.Json;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R225: the original's <b>compiled-XAML binding table</b> — the descriptors Avalonia emits as
/// <c>Namespace.Type,Cybersole.Member!Getter|Setter</c> — was carved out of the image and saved as
/// <c>docs/xaml_bindings.json</c>. It names, for every view and model the UI binds to, exactly which members exist.
///
/// <para>
/// That is a different kind of evidence from the locale: the locale says what the UI <i>prints</i>, this says what the UI
/// <i>touches</i>. It found the gap this round closed — <c>CustomBrowser</c> binds eight members and the replica had
/// two.
/// </para>
/// </summary>
public sealed class XamlBindingTableTests
{
    private readonly ITestOutputHelper _out;
    public XamlBindingTableTests(ITestOutputHelper output) => _out = output;

    private static JsonElement Table()
    {
        var path = Path.Combine(Root(), "docs", "xaml_bindings.json");
        return JsonDocument.Parse(File.ReadAllText(path)).RootElement.Clone();
    }

    private static string View(string relative) => File.ReadAllText(Path.Combine(Root(),
        "src", "Cybersole.Ui", "Views", relative.Replace('/', Path.DirectorySeparatorChar)));

    [Fact]
    public void TheTableIsTheOriginalInventory()
    {
        var table = Table();
        var types = table.EnumerateObject().ToList();
        var members = types.Sum(t => t.Value.EnumerateArray().Count());

        _out.WriteLine($"{types.Count} bound types, {members} bound members");
        Assert.True(types.Count > 150, "the table should cover the whole UI, not a corner");
        // 819 distinct member names; 1457 getter/setter descriptors before de-duplication
        Assert.True(members > 700, "the table should be the whole binding surface, not a sample");

        // the three that this round used
        Assert.True(table.TryGetProperty("Cybersole.Ui.Views.Browser.CustomBrowser", out var browser));
        Assert.Equal(
            new[] { "Autofill", "Back", "Exit", "Forward", "Minimise", "Refresh", "Status", "Type" },
            browser.EnumerateArray().Select(e => e.GetString()!).OrderBy(s => s, System.StringComparer.Ordinal).ToArray());
    }

    [Fact]
    public void TheBrowserWindowNowHasEveryMemberTheOriginalBinds()
    {
        var table = Table();
        var bound = table.GetProperty("Cybersole.Ui.Views.Browser.CustomBrowser")
            .EnumerateArray().Select(e => e.GetString()!).ToList();

        var source = View("Browser/CustomBrowser.cs");

        foreach (var member in bound)
        {
            // every bound member is either a member of the class or served by the existing API (Autofill/Status are)
            var present = source.Contains(member + "()", System.StringComparison.Ordinal)
                          || source.Contains(" " + member + " ", System.StringComparison.Ordinal)
                          || source.Contains("\"" + member + "\"", System.StringComparison.Ordinal);

            _out.WriteLine($"{member}: {(present ? "present" : "MISSING")}");
            Assert.True(present, "CustomBrowser does not expose " + member);
        }
    }

    [Fact]
    public void TheBigViewsBoundVocabularyIsOnRecord()
    {
        var table = Table();

        // the two heaviest views, so a future round can work down the list instead of rediscovering it
        var tasks = table.GetProperty("Cybersole.Ui.Views.Tasks.TaskView").EnumerateArray()
            .Select(e => e.GetString()!).ToList();
        var proxies = table.GetProperty("Cybersole.Ui.Views.Proxies.ProxyView").EnumerateArray()
            .Select(e => e.GetString()!).ToList();

        _out.WriteLine($"TaskView {tasks.Count}: {string.Join(", ", tasks)}");
        _out.WriteLine($"ProxyView {proxies.Count}: {string.Join(", ", proxies)}");

        Assert.Contains("CopyUrl", tasks);
        Assert.Contains("ForceStartSelected", tasks);
        Assert.Contains("TestAllKeybind", proxies);
        Assert.Contains("ClearOver", proxies);
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }

    [Fact]
    public void TheProxyViewsBoundNamesExistAndTheButtonsCallThem()
    {
        // R226: the original binds these on ProxyView; the replica had the behaviour inside inline lambdas.
        var source = View("Proxies/ProxyView.cs");

        foreach (var name in new[]
                 {
                     "AddProxies", "ClearAll", "CopyProxies", "CloneProxies", "DeleteProxies", "TestProxies",
                 })
        {
            Assert.True(
                source.Contains("public void " + name + "(", System.StringComparison.Ordinal)
                || source.Contains("public ICommand " + name, System.StringComparison.Ordinal),
                "ProxyView does not expose " + name);
        }

        // and they are live: the buttons go through them, not around them
        Assert.Contains("UiKit.Button(\"Add Proxies\", () => AddProxies(target))", source);
        Assert.Contains("UiKit.Button(\"Clear All\", () => ClearAll(target))", source);
    }

    [Fact]
    public void TheDocExplainsTheTwoScopesAndTheNoise()
    {
        var doc = File.ReadAllText(Path.Combine(Root(), "docs", "XAML_BINDINGS.md"));
        Assert.Contains("两种口径", doc, System.StringComparison.Ordinal);
        Assert.Contains("per-file", doc, System.StringComparison.Ordinal);
        Assert.Contains("whole-source", doc, System.StringComparison.Ordinal);

        // the generic instantiation members are called out as compiler noise, not design
        Assert.Contains("HasMultiple_", doc, System.StringComparison.Ordinal);
        Assert.Contains("噪音", doc, System.StringComparison.Ordinal);

        // and the tool that produces the numbers ships with the repo
        Assert.True(File.Exists(Path.Combine(Root(), "tools", "bind_diff.py")));
    }
}
