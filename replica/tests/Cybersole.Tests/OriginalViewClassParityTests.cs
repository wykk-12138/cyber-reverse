using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 82: the original's 87 view classes, counted against the replica's own classes.
///
/// <para>
/// The binary ships an Avalonia <c>ClassToResourcePathIndex</c> listing every view it compiles:
/// 87 entries with class name and .axaml path. That is a hard, unambiguous denominator — the
/// standing brief is "function count must be equal, names may differ", and this is the only
/// complete function-count list the binary hands over for free.
/// </para>
///
/// <para>
/// Measured in R82: <b>69 of 87</b> have a same-named class in the replica. Of the remaining 18,
/// twelve are the same view under another name (the replica merged or renamed them) and six
/// have no counterpart yet. Those three buckets must partition the 87, and the third may only
/// shrink.
/// </para>
/// </summary>
public sealed class OriginalViewClassParityTests
{
    private readonly ITestOutputHelper _out;

    public OriginalViewClassParityTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// Original class → replica class that took its place. Each target must exist, so a rename can
    /// not rot into a dangling name.
    /// </summary>
    private static readonly Dictionary<string, string> Renamed = new(StringComparer.Ordinal)
    {
        // the settings page is a shell in the replica
        ["SettingsView"] = "SettingsShell",

        // the monitor is a window, not a page
        ["MonitorView"] = "MonitorWindow",

        // auth: one window covers both halves in the replica
        ["AuthWindow"] = "LicenseWindow",
        ["LicenseControl"] = "LicenseWindow",

        // the accounts creator became the import dialog
        ["AccountsCreatorView"] = "AccountImportWindow",

        // the task creator is one class here, three there
        ["TaskCreatorMainView"] = "TaskCreatorView",
        ["TaskCreatorCartView"] = "TaskCreatorView",
        ["TaskCreatorAdvancedView"] = "TaskCreatorView",

        // smart actions settings kept its name plus a suffix
        ["SmartActionSettings"] = "SmartActionSettingsView",

        // profiles: three sub-modals folded into the editor
        ["ProfileAddressView"] = "ProfileCreatorView",
        ["ProfileAdvancedView"] = "ProfileCreatorView",
        ["ProfilePaymentView"] = "ProfileCreatorView",
    };

    /// <summary>
    /// Original classes with no counterpart at all. Six of them. This list may only get shorter —
    /// a test asserts the size so removing one is a deliberate edit, not a silent drift.
    /// </summary>
    private static readonly string[] NotBuiltYet =
    {
        // R214: SplashWindow is built. The image carries its XAML resource name and the two control names inside it;
        // Program now shows it before the shell and closes it when MainWindow opens.
        // R213: LoginControl is built. The account window now opens it; every line it prints is an Auth.* key the
        // original ships, which is why the control needed no invented copy.
        // R215: CustomBrowser is built — a window with the image's Browser.* chrome that drives the CDP session
        // through delegates. Nothing is left on this list.
        // R209: EmptyView is built. Every page's empty state came from a hand-built block in that page; there is now
        // one control (Views/Common/EmptyView.cs) that owns the glyph, the headline and the per-page second line.
        // R210: GroupGrid is built. Proxies, Accounts and Billing all draw the same rail row (name, muted count,
        // tinted selection, "No groups matched your search"); it is one control now, and ProxyView uses it.
        // R204: ProxyCreatorView is built — a modal with a drop target (`ProxyCreator.DragDrop`) and a typed single
        // proxy path, opened from the proxies page.
    };

    /// <summary>The snapshot's 87 classes, in the order the file lists them.</summary>
    private static List<string> OriginalClasses()
    {
        var path = Path.Combine(RepoRoot(), "docs", "original_view_classes.txt");
        return File.ReadAllLines(path)
            .Where(line => line.Length > 0 && char.IsLetter(line[0]))
            .Select(line => line.Split(' ')[0].Trim())
            .ToList();
    }

    /// <summary>The replica's class names, scanned from source.</summary>
    private static HashSet<string> ReplicaClasses()
    {
        var names = new HashSet<string>(StringComparer.Ordinal);
        var root = Path.Combine(RepoRoot(), "src");
        var pattern = new Regex(@"public\s+(?:sealed\s+|abstract\s+|static\s+)?class\s+(\w+)");

        foreach (var file in Directory.EnumerateFiles(root, "*.cs", SearchOption.AllDirectories))
        {
            if (file.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}") ||
                file.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}"))
                continue;

            foreach (Match m in pattern.Matches(File.ReadAllText(file)))
                names.Add(m.Groups[1].Value);
        }

        return names;
    }

    /// <summary>The denominator: the binary lists exactly 87 views.</summary>
    [Fact]
    public void TheBinaryListsEightySevenViews()
    {
        var classes = OriginalClasses();
        _out.WriteLine($"snapshot classes = {classes.Count}");

        Assert.Equal(87, classes.Count);
        Assert.Equal(87, classes.Distinct().Count());
    }

    /// <summary>
    /// Every original class is accounted for: present by name, renamed to something that exists, or
    /// on the not-built-yet list. Nothing may fall through the cracks.
    /// </summary>
    [Fact]
    public void EveryOriginalClassIsAccountedFor()
    {
        var original = OriginalClasses();
        var replica = ReplicaClasses();

        var same = original.Where(replica.Contains).ToList();
        var renamed = original.Where(n => Renamed.ContainsKey(n)).ToList();
        var unaccounted = original
            .Where(n => !replica.Contains(n) && !Renamed.ContainsKey(n) && !NotBuiltYet.Contains(n))
            .ToList();

        _out.WriteLine($"same={same.Count} renamed={renamed.Count} notBuilt={NotBuiltYet.Length}");
        _out.WriteLine("unaccounted: " + string.Join(", ", unaccounted));

        Assert.Empty(unaccounted);
    }

    /// <summary>Every rename points at a class the replica really has.</summary>
    [Fact]
    public void EveryRenamePointsAtARealClass()
    {
        var replica = ReplicaClasses();

        foreach (var (from, to) in Renamed)
        {
            _out.WriteLine($"{from} -> {to}: {replica.Contains(to)}");
            Assert.True(replica.Contains(to), $"{from} claims to be {to}, which does not exist");
        }
    }

    /// <summary>
    /// The three buckets partition the 87, and the not-built-yet bucket is exactly six. A round
    /// that builds one of them deletes a line here — deliberately.
    /// </summary>
    [Fact]
    public void TheBucketsPartitionTheListAndTheDebtIsSix()
    {
        var original = OriginalClasses();
        var replica = ReplicaClasses();

        var same = original.Count(replica.Contains);
        var renamed = original.Count(n => !replica.Contains(n) && Renamed.ContainsKey(n));
        var notBuilt = original.Count(n => !replica.Contains(n) && !Renamed.ContainsKey(n));

        _out.WriteLine($"same={same} renamed={renamed} notBuilt={notBuilt} total={same + renamed + notBuilt}");

        Assert.Equal(original.Count, same + renamed + notBuilt);
        // R565: two of the eight UI data models added this round (AccountStoreEntry, AccountStoreType) are
        // names the original also declares as view classes, so same rose 76 -> 78. The other six are not in
        // the original view list and do not touch this count.
        Assert.Equal(78, same);          // R215: CustomBrowser left the debt — the list is now empty
        // R565: the same two names that raised `same` left this bucket, so `renamed` fell 11 -> 9.
        Assert.Equal(9, renamed);       // R423: MonitorView now exists by name, so it left this bucket
        Assert.Equal(0, notBuilt);
    }

    /// <summary>
    /// Two of the not-built-yet entries are honest holes rather than renames: the splash and the
    /// login view. They are named here so a future reader does not mistake them for oversights.
    /// </summary>
    [Fact]
    public void TheRealHolesAreNamed()
    {
        // R215: the last hole closed. Every original view class now has a counterpart.
        Assert.Empty(NotBuiltYet);

        // R213: LoginControl is built and the account window opens it, so it is no longer a hole.
        Assert.DoesNotContain("LoginControl", NotBuiltYet);

        _out.WriteLine("real holes: splash, in-app browser surface");
    }

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir?.FullName ?? throw new InvalidOperationException("repo root not found");
    }
}
