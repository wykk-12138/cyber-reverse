import io, re
# a test that keeps the two classes apart: only literal flows may be compared to a recovered segment
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\StoreFlowSourceTests.cs'
t = '''using System.IO;
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
    public void TheLiteralFlowsAreMarkedLiteral()
    {
        foreach (var flow in StoreFlowSteps.All)
            _out.WriteLine($"{flow.Store}: {flow.Source} ({flow.Count} steps)");

        var literal = StoreFlowSteps.All.Where(f => f.Source == StoreFlowSteps.FlowSource.Literal)
            .Select(f => f.Store).ToList();

        Assert.Equal(new[] { "structure-token-multi", "structure-token-single" }, literal);
    }

    [Fact]
    public void EveryOtherFlowIsEndpointDerivedAndSaidSo()
    {
        var endpoints = StoreFlowSteps.All.Where(f => f.Source == StoreFlowSteps.FlowSource.Endpoint)
            .Select(f => f.Store).ToList();

        Assert.Contains("nike", endpoints);
        Assert.Contains("popmart", endpoints);
        Assert.Contains("johnlewis", endpoints);
        Assert.DoesNotContain("structure-token-multi", endpoints);
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
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('StoreFlowSourceTests written')
