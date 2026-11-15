using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Utilities;
using Xunit;

namespace Cybersole.Tests;

/// <summary>R14: store groups page, plus the loopback probe that guards the e2e harness.</summary>
public class UtilitiesAndProbeTests
{
    [Fact]
    public void UtilitiesViewConstructs()
    {
        using var services = TestServices.Create();
        var view = new UtilitiesView(services);
        Assert.IsAssignableFrom<UserControl>(view);
    }

    [Fact]
    public void StoreGroupModalIsAWindow()
    {
        Assert.True(typeof(Window).IsAssignableFrom(typeof(StoreGroupModal)));
        Assert.NotNull(typeof(StoreGroupModal).GetConstructors().FirstOrDefault());
    }

    [Fact]
    public void StoreGroupCarriesItsStores()
    {
        var group = new StoreGroup { Name = "EU" };
        group.Stores.Add("shopify");
        group.Stores.Add("endclothing");

        Assert.Equal(2, group.Stores.Count);
        Assert.True(group.Enabled);
        Assert.Contains("EU", group.ToString());
    }

    [Fact]
    public void SettingsExposeStoreGroups()
    {
        using var services = TestServices.Create();
        var groups = services.Config.Settings.StoreGroups;
        Assert.NotNull(groups);

        groups.Add(new StoreGroup { Name = "Test" });
        Assert.Single(services.Config.Settings.StoreGroups);
        groups.Clear();
    }

    [Fact]
    public void EveryCatalogModuleHasAStableIdForGroupMembership()
    {
        using var services = TestServices.Create();
        var ids = services.Stores.Modules.Select(m => m.Id).ToList();
        Assert.Equal(ids.Count, ids.Distinct().Count());
        Assert.All(ids, id => Assert.False(string.IsNullOrWhiteSpace(id)));
    }
}
