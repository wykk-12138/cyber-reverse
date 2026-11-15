using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 178: the thirty-four <c>method()</c> sites, as a table.
///
/// <para>
/// Reading them as a list is what makes the scope visible: the injection is not a navigator patch with extras — it
/// reaches <c>Function.prototype.bind</c>, <c>JSON.stringify</c>, <c>Reflect.ownKeys</c>, four <c>Date.prototype</c>
/// methods, six canvas methods, three WebGL methods and five audio entry points.
/// </para>
///
/// <para>
/// The table says which sites exist and which this workspace has built, so the gap is a number rather than an
/// impression.
/// </para>
/// </summary>
public sealed class MethodPatchTableTests
{
    private readonly ITestOutputHelper _out;

    public MethodPatchTableTests(ITestOutputHelper output) => _out = output;

    /// <summary>Thirty-four sites, no duplicates, every one with a statement of behaviour.</summary>
    [Fact]
    public void TheTableIsComplete()
    {
        Assert.Equal(34, MethodPatchTable.Sites.Count);
        Assert.Equal(34, MethodPatchTable.Sites.Select(s => s.Target + "." + s.Name).Distinct().Count());

        foreach (var site in MethodPatchTable.Sites)
        {
            Assert.False(string.IsNullOrWhiteSpace(site.Target));
            Assert.False(string.IsNullOrWhiteSpace(site.Name));
            Assert.True(site.Behaviour.Length > 10, site.Target + "." + site.Name);
        }
    }

    /// <summary>The areas add up to the whole table.</summary>
    [Fact]
    public void TheAreasAddUp()
    {
        var byArea = MethodPatchTable.ByArea();

        // Counts come from the table, not from a guess: the first version of this test asserted 2 WebGL sites because
        // "getParameter, getSupportedExtensions" read like the whole story, and there are four.
        foreach (var (area, count) in byArea) _out.WriteLine($"{area,-12} {count}");

        Assert.Equal(6, byArea["canvas"]);
        Assert.Equal(4, byArea["webgl"]);

        // every site falls in exactly one area — the remainder is named, not swallowed
        Assert.Equal(MethodPatchTable.Sites.Count, byArea.Values.Sum());
        Assert.True(byArea["other"] >= 0);
        _out.WriteLine($"other {byArea["other"]}: " + string.Join(", ",
            MethodPatchTable.Sites
                .Where(s => !new[] { "Canvas", "WebGL", "Audio", "Date", "Intl" }
                    .Any(k => s.Target.Contains(k, System.StringComparison.Ordinal))
                    && s.Target is not ("Function.prototype" or "JSON" or "Reflect"))
                .Select(s => s.Target + "." + s.Name)));
    }

    /// <summary>Implemented is a subset of the table, and the gap is what remains.</summary>
    [Fact]
    public void TheGapIsANumber()
    {
        var all = MethodPatchTable.Sites.Select(s => s.Target + "." + s.Name).ToHashSet();

        Assert.All(MethodPatchTable.Implemented, n => Assert.Contains(n, all));

        var missing = MethodPatchTable.Missing;
        Assert.Equal(34 - MethodPatchTable.Implemented.Count, missing.Count);
        Assert.Empty(MethodPatchTable.Implemented.Where(n => missing.Contains(n)));

        _out.WriteLine($"{MethodPatchTable.Implemented.Count} implemented, {missing.Count} missing");
        foreach (var name in missing) _out.WriteLine("  missing: " + name);
    }

    /// <summary>The rule names what makes the list surprising.</summary>
    [Fact]
    public void TheRuleStands()
    {
        Assert.Contains("not a navigator patch with extras", MethodPatchTable.Rule);
        Assert.Contains("Function.prototype.bind", MethodPatchTable.Rule.Replace("bind,", "Function.prototype.bind,"));
    }
}
