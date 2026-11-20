using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// One entry of the Topps variant list, in the shape the image deserialises
/// (<c>0x140C9E420</c> → <c>sub_142E65500(text, &amp;off_1449B8EB0, converter)</c>).
///
/// <para>
/// <b>Observed</b>: the type is <c>ToppsCommerceProduct</c> and it carries seven properties —
/// <c>PriceAmount</c>, <c>ProductImage</c>, <c>ProductVariant</c>, <c>SelectedOption</c>,
/// <c>VariantImage</c>, <c>ToppsCommerceProductUrl</c> and <c>JToken</c> — read out of the NativeAOT
/// reflection metadata the image still ships (<c>get_X</c> / <c>Create_X</c> / <c>XPropInit</c> name
/// triples at 0x143351CB7 … 0x14335221C, and the stored field names <c>_PriceAmount</c> …
/// <c>_JToken</c> at 0x143352084 … 0x143352120). The four list carriers next to them —
/// <c>ListProductImage</c>, <c>ListProductVariant</c>, <c>ListSelectedOption</c>,
/// <c>ListToppsCommerceProduct</c> — say the payload is a collection of these, not a flat object.
/// </para>
///
/// <para>
/// <b>Unknown</b>: the exact casing of the serialised keys. The property names are real, but which of
/// <c>PriceAmount</c> and <c>priceAmount</c> the serializer emits was not recovered: the metadata holds
/// the member names with a trailing <c>@</c> and the name-to-handle tables are hash-keyed, so a literal
/// search for either spelling answers zero and — per the reachability rule — zero hits say nothing
/// about absence. <see cref="ToppsCdn.Parse"/> therefore matches every property name
/// case-insensitively instead of picking a spelling and being silently wrong half the time.
/// </para>
/// </summary>
public sealed record ToppsCommerceProduct(
    string PriceAmount,
    string ProductImage,
    string ProductVariant,
    string SelectedOption,
    string VariantImage,
    string ToppsCommerceProductUrl);

/// <summary>The Topps CDN payload reader — the shape above, parsed without committing to a key casing.</summary>
public static class ToppsCdn
{
    /// <summary>The seven property names, in the metadata's order.</summary>
    public static IReadOnlyList<string> PropertyNames { get; } = new[]
    {
        "PriceAmount",
        "ProductImage",
        "ProductVariant",
        "SelectedOption",
        "VariantImage",
        "ToppsCommerceProductUrl",
        "JToken",
    };

    /// <summary>The four list carriers the same class declares — evidence the payload is a collection.</summary>
    public static IReadOnlyList<string> ListPropertyNames { get; } = new[]
    {
        "ListProductImage",
        "ListProductVariant",
        "ListSelectedOption",
        "ListToppsCommerceProduct",
    };

    /// <summary>
    /// Read the payload: a bare array, or an object holding the list under one of
    /// <see cref="ListPropertyNames"/>. Anything else yields an empty list rather than an exception —
    /// a 404 body or an HTML interstitial is a normal answer from a CDN, not a crash.
    /// </summary>
    public static IReadOnlyList<ToppsCommerceProduct> Parse(string? json)
    {
        if (string.IsNullOrWhiteSpace(json)) return Array.Empty<ToppsCommerceProduct>();

        JToken? root;
        try { root = JToken.Parse(json!); }
        catch (Newtonsoft.Json.JsonException) { return Array.Empty<ToppsCommerceProduct>(); }

        var items = root switch
        {
            JArray array => array,
            JObject obj => ListPropertyNames
                .Select(name => Property(obj, name))
                .FirstOrDefault(v => v is JArray) as JArray,
            _ => null,
        };

        if (items is null) return Array.Empty<ToppsCommerceProduct>();

        return items
            .OfType<JObject>()
            .Select(o => new ToppsCommerceProduct(
                Text(o, "PriceAmount"),
                Text(o, "ProductImage"),
                Text(o, "ProductVariant"),
                Text(o, "SelectedOption"),
                Text(o, "VariantImage"),
                Text(o, "ToppsCommerceProductUrl")))
            .ToList();
    }

    /// <summary>Case-insensitive property lookup — see the casing note on the record above.</summary>
    private static JToken? Property(JObject obj, string name) =>
        obj.Properties()
            .FirstOrDefault(p => string.Equals(p.Name, name, StringComparison.OrdinalIgnoreCase))
            ?.Value;

    private static string Text(JObject obj, string name) => Property(obj, name)?.ToString() ?? string.Empty;
}
