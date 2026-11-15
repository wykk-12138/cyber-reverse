using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 67, found in a screenshot: four rows rendered the same sentence twice.
///
/// <code>
/// Enable clock        [x] Enable clock
/// One checkout        [x] One checkout
/// Price check         [x] Price check
/// Linked delays       [x] Linked delays
/// </code>
///
/// Each was <c>UiKit.Row("X", UiKit.Check("X", v))</c>: the row draws the label on the left and
/// the checkbox draws its own Content on the right. Both are the same string, and neither is
/// wrong on its own — the pair is.
/// </summary>
public sealed class CheckboxLabelTests
{
    private readonly ITestOutputHelper _out;

    public CheckboxLabelTests(ITestOutputHelper output) => _out = output;

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }

    private static IEnumerable<(string File, string Line)> UiSources()
    {
        var ui = Path.Combine(RepoRoot(), "src", "Cybersole.Ui");
        foreach (var file in Directory.EnumerateFiles(ui, "*.cs", SearchOption.AllDirectories))
        {
            if (file.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")) continue;
            foreach (var line in File.ReadAllLines(file))
                yield return (Path.GetFileName(file), line);
        }
    }

    /// <summary>
    /// No row puts a label on both sides. The pattern is
    /// <c>UiKit.Row("X", ... UiKit.Check("X" ...)</c> on one line — same literal twice.
    /// </summary>
    [Fact]
    public void NoRowDuplicatesItsLabel()
    {
        var dupes = new List<string>();

        foreach (var (file, line) in UiSources())
        {
            // Skip comments. The doc comment in UiKit.cs quotes the old shape as an example, and
            // a matcher that counts its own documentation is the fourth substring-vs-set mistake
            // in this file's history.
            var trimmed = line.TrimStart();
            if (trimmed.StartsWith("//", StringComparison.Ordinal)) continue;

            // Same quoted literal appearing twice in one call to Row.
            var row = Regex.Match(line, @"UiKit\.Row\(""([^""]+)""");
            if (!row.Success) continue;

            var label = row.Groups[1].Value;
            var check = Regex.Match(line, $@"UiKit\.Check\(""{Regex.Escape(label)}""");
            if (check.Success) dupes.Add($"{file}: {line.Trim()}");
        }

        _out.WriteLine(dupes.Count == 0 ? "no duplicated row labels" : string.Join("\n", dupes));
        Assert.Empty(dupes);
    }

    /// <summary>
    /// <c>RowCheck</c> exists and is what those rows use now.
    /// </summary>
    [Fact]
    public void RowCheckIsUsedForLabelledBoxes()
    {
        var ui = Path.Combine(RepoRoot(), "src", "Cybersole.Ui");
        var kit = File.ReadAllText(Path.Combine(ui, "Views", "UiKit.cs"));

        var defines = kit.Contains("public static Control RowCheck(", StringComparison.Ordinal);
        var emptyContent = kit.Contains("Check(string.Empty, value, onChanged)", StringComparison.Ordinal);

        var callSites = new List<string>();
        foreach (var file in Directory.EnumerateFiles(ui, "*.cs", SearchOption.AllDirectories))
        {
            if (file.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")) continue;
            var n = Regex.Matches(File.ReadAllText(file), @"UiKit\.RowCheck\(").Count;
            if (n > 0) callSites.Add($"{Path.GetFileName(file)}:{n}");
        }

        _out.WriteLine($"defines={defines} emptyContent={emptyContent}");
        _out.WriteLine($"call sites: {string.Join(", ", callSites)}");

        Assert.True(defines, "UiKit.RowCheck is gone");
        Assert.True(emptyContent, "RowCheck no longer blanks the checkbox content");
        Assert.NotEmpty(callSites);
    }
}
