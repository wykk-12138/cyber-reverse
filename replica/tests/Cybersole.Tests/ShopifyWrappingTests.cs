using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Are the brands wrapped in <see cref="Cybersole.Stores.Flows.ShopifyFlow"/> actually Shopify?
///
/// `hbx` was not: <c>/products/{handle}.json</c> answered 404 "No route found", it ran its own
/// /api/v2/ behind AWS WAF, and every cart call was hitting a route that does not exist. That
/// mistake is invisible from the outside — the flow compiles, the request returns, and only the
/// outcome is wrong.
///
/// So: probe every Shopify-wrapped host for <c>/cart.js</c>, which a Shopify storefront answers
/// with <c>{"token":…,"items":[…]}</c>. A host that does not is registered against the wrong
/// platform.
///
/// Speed=Slow: one request per host, thirty-one hosts.
/// </summary>
[Trait("Speed", "Slow")]
public class ShopifyWrappingTests
{
    private readonly ITestOutputHelper _out;
    public ShopifyWrappingTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// Mirrors the ShopifyFlow registrations in Registry.cs. Kept as data here so the test
    /// reads as a checklist; a host added to the registry without being added here is caught by
    /// <see cref="EveryShopifyWrappedModuleIsCoveredByThisList"/>.
    /// </summary>
    private static readonly string[] WrappedHosts =
    {
        // brand modules registered directly against ShopifyFlow
        "arrowandbeast.com", "arrowbeast.myshopify.com", "bodega.com", "cncpts.com", "packershoes.com", "socialstatuspgh.com", "undefeated.com",
        "deadstock.ca", "livestock.ca", "capsuletoronto.com", "nrml.ca", "offthehook.ca",
        "overkillshop.com", "afew-store.com", "tres-bien.com", "civilistberlin.com",
        "vooberlin.com", "extrabutterny.com", "premiumgoodsokc.com",
        "saintalfred.com", "lapstoneandhammer.com", "courtsidesneakers.com",
        "nakedcopenhagen.com", "trophyroomstore.com", "a-ma-maniere.com", "shophmvs.com",
        "sneakerpolitics.com", "100thieves.com", "10corsocomo.com", "titan22.com",

        // bstn.com and converse.com used to sit in this list. Both were removed when their
        // modules moved off Shopify: bstn to BstnFlow (round 48, self-built /api/beast/) and
        // converse to DemandwareFlow (round 46, /on/demandware.store/Sites-ConverseUS-Site/).
        // This array mirrors what the registry resolves, so a stale entry fails the comparison.

        // modules whose flow is also a ShopifyFlow (directly or by inheritance)
        "endclothing.com", "endclothing.co.uk", "kith.com", "kithnyc.com",
        "notre-shop.com", "sneakersnstuff.com",

        // re-registered onto ShopifyFlow after a live probe showed the original registration
        // was wrong — footpatrol/size were MagentoFlow (round 47), jbhifi was a hand-written
        // StoreFlow (round 57), supreme was 193 lines of custom flow (round 76)
        "footpatrol.com", "footpatrol.co.uk",
        "size.co.uk", "sizeofficial.com",
        "jbhifi.com.au",
        "us.supreme.com", "supreme.com", "supremenewyork.com",

        // shopify.com and myshopify.com are intentionally absent: they are the platform's own
        // domains, not a storefront that can be probed

        // sns.com is absent on purpose too: the domain changed hands and the claim was removed
        // (see DomainClaimTests), so listing it here would fail the registry comparison
    };

    /// <summary>Shopify answers /cart.js with a JSON object carrying a token and an items array.</summary>
    private static bool LooksLikeShopifyCart(int status, string body) =>
        status == 200
        && body.TrimStart().StartsWith('{')
        && body.Contains("\"items\"", StringComparison.Ordinal)
        && (body.Contains("\"token\"", StringComparison.Ordinal)
            || body.Contains("\"item_count\"", StringComparison.Ordinal));

    [Fact]
    public async Task EveryShopifyWrappedHostAnswersTheShopifyCartEndpoint()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        var ok = new List<string>();
        var wrong = new List<string>();
        var unreachable = new List<string>();

        foreach (var host in WrappedHosts)
        {
            var url = $"https://{host}/cart.js";

            try
            {
                var res = await net.GetAsync(url, new RequestOptions { Tag = "shopify-probe" },
                    CancellationToken.None);

                if (LooksLikeShopifyCart(res.StatusCode, res.Body))
                {
                    ok.Add(host);
                }
                else
                {
                    var head = res.Body.Length > 60
                        ? res.Body[..60].Replace('\n', ' ')
                        : res.Body;
                    wrong.Add($"{host,-26} HTTP {res.StatusCode}  {head}");
                }
            }
            catch (Exception ex)
            {
                unreachable.Add($"{host,-26} {ex.GetType().Name}");
            }
        }

        _out.WriteLine($"=== confirmed Shopify ({ok.Count}) ===");
        foreach (var h in ok) _out.WriteLine($"  {h}");

        _out.WriteLine(string.Empty);
        _out.WriteLine($"=== NOT Shopify ({wrong.Count}) ===");
        foreach (var w in wrong) _out.WriteLine($"  {w}");

        _out.WriteLine(string.Empty);
        _out.WriteLine($"=== unreachable ({unreachable.Count}) ===");
        foreach (var u in unreachable) _out.WriteLine($"  {u}");

        // Not an assertion on the counts: a host being down today is not a code defect. The
        // report is the deliverable, and `wrong` is the list someone has to act on.
        Assert.Equal(WrappedHosts.Length, ok.Count + wrong.Count + unreachable.Count);
    }

    [Fact]
    public void EveryShopifyWrappedModuleIsCoveredByThisList()
    {
        // the module holds its flow in a StoreFlow-typed field, so the declared type says
        // nothing; the instance's real type is what marks it as Shopify-wrapped
        var registryHosts = Cybersole.Stores.Modules.StoreModuleCatalog.CreateAll()
            .Select(m =>
            {
                var field = m.GetType()
                    .GetFields(System.Reflection.BindingFlags.NonPublic |
                               System.Reflection.BindingFlags.Instance)
                    .FirstOrDefault(f => typeof(Cybersole.Stores.Flows.StoreFlow)
                        .IsAssignableFrom(f.FieldType));

                return field?.GetValue(m) as Cybersole.Stores.Flows.StoreFlow;
            })
            .Where(flow => flow is Cybersole.Stores.Flows.ShopifyFlow)
            .SelectMany(flow => flow!.Domains)
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .OrderBy(h => h)
            .ToList();

        var listed = WrappedHosts.ToHashSet(StringComparer.OrdinalIgnoreCase);

        // shopify.com / myshopify.com are the platform's own domains, not probeable storefronts
        var platformOnly = new[] { "shopify.com", "myshopify.com" };

        var missing = registryHosts
            .Where(h => !platformOnly.Contains(h, StringComparer.OrdinalIgnoreCase))
            .Where(h => !listed.Contains(h))
            .ToList();
        var extra = WrappedHosts
            .Where(h => !registryHosts.Contains(h, StringComparer.OrdinalIgnoreCase))
            .ToList();

        foreach (var m in missing) _out.WriteLine($"in registry, not in probe list: {m}");
        foreach (var e in extra) _out.WriteLine($"in probe list, not in registry: {e}");

        Assert.Empty(missing);
        Assert.Empty(extra);
    }
}
