using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Loopback behavioral parity probes for Batch 3C safe payment, GraphQL, storefront,
/// and HTTP transport surfaces. Every probe asserts real wire requests (method, path,
/// headers, payload fields) and session state mutations against local <see cref="TinyServer"/>
/// endpoints with zero external network I/O or anti-bot bypasses.
/// </summary>
public sealed class C7cBehavioralParityTests
{
    private static Profile SampleProfile(string country = "US") => new()
    {
        FirstName = "Ada",
        LastName = "Lovelace",
        Email = "ada@parity.test",
        Phone = "5550199",
        Address1 = "101 Main St",
        Address2 = "Suite 4",
        City = "Austin",
        State = "TX",
        Zip = "78701",
        Country = country,
    };

    private static Card SampleCard() => new()
    {
        Number = "4111111111114242",
        Month = "08",
        Year = "2031",
        Cvv = "737",
        Name = "Ada Lovelace",
    };

    private static string FakeJwt(JObject payload)
    {
        static string B64Url(string s) =>
            Convert.ToBase64String(Encoding.UTF8.GetBytes(s))
                .TrimEnd('=').Replace('+', '-').Replace('/', '_');

        return B64Url("{\"alg\":\"RS256\"}") + "." +
               B64Url(payload.ToString(Newtonsoft.Json.Formatting.None)) + ".sig";
    }

    [Fact]
    public async Task WarhammerCommercetoolsExecutesFullChainAndCreditCardPoll()
    {
        var opsSeen = new List<string>();
        var flexTokensUrl = string.Empty;

        using var flexServer = new TinyServer((_, _) => (200, "{\"token\":\"flex_tok_99\",\"cardType\":\"001\"}"));
        flexTokensUrl = flexServer.BaseUrl + "/flex/v2/tokens";
        var captureJwt = FakeJwt(new JObject { ["flx"] = new JObject { ["tokensUrl"] = flexTokensUrl } });

        var pollCount = 0;
        using var apiServer = new TinyServer((req, body) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path.StartsWith("/payments/creditCardWithPayerAuthentication/", StringComparison.Ordinal))
            {
                pollCount++;
                return pollCount == 1
                    ? (200, "{\"status\":\"PENDING\"}")
                    : (200, "{\"status\":\"AUTHORIZED\",\"orderNumber\":\"WH-CT-777\"}");
            }

            if (path == "/graphql")
            {
                var doc = JObject.Parse(body);
                var op = doc["operationName"]?.ToString() ?? string.Empty;
                if (string.IsNullOrEmpty(op) &&
                    (doc["query"]?.ToString()?.Contains("addPaymentToCart", StringComparison.Ordinal) ?? false))
                    op = "addPaymentToCart";
                opsSeen.Add(op);
                return op switch
                {
                    "createCartByStore" => (200, "{\"data\":{\"createMyCart\":{\"id\":\"ct-cart-1\",\"version\":1}}}"),
                    "getCart" => (200, "{\"data\":{\"inStore\":{\"me\":{\"activeCart\":{\"id\":\"ct-cart-1\",\"version\":1,\"lineItems\":[{\"id\":\"li-1\",\"quantity\":1}]}}}}}"),
                    "addToCartByChannel" => (200, "{\"data\":{\"updateMyCart\":{\"id\":\"ct-cart-1\",\"version\":2}}}"),
                    "initiateCheckout" => (200, "{\"data\":{\"initiateCheckout\":{\"id\":\"ct-chk-1\",\"version\":3}}}"),
                    "saveAddress" => (200, "{\"data\":{\"setShippingAddress\":{\"id\":\"ct-cart-1\",\"version\":4}}}"),
                    "maintainShippingGroups" => (200, "{\"data\":{\"maintainMyShippingGroups\":{\"id\":\"ct-cart-1\",\"version\":5,\"isAbleToCheckout\":true}}}"),
                    "createMyPayment" => (200, new JObject
                    {
                        ["data"] = new JObject
                        {
                            ["createMyPayment"] = new JObject
                            {
                                ["id"] = "pay-ct-1",
                                ["version"] = 1,
                                ["custom"] = new JObject
                                {
                                    ["customFieldsRaw"] = new JArray
                                    {
                                        new JObject
                                        {
                                            ["name"] = CybersourcePayment.CaptureContextSignatureKey,
                                            ["value"] = captureJwt,
                                        },
                                    },
                                },
                            },
                        },
                    }.ToString(Newtonsoft.Json.Formatting.None)),
                    "addPaymentToCart" => (200, "{\"data\":{\"updateMyCart\":{\"id\":\"ct-cart-1\",\"version\":6,\"isAbleToCheckout\":true}}}"),
                    "updateMyCart" => (200, "{\"data\":{\"updateMyCart\":{\"id\":\"ct-cart-1\",\"version\":6,\"isAbleToCheckout\":true}}}"),
                    "updateMyPaymentWithActions" => (200, "{\"data\":{\"updateMyPayment\":{\"id\":\"pay-ct-1\",\"version\":2}}}"),
                    "removeLineItemFromCart" => (200, "{\"data\":{\"updateMyCart\":{\"id\":\"ct-cart-1\",\"version\":7}}}"),
                    _ => (404, "{}"),
                };
            }

            return (200, "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = "https://www.warhammer.com/en-US/",
            ProfileData = SampleProfile(),
            Card = SampleCard(),
        };
        ctx.Session.Vars["wh.commercetools"] = "true";
        ctx.Session.Vars["wh.apiHost"] = apiServer.BaseUrl;
        ctx.Session.Vars["wh.pollMs"] = "0";
        ctx.Session.Vars["wh.gwToken"] = "gw-tok";
        ctx.Session.Vars["wh.productId"] = "prod-wh-1";
        ctx.Session.Vars["awsWafToken"] = "aws-waf-1";
        ctx.Session.Vars["accessToken"] = "bearer-ct";

        var flow = new WarhammerFlow();
        Assert.True((await flow.CreateCartAsync(ctx, default)).Ok);
        Assert.True((await flow.GetCartAsync(ctx, default)).Ok);
        Assert.True((await flow.AddToCartAsync(ctx, default)).Ok);
        Assert.True((await flow.InitiateCheckoutAsync(ctx, default)).Ok);
        Assert.True((await flow.SubmitShippingAsync(ctx, default)).Ok);
        Assert.True((await flow.SubmitBillingAsync(ctx, default)).Ok);
        Assert.True((await flow.Process3DSAsync(ctx, default)).Ok);
        Assert.True((await flow.ClearCartAsync(ctx, default)).Ok);

        Assert.Equal(apiServer.BaseUrl + "/graphql", ctx.Session.Vars["storeSession.origin"]);
        Assert.Equal("flex_tok_99", ctx.Session.PaymentToken);
        Assert.Equal("WH-CT-777", ctx.Session.OrderNumber);
        Assert.Contains("createCartByStore", opsSeen);
        Assert.Contains("getCart", opsSeen);
        Assert.Contains("addToCartByChannel", opsSeen);
        Assert.Contains("initiateCheckout", opsSeen);
        Assert.Contains("saveAddress", opsSeen);
        Assert.Contains("maintainShippingGroups", opsSeen);
        Assert.Contains("createMyPayment", opsSeen);
        Assert.Contains("updateMyPaymentWithActions", opsSeen);
        Assert.Contains("removeLineItemFromCart", opsSeen);
        Assert.Single(flexServer.Requests);
        Assert.Equal(2, pollCount);
        Assert.NotEmpty(apiServer.RequestHeaders[0]["x-trace-id"]);
    }

    [Fact]
    public async Task JdSportsFinlOwnershipWiresGraphQlHashSuiteAndVantivEProtect()
    {
        var opsSeen = new List<string>();
        using var server = new TinyServer((req, body) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == "/eprotect")
                return (200, "{\"paypageRegistrationId\":\"finl_reg_1\"}");

            if (path == "/graphql")
            {
                var doc = JObject.Parse(body);
                var op = doc["operationName"]?.ToString() ?? string.Empty;
                if (string.IsNullOrEmpty(op) &&
                    (doc["query"]?.ToString()?.Contains("addPaymentToCart", StringComparison.Ordinal) ?? false))
                    op = "addPaymentToCart";
                opsSeen.Add(op);
                return op switch
                {
                    "GetCartCookie" => (200, "{\"data\":{\"getCartCookie\":{\"ctCartJWT\":\"jwt-finl-1\"}}}"),
                    "GetProductInventory" => (200, "{\"data\":{\"productInventory\":{\"hasStock\":true,\"inventory\":{\"sizes\":[{\"sku\":\"SKU-FINL-9\"}]}}}}"),
                    "GetCart" => (200, "{\"data\":{\"getCart\":{\"id\":\"finl-cart-1\"}}}"),
                    "UpdateContactDetails" => (200, "{\"data\":{\"updateContactDetails\":{\"ok\":true}}}"),
                    "updateShipAddress" => (200, "{\"data\":{\"updateShipAddress\":{\"id\":\"finl-cart-1\"}}}"),
                    "AddCreditCard" => (200, "{\"data\":{\"addCreditCard\":{\"paymentInfo\":{\"payments\":[{\"id\":\"finl-pay-1\"}]}}}}"),
                    _ when body.Contains("submitOrder(cartToken", StringComparison.Ordinal) =>
                        (200, "{\"data\":{\"submitOrder\":{\"id\":\"ord-1\",\"customerId\":\"cust-1\",\"orderNumber\":\"FINL-888\"}}}"),
                    _ => (404, "{}"),
                };
            }
            return (404, "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = "https://www.finishline.com/store/product/shoe",
            ProfileData = SampleProfile(),
            Card = SampleCard(),
        };
        ctx.Session.Vars["jdsports.finl"] = "true";
        ctx.Session.Vars["jdsports.apiUrl"] = server.BaseUrl + "/graphql";
        ctx.Session.Vars["jdsports.paypageUrl"] = server.BaseUrl + "/eprotect";
        ctx.Session.Vars["jdsports.productId"] = "prod-finl-1";
        ctx.Session.Vars["jdsports.cartToken"] = "ctok-finl-1";

        // Verify www -> api URL rewrite rule directly
        var bareCtx = new FlowContext { Http = http, Url = "https://www.jdsports.com/product/p1" };
        Assert.Equal("https://api.jdsports.com/graphql", JdSportsFlow.FinlApiUrl(bareCtx));

        var flow = new JdSportsFlow();
        Assert.True((await flow.VerifySessionAsync(ctx, default)).Ok);
        Assert.True((await flow.FindProductAsync(ctx, default)).Ok);
        Assert.True((await flow.GetCartAsync(ctx, default)).Ok);
        Assert.True((await flow.SubmitEmailAsync(ctx, default)).Ok);
        Assert.True((await flow.SubmitShippingAsync(ctx, default)).Ok);
        Assert.True((await flow.SubmitBillingAsync(ctx, default)).Ok);
        Assert.True((await flow.SubmitOrderAsync(ctx, default)).Ok);

        Assert.Equal("jwt-finl-1", ctx.Session.Vars["jdsports.ctCartJwt"]);
        Assert.Equal("SKU-FINL-9", ctx.Session.VariantId);
        Assert.Equal("FINL-888", ctx.Session.OrderNumber);
        Assert.Equal(new[] { "GetCartCookie", "GetProductInventory", "GetCart", "UpdateContactDetails", "updateShipAddress", "AddCreditCard" },
            opsSeen.Take(6).ToArray());
    }

    [Fact]
    public async Task CasioPreCheckoutAndStripeAdyenSquareNonPowGatewaysExecuteFaithfully()
    {
        var seenTargets = new List<string>();
        var shippingPayloads = new List<JObject>();

        using var server = new TinyServer((req, body) =>
        {
            var rawTarget = req.RawUrl ?? "/";
            var path = req.Url?.AbsolutePath ?? "/";
            seenTargets.Add(rawTarget);

            if (path == "/graphql" && body.Contains("customerCart", StringComparison.Ordinal))
                return (200, "{\"data\":{\"customerCart\":{\"id\":\"casio-c1\",\"total_quantity\":1,\"items\":[{\"uid\":\"u1\",\"quantity\":1}]}}}");
            if (path == "/graphql" && body.Contains("updateCartItems", StringComparison.Ordinal))
                return (200, "{\"data\":{\"updateCartItems\":{\"cart\":{\"id\":\"casio-c1\",\"total_quantity\":0,\"items\":[]}}}}");

            if (path.EndsWith("/set-guest-email-address", StringComparison.Ordinal))
                return (200, "true");
            if (path.EndsWith("/estimate-shipping-methods", StringComparison.Ordinal))
                return (200, "[{\"carrier_code\":\"ups\",\"method_code\":\"ground\"}]");
            if (path.EndsWith("/shipping-information", StringComparison.Ordinal))
            {
                shippingPayloads.Add(JObject.Parse(body));
                return (200, "{\"payment_methods\":[]}");
            }
            if (path.EndsWith("/get_stripe_configuration", StringComparison.Ordinal))
                return (200, "{\"apiKey\":\"pk_live_casio\"}");
            if (path.EndsWith("/set-payment-information", StringComparison.Ordinal))
                return (200, "true");
            if (path.EndsWith("/payment-information", StringComparison.Ordinal))
                return (200, "\"100042\"");
            if (path.EndsWith("/stripe/payments/get_requires_action", StringComparison.Ordinal))
                return (200, "{\"clientSecret\":\"pi_casio_secret_cs_1\"}");
            if (path.StartsWith("/v1/payment_intents/", StringComparison.Ordinal))
                return (200, "{\"id\":\"pi_casio\",\"status\":\"succeeded\"}");
            if (path.Contains("/adyen/orders/", StringComparison.Ordinal))
                return (200, "{\"action\":{\"type\":\"threeDS2\",\"token\":\"tok-3ds\"}}");
            if (path.Contains("/payments-details", StringComparison.Ordinal))
                return (200, "{\"resultCode\":\"Authorised\"}");
            if (path == "/payments/hydrate")
                return (200, "{\"instanceId\":\"sq-inst\"}");

            return (404, "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var casio = new CasioFlow();

        // 1) Pre-checkout + Stripe gateway (non-PoW)
        var stripeCtx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/products/gshock",
            ProfileData = SampleProfile(),
            Card = SampleCard(),
        };
        stripeCtx.Session.CartId = "casio-c1";
        stripeCtx.Session.Vars["casio.graphqlPath"] = server.BaseUrl + "/graphql";
        stripeCtx.Session.Vars["casio.siteBase"] = server.BaseUrl + "/us";
        stripeCtx.Session.Vars["stripe.storeOrigin"] = server.BaseUrl;
        stripeCtx.Session.Vars["stripe.storeCode"] = "us";
        stripeCtx.Session.Vars["stripe.apiUrl"] = server.BaseUrl;
        stripeCtx.Session.Vars["stripe.paymentMethodId"] = "pm_casio_1";
        stripeCtx.Session.Vars["casio.gateway"] = "stripe";

        Assert.True((await casio.ClearCartAsync(stripeCtx, default)).Ok);
        Assert.True((await casio.SubmitEmailAsync(stripeCtx, default)).Ok);
        Assert.True((await casio.GetShippingRatesAsync(stripeCtx, default)).Ok);
        Assert.True((await casio.SubmitShippingAsync(stripeCtx, default)).Ok);
        Assert.True((await casio.SubmitPaymentAsync(stripeCtx, default)).Ok);
        Assert.True((await casio.SubmitOrderAsync(stripeCtx, default)).Ok);
        Assert.True((await casio.Process3DSAsync(stripeCtx, default)).Ok);

        // Stripe shipping extension_attributes is empty {}
        Assert.Empty((JObject)shippingPayloads[0]["addressInformation"]!["extension_attributes"]!);
        Assert.Contains(seenTargets, t => t.Contains("2025-08-27.basil", StringComparison.Ordinal));

        // 2) Adyen gateway
        var adyenCtx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/products/gshock",
            ProfileData = SampleProfile(),
            Card = SampleCard(),
        };
        adyenCtx.Session.CartId = "casio-c2";
        adyenCtx.Session.Vars["casio.siteBase"] = server.BaseUrl + "/us";
        adyenCtx.Session.Vars["casio.gateway"] = "adyen";
        adyenCtx.Session.Vars["threeDsPayload"] = "adyen-3ds-res";

        Assert.True((await casio.SubmitShippingAsync(adyenCtx, default)).Ok);
        Assert.True((await casio.SubmitPaymentAsync(adyenCtx, default)).Ok);
        Assert.True((await casio.SubmitOrderAsync(adyenCtx, default)).Ok);
        Assert.True((await casio.Process3DSAsync(adyenCtx, default)).Ok);
        Assert.False(shippingPayloads[1]["addressInformation"]!["extension_attributes"]!["membership_agreement_data"]!.Value<bool>());

        // 3) Square gateway (non-PoW)
        var squareCtx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/products/gshock",
            ProfileData = SampleProfile(),
            Card = SampleCard(),
        };
        squareCtx.Session.CartId = "casio-c3";
        squareCtx.Session.Vars["casio.siteBase"] = server.BaseUrl + "/us";
        squareCtx.Session.Vars["casio.gateway"] = "square";
        squareCtx.Session.Vars["square.hydrateUrl"] = server.BaseUrl + "/payments/hydrate";
        squareCtx.Session.Vars["square.nonce"] = "cnon:preset-nonpow";

        Assert.True((await casio.SubmitPaymentAsync(squareCtx, default)).Ok);
        Assert.True((await casio.SubmitOrderAsync(squareCtx, default)).Ok);
        Assert.Equal("100042", squareCtx.Session.OrderNumber);
        Assert.Contains(seenTargets, t => t.Contains("/payments/hydrate?applicationId=", StringComparison.Ordinal));
    }

    [Fact]
    public async Task ScheelsApiHubWiresAllStorefrontApiOpsAndKeepsSearchEndpoint()
    {
        var gqlOps = new List<string>();
        var sawSearch = false;

        using var server = new TinyServer((req, body) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == "/api/graphql")
            {
                var doc = JObject.Parse(body);
                var op = doc["operationName"]?.ToString() ?? string.Empty;
                gqlOps.Add(op);
                if (op == "AddItemToCart")
                {
                    Assert.Single(((JObject)doc["variables"]!).Properties());
                    Assert.NotNull(doc["variables"]!["input"]);
                }

                return op switch
                {
                    "getSession" => (200, "{\"data\":{\"session\":{\"access_token\":\"tok-sc-1\"}}}"),
                    "Product" => (200, "{\"data\":{\"product\":{\"id\":\"p-sc-1\",\"name\":\"Boot\",\"price\":\"199.99\"}}}"),
                    "CreateInitialCart" => (200, "{\"data\":{\"createCart\":{\"id\":\"sc-cart-1\"}}}"),
                    "AddItemToCart" => (200, "{\"data\":{\"addItemToCart\":{\"id\":\"sc-cart-1\"}}}"),
                    "CheckoutCart" => (200, "{\"data\":{\"cart\":{\"id\":\"sc-cart-1\"}}}"),
                    "UpdateCustomerForCart" => (200, "{\"data\":{\"updateCustomerForCart\":{\"id\":\"sc-cart-1\"}}}"),
                    "UpdateShippingAddress" => (200, "{\"data\":{\"updateShippingAddress\":{\"id\":\"sc-cart-1\"}}}"),
                    _ => (404, "{}"),
                };
            }

            if (path == "/api/checkout/v1/orders/ord-sc-1/finalize")
            {
                gqlOps.Add("CreditCard");
                return (200, "{\"data\":{\"creditCard\":{\"orderNo\":\"SC-999\",\"status\":\"CONFIRMED\"}}}");
            }

            if (path == "/api/search")
            {
                sawSearch = true;
                return (200, "{\"results\":[]}");
            }

            return (404, "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/p/p-sc-1",
            ProfileData = SampleProfile(),
            Card = SampleCard(),
        };
        ctx.Session.VariantId = "var-sc-1";
        ctx.Session.Vars["scheels.apiHub"] = "true";
        ctx.Session.Vars["scheels.hubOrigin"] = server.BaseUrl;
        ctx.Session.Vars["scheels.hubOrderId"] = "ord-sc-1";

        var flow = new ScheelsFlow();
        Assert.True((await flow.VerifySessionAsync(ctx, default)).Ok);
        Assert.True((await flow.FindProductAsync(ctx, default)).Ok);
        Assert.True((await flow.CreateCartAsync(ctx, default)).Ok);
        Assert.True((await flow.AddToCartAsync(ctx, default)).Ok);
        Assert.True((await flow.GetCheckoutAsync(ctx, default)).Ok);
        Assert.True((await flow.SubmitEmailAsync(ctx, default)).Ok);
        Assert.True((await flow.SubmitShippingAsync(ctx, default)).Ok);
        Assert.True((await flow.SubmitOrderAsync(ctx, default)).Ok);

        Assert.Equal("SC-999", ctx.Session.OrderNumber);
        Assert.Equal(new[]
        {
            "getSession", "Product", "CreateInitialCart", "AddItemToCart",
            "CheckoutCart", "UpdateCustomerForCart", "UpdateShippingAddress", "CreditCard",
        }, gqlOps.ToArray());
        Assert.False(sawSearch);
    }

    [Fact]
    public async Task ShopifyStorefrontDropsShopAppPaypalDetailsAndOnRunningWorkEndToEnd()
    {
        var seen = new List<string>();
        var paypalPollCount = 0;

        using var server = new TinyServer((req, body) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            var target = req.RawUrl ?? "/";
            seen.Add(path + " | " + target);

            if (path == "/shopapp/graphql")
            {
                var op = JObject.Parse(body)["operationName"]?.ToString();
                if (op == "SignInAsGuest")
                    return (200, "{\"data\":{\"signInAsGuest\":{\"authPayload\":{\"accessToken\":\"sa_at\",\"refreshToken\":\"sa_rt\"}}}}");
                if (op == "ShopProductSearch")
                    return (200, "{\"data\":{\"shopProductSearch\":{\"nodes\":[{\"id\":\"gid://shop/Product/1\",\"defaultVariantId\":\"gid://shop/ProductVariant/2\",\"shop\":{\"id\":\"broker-1\"}}]}}}");
            }

            if (path == "/apps/product-drops")
                return (200, "{\"data\":{\"createCheckout\":{\"id\":\"pd-1\",\"checkoutUrl\":\"" + req.Url!.GetLeftPart(UriPartial.Authority) + "/checkouts/cn/pdtoken1234567890123456\"}}}");

            if (path == "/checkouts/internal/graphql/persisted")
            {
                var parsed = JObject.Parse(body);
                paypalPollCount++;
                if (parsed["operationName"]?.ToString() == "PaypalDetails" && paypalPollCount == 1)
                    return (200, "{\"data\":{\"paypalDetails\":{\"__typename\":\"PendingTask\",\"taskId\":\"pt-1\"}}}");
                return (200, "{\"data\":{\"paypalDetails\":{\"__typename\":\"PaypalDetailsFetchSuccess\"}}}");
            }

            if (path == "/ko-kr/graphql")
                return (200, "{\"data\":{\"checkoutAsGuest\":{\"order\":{\"errors\":[]}}}}");

            return (200, "<html></html>");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var shopify = new ShopifyFlow();

        // 1) ShopApp SignInAsGuest + ShopProductSearch variable derivation
        var saCtx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        saCtx.Session.Vars["shopapp.url"] = server.BaseUrl + "/shopapp/graphql";
        saCtx.Session.Vars["shopapp.guestMedium"] = "EMAIL";
        saCtx.Session.Vars["shopapp.searchKey"] = "tee";
        saCtx.Session.Vars["shopapp.brokerId"] = "broker-1";
        Assert.True((await shopify.LoginAsync(saCtx, default)).Ok);
        Assert.Equal("sa_at", saCtx.Session.Vars["shopapp.accessToken"]);
        Assert.True((await shopify.FindProductAsync(saCtx, default)).Ok);
        Assert.Equal("gid://shop/Product/1", saCtx.Session.Vars["shopapp.productId"]);

        // 2) ShopifyProductDrops CreateCheckoutAsync
        var dropsCtx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/drop-item" };
        dropsCtx.Session.VariantId = "gid://shop/ProductVariant/99";
        dropsCtx.Session.Vars["productdrops.origin"] = server.BaseUrl;
        dropsCtx.Session.Vars["shopify.useDropsCheckout"] = "true";
        Assert.True((await shopify.InitiateCheckoutAsync(dropsCtx, default)).Ok);
        Assert.Equal("pdtoken1234567890123456", dropsCtx.Session.CheckoutToken);

        // 3) Persisted PaypalDetails + PendingTask poll
        var ppCtx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ppCtx.Session.Vars["paypal.partnerToken"] = "EC-TEST-9";
        ppCtx.Session.Vars["shopify.pollMs"] = "0";
        Assert.True((await shopify.FetchPayPalDetailsAsync(ppCtx, default)).Ok);
        Assert.Contains("PaypalDetailsFetchSuccess", ppCtx.Session.Vars["paypalDetails"]);
        Assert.Equal(2, paypalPollCount);

        // 4) Verified On Running router constant + Storefront customerAccessTokenCreate / createCart URI shapes
        Assert.Equal("/?graphql_router=0xdjmg_aa6", ShopifyFlow.OnRunningRouterQuery);
        Assert.Equal("https://www.on.com", ShopifyFlow.OnRunningOrigin);
        Assert.Equal("https://shop.test/api/2025-04/graphql.json",
            ShopifyGraphQl.Endpoint("shop.test", ShopifyStorefrontQueries.ApiVersion));
        Assert.Equal("https://shop.test/api/2021-10/graphql.json",
            ShopifyGraphQl.Endpoint("shop.test", ShopifyStorefrontQueries.CartCreateApiVersion));
    }

    [Fact]
    public async Task PaniniEightStepOnepaniniAndPpcpRestCheckoutRunEndToEnd()
    {
        var opsSeen = new List<string>();
        var btToken = Convert.ToBase64String(Encoding.UTF8.GetBytes("{\"authorizationFingerprint\":\"auth_fp_panini\"}"));

        using var server = new TinyServer((req, body) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == "/onepanini")
            {
                if (body.Contains("query item", StringComparison.Ordinal))
                {
                    opsSeen.Add("item");
                    return (200, "{\"data\":{\"item\":{\"sku\":\"PAN-SKU-1\",\"name\":\"Prizm Box\",\"price\":\"299\"}}}");
                }
                if (body.Contains("addToCart(", StringComparison.Ordinal))
                {
                    opsSeen.Add("addToCart");
                    return (200, "{\"data\":{\"addToCart\":{\"cart_id\":\"pan-cart-1\",\"status\":true}}}");
                }
                if (body.Contains("buynow(", StringComparison.Ordinal))
                {
                    opsSeen.Add("buynow");
                    return (200, "{\"data\":{\"buynow\":{\"cart_id\":\"pan-cart-1\",\"session_id\":\"ps-1\"}}}");
                }
                if (body.Contains("getShippingMethods", StringComparison.Ordinal))
                {
                    opsSeen.Add("getShippingMethods");
                    return (200, "{\"data\":{\"getShippingMethods\":[{\"carrier_code\":\"fedex\",\"method_code\":\"2day\"}]}}");
                }
                if (body.Contains("getPaymentdMethods", StringComparison.Ordinal))
                {
                    opsSeen.Add("getPaymentdMethods");
                    return (200, "{\"data\":{\"getPaymentdMethods\":[{\"code\":\"braintree\"}]}}");
                }
                if (body.Contains("generateClientToken", StringComparison.Ordinal))
                {
                    opsSeen.Add("generateClientToken");
                    return (200, "{\"data\":{\"generateClientToken\":{\"data\":{\"clientToken\":\"" + btToken + "\"}}}}");
                }
                if (body.Contains("placeOrderWithPaypal", StringComparison.Ordinal))
                {
                    opsSeen.Add("placeOrderWithPaypal");
                    return (200, "{\"data\":{\"placeOrderWithPaypal\":{\"status\":\"true\",\"data\":{\"orderNumber\":\"PAN-ORD-1\"}}}}");
                }
            }

            if (path == "/braintree/graphql")
            {
                opsSeen.Add("TokenizeCreditCard");
                return (200, "{\"data\":{\"tokenizeCreditCard\":{\"token\":\"nonce-pan-1\"}}}");
            }

            if (path == "/rest/V1/ppcp/createGuestOrder")
            {
                opsSeen.Add("ppcp:guest");
                return (200, "{\"orderId\":\"PPCP-GUEST-1\"}");
            }

            if (path == "/rest/V1/ppcp/createOrder")
            {
                opsSeen.Add("ppcp:auth");
                return (200, "{\"orderId\":\"PPCP-AUTH-1\"}");
            }

            return (404, "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/product/prizm",
            ProfileData = SampleProfile(),
            Card = SampleCard(),
        };
        ctx.Session.Vars["magento.mode"] = "panini";
        ctx.Session.Vars["panini.endpoint"] = server.BaseUrl + "/onepanini";
        ctx.Session.Vars["panini.braintreeUrl"] = server.BaseUrl + "/braintree/graphql";

        var flow = new MagentoFlow("panini", "Panini", new[] { "paniniamerica.net" });
        Assert.True((await flow.FindProductAsync(ctx, default)).Ok);
        Assert.True((await flow.AddToCartAsync(ctx, default)).Ok);
        Assert.True((await flow.GetShippingRatesAsync(ctx, default)).Ok);
        Assert.True((await flow.GetPaymentPageAsync(ctx, default)).Ok);
        Assert.True((await flow.GetPaymentTokenAsync(ctx, default)).Ok);
        Assert.True((await flow.SubmitOrderAsync(ctx, default)).Ok);

        Assert.Equal("auth_fp_panini", ctx.Session.Vars["braintree.fingerprint"]);
        Assert.Equal("nonce-pan-1", ctx.Session.PaymentToken);
        Assert.Equal("PAN-ORD-1", ctx.Session.OrderNumber);

        // Verify PPCP createGuestOrder + createOrder
        ctx.Session.Vars["panini.ppcpBase"] = server.BaseUrl;
        Assert.True((await flow.SubmitPpcpOrderAsync(ctx, default)).Ok);
        Assert.Equal("PPCP-GUEST-1", ctx.Session.OrderNumber);
        ctx.Session.Vars["panini.authenticated"] = "true";
        Assert.True((await flow.SubmitPpcpOrderAsync(ctx, default)).Ok);
        Assert.Equal("PPCP-AUTH-1", ctx.Session.OrderNumber);

        Assert.Equal(new[]
        {
            "item", "addToCart", "getShippingMethods", "getPaymentdMethods",
            "generateClientToken", "TokenizeCreditCard", "placeOrderWithPaypal",
            "ppcp:guest", "ppcp:auth",
        }, opsSeen.ToArray());
    }

    [Fact]
    public async Task AsyncTailNikePopMartSauconyJohnLewisVansAndHttpParityHold()
    {
        var seen = new List<(string Method, string Path, string Body)>();
        using var server = new TinyServer((req, body) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            seen.Add((req.HttpMethod, path, body));

            if (path == "/nike/paypal_details")
                return (200, "{\"id\":\"job-pp-1\"}");
            if (path == "/nike/paypal_details/jobs/job-pp-1")
                return (200, "{\"status\":\"COMPLETED\",\"paypalToken\":\"EC-N1\"}");
            if (path == "/nike/deferred_forms")
                return (200, "{\"id\":\"job-df-1\"}");
            if (path == "/nike/deferred_forms/jobs/job-df-1")
                return (200, "{\"formUrl\":\"https://klarna.test/redirect\"}");
            if (path == "/store/v1/store/cart/listByStore")
                return (200, "{\"code\":\"OK\",\"data\":[]}");
            if (path.StartsWith("/rpc/payment/pay/", StringComparison.Ordinal))
                return (200, "{\"success\":true}");
            if (path.StartsWith("/api/cart/v2/checkout/order/", StringComparison.Ordinal))
                return (200, "{\"orderNumber\":\"VANS-3DS-1\",\"orderId\":\"v-oid-1\",\"isFinal\":true}");
            if (path.EndsWith("/CheckoutHelper-PlaceOrder", StringComparison.Ordinal))
            {
                if (body.Contains("isPayerValidationCall=true", StringComparison.Ordinal))
                    return (200, "{\"redirectUrl\":\"https://acs.saucony.test/step\"}");
                return (200, "{\"error\":false,\"orderNumber\":\"SAU-100\"}");
            }

            return (200, "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };

        // 1) Nike PayPalDetails + DeferredPaymentForms
        var nikeCtx = new FlowContext { Http = http, Url = "https://www.nike.com/us/launch/t/shoe" };
        nikeCtx.Session.Vars["nike.paypalDetailsUrl"] = server.BaseUrl + "/nike/paypal_details";
        nikeCtx.Session.Vars["nike.paypalDetailsJobsUrl"] = server.BaseUrl + "/nike/paypal_details/jobs/";
        nikeCtx.Session.Vars["nike.deferredPaymentFormsUrl"] = server.BaseUrl + "/nike/deferred_forms";
        nikeCtx.Session.Vars["nike.deferredPaymentFormsJobsUrl"] = server.BaseUrl + "/nike/deferred_forms/jobs/";
        var nike = new NikeFlow();
        Assert.True((await nike.FetchPayPalDetailsAsync(nikeCtx, "EC-N1", default)).Ok);
        Assert.True((await nike.CreateDeferredPaymentFormAsync(nikeCtx, "ORD-N1", "APP-1", default)).Ok);
        Assert.Contains("COMPLETED", nikeCtx.Session.Vars["nike.paypalDetails"]);
        Assert.Contains("klarna.test", nikeCtx.Session.Vars["nike.deferredForm"]);

        // 2) PopMart Store list + RPC PayPal + Adyen details
        var pmCtx = new FlowContext { Http = http, Url = server.BaseUrl + "/product/labubu" };
        var popMart = new PopMartFlow();
        Assert.True((await popMart.GetCartListByStoreAsync(pmCtx, "gid-1", "st-1", default)).Ok);
        Assert.True((await popMart.RpcInitiatePayPalAsync(pmCtx, new JObject { ["orderNumber"] = "PM-1", ["payChannel"] = "paypal" }, default)).Ok);
        Assert.True((await popMart.RpcCapturePayPalAsync(pmCtx, "CH-9", default)).Ok);
        Assert.True((await popMart.RpcSubmitAdyenDetailsAsync(pmCtx, "MO-1", "{\"transStatus\":\"Y\"}", default)).Ok);
        Assert.False((await popMart.RpcSubmitAdyenDetailsAsync(pmCtx, "MO-1", "{\"transStatus\":\"N\"}", default)).Ok);

        // 3) Vans CompleteVansOrder3dsAsync (mutating PUT verb + transStatus check)
        var vansCtx = new FlowContext { Http = http, Url = server.BaseUrl + "/en_us/cart" };
        Assert.True((await popMart.CompleteVansOrder3dsAsync(
            vansCtx, "ord-v1", "en_us", "{\"transStatus\":\"Y\"}", "auth-v1", "pi-v1", "sess-v1", "VISA", default)).Ok);
        Assert.Equal("VANS-3DS-1", vansCtx.Session.OrderNumber);
        Assert.Contains(seen, r => r.Method == "PUT" && r.Path == "/api/cart/v2/checkout/order/ord-v1");

        // 4) Saucony PayerAuthenticateAsync writes saucony.threeDsReply
        var sauCtx = new FlowContext { Http = http, Url = server.BaseUrl + "/en_us/checkout" };
        var sau = new SauconyFlow();
        Assert.True((await sau.PayerAuthenticateAsync(sauCtx, default)).Ok);
        Assert.Contains("acs.saucony.test", sauCtx.Session.Vars["saucony.threeDsReply"]);

        // 5) Cybersole.Http ContentEncodingCodec (zstd + gzip roundtrip)
        var rawBytes = Encoding.UTF8.GetBytes("{\"parity\":\"ok\"}");
        using (var comp = new ZstdSharp.Compressor())
        {
            var zstdBytes = comp.Wrap(rawBytes).ToArray();
            var decoded = Cybersole.Http.Compression.ContentEncodingCodec.Decompress(zstdBytes, "zstd");
            Assert.Equal("{\"parity\":\"ok\"}", Encoding.UTF8.GetString(decoded));
        }

        // 6) JohnLewis BFF PUT ?methodId=...&setupFutureUsage=false + PlaceOrder DECLINED guard
        using var jlServer = new TinyServer((req, _) =>
        {
            var p = req.Url?.AbsolutePath ?? "/";
            if (p == "/bff/v2/orderforms/payments")
                return (200, "{\"next_action\":{}}");
            if (p == "/bff/v2/orders/ok")
                return (200, "{\"orderNo\":\"JL-77\"}");
            return (200, "{\"status\":\"DECLINED\"}");
        });
        var jl = new JohnLewisFlow();
        var jlCtx = new FlowContext { Http = http, Url = "https://www.johnlewis.com/p/1" };
        jlCtx.Session.Vars["jl.paymentsUrl"] = jlServer.BaseUrl + "/bff/v2/orderforms/payments";
        jlCtx.Session.Vars["jl.methodId"] = "pm-jl-1";
        jlCtx.Session.Vars["jl.ordersUrl"] = jlServer.BaseUrl + "/bff/v2/orders/ok";
        Assert.True((await jl.SubmitOrderStripeAsync(jlCtx, default)).Ok);
        Assert.True((await jl.PlaceOrderAsync(jlCtx, default)).Ok);
        Assert.Equal("JL-77", jlCtx.Session.OrderNumber);
        jlCtx.Session.Vars["jl.ordersUrl"] = jlServer.BaseUrl + "/bff/v2/orders/declined";
        Assert.False((await jl.PlaceOrderAsync(jlCtx, default)).Ok);

        // 7) RequestOptions.OverrideHeaders + Properties isolation
        var opts = new RequestOptions
        {
            OverrideHeaders = true,
            Headers = { ["x-only-this"] = "yes" },
        };
        opts.Properties["Akamai"] = "1";
        var cloned = opts.Clone();
        Assert.True(cloned.OverrideHeaders);
        Assert.Equal("1", cloned.Properties["Akamai"]);
    }
}
