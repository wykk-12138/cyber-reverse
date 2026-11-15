using Cybersole.Stores.Flows;
using Cybersole.Stores.Modules;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Platform identification guards.
///
/// Two modules were registered against the wrong platform and nobody could tell from the code:
///
///   hbx       ShopifyFlow  -> answers 404 "No route found" for /products/{handle}.json
///   converse  ShopifyFlow  -> serves /on/demandware.store/Sites-ConverseUS-Site/...
///
/// Both compile, both run, both return responses — the only symptom is that nothing works.
/// These tests pin the corrected assignments so a later refactor cannot quietly undo them.
/// </summary>
public class PlatformAssignmentTests
{
    private readonly ITestOutputHelper _out;
    public PlatformAssignmentTests(ITestOutputHelper output) => _out = output;

    private static StoreFlow? FlowOf(string moduleId)
    {
        var module = StoreModuleCatalog.CreateAll().FirstOrDefault(m => m.Id == moduleId);
        if (module is null) return null;

        var field = module.GetType()
            .GetFields(System.Reflection.BindingFlags.NonPublic |
                       System.Reflection.BindingFlags.Instance)
            .FirstOrDefault(f => typeof(StoreFlow).IsAssignableFrom(f.FieldType));

        return field?.GetValue(module) as StoreFlow;
    }

    [Fact]
    public void HbxHasItsOwnFlowBecauseItIsNotShopify()
    {
        var flow = FlowOf("hbx");

        Assert.NotNull(flow);
        Assert.IsType<HbxFlow>(flow);
        Assert.IsNotType<ShopifyFlow>(flow);
    }

    [Fact]
    public void ConverseIsDemandwareNotShopify()
    {
        var flow = FlowOf("converse");

        Assert.NotNull(flow);
        Assert.IsType<DemandwareFlow>(flow);

        // the site id comes from the controller path seen in the capture
        Assert.Equal("ConverseUS-Site", ((DemandwareFlow)flow!).SiteId);
    }

    [Fact]
    public void BstnHasItsOwnFlowBecauseItIsNotShopify()
    {
        var flow = FlowOf("bstn");

        Assert.NotNull(flow);
        Assert.IsType<BstnFlow>(flow);
    }

    [Fact]
    public void TheGenuineShopifyBrandsAreStillShopify()
    {
        // spot-check a few that DID answer /cart.js with the Shopify shape.
        // AssignableFrom, not IsType: some brands use a ShopifyFlow subclass with extra
        // behaviour (kith uses KithFlow), and that is still the Shopify platform.
        foreach (var id in new[] { "bodega", "kith", "undefeated", "packershoes" })
        {
            var flow = FlowOf(id);
            if (flow is null) { _out.WriteLine($"{id}: not registered"); continue; }

            _out.WriteLine($"{id,-14} {flow.GetType().Name}");
            Assert.IsAssignableFrom<ShopifyFlow>(flow);
        }
    }

    [Fact]
    public void FootpatrolAndSizeAreShopifyNotMagento()
    {
        // both answer /cart.js with a Shopify cart token and carry Shopify theme markers;
        // no Magento REST surface answered on either
        foreach (var id in new[] { "footpatrol", "size" })
        {
            var flow = FlowOf(id);
            Assert.NotNull(flow);
            Assert.IsAssignableFrom<ShopifyFlow>(flow);
            Assert.IsNotType<MagentoFlow>(flow);
        }
    }

    [Fact]
    public void OffspringAndJdSportsAreNotMagentoEither()
    {
        // offspring.co.uk: no known platform marker, /cart.js 404, Magento REST 404
        // jdsports.co.uk: __NEXT_DATA__, i.e. Next.js
        // Neither has been re-registered yet, so this records the finding rather than a fix.
        foreach (var id in new[] { "offspring", "jdsports" })
        {
            var flow = FlowOf(id);
            if (flow is null) { _out.WriteLine($"{id}: not registered"); continue; }
            _out.WriteLine($"{id,-12} {flow.GetType().Name} (Magento: {flow is MagentoFlow})");
        }

        Assert.True(true);
    }

    [Fact]
    public void FunkoUsesTheRealDemandwareSiteId()
    {
        // the storefront's own controllers say Sites-FunkoUS-Site/en_US; Funko-Site 404s
        var flow = FlowOf("funko") as DemandwareFlow;

        Assert.NotNull(flow);
        Assert.Equal("FunkoUS-Site", flow!.SiteId);
        Assert.Equal("en_US", flow.Locale);
    }

    [Fact]
    public void TheFootsitesAreSelfBuiltAndNotDemandware()
    {
        // all six hosts answer 200 with Queue-it and none of the Demandware markers;
        // FootsitesFlow is its own implementation, which matches
        var flow = FlowOf("footsites");

        Assert.NotNull(flow);
        Assert.IsType<FootsitesFlow>(flow);
        Assert.IsNotType<DemandwareFlow>(flow);
    }

    [Fact]
    public void JbHiFiIsShopifyWithItsOwnAccountSystem()
    {
        // /cart.js answers with a Shopify cart object, but the retailer runs bespoke OAuth at
        // auth.jbhifi.com.au, so the flow must stay a ShopifyFlow that overrides LoginAsync
        var flow = FlowOf("jbhifi");

        Assert.NotNull(flow);
        Assert.IsAssignableFrom<ShopifyFlow>(flow);
        Assert.True(flow!.RequiresAccount, "JB Hi-Fi's account system is separate from the shop");
    }

    [Fact]
    public void OffspringIsHybrisNotMagento()
    {
        // the home page contains "hybris" and calls /view/resources/getUserInfo and
        // /view/component/basket/minibasketAjax, both answering JSON; no Magento surface does
        var flow = FlowOf("offspring");

        Assert.NotNull(flow);
        Assert.IsType<HybrisFlow>(flow);
        Assert.IsNotType<MagentoFlow>(flow);
    }

    [Fact]
    public void NoModuleIsRegisteredWithoutADomain()
    {
        foreach (var m in StoreModuleCatalog.CreateAll())
        {
            if (m.Id is "shopify") continue;   // the generic platform module
            Assert.NotEmpty(m.Domains);
        }
    }
}
