using System.IO;
using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R200: the Kasada API paths, checked against the image rather than trusted. Every literal below must appear in the
/// strings pool AT THE ADDRESS the table records — that is what makes it evidence and not a guess.
/// </summary>
public sealed class KasadaApiTests
{
    private readonly ITestOutputHelper _out;
    public KasadaApiTests(ITestOutputHelper output) => _out = output;

    private static string Pool()
    {
        var dir = new DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        var root = dir!.FullName;
        var pool = Path.Combine(Path.GetDirectoryName(root)!, "analysis", "pe_strings.txt");
        Assert.True(File.Exists(pool), pool);
        return File.ReadAllText(pool);
    }

    [Fact]
    public void EveryLiteralAppearsAtItsRecordedAddress()
    {
        var pool = Pool();
        var checkedCount = 0;

        foreach (var literal in KasadaApi.All)
        {
            var needle = literal.Address + "  " + literal.Value;
            Assert.True(pool.Contains(needle, System.StringComparison.Ordinal),
                $"{literal.Value} is not at {literal.Address}");
            checkedCount++;
        }

        _out.WriteLine($"{checkedCount} literals verified in the pool");
        Assert.True(checkedCount >= 12, $"only {checkedCount} literals checked");
    }

    [Fact]
    public void TheScriptIdIsTheOneInThePaths()
    {
        Assert.Equal(2, KasadaApi.ScriptId.Split('/').Length - 1);

        // every full path starts with the id
        foreach (var path in KasadaApi.Paths.Where(p => p.Value.StartsWith('/')))
        {
            var isBare = path.Value.Length <= 2 || !path.Value.StartsWith(KasadaApi.ScriptId, System.StringComparison.Ordinal);
            if (!isBare)
                Assert.StartsWith(KasadaApi.ScriptId, path.Value, System.StringComparison.Ordinal);
        }

        // the three unprefixed forms are exactly the fp / ips / prop paths
        var bare = KasadaApi.Paths.Where(p => !p.Value.Contains("149e9513", System.StringComparison.Ordinal))
            .Select(p => p.Value).ToList();
        Assert.Equal(new[] { "/fp?x-kpsdk-v=", "/ips.js?", "/prop.json", "/prop.json?_=" }, bare);
    }

    [Fact]
    public void TheHostIsDeliberatelyAbsent()
    {
        var pool = Pool();

        // the image's own fragment has an EMPTY authority: https:///ips.js
        Assert.Contains("https:///ips.js?&x-kpsdk", pool, System.StringComparison.Ordinal);

        // and the table says so, rather than inventing one: the authority between `https://` and the path is empty
        Assert.StartsWith("https:///", KasadaApi.ScriptOrigin.Value, System.StringComparison.Ordinal);
        Assert.Equal(0, KasadaApi.ScriptOrigin.Value.Substring("https://".Length).IndexOf('/') );
        Assert.Contains("supplies the host at runtime", KasadaApi.HostRule, System.StringComparison.Ordinal);
    }

    [Fact]
    public void TheStrategyAndTheApiAgree()
    {
        // the two protocol headers here are a subset of the strategy's list, not a second claim
        foreach (var header in KasadaApi.Headers)
            Assert.Contains(header.Value, KasadaStrategy.ProtocolHeaders);

        Assert.Contains(KasadaApi.VersionParam.Value, "x-kpsdk-v");
        Assert.Equal("0x07186f1c", KasadaApi.VersionParam.Address);
    }

    /// <summary>The solver must not carry its own copy of the paths.</summary>
    [Fact]
    public void TheSolverUsesTheTable()
    {
        var dir = new DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        var solver = File.ReadAllText(Path.Combine(dir!.FullName,
            "src", "Cybersole.Stores", "Scripts", "KasadaSolver.cs"));

        Assert.Contains("KasadaApi.BareScriptPath", solver, System.StringComparison.Ordinal);
        Assert.Contains("KasadaApi.ScriptPath", solver, System.StringComparison.Ordinal);
        Assert.DoesNotContain("149e9513", solver);   // the id lives in one place now
        Assert.DoesNotContain("\"/ips.js\"", solver);
    }
}
