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

    /// <summary>
    /// item prefix (67 characters from 0x147146EF4) and suffix (5775 characters from 0x146A6E6EC).
    /// <b>Observed</b> (R1382): <c>sub_140B60C90</c> (<c>onepanini</c>) concatenates prefix + name + suffix.
    /// R1359 copied only the 67-character prefix, leaving <c>ItemDocument</c> an unclosed query.
    /// </summary>
    public const string ItemPrefix = "query item {\n  item(\n    attribute_code: []\n    sku: \"\"\n    name: \"";

    /// <summary>item suffix, 5775 characters from 0x146A6E6EC (<c>sub_140B60C90</c>).</summary>
    public const string ItemSuffix = "\"\n  ) {\n    id\n    sku\n    psku\n    name\n    price\n    highest_sale\n    lowest_sale\n    final_price\n    description\n    short_description\n    category_ids\n    reward_points\n    news_from_date\n    news_to_date\n    meta_title\n    meta_keywords\n    meta_description\n    created_at\n    min_sale_qty\n    max_sale_qty\n    special_price\n    url_key\n    is_in_stock\n    special_from_date\n    special_to_date\n    pan_coming_soon\n    pan_offer_start_date\n    pan_offer_end_date\n    isStore\n    pan_background_image_url\n    product_links {\n      sku\n      link_type\n      linked_product_sku\n      linked_product_type\n      position\n      info {\n        id\n        sku\n        name\n        image\n        thumbnail\n        price\n        special_price\n        final_price\n        url_key\n        created_at\n        visibility\n        pan_hide_price\n        pan_show_timer\n        pan_trending_product_sort_order\n        __typename\n      }\n      __typename\n    }\n    isShowLeftInStock\n    qty_left_after\n    pan_show_qty_left_after\n    pan_sale_quantity_tracker\n    cardset\n    end_seq\n    start_seq\n    media_gallery_entries {\n      label\n      media_type\n      types\n      file\n      __typename\n    }\n    type_id\n    timestamp\n    tnc\n    status\n    options {\n      attribute_id\n      attribute_code\n      label\n      position\n      options {\n        label\n        value\n        __typename\n      }\n      __typename\n    }\n    pan_store_auction_start_price\n    pan_store_auction_end_price\n    pan_store_auction_price_drop\n    pan_store_auction_start_points\n    pan_store_auction_end_points\n    pan_store_auction_drop_points\n    pan_boxes_per_case\n    pan_configuration\n    pan_looking_for\n    pan_cards_per_pack\n    pan_packs_per_box\n    pan_key_athletes_flag\n    pan_key_athletes_name\n    pan_shipping_charges\n    pan_shipping_info\n    pan_terms_of_sale\n    pan_album\n    pan_sticker_packets\n    pan_stickers_per_packet\n    pan_authentic_product\n    pan_rookie_veterans_legends\n    pan_legend_athlete_names\n    pan_veteran_athlete_names\n    pan_rookie_athlete_names\n    isAuction\n    isCrypto\n    isNil\n    is_crypto_market\n    is_owner\n    is_bid\n    identifier\n    highest_bid\n    total_bids\n    buy_now_price\n    decline_price\n    auction_id\n    is_top_bidder\n    fullname\n    current_user\n    is_placed_bid\n    collection\n    sport\n    athlete\n    pan_show_timer\n    seller_comment\n    current_time\n    is_admin_created_auction\n    is_validating\n    last_bid_time\n    bid_reset_interval\n    panini_fee_msg\n    pan_physical_gift\n    physical_gift_description\n    pan_gift_image_1\n    pan_gift_image_2\n    pan_gift_image_3\n    is_address_specified\n    address_id\n    pan_hide_price\n    web_color\n    web_product_icon\n    type_type\n    is_user_liked\n    is_public_visible\n    allow_offers\n    visibility_type\n    likes_count\n    in_public_auction\n    pan_accept_bids\n    membership_sold_qty\n    max_bid {\n      highest_bid\n      highest_bid_status\n      is_top_bidder\n      __typename\n    }\n    pan_is_ipo\n    next_increment_amount\n    pan_ipo_user_max_offers\n    user_ipo_count\n    pan_video_link\n    extended_bid_interval\n    pan_desc_video_link\n    pan_product_web_banner\n    pan_product_app_banner\n    extended_timer_enabled\n    auction_type\n    is_product_transferred\n    card_type\n    card_rarity\n    rarity_gradient_color\n    rarity_icon\n    rarity_font_color\n    rarity_primary_color\n    rarity_secondary_bg_color\n    year\n    auction_duration_days\n    card_relist_count\n    relist_processed_count\n    relisting_duration_days\n    relist_msg\n    pan_membership_banner_url\n    pan_total_slots\n    transaction_hash\n    sport_name\n    program\n    product_brand\n    pan_release_year\n    pan_product_type\n    bundle_product_options {\n      option_title\n      option_id\n      option_type\n      product_links {\n        selection_product_name\n        selection_option_id\n        selection_id\n        selection_product_image\n        selection_product_description\n        selection_product_quantity\n        __typename\n      }\n      __typename\n    }\n    membership_product_options {\n      name\n      sku\n      image\n      description\n      max_sale_qty\n      __typename\n    }\n    pan_hide_qty\n    children {\n      key\n      value {\n        id\n        sku\n        name\n        price\n        final_price\n        description\n        short_description\n        category_ids\n        reward_points\n        news_from_date\n        news_to_date\n        meta_title\n        meta_keywords\n        meta_description\n        min_sale_qty\n        max_sale_qty\n        special_price\n        url_key\n        is_in_stock\n        special_from_date\n        special_to_date\n        pan_offer_start_date\n        pan_offer_end_date\n        pan_show_qty_left_after\n        media_gallery_entries {\n          label\n          media_type\n          types\n          file\n          __typename\n        }\n        type_id\n        pan_store_auction_start_price\n        pan_store_auction_end_price\n        pan_store_auction_price_drop\n        pan_coming_soon\n        pan_boxes_per_case\n        pan_configuration\n        pan_looking_for\n        pan_cards_per_pack\n        pan_packs_per_box\n        pan_key_athletes_flag\n        pan_key_athletes_name\n        pan_shipping_charges\n        pan_shipping_info\n        pan_terms_of_sale\n        pan_album\n        pan_sticker_packets\n        pan_stickers_per_packet\n        pan_authentic_product\n        pan_rookie_veterans_legends\n        pan_legend_athlete_names\n        pan_veteran_athlete_names\n        pan_rookie_athlete_names\n        isAuction\n        isCrypto\n        image\n        pan_hide_price\n        is_user_liked\n        is_public_visible\n        allow_offers\n        visibility_type\n        likes_count\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n";

    /// <summary>Complete item query with an empty name filter (67 + 5775 = 5842 characters).</summary>
    public const string ItemDocument = ItemPrefix + ItemSuffix;

    /// <summary>Build the <c>item</c> query interpolating <paramref name="name"/> as <c>sub_140B60C90</c> does.</summary>
    public static string BuildItemDocument(string? name)
    {
        var safe = (name ?? string.Empty).Replace("\\", "\\\\").Replace("\"", "\\\"");
        return ItemPrefix + safe + ItemSuffix;
    }

    /// <summary>
    /// removeLineItemFromCart, 1553 characters from 0x1470F4C84 (<c>sub_140E59240</c>, Commercetools session block).
    /// Moved here from <c>ShopifyStorefrontQueries</c> in R1382.
    /// </summary>
    public const string RemoveLineItemFromCartDocument = "mutation removeLineItemFromCart($cartId: String!, $lineItemId: String!, $version: Long!, $quantity: Long!, $locale: Locale!) {\n  updateMyCart(\n    id: $cartId\n    actions: {removeLineItem: {lineItemId: $lineItemId, quantity: $quantity}}\n    version: $version\n  ) {\n    id\n    version\n    isAbleToCheckout\n    isRestricted\n    isHazardous\n    isEmpty\n    isDangerous\n    splittableSupplyChannelKeys\n    isSplit\n    discountedPrice {\n      centAmount\n      currencyCode\n      fractionDigits\n    }\n    customerGroup {\n      key\n    }\n    lineItems {\n      ...defaultLineItem\n    }\n    totalLineItemQuantity\n    totalPrice {\n      centAmount\n      currencyCode\n      fractionDigits\n    }\n  }\n}\n\nfragment defaultLineItem on LineItem {\n  id\n  productId\n  productSlug(locale: $locale)\n  name(locale: $locale)\n  productType {\n    id\n    version\n    name\n  }\n  totalPrice {\n    centAmount\n    currencyCode\n    fractionDigits\n  }\n  preDiscountedPrice {\n    centAmount\n    currencyCode\n    fractionDigits\n  }\n  shippingDetails {\n    targets {\n      addressKey\n      shippingMethodKey\n      quantity\n    }\n    valid\n  }\n  productKey\n  quantity\n  variant {\n    sku\n    key\n    images {\n      url\n    }\n    attributesRaw {\n      name\n      value\n    }\n  }\n  discountedPricePerQuantity {\n    discountedPrice {\n      includedDiscounts {\n        discount {\n          id\n          key\n          description(locale: $locale)\n        }\n      }\n    }\n  }\n  custom {\n    customFieldsRaw {\n      name\n      value\n    }\n  }\n  supplyChannel {\n    id\n    key\n  }\n  lineItemMode\n}";

    /// <summary>
    /// UpdateContactDetails, 244 characters from 0x1470E37BC. Its other handler sends the same operation by hash
    /// from the 0x14088xxxx block (R1357); which one a run picks is not established, so only this one is wired.
    /// </summary>
    public const string UpdateContactDetailsDocument = "mutation UpdateContactDetails($phone: String!, $emailOptIn: Boolean!, $email: String) {\n  updateContactDetails(phone: $phone, emailOptIn: $emailOptIn, email: $email) {\n    billingAddress {\n      phone\n      __typename\n    }\n    __typename\n  }\n}";

    /// <summary>addToCartByChannel, 2271 characters from 0x1470E8DCC.</summary>
    public const string AddToCartByChannelDocument = "mutation addToCartByChannel($cartId: String!, $productId: String!, $quantity: Long!, $version: Long!, $locale: Locale!) {\n  updateMyCart(\n    id: $cartId\n    actions: {addLineItem: {productId: $productId, quantity: $quantity, custom: {typeKey: \"line-item-custom-fields\"}}}\n    version: $version\n  ) {\n    id\n    isAbleToCheckout\n    isRestricted\n    isHazardous\n    isEmpty\n    isDangerous\n    version\n    isSplit\n    splittableSupplyChannelKeys\n    totalLineItemQuantity\n    discountedPrice {\n      centAmount\n      currencyCode\n      fractionDigits\n    }\n    totalPrice {\n      centAmount\n      currencyCode\n      fractionDigits\n    }\n    shipping {\n      ...defaultShipping\n    }\n    lineItems {\n      ...defaultLineItem\n    }\n  }\n}\n\nfragment defaultShipping on Shipping {\n  shippingKey\n  shippingInfo {\n    isHazardous\n    deliveries {\n      id\n      items {\n        id\n        quantity\n      }\n    }\n    price {\n      centAmount\n      currencyCode\n      fractionDigits\n    }\n    shippingMethodName\n    shippingMethod {\n      localizedName(locale: $locale)\n    }\n  }\n  shippingAddress {\n    ...defaultAddress\n  }\n  isValid\n}\n\nfragment defaultAddress on Address {\n  isDefault\n  id\n  key\n  streetName\n  streetNumber\n  additionalStreetInfo\n  city\n  postalCode\n  region\n  state\n  country\n  firstName\n  lastName\n  email\n  phone\n  externalId\n  custom {\n    customFieldsRaw {\n      name\n      value\n    }\n  }\n}\n\nfragment defaultLineItem on LineItem {\n  id\n  productId\n  productSlug(locale: $locale)\n  name(locale: $locale)\n  productType {\n    id\n    version\n    name\n  }\n  totalPrice {\n    centAmount\n    currencyCode\n    fractionDigits\n  }\n  preDiscountedPrice {\n    centAmount\n    currencyCode\n    fractionDigits\n  }\n  shippingDetails {\n    targets {\n      addressKey\n      shippingMethodKey\n      quantity\n    }\n    valid\n  }\n  productKey\n  quantity\n  variant {\n    sku\n    key\n    images {\n      url\n    }\n    attributesRaw {\n      name\n      value\n    }\n  }\n  discountedPricePerQuantity {\n    discountedPrice {\n      includedDiscounts {\n        discount {\n          id\n          key\n          description(locale: $locale)\n        }\n      }\n    }\n  }\n  custom {\n    customFieldsRaw {\n      name\n      value\n    }\n  }\n  supplyChannel {\n    id\n    key\n  }\n  lineItemMode\n}";

    /// <summary>
    /// <summary>createCartByStore, 421 characters from 0x1470f32d4.</summary>
    public const string CreateCartByStoreDocument = "mutation createCartByStore($currency: Currency!, $locale: Locale!, $storeKey: String!, $country: Country!, $taxMode: TaxMode!) {\n  createMyCart(\n    draft: {currency: $currency, locale: $locale, store: {key: $storeKey}, country: $country, inventoryMode: ReserveOnOrder, shippingMode: Multiple, taxMode: $taxMode}\n  ) {\n    id\n    version\n    custom {\n      customFieldsRaw {\n        name\n        value\n      }\n    }\n  }\n}";

    /// <summary>initiateCheckout, 251 characters from 0x1470f489c.</summary>
    public const string InitiateCheckoutDocument = "mutation initiateCheckout {\n  initiateCheckout {\n    id\n    version\n    paymentInfo {\n      payments {\n        id\n        version\n        custom {\n          customFieldsRaw {\n            name\n            value\n          }\n        }\n      }\n    }\n  }\n}";

    /// <summary>SignInAsGuest, 453 characters from 0x1470e1adc.</summary>
    public const string SignInAsGuestDocument = "mutation SignInAsGuest($medium: SignInMediumTypeEnum) {\r\n                signInAsGuest(medium: $medium) {\r\n                authPayload {\r\n                    accessToken\r\n                    refreshToken\r\n                    __typename\r\n                }\r\n                userErrors {\r\n                    field\r\n                    message\r\n                    __typename\r\n                }\r\n                __typename\r\n                }\r\n            }";



    /// <summary>maintainShippingGroups, 223 characters from 0x1470f4aac.</summary>
    public const string MaintainShippingGroupsDocument = "mutation maintainShippingGroups($cartId: String!) {\n  maintainMyShippingGroups(cartId: $cartId) {\n    id\n    version\n    isAbleToCheckout\n    totalPrice {\n      centAmount\n      currencyCode\n      fractionDigits\n    }\n  }\n}";

    /// saveAddress, 296 characters from 0x1470F58BC. The image's own async tail names a SaveAddress step, which is
    /// what corroborates it as a store step rather than a helper.
    /// </summary>
    public const string SaveAddressDocument = "mutation saveAddress($address: AddressInput!, $saveAddress: Boolean, $setDefault: Boolean, $editAddress: Boolean) {\n  setShippingAddress(\n    address: $address\n    saveAddress: $saveAddress\n    setDefault: $setDefault\n    editAddress: $editAddress\n  ) {\n    id\n    version\n    customerEmail\n  }\n}";

    /// <summary>getCart, 3234 characters from 0x14714361C.</summary>
    public const string GetCartDocument = "query getCart($locale: Locale!, $key: KeyReferenceInput!) {\n  inStore(key: $key) {\n    me {\n      activeCart {\n        ...defaultCart\n      }\n    }\n  }\n}\n\nfragment defaultCart on Cart {\n  id\n  version\n  locale\n  isAbleToCheckout\n  isRestricted\n  isHazardous\n  isEmpty\n  isDangerous\n  splittableSupplyChannelKeys\n  isSplit\n  shippingMode\n  totalLineItemQuantity\n  anonymousId\n  customerId\n  whPlusOnly\n  customerEmail\n  customer {\n    ...defaultCustomer\n  }\n  billingAddress {\n    ...defaultAddress\n  }\n  paymentInfo {\n    payments {\n      amountPlanned {\n        type\n        currencyCode\n        centAmount\n        fractionDigits\n      }\n      paymentMethodInfo {\n        method\n      }\n      id\n      version\n      custom {\n        customFieldsRaw {\n          name\n          value\n        }\n      }\n    }\n  }\n  shipping {\n    ...defaultShipping\n  }\n  customerGroup {\n    key\n  }\n  lineItems {\n    ...defaultLineItem\n  }\n  itemShippingAddresses {\n    ...defaultAddress\n  }\n  discountedPrice {\n    centAmount\n    currencyCode\n    fractionDigits\n  }\n  totalPrice {\n    centAmount\n    currencyCode\n    fractionDigits\n  }\n  taxedPrice {\n    totalTax {\n      centAmount\n      currencyCode\n      fractionDigits\n    }\n    totalGross {\n      centAmount\n      currencyCode\n      fractionDigits\n    }\n    taxPortions {\n      name\n      amount {\n        centAmount\n        currencyCode\n        fractionDigits\n      }\n    }\n  }\n  custom {\n    customFieldsRaw {\n      name\n      value\n    }\n  }\n  hasGift\n}\n\nfragment defaultCustomer on Customer {\n  custom {\n    customFieldsRaw {\n      name\n      value\n    }\n  }\n  email\n  defaultShippingAddressId\n  shippingAddressIds\n  addresses {\n    ...defaultAddress\n  }\n}\n\nfragment defaultAddress on Address {\n  isDefault\n  id\n  key\n  streetName\n  streetNumber\n  additionalStreetInfo\n  city\n  postalCode\n  region\n  state\n  country\n  firstName\n  lastName\n  email\n  phone\n  externalId\n  custom {\n    customFieldsRaw {\n      name\n      value\n    }\n  }\n}\n\nfragment defaultShipping on Shipping {\n  shippingKey\n  shippingInfo {\n    isHazardous\n    deliveries {\n      id\n      items {\n        id\n        quantity\n      }\n    }\n    price {\n      centAmount\n      currencyCode\n      fractionDigits\n    }\n    shippingMethodName\n    shippingMethod {\n      localizedName(locale: $locale)\n    }\n  }\n  shippingAddress {\n    ...defaultAddress\n  }\n  isValid\n}\n\nfragment defaultLineItem on LineItem {\n  id\n  productId\n  productSlug(locale: $locale)\n  name(locale: $locale)\n  productType {\n    id\n    version\n    name\n  }\n  totalPrice {\n    centAmount\n    currencyCode\n    fractionDigits\n  }\n  preDiscountedPrice {\n    centAmount\n    currencyCode\n    fractionDigits\n  }\n  shippingDetails {\n    targets {\n      addressKey\n      shippingMethodKey\n      quantity\n    }\n    valid\n  }\n  productKey\n  quantity\n  variant {\n    sku\n    key\n    images {\n      url\n    }\n    attributesRaw {\n      name\n      value\n    }\n  }\n  discountedPricePerQuantity {\n    discountedPrice {\n      includedDiscounts {\n        discount {\n          id\n          key\n          description(locale: $locale)\n        }\n      }\n    }\n  }\n  custom {\n    customFieldsRaw {\n      name\n      value\n    }\n  }\n  supplyChannel {\n    id\n    key\n  }\n  lineItemMode\n}";

    /// <summary>The variables each document declares.</summary>
    public static readonly IReadOnlyDictionary<string, string[]> Declared = new Dictionary<string, string[]>
    {
        ["getCustomerInformation"] = Array.Empty<string>(),
        ["getPaymentdMethods"] = Array.Empty<string>(),
        ["item"] = Array.Empty<string>(),
        ["getCart"] = new[] { "key", "locale" },
        ["addToCartByChannel"] = new[] { "cartId", "locale", "productId", "quantity", "version" },
        ["UpdateContactDetails"] = new[] { "email", "emailOptIn", "phone" },
        ["saveAddress"] = new[] { "address", "editAddress", "saveAddress", "setDefault" },
        ["createCartByStore"] = new[] { "country", "currency", "locale", "storeKey", "taxMode" },
        ["SignInAsGuest"] = new[] { "medium" },
        ["initiateCheckout"] = Array.Empty<string>(),
        ["maintainShippingGroups"] = new[] { "cartId" },
        ["removeLineItemFromCart"] = new[] { "cartId", "lineItemId", "version", "quantity", "locale" },
    };

    /// <summary>The document for an operation, or null when it is not one of the four.</summary>
    public static string? DocumentFor(string operation) => operation switch
    {
        "getCustomerInformation" => GetCustomerInformationDocument,
        "getPaymentdMethods" => GetPaymentdMethodsDocument,
        "item" => ItemDocument,
        "getCart" => GetCartDocument,
        "addToCartByChannel" => AddToCartByChannelDocument,
        "UpdateContactDetails" => UpdateContactDetailsDocument,
        "saveAddress" => SaveAddressDocument,
        "createCartByStore" => CreateCartByStoreDocument,
        "SignInAsGuest" => SignInAsGuestDocument,
        "initiateCheckout" => InitiateCheckoutDocument,
        "maintainShippingGroups" => MaintainShippingGroupsDocument,
        "removeLineItemFromCart" => RemoveLineItemFromCartDocument,
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
