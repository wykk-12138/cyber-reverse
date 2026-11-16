using System.Text;

namespace Cybersole.Stores.Stores;

/// <summary>
/// Global-e — cross-border checkout, and the first vendor whose URL construction is fully recoverable.
///
/// <para>
/// R922. Four literals, and between them they give more than any vendor so far: two merchant identifiers, a template
/// placeholder, and a complete tracking-parameter set.
/// </para>
///
/// <code>
/// /Checkout/v2/8x1r
/// /Checkout/v2/8um2
/// /Checkout/v2/8x1r/641efc40-744a-443c-ad99-420a092c6644?gaSesID=…&amp;ga4SID=…&amp;chkcuid=…&amp;isNECAllowed=true
///                                     &amp;_vwo_store=&amp;vph=1081&amp;vpw=2649&amp;ift=113&amp;utm_source=direct&amp;utm_medium=
/// /Checkout/v2/{_encodedMerchantId}/641efc40-…?（同一套参数）
/// </code>
///
/// <para>
/// Global-e localizes prices and duties across borders at checkout, which is why this is a checkout concern rather than
/// a payment-gateway one: the flow has to reach it before the order is priced, not after it is paid. The two merchant
/// identifiers are two different shops' accounts, which means the identifier is per merchant rather than global — and
/// the fourth literal being a template with <c>{_encodedMerchantId}</c> says the original builds this URL by
/// substitution rather than by concatenating a constant.
/// </para>
///
/// <para>
/// <b>What the parameters mean.</b> Three are legible: <c>chkcuid</c> is a checkout customer identifier and appears as
/// a GUID in the recovered literal, <c>vph</c> and <c>vpw</c> are a viewport's height and width, and
/// <c>isNECAllowed</c> reads as whether a non-EU country is permitted. The others — <c>gaSesID</c>, <c>ga4SID</c>,
/// <c>_vwo_store</c>, <c>ift</c>, <c>utm_*</c> — are analytics and experimentation identifiers, which matter here only
/// because a request missing them may be treated differently from one carrying them.
/// </para>
///
/// <para>
/// <b>What is inference.</b> Which parameters are required and which are optional, and what the checkout returns. The
/// builder below emits all of them, empty where a value is unknown, because the recovered literal carries empty values
/// too (<c>_vwo_store=</c>, <c>utm_medium=</c>) — so an empty parameter is evidence of a normal request rather than of
/// a mistake.
/// </para>
/// </summary>
public static class GlobalECheckout
{
    internal const string WebServicesHost = "https://webservices.global-e.com";
    internal const string DsyHost = "https://web-dsy.global-e.com";

    /// <summary>The two merchant identifiers the image carries, and the template that stands in for one.</summary>
    internal static readonly string[] RecoveredMerchantIds = { "8x1r", "8um2" };

    internal const string MerchantPlaceholder = "{_encodedMerchantId}";

    /// <summary>The customer identifier from the recovered literal. One value, so it is a sample rather than a rule.</summary>
    internal const string SampleCheckoutCustomerId = "641efc40-744a-443c-ad99-420a092c6644";

    /// <summary>
    /// The parameter names in the order the literal gives them, so a built URL can be compared with the recovered one
    /// position by position instead of only by set membership.
    /// </summary>
    internal static readonly string[] ParamOrder =
    {
        "gaSesID", "ga4SID", "chkcuid", "isNECAllowed", "_vwo_store", "vph", "vpw", "ift", "utm_source", "utm_medium",
    };

    /// <summary>
    /// Builds the checkout URL for a merchant. Every parameter in <see cref="ParamOrder"/> is emitted, empty where the
    /// caller supplies nothing, because the recovered literal carries empty values as well.
    /// </summary>
    public static string UrlFor(string merchantId, IReadOnlyDictionary<string, string>? values = null)
    {
        if (string.IsNullOrWhiteSpace(merchantId))
            throw new ArgumentException("Global-e needs a merchant id", nameof(merchantId));

        var sb = new StringBuilder();
        sb.Append(WebServicesHost).Append("/Checkout/v2/").Append(merchantId)
          .Append('/').Append(SampleCheckoutCustomerId).Append('?');

        for (var i = 0; i < ParamOrder.Length; i++)
        {
            if (i > 0) sb.Append('&');
            sb.Append(ParamOrder[i]).Append('=');
            if (values != null && values.TryGetValue(ParamOrder[i], out var v) && v != null)
                sb.Append(Uri.EscapeDataString(v));
        }

        return sb.ToString();
    }

    /// <summary>
    /// Whether a country code is inside the non-EU set the <c>isNECAllowed</c> parameter refers to.
    ///
    /// <para>
    /// Inference, and narrowly stated: the parameter name says non-EU, the flow needs a boolean, and a set is the only
    /// way to get one. The set below is the EEA plus the UK and Switzerland, which is a guess at where the boundary
    /// falls and is labelled as one rather than presented as recovered.
    /// </para>
    /// </summary>
    internal static bool IsNonEu(string countryCode)
    {
        var eu = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV",
            "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE",
            // EEA and the two adjacent markets Global-e commonly groups with the EU for duty purposes
            "IS", "LI", "NO", "GB", "CH",
        };
        return !eu.Contains(countryCode ?? string.Empty);
    }
}