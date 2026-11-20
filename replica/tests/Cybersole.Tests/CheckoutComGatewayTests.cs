using System.Net;
using System.Text;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

public sealed class CheckoutComGatewayTests
{
    private sealed class LoopbackServer : IDisposable
    {
        private readonly HttpListener _listener = new();
        public string BaseUrl { get; }
        public List<(string Method, string PathAndQuery, Dictionary<string, string> Headers, string Body)> Requests { get; } = new();

        public LoopbackServer(Func<HttpListenerRequest, string, (int Status, string ContentType, string Body)> handler)
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

                    var (status, ct, respBody) = handler(ctx.Request, body);
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
    public void CheckoutComGatewayIsRegisteredInDefaultRegistry()
    {
        var gw = PaymentGatewayRegistry.Default.Resolve("checkoutcom");
        Assert.NotNull(gw);
        Assert.IsType<CheckoutComGateway>(gw);
    }

    [Fact]
    public async Task ShopifyOffsiteBootstrapTokenizeSubmitAnd3dsRunEndToEnd()
    {
        using var server = new LoopbackServer((req, _) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            var origin = $"http://127.0.0.1:{req.Url!.Port}";

            if (path == "/pay-offsite")
            {
                var pageCtx = new JObject
                {
                    ["pk"] = "pk_sbox_12345",
                    ["payment_session"] = new JObject { ["id"] = "ps_999" },
                }.ToString(Newtonsoft.Json.Formatting.None);
                var nextData = new JObject
                {
                    ["props"] = new JObject
                    {
                        ["pageProps"] = new JObject { ["paymentPageContextSerialized"] = pageCtx },
                    },
                }.ToString(Newtonsoft.Json.Formatting.None);
                return (200, "text/html", $"<html><script id=\"__NEXT_DATA__\" type=\"application/json\">{nextData}</script></html>");
            }
            if (path == "/tokens")
                return (201, "application/json", """{"token":"tok_cko_1"}""");
            if (path == "/payment-sessions/ps_999/submit")
                return (202, "application/json", new JObject
                {
                    ["status"] = "Action Required",
                    ["action"] = new JObject { ["url"] = $"{origin}/3ds/sess_1" },
                }.ToString());
            if (path == "/3ds/sess_1")
                return (200, "text/html", "<script>var x = { transactionId: 'tx_cko_42', ok: true };</script>");
            if (path == "/3ds/sess_1/device-information")
                return (200, "text/html", "<script>CKO3DS.challenge.get3ds2FullRedirectChallenge('{\"acsTransID\":\"a1\"}');</script>");
            if (path == "/sessions-interceptor/hosted-challenge-notification")
                return (200, "application/json", """{"ok":true}""");
            if (path == "/3ds/sess_1/processing")
                return (200, "application/json", """{"processing":true}""");
            if (path == "/3ds/sess_1/long-verify")
                return (200, "application/json", new JObject
                {
                    ["action"] = "Redirect",
                    ["redirect_to_url"] = $"{origin}/thank-you",
                }.ToString());
            if (path == "/thank-you")
                return (200, "text/html", $"<script>window.top.location.replace('{origin}/orders/confirmed');</script>");
            if (path == "/orders/confirmed")
                return (200, "text/html", "<html>Confirmed</html>");
            return (404, "application/json", "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = "https://shop.example/checkout",
            Card = new Card { Number = "4242 4242 4242 4242", Month = "12", Year = "2030", Cvv = "123", Name = "Ada Lovelace" },
        };
        ctx.Session.Vars["checkoutcom.apiHost"] = server.BaseUrl;
        ctx.Session.Vars["checkoutcom.authDevicesHost"] = server.BaseUrl;
        ctx.Session.Vars["checkoutcom.offsiteUrl"] = server.BaseUrl + "/pay-offsite";
        ctx.Session.Vars["checkoutcom.s"] = "s_tok_7";
        ctx.Session.Vars["checkoutcom.challengeForm"] = """{"cres":"cres-ok"}""";
        ctx.Session.Vars["shopify.autoContinue3ds"] = "true";

        var step = await new ShopifyFlow().SubmitPaymentAsync(ctx, default);
        Assert.True(step.Ok, step.Error);
        Assert.Equal($"{server.BaseUrl}/orders/confirmed", ctx.Session.Vars["checkoutcom.redirectUrl"]);
        Assert.False(string.IsNullOrEmpty(ctx.Session.Vars["checkoutcom.creq"]));

        var tokReq = Assert.Single(server.Requests, r => r.PathAndQuery == "/tokens");
        Assert.Equal("pk_sbox_12345", tokReq.Headers["Authorization"]);
        Assert.Equal("4242424242424242", JObject.Parse(tokReq.Body)["number"]?.ToString());

        var submitReq = Assert.Single(server.Requests, r => r.PathAndQuery == "/payment-sessions/ps_999/submit");
        Assert.Equal("42424242", JObject.Parse(submitReq.Body)["card_metadata"]?["bin"]?.ToString());

        var devReq = Assert.Single(server.Requests, r => r.PathAndQuery == "/3ds/sess_1/device-information");
        Assert.Contains("threeDSServerTransID=tx_cko_42", devReq.Body);
        Assert.Contains("browserColorDepth=24", devReq.Body);
        Assert.Contains(server.Requests, r => r.PathAndQuery == "/3ds/sess_1/processing?s=s_tok_7");
    }

    [Fact]
    public async Task InterceptorPathAndNikeGsEswPathAndMollieChallengeAllMatchRecoveredContracts()
    {
        using var server = new LoopbackServer((req, _) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            var origin = $"http://127.0.0.1:{req.Url!.Port}";

            if (path == "/sessions-interceptor/sid_55")
                return (200, "text/html", "<script>transactionId: 'tx_int_55',</script>");
            if (path == "/sessions-interceptor/3ds-method-notification")
                return (200, "application/json", "{}");
            if (path == "/sessions-interceptor/sid_55/device-information")
                return (200, "text/html", "<script>CKO3DS.challenge.get3ds2FullRedirectChallenge('{\"id\":1}');</script>");
            if (path == "/sessions-interceptor/hosted-challenge-notification")
                return (200, "application/json", new JObject
                {
                    ["action"] = "Redirect",
                    ["redirect_to_url"] = $"{origin}/done",
                }.ToString());
            if (path == "/done")
                return (200, "text/plain", "ok");
            if (path == "/esw/3ds")
                return (200, "text/html", "<script>transactionId: 'tx_esw_88',</script>");
            if (path == "/esw/3ds/device-information")
                return (200, "text/html", "<html>ok</html>");
            if (path == "/esw/3ds/processing")
                return (200, "application/json", "{}");
            if (path == "/esw/3ds/long-verify")
                return (200, "application/json", new JObject
                {
                    ["action"] = "Redirect",
                    ["redirect_to_url"] = $"{origin}/esw-done",
                }.ToString());
            if (path == "/sessions-interceptor/challenge-notification")
                return (200, "application/json", """{"notified":true}""");
            if (path == "/api/v1/public/core/payments/poll")
                return (200, "application/json", """{"status":"paid","id":"tr_mollie_1"}""");
            return (404, "application/json", "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };

        // Path 2: Gateway Dispatcher (/sessions-interceptor/{id})
        var intCtx = new FlowContext { Http = http, Url = server.BaseUrl };
        intCtx.Session.Vars["checkoutcom.apiHost"] = server.BaseUrl;
        intCtx.Session.Vars["checkoutcom.mode"] = "interceptor";
        intCtx.Session.Vars["checkoutcom.actionUrl"] = server.BaseUrl + "/sessions-interceptor/sid_55";
        var intRes = await new CheckoutComGateway().CompleteActionAsync(intCtx, """{"cres":"c1"}""", default);
        Assert.True(intRes.Ok, intRes.Error);
        var intDev = Assert.Single(server.Requests, r => r.PathAndQuery == "/sessions-interceptor/sid_55/device-information");
        Assert.Contains("iframePaymentAllowed=false", intDev.Body);

        // Path 3: NIKE-GS / ESW
        var gsCtx = new FlowContext { Http = http, Url = "https://kids.nike.com/checkout" };
        gsCtx.Session.Vars["checkoutcom.authDevicesHost"] = server.BaseUrl;
        gsCtx.Session.Vars["checkoutcom.mode"] = "nike-gs";
        gsCtx.Session.Vars["nike.threeDSecureRedirectUrl"] = server.BaseUrl + "/esw/3ds";
        gsCtx.Session.Vars["threeDsPayload"] = """{"cres":"c2","s":"esw_s"}""";
        var gsRes = await new NikeGsFlow().Process3DSAsync(gsCtx, default);
        Assert.True(gsRes.Ok, gsRes.Error);
        var eswDev = Assert.Single(server.Requests, r => r.PathAndQuery == "/esw/3ds/device-information");
        Assert.Contains("browserColorDepth=32", eswDev.Body);
        Assert.Contains("iframePaymentAllowed=true", eswDev.Body);

        // Path 4: Mollie challenge notification + poll
        var mollieCtx = new FlowContext { Http = http, Url = server.BaseUrl };
        mollieCtx.Session.Vars["checkoutcom.apiHost"] = server.BaseUrl;
        mollieCtx.Session.Vars["mollie.apiHost"] = server.BaseUrl;
        mollieCtx.Session.Vars["mollie.mode"] = "checkoutcom";
        var mollieRes = await new MollieGateway().CompleteActionAsync(mollieCtx, """{"cres":"c3"}""", default);
        Assert.True(mollieRes.Ok, mollieRes.Error);
        Assert.Contains(server.Requests, r => r.PathAndQuery == "/sessions-interceptor/challenge-notification");
        Assert.Contains(server.Requests, r => r.PathAndQuery == "/api/v1/public/core/payments/poll");
    }
}
