using System.Net;
using Cybersole.Stores.Modules;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// The first domain of every module must resolve.
///
/// This exists because of a real bug: FootpatrolFlow listed
/// <c>["footpatrol.co.uk", "footpatrol.com"]</c>, and the .co.uk host had stopped resolving. Since
/// Domains.First() is what both the router and the reachability sweep use, a working module
/// reported as unreachable. Fixing the order fixed the module; this test stops the order from
/// rotting again.
///
/// DNS only — no HTTP. That keeps it fast (milliseconds per host instead of seconds) and free of
/// rate limits, and it catches exactly the failure that happened: a host with no record.
///
/// Hosts that are known to be dead are excluded by name, and each one also appears in
/// DomainClaimTests.knownDead so the exclusion cannot be used to hide a new problem.
///
/// Speed=Slow only because it touches the network; it needs no browser and no HTTP.
/// </summary>
[Trait("Speed", "Slow")]
public class FirstDomainResolvesTests
{
    private readonly ITestOutputHelper _out;
    public FirstDomainResolvesTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// Modules whose first domain is deliberately unresolvable. Each entry must also be justified
    /// in DomainClaimTests.
    /// </summary>
    private static readonly Dictionary<string, string> AllowedDead = new(StringComparer.OrdinalIgnoreCase)
    {
        ["demandware"] = "platform template — demandware.example is a placeholder",
        ["nike-gs"] = "no Nike kids subdomain exists; GS is selected by size, not by host",
    };

    [Fact]
    public async Task TheFirstDomainOfEveryModuleResolves()
    {
        var failures = new List<string>();
        var checkedCount = 0;

        foreach (var module in StoreModuleCatalog.CreateAll().OrderBy(m => m.Id))
        {
            var host = module.Domains.FirstOrDefault();
            if (string.IsNullOrEmpty(host)) continue;

            // strip any scheme so Dns can take it
            var bare = host.Contains("://", StringComparison.Ordinal)
                ? new Uri(host).Host
                : host;

            if (AllowedDead.ContainsKey(module.Id))
            {
                _out.WriteLine($"{module.Id,-16} {bare,-32} allowed-dead ({AllowedDead[module.Id]})");
                continue;
            }

            checkedCount++;

            try
            {
                var addresses = await Dns.GetHostAddressesAsync(bare);
                if (addresses.Length == 0)
                {
                    failures.Add($"{module.Id}: {bare} resolved to nothing");
                    _out.WriteLine($"{module.Id,-16} {bare,-32} EMPTY");
                }
            }
            catch (Exception ex)
            {
                failures.Add($"{module.Id}: {bare} — {ex.GetType().Name}");
                _out.WriteLine($"{module.Id,-16} {bare,-32} FAILED {ex.GetType().Name}");
            }
        }

        _out.WriteLine(string.Empty);
        _out.WriteLine($"checked {checkedCount}, allowed-dead {AllowedDead.Count}, " +
                       $"failed {failures.Count}");

        if (failures.Count > 0)
        {
            _out.WriteLine(string.Empty);
            _out.WriteLine("these modules cannot be reached at all — move a working host to the " +
                           "front of Domains, or record the host as dead:");
            foreach (var f in failures) _out.WriteLine("  " + f);
        }

        Assert.Empty(failures);
    }

    /// <summary>
    /// The exclusion list must stay honest: every name in it has to still be a registered module.
    /// Otherwise the list slowly fills with names that no longer exist and starts excusing
    /// nothing while looking like it excuses something.
    /// </summary>
    [Fact]
    public void TheAllowListOnlyNamesModulesThatExist()
    {
        var ids = StoreModuleCatalog.CreateAll().Select(m => m.Id).ToHashSet(StringComparer.OrdinalIgnoreCase);
        var stale = AllowedDead.Keys.Where(k => !ids.Contains(k)).ToList();

        if (stale.Count > 0)
            _out.WriteLine("stale exclusions: " + string.Join(", ", stale));

        Assert.Empty(stale);
    }
}
