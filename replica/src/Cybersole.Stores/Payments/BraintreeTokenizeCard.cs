using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Braintree's card tokenisation, at the payments host its handler names.
///
/// <para>
/// <b>Observed</b> (R1360): <c>sub_140B632B0</c> holds <c>https://payments.braintree-api.com/graphql</c> together
/// with <c>client</c>, <c>clientSdkMetadata</c>, <c>creditCard</c>, <c>cvv</c>, <c>expirationMonth</c>,
/// <c>expirationYear</c>, <c>billingAddress</c> and <c>dropin2</c> — Braintree's payments API and its Drop-in v2
/// marker. The document is 505 characters at 0x1470E33B4.
/// </para>
///
/// <para>
/// <b>Observed:</b> the same module also fetches a client token (R1358), so the two belong to one Braintree
/// integration rather than to a store's own checkout.
/// </para>
/// </summary>
public static class BraintreeTokenizeCard
{
    /// <summary>The host the handler names.</summary>
    public const string Url = "https://payments.braintree-api.com/graphql";

    /// <summary>The operation name.</summary>
    public const string OperationName = "TokenizeCreditCard";

    /// <summary>The document, 505 characters from 0x1470E33B4.</summary>
    public const string Document =
        "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId         business         consumer         purchase         corporate       }     }   } }";

    /// <summary>The SDK marker the handler carries — Drop-in v2.</summary>
    public const string ClientSdkName = "dropin2";

    /// <summary>The field names the handler names beside the operation.</summary>
    public static readonly string[] ObservedFields =
    {
        "client", "clientSdkMetadata", "creditCard", "cvv", "expirationMonth", "expirationYear",
        "billingAddress", "input",
    };

    /// <summary>The request body.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Tokenise a card. The credit-card object, the client token and the SDK metadata are the caller's — copying
    /// card fields into source would be copying credentials, the same rule the storefront token goes by.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> TokenizeAsync(
        FlowContext c, JObject variables, CancellationToken ct, string? url = null)
    {
        var creditCard = variables?["creditCard"] ?? variables?["input"]?["creditCard"];
        if (creditCard is null)
            return (null, "braintree: no creditCard — the mutation is keyed by it");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url ?? Url, Envelope(variables!), "braintree-tokenize", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "braintree: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "braintree: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject;
            return data is null ? (null, "braintree: no data in reply") : (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "braintree: " + ex.GetType().Name);
        }
    }
}
