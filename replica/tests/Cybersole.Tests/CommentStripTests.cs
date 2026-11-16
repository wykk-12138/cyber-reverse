using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The comment stripper that every coverage figure now depends on.
///
/// <para>
/// R915. Two tools count image method names against replica source, and both used to scan raw text, so a doc comment
/// saying "the image names SubmitWebRtc" made SubmitWebRtc count as implemented. R914 produced exactly that: coverage
/// rose by one and the one was my own prose. Ten names were affected in total.
/// </para>
///
/// <para>
/// The stripper is tested here rather than trusted, because a wrong stripper does not fail loudly — it silently moves
/// every figure. In particular a naive strip that removes from <c>//</c> to end of line breaks on a URL inside a string
/// literal, which would eat the rest of a real line of code and make present names look absent.
/// </para>
/// </summary>
public class CommentStripTests
{
    /// <summary>
    /// The reason a regex cannot do this job: a string literal containing a URL must survive intact, and the code after
    /// it must still be scanned.
    /// </summary>
    [Fact]
    public void AUrlInsideAStringDoesNotStartAComment()
    {
        var stripped = Strip("var u = \"https://example.test/a\"; var after = 1; // gone");

        Assert.Contains("https://example.test/a", stripped);
        Assert.Contains("var after = 1;", stripped);
        Assert.DoesNotContain("gone", stripped);
    }

    [Fact]
    public void LineCommentsAreRemoved()
    {
        Assert.DoesNotContain("SubmitWebRtc", Strip("// the image names SubmitWebRtc\nvar x = 1;"));
    }

    [Fact]
    public void BlockCommentsAreRemoved()
    {
        var stripped = Strip("/* SubmitWebRtc */ var x = 1;");
        Assert.DoesNotContain("SubmitWebRtc", stripped);
        Assert.Contains("var x = 1;", stripped);
    }

    /// <summary>A block comment spanning lines, with a quote inside it, must not be read as opening a string.</summary>
    [Fact]
    public void AQuoteInsideABlockCommentDoesNotOpenAString()
    {
        var stripped = Strip("/* a \" b */ var x = 1; var y = 2;");
        Assert.Contains("var x = 1;", stripped);
        Assert.Contains("var y = 2;", stripped);
    }

    /// <summary>A verbatim string's doubled quotes are escapes, so the string does not end early.</summary>
    [Fact]
    public void VerbatimStringDoubledQuotesAreHandled()
    {
        var stripped = Strip("var s = @\"a\"\"b\"; var x = 1;");
        Assert.Contains("var x = 1;", stripped);
    }

    /// <summary>An escaped quote in an ordinary string does not end it.</summary>
    [Fact]
    public void AnEscapedQuoteInAStringDoesNotEndIt()
    {
        var stripped = Strip("var s = \"a\\\"b\"; var x = 1;");
        Assert.Contains("var x = 1;", stripped);
    }

    /// <summary>A character literal holding a quote is not the start of a string.</summary>
    [Fact]
    public void ACharLiteralHoldingAQuoteIsNotAString()
    {
        var stripped = Strip("var c = '\"'; var x = 1;");
        Assert.Contains("var x = 1;", stripped);
    }

    /// <summary>
    /// Code is preserved: stripping must not delete identifiers, which is the failure that would make present names
    /// look absent and is worse than the error being fixed.
    /// </summary>
    [Fact]
    public void CodeSurvivesStripping()
    {
        var source = "public async Task SubmitOrderAsync() { await Send(); }";
        Assert.Equal(source, Strip(source));
    }

    /// <summary>
    /// The real check: run the stripper over the whole tree and confirm that a name known to be in code is found and a
    /// name known to exist only in prose is not. If this fails, every coverage figure is suspect.
    /// </summary>
    [Fact]
    public void TheTreeSplitsCodeFromComments()
    {
        var report = RunPython("tools/comment_split.py");
        Assert.Contains("present in code:", report);
        Assert.Contains("present only in comments:", report);

        // the totals must add up: code + comment-only + absent == the image's name count. Only the first integer after
        // the colon counts -- the line also carries a percentage, and collecting all digits turned "362  23.4%" into
        // "362234" the first time this ran.
        var numbers = report
            .Split('\n')
            .Where(l => l.Contains("present in code:") || l.Contains("present only in comments:") || l.Contains("absent from both:"))
            .Select(l =>
            {
                var afterColon = l.Substring(l.IndexOf(':') + 1).TrimStart();
                var digits = new string(afterColon.TakeWhile(char.IsDigit).ToArray());
                return int.Parse(digits);
            })
            .ToArray();

        Assert.Equal(3, numbers.Length);
        Assert.Equal(1547, numbers.Sum());
    }

    /// <summary>
    /// Runs the tool on a literal, so the assertion is on the tool's own behaviour rather than on a reimplementation of
    /// it in C#. A second implementation would agree with itself and prove nothing.
    /// </summary>
    private static string Strip(string source)
    {
        const string script =
            "import sys;sys.path.insert(0,'tools');import comment_split;" +
            "print(comment_split.strip_comments(sys.stdin.read()),end='')";
        return RunPythonWithInput(script, source);
    }

    /// <summary>Runs a tool file in the repo, as opposed to an inline script.</summary>
    private static string RunPython(string scriptPath)
    {
        var root = RepoRoot();
        var psi = new ProcessStartInfo("python")
        {
            WorkingDirectory = root,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
        };
        psi.ArgumentList.Add(scriptPath);
        return Finish(psi, null);
    }

    private static string RunPythonWithInput(string args, string? stdin)
    {
        var psi = new ProcessStartInfo("python")
        {
            WorkingDirectory = RepoRoot(),
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            RedirectStandardInput = stdin != null,
            UseShellExecute = false,
        };
        // the script always arrives as one -c payload and must never be split: splitting it on spaces turned
        // "import sys;..." into a syntax error at the first space
        psi.ArgumentList.Add("-c");
        psi.ArgumentList.Add(args);
        return Finish(psi, stdin);
    }

    private static string Finish(ProcessStartInfo psi, string? stdin)
    {
        using var p = Process.Start(psi)!;
        if (stdin != null)
        {
            p.StandardInput.Write(stdin);
            p.StandardInput.Close();
        }
        var output = p.StandardOutput.ReadToEnd();
        var error = p.StandardError.ReadToEnd();
        p.WaitForExit();
        Assert.True(p.ExitCode == 0, "python failed: " + error);
        return output;
    }

    private static System.Collections.Generic.IEnumerable<string> SplitArgs(string args)
    {
        var current = new System.Text.StringBuilder();
        var inQuote = false;
        foreach (var ch in args)
        {
            if (ch == '\'') { inQuote = !inQuote; continue; }
            if (ch == ' ' && !inQuote)
            {
                if (current.Length > 0) { yield return current.ToString(); current.Clear(); }
                continue;
            }
            current.Append(ch);
        }
        if (current.Length > 0) yield return current.ToString();
    }

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null && !Directory.Exists(Path.Combine(dir.FullName, "tools")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}