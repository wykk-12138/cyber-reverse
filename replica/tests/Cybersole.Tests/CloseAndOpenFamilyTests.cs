using System.Linq;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Modals;
using Cybersole.Ui.Views.Tasks;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R355: the "Close" and "OpenUrl" family the binding table names on dialogs, as members instead of click lambdas.
///
/// <para>
/// Close is bound on TaskCreatorView, TaskDetailsView, TaskGroupView, ProxyCreatorView, ProfileGroupView and others; the
/// panel behind the avatar binds OpenUrl. Each returns false when there is no window or no browser, which is what a
/// host-less construction — and a locked-down machine — actually sees.
/// </para>
/// </summary>
public sealed class CloseAndOpenFamilyTests
{
    private readonly ITestOutputHelper _out;
    public CloseAndOpenFamilyTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheDialogsCarryClose()
    {
        foreach (var type in new[] { typeof(TaskCreatorView), typeof(TaskDetailsView), typeof(TaskGroupView) })
        {
            var has = type.GetMembers().Any(m => m.Name == "Close");
            _out.WriteLine(type.Name + ": " + has);
            Assert.True(has, type.Name + " has no Close()");
        }
    }

    [Fact]
    public void WithoutAHostCloseReportsFalse()
    {
        using var services = TestServices.Create();
        var details = new TaskDetailsView(services, new BotTask { Name = "t" });

        Assert.False(details.CloseCore());
    }

    [Fact]
    public void OpeningSomethingUnopenableReportsFalse()
    {
        Assert.False(UserView.OpenUrl("not-a-url"));
    }

    [Fact]
    public void TheProxyAndProfileDialogsCarryCloseToo()
    {
        var names = new[]
        {
            typeof(Cybersole.Ui.Views.Proxies.ProxyGroupView),
            typeof(Cybersole.Ui.Views.Proxies.ProxyCreatorView),
            typeof(Cybersole.Ui.Views.Profiles.ProfileGroupView),
        };

        foreach (var type in names)
        {
            var has = type.GetMembers().Any(m => m.Name == "Close");
            _out.WriteLine(type.Name + ": " + has);
            Assert.True(has, type.Name + " has no Close()");
        }
    }

    [Fact]
    public void DeletingAProxyGroupTakesTheListItCameFrom()
    {
        var group = new ProxyGroup { Name = "g" };
        var all = new List<ProxyGroup> { group };
        var view = new Cybersole.Ui.Views.Proxies.ProxyGroupView(group);

        Assert.True(view.Delete(all));
        Assert.False(view.Delete(all));
    }

    [Fact]
    public void TheAccountGridReportsItsGroupAndWhetherItCanEdit()
    {
        // R418: AccountGrid.AccountGroup / Edit — both read-only in the image (Getter,Property).
        var accounts = new List<Cybersole.Core.Models.Account>
        {
            new() { Email = "a@example.com", GroupId = "grp-1" },
        };
        var grid = new Cybersole.Ui.Views.Accounts.AccountGrid(accounts);

        _out.WriteLine($"{grid.AccountGroup} / {grid.Edit}");
        Assert.Equal("grp-1", grid.AccountGroup);
        Assert.True(grid.Edit);

        var empty = new Cybersole.Ui.Views.Accounts.AccountGrid(new List<Cybersole.Core.Models.Account>());
        Assert.Equal(string.Empty, empty.AccountGroup);
        Assert.False(empty.Edit);
    }

    [Fact]
    public void TheProfileCreatorReportsItsStepAndCount()
    {
        // R419: ProfileCreatorView binds Navigate / Count / Profile / Names / PaymentView / AdvancedView.
        using var services = TestServices.Create();
        var creator = new Cybersole.Ui.Views.Profiles.ProfileCreatorView(services);

        _out.WriteLine($"{creator.Navigate} / {creator.Count} / {creator.Names.Count} / {creator.PaymentView}");
        Assert.Equal("Details", creator.Navigate);
        Assert.Equal(1, creator.Count);
        Assert.Single(creator.Names);
        Assert.True(creator.PaymentView);
        Assert.True(creator.AdvancedView);
        Assert.NotNull(creator.Profile);

        creator.IsBulk = true;
        Assert.Equal(1, creator.Count);   // bulk with one name is still one profile
        creator.Navigate = "Payment";
        Assert.Equal("Payment", creator.Navigate);
    }
}
