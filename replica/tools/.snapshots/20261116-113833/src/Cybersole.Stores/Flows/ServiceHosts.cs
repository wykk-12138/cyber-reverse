using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Third-party service hosts the 5.18.32 image talks to, read out in R114 — the layer below the
/// store flows, recorded verbatim because every one of them is a real integration the replica either
/// has or does not.
///
/// <code>
/// Scheels mobile API   https://mobile-api.scheels.com/v5/auth/guest
///                      https://mobile-api.scheels.com/v5/products/
/// END Clothing REST    https://api2.endclothing.com/rest/V1
/// AYCD inbox           https://inbox-api.aycd.io/api/v1/user/verify
///                      https://inbox-api.aycd.io/api/v1/tasks/mail/create
///                      https://inbox-api.aycd.io/api/v1/tasks/completed?group=
/// Parallax Systems     https://api.parallaxsystems.io/gen
///                      https://api.parallaxsystems.io/holdcaptcha
/// Google Maps          https://maps.googleapis.com/maps/api/geocode/json?address=
///                      https://maps.googleapis.com/maps/api/js?libraries=places&amp;key=
/// </code>
///
/// <para>
/// Three of these are not storefronts at all and are worth naming plainly:
/// </para>
///
/// <list type="bullet">
/// <item><b>Parallax Systems</b> — <c>/gen</c> and <c>/holdcaptcha</c>. The image carries the
/// property names <c>GenEndpoint</c> and <c>HoldCaptchaEndpoint</c> next to them, so this is a
/// captcha service the tool holds a slot with before solving, not a token generator.</item>
/// <item><b>AYCD inbox</b> — the same three endpoints the Settings → IMAP page talks about: verify the
/// key, create a mail task, poll completed tasks by group.</item>
/// <item><b>Google Maps</b> — geocode and Places autocomplete, which is how a checkout fills an
/// address field from a postcode rather than from a dropdown.</item>
/// </list>
///
/// <para>
/// <b>Scheels has two APIs.</b> R103 recorded the Frontastic action hub
/// (<c>apihub.scheels.com/frontastic/action/…</c>); this is the <b>mobile</b> one, v5, with a guest
/// auth endpoint and a products endpoint. A store that has both is a store whose app and web flows
/// differ — which is the same shape the Demandware <c>App</c>/<c>Dw</c> step lists showed in R112.
/// </para>
/// </summary>
public static class ServiceHosts
{
    /// <summary>
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
                // SubmitOrderApp was mapped to a Scheels order endpoint in R115; R127 removed it
                // because that endpoint belongs to Nike. The step stays unmapped rather than guessed.
            };

        /// <summary>Step names that read as the web-side half, with the hub action each matches.</summary>
        public static readonly IReadOnlyDictionary<string, string> WebSteps =
            new Dictionary<string, string>(System.StringComparer.Ordinal)
            {
                ["Login"] = RetailApiFamilies.ScheelsFrontastic.Login,
                ["GetProduct"] = RetailApiFamilies.ScheelsFrontastic.GetProduct,
                ["AddToCart"] = RetailApiFamilies.ScheelsFrontastic.AddToCart,
                ["Checkout"] = RetailApiFamilies.ScheelsFrontastic.Checkout,
                ["CompleteDetailsCheckout"] = RetailApiFamilies.ScheelsFrontastic.CompleteDetailsCheckout,
                ["SignifydStepUpCode"] = RetailApiFamilies.ScheelsFrontastic.SignifydStepUpCode,
                ["CompleteSignifydStepUp"] = RetailApiFamilies.ScheelsFrontastic.CompleteSignifydStepUp,
            };

        /// <summary>How this map was drawn — recorded so it is never mistaken for a capture.</summary>
        public const string Evidence = "name correlation between the *App step list and mobile-api/v5; " +
                                       "no request capture; hub map from R103's Frontastic table";
    }

    /// <summary>END Clothing's Magento REST API.</summary>
    public static class EndClothing
    {
        public const string Base = "https://api2.endclothing.com";
        public const string Rest = Base + "/rest/";
        public const string RestV1 = Base + "/rest/V1";
        public static readonly IReadOnlyList<string> All = new[] { Base, Rest, RestV1 };
    }

    /// <summary>AYCD's inbox service — the Settings → IMAP integration's backend.</summary>
    public static class AycdInbox
    {
        public const string Base = "https://inbox-api.aycd.io/api/v1";
        public const string Verify = Base + "/user/verify";
        public const string CreateMail = Base + "/tasks/mail/create";
        public const string Completed = Base + "/tasks/completed?group=";
        public static readonly IReadOnlyList<string> All = new[] { Verify, CreateMail, Completed };
    }

    /// <summary>Parallax Systems — a captcha service with a slot-holding endpoint.</summary>
    public static class ParallaxSystems
    {
        public const string Base = "https://api.parallaxsystems.io";
        /// <summary>Named <c>GenEndpoint</c> in the image.</summary>
        public const string Gen = Base + "/gen";
        /// <summary>Named <c>HoldCaptchaEndpoint</c> in the image — hold a slot, then solve.</summary>
        public const string HoldCaptcha = Base + "/holdcaptcha";
        public static readonly IReadOnlyList<string> All = new[] { Gen, HoldCaptcha };
    }

    /// <summary>Google's geocode and Places endpoints.</summary>
    public static class GoogleMaps
    {
        public const string Geocode = "https://maps.googleapis.com/maps/api/geocode/json?address=";
        public const string PlacesJs = "https://maps.googleapis.com/maps/api/js?libraries=places&key=";
        public const string Autocomplete =
            "https://maps.googleapis.com/maps/api/place/js/AutocompletionService.GetPredictions?1s";
        public static readonly IReadOnlyList<string> All = new[] { Geocode, PlacesJs, Autocomplete };
    }

    /// <summary>Every host literal in this layer.</summary>
    public static readonly IReadOnlyList<string> All = ScheelsMobile.All
        .Concat(EndClothing.All)
        .Concat(AycdInbox.All)
        .Concat(ParallaxSystems.All)
        .Concat(GoogleMaps.All)
        .ToList();

    /// <summary>The five services, by name.</summary>
    public static readonly IReadOnlyList<string> Services = new[]
    {
        "ScheelsMobile", "EndClothing", "AycdInbox", "ParallaxSystems", "GoogleMaps",
    };

    /// <summary>True when the URL belongs to one of the five.</summary>
    public static bool IsKnown(string? url) =>
        !string.IsNullOrEmpty(url) && All.Contains(url, System.StringComparer.Ordinal);
}
