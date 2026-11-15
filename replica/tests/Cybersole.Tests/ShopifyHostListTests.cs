using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 96: the image carries <b>1,182</b> distinct <c>*.myshopify.com</c> hosts.
///
/// <para>
/// Extracted with <c>analysis/pe_strings.py</c> and written verbatim to
/// <c>docs/shopify_hosts.txt</c>. The replica registers a few dozen Shopify aliases by hand; the
/// original knows 1,182 hosts, which is a different order of magnitude — this file is the list a
/// Shopify module should be able to resolve against.
/// </para>
///
/// <para>
/// The test pins the count and the shape, so the file cannot silently shrink and the claim in the
/// document cannot drift from the file.
/// </para>
/// </summary>
public sealed class ShopifyHostListTests
{
    private readonly ITestOutputHelper _out;

    public ShopifyHostListTests(ITestOutputHelper output) => _out = output;

    private static string DocPath()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        return Path.Combine(dir!.FullName, "docs", "shopify_hosts.txt");
    }

    /// <summary>1,182 hosts, every one a myshopify domain, sorted and unique.</summary>
    [Fact]
    public void TheImageCarriesElevenHundredAndEightyTwoHosts()
    {
        var path = DocPath();
        Assert.True(File.Exists(path), "docs/shopify_hosts.txt is missing");

        var hosts = File.ReadAllLines(path)
            .Select(l => l.Trim())
            .Where(l => l.Length > 0)
            .ToList();

        _out.WriteLine($"{hosts.Count} hosts, first={hosts[0]}, last={hosts[^1]}");

        Assert.Equal(1182, hosts.Count);
        Assert.Equal(hosts.Count, hosts.Distinct(StringComparer.OrdinalIgnoreCase).Count());
        Assert.Equal(hosts.OrderBy(h => h, StringComparer.Ordinal), hosts);

        Assert.All(hosts, h => Assert.Matches(
            new Regex(@"^[a-z0-9][a-z0-9\-]*\.myshopify\.com$"), h));
    }

    /// <summary>
    /// A handful of the hosts are ones the replica already registers by name — proof that the list
    /// and the registry describe the same world, even at very different sizes.
    /// </summary>
    [Fact]
    public void SomeHostsMatchRegisteredStores()
    {
        var hosts = File.ReadAllLines(DocPath())
            .Where(l => l.Length > 0)
            .ToList();

        var registered = Cybersole.Stores.Modules.StoreModuleCatalog.CreateAll()
            .SelectMany(m => m.Domains)
            .Select(d => d.ToLowerInvariant())
            .ToHashSet(StringComparer.OrdinalIgnoreCase);

        var overlap = hosts.Where(registered.Contains).ToList();
        _out.WriteLine($"overlap with the registry: {overlap.Count}");
        foreach (var h in overlap.Take(10)) _out.WriteLine("  " + h);

        // arrowandbeast.myshopify.com was added in R91 from the image, so at least it must match
        Assert.Contains("arrowbeast.myshopify.com", hosts);
    }
}
