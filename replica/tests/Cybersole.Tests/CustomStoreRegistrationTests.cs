using Cybersole.Core.Models;
using Cybersole.Http.Stores;
using Cybersole.Stores.Modules;
using Xunit;

namespace Cybersole.Tests;

public class CustomStoreRegistrationTests
{
    [Fact]
    public void Custom_Store_Becomes_A_Shopify_Alias()
    {
        var registry = new StoreRegistry();
        StoreModuleCatalog.RegisterCustom(registry, new[]
        {
            new CustomStore { Id = "mystore", Name = "My Store", Url = "https://mystore.example.com" },
        });

        var module = Assert.Single(registry.Modules);
        Assert.Equal("mystore-example-com", module.Id);
        Assert.Equal("My Store", module.Name);
        Assert.Equal("mystore.example.com", module.Domains[0]);
    }

    [Fact]
    public void Missing_Scheme_Is_Tolerated()
    {
        var registry = new StoreRegistry();
        StoreModuleCatalog.RegisterCustom(registry, new[]
        {
            new CustomStore { Name = "No Scheme", Url = "noscheme.example.com" },
        });

        Assert.Equal("noscheme.example.com", Assert.Single(registry.Modules).Domains[0]);
    }

    [Fact]
    public void Id_Derived_From_Host_When_Omitted()
    {
        var registry = new StoreRegistry();
        StoreModuleCatalog.RegisterCustom(registry, new[]
        {
            new CustomStore { Name = "Auto", Url = "https://auto-shop.example.com" },
        });

        Assert.Equal("auto-shop-example-com", Assert.Single(registry.Modules).Id);
    }

    [Fact]
    public void Duplicate_Ids_Are_Not_Registered_Twice()
    {
        var registry = new StoreRegistry();
        registry.Register(new ShopifyModule("clash-example-com", "Shopify", new[] { "myshopify.com" }));

        StoreModuleCatalog.RegisterCustom(registry, new[]
        {
            new CustomStore { Id = "shopify", Name = "Clash", Url = "https://clash.example.com" },
        });

        Assert.Single(registry.Modules);   // the built-in wins
    }

    [Fact]
    public void Blank_Url_Is_Skipped()
    {
        var registry = new StoreRegistry();
        StoreModuleCatalog.RegisterCustom(registry, new[]
        {
            new CustomStore { Name = "Broken", Url = "" },
            new CustomStore { Name = "Fine", Url = "https://fine.example.com" },
        });

        Assert.Equal("Fine", Assert.Single(registry.Modules).Name);
    }

    [Fact]
    public void Null_List_Is_A_NoOp()
    {
        var registry = new StoreRegistry();
        StoreModuleCatalog.RegisterCustom(registry, null);
        Assert.Empty(registry.Modules);
    }

    [Fact]
    public void Custom_Store_Can_Handle_Its_Own_Host()
    {
        var registry = new StoreRegistry();
        StoreModuleCatalog.RegisterCustom(registry, new[]
        {
            new CustomStore { Name = "Mine", Url = "https://mine.example.com" },
        });

        var resolved = registry.Resolve(new Uri("https://mine.example.com/products/x"));
        Assert.NotNull(resolved);
        Assert.Equal("Mine", resolved!.Name);
    }
}
