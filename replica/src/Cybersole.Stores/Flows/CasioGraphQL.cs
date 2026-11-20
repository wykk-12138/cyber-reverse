using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Casio's product search, which is a Magento GraphQL document rather than a page to scrape.
///
/// <para>
/// <b>Observed</b>: the image holds the document's field selection as one frozen UTF-16 string
/// (0x146A758CC onwards):
/// <c>sort:{name:ASC},pageSize:40){items{sku name url_key stock_status only_x_left_in_stock
/// casio_sales_type casio_can_purchase casio_sales_start_date casio_sales_end_date casio_image_url
/// image{url label} price_range{minimum_price{final_price{value currency}}}} total_count}}</c>.
/// Three of those fields — <c>casio_sales_type</c>, <c>casio_can_purchase</c>, <c>casio_sales_start_date</c>
/// — exist on no standard Magento type; they are Casio's own sale-window attributes, which is why the
/// store cannot be read like an ordinary catalogue page.
/// </para>
///
/// <para>
/// <b>Unknown</b>: the head of the document. The frozen string starts mid-object, at the <c>]}}</c> that
/// closes a filter and its arguments, so everything before <c>,sort:</c> was not in the captured window.
/// <see cref="SearchDocument"/> therefore composes the smallest wrapper that can carry the observed
/// selection, and says so — the selection is quoted from the image, the wrapper around it is inference.
/// A caller that has the real head should pass it rather than use the composed one.
/// </para>
/// </summary>
public static class CasioGraphQL
{
    /// <summary>The store's GraphQL endpoint, relative to the storefront origin.</summary>
    public const string Path = "/graphql";

    /// <summary>The page size the document asks for.</summary>
    public const int PageSize = 40;

    /// <summary>The sort the document asks for.</summary>
    public const string Sort = "{name:ASC}";

    /// <summary>
    /// The field selection, byte for byte from 0x146A758CC — 274 characters, beginning with the quote that
    /// closes the filter's last value and with the <c>]</c> that closes its array. That leading <c>"]</c> is
    /// itself evidence: the filter carries a list, not a single value, so the head has to open
    /// <c>sku:{in:[</c> rather than <c>sku:{eq:</c> for the braces to balance.
    /// </summary>
    public const string ObservedSelection =
        "\"]}},sort:{name:ASC},pageSize:40){items{sku name url_key stock_status only_x_left_in_stock " +
        "casio_sales_type casio_can_purchase casio_sales_start_date casio_sales_end_date casio_image_url " +
        "image{url label} price_range{minimum_price{final_price{value currency}}}} total_count}}";

    /// <summary>Every field the selection asks for, in the image's order, for anything that has to check.</summary>
    public static IReadOnlyList<string> Fields { get; } = new[]
    {
        "sku", "name", "url_key", "stock_status", "only_x_left_in_stock",
        "casio_sales_type", "casio_can_purchase", "casio_sales_start_date", "casio_sales_end_date",
        "casio_image_url", "image", "price_range", "total_count",
    };

    /// <summary>
    /// The document, wrapped around the observed selection.
    ///
    /// <para>
    /// <b>Inference</b>: the wrapper. <c>products(filter: ...)</c> with a <c>sku</c> equality is the shape
    /// whose closing braces match the tail the image captured, but the head itself was not recovered, so a
    /// caller with better evidence should pass its own document to <see cref="SearchAsync"/>.
    /// </para>
    /// </summary>
    public static string SearchDocument(string skuOrName)
    {
        var escaped = (skuOrName ?? string.Empty)
            .Replace("\\", "\\\\", StringComparison.Ordinal)
            .Replace("\"", "\\\"", StringComparison.Ordinal);

        // The captured tail begins with the quote that closes the filter's value and the bracket that
        // closes its list, so the head opens `sku:{in:[` and the tail completes it.
        return "query{products(filter:{sku:{in:[\"" + escaped + ObservedSelection;
    }

    /// <summary>The request body: a GraphQL POST with the document under <c>query</c>.</summary>
    public static JObject SearchBody(string skuOrName) =>
        new() { ["query"] = SearchDocument(skuOrName) };

    /// <summary>
    /// Ask the store. Returns null when the reply carries no product, which is the ordinary answer for a
    /// sku that is not on sale yet — the caller falls back to reading the page.
    /// </summary>
    public static async Task<CasioProduct?> SearchAsync(
        FlowContext c,
        string skuOrName,
        CancellationToken ct,
        string? path = null,
        string? document = null)
    {
        var target = path ?? Path;
        // A caller may hand in an absolute endpoint (tests do); only a relative path gets the origin.
        var url = target.StartsWith("http", StringComparison.OrdinalIgnoreCase)
            ? target
            : Payments.GatewayHttp.OriginOf(c.Url) + target;
        var body = document is null ? SearchBody(skuOrName) : new JObject { ["query"] = document };

        var reply = await Payments.GatewayHttp
            .PostAsync(c, url, body, "casio-graphql", ct)
            .ConfigureAwait(false);

        return ReadProduct(reply);
    }

    /// <summary>
    /// One product out of a reply, or null when the reply carries none. The three Casio attributes are the
    /// reason this exists: a product can be in stock and still not be on sale, and only these say which.
    /// </summary>
    public static CasioProduct? ReadProduct(JObject? reply)
    {
        var items = reply?["data"]?["products"]?["items"] as JArray;
        if (items is null || items.Count == 0) return null;
        var item = items[0] as JObject;
        if (item is null) return null;

        var price = item["price_range"]?["minimum_price"]?["final_price"];
        return new CasioProduct
        {
            Sku = item["sku"]?.ToString() ?? string.Empty,
            Name = item["name"]?.ToString() ?? string.Empty,
            UrlKey = item["url_key"]?.ToString() ?? string.Empty,
            StockStatus = item["stock_status"]?.ToString() ?? string.Empty,
            OnlyXLeftInStock = item["only_x_left_in_stock"]?.ToString() ?? string.Empty,
            SalesType = item["casio_sales_type"]?.ToString() ?? string.Empty,
            CanPurchase = item["casio_can_purchase"]?.ToString() ?? string.Empty,
            SalesStart = item["casio_sales_start_date"]?.ToString() ?? string.Empty,
            SalesEnd = item["casio_sales_end_date"]?.ToString() ?? string.Empty,
            ImageUrl = item["casio_image_url"]?.ToString() ?? string.Empty,
            ImageLabel = item["image"]?["label"]?.ToString() ?? string.Empty,
            Price = price?["value"]?.ToString() ?? string.Empty,
            Currency = price?["currency"]?.ToString() ?? string.Empty,
            TotalCount = reply?["data"]?["products"]?["total_count"]?.ToString() ?? string.Empty,
        };
    }

    /// <summary>
    /// Whether the product can be bought right now. <c>casio_can_purchase</c> is the store's own verdict and
    /// wins when it is present; otherwise in-stock and not sold out is the best that can be said.
    /// </summary>
    public static bool CanBuy(CasioProduct product)
    {
        if (!string.IsNullOrEmpty(product.CanPurchase))
            return product.CanPurchase.Equals("true", StringComparison.OrdinalIgnoreCase)
                || product.CanPurchase.Equals("1", StringComparison.Ordinal);

        return product.StockStatus.Equals("IN_STOCK", StringComparison.OrdinalIgnoreCase);
    }
}

/// <summary>One Casio product, as the GraphQL selection returns it.</summary>
public sealed class CasioProduct
{
    public string Sku { get; init; } = string.Empty;
    public string Name { get; init; } = string.Empty;
    public string UrlKey { get; init; } = string.Empty;
    public string StockStatus { get; init; } = string.Empty;
    public string OnlyXLeftInStock { get; init; } = string.Empty;
    public string SalesType { get; init; } = string.Empty;
    public string CanPurchase { get; init; } = string.Empty;
    public string SalesStart { get; init; } = string.Empty;
    public string SalesEnd { get; init; } = string.Empty;
    public string ImageUrl { get; init; } = string.Empty;
    public string ImageLabel { get; init; } = string.Empty;
    public string Price { get; init; } = string.Empty;
    public string Currency { get; init; } = string.Empty;
    public string TotalCount { get; init; } = string.Empty;
}
