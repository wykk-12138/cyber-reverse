using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The Shopify product-drops app query — <c>getProductDetails</c>.
///
/// <para>
/// <b>Observed</b> (R1351): the sender at <c>sub_140C81880</c> (1010 bytes) builds the relative path
/// <c>apps/product-drops?kind=mutation&amp;operation=getProductDetails</c> — the operation travels as a query
/// parameter, and the only document variable is <c>$handle</c>. The document is 499 characters at 0x1470F43C4.
/// </para>
///
/// <para>
/// <b>Inference:</b> that the parameter name <c>kind</c> means the same thing here as in the partner family, where
/// its values are operational words. Nothing in this sender sets it to anything but <c>mutation</c>, so no other
/// value is offered here.
/// </para>
/// </summary>
public static class ShopifyProductDrops
{
    /// <summary>The relative path the sender builds, including its query string.</summary>
    public const string Path = "apps/product-drops?kind=mutation&operation=getProductDetails";

    /// <summary>The operation name, which also appears inside <see cref="Path"/>.</summary>
    public const string OperationName = "getProductDetails";

    /// <summary>The document, 499 characters from 0x1470F43C4.</summary>
    public const string Document =
        "mutation getProductDetails($handle: String) {\n  storefront {\n    getProductDetails(handle: $handle) {\n      success\n      errors {\n        message\n        code\n        ... on InvalidRecordError {\n          model {\n            apiIdentifier\n            __typename\n          }\n          validationErrors {\n            message\n            apiIdentifier\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      result\n      __typename\n    }\n    __typename\n  }\n}";

    /// <summary>The one variable the document declares.</summary>
    public static readonly string[] DeclaredVariables = { "handle" };

    /// <summary>The request body the sender builds.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Ask for a product by handle. <paramref name="origin"/> is the store's, because the path is relative.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> FetchAsync(
        FlowContext c, string? origin, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(origin)) return (null, "product-drops: no origin");
        if (variables?["handle"] is null || string.IsNullOrEmpty(variables["handle"]!.ToString()))
            return (null, "product-drops: no handle — the only variable the document declares");

        var url = origin!.TrimEnd('/') + "/" + Path;
        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url, Envelope(variables), "product-drops", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "product-drops: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "product-drops: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject;
            return data is null ? (null, "product-drops: no data in reply") : (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "product-drops: " + ex.GetType().Name);
        }
    }
}
