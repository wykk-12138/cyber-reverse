using System.Collections.Generic;
using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R290: a digest per flow — every step's name and ordinal, in order, joined into one string.
///
/// <para>
/// The digests were produced from the literals in the image (addresses are recorded in <c>StoreFlowSteps</c> next to
/// each flow). Editing a flow now <b>changes its digest</b>, so a silent edit fails here instead of quietly becoming the
/// new truth — which is exactly how <c>structure-token-single</c> kept a wrong step until R287.
/// </para>
/// </summary>
public sealed class StoreFlowDigestTests
{
    private readonly ITestOutputHelper _out;
    public StoreFlowDigestTests(ITestOutputHelper output) => _out = output;

    private static string Digest(StoreFlowSteps.Flow flow) =>
        string.Join("|", flow.Steps.Select(s => s.Name + ":" + s.Ordinal));

    private static readonly Dictionary<string, string> Expected = new()
    {
        ["nike"] = "StartEcomSession:41|Authorize:42|GetAccessToken:43|FindVariant:44|CreateBasket:46|SubmitCustomer:48|ValidateAddress:49|SubmitShippingAddress:50|GetShippingMethods:51|SubmitShippingMethod:52|SubmitBillingAddress:53|BeginCheckout:54|CheckInventory:55|GetShopperIp:56|GetPaymentMethods:57|SubmitOrder:58",
        ["popmart"] = "GetOrders:104|GetInstoreOrders:105|StartDrawFlow:115|StartDrawCheckFlow:116|FindDraw:117|CheckDraw:118|EnterDraw:119|CheckResult:120|StartDrawEventFlow:131|FindDrawEvent:132|FindMegaDraw:133|EnterDrawEvent:134|ChooseGoods:135|RedeemMemberPoints:136|RedeemLuckPoints:137|FetchAliases:138|StartExhibitFlow:139|FindExhibit:141|EnterExhibit:142|StartReservationFlow:149|FetchDetails:150|FindDates:151|FindTimeSlots:152|EnterReservation:153",
        ["johnlewis"] = "GetHome:20|FindProduct:21|AddToCart:22|WebHandOver:23|SessionHandover:24|GuestCallback:25|DeliveryPage:26|SubmitShipping:27|CreateDelivery:28|GetDeliveryMethods:29|SubmitDeliveryMethod:30|GetPaymentPage:31|SubmitOrderStripe:32|SubmitOrder:33|AuthenticatePayment:34|SubmitBillingAddress:35|PlaceOrder:36|HandleRequiresAction:37|GetStripePaymentIntent:39",
        ["demandware-classic"] = "AddToCart:32|InitiateCheckout:33|GenerateCSRF:34|GetCheckout:35|SubmitBillingAddress:36|SubmitConsignment:37|SubmitShippingOption:38|GetPaymentMethod:39|CreateStripePaymentMethod:40|CreateOrder:41|SubmitPayment:42|ConfirmPayment:43",
        ["demandware-dual"] = "GetRates:26|GetCheckout:27|SubmitOrder:28|StartAppFast:36|StartAppSafe:37|GetSessionDw:38|GetCartDw:39|FindProductApp:40|AddToCartApp:41|AddToCartAppDw:42|SaveSessionDw:43|ApplyDiscountApp:44|GetCheckoutApp:45|GetRatesApp:46|SubmitOrderApp:47",
        ["collectplus-app"] = "GetHome:33|GetProduct:34|FindProductApp:35|GetSessionApp:36|AddToCartApp:37|CreateCheckoutApp:38|GetBasket:39|AddToCart:40|SubmitDiscount:41|LookupAddress:42|GetDelivery:43|GetCollectPlusLocations:44|SubmitCollectPlus:45|SubmitDelivery:47|SubmitBilling:48|StartPayment:49|GetPaymentUrl:50",
        ["structure-token-multi"] = "FindProductMulti:29|FindProductFlow:30|FindVariant:32|AddToCartMulti:33|GetCheckout:37|GetMerchantCode:38|GetShippingRate:39|SubmitShipping:40|CalculateTaxes:41|GetStructureToken:42|CreateTransaction:43|SubmitPayment:44|GetPayPalToken:45|SubmitPayPal:46|ProcessPayment:47",
        ["structure-token-single"] = "EditLine:40|AddToCart:41|GetCheckout:42|GetShippingRate:43|SubmitShipping:44|CalculateTaxes:45|GetStructureToken:46|CreateTransaction:47|SubmitPayment:48|GetPayPalToken:49|SubmitPayPal:50|ProcessPayment:51",
    };

    [Fact]
    public void EveryFlowMatchesItsLiteralDigest()
    {
        foreach (var flow in StoreFlowSteps.All)
        {
            var digest = Digest(flow);
            _out.WriteLine($"{flow.Store}: {digest}");
            Assert.True(Expected.ContainsKey(flow.Store), "flow not in the digest table: " + flow.Store);
            Assert.Equal(Expected[flow.Store], digest);
        }
    }

    [Fact]
    public void TheDigestTableCoversEveryFlow()
    {
        Assert.Equal(StoreFlowSteps.All.Count, Expected.Count);
    }
}
