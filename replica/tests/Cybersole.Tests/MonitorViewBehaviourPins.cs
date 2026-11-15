using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R434 guard: the three MonitorView commands whose behaviour is unknown must be <b>declared</b> unknown in
/// <c>docs/PARITY_CLAIMS.md</c> <b>and</b> carry their claim id in the <c>MonitorView</c> source comments.
///
/// <para>
/// Why this exists: an Unknown is only worth recording if it cannot quietly disappear. Deleting the claim row
/// (making the ledger look cleaner) or deleting the comment (making the code look finished) are both ways to
/// lose the question without answering it — either one turns this test red.
/// </para>
/// <para>
/// Nothing here asserts that the behaviour is wrong; it asserts that the question is still on the books.
/// </para>
/// </summary>
public sealed class MonitorViewBehaviourPins
{
    private readonly ITestOutputHelper _out;

    public MonitorViewBehaviourPins(ITestOutputHelper output) => _out = output;

    private static readonly string[] ClaimIds =
    {
        "C-monitor-openurl",
        "C-monitor-linkchange",
        "C-monitor-quicktask",
    };

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }

    private static string ClaimsDoc() =>
        Path.Combine(Path.GetDirectoryName(RepoRoot())!, "docs", "PARITY_CLAIMS.md");

    private static string MonitorViewSource() =>
        Path.Combine(RepoRoot(), "src", "Cybersole.Ui", "Views", "Monitor", "MonitorView.cs");

    [Fact]
    public void ClaimsDoc_Exists_AndEveryUnknownClaimIsPresentWithAuthorityUnknown()
    {
        var path = ClaimsDoc();
        Assert.True(File.Exists(path), "missing claim ledger: " + path);
        var doc = File.ReadAllText(path);

        foreach (var claimId in ClaimIds)
        {
            var line = doc.Split('\n')
                .FirstOrDefault(l => l.TrimStart().StartsWith("| " + claimId + " |", StringComparison.Ordinal));
            Assert.NotNull(line);

            var cells = line!.Split('|').Select(c => c.Trim()).ToArray();
            // | id | claim | status | authority | command | gap_reason |
            Assert.True(cells.Length >= 7, claimId + " row must have the six documented columns");
            Assert.Contains("unknown", cells[3], StringComparison.OrdinalIgnoreCase);   // status
            Assert.Equal("unknown", cells[4], StringComparer.OrdinalIgnoreCase);        // authority
            Assert.NotEqual("—", cells[6]);                                             // gap_reason required
            _out.WriteLine($"{claimId}: authority={cells[4]} gap_reason={cells[6]}");
        }
    }

    [Fact]
    public void MonitorViewSource_MentionsEveryUnknownClaimId()
    {
        var path = MonitorViewSource();
        Assert.True(File.Exists(path), "missing source: " + path);
        var source = File.ReadAllText(path);

        // Strictly the DOC COMMENT lines, and the id must end at a token boundary. Two weaker versions were tried
        // and both passed when they should have failed: (a) matching the whole file also matched the command-binding
        // string literal, (b) plain Contains() also matched "C-monitor-quicktask-REMOVED" because it is a substring.
        // A guard that cannot fail is not a guard — hence the explicit right boundary below.
        var docLines = source.Split('\n')
            .Select(l => l.Trim())
            .Where(l => l.StartsWith("///", StringComparison.Ordinal))
            .ToArray();

        foreach (var claimId in ClaimIds)
        {
            var pattern = Regex.Escape(claimId) + "(?![A-Za-z0-9-])";
            Assert.Contains(docLines, l => Regex.IsMatch(l, pattern));
            _out.WriteLine(claimId + " documented in a /// line");
        }
    }

    [Fact]
    public void TheTwoImplementedCommands_AreNotClaimedAsUnknown()
    {
        var doc = File.ReadAllText(ClaimsDoc());

        foreach (var claimId in new[] { "C-monitor-view", "C-monitor-openfilter" })
        {
            var line = doc.Split('\n')
                .FirstOrDefault(l => l.TrimStart().StartsWith("| " + claimId + " |", StringComparison.Ordinal));
            Assert.NotNull(line);
            var cells = line!.Split('|').Select(c => c.Trim()).ToArray();
            Assert.Equal("tool-evidence", cells[4], StringComparer.OrdinalIgnoreCase);
            Assert.NotEqual("—", cells[5]);      // command required for a non-unknown claim
        }
    }
}
