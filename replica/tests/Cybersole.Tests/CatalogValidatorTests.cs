using Cybersole.Stores.Modules;
using Xunit;

namespace Cybersole.Tests;

public class CatalogValidatorTests
{
    [Fact]
    public void BuiltIn_Catalog_Is_Clean()
    {
        var catalog = StoreModuleCatalog.CreateAll();
        var problems = CatalogValidator.Validate(catalog);

        Assert.Empty(problems);
    }

    [Fact]
    public void Detects_Duplicate_Ids()
    {
        var catalog = StoreModuleCatalog.CreateAll()
            .Concat(new[] { new ShopifyModule("bodega", "Bodega Duplicate", new[] { "bodega2.com" }) })
            .ToList();

        var problems = CatalogValidator.Validate(catalog);
        Assert.Contains(problems, p => p.Contains("duplicate module id 'bodega'"));
    }

    [Fact]
    public void Detects_Missing_Domains()
    {
        var catalog = new List<Cybersole.Http.Stores.IStoreModule>
        {
            new ShopifyModule("empty", "Empty", Array.Empty<string>()),
        };

        var problems = CatalogValidator.Validate(catalog);
        Assert.Contains(problems, p => p.Contains("declares no domains"));
    }

    [Fact]
    public void Shopify_Aliases_Each_Have_Own_Id()
    {
        var catalog = StoreModuleCatalog.CreateAll();
        var shopifyFamily = catalog.Where(m => m.Id is "shopify" or "bodega" or "concepts"
            or "packershoes" or "socialstatus" or "undefeated" or "deadstock" or "livestock"
            or "capsule" or "nrml" or "offthehook" or "overkill" or "afew" or "tresbien"
            or "civilist" or "vooberlin" or "bstn" or "extrabutter" or "premiumgoods"
            or "saintalfred" or "lapstone" or "courtside" or "nakedcph"
            or "trophyroom" or "a-ma-maniere" or "shophmvs" or "sneakerpolitics").ToList();

        Assert.Equal(27, shopifyFamily.Count);
        Assert.Equal(shopifyFamily.Count, shopifyFamily.Select(m => m.Id).Distinct().Count());
    }
}
