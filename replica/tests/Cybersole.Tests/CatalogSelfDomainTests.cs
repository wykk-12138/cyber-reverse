using Cybersole.Stores.Modules;
using Xunit;

namespace Cybersole.Tests;

public class CatalogSelfDomainTests
{
    [Fact]
    public void Every_Module_Accepts_Its_Own_Domains()
    {
        var problems = CatalogValidator.Validate(StoreModuleCatalog.CreateAll())
            .Where(p => p.Contains("its own domain") || p.Contains("unparsable domain"))
            .ToList();

        Assert.True(problems.Count == 0, string.Join("\n", problems));
    }

    [Fact]
    public void Resolve_Finds_Every_Built_In_Module_By_Its_First_Domain()
    {
        var registry = new Cybersole.Http.Stores.StoreRegistry();
        StoreModuleCatalog.RegisterAll(registry);

        var misses = new List<string>();
        foreach (var module in registry.Modules)
        {
            var domain = module.Domains.FirstOrDefault();
            if (string.IsNullOrWhiteSpace(domain)) continue;

            var resolved = registry.Resolve(new Uri("https://" + domain.TrimStart('.') + "/products/x"));
            if (resolved is null)
                misses.Add($"{module.Id} ({domain}) resolved to nothing");
        }

        Assert.True(misses.Count == 0, string.Join("\n", misses));
    }

    [Fact]
    public void Resolve_Prefers_The_Specific_Brand_Over_The_Generic_Shopify_Module()
    {
        var registry = new Cybersole.Http.Stores.StoreRegistry();
        StoreModuleCatalog.RegisterAll(registry);

        var resolved = registry.Resolve(new Uri("https://bodega.com/products/x"));
        Assert.NotNull(resolved);
        Assert.Equal("bodega", resolved!.Id);
    }
}
