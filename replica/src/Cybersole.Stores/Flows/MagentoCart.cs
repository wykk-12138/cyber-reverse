using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The Magento cart documents the image carries, and the two calls they make.
///
/// <para>
/// <b>Observed</b>, all three read out byte for byte (UTF-16 in the image, decoded by
/// <c>analysis/read_magento_cart.py</c>):
/// <c>mutation { addProductsToCart(cartId: "%CART_ID%", cartItems: [{ quantity: %QTY%, sku: "%SKU%" }])
/// { cart { id items { id quantity } total_quantity prices { grand_total { value currency } } }
/// user_errors { code message } } }</c> at 0x1470FD624 (240 characters);
/// <c>mutation { createEmptyCart }</c> at 0x1470FD4C4 (32); and
/// <c>{ customerCart { id total_quantity items { uid quantity } } }</c> at 0x14718FB74 (61).
/// The first one carries <c>%CART_ID%</c>, <c>%QTY%</c> and <c>%SKU%</c> as literal substitution tokens,
/// which is how the image fills it in rather than using GraphQL variables.
/// </para>
///
/// <para>
/// <b>Inference</b>: that a store reaches these through the same <c>/graphql</c> endpoint the product query
/// uses. That is how Magento serves them, and the product query in <see cref="CasioGraphQL"/> is a Magento
/// document, but no literal in the image pairs the two.
/// </para>
/// </summary>
public static class MagentoCart
{
    /// <summary>The add-to-cart mutation, with its three substitution tokens left in place.</summary>
    public const string AddProductsDocument =
        "mutation {\r\n  addProductsToCart(cartId: \"%CART_ID%\", cartItems: [{ quantity: %QTY%, sku: \"%SKU%\" }]) {\r\n" +
        "    cart { id items { id quantity } total_quantity prices { grand_total { value currency } } }\r\n" +
        "    user_errors { code message }\r\n  }\r\n}";

    /// <summary>The empty-cart mutation.</summary>
    public const string CreateEmptyCartDocument = "mutation {\n    createEmptyCart\n}";

    /// <summary>
    /// R1322: attach a payment to the cart, 236 characters from 0x1470E87CC. The same <c>updateMyCart</c>
    /// family as the billing mutation — one action, <c>addPayment</c> — and the same required
    /// <c>$version</c>, answering <c>id</c>, <c>version</c> and <c>isAbleToCheckout</c>.
    /// </summary>
    public const string AddPaymentDocument =
        "mutation addPaymentToCart($id: String!, $version: Long!, $paymentId: String!) {\n  updateMyCart(\n" +
        "    actions: {addPayment: {payment: {id: $paymentId}}}\n    version: $version\n    id: $id\n  ) {\n" +
        "    id\n    version\n    isAbleToCheckout\n  }\n}";

    /// <summary>
    /// R1322: submit the order, 141 characters from 0x1470E1E7C. It takes a <b>cart token</b>, not the cart
    /// id, and answers <c>id</c>, <c>customerId</c> and <c>orderNumber</c> — the order number being the only
    /// thing a run log should be judged on.
    /// </summary>
    public const string SubmitOrderDocument =
        "mutation SubmitOrder($cartToken: String!) {\n  submitOrder(cartToken: $cartToken) {\n" +
        "    id\n    customerId\n    orderNumber\n    __typename\n  }\n}";

    /// <summary>The customer-cart query.</summary>
    public const string CustomerCartDocument = "{ customerCart { id total_quantity items { uid quantity } } }";

    /// <summary>
    /// R1321: the billing-address mutation, 323 characters from 0x1470E4F94. It is Magento's
    /// <c>updateMyCart</c> with two actions — set the billing address, set the customer email — and it
    /// answers <c>id</c>, <c>version</c> and <c>isAbleToCheckout</c>. Unlike the add mutation it uses
    /// GraphQL variables rather than substitution tokens, and it needs the cart's <c>version</c>, which is
    /// why the flow has to carry one.
    /// </summary>
    public const string AddBillingAddressDocument =
        "mutation addBillingAddressToCart($cartId: String!, $version: Long!, $address: AddressInput!, " +
        "$emailAddress: String) {\n  updateMyCart(\n    actions: [{setBillingAddress: {address: $address}}, " +
        "{setCustomerEmail: {email: $emailAddress}}]\n    version: $version\n    id: $cartId\n  ) {\n" +
        "    id\n    version\n    isAbleToCheckout\n  }\n}";


    /// <summary>The three tokens the add mutation substitutes.</summary>
    public static readonly string[] Placeholders = { "%CART_ID%", "%QTY%", "%SKU%" };

    /// <summary>
    /// The document with its tokens replaced. The tokens are substituted as text, not through GraphQL
    /// variables, because that is what the image's document is written for.
    /// </summary>
    public static string FillAddProducts(string cartId, string sku, int quantity)
    {
        if (string.IsNullOrEmpty(cartId)) throw new ArgumentException("cart id is required", nameof(cartId));

        return AddProductsDocument
            .Replace("%CART_ID%", Escape(cartId), StringComparison.Ordinal)
            .Replace("%SKU%", Escape(sku ?? string.Empty), StringComparison.Ordinal)
            .Replace("%QTY%", quantity.ToString(System.Globalization.CultureInfo.InvariantCulture),
                StringComparison.Ordinal);
    }

    /// <summary>A GraphQL request body: the document under <c>query</c>.</summary>
    public static JObject Body(string document) => new() { ["query"] = document };

    /// <summary>
    /// Create a cart and return its id, or null when the reply carries none. Magento answers
    /// <c>{"data":{"createEmptyCart":"&lt;masked id&gt;"}}</c>.
    /// </summary>
    public static async Task<string?> CreateEmptyAsync(FlowContext c, string endpoint, CancellationToken ct)
    {
        var reply = await PostAsync(c, endpoint, Body(CreateEmptyCartDocument), ct).ConfigureAwait(false);
        return reply?["data"]?["createEmptyCart"]?.ToString();
    }

    /// <summary>
    /// Add a line and return the cart id the mutation answered with, or null. <c>user_errors</c> is checked
    /// first: Magento reports a rejected line there while still answering 200, so a caller that only looked
    /// at the HTTP status would treat a failure as success.
    /// </summary>
    public static async Task<MagentoCartResult> AddProductAsync(
        FlowContext c, string endpoint, string cartId, string sku, int quantity, CancellationToken ct)
    {
        var reply = await PostAsync(c, endpoint, Body(FillAddProducts(cartId, sku, quantity)), ct)
            .ConfigureAwait(false);

        if (reply is null) return MagentoCartResult.Fail("cart: no reply");

        var errors = reply["data"]?["addProductsToCart"]?["user_errors"] as JArray;
        if (errors is { Count: > 0 })
        {
            var first = errors[0];
            return MagentoCartResult.Fail("cart: " + (first["message"]?.ToString() ?? first["code"]?.ToString() ?? "rejected"));
        }

        if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
            return MagentoCartResult.Fail("cart: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

        var cart = reply["data"]?["addProductsToCart"]?["cart"];
        if (cart is null) return MagentoCartResult.Fail("cart: no cart in reply");

        return new MagentoCartResult
        {
            Ok = true,
            CartId = cart["id"]?.ToString() ?? cartId,
            TotalQuantity = cart["total_quantity"]?.ToString() ?? string.Empty,
            GrandTotal = cart["prices"]?["grand_total"]?["value"]?.ToString() ?? string.Empty,
            Currency = cart["prices"]?["grand_total"]?["currency"]?.ToString() ?? string.Empty,
        };
    }

    /// <summary>
    /// Set the billing address and customer email, returning the cart's new version and whether it can now
    /// check out. The version is an argument because the document requires one and the add mutation does not
    /// return it — a caller that has never seen a version has nothing to pass, and guessing 0 or 1 would be a
    /// fabricated number in a request the store validates.
    /// </summary>
    public static async Task<MagentoBillingResult> SetBillingAsync(
        FlowContext c,
        string endpoint,
        string cartId,
        long version,
        JObject address,
        string email,
        CancellationToken ct)
    {
        var body = new JObject
        {
            ["query"] = AddBillingAddressDocument,
            ["variables"] = new JObject
            {
                ["cartId"] = cartId,
                ["version"] = version,
                ["address"] = address,
                ["emailAddress"] = email,
            },
        };

        var reply = await PostAsync(c, endpoint, body, ct).ConfigureAwait(false);
        if (reply is null) return MagentoBillingResult.Fail("billing: no reply");

        if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
            return MagentoBillingResult.Fail("billing: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

        var cart = reply["data"]?["updateMyCart"];
        if (cart is null) return MagentoBillingResult.Fail("billing: no cart in reply");

        // Magento answers a JSON boolean, and JToken.ToString() renders it "True"; the session carries strings
        // that other steps compare, so it is normalised here rather than at every reader.
        var canCheckout = cart["isAbleToCheckout"];
        var canCheckoutText = canCheckout is null
            ? string.Empty
            : canCheckout.Type == JTokenType.Boolean
                ? (canCheckout.Value<bool>() ? "true" : "false")
                : canCheckout.ToString();

        return new MagentoBillingResult
        {
            Ok = true,
            CartId = cart["id"]?.ToString() ?? cartId,
            Version = cart["version"]?.ToString() ?? version.ToString(System.Globalization.CultureInfo.InvariantCulture),
            CanCheckout = canCheckoutText,
        };
    }

    /// <summary>
    /// Attach a payment id to the cart. Same shape as <see cref="SetBillingAsync"/> and the same reason for
    /// taking the version as an argument rather than working it out.
    /// </summary>
    public static async Task<MagentoBillingResult> AddPaymentAsync(
        FlowContext c, string endpoint, string cartId, long version, string paymentId, CancellationToken ct)
    {
        var body = new JObject
        {
            ["query"] = AddPaymentDocument,
            ["variables"] = new JObject
            {
                ["id"] = cartId,
                ["version"] = version,
                ["paymentId"] = paymentId,
            },
        };

        return await UpdateMyCartAsync(c, endpoint, body, cartId, version, "payment", ct).ConfigureAwait(false);
    }

    /// <summary>
    /// Submit the order and return its number. Null when the reply carries none, which is the answer for a
    /// rejected submission — <c>submitOrder</c> reports refusal in the GraphQL error list.
    /// </summary>
    public static async Task<MagentoOrderResult> SubmitOrderAsync(
        FlowContext c, string endpoint, string cartToken, CancellationToken ct)
    {
        var body = new JObject
        {
            ["query"] = SubmitOrderDocument,
            ["variables"] = new JObject { ["cartToken"] = cartToken },
        };

        var reply = await PostAsync(c, endpoint, body, ct).ConfigureAwait(false);
        if (reply is null) return MagentoOrderResult.Fail("order: no reply");

        if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
            return MagentoOrderResult.Fail("order: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

        var order = reply["data"]?["submitOrder"];
        if (order is null) return MagentoOrderResult.Fail("order: no order in reply");

        var number = order["orderNumber"]?.ToString();
        if (string.IsNullOrEmpty(number)) return MagentoOrderResult.Fail("order: no order number in reply");

        return new MagentoOrderResult
        {
            Ok = true,
            OrderNumber = number!,
            OrderId = order["id"]?.ToString() ?? string.Empty,
            CustomerId = order["customerId"]?.ToString() ?? string.Empty,
        };
    }

    /// <summary>The shared tail of the two <c>updateMyCart</c> mutations: read the cart or the GraphQL errors.</summary>
    private static async Task<MagentoBillingResult> UpdateMyCartAsync(
        FlowContext c, string endpoint, JObject body, string cartId, long version, string what, CancellationToken ct)
    {
        var reply = await PostAsync(c, endpoint, body, ct).ConfigureAwait(false);
        if (reply is null) return MagentoBillingResult.Fail(what + ": no reply");

        if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
            return MagentoBillingResult.Fail(what + ": " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

        var cart = reply["data"]?["updateMyCart"];
        if (cart is null) return MagentoBillingResult.Fail(what + ": no cart in reply");

        var canCheckout = cart["isAbleToCheckout"];
        var canCheckoutText = canCheckout is null
            ? string.Empty
            : canCheckout.Type == JTokenType.Boolean
                ? (canCheckout.Value<bool>() ? "true" : "false")
                : canCheckout.ToString();

        return new MagentoBillingResult
        {
            Ok = true,
            CartId = cart["id"]?.ToString() ?? cartId,
            Version = cart["version"]?.ToString() ?? version.ToString(System.Globalization.CultureInfo.InvariantCulture),
            CanCheckout = canCheckoutText,
        };
    }

    /// <summary>
    /// Read the customer cart — the 61-character <see cref="CustomerCartDocument"/> the image carries at
    /// 0x14718FB74. R1329: the constant had no caller from R1320 until this, which made it a document the
    /// replica could not actually send.
    /// </summary>
    public static async Task<MagentoCartResult> ReadCartAsync(
        FlowContext c, string endpoint, CancellationToken ct)
    {
        var reply = await PostAsync(c, endpoint, Body(CustomerCartDocument), ct).ConfigureAwait(false);
        if (reply is null) return MagentoCartResult.Fail("cart: no reply");

        if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
            return MagentoCartResult.Fail("cart: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

        var customerCart = reply["data"]?["customerCart"];
        if (customerCart is null)
            return MagentoCartResult.Fail("cart: no customerCart in reply — this store may key carts by masked id");

        return new MagentoCartResult
        {
            Ok = true,
            CartId = customerCart["id"]?.ToString() ?? string.Empty,
            TotalQuantity = customerCart["total_quantity"]?.ToString() ?? string.Empty,
        };
    }

    private static async Task<JObject?> PostAsync(FlowContext c, string endpoint, JObject body, CancellationToken ct)
    {
        try
        {
            var res = await c.Http
                .PostJsonAsync(endpoint, body.ToString(Newtonsoft.Json.Formatting.None), c.Options("magento-cart"), ct)
                .ConfigureAwait(false);
            c.Session.AbsorbCookies(res.Cookies);
            if (!res.IsSuccess) return null;
            return JObject.Parse(res.Body);
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static string Escape(string value) =>
        value.Replace("\\", "\\\\", StringComparison.Ordinal).Replace("\"", "\\\"", StringComparison.Ordinal);
}

/// <summary>What an order submission produced.</summary>
public sealed class MagentoOrderResult
{
    public bool Ok { get; init; }
    public string OrderNumber { get; init; } = string.Empty;
    public string OrderId { get; init; } = string.Empty;
    public string CustomerId { get; init; } = string.Empty;
    public string Error { get; init; } = string.Empty;

    public static MagentoOrderResult Fail(string error) => new() { Ok = false, Error = error };
}

/// <summary>What the billing mutation produced.</summary>
public sealed class MagentoBillingResult
{
    public bool Ok { get; init; }
    public string CartId { get; init; } = string.Empty;
    public string Version { get; init; } = string.Empty;
    public string CanCheckout { get; init; } = string.Empty;
    public string Error { get; init; } = string.Empty;

    public static MagentoBillingResult Fail(string error) => new() { Ok = false, Error = error };
}

/// <summary>What an add-to-cart mutation produced.</summary>
public sealed class MagentoCartResult
{
    public bool Ok { get; init; }
    public string CartId { get; init; } = string.Empty;
    public string TotalQuantity { get; init; } = string.Empty;
    public string GrandTotal { get; init; } = string.Empty;
    public string Currency { get; init; } = string.Empty;
    public string Error { get; init; } = string.Empty;

    public static MagentoCartResult Fail(string error) => new() { Ok = false, Error = error };
}
