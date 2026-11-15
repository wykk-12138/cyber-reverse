using System.IO;
using System.Linq;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R228: <c>TaskView.CopyUrl</c>, and the correction that made it possible.
///
/// <para>
/// R227 removed this command with the note "there is no URL source". That was wrong: the replica's
/// <c>Product</c> model has a <c>Url</c> and <c>TaskEngine</c> polls exactly that URL. The mistake was reading only
/// <c>BotTask</c>, whose bound members are <c>Product</c> and <c>Products</c> — the URL lives one level down.
/// </para>
///
/// <para>
/// The command now copies the monitored URL, and falls back to the store's own domain (the only other URL the app knows
/// for a task) when the product has none.
/// </para>
/// </summary>
public sealed class CopyUrlTests
{
    private readonly ITestOutputHelper _out;
    public CopyUrlTests(ITestOutputHelper output) => _out = output;

    private static string Source() => File.ReadAllText(Path.Combine(Root(),
        "src", "Cybersole.Ui", "Views", "Tasks", "TaskView.cs"));

    [Fact]
    public void TheCommandExistsAndCopiesTheMonitoredUrl()
    {
        var source = Source();

        Assert.Contains("public bool CopyUrl(Action<string>? copyToClipboard = null)", source);
        // the URL it copies is the one the engine polls
        Assert.Contains("task.Product?.Url", source);
        // and the correction is recorded where the next reader will see it
        Assert.Contains("R228 corrected R227", source);
    }

    [Fact]
    public void ItFallsBackToTheStoreDomain()
    {
        var source = Source();

        Assert.Contains("_services.Stores.Modules", source);
        Assert.Contains("module?.Domains.FirstOrDefault()", source);
        Assert.Contains("\"https://\" + domain", source);
    }

    [Fact]
    public void TheUrlFieldItReadsReallyIsTheModelField()
    {
        var tasks = File.ReadAllText(Path.Combine(Root(),
            "src", "Cybersole.Core", "Models", "Tasks.cs"));

        _out.WriteLine("Product.Url present: " + tasks.Contains("public string? Url { get; set; }"));
        Assert.Contains("public string? Url { get; set; }", tasks);

        var engine = File.ReadAllText(Path.Combine(Root(),
            "src", "Cybersole.Services", "TaskEngine.cs"));
        Assert.Contains("Url = current.Url", engine);
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }
}
