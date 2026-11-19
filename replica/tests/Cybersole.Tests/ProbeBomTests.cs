using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R1180: a probe file with a byte-order mark must still read its first needle.
///
/// <para>
/// The tool read the strings file as plain UTF-8, so a BOM written by <c>Set-Content -Encoding utf8</c> rode
/// along on the first line only: the needle became <c>\uFEFFProduct-Show</c> and could never match, which made
/// the first row of every table a false absence. Several rounds quoted those first rows as evidence - one of
/// them was the reason two literals were recorded as "still trimmed" when the bytes were in the artifact all
/// along, confirmed by searching the file directly.
/// </para>
///
/// <para>
/// The guard writes such a file on purpose and asserts the first row reads present, so the reading no longer
/// depends on remembering how the file was encoded.
/// </para>
/// </summary>
[Collection("external-tools")]
public sealed class ProbeBomTests
{
    private readonly ITestOutputHelper _out;

    public ProbeBomTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void AProbeFileWithABomStillReadsItsFirstNeedle()
    {
        var root = FindReplicaRoot();
        var path = Path.Combine(Path.GetTempPath(), "probe-bom-" + Guid.NewGuid().ToString("N") + ".txt");
        // the literal the artifact is known to carry, with the BOM in front of it
        File.WriteAllText(path, "www.paypal.com/v2/checkout/orders\n", new UTF8Encoding(encoderShouldEmitUTF8Identifier: true));
        // R1182: a tiny synthetic subject keeps this guard about the reader, not the 54 MB publish.
        var fake = Path.Combine(Path.GetTempPath(), "probe-fake-" + Guid.NewGuid().ToString("N") + ".bin");
        File.WriteAllText(fake, "www.paypal.com/v2/checkout/orders");
        try
        {
            var psi = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = "tools/artifact_probe.py --exe \"" + fake + "\" --strings-file \"" + path +
                            "\" --no-record",
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
            Assert.DoesNotContain("no", FirstRow(stdout));
        }
        finally
        {
            File.Delete(path);
            if (File.Exists(fake)) File.Delete(fake);
        }
    }

    private static string FirstRow(string stdout)
    {
        foreach (var raw in stdout.Split('\n'))
        {
            var line = raw.TrimEnd('\r');
            if (line.Contains("utf-16-le", StringComparison.Ordinal) && line.Contains("present", StringComparison.Ordinal))
                continue;
            if (line.Contains("checkout/orders", StringComparison.Ordinal))
                return line;
        }
        return string.Empty;
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
