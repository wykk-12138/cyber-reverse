using System.Net;
using System.Text;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

public sealed class Phase2StoreStepsTests
{
    private sealed class LoopbackServer : IDisposable
    {
        private readonly HttpListener _listener = new();
        public string BaseUrl { get; }
        public List<(string Method, string PathAndQuery, Dictionary<string, string> Headers, byte[] RawBody, string BodyText)> Requests { get; } = new();

        public LoopbackServer(Func<HttpListenerRequest, byte[], (int Status, string ContentType, string Body)> handler)
        {
            var port = FreePort();
            BaseUrl = $"http://127.0.0.1:{port}";
            _listener.Prefixes.Add(BaseUrl + "/");
            _listener.Start();

            _ = Task.Run(async () =>
            {
                while (_listener.IsListening)
                {
                    HttpListenerContext ctx;
                    try { ctx = await _listener.GetContextAsync().ConfigureAwait(false); }
                    catch { return; }

                    using var ms = new MemoryStream();
                    await ctx.Request.InputStream.CopyToAsync(ms).ConfigureAwait(false);
                    var raw = ms.ToArray();
                    var text = Encoding.UTF8.GetString(raw);

                    var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
                    foreach (string? k in ctx.Request.Headers.AllKeys)
                    {
                        if (k is not null) headers[k] = ctx.Request.Headers[k] ?? string.Empty;
                    }

                    Requests.Add((ctx.Request.HttpMethod, ctx.Request.Url?.PathAndQuery ?? "/", headers, raw, text));

                    var (status, ct, respBody) = handler(ctx.Request, raw);
                    ctx.Response.StatusCode = status;
                    ctx.Response.ContentType = ct;
                    var bytes = Encoding.UTF8.GetBytes(respBody);
                    await ctx.Response.OutputStream.WriteAsync(bytes).ConfigureAwait(false);
                    ctx.Response.Close();
                }
            });
        }

        private static int FreePort()
        {
            var l = new System.Net.Sockets.TcpListener(IPAddress.Loopback, 0);
            l.Start();
            var port = ((IPEndPoint)l.LocalEndpoint).Port;
            l.Stop();
            return port;
        }

        public void Dispose()
        {
            try { _listener.Stop(); } catch { }
            _listener.Close();
        }
    }

    [Fact]
    public async Task CheckPriceLimitAppQueriesGraphQlWithMobileSdkHeadersAndChecksBounds()
    {
        using var server = new LoopbackServer((req, _) =>
        {
            if (req.Url?.AbsolutePath == "/api/2020-04/graphql.json")
            {
                return (200, "application/json", """
                    {
                      "data": {
                        "product": {
                          "variants": {
                            "edges": [
                              { "node": { "id": "gid://shopify/ProductVariant/111", "priceV2": { "amount": "220.00", "currencyCode": "USD" } } },
                              { "node": { "id": "gid://shopify/ProductVariant/222", "priceV2": { "amount": "150.00", "currencyCode": "USD" } } }
                            ]
                          }
                        }
                      }
                    }
                    """);
            }
            return (404, "application/json", "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var shopify = new ShopifyFlow();

        // Pre-flight rejects /cart/ URL
        var cartCtx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/cart/",
            Product = new Product { PriceCheck = true, Price = "160.00" },
        };
        var cartRes = await shopify.CheckPriceLimitAsync(cartCtx, default);
        Assert.False(cartRes.Ok);
        Assert.Equal("Price limit requires keyword or URL input", cartRes.Error);

        // App mode passes when variant 222 (150.00) <= 160.00
        var okCtx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/products/air-jordan",
            Product = new Product { Name = "air-jordan", PriceCheck = true, Price = "160.00" },
        };
        okCtx.Session.VariantId = "222";
        okCtx.Session.Vars["shopify.mode"] = "app";
        okCtx.Session.Vars["shopify.appContext"] = "US";
        okCtx.Session.Vars[ShopifyFlow.GraphQlTokenVar] = "sf_tok_9";

        var okRes = await shopify.CheckPriceLimitAsync(okCtx, default);
        Assert.True(okRes.Ok, okRes.Error);
        Assert.Equal("150.00", okCtx.Session.Vars["price"]);

        var gqlReq = Assert.Single(server.Requests);
        Assert.Equal("/api/2020-04/graphql.json", gqlReq.PathAndQuery);
        Assert.Contains("application/graphql", gqlReq.Headers["Content-Type"]);
        Assert.Equal("sf_tok_9", gqlReq.Headers[ShopifyHeaders.StorefrontAccessToken]);
        Assert.Equal("ios", gqlReq.Headers["X-SDK-Variant"]);
        Assert.Equal("3.7.1", gqlReq.Headers["X-SDK-Version"]);
        Assert.Equal("Mobile Buy SDK iOS/3.7.1/com.tapcart.hoyJaSjQM2", gqlReq.Headers["User-Agent"]);
        Assert.Contains("@inContext(country: US)", gqlReq.BodyText);

        // Exceeds limit when variant 111 (220.00) > 160.00
        okCtx.Session.VariantId = "111";
        var failRes = await shopify.CheckPriceLimitAsync(okCtx, default);
        Assert.False(failRes.Ok);
        Assert.Equal("Price exceeded", failRes.Error);
    }

    [Fact]
    public async Task FindProductCdnFetchesLowercaseFirstTokenAndHandles404Retry()
    {
        using var server = new LoopbackServer((req, _) =>
        {
            if (req.Url?.AbsolutePath == "/variants/topps-chrome2026.json")
                return (200, "application/json", """{"title":"Topps Chrome 2026","opaque":"payload"}""");
            if (req.Url?.AbsolutePath == "/variants/topps-missing.json")
                return (404, "application/json", "{}");
            return (404, "application/json", "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var shopify = new ShopifyFlow();

        var ctx = new FlowContext
        {
            Http = http,
            Url = "https://topps-uk.myshopify.com/products/chrome",
            Product = new Product { Name = "Chrome2026 Hobby Box" },
        };
        ctx.Session.Vars["topps.cdnOrigin"] = server.BaseUrl;

        var ok = await shopify.FindProductFlowAsync(ctx, default);
        Assert.True(ok.Ok, ok.Error);
        Assert.Equal("unknown", ctx.Session.Vars["topps.schema"]);
        Assert.Contains(server.Requests, r => r.PathAndQuery == "/variants/topps-chrome2026.json");

        ctx.Session.Vars["topps.input"] = "MISSING Token";
        var miss = await shopify.FindProductFlowAsync(ctx, default);
        Assert.False(miss.Ok);
        Assert.True(miss.Retryable);
    }

    [Fact]
    public async Task FunkoFanRewardStateBalanceAndSignupMatchRecoveredContracts()
    {
        using var server = new LoopbackServer((req, _) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == "/account")
                return (200, "text/html", """<div class="crowd-twist-points"><span class="points-value"> 1,250 </span></div>""");
            if (path == "/no-rewards/account")
                return (200, "text/html", "<html><div>regular account</div></html>");
            if (path == "/on/demandware.store/Sites-FunkoUS-Site/en_US/CrowdTwist-Register" && req.HttpMethod == "POST")
                return (200, "application/json", """{"success":true}""");
            return (404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var funko = new FunkoFlow();

        // 1. Check state (already signed up) & check balance
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/home" };
        ctx.Session.Vars["funko.mode"] = "fan rewards state";
        Assert.True((await funko.CheckLoginAsync(ctx, default)).Ok);
        Assert.Equal("already_signed_up", ctx.Session.Vars["fanRewards.state"]);

        ctx.Session.Vars["funko.mode"] = "check balance";
        Assert.True((await funko.CheckLoginAsync(ctx, default)).Ok);
        Assert.Equal("1,250 pts", ctx.Session.Vars["fanRewards.balance"]);

        // 2. Not signed up -> SignUpAsync calls CrowdTwist-Register
        var signCtx = new FlowContext { Http = http, Url = server.BaseUrl + "/home" };
        signCtx.Session.Vars["funko.accountPrefix"] = "no-rewards";
        var signRes = await funko.SignUpAsync(signCtx, default);
        Assert.True(signRes.Ok, signRes.Error);
        Assert.Equal("registered", signCtx.Session.Vars["fanRewards.signup"]);

        var regReq = Assert.Single(server.Requests,
            r => r.PathAndQuery == "/on/demandware.store/Sites-FunkoUS-Site/en_US/CrowdTwist-Register");
        Assert.Equal("POST", regReq.Method);
        Assert.Equal(server.BaseUrl + "/fanrewards-join/", regReq.Headers["Referer"]);
        Assert.Equal(server.BaseUrl, regReq.Headers["Origin"]);
        Assert.Equal("XMLHttpRequest", regReq.Headers["X-Requested-With"]);
        Assert.Empty(regReq.RawBody);
    }

    [Fact]
    public async Task ConvenienceStoreHandlesKomojuJsonAndWebCvsShiftJis()
    {
        Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);

        using var server = new LoopbackServer((req, _) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == "/komoju-pay")
                return (200, "text/html", """<html><head><meta name="csrf-token" content="csrf-k-1"></head><body><form action="/komoju-submit"></form></body></html>""");
            if (path == "/komoju-submit" && req.HttpMethod == "POST")
                return (200, "application/json", """{"ok":true}""");
            if (path == "/webcvs-entry")
                return (200, "text/html", """<form name="webcvsFepChargePaymentInfoEntryActionForm" action="/webcvs-post"><input type="hidden" name="org.apache.struts.taglib.html.TOKEN" value="struts-99"/></form>""");
            if (path == "/webcvs-post" && req.HttpMethod == "POST")
                return (200, "text/html", "<html>ok</html>");
            return (404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var shopify = new ShopifyFlow();

        // Komoju flow
        var komojuCtx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl,
            ProfileData = new Profile { Email = "buyer@example.jp", FirstName = "Taro" },
        };
        komojuCtx.Session.Vars["convenienceStore"] = "Family Mart";
        komojuCtx.Session.Vars["shopify.offsiteKind"] = "komoju";
        komojuCtx.Session.Vars["offsiteUrl"] = server.BaseUrl + "/komoju-pay";

        var kRes = await shopify.SubmitPaymentAsync(komojuCtx, default);
        Assert.True(kRes.Ok, kRes.Error);
        var kPost = Assert.Single(server.Requests, r => r.PathAndQuery == "/komoju-submit");
        Assert.Equal("https://komoju.com", kPost.Headers["Origin"]);
        Assert.Equal("https://komoju.com", kPost.Headers["Referer"]);
        var kJson = Newtonsoft.Json.Linq.JObject.Parse(kPost.BodyText);
        Assert.Equal("csrf-k-1", kJson["authenticity_token"]?.ToString());
        Assert.Equal("konbini", kJson["payment_details"]?["type"]?.ToString());
        Assert.Equal("family-mart", kJson["payment_details"]?["store"]?.ToString());
        Assert.Equal("Taro", kJson["payment_details"]?["given_name"]?.ToString());

        // WebCVS shift_jis flow
        var webCvsCtx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl,
            ProfileData = new Profile { Email = "buyer@example.jp", FirstName = "太郎", LastName = "山田", Phone = "09012345678" },
        };
        webCvsCtx.Session.Vars["convenienceStore"] = "Ministop";
        webCvsCtx.Session.Vars["offsiteUrl"] = server.BaseUrl + "/webcvs-entry";

        var wRes = await shopify.SubmitPaymentAsync(webCvsCtx, default);
        Assert.True(wRes.Ok, wRes.Error);
        var wPost = Assert.Single(server.Requests, r => r.PathAndQuery == "/webcvs-post");
        var decodedBody = Encoding.GetEncoding("shift_jis").GetString(wPost.RawBody);
        Assert.Contains("org.apache.struts.taglib.html.TOKEN=struts-99", decodedBody);
        Assert.Contains("webCvsType=005", decodedBody);
        Assert.Contains("webCvsType1=999", decodedBody);
        Assert.Contains("webCvsType2=005", decodedBody);
        Assert.Contains("zipCode1=000", decodedBody);
        Assert.Contains("zipCode2=0000", decodedBody);
        // Verify shift_jis URL-encoded bytes for 山田 (%8ER%93c)
        Assert.Contains("lastName=%8ER%93c", decodedBody, StringComparison.OrdinalIgnoreCase);
    }
}
