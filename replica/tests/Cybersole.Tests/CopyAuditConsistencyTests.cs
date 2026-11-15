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

        using var p = Process.Start(psi);
        Assert.True(p is not null, "could not start 'python'; the guard fails rather than skips");

        var stdout = p.StandardOutput.ReadToEnd();
        var stderr = p.StandardError.ReadToEnd();
        p.WaitForExit();
        _out.WriteLine(stdout);

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
