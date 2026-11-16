using System.Reflection;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Modules;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R25: an honest per-module coverage matrix, computed by reflection rather than by grepping
/// source. R24 showed the static audit was blind to `=> NotSupported(...)`, and a text scan
/// also cannot see through inheritance — a flow that extends ShopifyFlow inherits its
/// FindProduct, which counts as implemented.
/// </summary>
public class ModuleCoverageTests
{
    private readonly ITestOutputHelper _out;
    public ModuleCoverageTests(ITestOutputHelper output) => _out = output;

    private static readonly string[] Required =
    {
        "FindProductAsync",
        "FindVariantAsync",
        "AddToCartAsync",
        "GetCheckoutAsync",
        "SubmitShippingAsync",
        "SubmitPaymentAsync",
        "SubmitOrderAsync",
    };

    /// <summary>
    /// Modules whose flow is not the e-commerce shape at all. Measuring them against the seven
    /// commerce steps says nothing useful, so each is scored on its own steps instead:
    ///
    ///   raffle       scrape form -> solve Turnstile -> enter
    ///   pocketgames  release feed -> wait for release -> enter raffle
    ///   riotgames    register -> confirm -> login -> enter raffle
    ///
    /// They scored 0-29% on the commerce yardstick purely because the yardstick does not fit.
    /// </summary>
    private static readonly Dictionary<string, string[]> NonCommerce = new()
    {
        ["raffle"] = new[]
        {
            "ScrapeRaffleFormAsync",
            "GetRaffleDataAsync",
            "EnterRaffleAsync",
            "SolveCaptchaAsync",
        },
        ["pocketgames"] = new[]
        {
            "GetReleaseFeedAsync",
            "WaitForReleaseAsync",
            "FindProductAsync",
            "FindVariantAsync",
            "ScrapeVariantAvailabilityAsync",
            "EnterRaffleAsync",
        },
        ["riotgames"] = new[]
        {
            "GetHomeAsync",
            "FindProductAsync",
            "FindVariantAsync",
            "RegisterAsync",
            "CompleteRegistrationAsync",
            "LoginAsync",
            "EnterRaffleAsync",
        },
    };

    /// <summary>
    /// Modules where the seven-step score must not be read as a gap, each with the evidence for why. R770.
    ///
    /// <para>
    /// The matrix counts every module against the same seven steps, so <c>yeezysupply</c> scoring 71% read as
    /// unfinished work, and R765 recorded twelve modules as "cannot place an order" on that basis. Probing the image
    /// per store shows that for some of them the original has no checkout to replicate either:
    /// </para>
    ///
    /// <code>
    /// fanatics    9 strings, 7 URLs, all id.fanatics.com/api-internal/{oauth2/*, login/factor-request}
    ///             0 checkout words, 0 platform names
    /// yeezysupply 1 string in the whole pool: https://www.yeezysupply.com
    /// </code>
    ///
    /// <para>
    /// So the two steps the matrix calls missing are steps the image does not have, which makes the replica faithful
    /// rather than incomplete. <b>Every entry must carry its evidence</b> --
    /// <see cref="EveryExemptionCarriesItsEvidence"/> enforces that, because an exemption without a reason is
    /// exactly the kind of thing that quietly grows.
    /// </para>
    ///
    /// <para>
    /// Deliberately absent: <c>warhammer</c>, which exposes api.prod.warhammer.com/graphql and may well carry a
    /// checkout mutation, so it is unresolved rather than excluded; <c>goat</c>, whose surface is drops and captcha
    /// submission and whose yardstick has not been decided; and <c>bstn</c>, which is the opposite case — a module
    /// the replica has and the image does not, filed for a separate decision.
    /// </para>
    /// </summary>
    private static readonly Dictionary<string, string> YardstickDoesNotApply = new()
    {
        ["fanatics"] =
            "R769: the image carries 9 strings for fanatics, 7 of them URLs, all id.fanatics.com/api-internal/"
            + "{oauth2/auth, oauth2/login, oauth2/login-factor, login/factor-request}; zero checkout words",
        ["yeezysupply"] =
            "R769: the image carries exactly one string for this store, the bare domain https://www.yeezysupply.com",
    };

    [Fact]
    public void EveryExemptionCarriesItsEvidence()
    {
        // An exemption is a claim that a number should not be read as a gap. A claim needs a reason, and a reason
        // needs to say where it came from -- otherwise this dictionary becomes the place gaps go to be forgotten.
        foreach (var (id, why) in YardstickDoesNotApply)
        {
            Assert.False(string.IsNullOrWhiteSpace(why), $"{id} is exempted without a reason");
            Assert.Matches(@"R\d{3}:", why);          // names the round the evidence came from
            Assert.True(why.Length > 60, $"{id}'s reason is too short to be evidence: {why}");
            Assert.NotNull(StoreModuleCatalog.CreateAll().FirstOrDefault(m => m.Id == id));
        }
    }

    /// <summary>True when the method is implemented somewhere below StoreFlow.</summary>
    private static bool IsImplemented(Type flow, string method)
    {
        var info = flow.GetMethod(method, BindingFlags.Public | BindingFlags.Instance);
        return info is not null && info.DeclaringType != typeof(StoreFlow);
    }

    private static Type? FlowTypeOf(string moduleId)
    {
        var module = StoreModuleCatalog.CreateAll().FirstOrDefault(m => m.Id == moduleId);
        if (module is null) return null;

        var field = module.GetType()
            .GetFields(BindingFlags.NonPublic | BindingFlags.Instance)
            .FirstOrDefault(f => typeof(StoreFlow).IsAssignableFrom(f.FieldType));

        if (field?.GetValue(module) is StoreFlow instance) return instance.GetType();

        var prop = module.GetType()
            .GetProperties(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance)
            .FirstOrDefault(p => typeof(StoreFlow).IsAssignableFrom(p.PropertyType));

        if (prop?.GetValue(module) is StoreFlow fromProp) return fromProp.GetType();

        return null;
    }

    [Fact]
    public void EveryModuleReportsItsCoverage()
    {
        var modules = StoreModuleCatalog.CreateAll().Select(m => m.Id).OrderBy(x => x).ToList();

        _out.WriteLine($"{"module",-22} " + string.Join(" ", Required.Select(r => r.Replace("Async", "")[..6])));
        _out.WriteLine(new string('-', 90));

        var totals = Required.ToDictionary(r => r, _ => 0);
        var resolved = 0;
        var full = 0;
        var exempted = 0;
        var unresolved = new List<string>();

        foreach (var id in modules)
        {
            var type = FlowTypeOf(id);
            if (type is null)
            {
                unresolved.Add(id);
                continue;
            }

            resolved++;

            var cells = new List<string>();
            var done = 0;

            foreach (var step in Required)
            {
                var ok = IsImplemented(type, step);
                cells.Add(ok ? "+" : "-");
                if (ok) { done++; totals[step]++; }
            }

            // A raffle flow measured against the seven commerce steps scores low by construction:
            // it has no cart and no checkout to implement. Printing "29%" next to "100%" for the
            // same module — which the non-commerce table below does — invites the reader to treat
            // the low number as a gap. Mark it instead.
            //
            // R770: same reasoning one step further out. YardstickDoesNotApply covers modules where the image has no
            // checkout to replicate, so their percentage is not a gap either. Those rows are counted separately
            // rather than as "not fully covered", which is what R765 mistook them for.
            var exempt = YardstickDoesNotApply.ContainsKey(id);
            var note = NonCommerce.ContainsKey(id)
                ? "   (non-commerce — see below)"
                : (exempt ? "   (not in the image — see the exemption table)" : "");

            if (exempt) exempted++;
            else if (done == Required.Length) full++;

            _out.WriteLine($"{id,-22} " + string.Join("      ", cells) +
                           $"   {100.0 * done / Required.Length:0}%{note}");
        }

        _out.WriteLine("");
        _out.WriteLine($"resolved {resolved}/{modules.Count} flows; fully covered {full}; exempt {exempted}");

        // report non-commerce modules on their own yardstick so their 0/7 does not read as a gap
        _out.WriteLine(string.Empty);
        _out.WriteLine("non-commerce flows (measured against their own steps):");

        foreach (var (id, steps) in NonCommerce)
        {
            var type = FlowTypeOf(id);
            if (type is null) { _out.WriteLine($"  {id,-22}  flow type not resolvable"); continue; }

            var done = steps.Count(s => IsImplemented(type, s));
            _out.WriteLine($"  {id,-22}  {done}/{steps.Length}  " +
                           string.Join(" ", steps.Select(s => IsImplemented(type, s) ? "+" : "-")));
        }
        foreach (var step in Required)
            _out.WriteLine($"  {step.Replace("Async", ""),-18} {totals[step],3} / {resolved}");

        if (unresolved.Count > 0)
            _out.WriteLine("unresolved: " + string.Join(", ", unresolved));

        // Every module must expose a StoreFlow instance we can inspect.
        Assert.True(resolved > 40, $"only resolved {resolved} of {modules.Count} modules");

        // A flow with no product lookup cannot monitor anything.
        Assert.True(totals["FindProductAsync"] >= resolved - 3,
            $"only {totals["FindProductAsync"]}/{resolved} flows implement FindProduct");

        // Add-to-cart is the one step every purchasable store needs.
        Assert.True(totals["AddToCartAsync"] >= resolved * 0.6,
            $"only {totals["AddToCartAsync"]}/{resolved} flows implement AddToCart");
    }

    [Fact]
    public void EveryGapIsNamed()
    {
        var modules = StoreModuleCatalog.CreateAll().Select(m => m.Id).OrderBy(x => x).ToList();

        foreach (var step in Required)
        {
            var missing = new List<string>();
            foreach (var id in modules)
            {
                var type = FlowTypeOf(id);
                if (type is null) continue;
                if (!IsImplemented(type, step)) missing.Add(id);
            }

            _out.WriteLine($"{step.Replace("Async", ""),-16} missing {missing.Count,2}: " +
                           string.Join(", ", missing));
        }
    }

    [Fact]
    public void TheBaseClassRefusesTheSevenRequiredSteps()
    {
        foreach (var step in Required)
        {
            var info = typeof(StoreFlow).GetMethod(step, BindingFlags.Public | BindingFlags.Instance);
            Assert.NotNull(info);
            Assert.Equal(typeof(StoreFlow), info!.DeclaringType);
        }
    }

    [Fact]
    public void InheritanceCountsAsImplementation()
    {
        // ShopifyFlow implements FindProduct; the brand flows extend it and inherit that.
        foreach (var id in new[] { "shopify", "a-ma-maniere", "bodega", "concepts" })
        {
            var type = FlowTypeOf(id);
            if (type is null) continue;

            Assert.True(IsImplemented(type, "FindProductAsync"),
                $"{id} ({type.Name}) does not resolve FindProduct");
        }
    }
}
