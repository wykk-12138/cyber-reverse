using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The Shopify Storefront cart creation — <c>cartApiObjectCreate</c>.
///
/// <para>
/// <b>Observed</b> (R1348): the sender at <c>sub_140D1B380</c> (2258 bytes) posts to
/// <c>api/2025-04/graphql.json</c> with <c>buyerIdentity</c>, <c>customerAccessToken</c>,
/// <c>gid://shopify/ProductVariant/</c> and the five <c>include*</c> flags — the Storefront API the replica already
/// addresses through <see cref="ShopifyGraphQl.Endpoint"/>. The document is 5876 characters at 0x1470EF5FC and
/// declares <c>$input</c> plus seven flags; the sender sets all but <c>metafieldsIdentifiers</c>.
/// </para>
///
/// <para>
/// <b>Not reproduced:</b> the storefront access token that sits in the image as a literal
/// (<c>e927ea99…</c>). It is a credential, and a credential copied into source is a credential that leaks; the
/// caller supplies its own.
/// </para>
/// </summary>
public static class ShopifyCartCreate
{
    /// <summary>The operation name, from the document's own header.</summary>
    public const string OperationName = "cartApiObjectCreate";

    /// <summary>The API version the sender addresses.</summary>
    public const string ApiVersion = "2025-04";

    /// <summary>The document, 5876 characters from 0x1470EF5FC.</summary>
    public const string Document =
        "mutation cartApiObjectCreate($input: CartInput!, $includeInventory: Boolean!, $includeStoreAvailability: Boolean!, $includeProductTags: Boolean!, $includeCustomerTags: Boolean!, $includeSellingPlans: Boolean!, $country: CountryCode, $metafieldsIdentifiers: [HasMetafieldsIdentifier!]!) @inContext(country: $country) {  cartCreate(input: $input) {    cart {      ...CartApiObject    }    userErrors {      code      field      message    }  }}fragment CartApiObject on Cart {  lines(first: 250) {    edges {      node {        ...CartApiLine      }    }  }  attributes {    key    value  }  buyerIdentity {    countryCode    customer {      ...Customer    }    email    phone  }  checkoutUrl  createdAt  discountCodes {    applicable    code  }  estimatedCost {    subtotalAmount {      amount      currencyCode    }    totalAmount {      amount      currencyCode    }    totalDutyAmount {      amount      currencyCode    }    totalTaxAmount {      amount      currencyCode    }  }  id  note  updatedAt}fragment CartApiLine on CartLine {  attributes {    key    value  }  discountAllocations {    discountedAmount {      amount      currencyCode    }  }  estimatedCost {    subtotalAmount {      amount      currencyCode    }    totalAmount {      amount      currencyCode    }  }  id  merchandise {    ...Variant    ... on ProductVariant {      product {        ...Product      }    }  }  quantity  sellingPlanAllocation @include(if: $includeSellingPlans) {    ...SellingPlanAllocation  }}fragment Variant on ProductVariant {  metafields(identifiers: $metafieldsIdentifiers) {    ...Metafield  }  storeAvailability(first: 250) @include(if: $includeStoreAvailability) {    edges {      node {        available        location {          address {            address1            address2            city            country            countryCode            formatted            latitude            longitude            phone            province            provinceCode            zip          }          id          name        }        pickUpTime      }    }  }  availableForSale  compareAtPriceV2 {    amount    currencyCode  }  currentlyNotInStock  id  image {    ...Image  }  priceV2 {    amount    currencyCode  }  quantityAvailable @include(if: $includeInventory)  requiresShipping  selectedOptions {    name    value  }  sku  title  unitPrice {    amount    currencyCode  }  unitPriceMeasurement {    measuredType    quantityUnit    quantityValue    referenceUnit    referenceValue  }  weight  weightUnit  swatch1x: image {    alt: altText    uri: transformedSrc(scale: 1, maxWidth: 36, maxHeight: 36)  }  swatch2x: image {    alt: altText    uri: transformedSrc(scale: 2, maxWidth: 36, maxHeight: 36)  }  swatch3x: image {    alt: altText    uri: transformedSrc(scale: 3, maxWidth: 36, maxHeight: 36)  }}fragment Metafield on Metafield {  createdAt  description  id  key  namespace  type  updatedAt  value}fragment Image on Image {  id  originalSrc  altText  height  width}fragment Product on Product {  collections(first: 250) {    edges {      node {        id        title        handle      }    }  }  images(first: 250) {    edges {      node {        ...Image      }    }  }  media(first: 250) {    edges {      node {        ...Media      }    }  }  metafields(identifiers: $metafieldsIdentifiers) {    ...Metafield  }  variants(first: 250) {    pageInfo {      hasNextPage      hasPreviousPage    }    edges {      cursor      node {        ...Variant      }    }  }  availableForSale  compareAtPriceRange {    maxVariantPrice {      amount      currencyCode    }    minVariantPrice {      amount      currencyCode    }  }  createdAt  description  descriptionHtml  handle  id  onlineStoreUrl  options {    id    name    values  }  priceRange {    maxVariantPrice {      amount      currencyCode    }    minVariantPrice {      amount      currencyCode    }  }  productType  publishedAt  seo {    description    title  }  tags @include(if: $includeProductTags)  title  totalInventory @include(if: $includeInventory)  updatedAt  vendor}fragment Media on Media {  __typename  alt  mediaContentType  previewImage {    ...Image  }  ... on ExternalVideo {    embeddedUrl    host    id  }  ... on MediaImage {    id    image {      ...Image    }  }  ... on Model3d {    id    sources {      filesize      format      mimeType      url    }  }  ... on Video {    id    sources {      format      height      mimeType      url      width    }  }}fragment SellingPlanAllocation on SellingPlanAllocation {  priceAdjustments {    compareAtPrice {      amount      currencyCode    }    perDeliveryPrice {      amount      currencyCode    }    price {      amount      currencyCode    }    unitPrice {      amount      currencyCode    }  }  sellingPlan {    ...SellingPlan  }}fragment SellingPlan on SellingPlan {  description  id  name  options {    name    value  }  priceAdjustments {    adjustmentValue {      __typename      ... on SellingPlanFixedAmountPriceAdjustment {        adjustmentAmount {          amount          currencyCode        }      }      ... on SellingPlanFixedPriceAdjustment {        price {          amount          currencyCode        }      }      ... on SellingPlanPercentagePriceAdjustment {        adjustmentPercentage      }    }    orderCount  }  recurringDeliveries}fragment Customer on Customer {  ...SavedAddresses  acceptsMarketing  createdAt  displayName  email  firstName  id  lastName  phone  tags @include(if: $includeCustomerTags)  updatedAt}fragment SavedAddresses on Customer {  addresses(first: 100) {    edges {      node {        ...Address      }    }  }  defaultAddress {    id  }}fragment Address on MailingAddress {  address1  address2  city  company  country  countryCodeV2  firstName  formatted(withCompany: true, withName: true)  formattedArea  id  lastName  latitude  longitude  name  phone  province  provinceCode  zip}";

    /// <summary>The eight variables the document declares.</summary>
    public static readonly string[] DeclaredVariables =
    {
        "input", "includeInventory", "includeStoreAvailability", "includeSellingPlans",
        "includeProductTags", "includeCustomerTags", "country", "metafieldsIdentifiers",
    };

    /// <summary>
    /// The variables the sender fills. <c>metafieldsIdentifiers</c> is declared and left out, so it stays the
    /// caller's to add when a store asks for metafields.
    /// </summary>
    public static readonly string[] SenderVariables =
    {
        "input", "includeInventory", "includeStoreAvailability", "includeSellingPlans",
        "includeProductTags", "includeCustomerTags", "country",
    };

    /// <summary>The request body.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Create a cart. <paramref name="host"/> is the store's hostname and <paramref name="token"/> its Storefront
    /// access token — both are the caller's, because the image's own copy is a credential rather than a fact.
    /// </summary>
    public static async Task<(string? CartId, string Error)> CreateAsync(
        FlowContext c, string? host, string? token, JObject variables, CancellationToken ct, string? version = null)
    {
        if (string.IsNullOrWhiteSpace(host)) return (null, "shopify-cart: no store host");
        if (string.IsNullOrWhiteSpace(token)) return (null, "shopify-cart: no storefront access token");
        if (variables is null || variables["input"] is null)
            return (null, "shopify-cart: no $input — the document requires a CartInput");

        var url = ShopifyGraphQl.Endpoint(host!, version ?? ApiVersion);
        c.Session.Headers[ShopifyHeaders.StorefrontAccessToken] = token!;

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url, Envelope(variables), "shopify-cart-create", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "shopify-cart: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "shopify-cart: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var cart = reply["data"]?["cartCreate"]?["cart"];
            var cartId = cart?["id"]?.ToString();
            return string.IsNullOrEmpty(cartId)
                ? (null, "shopify-cart: no cart in reply")
                : (cartId, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "shopify-cart: " + ex.GetType().Name);
        }
    }
}
