using System;
using System.Collections.Generic;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The Magento REST paths the image actually carries, as opposed to the ones the replica assumed.
///
/// <para>
/// <b>Observed</b> (R1250, from the full string dump <c>analysis/ida_strings.txt</c>): the image holds
/// <c>/carts/mine/items/</c>, <c>/carts/mine/items/?estimate=true</c>, <c>/carts/mine/coupons/</c>,
/// <c>/carts/mine/estimate-shipping-methods?</c>, <c>/carts/mine/payment-information</c>,
/// <c>/carts/mine/shipping-information</c>, the <c>/V1/</c>-prefixed pair of the last two,
/// <c>/adyen/carts/mine/payments-details</c>, <c>/adyen/orders/carts/mine/payment-status</c>,
/// <c>/end/carts/mine/</c>, the prefixes <c>/rest/V1</c> and <c>/rest/V1/ppcp/</c>, the bare token
/// <c>carts/mine</c>, the host <c>https://api2.endclothing.com/rest/V1</c>, and the locale-prefixed forms
/// <c>rest/en_ph/V1/carts/mine/payment-information</c> and <c>…/shipping-information</c>.
/// </para>
///
/// <para>
/// <b>Not observed</b>, and previously assumed by the replica: <c>/rest/V1/carts/mine</c> and
/// <c>/rest/V1/carts/mine/totals</c>. Neither appears in the image in any casing or neighbour, which the R1249
/// neighbour search established for the whole twenty-six-literal no-hit list.
/// </para>
///
/// <para>
/// <b>Inference</b>: the <c>rest/{locale}/V1/…</c> pair shows the storefront composes a locale segment between
/// <c>rest/</c> and <c>V1/</c>, which is how one class serves both <c>rest/V1/…</c> and <c>rest/en_ph/V1/…</c>.
/// That is why <see cref="RestBase"/> takes the locale.
/// </para>
///
/// <para>
/// <b>Unknown</b>: which store uses which of these, and whether a given storefront prefixes with <c>/rest/{locale}/V1</c>
/// or with <c>/V1</c> alone. Dispatch is not observable (R1219), so both are offered and neither is assigned.
/// </para>
/// </summary>
public static class MagentoRest
{
    public const string PaymentInformation = "/carts/mine/payment-information";

    public const string ShippingInformation = "/carts/mine/shipping-information";

    public const string Items = "/carts/mine/items/";

    public const string ItemsEstimate = "/carts/mine/items/?estimate=true";

    public const string Coupons = "/carts/mine/coupons/";

    public const string EstimateShippingMethods = "/carts/mine/estimate-shipping-methods?";

    /// <summary>The <c>/V1/</c>-prefixed pair: the same two endpoints as the bare forms above.</summary>
    public const string V1PaymentInformation = "/V1/carts/mine/payment-information";

    public const string V1ShippingInformation = "/V1/carts/mine/shipping-information";

    /// <summary>Adyen's Magento plugin paths — the reason the Adyen flow talks REST at all.</summary>
    public const string AdyenPaymentsDetails = "/adyen/carts/mine/payments-details";

    public const string AdyenPaymentStatus = "/adyen/orders/carts/mine/payment-status";

    /// <summary>The End Clothing storefront's shape: the prefix carries the host and the path is short.</summary>
    public const string EndClothingRestHost = "https://api2.endclothing.com/rest/V1";

    public const string EndClothingCartsMine = "/end/carts/mine/";

    /// <summary>
    /// <c>rest/</c> plus the locale segment plus <c>/V1</c>. Pass <c>null</c> or empty for the unlocalised
    /// <c>/rest/V1</c> the image also carries; pass <c>"en_ph"</c> for the locale-prefixed form it carries beside it.
    /// </summary>
    public static string RestBase(string? locale) =>
        string.IsNullOrEmpty(locale) ? "/rest/V1" : "/rest/" + locale + "/V1";

    /// <summary>One REST path under a base, for callers that hold a base from <see cref="RestBase"/>.</summary>
    public static string Under(string basePath, string path) =>
        (basePath ?? string.Empty).TrimEnd('/') + (path ?? string.Empty);
}
