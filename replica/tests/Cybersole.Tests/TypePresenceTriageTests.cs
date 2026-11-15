using System;
using System.Diagnostics;
using System.IO;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Keeps the type-presence triage complete: every type the presence metric calls absent must carry exactly one verdict.
/// </summary>
/// <remarks>
/// `bind_diff.py --type-presence` reports how many contract types have no same-name declaration, and its own footnote
/// says the number may not be used as a gap count until each one is classified. `analysis/type_presence_triage.py`
/// produces that classification (R619/R620).
///
/// The invariant checked here is deliberately narrow: **the number of triage rows must equal the number of absent
/// types**, and the verdict counts must sum to it. Nothing about the verdicts themselves is asserted — that is an
/// analysis judgement, not a mechanical fact.
///
/// Why the pair is compared instead of a literal: hard-coding either number would make this test drift the moment the
/// bindings change. Comparing the two tools means the test fails exactly when they disagree, which is the condition
/// worth failing on.
///
/// If no Python interpreter is available the test fails rather than skips — a skipped guard reads as a passing one.
/// </remarks>
[Collection("external-tools")]
public sealed class TypePresenceTriageTests
{
    private readonly ITestOutputHelper _out;

    public TypePresenceTriageTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void EveryAbsentTypeCarriesExactlyOneVerdict()
    {
        var repo = RepoRoot();
        // bind_diff lives under replica/tools and must run with replica/ as its working directory;
        // the triage script lives under repo/analysis. Two different roots on purpose -- the first version of this
        // guard got it wrong and the guard caught it, which is why it compares tools instead of trusting a path.
        var replica = Path.Combine(repo, "replica");

        var absent = AbsentCount(replica);
        Assert.True(absent > 0, "bind_diff reported no absent types; the comparison would be vacuous");

        var (exit, stdout, stderr) = Run(repo, "analysis/type_presence_triage.py");
        _out.WriteLine(stdout);
        Assert.True(exit == 0, "type_presence_triage.py exited " + exit + ": " + stderr);

        var rows = Regex.Match(stdout, @"triage rows:\s*(\d+)");
        Assert.True(rows.Success, "triage output has no 'triage rows:' line");

        var verdicts = Regex.Match(stdout, @"verdicts:\s*(.+)");
        Assert.True(verdicts.Success, "triage output has no 'verdicts:' line");

        var sum = 0;
        foreach (Match m in Regex.Matches(verdicts.Groups[1].Value, @"=\s*(\d+)"))
        {
            sum += int.Parse(m.Groups[1].Value);
        }

        Assert.Equal(absent, int.Parse(rows.Groups[1].Value));
        Assert.Equal(absent, sum);
    }

    private static int AbsentCount(string repo)
    {
        var (exit, stdout, stderr) = Run(repo, "tools/bind_diff.py", "--type-presence");
        Assert.True(exit == 0, "bind_diff.py exited " + exit + ": " + stderr);

        var m = Regex.Match(stdout, @"(\d+)\s+absent");
        Assert.True(m.Success, "bind_diff output has no '<n> absent' line");
        return int.Parse(m.Groups[1].Value);
    }

    private static (int Exit, string Out, string Err) Run(string repo, string script, params string[] args)
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
        psi.ArgumentList.Add(script);
        foreach (var a in args)
        {
            psi.ArgumentList.Add(a);
        }

        using var p = Process.Start(psi);
        if (p is null)
        {
            throw new InvalidOperationException("could not start 'python'; the guard fails rather than skips");
        }

        var stdout = p.StandardOutput.ReadToEnd();
        var stderr = p.StandardError.ReadToEnd();
        p.WaitForExit();
        return (p.ExitCode, stdout, stderr);
    }

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "src")))
        {
            dir = dir.Parent;
        }

        Assert.True(dir?.Parent is not null, "could not locate the repository root from " + AppContext.BaseDirectory);
        return dir!.Parent!.FullName;
    }
}
