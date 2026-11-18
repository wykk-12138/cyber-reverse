using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R246: the XAML binding gap can only shrink.
///
/// <para>
/// <c>docs/xaml_bindings.json</c> is the original's compiled-XAML binding table (174 types, 819 members). Every round
/// since R225 has been closing the difference between it and the replica, by name, across the whole <c>src/</c> tree.
/// Nothing stopped a rename from <b>re-opening</b> a gap that had already been closed — this test does: the real gap
/// (noise excluded) may never exceed the number recorded here, and the number must come down when work lands.
/// </para>
///
/// <para>
/// "Noise" is the compiler's own generic instantiations (<c>HasMultiple_87</c>, <c>Value_100</c>) — identified by
/// <b>shape</b>, not by whichever examples happened to be seen.
/// </para>
/// </summary>
public sealed class BindingGapRatchetTests
{
    /// <summary>The ceiling. Lower it in the same commit that closes members; never raise it.</summary>
    private const int MaxRealGap = 16;   // R432: re-baselined to the measured 16 (R430 closed one name but left the ceiling at 17)

    private static readonly Regex Noise = new(@"^(HasMultiple|Value)_\d+$", RegexOptions.Compiled);

    private readonly ITestOutputHelper _out;
    public BindingGapRatchetTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheRealGapNeverGrows()
    {
        var (noise, real, missing) = Measure();

        _out.WriteLine($"noise {noise}, real {real} (ceiling {MaxRealGap})");
        foreach (var m in missing.Take(40)) _out.WriteLine("  " + m);

        Assert.True(real <= MaxRealGap,
            $"the binding gap grew to {real} (ceiling {MaxRealGap}); a rename re-opened a member that used to be closed");
    }

    [Fact]
    public void TheTableIsStillTheOriginalsInventory()
    {
        var table = JsonDocument.Parse(File.ReadAllText(Path.Combine(Root(), "docs", "xaml_bindings.json")))
            .RootElement;

        var types = table.EnumerateObject().Count();
        var members = table.EnumerateObject().Sum(t => t.Value.EnumerateArray().Count());

        _out.WriteLine($"{types} types, {members} members");
        Assert.True(types >= 174);
        // R1112: the floor drops 819 -> 814 because five of those members were artifacts. A markup
        // extension or converter sits in a descriptor's FIRST position as the binding helper and
        // never as the owner, so the property recorded against it belongs to the owner. Measured
        // over 2,474 descriptor pairs: the four Localize*Extension types appear only in the first
        // position (15 occurrences) and never in the owner position. The generator now records them
        // with no members (analysis/_xaml_bindings.py), and this ratchet follows the corrected
        // inventory rather than the inflated one.
        Assert.True(members >= 814);
    }

    private static (int Noise, int Real, List<string> Missing) Measure()
    {
        var table = JsonDocument.Parse(File.ReadAllText(Path.Combine(Root(), "docs", "xaml_bindings.json")))
            .RootElement;

        var src = Path.Combine(Root(), "src");
        var blob = string.Join("\n", Directory
            .EnumerateFiles(src, "*.cs", SearchOption.AllDirectories)
            .Where(f => !f.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")
                        && !f.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}"))
            .Select(f => StripComments(File.ReadAllText(f))));

        var noise = 0;
        var real = 0;
        var missing = new List<string>();

        foreach (var type in table.EnumerateObject())
        {
            foreach (var member in type.Value.EnumerateArray())
            {
                var name = member.GetString();
                if (name is null) continue;
                if (Regex.IsMatch(blob, @"\b" + Regex.Escape(name) + @"\b")) continue;

                if (Noise.IsMatch(name))
                {
                    noise++;
                    continue;
                }

                real++;
                missing.Add(type.Name.Split('.').Last() + "." + name);
            }
        }

        return (noise, real, missing);
    }

    /// <summary>
    /// Removes comments before matching. Without this a name like <c>Plus</c> looks "present" because some unrelated
    /// comment says "plus" — R249 found exactly that: the ledger had been counting prose as code.
    /// </summary>
    private static string StripComments(string text)
    {
        text = Regex.Replace(text, @"/\*.*?\*/", " ", RegexOptions.Singleline);
        return Regex.Replace(text, @"(?<!:)//[^\n]*", " ");   // not "https://..."
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }

    [Fact]
    public void TheBacklogDocQuotesTheCeiling()
    {
        var doc = File.ReadAllText(Path.Combine(Root(), "docs", "BINDING_BACKLOG.md"));

        // R434: the ledger no longer hard-codes the number at all. R433 decision 1 moved every "current value"
        // into docs/METRICS.md (generated by tools/metrics_report.py) precisely because a number living in six
        // documents is a number that will be wrong in five of them. So the thing to ratchet now is the *link*:
        // the ledger must point at the single source of truth, and must not re-introduce a literal count.
        Assert.Contains("docs/METRICS.md", doc, System.StringComparison.Ordinal);
        Assert.DoesNotContain($"当前 {MaxRealGap} =", doc, System.StringComparison.Ordinal);
        _out.WriteLine("backlog doc points at docs/METRICS.md (no literal count); ratchet ceiling " + MaxRealGap);
    }
}
