using System.Text.Json;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The Shopify Storefront GraphQL surface, read out of the 5.18.32 image in R97.
///
/// <para>
/// The replica had <b>no GraphQL path at all</b> — it used <c>cart/add.js</c> + <c>cart.js</c> only.
/// The image carries two complete GraphQL documents and four API versions, so the original can drive
/// a storefront through GraphQL when a store hands it a token.
/// </para>
///
/// <para>
/// The two documents below are the image's own text, character for character. The query fragment
/// starts mid-document (the pool stores it without its operation header), so
/// <see cref="CartQueryDocument"/> supplies the header and keeps the fragment verbatim.
/// </para>
/// </summary>
public static class ShopifyGraphQl
{
    /// <summary>Every <c>api/&lt;version&gt;/graphql.json</c> the image names.</summary>
    public static readonly IReadOnlyList<string> ApiVersions = new[]
    {
        "2020-04", "2021-10", "2024-10", "2025-04",
    };

    /// <summary>
    /// The cart selection set, verbatim from the image (354 characters). It is a fragment — the pool
    /// stores it without its operation header — and it is the shape a cart read must return:
    /// <c>checkoutUrl</c>, totals, and up to 250 lines with variant availability.
    /// </summary>
    public const string CartSelection =
        "\"){id,checkoutUrl,totalQuantity,cost{subtotalAmount{amount,currencyCode}},lines(first:250){nodes{__typename,id,quantity,cost{amountPerQuantity{amount,currencyCode},compareAtAmountPerQuantity{amount,currencyCode}},merchandise{__typename,... on ProductVariant{id,availableForSale,quantityAvailable,title,image{id,altText,url},product{id,title,handle}}}}}}}";

    /// <summary>The mutation that changes line quantities, verbatim from the image.</summary>
    public const string CartLinesUpdate =
        "mutation { cartLinesUpdate(cartId: $cartId, lines: $lines) { cart { checkoutUrl, lines(first:250){nodes{__typename,id,quantity,cost{amountPerQuantity{amount,currencyCode},compareAtAmountPerQuantity{amount,currencyCode}},merchandise{__typename,... on ProductVariant{id,availableForSale,title,image{id,altText,url},product{id,title,handle}}}}} } }}";

    /// <summary>
    /// The cart query as a complete document: the image's fragment with the operation header the pool
    /// strips. <paramref name="query"/> is a <c>cart(id: $cartId)</c> or <c>cart(cartId: …)</c> call.
    /// </summary>
    public static string CartQueryDocument(string query) => query + CartSelection;

    /// <summary>
    /// <c>https://{host}/api/{version}/graphql.json</c> — the shape the image's four literals imply.
    /// </summary>
    public static string Endpoint(string host, string apiVersion = "2025-04") =>
        $"https://{host}/api/{apiVersion}/graphql.json";

    /// <summary>The internal checkout endpoint the image also names.</summary>
    public const string InternalCheckout = "/checkouts/internal/graphql";

    /// <summary>The response key the image's own literals use: <c>"checkoutUrl":"</c>.</summary>
    public const string CheckoutUrlKey = "checkoutUrl";

    /// <summary>
    /// Pulls <c>checkoutUrl</c> out of a Storefront response. Returns null when the document has no
    /// checkout URL, which is what happens before a cart has a delivery address.
    /// </summary>
    public static string? ParseCheckoutUrl(string? json)
    {
        if (string.IsNullOrWhiteSpace(json)) return null;

        try
        {
            using var doc = JsonDocument.Parse(json);
            return Find(doc.RootElement, CheckoutUrlKey, 0);
        }
        catch (JsonException)
        {
            return null;
        }
    }

    /// <summary>
    /// Depth-first search for a string property. The Storefront response nests the cart under
    /// <c>data</c> and the mutation under <c>cartLinesUpdate.cart</c>, so a fixed path would be wrong
    /// for at least one of them.
    /// </summary>
    private static string? Find(JsonElement element, string name, int depth)
    {
        if (depth > 12) return null;

        switch (element.ValueKind)
        {
            case JsonValueKind.Object:
                foreach (var property in element.EnumerateObject())
                {
                    if (property.NameEquals(name) && property.Value.ValueKind == JsonValueKind.String)
                    {
                        var value = property.Value.GetString();
                        if (!string.IsNullOrWhiteSpace(value)) return value;
                    }

                    var nested = Find(property.Value, name, depth + 1);
                    if (nested is not null) return nested;
                }

                break;

            case JsonValueKind.Array:
                foreach (var item in element.EnumerateArray())
                {
                    var nested = Find(item, name, depth + 1);
                    if (nested is not null) return nested;
                }

                break;
        }

        return null;
    }
}
