namespace Cybersole.Stores.Flows;

/// <summary>
/// Three more endpoint families from the 5.18.32 image, dumped in R102 — twenty-two literals, all
/// verbatim.
///
/// <para>
/// Each family is a different store engine's checkout surface, and each was reached by the same
/// method R101 established: extract every path literal, cluster by prefix, read the names. No code
/// is written against them until the family is in hand.
/// </para>
/// </summary>
public static class StoreApiFamilies
{
    // ------------------------------------------------------------------------------------------
    // /rpc/ec — a retail POS/e-commerce RPC API (stock, address, freight, buy rules, order)
    // ------------------------------------------------------------------------------------------
    public static class RpcEc
    {
        public const string ValidateBuyRule = "/rpc/ec/buyRule/validateBuyRule";
        public const string CalculateShippingFee = "/rpc/ec/freight/calculateShippingFee";
        public const string CreateOrder = "/rpc/ec/order/create";
        public const string GetStock = "/rpc/ec/spu/getStock";
        public const string FindOneSpu = "/rpc/ec/spu/public_FindOne";
        public const string CreateAddress = "/rpc/ec/userAddress/create";
        public const string ListAddresses = "/rpc/ec/userAddress/findAll";

        /// <summary>The order in a buyer walks it: look, stock, address, freight, rule, order.</summary>
        public static readonly IReadOnlyList<string> Chain = new[]
        {
            FindOneSpu, GetStock, ListAddresses, CreateAddress, CalculateShippingFee,
            ValidateBuyRule, CreateOrder,
        };

        public static readonly IReadOnlyList<string> All = new[]
        {
            ValidateBuyRule, CalculateShippingFee, CreateOrder, GetStock, FindOneSpu,
            CreateAddress, ListAddresses,
        };
    }

    // ------------------------------------------------------------------------------------------
    // /component/singlepagecheckout — a Hybris-style single-page checkout
    // ------------------------------------------------------------------------------------------
    public static class SinglePageCheckout
    {
        public const string AddEditBillingAddress =
            "/component/singlepagecheckout/addEditBillingAddress";
        public const string AddEditDeliveryAddress =
            "/component/singlepagecheckout/addEditDeliveryAddress";
        public const string Submit = "/component/singlepagecheckout/cac/submit";
        public const string ContinueToPaymentDetails =
            "/component/singlepagecheckout/continueToPaymentDetails";
        public const string PickupStores =
            "/component/singlepagecheckout/getClickAndCollectOrCollectPlusPoiStores";
        public const string SetDeliveryCountry =
            "/component/singlepagecheckout/setDeliveryCountry";
        public const string SetDeliveryMode = "/component/singlepagecheckout/setDeliveryMode";

        /// <summary>Delivery first, then billing, then payment, then submit.</summary>
        public static readonly IReadOnlyList<string> Chain = new[]
        {
            SetDeliveryCountry, SetDeliveryMode, AddEditDeliveryAddress, ContinueToPaymentDetails,
            AddEditBillingAddress, Submit,
        };

        public static readonly IReadOnlyList<string> All = new[]
        {
            AddEditBillingAddress, AddEditDeliveryAddress, Submit, ContinueToPaymentDetails,
            PickupStores, SetDeliveryCountry, SetDeliveryMode,
        };
    }

    // ------------------------------------------------------------------------------------------
    // /apps/gatekeeper/api — a release gate: token, challenge, audit
    // ------------------------------------------------------------------------------------------
    public static class Gatekeeper
    {
        public const string Bootstrap = "/apps/gatekeeper/api/bootstrap?";
        public const string Token = "/apps/gatekeeper/api/gatekeeper-token?";
        public const string RenderToken = "/apps/gatekeeper/api/render-token?";
        public const string ValidateToken = "/apps/gatekeeper/api/validate-gatekeeper-token?";
        public const string CreateChallenge = "/apps/gatekeeper/api/interaction-challenge/create?";
        public const string ReleaseDetails = "/apps/gatekeeper/api/release-details?";
        public const string AuditCartAdd = "/apps/gatekeeper/api/audit-events/cart-add?shop=";
        public const string AuditCheckoutBehaviour =
            "/apps/gatekeeper/api/audit-events/checkout-behaviour?shop=";

        /// <summary>
        /// The gate in the order a drop walks it: bootstrap, ask for a challenge, get a render token,
        /// swap it for a gatekeeper token, have the server agree it is valid.
        /// </summary>
        public static readonly IReadOnlyList<string> Gate = new[]
        {
            Bootstrap, CreateChallenge, RenderToken, Token, ValidateToken, ReleaseDetails,
        };

        public static readonly IReadOnlyList<string> All = new[]
        {
            AuditCartAdd, AuditCheckoutBehaviour, Bootstrap, Token, CreateChallenge, ReleaseDetails,
            RenderToken, ValidateToken,
        };
    }

    /// <summary>Every path in the three families.</summary>
    public static readonly IReadOnlyList<string> All = RpcEc.All
        .Concat(SinglePageCheckout.All)
        .Concat(Gatekeeper.All)
        .ToList();

    /// <summary>True when the path belongs to any of the three families.</summary>
    public static bool IsKnown(string? path) =>
        !string.IsNullOrEmpty(path) && All.Contains(path, StringComparer.Ordinal);
}
