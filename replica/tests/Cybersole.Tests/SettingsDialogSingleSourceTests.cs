using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Settings;
using Cybersole.Ui.Views.Settings.Modals;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 83: one dialog, one implementation.
///
/// <para>
/// R79 and R80 hand-built "Add Custom Store" and "Add Custom Sizes" as inline <c>Window</c>s inside
/// the two preset pages — while <c>Views/Settings/Modals/StoreCreatorView.cs</c> and
/// <c>SizeCreatorView.cs</c> had existed all along (the binary's resource index names those exact
/// files). Two copies of one dialog is a worse shape than a missing one: both work, and then both
/// drift.
/// </para>
///
/// <para>
/// R83 inverted the fix. The <b>existing</b> modal classes were rewritten to the wording R79/R80
/// captured off the live build, and the pages now open them. The old modal designs — a Name+URL
/// form for stores, a tick-list of thirty sizes for sizes — were invented and had no evidence
/// behind them, so they went.
/// </para>
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class SettingsDialogSingleSourceTests
{
    private readonly ITestOutputHelper _out;

    public SettingsDialogSingleSourceTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// The store dialog is one field and one button.
    ///
    /// <para>
    /// Asserted against the source rather than a constructed control tree: these are
    /// <see cref="Window"/> subclasses, and constructing a Window needs an
    /// <c>IWindowingPlatform</c>, which a headless test run does not have. The strings are
    /// constants, so the class's shape is readable without instantiating it.
    /// </para>
    /// </summary>
    [Fact]
    public void TheStoreDialogIsOneFieldAndOneButton()
    {
        _out.WriteLine($"{StoreCreatorView.DialogTitle} / {StoreCreatorView.Prompt}");

        Assert.Equal("Add Custom Store", StoreCreatorView.DialogTitle);
        Assert.Equal("Enter store URL", StoreCreatorView.Prompt);

        var source = ModalSource("StoreCreatorView");

        Assert.Contains("UiKit.Row(Prompt, url, 130)", source);
        Assert.Contains("Content = \"Add\"", source);

        // the invented Name/URL pair and the generic Save/Close footer are gone
        Assert.DoesNotContain("UiKit.Row(\"Name\"", source);
        Assert.DoesNotContain("SaveButton(", source);
        Assert.DoesNotContain("BuildFooter(", source);
    }

    /// <summary>The size dialog keeps its four captured strings and its two inline controls.</summary>
    [Fact]
    public void TheSizeDialogCarriesTheCapturedWording()
    {
        _out.WriteLine($"{SizeCreatorView.DialogTitle} / {SizeCreatorView.Prompt} / " +
                       $"{SizeCreatorView.EmptyTitle} / {SizeCreatorView.EmptySubtitle}");

        Assert.Equal("Add Custom Sizes", SizeCreatorView.DialogTitle);
        Assert.Equal("Enter product URL", SizeCreatorView.Prompt);
        Assert.Equal("Nothing to see here", SizeCreatorView.EmptyTitle);
        Assert.Equal("Search a valid product URL", SizeCreatorView.EmptySubtitle);

        var source = ModalSource("SizeCreatorView");

        Assert.Contains("Content = \"Search\"", source);
        Assert.Contains("UiKit.Button(\"Clear\"", source);
        Assert.Contains("EmptyTitle", source);
        Assert.Contains("EmptySubtitle", source);

        // the invented size catalogue is gone
        Assert.DoesNotContain("Toggle size selected", source);
        Assert.DoesNotContain("SaveButton(", source);
        Assert.DoesNotContain("BuildFooter(", source);
    }

    /// <summary>
    /// The store dialog is the only writer of a new preset: it parses the URL, derives the name
    /// from the host, and calls back so the page refreshes.
    /// </summary>
    [Fact]
    public void TheStoreDialogWritesThroughToSettings()
    {
        var source = ModalSource("StoreCreatorView");

        Assert.Contains("Settings.CustomStores ??= new List<CustomStore>()", source);
        Assert.Contains("Name = uri.Host.Replace(\"www.\", string.Empty", source);
        Assert.Contains("onAdded?.Invoke();", source);
        Assert.Contains("services.Config.Save();", source);
    }

    /// <summary>
    /// The two pages no longer build a dialog of their own: they construct the shared modals. This
    /// reads the source, because "does not contain a second Window" is a property of the code, not
    /// of a constructed control tree.
    /// </summary>
    [Fact]
    public void ThePagesDoNotBuildTheirOwnDialogs()
    {
        var root = RepoRoot();
        var text = File.ReadAllText(Path.Combine(root, "src", "Cybersole.Ui", "Views", "Settings",
            "ProviderViews.cs"));

        var start = text.IndexOf("public sealed class CustomStoresView", StringComparison.Ordinal);
        var end = text.IndexOf("public sealed class DataView", StringComparison.Ordinal);
        Assert.True(start > 0 && end > start);

        var stores = text[start..end];

        var start2 = text.IndexOf("public sealed class CustomSizesView", StringComparison.Ordinal);
        var end2 = text.IndexOf("public sealed class CustomStoresView", StringComparison.Ordinal);
        Assert.True(start2 > 0 && end2 > start2);

        var sizes = text[start2..end2];

        _out.WriteLine($"stores opens StoreCreatorView: {stores.Contains("Modals.StoreCreatorView")}");
        _out.WriteLine($"sizes opens SizeCreatorView:   {sizes.Contains("Modals.SizeCreatorView")}");

        Assert.Contains("Modals.StoreCreatorView", stores);
        Assert.Contains("Modals.SizeCreatorView", sizes);

        // neither page declares a Window of its own any more
        Assert.DoesNotContain("new Window", stores);
        Assert.DoesNotContain("new Window", sizes);
    }

    // ---------------------------------------------------------------- helpers

    /// <summary>One dialog class's source text, so its shape can be asserted without a window.</summary>
    private static string ModalSource(string className)
    {
        var path = Path.Combine(RepoRoot(), "src", "Cybersole.Ui", "Views", "Settings", "Modals",
            "SettingsModals.cs");
        var text = File.ReadAllText(path);

        var start = text.IndexOf("class " + className, StringComparison.Ordinal);
        Assert.True(start > 0, className + " not found");

        // the class ends at the next top-level class doc comment
        var next = text.IndexOf("\npublic sealed class ", start, StringComparison.Ordinal);
        return next > start ? text[start..next] : text[start..];
    }

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir?.FullName ?? throw new InvalidOperationException("repo root not found");
    }

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
