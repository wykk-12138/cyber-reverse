using System.Text.RegularExpressions;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Modules;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// VERDICT.md makes numeric claims. This test makes sure they stay true.
///
/// The first thing it caught: the document said 61 modules while verify.ps1 reported 62. The
/// script was counting every `new XModule(` literal in Registry.cs, and RegisterShopifyHost()
/// contains one inside a helper — so the script counted a helper call as a module. The real
/// figure was 61, and the script now reads only CreateAll().
///
/// A document that drifts from the code is worse than no document: it is read as authoritative
/// and is wrong.
/// </summary>
public class DocsConsistencyTests
{
    private readonly ITestOutputHelper _out;
    public DocsConsistencyTests(ITestOutputHelper output) => _out = output;

    private static string DocPath()
    {
        // tests run from tests/Cybersole.Tests/bin/Debug/net8.0
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "docs", "VERDICT.md")))
            dir = dir.Parent;

        return dir is null ? string.Empty : Path.Combine(dir.FullName, "docs", "VERDICT.md");
    }

    [Fact]
    public void TheModuleCountInVerdictMatchesTheCatalogue()
    {
        var path = DocPath();
        Assert.False(string.IsNullOrEmpty(path), "docs/VERDICT.md not found from the test bin dir");

        var doc = File.ReadAllText(path);
        var actual = StoreModuleCatalog.CreateAll().Count;

        _out.WriteLine($"catalogue: {actual} modules");

        // every "<n> 个模块" / "<n> modules" claim in the document
        // Fenced blocks are quoted output from past runs ("catalogue: 61 modules"), not
        // claims this document is making. R91 added a module and the guard went red on a log
        // line from three rounds earlier — leave history alone, scan prose only.
        var prose = Regex.Replace(doc, "```.*?```", "\n", RegexOptions.Singleline);

        // R918: scope to the summary block, not the whole file.
        //
        // VERDICT.md is an append-only log of more than forty-nine thousand lines, and it carries twelve prose claims
        // of the form "<n> 个模块" from rounds in which the catalogue genuinely held sixty-three entries. Replacing
        // those with sixty-four would make every one of them false -- they describe measurements taken at the time, and
        // one of them says so explicitly. The guard's own note above says fenced blocks are history and only prose is
        // scanned, which is the right intent; it could not tell a historical section from a current summary, because a
        // heading looks like a heading either way.
        //
        // So the scan covers the summary block, which starts at the document's status table and ends at the first
        // horizontal rule after it. That is where a claim about the catalogue today belongs. A historical claim inside
        // the log stays as it was written.
        var summaryStart = doc.IndexOf("| 注册模块 |", StringComparison.Ordinal);
        Assert.True(summaryStart >= 0, "VERDICT.md no longer has a module-count row");
        var summaryEnd = doc.IndexOf("\n---", summaryStart, StringComparison.Ordinal);
        var summary = summaryEnd < 0 ? doc[summaryStart..] : doc[summaryStart..summaryEnd];

        var claims = Regex.Matches(summary, @"(\d+)\s*(?:个模块|modules)")
            .Select(m => int.Parse(m.Groups[1].Value))
            .Where(n => n >= 20)                    // ignore unrelated small numbers
            .Distinct()
            .ToList();

        _out.WriteLine($"claims in VERDICT: {string.Join(", ", claims)}");

        Assert.True(claims.Count > 0, "VERDICT no longer states a module count — update this test");
        Assert.All(claims, n => Assert.Equal(actual, n));
    }

    /// <summary>
    /// The "N 个模块" phrase in the verdict must not spread further.
    ///
    /// <para>
    /// R881. <see cref="TheModuleCountInVerdictMatchesTheCatalogue"/> has gone red four times — R457, R464, R813 and
    /// R880 — and every time the repair was to change the number, which holds only until the next module lands. The
    /// phrase is the trap: the guard scans for a number followed by "个模块" and cannot tell a claim about the
    /// catalogue's size from a sentence reporting that some round handled that many. Thirteen such sentences are in the
    /// document today, all correct, all fragile.
    /// </para>
    ///
    /// <para>
    /// This test does not weaken that guard or rewrite history. It fixes a ceiling: the count may fall as sentences are
    /// reworded but may not rise, so the habit is caught where it is formed. To state the catalogue's size, cite
    /// docs/METRICS.md or say "模块" without a number.
    /// </para>
    ///
    /// <para>
    /// The ceiling is sixteen rather than the thirteen I first wrote, and that correction is part of the point: my
    /// counting script disagreed with this test, the test was right, and the discrepancy came from my own bad
    /// measurement rather than from a difference between Python and C#. A ceiling derived from a hand count would have
    /// been a number asserted from a tool I had not checked.
    /// </para>
    /// </summary>
    [Fact]
    public void TheModuleCountPhraseDoesNotSpread()
    {
        const int ceiling = 16;

        var path = DocPath();
        Assert.False(string.IsNullOrEmpty(path), "docs/VERDICT.md not found from the test bin dir");

        var doc = File.ReadAllText(path);
        var prose = Regex.Replace(doc, "```.*?```", "\n", RegexOptions.Singleline);
        var count = Regex.Matches(prose, @"(\d+)\s*(?:个模块|modules)")
            .Select(m => int.Parse(m.Groups[1].Value))
            .Where(n => n >= 20)
            .Count();

        _out.WriteLine($"'N 个模块' sentences in prose: {count} (ceiling {ceiling})");

        Assert.True(count <= ceiling,
            $"the phrase spread from {ceiling} to {count}. Reword the new sentence without a number — cite " +
            "docs/METRICS.md instead — rather than raising this ceiling.");
    }

    [Fact]
    public void TheCoverageTestAndTheCatalogueAgree()
    {
        // the coverage matrix walks CreateAll(), so the two numbers must be the same by
        // construction. This pins it so a future refactor cannot quietly diverge them.
        var all = StoreModuleCatalog.CreateAll();
        var distinctIds = all.Select(m => m.Id).Distinct().Count();

        _out.WriteLine($"modules: {all.Count}, distinct ids: {distinctIds}");
        Assert.Equal(all.Count, distinctIds);
    }

    [Fact]
    public void EveryModuleHasAtLeastOneDomain()
    {
        var missing = StoreModuleCatalog.CreateAll()
            .Where(m => m.Domains is null || m.Domains.Count == 0)
            .Select(m => m.Id)
            .ToList();

        if (missing.Count > 0)
            _out.WriteLine($"without a domain: {string.Join(", ", missing)}");

        Assert.Empty(missing);
    }

    /// <summary>
    /// VERDICT claims "13 条逐字对齐". ErrorCatalogTests already pins the catalogue at 13;
    /// this pins the document to the same number, so the two cannot drift apart.
    /// </summary>
    [Fact]
    public void TheErrorTextCountInVerdictMatchesTheCatalogue()
    {
        var path = DocPath();
        Assert.False(string.IsNullOrEmpty(path));

        var doc = File.ReadAllText(path);
        var actual = ErrorCatalog.All.Count;

        // any "<n> 条" followed by wording about the error texts
        // R426: narrowed to error-specific wording - the old pattern also caught "39 条文案" / "8 条逐字"
        var claims = Regex.Matches(doc, @"(\d+)\s*条(?:错误文案|错误文本)")
            .Select(m => int.Parse(m.Groups[1].Value))
            .Distinct()
            .ToList();

        _out.WriteLine($"ErrorCatalog.All.Count = {actual}");
        _out.WriteLine($"claims in VERDICT: {string.Join(", ", claims)}");

        Assert.True(claims.Count > 0, "VERDICT no longer states an error-text count");
        Assert.All(claims, n => Assert.Equal(actual, n));
    }

    /// <summary>
    /// Every gap the document lists must belong to exactly one of the three classes, and each
    /// class must have at least one item. A gap that is not classified is a gap nobody knows
    /// what to do with — which is why this section exists separately from the achievements.
    /// </summary>
    [Fact]
    public void EveryGapIsAssignedToAClass()
    {
        var path = DocPath();
        Assert.False(string.IsNullOrEmpty(path));

        var doc = File.ReadAllText(path);

        var start = doc.IndexOf("## 十一、缺口清单", StringComparison.Ordinal);
        Assert.True(start >= 0, "the gap inventory section is missing");

        var section = doc[start..];
        var heads = Regex.Matches(section, @"### ([ABC]) 类")
            .Select(m => m.Groups[1].Value)
            .ToList();

        _out.WriteLine("classes present: " + string.Join(", ", heads));
        Assert.Equal(new[] { "A", "B", "C" }, heads);

        foreach (var cls in new[] { "A", "B", "C" })
        {
            var idx = section.IndexOf($"### {cls} 类", StringComparison.Ordinal);
            var next = section.IndexOf("### ", idx + 4, StringComparison.Ordinal);
            var block = next < 0 ? section[idx..] : section[idx..next];

            var rows = block.Split('\n')
                .Count(l => l.StartsWith("| ")
                            && !l.StartsWith("| 项")
                            && !l.StartsWith("|---"));

            _out.WriteLine($"  class {cls}: {rows} item(s)");
            Assert.True(rows >= 1, $"class {cls} has no items");
        }
    }

    /// <summary>
    /// The platform count claims "N / N" in several places. Hybris was added in round 64 and six
    /// spots kept saying 14/14 until round 88 — nothing caught it, because there is no Platform
    /// entity in the code to compare against.
    ///
    /// So this checks internal consistency instead: every "a / b" platform claim must have
    /// a == b, and all of them must agree with each other. A future addition that edits some but
    /// not all of them will fail here.
    /// </summary>
    [Fact]
    public void ThePlatformCountClaimsAgreeWithEachOther()
    {
        var path = DocPath();
        Assert.False(string.IsNullOrEmpty(path));

        var doc = File.ReadAllText(path);

        var claims = Regex.Matches(doc, @"平台\s*\*{0,2}(\d+)\s*\*{0,2}\s*/\s*\*{0,2}(\d+)")
            .Select(m => (Have: int.Parse(m.Groups[1].Value), Total: int.Parse(m.Groups[2].Value)))
            .Where(c => c.Total >= 10)
            .Distinct()
            .ToList();

        _out.WriteLine("platform claims: " +
                       string.Join(", ", claims.Select(c => $"{c.Have}/{c.Total}")));

        Assert.NotEmpty(claims);
        Assert.All(claims, c => Assert.Equal(c.Total, c.Have));
        Assert.Single(claims);
    }

    /// <summary>
    /// Numbers that are measurements rather than facts must say so. A p50 ratio changes every
    /// run; a Settings page count came from reading the GUI once. If the document presents them
    /// as fixed truths it will be wrong on the next run, and a reader has no way to tell.
    /// </summary>
    [Fact]
    public void MeasuredNumbersAreLabelledAsSnapshots()
    {
        var path = DocPath();
        Assert.False(string.IsNullOrEmpty(path));

        var doc = File.ReadAllText(path);

        // the efficiency section must carry a caveat within a few lines of the ratio
        var ratio = doc.IndexOf("p50 ratio", StringComparison.Ordinal);
        if (ratio >= 0)
        {
            var window = doc.Substring(ratio, Math.Min(900, doc.Length - ratio));
            var labelled = window.Contains("样本", StringComparison.Ordinal)
                           || window.Contains("snapshot", StringComparison.OrdinalIgnoreCase)
                           || window.Contains("快照", StringComparison.Ordinal);

            _out.WriteLine($"efficiency ratio found; sample-size caveat nearby: {labelled}");
            Assert.True(labelled, "the p50 block must state its sample size");
        }

        // the GUI baseline must say it was read once, not continuously verified
        var gui = doc.IndexOf("Settings 页", StringComparison.Ordinal);
        if (gui >= 0)
        {
            var window = doc.Substring(gui, Math.Min(600, doc.Length - gui));
            var labelled = window.Contains("基线", StringComparison.Ordinal)
                           || window.Contains("一次", StringComparison.Ordinal)
                           || window.Contains("快照", StringComparison.Ordinal);

            _out.WriteLine($"Settings claim found; baseline wording nearby: {labelled}");
            Assert.True(labelled, "the Settings page count must be described as a baseline");
        }

        Assert.True(true);
    }
}
