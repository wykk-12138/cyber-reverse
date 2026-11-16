using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The Poq app surface, as the image impersonates it. R779.
///
/// <para>
/// This is not Offspring's web checkout. That surface is Hybris, and a live-evidence test pins it
/// (<c>PlatformAssignmentTests.OffspringIsHybrisNotMagento</c>). The strings behind this class are the <b>app</b>
/// surface: a Poq platform host addressed per client, carrying the identity of Poq's own iOS app. R772 built a flow
/// from one of those two surfaces and was reverted for treating it as a replacement; both are real, on different
/// levels.
/// </para>
///
/// <para>
/// <b>The identity, all Observation (R777/R778):</b>
/// </para>
///
/// <code>
/// user-agent             Poq-Native-iOS-App
/// accept                 application/json
/// accept-encoding        gzip, deflate, br
/// accept-language        nl-NL,nl;q=0.9
/// version-code           26.0
/// platform               iphone
/// poq-app-id             275
/// poq-app-identifier     a1dad595-7431-45bc-9fb9-684dac169b5b
/// </code>
///
/// <para>
/// Three more headers exist but carry runtime values rather than constants -- <c>poq-country-identifier</c>,
/// <c>poq-currency-identifier</c>, <c>poq-user-id</c> -- plus <c>authorization</c>, which the image builds as
/// <c>"Bearer " + token</c>. They are read from the session here; copying the image's constants into them would
/// present runtime data as fixed values.
/// </para>
///
/// <para>
/// <b>Inference (low):</b> <c>accept-language</c> is Dutch. That is the literal in the builder, but whether another
/// region overrides it is unknown, so it is applied as a default that a caller may replace rather than as settled.
/// </para>
///
/// <para>
/// Four actions are evidenced and implemented: guest token, product lookup by id, cart items, checkout start. The
/// other three commerce steps are <b>not</b> overridden -- the image names no address, payment or order endpoint for
/// this surface, and an override that always fails would count as implemented in ModuleCoverageTests while being
/// unable to complete a purchase.
/// </para>
/// </summary>
public sealed class PoqAppFlow : StoreFlow
{
    /// <summary>The platform host, verbatim.</summary>
    public const string Platform = "https://platform.poq.io";

    // ---- identity (Observation) ----
    public const string IdentityUserAgent = "Poq-Native-iOS-App";
    public const string IdentityAccept = "application/json";
    public const string IdentityAcceptEncoding = "gzip, deflate, br";
    /// <summary>Inference (low): a Dutch default; a caller in another region may override it.</summary>
    public const string IdentityAcceptLanguage = "nl-NL,nl;q=0.9";
    public const string IdentityVersionCode = "26.0";
    public const string IdentityPlatformName = "iphone";
    public const string IdentityAppId = "275";
    public const string IdentityAppIdentifier = "a1dad595-7431-45bc-9fb9-684dac169b5b";

    // ---- actions (Observation) ----
    public const string GuestToken = Platform + "/clients/offspring/account/guest-token";
    public const string CartItems = Platform + "/clients/offspring/cart/items";
    public const string CheckoutStart = Platform + "/clients/offspring/checkout/start";
    public const string Products = Platform + "/clients/offspring/products?ids=";

    /// <summary>Office's ATA verification-code action, for the sibling client.</summary>
    public const string OfficeAtaVerify = Platform + "/clients/office/AtaVerifyCaptcha";

    private readonly string _id;
    private readonly string _name;
    private readonly IReadOnlyList<string> _domains;
    private readonly string _client;

    public PoqAppFlow(string id, string name, IReadOnlyList<string> domains, string client)
    {
        _id = id;
        _name = name;
        _domains = domains;
        _client = client;
    }

    /// <summary>Offspring's app surface, the one client for which the image names a full action set.</summary>
    public PoqAppFlow() : this("poq-app", "Poq App", new[] { "platform.poq.io" }, "offspring")
    {
    }

    public override string Id => _id;
    public override string Name => _name;
    public override IReadOnlyList<string> Domains => _domains;

    private static bool IsBlocked(NetResponse? res) => res is { StatusCode: 403 or 429 };

    private string Action(string rest) => Platform + "/clients/" + _client + "/" + rest;

    /// <summary>
    /// Put the app identity on the session, which is where the request layer reads headers from. Runtime values win
    /// over the constants: a session that already carries a token or a country keeps it.
    /// </summary>
    private void ApplyIdentity(FlowContext c)
    {
        var h = c.Session.Headers;
        h["user-agent"] = IdentityUserAgent;
        h["accept"] = IdentityAccept;
        h["accept-encoding"] = IdentityAcceptEncoding;
        if (!h.ContainsKey("accept-language")) h["accept-language"] = IdentityAcceptLanguage;
        h["version-code"] = IdentityVersionCode;
        h["platform"] = IdentityPlatformName;
        h["poq-app-id"] = IdentityAppId;
        h["poq-app-identifier"] = IdentityAppIdentifier;

        foreach (var key in new[] { "poq-country-identifier", "poq-currency-identifier", "poq-user-id" })
            if (c.Session.Vars.TryGetValue("header:" + key, out var value) && value.Length > 0)
                h[key] = value;
    }

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        ApplyIdentity(c);

        var res = await PostJsonAsync(c, Action("account/guest-token"), "{}", _id + "-guest-token", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail($"{_id}: guest token unreachable", retryable: true);
        if (IsBlocked(res)) return StepOutcome.Fail($"{_id}: guest token blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"{_id}: guest token HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["guestToken"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>Product lookup by id — the image carries <c>products?ids=</c> with the query left open.</summary>
    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        ApplyIdentity(c);

        var productId = c.Session.Vars.TryGetValue("productId", out var pid) && pid.Length > 0
            ? pid
            : TailOf(c.Url);

        if (string.IsNullOrEmpty(productId))
            return StepOutcome.Fail($"{_id}: no product id in the url to look up");

        var res = await GetAsync(c, Action("products?ids=") + productId, _id + "-product", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail($"{_id}: product unreachable", retryable: true);
        if (IsBlocked(res)) return StepOutcome.Fail($"{_id}: product blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"{_id}: product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["product"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>Sizes come from the product payload. Inference (medium): the payload shape.</summary>
    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.Vars.TryGetValue("product", out var body) || string.IsNullOrEmpty(body))
            return Task.FromResult(StepOutcome.Fail($"{_id}: no product payload to read sizes from"));

        var sizes = new List<string>();
        try
        {
            foreach (var node in JToken.Parse(body).SelectTokens("$..variants[*]"))
            {
                var size = node["size"]?.ToString() ?? node["name"]?.ToString();
                if (!string.IsNullOrEmpty(size) && !sizes.Contains(size)) sizes.Add(size);
            }
        }
        catch (Newtonsoft.Json.JsonException)
        {
            return Task.FromResult(StepOutcome.Fail($"{_id}: product payload is not json"));
        }

        c.Session.Vars["sizes"] = string.Join(",", sizes);
        return Task.FromResult(sizes.Count > 0
            ? StepOutcome.Success()
            : StepOutcome.Fail($"{_id}: product payload lists no variants"));
    }

    /// <summary>Adds a line item. Inference (medium): the request body; the endpoint is Observation.</summary>
    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        ApplyIdentity(c);

        var variant = c.Session.VariantId ?? string.Empty;
        if (string.IsNullOrEmpty(variant)) return StepOutcome.Fail($"{_id}: no variant id to add");

        var payload = new JObject
        {
            ["productId"] = c.Session.Vars.TryGetValue("productId", out var pid) ? pid : null,
            ["variantId"] = variant,
            ["quantity"] = 1,
        };

        var res = await PostJsonAsync(c, Action("cart/items"),
            payload.ToString(Newtonsoft.Json.Formatting.None), _id + "-cart-items", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail($"{_id}: cart items unreachable", retryable: true);
        if (IsBlocked(res)) return StepOutcome.Fail($"{_id}: cart items blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"{_id}: cart items HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>Observation: <c>checkout/start</c>.</summary>
    public override async Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct)
    {
        ApplyIdentity(c);

        var res = await PostJsonAsync(c, Action("checkout/start"), "{}", _id + "-checkout-start", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail($"{_id}: checkout start unreachable", retryable: true);
        if (IsBlocked(res)) return StepOutcome.Fail($"{_id}: checkout start blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"{_id}: checkout start HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["checkout"] = res.Body;
        return StepOutcome.Success();
    }

    // SubmitShippingAsync, SubmitPaymentAsync and SubmitOrderAsync are intentionally absent: the image names no
    // address, payment or order endpoint on this surface. An override returning a failure would count as
    // implemented in ModuleCoverageTests and misreport the module as able to complete a purchase.

    private static string TailOf(string url)
    {
        var trimmed = url.TrimEnd('/');
        var slash = trimmed.LastIndexOf('/');
        return slash >= 0 && slash < trimmed.Length - 1 ? trimmed[(slash + 1)..] : string.Empty;
    }
}
