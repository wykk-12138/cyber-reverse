using System.Text.RegularExpressions;
using Cybersole.Core.Models;
using Cybersole.Http;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// SAP Commerce Cloud (Hybris).
///
/// Why this platform exists: Offspring was registered as MagentoFlow, but nothing Magento ever
/// answered — /rest/V1/store/storeConfigs, /customer/section/load/ and /cart.js are all 404 on
/// both offspring.co.uk and offspring.com. A capture of the home page showed what it does call:
///
///   GET  /akam/13/710368ee                          Akamai Bot Manager
///   GET  /view/resources/getUserInfo                -> 200, 418 B,  application/json
///   GET  /view/component/basket/minibasketAjax      -> 200, 1164 B, application/json
///
/// and the page HTML literally contains "hybris". The /view/... controller shape is SAP
/// Commerce's, not Magento's, not Shopify's and not Demandware's. That is grade-A evidence:
/// the site names its own backend and two of its controllers answer with real payloads.
///
/// Verified:  the two /view/ controllers above.
/// Inferred:  the product, cart-add and checkout paths — Hybris's documented /p/ and cart
///            controller shape, marked at each site below.
/// </summary>
public sealed class HybrisFlow : StoreFlow
{
    private readonly string _id;
    private readonly string _name;
    private readonly IReadOnlyList<string> _domains;
    private readonly string _siteUid;

    public HybrisFlow(string id, string name, IReadOnlyList<string> domains,
        string siteUid = "main")
    {
        _id = id;
        _name = name;
        _domains = domains;
        _siteUid = siteUid;
    }

    public override string Id => _id;
    public override string Name => _name;
    public override IReadOnlyList<string> Domains => _domains;

    /// <summary>Hybris guards its controllers with Akamai, so a plain 403 is expected on cold starts.</summary>
    private static bool IsBlocked(NetResponse? res) => res is { StatusCode: 403 or 429 };

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/", _id + "-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail($"{_id} home unreachable", retryable: true);
        if (IsBlocked(res)) return StepOutcome.Fail($"{_id} home blocked (akamai)", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"{_id} home HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["home"] = res.Body;

        // verified endpoint: confirms the session cookie is usable before any cart work
        var info = await GetAsync(c, Origin(c.Url) + "/view/resources/getUserInfo",  // inferred: no image evidence (R294)
            _id + "-userinfo", ct).ConfigureAwait(false);

        if (info is { IsSuccess: true }) c.Session.Vars["userInfo"] = info.Body;

        return StepOutcome.Success();
    }

    /// <summary>Verified: GET /view/component/basket/minibasketAjax answers JSON.</summary>
    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/view/component/basket/minibasketAjax",
            _id + "-minibasket", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail($"{_id} basket unreachable", retryable: true);
        if (IsBlocked(res)) return StepOutcome.Fail($"{_id} basket blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"{_id} basket HTTP {res.StatusCode}",
            retryable: true);

        c.Session.Vars["cart"] = res.Body;

        var count = Regex.Match(res.Body, @"""?(?:totalUnitCount|unitCount)""?\s*:\s*(\d+)");
        if (count.Success) c.Session.Vars["cartCount"] = count.Groups[1].Value;

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, _id + "-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail($"{_id} product unreachable", retryable: true);
        if (IsBlocked(res)) return StepOutcome.Fail($"{_id} product blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"{_id} product HTTP {res.StatusCode}",
            retryable: true);

        c.Session.Vars["raw"] = res.Body;

        // Hybris pages put the product in a data attribute and the name in an h1
        var name = Regex.Match(res.Body, @"<h1[^>]*>([^<]{2,80})</h1>").Groups[1].Value.Trim();
        if (string.IsNullOrEmpty(name))
            name = Regex.Match(res.Body, @"<title>([^<|]+)").Groups[1].Value.Trim();
        if (!string.IsNullOrEmpty(name)) c.Session.Vars["product"] = name;

        // price: Hybris renders a formatted amount next to a currency; take the first one
        var price = Regex.Match(res.Body, @"[""']?(?:value|price)[""']?\s*:\s*([\d]+\.?\d*)");
        if (!price.Success)
            price = Regex.Match(res.Body, @"(?:£|\$|€)\s?([\d,]+\.\d{2})");

        if (price.Success && decimal.TryParse(price.Groups[1].Value.Replace(",", ""),
                System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var amount)
            && amount > 0)
            c.Session.Vars["price"] = amount.ToString("0.00");

        return StepOutcome.Success();
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;

        // Hybris calls the sku "code" and the variant a "variantOption"; both live in the page
        var code = Regex.Match(body, @"""code""\s*:\s*""([A-Za-z0-9\-_]{4,})""").Groups[1].Value;
        if (string.IsNullOrEmpty(code))
            code = Regex.Match(c.Url, @"[/-]([A-Za-z0-9]{6,})(?:[/?#]|$)").Groups[1].Value;

        if (string.IsNullOrEmpty(code))
            return Task.FromResult(StepOutcome.Fail($"{_id}: no product code in the page"));

        c.Session.VariantId = code;

        // sizes are rendered as option buttons labelled with the size text
        var sizes = Regex.Matches(body, @"""size""\s*:\s*""([^""]{1,10})""")
            .Select(m => m.Groups[1].Value).Distinct().ToList();

        if (sizes.Count > 0) c.Session.Vars["sizes"] = string.Join(',', sizes);

        return Task.FromResult(StepOutcome.Success());
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c,
        CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;

        var oos = body.Contains("\"stockLevelStatus\":\"outOfStock\"", StringComparison.OrdinalIgnoreCase)
                  || body.Contains("\"purchasable\":false", StringComparison.OrdinalIgnoreCase)
                  || body.Contains("out of stock", StringComparison.OrdinalIgnoreCase);

        c.Session.Vars["available"] = oos ? "false" : "true";
        return Task.FromResult(StepOutcome.Success());
    }

    /// <summary>
    /// Add to basket, using the controller path the original binary names.
    ///
    /// Four candidates had been tried here and by <c>HybrisCartPathTests</c>, with the verified
    /// <c>minibasketAjax</c> as a control:
    ///
    ///   /cart/add                   404, 162 KB HTML
    ///   /view/cart/add              404, 162 KB HTML
    ///   /view/component/cart/add    404, 162 KB HTML
    ///   /view/component/basket/add  404, 162 KB HTML
    ///   control: minibasketAjax     200, 1.1 KB JSON     &lt;- host and cookie are fine
    ///
    /// Every candidate assumed the add controller sat beside the minibasket one. It does not.
    /// The string table of <c>Cybersole.exe</c> contains three Hybris controller paths:
    ///
    ///   view/basket/add                       &lt;- one segment shallower
    ///   view/basket/addPromotionalCode
    ///   view/component/basket/minibasketAjax  &lt;- the control, one segment deeper
    ///
    /// The add controller is at <c>/view/basket/</c>, not <c>/view/component/basket/</c>; the
    /// minibasket lives under <c>/view/component/</c>. That asymmetry is why prefixing every
    /// guess with <c>/view/component/</c> never reached the real route.
    ///
    /// This asks the real path once. If it answers 404 too, the failure now says which URL was
    /// tried rather than listing four that were not.
    ///
    /// <para>
    /// Not verified live. When this was changed, offspring answered 403 to <em>every</em> path
    /// including the minibasket control that used to return 200 — so the host is currently
    /// refusing this client outright and no path can be distinguished. The change rests on the
    /// binary's own string table, which is a stronger source than a probe against a host that has
    /// stopped talking; but it is not a confirmed 200, and should not be recorded as one.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        var variant = c.Session.VariantId ?? string.Empty;
        if (string.IsNullOrEmpty(variant))
            return StepOutcome.Fail($"{_id}: no variant id to add");

        var form = new Dictionary<string, string>
        {
            ["productCodePost"] = variant,
            ["qty"] = c.Session.Vars.TryGetValue("qty", out var qty) && qty.Length > 0 ? qty : "1",
        };

        var res = await PostFormAsync(c, Origin(c.Url) + "/view/basket/add", form,
            _id + "-basket-add", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail($"{_id}: basket add unreachable", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail(
                $"{_id}: basket add HTTP {res.StatusCode} at /view/basket/add",
                retryable: res.StatusCode >= 500);

        c.Session.Vars["basket"] = res.Body;
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
        OpenCheckoutAsync(c, _id + "-checkout", "/cart/checkout", ct);

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        // Hybris checkout is a multi-step controller flow; there is no single POST that places
        // the order. Saying which step is missing is more useful than a bare failure.
        var res = await GetAsync(c, Origin(c.Url) + "/cart/checkout", _id + "-checkout-state", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail($"{_id}: checkout unreachable", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail($"{_id}: checkout HTTP {res.StatusCode}", retryable: true);

        return StepOutcome.Fail(
            $"{_id}: Hybris checkout is a staged controller flow (delivery → payment → review); " +
            "placing the order needs the per-stage form posts, which are not captured yet");
    }
}
