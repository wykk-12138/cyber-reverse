using Avalonia.Controls;
using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 80: Custom Sizes is the same table shape as Custom Stores, and its dialog was opened for
/// the first time.
///
/// <code>
/// Custom Sizes
/// Add custom Shopify size presets for easy access
/// 0 Custom Sizes                     [Clear Sizes]  [Add Size(s)]
/// [ ]  Name ⇅
///            Nothing to see here
///        Add some size presets to get started
///
/// Add Size(s) opens "Add Custom Sizes":
///   Enter product URL  [ https://cybersole.io/ ]  [Clear]
///   +---------------------------------------+
///   |        Nothing to see here            |
///   |     Search a valid product URL        |
///   +---------------------------------------+
///   [               Search                  ]
/// </code>
///
/// <para>
/// The post-search state was not captured, so the replica keeps its own discovered list (ticking a
/// size adds it) instead of inventing a second button. Everything the capture did show is exact.
/// </para>
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class CustomSizesPageTests
{
    private readonly ITestOutputHelper _out;

    public CustomSizesPageTests(ITestOutputHelper output) => _out = output;

    /// <summary>One sortable column, as the live page has.</summary>
    [Fact]
    public void TheTableHasOneColumn()
    {
        _out.WriteLine(string.Join(" | ", CustomSizesView.Columns));
        Assert.Equal(new[] { "Name" }, CustomSizesView.Columns);
    }

    /// <summary>"0 Custom Sizes" / "1 Custom Size" — the live page's plural rule.</summary>
    [Fact]
    public void TheCountCaptionIsTheLocalesWords()
    {
        Assert.Equal("0 Custom Sizes", CustomSizesView.CountCaption(0));
        Assert.Equal("1 Custom Size", CustomSizesView.CountCaption(1));
        Assert.Equal("4 Custom Sizes", CustomSizesView.CountCaption(4));
    }

    /// <summary>The dialog's four strings, word for word.</summary>
    [Fact]
    public void TheDialogWordsAreTheLiveOnes()
    {
        _out.WriteLine($"{CustomSizesView.DialogTitle} / {CustomSizesView.DialogPrompt} / " +
                       $"{CustomSizesView.DialogEmptyTitle} / {CustomSizesView.DialogEmptySubtitle}");

        Assert.Equal("Add Custom Sizes", CustomSizesView.DialogTitle);
        Assert.Equal("Enter product URL", CustomSizesView.DialogPrompt);
        Assert.Equal("Nothing to see here", CustomSizesView.DialogEmptyTitle);
        Assert.Equal("Search a valid product URL", CustomSizesView.DialogEmptySubtitle);
    }

    /// <summary>
    /// The page prints its count, both header buttons and the two empty lines — and no longer the
    /// inline "Enter product URL" that used to sit on it (that moved into the modal).
    /// </summary>
    [Fact]
    public void ThePagePrintsTheLiveChromeAndNothingElse()
    {
        var services = TestServices.Create();
        services.Config.Settings.CustomSizes = new List<string>();
        var view = new CustomSizesView(services);

        var texts = Descendants(view).OfType<TextBlock>().Select(t => t.Text ?? "").ToList();
        var buttons = Descendants(view).OfType<Button>().Select(b => b.Content?.ToString() ?? "").ToList();

        foreach (var label in new[] { "0 Custom Sizes", "Nothing to see here", "Add some size presets to get started" })
        {
            _out.WriteLine($"{label}: {texts.Contains(label)}");
            Assert.Contains(label, texts);
        }

        Assert.Contains("Clear Sizes", buttons);
        Assert.Contains("Add Size(s)", buttons);

        // the prompt lives in the modal now
        Assert.DoesNotContain("Enter product URL", texts);
        Assert.DoesNotContain("Search", buttons);
    }

    /// <summary>With one preset the head shows, the row renders, and the empty pane hides.</summary>
    [Fact]
    public void TheTableHeadAppearsWithTheFirstRow()
    {
        var services = TestServices.Create();
        services.Config.Settings.CustomSizes = new List<string> { "M", "S" };
        var view = new CustomSizesView(services);

        var texts = Descendants(view).OfType<TextBlock>().Select(t => t.Text ?? "").ToList();
        var buttons = Descendants(view).OfType<Button>().Select(b => b.Content?.ToString() ?? "").ToList();

        _out.WriteLine("headers: " + string.Join(" | ", buttons.Where(b => b.StartsWith("Name", StringComparison.Ordinal))));

        Assert.Contains("2 Custom Sizes", texts);
        Assert.Contains("M", texts);
        Assert.Contains("S", texts);
        Assert.Contains("Name ↑", buttons);

        var emptyLine = Descendants(view).OfType<TextBlock>()
            .First(t => t.Text == "Nothing to see here");
        var hidden = false;
        for (Avalonia.StyledElement? node = emptyLine; node is not null; node = node.Parent)
            if (node is Control control && !control.IsVisible) { hidden = true; break; }

        Assert.True(hidden);
    }

    // ---------------------------------------------------------------- helpers

    private static IEnumerable<Control> Descendants(Control root)
    {
        var queue = new Queue<Control>();
        queue.Enqueue(root);
        while (queue.Count > 0)
        {
            var current = queue.Dequeue();
            if (!ReferenceEquals(current, root)) yield return current;

            foreach (var child in Avalonia.LogicalTree.LogicalExtensions
                         .GetLogicalChildren(current).OfType<Control>())
                queue.Enqueue(child);
        }
    }
}
