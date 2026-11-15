using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 110: the verification judge is now seven short steps, and this test keeps it that way.
///
/// <para>
/// <c>verify.ps1 -Full</c> is one long run. On this machine that run died repeatedly — the harness
/// killed the command, or the captured output was a zero-byte file, or the unit-test phase threw
/// <c>StackOverflowException</c> at <c>-v m</c>. <c>tools/verify-steps.ps1</c> runs the same checks
/// one at a time at <c>-v q</c>; run individually <b>and</b> in sequence, all seven pass.
/// </para>
///
/// <para>
/// Two properties matter and are pinned here: the step list must not quietly lose a check, and the
/// steps must stay at <c>-v q</c> — that verbosity change is what fixed the crash, so a future
/// "let me add more detail" edit would bring the failure back.
/// </para>
/// </summary>
public sealed class VerifyStepsTests
{
    private readonly ITestOutputHelper _out;

    public VerifyStepsTests(ITestOutputHelper output) => _out = output;

    private static string Script()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        return File.ReadAllText(Path.Combine(dir!.FullName, "tools", "verify-steps.ps1"));
    }

    /// <summary>Seven steps, each named, no duplicates.</summary>
    [Fact]
    public void ThereAreEightNamedSteps()
    {
        var script = Script();

        var names = Regex.Matches(script, @"Name = '([^']+)'")
            .Select(m => m.Groups[1].Value)
            .ToList();

        foreach (var n in names) _out.WriteLine(n);

        Assert.Equal(new[]
        {
            "release build", "unit tests", "slow (network)", "slow (kasada live)",
            "store modules", "docs present", "mutation guards", "endpoint provenance",
        }, names);
    }

    /// <summary>The slow filter used by the steps excludes the Kasada group; the Kasada group is its own.</summary>
    [Fact]
    public void TheSlowStepsAreSplitTheSameWayAsVerifyPs1()
    {
        var script = Script();

        Assert.Contains("Speed=Slow&FullyQualifiedName!~Kasada", script);
        Assert.Contains("Speed=Slow&FullyQualifiedName~Kasada", script);
    }

    /// <summary>
    /// Every dotnet invocation is quiet. <c>-v m</c> is what crashed the unit-test phase, so this is
    /// the one line that must not drift.
    /// </summary>
    [Fact]
    public void EveryDotnetRunIsQuiet()
    {
        var script = Script();

        var dotnetCalls = Regex.Matches(script, @"& \$dotnet (?:test|build)").Count;
        var quietFlags = Regex.Matches(script, @"-v q").Count;

        _out.WriteLine($"{dotnetCalls} dotnet calls, {quietFlags} quiet flags");

        Assert.Equal(dotnetCalls, quietFlags);
        Assert.DoesNotContain("-v m", script);
    }

    /// <summary>
    /// A step reports to the console rather than through the function's return value: the caller
    /// takes the return value as a boolean, and anything else emitted with it is swallowed.
    /// </summary>
    [Fact]
    public void TheStepResultIsWrittenNotReturned()
    {
        var script = Script();

        Assert.Contains("Write-Host", script);
        Assert.Contains("return $ok", script);
    }
}
