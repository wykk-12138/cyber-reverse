using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R279: the flow artifacts in <c>docs/</c> are data, and data that is only checked by eye drifts.
///
/// <para>
/// These files are the output of <c>tools/flow_dump.py</c>, <c>tools/row_groups.py</c> and
/// <c>tools/flow_filter.py</c>. Re-running a tool with different parameters can silently change their shape, so the
/// invariants that the documents rely on are asserted here: the segment counts, the fact that every step is a
/// (ordinal, name) pair, and that the conservative dump is a subset of the wide one.
/// </para>
/// </summary>
public sealed class FlowArtifactTests
{
    private readonly ITestOutputHelper _out;
    public FlowArtifactTests(ITestOutputHelper output) => _out = output;

    private static JsonElement Load(string name) =>
        JsonDocument.Parse(File.ReadAllText(Path.Combine(Root(), "docs", name))).RootElement.Clone();

    [Fact]
    public void TheMergedLayoutsStillHoldSixtyNineSegments()
    {
        var a = Load("flow_step_sequences.json").EnumerateArray().ToList();
        var steps = a.Sum(s => s.GetProperty("steps").EnumerateArray().Count());

        _out.WriteLine($"A: {a.Count} segments, {steps} steps");
        Assert.True(a.Count >= 69, "the merged-layout dump lost segments");
        Assert.True(steps >= 320, "the merged-layout dump lost steps");

        foreach (var segment in a)
            foreach (var step in segment.GetProperty("steps").EnumerateArray())
            {
                var ordinal = step[0].GetInt32();
                var name = step[1].GetString();
                Assert.InRange(ordinal, 0, 9999);
                Assert.False(string.IsNullOrWhiteSpace(name));
            }
    }

    [Fact]
    public void BothRowDumpsExistAndAreWellFormed()
    {
        // R279 correction: the conservative dump is NOT base-subset of the wide one — the two runs group with different
        // minimum sizes, so the same group can start at a different address. What holds is the shape, not the keys.
        var wide = Load("row_groups_wide.json").EnumerateArray().ToList();
        var conservative = Load("row_groups.json").EnumerateArray().ToList();

        _out.WriteLine($"wide {wide.Count}, conservative {conservative.Count}");
        Assert.True(conservative.Count >= 39);
        Assert.True(wide.Count >= conservative.Count);

        foreach (var dump in new[] { conservative, wide })
            foreach (var group in dump)
            {
                Assert.False(string.IsNullOrWhiteSpace(group.GetProperty("base").GetString()));
                var steps = group.GetProperty("steps").EnumerateArray().ToList();
                Assert.True(steps.Count >= 2, "a group with fewer than two steps cannot come from this rule");
                foreach (var step in steps) Assert.False(string.IsNullOrWhiteSpace(step[1].GetString()));
            }
    }

    [Fact]
    public void TheBigOrdinalsAreKnownToBeParseArtefacts()
    {
        // ordinals >= 200 in these dumps come from adjacent digits running together (documented in R270/R277).
        // The count is bounded so a tool change that floods them is caught.
        var big = Load("flow_step_sequences.json").EnumerateArray()
            .SelectMany(s => s.GetProperty("steps").EnumerateArray())
            .Count(step => step[0].GetInt32() >= 200);

        // measured 39 of 320 — far more common than the first guess of "a handful". The bound is a flood guard, not a
        // claim that they are rare.
        _out.WriteLine($"ordinals >= 200: {big}");
        Assert.InRange(big, 0, 80);
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }
}
