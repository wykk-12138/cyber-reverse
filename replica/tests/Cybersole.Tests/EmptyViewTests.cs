using System.IO;
using System.Linq;
using Cybersole.Ui.Views.Common;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R209: the shared empty state. Every page in the running build draws the same block — a circular glyph, the headline
/// <c>Nothing to see here</c>, and one page-specific line — and the original's view list has it as a class
/// (<c>EmptyView</c>). This replica had six hand-built copies.
/// </summary>
public sealed class EmptyViewTests
{
    private readonly ITestOutputHelper _out;
    public EmptyViewTests(ITestOutputHelper output) => _out = output;

    private static string Root()
    {
        var dir = new DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }

    private static string Ui(string relative) =>
        File.ReadAllText(Path.Combine(Root(), "src", "Cybersole.Ui", "Views",
            relative.Replace('/', Path.DirectorySeparatorChar)));

    [Fact]
    public void TheHeadlineIsOneConstantAndTheBodiesAreTheFiveMeasuredLines()
    {
        Assert.Equal("Nothing to see here", EmptyView.Headline);

        Assert.Equal("You haven't made any checkouts for this period", EmptyView.Bodies["checkouts"]);
        Assert.Equal("You haven't made any checkouts yet", EmptyView.Bodies["feed"]);
        Assert.Equal("Add some tasks to get started", EmptyView.Bodies["tasks"]);
        Assert.Equal("Add a group to get started", EmptyView.Bodies["accounts"]);
        Assert.Equal("Add some proxies to get started", EmptyView.Bodies["proxies"]);
        Assert.Equal("Add some profiles to get started", EmptyView.Bodies["profiles"]);
    }

    [Fact]
    public void TheBlockIsAGlyphHeadlineAndBody()
    {
        var view = EmptyView.For("tasks");

        Assert.NotNull(view.Icon);
        Assert.Equal(EmptyView.Headline, view.HeadlineText.Text);
        Assert.Equal(EmptyView.Bodies["tasks"], view.BodyText.Text);

        // an unknown page key produces the headline with an empty second line rather than throwing
        Assert.Equal(string.Empty, EmptyView.For("no-such-page").BodyText.Text);
    }

    [Fact]
    public void NoPageKeepsItsOwnCopyOfTheHeadline()
    {
        // Repo-wide: the headline string literal may exist in exactly one file, and only in code.
        // Doc comments are allowed to quote it — several pages describe the window's layout in their headers.
        var offenders = new System.Collections.Generic.List<string>();

        foreach (var file in Directory.EnumerateFiles(
                     Path.Combine(Root(), "src", "Cybersole.Ui"), "*.cs", SearchOption.AllDirectories))
        {
            var code = string.Join("\n", File.ReadAllLines(file)
                .Where(line => !line.TrimStart().StartsWith("//", System.StringComparison.Ordinal)));

            if (code.Contains("\"Nothing to see here\"", System.StringComparison.Ordinal))
                offenders.Add(Path.GetFileName(file));
        }

        _out.WriteLine("files that still hard-code the headline: " + string.Join(", ", offenders));

        Assert.Equal(new[] { "EmptyView.cs" }, offenders.ToArray());
    }

    [Fact]
    public void EveryPageUsesTheSharedControl()
    {
        // the five pages the window draws this block on
        Assert.Contains("EmptyView.For(\"tasks\")", Ui("Tasks/TaskGrid.cs"));
        Assert.Contains("EmptyView.For(\"proxies\")", Ui("Proxies/ProxyGrid.cs"));
        Assert.Contains("EmptyView.For(\"profiles\"", Ui("BillingView.cs"));
        Assert.Contains("Common.EmptyView(", Ui("Analytics/AnalyticsViews.cs"));

        // and the shared helpers that used to take the title as a parameter now read the constant
        Assert.Contains("AccountTable(Columns, EmptyView.Headline", Ui("Settings/SettingsViews.cs"));
        Assert.Contains("EmptyView.For(\"cloudflare\")", Ui("Settings/ProviderViews.cs"));
    }

    [Fact]
    public void EachPageCanCarryItsOwnSecondLine()
    {
        // R400: the Cloudflare page printed the proxies sentence; EmptyView now holds one line per page.
        Assert.Equal("Add a Cloudflare provider to get started", EmptyView.Body("cloudflare"));
        Assert.Equal("Add some proxies to get started", EmptyView.Body("proxies"));
        Assert.Equal("Add some tasks to get started", EmptyView.Body("tasks"));
        Assert.Equal(string.Empty, EmptyView.Body("no-such-page"));

        var view = EmptyView.For("cloudflare");
        _out.WriteLine(view.BodyText.Text);
        Assert.Equal("Nothing to see here", view.HeadlineText.Text);
        Assert.Equal("Add a Cloudflare provider to get started", view.BodyText.Text);
    }
}
