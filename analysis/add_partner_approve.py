"""R1335: the PayPal partner approval — document, endpoint and variable names, all observed.

Following the document at 0x1470E9FA4 to its sender lands on sub_14110C600 (1647 bytes), and that function
gives the whole request:

    0x147097E78  len=31  "https://www.paypal.com/graphql/"     <- the base, with a trailing slash
    0x1470E9F98          the 5407-character document (R1321 decoded it)
    0x147109320  len=13  "operationName"
    0x14711CCB0  len=5   "query"
    0x14717D2E8  len=9   "variables"
    0x146F76688  len=16  "application/json"
    0x146F79800  len=20  "approveMemberPayment"

and the variables it fills, by name:

    token, selectedAddressId, preferredShippingAddressId, selectedFundingOptionId,
    preferredFundingOptionId, secondaryFundingOptionIds, preAuthorizationRequired,
    fundingMethodType, setStickyFiRequired, scaCompleted, experiences

plus two enum values, IFRAME (0x146DB53D8) and INSTANT (0x146DB59A8), which belong to fundingMethodType or
experiences.

That is more than enough to build the request without inventing anything: the URL is the observed base plus the
observed operation name, and the variables are the observed names. The document is written from the decoded
bytes, never pasted — R1326's lesson.

Usage: python analysis/add_partner_approve.py
"""
import io
import json

DOCS = 'analysis/.magento_cart_docs.json'
OUT = 'replica/src/Cybersole.Stores/Payments/PayPalPartnerApprove.cs'

document = json.loads(io.open(DOCS, encoding='utf-8').read())['approve_member_payment']
literal = document.replace('"', '""')

source = '''using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// The PayPal partner approval — <c>approveMemberPayment</c> — read out of the image.
///
/// <para>
/// <b>Observed</b>, all from the sender at <c>sub_14110C600</c> (1647 bytes) and the document at 0x1470E9FA4:
/// the base URL <c>https://www.paypal.com/graphql/</c> (0x147097E78, 31 characters, with the trailing slash),
/// the operation name, the envelope keys (<c>operationName</c>, <c>query</c>, <c>variables</c>) and the
/// content type <c>application/json</c>; the eleven variable names; and the two enum literals
/// <c>IFRAME</c> and <c>INSTANT</c>.
/// </para>
///
/// <para>
/// <b>Inference:</b> that <c>IFRAME</c> and <c>INSTANT</c> belong to <c>fundingMethodType</c>. The image puts
/// both in this function beside that variable's name, but no assignment pairs them, so they are exposed as
/// constants and a caller chooses rather than this class guessing.
/// </para>
/// </summary>
public static class PayPalPartnerApprove
{
    /// <summary>The observed base URL, trailing slash included, from 0x147097E78.</summary>
    public const string BaseUrl = "https://www.paypal.com/graphql/";

    /// <summary>The operation name the image sends, from 0x146F79800.</summary>
    public const string OperationName = "approveMemberPayment";

    /// <summary>The endpoint the image composes: base plus operation name.</summary>
    public const string Url = BaseUrl + OperationName;

    /// <summary>The document, 5407 characters from 0x1470E9FA4.</summary>
    public const string Document = @"__DOCUMENT__";

    /// <summary>The eleven variable names the sender fills, in the image's own spelling.</summary>
    public static readonly string[] VariableNames =
    {
        "token", "selectedAddressId", "preferredShippingAddressId", "selectedFundingOptionId",
        "preferredFundingOptionId", "secondaryFundingOptionIds", "preAuthorizationRequired",
        "fundingMethodType", "setStickyFiRequired", "scaCompleted", "experiences",
    };

    /// <summary>The two enum literals that sit beside <c>fundingMethodType</c> in the sender.</summary>
    public const string FundingMethodIframe = "IFRAME";
    public const string FundingMethodInstant = "INSTANT";

    /// <summary>
    /// The request body: the operation name, the document and the variables, which is the envelope the sender
    /// builds. <paramref name="variables"/> is passed through rather than assembled here, because seven of the
    /// eleven are the caller's — a payment method id, an address id, a token — and inventing defaults for them
    /// would send a request the partner could accept with the wrong meaning.
    /// </summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Approve a member payment. Returns the GraphQL <c>data</c> node, or null with the reason in
    /// <paramref name="error"/>. The document returns <c>state</c>, the buyer, the cart, payment contingencies
    /// and completed payment info, so a caller reads <c>state</c> first and treats anything other than a
    /// completed state as a non-approval.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> ApproveAsync(
        FlowContext c, JObject variables, CancellationToken ct, string? url = null)
    {
        if (variables?["token"] is null || string.IsNullOrEmpty(variables["token"]!.ToString()))
            return (null, "approve: no token — the approval is keyed by the buyer token and cannot be replayed");

        var options = c.Options("paypal-approve");
        var body = Envelope(variables);

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url ?? Url, body, "paypal-approve", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "approve: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "approve: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject;
            return data is null ? (null, "approve: no data in reply") : (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "approve: " + ex.GetType().Name);
        }
    }
}
'''.replace('__DOCUMENT__', literal)

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s with a %d-character document' % (OUT, len(document)))
