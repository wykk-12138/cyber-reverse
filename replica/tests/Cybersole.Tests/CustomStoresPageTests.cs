using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 79: Custom Stores is a table with a modal, not a form.
///
/// <para>
/// The live page, driven in R79:
/// </para>
///
/// <code>
/// Custom Stores
/// Add custom Shopify store presets for easy access
/// 0 Presets                          [Clear Presets]  [Add Preset]
/// [ ]  Name ⇅      URL ⇅      Currency ⇅
///            Nothing to see here
///        Add some store presets to get started
/// </code>
///
/// <para>
/// "Add Preset" opens a modal titled <b>Add Custom Store</b> holding one field — <c>Enter store
/// URL</c> — and a full-width <c>Add</c>. Name and Currency are not inputs because they are read
/// off the URL, which is why they are table columns.
/// </para>
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class CustomStoresPageTests
{
    private readonly ITestOutputHelper _out;

    public CustomStoresPageTests(ITestOutputHelper output) => _out = output;

    /// <summary>The three sortable columns, in the live page's order.</summary>
    [Fact]
    public void TheTableHasThreeSortableColumns()
    {
        _out.WriteLine(string.Join(" | ", CustomStoresView.Columns));

        Assert.Equal(new[] { "Name", "URL", "Currency" }, CustomStoresView.Columns);
    }

    /// <summary>The count caption says "Presets" — and says "Preset" for one.</summary>
    [Fact]
    public void TheCountCaptionIsTheLocalesWords()
    {
        Assert.Equal("0 Presets", CustomStoresView.CountCaption(0));
        Assert.Equal("1 Preset", CustomStoresView.CountCaption(1));
        Assert.Equal("3 Presets", CustomStoresView.CountCaption(3));
    }

    /// <summary>The dialog is one field with one button, and both are worded as the live build words them.</summary>
    [Fact]
    public void TheDialogIsOneField()
    {
        _out.WriteLine($"{CustomStoresView.DialogTitle} / {CustomStoresView.DialogPrompt}");

        Assert.Equal("Add Custom Store", CustomStoresView.DialogTitle);
        Assert.Equal("Enter store URL", CustomStoresView.DialogPrompt);
    }

    /// <summary>The page prints the count, both header buttons, the three column headers and the two empty lines.</summary>
    [Fact]
    public void ThePagePrintsTheLiveChrome()
    {
        var services = TestServices.Create();
        services.Config.Settings.CustomStores = new List<CustomStore>();
        var view = new CustomStoresView(services);

        var texts = Descendants(view).OfType<TextBlock>().Select(t => t.Text ?? "").ToList();
        var buttons = Descendants(view).OfType<Button>().Select(b => b.Content?.ToString() ?? "").ToList();

        foreach (var label in new[] { "0 Presets", "Nothing to see here", "Add some store presets to get started" })
        {
            _out.WriteLine($"{label}: {texts.Contains(label)}");
            Assert.Contains(label, texts);
        }

        Assert.Contains("Clear Presets", buttons);
        Assert.Contains("Add Preset", buttons);
    }

    /// <summary>
    /// With no presets the table head is hidden and the empty state shows — the live page's shape.
    /// With one, the head appears and the row carries the three values.
    /// </summary>
    [Fact]
    public void TheTableHeadAppearsWithTheFirstRow()
    {
        var services = TestServices.Create();
        services.Config.Settings.CustomStores = new List<CustomStore>
        {
            new() { Name = "demo-shop.example.com", Url = "https://demo-shop.example.com/", Currency = "USD" },
        };

        var view = new CustomStoresView(services);
        var texts = Descendants(view).OfType<TextBlock>().Select(t => t.Text ?? "").ToList();
        var buttons = Descendants(view).OfType<Button>().Select(b => b.Content?.ToString() ?? "").ToList();

        _out.WriteLine("count: " + texts.FirstOrDefault(t => t.EndsWith("Preset", StringComparison.Ordinal)));
        _out.WriteLine("headers: " + string.Join(" | ", buttons.Where(b => b.StartsWith("Name") || b.StartsWith("URL") || b.StartsWith("Currency"))));

        Assert.Contains("1 Preset", texts);
        Assert.Contains("demo-shop.example.com", texts);
        Assert.Contains("https://demo-shop.example.com/", texts);
        Assert.Contains("USD", texts);

        // the sortable headers are buttons, and the sorted one shows its direction
        Assert.Contains(buttons, b => b.StartsWith("Name", StringComparison.Ordinal));
        Assert.Contains(buttons, b => b.StartsWith("URL", StringComparison.Ordinal));
        Assert.Contains(buttons, b => b.StartsWith("Currency", StringComparison.Ordinal));
        Assert.Contains("Name ↑", buttons);

        // and the empty state is hidden. It stays in the tree — IsVisible=false is how Avalonia
        // removes something from the screen — and the flag sits on the panel that wraps the two
        // lines, not on the lines themselves, so the assertion walks up to find it.
        var emptyLine = Descendants(view).OfType<TextBlock>()
            .First(t => t.Text == "Nothing to see here");

        var hidden = false;
        for (Avalonia.StyledElement? node = emptyLine; node is not null; node = node.Parent)
            if (node is Control control && !control.IsVisible) { hidden = true; break; }

        _out.WriteLine($"empty state hidden by an ancestor: {hidden}");
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
