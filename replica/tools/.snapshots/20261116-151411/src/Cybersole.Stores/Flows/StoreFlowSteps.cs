using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The step lists of the store flows the 5.18.32 image carries, read out in R112.
///
/// <para>
/// Each flow's steps sit in one adjacent run in the string pool, with the compiler's
/// <c>d__N</c> ordinals attached — which makes the list authoritative rather than reconstructed.
/// R111 found Nike this way; the same run turns out to hold every store's flow.
/// </para>
///
/// <para>
/// Five flows are named below because the evidence to name them already exists: their steps line up
/// with endpoint families this session has already proven.
/// </para>
///
/// <code>
/// Nike        16   SubmitCustomer / ValidateAddress / BeginCheckout …   (NikeEndpoints, R87)
/// Pop Mart    24   StartDrawFlow / FindMegaDraw / ChooseGoods …          (/shop/v1/*, R100)
/// John Lewis  17   WebHandOver / GuestCallback / GetStripePaymentIntent  (bff/v1..v4, R103)
/// Demandware  12   InitiateCheckout / GenerateCSRF / SubmitConsignment   (controllers, R94)
/// Demandware  15   StartAppFast / GetCartDw / ToCartAppDw …              (SCAPI vs classic, R101)
/// </code>
///
/// <para>
/// The Demandware pair is the interesting one: fifteen steps with <c>App</c> and <c>Dw</c> variants
/// of the same action (<c>AddToCartApp</c> / <c>AddToCartAppDw</c>, <c>GetCartDw</c>,
/// <c>SaveSessionDw</c>) is a flow that keeps <b>two paths alive at once</b> — the app-side and the
/// web-side — which is what R101 found in the image's endpoints and R107 wired into DemandwareFlow.
/// </para>
/// </summary>
public static class StoreFlowSteps
{
    /// <summary>One step: name and the compiler ordinal.</summary>
    public sealed record Step(string Name, int Ordinal);

    /// <summary>A named flow: the store it belongs to and its steps in order.</summary>
    /// <summary>
    /// Where a flow's step list came from — the distinction R274 found missing.
    ///
    /// <para><see cref="FlowSource.Literal"/>: read straight out of one literal in the image, so it can be checked
    /// against a recovered segment step by step. <see cref="FlowSource.Endpoint"/>: reconstructed from an endpoint
    /// family, with names that are not the image's method names (<c>StartEcomSession</c> vs <c>Start</c>) — it must not
    /// be compared to a literal segment, and calling the two together "1:1" is exactly the mistake this avoids.</para>
    /// </summary>
    public enum FlowSource
    {
        /// <summary>Read from one literal; step-by-step verifiable.</summary>
        Literal = 0,
        /// <summary>Reconstructed from endpoints; narrative, not literal names.</summary>
        Endpoint = 1,
    }

    public sealed record Flow(string Store, IReadOnlyList<Step> Steps, FlowSource Source = FlowSource.Endpoint)
    {
        public int Count => Steps.Count;
        public IReadOnlyList<string> Names => Steps.Select(s => s.Name).ToList();
    }

    public static readonly Flow Nike = new("nike", new[]
    {
        new Step("StartEcomSession", 41), new Step("Authorize", 42), new Step("GetAccessToken", 43),
        new Step("FindVariant", 44), new Step("CreateBasket", 46), new Step("SubmitCustomer", 48),
        new Step("ValidateAddress", 49), new Step("SubmitShippingAddress", 50),
        new Step("GetShippingMethods", 51), new Step("SubmitShippingMethod", 52),
        new Step("SubmitBillingAddress", 53), new Step("BeginCheckout", 54),
        new Step("CheckInventory", 55), new Step("GetShopperIp", 56),
        new Step("GetPaymentMethods", 57), new Step("SubmitOrder", 58),
    }, FlowSource.Literal);

    public static readonly Flow PopMart = new("popmart", new[]
    {
        new Step("GetOrders", 104), new Step("GetInstoreOrders", 105),
        new Step("StartDrawFlow", 115), new Step("StartDrawCheckFlow", 116),
        new Step("FindDraw", 117), new Step("CheckDraw", 118), new Step("EnterDraw", 119),
        new Step("CheckResult", 120), new Step("StartDrawEventFlow", 131),
        new Step("FindDrawEvent", 132), new Step("FindMegaDraw", 133),
        new Step("EnterDrawEvent", 134), new Step("ChooseGoods", 135),
        new Step("RedeemMemberPoints", 136), new Step("RedeemLuckPoints", 137),
        new Step("FetchAliases", 138), new Step("StartExhibitFlow", 139),
        new Step("FindExhibit", 141), new Step("EnterExhibit", 142),
        new Step("StartReservationFlow", 149), new Step("FetchDetails", 150),
        new Step("FindDates", 151), new Step("FindTimeSlots", 152),
        new Step("EnterReservation", 153),
    }, FlowSource.Literal);

    /// <summary>
    /// John Lewis, <b>nineteen</b> steps.
    ///
    /// <para>
    /// R112 read this flow as seventeen because the step literal jumps from ordinal 20 to 23 and the
    /// gap looked like compiler noise. It is not: the class's <b>lambda literal</b>
    /// (<c>&lt;&lt;FindProduct&gt;g__Available|21_3</c>, <c>&lt;AddToCart&gt;b__22_0</c>) names methods 21
    /// and 22, so <c>FindProduct</c> and <c>AddToCart</c> are steps of the same flow. Nineteen.
    /// </para>
    ///
    /// <para>
    /// The lesson is the same one three rounds have taught: a gap in the ordinals is not permission to
    /// skip it. Nike's 45/47 really were <c>MoveNext</c> helpers; these two are not. The difference is
    /// only visible in a second literal.
    /// </para>
    /// </summary>
    public static readonly Flow JohnLewis = new("johnlewis", new[]
    {
        new Step("GetHome", 20), new Step("FindProduct", 21), new Step("AddToCart", 22),
        new Step("WebHandOver", 23), new Step("SessionHandover", 24),
        new Step("GuestCallback", 25), new Step("DeliveryPage", 26), new Step("SubmitShipping", 27),
        new Step("CreateDelivery", 28), new Step("GetDeliveryMethods", 29),
        new Step("SubmitDeliveryMethod", 30), new Step("GetPaymentPage", 31),
        new Step("SubmitOrderStripe", 32), new Step("SubmitOrder", 33),
        new Step("AuthenticatePayment", 34), new Step("SubmitBillingAddress", 35),
        new Step("PlaceOrder", 36), new Step("HandleRequiresAction", 37),
        new Step("GetStripePaymentIntent", 39),
    }, FlowSource.Literal);

    public static readonly Flow DemandwareClassic = new("demandware-classic", new[]
    {
        new Step("AddToCart", 32), new Step("InitiateCheckout", 33), new Step("GenerateCSRF", 34),
        new Step("GetCheckout", 35), new Step("SubmitBillingAddress", 36),
        new Step("SubmitConsignment", 37), new Step("SubmitShippingOption", 38),
        new Step("GetPaymentMethod", 39), new Step("CreateStripePaymentMethod", 40),
        new Step("CreateOrder", 41), new Step("SubmitPayment", 42), new Step("ConfirmPayment", 43),
    }, FlowSource.Literal);

    public static readonly Flow DemandwareDual = new("demandware-dual", new[]
    {
        new Step("GetRates", 26), new Step("GetCheckout", 27), new Step("SubmitOrder", 28),
        new Step("StartAppFast", 36), new Step("StartAppSafe", 37), new Step("GetSessionDw", 38),
        new Step("GetCartDw", 39), new Step("FindProductApp", 40), new Step("AddToCartApp", 41),
        new Step("AddToCartAppDw", 42), new Step("SaveSessionDw", 43),
        new Step("ApplyDiscountApp", 44), new Step("GetCheckoutApp", 45),
        new Step("GetRatesApp", 46), new Step("SubmitOrderApp", 47),
    }, FlowSource.Literal);

    /// <summary>
    /// A UK retailer's app flow: 17 steps that keep an <c>App</c> path (<c>FindProductApp</c>,
    /// <c>GetSessionApp</c>, <c>AddToCartApp</c>, <c>CreateCheckoutApp</c>) beside the web steps, and
    /// end in <c>StartPayment</c> / <c>GetPaymentUrl</c> rather than a card form.
    ///
    /// <para>
    /// The distinctive pair is <c>GetCollectPlusLocations</c> / <c>SubmitCollectPlus</c>: CollectPlus
    /// is a UK parcel network, so this flow is a UK store with click-and-collect. <b>The brand is not
    /// proven</b> — CollectPlus is used by more than one UK retailer — so the flow is named for its
    /// evidence, not for a guess at the logo.
    /// </para>
    /// </summary>
    public static readonly Flow CollectPlusApp = new("collectplus-app", new[]
    {
        new Step("GetHome", 33), new Step("GetProduct", 34), new Step("FindProductApp", 35),
        new Step("GetSessionApp", 36), new Step("AddToCartApp", 37),
        new Step("CreateCheckoutApp", 38), new Step("GetBasket", 39), new Step("AddToCart", 40),
        new Step("SubmitDiscount", 41), new Step("LookupAddress", 42), new Step("GetDelivery", 43),
        new Step("GetCollectPlusLocations", 44), new Step("SubmitCollectPlus", 45),
        new Step("SubmitDelivery", 47), new Step("SubmitBilling", 48),
        new Step("StartPayment", 49), new Step("GetPaymentUrl", 50),
    }, FlowSource.Literal);

    /// <summary>
    /// Fifteen steps on an engine that issues a <b>structure token</b> before it will take a payment:
    /// <c>GetMerchantCode</c> → <c>GetStructureToken</c> → <c>CreateTransaction</c> →
    /// <c>SubmitPayment</c> → <c>ProcessPayment</c>.
    ///
    /// <para>
    /// The payment vocabulary is the evidence: the image also carries
    /// <c>PaymentData.UrlStructureTokenEncoded</c>, <c>_structureToken</c> and
    /// <c>#UrlStructureTokenEncoded</c>, so "structure token" is a real field of a real payment
    /// integration rather than a name invented here. <b>Which provider it is, is not proven</b> — the
    /// flow is named for the mechanic.
    /// </para>
    ///
    /// <para>
    /// This is the multi-variant variant: it opens with <c>FindProductMulti</c> /
    /// <c>AddToCartMulti</c> and includes <c>CalculateTaxes</c>.
    /// </para>
    /// </summary>
    public static readonly Flow StructureTokenMulti = new("structure-token-multi", new[]
    {
        new Step("FindProductMulti", 29), new Step("FindProductFlow", 30),
        new Step("FindVariant", 32), new Step("AddToCartMulti", 33),
        new Step("GetCheckout", 37), new Step("GetMerchantCode", 38),
        new Step("GetShippingRate", 39), new Step("SubmitShipping", 40),
        new Step("CalculateTaxes", 41), new Step("GetStructureToken", 42),
        new Step("CreateTransaction", 43), new Step("SubmitPayment", 44),
        new Step("GetPayPalToken", 45), new Step("SubmitPayPal", 46),
        new Step("ProcessPayment", 47),
    }, FlowSource.Literal);

    /// <summary>
    /// The same engine in its single-variant shape: twelve steps, opening with <c>EditLine</c> and
    /// carrying <c>GetStructureToken</c> at ordinal 46 and <c>CalculateTaxes</c> at 45.
    ///
    /// <para>
    /// Two flows sharing five step names (<c>GetCheckout</c>, <c>GetShippingRate</c>,
    /// <c>SubmitShipping</c>, <c>GetStructureToken</c>, <c>CreateTransaction</c>, <c>SubmitPayment</c>,
    /// <c>GetPayPalToken</c>, <c>SubmitPayPal</c>, <c>ProcessPayment</c>) is not a coincidence: it is
    /// one engine behind two storefronts, and keeping both is how the replica stays honest about them.
    /// </para>
    /// </summary>
    public static readonly Flow StructureTokenSingle = new("structure-token-single", new[]
    {
        // R287: the list here had GetMerchantCode at 37 and no CalculateTaxes, and the ordinals were 34–45. The literal at
        // 0x034b23a5 says otherwise, and its own lambda table (b__43_1 GetShippingRate, b__44_1 SubmitShipping,
        // b__45_1 CalculateTaxes, b__46_1 GetStructureToken …) agrees with it step for step:
        //   EditLine 40, AddToCart 41, GetCheckout 42, GetShippingRate 43, SubmitShipping 44, CalculateTaxes 45,
        //   GetStructureToken 46, CreateTransaction 47, SubmitPayment 48, GetPayPalToken 49, SubmitPayPal 50,
        //   ProcessPayment 51
        // GetMerchantCode is not a step of this flow — it belongs to structure-token-multi at ordinal 38.
        new Step("EditLine", 40), new Step("AddToCart", 41), new Step("GetCheckout", 42),
        new Step("GetShippingRate", 43), new Step("SubmitShipping", 44),
        new Step("CalculateTaxes", 45), new Step("GetStructureToken", 46),
        new Step("CreateTransaction", 47), new Step("SubmitPayment", 48),
        new Step("GetPayPalToken", 49), new Step("SubmitPayPal", 50),
        new Step("ProcessPayment", 51),
    }, FlowSource.Literal);

    /// <summary>
    /// What identifies each unnamed flow, recorded next to it so a later round can name it with
    /// evidence instead of guessing. <b>No brand is claimed.</b>
    /// </summary>
    public static readonly IReadOnlyDictionary<string, string> IdentityEvidence =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            ["collectplus-app"] =
                "GetCollectPlusLocations + *App steps + GetPaymentUrl — UK click-and-collect store",
            ["structure-token-multi"] =
                "GetMerchantCode + GetStructureToken + CalculateTaxes, multi-variant (FindProductMulti)",
            ["structure-token-single"] =
                "same engine, single-variant (EditLine first), GetStructureToken at ordinal 40",
        };

    /// <summary>All eight flows.</summary>
    public static readonly IReadOnlyList<Flow> All = new[]
    {
        Nike, PopMart, JohnLewis, DemandwareClassic, DemandwareDual,
        CollectPlusApp, StructureTokenMulti, StructureTokenSingle,
    };

    /// <summary>Every step name across every flow.</summary>
    public static IReadOnlyList<string> AllStepNames() => All.SelectMany(f => f.Names).ToList();

    /// <summary>The flow whose steps include <paramref name="stepName"/>, if any.</summary>
    public static Flow? FlowFor(string? stepName) =>
        string.IsNullOrEmpty(stepName)
            ? null
            : All.FirstOrDefault(f => f.Names.Contains(stepName));

    /// <summary>True when the name is a step of at least one flow.</summary>
    public static bool IsStep(string? stepName) => FlowFor(stepName) is not null;
}
