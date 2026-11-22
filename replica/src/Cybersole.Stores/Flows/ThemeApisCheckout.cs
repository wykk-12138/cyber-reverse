using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The theme APIs cart checkout endpoint.
///
/// <para>
/// <b>Observed</b> (R1373): <c>sub_140C32160</c> references <c>/cartApi/checkout</c>, <c>CartType</c>,
/// <c>CouponReferences</c>, <c>LineItems</c>, <c>LocationId</c>, <c>SourceSystem</c>, the two cart-type values
/// <c>Retail</c> and <c>Shopify</c>, and the host fragments <c>https://</c>, <c>www</c>, <c>themeapis</c>. The
/// function's literal table carries the path, so the reference is real and not a byte-pattern coincidence.
/// </para>
///
/// <para>
/// <b>Not observed:</b> the top-level domain. Those eleven literals do not include one, so the host is the caller's
/// value; this class will not write ".com" for a string the image does not carry.
/// </para>
/// </summary>
public static class ThemeApisCheckout
{
    /// <summary>The request path.</summary>
    public const string Path = "/cartApi/checkout";

    /// <summary>The scheme the sender writes.</summary>
    public const string Scheme = "https://";

    /// <summary>The subdomain label.</summary>
    public const string SubdomainLabel = "www";

    /// <summary>The host label.</summary>
    public const string HostLabel = "themeapis";

    /// <summary>The two cart types the sender names.</summary>
    public const string CartTypeRetail = "Retail";

    /// <summary>The Shopify cart type.</summary>
    public const string CartTypeShopify = "Shopify";

    /// <summary>The body field names the sender names.</summary>
    public static readonly string[] BodyFieldNames =
    {
        "CartType", "LineItems", "LocationId", "SourceSystem", "CouponReferences",
    };

    /// <summary>
    /// The host the sender would build, given the top-level domain — the one piece its literals do not carry.
    /// </summary>
    public static string HostFor(string topLevelDomain) =>
        Scheme + SubdomainLabel + "." + HostLabel + "." + topLevelDomain.TrimStart('.');

    /// <summary>The full url for a top-level domain.</summary>
    public static string UrlFor(string topLevelDomain) => HostFor(topLevelDomain) + Path;

    /// <summary>
    /// The request body. Only the fields a caller has are written; the sender's own field list is the order.
    /// </summary>
    public static JObject Body(
        string cartType, JArray? lineItems, string? locationId, string? sourceSystem, JArray? couponReferences)
    {
        if (cartType != CartTypeRetail && cartType != CartTypeShopify)
            throw new ArgumentOutOfRangeException(nameof(cartType),
                "cart type is one of the two values the sender names");

        var body = new JObject { ["CartType"] = cartType };
        if (lineItems is not null) body["LineItems"] = lineItems;
        if (!string.IsNullOrEmpty(locationId)) body["LocationId"] = locationId;
        if (!string.IsNullOrEmpty(sourceSystem)) body["SourceSystem"] = sourceSystem;
        if (couponReferences is not null) body["CouponReferences"] = couponReferences;
        return body;
    }

    /// <summary>Post the checkout.</summary>
    public static async Task<(JObject? Data, string Error)> SendAsync(
        FlowContext c, string? topLevelDomain, JObject body, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(topLevelDomain))
            return (null, "themeapis: no top-level domain — the image's literals stop at the host label");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, UrlFor(topLevelDomain!), body, "themeapis-checkout", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "themeapis: no reply");

            var data = reply["data"] as JObject ?? reply;
            return (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "themeapis: " + ex.GetType().Name);
        }
    }
}
