using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// The reading guide at the top of VERDICT.md states numbers. Numbers in prose go stale: nobody
/// recomputes them, and after a few rounds they describe a build that no longer exists.
///
/// R208 found this the way R198 found seven labels with no fields — by asking what each claim
/// rests on. Three of the five in that block can be derived here, so they are checked. The other
/// two cannot: the test count only exists after a run, and the line count changes with every
/// edit including this one. Those two stay written but are excluded by name, with the reason.
///
/// Doc tests are worth less than behaviour tests and are kept small for that reason. Their job is
/// narrow: catch the number that drifted, not prove the document true.
/// </summary>
public class SummaryBlockTests
{
    private readonly ITestOutputHelper _out;
    public SummaryBlockTests(ITestOutputHelper output) => _out = output;

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;

        return dir?.FullName ?? string.Empty;
    }

    private static string Read(string relative)
    {
        var path = Path.Combine(RepoRoot(), relative.Replace('/', Path.DirectorySeparatorChar));
        Assert.True(File.Exists(path), $"{relative} not found");
        return File.ReadAllText(path);
    }

    /// <summary>The guide sits between the title and the first historical section.</summary>
    private static string Guide()
    {
        var text = Read("docs/VERDICT.md");
        var start = text.IndexOf("# 这个文档怎么读", StringComparison.Ordinal);
        Assert.True(start >= 0, "the reading guide is gone");

        var end = text.IndexOf("## 零、", start, StringComparison.Ordinal);
        Assert.True(end > start, "the reading guide has no end marker");

        return text[start..end];
    }

    [Fact]
    public void ModuleCountInTheGuideMatchesTheRegistry()
    {
        var registry = Read("src/Cybersole.Stores/Modules/Registry.cs");

        // Count static registrations only. Registry.cs also has one inside a
        // `foreach (var store in customStores)` loop — `new ShopifyFlow(id, name, …)` — which
        // registers however many custom stores the user configured, so it is one occurrence of
        // text and a variable number of modules. The first version counted 62 because of it.
        var lines = registry.Split('\n')
            .Where(l => !l.TrimStart().StartsWith("//", StringComparison.Ordinal))
            .Where(l => Regex.IsMatch(l, @"new\s+\w+Flow\s*\("))
            .Where(l => !Regex.IsMatch(l, @"new\s+\w+Flow\s*\(\s*id\s*,"))   // the loop
            .ToList();

        _out.WriteLine($"static flow registrations: {lines.Count}");

        var guide = Guide();
        var claimed = Regex.Match(guide, @"注册模块 \| \*\*(\d+)\*\*");
        Assert.True(claimed.Success, "the guide no longer states a module count");

        var value = int.Parse(claimed.Groups[1].Value);
        _out.WriteLine($"guide claims: {value}");

        Assert.Equal(lines.Count, value);
    }

    [Fact]
    public void MutationCountInTheGuideMatchesTheScript()
    {
        var script = Read("tools/mutation-check.py");

        var count = Regex.Matches(script, @"""name"":\s*""").Count;
        _out.WriteLine($"mutations defined: {count}");

        var guide = Guide();
        // the cell reads "**23 条，全部 guard fired**" — the number is not alone between the
        // asterisks, so a pattern anchored on **\d+** alone misses it
        var claimed = Regex.Match(guide, @"变异检查 \| \*\*(\d+) 条");
        Assert.True(claimed.Success, "the guide no longer states a mutation count");

        var value = int.Parse(claimed.Groups[1].Value);
        _out.WriteLine($"guide claims: {value}");

        Assert.Equal(count, value);
    }

    [Fact]
    public void UiCountsInTheGuideMatchTheScan()
    {
        // same scan as UnreachedUiTypesTests, kept local rather than shared: a helper used by one
        // test is a helper that can be changed to make that test pass
        var root = Path.Combine(RepoRoot(), "src");
        var ui = Path.Combine(root, "Cybersole.Ui");

        var files = Directory.EnumerateFiles(root, "*.cs", SearchOption.AllDirectories)
            .Where(f => !f.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")
                        && !f.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}"))
            .ToDictionary(f => f, File.ReadAllText);
        var all = string.Join("\n", files.Values);

        var declared = new Regex(@"public\s+(sealed\s+|abstract\s+|static\s+)?class\s+(\w+)");
        var notAQuestion = new HashSet<string>(StringComparer.Ordinal) { "App", "UiKit", "SettingsModal" };

        int total = 0, unreachable = 0;
        foreach (var (path, text) in files)
        {
            if (!path.StartsWith(ui, StringComparison.OrdinalIgnoreCase)) continue;

            foreach (Match m in declared.Matches(text))
            {
                var mods = m.Groups[1].Value;
                var name = m.Groups[2].Value;
                if (notAQuestion.Contains(name)) continue;
                if (mods.Contains("abstract", StringComparison.Ordinal)) continue;
                if (mods.Contains("static", StringComparison.Ordinal)) continue;

                total++;
                if (!Regex.IsMatch(all, $@"\bnew\s+(?:[\w]+\.)*{Regex.Escape(name)}\s*\("))
                    unreachable++;
            }
        }

        _out.WriteLine($"UI classes: {total}, unreachable: {unreachable}");

        var guide = Guide();
        var claimed = Regex.Match(guide, @"UI 类 \| (\d+) 个，\*\*(\d+) 个不可达\*\*");
        Assert.True(claimed.Success, "the guide no longer states UI counts");

        _out.WriteLine($"guide claims: {claimed.Groups[1].Value} / {claimed.Groups[2].Value}");

        Assert.Equal(total, int.Parse(claimed.Groups[1].Value));
        Assert.Equal(unreachable, int.Parse(claimed.Groups[2].Value));
    }

    /// <summary>
    /// The two numbers this file cannot verify must still be there — deleting them would make the
    /// suite green while removing the claims a reader relies on most.
    /// </summary>
    [Fact]
    public void TheUnverifiableClaimsAreStillPresent()
    {
        var guide = Guide();

        Assert.Matches(@"单元测试（快） \| \*\*\d+ 通过", guide);
        Assert.Matches(@"源码 \| \d+ 个 `\.cs`", guide);

        _out.WriteLine("the test count and the line count are written, and checked by verify.ps1 " +
                       "rather than here: neither can be derived from source");
    }
}
