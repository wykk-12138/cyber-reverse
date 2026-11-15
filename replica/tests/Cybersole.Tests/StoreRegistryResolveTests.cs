using Cybersole.Http.Stores;
using Cybersole.Stores.Abstractions;
using Cybersole.Stores.Modules;
using Xunit;

namespace Cybersole.Tests;

public class StoreRegistryResolveTests
{
    private sealed class FakeModule : StoreModuleBase
    {
        private readonly string _id;
        private readonly string[] _domains;

        public FakeModule(string id, params string[] domains)
        {
            _id = id;
            _domains = domains;
        }

        public override string Id => _id;
        public override string Name => _id;
        public override IReadOnlyList<string> Domains => _domains;

        public override Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
            => Task.FromResult(MonitorResult.Fail("not used"));

        public override Task<CheckoutOutcome> CheckoutAsync(CheckoutContext ctx, CancellationToken ct)
            => Task.FromResult(new CheckoutOutcome { Success = false, Result = Cybersole.Core.Models.CheckoutResult.Error });
    }

    [Fact]
    public void Longest_Domain_Wins_Regardless_Of_Registration_Order()
    {
        var registry = new StoreRegistry();
        registry.Register(new FakeModule("generic", "shopify.com"));
        registry.Register(new FakeModule("specific", "my-shop.shopify.com"));

        var resolved = registry.Resolve(new Uri("https://my-shop.shopify.com/products/x"));
        Assert.Equal("specific", resolved!.Id);
    }

    [Fact]
    public void Generic_Still_Wins_For_Its_Own_Host()
    {
        var registry = new StoreRegistry();
        registry.Register(new FakeModule("generic", "shopify.com"));
        registry.Register(new FakeModule("specific", "my-shop.shopify.com"));

        Assert.Equal("generic", registry.Resolve(new Uri("https://other.shopify.com/products/x"))!.Id);
    }

    [Fact]
    public void No_Match_Returns_Null()
    {
        var registry = new StoreRegistry();
        registry.Register(new FakeModule("a", "a.com"));
        Assert.Null(registry.Resolve(new Uri("https://unrelated.example/x")));
    }

    [Fact]
    public void Duplicate_Ids_Are_Ignored_On_Register()
    {
        var registry = new StoreRegistry();
        registry.Register(new FakeModule("dup", "one.com"));
        registry.Register(new FakeModule("dup", "two.com"));

        Assert.Single(registry.Modules);
        Assert.Null(registry.Resolve(new Uri("https://two.com/x")));
    }

    [Fact]
    public void Real_Catalog_Resolves_Brands_Not_The_Generic_Module()
    {
        var registry = new StoreRegistry();
        StoreModuleCatalog.RegisterAll(registry);

        foreach (var (host, expected) in new[]
                 {
                     ("bodega.com", "bodega"),
                     ("cncpts.com", "concepts"),
                     ("nakedcopenhagen.com", "nakedcph"),
                     ("kith.com", "kith"),
                 })
        {
            var resolved = registry.Resolve(new Uri($"https://{host}/products/x"));
            Assert.Equal(expected, resolved!.Id);
        }
    }
}
