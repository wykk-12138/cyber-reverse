namespace Cybersole.Stores.Flows;

/// <summary>
/// The residual hostless paths: the ones R901's canonical measurement found in the image with no owning store and
/// no literal in the replica. R903 closes the set R902 started.
///
/// <para>
/// <b>What is observed.</b> Eleven path literals. They cluster into five concerns: order submission, product and bag
/// reads, legacy account access, verification codes, card capture, 3-D Secure fingerprint submission, and an OTP
/// check under <c>/shield/</c>.
/// </para>
///
/// <para>
/// <b>What is unknown, and it is the same gap R902 recorded.</b> No literal holding any of these also holds a host,
/// so none of them can be attributed to a store. The names are generic enough that several stores could serve the
/// same paths, and nothing recovered distinguishes them.
/// </para>
///
/// <para>
/// <b>Two are worth singling out.</b> <see cref="ShieldVerifyOtp"/> sits under <c>/shield/</c>, which reads as a
/// protection service rather than a storefront, so it belongs to the anti-bot layer rather than to a checkout flow —
/// that priority is the one YG put second. <see cref="ThreeDs2Fingerprint"/> carries the token in its query, which
/// means the device fingerprint is the input and not something this layer computes.
/// </para>
///
/// <para>
/// <b>What is absent.</b> Bodies, responses, authentication and callers, as with R902's ten. No step uses these.
/// </para>
/// </summary>
public static class SharedCommerceEndpoints
{
    /// <summary>Order submission at the platform level, distinct from a store's own cart endpoint.</summary>
    public const string CheckoutOrders = "/checkout/v1/orders";

    /// <summary>
    /// 3-D Secure 2 fingerprint submission. The token arrives in the query, so the fingerprint is supplied by a caller
    /// that already has one.
    /// </summary>
    public const string ThreeDs2Fingerprint = "/checkoutshopper/v1/submitThreeDS2Fingerprint?token=";

    /// <summary>The bag — this platform's word for a cart, which is why the replica's cart classes never matched it.</summary>
    public const string CommerceBags = "/commerce/v1/bags";

    /// <summary>The product read on the same platform.</summary>
    public const string CommerceProducts = "/commerce/v1/products";

    /// <summary>Sign-in on the legacy API, which some stores still answer alongside the newer one.</summary>
    public const string LegacyLogin = "/legacy/v1/account/login";

    /// <summary>The legacy API's view of the signed-in user.</summary>
    public const string LegacyUsersMe = "/legacy/v1/users/me";

    /// <summary>Verification codes. Plural in the path, unlike R902's <c>/customer/v1/verification/send</c>.</summary>
    public const string MarketingVerificationCodes = "/marketing/v1/verificationcodes";

    /// <summary>Card capture — storing a card rather than charging it, judging by the name.</summary>
    public const string CardCapture = "/payments-vas/v1/card-capture";

    /// <summary>The product detail page read.</summary>
    public const string ProductCorePdp = "/product-core/v1/pdp";

    /// <summary>The same read narrowed to a SKU.</summary>
    public const string ProductCorePdpSku = "/product-core/v1/pdp/sku";

    /// <summary>
    /// OTP verification under <c>/shield/</c>. This is the one that belongs to the anti-bot priority: the path names a
    /// protection service, not a storefront.
    /// </summary>
    public const string ShieldVerifyOtp = "/shield/v1/verify_otp";

    /// <summary>Every path above.</summary>
    public static readonly IReadOnlyList<string> All = new[]
    {
        CheckoutOrders, ThreeDs2Fingerprint, CommerceBags, CommerceProducts,
        LegacyLogin, LegacyUsersMe, MarketingVerificationCodes, CardCapture,
        ProductCorePdp, ProductCorePdpSku, ShieldVerifyOtp,
    };

    /// <summary>
    /// True: none of these shares a literal with a host, so the owning store is unknown rather than unconfirmed.
    /// </summary>
    public const bool OwnerIsUnknown = true;

    /// <summary>Eleven, which is what the image holds after R902's ten were taken out of the set.</summary>
    public const int RecoveredPathCount = 11;

    /// <summary>
    /// The subset that belongs to the anti-bot priority rather than to a checkout flow, named so a later round can
    /// count that priority's coverage without re-reading every path.
    /// </summary>
    public static readonly IReadOnlyList<string> AntiBotRelated = new[]
    {
        ShieldVerifyOtp, ThreeDs2Fingerprint,
    };
}
