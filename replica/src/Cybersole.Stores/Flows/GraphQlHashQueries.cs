using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The family that posts persisted GraphQL queries by hash rather than by document.
///
/// <para>
/// <b>Observed</b> (R1357): <c>sub_14088BB80</c> — the function that references <c>GetCartCookie</c>'s name — names
/// the headers <c>x-graphql-hash</c>, <c>x-graphql-query-name</c> and <c>x-header-id</c>, and holds two 64-hex
/// constants that fit the first of those:
/// <c>83c4b10c…f1950</c> and <c>b6138937…06866</c>. It also carries "Getting session" and "StatusInfo".
/// </para>
///
/// <para>
/// <b>Unknown:</b> which hash belongs to which operation. Two values and three operations do not settle it, so the
/// class takes the hash from the caller and never picks one itself. The documents are still sent when a caller has
/// no hash — a server that accepts persisted queries generally accepts the query too, and sending the wrong hash
/// would be worse than sending none.
/// </para>
/// </summary>
public static class GraphQlHashQueries
{
    /// <summary>The hash header.</summary>
    public const string HashHeader = "x-graphql-hash";

    /// <summary>The query-name header.</summary>
    public const string QueryNameHeader = "x-graphql-query-name";

    /// <summary>The header the same function also names.</summary>
    public const string HeaderIdHeader = "x-header-id";

    /// <summary>The two 64-hex values the handler holds, in the order they appear.</summary>
    public static readonly string[] ObservedHashes =
    {
        "83c4b10c99a6f6c89abf7e84f83d5dc6360f8627eb2b70c7eb4b12590c6f1950",
        "b613893783ae3da73f38b5f93a9a59ccbaa7f131a209cac92634a93d06f06866",
    };

    /// <summary>GetCartCookie, 74 characters from 0x147120B5C.</summary>
    public const string GetCartCookieDocument = "query GetCartCookie {\n  getCartCookie {\n    ctCartJWT\n    __typename\n  }\n}";

    /// <summary>GetProductInventory, 490 characters from 0x147120C0C.</summary>
    public const string GetProductInventoryDocument = "query GetProductInventory($input: ProductInventoryInput!) {\n  productInventory(input: $input) {\n    hasStock\n    inventory {\n      styleColor\n      sizes {\n        name\n        sku\n        stock {\n          store {\n            location\n            stockLevel\n            __typename\n          }\n          web {\n            location\n            stockLevel\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}";

    /// <summary>GetCart, 3520 characters from 0x14711EFC4.</summary>
    public const string GetCartDocument = "query GetCart {\n  getCart {\n    id\n    isUser\n    shippingAddress {\n      firstName\n      lastName\n      email\n      phone\n      __typename\n    }\n    lineItems {\n      name\n      quantity\n      variant {\n        sku\n        prices {\n          ... on CartLineItemVariantPrice {\n            value {\n              centAmount\n              __typename\n            }\n            key\n            __typename\n          }\n          __typename\n        }\n        attributesRaw {\n          ... on CustomFieldRaw {\n            name\n            value\n            __typename\n          }\n          ... on CustomFieldRawArray {\n            name\n            arrayValue: value\n            __typename\n          }\n          ... on CustomFieldRawProduct {\n            name\n            productValue: value {\n              typeId\n              id\n              __typename\n            }\n            __typename\n          }\n          ... on CustomFieldRawBrand {\n            name\n            brandValue: value {\n              key\n              label\n              __typename\n            }\n            __typename\n          }\n          ... on CustomFieldRawKeyLabel {\n            name\n            keyLabel: value {\n              key\n              label\n              __typename\n            }\n            __typename\n          }\n          ... on CustomFieldRawWholesalePrice {\n            name\n            wpValue: value {\n              currencyCode\n              centAmount\n              fractionDigits\n              type\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        parentProduct {\n          referencedResource {\n            id\n            key\n            masterData {\n              current {\n                categories {\n                  id\n                  externalId\n                  name\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      price {\n        key\n        value {\n          centAmount\n          __typename\n        }\n        custom {\n          customFieldsRaw {\n            name\n            value {\n              type\n              currencyCode\n              centAmount\n              fractionDigits\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    couponDiscount {\n      label\n      centAmount\n      __typename\n    }\n    rewardDiscount {\n      label\n      centAmount\n      __typename\n    }\n    promotionalDiscount {\n      label\n      centAmount\n      __typename\n    }\n    totalPrice {\n      centAmount\n      currencyCode\n      fractionDigits\n      type\n      __typename\n    }\n    custom {\n      customFieldsRaw {\n        name\n        value\n        __typename\n      }\n      __typename\n    }\n    shippingInfo {\n      price {\n        centAmount\n        __typename\n      }\n      discountedPrice {\n        value {\n          centAmount\n          __typename\n        }\n        __typename\n      }\n      shippingMethod {\n        id\n        name\n        key\n        __typename\n      }\n      shippingRate {\n        price {\n          centAmount\n          __typename\n        }\n        freeAbove {\n          centAmount\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  getAvailableShippingMethods {\n    freeAbove\n    key\n    __typename\n  }\n}";

    /// <summary>The document for an operation, or null when it is not one of the three.</summary>
    public static string? DocumentFor(string operation) => operation switch
    {
        "GetCartCookie" => GetCartCookieDocument,
        "GetProductInventory" => GetProductInventoryDocument,
        "GetCart" => GetCartDocument,
        _ => null,
    };

    /// <summary>The body: variables always, the query only when there is no hash to identify it.</summary>
    public static JObject Envelope(string operation, JObject variables, bool includeDocument)
    {
        var body = new JObject
        {
            ["operationName"] = operation,
            ["variables"] = variables,
        };
        if (includeDocument) body["query"] = DocumentFor(operation);
        return body;
    }

    /// <summary>
    /// Post one operation. With a hash the query travels as a header and the body carries variables alone; without
    /// one the document is sent, which is the same request in the long form.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> SendAsync(
        FlowContext c, string? origin, string operation, JObject variables, string? hash,
        CancellationToken ct, string? headerId = null)
    {
        if (string.IsNullOrWhiteSpace(origin)) return (null, "graphql-hash: no origin");
        if (DocumentFor(operation) is null) return (null, "graphql-hash: unknown operation " + operation);

        var byHash = !string.IsNullOrWhiteSpace(hash);
        if (byHash)
        {
            c.Session.Headers[HashHeader] = hash!;
            c.Session.Headers[QueryNameHeader] = operation;
            if (!string.IsNullOrEmpty(headerId)) c.Session.Headers[HeaderIdHeader] = headerId!;
        }

        var url = origin!.TrimEnd('/');
        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url, Envelope(operation, variables, !byHash), "graphql-hash", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, operation + ": no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, operation + ": " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject;
            return data is null ? (null, operation + ": no data in reply") : (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, operation + ": " + ex.GetType().Name);
        }
    }
}
