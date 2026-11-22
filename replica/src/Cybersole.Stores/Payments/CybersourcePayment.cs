using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Cybersource's payment creation, as this image builds it.
///
/// <para>
/// <b>Observed</b> (R1371): the request handler <c>sub_140E55A00</c> composes <c>customFields</c> from
/// <c>isv_payment_data</c>, <c>isv_store</c>, <c>isv_screenHeight</c>, <c>isv_screenWidth</c> and
/// <c>isv_customerIpAddress</c>, with <c>centAmount</c> and <c>currencyCode</c> beside them, and names
/// <c>cybersource</c> and <c>creditCardWithPayerAuthentication</c>. Its refusal is "No capture context".
/// The reply handler <c>sub_140E51E20</c> reads <c>isv_tokenCaptureContextSignature</c> out of <c>data</c> and
/// carries "Error processing payment".
/// </para>
///
/// <para>
/// <b>Not observed:</b> a host. Neither handler names one, so the endpoint is the merchant's own and comes from the
/// caller — the same rule every family without a host follows here.
/// </para>
/// </summary>
public static class CybersourcePayment
{
    /// <summary>The operation name.</summary>
    public const string OperationName = "createMyPayment";

    /// <summary>The document, 493 characters from 0x1470E... (see .block_a_docs.json: create_my_payment).</summary>
    public const string Document =
        "mutation createMyPayment($amount: MoneyInput!, $paymentMethod: String!, $paymentInterface: String!, $key: String!, $customFields: [CustomFieldInput!]) {\n  createMyPayment(\n    draft: {amountPlanned: $amount, paymentMethodInfo: {method: $paymentMethod, paymentInterface: $paymentInterface}, custom: {type: {key: $key}, fields: $customFields}}\n  ) {\n    id\n    version\n    paymentMethodInfo {\n      method\n    }\n    custom {\n      customFieldsRaw {\n        name\n        value\n      }\n    }\n  }\n}";

    /// <summary>
    /// updateMyPaymentWithActions, 401 characters from 0x1470FD05C — the same family's update, sent by the handler
    /// at 0x140E55A00 that R1364 read. Declares $actions, $id, $version.
    /// </summary>
    public const string UpdatePaymentDocument = @"mutation updateMyPaymentWithActions($version: Long!, $id: String!, $actions: [MyPaymentUpdateAction!]!) {
  updateMyPayment(version: $version, actions: $actions, id: $id) {
    id
    version
    amountPlanned {
      currencyCode
      centAmount
      fractionDigits
    }
    paymentMethodInfo {
      method
    }
    custom {
      customFieldsRaw {
        name
        value
      }
    }
  }
}";

    /// <summary>The provider name the handler carries.</summary>
    public const string ProviderName = "cybersource";

    /// <summary>The payment method the handler names.</summary>
    public const string PayerAuthenticationMethod = "creditCardWithPayerAuthentication";

    /// <summary>The custom-field keys, in the order the handler names them.</summary>
    public static readonly string[] CustomFieldNames =
    {
        "isv_payment_data", "isv_store", "isv_screenHeight", "isv_screenWidth", "isv_customerIpAddress",
    };

    /// <summary>The handler's words when the capture context is missing.</summary>
    public const string NoCaptureContextMessage = "No capture context";

    /// <summary>The reply handler's words when the provider refuses.</summary>
    public const string ErrorProcessingPaymentMessage = "Error processing payment";

    /// <summary>The reply key the capture context signature arrives in.</summary>
    public const string CaptureContextSignatureKey = "isv_tokenCaptureContextSignature";

    /// <summary>
    /// Build the custom fields from what a run knows: the payment data blob, the store name, the two screen
    /// dimensions and the customer's address. Empty values are dropped rather than sent as blanks, because the
    /// provider reads a present-but-empty field differently from an absent one.
    /// </summary>
    public static JObject BuildCustomFields(
        string? paymentData, string? store, int screenHeight, int screenWidth, string? customerIpAddress)
    {
        var fields = new JObject();
        if (!string.IsNullOrEmpty(paymentData)) fields["isv_payment_data"] = paymentData;
        if (!string.IsNullOrEmpty(store)) fields["isv_store"] = store;
        if (screenHeight > 0) fields["isv_screenHeight"] = screenHeight;
        if (screenWidth > 0) fields["isv_screenWidth"] = screenWidth;
        if (!string.IsNullOrEmpty(customerIpAddress)) fields["isv_customerIpAddress"] = customerIpAddress;
        return fields;
    }

    /// <summary>The request body.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Create the payment. Without a capture context the handler refuses, so this refuses too rather than sending a
    /// request the provider would answer with an authorisation error.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> CreateAsync(
        FlowContext c, string? endpoint, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(endpoint))
            return (null, "cybersource: no endpoint — the merchant host is the caller's");

        var signature = variables?["captureContext"]?.ToString()
                        ?? variables?["customFields"]?["isv_payment_data"]?.ToString();
        if (string.IsNullOrEmpty(signature)) return (null, NoCaptureContextMessage);

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, endpoint!.TrimEnd('/'), Envelope(variables!), "cybersource", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, ErrorProcessingPaymentMessage);

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, ErrorProcessingPaymentMessage);

            var data = reply["data"] as JObject;
            return data is null ? (null, ErrorProcessingPaymentMessage) : (data, string.Empty);
        }
        catch (Exception)
        {
            return (null, ErrorProcessingPaymentMessage);
        }
    }

    /// <summary>
    /// Send the update. Same endpoint rule as the create: the merchant host is the caller's, and a payment without a
    /// capture context is refused before it leaves.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> UpdateAsync(
        FlowContext c, string? endpoint, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(endpoint))
            return (null, "cybersource: no endpoint — the merchant host is the caller's");

        if (variables?["customFields"]?["isv_payment_data"] is null)
            return (null, NoCaptureContextMessage);

        try
        {
            var body = new JObject
            {
                ["operationName"] = "updateMyPaymentWithActions",
                ["query"] = UpdatePaymentDocument,
                ["variables"] = variables,
            };

            var reply = await GatewayHttp
                .PostAsync(c, endpoint!.TrimEnd('/'), body, "cybersource-update", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, ErrorProcessingPaymentMessage);

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, ErrorProcessingPaymentMessage);

            var data = reply["data"] as JObject;
            return data is null ? (null, ErrorProcessingPaymentMessage) : (data, string.Empty);
        }
        catch (Exception)
        {
            return (null, ErrorProcessingPaymentMessage);
        }
    }
}
