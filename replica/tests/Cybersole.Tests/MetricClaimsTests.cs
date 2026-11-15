using System;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Keeps <c>docs/METRIC_CLAIMS.md</c> honest as the tools evolve: every tool it names must exist, and every metric
/// the report runner declares must have a section in it.
/// </summary>
/// <remarks>
/// The document is **hand-written** while `docs/METRICS.md` is generated, so nothing else keeps them together. Without
/// this guard, adding a seventh metric or renaming a script leaves a document that still reads authoritatively and is
/// silently incomplete — which is the failure mode the document itself is about.
///
/// Two invariants, both mechanical:
///
/// <list type="number">
/// <item>every <c>tools/&lt;name&gt;.py</c> mentioned in the document exists on disk;</item>
/// <item>every <c>tools/&lt;name&gt;.py</c> in <c>metrics_report.py</c>'s METRICS list is mentioned in the document.</item>
/// </list>
///
/// It deliberately does **not** check the numbers. Those have one source (`docs/METRICS.md`), and the document is
/// written to avoid quoting them at all.
/// </remarks>
[Collection("external-tools")]
public sealed class MetricClaimsTests
{
    private static readonly Regex ToolPath = new(@"tools/([A-Za-z0-9_]+\.py)", RegexOptions.Compiled);

    private readonly ITestOutputHelper _out;

    public MetricClaimsTests(ITestOutputHelper output) => _out = output;

    /// <summary>Every tool the document names must exist under <c>replica/tools/</c>.</summary>
    [Fact]
    public void EveryToolTheDocumentNamesExists()
    {
        var (repo, replica) = Roots();
        var doc = File.ReadAllText(Path.Combine(repo, "docs", "METRIC_CLAIMS.md"));

        var named = new HashSet<string>();
        foreach (Match m in ToolPath.Matches(doc))
        {
            named.Add(m.Groups[1].Value);
        }

        _out.WriteLine("tools named: " + string.Join(", ", named));
        Assert.NotEmpty(named);

        var missing = new List<string>();
        foreach (var name in named)
        {
            if (!File.Exists(Path.Combine(replica, "tools", name)))
            {
                missing.Add(name);
            }
        }

        Assert.True(missing.Count == 0,
            "docs/METRIC_CLAIMS.md names tools that do not exist: " + string.Join(", ", missing));
    }

    /// <summary>Every metric the report runner executes must be covered by a section in the document.</summary>
    [Fact]
    public void EveryMetricInTheRunnerIsCoveredByTheDocument()
    {
        var (repo, replica) = Roots();
        var doc = File.ReadAllText(Path.Combine(repo, "docs", "METRIC_CLAIMS.md"));
        var runner = File.ReadAllText(Path.Combine(replica, "tools", "metrics_report.py"));

        // the METRICS list only: between its opening bracket and the matching close
        var start = runner.IndexOf("METRICS = [", StringComparison.Ordinal);
        Assert.True(start >= 0, "METRICS list not found in metrics_report.py");
        var end = runner.IndexOf(']', start);
        Assert.True(end > start, "METRICS list is not terminated");

        var block = runner[start..end];
        var declared = new HashSet<string>();
        foreach (Match m in ToolPath.Matches(block))
        {
            declared.Add(m.Groups[1].Value);
        }

        _out.WriteLine("metrics declared: " + string.Join(", ", declared));
        Assert.NotEmpty(declared);

        var uncovered = new List<string>();
        foreach (var name in declared)
        {
            if (!doc.Contains("tools/" + name, StringComparison.Ordinal))
            {
                uncovered.Add(name);
            }
        }

        Assert.True(uncovered.Count == 0,
            "these metrics run but have no section in docs/METRIC_CLAIMS.md: " + string.Join(", ", uncovered));
    }

    /// <summary>
    /// The metric index in <c>BLOCKERS.md</c> points at section numbers; every one of them must exist.
    /// </summary>
    /// <remarks>
    /// The index answers "I don't believe this number, what do I read?" (R606). It is hand-written like the claims
    /// document, so the same hazard applies: a renumbering or a reworded heading leaves a pointer into nothing, and
    /// a pointer into nothing is worse than no pointer — it reads as if the explanation exists.
    /// </remarks>
    [Fact]
    public void EverySectionTheMetricIndexReferencesExists()
    {
        var (repo, _replica) = Roots();
        var doc = File.ReadAllText(Path.Combine(repo, "docs", "BLOCKERS.md"));

        var headings = new HashSet<int>();
        foreach (Match m in Regex.Matches(doc, @"^##\s+(\d+)\.", RegexOptions.Multiline))
        {
            headings.Add(int.Parse(m.Groups[1].Value));
        }

        Assert.NotEmpty(headings);

        // the index block: from its heading to the next top-level heading
        var start = doc.IndexOf("## 1.5 度量索引", StringComparison.Ordinal);
        Assert.True(start >= 0, "the metric index section is missing from BLOCKERS.md");
        var next = doc.IndexOf("\n## ", start + 3, StringComparison.Ordinal);
        var block = next > start ? doc[start..next] : doc[start..];

        var referenced = new HashSet<int>();
        foreach (Match m in Regex.Matches(block, @"§(\d+)"))
        {
            referenced.Add(int.Parse(m.Groups[1].Value));
        }

        _out.WriteLine($"index references {referenced.Count} sections; document has {headings.Count} headings");
        Assert.NotEmpty(referenced);

        var dangling = new List<int>();
        foreach (var n in referenced)
        {
            if (!headings.Contains(n))
            {
                dangling.Add(n);
            }
        }

        dangling.Sort();
        Assert.True(dangling.Count == 0,
            "the metric index points at sections that do not exist: " + string.Join(", ", dangling));
    }

    private static (string Repo, string Replica) Roots()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "src")))
        {
            dir = dir.Parent;
        }

        Assert.True(dir?.Parent is not null, "could not locate the repository root from " + AppContext.BaseDirectory);
        return (dir!.Parent!.FullName, dir.FullName);
    }
}
