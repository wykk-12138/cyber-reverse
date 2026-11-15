using Cybersole.Core.Models;
using Cybersole.Services;
using Xunit;

namespace Cybersole.Tests;

public class MonitorFilterPolicyTests
{
    [Fact]
    public void Shopify_Toggle_Gates_Shopify_And_Kith()
    {
        var filters = new MonitorFilters { Shopify = false };
        Assert.False(MonitorFilterPolicy.IsEnabled(filters, "shopify"));
        Assert.False(MonitorFilterPolicy.IsEnabled(filters, "kith"));
        Assert.True(MonitorFilterPolicy.IsEnabled(filters, "nike"));
    }

    [Fact]
    public void Nike_Toggle_Gates_Nike_Family()
    {
        var filters = new MonitorFilters { Nike = false };
        Assert.False(MonitorFilterPolicy.IsEnabled(filters, "nike"));
        Assert.False(MonitorFilterPolicy.IsEnabled(filters, "yeezysupply"));
        Assert.True(MonitorFilterPolicy.IsEnabled(filters, "shopify"));
    }

    [Fact]
    public void Unknown_Stores_Always_Enabled()
    {
        var filters = new MonitorFilters
        {
            Shopify = false, Nike = false, Footsites = false, Supreme = false,
            OffSpringOrOffice = false, PopMart = false,
        };
        Assert.True(MonitorFilterPolicy.IsEnabled(filters, "casio"));
        Assert.True(MonitorFilterPolicy.IsEnabled(filters, "my-custom-store"));
    }

    [Fact]
    public void Disabled_Lists_Only_Switched_Off_Stores()
    {
        var filters = new MonitorFilters { Supreme = false, PopMart = false };
        var disabled = MonitorFilterPolicy.Disabled(filters);
        Assert.Contains("supreme", disabled);
        Assert.Contains("popmart", disabled);
        Assert.DoesNotContain("shopify", disabled);
    }

    [Fact]
    public void Defaults_Enable_Everything()
    {
        var filters = new MonitorFilters();
        Assert.Empty(MonitorFilterPolicy.Disabled(filters));
        foreach (var id in new[] { "shopify", "nike", "footsites", "supreme", "offspring", "popmart" })
            Assert.True(MonitorFilterPolicy.IsEnabled(filters, id));
    }
}
