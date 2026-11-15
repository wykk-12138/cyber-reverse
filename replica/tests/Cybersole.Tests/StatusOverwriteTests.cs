using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Three "the code looks finished" hazards, each of which produced a real bug in an earlier round
/// and none of which the compiler or the existing tests could see.
/// </summary>
public class StatusOverwriteTests
{
    private readonly ITestOutputHelper _out;
    public StatusOverwriteTests(ITestOutputHelper output) => _out = output;

    private static string RepoRoot()
    {
        var dir = AppContext.BaseDirectory;
        while (dir is not null && !Directory.Exists(Path.Combine(dir, "src")))
            dir = Path.GetDirectoryName(dir);

        Assert.NotNull(dir);
        return dir;
    }

    private static IEnumerable<(string Rel, string Full)> Sources(string top)
    {
        var root = Path.Combine(RepoRoot(), top);
        foreach (var file in Directory.EnumerateFiles(root, "*.cs", SearchOption.AllDirectories))
        {
            var rel = Path.GetRelativePath(root, file).Replace('\\', '/');
            if (rel.Contains("/obj/") || rel.Contains("/bin/")) continue;
            yield return (rel, file);
        }
    }

    private static readonly Regex Catch = new(@"\bcatch\s*(\([^)]*\))?\s*\{", RegexOptions.Compiled);

    /// <summary>`_status.Text = …` or `Status = …`; returns the left-most identifier.</summary>
    private static readonly Regex Write =
        new(@"^\s*([A-Za-z_]\w*)(?:\.\w+)*\s*=\s*[^=]", RegexOptions.Compiled);

    /// <summary>Index of the brace that closes the block opened at <paramref name="open"/>.</summary>
    private static int ClosingBrace(string src, int open)
    {
        var depth = 0;
        for (var i = open; i < src.Length; i++)
        {
            if (src[i] == '{') depth++;
            else if (src[i] == '}')
            {
                depth--;
                if (depth == 0) return i;
            }
        }
        return -1;
    }

    /// <summary>
    /// A status message must not be overwritten one statement after the catch that produced it.
    ///
    /// Round 103: the Tasks page ended its start-all handler with `_status.Text = "Starting all
    /// tasks."` — placed after the try/catch, so every diagnostic the earlier code had written was
    /// gone before the user could read it. Round 122 found the identical shape in the sign-in
    /// dialog, where a failed browser launch reported "browser opened".
    /// </summary>
    [Fact]
    public void NoStatusWriteImmediatelyFollowsItsOwnCatch()
    {
        var hits = new List<string>();

        foreach (var (rel, file) in Sources("src"))
        {
            var src = File.ReadAllText(file);

            foreach (Match m in Catch.Matches(src))
            {
                var open = src.IndexOf('{', m.Index);
                if (open < 0) continue;
                var close = ClosingBrace(src, open);
                if (close < 0) continue;

                var written = new HashSet<string>();
                foreach (var bodyLine in src[(open + 1)..close].Split('\n'))
                {
                    var w = Write.Match(bodyLine);
                    if (w.Success) written.Add(w.Groups[1].Value);
                }
                if (written.Count == 0) continue;

                // first statement after the block, skipping blanks and comments
                var offset = 0;
                string? first = null;
                foreach (var raw in src[(close + 1)..].Split('\n').Skip(1))
                {
                    offset++;
                    var s = raw.Trim();
                    if (s.Length == 0 || s.StartsWith("//")) continue;
                    first = s;
                    break;
                }
                if (first is null) continue;

                var next = Write.Match(" " + first);
                if (!next.Success || !written.Contains(next.Groups[1].Value)) continue;

                var line = src[..close].Count(c => c == '\n') + 1 + offset;
                hits.Add($"{rel}:{line}  {first}");
            }
        }

        _out.WriteLine($"status writes right after their own catch: {hits.Count}");
        foreach (var h in hits) _out.WriteLine("  " + h);

        Assert.Empty(hits);
    }

    /// <summary>
    /// A one-line catch followed by an unconditional status write to the same receiver: the exact
    /// R122 layout in the sign-in dialog.
    /// </summary>
    [Fact]
    public void SuccessLineIsNotOutsideItsTry()
    {
        var hits = new List<string>();

        foreach (var (rel, file) in Sources("src"))
        {
            var lines = File.ReadAllLines(file);
            for (var i = 0; i + 1 < lines.Length; i++)
            {
                if (!Regex.IsMatch(lines[i], @"catch\s*(\([^)]*\))?\s*\{[^}]*\}\s*$")) continue;

                var brace = lines[i].IndexOf('{');
                if (brace < 0) continue;

                var catchWrite = Write.Match(lines[i][brace..]);
                var nextWrite = Write.Match(" " + lines[i + 1].Trim());
                if (!catchWrite.Success || !nextWrite.Success) continue;
                if (catchWrite.Groups[1].Value != nextWrite.Groups[1].Value) continue;

                hits.Add($"{rel}:{i + 2}  {lines[i + 1].Trim()}");
            }
        }

        _out.WriteLine($"success lines outside their try: {hits.Count}");
        foreach (var h in hits) _out.WriteLine("  " + h);

        Assert.Empty(hits);
    }

    /// <summary>
    /// A UI field holding a freshly constructed settings object in a file that also saves: almost
    /// certainly editing a copy.
    ///
    /// Round 113: CaptchaProvidersView edited registry.Configs and saved
    /// GlobalSettings.CaptchaProviders — two objects, no wire. Round 122: SolverWindow's
    /// `private readonly SolverSettings _settings = new();` meant seven toggles wrote into a
    /// throwaway while Config.Save() persisted the untouched list.
    ///
    /// Both were found by clicking, not by reading. This is the reading half.
    /// </summary>
    [Fact]
    public void NoUiFieldHoldsAThrowawaySettingsObjectWhileSaving()
    {
        // Round 145: the type pattern used to be [A-Z]\w*, which cannot match a qualified name.
        //
        //   private readonly SolverSettings _throwaway = new();               <- matched
        //   private readonly Cybersole.Core.Models.SolverSettings _t = new(); <- NOT matched
        //
        // Both are the same bug. A mutation using the qualified form stayed green, which is how
        // this was found; the fix is to let the pattern span dots.
        var throwaway = new Regex(
            @"private\s+(?:readonly\s+)?([A-Z][\w.]*(?:Settings|Config|Options|Document))\s+\w+\s*=\s*new\s*\(",
            RegexOptions.Compiled);

        var hits = new List<string>();

        foreach (var (rel, file) in Sources(Path.Combine("src", "Cybersole.Ui")))
        {
            var src = File.ReadAllText(file);
            if (!src.Contains("Config.Save()")) continue;   // nothing being persisted here

            foreach (Match m in throwaway.Matches(src))
            {
                var line = src[..m.Index].Count(c => c == '\n') + 1;
                hits.Add($"{rel}:{line}  {m.Value.Trim()}");
            }
        }

        _out.WriteLine($"throwaway settings objects in saving files: {hits.Count}");
        foreach (var h in hits) _out.WriteLine("  " + h);

        Assert.Empty(hits);
    }
}
