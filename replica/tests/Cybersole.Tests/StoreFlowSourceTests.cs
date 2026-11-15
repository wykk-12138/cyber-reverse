using System.IO;
using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R275: <see cref="StoreFlowSteps.Flow"/> now says where its steps came from.
///
/// <para>
/// R274 found the table mixing two kinds of evidence: <c>structure-token-*</c> was read out of a literal and matches a
/// recovered segment step for step (15/15, 11/12), while the named store flows were reconstructed from endpoint families
/// and match 0–4 of their steps. Reporting both as "1:1" is the mistake this test exists to prevent.
/// </para>
/// </summary>
public sealed class StoreFlowSourceTests
{
    private readonly ITestOutputHelper _out;
    public StoreFlowSourceTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void EveryFlowIsLiteralBackedAndNamesItsLiteral()
    {
        // R289: the last two flows were assembled from evidence and are now literal-backed as well — nike from two d__
        // literals of one class (0x03385576 + 0x0338562c), johnlewis from one d__ literal plus the lambda row that names
        // the two steps R112 had to deduce by hand (0x0338a655 + 0x0338af47). So the endpoint bucket is empty, and the
        // test that used to require members in it now requires the opposite: nothing is left unverified.
        foreach (var flow in StoreFlowSteps.All)
            _out.WriteLine($"{flow.Store}: {flow.Source} ({flow.Count} steps)");

        var endpoints = StoreFlowSteps.All.Where(f => f.Source == StoreFlowSteps.FlowSource.Endpoint)
            .Select(f => f.Store).ToList();
        var literal = StoreFlowSteps.All.Where(f => f.Source == StoreFlowSteps.FlowSource.Literal)
            .Select(f => f.Store).OrderBy(n => n, System.StringComparer.Ordinal).ToList();

        _out.WriteLine("endpoint-derived: " + (endpoints.Count == 0 ? "(none)" : string.Join(", ", endpoints)));
        Assert.Empty(endpoints);
        Assert.Equal(8, literal.Count);
        Assert.Contains("nike", literal);
        Assert.Contains("johnlewis", literal);
        Assert.Contains("popmart", literal);
        Assert.Contains("structure-token-single", literal);
    }

    [Fact]
    public void TheDistinctionIsWrittenDown()
    {
        var source = File.ReadAllText(Path.Combine(Root(), "src", "Cybersole.Stores", "Flows", "StoreFlowSteps.cs"));
        Assert.Contains("must not", source, System.StringComparison.OrdinalIgnoreCase);
        Assert.Contains("FlowSource", source);
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }
}
