using System;
using System.Diagnostics;
using System.IO;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R1174: the name-level binding gap is zero inside the boundary R702 set, and stays that way.
///
/// <para>
/// <c>tools/bind_diff.py --buckets</c> separates two things that used to share one number: generic
/// instantiation artefacts (<c>HasMultiple_NN</c>), and the two members that belong to the login-credential
/// and licence UI R702 placed outside the function set. Before this, the report said "real gap: 2" for those
/// two, which reads as outstanding work when it is a decision. The ratchet is deliberately two-sided: the real
/// gap must be zero, and this set must stay exactly two, so a future round cannot widen the exclusion to make
/// the number look better.
/// </para>
/// </summary>
[Collection("external-tools")]
public sealed class NameBindingGapTests
{
    private readonly ITestOutputHelper _out;

    public NameBindingGapTests(ITestOutputHelper output) => _out = output;

    private static (int Code, string Stdout) RunBuckets()
    {
        var repo = FindRepoRoot();
        var psi = new ProcessStartInfo
        {
            FileName = "python",
            Arguments = "tools/bind_diff.py --buckets",
            WorkingDirectory = repo,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
        };
        using var proc = Process.Start(psi)!;
        var stdout = proc.StandardOutput.ReadToEnd();
        proc.WaitForExit();
        return (proc.ExitCode, stdout);
    }

    private static string FindRepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "tools")))
            dir = dir.Parent;
        if (dir is null) throw new InvalidOperationException("replica root not found");
        return dir.FullName;
    }

    [Fact]
    public void TheRealNameLevelGapIsZero()
    {
        var (code, stdout) = RunBuckets();
        Assert.Equal(0, code);
        _out.WriteLine(stdout);

        Assert.Contains("real gap              : 0", stdout);
    }

    /// <summary>The exclusion is a decision with a fixed size, not an adjustable one.</summary>
    [Fact]
    public void ExactlyTwoMembersAreOutsideTheFunctionSet()
    {
        var (code, stdout) = RunBuckets();
        Assert.Equal(0, code);

        Assert.Contains("not in function set   : 2", stdout);
    }
}
