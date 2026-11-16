namespace Cybersole.Stores.Flows;

/// <summary>
/// The Salesforce Commerce API (SCAPI) basket and login surface, read out of the 5.18.32 image in
/// R101 — nine endpoints, verbatim.
///
/// <para>
/// This is the <b>second</b> SFCC path the original carries. <c>DemandwareFlow</c> drives the classic
/// <c>/on/demandware.store/Sites-{site}-Site/{locale}/{controller}</c> controllers; SCAPI is the
/// headless REST API a modern SFCC store exposes instead, and the replica had none of it.
/// </para>
///
/// <code>
/// /scapi/ShopperBaskets/createBasket
/// /scapi/ShopperBaskets/addItemToBasket
/// /scapi/ShopperBaskets/updateBasket
/// /scapi/ShopperBaskets/updateCustomerForBasket
/// /scapi/ShopperBaskets/updateShippingAddressForShipment
/// /scapi/ShopperBaskets/updateShippingMethodForShipment
/// /scapi/ShopperBaskets/updateBillingAddressForBasket
/// /scapi/ShopperLogin/authorizeCustomer
/// /scapi/ShopperLogin/getAccessToken
/// </code>
///
/// <para>
/// The order is not alphabetical by accident of the pool — it is the order a checkout walks it:
/// create, add, set the customer, set the address, pick the method, set billing, then authorise.
/// </para>
/// </summary>
public static class ScapiEndpoints
{
    public const string CreateBasket = "/scapi/ShopperBaskets/createBasket";
    public const string AddItemToBasket = "/scapi/ShopperBaskets/addItemToBasket";
    public const string UpdateBasket = "/scapi/ShopperBaskets/updateBasket";
    public const string UpdateCustomer = "/scapi/ShopperBaskets/updateCustomerForBasket";
    public const string UpdateShippingAddress =
        "/scapi/ShopperBaskets/updateShippingAddressForShipment";
    public const string UpdateShippingMethod =
        "/scapi/ShopperBaskets/updateShippingMethodForShipment";
    public const string UpdateBillingAddress =
        "/scapi/ShopperBaskets/updateBillingAddressForBasket";
    public const string AuthorizeCustomer = "/scapi/ShopperLogin/authorizeCustomer";
    public const string GetAccessToken = "/scapi/ShopperLogin/getAccessToken";

    /// <summary>The basket chain, in checkout order.</summary>
    public static readonly IReadOnlyList<string> BasketChain = new[]
    {
        CreateBasket,
        AddItemToBasket,
        UpdateCustomer,
        UpdateShippingAddress,
        UpdateShippingMethod,
        UpdateBillingAddress,
        UpdateBasket,
    };

    /// <summary>All nine.</summary>
    public static readonly IReadOnlyList<string> All = new[]
    {
        CreateBasket, AddItemToBasket, UpdateBasket, UpdateCustomer,
        UpdateShippingAddress, UpdateShippingMethod, UpdateBillingAddress,
        AuthorizeCustomer, GetAccessToken,
    };

    /// <summary>The two halves of a headless SFCC session.</summary>
    public static readonly IReadOnlyList<string> Login = new[] { AuthorizeCustomer, GetAccessToken };

    /// <summary>True when <paramref name="path"/> starts with one of the nine.</summary>
    public static bool IsKnown(string? path) =>
        !string.IsNullOrEmpty(path) && All.Contains(path, StringComparer.Ordinal);

    /// <summary>True when the path belongs to SCAPI at all, known or not.</summary>
    public static bool IsScapi(string? path) =>
        !string.IsNullOrEmpty(path) && path.StartsWith("/scapi/", StringComparison.Ordinal);
}
