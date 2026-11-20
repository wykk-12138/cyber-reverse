using System.Net;
using System.Text;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

public sealed class UnzerThreeDsTests
{
    private sealed class LoopbackServer : IDisposable
    {
        private readonly HttpListener _listener = new();
        public string BaseUrl { get; }
        public List<(string Method, string PathAndQuery, Dictionary<string, string> Headers, string Body)> Requests { get; } = new();

        public LoopbackServer(Func<HttpListenerRequest, string, (int Status, string ContentType, Dictionary<string, string>? Headers, string Body)> handler)
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

                    string body;
                    using (var reader = new StreamReader(ctx.Request.InputStream, Encoding.UTF8))
                        body = await reader.ReadToEndAsync().ConfigureAwait(false);

                    var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
                    foreach (string? k in ctx.Request.Headers.AllKeys)
                    {
                        if (k is not null) headers[k] = ctx.Request.Headers[k] ?? string.Empty;
                    }

                    Requests.Add((ctx.Request.HttpMethod, ctx.Request.Url?.PathAndQuery ?? "/", headers, body));

                    var (status, contentType, respHeaders, respBody) = handler(ctx.Request, body);
                    ctx.Response.StatusCode = status;
                    ctx.Response.ContentType = contentType;
                    if (respHeaders is not null)
                    {
                        foreach (var kv in respHeaders)
                        {
                            if (string.Equals(kv.Key, "Location", StringComparison.OrdinalIgnoreCase))
                                ctx.Response.RedirectLocation = kv.Value;
                            else
                                ctx.Response.Headers[kv.Key] = kv.Value;
                        }
                    }

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

    private static FlowContext Context(NetClient http, string baseUrl) => new()
    {
        Http = http,
        Url = baseUrl + "/us/watch",
        Card = new Card { Number = "4111 1111 1111 1111", Cvv = "737", Month = "4", Year = "2030", Name = "Ada Lovelace" },
        ProfileData = new Profile
        {
            Email = "ada@example.com",
            FirstName = "Ada",
            LastName = "Lovelace",
            Phone = "+15550100",
            Address1 = "1 Analytical Way",
            City = "London",
            State = "LDN",
            Zip = "E1 6AN",
            Country = "GB",
        },
        Billing = new Address
        {
            FirstName = "Ada",
            LastName = "Lovelace",
            Address1 = "1 Analytical Way",
            Address2 = "Suite 2",
            City = "London",
            State = "LDN",
            ZipCode = "E1 6AN",
            Country = "GB",
        },
    };

    [Fact]
    public async Task TokenizeSendsRecoveredBasicAuthSdkHeadersAndStrippedCard()
    {
        using var server = new LoopbackServer((req, body) =>
        {
            if (req.Url?.AbsolutePath == "/v1/types/card")
                return (201, "application/json", null, """{"id":"s-crd-123"}""");
            return (404, "application/json", null, "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server.BaseUrl);
        ctx.Session.Vars["unzer.apiUrl"] = server.BaseUrl;
        ctx.Session.Vars["unzer.publicKey"] = "s-pub-testkey";

        var gw = new UnzerGateway();
        var res = await gw.TokenizeAsync(ctx, default);

        Assert.True(res.Ok, res.Error);
        Assert.Equal("s-crd-123", res.GatewayReference);
        Assert.Equal("s-crd-123", ctx.Session.Vars["unzer.resourceId"]);

        var req = Assert.Single(server.Requests);
        Assert.Equal("POST", req.Method);
        Assert.Equal("/v1/types/card", req.PathAndQuery);
        Assert.Equal("Basic " + Convert.ToBase64String(Encoding.UTF8.GetBytes("s-pub-testkey:")), req.Headers["Authorization"]);
        Assert.Equal(UnzerGateway.StaticOrigin, req.Headers["Origin"]);
        Assert.Equal("de-DE", req.Headers["Accept-Language"]);
        Assert.Equal(UnzerGateway.SdkTypeHeader, req.Headers["sdk-type"]);
        Assert.Equal(UnzerGateway.SdkVersionHeader, req.Headers["sdk-version"]);
        // NetClient.BuildRequest (owned outside Cybersole.Stores) pre-adds sec-fetch-site: none via TryAddWithoutValidation
        // before applying options.Headers, so the wire header contains either "same-site" or "none, same-site".
        Assert.Contains("same-site", req.Headers["sec-fetch-site"]
            .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries));

        var json = JObject.Parse(req.Body);
        Assert.Equal("4111111111111111", json["number"]?.ToString());
        Assert.Equal("04/30", json["expiryDate"]?.ToString());
        Assert.Equal("737", json["cvc"]?.ToString());
        Assert.Equal("Ada Lovelace", json["cardHolder"]?.ToString());
    }

    [Fact]
    public async Task TokenizeReportsInvalidCardOn400AndMissingPublicKey()
    {
        using var server = new LoopbackServer((_, _) => (400, "application/json", null, """{"errors":[{"message":"bad card"}]}"""));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var gw = new UnzerGateway();

        var missingCtx = Context(http, server.BaseUrl);
        var missingRes = await gw.TokenizeAsync(missingCtx, default);
        Assert.False(missingRes.Ok);
        Assert.Equal("Missing Unzer public key", missingRes.Error);

        var badCtx = Context(http, server.BaseUrl);
        badCtx.Session.Vars["unzer.apiUrl"] = server.BaseUrl;
        badCtx.Session.Vars["unzer.publicKey"] = "s-pub-test";
        var badRes = await gw.TokenizeAsync(badCtx, default);
        Assert.False(badRes.Ok);
        Assert.Equal("Invalid card", badRes.Error);
    }

    [Fact]
    public async Task ContinueUnzerThreeDsDrivesFormExtractionMethodNotifyContinueRewriteAndSuccessLanding()
    {
        using var server = new LoopbackServer((req, body) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == "/us/unzer/payment/redirect")
            {
                return (200, "text/html", null, """
                    <html><body>
                      <form action="/unzer-3ds-iframe" method="GET">
                        <input type="hidden" name="token" value="t1" />
                      </form>
                    </body></html>
                    """);
            }
            if (path == "/unzer-3ds-iframe")
            {
                return (200, "text/html", null, """
                    <html><body>
                      <div id="threeds-method-data"
                           data-notification-url="/3ds-notify"
                           data-continue-url="/unzer/continue/step"
                           data-server-trans-id="srv-tx-99"></div>
                    </body></html>
                    """);
            }
            if (path == "/3ds-notify" && req.HttpMethod == "POST")
                return (200, "application/json", null, """{"ok":true}""");

            if (path == "/unzer/receiver/step")
                return (302, "text/html", new Dictionary<string, string> { ["Location"] = "/us/checkout/onepage/success" }, "");

            if (path == "/us/checkout/onepage/success")
                return (200, "text/html", null, "<html>Order Complete</html>");

            return (404, "text/plain", null, "not found");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server.BaseUrl);
        ctx.Session.Vars["unzer.storeOrigin"] = server.BaseUrl;
        ctx.Session.Vars["unzer.storeCode"] = "us";
        ctx.Session.OrderId = "CASIO-1001";

        var gw = new UnzerGateway();
        var res = await gw.CompleteActionAsync(ctx, string.Empty, default);

        Assert.True(res.Ok, res.Error);
        Assert.Equal("Complete3DS", ctx.Session.Vars["unzer.state"]);
        Assert.Contains("/us/checkout/onepage/success", ctx.Session.Vars["unzer.landedUrl"]);

        Assert.Contains(server.Requests, r => r.PathAndQuery == "/us/unzer/payment/redirect" && r.Method == "GET");
        Assert.Contains(server.Requests, r => r.PathAndQuery == "/unzer-3ds-iframe" && r.Method == "GET");
        var notifyReq = Assert.Single(server.Requests, r => r.PathAndQuery == "/3ds-notify");
        Assert.Equal("POST", notifyReq.Method);
        Assert.Contains("threeDSMethodData=", notifyReq.Body);

        var encodedParam = Uri.UnescapeDataString(notifyReq.Body.Split('=')[1]);
        var padded = encodedParam.Replace('-', '+').Replace('_', '/');
        padded = padded.PadRight(padded.Length + (4 - padded.Length % 4) % 4, '=');
        var decodedJson = JObject.Parse(Encoding.UTF8.GetString(Convert.FromBase64String(padded)));
        Assert.Equal("srv-tx-99", decodedJson["threeDSServerTransID"]?.ToString());

        Assert.Contains(server.Requests, r => r.PathAndQuery == "/unzer/receiver/step");
        Assert.DoesNotContain(server.Requests, r => r.PathAndQuery == "/unzer/continue/step");
    }

    [Fact]
    public async Task ContinueUnzerThreeDsNoFormFallsBackToCallbackAndDetectsCartReturn()
    {
        using var server = new LoopbackServer((req, _) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == "/us/unzer/payment/redirect")
                return (200, "text/html", null, "<html><body>no form here</body></html>");
            if (path == "/us/unzer/payment/callback/")
                return (302, "text/html", new Dictionary<string, string> { ["Location"] = "/us/checkout/cart" }, "");
            if (path == "/us/checkout/cart")
                return (200, "text/html", null, "<html>Cart</html>");
            return (404, "text/plain", null, "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server.BaseUrl);
        ctx.Session.Vars["unzer.storeOrigin"] = server.BaseUrl;
        ctx.Session.Vars["unzer.storeCode"] = "us";

        var res = await new UnzerGateway().CompleteActionAsync(ctx, string.Empty, default);
        Assert.False(res.Ok);
        Assert.Contains("Unzer returned to cart:", res.Error);
        Assert.Contains(server.Requests, r => r.PathAndQuery == "/us/unzer/payment/callback/");
    }

    [Fact]
    public async Task CasioFlowDrivesTokenizeSetPaymentOrderSubmitAndProcess3dsViaStoreFlow()
    {
        using var server = new LoopbackServer((req, _) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == "/v1/types/card")
                return (201, "application/json", null, """{"id":"s-crd-casio"}""");
            if (path == "/us/rest/V1/guest-carts/cart-77/set-payment-information")
                return (200, "application/json", null, "true");
            if (path == "/us/rest/V1/guest-carts/cart-77/payment-information")
                return (200, "application/json", null, "\"ORD-7788\"");
            if (path == "/us/unzer/payment/redirect")
                return (302, "text/html", new Dictionary<string, string> { ["Location"] = "/us/checkout/success" }, "");
            if (path == "/us/checkout/success")
                return (200, "text/html", null, "<html>Thanks</html>");
            return (404, "application/json", null, "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server.BaseUrl);
        ctx.Session.CartId = "cart-77";
        ctx.Session.Vars["unzer.apiUrl"] = server.BaseUrl;
        ctx.Session.Vars["unzer.storeOrigin"] = server.BaseUrl;
        ctx.Session.Vars["unzer.storeCode"] = "us";
        ctx.Session.Vars["unzer.publicKey"] = "s-pub-casio";
        ctx.Session.Vars["unzer.policyAgreed"] = "true";

        var casio = new CasioFlow();
        Assert.True((await casio.SubmitPaymentAsync(ctx, default)).Ok);
        Assert.True((await casio.SubmitOrderAsync(ctx, default)).Ok);
        Assert.Equal("ORD-7788", ctx.Session.OrderId);
        Assert.Equal("requires_action", ctx.Session.Vars["paymentStatus"]);

        var viaStoreFlow = await casio.ProcessPaymentAsync(ctx, default);
        Assert.True(viaStoreFlow.Ok, viaStoreFlow.Error);
        Assert.Equal("Complete3DS", ctx.Session.Vars["unzer.state"]);

        var orderReq = Assert.Single(server.Requests, r => r.PathAndQuery == "/us/rest/V1/guest-carts/cart-77/payment-information");
        Assert.Equal("XMLHttpRequest", orderReq.Headers["x-requested-with"]);
        var orderJson = JObject.Parse(orderReq.Body);
        Assert.Equal("unzer_cards", orderJson["paymentMethod"]?["method"]?.ToString());
        Assert.Equal("s-crd-casio", orderJson["paymentMethod"]?["additional_data"]?["resource_id"]?.ToString());
        Assert.True(orderJson["paymentMethod"]?["extension_attributes"]?["is_policy_agreed"]?.Value<bool>() == true);
    }
}
