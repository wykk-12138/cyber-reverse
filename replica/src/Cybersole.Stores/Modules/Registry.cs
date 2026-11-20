using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Http.Stores;
using Cybersole.Stores.Abstractions;
using Cybersole.Stores.Flows;

namespace Cybersole.Stores.Modules;

/// <summary>Supreme module — weekly drop, session cookie + cart POST.</summary>
public sealed class SupremeModule : StoreModuleBase
{
    public override string Id => "supreme";
    public override string Name => "Supreme";
    public override IReadOnlyList<string> Domains => new[] { "supremenewyork.com" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "supreme-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var soldOut = res.Body.Contains("sold_out", StringComparison.OrdinalIgnoreCase);
            var price = MatchGroup(res.Body, @"\$([\d,]+)");
            var title = MatchGroup(res.Body, @"<h1[^>]*>([^<]+)</h1>");
            var color = MatchGroup(res.Body, @"""color_name""\s*:\s*""([^""]+)""");
            var sizes = System.Text.RegularExpressions.Regex
                .Matches(res.Body, @"""name""\s*:\s*""(S|M|L|XL|XXL)""")
                .Select(m => m.Groups[1].Value).Distinct().ToList();

            return new MonitorResult
            {
                Status = soldOut ? MonitorStatus.SoldOut : MonitorStatus.Available,
                ProductName = title,
                Price = price,
                VariantTitle = color,
                Sizes = sizes,
                Raw = res.Body,
            };
        }
        catch (Exception ex)
        {
            return MonitorResult.Fail(ex.Message);
        }
    }

    public override async Task<CheckoutOutcome> CheckoutAsync(CheckoutContext ctx, CancellationToken ct)
    {
        try
        {
            var origin = new Uri(ctx.Url);
            var addUrl = $"{origin.Scheme}://{origin.Host}/shop/{ctx.VariantId}/add";
            var res = await ctx.Http.GetAsync(addUrl,
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "supreme-add"), ct)
                .ConfigureAwait(false);

            if (!res.IsSuccess)
                return new CheckoutOutcome
                {
                    Success = false,
                    Error = $"add HTTP {res.StatusCode}",
                    Result = CheckoutResult.Error,
                };

            var checkout = await ctx.Http.GetAsync($"{origin.Scheme}://{origin.Host}/checkout",
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "supreme-checkout"), ct)
                .ConfigureAwait(false);

            var order = MatchGroup(checkout.Body, @"order\s*#?\s*([A-Z0-9]{6,})");
            return new CheckoutOutcome
            {
                Success = order is not null,
                OrderNumber = order,
                Result = order is not null ? CheckoutResult.Success : CheckoutResult.Declined,
            };
        }
        catch (Exception ex)
        {
            return new CheckoutOutcome { Success = false, Error = ex.Message, Result = CheckoutResult.Error };
        }
    }
}

/// <summary>Raffle / giveaway landing pages (r419.com, lndg.page style).</summary>
public sealed class RaffleModule : StoreModuleBase
{
    public override string Id => "raffle";
    public override string Name => "Raffle";
    public override IReadOnlyList<string> Domains => new[] { "r419.com", "lndg.page", "abovetheclouds.nodnod.digital" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "raffle-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var open = res.Body.Contains("\"open\":true", StringComparison.OrdinalIgnoreCase) ||
                       res.Body.Contains("enter", StringComparison.OrdinalIgnoreCase);

            return new MonitorResult
            {
                Status = open ? MonitorStatus.Available : MonitorStatus.Unavailable,
                ProductName = MatchGroup(res.Body, @"<title>([^<|]+)"),
                Price = "0.00",
                Sizes = new List<string> { "One Size" },
                Raw = res.Body,
            };
        }
        catch (Exception ex)
        {
            return MonitorResult.Fail(ex.Message);
        }
    }

    public override async Task<CheckoutOutcome> CheckoutAsync(CheckoutContext ctx, CancellationToken ct)
    {
        try
        {
            var origin = new Uri(ctx.Url);
            var payload = Newtonsoft.Json.JsonConvert.SerializeObject(new
            {
                email = ctx.ProfileData.Email,
                firstName = ctx.ProfileData.FirstName,
                lastName = ctx.ProfileData.LastName,
                phone = ctx.ProfileData.Phone,
                address = ctx.ProfileData.Address1,
                country = ctx.ProfileData.Country,
            });

            var res = await ctx.Http.PostJsonAsync($"{origin.Scheme}://{origin.Host}/entry", payload,
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "raffle-entry"), ct)
                .ConfigureAwait(false);

            var conf = MatchGroup(res.Body, @"""confirmation""\s*:\s*""?([\w\-]+)""?");
            return new CheckoutOutcome
            {
                Success = res.IsSuccess && conf is not null,
                OrderNumber = conf,
                Result = conf is not null ? CheckoutResult.Success : CheckoutResult.Declined,
            };
        }
        catch (Exception ex)
        {
            return new CheckoutOutcome { Success = false, Error = ex.Message, Result = CheckoutResult.Error };
        }
    }
}

/// <summary>Registry wiring for every built-in module.</summary>
public static class StoreModuleCatalog
{
    public static IReadOnlyList<IStoreModule> CreateAll() => new IStoreModule[]
    {
        new FlowStoreModule(new ShopifyFlow()),
        new FlowStoreModule(new KithFlow()),
        new FlowStoreModule(new NikeFlow()),
        new FlowStoreModule(new FootsitesFlow()),
        new FlowStoreModule(new SupremeFlow()),
        new FlowStoreModule(new EndClothingFlow()),
        new FlowStoreModule(new JohnLewisFlow()),
        new FlowStoreModule(new PopMartFlow()),
        new FlowStoreModule(new YeezySupplyFlow()),
        // R779: the app surface, which is a second surface rather than a replacement for offspring's web one.
        // Platform host and per-client actions are the image's; see PoqAppFlow.
        new FlowStoreModule(new PoqAppFlow()),
        // R773: offspring's WEB surface is Hybris — the home page carries "hybris" and answers JSON at
        // /view/resources/getUserInfo and /view/component/basket/minibasketAjax (PlatformAssignmentTests).
        // The image's platform.poq.io/clients/offspring/* strings are the app surface, a second surface, not a
        // replacement for this one. See BLOCKERS 199.
        new FlowStoreModule(new HybrisFlow("offspring", "Offspring",
            new[] { "offspring.co.uk", "offspring.com" })),
        new FlowStoreModule(new RaffleFlow()),
        new FlowStoreModule(new CasioFlow()),
        new FlowStoreModule(new WarhammerFlow()),
        new FlowStoreModule(new JbHiFiFlow()),
        new FlowStoreModule(new SuperswipeFlow()),
        new FlowStoreModule(new PocketGamesFlow()),
        new FlowStoreModule(new SnsFlow()),
        new FlowStoreModule(new SizeFlow()),
        // R918: two stores the image supports and the replica had nowhere. R917's core coverage table found them by
        // a host label appearing nowhere in src; the binary carries thirteen literals for Sportsshoes across three
        // hosts and six for Dicks Sporting Goods.
        new FlowStoreModule(new SportsshoesFlow()),
        new FlowStoreModule(new DicksSportingGoodsFlow()),
        // R1309: the image has a Saucony store the catalog never listed. R1308 found its class by grouping
        // the async state-machine names by metadata blob: four store ids, four display names, the
        // storefront in the alphabetised domain table, and eight steps of its own. The flow is real as far
        // as the home and product fetches go and refuses the rest by name — see SauconyFlow.
        new FlowStoreModule(new SauconyFlow()),
        new FlowStoreModule(new JdSportsFlow()),
        new FlowStoreModule(new FanaticsFlow()),
        new FlowStoreModule(new RiotGamesFlow()),
        new FlowStoreModule(new HypeCommerceFlow()),
        new FlowStoreModule(new FootpatrolFlow()),
        new FlowStoreModule(new NotreFlow()),

        // Shopify-powered streetwear retailers (same engine, brand-specific identity)
        new FlowStoreModule(new ShopifyFlow("bodega", "Bodega", new[] { "bodega.com" })),
        new FlowStoreModule(new ShopifyFlow("concepts", "Concepts", new[] { "cncpts.com" })),
        new FlowStoreModule(new ShopifyFlow("packershoes", "Packer", new[] { "packershoes.com" })),
        new FlowStoreModule(new ShopifyFlow("socialstatus", "Social Status", new[] { "socialstatuspgh.com" })),
        new FlowStoreModule(new ShopifyFlow("undefeated", "Undefeated", new[] { "undefeated.com" })),
        new FlowStoreModule(new ShopifyFlow("deadstock", "Deadstock", new[] { "deadstock.ca" })),
        new FlowStoreModule(new ShopifyFlow("livestock", "Livestock", new[] { "livestock.ca" })),
        new FlowStoreModule(new ShopifyFlow("capsule", "Capsule Toronto", new[] { "capsuletoronto.com" })),
        new FlowStoreModule(new ShopifyFlow("nrml", "NRML", new[] { "nrml.ca" })),
        new FlowStoreModule(new ShopifyFlow("offthehook", "Off The Hook", new[] { "offthehook.ca" })),
        new FlowStoreModule(new ShopifyFlow("overkill", "Overkill", new[] { "overkillshop.com" })),
        new FlowStoreModule(new ShopifyFlow("afew", "Afew", new[] { "afew-store.com" })),
        new FlowStoreModule(new ShopifyFlow("tresbien", "Tr猫s Bien", new[] { "tres-bien.com" })),
        new FlowStoreModule(new ShopifyFlow("civilist", "Civilist", new[] { "civilistberlin.com" })),
        new FlowStoreModule(new ShopifyFlow("vooberlin", "Voo Store", new[] { "vooberlin.com" })),
        // R91: the image names this store outright — the display string "ARROW & BEAST" and two
        // hosts, https://arrowandbeast.com/ and https://arrowbeast.myshopify.com/. It is a Shopify
        // storefront with its own domain in front, which is exactly the ShopifyFlow alias shape.
        // The replica had no such store before; the binary says it has one.
        new FlowStoreModule(new ShopifyFlow("arrowandbeast", "Arrow & Beast",
            new[] { "arrowandbeast.com", "arrowbeast.myshopify.com" })),

        // BSTN is not Shopify: it runs its own /api/beast/ prefix and checks out through Adyen.
        // /cart.js is 404. See BstnFlow for the evidence and what is still unknown.
        new FlowStoreModule(new BstnFlow()),

        // more Shopify-powered boutiques (US / EU / CA)
        new FlowStoreModule(new ShopifyFlow("extrabutter", "Extra Butter", new[] { "extrabutterny.com" })),
        new FlowStoreModule(new ShopifyFlow("premiumgoods", "Premium Goods", new[] { "premiumgoodsokc.com" })),
        new FlowStoreModule(new ShopifyFlow("saintalfred", "Saint Alfred", new[] { "saintalfred.com" })),
        new FlowStoreModule(new ShopifyFlow("lapstone", "Lapstone & Hammer", new[] { "lapstoneandhammer.com" })),
        new FlowStoreModule(new ShopifyFlow("courtside", "Courtside Sneakers", new[] { "courtsidesneakers.com" })),
        new FlowStoreModule(new ShopifyFlow("nakedcph", "Naked Copenhagen", new[] { "nakedcopenhagen.com" })),
        new FlowStoreModule(new ShopifyFlow("trophyroom", "Trophy Room", new[] { "trophyroomstore.com" })),
        new FlowStoreModule(new ShopifyFlow("a-ma-maniere", "A Ma Mani茅re", new[] { "a-ma-maniere.com" })),
        new FlowStoreModule(new ShopifyFlow("shophmvs", "HMVS", new[] { "shophmvs.com" })),
        new FlowStoreModule(new ShopifyFlow("sneakerpolitics", "Sneaker Politics", new[] { "sneakerpolitics.com" })),

        // Three Shopify storefronts the binary knows about that were still missing here.
        new FlowStoreModule(new ShopifyFlow("100thieves", "100 Thieves", new[] { "100thieves.com" })),
        new FlowStoreModule(new ShopifyFlow("10corsocomo", "10 Corso Como", new[] { "10corsocomo.com" })),
        new FlowStoreModule(new ShopifyFlow("titan22", "Titan 22", new[] { "titan22.com" })),
        // HBX is not Shopify: /products/{handle}.json answers 404 "No route found".
        // See HbxFlow for the evidence and for what is still unknown.
        new FlowStoreModule(new HbxFlow()),
        // Converse is Demandware, not Shopify. Verified from a live capture:
        //   /on/demandware.store/Sites-ConverseUS-Site/default/Cms-GetProductStrip
        //   /on/demandware.static/Sites-ConverseUS-Site/...
        // with Kasada (x-kpsdk-v=j-1.2.988) and Queue-it (x-queueit-ajaxpageurl) in front.
        // The site id is ConverseUS.
        new FlowStoreModule(new DemandwareFlow("converse", "Converse",
            new[] { "converse.com" }, "ConverseUS-Site")),

        // Platforms the running build lists under ACCOUNT GROUPS that the replica was missing.
        // Demandware (Salesforce Commerce Cloud) is one implementation, two entries: Funko runs
        // its own SFCC site id, everything else falls under the generic one.
        // This entry is a template, not a store: demandware.example is a placeholder domain
        // and the site id is a placeholder too. It is kept so the Demandware platform has a
        // discoverable example, and it is expected to report Dead in the reachability sweep.
        new FlowStoreModule(new DemandwareFlow("demandware", "Demandware (template)",
            new[] { "demandware.example" }, "Demandware-Site")),
        new FlowStoreModule(new FunkoFlow()),

        // Nike GS is its own Type in the running build, sitting next to Nike.
        new FlowStoreModule(new NikeGsFlow()),

        // Farfetch: the binary only carries the display name, so the flow follows the site's
        // public JSON API. Endpoint shape documented on FarfetchFlow.
        new FlowStoreModule(new FarfetchFlow()),

        // Goat: endpoints captured live (tools/NetworkCapture), not guessed. See GoatFlow.
        new FlowStoreModule(new GoatFlow()),

        // Scheels: Kasada (same build as Nike), captured live. See ScheelsFlow.
        new FlowStoreModule(new ScheelsFlow()),
    };

    public static void RegisterAll(StoreRegistry registry)
    {
        foreach (var module in CreateAll())
            registry.Register(module);
    }

    /// <summary>
    /// settings.customStores — each user-defined shop becomes a Shopify alias so it shows up in
    /// the store picker without touching code.
    /// </summary>
    public static void RegisterCustom(StoreRegistry registry, IEnumerable<Cybersole.Core.Models.CustomStore>? customStores)
    {
        if (customStores is null) return;

        foreach (var store in customStores)
        {
            var host = HostOf(store.Url);
            if (host.Length == 0) continue;

            // CustomStore.Id defaults to a random guid, so the host is the reliable identity
            var id = Slug(host);
            if (registry.Modules.Any(m => m.Id == id)) continue;

            var name = string.IsNullOrWhiteSpace(store.Name) ? host : store.Name;
            registry.Register(new FlowStoreModule(new ShopifyFlow(id, name, new[] { host })));
        }
    }

    private static string HostOf(string? url)
    {
        if (string.IsNullOrWhiteSpace(url)) return string.Empty;
        if (!url.Contains("://")) url = "https://" + url;
        return Uri.TryCreate(url, UriKind.Absolute, out var uri) ? uri.Host.ToLowerInvariant() : string.Empty;
    }

    private static string Slug(string host)
    {
        var slug = new string(host.Select(c => char.IsLetterOrDigit(c) ? c : '-').ToArray());
        return slug.Trim('-');
    }
}
