using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// No mojibake in source or docs.
///
/// Round 112 found 54 occurrences of three sequences — an em dash, a right arrow and a colon,
/// each written as two CJK-ish bytes followed by a question mark — scattered across 17 files.
/// They are what those characters look like when UTF-8 is decoded as GBK, so some file was
/// written with the wrong encoding at some point and the damage survived every later edit.
///
/// The literal sequences are spelled in code points below rather than typed here, because a test
/// that looks for mojibake must not contain any.
///
/// All 54 were inside doc comments, so no behaviour was ever wrong. That is exactly why they
/// matter: a reader who sees garbled punctuation in a comment has to wonder whether the code
/// around it was corrupted too, and there is no way to answer that by looking.
///
/// This test keeps them from coming back.
/// </summary>
public class SourceEncodingTests
{
    private readonly ITestOutputHelper _out;
    public SourceEncodingTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// A CJK ideograph immediately followed by a question mark or the replacement character is
    /// the signature of this corruption. Ordinary Chinese prose does not produce that pair, and
    /// these files are otherwise English, so a hit is always damage.
    /// </summary>
    ///
    /// Round 133 corrected this. The original pattern was `[\u4e00-\u9fff]{1,3}[\ufffd?]`, which
    /// flags any CJK character followed by a question mark — and that is ordinary Chinese
    /// punctuation: "确定吗?" is a correctly written UI string, not damage. The check only stayed
    /// green until round 131 added the real Chinese locale, at which point it produced 18 false
    /// positives in one file.
    ///
    /// What round 112 actually found were three specific sequences left by a UTF-8 file being
    /// read as GBK: U+9225, U+922B and U+95B3, each followed by '?'. Those are the tell. A bare
    /// U+FFFD is also damage. Nothing else is.
    private static readonly Regex Mojibake = new(
        @"\u9225\?|\u922b\?|\u95b3\?|\ufffd",
        RegexOptions.Compiled);

    private static string RepoRoot()
    {
        var dir = AppContext.BaseDirectory;
        while (dir is not null && !Directory.Exists(Path.Combine(dir, "src")))
            dir = Path.GetDirectoryName(dir);

        Assert.NotNull(dir);
        return dir;
    }

    [Fact]
    public void NoSourceFileContainsMojibake()
    {
        var root = RepoRoot();
        var hits = new List<string>();

        foreach (var top in new[] { "src", "tests", "tools", "docs" })
        {
            var start = Path.Combine(root, top);
            if (!Directory.Exists(start)) continue;

            foreach (var file in Directory.EnumerateFiles(start, "*", SearchOption.AllDirectories))
            {
                var rel = Path.GetRelativePath(root, file).Replace('\\', '/');
                if (rel.Contains("/obj/") || rel.Contains("/bin/")) continue;

                var ext = Path.GetExtension(file);
                if (ext is not (".cs" or ".md" or ".json" or ".ps1")) continue;

                string text;
                try { text = File.ReadAllText(file); }
                catch (Exception ex)
                {
                    hits.Add($"{rel}: unreadable as UTF-8 — {ex.GetType().Name}");
                    continue;
                }

                foreach (Match m in Mojibake.Matches(text))
                {
                    var line = text[..m.Index].Count(c => c == '\n') + 1;
                    hits.Add($"{rel}:{line}  {m.Value}");
                }
            }
        }

        _out.WriteLine($"mojibake hits: {hits.Count}");
        foreach (var h in hits.Take(20)) _out.WriteLine("  " + h);

        Assert.Empty(hits);
    }

    /// <summary>
    /// The round-112 repair replaced a broken sequence with "dash + space" — which is wrong when
    /// the sequence sat at a line break, because the following line already starts with a comment
    /// marker. One occurrence produced "cart.js" followed by an arrow, a space and "/// checkout"
    /// on the same line. This catches that shape (also spelled in code points, not typed).
    /// </summary>
    [Fact]
    public void NoCommentMarkerIsGluedToAnArrowOrDash()
    {
        var root = RepoRoot();
        var glued = new Regex(@"[\u2192\u2014]\s*///");
        var hits = new List<string>();

        foreach (var top in new[] { "src", "tests", "tools" })
        {
            var start = Path.Combine(root, top);
            if (!Directory.Exists(start)) continue;

            foreach (var file in Directory.EnumerateFiles(start, "*.cs", SearchOption.AllDirectories))
            {
                var rel = Path.GetRelativePath(root, file).Replace('\\', '/');
                if (rel.Contains("/obj/") || rel.Contains("/bin/")) continue;

                var lines = File.ReadAllLines(file);
                for (var i = 0; i < lines.Length; i++)
                {
                    if (glued.IsMatch(lines[i]))
                        hits.Add($"{rel}:{i + 1}  {lines[i].Trim()}");
                }
            }
        }

        _out.WriteLine($"glued comment markers: {hits.Count}");
        foreach (var h in hits.Take(20)) _out.WriteLine("  " + h);

        Assert.Empty(hits);
    }
}
