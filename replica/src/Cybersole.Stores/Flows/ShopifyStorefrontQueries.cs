using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The Shopify Storefront mutations the image carries.
///
/// <para>
/// <b>Observed</b> (R1348, R1349): three documents whose variable signatures are Storefront's own —
/// <c>cartApiObjectCreate</c> (5876 characters, 0x1470EF5FC), <c>createCart</c> (1622, 0x1470F260C) and
/// <c>removeLineItemFromCart</c> (1553, 0x1470F4C84) — posted to <c>api/&lt;version&gt;/graphql.json</c> with a
/// Storefront access token header.
/// </para>
///
/// <para>
/// <b>Why only three:</b> the other documents in that address range are not Storefront. <c>setBillingAddress</c>
/// declares an action object plus two locales, which is the shape the Highsnobiety family uses, and
/// <c>createCheckout</c> carries a recaptcha token. An address cluster is a lead; the variable signature is the
/// evidence.
/// </para>
///
/// <para>
/// <b>Not reproduced:</b> the Storefront access token the image holds as a literal. A credential copied into source
/// is a credential that leaks, so the caller supplies its own.
/// </para>
/// </summary>
public static class ShopifyStorefrontQueries
{
    /// <summary>The API version the senders address.</summary>
    public const string ApiVersion = "2025-04";

    /// <summary>cartApiObjectCreate, 5876 characters from 0x1470EF5FC.</summary>
    public const string CartApiObjectCreate = "mutation cartApiObjectCreate($input: CartInput!, $includeInventory: Boolean!, $includeStoreAvailability: Boolean!, $includeProductTags: Boolean!, $includeCustomerTags: Boolean!, $includeSellingPlans: Boolean!, $country: CountryCode, $metafieldsIdentifiers: [HasMetafieldsIdentifier!]!) @inContext(country: $country) {  cartCreate(input: $input) {    cart {      ...CartApiObject    }    userErrors {      code      field      message    }  }}fragment CartApiObject on Cart {  lines(first: 250) {    edges {      node {        ...CartApiLine      }    }  }  attributes {    key    value  }  buyerIdentity {    countryCode    customer {      ...Customer    }    email    phone  }  checkoutUrl  createdAt  discountCodes {    applicable    code  }  estimatedCost {    subtotalAmount {      amount      currencyCode    }    totalAmount {      amount      currencyCode    }    totalDutyAmount {      amount      currencyCode    }    totalTaxAmount {      amount      currencyCode    }  }  id  note  updatedAt}fragment CartApiLine on CartLine {  attributes {    key    value  }  discountAllocations {    discountedAmount {      amount      currencyCode    }  }  estimatedCost {    subtotalAmount {      amount      currencyCode    }    totalAmount {      amount      currencyCode    }  }  id  merchandise {    ...Variant    ... on ProductVariant {      product {        ...Product      }    }  }  quantity  sellingPlanAllocation @include(if: $includeSellingPlans) {    ...SellingPlanAllocation  }}fragment Variant on ProductVariant {  metafields(identifiers: $metafieldsIdentifiers) {    ...Metafield  }  storeAvailability(first: 250) @include(if: $includeStoreAvailability) {    edges {      node {        available        location {          address {            address1            address2            city            country            countryCode            formatted            latitude            longitude            phone            province            provinceCode            zip          }          id          name        }        pickUpTime      }    }  }  availableForSale  compareAtPriceV2 {    amount    currencyCode  }  currentlyNotInStock  id  image {    ...Image  }  priceV2 {    amount    currencyCode  }  quantityAvailable @include(if: $includeInventory)  requiresShipping  selectedOptions {    name    value  }  sku  title  unitPrice {    amount    currencyCode  }  unitPriceMeasurement {    measuredType    quantityUnit    quantityValue    referenceUnit    referenceValue  }  weight  weightUnit  swatch1x: image {    alt: altText    uri: transformedSrc(scale: 1, maxWidth: 36, maxHeight: 36)  }  swatch2x: image {    alt: altText    uri: transformedSrc(scale: 2, maxWidth: 36, maxHeight: 36)  }  swatch3x: image {    alt: altText    uri: transformedSrc(scale: 3, maxWidth: 36, maxHeight: 36)  }}fragment Metafield on Metafield {  createdAt  description  id  key  namespace  type  updatedAt  value}fragment Image on Image {  id  originalSrc  altText  height  width}fragment Product on Product {  collections(first: 250) {    edges {      node {        id        title        handle      }    }  }  images(first: 250) {    edges {      node {        ...Image      }    }  }  media(first: 250) {    edges {      node {        ...Media      }    }  }  metafields(identifiers: $metafieldsIdentifiers) {    ...Metafield  }  variants(first: 250) {    pageInfo {      hasNextPage      hasPreviousPage    }    edges {      cursor      node {        ...Variant      }    }  }  availableForSale  compareAtPriceRange {    maxVariantPrice {      amount      currencyCode    }    minVariantPrice {      amount      currencyCode    }  }  createdAt  description  descriptionHtml  handle  id  onlineStoreUrl  options {    id    name    values  }  priceRange {    maxVariantPrice {      amount      currencyCode    }    minVariantPrice {      amount      currencyCode    }  }  productType  publishedAt  seo {    description    title  }  tags @include(if: $includeProductTags)  title  totalInventory @include(if: $includeInventory)  updatedAt  vendor}fragment Media on Media {  __typename  alt  mediaContentType  previewImage {    ...Image  }  ... on ExternalVideo {    embeddedUrl    host    id  }  ... on MediaImage {    id    image {      ...Image    }  }  ... on Model3d {    id    sources {      filesize      format      mimeType      url    }  }  ... on Video {    id    sources {      format      height      mimeType      url      width    }  }}fragment SellingPlanAllocation on SellingPlanAllocation {  priceAdjustments {    compareAtPrice {      amount      currencyCode    }    perDeliveryPrice {      amount      currencyCode    }    price {      amount      currencyCode    }    unitPrice {      amount      currencyCode    }  }  sellingPlan {    ...SellingPlan  }}fragment SellingPlan on SellingPlan {  description  id  name  options {    name    value  }  priceAdjustments {    adjustmentValue {      __typename      ... on SellingPlanFixedAmountPriceAdjustment {        adjustmentAmount {          amount          currencyCode        }      }      ... on SellingPlanFixedPriceAdjustment {        price {          amount          currencyCode        }      }      ... on SellingPlanPercentagePriceAdjustment {        adjustmentPercentage      }    }    orderCount  }  recurringDeliveries}fragment Customer on Customer {  ...SavedAddresses  acceptsMarketing  createdAt  displayName  email  firstName  id  lastName  phone  tags @include(if: $includeCustomerTags)  updatedAt}fragment SavedAddresses on Customer {  addresses(first: 100) {    edges {      node {        ...Address      }    }  }  defaultAddress {    id  }}fragment Address on MailingAddress {  address1  address2  city  company  country  countryCodeV2  firstName  formatted(withCompany: true, withName: true)  formattedArea  id  lastName  latitude  longitude  name  phone  province  provinceCode  zip}";

    /// <summary>createCart, 1622 characters from 0x1470F260C.</summary>
    public const string CreateCart = "mutation createCart($lines: [CartLineInput!]!, $buyerIdentity: CartBuyerIdentityInput!, $attributes: [AttributeInput!], $language: LanguageCode, $country: CountryCode) @inContext(language: $language, country: $country) {\r\n  cartCreate(\r\n    input: {lines: $lines, buyerIdentity: $buyerIdentity, attributes: $attributes}\r\n  ) {\r\n    cart {\r\n      ...ShopifyCart\r\n    }\r\n    userErrors {\r\n      field\r\n      message\r\n    }\r\n  }\r\n}\r\n\r\nfragment ShopifyCart on Cart {\r\n  id\r\n  checkoutUrl\r\n  totalQuantity\r\n  attributes {\r\n    key\r\n    value\r\n  }\r\n  lines(first: 250) {\r\n    edges {\r\n      node {\r\n        id\r\n        quantity\r\n        attributes {\r\n          key\r\n          value\r\n        }\r\n        cost {\r\n          amountPerQuantity {\r\n            amount\r\n            currencyCode\r\n          }\r\n          totalAmount {\r\n            amount\r\n            currencyCode\r\n          }\r\n          subtotalAmount {\r\n            amount\r\n            currencyCode\r\n          }\r\n        }\r\n        merchandise {\r\n          ...ProductVariant\r\n        }\r\n      }\r\n    }\r\n  }\r\n  discountAllocations {\r\n    discountedAmount {\r\n      amount\r\n      currencyCode\r\n    }\r\n  }\r\n  cost {\r\n    totalAmount {\r\n      amount\r\n      currencyCode\r\n    }\r\n    subtotalAmount {\r\n      amount\r\n      currencyCode\r\n    }\r\n  }\r\n}\r\n\r\nfragment ProductVariant on ProductVariant {\r\n  id\r\n  sku\r\n  price {\r\n    amount\r\n    currencyCode\r\n  }\r\n  product {\r\n    id\r\n    description\r\n    title\r\n  }\r\n  image {\r\n    url\r\n  }\r\n  title\r\n  unitPrice {\r\n    amount\r\n    currencyCode\r\n  }\r\n  taxable\r\n  currentlyNotInStock\r\n  selectedOptions {\r\n    name\r\n    value\r\n  }\r\n}";

    /// <summary>removeLineItemFromCart, 1553 characters from 0x1470F4C84.</summary>
    public const string RemoveLineItemFromCart = "mutation removeLineItemFromCart($cartId: String!, $lineItemId: String!, $version: Long!, $quantity: Long!, $locale: Locale!) {\n  updateMyCart(\n    id: $cartId\n    actions: {removeLineItem: {lineItemId: $lineItemId, quantity: $quantity}}\n    version: $version\n  ) {\n    id\n    version\n    isAbleToCheckout\n    isRestricted\n    isHazardous\n    isEmpty\n    isDangerous\n    splittableSupplyChannelKeys\n    isSplit\n    discountedPrice {\n      centAmount\n      currencyCode\n      fractionDigits\n    }\n    customerGroup {\n      key\n    }\n    lineItems {\n      ...defaultLineItem\n    }\n    totalLineItemQuantity\n    totalPrice {\n      centAmount\n      currencyCode\n      fractionDigits\n    }\n  }\n}\n\nfragment defaultLineItem on LineItem {\n  id\n  productId\n  productSlug(locale: $locale)\n  name(locale: $locale)\n  productType {\n    id\n    version\n    name\n  }\n  totalPrice {\n    centAmount\n    currencyCode\n    fractionDigits\n  }\n  preDiscountedPrice {\n    centAmount\n    currencyCode\n    fractionDigits\n  }\n  shippingDetails {\n    targets {\n      addressKey\n      shippingMethodKey\n      quantity\n    }\n    valid\n  }\n  productKey\n  quantity\n  variant {\n    sku\n    key\n    images {\n      url\n    }\n    attributesRaw {\n      name\n      value\n    }\n  }\n  discountedPricePerQuantity {\n    discountedPrice {\n      includedDiscounts {\n        discount {\n          id\n          key\n          description(locale: $locale)\n        }\n      }\n    }\n  }\n  custom {\n    customFieldsRaw {\n      name\n      value\n    }\n  }\n  supplyChannel {\n    id\n    key\n  }\n  lineItemMode\n}";

    /// <summary>The variables each document declares.</summary>
    public static readonly IReadOnlyDictionary<string, string[]> Declared = new Dictionary<string, string[]>
    {
        ["cartApiObjectCreate"] = new[]
        {
            "input", "includeInventory", "includeStoreAvailability", "includeSellingPlans",
            "includeProductTags", "includeCustomerTags", "country", "metafieldsIdentifiers",
        },
        ["createCart"] = new[] { "lines", "buyerIdentity", "attributes", "country", "language" },
        ["removeLineItemFromCart"] = new[] { "cartId", "lineItemId", "version", "quantity", "locale" },
    };

    /// <summary>The variables each sender fills. <c>metafieldsIdentifiers</c> is declared and left out.</summary>
    public static readonly IReadOnlyDictionary<string, string[]> SenderFills = new Dictionary<string, string[]>
    {
        ["cartApiObjectCreate"] = new[]
        {
            "input", "includeInventory", "includeStoreAvailability", "includeSellingPlans",
            "includeProductTags", "includeCustomerTags", "country",
        },
        ["createCart"] = new[] { "lines", "buyerIdentity", "attributes", "country", "language" },
        ["removeLineItemFromCart"] = new[] { "cartId", "lineItemId", "version", "quantity", "locale" },
    };

    /// <summary>The document for an operation, or null when it is not one of the three.</summary>
    public static string? DocumentFor(string operation) => operation switch
    {
        "cartApiObjectCreate" => CartApiObjectCreate,
        "createCart" => CreateCart,
        "removeLineItemFromCart" => RemoveLineItemFromCart,
        _ => null,
    };

    /// <summary>The request body.</summary>
    public static JObject Envelope(string operation, JObject variables) => new()
    {
        ["operationName"] = operation,
        ["query"] = DocumentFor(operation) ?? throw new ArgumentOutOfRangeException(nameof(operation)),
        ["variables"] = variables,
    };

    /// <summary>
    /// Post one Storefront operation. <paramref name="host"/> and <paramref name="token"/> are the caller's — the
    /// image's own token is a credential rather than a fact to copy.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> SendAsync(
        FlowContext c, string? host, string? token, string operation, JObject variables,
        CancellationToken ct, string? version = null)
    {
        if (string.IsNullOrWhiteSpace(host)) return (null, "shopify-storefront: no store host");
        if (string.IsNullOrWhiteSpace(token)) return (null, "shopify-storefront: no storefront access token");

        var document = DocumentFor(operation);
        if (document is null) return (null, "shopify-storefront: unknown operation " + operation);

        foreach (var property in variables.Properties())
        {
            if (Array.IndexOf(Declared[operation], property.Name) >= 0) continue;
            return (null, "shopify-storefront: " + operation + " does not declare $" + property.Name);
        }

        var url = ShopifyGraphQl.Endpoint(host!, version ?? ApiVersion);
        c.Session.Headers[ShopifyHeaders.StorefrontAccessToken] = token!;

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url, Envelope(operation, variables), "shopify-" + operation, ct)
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
