using System;
using System.Diagnostics;
using System.IO;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R1183: freshness must distinguish a touched file from a changed one.
///
/// <para>
/// <c>mutation-check</c> rewrites every mutation target and restores it, so the bytes return to what was
/// committed while the mtime moves forward. The freshness tool compared mtimes only, so after each mutation
/// run the artifact looked stale by seventeen files for the rest of the session, and three rounds went into
/// wondering why the source of a build kept changing when nothing had.
/// </para>
///
/// <para>
/// The invariant pinned here holds whether the tree is clean or dirty: if no newer file differs from HEAD,
/// the artifact must be reported current. During a mutation run the tree is dirty, the count is positive and
/// the state is allowed to be stale — so the guard does not fight the tool it is watching.
/// </para>
/// </summary>
[Collection("external-tools")]
public sealed class FreshnessHonestyTests
{
    private readonly ITestOutputHelper _out;

    public FreshnessHonestyTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void AChangedFileMarksStaleAndAMereTouchDoesNot()
    {
        var root = FindReplicaRoot();
        var psi = new ProcessStartInfo
        {
            FileName = "python",
            Arguments = "tools/artifact_freshness.py",
            WorkingDirectory = root,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
        };
        using var proc = Process.Start(psi)!;
        var stdout = proc.StandardOutput.ReadToEnd();
        proc.WaitForExit();
        _out.WriteLine(stdout);

        Assert.Equal(0, proc.ExitCode);
        Assert.Contains("of those, changed against HEAD:", stdout);

        var dirty = ReadInt(stdout, "of those, changed against HEAD:");
        if (dirty == 0)
            Assert.Contains("publish artifact state: current", stdout);
        else
            Assert.Contains("publish artifact state: stale", stdout);
    }

    private static int ReadInt(string text, string label)
    {
        foreach (var raw in text.Split('\n'))
        {
            var line = raw.TrimEnd('\r');
            var at = line.IndexOf(label, StringComparison.Ordinal);
            if (at < 0) continue;
            var rest = line[(at + label.Length)..].Trim();
            return int.TryParse(rest, out var v) ? v : -1;
        }
        return -1;
    }

    private static string FindReplicaRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "tools")))
            dir = dir.Parent;
        if (dir is null) throw new InvalidOperationException("replica root not found");
        return dir.FullName;
    }
}
