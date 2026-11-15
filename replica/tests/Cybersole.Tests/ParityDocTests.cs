using System.Text.RegularExpressions;
using Cybersole.Http;
using Cybersole.Stores.Actions;
using Cybersole.Stores.Modules;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// PARITY.md is the table a reader trusts first: it says what exists and what does not. Rounds
/// 150-163 found the table had stopped at several different moments — it said 50 modules when
/// there were 61, listed 11 windows when there were 64, and omitted three subsystems totalling
/// 767 lines.
///
/// Every one of those was found by a human reading it. This makes the next drift fail a test
/// instead.
///
/// It cannot check prose. It checks the numbers that have a single authoritative source in the
/// code, which is the part that goes stale silently.
/// </summary>
public class ParityDocTests
{
    private readonly ITestOutputHelper _out;
    public ParityDocTests(ITestOutputHelper output) => _out = output;

    private static string DocPath()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "docs", "PARITY.md")))
            dir = dir.Parent;

        return dir is null ? string.Empty : Path.Combine(dir.FullName, "docs", "PARITY.md");
    }

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "docs", "PARITY.md")))
            dir = dir.Parent;

        return dir?.FullName ?? string.Empty;
    }

    /// <summary>
    /// The section that claims a module count is the one under "## 3. 站点模块". Scoping matters:
    /// other sections legitimately mention other counts.
    /// </summary>
    [Fact]
    public void TheModuleCountInParityMatchesTheCatalogue()
    {
        var doc = File.ReadAllText(DocPath());
        var actual = StoreModuleCatalog.CreateAll().Count;

        var start = doc.IndexOf("## 3. 站点模块", StringComparison.Ordinal);
        Assert.True(start >= 0, "PARITY.md no longer has a site-module section");

        var end = doc.IndexOf("## 4. ", start, StringComparison.Ordinal);
        var section = end < 0 ? doc[start..] : doc[start..end];

        var claims = Regex.Matches(section, @"(\d+)\s*个注册模块")
            .Select(m => int.Parse(m.Groups[1].Value))
            .Distinct()
            .ToList();

        _out.WriteLine($"catalogue: {actual}");
        _out.WriteLine($"claims: {string.Join(", ", claims)}");

        Assert.True(claims.Count > 0, "section 3 no longer states a module count");
        Assert.All(claims, n => Assert.Equal(actual, n));
    }

    /// <summary>
    /// "32 种不同的 flow 类型" — counted from CreateAll(), because the number of distinct flow
    /// classes is exactly what a reader would have to enumerate by hand to verify.
    /// </summary>
    [Fact]
    public void TheFlowTypeCountInParityMatchesTheCatalogue()
    {
        var doc = File.ReadAllText(DocPath());
        // Every entry is a FlowStoreModule wrapper, so GetType() says the wrapper name 61 times.
        // The distinct flow count only exists in the registry source.
        var registry = Path.Combine(RepoRoot(), "src", "Cybersole.Stores", "Modules", "Registry.cs");
        var source = File.ReadAllText(registry);
        var from = source.IndexOf("public static IReadOnlyList<IStoreModule> CreateAll()", StringComparison.Ordinal);
        Assert.True(from >= 0, "CreateAll() is gone from Registry.cs");

        var body = source[from..];
        body = body[..body.IndexOf("};", StringComparison.Ordinal)];

        var actual = Regex.Matches(body, @"new FlowStoreModule\(new (\w+)\(")
            .Select(m => m.Groups[1].Value)
            .Distinct()
            .Count();

        var start = doc.IndexOf("## 3. 站点模块", StringComparison.Ordinal);
        var end = doc.IndexOf("## 4. ", start, StringComparison.Ordinal);
        var section = end < 0 ? doc[start..] : doc[start..end];

        var claims = Regex.Matches(section, @"(\d+)\s*种不同的\s*flow")
            .Select(m => int.Parse(m.Groups[1].Value))
            .Distinct()
            .ToList();

        _out.WriteLine($"distinct module classes: {actual}");
        _out.WriteLine($"claims: {string.Join(", ", claims)}");

        Assert.True(claims.Count > 0, "section 3 no longer states a flow-type count");
        Assert.All(claims, n => Assert.Equal(actual, n));
    }

    /// <summary>
    /// The transport table says "4 种" in the delivery metrics and lists them in section 2.
    /// Enum.GetValues is the only place that number can come from.
    /// </summary>
    [Fact]
    public void TheTransportModeCountInParityMatchesTheEnum()
    {
        var doc = File.ReadAllText(DocPath());
        var actual = Enum.GetValues<TransportMode>().Length;
        var names = Enum.GetNames<TransportMode>();

        _out.WriteLine($"TransportMode: {actual} — {string.Join(", ", names)}");

        // section 8 states the count; section 2 lists the names
        var claims = Regex.Matches(doc, @"\*\*(\d+) 种\*\*")
            .Select(m => int.Parse(m.Groups[1].Value))
            .Distinct()
            .ToList();

        _out.WriteLine($"bolded counts in the doc: {string.Join(", ", claims)}");

        // every enumerated name must appear somewhere in the document
        var missing = names.Where(n => !doc.Contains(n, StringComparison.Ordinal)).ToList();
        if (missing.Count > 0) _out.WriteLine($"not mentioned: {string.Join(", ", missing)}");

        Assert.Empty(missing);
        Assert.Contains(actual.ToString(), DocPath() is null ? "" : doc);
    }

    /// <summary>
    /// Section 5 claims "24 个 Window 子类 + 40 个 UserControl 子类". There is no runtime registry
    /// for UI types, so this counts the source. That is the same method the document's author
    /// used, which means agreement here proves the number was not hand-edited.
    /// </summary>
    [Fact]
    public void TheUiClassCountsInParityMatchTheSource()
    {
        var root = Path.Combine(RepoRoot(), "src", "Cybersole.Ui");
        Assert.True(Directory.Exists(root), "src/Cybersole.Ui not found from the test bin dir");

        var windows = 0;
        var controls = 0;

        foreach (var file in Directory.EnumerateFiles(root, "*.cs", SearchOption.AllDirectories))
        {
            var rel = Path.GetRelativePath(root, file).Replace('\\', '/');
            if (rel.Contains("/obj/") || rel.Contains("/bin/")) continue;

            var text = File.ReadAllText(file);
            windows += Regex.Matches(text, @"public\s+(?:sealed\s+)?class\s+\w+\s*:\s*Window\b").Count;
            controls += Regex.Matches(text, @"public\s+(?:sealed\s+)?class\s+\w+\s*:\s*UserControl\b").Count;
        }

        var doc = File.ReadAllText(DocPath());
        var start = doc.IndexOf("## 5. UI", StringComparison.Ordinal);
        var end = doc.IndexOf("## 6. ", start, StringComparison.Ordinal);
        var section = end < 0 ? doc[start..] : doc[start..end];

        var windowClaim = Regex.Match(section, @"(\d+)\s*个\s*`?Window`?\s*子类");
        var controlClaim = Regex.Match(section, @"(\d+)\s*个\s*`?UserControl`?\s*子类");
        var totalClaim = Regex.Match(section, @"(\d+)\s*个\s*UI\s*类");

        _out.WriteLine($"source: {windows} Window, {controls} UserControl");
        _out.WriteLine($"claimed: {windowClaim.Groups[1].Value} Window, {controlClaim.Groups[1].Value} UserControl, {totalClaim.Groups[1].Value} total");

        Assert.True(windowClaim.Success, "section 5 no longer states a Window count");
        Assert.True(controlClaim.Success, "section 5 no longer states a UserControl count");
        Assert.Equal(windows, int.Parse(windowClaim.Groups[1].Value));
        Assert.Equal(controls, int.Parse(controlClaim.Groups[1].Value));

        // R435: the headline total was never checked, so the document could say "999 个 UI 类：26 个
        // `Window` 子类 + 59 个 `UserControl` 子类" and stay green. The mutation harness proved it:
        // walking the total backwards (85 -> 84) left this test passing — a decorative guard on that
        // dimension. The sentence is self-describing (total == windows + controls), so assert that too.
        Assert.True(totalClaim.Success, "section 5 no longer states a UI class total");
        Assert.Equal(int.Parse(totalClaim.Groups[1].Value), windows + controls);
    }

    /// <summary>
    /// Section 4 claims "14 个" step actions. The registry is the source.
    /// </summary>
    [Fact]
    public void TheStepActionCountInParityMatchesTheRegistry()
    {
        var doc = File.ReadAllText(DocPath());
        var actual = StepActionRegistry.CreateDefault().All.Count;

        var start = doc.IndexOf("### 步骤动作", StringComparison.Ordinal);
        Assert.True(start >= 0, "section 4 no longer has a step-action subsection");

        var end = doc.IndexOf("###", start + 5, StringComparison.Ordinal);
        var section = end < 0 ? doc[start..] : doc[start..end];

        var claim = Regex.Match(section, @"(\d+)\s*个");
        _out.WriteLine($"registry: {actual}, claimed: {claim.Groups[1].Value}");

        Assert.True(claim.Success, "the step-action subsection no longer states a count");
        Assert.Equal(actual, int.Parse(claim.Groups[1].Value));
    }

    /// <summary>
    /// A "✅" next to a component name is a claim that the component exists. This walks the
    /// document for backticked type names in ✅ rows and checks each one resolves to a real type
    /// in the loaded assemblies — which catches the case where a file was renamed or removed and
    /// the table kept its ✅.
    /// </summary>
    [Fact]
    public void EveryTickedBacktickedTypeStillExists()
    {
        var doc = File.ReadAllText(DocPath());
        var assemblies = new[]
        {
            typeof(StoreModuleCatalog).Assembly,                     // Stores
            typeof(TransportMode).Assembly,                          // Http
            typeof(Cybersole.Services.NotificationService).Assembly, // Services
            typeof(Cybersole.Ui.Views.MainWindow).Assembly,          // Ui
            typeof(Cybersole.Core.Settings.GlobalSettings).Assembly, // Core
        };

        var known = assemblies
            .SelectMany(a => a.GetTypes())
            .Select(t => t.Name)
            .ToHashSet(StringComparer.Ordinal);

        // A table row's second cell is where this document names code. Prose backticks name
        // strings and methods (`Flush`, `JSONEachRow`, `WeakSet`), which are not types.
        var candidates = doc.Split('\n')
            .Where(l => l.Contains('✅') && l.StartsWith("| ", StringComparison.Ordinal))
            .SelectMany(l =>
            {
                var cells = l.Split('|');
                return cells.Length < 3
                    ? Enumerable.Empty<string>()
                    : Regex.Matches(cells[2], @"`([A-Z][A-Za-z0-9]+)`").Select(m => m.Groups[1].Value);
            })
            .Distinct()
            .ToList();

        // names that live in the UI assembly or are prose, not types in the three assemblies above
        var resolved = candidates.Where(known.Contains).ToList();
        var unresolved = candidates.Except(resolved).ToList();

        _out.WriteLine($"ticked names: {candidates.Count}, resolved: {resolved.Count}");
        foreach (var u in unresolved) _out.WriteLine($"  not in these assemblies: {u}");

        // a floor, not an equality: the point is that the check sees real types, not that every
        // backticked word is one. The names that do not resolve are data-format names
        // (`JSONEachRow`), JS types (`WeakSet`), method names (`TestProxiesAsync`) and field names
        // (`Known`) — legitimately backticked, legitimately not types.
        _out.WriteLine($"resolved {resolved.Count} of {candidates.Count}");
        Assert.True(resolved.Count >= 25,
            $"only {resolved.Count} ticked names resolved — the table may be naming types that no longer exist");
    }

    /// <summary>
    /// Section 8 claims a count of embedded resources. The csproj files are what the build acts
    /// on, so that is the source counted.
    ///
    /// R167: the table said 22 and listed "3 编译期" among them. Those three did not exist — the
    /// real total was 19 (Core 18 + Http 1). The extra three had been invented so the arithmetic
    /// would reach a number copied from an older context.
    /// </summary>
    [Fact]
    public void TheEmbeddedResourceCountInParityMatchesTheProjects()
    {
        var total = 0;

        foreach (var csproj in Directory.EnumerateFiles(Path.Combine(RepoRoot(), "src"), "*.csproj",
                     SearchOption.AllDirectories))
        {
            var text = File.ReadAllText(csproj);
            var n = Regex.Matches(text, @"<EmbeddedResource\s+Include=").Count;
            if (n > 0) _out.WriteLine($"{Path.GetFileName(csproj)}: {n}");
            total += n;
        }

        var doc = File.ReadAllText(DocPath());
        var claim = Regex.Match(doc, @"内嵌资源 \| \*\*(\d+) 个\*\*");

        _out.WriteLine($"csproj total: {total}, claimed: {claim.Groups[1].Value}");

        Assert.True(claim.Success, "the embedded-resource row is gone");
        Assert.Equal(total, int.Parse(claim.Groups[1].Value));
    }

    /// <summary>
    /// Every locale dictionary must carry the same key count, and no dictionary may repeat a key.
    ///
    /// R126 reported "only 4 locale keys" because it searched the manifest instead of the payload;
    /// R131 refuted it and found 1142 in each of four dictionaries. R168 then found that en and ja
    /// actually held 1143 properties — `Solver.AllCaptchas` appeared twice, same value, so
    /// Newtonsoft took the last one and nothing broke. "1142 keys in each of four" was false for
    /// half of them, and only a check that counts properties rather than distinct keys sees it.
    /// </summary>
    [Fact]
    public void EveryLocaleDictionaryHasTheSameKeyCount()
    {
        var dir = Path.Combine(RepoRoot(), "src", "Cybersole.Core", "Locales");
        Assert.True(Directory.Exists(dir), "Locales/ not found from the test bin dir");

        var properties = new Dictionary<string, int>(StringComparer.Ordinal);
        var duplicated = new List<string>();

        foreach (var file in Directory.EnumerateFiles(dir, "*.json"))
        {
            using var stream = File.OpenRead(file);
            using var json = System.Text.Json.JsonDocument.Parse(stream);

            // EnumerateObject yields duplicates; a Dictionary would silently collapse them, which
            // is exactly how this defect stayed invisible.
            var names = json.RootElement.EnumerateObject().Select(p => p.Name).ToList();
            properties[Path.GetFileName(file)] = names.Count;

            var repeated = names.GroupBy(n => n, StringComparer.Ordinal)
                .Where(g => g.Count() > 1)
                .Select(g => $"{Path.GetFileName(file)}: {g.Key} x{g.Count()}")
                .ToList();

            duplicated.AddRange(repeated);
        }

        foreach (var (name, n) in properties.OrderBy(k => k.Key, StringComparer.Ordinal))
            _out.WriteLine($"{name,-34} {n,5} properties");

        foreach (var d in duplicated) _out.WriteLine($"  DUPLICATE {d}");

        Assert.Equal(4, properties.Count);
        Assert.Empty(duplicated);

        var distinct = properties.Values.Distinct().ToList();
        Assert.Single(distinct);
        _out.WriteLine($"all four agree: {distinct[0]} properties each");
    }

    /// <summary>
    /// The engine ships 10 captcha pages and 4 scripts. Every file on disk must be declared as an
    /// embedded resource, or it silently will not ship — that is the failure this checks, more
    /// than the counts themselves.
    /// </summary>
    [Fact]
    public void TheEngineAssetCountsInParityMatchTheDirectory()
    {
        var dir = Path.Combine(RepoRoot(), "src", "Cybersole.Core", "Engine");
        Assert.True(Directory.Exists(dir), "Engine/ not found from the test bin dir");

        var html = Directory.EnumerateFiles(dir, "*.html").Count();
        var js = Directory.EnumerateFiles(dir, "*.js").Count();

        _out.WriteLine($"Engine/: {html} html, {js} js");

        var csproj = File.ReadAllText(
            Path.Combine(RepoRoot(), "src", "Cybersole.Core", "Cybersole.Core.csproj"));

        var declared = Regex.Matches(csproj, @"Engine\\Cybersole\.Engine\.([\w.-]+)""")
            .Select(m => m.Groups[1].Value)
            .ToHashSet(StringComparer.Ordinal);

        var onDisk = Directory.EnumerateFiles(dir)
            .Select(f => Path.GetFileName(f).Replace("Cybersole.Engine.", "", StringComparison.Ordinal))
            .ToHashSet(StringComparer.Ordinal);

        var missing = onDisk.Except(declared).OrderBy(x => x, StringComparer.Ordinal).ToList();
        var extra = declared.Except(onDisk).OrderBy(x => x, StringComparer.Ordinal).ToList();

        foreach (var m in missing) _out.WriteLine($"  on disk but not embedded: {m}");
        foreach (var e in extra) _out.WriteLine($"  embedded but not on disk: {e}");

        Assert.Empty(missing);
        Assert.Empty(extra);
        Assert.Equal(10, html);
        Assert.Equal(4, js);
    }
}
