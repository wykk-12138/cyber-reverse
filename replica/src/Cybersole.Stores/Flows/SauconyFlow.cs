using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Saucony — Salesforce Commerce Cloud (Demandware) storefront checkout recovered from
/// <c>0x140A740B0..0x140A7C56B</c>.
///
/// <para>
/// <b>Observed</b>: four store ids (<c>saucony_us</c> 0x14715229C, <c>saucony_ca</c> 0x147152204,
/// <c>saucony_eu</c> 0x147152234, <c>saucony_europe</c> 0x147152264), four display names
/// (<c>Saucony</c> 0x146E79BBC, <c>Saucony CA</c>, <c>Saucony EU</c>, <c>Saucony UK</c>), the storefront
/// <c>https://www.saucony.com</c> (0x147099D1C), and SFCC controllers
/// <c>ProductInfo-GetDimensionsAndVariations?productID=</c>, <c>Cart-AddProduct?format=ajax</c>,
/// <c>Checkout-ContinueToBilling</c>, <c>Checkout-SubmitPaymentDetails</c>,
/// <c>CheckoutHelper-PlaceOrder</c>, and <c>PayerAuth-Return</c> (Cardinal Cruise StepUp for EU/UK).
/// </para>
/// </summary>
public sealed class SauconyFlow : StoreFlow
{
    private const string CardinalStepUpUrl = "https://centinelapi.cardinalcommerce.com/V2/Cruise/StepUp";

    public override string Id => "saucony";
    public override string Name => "Saucony";
    public override IReadOnlyList<string> Domains => new[] { "saucony.com" };

    /// <summary>The four store ids the image names, in its order, so a caller can pick a region.</summary>
    public static IReadOnlyList<string> StoreIds { get; } = new[]
    {
        "saucony_us", "saucony_ca", "saucony_eu", "saucony_europe",
    };

    public static string SiteNameFor(FlowContext c) =>
        c.Session.Vars.GetValueOrDefault("saucony.siteName")
        ?? StoreIdFor(c.Url)
        ?? "saucony_us";

    public static string CountryCodeFor(FlowContext c)
    {
        var raw = c.Session.Vars.GetValueOrDefault("saucony.country")
                  ?? c.Shipping?.Country
                  ?? c.Billing?.Country
                  ?? c.ProfileData?.Country;
        if (!string.IsNullOrWhiteSpace(raw))
        {
            var cc = raw.Trim().ToUpperInvariant();
            return cc == "UK" ? "GB" : cc;
        }

        return SiteNameFor(c) switch
        {
            "saucony_ca" => "CA",
            "saucony_eu" => "GB",
            "saucony_europe" => "EU",
            _ => "US",
        };
    }

    public static string LocaleSegmentFor(FlowContext c)
    {
        var cc = CountryCodeFor(c);
        return cc is "US" or "CA" ? "default" : "en_" + cc;
    }

    public static string SfccUrl(FlowContext c, string controller)
    {
        var site = SiteNameFor(c);
        var locale = LocaleSegmentFor(c);
        return $"{Origin(c.Url)}/on/demandware.store/Sites-{site}-Site/{locale}/{controller.TrimStart('/')}";
    }

    public static string CheckoutPath(FlowContext c)
    {
        var cc = CountryCodeFor(c);
        var prefix = cc switch
        {
            "CA" => "CA/en_CA",
            "US" => "en",
            "GB" => "UK/en_GB",
            _ => "en_" + cc.ToUpperInvariant(),
        };
        return prefix + "/checkout";
    }

    public static string CheckoutUrl(FlowContext c) => Origin(c.Url) + "/" + CheckoutPath(c);

    /// <summary>
    /// <c>GetHome</c> — plain GET against the storefront root.
    /// </summary>
    public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, c.Url, "saucony-home", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("saucony home unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"saucony home HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["home"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// <c>FindProduct</c> (<c>d__6</c>) — queries <c>ProductInfo-GetDimensionsAndVariations?productID={pid}</c>
    /// when a product id or variations URL is supplied, otherwise falls back to reading the product page.
    /// </summary>
    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var pid = ResolveProductId(c);
        if (c.Url.Contains("ProductInfo-GetDimensionsAndVariations", StringComparison.OrdinalIgnoreCase) ||
            !string.IsNullOrEmpty(pid))
        {
            var target = SfccUrl(c, $"ProductInfo-GetDimensionsAndVariations?productID={Uri.EscapeDataString(pid ?? string.Empty)}");
            var sfccRes = await GetAsync(c, target, "saucony-product", ct).ConfigureAwait(false);
            if (sfccRes is null) return StepOutcome.Fail("saucony product unreachable", retryable: true);
            if (!sfccRes.IsSuccess) return StepOutcome.Fail($"saucony product HTTP {sfccRes.StatusCode}", retryable: true);

            c.Session.Vars["raw"] = sfccRes.Body;
            if (!string.IsNullOrEmpty(pid))
            {
                c.Session.Vars["masterpid"] = pid!;
                c.Session.Vars["productId"] = pid!;
            }

            JObject json;
            try { json = JObject.Parse(sfccRes.Body); }
            catch (Exception ex) { return StepOutcome.Fail($"saucony product json: {ex.Message}", retryable: true); }

            if (IsTruthy(json["error"]))
                return StepOutcome.Fail("Waiting for product", retryable: true);

            var pName = json["productName"]?.ToString()
                        ?? json["name"]?.ToString()
                        ?? json["product"]?["productName"]?.ToString()
                        ?? json["product"]?["name"]?.ToString();
            if (!string.IsNullOrEmpty(pName)) c.Session.Vars["product"] = pName!;

            var pPrice = json["price"]?["sales"]?["value"]?.ToString()
                         ?? json["price"]?.ToString()
                         ?? json["product"]?["price"]?.ToString();
            if (!string.IsNullOrEmpty(pPrice)) c.Session.Vars["price"] = pPrice!;

            var wantedColor = c.Product?.Color;
            if (json["color"]?["values"] is JArray colorValues && colorValues.Count > 0)
            {
                JToken? pickedColor = null;
                if (!string.IsNullOrWhiteSpace(wantedColor))
                {
                    pickedColor = colorValues.FirstOrDefault(v =>
                        string.Equals(v["displayValue"]?.ToString(), wantedColor, StringComparison.OrdinalIgnoreCase) ||
                        string.Equals(v["value"]?.ToString(), wantedColor, StringComparison.OrdinalIgnoreCase) ||
                        string.Equals(v["id"]?.ToString(), wantedColor, StringComparison.OrdinalIgnoreCase));
                }
                pickedColor ??= colorValues.FirstOrDefault(v => IsTruthy(v["selected"])) ?? colorValues[0];
                var colorVal = pickedColor["value"]?.ToString()
                               ?? pickedColor["id"]?.ToString()
                               ?? pickedColor["displayValue"]?.ToString();
                if (!string.IsNullOrEmpty(colorVal))
                    c.Session.Vars["saucony.color"] = colorVal!;
            }

            var wantedSize = c.Product?.Sizes.FirstOrDefault() ?? c.Session.Vars.GetValueOrDefault("size");
            var chosenVariant = ExtractVariantId(json["variations"], wantedSize);
            if (!string.IsNullOrEmpty(chosenVariant))
            {
                c.Session.VariantId = chosenVariant;
                c.Session.Vars["variant"] = chosenVariant!;
                return StepOutcome.Success();
            }

            if (json["variations"] is not null)
                return StepOutcome.Fail("Waiting for product", retryable: true);

            return StepOutcome.Success();
        }

        var res = await GetAsync(c, c.Url, "saucony-product", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("saucony product unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"saucony product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;

        var name = Regex.Match(res.Body, @"""(?:productName|name|title)""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (!string.IsNullOrEmpty(name)) c.Session.Vars["product"] = name;

        var price = Regex.Match(res.Body, @"""(?:price|listPrice)""\s*:\s*""?([\d.,]+)""?").Groups[1].Value;
        if (!string.IsNullOrEmpty(price)) c.Session.Vars["price"] = price;

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        var pid = c.Session.VariantId
                  ?? c.Session.Vars.GetValueOrDefault("variant")
                  ?? c.Session.Vars.GetValueOrDefault("saucony.pid")
                  ?? c.Product?.Variant;
        if (string.IsNullOrEmpty(pid))
            return StepOutcome.Fail("saucony: no variant id for ATC", retryable: false);

        var masterpid = c.Session.Vars.GetValueOrDefault("masterpid")
                        ?? c.Session.Vars.GetValueOrDefault("productId")
                        ?? pid!;
        var usertype = c.Session.Vars.GetValueOrDefault("saucony.usertype") ?? "Wide";

        var form = new Dictionary<string, string>
        {
            ["usertype"] = usertype,
            ["isQuickView"] = "true",
            ["p_source"] = "quickview",
            ["source"] = "null",
            ["cartAction"] = "add",
            ["masterpid"] = masterpid,
            ["pid"] = pid!,
        };

        var res = await PostFormAsync(c, SfccUrl(c, "Cart-AddProduct?format=ajax"), form, "saucony-atc", ct)
            .ConfigureAwait(false);
        if (res is null || !res.IsSuccess)
            return StepOutcome.Fail("Waiting for restock (ATC)", retryable: true);

        var body = res.Body ?? string.Empty;
        var hasMiniCartTotal = body.Contains("mini-cart-total", StringComparison.OrdinalIgnoreCase);
        var qtyMatch = Regex.Match(
            body,
            @"class\s*=\s*[""'][^""']*\bmini-cart-quantity-bag\b[^""']*[""'][^>]*>(.*?)</",
            RegexOptions.IgnoreCase | RegexOptions.Singleline);
        var qtyText = qtyMatch.Success
            ? WebUtility.HtmlDecode(Regex.Replace(qtyMatch.Groups[1].Value, "<[^>]+>", string.Empty)).Trim()
            : string.Empty;

        if (!hasMiniCartTotal || !string.Equals(qtyText, "1", StringComparison.Ordinal))
            return StepOutcome.Fail("Waiting for restock (ATC)", retryable: true);

        var nameMatch = Regex.Match(
            body,
            @"class\s*=\s*[""'][^""']*\b(?:mini-cart-name|product-name)\b[^""']*[""'][^>]*>(.*?)</(?:a|span|div|h\d)>",
            RegexOptions.IgnoreCase | RegexOptions.Singleline);
        if (nameMatch.Success)
        {
            var title = WebUtility.HtmlDecode(Regex.Replace(nameMatch.Groups[1].Value, "<[^>]+>", string.Empty)).Trim();
            if (!string.IsNullOrEmpty(title)) c.Session.Vars["product"] = title;
        }

        var imgMatch = Regex.Match(body, @"<img\b[^>]*\bsrc\s*=\s*[""']([^""']+)[""']", RegexOptions.IgnoreCase);
        if (imgMatch.Success && !string.IsNullOrEmpty(imgMatch.Groups[1].Value))
            c.Session.Vars["image"] = WebUtility.HtmlDecode(imgMatch.Groups[1].Value);

        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, CheckoutUrl(c), "saucony-checkout", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("saucony checkout unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"saucony checkout HTTP {res.StatusCode}", retryable: true);

        c.Session.CheckoutUrl = res.Url.ToString();
        c.Session.Vars["checkout"] = res.Body;

        var csrf = Regex.Match(res.Body, @"csrfToken\s*:\s*""([^""]+)""").Groups[1].Value;
        if (string.IsNullOrEmpty(csrf))
            csrf = Regex.Match(res.Body, @"""csrfToken""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (string.IsNullOrEmpty(csrf))
            csrf = Regex.Match(res.Body, @"name\s*=\s*[""']csrf_token[""'][^>]*value\s*=\s*[""']([^""']+)[""']").Groups[1].Value;

        if (string.IsNullOrEmpty(csrf))
            return StepOutcome.Fail("saucony: missing csrfToken on checkout page", retryable: true);

        c.Session.Vars["csrfToken"] = csrf;
        c.Session.CsrfToken = csrf;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct)
    {
        var ship = c.Shipping ?? c.Billing ?? AddressFromProfile(c);
        if (ship is null) return StepOutcome.Fail("saucony: no shipping address");

        var site = SiteNameFor(c);
        var csrf = c.Session.Vars.GetValueOrDefault("csrfToken") ?? c.Session.CsrfToken ?? string.Empty;

        var form = new Dictionary<string, string>
        {
            ["dwfrm_singleshipping_shippingAddress_addressFields_firstName"] = ship.FirstName ?? string.Empty,
            ["dwfrm_singleshipping_shippingAddress_addressFields_lastName"] = ship.LastName ?? string.Empty,
            ["dwfrm_singleshipping_shippingAddress_addressFields_countries_country"] = ship.Country ?? CountryCodeFor(c),
            ["dwfrm_singleshipping_shippingAddress_addressFields_address1"] = ship.Address1 ?? string.Empty,
            ["dwfrm_singleshipping_shippingAddress_addressFields_address2"] = ship.Address2 ?? string.Empty,
            ["dwfrm_singleshipping_shippingAddress_addressFields_city"] = ship.City ?? string.Empty,
            ["dwfrm_singleshipping_shippingAddress_addressFields_zip"] = ship.ZipCode ?? string.Empty,
            ["dwfrm_singleshipping_shippingAddress_addToAddressBook"] = "false",
            ["dwfrm_singleshipping_shippingAddress_addressFields_poboxNumber"] = string.Empty,
            ["dwfrm_singleshipping_shippingAddress_addressFields_phone"] = c.ProfileData?.Phone ?? string.Empty,
            ["dwfrm_singleshipping_shippingAddress_addressFields_emailAddress"] = c.ProfileData?.Email ?? c.Account?.Email ?? string.Empty,
            ["dwfrm_singleshipping_email_addToEmailList"] = "false",
            ["dwfrm_singleshipping_ageVerification"] = "true",
            ["bypassBEV"] = "true",
            ["qasVerified"] = "false",
            ["isFrontEndValidated"] = "false",
            ["csrf_token"] = csrf,
        };

        if (string.Equals(site, "saucony_us", StringComparison.OrdinalIgnoreCase) ||
            string.Equals(site, "saucony_ca", StringComparison.OrdinalIgnoreCase))
        {
            form["dwfrm_singleshipping_shippingAddress_addressFields_states_state"] = ship.State ?? string.Empty;
        }

        var res = await PostFormAsync(c, SfccUrl(c, "Checkout-ContinueToBilling"), form, "saucony-shipping", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("saucony shipping unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"saucony shipping HTTP {res.StatusCode}", retryable: true);

        var json = TryParseJson(res.Body);
        if (json?["isShippingDataProvided"]?.ToObject<bool?>() != true)
            return StepOutcome.Fail("saucony: shipping data not accepted", retryable: false);

        c.Session.Vars["shipping"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitBillingAsync(FlowContext c, CancellationToken ct)
    {
        var bill = c.Billing ?? c.Shipping ?? AddressFromProfile(c);
        if (bill is null) return StepOutcome.Fail("saucony: no billing address");

        var card = c.Card;
        if (card?.Number is null) return StepOutcome.Fail("saucony: no card");

        var site = SiteNameFor(c);
        var csrf = c.Session.Vars.GetValueOrDefault("csrfToken") ?? c.Session.CsrfToken ?? string.Empty;
        var cardNumber = card.Number.Replace(" ", string.Empty);
        var cardType = cardNumber.StartsWith('3') ? "Amex" : cardNumber.StartsWith('4') ? "Visa" : "MasterCard";
        var expMonth = (card.Month ?? string.Empty).Trim().PadLeft(2, '0');
        var expYear = (card.Year ?? string.Empty).Trim();
        if (expYear.Length == 2) expYear = "20" + expYear;
        var expiration = $"{expMonth}/{expYear}";
        var email = c.ProfileData?.Email ?? c.Account?.Email ?? string.Empty;

        var form = new Dictionary<string, string>
        {
            ["dwfrm_billing_billingAddress_addressFields_firstName"] = bill.FirstName ?? string.Empty,
            ["dwfrm_billing_billingAddress_addressFields_lastName"] = bill.LastName ?? string.Empty,
            ["dwfrm_billing_billingAddress_addressFields_countries_country"] = bill.Country ?? CountryCodeFor(c),
            ["dwfrm_billing_billingAddress_addressFields_address1"] = bill.Address1 ?? string.Empty,
            ["dwfrm_billing_billingAddress_addressFields_address2"] = bill.Address2 ?? string.Empty,
            ["dwfrm_billing_billingAddress_addressFields_city"] = bill.City ?? string.Empty,
            ["dwfrm_billing_billingAddress_addressFields_zip"] = bill.ZipCode ?? string.Empty,
            ["dwfrm_billing_billingAddress_addressFields_phone"] = c.ProfileData?.Phone ?? string.Empty,
            ["dwfrm_billing_billingAddress_addressFields_emailAddress"] = email,
            ["dwfrm_billing_paymentMethods_creditCard_number"] = cardNumber,
            ["dwfrm_billing_paymentMethods_creditCard_owner"] = card.Name ?? bill.FullName,
            ["dwfrm_billing_paymentMethods_creditCard_expiration"] = expiration,
            ["dwfrm_billing_paymentMethods_creditCard_cvn"] = card.Cvv ?? string.Empty,
            ["dwfrm_billing_paymentMethods_creditCard_saveCard"] = "false",
            ["dwfrm_billing_paymentMethods_creditCard_type"] = cardType,
            ["dwfrm_billing_paymentMethods_ideal_subBank"] = string.Empty,
            ["dwfrm_billing_paymentMethods_sofurt_sofurt__bankcode"] = string.Empty,
            ["dwfrm_billing_paymentMethods_selectedPaymentMethodID"] = "CREDIT_CARD",
            ["dwfrm_singleshipping_shippingAddress_useAsBillingAddress"] = c.Billing is null ? "true" : "false",
            ["dwfrm_singleshipping_email_addToEmailList"] = "false",
            ["csrf_token"] = csrf,
        };

        if (string.Equals(site, "saucony_us", StringComparison.OrdinalIgnoreCase) ||
            string.Equals(site, "saucony_ca", StringComparison.OrdinalIgnoreCase))
        {
            form["dwfrm_billing_billingAddress_addressFields_states_state"] = bill.State ?? string.Empty;
        }

        var res = await PostFormAsync(c, SfccUrl(c, "Checkout-SubmitPaymentDetails"), form, "saucony-billing", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("saucony billing unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"saucony billing HTTP {res.StatusCode}", retryable: true);

        var json = TryParseJson(res.Body);
        if (IsTruthy(json?["cart"]?["valid"]?["error"]) || IsTruthy(json?["error"]))
            return StepOutcome.Fail("saucony: payment details rejected", retryable: false);

        c.Session.Vars["billing"] = res.Body;
        return StepOutcome.Success();
    }

    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        var site = SiteNameFor(c);
        var csrf = c.Session.Vars.GetValueOrDefault("csrfToken") ?? c.Session.CsrfToken ?? string.Empty;
        var form = new Dictionary<string, string>
        {
            ["dwfrm_singleshipping_email_addToEmailList"] = "false",
            ["csrf_token"] = csrf,
        };

        var res = await PostFormAsync(c, SfccUrl(c, "CheckoutHelper-PlaceOrder"), form, "saucony-order", ct)
            .ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("Error submitting order", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"saucony order HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["order"] = res.Body;

        var json = TryParseJson(res.Body);
        if ((string.Equals(site, "saucony_eu", StringComparison.OrdinalIgnoreCase) ||
             string.Equals(site, "saucony_europe", StringComparison.OrdinalIgnoreCase)) &&
            IsTruthy(json?["isPAEnable"]))
        {
            var jwt = json?["jwtToken"]?.ToString() ?? json?["jwt"]?.ToString();
            if (!string.IsNullOrEmpty(jwt))
                c.Session.Vars["saucony.jwtToken"] = jwt!;
            return await PayerAuthenticateAsync(c, ct).ConfigureAwait(false);
        }

        return HandleOrderResult(c, res.Body);
    }

    /// <summary>
    /// <c>HandleOrderResult</c> (<c>d__12</c>) — inspects the <c>CheckoutHelper-PlaceOrder</c> reply.
    /// </summary>
    public StepOutcome HandleOrderResult(FlowContext c) =>
        HandleOrderResult(c, c.Session.Vars.GetValueOrDefault("order"));

    /// <summary>
    /// <c>HandleOrderResult</c> (<c>d__12</c>) — inspects <paramref name="responseBody"/> (or <c>order</c> in session vars).
    /// </summary>
    public StepOutcome HandleOrderResult(FlowContext c, string? responseBody)
    {
        var body = responseBody ?? c.Session.Vars.GetValueOrDefault("order");
        if (string.IsNullOrWhiteSpace(body))
            return StepOutcome.Fail("Error submitting order", retryable: true);

        var json = TryParseJson(body);
        if (json is null)
            return StepOutcome.Fail("Error submitting order", retryable: true);

        var redirectUrl = json["redirectUrl"]?.ToString();
        if (!string.IsNullOrEmpty(redirectUrl))
        {
            if (redirectUrl.Contains("/cart", StringComparison.OrdinalIgnoreCase))
                return StepOutcome.Fail("Waiting for restock", retryable: true);

            var orderId = ExtractOrderNumber(json, redirectUrl);
            if (!string.IsNullOrEmpty(orderId))
                c.Session.OrderNumber = orderId;
            return StepOutcome.Success();
        }

        if (json["error"]?.Type == JTokenType.Boolean && !json["error"]!.Value<bool>())
        {
            var orderId = ExtractOrderNumber(json, null);
            if (!string.IsNullOrEmpty(orderId))
                c.Session.OrderNumber = orderId;
            return StepOutcome.Success();
        }

        if (IsTruthy(json["paymentError"]?["declined"]) ||
            string.Equals(json["paymentError"]?.ToString(), "declined", StringComparison.OrdinalIgnoreCase))
        {
            return StepOutcome.Fail("Card declined", retryable: false);
        }

        if (string.Equals(json["errorMessage"]?.ToString(), "Your order could not be submitted.",
                StringComparison.Ordinal))
        {
            return StepOutcome.Fail("Waiting for restock", retryable: true);
        }

        return StepOutcome.Fail("Error submitting order", retryable: true);
    }

    /// <summary>
    /// <c>PayerAuthenticate</c> (<c>d__13</c>) — synchronous classification helper when a caller supplies
    /// <c>saucony.threeDsReply</c> directly.
    /// </summary>
    public StepOutcome PayerAuthenticate(FlowContext c)
    {
        var replyText = c.Session.Vars.GetValueOrDefault("saucony.threeDsReply");
        if (string.IsNullOrWhiteSpace(replyText))
            return StepOutcome.Fail("saucony: PayerAuthenticate (d__13) requires saucony.threeDsReply or PayerAuthenticateAsync", retryable: false);

        JObject reply;
        try
        {
            reply = JObject.Parse(replyText!);
        }
        catch (Newtonsoft.Json.JsonException)
        {
            return StepOutcome.Fail("saucony: saucony.threeDsReply is not valid JSON", retryable: false);
        }

        var (shape, url, jwt) = SauconyThreeDs.Classify(reply);
        c.Session.Vars["saucony.threeDsShape"] = shape.ToString();
        if (!string.IsNullOrEmpty(url)) c.Session.Vars["saucony.threeDsUrl"] = url;
        if (!string.IsNullOrEmpty(jwt)) c.Session.Vars["saucony.threeDsJwt"] = jwt;

        return shape == SauconyThreeDs.Shape.Unexpected
            ? StepOutcome.Fail(SauconyThreeDs.UnexpectedResponseMessage, retryable: false)
            : StepOutcome.Success();
    }

    /// <summary>
    /// <c>PayerAuthenticate</c> (<c>d__13</c>) — EU/UK 3-D Secure validation call, Cardinal Cruise StepUp,
    /// and final authentic order completion.
    /// </summary>
    public async Task<StepOutcome> PayerAuthenticateAsync(FlowContext c, CancellationToken ct = default)
    {
        var csrf = c.Session.Vars.GetValueOrDefault("csrfToken") ?? c.Session.CsrfToken ?? string.Empty;
        var placeOrderUrl = SfccUrl(c, "CheckoutHelper-PlaceOrder");

        var validationForm = new Dictionary<string, string>
        {
            ["isPayerValidationCall"] = "true",
            ["csrf_token"] = csrf,
        };
        var valRes = await PostFormAsync(c, placeOrderUrl, validationForm, "saucony-payer-validate", ct)
            .ConfigureAwait(false);
        if (valRes is null || !valRes.IsSuccess)
            return StepOutcome.Fail("saucony: payer validation failed", retryable: true);

        c.Session.Vars["saucony.threeDsReply"] = valRes.Body ?? string.Empty;
        var valJson = TryParseJson(valRes.Body);
        var (shape, url, jwt) = SauconyThreeDs.Classify(valJson);
        c.Session.Vars["saucony.threeDsShape"] = shape.ToString();
        if (!string.IsNullOrEmpty(url)) c.Session.Vars["saucony.threeDsUrl"] = url!;
        if (!string.IsNullOrEmpty(jwt)) c.Session.Vars["saucony.threeDsJwt"] = jwt!;

        if (shape == SauconyThreeDs.Shape.Unexpected)
            return StepOutcome.Fail(SauconyThreeDs.UnexpectedResponseMessage, retryable: false);

        if (shape == SauconyThreeDs.Shape.StepUp)
        {
            var stepUpTarget = c.Session.Vars.GetValueOrDefault("saucony.stepUpUrl")
                               ?? (!string.IsNullOrEmpty(url) ? url! : CardinalStepUpUrl);
            var md = valJson?["MD"]?.ToString()
                     ?? valJson?["data"]?["MD"]?.ToString()
                     ?? c.Session.Vars.GetValueOrDefault("saucony.md")
                     ?? string.Empty;
            var returnUrl = c.Session.Vars.GetValueOrDefault("saucony.payerAuthReturnUrl")
                            ?? SfccUrl(c, "PayerAuth-Return");
            var stepUpForm = new Dictionary<string, string>
            {
                ["JWT"] = jwt ?? c.Session.Vars.GetValueOrDefault("saucony.jwtToken") ?? string.Empty,
                ["MD"] = md,
                ["ReturnUrl"] = returnUrl,
            };

            var stepRes = await PostFormAsync(c, stepUpTarget, stepUpForm, "saucony-stepup", ct)
                .ConfigureAwait(false);
            if (stepRes is null || !stepRes.IsSuccess)
                return StepOutcome.Fail("saucony: cardinal step-up failed", retryable: true);
        }

        var browserfields = c.Session.Vars.GetValueOrDefault("saucony.browserfields")
                            ?? """{"colorDepth":24,"javaEnabled":false,"language":"en-US","screenHeight":1067,"screenWidth":1707,"timeZoneOffset":-60}""";
        var authForm = new Dictionary<string, string>
        {
            ["isPayerAuthenticCall"] = "true",
            ["browserfields"] = browserfields,
            ["csrf_token"] = csrf,
        };
        var authRes = await PostFormAsync(c, placeOrderUrl, authForm, "saucony-payer-auth", ct)
            .ConfigureAwait(false);
        if (authRes is null || !authRes.IsSuccess)
            return StepOutcome.Fail("Error submitting order", retryable: true);

        c.Session.Vars["order"] = authRes.Body;
        return HandleOrderResult(c, authRes.Body);
    }

    /// <summary>
    /// Which store id applies to a host, out of the four the image names. Returns null when the host is
    /// not one of the regional storefronts, rather than defaulting to the US id.
    /// </summary>
    public static string? StoreIdFor(string? url)
    {
        var host = FlowHost(url);
        if (host.Length == 0) return null;
        if (!host.Contains("saucony", StringComparison.Ordinal)) return null;
        if (host.EndsWith(".ca", StringComparison.Ordinal)) return "saucony_ca";
        if (host.EndsWith(".co.uk", StringComparison.Ordinal)) return "saucony_eu";
        if (host.EndsWith(".eu", StringComparison.Ordinal)) return "saucony_europe";
        if (host.EndsWith(".com", StringComparison.Ordinal)) return "saucony_us";
        return null;
    }

    private static string? ResolveProductId(FlowContext c)
    {
        var explicitPid = c.Session.Vars.GetValueOrDefault("saucony.pid");
        if (!string.IsNullOrEmpty(explicitPid)) return explicitPid;

        var urlPid = Regex.Match(c.Url ?? string.Empty, @"[?&](?:productID|pid)=([^&#]+)", RegexOptions.IgnoreCase);
        if (urlPid.Success) return Uri.UnescapeDataString(urlPid.Groups[1].Value);

        if (!string.IsNullOrEmpty(c.Product?.Variant)) return c.Product.Variant;

        var input = c.Product?.Input;
        if (!string.IsNullOrWhiteSpace(input))
        {
            var inQuery = Regex.Match(input, @"[?&](?:productID|pid)=([^&#]+)", RegexOptions.IgnoreCase);
            if (inQuery.Success) return Uri.UnescapeDataString(inQuery.Groups[1].Value);
            if (!input.Contains("://", StringComparison.Ordinal)) return input.Trim();
            var inHtml = Regex.Match(input, @"-([A-Za-z0-9_\-]+)\.html", RegexOptions.IgnoreCase);
            if (inHtml.Success) return inHtml.Groups[1].Value;
        }

        if ((c.Url ?? string.Empty).Contains("ProductInfo-GetDimensionsAndVariations", StringComparison.OrdinalIgnoreCase))
            return c.Session.Vars.GetValueOrDefault("productId");

        return null;
    }

    private static string? ExtractVariantId(JToken? variations, string? wantedSize)
    {
        if (variations is null) return null;

        var list = new List<(string Id, string Size, bool Available)>();
        if (variations is JArray arr)
        {
            foreach (var item in arr)
                CollectVariant(item, null, list);
        }
        else if (variations is JObject obj)
        {
            if (obj["variants"] is JArray innerArr)
            {
                foreach (var item in innerArr)
                    CollectVariant(item, null, list);
            }
            else
            {
                foreach (var prop in obj.Properties())
                    CollectVariant(prop.Value, prop.Name, list);
            }
        }

        if (list.Count == 0) return null;
        if (!string.IsNullOrWhiteSpace(wantedSize))
        {
            var sizeMatch = list.FirstOrDefault(v =>
                v.Available && string.Equals(v.Size, wantedSize.Trim(), StringComparison.OrdinalIgnoreCase));
            if (!string.IsNullOrEmpty(sizeMatch.Id)) return sizeMatch.Id;
        }

        var firstAvail = list.FirstOrDefault(v => v.Available);
        return !string.IsNullOrEmpty(firstAvail.Id) ? firstAvail.Id : list[0].Id;
    }

    private static void CollectVariant(JToken token, string? keyName, List<(string Id, string Size, bool Available)> list)
    {
        if (token is JValue val)
        {
            var str = val.ToString();
            if (!string.IsNullOrEmpty(str))
                list.Add((str, keyName ?? string.Empty, true));
            return;
        }

        if (token is not JObject obj) return;
        var id = obj["id"]?.ToString()
                 ?? obj["pid"]?.ToString()
                 ?? obj["variantId"]?.ToString()
                 ?? obj["sku"]?.ToString()
                 ?? keyName
                 ?? string.Empty;
        if (string.IsNullOrEmpty(id)) return;

        var size = obj["size"]?.ToString()
                   ?? obj["displayValue"]?.ToString()
                   ?? obj["value"]?.ToString()
                   ?? keyName
                   ?? string.Empty;
        var available = obj["available"]?.ToObject<bool?>()
                        ?? obj["inStock"]?.ToObject<bool?>()
                        ?? obj["selectable"]?.ToObject<bool?>()
                        ?? true;
        list.Add((id, size, available));
    }

    private static string? ExtractOrderNumber(JObject json, string? redirectUrl)
    {
        var orderId = json["orderNo"]?.ToString()
                      ?? json["orderID"]?.ToString()
                      ?? json["orderNumber"]?.ToString();
        if (!string.IsNullOrEmpty(orderId)) return orderId;

        if (!string.IsNullOrEmpty(redirectUrl))
        {
            var m = Regex.Match(redirectUrl, @"[?&](?:orderNo|orderID|orderNumber)=([^&#]+)", RegexOptions.IgnoreCase);
            if (m.Success) return Uri.UnescapeDataString(m.Groups[1].Value);
        }

        return null;
    }

    private static JObject? TryParseJson(string? body)
    {
        if (string.IsNullOrWhiteSpace(body)) return null;
        try { return JObject.Parse(body); }
        catch { return null; }
    }

    private static bool IsTruthy(JToken? token)
    {
        if (token is null || token.Type == JTokenType.Null) return false;
        if (token.Type == JTokenType.Boolean) return token.Value<bool>();
        if (token.Type == JTokenType.Integer) return token.Value<long>() != 0;
        var s = token.ToString();
        return !string.IsNullOrWhiteSpace(s) && !string.Equals(s, "false", StringComparison.OrdinalIgnoreCase);
    }

    private static string FlowHost(string? url)
    {
        if (string.IsNullOrEmpty(url)) return string.Empty;
        if (!Uri.TryCreate(url, UriKind.Absolute, out var uri)) return string.Empty;
        return uri.Host.ToLowerInvariant();
    }

    private static Cybersole.Core.Models.Address? AddressFromProfile(FlowContext c)
    {
        var p = c.ProfileData;
        if (p is null) return null;
        return new Cybersole.Core.Models.Address
        {
            FirstName = p.FirstName,
            LastName = p.LastName,
            Address1 = p.Address1,
            Address2 = p.Address2,
            City = p.City,
            State = p.State,
            ZipCode = p.Zip,
            Country = p.Country,
        };
    }
}
