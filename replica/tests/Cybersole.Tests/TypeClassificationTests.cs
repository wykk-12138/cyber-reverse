using System;
using System.Diagnostics;
using System.IO;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R1184: "15 types absent from source" is not fifteen gaps until each one is classified.
///
/// <para>
/// AGENTS.md §0 allows the replica to rename, and R702 placed the login-credential and licence UI outside the
/// function set, so an absent type is a rename or a ruling by default. The classification lives in
/// <c>tools/type_classification.json</c> with the counterpart or the ruling beside each entry, and this guard
/// pins the two numbers that matter: nothing unclassified, and nothing declared unimplemented. A genuine gap
/// would trip the second and has to be dealt with rather than absorbed into a total.
/// </para>
/// </summary>
[Collection("external-tools")]
public sealed class TypeClassificationTests
{
    private readonly ITestOutputHelper _out;

    public TypeClassificationTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void EveryAbsentTypeIsClassifiedAndNoneIsUnimplemented()
    {
        var root = FindReplicaRoot();
        var psi = new ProcessStartInfo
        {
            FileName = "python",
            Arguments = "tools/bind_diff.py --type-presence",
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
        Assert.Contains("classified:", stdout);
        Assert.Contains("unclassified 0", stdout);
        Assert.Contains("unimplemented 0", stdout);
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
