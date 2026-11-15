import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\ServiceHosts.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    /// <summary>
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
    }'''

new = '''    /// <summary>
    /// Scheels' mobile API (v5) — the app-side counterpart of the Frontastic hub. <b>Two endpoints.</b>
    ///
    /// <para>
    /// <b>R127 correction.</b> R115 recorded a third endpoint,
    /// <c>https://mobile-api.scheels.com/v5/Order/</c>, by appending a path it had seen to the Scheels
    /// base. The census showed the path belongs elsewhere: the only literal containing <c>v5/Order/</c>
    /// in the whole image is
    /// </para>
    ///
    /// <code>
    /// https://www.nike.com/gs/checkout-api/api/v5/Order/
    /// </code>
    ///
    /// <para>
    /// — Nike's order endpoint, not Scheels'. The Scheels mobile API is
    /// <c>/v5/auth/guest</c> and <c>/v5/products/</c>, exactly as its 17-path hub sibling suggests a
    /// store whose app does far less than its web front end. The invented third endpoint has been
    /// removed, and <c>DualApi.AppSteps["SubmitOrderApp"]</c> with it.
    /// </para>
    /// </summary>
    public static class ScheelsMobile
    {
        public const string Base = "https://mobile-api.scheels.com";
        public const string GuestAuth = Base + "/v5/auth/guest";
        public const string Products = Base + "/v5/products/";
        public static readonly IReadOnlyList<string> All = new[] { GuestAuth, Products };
    }'''

if old not in t:
    raise SystemExit("ScheelsMobile block not found")
t = t.replace(old, new, 1)

# the dual map claimed SubmitOrderApp → Scheels orders; that target no longer exists
old_map = '''                ["AddToCartApp"] = ScheelsMobile.Products,
                ["SubmitOrderApp"] = ScheelsMobile.Orders,
            };'''
new_map = '''                ["AddToCartApp"] = ScheelsMobile.Products,
                // SubmitOrderApp was mapped to a Scheels order endpoint in R115; R127 removed it
                // because that endpoint belongs to Nike. The step stays unmapped rather than guessed.
            };'''
if old_map not in t:
    raise SystemExit("dual map anchor missing")
t = t.replace(old_map, new_map, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("Scheels mobile corrected to two endpoints")
