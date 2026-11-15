import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\ServiceHosts.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    /// <summary>Scheels' mobile API (v5) — the app-side counterpart of the Frontastic hub.</summary>
    public static class ScheelsMobile
    {
        public const string Base = "https://mobile-api.scheels.com";
        public const string GuestAuth = Base + "/v5/auth/guest";
        public const string Products = Base + "/v5/products/";
        public static readonly IReadOnlyList<string> All = new[] { GuestAuth, Products };
    }'''

new = '''    /// <summary>
    /// Scheels' mobile API (v5) — the app-side counterpart of the Frontastic hub.
    ///
    /// <para>
    /// R115 adds the third endpoint: <c>/v5/Order/</c>. Three calls is exactly the shape the app-side
    /// step names describe — authenticate as a guest, look a product up, place an order — which is why
    /// the step-to-host mapping below is drawn where the names agree and nowhere else.
    /// </para>
    /// </summary>
    public static class ScheelsMobile
    {
        public const string Base = "https://mobile-api.scheels.com";
        public const string GuestAuth = Base + "/v5/auth/guest";
        public const string Products = Base + "/v5/products/";
        public const string Orders = Base + "/v5/Order/";
        public static readonly IReadOnlyList<string> All = new[] { GuestAuth, Products, Orders };
    }

    /// <summary>
    /// The two Scheels APIs side by side, with the step names that plausibly land on each.
    ///
    /// <para>
    /// <b>This is a name correlation, not a capture.</b> <c>FindProductApp</c> and
    /// <c>mobile-api/v5/products/</c> agree on the noun; <c>SubmitOrderApp</c> and <c>/v5/Order/</c>
    /// likewise. What is <i>not</i> claimed is that these are the only calls each API serves, or that
    /// the app path is used for Scheels specifically rather than by some other store on the same
    /// engine. Both lists are recorded so a later capture can confirm or refute them.
    /// </para>
    /// </summary>
    public static class DualApi
    {
        /// <summary>Step names that read as the app-side half, with the mobile endpoint each matches.</summary>
        public static readonly IReadOnlyDictionary<string, string> AppSteps =
            new Dictionary<string, string>(System.StringComparer.Ordinal)
            {
                ["StartAppFast"] = ScheelsMobile.GuestAuth,
                ["StartAppSafe"] = ScheelsMobile.GuestAuth,
                ["FindProductApp"] = ScheelsMobile.Products,
                ["AddToCartApp"] = ScheelsMobile.Products,
                ["SubmitOrderApp"] = ScheelsMobile.Orders,
            };

        /// <summary>Step names that read as the web-side half, with the hub action each matches.</summary>
        public static readonly IReadOnlyDictionary<string, string> WebSteps =
            new Dictionary<string, string>(System.StringComparer.Ordinal)
            {
                ["Login"] = ScheelsFrontastic.Login,
                ["GetProduct"] = ScheelsFrontastic.GetProduct,
                ["AddToCart"] = ScheelsFrontastic.AddToCart,
                ["Checkout"] = ScheelsFrontastic.Checkout,
                ["CompleteDetailsCheckout"] = ScheelsFrontastic.CompleteDetailsCheckout,
                ["SignifydStepUpCode"] = ScheelsFrontastic.SignifydStepUpCode,
                ["CompleteSignifydStepUp"] = ScheelsFrontastic.CompleteSignifydStepUp,
            };

        /// <summary>How this map was drawn — recorded so it is never mistaken for a capture.</summary>
        public const string Evidence = "name correlation between the *App step list and mobile-api/v5; " +
                                       "no request capture; hub map from R103's Frontastic table";
    }'''

if old not in t:
    raise SystemExit("ScheelsMobile block not found")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("Scheels mobile /v5/Order/ added, dual-API map recorded")
