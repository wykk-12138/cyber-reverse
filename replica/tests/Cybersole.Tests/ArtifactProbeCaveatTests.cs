using System;
using System.Diagnostics;
using System.IO;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R1176: <c>artifact_probe.py</c> must say out loud that an absent literal proves nothing.
///
/// <para>
/// Two probes settle it: <c>Cart-AddProduct</c> and <c>Checkout-Begin</c> are absent from the current
/// published artifact, yet <c>DemandwareFlow</c> posts and gets them at runtime (lines 279 and 425). The
/// step bodies are reached through <c>StepActionRunner</c>'s reflection, which the AOT trimmer cannot see
/// through, so whole bodies are dropped together with their literals. A "no" therefore reads the same for
/// dead code and for live code behind reflective dispatch, and only a "yes" carries information.
/// </para>
///
/// <para>
/// This guard keeps that sentence attached to the output: without it the table is easy to read as an
/// absence proof, which is exactly how R1150 and R1152 used it.
/// </para>
/// </summary>
[Collection("external-tools")]
public sealed class ArtifactProbeCaveatTests
{
    private readonly ITestOutputHelper _out;

    public ArtifactProbeCaveatTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void AnAbsentLiteralIsReportedAsUninformative()
    {
        var root = FindReplicaRoot();
        var probes = Path.Combine(Path.GetTempPath(), "probe-caveat-" + Guid.NewGuid().ToString("N") + ".txt");
        File.WriteAllText(probes, "Cart-AddProduct\nwww.paypal.com/v2/checkout/orders\n");
        try
        {
            var psi = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = "tools/artifact_probe.py --strings-file \"" + probes + "\" --no-record",
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
            Assert.Contains("not that the code is dead", stdout);
        }
        finally
        {
            File.Delete(probes);
        }
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
