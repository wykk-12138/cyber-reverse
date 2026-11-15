using System.Diagnostics;
using Cybersole.Http;
using Cybersole.Stores.Modules;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Is each module's store actually reachable right now?
///
/// The coverage matrix says a flow implements seven steps. It cannot say whether the store those
/// steps point at still exists. Between rounds 47 and 77 nine modules were found registered
/// against a platform that had changed underneath them, and one more (hypecommerce) against a
/// parked domain. A reachability sweep is the cheapest way to see that class of rot whole.
///
/// Categories, deliberately separated because they mean different things:
///
///   live      the host answered 2xx/3xx — the module has somewhere to run
///   guarded   401/403/429 — the host is there and refuses automation; the module may still work
///             with a real session, so this is NOT counted as rot
///   wildcard  a bare storefront base such as myshopify.com — the root answers 404 by design,
///             because the shops live at <name>.myshopify.com. Round 150: this used to be
///             reported as Missing, which read as a defect when it is the host behaving correctly
///   missing   404/410 on the root — the domain resolves but has no site
///   reserved  a name reserved for documentation (.example, .invalid, .test, .localhost).
///             Round 151: demandware.example sat in this column for rounds, reported as Dead,
///             when it can never resolve by design. Same mistake as myshopify.com, one column over
///   dead      DNS or TLS failure — nothing to talk to
///
/// A warning about this machine's network: it runs Mihomo, whose DNS answers every A query with a
/// 198.18.x.x placeholder from its fake-IP pool. Seven of the nine Dead entries are that — the
/// proxy never forwarded the TLS handshake, and DoH shows bodega.com and offthehook.ca both have
/// real records. So `dead` here means "this sweep could not reach it", not "the shop is gone".
/// Verifying which needs a direct resolver; the sweep deliberately does not add one, because a
/// test that depends on a network path is not a test of the code.
///
/// Speed=Slow, network-bound. Roughly a minute for all 61 modules.
/// </summary>
[Trait("Speed", "Slow")]
public class ModuleReachabilityTests
{
    private readonly ITestOutputHelper _out;
    public ModuleReachabilityTests(ITestOutputHelper output) => _out = output;

    private enum State { Live, Guarded, Wildcard, Missing, Reserved, Dead }

    /// <summary>
    /// Hosts whose root is expected to 404: they are bases, not storefronts. A shop lives at
    /// <c>&lt;name&gt;.myshopify.com</c>, so asking the base for a page and getting 404 is the
    /// correct answer — the same reason <c>example.com</c> would not be "rot".
    /// </summary>
    private static readonly HashSet<string> WildcardBases = new(StringComparer.OrdinalIgnoreCase)
    {
        "myshopify.com",
        "shopify.com",
    };

    /// <summary>
    /// Reserved for documentation (RFC 2606). These can never resolve, so a failure here says
    /// nothing about the module.
    /// </summary>
    private static readonly string[] ReservedSuffixes =
    {
        ".example", ".invalid", ".test", ".localhost",
    };

    private static bool IsReserved(string host) =>
        ReservedSuffixes.Any(s => host.EndsWith(s, StringComparison.OrdinalIgnoreCase));

    [Fact]
    public async Task EveryModuleStillPointsAtSomething()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        var modules = StoreModuleCatalog.CreateAll().OrderBy(m => m.Id).ToList();
        var byState = new Dictionary<State, List<string>>();

        foreach (State s in Enum.GetValues<State>()) byState[s] = new List<string>();

        _out.WriteLine($"{"module",-16} {"host",-34} {"http",-5} {"state",-8} ms");
        _out.WriteLine(new string('-', 82));

        foreach (var module in modules)
        {
            var host = module.Domains.FirstOrDefault();
            if (string.IsNullOrEmpty(host))
            {
                byState[State.Dead].Add(module.Id);
                _out.WriteLine($"{module.Id,-16} {"(no domain)",-34} {"-",-5} {"Dead",-8}");
                continue;
            }

            // decided without touching the network: a reserved name can never resolve
            if (IsReserved(host))
            {
                byState[State.Reserved].Add(module.Id);
                _out.WriteLine($"{module.Id,-16} {host,-34} {"-",-5} {State.Reserved,-8}");
                continue;
            }

            var url = host.Contains("://", StringComparison.Ordinal) ? host : "https://" + host;
            var started = Stopwatch.StartNew();
            string http;
            State state;

            try
            {
                var res = await net.GetAsync(url, new RequestOptions { Tag = "reach" },
                    CancellationToken.None);
                started.Stop();

                http = res.StatusCode.ToString();
                state = res.StatusCode switch
                {
                    >= 200 and < 400 => State.Live,
                    401 or 403 or 429 => State.Guarded,
                    // a base host with no storefront of its own: 404 is the answer it should give
                    (404 or 410) when WildcardBases.Contains(host) => State.Wildcard,
                    404 or 410 => State.Missing,
                    _ => State.Live,       // 5xx still means something is listening
                };
            }
            catch (Exception)
            {
                started.Stop();
                http = "-";
                state = State.Dead;
            }

            byState[state].Add(module.Id);
            _out.WriteLine($"{module.Id,-16} {host,-34} {http,-5} {state,-8} {started.ElapsedMilliseconds}");
        }

        _out.WriteLine(string.Empty);
        _out.WriteLine($"total {modules.Count} modules");
        foreach (var (state, ids) in byState.OrderBy(kv => kv.Key))
            _out.WriteLine($"  {state,-8} {ids.Count,3}   {string.Join(", ", ids)}");

        // The assertion is deliberately weak: this sweep reports, it does not gate. A store being
        // down is not a code defect, and making it red would only teach the reader to ignore it.
        Assert.True(byState[State.Live].Count + byState[State.Guarded].Count >= 30,
            $"only {byState[State.Live].Count + byState[State.Guarded].Count} of {modules.Count} " +
            "modules point at a reachable host — check whether domains moved");
    }
}
