"""R1336: CurrencyConversion lands, and the image spells one of its variables wrong.

Same method as R1335, and it works again: the 10406-character document at 0x1470D0FB4 has one code reference,
0x14110FB42 inside sub_14110F8C0 (1173 bytes), and that sender hands over the request:

    0x147097E78  len=31  "https://www.paypal.com/graphql/"   <- same base as the approval
    0x146BAAEC8  len=18  "CurrencyConversion"
    0x147109320          "operationName"
    0x14711CCB0          "query"
    0x14717D2E8          "variables"
    0x146F76688          "application/json"
    0x147171D48  len=5   "token"
    0x146FD6F98  len=14  "conversionType"
    0x1470210A8  len=11  "expeirences"      <- sic, the image's own spelling
    0x146F1AF90  len=6   "VENDOR"

The document declares $conversionType, $experiences and $token. The sender writes the middle key as
`expeirences`. That is not a typo to fix: it is the request the image sends, and correcting it would be a
behaviour change dressed as housekeeping. It is pinned by a test with the reason beside it.

Usage: python analysis/add_partner_currency.py
"""
import io
import json

DOCS = 'analysis/.paypal_onboard.json'
OUT = 'replica/src/Cybersole.Stores/Payments/PayPalPartnerCurrency.cs'

document = json.loads(io.open(DOCS, encoding='utf-8').read())['currency_conversion']
literal = document.replace('"', '""')

source = '''using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// The PayPal partner currency conversion — <c>CurrencyConversion</c> — read out of the image.
///
/// <para>
/// <b>Observed</b>, from the sender at <c>sub_14110F8C0</c> (1173 bytes) and the document at 0x1470D0FB4:
/// the base <c>https://www.paypal.com/graphql/</c> (the same one the approval uses), the operation name, the
/// envelope keys, the content type, and the three variable keys the sender writes — <c>token</c>,
/// <c>conversionType</c> and <c>expeirences</c>. That last spelling is the image's: the document declares
/// <c>$experiences</c> and the sender sends <c>expeirences</c>. A faithful replica sends it the same way.
/// </para>
///
/// <para>
/// <b>Observed</b> enum: <c>VENDOR</c> (0x146F1AF90), which belongs to <c>conversionType</c>; the enum's other
/// members are not in this function, so callers may pass their own.
/// </para>
/// </summary>
public static class PayPalPartnerCurrency
{
    /// <summary>The shared partner base URL, from 0x147097E78. Same string the approval uses.</summary>
    public const string BaseUrl = PayPalPartnerApprove.BaseUrl;

    /// <summary>The operation name the image sends, from 0x146BAAEC8.</summary>
    public const string OperationName = "CurrencyConversion";

    /// <summary>The endpoint: base plus operation name.</summary>
    public const string Url = BaseUrl + OperationName;

    /// <summary>The document, 10406 characters from 0x1470D0FB4.</summary>
    public const string Document = @"__DOCUMENT__";

    /// <summary>
    /// The three variable keys the sender writes, in its own spelling — including <c>expeirences</c>, which the
    /// document calls <c>$experiences</c>. Asserting that pairing is what stops a future edit from "fixing" it.
    /// </summary>
    public static readonly string[] VariableNames = { "token", "conversionType", "expeirences" };

    /// <summary>The conversion type the sender names, from 0x146F1AF90.</summary>
    public const string ConversionTypeVendor = "VENDOR";

    /// <summary>The request body: the envelope the sender builds.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Ask for the conversion. Returns the <c>updateCurrencyConversionType</c> node, whose first useful child is
    /// <c>fundingOptions</c> with the converted amounts, or null with the reason in <paramref name="error"/>.
    /// </summary>
    public static async Task<(JObject? Conversion, string Error)> ConvertAsync(
        FlowContext c, JObject variables, CancellationToken ct, string? url = null)
    {
        if (variables?["token"] is null || string.IsNullOrEmpty(variables["token"]!.ToString()))
            return (null, "currency: no token — the conversion is keyed by the buyer token");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url ?? Url, Envelope(variables), "paypal-currency", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "currency: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "currency: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var conversion = reply["data"]?["updateCurrencyConversionType"] as JObject;
            return conversion is null ? (null, "currency: no conversion in reply") : (conversion, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "currency: " + ex.GetType().Name);
        }
    }
}
'''.replace('__DOCUMENT__', literal)

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s with a %d-character document' % (OUT, len(document)))
