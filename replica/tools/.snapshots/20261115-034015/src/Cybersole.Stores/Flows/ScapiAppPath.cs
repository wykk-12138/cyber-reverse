using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Demandware's fifteen-step dual flow, split by <b>which half each step has an endpoint for</b> —
/// the finding of R124, and the reason the dual path is not two complete paths.
///
/// <para>
/// The dual step list (<see cref="StoreFlowSteps.DemandwareDual"/>) keeps an <c>App</c> vocabulary
/// beside a <c>Dw</c> one. Pairing those steps against the two endpoint families shows the split is
/// not "app does everything, dw does everything":
/// </para>
///
/// <code>
/// App side   StartAppFast / StartAppSafe → /scapi/ShopperLogin/getAccessToken
///            AddToCartApp               → /scapi/ShopperBaskets/addItemToBasket
/// Dw side    GetSessionDw / GetCartDw    → demandware.store Cart-Get
///            AddToCartAppDw              → demandware.store Cart-AddProduct
///            ApplyDiscountApp / GetCheckoutApp / GetRatesApp / SubmitOrderApp → no SCAPI endpoint
/// </code>
///
/// <para>
/// <b>There is no SCAPI orders endpoint in the image.</b> The ShopperBaskets family runs
/// create → add → update ×4, and ShopperLogin runs two calls, and that is all: nothing creates an
/// order. So a store that starts on the app path cannot finish there — it must cross back to the
/// classic controllers for checkout and the order, which is exactly what a fifteen-step flow with both
/// vocabularies describes.
/// </para>
///
/// <para>
/// That also explains the step names: the four unpaired <c>*App</c> steps are the ones the image
/// performs against the <b>site's own</b> endpoints rather than SCAPI — headless app calls proxied by
/// the storefront, which is why no SCAPI path names them.
/// </para>
/// </summary>
public static class ScapiAppPath
{
    /// <summary>App-side steps with a real SCAPI endpoint.</summary>
    public static readonly IReadOnlyDictionary<string, string> AppWithEndpoint =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            ["StartAppFast"] = ScapiEndpoints.GetAccessToken,
            ["StartAppSafe"] = ScapiEndpoints.GetAccessToken,
            ["AddToCartApp"] = ScapiEndpoints.AddItemToBasket,
        };

    /// <summary>Dw-side steps with a real classic controller.</summary>
    public static readonly IReadOnlyDictionary<string, string> DwWithEndpoint =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            ["GetSessionDw"] = DemandwareControllers.CartGet,
            ["GetCartDw"] = DemandwareControllers.CartGet,
            ["AddToCartAppDw"] = DemandwareControllers.CartAddProduct,
        };

    /// <summary>
    /// The four app steps with no SCAPI endpoint — the ones that must run against the storefront
    /// itself, and the reason an app-only order is impossible.
    /// </summary>
    public static readonly IReadOnlyList<string> AppWithoutEndpoint = new[]
    {
        "ApplyDiscountApp", "GetCheckoutApp", "GetRatesApp", "SubmitOrderApp",
    };

    /// <summary>
    /// The structural fact: six ShopperBaskets calls and two ShopperLogin calls, and no orders call.
    /// </summary>
    public const string NoOrdersEndpoint =
        "the SCAPI family has no orders endpoint: create/add/update baskets and two login calls only, " +
        "so an app-path order must cross back to the classic controllers";

    /// <summary>How this split was drawn.</summary>
    public const string Evidence =
        "name correlation between the 15 dual steps and the two endpoint families; " +
        "no request capture; the four unpaired app steps are recorded, not given invented paths";

    /// <summary>True when the step is app-side with an endpoint.</summary>
    public static bool IsAppMapped(string? step) =>
        !string.IsNullOrEmpty(step) && AppWithEndpoint.ContainsKey(step);

    /// <summary>True when the step is Dw-side with an endpoint.</summary>
    public static bool IsDwMapped(string? step) =>
        !string.IsNullOrEmpty(step) && DwWithEndpoint.ContainsKey(step);

    /// <summary>True when the step is app-side with no endpoint.</summary>
    public static bool IsAppGap(string? step) =>
        !string.IsNullOrEmpty(step) && AppWithoutEndpoint.Contains(step);

    /// <summary>All steps accounted for: three app, three dw, four gaps.</summary>
    public static int AccountedCount =>
        AppWithEndpoint.Count + DwWithEndpoint.Count + AppWithoutEndpoint.Count;
}
