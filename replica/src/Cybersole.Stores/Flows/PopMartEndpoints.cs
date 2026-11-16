namespace Cybersole.Stores.Flows;

/// <summary>
/// The Pop Mart storefront API, read out of the 5.18.32 image in R100 — <b>thirty-nine</b>
/// <c>/shop/v1/*</c> endpoints, verbatim.
///
/// <para>
/// The replica's <c>PopMartFlow</c> posted to <c>/api/cart/add</c> and <c>/api/order/submit</c>.  // inferred: no image evidence (R294)
/// Neither is in the image: the real surface is this family, and the names say exactly what the
/// flow needed — <c>/shop/v1/box/boxCart/addBoxListToCart</c> for the basket and
/// <c>/shop/v1/order/pre/v2/buyNow</c> for the order, with a payment desk for each provider
/// (Adyen, Alipay Global, PayPal, Stripe) hanging off <c>/shop/v1/shop/cash/desk/*</c>.
/// </para>
///
/// <para>
/// Pop Mart sells sealed boxes, so the "variant" is a box set: <c>box_set/preview</c> and
/// <c>box_set/extract</c> are how a buyer picks from a series without knowing the contents. That is
/// the mechanism the replica's flow never had.
/// </para>
/// </summary>
public static class PopMartEndpoints
{
    // ---- product / box
    public const string ProductDetails = "/shop/v1/shop/productDetails?spuId=";
    public const string BoxGoodsList = "/shop/v1/box/goodsListV2";
    public const string BoxSpuDetail = "/shop/v1/box/box_spu/detail";
    public const string BoxSetPreview = "/shop/v1/box/box_set/preview";
    public const string BoxSetExtract = "/shop/v1/box/box_set/extract";
    public const string BoxExtract = "/shop/v1/box/extract";

    // ---- cart
    public const string AddBoxListToCart = "/shop/v1/box/boxCart/addBoxListToCart";
    public const string ShoppingCartDataList =
        "/shop/v1/shoppingcart/shoppingCartDataList?actionType=";

    // ---- order
    public const string BuyNow = "/shop/v1/order/pre/v2/buyNow";
    public const string OrderCounter = "/shop/v1/order/pre/counter";
    public const string CanPlaceOrder = "/shop/v1/shop/can/place/order";
    public const string OrderList = "/shop/v1/order/list?currentPage=1&pageSize=20";
    public const string OrderDetail = "/shop/v1/order/v2/detailV2?orderNo=";

    // ---- payment desk, one path per provider
    public const string AdyenDetails = "/shop/v1/shop/adyen/details";
    public const string CashDeskAdyenDetails = "/shop/v1/shop/cash/desk/adyen/details";
    public const string CashDeskAdyenPay = "/shop/v1/shop/cash/desk/adyen/pay";
    public const string CashDeskAlipayGlobalPay = "/shop/v1/shop/cash/desk/alipayGlobal/pay";
    public const string CashDeskPayPalPay = "/shop/v1/shop/cash/desk/paypal/pay";
    public const string CashDeskStripeSession = "/shop/v1/shop/cash/desk/stripe/customerSession";
    public const string CashDeskStripePay = "/shop/v1/shop/cash/desk/stripe/pay";
    public const string CashDeskQuery = "/shop/v1/shop/cash/desk/pay/query";

    // ---- draws and tickets
    public const string DrawScratchDetail = "/shop/v1/drawScratch/detail?uniqCode=";
    public const string DrawScratchChooseGoods = "/shop/v1/drawScratch/chooseGoods";
    public const string DrawScratchDraw = "/shop/v1/drawScratch/draw";
    public const string MegaDrawHit = "/shop/v1/drawScratch/megaDraw/hit";
    public const string LuckyPointsDraw = "/shop/v1/redeem/lucky_points_redeem_draw";
    public const string PointsRedeemDraw = "/shop/v1/redeem/points_redeem_draw";
    public const string StoreOfflineDrawInfo = "/shop/v1/storeOfflineDraw/info?alias=";
    public const string StoreOfflineDrawJoin = "/shop/v1/storeOfflineDraw/join";
    public const string StoreOfflineDrawJoinResult = "/shop/v1/storeOfflineDraw/joinResult?alias=";
    public const string StoreTicketDates = "/shop/v1/store_ticket/dateList";
    public const string StoreTicketMainPage = "/shop/v1/store_ticket/mainPage?uniqID=";

    /// <summary>
    /// Reserving a store ticket slot.
    ///
    /// <para>
    /// R890. Missing until now: enumerating every <c>/shop/v1/</c> literal in the image yields forty-one paths, this
    /// file held thirty-nine, and none of its constants was absent from the image. These two are the whole of the gap.
    /// </para>
    ///
    /// <para>
    /// What is <b>not</b> known is the request body a reservation posts, so no step uses these yet — the constant is
    /// recorded because the path is an observation, and an endpoint with no caller is more honest than a step that
    /// posts an invented body.
    /// </para>
    /// </summary>
    public const string StoreTicketReserve = "/shop/v1/store_ticket/reserve";

    /// <summary>The session list for a store ticket. Same provenance and same caveat as <see cref="StoreTicketReserve"/>.</summary>
    public const string StoreTicketSessionList = "/shop/v1/store_ticket/sessionList";

    // ---- the in-store family, /store/v1/ rather than /shop/v1/
    //
    // R891. R890 established that GetInstoreOrders' endpoint was not under /shop/v1/, which narrowed the question to
    // "where is it not". Enumerating order-shaped paths across the whole image found it at a different prefix
    // entirely, and the prefix turns out to hold five paths rather than one.
    //
    // This is why the anchor matters when scanning: a loose path pattern over the whole pool returned GUIDs and
    // base64 fragments, and anchoring on the word "order" found the endpoint in one pass.
    public const string InstoreCartAdd = "/store/v1/store/cart/add";
    public const string InstoreCartDelete = "/store/v1/store/cart/del";
    public const string InstoreCartList = "/store/v1/store/cart/listByStore?actionType=1&GID=";

    /// <summary>Step <c>GetInstoreOrders</c>. The query shape is fixed in the constant, so the step needs no invented body.</summary>
    public const string InstoreOrderList = "/store/v1/store/order/listV3?currentPage=1&status=1&pageSize=20";

    /// <summary>Step <c>FindProductInstore</c> — the image's ordinal 76, which R882 saw next to FindProduct.</summary>
    public const string InstoreProductDetail = "/store/v1/store/product/detail?storeId=";

    // ---- promotions and missions
    public const string CouponsList = "/shop/v1/coupons/list";
    public const string CouponsVerify = "/shop/v1/coupons/verify";
    public const string PromotionList = "/shop/v1/promotion/getList";
    public const string FreightResult = "/shop/v1/freight/result";
    public const string MissionList = "/shop/v1/mission/list?group_name=mission_center";
    public const string MissionClaimReward = "/shop/v1/mission/claim_reward";
    public const string MissionCheckIn = "/shop/v1/mission/trigger/check_in";

    /// <summary>All thirty-nine, in the order the image lists them.</summary>
    public static readonly IReadOnlyList<string> All = new[]
    {
        AddBoxListToCart, BoxSetExtract, BoxSetPreview, BoxSpuDetail, BoxExtract, BoxGoodsList,
        CouponsList, CouponsVerify,
        DrawScratchChooseGoods, DrawScratchDetail, DrawScratchDraw, MegaDrawHit,
        FreightResult, MissionClaimReward, MissionList, MissionCheckIn,
        OrderList, OrderCounter, BuyNow, OrderDetail,
        PromotionList, LuckyPointsDraw, PointsRedeemDraw,
        AdyenDetails, CanPlaceOrder, CashDeskAdyenDetails, CashDeskAdyenPay,
        CashDeskAlipayGlobalPay, CashDeskQuery, CashDeskStripeSession, CashDeskStripePay,
        CashDeskPayPalPay, ProductDetails, ShoppingCartDataList,
        StoreOfflineDrawInfo, StoreOfflineDrawJoin, StoreOfflineDrawJoinResult,
        StoreTicketDates, StoreTicketMainPage,
    };

    /// <summary>The two paths the replica invented, kept as data so a test can forbid them.</summary>
    public static readonly IReadOnlyList<string> Invented = new[]
    {
        "/api/cart/add", "/api/order/submit", "/api/stock",  // inferred: no image evidence (R294)
    };

    /// <summary>True when <paramref name="path"/> starts with one of the thirty-nine.</summary>
    public static bool IsKnown(string? path) =>
        !string.IsNullOrEmpty(path) &&
        All.Any(e => path.StartsWith(e, StringComparison.Ordinal));
}
