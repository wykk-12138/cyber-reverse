using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// On Running's GraphQL endpoint — the guest checkout mutation.
///
/// <para>
/// <b>Observed</b> (R1353): the sender at <c>sub_140E15490</c> carries <c>https://www.on.com/ko-kr/graphql</c>, which
/// is the string <see cref="AccountAndAuthFamilies.OnRunning.GraphQl"/> already held from an earlier sweep — the
/// table was written before anything was known to use it. The document is 148 characters at 0x1470F24CC and
/// declares <c>$email</c>.
/// </para>
/// </summary>
public static class OnRunningGraphQl
{
    /// <summary>The URL the sender carries, built from the table rather than written twice.</summary>
    public const string Url = "https://" + AccountAndAuthFamilies.OnRunning.GraphQl;

    /// <summary>The operation name.</summary>
    public const string OperationName = "checkoutAsGuest";

    /// <summary>The document, 148 characters from 0x1470F24CC.</summary>
    public const string Document =
        "mutation checkoutAsGuest($email: String!) {\n  checkoutAsGuest(email: $email) {\n    order {\n      errors\n      __typename\n    }\n    __typename\n  }\n}\n";

    /// <summary>The one variable the document declares.</summary>
    public static readonly string[] DeclaredVariables = { "email" };

    /// <summary>The request body.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Start a guest checkout. The document's only variable is the email; the mutation's own reply carries whatever
    /// the store returns.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> CheckoutAsGuestAsync(
        FlowContext c, JObject variables, CancellationToken ct)
    {
        if (variables?["email"] is null || string.IsNullOrEmpty(variables["email"]!.ToString()))
            return (null, "on-running: no email — the mutation's only variable");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, Url, Envelope(variables), "on-running-guest", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "on-running: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "on-running: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject;
            return data is null ? (null, "on-running: no data in reply") : (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "on-running: " + ex.GetType().Name);
        }
    }
}
