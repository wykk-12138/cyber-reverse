using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// An event that is declared and raised but never subscribed is a promise nobody keeps.
///
/// R179: `SettingsShell.UpdateRequested` is declared, raised in the CHECK FOR UPDATES handler, and
/// has no `+=` anywhere in the repository. Round 118 fixed the button by making it do the work
/// itself — a real fix, and the reason it is not in DeadButtonTests' known list — but the event
/// it used to raise was left behind, still looking like an extension point.
///
/// This is the event-shaped version of the dead-button rule: a thing that appears to do something
/// and does nothing is worse than an absent thing, because a reader budgets for it.
///
/// A false positive here would be an event raised for a consumer in another assembly. There is no
/// other assembly; every project in the solution is scanned.
/// </summary>
public class UnsubscribedEventsTests
{
    private readonly ITestOutputHelper _out;
    public UnsubscribedEventsTests(ITestOutputHelper output) => _out = output;

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;

        return dir?.FullName ?? string.Empty;
    }

    private static readonly Regex Declared = new(
        @"public\s+event\s+[\w.<>?]+\s+(\w+)\s*;", RegexOptions.Compiled);

    /// <summary>
    /// Events that are raised by design with no subscriber in this build. Two categories:
    ///
    ///   contract   a member an interface requires (ICommand.CanExecuteChanged). The framework
    ///              subscribes, not this repository.
    ///   extension  a service's change hook whose primary output is a property the callers do
    ///              read. Removing the event would leave the service with no way to announce a
    ///              change; keeping it costs one null check per tick.
    ///
    /// Anything not in one of those two categories is a defect: R118's UpdateRequested and
    /// LogoutRequested were, and this test is why they are gone.
    /// </summary>
    private static readonly Dictionary<string, string> KnownUnsubscribed = new(StringComparer.Ordinal)
    {
        ["CanExecuteChanged"] = "contract: ICommand requires it; Avalonia subscribes",
        // R976: ObservableDictionary exists to carry these two. The interface requires declaring them and nothing in this
        // repository binds to a dictionary yet -- a subscriber would be UI, which was deferred. Declaring them is the
        // contract; not listening yet is the state of the work, not a broken promise.
        ["CollectionChanged"] = "contract: INotifyCollectionChanged requires it; a binding subscribes",
        ["PropertyChanged"] = "contract: INotifyPropertyChanged requires it; a binding subscribes",
        ["Ticked"] = "extension: ClockService.Current is what callers read",
        ["Saved"] = "extension: ConfigurationStore.Saved; callers re-read the properties",
        ["SignedIn"] = "extension: AuthService exposes the state as a property",
        ["SignedOut"] = "extension: AuthService exposes the state as a property",
    };

    [Fact]
    public void NoEventIsDeclaredRaisedAndNeverListenedTo()
    {
        var root = RepoRoot();
        var files = Directory
            .EnumerateFiles(Path.Combine(root, "src"), "*.cs", SearchOption.AllDirectories)
            .Where(f => !f.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")
                        && !f.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}"))
            .ToList();

        // one pass over every source file, so a subscription in any project counts
        var sources = files.ToDictionary(
            f => f,
            f => File.ReadAllText(f));

        var all = string.Join("\n", sources.Values);

        var findings = new List<string>();

        foreach (var (file, text) in sources)
        {
            foreach (Match m in Declared.Matches(text))
            {
                var name = m.Groups[1].Value;

                // a subscription looks like `+=` on the same name, in any file
                var subscribed = Regex.IsMatch(all, $@"\b{Regex.Escape(name)}\s*\+=");
                if (subscribed) continue;

                // raising it is what makes the absence worth reporting; a declared-but-unused
                // event is dead code, not a broken promise
                var raised = Regex.IsMatch(text, $@"\b{Regex.Escape(name)}\s*\?\.Invoke\b")
                             || Regex.IsMatch(text, $@"\b{Regex.Escape(name)}\s*\.Invoke\b")
                             || Regex.IsMatch(text, $@"\b{Regex.Escape(name)}\s*\(this,");

                if (!raised) continue;
                if (KnownUnsubscribed.ContainsKey(name)) continue;

                var rel = Path.GetRelativePath(root, file).Replace('\\', '/');
                var line = text[..m.Index].Count(c => c == '\n') + 1;
                findings.Add($"{rel}:{line}  {name} is raised but never subscribed");
            }
        }

        foreach (var f in findings) _out.WriteLine("  " + f);
        _out.WriteLine($"raised-but-unsubscribed events: {findings.Count}");

        Assert.Empty(findings);
    }
}
