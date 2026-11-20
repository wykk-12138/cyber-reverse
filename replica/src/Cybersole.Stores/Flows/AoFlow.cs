using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;

namespace Cybersole.Stores.Flows;

/// <summary>
/// AO.com — a UK appliance retailer whose checkout is a separate ASP.NET host with its own JSON API.
///
/// <para>
/// <b>Observed</b>: the image's URL pool carries <c>https://ao.com</c> (0x147052594),
/// <c>https://checkout.ao.com</c> (0x14705D014), the basket page
/// <c>https://checkout.ao.com/shoppingbasket.aspx</c> (0x14705D0A4) and three API endpoints —
/// <c>/v2/app/contact</c> (0x14705D114), <c>/v2/app/delivery</c> (0x14705D17C) and
/// <c>/v2/app/payment</c> (0x14705D1E4). Three endpoints named contact, delivery and payment is a
/// three-step checkout, and the host split says the basket lives on a different origin from the shop.
/// The replica's catalogue had no AO entry at all: <c>ao.com</c> appeared only inside a Cardinal 3DS host
/// check.
/// </para>
///
/// <para>
/// <b>Unknown</b>, and why only two steps are overridden here: the request bodies for those three
/// endpoints. Nothing in the image spells their members — the URLs sit in an alphabetically sorted pool,
/// so their neighbours are other stores rather than their own keys — and this project has retracted more
/// invented bodies than anything else. The three paths are recorded as constants so the next session
/// starts from them; the steps that would post to them are left to the base class, which fails with its
/// own message rather than with a fabricated payload.
/// </para>
/// </summary>
public sealed class AoFlow : StoreFlow
{
    /// <summary>The shop.</summary>
    public const string Origin = "https://ao.com";

    /// <summary>The checkout host, which is a different origin from the shop.</summary>
    public const string CheckoutOrigin = "https://checkout.ao.com";

    /// <summary>The basket page on the checkout host.</summary>
    public const string BasketPath = "/shoppingbasket.aspx";

    /// <summary>Step one of the checkout API: the contact details.</summary>
    public const string ContactPath = "/v2/app/contact";

    /// <summary>Step two: the delivery slot and address.</summary>
    public const string DeliveryPath = "/v2/app/delivery";

    /// <summary>Step three: the payment.</summary>
    public const string PaymentPath = "/v2/app/payment";

    public override string Id => "ao";
    public override string Name => "AO";
    public override IReadOnlyList<string> Domains => new[] { "ao.com" };

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "ao-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("ao home unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"ao home HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["home"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// The product page. AO is server-rendered, so the title and price are in the markup; the structured
    /// data block is tried first because it carries the price as a number rather than as formatted text.
    /// </summary>
    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "ao-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("ao product unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"ao product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;

        var name = Regex.Match(res.Body, @"""name""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (string.IsNullOrEmpty(name)) name = Regex.Match(res.Body, @"<title>([^<|]+)").Groups[1].Value;
        if (!string.IsNullOrEmpty(name)) c.Session.Vars["product"] = name.Trim();

        var price = Regex.Match(res.Body, @"""price""\s*:\s*""?([\d.]+)""?").Groups[1].Value;
        if (string.IsNullOrEmpty(price))
            price = Regex.Match(res.Body, @"£\s?([\d,]+\.\d{2})").Groups[1].Value;
        if (!string.IsNullOrEmpty(price)) c.Session.Vars["price"] = price;

        var outOfStock = res.Body.Contains("out of stock", StringComparison.OrdinalIgnoreCase)
                         || res.Body.Contains("outofstock", StringComparison.OrdinalIgnoreCase);
        c.Session.Vars["stock"] = outOfStock ? "OUT_OF_STOCK" : "IN_STOCK";

        return StepOutcome.Success();
    }

    /// <summary>
    /// The basket page. AO keeps the basket on <c>checkout.ao.com</c>, so a flow that has to reach it needs
    /// the other origin rather than the one the task was opened on — the shop and the basket are different
    /// hosts in the image, not two paths on one.
    /// </summary>
    public static string BasketUrl() => CheckoutOrigin + BasketPath;

    /// <summary>Where a checkout step posts, on the checkout host.</summary>
    public static string StepUrl(string path) => CheckoutOrigin + path;
}
