using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Http.Stores;
using Cybersole.Stores.Modules;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Every module must survive junk input without throwing — the engine treats a thrown
/// MonitorAsync as a crashed task, so one malformed URL would take the worker down.
/// </summary>
public class ModuleRobustnessTests
{
    public static IEnumerable<object[]> AllModules()
        => StoreModuleCatalog.CreateAll().Select(m => new object[] { m.Id });

    private static IStoreModule Module(string id)
        => StoreModuleCatalog.CreateAll().First(m => m.Id == id);

    [Trait("Speed", "Slow")]
    [Theory]
    [MemberData(nameof(AllModules))]
    public async Task Monitor_Survives_An_Empty_Url(string id)
    {
        var module = Module(id);
        var result = await module.MonitorAsync(new MonitorContext
        {
            Http = new NetClient(),
            Url = string.Empty,
            TimeoutSeconds = 2,
        }, CancellationToken.None);

        Assert.NotNull(result);           // must not throw; fail-fast status varies per module
    }

    [Trait("Speed", "Slow")]
    [Theory]
    [MemberData(nameof(AllModules))]
    public async Task Monitor_Survives_An_Unreachable_Host(string id)
    {
        var module = Module(id);
        var result = await module.MonitorAsync(new MonitorContext
        {
            Http = new NetClient(),
            Url = "https://no-such-host.invalid/products/x",   // parses fine, never resolves
            TimeoutSeconds = 2,
        }, CancellationToken.None);

        Assert.NotNull(result);
        Assert.False(string.IsNullOrEmpty(result.Error));

        // An unreachable host must never look like stock. Modules that carry an anti-bot
        // gate report that gate specifically (Nike fails closed on Kasada, Superswipe on
        // its captcha step); everything else reports a plain transport error.
        Assert.NotEqual(MonitorStatus.Available, result.Status);

        // nike-gs inherits NikeFlow, so it fails closed on the same Kasada gate — it was missing
        // from this list and had been failing here since the module was added.
        //
        // R821: poq-app belongs here for a different reason. Its GetHomeAsync ignores the context URL entirely and
        // POSTs to https://platform.poq.io/clients/<client>/account/guest-token, because the Poq surface is an app API
        // addressed per client rather than a web page. That host answers 403 to an unattributed request, and
        // PoqAppFlow.IsBlocked treats 403 as blocked, so the flow reports the gate it actually met. The test's premise
        // — that a URL which never resolves must not look like stock — holds for every flow that fetches the URL it is
        // given; this one never fetches it, so the expectation has to say what it means.
        if (id is "nike" or "nike-gs" or "superswipe" or "poq-app")
            Assert.True(result.Status is MonitorStatus.Blocked or MonitorStatus.Captcha,
                $"{id} should report its gate, got {result.Status}");
        else
            Assert.Equal(MonitorStatus.Error, result.Status);
    }

    [Trait("Speed", "Slow")]
    [Theory]
    [MemberData(nameof(AllModules))]
    public async Task Checkout_Survives_An_Empty_Variant(string id)
    {
        var module = Module(id);
        var outcome = await module.CheckoutAsync(new CheckoutContext
        {
            Http = new NetClient(),
            Url = string.Empty,
            VariantId = string.Empty,
            Size = "10",
            ProfileData = new Profile { Name = "p" },
            TimeoutSeconds = 2,
        }, CancellationToken.None);

        Assert.False(outcome.Success);
    }

    [Fact]
    public void Every_Module_Declares_A_Display_Name_And_Domains()
    {
        foreach (var module in StoreModuleCatalog.CreateAll())
        {
            Assert.False(string.IsNullOrWhiteSpace(module.Name), $"{module.Id} has no name");
            Assert.NotEmpty(module.Domains);
            Assert.All(module.Domains, d => Assert.False(string.IsNullOrWhiteSpace(d)));
        }
    }
}
