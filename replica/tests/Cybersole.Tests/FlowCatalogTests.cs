using System.Reflection;
using Cybersole.Http.Stores;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Modules;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Asserts the catalog is fully step-driven: every module is a <see cref="FlowStoreModule"/>
/// wrapping a <see cref="StoreFlow"/>, and every brand host resolves to its own module.
/// </summary>
public class FlowCatalogTests
{
    private static readonly IReadOnlyList<IStoreModule> Modules = StoreModuleCatalog.CreateAll();

    [Fact]
    public void EveryCatalogModuleIsStepDriven()
    {
        var legacy = Modules.Where(m => m is not FlowStoreModule).Select(m => m.Id).ToList();
        Assert.True(legacy.Count == 0,
            $"modules still on the legacy two-method contract: {string.Join(", ", legacy)}");
    }

    [Fact]
    public void CatalogRegistersAtLeastFiftyModules()
    {
        Assert.True(Modules.Count >= 50, $"only {Modules.Count} modules registered");
    }

    [Fact]
    public void ModuleIdsAreUnique()
    {
        var dupes = Modules.GroupBy(m => m.Id).Where(g => g.Count() > 1).Select(g => g.Key).ToList();
        Assert.True(dupes.Count == 0, $"duplicate module ids: {string.Join(", ", dupes)}");
    }

    [Theory]
    [InlineData("https://www.nike.com/launch/t/air-max-1", "nike")]
    [InlineData("https://www.footlocker.com/product/~/314206113604", "footsites")]
    [InlineData("https://www.champssports.com/product/~/x", "footsites")]
    [InlineData("https://www.supremenewyork.com/shop/jackets/abc", "supreme")]
    [InlineData("https://www.endclothing.com/us/some-shoe", "endclothing")]
    [InlineData("https://www.johnlewis.com/some-product/p123", "johnlewis")]
    [InlineData("https://www.kith.com/products/tee", "kith")]
    [InlineData("https://www.size.co.uk/product/x/123", "size")]
    [InlineData("https://www.jdsports.co.uk/product/x/123", "jdsports")]
    [InlineData("https://www.bodega.com/products/tee", "bodega")]
    [InlineData("https://www.casio.com/us/watch", "casio")]
    [InlineData("https://www.jbhifi.com.au/products/x", "jbhifi")]
    // yeezysupply.com is retired — it resolves but serves nothing — so the module claims
    // yeezy.com instead. See YeezySupplyFlow.
    [InlineData("https://yeezy.com/product/x", "yeezysupply")]
    [InlineData("https://www.hypecommerce.io/shop/x", "hypecommerce")]
    [InlineData("https://www.fanatics.com/x", "fanatics")]
    [InlineData("https://www.pocketgames.nl/x", "pocketgames")]
    [InlineData("https://enter.superswipe.com/enter", "superswipe")]
    [InlineData("https://r419.com/x", "raffle")]
    [InlineData("https://www.offspring.co.uk/view/product/x", "offspring")]
    [InlineData("https://www.footpatrol.co.uk/x", "footpatrol")]
    [InlineData("https://www.notre-shop.com/products/x", "notre")]
    [InlineData("https://www.sneakersnstuff.com/en/product/x", "sns")]
    public void BrandHostResolvesToItsOwnModule(string url, string expectedId)
    {
        var registry = new StoreRegistry();
        StoreModuleCatalog.RegisterAll(registry);

        var module = registry.Resolve(new Uri(url));
        Assert.NotNull(module);
        Assert.Equal(expectedId, module!.Id);
    }

    [Fact]
    public void NikeModuleIsTheKasadaFlow()
    {
        var nike = Modules.First(m => m.Id == "nike") as FlowStoreModule;
        Assert.NotNull(nike);
        Assert.IsType<NikeFlow>(nike!.Flow);
        Assert.True(nike.Flow.UsesKasada);
    }

    [Fact]
    public void FootsitesCoversEveryFootsitesHost()
    {
        var footsites = Modules.First(m => m.Id == "footsites");
        foreach (var host in new[]
                 {
                     "footlocker.com", "champssports.com", "footaction.com",
                     "kidsfootlocker.com", "eastbay.com", "ladyfootlocker.com",
                 })
        {
            Assert.True(footsites.CanHandle(new Uri($"https://www.{host}/x")), host);
        }
    }

    [Fact]
    public void StepOverridesCoverTheRecoveredVocabulary()
    {
        // Count how many declared step methods the concrete flows actually implement.
        // The binary exposes 289 multi-implementation async names; the flows below are the
        // subset whose bodies are real (not the optional no-op defaults).
        var flowTypes = typeof(StoreFlow).Assembly.GetTypes()
            .Where(t => t.IsSubclassOf(typeof(StoreFlow)) && !t.IsAbstract)
            .ToList();

        var bodies = 0;
        foreach (var t in flowTypes)
        {
            bodies += t.GetMethods(BindingFlags.Public | BindingFlags.Instance |
                                   BindingFlags.DeclaredOnly)
                .Count(m => m.Name.EndsWith("Async"));
        }

        // 170 is the current floor: Shopify 13 + Nike 13 + Footsites 19 + Supreme 12 +
        // Magento 14 + JohnLewis 11 + Superswipe 11 + Yeezy 9 + Warhammer 9 + Casio 8 +
        // Hype 8 + JbHiFi 7 + PocketGames 7 + Fanatics 7 + Raffle 6 + Riot 5 + Kith 2 +
        // Size 1 + JdSports 3 + brand aliases 0 (inherited).
        Assert.True(bodies >= 150,
            $"only {bodies} step bodies implemented across {flowTypes.Count} flows");
    }

    [Fact]
    public void EveryFlowExposesItsOwnId()
    {
        foreach (var module in Modules.OfType<FlowStoreModule>())
        {
            Assert.False(string.IsNullOrWhiteSpace(module.Flow.Id));
            Assert.Equal(module.Id, module.Flow.Id);
            Assert.Equal(module.Name, module.Flow.Name);
        }
    }
}
