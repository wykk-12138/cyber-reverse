using Avalonia.Controls;
using Cybersole.Core.Settings;
using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 76: the Keyboard Shortcuts page, copied whole off the live build.
///
/// <para>
/// The model already carried all 22 chords — R116 read them off this same page — but the view listed
/// seven task chords, four proxy chords and three billing chords, with labels it had invented
/// ("New task", "Edit task", "Clone", "Delete", "Start all"). Five task chords therefore had no row
/// at all, and the same-page clash check could not see them.
/// </para>
///
/// <code>
/// Tasks    12: New Group Ctrl+G, Task Creator Ctrl+N, Task Editor Ctrl+E, Start All F1,
///              Stop All F2, Delete Selected Delete, Clone Selected Ctrl+C, Search Ctrl+F,
///              Quicktask Ctrl+Q, Link Change Ctrl+M, Next Group Ctrl+Right, Previous Group Ctrl+Left
/// Proxies   6: New Group Ctrl+G, Add Proxies Ctrl+N, Test All Ctrl+T, Copy Selected Ctrl+C,
///              Clone Selected Ctrl+D, Delete Selected Delete
/// Billing   4: New Group Ctrl+G, Add Profile Ctrl+N, Clone Selected Ctrl+D, Delete Selected Delete
/// </code>
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class KeyBindsPageTests
{
    private readonly ITestOutputHelper _out;

    public KeyBindsPageTests(ITestOutputHelper output) => _out = output;

    /// <summary>The three tables, with the labels the live page prints, in its order.</summary>
    [Fact]
    public void ThePageListsEveryChordTheModelHas()
    {
        _out.WriteLine("tasks:   " + string.Join(", ", KeyBindsView.TaskLabels));
        _out.WriteLine("proxies: " + string.Join(", ", KeyBindsView.ProxyLabels));
        _out.WriteLine("billing: " + string.Join(", ", KeyBindsView.BillingLabels));

        Assert.Equal(new[]
        {
            "New Group", "Task Creator", "Task Editor", "Start All", "Stop All", "Delete Selected",
            "Clone Selected", "Search", "Quicktask", "Link Change", "Next Group", "Previous Group",
        }, KeyBindsView.TaskLabels);

        Assert.Equal(new[]
        {
            "New Group", "Add Proxies", "Test All", "Copy Selected", "Clone Selected", "Delete Selected",
        }, KeyBindsView.ProxyLabels);

        Assert.Equal(new[] { "New Group", "Add Profile", "Clone Selected", "Delete Selected" },
            KeyBindsView.BillingLabels);
    }

    /// <summary>
    /// The label count equals the chord count, page by page. The old view listed seven of twelve
    /// tasks while the model held twelve; this is the assertion that would have caught it.
    /// </summary>
    [Fact]
    public void TheLabelCountMatchesTheModelCount()
    {
        var model = new KeyBindSet();

        var tasks = typeof(TaskKeyBinds).GetProperties().Length;
        var proxies = typeof(ProxyKeyBinds).GetProperties().Length;
        var billing = typeof(BillingKeyBinds).GetProperties().Length;

        _out.WriteLine($"model: {tasks}/{proxies}/{billing}   view: " +
                       $"{KeyBindsView.TaskLabels.Count}/{KeyBindsView.ProxyLabels.Count}/{KeyBindsView.BillingLabels.Count}");

        Assert.Equal(tasks, KeyBindsView.TaskLabels.Count);
        Assert.Equal(proxies, KeyBindsView.ProxyLabels.Count);
        Assert.Equal(billing, KeyBindsView.BillingLabels.Count);

        Assert.NotNull(model);
    }

    /// <summary>The defaults the page shows are the chords the live build shows.</summary>
    [Fact]
    public void TheDefaultsAreTheLiveChords()
    {
        var s = new GlobalSettings();

        // Ctrl+G, Ctrl+N, Ctrl+E, F1, F2, Delete, Ctrl+C, Ctrl+F, Ctrl+Q, Ctrl+M, Ctrl+Right, Ctrl+Left
        var tasks = string.Join(" ", new[]
        {
            Describe(s.KeyBinds.Tasks.New), Describe(s.KeyBinds.Tasks.Creator),
            Describe(s.KeyBinds.Tasks.Editor), Describe(s.KeyBinds.Tasks.StartAll),
            Describe(s.KeyBinds.Tasks.StopAll), Describe(s.KeyBinds.Tasks.Delete),
            Describe(s.KeyBinds.Tasks.Clone), Describe(s.KeyBinds.Tasks.Search),
            Describe(s.KeyBinds.Tasks.Quicktask), Describe(s.KeyBinds.Tasks.LinkChange),
            Describe(s.KeyBinds.Tasks.NextGroup), Describe(s.KeyBinds.Tasks.PreviousGroup),
        });

        _out.WriteLine("tasks: " + tasks);

        Assert.Equal(
            "Ctrl+G Ctrl+N Ctrl+E F1 F2 Delete Ctrl+C Ctrl+F Ctrl+Q Ctrl+M Ctrl+Right Ctrl+Left",
            tasks);

        Assert.Equal("Ctrl+G Ctrl+N Ctrl+T Ctrl+C Ctrl+D Delete",
            string.Join(" ", new[]
            {
                Describe(s.KeyBinds.Proxies.New), Describe(s.KeyBinds.Proxies.Add),
                Describe(s.KeyBinds.Proxies.TestAll), Describe(s.KeyBinds.Proxies.Copy),
                Describe(s.KeyBinds.Proxies.Clone), Describe(s.KeyBinds.Proxies.Delete),
            }));

        Assert.Equal("Ctrl+G Ctrl+N Ctrl+D Delete",
            string.Join(" ", new[]
            {
                Describe(s.KeyBinds.Billing.New), Describe(s.KeyBinds.Billing.Add),
                Describe(s.KeyBinds.Billing.Clone), Describe(s.KeyBinds.Billing.Delete),
            }));
    }

    private static string Describe(Cybersole.Core.Models.KeyBind bind) =>
        Cybersole.Core.Input.KeyBindMatcher.Describe(bind);

    /// <summary>
    /// The three sections are named Tasks / Proxies / Billing, and the page-level switch is
    /// "Enable Keyboard Shortcuts" — the same three headings and one switch the live page has.
    /// </summary>
    [Fact]
    public void ThePageHasThreeSectionsAndOneSwitch()
    {
        var services = TestServices.Create();
        var view = new KeyBindsView(services);
        var texts = Descendants(view).OfType<TextBlock>().Select(t => t.Text ?? "").ToList();

        foreach (var title in new[] { "Tasks", "Proxies", "Billing", "Enable Keyboard Shortcuts" })
        {
            _out.WriteLine($"{title}: {texts.Contains(title)}");
            Assert.Contains(title, texts);
        }
    }

    // ---------------------------------------------------------------- the restored pages

    /// <summary>
    /// Appearance prints the ten preview captions the live page shows, in its order. They are not
    /// decoration: the block exists so the scrollbar can be tested before leaving the page.
    /// </summary>
    [Fact]
    public void AppearancePrintsTheTenPreviewCaptions()
    {
        _out.WriteLine($"captions = {AppearanceView.PreviewCaptions.Count}");

        Assert.Equal(10, AppearanceView.PreviewCaptions.Count);
        Assert.Equal("Scroll to test the scrollbar appearance", AppearanceView.PreviewCaptions[0]);
        Assert.Equal("This preview area lets you test before leaving settings",
            AppearanceView.PreviewCaptions[^1]);
    }

    /// <summary>
    /// Notifications has five tabs, in the live page's order: Checkout, Decline, Captcha,
    /// Smart Actions, Other. (R78 renamed the accessor from TabCaptions to Tabs once the five
    /// panels turned out to be one formula.)
    /// </summary>
    [Fact]
    public void NotificationsHasTheFiveTabs()
    {
        var tabs = NotificationsView.Tabs;

        _out.WriteLine(string.Join(" | ", tabs));

        Assert.Equal(new[] { "Checkout", "Decline", "Captcha", "Smart Actions", "Other" }, tabs);
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
