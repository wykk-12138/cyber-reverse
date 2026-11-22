using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// AO's app checkout endpoints.
///
/// <para>
/// <b>Observed</b> (R1374): three full urls at 0x14705D114/17C/1E4, each carried in the literal table of the function
/// that sends it. The origin the senders set is <c>https://checkout.ao.com</c>; the contact step labels itself
/// "Submitting info" and the payment step "Getting checkout"; the payment sender has both a JSON path and a
/// form-encoded one.
/// </para>
///
/// <para>
/// <b>Not observed here:</b> the body field names. These functions carry header names — accept, cookie, origin,
/// newrelic, priority — and the JSON is built by their callers, so a body is the caller's to supply.
/// </para>
/// </summary>
public static class AoCheckout
{
    /// <summary>The contact step's url.</summary>
    public const string ContactUrl = "https://checkout.ao.com/v2/app/contact";

    /// <summary>The delivery step's url.</summary>
    public const string DeliveryUrl = "https://checkout.ao.com/v2/app/delivery";

    /// <summary>The payment step's url.</summary>
    public const string PaymentUrl = "https://checkout.ao.com/v2/app/payment";

    /// <summary>The origin every sender sets.</summary>
    public const string Origin = "https://checkout.ao.com";

    /// <summary>The contact step's own words.</summary>
    public const string SubmittingInfoMessage = "Submitting info";

    /// <summary>The payment step's own words.</summary>
    public const string GettingCheckoutMessage = "Getting checkout";

    /// <summary>The content type the payment sender uses on its form path.</summary>
    public const string FormContentType = "application/x-www-form-urlencoded";

    /// <summary>The three steps, in the order a checkout runs them.</summary>
    public static readonly string[] Steps = { "contact", "delivery", "payment" };

    /// <summary>The url for one step, or null when the step is not one of the three.</summary>
    public static string? UrlFor(string step) => step switch
    {
        "contact" => ContactUrl,
        "delivery" => DeliveryUrl,
        "payment" => PaymentUrl,
        _ => null,
    };

    /// <summary>Post one step. The body is the caller's: these functions name headers, not fields.</summary>
    public static async Task<(JObject? Data, string Error)> SendAsync(
        FlowContext c, string step, JObject body, CancellationToken ct)
    {
        var url = UrlFor(step);
        if (url is null) return (null, "ao: unknown step " + step);

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url, body ?? new JObject(), "ao-" + step, ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "ao: no reply on " + step);

            var data = reply["data"] as JObject ?? reply;
            return (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "ao: " + ex.GetType().Name);
        }
    }
}
