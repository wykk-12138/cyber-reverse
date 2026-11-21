"""R1343: the PayPal checkout pair — PayWithQuery and ShipToQuery, sent by one function.

0x14110D030 (1512 bytes) references two documents and posts both to the partner base:

    https://www.paypal.com/graphql/   (0x147097E78, the same base the approval and currency use)
    operationName PayWithQuery        document 12561 chars at 0x14712190C
    operationName ShipToQuery         document  2031 chars at 0x147139B2C
    variables token, withSplitTender, expeirences

`expeirences` again — the image spells that key this way in every operation that takes it, so the replica keeps
sending it and a test says so. The documents themselves declare $token / $experiences / $withSplitTender and
$token respectively.

A second sender, 0x140F4C550 (2099 bytes), posts PayWithQuery through the browser-facing checkout web instead:
base https://www.paypal.com, x-app-name checkoutuinodeweb_hermione, x-paypal-internal-euat,
paypal-client-metadata-id, and the usual sec-fetch-* set. That is a different transport for the same query, and
this round does not guess which one a run wants — the partner path is the one the other four operations use, so
it is the one implemented.

Usage: python analysis/add_paypal_checkout.py
"""
import io
import json

DOCS = 'analysis/.paypal_checkout_docs.json'
OUT = 'replica/src/Cybersole.Stores/Payments/PayPalCheckoutQueries.cs'

documents = json.loads(io.open(DOCS, encoding='utf-8').read())


def escape_literal(text):
    out = []
    for character in text:
        if character == '\\':
            out.append('\\\\')
        elif character == '"':
            out.append('\\"')
        elif character == '\r':
            out.append('\\r')
        elif character == '\n':
            out.append('\\n')
        elif character == '\t':
            out.append('\\t')
        else:
            out.append(character)
    return ''.join(out)


source = '''using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// The PayPal partner checkout pair — <c>PayWithQuery</c> and <c>ShipToQuery</c> — read out of the image.
///
/// <para>
/// <b>Observed</b> (R1343): one sender, <c>sub_14110D030</c> (1512 bytes), references both documents and posts
/// them to the partner base <c>https://www.paypal.com/graphql/</c> (0x147097E78) with the envelope
/// <c>operationName</c> / <c>query</c> / <c>variables</c>. The documents are 12561 characters at 0x14712190C and
/// 2031 at 0x147139B2C; they declare <c>$token</c>, <c>$experiences</c> and <c>$withSplitTender</c>, and
/// <c>$token</c> alone.
/// </para>
///
/// <para>
/// <b>Observed:</b> the sender writes the middle variable key as <c>expeirences</c> — the same spelling the
/// currency sender uses — while the document declares <c>$experiences</c>. A faithful replica sends it the same
/// way; a test pins the pairing so nobody tidies it.
/// </para>
///
/// <para>
/// <b>Not used here:</b> a second sender, <c>sub_140F4C550</c> (2099 bytes), posts <c>PayWithQuery</c> through the
/// browser-facing checkout web with <c>checkoutuinodeweb_hermione</c>, <c>x-paypal-internal-euat</c> and
/// <c>paypal-client-metadata-id</c>. Two transports, one query; which a run wants is not established, so this
/// class implements the partner one that the other four operations share.
/// </para>
/// </summary>
public static class PayPalCheckoutQueries
{
    /// <summary>The partner base, shared with the approval and the currency conversion, 0x147097E78.</summary>
    public const string BaseUrl = PayPalPartnerApprove.BaseUrl;

    /// <summary>The pay-with operation, 0x146E3ACC0.</summary>
    public const string PayWithOperation = "PayWithQuery";

    /// <summary>The ship-to operation, 0x146E8A680.</summary>
    public const string ShipToOperation = "ShipToQuery";

    /// <summary>The pay-with endpoint: base plus operation name.</summary>
    public const string PayWithUrl = BaseUrl + PayWithOperation;

    /// <summary>The ship-to endpoint: base plus operation name.</summary>
    public const string ShipToUrl = BaseUrl + ShipToOperation;

    /// <summary>The pay-with document, 12561 characters from 0x14712190C.</summary>
    public const string PayWithDocument =
        "__PAY_WITH__";

    /// <summary>The ship-to document, 2031 characters from 0x147139B2C.</summary>
    public const string ShipToDocument =
        "__SHIP_TO__";

    /// <summary>
    /// The three variable keys the pay-with sender writes — including <c>expeirences</c>, which the document
    /// calls <c>$experiences</c>. The ship-to query declares only <c>token</c>.
    /// </summary>
    public static readonly string[] PayWithVariableNames = { "token", "withSplitTender", "expeirences" };

    /// <summary>The request body the sender builds.</summary>
    public static JObject Envelope(string operation, string document, JObject variables) => new()
    {
        ["operationName"] = operation,
        ["query"] = document,
        ["variables"] = variables,
    };

    /// <summary>Ask what the buyer can pay with. Null with a reason when the reply carries no session.</summary>
    public static async Task<(JObject? Session, string Error)> PayWithAsync(
        FlowContext c, JObject variables, CancellationToken ct, string? url = null)
        => await AskAsync(c, PayWithOperation, PayWithDocument, variables, "checkoutSession", ct,
            url ?? PayWithUrl).ConfigureAwait(false);

    /// <summary>Ask where the buyer's order ships. Same envelope, one variable.</summary>
    public static async Task<(JObject? Session, string Error)> ShipToAsync(
        FlowContext c, JObject variables, CancellationToken ct, string? url = null)
        => await AskAsync(c, ShipToOperation, ShipToDocument, variables, "checkoutSession", ct,
            url ?? ShipToUrl).ConfigureAwait(false);

    private static async Task<(JObject? Session, string Error)> AskAsync(
        FlowContext c, string operation, string document, JObject variables, string root, CancellationToken ct,
        string url)
    {
        if (variables?["token"] is null || string.IsNullOrEmpty(variables["token"]!.ToString()))
            return (null, operation + ": no token — the query is keyed by the buyer token");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url, Envelope(operation, document, variables), "paypal-checkout", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, operation + ": no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, operation + ": " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var session = reply["data"]?[root] as JObject ?? reply["data"] as JObject;
            return session is null ? (null, operation + ": no session in reply") : (session, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, operation + ": " + ex.GetType().Name);
        }
    }
}
'''.replace('__PAY_WITH__', escape_literal(documents['pay_with'])) \
   .replace('__SHIP_TO__', escape_literal(documents['ship_to']))

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s (%d bytes)' % (OUT, len(source)))
