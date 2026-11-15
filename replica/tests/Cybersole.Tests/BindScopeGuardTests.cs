using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Guards <c>tools/bind_scope.py</c>, whose single number — <c>types with scope misses</c>, currently 0 — is the
/// only one of the four metrics that already reached zero, and therefore the easiest to break without noticing.
/// </summary>
/// <remarks>
/// R580 added two counters to the tool because its failure direction was invisible: when `DECL` stops matching a
/// declaration form, that type is <c>continue</c>d past and the miss count stays at 0. A type can drop out of the
/// check and the metric looks <em>better</em>, not worse.
///
/// The counters immediately paid for themselves. They showed `examined: 152, skipped_generic: 2` against
/// <c>bind_diff</c>'s `157 present in source` — five types in neither bucket:
///
/// <list type="bullet">
/// <item><c>Cybersole.Ui.Controls.ComboBoxToken</c>, <c>ComboBoxGroupHeader</c>, <c>Cybersole.Models.Notification</c>
///   — <b>positional records</b>: <c>DECL</c> requires <c>{</c> after the name, and <c>sealed record X(...)</c>
///   puts parentheses there instead.</item>
/// <item><c>Cybersole.Models.State</c> — an <b>enum</b>; <c>DECL</c> lists class/interface/record/struct only.</item>
/// <item><b>And <c>State</c> is worse than unseen — it is mis-matched.</b> The contract binds <c>Name</c>
///   on <c>Cybersole.Models.State</c>; the replica's only <c>State</c> is an unrelated enum in
///   <c>Cybersole.Stores.Scripts</c>. R581 measured the obvious fix (require the namespace to match) and it
///   would push 类型缺失 from 17 to 82, because 64 of those 65 are the same type placed in
///   <c>Cybersole.Core.Models</c> instead. So <c>DECL</c> deliberately stays away from enums: reporting
///   <c>State.Name</c> as a miss would say "this enum lacks a property" when the truth is "this is the
///   wrong type". A misleading miss is worse than none.</item>
/// <item><c>Cybersole.Models.EditValue`1</c> — generic arity, skipped deliberately (matching it would make
///   <c>HasMultiple_93</c> read as missing and turn the 0 into 1).</item>
/// </list>
///
/// That gap is <b>documented here rather than silently fixed</b>. Teaching <c>DECL</c> about positional records
/// and enums would change the metric (a probe showed <c>State</c> reporting a miss on <c>Name</c>), which is a
/// decision for its own round. This test pins the current reconciliation so that a fix — or a further narrowing —
/// cannot happen silently.
/// </remarks>
[Collection("external-tools")]
public sealed class BindScopeGuardTests
{
    /// <summary>
    /// Types that are present per <c>bind_diff --type-presence</c> but that <c>bind_scope</c> never examines.
    /// 3 positional records + 1 enum + 1 generic-arity type. If this list shrinks, someone fixed `DECL`; if it
    /// grows, someone narrowed it. Either way the test below fails and the change becomes deliberate.
    /// </summary>
    private const int KnownUnseenTypes = 5;

    private readonly ITestOutputHelper _out;

    public BindScopeGuardTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// The tool must still report zero misses, and it must still look at the types it looked at when the counters
    /// were introduced — measured against the other tool's total rather than against a bare constant.
    /// </summary>
    [Fact]
    public void ScopeMissesStayAtZeroAndTheExaminedSetReconciles()
    {
        var (scopeCode, scopeOut, scopeErr) = Run("bind_scope.py", "");
        _out.WriteLine(scopeOut);
        if (scopeErr.Length > 0)
        {
            _out.WriteLine("stderr: " + scopeErr);
        }

        Assert.True(scopeCode == 0, $"bind_scope.py exited {scopeCode}");

        var misses = ReadInt(scopeOut, "types with scope misses:");
        var examined = ReadInt(scopeOut, "types examined:");
        var skippedGeneric = ReadInt(scopeOut, "types skipped for generic arity:");

        Assert.Equal(0, misses);

        var (diffCode, diffOut, _) = Run("bind_diff.py", "--type-presence");
        Assert.True(diffCode == 0, $"bind_diff.py --type-presence exited {diffCode}");
        // the header reads "174 declared in bindings, 157 present in source, 17 absent" -- the number comes
        // BEFORE the label, unlike bind_scope's "types examined: 152"
        var present = ReadIntBefore(diffOut, "present in source");

        _out.WriteLine($"examined={examined} skippedGeneric={skippedGeneric} unseen={KnownUnseenTypes} present={present}");

        // `skipped_generic` is NOT part of this sum: bind_scope walks all 174 binding types, so that counter
        // includes generic-arity types that are absent from the replica as well as the one that is present.
        // The five types this test accounts for already include that present generic-arity type.
        Assert.Equal(present, examined + KnownUnseenTypes);
    }

    /// <summary>
    /// A narrowing of <c>DECL</c> has to move <c>examined</c> downwards, so the counter must be non-trivial: if it
    /// ever reported 0 the reconciliation above would be satisfied by accident.
    /// </summary>
    [Fact]
    public void TheExaminedCounterReportsARealNumberOfTypes()
    {
        var (code, stdout, _) = Run("bind_scope.py", "");
        Assert.True(code == 0, $"bind_scope.py exited {code}");

        var examined = ReadInt(stdout, "types examined:");
        _out.WriteLine($"types examined: {examined}");

        Assert.True(examined > 100, $"only {examined} types examined — the DECL regex has stopped matching");
    }

    /// <summary>
    /// Read the integer that precedes <paramref name="label"/> — for headers shaped like
    /// <c>"174 declared in bindings, 157 present in source, 17 absent"</c>.
    /// </summary>
    private static int ReadIntBefore(string stdout, string label)
    {
        foreach (var raw in stdout.Split('\n'))
        {
            var line = raw.TrimEnd('\r');
            var at = line.IndexOf(label, StringComparison.Ordinal);
            if (at < 0)
            {
                continue;
            }

            var before = line[..at].TrimEnd();
            var end = before.Length;
            var start = end;
            while (start > 0 && char.IsDigit(before[start - 1]))
            {
                start--;
            }

            if (start < end)
            {
                return int.Parse(before[start..end]);
            }
        }

        throw new InvalidOperationException($"no integer before '{label}' in:\n{stdout}");
    }

    private static int ReadInt(string stdout, string label)
    {
        foreach (var raw in stdout.Split('\n'))
        {
            var line = raw.TrimEnd('\r');
            var at = line.IndexOf(label, StringComparison.Ordinal);
            if (at < 0)
            {
                continue;
            }

            var rest = line[(at + label.Length)..].Trim();
            var digits = new StringBuilder();
            foreach (var ch in rest)
            {
                if (char.IsDigit(ch))
                {
                    digits.Append(ch);
                }
                else if (digits.Length > 0)
                {
                    break;
                }
            }

            if (digits.Length > 0)
            {
                return int.Parse(digits.ToString());
            }
        }

        throw new InvalidOperationException($"no integer found after '{label}' in:\n{stdout}");
    }

    /// <summary>Run one of the tools from the repository root, reading stdout as UTF-8 (console code page is GBK).</summary>
    private static (int Code, string Stdout, string Stderr) Run(string script, string argument)
    {
        var root = RepoRoot();
        var path = Path.Combine(root, "tools", script);
        Assert.True(File.Exists(path), script + " is missing: " + path);

        var interpreter = ResolvePython();
        Assert.True(interpreter is not null, "no Python interpreter found; " + script + " cannot be guarded.");

        var psi = new ProcessStartInfo(interpreter!, "\"" + path + "\"" + (argument.Length > 0 ? " " + argument : ""))
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
