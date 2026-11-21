using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The <c>Product</c> query of a storefront API that posts to a relative <c>api/graphql</c>.
///
/// <para>
/// <b>Observed</b> (R1345): the sender at <c>sub_140E1BAB0</c> (1076 bytes) sets <c>operationName</c> to
/// <c>Product</c> (0x146E4BB30), fills <c>id</c> and <c>variationId</c>, and appends the path <c>api/graphql</c>
/// — built character by character, which is why the constant at 0x145E99C50 reads "api/grap" rather than a URL.
/// The document is 10620 characters at 0x147127B44.
/// </para>
///
/// <para>
/// <b>Observed:</b> four neighbours post to the same relative path with their own operations —
/// <c>AddItemToCart</c> (0x140E1B1D0), <c>CreateInitialCart</c> (0x140E1B700), <c>CheckoutCart</c> (0x140E1BF40)
/// and a session query (0x140E1C390). Together they are one store's storefront API, and none of the five carries
/// the host, so the origin has to come from the caller. That is why the endpoint is a parameter here rather than a
/// constant: a relative path with an invented host would send a real request to the wrong server.
/// </para>
/// </summary>
public static class StorefrontApiProduct
{
    /// <summary>The operation name, 0x146E4BB30.</summary>
    public const string OperationName = "Product";

    /// <summary>The relative path every sender in this family appends.</summary>
    public const string Path = "api/graphql";

    /// <summary>The document, 10620 characters from 0x147127B44.</summary>
    public const string Document =
        "query Product($id: ID!, $isDraft: String, $variationId: ID, $src: String) {\n  product(id: $id) {\n    content(isDraft: $isDraft) {\n      ...ProductContentFields\n      __typename\n    }\n    id\n    name\n    description\n    primaryCategoryId\n    brand\n    promotion {\n      ...promoFields\n      __typename\n    }\n    productStory {\n      longDescription\n      careInstructions\n      __typename\n    }\n    price\n    image {\n      href\n      alt\n      __typename\n    }\n    brand\n    orderable\n    badge\n    look(id: $variationId) {\n      id\n      image {\n        href\n        alt\n        __typename\n      }\n      products {\n        id\n        __typename\n      }\n      __typename\n    }\n    score {\n      rating\n      amount\n      __typename\n    }\n    ...sizes\n    category {\n      ...category\n      parentCategory {\n        ...category\n        parentCategory {\n          ...category\n          parentCategory {\n            ...category\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    variations {\n      variantId\n      specialMessage\n      ean\n      validUntil\n      ...styles\n      id\n      badge\n      salePrice\n      price\n      colorValue\n      colorName\n      preview\n      sizes {\n        id\n        label\n        orderable\n        productId\n        __typename\n      }\n      images {\n        alt\n        href\n        __typename\n      }\n      materialComposition\n      displayOutOfStock {\n        soldout\n        comingsoon\n        backsoon\n        presale\n        displayValue\n        validTo\n        __typename\n      }\n      orderable\n      manufacturerInfo {\n        manufacturerAddress {\n          label\n          content\n          __typename\n        }\n        countryOfOrigin {\n          label\n          content\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    userGeneratedContentForWeb {\n      source\n      pixleeCdnPhotos {\n        squareMediumUrl\n        __typename\n      }\n      altText\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment category on Category {\n  id\n  name\n  title\n  url\n  visible\n}\n\nfragment sizes on Product {\n  productMeasurements {\n    metric\n    imperial\n    __typename\n  }\n}\n\nfragment styles on Variant {\n  preview\n  colorValue\n  colorName\n}\n\nfragment ProductContentFields on Pdp {\n  id\n  aboveProductStory(src: $src) {\n    ...ContentFields\n    __typename\n  }\n  belowProductStory(src: $src) {\n    ...ContentFields\n    __typename\n  }\n}\n\nfragment ContentFields on componentWithFilters {\n  id\n  targetDevices\n  component {\n    ...BodyContentFields\n    ...SplitHeroFields\n    ...FullBleedHeroFields\n    ...VideoHeroFields\n    ...ProductCarouselFields\n    ...CountdownClockFields\n    ...FeaturesGridFields\n    ...HotspotHeroFields\n    ...ProductGroupFeaturesFields\n    ...QuoteCalloutFields\n    ...ShopCollectionFields\n    ...SideBySideFields\n    ...TrendingInlineFields\n    ...YouTubeVideoCarouselFields\n    ...StyliticsCarouselFields\n    ...ProductRecommenderFields\n    ...FeatureHeroFields\n    ...SignUpFormFields\n    ...InfoBannerFields\n    ...LaunchCalendarFields\n    ...IframeFields\n    __typename\n  }\n}\n\nfragment FullBleedHeroFields on FullBleedHero {\n  __typename\n  id\n  backgroundImage {\n    ...SanityImageFields\n    __typename\n  }\n  mobileBackgroundImage {\n    ...SanityImageFields\n    __typename\n  }\n  logo {\n    ...SanityImageFields\n    __typename\n  }\n  logoMobile {\n    ...SanityImageFields\n    __typename\n  }\n  logoPosition\n  header\n  copy\n  footnote\n  ctas {\n    ...ctaFields\n    __typename\n  }\n  textAlignment\n  horizontalAlignment\n  verticalAlignment\n  textColor\n  backgroundColor\n  overlayContent\n  minAspectRatio\n}\n\nfragment ctaFields on CTA {\n  __typename\n  _type\n  id\n  link\n  title\n  variant\n  outlined\n  newtab\n  popup\n  query\n}\n\nfragment SanityImageFields on SanityImage {\n  alt\n  hotspot {\n    _key\n    width\n    height\n    x\n    y\n    __typename\n  }\n  asset {\n    _id\n    url\n    metadata {\n      lqip\n      dimensions {\n        width\n        height\n        __typename\n      }\n      __typename\n    }\n    extension\n    __typename\n  }\n}\n\nfragment BodyContentFields on BodyContent {\n  id\n  horizontalAlignment\n  header\n  copy\n  logo {\n    _key\n    alt\n    asset {\n      _id\n      url\n      __typename\n    }\n    __typename\n  }\n  __typename\n  ctas {\n    ...ctaFields\n    __typename\n  }\n}\n\nfragment SplitHeroFields on SplitHero {\n  __typename\n  id\n  backgroundImage {\n    ...SanityImageFields\n    __typename\n  }\n  mobileBackgroundImage {\n    ...SanityImageFields\n    __typename\n  }\n  header\n  copy\n  footnote\n  ctas {\n    ...ctaFields\n    __typename\n  }\n  layout\n  horizontalAlignment\n  backgroundColor\n  textColor\n}\n\nfragment VideoHeroFields on VideoHero {\n  __typename\n  id\n  backgroundVideo\n  mobileBackgroundVideo\n  header\n  copy\n  footnote\n  ctas {\n    ...ctaFields\n    __typename\n  }\n  textColor\n  horizontalAlignment\n  verticalAlignment\n  overlayContent\n  autoplay\n  loop\n  mute\n  minAspectRatio\n}\n\nfragment ProductCarouselFields on ProductCarousel {\n  __typename\n  id\n  header\n  products {\n    __typename\n    id\n    masterId\n    price\n    salePrice\n    name\n    orderable\n    colorValue\n    displayOutOfStock {\n      displayValue\n      __typename\n    }\n    images {\n      href\n      alt\n      __typename\n    }\n  }\n}\n\nfragment CountdownClockFields on CountdownClock {\n  id\n  __typename\n}\n\nfragment FeaturesGridFields on FeaturesGrid {\n  id\n  __typename\n  featureRows {\n    id\n    primaryImage {\n      ...SanityImageFields\n      __typename\n    }\n    mobilePrimaryImage {\n      ...SanityImageFields\n      __typename\n    }\n    header\n    copy\n    ctas {\n      ...ctaFields\n      __typename\n    }\n    secondaryImage {\n      ...SanityImageFields\n      __typename\n    }\n    layout\n    __typename\n  }\n}\n\nfragment HotspotHeroFields on HotspotHero {\n  id\n  __typename\n}\n\nfragment ProductGroupFeaturesFields on ProductGroupFeatures {\n  id\n  __typename\n  productFeatures {\n    id\n    header\n    copy\n    horizontalAlignment\n    image {\n      ...SanityImageFields\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment QuoteCalloutFields on QuoteCallout {\n  id\n  __typename\n  header\n  copy\n  ctas {\n    ...ctaFields\n    __typename\n  }\n}\n\nfragment ShopCollectionFields on ShopCollection {\n  id\n  __typename\n}\n\nfragment SideBySideFields on SideBySide {\n  id\n  __typename\n  requiredTiles: tiles {\n    id\n    header\n    copy\n    backgroundImage {\n      ...SanityImageFields\n      __typename\n    }\n    ctas {\n      ...ctaFields\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment TrendingInlineFields on TrendingInline {\n  id\n  __typename\n  requiredTiles: tiles {\n    id\n    header\n    copy\n    overlay\n    backgroundImage {\n      ...SanityImageFields\n      __typename\n    }\n    ctas {\n      ...ctaFields\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment YouTubeVideoCarouselFields on YouTubeVideoCarousel {\n  id\n  playlistId\n  videoIds\n  autoplay\n  showThumbnails\n  __typename\n}\n\nfragment StyliticsCarouselFields on StyliticsCarousel {\n  __typename\n  id\n  header\n  tiles {\n    __typename\n    id\n    position\n    tile {\n      ...PromoTileFields\n      __typename\n    }\n  }\n  numberOfTiles\n  tileLayout\n  outfits {\n    id\n    image {\n      href\n      alt\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment PromoTileFields on PromoTile {\n  id\n  header\n  copy\n  textColor\n  backgroundColor\n  verticalAlignment\n  contentBelow\n  backgroundImage {\n    ...SanityImageFields\n    __typename\n  }\n  mobileBackgroundImage {\n    ...SanityImageFields\n    __typename\n  }\n  cta {\n    ...ctaFields\n    __typename\n  }\n}\n\nfragment ProductRecommenderFields on ProductRecommender {\n  __typename\n  id\n  header\n  type\n}\n\nfragment FeatureHeroFields on FeatureHero {\n  id\n  __typename\n  header\n  copy\n  footnote\n  backgroundColor\n  textColor\n  ctas {\n    ...ctaFields\n    __typename\n  }\n  optionalPrimaryImage: primaryImage {\n    ...SanityImageFields\n    __typename\n  }\n  primaryVideo {\n    id\n    source\n    mute\n    loop\n    autoplay\n    __typename\n  }\n  optionalSecondaryImage: secondaryImage {\n    ...SanityImageFields\n    __typename\n  }\n  secondaryVideo {\n    id\n    source\n    mute\n    loop\n    autoplay\n    __typename\n  }\n}\n\nfragment SignUpFormFields on SignUpForm {\n  id\n  __typename\n  header\n  copy\n  footnote\n  contactSource\n  disclaimerText\n  submitButtonText\n  submitButtonTextColor\n  submitButtonColor\n  fields\n  textColor\n  backgroundColor\n  successHeader\n  successCopy\n  successFootnote\n  ctas {\n    ...ctaFields\n    __typename\n  }\n  successImage {\n    ...SanityImageFields\n    __typename\n  }\n  mobileBackgroundImage {\n    ...SanityImageFields\n    __typename\n  }\n  formBackgroundImage: backgroundImage {\n    ...SanityImageFields\n    __typename\n  }\n}\n\nfragment InfoBannerFields on InfoBanner {\n  id\n  __typename\n  header\n  copy\n  footnote\n  optionalBackgroundImage: backgroundImage {\n    ...SanityImageFields\n    __typename\n  }\n  mobileBackgroundImage {\n    ...SanityImageFields\n    __typename\n  }\n  backgroundColor\n  textColor\n  ctas {\n    ...ctaFields\n    __typename\n  }\n}\n\nfragment LaunchCalendarFields on LaunchCalendar {\n  id\n  __typename\n  calendarContent {\n    ...CardFields\n    ...TileFields\n    __typename\n  }\n}\n\nfragment CardFields on Card {\n  id\n  __typename\n  style {\n    ...StyleFields\n    __typename\n  }\n  badge {\n    ...BadgeFields\n    __typename\n  }\n  image {\n    ...ImageFields\n    __typename\n  }\n  text {\n    ...TextFields\n    __typename\n  }\n  link {\n    ...LinkFields\n    __typename\n  }\n  ctas {\n    ...CallToActionFields\n    __typename\n  }\n}\n\nfragment BadgeFields on Badge {\n  label\n  color\n}\n\nfragment ImageFields on Image {\n  portrait {\n    ...SanityImageFields\n    __typename\n  }\n  square {\n    ...SanityImageFields\n    __typename\n  }\n  landscape {\n    ...SanityImageFields\n    __typename\n  }\n}\n\nfragment TextFields on Text {\n  header\n  copy\n  footnote\n  align\n  color\n}\n\nfragment StyleFields on Style {\n  background\n  border\n  rounded\n  shadow\n}\n\nfragment LinkFields on Link {\n  href\n  query\n  newtab\n}\n\nfragment CallToActionFields on CallToAction {\n  id\n  title\n  variant\n  outlined\n  width\n  link {\n    ...LinkFields\n    __typename\n  }\n}\n\nfragment TileFields on Tile {\n  id\n  __typename\n  aspectRatio\n  alignment {\n    vertical\n    horizontal\n    __typename\n  }\n  style {\n    ...StyleFields\n    __typename\n  }\n  image {\n    ...ImageFields\n    __typename\n  }\n  text {\n    ...TextFields\n    __typename\n  }\n  link {\n    ...LinkFields\n    __typename\n  }\n  ctas {\n    ...CallToActionFields\n    __typename\n  }\n}\n\nfragment IframeFields on Iframe {\n  __typename\n  id\n  src\n  fullScreen\n  height\n}\n\nfragment promoFields on ProductPromotion {\n  id\n  calloutMessage\n}\n";

    /// <summary>
    /// The four variables the document declares — <c>$id</c>, <c>$isDraft</c>, <c>$variationId</c>, <c>$src</c>.
    /// </summary>
    public static readonly string[] DeclaredVariables = { "id", "isDraft", "variationId", "src" };

    /// <summary>
    /// The two the sender actually fills. The other two are optional in the document and this class does not
    /// invent values for them: a draft product and a source override change what the query returns.
    /// </summary>
    public static readonly string[] SenderVariables = { "id", "variationId" };

    /// <summary>The request body the sender builds.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Ask for a product. <paramref name="origin"/> is the store's origin — the family never carries it — and the
    /// step refuses rather than guessing, because a guess here is a real request to a real server.
    /// </summary>
    public static async Task<(JObject? Product, string Error)> FetchAsync(
        FlowContext c, string? origin, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(origin))
            return (null, "storefront-api: no origin — this family posts a relative api/graphql and the image " +
                          "keeps the host above the senders");

        if (variables is null || variables["id"] is null || string.IsNullOrEmpty(variables["id"]!.ToString()))
            return (null, "storefront-api: no id to ask about");

        var url = origin!.TrimEnd('/') + "/" + Path;
        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url, Envelope(variables), "storefront-product", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "storefront-api: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "storefront-api: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var product = reply["data"]?["product"] as JObject ?? reply["data"] as JObject;
            return product is null ? (null, "storefront-api: no product in reply") : (product, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "storefront-api: " + ex.GetType().Name);
        }
    }
}
