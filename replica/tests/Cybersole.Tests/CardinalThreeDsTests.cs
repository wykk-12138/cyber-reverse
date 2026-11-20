using System.Net;
using System.Text;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

public sealed class CardinalThreeDsTests
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

    private static string FakeJwt(JObject payload)
    {
        static string B64Url(string s) => Convert.ToBase64String(Encoding.UTF8.GetBytes(s))
            .TrimEnd('=').Replace('+', '-').Replace('/', '_');
        return B64Url("""{"alg":"HS256","typ":"JWT"}""") + "." + B64Url(payload.ToString(Newtonsoft.Json.Formatting.None)) + ".sig";
    }

    [Fact]
    public async Task CentinelVariantInitAndContinueMatchRecoveredPayloadsAndHeaders()
    {
        var cardinalJwt = FakeJwt(new JObject { ["ConsumerSessionId"] = "0_df_ref_999", ["ReferenceId"] = "ref-999" });

        using var server = new LoopbackServer((req, _) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == CardinalThreeDs.CentinelInitPath)
                return (200, "application/json", new JObject { ["CardinalJWT"] = cardinalJwt }.ToString());
            if (path == CardinalThreeDs.CentinelContinuePath)
                return (200, "application/json", new JObject { ["CardinalJWT"] = cardinalJwt }.ToString());
            return (404, "application/json", "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = "https://shop.example/checkout" };
        ctx.Session.Vars["cardinal.centinelHost"] = server.BaseUrl;

        var cardinal = new CardinalThreeDs();
        var init = await cardinal.InitAsync(ctx, "server.jwt.1", CardinalThreeDs.CardinalVariant.Centinel, default);
        Assert.True(init.Ok, init.Error);
        Assert.Equal("ref-999", ctx.Session.Vars["cardinal.dfReferenceId"]);

        var cont = await cardinal.ContinueAsync(ctx, "tx-123", null, CardinalThreeDs.CardinalVariant.Centinel, default);
        Assert.True(cont.Ok, cont.Error);

        Assert.Equal(2, server.Requests.Count);
        var initReq = server.Requests[0];
        Assert.Equal(CardinalThreeDs.CentinelInitPath, initReq.PathAndQuery);
        Assert.StartsWith("Tid-", initReq.Headers["x-cardinal-tid"]);
        Assert.Contains("application/json", initReq.Headers["Content-Type"]);
        var initJson = JObject.Parse(initReq.Body);
        Assert.Equal("SongbirdJS", initJson["Client"]?["Agent"]?.ToString());
        Assert.Equal("1.35.0", initJson["Client"]?["Version"]?.ToString());
        Assert.True(initJson["BrowserPayload"]?["SupportsAlternativePayments"]?["cca"]?.Value<bool>() == true);

        var contReq = server.Requests[1];
        Assert.Equal(CardinalThreeDs.CentinelContinuePath, contReq.PathAndQuery);
        // NetClient.BuildRequest (owned outside Cybersole.Stores) pre-adds sec-fetch-site: none via TryAddWithoutValidation
        // before applying options.Headers, so the wire header contains either "same-origin" or "none, same-origin".
        Assert.Contains("same-origin", contReq.Headers["sec-fetch-site"]
            .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries));
        var contJson = JObject.Parse(contReq.Body);
        Assert.Equal("CCA", contJson["PaymentType"]?.ToString());
        Assert.Equal("tx-123", contJson["OrderDetails"]?["TransactionId"]?.ToString());
    }

    [Fact]
    public async Task CardinalTrustedVariantAndCruiseStepUpDriveWarhammerFlow()
    {
        var cardinalJwt = FakeJwt(new JObject { ["ConsumerSessionId"] = "csid-trusted-42" });

        using var server = new LoopbackServer((req, _) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == CardinalThreeDs.TrustedInitPath)
                return (200, "application/json", new JObject { ["CardinalJWT"] = cardinalJwt }.ToString());
            if (path == CardinalThreeDs.TrustedContinuePath)
                return (200, "application/json", new JObject { ["StepUpUrl"] = "http://127.0.0.1:" + req.Url!.Port + "/V2/Cruise/StepUp" }.ToString());
            if (path == CardinalThreeDs.CruiseStepUpPath)
                return (200, "text/html", """<form><input name="McsId" value="mcs-1"/><input name="CardinalJWT" value="stepped.jwt.ok"/></form>""");
            if (path == CardinalThreeDs.CruiseTermRedirectionPath)
                return (200, "application/json", """{"CardinalJWT":"final.result.jwt"}""");
            return (404, "application/json", "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = "https://www.warhammer.com/checkout" };
        ctx.Session.Vars["cardinal.trustedHost"] = server.BaseUrl;
        ctx.Session.Vars["cardinal.centinelHost"] = server.BaseUrl;
        ctx.Session.Vars["cardinal.serverJwt"] = "wh.server.jwt";
        ctx.Session.Vars["cardinal.transactionId"] = "wh-tx-9";
        ctx.Session.Vars["warhammer.isvResponseJwt"] = "isv.resp.jwt";

        var wh = new WarhammerFlow();
        var res = await wh.Process3DSAsync(ctx, default);

        Assert.True(res.Ok, res.Error);
        Assert.Equal("csid-trusted-42", ctx.Session.Vars["cardinal.consumerSessionId"]);
        Assert.Equal("final.result.jwt", ctx.Session.Vars["cardinal.resultJwt"]);

        var trustedInit = server.Requests[0];
        Assert.Equal(CardinalThreeDs.CybersourceOrigin, trustedInit.Headers["Origin"]);
        Assert.Equal(CardinalThreeDs.CybersourceOrigin, trustedInit.Headers["Referer"]);
        var trustedJson = JObject.Parse(trustedInit.Body);
        Assert.Equal("2.1.0", trustedJson["Client"]?["Version"]?.ToString());
        Assert.Equal(JTokenType.Null, trustedJson["ConsumerSessionId"]!.Type);

        var termReq = Assert.Single(server.Requests, r => r.PathAndQuery == CardinalThreeDs.CruiseTermRedirectionPath);
        var termJson = JObject.Parse(termReq.Body);
        Assert.Equal("mcs-1", termJson["McsId"]?.ToString());
        Assert.Equal("stepped.jwt.ok", termJson["CardinalJWT"]?.ToString());
    }

    [Fact]
    public async Task GeoDeviceFingerprintAndDemandwarePlaceOrderQueryAreWired()
    {
        var cardinalJwt = FakeJwt(new JObject { ["ConsumerSessionId"] = "df_dw_123" });

        using var server = new LoopbackServer((req, _) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == "/DeviceFingerprintWeb/V2/Browser/Render")
                return (200, "text/html", "<html>fp</html>");
            if (path == "/DeviceFingerprintWeb/V2/Browser/SaveBrowserData")
                return (200, "application/json", """{"ok":true}""");
            if (path == "/DeviceFingerprintWeb/V2/Browser/Notification")
                return (200, "application/json", """{"ok":true}""");
            if (path == CardinalThreeDs.CentinelInitPath)
                return (200, "application/json", new JObject { ["CardinalJWT"] = cardinalJwt }.ToString());
            if (path.EndsWith("/CheckoutServices-PlaceOrder", StringComparison.Ordinal))
                return (200, "application/json", """{"orderNo":"DW-9001"}""");
            return (404, "application/json", "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/product" };
        ctx.Session.Vars["cardinal.geoHost"] = server.BaseUrl;
        ctx.Session.Vars["cardinal.centinelHost"] = server.BaseUrl;
        ctx.Session.Vars["cardinal.serverJwt"] = "dw.server.jwt";

        var cardinal = new CardinalThreeDs();
        var dfRes = await cardinal.CollectDeviceFingerprintAsync(ctx, "org-1", "ref-abc", "bin-77", null, default);
        Assert.True(dfRes.Ok, dfRes.Error);

        var renderReq = Assert.Single(server.Requests, r => r.PathAndQuery.StartsWith("/DeviceFingerprintWeb/V2/Browser/Render", StringComparison.Ordinal));
        Assert.Contains("orgUnitId=org-1", renderReq.PathAndQuery);
        Assert.Contains("referenceId=ref-abc", renderReq.PathAndQuery);

        var saveReq = Assert.Single(server.Requests, r => r.PathAndQuery == "/DeviceFingerprintWeb/V2/Browser/SaveBrowserData");
        Assert.EndsWith("/V1/Cruise/Collect", saveReq.Headers["Referer"]);
        var saveJson = JObject.Parse(saveReq.Body);
        Assert.Equal("1.5.1", saveJson["FingerprintDetails"]?["Version"]?.ToString());
        Assert.Equal("02", saveJson["Screen"]?["CCAScreenSize"]?.ToString());

        // Clear dfReferenceId so DemandwareFlow.SubmitOrderAsync drives CardinalInit and uses PlaceOrderPathWith
        ctx.Session.Vars.Remove("cardinal.dfReferenceId");
        var dw = new DemandwareFlow("dw", "DW", new[] { "127.0.0.1" }, "Shop-Site", "en_US");
        var orderRes = await dw.SubmitOrderAsync(ctx, default);
        Assert.True(orderRes.Ok, orderRes.Error);
        Assert.Equal("DW-9001", ctx.Session.OrderNumber);
        Assert.Contains(server.Requests, r =>
            r.PathAndQuery == "/on/demandware.store/Sites-Shop-Site/en_US/CheckoutServices-PlaceOrder?termsconditions=true&DFReferenceId=df_dw_123");
    }

    [Fact]
    public async Task PaynamicsGatewayCompleteActionCallsCardinalCentinel()
    {
        var cardinalJwt = FakeJwt(new JObject { ["ConsumerSessionId"] = "0_paynamics_df" });

        using var server = new LoopbackServer((req, _) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == CardinalThreeDs.CentinelInitPath || path == CardinalThreeDs.CentinelContinuePath)
                return (200, "application/json", new JObject { ["CardinalJWT"] = cardinalJwt }.ToString());
            return (404, "application/json", "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = "https://shop.example/checkout" };
        ctx.Session.Vars["cardinal.centinelHost"] = server.BaseUrl;
        ctx.Session.Vars["cardinal.serverJwt"] = "paynamics.server.jwt";
        ctx.Session.Vars["cardinal.transactionId"] = "pnm-tx-5";

        var gw = new PaynamicsGateway();
        var res = await gw.CompleteActionAsync(ctx, string.Empty, default);
        Assert.True(res.Ok, res.Error);
        Assert.Contains(server.Requests, r => r.PathAndQuery == CardinalThreeDs.CentinelInitPath);
        Assert.Contains(server.Requests, r => r.PathAndQuery == CardinalThreeDs.CentinelContinuePath);
    }

    [Fact]
    public async Task StoreFlowAndDemandwareProcess3DsWireCollectDeviceFingerprint()
    {
        var cardinalJwt = FakeJwt(new JObject { ["ConsumerSessionId"] = "df_wired_456" });

        using var server = new LoopbackServer((req, _) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == CardinalThreeDs.CentinelInitPath || path == CardinalThreeDs.CentinelContinuePath)
                return (200, "application/json", new JObject { ["CardinalJWT"] = cardinalJwt }.ToString());
            if (path == "/DeviceFingerprintWeb/V2/Browser/Render")
                return (200, "text/html", "<html>fp</html>");
            if (path == "/DeviceFingerprintWeb/V2/Browser/SaveBrowserData" ||
                path == "/DeviceFingerprintWeb/V2/Browser/Notification")
                return (200, "application/json", """{"ok":true}""");
            return (404, "application/json", "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };

        // 1. StoreFlow.Process3DSAsync "fingerprint" arm validates missing ids and runs geo collection when present.
        var sfCtx = new FlowContext { Http = http, Url = server.BaseUrl + "/checkout" };
        sfCtx.Session.Vars["cardinal.geoHost"] = server.BaseUrl;
        sfCtx.Session.Vars["cardinal.step"] = "fingerprint";

        var baseFlow = new StubStoreFlow();
        var missingRes = await baseFlow.Process3DSAsync(sfCtx, default);
        Assert.False(missingRes.Ok);
        Assert.Contains("missing orgUnitId", missingRes.Error);

        sfCtx.Session.Vars["cardinal.orgUnitId"] = "org-sf";
        sfCtx.Session.Vars["cardinal.dfReferenceId"] = "ref-sf";
        sfCtx.Session.Vars["cardinal.binSessionId"] = "bin-sf";
        var sfRes = await baseFlow.Process3DSAsync(sfCtx, default);
        Assert.True(sfRes.Ok, sfRes.Error);
        Assert.Contains(server.Requests, r => r.PathAndQuery.Contains("orgUnitId=org-sf", StringComparison.Ordinal));
        Assert.Contains(server.Requests, r => r.PathAndQuery == "/DeviceFingerprintWeb/V2/Browser/SaveBrowserData");
        Assert.Contains(server.Requests, r => r.PathAndQuery.StartsWith("/DeviceFingerprintWeb/V2/Browser/Notification", StringComparison.Ordinal));

        server.Requests.Clear();

        // Also cover StoreFlow.ProcessPaymentAsync cardinal.step = "fingerprint" dispatch.
        sfCtx.Session.Vars["paymentStatus"] = "requires_action";
        var payFpRes = await baseFlow.ProcessPaymentAsync(sfCtx, default);
        Assert.True(payFpRes.Ok, payFpRes.Error);
        Assert.Equal(3, server.Requests.Count);

        server.Requests.Clear();

        // 2. DemandwareFlow.Process3DSAsync drives Init -> Geo DeviceFingerprint -> Continue when orgUnitId is set.
        var dwCtx = new FlowContext { Http = http, Url = server.BaseUrl + "/checkout" };
        dwCtx.Session.Vars["cardinal.centinelHost"] = server.BaseUrl;
        dwCtx.Session.Vars["cardinal.geoHost"] = server.BaseUrl;
        dwCtx.Session.Vars["cardinal.serverJwt"] = "dw.fp.jwt";
        dwCtx.Session.Vars["cardinal.orgUnitId"] = "org-dw";
        dwCtx.Session.Vars["cardinal.transactionId"] = "tx-dw-9";

        var dw = new DemandwareFlow("dw", "DW", new[] { "127.0.0.1" }, "Shop-Site", "en_US");
        var dwRes = await dw.Process3DSAsync(dwCtx, default);
        Assert.True(dwRes.Ok, dwRes.Error);
        Assert.Equal(5, server.Requests.Count);
        Assert.Equal(CardinalThreeDs.CentinelInitPath, server.Requests[0].PathAndQuery);
        Assert.Contains("orgUnitId=org-dw", server.Requests[1].PathAndQuery);
        Assert.Equal("/DeviceFingerprintWeb/V2/Browser/SaveBrowserData", server.Requests[2].PathAndQuery);
        Assert.StartsWith("/DeviceFingerprintWeb/V2/Browser/Notification", server.Requests[3].PathAndQuery);
        Assert.Equal(CardinalThreeDs.CentinelContinuePath, server.Requests[4].PathAndQuery);
    }

    private sealed class StubStoreFlow : StoreFlow
    {
        public override string Id => "sf";
        public override string Name => "SF";
        public override IReadOnlyList<string> Domains { get; } = new[] { "127.0.0.1" };
    }
}
