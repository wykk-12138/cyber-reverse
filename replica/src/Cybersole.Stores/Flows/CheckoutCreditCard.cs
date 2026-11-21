using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The card submission that finalises an order — <c>CreditCard</c>.
///
/// <para>
/// <b>Observed</b> (R1368): <c>sub_140AAE300</c> builds <c>api/checkout/v1/orders/</c> plus the order id plus
/// <c>/finalize</c>, with the card fields <c>cardNumber</c>, <c>cardCvv</c>, <c>cardExpiryMonth</c>,
/// <c>cardExpiryYear</c>, <c>cardName</c> and the label "Submit order". The path is relative, so the origin is the
/// caller's and the order id is a path segment rather than a variable in the document.
/// </para>
///
/// <para>
/// <b>Recorded, not implemented:</b> a second handler carries <c>https://www.nike.com/nl/checkout/confirmation?cid=</c>
/// with "Submit payment" and the SHIP/ASTLA tokens — the Nike variant, which belongs with that store's own steps
/// rather than with this generic path.
/// </para>
/// </summary>
public static class CheckoutCreditCard
{
    /// <summary>The operation name.</summary>
    public const string OperationName = "CreditCard";

    /// <summary>The relative path prefix the sender builds.</summary>
    public const string OrderPathPrefix = "api/checkout/v1/orders/";

    /// <summary>The suffix the sender appends after the order id.</summary>
    public const string FinalizeSuffix = "/finalize";

    /// <summary>The document, 2867 characters from 0x1470CF934.</summary>
    public const string Document =
        "mutation CreditCard($input: CreditCardInput!) {\n  creditCard(input: $input) {\n    orderNo\n    status\n    ...orderConfirmationFields\n    subTotal\n    orderAdjustments {\n      promotionId\n      itemText\n      price\n      couponCode\n      __typename\n    }\n    shippingAdjustments {\n      promotionId\n      itemText\n      price\n      couponCode\n      __typename\n    }\n    orderNo\n    taxTotal\n    estimatedTotal\n    status\n    products {\n      ...productCartItemFields\n      __typename\n    }\n    ...orderPaymentInstrumentFields\n    __typename\n  }\n}\n\nfragment orderConfirmationFields on BaseOrder {\n  billingAddress {\n    id\n    firstName\n    lastName\n    address1\n    address2\n    postalCode\n    city\n    countryCode\n    stateCode\n    __typename\n  }\n  shipment {\n    id\n    shipmentMethod {\n      id\n      name\n      price\n      __typename\n    }\n    address {\n      id\n      firstName\n      lastName\n      address1\n      address2\n      postalCode\n      city\n      countryCode\n      stateCode\n      phone\n      __typename\n    }\n    __typename\n  }\n  customer {\n    email\n    id\n    __typename\n  }\n}\n\nfragment orderPaymentInstrumentFields on BaseOrder {\n  paymentInstruments {\n    ... on AmbassadorCard {\n      id\n      __typename\n      authorizationStatus\n      maskedNumber\n      amount\n    }\n    ... on CreditCard {\n      id\n      amount\n      maskedNumber\n      cardType\n      authorizationStatus\n      __typename\n    }\n    ... on AfterPay {\n      id\n      authorizationStatus\n      __typename\n    }\n    ... on ApplePay {\n      id\n      authorizationStatus\n      __typename\n    }\n    ... on PayPal {\n      id\n      authorizationStatus\n      __typename\n    }\n    ... on GiftCard {\n      id\n      __typename\n      maskedNumber\n      authorizationStatus\n      amount\n    }\n    ... on CashOnDelivery {\n      id\n      __typename\n      amount\n    }\n    ... on UPI {\n      id\n      __typename\n    }\n    ... on Wallet {\n      id\n      authorizationStatus\n      __typename\n    }\n    ... on OnlineBanking {\n      id\n      authorizationStatus\n      __typename\n    }\n    ... on PayTm {\n      id\n      authorizationStatus\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment productCartItemFields on CartItem {\n  ... on GiftCardCartItem {\n    id\n    imageUrl\n    amount\n    recipientEmail\n    recipientName\n    senderName\n    __typename\n  }\n  ... on ProductCartItem {\n    __typename\n    id\n    adjustments {\n      promotionId\n      itemText\n      price\n      couponCode\n      __typename\n    }\n    bonusItemId\n    restricted\n    quantity\n    product {\n      masterId\n      id\n      name\n      price\n      salePrice\n      images {\n        href\n        alt\n        __typename\n      }\n      inventory\n      primaryCategoryId\n      styleNumber\n      colorValue\n      colorName\n      size {\n        name\n        value\n        __typename\n      }\n      offline\n      __typename\n    }\n  }\n}\n";

    /// <summary>The card fields the handler names.</summary>
    public static readonly string[] CardFields =
    {
        "cardNumber", "cardCvv", "cardExpiryMonth", "cardExpiryYear", "cardName",
    };

    /// <summary>The handler's words for this step.</summary>
    public const string SubmitOrderMessage = "Submit order";

    /// <summary>The url for one order: origin + the relative path + the id + the suffix.</summary>
    public static string UrlFor(string origin, string orderId) =>
        origin.TrimEnd('/') + "/" + OrderPathPrefix + orderId + FinalizeSuffix;

    /// <summary>The request body.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Submit the card. The card object is the caller's; nothing about a card belongs in source.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> SubmitAsync(
        FlowContext c, string? origin, string? orderId, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(origin)) return (null, "checkout-card: no origin");
        if (string.IsNullOrWhiteSpace(orderId))
            return (null, "checkout-card: no order id — it is a path segment, not a variable");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, UrlFor(origin!, orderId!), Envelope(variables ?? new JObject()),
                    "checkout-card", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, SubmitOrderMessage);

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, topLevel[0]?["message"]?.ToString() ?? SubmitOrderMessage);

            var data = reply["data"] as JObject ?? reply;
            return (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "checkout-card: " + ex.GetType().Name);
        }
    }
}
