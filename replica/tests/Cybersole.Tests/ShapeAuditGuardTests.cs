using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Guards the shape audit's own classification, because a metric that quietly reports "not found" for a member
/// that <em>is</em> there makes every number built on it wrong.
/// </summary>
/// <remarks>
/// R575 fixed a regex in <c>tools/shape_audit.py</c>: the return-type character class
/// <c>[\w&lt;&gt;,\[\]\.\s]+?</c> had no <c>?</c>, so a public method returning a <b>nullable</b> type failed to
/// match and fell through to <c>?</c> — "the replica does not have this member". Two rows were affected:
/// <c>SmartActionsCreator.AddInput</c> (<c>SmartActionFilterInput?</c>) and
/// <c>SizeCreatorView.ToggleSizeSelected</c> (also declared with a nullable result).
///
/// That was the fourth regex defect of the same family found in this project's metric tools
/// (R470b property blocks, R517 call-sites, R530 private declarations, R575 nullable returns), and <b>none of
/// them had a guard</b>: a survey in R578 found zero tests referencing <c>shape_audit</c>. A tool whose output is
/// the project's only source of numbers needs at least one assertion that fails when it regresses.
///
/// This test runs the tool and asserts on its <b>output</b>, not on a re-implementation of its regex — a copy of
/// the pattern would test the copy.
/// </remarks>
[Collection("external-tools")]
public sealed class ShapeAuditGuardTests
{
    private readonly ITestOutputHelper _out;

    public ShapeAuditGuardTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// <c>AddInput</c> is a public method taking three parameters and returning <c>SmartActionFilterInput?</c>.
    /// The audit must classify it as <c>method</c> (the member exists, the shape is wrong) and never as <c>?</c>
    /// (the member does not exist) — those two lead to opposite work.
    /// </summary>
    [Fact]
    public void NullableReturningPublicMethodsAreNotReportedAsMissing()
    {
        var (code, stdout, stderr) = RunShapeAudit();
        _out.WriteLine(stdout);
        if (stderr.Length > 0)
        {
            _out.WriteLine("stderr: " + stderr);
        }

        Assert.True(code == 0, $"shape_audit.py exited {code}");

        var line = FindRow(stdout, "SmartActionsCreator", "AddInput");
        Assert.NotNull(line);
        _out.WriteLine("row: " + line);

        Assert.DoesNotContain("replica=?", line);
        Assert.Contains("replica=method", line);
    }

    /// <summary>
    /// The same defect, on the other affected member: <c>SizeCreatorView.ToggleSizeSelected</c> is declared with a
    /// nullable result in the replica, so a narrow return-type class also hides it.
    /// </summary>
    [Fact]
    public void TheOtherNullableReturningMemberIsAlsoClassifiedAsMethod()
    {
        var (code, stdout, _) = RunShapeAudit();
        Assert.True(code == 0, $"shape_audit.py exited {code}");

        var line = FindRow(stdout, "SizeCreatorView", "ToggleSizeSelected");
        Assert.NotNull(line);
        _out.WriteLine("row: " + line);

        Assert.DoesNotContain("replica=?", line);
        Assert.Contains("replica=method", line);
    }

    private static string? FindRow(string stdout, string type, string member)
    {
        foreach (var raw in stdout.Split('\n'))
        {
            var line = raw.TrimEnd('\r');
            if (line.Contains(type, StringComparison.Ordinal)
                && line.Contains(member, StringComparison.Ordinal)
                && line.Contains("evidence=", StringComparison.Ordinal)
                && line.Contains("replica=", StringComparison.Ordinal))
            {
                return line;
            }
        }

        return null;
    }

    /// <summary>
    /// Run <c>python tools/shape_audit.py</c> from the repository root.
    /// </summary>
    /// <remarks>
    /// No test in this project launched a process before R578, so there is no house pattern to follow. The
    /// details that matter: the working directory must be the repository root (the tool resolves <c>src/</c>
    /// relative to it), and stdout must be read as UTF-8 — the console code page on this machine is GBK, and the
    /// tool's output is Chinese in places.
    ///
    /// If no interpreter is present the test <b>fails</b> rather than passing vacuously: a guard that silently
    /// does nothing is exactly what <c>mutation-check.py</c> exists to catch.
    /// </remarks>
    private static (int Code, string Stdout, string Stderr) RunShapeAudit()
    {
        var root = RepoRoot();
        var script = Path.Combine(root, "tools", "shape_audit.py");
        Assert.True(File.Exists(script), "tools/shape_audit.py is missing: " + script);

        var interpreter = ResolvePython();
        Assert.True(interpreter is not null,
            "no Python interpreter found; shape_audit.py cannot be guarded. Tried C:\\Python312\\python.exe and PATH.");

        var psi = new ProcessStartInfo(interpreter!, "\"" + script + "\"")
        {
            WorkingDirectory = root,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            StandardOutputEncoding = Encoding.UTF8,
            StandardErrorEncoding = Encoding.UTF8,
        };

        using var proc = Process.Start(psi)!;
        var stdout = proc.StandardOutput.ReadToEnd();
        var stderr = proc.StandardError.ReadToEnd();
        proc.WaitForExit();

        return (proc.ExitCode, stdout, stderr);
    }

    private static string? ResolvePython()
    {
        const string fixedPath = @"C:\Python312\python.exe";
        if (File.Exists(fixedPath))
        {
            return fixedPath;
        }

        try
        {
            var psi = new ProcessStartInfo("python", "--version")
            {
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
            };
            using var proc = Process.Start(psi);
            proc?.WaitForExit(5000);
            return proc is { ExitCode: 0 } ? "python" : null;
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "src")))
        {
            dir = dir.Parent;
        }

        return dir?.FullName ?? string.Empty;
    }
}
