using System;
using System.Diagnostics;
using System.IO;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Guards the copy audit's two consumers against divergence.
/// </summary>
/// <remarks>
/// `copy_audit_report.py` computes the missing-key count twice: once for the per-area summary and once for the detail
/// table. R590 found them using different predicates -- the summary had been fixed and the detail loop had not -- so
/// the file said one number in the table and listed another number of rows. R622 changed the predicate again
/// (a key whose name appears in the source now counts as in use), which is exactly the kind of edit that can be
/// applied to one consumer and not the other.
///
/// The invariant is narrow and mechanical: **the detail row count must equal the summary's missing total.** Both come
/// from the tool, so nothing is hard-coded and the test fails only when the two disagree.
/// </remarks>
[Collection("external-tools")]
public sealed class CopyAuditConsistencyTests
{
    private readonly ITestOutputHelper _out;

    public CopyAuditConsistencyTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void DetailRowsMatchTheSummaryTotal()
    {
        var repo = RepoRoot();

        // R981: two runs, because one is not enough. On the real tree the copy gap is zero, so summary is zero and detail
        // is zero and the invariant is 0 == 0 -- no edit to either loop can break it, which is why round 623's mutation
        // reported that this guard was decorative. It was not decorative; it had nothing to guard. The fixture below is
        // the one shape where the wide and narrow predicates disagree: a key whose name appears in the source while its
        // value does not, so the wide predicate counts it as in use and the narrow one does not. There the invariant has
        // content, and reverting the detail loop to the narrow predicate must break it.
        AssertInvariantHolds(repo, null);

        var fixture = Path.Combine(Path.GetTempPath(), "copyaudit-fixture-" + Guid.NewGuid().ToString("N"));
        try
        {
            var src = Path.Combine(fixture, "src");
            Directory.CreateDirectory(src);
            File.WriteAllText(Path.Combine(fixture, "pool.txt"),
                "\"Accounts.Test.Key\": \"a value that appears nowhere at all\",\n");
            File.WriteAllText(Path.Combine(src, "Sample.cs"),
                "class Sample { const string K = \"Accounts.Test.Key\"; }\n");

            AssertInvariantHolds(repo, fixture);
        }
        finally
        {
            try { Directory.Delete(fixture, true); } catch (IOException) { /* a temp dir left behind is not a failure */ }
        }
    }

    /// <summary>
    /// Run the tool once, then require the summary's missing total to equal the number of detail rows it wrote.
    /// <paramref name="fixture"/> is null for the real tree; otherwise it holds <c>pool.txt</c> and <c>src/</c>.
    /// </summary>
    private void AssertInvariantHolds(string repo, string? fixture)
    {
        var psi = new ProcessStartInfo("python")
        {
            WorkingDirectory = repo,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            StandardOutputEncoding = System.Text.Encoding.UTF8,
            StandardErrorEncoding = System.Text.Encoding.UTF8,
        };
        psi.ArgumentList.Add("tools/copy_audit_report.py");

        string? report = null;
        if (fixture is not null)
        {
            report = Path.Combine(fixture, "report.md");
            psi.ArgumentList.Add("--pool");
            psi.ArgumentList.Add(Path.Combine(fixture, "pool.txt"));
            psi.ArgumentList.Add("--src");
            psi.ArgumentList.Add(Path.Combine(fixture, "src"));
            psi.ArgumentList.Add("--out");
            psi.ArgumentList.Add(report);
        }

        using var p = Process.Start(psi);
        Assert.True(p is not null, "could not start 'python'; the guard fails rather than skips");

        var stdout = p.StandardOutput.ReadToEnd();
        var stderr = p.StandardError.ReadToEnd();
        p.WaitForExit();
        _out.WriteLine((fixture is null ? "[real tree]" : "[fixture]") + Environment.NewLine + stdout);

        Assert.True(p.ExitCode == 0, "copy_audit_report.py exited " + p.ExitCode + ": " + stderr);

        var summary = Regex.Match(stdout, @"----\s*summary\s*----.+?\|\s*(\d+)\s*missing");
        Assert.True(summary.Success, "summary line missing from copy_audit_report.py output");

        var detail = Regex.Match(stdout, @"detail rows:\s*(\d+)");
        Assert.True(detail.Success, "detail-rows self-check missing from copy_audit_report.py output");

        Assert.Equal(int.Parse(summary.Groups[1].Value), int.Parse(detail.Groups[1].Value));
    }

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "src")))
        {
            dir = dir.Parent;
        }

        Assert.True(dir?.Parent is not null, "could not locate the repository root from " + AppContext.BaseDirectory);
        return dir!.FullName;
    }
}
