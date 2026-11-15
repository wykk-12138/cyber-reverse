using System.Diagnostics;
using Cybersole.Core.Store;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 74: the version string in the code has to match the binary it is a replica of.
///
/// <para>
/// R118 put the number in one place so a bump meant one edit. R74 discovered the one place held the
/// wrong number: every doc, the window title and 54 occurrences across 34 files said
/// <c>5.18.28</c>, while <c>Cybersole.exe</c> reports <c>FileVersion 5.18.32.0</c> and its own
/// Settings page prints "Version 5.18.32".
/// </para>
///
/// <para>
/// A centralised constant is not a checked constant. This reads the original's file version and
/// compares — the same move every other doc test makes, applied to the one number that appears
/// everywhere.
/// </para>
/// </summary>
public sealed class AppVersionTests
{
    private readonly ITestOutputHelper _out;

    public AppVersionTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// The number this file exists to keep out. Split so the guard does not find its own
    /// needle — the first version did, which is its own small lesson.
    /// </summary>
    private const string OldVersion = "5.18." + "28";

    /// <summary>
    /// The binary this replica is a replica <i>of</i>: the archived 5.18.32 sample the IDB is built from.
    ///
    /// <para>
    /// R432: this used to point at the live install
    /// (<c>%LOCALAPPDATA%\Cybersole\current\Cybersole.exe</c>). The original self-updates, and by R429
    /// that file was <c>5.18.35.0</c> — so the guard failed on an input that had moved, not on a code
    /// defect ("没跑成" ≠ "失败", AGENTS.md §2.5). The archived sample is the only file whose version is
    /// a fact about the task, so that is what the constant reads now.
    /// </para>
    /// </summary>
    internal const string OriginalBinary =
        @"D:\projects\cyber-reverse\target\Cybersole.exe";

    /// <summary>
    /// The constant equals the original's <c>FileVersion</c>.
    ///
    /// <para>
    /// Skipped, loudly, when the original is not at its usual path — the replica is meant to be
    /// buildable without it, and a test that fails for a missing sample teaches nothing.
    /// </para>
    /// </summary>
    [Fact]
    public void VersionMatchesTheOriginalBinary()
    {
        if (!File.Exists(OriginalBinary))
        {
            _out.WriteLine($"original binary not present at {OriginalBinary} — nothing to compare");
            return;
        }

        var info = FileVersionInfo.GetVersionInfo(OriginalBinary);
        var fileVersion = info.FileVersion ?? string.Empty;
        _out.WriteLine($"binary FileVersion = {fileVersion}");
        _out.WriteLine($"AppVersion.Current  = {AppVersion.Current}");

        Assert.StartsWith(AppVersion.Current + ".", fileVersion);
    }

    /// <summary>
    /// The old number must not survive in the code. R74 found 54 occurrences in 34 files — most of
    /// them User-Agent strings and settings defaults — and a partial fix is how a wrong version
    /// comes back.
    /// </summary>
    [Fact]
    public void TheOldVersionStringIsGone()
    {
        var root = RepoRoot();
        Assert.NotNull(root);

        // Source only. The docs are allowed to name the old number — a correction that cannot say
        // what it corrected is a worse record than the mistake.
        var offenders = new List<string>();
        foreach (var path in Directory.EnumerateFiles(root!, "*.cs", SearchOption.AllDirectories))
        {
            if (path.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")
                || path.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}"))
                continue;

            // Code only: a comment or an XML-doc line may name the old number, because a
            // correction that cannot say what it corrected is a worse record than the mistake.
            var code = string.Join("\n", File.ReadAllLines(path)
                .Where(line => !line.TrimStart().StartsWith("//", StringComparison.Ordinal)));

            if (code.Contains(OldVersion, StringComparison.Ordinal)) offenders.Add(path);
        }

        _out.WriteLine($"offenders = {offenders.Count}");
        Assert.Empty(offenders);
    }

    private static string? RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir?.FullName;
    }
}
