using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The PayPal Express cart submission that carries an <see cref="AddressInput"/>.
///
/// <para>
/// <b>Observed</b> (R1378): <c>sub_140AD5B10</c> posts to <c>/cart/paypal</c> with <c>application/json</c>, and its
/// literals name <c>billingAddress</c>, <c>checkoutType</c> with the two values <c>EXPRESS</c> and <c>OTHER</c>,
/// <c>payerId</c>, <c>details</c>, <c>nonce</c>, <c>PayPalAccount</c>, <c>Store</c> and the label "Submit info".
/// </para>
///
/// <para>
/// <b>Not observed:</b> a host. The path is relative, so the origin is the caller's.
/// </para>
/// </summary>
public static class PayPalExpressCart
{
    /// <summary>The relative path the sender builds.</summary>
    public const string Path = "/cart/paypal";

    /// <summary>The Express checkout type.</summary>
    public const string CheckoutTypeExpress = "EXPRESS";

    /// <summary>The other checkout type the sender names.</summary>
    public const string CheckoutTypeOther = "OTHER";

    /// <summary>The step's label.</summary>
    public const string SubmitInfoMessage = "Submit info";

    /// <summary>The body field names the sender names.</summary>
    public static readonly string[] BodyFieldNames =
    {
        "billingAddress", "checkoutType", "payerId", "nonce", "details",
    };

    /// <summary>The url for one origin.</summary>
    public static string UrlFor(string origin) => origin.TrimEnd('/') + Path;

    /// <summary>
    /// The request body. The address is the builder's object; the checkout type is one of the two the sender names.
    /// </summary>
    public static JObject Body(
        AddressInput address, string checkoutType, string? payerId, string? nonce, JObject? details = null)
    {
        if (checkoutType != CheckoutTypeExpress && checkoutType != CheckoutTypeOther)
            throw new ArgumentOutOfRangeException(nameof(checkoutType),
                "checkout type is one of the two values the sender names");

        var body = new JObject
        {
            ["billingAddress"] = address?.ToJson() ?? new JObject(),
            ["checkoutType"] = checkoutType,
        };
        if (!string.IsNullOrEmpty(payerId)) body["payerId"] = payerId;
        if (!string.IsNullOrEmpty(nonce)) body["nonce"] = nonce;
        if (details is not null) body["details"] = details;
        return body;
    }

    /// <summary>Post the submission.</summary>
    public static async Task<(JObject? Data, string Error)> SendAsync(
        FlowContext c, string? origin, JObject body, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(origin)) return (null, "paypal-express: no origin");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, UrlFor(origin!), body, "paypal-express", ct).ConfigureAwait(false);
            if (reply is null) return (null, "paypal-express: no reply");

            var data = reply["data"] as JObject ?? reply;
            return (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "paypal-express: " + ex.GetType().Name);
        }
    }
}
