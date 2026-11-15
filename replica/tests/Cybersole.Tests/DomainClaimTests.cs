using Cybersole.Stores.Modules;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Domain claims that have gone stale.
///
/// Four hosts were flagged as suspicious in the Shopify sweep. Checking each one showed they are
/// not mostly "wrong platform" — they are *dead or repurposed domains*:
///
///   saintalfred.com      now a GoDaddy parked page (web-api.aws.parking.godaddy.com)
///   sns.com              now resolves to an unrelated managed-services company
///   trophyroomstore.com  404 at the root
///   civilistberlin.com   Sanity CMS, no commerce API at all
///
/// A dead claim is mostly harmless (nothing matches it). A claim on a domain that now belongs
/// to somebody else is actively harmful: that site's URLs get routed into a store flow and fail
/// in a way that looks like a storefront problem.
///
/// sneakersnstuff.com — the real SNS storefront — still answers Shopify's monorail and /cdn/shop
/// paths, so the module itself is correct; only the alias had to go.
/// </summary>
public class DomainClaimTests
{
    private readonly ITestOutputHelper _out;
    public DomainClaimTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void SnsNoLongerClaimsTheRepurposedAlias()
    {
        var sns = StoreModuleCatalog.CreateAll().FirstOrDefault(m => m.Id == "sns");

        Assert.NotNull(sns);
        Assert.Contains("sneakersnstuff.com", sns!.Domains);
        Assert.DoesNotContain("sns.com", sns.Domains);
    }

    [Fact]
    public void NoTwoModulesClaimTheSameDomain()
    {
        var claims = new Dictionary<string, List<string>>(StringComparer.OrdinalIgnoreCase);

        foreach (var module in StoreModuleCatalog.CreateAll())
        foreach (var domain in module.Domains)
        {
            if (!claims.TryGetValue(domain, out var owners))
                claims[domain] = owners = new List<string>();
            owners.Add(module.Id);
        }

        var contested = claims.Where(kv => kv.Value.Count > 1).ToList();
        foreach (var (domain, owners) in contested)
            _out.WriteLine($"{domain,-32} claimed by {string.Join(", ", owners)}");

        Assert.Empty(contested);
    }

    [Fact]
    public void EveryDeadDomainIsRecordedHereSoItIsNotRediscovered()
    {
        // The point of this test is the list, not the assertion: it is the place where a
        // dead or repurposed domain gets written down instead of being re-investigated.
        var knownDead = new[]
        {
            ("saintalfred.com", "GoDaddy parked page"),
            ("sns.com", "now an unrelated managed-services company"),
            ("trophyroomstore.com", "404 at the root"),
            ("civilistberlin.com", "Sanity CMS, no commerce API"),
            ("hypecommerce.com", "GoDaddy reseller parking page"),
            ("hypecommerce.io", "same operator, no storefront"),
            ("kids.nike.com", "no DNS record \u2014 Nike has no kids subdomain"),
            ("snkrs.nike.com", "no DNS record \u2014 the SNKRS app is not a host"),
            ("footpatrol.co.uk", "no DNS record \u2014 the store moved to footpatrol.com"),
            ("demandware.example", "placeholder, kept as a platform template"),
        };

        foreach (var (domain, why) in knownDead)
            _out.WriteLine($"{domain,-24} {why}");

        Assert.Equal(10, knownDead.Length);
    }
}
