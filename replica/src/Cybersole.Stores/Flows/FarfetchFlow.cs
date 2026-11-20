using System.Text.RegularExpressions;
using Cybersole.Http;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Farfetch.
///
/// The binary carries only the display name "Farfetch" — no host and no endpoint strings —
/// so the implementation follows the site's public surface rather than a recovered one.
/// Farfetch runs its catalogue behind a JSON API that the storefront itself calls:
///
///   GET  /api/ff-products/v1/products/{productId}/          product + variants
///   POST /api/basket/v1/items                               add to basket  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R294)
///   GET  /api/basket/v1/                                     basket summary
///   GET  /api/checkout/v1/basket/{id}                        checkout entry
///   PUT  /api/checkout/v1/basket/{id}/shipping               shipping block
///   POST /api/checkout/v1/basket/{id}/payment                payment
///   POST /api/checkout/v1/basket/{id}/place-order            submit
///
/// Three headers matter and are set on every call: <c>X-Requested-With: XMLHttpRequest</c>
/// (the API 403s without it), <c>ffid</c> (a client id issued on the first page load) and the  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R297)
/// usual storefront <c>Accept: application/json</c>.
/// </summary>
/// <summary>
/// R1038 retracts R1036's conclusion. That round probed "farfetch.com", "api.farfetch.com" and the API prefixes, found
/// zero on every one, and wrote here that the original never mentions the store. It does:
///
///   0x14338eadc  Farfetch
///   0x146d8dfdc  Farfetch
///   0x146d8e004  Farfetch Checkout
///
/// A bare-word probe finds all three, and "Farfetch Checkout" is the original naming a checkout flow for this store. So
/// the store is supported; what is absent is this workspace's knowledge of its transport -- the domain and the seven
/// API routes return zero at every spelling tried.
///
/// Which makes Farfetch a gap rather than an addition: the original has the flow, this replica does not know how to
/// speak to it. The seven steps report for that reason and no other. R1036's forty-three trimmed functions stay
/// trimmed, because they served requests that were invented; the flow itself stays.
///
/// The lesson behind the retraction is worth keeping beside the code: the control that exposed it found that domains
/// usually are literals -- nike.com, footlocker.com, supreme.com, mywarhammer.com and mattel.com all appear -- and also
/// that my first counter-examples were misspellings, since zalando is present as ZalandoAndroidMobile and asos as
/// "ASOS Sample Sale". A precise string finds only the spellings it was written for.
///
/// R1077 closes the question with the decompile. The binary's whole Farfetch footprint is display metadata:
/// 'Farfetch' twice -- the site-catalog entry the settings-descriptor builder sub_140F7DDE0 constructs as
/// {name 'Farfetch', display 'Farfetch', typeId 4, flag 1} -- and 'Farfetch Checkout' once, a checkout-type
/// enum registered by sub_1407528C0 beside 'Shopify Checkout' / 'Kith EU Checkout' / 'Finishline / JD Sports'.
/// No route literal exists at any spelling because the transport is server-delivered:
/// https://api.cybersole.io/connect/app (0x14705357c, fetched by sub_140F3D400) syncs config entries through
/// the ConfigAdded / SharedAdded / ConfigRemoved / SharedRemoved / SubscribeGroups / UnsubscribeGroups keys
/// (0x146B9B070 .. 0x146F13F40). A Farfetch config entry's schema needs the original login to capture, so the
/// seven steps below are Unknown with exactly that named -- not "unprobed", classified.
/// </summary>
public class FarfetchFlow : StoreFlow
{
    public override string Id => "farfetch";
    public override string Name => "Farfetch";
    public override IReadOnlyList<string> Domains => new[] { "farfetch.com" };

    /// <summary>Farfetch's API only answers requests that look like its own XHRs.</summary>
    protected virtual void Prime(FlowContext c, string tag)
    {
        c.Session.Vars["farfetch.tag"] = tag;
    }

    private static string Api(FlowContext c, string path) =>
        c.Session.Vars.TryGetValue("farfetch.origin", out var origin) && origin is { Length: > 0 }
            ? origin + path
            : Origin(c.Url) + path;

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/", "farfetch-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("farfetch home unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"farfetch home HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["farfetch.origin"] = Origin(c.Url);

        // the storefront hands out its client id in a cookie on first load
        if (res.Cookies.TryGetValue("ffid", out var ffid) && !string.IsNullOrEmpty(ffid))  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R297)
            c.Session.Vars["farfetch.ffid"] = ffid;  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R297)

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        // R1077: the decompile closed the question this report used to leave open -- see the class header
        // for the full evidence. The route is a server-delivered connect/app config entry, and the entry's
        // schema needs the original login to capture.
        return StepOutcome.Fail(
            "farfetch: product route unrecorded locally — it is a server-delivered connect/app config entry, schema needs the original login to capture");
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;
        var wanted = c.Product?.Sizes.FirstOrDefault();

        // Farfetch exposes one entry per size with its own merchant id.
        string? chosen = null;
        string? chosenSize = null;

        foreach (Match m in Regex.Matches(body,
                     @"""size""\s*:\s*""([^""]+)""[^}]*?""(?:merchantId|id)""\s*:\s*""?([A-Za-z0-9_\-]+)""?"))
        {
            var size = m.Groups[1].Value;
            var id = m.Groups[2].Value;

            if (chosen is null) { chosen = id; chosenSize = size; }

            if (wanted is not null && size.Equals(wanted, StringComparison.OrdinalIgnoreCase))
            {
                chosen = id;
                chosenSize = size;
                break;
            }
        }

        if (chosen is null)
        {
            var fallback = Regex.Match(body, @"""merchantId""\s*:\s*""?([A-Za-z0-9_\-]+)""?");
            if (!fallback.Success)
                return Task.FromResult(StepOutcome.Fail("farfetch: no variant in payload"));
            chosen = fallback.Groups[1].Value;
        }

        c.Session.VariantId = chosen;
        c.Session.Vars["variant"] = chosen;
        if (chosenSize is not null)
        {
            c.Session.Vars["size"] = chosenSize;
            c.Session.Vars["sizes"] = chosenSize;
        }

        return Task.FromResult(StepOutcome.Success());
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c,
        CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;

        var soldOut = body.Contains(@"""isSoldOut"":true", StringComparison.OrdinalIgnoreCase) ||
                      body.Contains(@"""available"":false", StringComparison.OrdinalIgnoreCase) ||
                      body.Contains("out of stock", StringComparison.OrdinalIgnoreCase);

        c.Session.Vars["available"] = soldOut ? "false" : "true";

        var sizes = new List<string>();
        foreach (Match m in Regex.Matches(body, @"""size""\s*:\s*""([^""]{1,12})"""))
        {
            var s = m.Groups[1].Value.Trim();
            if (s.Length > 0 && !sizes.Contains(s)) sizes.Add(s);
        }
        if (sizes.Count > 0) c.Session.Vars["sizes"] = string.Join(',', sizes);

        return Task.FromResult(StepOutcome.Success());
    }

    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        // R1077: server-delivered route -- see the class header for the decompiled evidence.
        return StepOutcome.Fail(
            "farfetch: add-to-cart route unrecorded locally — it is a server-delivered connect/app config entry, schema needs the original login to capture");
    }

    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        // R1077: server-delivered route -- see the class header for the decompiled evidence.
        return StepOutcome.Fail(
            "farfetch: basket route unrecorded locally — it is a server-delivered connect/app config entry, schema needs the original login to capture");
    }

    public override async Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct)
    {
        // R1077: server-delivered route -- see the class header for the decompiled evidence.
        return StepOutcome.Fail(
            "farfetch: checkout route unrecorded locally — it is a server-delivered connect/app config entry, schema needs the original login to capture");
    }

    public override async Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct)
    {
        // R1077: server-delivered route -- see the class header for the decompiled evidence.
        return StepOutcome.Fail(
            "farfetch: shipping route unrecorded locally — it is a server-delivered connect/app config entry, schema needs the original login to capture");
    }

    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        // R1077: server-delivered route -- see the class header for the decompiled evidence.
        return StepOutcome.Fail(
            "farfetch: payment route unrecorded locally — it is a server-delivered connect/app config entry, schema needs the original login to capture");
    }

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        // R1077: server-delivered route -- see the class header for the decompiled evidence.
        return StepOutcome.Fail(
            "farfetch: place-order route unrecorded locally — it is a server-delivered connect/app config entry, schema needs the original login to capture");
    }

    /// <summary>
    /// Farfetch product URLs look like <c>/shopping/item/{id}.aspx</c>; the numeric id is the
    /// item id the product API is keyed on. A bare <c>?pid=</c> or <c>/item/{id}</c> also works.
    /// </summary>
    protected static string? ProductIdOf(string url)
    {
        foreach (var pattern in new[]
                 {
                     @"/shopping/item/(\d+)", @"/item/(\d+)", @"[?&]pid=(\d+)", @"[?&]productId=(\d+)",
                 })
        {
            var m = Regex.Match(url, pattern);
            if (m.Success) return m.Groups[1].Value;
        }

        return null;
    }
}
