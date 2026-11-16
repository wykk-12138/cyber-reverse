using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Buttons that only write status text.
///
/// Rounds 97 and 99 found five of these in TasksViews — New, Creator, Editor, Clone, and
/// "Create tasks". Every one looked alive: correct label, correct layout, and clicking changed
/// the status line. None did the thing the label promised, and two claimed success
/// ("Task creator opened.") while opening nothing.
///
/// A round 100 scan of the whole UI tree found 23. Four are fixed. The rest are either
/// legitimate (a Previous/Next pair over a static list has nothing to page) or blocked on a
/// window that does not exist yet.
///
/// This test pins the list. It cannot tell intent from oversight, so the list is explicit: a new
/// status-only button fails the build until someone adds it here and says why.
/// </summary>
public class DeadButtonTests
{
    private readonly ITestOutputHelper _out;
    public DeadButtonTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// One pattern, matched against the whole file: a UiKit.Button whose handler is a single
    /// expression that only touches status text. Written as one regex because slicing the text
    /// after the label cannot work — the first ')' in <c>(), => Status(…)</c> closes the empty
    /// parameter list, not the call (that mistake cost a round).
    /// </summary>
    private static readonly Regex StatusOnlyButton = new(
        @"UiKit\.Button\s*\(\s*""(?<label>[^""\\]*(?:\\.[^""\\]*)*)""\s*,\s*\(\s*\)\s*=>\s*"
        + @"(?<body>Status\(|_status\.Text\s*=|S\()",
        RegexOptions.Compiled);

    private static string UiRoot()
    {
        var dir = AppContext.BaseDirectory;
        while (dir is not null && !Directory.Exists(Path.Combine(dir, "src")))
            dir = Path.GetDirectoryName(dir);

        Assert.NotNull(dir);
        return Path.Combine(dir, "src", "Cybersole.Ui");
    }

    private static List<string> Scan()
    {
        var root = UiRoot();
        var found = new List<string>();

        foreach (var file in Directory.EnumerateFiles(root, "*.cs", SearchOption.AllDirectories))
        {
            var rel = Path.GetRelativePath(root, file).Replace('\\', '/');
            if (rel.Contains("/obj/") || rel.Contains("/bin/")) continue;

            var src = File.ReadAllText(file);
            foreach (Match m in StatusOnlyButton.Matches(src))
                found.Add($"{rel}:{m.Groups["label"].Value}");
        }

        return found;
    }

    /// <summary>
    /// Every status-only button that is known and accepted, by "File.cs:Label". Adding an entry
    /// is a decision: the button either genuinely has nothing to do, or the window it would open
    /// does not exist yet. Neither is "I did not get to it", which is what this list exposes.
    /// </summary>
    private static readonly string[] Known =
    {
        // R181 removed two entries that had been here since round 100:
        //
        //   Views/Profiles/ProfileViews.cs:Open CSV editor
        //   Views/Profiles/ProfileViews.cs:Create group
        //
        // Their reason read "the target window does not exist". The windows did not exist, but
        // the views did — ProfileCsvEditorView and ProfileGroupView were complete UserControls in
        // the same file, 200 lines apart. ViewHostModal now supplies the window, so both buttons
        // open something and neither belongs on this list.
        //
        // That is the distinction EveryKnownEntryStillExists cannot make: it checks the button is
        // still present, not that the reason is still true.

        // static pages: there is no page to move to
        // R710 removed one entry from here:
        //
        //   Views/Analytics/AnalyticsViews.cs:Close
        //
        // It said these were static pages with no page to move to, which is still true -- but the
        // button is no longer merely a caption. The original's compiled-XAML descriptors carry
        // `...CheckoutView,Cybersole.UI.Close!Getter` and `...ReleaseView,Cybersole.UI.Close!Getter`,
        // and R710 wired both views' Close to an ICommand, so the label now runs a bound member the
        // way the original binds it. A button with a command is not the thing this list is about.
        "Views/Analytics/AnalyticsViews.cs:Show guide",
        "Views/Analytics/AnalyticsViews.cs:Show site list",
        // R303: "Open tracking" was here — it wrote a sentence and nothing else. It now opens
        // CheckoutEvent.TrackingUrl through the platform launcher, so it is no longer a dead button.

        // "Show" writes the selected row into the status line. The label promises a detail panel
        // that does not exist; the behaviour is at least not a lie, so it stays with the text
        // saying what it actually does.

        // Settings is a tab in MainWindow, not a window this page can open
        "Views/Profiles/ProfileViews.cs:Open settings",

        // SmartAction has no template flag, so "Publish" has nowhere to write. The three template
        // buttons (From scratch / From template / Blank) were fixed in round 101 and are gone
        // from this list — the editor opens now.
        // R256 removed one entry from here:
        //
        //   Views/SmartActions/SmartActionViews.cs:Publish
        //
        // It said templates were not implemented. They were: the locale has a whole
        // PublishTemplate dialog, PublishTemplateModal was written in that same file, and the
        // only missing piece was a list to write into. PublishTemplateModal now validates the
        // title against PublishTemplate.Error.NoTitle and appends to
        // SmartActionsDocument.Templates, so the button opens a dialog that publishes.


        // deliberate: the extra-URL control lives in the same editor
        "Views/Tasks/TasksViews.cs:Create tasks",
    };

    [Fact]
    public void NoNewStatusOnlyButtonsAppear()
    {
        var found = Scan().Distinct().OrderBy(f => f).ToList();

        _out.WriteLine($"status-only buttons: {found.Count} (known: {Known.Length})");
        foreach (var f in found) _out.WriteLine($"  {f}");

        var unexpected = found.Where(f => !Known.Contains(f)).ToList();
        foreach (var u in unexpected) _out.WriteLine($"  NEW (unclassified): {u}");

        Assert.Empty(unexpected);
    }

    /// <summary>
    /// The list must not outlive its reasons: an entry naming a button that no longer exists is
    /// stale documentation, and stale documentation is how the original five went unnoticed.
    /// </summary>
    [Fact]
    public void EveryKnownEntryStillExists()
    {
        var live = Scan().ToHashSet();

        var stale = Known.Where(k => !live.Contains(k)).ToList();
        foreach (var s in stale) _out.WriteLine($"  STALE: {s}");

        _out.WriteLine($"live: {live.Count}, known: {Known.Length}");
        Assert.Empty(stale);
    }
}
