using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// A UI type that is complete and never constructed is invisible: correct code, zero surface.
///
/// R181 found the narrow version — two buttons saying "no window exists" while the views sat in
/// the same file. R183 asked the general question and found 42 more: settings creators for IMAP,
/// CAPTCHA, Cloudflare, Google, PayPal, sizes, stores, webhooks; the Tasks detail/group views;
/// the Smart Actions editor family; the four common modals. All declared, all constructed nowhere.
///
/// This does not demand they be wired — that is a UI project of its own, and much of it needs
/// decisions about where each one belongs. What it demands is that the number not grow. A new
/// type with no construction site is the same defect arriving fresh, and it is cheap to prevent
/// while it is still one line.
///
/// The baseline is a statement of current state, not of intent. Shrinking it is progress;
/// the test prints the live list every run so the shrink stays visible.
/// </summary>
public class UnreachedUiTypesTests
{
    private readonly ITestOutputHelper _out;
    public UnreachedUiTypesTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// Types never constructed anywhere in src/ as of round 183. Grouped by where they sit, so a
    /// future reader can see the shape of the gap rather than a flat list of 42 names.
    /// </summary>
    private static readonly string[] Baseline =
    {
        // R317: a suggestion-list row from the binding table with no proven page yet — declared and tested only.
        "InputRow",
        // R312: a control extracted from the binding table with no proven page yet — declared, tested, unreachable.
        "ComboBoxEdit",
        // Settings → the "new X" modals. Each settings page lists its items, but none of the
        // creator dialogs is opened yet.
        "AycdInboxCreatorView", "CaptchaProviderCreatorView", "CloudflareSolverCreatorView",
        "GoogleAccountEditView", "ImapCreatorView", "PayPalAccountCreatorView",
        // R83 wired SizeCreatorView and StoreCreatorView: the two preset pages open those
        // dialogs instead of hand-building their own copies.
        "ShippingRatesCreatorView", "WebhookCreatorView",

        // Tasks — TaskView builds its sub-pages with BuildXxx() instead of these types.
        // R73 wired TaskDetailsView (View Task) and TaskGroupListView (Group Settings), so the
        // two came off this list — the guard says so, which is the point of the guard.
        "TaskCreatorView", "GroupSummary", "MonitorView",

        // Smart Actions — the whole editor family; only the settings page is reachable.
        //
        // R256 removed PublishTemplateModal from this list: SmartActionsView's Publish button now
        // opens it, and it writes to SmartActionsDocument.Templates instead of doing nothing.
        // 42 became 41.
        "ActionsModal", "SmartActionSettingsView",
        "SmartActionsCreator", "TemplateView",

        // Analytics — the release views; AnalyticsView draws its own panels.
        "CheckoutList", "CheckoutView", 

        // Common modals — the app uses Status() text where these would be dialogs.
        // R508 removed MessageBoxDialog from this list: AccountGrid.Clear now constructs it to ask the
// original's "Delete N accounts?" question (docs/R507_ROUTE_C_WORKED.md). 28 became 27.
"DesktopNotification", "DropdownModal", "InputModal",

        // Profiles
        //
        // R208 removed ProfileCsvEditorView: the Billing page's measured "CSV Editor" button now hosts it through
        // ViewHostModal, so it is constructed and the baseline shrank by one (37 -> 36).
        //
        // R208 also removed ProfileCreatorView: the same page's "Add Profile" button hosts it, so the baseline shrank
        // again (36 -> 35).
        "AdvancedView", "ExpressionView", "ProfileView",

        // Utilities and one-off windows
        // R231: StoreGroupModal is constructed by UtilitiesView.EditStoreGroup (the bound EditStoreGroup command).
        // R232: NotificationView / UserView are constructed by MainWindow.OpenNotifications / OpenProfile.
        // R261: HistoryWindow by SmartActionsView.ViewLogs; ReleaseGuideView by ReleaseView.ShowGuide.
        "StaggerStartView", "YoutubeWindow",

        // A Control, not a page: AnalyticsView may embed it by another route.
        "StoreBarChart",

        // R560: three data models added from the original's binding table (docs/TYPE_GAPS.md) so the
        // type-presence gap stops counting them. They are containers, not pages - nothing builds one yet,
        // so they enter the baseline honestly rather than being wired to a page just to shorten this list.
        "ErrorEntry", "LocalizedOption", "CheckoutProperty",

        // R565: eight data models added from the binding table (docs/TYPE_GAPS.md). Containers, not pages;
        // nothing constructs them yet, so they enter the baseline rather than being wired to a page.
        "AccountStoreEntry",
        "AccountStoreType",
        "ProfileAdvancedView",
        "ProfilePaymentView",
        "KeyBindSection",
        "SizeOption",
        "ActionConfigEntry",
        "TemplateGroup",
    };

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;

        return dir?.FullName ?? string.Empty;
    }

    private static readonly Regex Declared = new(
        @"public\s+(sealed\s+|abstract\s+|static\s+)?class\s+(\w+)\s*(?::\s*([\w.]+))?",
        RegexOptions.Compiled);

    /// <summary>
    /// Types the framework constructs (App) or that cannot be constructed (abstract SettingsModal)
    /// or that are static helpers (UiKit). Not part of the question.
    /// </summary>
    private static readonly HashSet<string> NotAQuestion = new(StringComparer.Ordinal)
    {
        "App", "UiKit", "SettingsModal",
    };

    private static (List<string> Never, int DeclaredCount) Scan()
    {
        var root = RepoRoot();
        var src = Path.Combine(root, "src");
        var ui = Path.Combine(src, "Cybersole.Ui");

        var files = Directory
            .EnumerateFiles(src, "*.cs", SearchOption.AllDirectories)
            .Where(f => !f.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")
                        && !f.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}"))
            .ToDictionary(f => f, File.ReadAllText);

        var all = string.Join("\n", files.Values);

        var never = new List<string>();
        var declared = 0;

        foreach (var (path, text) in files)
        {
            if (!path.StartsWith(ui, StringComparison.OrdinalIgnoreCase)) continue;

            foreach (Match m in Declared.Matches(text))
            {
                var mods = m.Groups[1].Value;
                var name = m.Groups[2].Value;

                if (NotAQuestion.Contains(name)) continue;
                if (mods.Contains("abstract", StringComparison.Ordinal)) continue;
                if (mods.Contains("static", StringComparison.Ordinal)) continue;

                declared++;

                // a construction may carry a namespace prefix: new Settings.SettingsShell(...)
                var constructed = Regex.IsMatch(all, $@"\bnew\s+(?:[\w]+\.)*{Regex.Escape(name)}\s*\(");
                if (!constructed) never.Add(name);
            }
        }

        never.Sort(StringComparer.Ordinal);
        return (never, declared);
    }

    [Fact]
    public void NoNewUiTypeIsDeclaredAndNeverConstructed()
    {
        var (never, declared) = Scan();

        _out.WriteLine($"UI classes that are not framework/abstract/static: {declared}");
        _out.WriteLine($"never constructed: {never.Count} (baseline: {Baseline.Length})");

        foreach (var n in never) _out.WriteLine($"  {n}");

        var baseline = Baseline.ToHashSet(StringComparer.Ordinal);
        var introduced = never.Where(n => !baseline.Contains(n)).ToList();

        foreach (var n in introduced) _out.WriteLine($"  NEW unreachable type: {n}");

        Assert.Empty(introduced);
    }

    /// <summary>
    /// The baseline must not accumulate entries that have since been wired. A name that is now
    /// constructed is stale documentation, and stale documentation is how the original five went
    /// unnoticed (see DeadButtonTests, which learned this first).
    /// </summary>
    [Fact]
    public void EveryBaselineEntryIsStillUnreachable()
    {
        var (never, _) = Scan();
        var live = never.ToHashSet(StringComparer.Ordinal);

        var stale = Baseline.Where(b => !live.Contains(b)).ToList();
        foreach (var s in stale) _out.WriteLine($"  now reachable, remove from baseline: {s}");

        Assert.Empty(stale);
    }

    /// <summary>
    /// Reports the count so the shrink is visible over time. Not an assertion — the number is
    /// not a target, and pretending it should reach zero would push the baseline toward whatever
    /// passes rather than toward what is honest.
    /// </summary>
    [Fact]
    public void TheGapIsReportedEachRun()
    {
        var (never, declared) = Scan();
        _out.WriteLine($"{never.Count} of {declared} UI classes are unreachable " +
                       $"({(double)never.Count / declared:P0})");
        Assert.True(declared > 60, $"only {declared} UI classes found — the scan is broken");
    }
}
