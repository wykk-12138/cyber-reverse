using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Four session-shaped operations whose handlers name no host.
///
/// <para>
/// <b>Observed</b> (R1359): the handlers for <c>getCustomerInformation</c> (sub_140E5B940) and
/// <c>updateMyPaymentWithActions</c> (sub_140E5B570) hold only <c>application/json</c> and the envelope keys, and they
/// sit in the same address block as <c>getCart</c>'s state machine. Nothing in the block carries a host, so the origin
/// belongs to the caller — sending a relative path to a guessed host would be worse than refusing.
/// </para>
///
/// <para>
/// <b>Observed:</b> the declared sets differ per operation and are published as measured:
/// getCustomerInformation [], getPaymentdMethods [], item [],
/// getCart ['key', 'locale'].
/// </para>
/// </summary>
public static class StoreSessionQueries
{
    /// <summary>getCustomerInformation, 197 characters from 0x147144F7C.</summary>
    public const string GetCustomerInformationDocument = "query getCustomerInformation {\n  me {\n    customer {\n      custom {\n        customFieldsRaw {\n          name\n          value\n        }\n      }\n      email\n      firstName\n      lastName\n    }\n  }\n}";

    /// <summary>getPaymentdMethods, 3067 characters from 0x14714511C — the operation's own misspelling.</summary>
    public const string GetPaymentdMethodsDocument = "query getPaymentdMethods {\n  getPaymentdMethods(\n    addressInformation: {shipping_carrier_code: $shippingCarrierCode, shipping_method_code: $shippingMethodCode, shipping_carrier_title: $shippingCarrierTitle, shipping_method_title: $shippingMethodTitle, shipping_address: {firstname: $firstname, lastname: $lastname, email: $email, street: [$street1, $street2], city: $city, region_id: $regionId, region: $region, region_code: $regionCode, postcode: $postcode, country_id: $countryId, telephone: $telephone, saveInAddressBook: 0}, billing_address: {firstname: $billingFirstname, lastname: $billingLastname, email: $email, street: [$billingStreet1, $billingStreet2], city: $billingCity, region_id: $billingRegionId, region: $billingRegion, region_code: $billingRegionCode, postcode: $billingPostcode, country_id: $billingCountryId, telephone: $telephone}, is_virtual: false}\n  ) {\n    payment_methods {\n      code\n      title\n      __typename\n    }\n    totals {\n      grand_total\n      base_grand_total\n      subtotal\n      base_subtotal\n      discount_amount\n      base_discount_amount\n      subtotal_with_discount\n      base_subtotal_with_discount\n      shipping_amount\n      base_shipping_amount\n      shipping_discount_amount\n      base_shipping_discount_amount\n      tax_amount\n      base_tax_amount\n      weee_tax_applied_amount\n      shipping_tax_amount\n      base_shipping_tax_amount\n      subtotal_incl_tax\n      shipping_incl_tax\n      base_shipping_incl_tax\n      base_currency_code\n      quote_currency_code\n      coupon_code\n      items_qty\n      items {\n        item_id\n        price\n        base_price\n        qty\n        row_total\n        base_row_total\n        row_total_with_discount\n        tax_amount\n        base_tax_amount\n        tax_percent\n        discount_amount\n        base_discount_amount\n        discount_percent\n        price_incl_tax\n        base_price_incl_tax\n        row_total_incl_tax\n        base_row_total_incl_tax\n        options\n        weee_tax_applied_amount\n        weee_tax_applied\n        name\n        extension_attributes {\n          amasty_promo {\n            image_src\n            __typename\n          }\n          pan_store_type_id\n          pan_store_type\n          thumbnail\n          sku\n          __typename\n        }\n        reward_points\n        isStore\n        isNil\n        isReward\n        __typename\n      }\n      total_segments {\n        code\n        title\n        value\n        __typename\n      }\n      __typename\n    }\n    extension_attributes {\n      original_address {\n        region\n        region_id\n        country_id\n        street\n        telephone\n        postcode\n        city\n        firstname\n        lastname\n        email\n        exact_match\n        __typename\n      }\n      valid_address {\n        region\n        region_id\n        country_id\n        street\n        telephone\n        postcode\n        city\n        firstname\n        lastname\n        email\n        exact_match\n        __typename\n      }\n      error_message\n      __typename\n    }\n    message\n    exact_match\n    __typename\n  }\n}\n";

    /// <summary>item, 67 characters from 0x147146EF4.</summary>
    public const string ItemDocument = "query item {\n  item(\n    attribute_code: []\n    sku: \"\"\n    name: \"";

    /// <summary>getCart, 3234 characters from 0x14714361C.</summary>
    public const string GetCartDocument = "query getCart($locale: Locale!, $key: KeyReferenceInput!) {\n  inStore(key: $key) {\n    me {\n      activeCart {\n        ...defaultCart\n      }\n    }\n  }\n}\n\nfragment defaultCart on Cart {\n  id\n  version\n  locale\n  isAbleToCheckout\n  isRestricted\n  isHazardous\n  isEmpty\n  isDangerous\n  splittableSupplyChannelKeys\n  isSplit\n  shippingMode\n  totalLineItemQuantity\n  anonymousId\n  customerId\n  whPlusOnly\n  customerEmail\n  customer {\n    ...defaultCustomer\n  }\n  billingAddress {\n    ...defaultAddress\n  }\n  paymentInfo {\n    payments {\n      amountPlanned {\n        type\n        currencyCode\n        centAmount\n        fractionDigits\n      }\n      paymentMethodInfo {\n        method\n      }\n      id\n      version\n      custom {\n        customFieldsRaw {\n          name\n          value\n        }\n      }\n    }\n  }\n  shipping {\n    ...defaultShipping\n  }\n  customerGroup {\n    key\n  }\n  lineItems {\n    ...defaultLineItem\n  }\n  itemShippingAddresses {\n    ...defaultAddress\n  }\n  discountedPrice {\n    centAmount\n    currencyCode\n    fractionDigits\n  }\n  totalPrice {\n    centAmount\n    currencyCode\n    fractionDigits\n  }\n  taxedPrice {\n    totalTax {\n      centAmount\n      currencyCode\n      fractionDigits\n    }\n    totalGross {\n      centAmount\n      currencyCode\n      fractionDigits\n    }\n    taxPortions {\n      name\n      amount {\n        centAmount\n        currencyCode\n        fractionDigits\n      }\n    }\n  }\n  custom {\n    customFieldsRaw {\n      name\n      value\n    }\n  }\n  hasGift\n}\n\nfragment defaultCustomer on Customer {\n  custom {\n    customFieldsRaw {\n      name\n      value\n    }\n  }\n  email\n  defaultShippingAddressId\n  shippingAddressIds\n  addresses {\n    ...defaultAddress\n  }\n}\n\nfragment defaultAddress on Address {\n  isDefault\n  id\n  key\n  streetName\n  streetNumber\n  additionalStreetInfo\n  city\n  postalCode\n  region\n  state\n  country\n  firstName\n  lastName\n  email\n  phone\n  externalId\n  custom {\n    customFieldsRaw {\n      name\n      value\n    }\n  }\n}\n\nfragment defaultShipping on Shipping {\n  shippingKey\n  shippingInfo {\n    isHazardous\n    deliveries {\n      id\n      items {\n        id\n        quantity\n      }\n    }\n    price {\n      centAmount\n      currencyCode\n      fractionDigits\n    }\n    shippingMethodName\n    shippingMethod {\n      localizedName(locale: $locale)\n    }\n  }\n  shippingAddress {\n    ...defaultAddress\n  }\n  isValid\n}\n\nfragment defaultLineItem on LineItem {\n  id\n  productId\n  productSlug(locale: $locale)\n  name(locale: $locale)\n  productType {\n    id\n    version\n    name\n  }\n  totalPrice {\n    centAmount\n    currencyCode\n    fractionDigits\n  }\n  preDiscountedPrice {\n    centAmount\n    currencyCode\n    fractionDigits\n  }\n  shippingDetails {\n    targets {\n      addressKey\n      shippingMethodKey\n      quantity\n    }\n    valid\n  }\n  productKey\n  quantity\n  variant {\n    sku\n    key\n    images {\n      url\n    }\n    attributesRaw {\n      name\n      value\n    }\n  }\n  discountedPricePerQuantity {\n    discountedPrice {\n      includedDiscounts {\n        discount {\n          id\n          key\n          description(locale: $locale)\n        }\n      }\n    }\n  }\n  custom {\n    customFieldsRaw {\n      name\n      value\n    }\n  }\n  supplyChannel {\n    id\n    key\n  }\n  lineItemMode\n}";

    /// <summary>The variables each document declares.</summary>
    public static readonly IReadOnlyDictionary<string, string[]> Declared = new Dictionary<string, string[]>
    {
        ["getCustomerInformation"] = Array.Empty<string>(),
        ["getPaymentdMethods"] = Array.Empty<string>(),
        ["item"] = Array.Empty<string>(),
        ["getCart"] = new[] { "key", "locale" },
    };

    /// <summary>The document for an operation, or null when it is not one of the four.</summary>
    public static string? DocumentFor(string operation) => operation switch
    {
        "getCustomerInformation" => GetCustomerInformationDocument,
        "getPaymentdMethods" => GetPaymentdMethodsDocument,
        "item" => ItemDocument,
        "getCart" => GetCartDocument,
        _ => null,
    };

    /// <summary>The request body.</summary>
    public static JObject Envelope(string operation, JObject variables) => new()
    {
        ["operationName"] = operation,
        ["query"] = DocumentFor(operation) ?? throw new ArgumentOutOfRangeException(nameof(operation)),
        ["variables"] = variables,
    };

    /// <summary>Post one operation; every variable must be one the document declares.</summary>
    public static async Task<(JObject? Data, string Error)> SendAsync(
        FlowContext c, string? origin, string operation, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(origin)) return (null, "store-session: no origin");
        var document = DocumentFor(operation);
        if (document is null) return (null, "store-session: unknown operation " + operation);

        foreach (var property in variables.Properties())
        {
            if (Array.IndexOf(Declared[operation], property.Name) >= 0) continue;
            return (null, "store-session: " + operation + " does not declare $" + property.Name);
        }

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, origin!.TrimEnd('/'), Envelope(operation, variables), "store-session", ct)
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
