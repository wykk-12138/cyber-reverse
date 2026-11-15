using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 108: <c>verify.ps1 -Full</c> has to stay a terminal judgement.
///
/// <para>
/// Its slow phase hits real hosts, and over four rounds six different live tests failed inside a
/// full run while each one passed on its own. That made the verdict depend on which host hiccuped,
/// so the phase now retries the filtered set once and says when the retry is what made it green.
/// </para>
///
/// <para>
/// The property worth pinning: a <b>genuine</b> regression must fail both passes. A retry that
/// turned a real failure into a green run would make the terminal judgement worthless — so the
/// retry is once, not three times, and the detail line records that it happened.
/// </para>
/// </summary>
public sealed class VerifyRetryPolicyTests
{
    private readonly ITestOutputHelper _out;

    public VerifyRetryPolicyTests(ITestOutputHelper output) => _out = output;

    private static string Script()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        return File.ReadAllText(Path.Combine(dir!.FullName, "tools", "verify.ps1"));
    }

    /// <summary>
    /// The slow phase retries the filtered set exactly once, and only when the first pass failed.
    ///
    /// <para>
    /// A targeted per-test re-run was written first and reverted the same round: it is more precise,
    /// but on this machine the full run produced no output at all twice in a row with it in place,
    /// and "the judge hung" is a worse failure than "the judge retried". The set retry is the version
    /// that runs.
    /// </para>
    /// </summary>
    [Fact]
    public void TheSlowPhaseRetriesTheSetOnce()
    {
        var script = Script();

        Assert.Contains("$slowRetried = $false", script);
        Assert.Contains("[retry] slow tests failed once", script);
        Assert.DoesNotContain("$flaked", script);

        // R109 split the phase: the set filter now excludes the Kasada group, and that filter is
        // still invoked twice (first pass + retry).
        var runs = Regex.Matches(script, @"--filter ""Speed=Slow&FullyQualifiedName!~Kasada""").Count;
        var kasada = Regex.Matches(script, @"--filter ""Speed=Slow&FullyQualifiedName~Kasada""").Count;
        _out.WriteLine($"{runs} set invocations, {kasada} kasada invocations");

        Assert.Equal(2, runs);
        Assert.Equal(1, kasada);
    }

    /// <summary>
    /// Round 109: the Kasada live group is its own check.
    ///
    /// <para>
    /// That group downloads and evaluates a real Kasada script. In R109 it ran past five minutes and
    /// had to be killed — and while it was inside the same check as everything else, a hang there
    /// erased every other live result. Split out, a Kasada problem is attributable to Kasada.
    /// </para>
    /// </summary>
    [Fact]
    public void TheKasadaGroupIsItsOwnCheck()
    {
        var script = Script();

        Assert.Contains("FullyQualifiedName!~Kasada", script);   // the rest, excluding it
        Assert.Contains("FullyQualifiedName~Kasada", script);    // the group on its own
        Assert.Contains("Check 'slow tests (kasada live)'", script);
        Assert.Contains("kasada live group green", script);

        // the two filters are distinct checks, not one
        Assert.Contains("Check 'slow tests (Speed=Slow)'", script);

        _out.WriteLine("two live checks: network group + kasada group");
    }

    /// <summary>
    /// A run rescued by the retry says so — a green run must not be reported as if the set had
    /// passed cleanly.
    /// </summary>
    [Fact]
    public void AGreenOnRetryRunSaysSo()
    {
        var script = Script();

        Assert.Contains("green on retry (first pass lost a live host)", script);
        Assert.Contains("if ($slowOk -and $slowRetried)", script);
        Assert.Contains("$slowRetried = $true", script);

        _out.WriteLine("retry-aware detail present");
    }

    /// <summary>
    /// A retry that fails again still fails the check — the retry is not a way to launder a
    /// regression into a green run, because the verdict reads the exit code of the last pass.
    /// </summary>
    [Fact]
    public void TheVerdictReadsTheLastExitCode()
    {
        var script = Script();

        Assert.Contains("$slowExit = $LASTEXITCODE", script);
        Assert.Contains("$slowOk = ($slowExit -eq 0)", script);
        Assert.Contains("Check 'slow tests (Speed=Slow)' $slowOk $slowDetail", script);
    }

    /// <summary>
    /// The script carries no merge markers or leftover notes.
    ///
    /// <para>
    /// Brace counting was tried and rejected: the script contains braces inside format strings and
    /// regexes, so a naive count reads 67 open / 68 close on a file the PowerShell parser accepts.
    /// The real parse check is <c>analysis/parse_check108.ps1</c>.
    /// </para>
    /// </summary>
    [Fact]
    public void TheScriptHasNoLeftoverMarkers()
    {
        var script = Script();

        Assert.DoesNotContain("<<<<<<<", script);
        Assert.DoesNotContain(">>>>>>>", script);
        Assert.DoesNotContain("TODO", script);

        _out.WriteLine($"{script.Length} characters, no merge markers");
    }

    /// <summary>
    /// A retry that fails again still fails the check — the retry is not a way to launder a
    /// regression into a green run, because the verdict reads the exit code of the last pass.
    /// </summary>
    [Fact]
    public void AFailingRetryStillFailsTheCheck()
    {
        var script = Script();

        // the retry reassigns both the output and the exit code
        Assert.Contains("$slow = & $dotnet test", script);
        Assert.Contains("$slowExit = $LASTEXITCODE", script);

        // and the check keys off that final code
        Assert.Contains("$slowOk = ($slowExit -eq 0)", script);
        Assert.Contains("Check 'slow tests (Speed=Slow)' $slowOk $slowDetail", script);

        _out.WriteLine("a failing retry leaves the verdict FAIL");
    }
}
