using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Braintree's client token, as this image asks for it.
///
/// <para>
/// <b>Observed</b> (R1358): the operation name's handler <c>sub_140B5EDB0</c> holds <c>authorizationFingerprint</c>,
/// <c>clientToken</c>, "Error getting token" and "StatusInfo"; <c>authorizationFingerprint</c> is Braintree's field
/// and <c>clientToken</c> is what the call returns. The document is 188 characters at 0x14714348C.
/// </para>
///
/// <para>
/// <b>Observed:</b> a second handler, <c>sub_140B61090</c>, holds <c>onepanini</c> — the marker that also appears in
/// the Shop app's add-to-cart handler and, as PANINI, in the PayPal order handler. So the payment stack is Braintree
/// under a module named after that token; the name itself is not protocol, which is why this class does not depend on
/// it.
/// </para>
/// </summary>
public static class BraintreeClientToken
{
    /// <summary>The operation name, 0x14703DADC.</summary>
    public const string OperationName = "generateClientToken";

    /// <summary>The document, 188 characters from 0x14714348C.</summary>
    public const string Document =
        "query generateClientToken($type: String) {\n  generateClientToken(type: $type) {\n    status\n    message\n    data {\n      clientToken\n      e_t_s\n      __typename\n    }\n    __typename\n  }\n}\n";

    /// <summary>The field Braintree calls the authorization fingerprint.</summary>
    public const string AuthorizationFingerprintField = "authorizationFingerprint";

    /// <summary>The field the reply carries the token in.</summary>
    public const string ClientTokenField = "clientToken";

    /// <summary>The handler's words when the token cannot be had.</summary>
    public const string ErrorGettingTokenMessage = "Error getting token";

    /// <summary>The request body.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Fetch the client token. The reply's <c>clientToken</c> is returned; a reply without one becomes the handler's
    /// own message rather than a raw error.
    /// </summary>
    public static async Task<(string? Token, string Error)> FetchAsync(
        FlowContext c, string? endpoint, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(endpoint)) return (null, "braintree: no endpoint");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, endpoint!, Envelope(variables ?? new JObject()), "braintree-token", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, ErrorGettingTokenMessage);

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, ErrorGettingTokenMessage);

            var token = reply["data"]?[ClientTokenField]?.ToString()
                        ?? reply[ClientTokenField]?.ToString();
            return string.IsNullOrEmpty(token) ? (null, ErrorGettingTokenMessage) : (token, string.Empty);
        }
        catch (Exception)
        {
            return (null, ErrorGettingTokenMessage);
        }
    }
}
