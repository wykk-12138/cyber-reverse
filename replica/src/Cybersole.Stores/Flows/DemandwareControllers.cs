namespace Cybersole.Stores.Flows;

/// <summary>
/// The Salesforce Commerce Cloud (Demandware) controller vocabulary found in the 5.18.32 image,
/// read out in R94 by extracting UTF-16 literals straight from the PE — the IDA database was lost in
/// R93, so this is the no-IDA route to the same evidence.
///
/// <para>
/// The string pool glues adjacent literals together (<c>Cart-AddProducton</c> is
/// <c>Cart-AddProduct</c> followed by the tail of the next one), so the names below are the ones
/// that appear cleanly, with the glued variants used only as corroboration.
/// </para>
///
/// <para>
/// <b>Why this exists:</b> the replica's <c>DemandwareFlow</c> posted to <c>Checkout-Submit</c>,
/// <c>Checkout-SubmitShipping</c> and <c>Checkout-SubmitPayment</c>. None of those three strings is
/// in the image. The real controllers are <c>CheckoutServices-*</c> and
/// <c>CheckoutShippingServices-SubmitShipping</c> — a different family entirely, which is the same
/// shape of mistake the Nike flow had with <c>buy/orders/v2</c>.
/// </para>
/// </summary>
public static class DemandwareControllers
{
    // ---- cart
    public const string CartAddProduct = "Cart-AddProduct";
    public const string CartGet = "Cart-Get";
    public const string CartMiniCartShow = "Cart-MiniCartShow";
    public const string CartAddCoupon = "Cart-AddCoupon";
    public const string CartRemoveProductLineItem = "Cart-RemoveProductLineItem";
    public const string CartEditProductLineItem = "Cart-EditProductLineItem";

    // ---- checkout
    public const string CheckoutBegin = "Checkout-Begin";
    public const string SubmitCustomer = "CheckoutServices-SubmitCustomer";
    public const string SubmitShipping = "CheckoutShippingServices-SubmitShipping";
    public const string SubmitPayment = "CheckoutServices-SubmitPayment";
    public const string PlaceOrder = "CheckoutServices-PlaceOrder";

    /// <summary>
    /// The place-order query when a Cardinal device-fingerprint reference exists (0x146AAF3F0).
    ///
    /// <para>
    /// <b>Observed</b> in <c>sub_140A729F0</c> (3,138 bytes), whose whole constant set is this literal, the
    /// undefined-variant below, the storefront prefix <c>on/demandware.store/Sites-</c> (0x147107D30), the
    /// <c>-Site/</c> joiner (0x146AA36D0), <c>0_</c> (0x146AC39D0), <c>NBJP</c> (0x146E10D68) and the report line
    /// <c>Submit order</c> (0x146EA00F0). The reference is Cardinal's DFReferenceId, the device-fingerprint id the
    /// 3-D Secure MPI hands back — so this is where an MPI fingerprint rides into a Demandware checkout.
    /// </para>
    /// </summary>
    public const string PlaceOrderQueryWithFingerprint =
        "?termsconditions=true&DFReferenceId=";

    /// <summary>
    /// The place-order query when there is no fingerprint (0x146AAF488): the literal says
    /// <c>undefined</c>, not an empty value — the storefront's own quirk, kept verbatim.
    /// </summary>
    public const string PlaceOrderQueryWithoutFingerprint = "?termsconditions=undefined";

    /// <summary>
    /// The place-order path plus the query that belongs to it. Pass the fingerpint id when the 3-D Secure device
    /// fingerprint ran, and null when it did not; the two shapes are the image's, not a choice of ours.
    /// </summary>
    public static string PlaceOrderPathWith(string? dfReferenceId) =>
        "/" + PlaceOrder + (string.IsNullOrEmpty(dfReferenceId)
            ? PlaceOrderQueryWithoutFingerprint
            : PlaceOrderQueryWithFingerprint + Uri.EscapeDataString(dfReferenceId!));

    // ---- account and product
    public const string AccountLogin = "Account-Login";
    public const string CsrfGenerate = "CSRF-Generate";
    public const string ProductVariation = "Product-Variation";
    public const string ProductShow = "Product-Show";
    public const string WishlistAddToCart = "Wishlist-AddToCart";

    // ---- payment
    public const string AdyenAuthorize = "AdyenUpgrade-Authorize";

    // ---- R117: five more the R94 window missed, plus the Adyen component family
    /// <summary>The billing-address submit — the step list's <c>SubmitBillingAddress</c>.</summary>
    public const string SubmitBilling = "CheckoutServices-SubmitBilling";

    /// <summary>Two-phase payment: this is the confirmation after the submit.</summary>
    public const string PaymentAuthorization = "CheckoutServices-PaymentAuthorization";

    /// <summary>Fetches the checkout's order model — what a "get checkout" really returns.</summary>
    public const string FetchOrderModel = "CheckoutServices-FetchOrderModel";

    /// <summary>Cash-on-delivery submit, the one non-card path.</summary>
    public const string SubmitCash = "CheckoutServices-SubmitCash";

    /// <summary>Changing the shipping method after the consignment exists.</summary>
    public const string UpdateShippingMethod = "CheckoutShippingServices-UpdateShippingMethod";

    /// <summary>Adyen's 3-D Secure 2 hand-off.</summary>
    public const string Adyen3Ds2 = "Adyen-Adyen3DS2";

    /// <summary>Adyen's payment-details call, used by the component-based flow.</summary>
    public const string AdyenPaymentsDetails = "Adyen-PaymentsDetails";

    // ---- R125: two the payment-flow literal pinned
    /// <summary>Express-checkout shopper details — the Adyen PayPal flow's step 37.</summary>
    public const string AdyenSaveExpressShopperDetails = "Adyen-SaveExpressShopperDetails";

    /// <summary>The shopper-IP endpoint a risk check reads.</summary>
    public const string ShopperInfoIp = "ShopperInfo-IP";

    // ---- R126: four the census found, each a clean name with a plausible tail
    /// <summary>Editing a line's quantity through the cart controller rather than the minicart.</summary>
    public const string CartUpdateProduct = "Cart-UpdateProduct";

    /// <summary>Showing a cart layer — the AJAX panel, not a page.</summary>
    public const string CartShowLayer = "Cart-ShowLayer";

    /// <summary>Adyen's component payment submit, the counterpart of <c>PaymentFromComponent</c>.</summary>
    public const string AdyenPaymentFromComponent = "Adyen-PaymentFromComponent";

    /// <summary>Adyen's PayPal order patch, used by the express flow's step 35.</summary>
    public const string AdyenPayPalPatchOrder = "Adyen-PayPalPatchOrder";

    /// <summary>Adyen's 3-D Secure 2 authorize, distinct from the generic authorize.</summary>
    public const string AdyenAuthorize3Ds2 = "Adyen-Authorize3DS2";

    // ---- raffle / sale entry (R95, from the full URL templates)
    public const string SaleSignupSubmit = "SaleRegistration-SignupSubmit";
    public const string SaleConfig = "SaleRegistration-Config";

    // ---- R1169: three PayPal controller actions the image carries (the literals were found in R1162)
    /// <summary>Reads the PayPal purchase unit for the cart. Verb observed as GET (0x146ab044c).</summary>
    public const string PaypalGetPurchaseUnit = "Paypal-GetPurchaseUnit";

    /// <summary>The order-id lookup; the caller appends <c>?csrf_token=</c> (0x146ab03ec).</summary>
    public const string PaypalGetPaypalOrderId = "Paypal-GetPaypalOrderId";

    /// <summary>The order-details lookup; the caller appends <c>?orderId=</c> (0x146ab0394).</summary>
    public const string PaypalGetOrderDetails = "Paypal-GetOrderDetails";

    // ---- R1173: the two brand stores' preload controllers
    //
    // R1172 established that Jacquemus and Maison Margiela are stores this image supports - each has a host
    // or a regional family, a display name, a region code and per-store log categories - and that the
    // replica has neither store. Their preload controllers are the first piece of them that can be written
    // down without inventing anything: both are SFCC *controller-action* names, so they compose through
    // Controller() exactly like the others. The steps that call them are still unobserved, which is why
    // only the names are here.
    //
    /// <summary>The Jacquemus storefront's preload action (0x146dd3ba8).</summary>
    public const string JacquemusPreload = "Jacquemus-Preload";

    /// <summary>The Maison Margiela storefront's preload action (0x146dfcbe0).</summary>
    public const string MargielaPreload = "Margiela-Preload";

    /// <summary>Funko CrowdTwist fan-rewards registration endpoint (<c>0x140a19360</c>).</summary>
    public const string CrowdTwistRegister = "CrowdTwist-Register";

    /// <summary>The controllers, in the order the checkout chain uses them.</summary>
    public static readonly IReadOnlyList<string> CheckoutChain = new[]
    {
        CartAddProduct, CartGet, CheckoutBegin,
        SubmitCustomer, SubmitShipping, SubmitPayment, PlaceOrder,
    };

    /// <summary>Everything confirmed in the image.</summary>
    public static readonly IReadOnlyList<string> All = new[]
    {
        CartAddProduct, CartGet, CartMiniCartShow, CartAddCoupon,
        CartRemoveProductLineItem, CartEditProductLineItem,
        CheckoutBegin, SubmitCustomer, SubmitShipping, SubmitPayment, PlaceOrder,
        AccountLogin, CsrfGenerate, ProductVariation, ProductShow, WishlistAddToCart,
        AdyenAuthorize, SaleSignupSubmit, SaleConfig,
        SubmitBilling, PaymentAuthorization, FetchOrderModel, SubmitCash,
        UpdateShippingMethod, Adyen3Ds2, AdyenPaymentsDetails,
        AdyenSaveExpressShopperDetails, ShopperInfoIp,
        CartUpdateProduct, CartShowLayer, AdyenPaymentFromComponent,
        AdyenPayPalPatchOrder, AdyenAuthorize3Ds2,
        PaypalGetPurchaseUnit, PaypalGetPaypalOrderId, PaypalGetOrderDetails,
        JacquemusPreload, MargielaPreload, CrowdTwistRegister,
    };

    /// <summary>The site ids the image names, e.g. <c>Sites-crocs_-Site</c>.</summary>
    public static readonly IReadOnlyList<string> Sites = new[]
    {
        "asics", "cpcompany", "crocs_", "crocs_on", "crocs_s", "mjsfra", "StoneNA", "vans",
    };

/// <summary>
    /// The store host each site id belongs to, where the image spells both out. Only the three the
    /// image actually pairs are here — asics / crocs / vans appear as site ids without their host in
    /// the same literal, so they are deliberately absent rather than guessed.
    /// </summary>
    public static readonly IReadOnlyDictionary<string, string> Hosts =
        new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["cpcompany"] = "www.cpcompany.com",
            ["mjsfra"] = "www.marcjacobs.com",
            ["StoneNA"] = "www.stoneisland.com",
        };

    /// <summary>
    /// The URL shape the image spells out end to end, verbatim:
    /// <code>
    /// https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Cart-AddProduct
    /// https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Product-Variation?pid=
    /// https://www.cpcompany.com/on/demandware.store/Sites-cpcompany-Site/
    /// https://www.stoneisland.com/on/demandware.store/Sites-StoneNA-Site/en_US/SaleRegistration-SignupSubmit
    /// </code>
    /// The locale segment is <c>default</c> on some stores and <c>en_US</c> on others, so it is a
    /// parameter rather than a constant.
    /// </summary>
    public static string SitePath(string host, string site, string locale, string controller) =>
        $"https://{host}/on/demandware.store/Sites-{site}-Site/{locale}/{controller}";

    /// <summary><c>SitePath</c> with the locale left out, as the cpcompany template does.</summary>
    public static string SiteRoot(string host, string site) =>
        $"https://{host}/on/demandware.store/Sites-{site}-Site/";

    /// <summary>True when <paramref name="controller"/> is one of the confirmed names.</summary>
    public static bool IsKnown(string? controller) =>
        !string.IsNullOrEmpty(controller) && All.Contains(controller, StringComparer.Ordinal);

    /// <summary>
    /// The three names the replica used that the image does not contain. Kept as data so a test can
    /// assert they never come back.
    /// </summary>
    public static readonly IReadOnlyList<string> Invented = new[]
    {
        "Checkout-Submit", "Checkout-SubmitShipping", "Checkout-SubmitPayment",
    };
}
