using System.Text.RegularExpressions;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Nothing may call a response "blocked" on the strength of it merely not being successful.
///
/// <para>
/// R984. Chasing R983's open question -- whether the replica's scattered block checks agree with each other -- produced a
/// measurement: twenty-three call sites in the store modules return <c>Status = MonitorStatus.Blocked</c> under the single
/// condition <c>if (!res.IsSuccess)</c>. <c>IsSuccess</c> is <c>StatusCode is &gt;= 200 and &lt; 400</c>, so that
/// condition is true for 404 and for 500 as well as for a challenge page. Meanwhile the central runner in the same project
/// treats only 401 and 429 that way, and separately reports a failed anti-bot probe.
/// </para>
///
/// <para>
/// So the two halves disagree, and the module half cannot tell "the product page is gone" from "the site is refusing me".
/// A monitor that reports a delisting as a block is worse than one that reports nothing, because it hides the drop that
/// did happen behind a story about being blocked.
/// </para>
///
/// <para>
/// This pins the number rather than fixing it. Fixing it means deciding, per site, what a 404 <em>should</em> mean, and
/// that needs original-side evidence this round did not obtain. What the guard can do is make sure the count only falls:
/// a new <c>!IsSuccess</c>-means-blocked site fails here, and each removal has to be a deliberate edit to the number.
/// </para>
/// </summary>
public class BlockIsNotTheAbsenceOfSuccessTests
{
    /// <summary>
    /// Sites that return Blocked under `if (!res.IsSuccess)`. Measured at R984. This number may only go down, and the edit
    /// that lowers it should say what replaced the condition.
    /// </summary>
    private const int KnownConflatedSites = 23;

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.True(dir is not null, "could not locate the repository root from " + AppContext.BaseDirectory);
        return dir!.FullName;
    }

    /// <summary>
    /// Count the sites: a line returning Blocked with the body, whose nearest preceding `if` is the bare success test.
    /// Walked backwards rather than matched as one blob because the two lines are sometimes separated by a comment.
    /// </summary>
    private static List<string> ConflatedSites()
    {
        var found = new List<string>();
        var src = Path.Combine(RepoRoot(), "src");

        foreach (var path in Directory.EnumerateFiles(src, "*.cs", SearchOption.AllDirectories))
        {
            if (path.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}") ||
                path.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}"))
                continue;

            var lines = File.ReadAllLines(path);
            for (var i = 0; i < lines.Length; i++)
            {
                if (!lines[i].Contains("Status = MonitorStatus.Blocked", StringComparison.Ordinal)) continue;
                if (!lines[i].Contains("Raw = res.Body", StringComparison.Ordinal)) continue;

                for (var back = i - 1; back >= 0 && back >= i - 6; back--)
                {
                    if (!Regex.IsMatch(lines[back], @"\bif\b")) continue;
                    if (Regex.IsMatch(lines[back], @"if\s*\(\s*!\s*res\.IsSuccess\s*\)"))
                        found.Add($"{Path.GetFileName(path)}:{back + 1}");
                    break;
                }
            }
        }

        return found;
    }

    [Fact]
    public void TheSuccessTestIsStillWhatSuccessMeans()
    {
        var typeFile = Path.Combine(RepoRoot(), "src", "Cybersole.Http", "TlsProfile.cs");
        var text = File.ReadAllText(typeFile);

        // If this changes, the count below no longer means what it says: a widened IsSuccess would silently shrink it.
        Assert.Contains("IsSuccess => StatusCode is >= 200 and < 400", text, StringComparison.Ordinal);
    }

    [Fact]
    public void NobodyNewTreatsAFailedResponseAsABlock()
    {
        var sites = ConflatedSites();

        Assert.True(sites.Count <= KnownConflatedSites,
            $"a response that merely is not successful is being reported as blocked at {sites.Count} sites, up from "
            + $"{KnownConflatedSites}. 404 and 500 are not blocks. New sites:"
            + Environment.NewLine + string.Join(Environment.NewLine, sites));
    }

    [Fact]
    public void TheCountIsNotStaleInTheOtherDirection()
    {
        var sites = ConflatedSites();

        // A number that is merely an upper bound stops describing the code once the code improves. If sites were removed,
        // say so here rather than leaving a figure that overstates the problem.
        Assert.True(sites.Count == KnownConflatedSites,
            $"KnownConflatedSites is {KnownConflatedSites} but {sites.Count} sites remain. Lower the constant to "
            + $"{sites.Count} and record what replaced the condition. Still conflated:"
            + Environment.NewLine + string.Join(Environment.NewLine, sites));
    }
}