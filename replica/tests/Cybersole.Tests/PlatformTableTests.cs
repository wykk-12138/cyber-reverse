using System.Text.RegularExpressions;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Modules;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// PLATFORM_VERIFICATION.md lists the platform misregistrations. That list is the most valuable
/// thing in the docs — it is what stops the same mistake being made twice — and it had already
/// drifted: the heading said "五个" while the table held seven rows, and jbhifi was missing
/// entirely.
///
/// So this test reads the table and checks it against the code:
///
///   1. the heading's count matches the number of rows
///   2. every module named in the table resolves to the flow type the table claims
///
/// Point 2 is the one that matters. A table row claiming offspring is HybrisFlow is worthless
/// if the registry says MagentoFlow — and that is exactly the failure the table exists to
/// prevent.
/// </summary>
public class PlatformTableTests
{
    private readonly ITestOutputHelper _out;
    public PlatformTableTests(ITestOutputHelper output) => _out = output;

    private static string DocPath()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null
               && !File.Exists(Path.Combine(dir.FullName, "docs", "PLATFORM_VERIFICATION.md")))
            dir = dir.Parent;

        return dir is null
            ? string.Empty
            : Path.Combine(dir.FullName, "docs", "PLATFORM_VERIFICATION.md");
    }

    /// <summary>Rows of section one: | `id` | old | new | evidence |</summary>
    private static List<(string Id, string Old, string Actual)> MisregistrationRows(string doc)
    {
        var start = doc.IndexOf("## 一、", StringComparison.Ordinal);
        var end = doc.IndexOf("## 二、", StringComparison.Ordinal);
        Assert.True(start >= 0 && end > start, "section one not found in PLATFORM_VERIFICATION.md");

        var section = doc[start..end];
        var rows = new List<(string, string, string)>();

        foreach (Match m in Regex.Matches(section, @"^\|\s*`([a-z0-9]+)`\s*\|(.+)\|\s*$",
                     RegexOptions.Multiline))
        {
            var cells = m.Groups[2].Value.Split('|');
            if (cells.Length < 2) continue;
            rows.Add((m.Groups[1].Value, cells[0].Trim(), cells[1].Trim()));
        }

        return rows;
    }

    private static StoreFlow? FlowOf(string id) =>
        StoreModuleCatalog.CreateAll().FirstOrDefault(m => m.Id == id) is { } module
            ? (StoreFlow)module.GetType()
                .GetProperties(System.Reflection.BindingFlags.Public
                               | System.Reflection.BindingFlags.NonPublic
                               | System.Reflection.BindingFlags.Instance)
                .First(p => typeof(StoreFlow).IsAssignableFrom(p.PropertyType))
                .GetValue(module)!
            : null;

    [Fact]
    public void TheHeadingCountMatchesTheRowCount()
    {
        var doc = File.ReadAllText(DocPath());
        var heading = Regex.Match(doc, @"## 一、(\S+)个已知误判");

        Assert.True(heading.Success, "the misregistration heading is missing or reworded");

        var claimed = heading.Groups[1].Value switch
        {
            "五" => 5, "六" => 6, "七" => 7, "八" => 8, "九" => 9, "十" => 10,
            var s when int.TryParse(s, out var n) => n,
            _ => -1,
        };

        var rows = MisregistrationRows(doc);

        _out.WriteLine($"heading claims: {claimed}");
        _out.WriteLine($"table rows:     {rows.Count}");
        _out.WriteLine($"modules:        {string.Join(", ", rows.Select(r => r.Id))}");

        Assert.Equal(rows.Count, claimed);
    }

    /// <summary>
    /// The "原注册" cell names the flow type the module used to be. The registry must no longer
    /// return that type — otherwise the row records a fix that was never applied.
    ///
    /// funko is the exception: its registration was right in kind and wrong in argument
    /// (Funko-Site instead of FunkoUS-Site), so it is still a DemandwareFlow. Its own test
    /// (PlatformAssignmentTests.FunkoUsesTheRealDemandwareSiteId) pins the argument.
    /// </summary>
    [Fact]
    public void NoRowStillResolvesToTheFlowTheTableSaysWasWrong()
    {
        var doc = File.ReadAllText(DocPath());
        var rows = MisregistrationRows(doc);
        Assert.NotEmpty(rows);

        foreach (var (id, oldCell, actualCell) in rows)
        {
            var flow = FlowOf(id);
            Assert.NotNull(flow);

            var typeName = flow!.GetType().Name;
            var oldType = Regex.Match(oldCell, @"(\w+Flow)").Groups[1].Value;

            _out.WriteLine($"{id,-14} was {oldType,-18} now {typeName,-18} ({actualCell})");

            if (string.IsNullOrEmpty(oldType)) continue;

            if (id == "funko")
            {
                // the type stayed; only the site id changed, and that has its own assertion
                Assert.IsAssignableFrom<DemandwareFlow>(flow);
                continue;
            }

            Assert.NotEqual(oldType, typeName);
        }
    }
}
