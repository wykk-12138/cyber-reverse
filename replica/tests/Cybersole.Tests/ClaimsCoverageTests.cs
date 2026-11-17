using System.Diagnostics;
using System.Text.RegularExpressions;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Criterion (d) says every claim row in docs/PARITY_CLAIMS.md carries authority, command and gap_reason.
///
/// <para>
/// R978. The script that checks this had been reporting PASS on five rows out of twenty-two since the day it was written,
/// because the document is not one table -- it is five, one per section, each opening with its own header -- and the script
/// found the first header and stopped at the first non-table line. It never changed; it was born that way. A check covering
/// a quarter of its subject while printing PASS is worse than none, because the verdict gets quoted.
/// </para>
///
/// <para>
/// So this pins two things the script cannot assert about itself: that the script's own row count equals an independent
/// count taken here, and that the number of tables is more than one. Two counters agreeing is the point -- one counter
/// printing a number is what went wrong.
/// </para>
/// </summary>
[Collection("external-tools")]
public class ClaimsCoverageTests
{
    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "AGENTS.md")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }

    private static string ClaimsPath() => Path.Combine(RepoRoot(), "docs", "PARITY_CLAIMS.md");

    private static readonly Regex Header =
        new(@"^\|\s*id\s*\|\s*claim\s*\|\s*status\s*\|\s*authority\s*\|\s*command\s*\|\s*gap_reason\s*\|", RegexOptions.Compiled);

    /// <summary>
    /// Count the claim rows here, by walking every table in the document, so the script's figure can be compared against
    /// a second implementation rather than believed.
    /// </summary>
    private static (int Tables, int Rows) CountClaims()
    {
        var lines = File.ReadAllLines(ClaimsPath());
        var tables = 0;
        var rows = 0;

        for (var i = 0; i < lines.Length; i++)
        {
            if (!Header.IsMatch(lines[i].Trim())) continue;

            tables++;
            i += 2;                                              // header, then the |---| separator
            while (i < lines.Length && lines[i].TrimStart().StartsWith("|", StringComparison.Ordinal))
            {
                if (lines[i].Split('|').Length >= 8) rows++;      // six cells plus the two outer pipes
                i++;
            }
        }

        return (tables, rows);
    }

    /// <summary>The document really is several tables, which is what broke the first version of the check.</summary>
    [Fact]
    public void TheDocumentIsMoreThanOneTable()
    {
        var (tables, rows) = CountClaims();

        Assert.True(tables > 1, $"only {tables} claim table(s) found -- the header pattern may have stopped matching");
        Assert.True(rows > 10, $"only {rows} claim rows found -- this is the figure that was wrong before R978");
    }

    /// <summary>
    /// The script's verdict and its row count must agree with a count taken independently here. A script that reports PASS
    /// over a subset satisfies nothing, so the coverage is the assertion, not just the verdict.
    /// </summary>
    [Fact]
    public void TheScriptAuditsEveryTableNotJustTheFirst()
    {
        var (_, expected) = CountClaims();
        var script = Path.Combine(RepoRoot(), "analysis", "check_claims.py");
        Assert.True(File.Exists(script), "check_claims.py is missing: " + script);

        var psi = new ProcessStartInfo("python", "\"" + script + "\"")
        {
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            WorkingDirectory = RepoRoot(),
        };

        using var proc = Process.Start(psi);
        Assert.NotNull(proc);
        var stdout = proc!.StandardOutput.ReadToEnd();
        proc.WaitForExit(120_000);

        var match = Regex.Match(stdout, @"claim rows:\s*(\d+)");
        Assert.True(match.Success, "check_claims.py did not report a row count; stdout was:" + Environment.NewLine + stdout);

        var reported = int.Parse(match.Groups[1].Value);
        Assert.Equal(expected, reported);
        Assert.Contains("criterion (d) by its own stated rule: PASS", stdout);
    }
}