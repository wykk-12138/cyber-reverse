using System.Text.RegularExpressions;
using Cybersole.Core.Models;
using Cybersole.Http;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// SAP Commerce Cloud (Hybris).
///
/// Why this platform exists: Offspring was registered as MagentoFlow, but nothing Magento ever
/// answered — /rest/V1/store/storeConfigs, /customer/section/load/ and /cart.js are all 404 on
/// both offspring.co.uk and offspring.com. A capture of the home page showed what it does call:
///
///   GET  /akam/13/710368ee                          Akamai Bot Manager
///   GET  /view/resources/getUserInfo                -> 200, 418 B,  application/json
///   GET  /view/component/basket/minibasketAjax      -> 200, 1164 B, application/json
///
/// and the page HTML literally contains "hybris". The /view/... controller shape is SAP
/// Commerce's, not Magento's, not Shopify's and not Demandware's. That is grade-A evidence:
/// the site names its own backend and two of its controllers answer with real payloads.
///
/// Verified:  the two /view/ controllers above.
/// Inferred:  the product, cart-add and checkout paths — Hybris's documented /p/ and cart
///            controller shape, marked at each site below.
/// </summary>
public sealed class HybrisFlow : StoreFlow
{
    private readonly string _id;
    private readonly string _name;
    private readonly IReadOnlyList<string> _domains;
    private readonly string _siteUid;

    public HybrisFlow(string id, string name, IReadOnlyList<string> domains,
        string siteUid = "main")
    {
        _id = id;
        _name = name;
        _domains = domains;
        _siteUid = siteUid;
    }

    public override string Id => _id;
    public override string Name => _name;
    public override IReadOnlyList<string> Domains => _domains;

    /// <summary>Hybris guards its controllers with Akamai, so a plain 403 is expected on cold starts.</summary>
    private static bool IsBlocked(NetResponse? res) => res is { StatusCode: 403 or 429 };

    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/", _id + "-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail($"{_id} home unreachable", retryable: true);
        if (IsBlocked(res)) return StepOutcome.Fail($"{_id} home blocked (akamai)", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"{_id} home HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["home"] = res.Body;

        // verified endpoint: confirms the session cookie is usable before any cart work
        var info = await GetAsync(c, Origin(c.Url) + "/view/resources/getUserInfo",  // inferred: no image evidence; 0 hits in the 324,901-entry dump; R1266: absence carries no information (R294)
            _id + "-userinfo", ct).ConfigureAwait(false);

        if (info is { IsSuccess: true }) c.Session.Vars["userInfo"] = info.Body;

        return StepOutcome.Success();
    }

    /// <summary>Verified: GET /view/component/basket/minibasketAjax answers JSON.</summary>
    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        // R1253: view/component/basket/minibasketAjax is attested in the image as a token without the leading slash;
        // this URL is the origin plus that token, not an invented path.
        var res = await GetAsync(c, Origin(c.Url) + "/view/component/basket/minibasketAjax",
            _id + "-minibasket", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail($"{_id} basket unreachable", retryable: true);
        if (IsBlocked(res)) return StepOutcome.Fail($"{_id} basket blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"{_id} basket HTTP {res.StatusCode}",
            retryable: true);

        c.Session.Vars["cart"] = res.Body;

        var count = Regex.Match(res.Body, @"""?(?:totalUnitCount|unitCount)""?\s*:\s*(\d+)");
        if (count.Success) c.Session.Vars["cartCount"] = count.Groups[1].Value;

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, _id + "-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail($"{_id} product unreachable", retryable: true);
        if (IsBlocked(res)) return StepOutcome.Fail($"{_id} product blocked", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"{_id} product HTTP {res.StatusCode}",
            retryable: true);

        c.Session.Vars["raw"] = res.Body;

        // Hybris pages put the product in a data attribute and the name in an h1
        var name = Regex.Match(res.Body, @"<h1[^>]*>([^<]{2,80})</h1>").Groups[1].Value.Trim();
        if (string.IsNullOrEmpty(name))
            name = Regex.Match(res.Body, @"<title>([^<|]+)").Groups[1].Value.Trim();
        if (!string.IsNullOrEmpty(name)) c.Session.Vars["product"] = name;

        // price: Hybris renders a formatted amount next to a currency; take the first one
        var price = Regex.Match(res.Body, @"[""']?(?:value|price)[""']?\s*:\s*([\d]+\.?\d*)");
        if (!price.Success)
            price = Regex.Match(res.Body, @"(?:£|\$|€)\s?([\d,]+\.\d{2})");

        if (price.Success && decimal.TryParse(price.Groups[1].Value.Replace(",", ""),
                System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var amount)
            && amount > 0)
            c.Session.Vars["price"] = amount.ToString("0.00");

        return StepOutcome.Success();
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;

        // Hybris calls the sku "code" and the variant a "variantOption"; both live in the page
        var code = Regex.Match(body, @"""code""\s*:\s*""([A-Za-z0-9\-_]{4,})""").Groups[1].Value;
        if (string.IsNullOrEmpty(code))
            code = Regex.Match(c.Url, @"[/-]([A-Za-z0-9]{6,})(?:[/?#]|$)").Groups[1].Value;

        if (string.IsNullOrEmpty(code))
            return Task.FromResult(StepOutcome.Fail($"{_id}: no product code in the page"));

        c.Session.VariantId = code;

        // sizes are rendered as option buttons labelled with the size text
        var sizes = Regex.Matches(body, @"""size""\s*:\s*""([^""]{1,10})""")
            .Select(m => m.Groups[1].Value).Distinct().ToList();

        if (sizes.Count > 0) c.Session.Vars["sizes"] = string.Join(',', sizes);

        return Task.FromResult(StepOutcome.Success());
    }

    public override Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c,
        CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var r) ? r : string.Empty;

        var oos = body.Contains("\"stockLevelStatus\":\"outOfStock\"", StringComparison.OrdinalIgnoreCase)
                  || body.Contains("\"purchasable\":false", StringComparison.OrdinalIgnoreCase)
                  || body.Contains("out of stock", StringComparison.OrdinalIgnoreCase);

        c.Session.Vars["available"] = oos ? "false" : "true";
        return Task.FromResult(StepOutcome.Success());
    }

    /// <summary>
    /// Add to basket, using the controller path the original binary names.
    ///
    /// Four candidates had been tried here and by <c>HybrisCartPathTests</c>, with the verified
    /// <c>minibasketAjax</c> as a control:
    ///
    ///   /cart/add                   404, 162 KB HTML
    ///   /view/cart/add              404, 162 KB HTML
    ///   /view/component/cart/add    404, 162 KB HTML
    ///   /view/component/basket/add  404, 162 KB HTML
    ///   control: minibasketAjax     200, 1.1 KB JSON     &lt;- host and cookie are fine
    ///
    /// Every candidate assumed the add controller sat beside the minibasket one. It does not.
    /// The string table of <c>Cybersole.exe</c> contains three Hybris controller paths:
    ///
    ///   view/basket/add                       &lt;- one segment shallower
    ///   view/basket/addPromotionalCode
    ///   view/component/basket/minibasketAjax  &lt;- the control, one segment deeper
    ///
    /// The add controller is at <c>/view/basket/</c>, not <c>/view/component/basket/</c>; the
    /// minibasket lives under <c>/view/component/</c>. That asymmetry is why prefixing every
    /// guess with <c>/view/component/</c> never reached the real route.
    ///
    /// This asks the real path once. If it answers 404 too, the failure now says which URL was
    /// tried rather than listing four that were not.
    ///
    /// <para>
    /// Not verified live. When this was changed, offspring answered 403 to <em>every</em> path
    /// including the minibasket control that used to return 200 — so the host is currently
    /// refusing this client outright and no path can be distinguished. The change rests on the
    /// binary's own string table, which is a stronger source than a probe against a host that has
    /// stopped talking; but it is not a confirmed 200, and should not be recorded as one.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        var variant = c.Session.VariantId ?? string.Empty;
        if (string.IsNullOrEmpty(variant))
            return StepOutcome.Fail($"{_id}: no variant id to add");

        var form = new Dictionary<string, string>
        {
            ["productCodePost"] = variant,
            ["qty"] = c.Session.Vars.TryGetValue("qty", out var qty) && qty.Length > 0 ? qty : "1",
        };

        // R1253: view/basket/add is an attested token too (the image also carries view/basket/addPromotionalCode
        // beside it, which is what identified this family as Hybris basket endpoints rather than guessed ones).
        var res = await PostFormAsync(c, Origin(c.Url) + "/view/basket/add", form,
            _id + "-basket-add", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail($"{_id}: basket add unreachable", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail(
                $"{_id}: basket add HTTP {res.StatusCode} at /view/basket/add",
                retryable: res.StatusCode >= 500);

        c.Session.Vars["basket"] = res.Body;
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
        OpenCheckoutAsync(c, _id + "-checkout", "/cart/checkout", ct);

    /// <summary>
    /// The profile's address under the image's own billing field names. R795.
    ///
    /// <para>
    /// <b>Observation:</b> the image carries forty <c>dwfrm_*</c> field names and every one is
    /// <c>dwfrm_billing_*</c> -- there are no <c>dwfrm_shipping_*</c> names at all. Among them
    /// <c>dwfrm_billing_addressFields_useShipping</c>, which is how this platform says "bill to the shipping
    /// address".
    /// </para>
    ///
    /// <para>
    /// So the names below are the image's, not invented. What is inferred (medium) is that the guest checkout accepts
    /// the same address fields under the billing prefix -- the platform's own <c>useShipping</c> flag suggests it has
    /// no separate shipping field set to submit.
    /// </para>
    /// </summary>
    private Dictionary<string, string> BillingAddress(FlowContext c)
    {
        var form = new Dictionary<string, string>();
        var p = c.ProfileData;
        if (p is not null)
        {
            form["dwfrm_billing_addressFields_firstName"] = p.FirstName;
            form["dwfrm_billing_addressFields_lastName"] = p.LastName;
            form["dwfrm_billing_addressFields_address1"] = p.Address1;
            form["dwfrm_billing_addressFields_address2"] = p.Address2;
            form["dwfrm_billing_addressFields_city"] = p.City;
            form["dwfrm_billing_addressFields_postalCode"] = p.Zip;
            form["dwfrm_billing_addressFields_phone"] = p.Phone;
            form["dwfrm_billing_addressFields_stateArea"] = p.State;
            form["dwfrm_billing_addressFields_country"] = p.Country;
        }
        if (c.Account?.Email is { Length: > 0 } email)
            form["dwfrm_billing_addressFields_email"] = email;
        return form;
    }

    /// <summary>
    /// Save the guest's address. R795.
    ///
    /// <para>
    /// <b>Observation:</b> <c>/Checkout-SaveGuest</c> is one of the fourteen <c>/Checkout-*</c> paths the image
    /// carries, alongside <c>/Checkout-Begin?stage=shipping</c> and <c>?step=shipping</c>.
    /// </para>
    ///
    /// <para>
    /// <b>Inference (medium):</b> that SaveGuest is the submit rather than merely a stage. The alternative reading is
    /// that shipping is entered after navigating to the shipping stage, and the image does not say which. The
    /// distinction is recorded here rather than resolved, because a wrong guess costs one HTTP round trip and reports
    /// itself, unlike a wrong identifier.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct)
    {
        var form = BillingAddress(c);
        form["dwfrm_billing_addressFields_useShipping"] = "true";

        var res = await PostFormAsync(c, Origin(c.Url) + "/Checkout-SaveGuest", form,
            _id + "-save-guest", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail($"{_id}: SaveGuest unreachable", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail($"{_id}: SaveGuest HTTP {res.StatusCode} at /Checkout-SaveGuest",
                retryable: res.StatusCode >= 500);

        c.Session.Vars["shipping"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// Submit the payment details. R796.
    ///
    /// <para>
    /// <b>Observation:</b> the image carries three families of card fields -- <c>dwfrm_billing_creditCardFields_*</c>
    /// with fifteen names, <c>dwfrm_billing_paymentMethods_creditCard_*</c> with six, and a GMO set for a Japanese
    /// gateway -- plus <c>dwfrm_billing_paymentMethod</c> and <c>dwfrm_billing_paymentMethods_selectedPaymentMethodID</c>
    /// to say which one is in use. Two names in the first family matter:
    /// <c>creditCardFields_adyenEncryptedData</c> and <c>saveCardAdyen</c>, which say this site can take a card through
    /// Adyen's client-side encryption rather than in the clear.
    /// </para>
    ///
    /// <para>
    /// So the fields below are the image's. What is unknown is whether plaintext card fields are accepted at all: if
    /// the site requires <c>adyenEncryptedData</c>, this submission will be rejected, and it will be rejected visibly.
    /// The payment-method id is likewise not recovered, so it is taken from the session and left out when absent.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        var form = BillingAddress(c);

        if (c.Session.Vars.TryGetValue("paymentMethodId", out var method) && method.Length > 0)
        {
            form["dwfrm_billing_paymentMethod"] = method;
            form["dwfrm_billing_paymentMethods_selectedPaymentMethodID"] = method;
        }

        var p = c.ProfileData;
        if (p is not null)
        {
            form["dwfrm_billing_creditCardFields_cardNumber"] = p.CardNumber;
            form["dwfrm_billing_creditCardFields_cardOwner"] = p.CardName;
            form["dwfrm_billing_creditCardFields_securityCode"] = p.CardCvv;
            form["dwfrm_billing_creditCardFields_saveCard"] = "false";

            // the expiry arrives as one string; the form wants the two halves separately
            var parts = (p.CardExpiry ?? string.Empty).Split('/');
            if (parts.Length == 2)
            {
                form["dwfrm_billing_creditCardFields_expirationMonth"] = parts[0].Trim().PadLeft(2, '0');
                var year = parts[1].Trim();
                form["dwfrm_billing_creditCardFields_expirationYear"] =
                    year.Length == 2 ? "20" + year : year;
            }
        }

        var res = await PostFormAsync(c, Origin(c.Url) + "/Checkout-SubmitPaymentDetails", form,
            _id + "-payment-details", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail($"{_id}: SubmitPaymentDetails unreachable", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail(
                $"{_id}: SubmitPaymentDetails HTTP {res.StatusCode} at /Checkout-SubmitPaymentDetails",
                retryable: res.StatusCode >= 500);

        c.Session.Vars["payment"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// Place the order. R795.
    ///
    /// <para>
    /// The earlier version said Hybris has no single POST that places an order. The image refutes that:
    /// <c>/Checkout-SubmitOrder</c> is right there in the pool, next to <c>/Checkout-SubmitPaymentDetails</c>. The
    /// comment was not wrong about the flow being staged -- <c>/Checkout-Begin</c> with its stage and step variants is
    /// also in the image -- but it drew the wrong conclusion from that.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        var res = await PostFormAsync(c, Origin(c.Url) + "/Checkout-SubmitOrder",
            new Dictionary<string, string>(), _id + "-submit-order", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail($"{_id}: SubmitOrder unreachable", retryable: true);
        if (!res.IsSuccess)
            return StepOutcome.Fail($"{_id}: SubmitOrder HTTP {res.StatusCode} at /Checkout-SubmitOrder",
                retryable: res.StatusCode >= 500);

        c.Session.Vars["order"] = res.Body;
        var number = System.Text.RegularExpressions.Regex.Match(
            res.Body, @"""(?:orderNumber|orderNo)""\s*:\s*""([^""]+)""");
        if (number.Success) c.Session.OrderNumber = number.Groups[1].Value;
        return StepOutcome.Success();
    }
}
