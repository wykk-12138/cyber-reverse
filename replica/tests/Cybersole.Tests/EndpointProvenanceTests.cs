using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 128: the provenance gate — every endpoint literal must appear <b>verbatim</b> in the string
/// pool extracted from the image.
///
/// <para>
/// Six times in this session an endpoint was invented by joining a host seen in one literal to a path
/// seen in another (Nike <c>buy/orders/v2</c>, BSTN <c>/api/beast</c>, Demandware
/// <c>Checkout-Submit*</c>, Shopify <c>cart/change.js</c>, Pop Mart <c>/api/*</c>, Scheels
/// <c>/v5/Order/</c> — the last of which was really Nike's). Each time the mistake was the same: the
/// host and the path never appeared together. This test makes that unrepresentable by checking the
/// concatenation against the pool.
/// </para>
///
/// <para>
/// The full check — including constants assembled from other constants — lives in
/// <c>tools/endpoint-provenance.py</c> and runs as verification step 8. This test covers the plain
/// literals, which is the majority, and skips when the pool dump is not present (a fresh clone has no
/// <c>analysis/pe_strings.txt</c>).
/// </para>
/// </summary>
public sealed class EndpointProvenanceTests
{
    private readonly ITestOutputHelper _out;

    public EndpointProvenanceTests(ITestOutputHelper output) => _out = output;

    private static DirectoryInfo RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir!;
    }

    private static string? PoolPath()
    {
        var candidate = Path.Combine(RepoRoot().Parent?.FullName ?? "", "analysis", "pe_strings.txt");
        return File.Exists(candidate) ? candidate : null;
    }

    /// <summary>Every plain endpoint literal in the flows is a literal that the image contains.</summary>
    [Fact]
    public void EveryEndpointLiteralExistsInTheImage()
    {
        var pool = PoolPath();
        if (pool is null)
        {
            _out.WriteLine("skipped: analysis/pe_strings.txt is not present");
            return;
        }

        var text = File.ReadAllText(pool);
        var flows = Path.Combine(RepoRoot().FullName, "src", "Cybersole.Stores", "Flows");
        var literal = new Regex("public const string (\\w+)\\s*=\\s*\"([^\"]{3,})\"\\s*;");

        var checkedCount = 0;
        var invented = new List<string>();

        foreach (var file in Directory.GetFiles(flows, "*.cs").OrderBy(f => f))
        {
            foreach (Match m in literal.Matches(File.ReadAllText(file)))
            {
                var value = m.Groups[2].Value;
                var looksLikeEndpoint = value.StartsWith("/", System.StringComparison.Ordinal)
                                        || value.Contains("://", System.StringComparison.Ordinal);
                if (!looksLikeEndpoint) continue;

                checkedCount++;
                if (!text.Contains(value, System.StringComparison.Ordinal))
                    invented.Add($"{Path.GetFileName(file)}:{m.Groups[1].Value} = {value}");
            }
        }

        _out.WriteLine($"{checkedCount} endpoint literals checked against the pool");
        foreach (var item in invented) _out.WriteLine("INVENTED: " + item);

        Assert.True(checkedCount > 100, $"only {checkedCount} literals found — the scan is broken");
        Assert.Empty(invented);
    }

    /// <summary>The full check exists as a tool and as a verification step.</summary>
    [Fact]
    public void TheFullCheckIsAStep()
    {
        var root = RepoRoot().FullName;

        Assert.True(File.Exists(Path.Combine(root, "tools", "endpoint-provenance.py")));

        var steps = File.ReadAllText(Path.Combine(root, "tools", "verify-steps.ps1"));
        Assert.Contains("endpoint provenance", steps);
        Assert.Contains("endpoint-provenance.py", steps);

        _out.WriteLine("step 8: endpoint provenance");
    }
}
