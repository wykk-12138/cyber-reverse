using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Guards <c>tools/bind_diff.py</c>, whose two numbers are the columns criterion (a) rests on: the type-presence
/// count and the noise/real split of the name-level gaps.
/// </summary>
/// <remarks>
/// R578 gave <c>shape_audit.py</c> its first guard after four regex defects had gone in unguarded. This is the
/// same move for the tool that produces 17 and 4. Three assertions, chosen because each one fails for a different
/// reason:
///
/// <list type="number">
/// <item>
/// <b>The simple-name split.</b> <c>bind_diff.py</c> matches a binding-table type to a source declaration by its
/// <em>simple</em> name: <c>typ.split('.')[-1].split('`')[0]</c>, so <c>Cybersole.Models.EditValue`1</c> matches
/// <c>class EditValue&lt;T&gt;</c>. Drop the <c>.split('`')[0]</c> and the generic type silently becomes "absent",
/// moving the count without anyone noticing. R576 investigated exactly this and found it correct.
/// </item>
/// <item>
/// <b>A known-absent type is still absent.</b> Without this, a bug that made <em>everything</em> match would pass
/// the first assertion. A check that can only ever say "present" is not a check.
/// </item>
/// <item>
/// <b>The noise split.</b> Twelve <c>HasMultiple_NN</c> members belong to the original's generic instantiations
/// and are not design members; they must stay out of the "real gap" figure. If the <c>NOISE</c> pattern stops
/// matching, the real gap jumps from 4 to 16 and criterion (a) looks far worse than it is.
/// </item>
/// </list>
///
/// These assert on the tool's <b>output</b>. Re-implementing its regexes here would test the copy, not the tool.
/// </remarks>
[Collection("external-tools")]
public sealed class BindDiffGuardTests
{
    private readonly ITestOutputHelper _out;

    public BindDiffGuardTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// <c>Cybersole.Models.EditValue`1</c> must not be reported absent: the replica declares
    /// <c>public sealed class EditValue&lt;T&gt;</c>, and the binding-table name carries a generic-arity suffix.
    /// </summary>
    [Fact]
    public void GenericTypeNameSuffixDoesNotMakeTheTypeAbsent()
    {
        var (code, stdout, stderr) = Run("--type-presence");
        _out.WriteLine(stdout);
        if (stderr.Length > 0)
        {
            _out.WriteLine("stderr: " + stderr);
        }

        Assert.True(code == 0, $"bind_diff.py --type-presence exited {code}");

        // the header must be there, otherwise the assertions below could pass against an empty output
        Assert.Contains("absent", stdout);

        foreach (var line in stdout.Split('\n'))
        {
            if (!line.Contains("ABSENT", StringComparison.Ordinal))
            {
                continue;
            }

            Assert.DoesNotContain("EditValue", line, StringComparison.Ordinal);
        }

        // Note: `ObservableDictionary` is NOT asserted here. It *is* legitimately absent — the replica has no
        // such type, and it is one of the five structural differences in docs/TYPE_GAPS.md. An earlier version of
        // this test asserted its absence away and went red for the right reason: the tool was right, the test
        // was wrong.
    }

    /// <summary>
    /// The check must still be able to say "absent". <c>CloudflareSolver</c> has no same-name declaration in the
    /// replica — the nearest is <c>CloudflareSolverConfig</c>, a different type — so it is in the count.
    /// </summary>
    [Fact]
    public void AKnownAbsentTypeIsStillReportedAbsent()
    {
        var (code, stdout, _) = Run("--type-presence");
        Assert.True(code == 0, $"bind_diff.py --type-presence exited {code}");

        var absent = AbsentLines(stdout);
        _out.WriteLine(absent);

        Assert.Contains("Cybersole.CloudflareSolvers.CloudflareSolver", absent, StringComparison.Ordinal);
    }

    /// <summary>
    /// The twelve <c>HasMultiple_NN</c> members are generic-instantiation artefacts of the original and must not be
    /// counted as real gaps.
    /// </summary>
    [Fact]
    public void GenericInstantiationMembersStayOutOfTheRealGap()
    {
        var (code, stdout, _) = Run("--buckets");
        Assert.True(code == 0, $"bind_diff.py --buckets exited {code}");
        _out.WriteLine(stdout);

        Assert.Contains("noise (HasMultiple_NN):", stdout);
        Assert.Contains("not in function set   :", stdout);
        Assert.Contains("real gap", stdout);

        var noise = ReadInt(stdout, "noise (HasMultiple_NN):");
        var notInFunctionSet = ReadInt(stdout, "not in function set");
        var real = ReadInt(stdout, "real gap");

        Assert.True(noise > 0, "the noise bucket disappeared — HasMultiple_NN members are no longer recognised");

        // R1174 added a third bucket for the two members R702 placed outside the function set, so this identity
        // now covers three: every missing member still has to be accounted for, which pins more than before.
        Assert.Equal(noise + notInFunctionSet + real, ReadInt(stdout, "missing:"));
    }

    private static string AbsentLines(string stdout)
    {
        var sb = new StringBuilder();
        foreach (var line in stdout.Split('\n'))
        {
            if (line.Contains("ABSENT", StringComparison.Ordinal))
            {
                sb.AppendLine(line.TrimEnd('\r'));
            }
        }

        return sb.ToString();
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

    /// <summary>
    /// Run <c>python tools/bind_diff.py &lt;arg&gt;</c> from the repository root.
    /// </summary>
    /// <remarks>
    /// Kept local rather than shared with <c>ShapeAuditGuardTests</c>: the house rationale for this project (see
    /// <c>SummaryBlockTests</c>) is that a helper used by one test is a helper that can be changed to make that
    /// test pass. The working directory must be the repository root (the tool resolves <c>src/</c> relatively) and
    /// stdout must be read as UTF-8, because this console's code page is GBK.
    /// </remarks>
    private static (int Code, string Stdout, string Stderr) Run(string argument)
    {
        var root = RepoRoot();
        var script = Path.Combine(root, "tools", "bind_diff.py");
        Assert.True(File.Exists(script), "tools/bind_diff.py is missing: " + script);

        var interpreter = ResolvePython();
        Assert.True(interpreter is not null,
            "no Python interpreter found; bind_diff.py cannot be guarded. Tried C:\\Python312\\python.exe and PATH.");

        var psi = new ProcessStartInfo(interpreter!, "\"" + script + "\" " + argument)
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
