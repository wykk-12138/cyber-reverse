using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

public sealed class CheckoutComAcsHandlersTests
{
    private sealed record CapturedRequest(
        string Method,
        string RawUrl,
        string Path,
        Dictionary<string, string> Headers,
        string? ContentType,
        string Body);

    private sealed record MockReply(
        int Status,
        string ContentType,
        string Body,
        Dictionary<string, string>? Headers = null);

    private sealed class AcsLoopbackServer : IDisposable
    {
        private readonly HttpListener _listener = new();
        public string BaseUrl { get; }
        public List<CapturedRequest> Requests { get; } = new();

        public AcsLoopbackServer(Func<CapturedRequest, MockReply> handler)
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

                    var captured = new CapturedRequest(
                        ctx.Request.HttpMethod,
                        ctx.Request.RawUrl ?? "/",
                        ctx.Request.Url?.AbsolutePath ?? "/",
                        headers,
                        ctx.Request.ContentType,
                        body);
                    Requests.Add(captured);

                    var reply = handler(captured);
                    ctx.Response.StatusCode = reply.Status;
                    ctx.Response.ContentType = reply.ContentType;
                    if (reply.Headers is not null)
                    {
                        foreach (var kv in reply.Headers)
                            ctx.Response.Headers[kv.Key] = kv.Value;
                    }

                    var bytes = Encoding.UTF8.GetBytes(reply.Body);
                    if (reply.Status != 205 && reply.Status != 204 && reply.Status != 304)
                        await ctx.Response.OutputStream.WriteAsync(bytes).ConfigureAwait(false);
                    ctx.Response.Close();
                }
            });
        }

        private static int FreePort()
        {
            var l = new TcpListener(IPAddress.Loopback, 0);
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

    private static FlowContext NewAcsContext(NetClient http, string baseUrl)
    {
        var c = new FlowContext { Http = http, Url = "https://shop.test/checkout" };
        c.Session.Vars["checkoutcom.acsBaseUrl"] = baseUrl;
        c.Session.Vars["checkoutcom.acsPollMs"] = "0";
        return c;
    }

    [Fact]
    public void All28KnownHostsMapToThe19ClustersAndUnknownsFallBack()
    {
        var expected = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["acs.apata.io"] = "01_apata",
            ["acs-challenge.apata.io"] = "01_apata",
            ["acs2.edb.com"] = "02_edb",
            ["3ds.soldo.com"] = "03_soldo",
            ["acs.touch.tech"] = "04_touchtech",
            ["cacs.icard.com"] = "05_icard",
            ["cacs-v2.icard.com"] = "05_icard",
            ["acs.revolut.com"] = "06_revolut",
            ["poseidon.revolut.com"] = "06_revolut",
            ["3dsecure.zen.com"] = "07_zen",
            ["verify.monzo.com"] = "08_monzo",
            ["3dsecure.mbank.cz"] = "09_mbank",
            ["secure4.arcot.com"] = "10_arcot",
            ["acs.capitalone.com"] = "11_capitalone",
            ["acs1.3ds.modirum.com"] = "12_modirum",
            ["acs2.3ds.modirum.com"] = "12_modirum",
            ["acs1.mpts.modirum.com"] = "12_modirum",
            ["acs2.mpts.modirum.com"] = "12_modirum",
            ["api.secure-code.bunq.com"] = "13_bunq",
            ["api.id.mastercard.bunq.com"] = "13_bunq",
            ["3dsecure.starlingbank.com"] = "14_starling",
            ["3ds-a.live.ext.prod.enfuce.com"] = "15_enfuce",
            ["3ds-b.live.ext.prod.enfuce.com"] = "15_enfuce",
            ["authentication-acs.marqeta.com"] = "16_marqeta",
            ["acs-safekey.americanexpress.com"] = "17_amex",
            ["idcheck.acs.touchtechpayments.com"] = "18_touchtechpayments",
            ["verifiedbyvisa.acs.touchtechpayments.com"] = "18_touchtechpayments",
            ["authentication.cardinalcommerce.com"] = "19_cardinal",
        };

        Assert.Equal(28, expected.Count);
        Assert.Equal(19, expected.Values.Distinct().Count());
        foreach (var host in AcsHosts.Known)
        {
            Assert.True(expected.TryGetValue(host, out var cluster), $"Missing mapping expectation for {host}");
            Assert.Equal(cluster, CheckoutComAcsHandlers.ClusterForHost($"https://{host}/challenge"));
        }

        Assert.Equal("20_fallback", CheckoutComAcsHandlers.ClusterForHost("https://acs.unknown-bank.test/3ds"));
    }

    [Fact]
    public async Task Cluster01ApataApprovalPickerAndPollingAndRedirectShortcutWork()
    {
        var polls = 0;
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/apata/start")
            {
                return new(200, "text/html", """
                    <html><body>How would you like to approve this payment
                      <form action="/apata/select">
                        <input name="transactionId" value="tx_ap_1" />
                        <button id="app-btn" value="1">App</button>
                      </form>
                    </body></html>
                    """);
            }
            if (req.Path == "/apata/select")
            {
                return new(200, "text/html", """
                    <script>var cfg = { "pollToken": "pt_ap_99" };</script>
                    <form id="challenge_form"><input name="creq" value="creq_ap" /></form>
                    """);
            }
            if (req.Path == "/v1/PollTransaction")
            {
                polls++;
                var state = polls == 1 ? "PENDING" : "COMPLETED";
                return new(200, "application/json", $"{{\"state\":\"{state}\"}}");
            }
            if (req.Path == "/v1/BrowserCReqAction")
            {
                return new(200, "text/html", """
                    <form action="https://merchant.test/3ds/done"><input name="cres" value="cres_ap_done" /></form>
                    """);
            }
            if (req.Path == "/apata/shortcut")
            {
                return new(200, "text/html", """
                    <form id="redirect-form" action="https://merchant.test/fast"><input name="cres" value="cres_fast" /></form>
                    """);
            }
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);
        var form = new Dictionary<string, string> { ["creq"] = "c0", ["threeDSSessionData"] = "drop-me" };

        var res = await CheckoutComAcsHandlers.ExecuteAsync(
            ctx, "https://acs.apata.io/apata/start", form, stripThreeDsSessionData: true, ct: default);

        Assert.True(res.Ok, res.Error);
        Assert.Equal("01_apata", res.Cluster);
        Assert.Equal("https://merchant.test/3ds/done", res.ActionUrl);
        Assert.Equal("cres_ap_done", res.Values["cres"]);

        Assert.DoesNotContain("threeDSSessionData", server.Requests[0].Body);
        var selectJson = JObject.Parse(server.Requests[1].Body);
        Assert.Equal("SUBMIT", selectJson["action"]?.ToString());
        Assert.Equal("tx_ap_1", selectJson["transactionId"]?.ToString());
        Assert.Equal("1", selectJson["answer"]?.ToString());
        Assert.Equal(2, server.Requests.Count(r => r.Path == "/v1/PollTransaction"));

        var fast = await CheckoutComAcsHandlers.ExecuteAsync(
            ctx, "https://acs-challenge.apata.io/apata/shortcut", new Dictionary<string, string>(), ct: default);
        Assert.True(fast.Ok, fast.Error);
        Assert.Equal("https://merchant.test/fast", fast.ActionUrl);
        Assert.Equal("cres_fast", fast.Values["cres"]);
    }

    [Fact]
    public async Task Cluster02EdbWalksFormSwitchAndPollsToAcsAndPares()
    {
        var collectPolls = 0;
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/edb/start")
                return new(200, "text/html", """<form name="postform" action="/edb/my"><input name="step" value="1" /></form>""");
            if (req.Path == "/edb/my")
                return new(200, "text/html", """<form name="myForm" action="/edb/fp"></form>""");
            if (req.Path == "/edb/fp")
                return new(200, "text/html", """<form name="externalPre" action="/edb/pre"></form>""");
            if (req.Path == "/edb/pre")
                return new(200, "text/html", """<form name="externalCollect" action="/edb/collect"></form>""");
            if (req.Path == "/edb/collect")
            {
                collectPolls++;
                return collectPolls == 1
                    ? new(200, "text/html", "<html>waiting</html>")
                    : new(200, "text/html", """<form id="toACSForm" action="/edb/final"><input name="tok" value="edb_t" /></form>""");
            }
            if (req.Path == "/edb/final")
                return new(200, "text/html", """<form name="PAResForm"><input name="PaRes" value="pares_edb" /><input name="MD" value="md_edb" /></form>""");
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);
        var res = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://acs2.edb.com/edb/start", null, ct: default);

        Assert.True(res.Ok, res.Error);
        Assert.Equal("02_edb", res.Cluster);
        Assert.Null(res.ActionUrl);
        Assert.Equal("pares_edb", res.Values["PaRes"]);
        Assert.Equal("md_edb", res.Values["MD"]);
        var fpReq = Assert.Single(server.Requests, r => r.Path == "/edb/fp");
        Assert.Equal("/edb/fp?fp=583237862", fpReq.RawUrl);
        Assert.Equal("fingprnt=583237862", fpReq.Body);
    }

    [Fact]
    public async Task Cluster03SoldoSendsPercentEncodedWebKitMultipartToDoubleSlashV2Form()
    {
        var polls = 0;
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/soldo/start")
                return new(200, "text/html", """<form><input name="a+b" value="1/2=" /></form>""");
            if (req.RawUrl == "//v2Form")
            {
                polls++;
                return polls == 1
                    ? new(200, "text/html", """<form><input name="nonce" value="n1" /></form>""")
                    : new(200, "text/html", """<form><input name="cres" value="cres_soldo" /></form>""");
            }
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);
        var res = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://3ds.soldo.com/soldo/start", null, ct: default);

        Assert.True(res.Ok, res.Error);
        Assert.Equal("03_soldo", res.Cluster);
        Assert.Equal("cres_soldo", res.Values["cres"]);

        var v2Reqs = server.Requests.Where(r => r.RawUrl == "//v2Form").ToList();
        Assert.Equal(2, v2Reqs.Count);
        Assert.Equal("multipart/form-data; boundary=----WebKitFormBoundaryT21mAUisfuWtVfY8", v2Reqs[0].ContentType);
        Assert.Contains("name=\"a%2Bb\"", v2Reqs[0].Body);
        Assert.Contains("1%2F2%3D", v2Reqs[0].Body);
    }

    [Fact]
    public async Task Cluster04TouchtechHandlesRedirectDelegatedPollAndMoneseFallback()
    {
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/tt/redirect")
            {
                var mdB64 = Convert.ToBase64String(Encoding.UTF8.GetBytes("{\"md\":\"md_tt_1\"}"));
                return new(200, "text/html", $"<script>function redirect(){{}} var pares = \"pares_tt_1\"; atob(\"{mdB64}\");</script>");
            }
            if (req.Path == "/tt/wise")
                return new(200, "text/html", "<html><head><title>Wise Auth</title></head><script>token: 'tt_tok_1'</script></html>");
            if (req.Path == "/v1/transactions/tt_tok_1/challenge/select")
                return new(200, "application/json", "{\"status\":\"ok\"}");
            if (req.Path == "/v1/transactions/tt_tok_1/challenge")
                return new(200, "application/json", "{\"status\":\"authenticated\"}");
            if (req.Path == "/v1/tt_tok_1/continue")
                return new(200, "text/html", """<form><input name="cres" value="cres_tt_1" /></form>""");
            if (req.Path == "/tt/monese")
                return new(200, "text/html", "<html><head><title>Challenge</title></head><body>Monese app token: 'm_1'</body></html>");
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);

        var r1 = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://acs.touch.tech/tt/redirect", null, ct: default);
        Assert.True(r1.Ok);
        Assert.Equal("pares_tt_1", r1.Values["PaRes"]);
        Assert.Equal("md_tt_1", r1.Values["MD"]);

        var r2 = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://acs.touch.tech/tt/wise", null, ct: default);
        Assert.True(r2.Ok, r2.Error);
        Assert.Equal("cres_tt_1", r2.Values["cres"]);
        var pollReq = Assert.Single(server.Requests, r => r.RawUrl == "/v1/transactions/tt_tok_1/challenge?retryCounter=0");
        Assert.Equal("https://acs.touch.tech/v1/emv3ds/challenge", pollReq.Headers["Referer"]);

        var r3 = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://acs.touch.tech/tt/monese", null, ct: default);
        Assert.False(r3.Ok);
        Assert.True(r3.RequiresInteractiveVerification);
        Assert.Equal("04_touchtech", r3.Cluster);
    }

    [Fact]
    public async Task Cluster05IcardHandlesV1AndV2AndOtpFallback()
    {
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/icard/start")
                return new(302, "text/plain", "", new Dictionary<string, string> { ["Location"] = "/push/acct_77?q=1" });
            if (req.Path == "/push/acct_77")
                return new(200, "text/html", "<html>Approve push</html>");
            if (req.Path == "/Process/CheckPush")
                return new(200, "application/json", "{\"responseCode\":\"0\"}");
            if (req.Path == "/ProcessV2/CheckPush")
                return new(200, "application/json", "{\"responseCode\":\"0\"}");
            if (req.Path == "/Process/SendSURes")
                return new(200, "text/html", """<form id="PAResForm1"><input name="PaRes" value="ic_pares" /></form>""");
            if (req.Path == "/icard/otp")
                return new(302, "text/plain", "", new Dictionary<string, string> { ["Location"] = "/otp/acct_88" });
            if (req.Path == "/otp/acct_88")
                return new(200, "text/html", "<html>Please confirm-otp code</html>");
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);

        var v1 = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://cacs.icard.com/icard/start", null, ct: default);
        Assert.True(v1.Ok, v1.Error);
        Assert.Equal("ic_pares", v1.Values["PaRes"]);
        Assert.Contains(server.Requests, r => r.Path == "/Process/CheckPush");

        var v2 = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://cacs-v2.icard.com/icard/start", null, ct: default);
        Assert.True(v2.Ok, v2.Error);
        Assert.Contains(server.Requests, r => r.Path == "/ProcessV2/CheckPush");

        var otp = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://cacs.icard.com/icard/otp", null, ct: default);
        Assert.False(otp.Ok);
        Assert.True(otp.RequiresInteractiveVerification);
    }

    [Fact]
    public async Task Cluster06RevolutPollsAndRetries205ResetContent()
    {
        var confirms = 0;
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/rev/start")
            {
                return new(200, "text/html", """
                    <script>
                      config.transaction = { transactionInfoURL: 'https://acs.revolut.com/rev/poll', confirmTransactionURL: 'https://poseidon.revolut.com/rev/confirm', x: 1 };
                    </script>
                    """);
            }
            if (req.Path == "/rev/poll")
                return new(200, "application/json", "{\"status\":\"AUTHENTICATED\"}");
            if (req.Path == "/rev/confirm")
            {
                confirms++;
                return confirms == 1
                    ? new(205, "text/plain", "")
                    : new(200, "text/html", """<form id="poseidonForm" action="https://merchant.test/rev-done"><input name="cres" value="cres_rev" /></form>""");
            }
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);
        var res = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://poseidon.revolut.com/rev/start", null, ct: default);

        Assert.True(res.Ok, res.Error);
        Assert.Equal("06_revolut", res.Cluster);
        Assert.Equal("https://merchant.test/rev-done", res.ActionUrl);
        Assert.Equal("cres_rev", res.Values["cres"]);
        Assert.Equal(2, confirms);
    }

    [Fact]
    public async Task Cluster07ZenOverridesHeadersNormalizesCreqAndHandlesJsfAjax()
    {
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/zen/challenge")
            {
                if (req.Body.Contains("mobile%3Aj_idt197"))
                    return new(200, "text/xml", "<partial-response>auth-complete</partial-response>");
                if (req.Body.Contains("mobile%3Aj_idt198=Continue"))
                    return new(200, "text/html", """<form id="challenge-form" action="https://merchant.test/zen-cb"><input name="cres" value="cres_zen" /></form>""");
                return new(200, "text/html", """
                    <form id="challenge-form">
                      <input name="SESSIONID" value="zen_sid" />
                      <input name="javax.faces.ViewState" value="zen_vs" />
                    </form>
                    """);
            }
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);
        var res = await CheckoutComAcsHandlers.ExecuteAsync(
            ctx,
            "https://3dsecure.zen.com/zen/challenge",
            new Dictionary<string, string> { ["creq"] = "abc==", ["threeDSSessionData"] = "strip" },
            ct: default);

        Assert.True(res.Ok, res.Error);
        Assert.Equal("07_zen", res.Cluster);
        Assert.Equal("https://merchant.test/zen-cb", res.ActionUrl);
        Assert.Equal("cres_zen", res.Values["cres"]);

        Assert.Contains("creq=abc", server.Requests[0].Body);
        Assert.DoesNotContain("creq=abc%3D", server.Requests[0].Body);
        Assert.DoesNotContain("threeDSSessionData", server.Requests[0].Body);
        Assert.Equal("iframe", server.Requests[0].Headers["sec-fetch-dest"]);
        Assert.Equal("active", server.Requests[0].Headers["sec-fetch-storage-access"]);
        Assert.Equal("partial/ajax", server.Requests[1].Headers["faces-request"]);
        Assert.False(server.Requests[2].Headers.ContainsKey("faces-request"));
    }

    [Fact]
    public async Task Cluster08MonzoBranches303Between3ds2And3ds1()
    {
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/monzo/3ds2")
                return new(303, "text/plain", "", new Dictionary<string, string> { ["Location"] = "https://verify.monzo.com/3ds2/challenge?id=m2" });
            if (req.Path == "/3ds2/challenge/poll")
                return new(200, "application/json", "{\"completed\":true}");
            if (req.Path == "/3ds2/challenge")
                return new(200, "text/html", """<form action="https://merchant.test/monzo2"><input name="cres" value="cres_m2" /></form>""");

            if (req.Path == "/monzo/3ds1")
                return new(303, "text/plain", "", new Dictionary<string, string> { ["Location"] = "https://verify.monzo.com/auth/tx_m1" });
            if (req.Path == "/3ds/v2/challenge-pending/tx_m1")
                return new(200, "text/html", """<input name="messageCorrelationId" value="mc/1" />""");
            if (req.Path == "/3ds/poll-challenge")
                return new(200, "application/json", "{\"completed\":true}");
            if (req.Path == "/3ds/v2/challenge-complete/tx_m1")
                return new(200, "text/html", """<input name="PaRes" value="pares_m1" />""");

            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);

        var r2 = await CheckoutComAcsHandlers.ExecuteAsync(
            ctx,
            "https://verify.monzo.com/monzo/3ds2",
            new Dictionary<string, string> { ["threeDSSessionData"] = "s_m2" },
            ct: default);
        Assert.True(r2.Ok, r2.Error);
        Assert.Equal("https://merchant.test/monzo2", r2.ActionUrl);
        Assert.Equal("cres_m2", r2.Values["cres"]);
        Assert.Equal("s_m2", r2.Values["threeDSSessionData"]);

        var r1 = await CheckoutComAcsHandlers.ExecuteAsync(
            ctx,
            "https://verify.monzo.com/monzo/3ds1",
            new Dictionary<string, string> { ["MD"] = "md_m1" },
            ct: default);
        Assert.True(r1.Ok, r1.Error);
        Assert.Null(r1.ActionUrl);
        Assert.Equal("pares_m1", r1.Values["PaRes"]);
        Assert.Equal("md_m1", r1.Values["MD"]);
    }

    [Fact]
    public async Task Cluster09MbankPollsUntilOnclickClearsThenConfirms()
    {
        var ajaxCalls = 0;
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/mbank/start")
            {
                return new(200, "text/html", """
                    <form id="challenge-form">
                      <input name="SESSIONID" value="mb_sid" />
                      <input id="j_id1:javax.faces.ViewState:0" name="javax.faces.ViewState" value="mb_vs" />
                    </form>
                    """);
            }
            if (req.Path == "/v2/brw/index.xhtml")
            {
                if (req.Headers.ContainsKey("Faces-Request"))
                {
                    ajaxCalls++;
                    return ajaxCalls == 1
                        ? new(200, "text/xml", "<partial-response><button onclick=\"poll()\"/></partial-response>")
                        : new(200, "text/xml", "<partial-response>ready</partial-response>");
                }
                return new(200, "text/html", """<form id="challenge-form"><input name="cres" value="cres_mb" /></form>""");
            }
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);
        var res = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://3dsecure.mbank.cz/mbank/start", null, ct: default);

        Assert.True(res.Ok, res.Error);
        Assert.Equal("09_mbank", res.Cluster);
        Assert.Equal("cres_mb", res.Values["cres"]);
        Assert.Equal(2, ajaxCalls);
    }

    [Fact]
    public async Task Cluster10ArcotDrivesBankAppAndFallsBackWhenCbsMissing()
    {
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/arcot/start")
            {
                return new(200, "text/html", """
                    <form id="landingForm" action="/arcot/select">
                      <input name="tx" value="a1" />
                      <button data-tykey='BANKAPP'>App</button>
                    </form>
                    """);
            }
            if (req.Path == "/arcot/select")
            {
                return new(200, "text/html", """
                    <script>
                      var cbsUrl = "/arcot/cbs";
                      var cbsTxnId = "cbs_99";
                      var cbsPollingFreq = 1;
                      var cbsPollingRetryAttempts = 3;
                      var displayMsgFlag = "false";
                    </script>
                    <form id="verify_form" action="/arcot/verify"><input name="v" value="1" /></form>
                    """);
            }
            if (req.Path == "/arcot/cbs")
                return new(200, "application/json", "{\"status\":\"COMPLETE\"}");
            if (req.Path == "/arcot/verify")
                return new(200, "text/html", """<form id="cres_form" action="https://merchant.test/arcot-done"><input name="cres" value="cres_arcot" /></form>""");
            if (req.Path == "/arcot/sms")
                return new(200, "text/html", "<form id=\"otpForm\"></form>");
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);

        var ok = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://secure4.arcot.com/arcot/start", null, ct: default);
        Assert.True(ok.Ok, ok.Error);
        Assert.Equal("10_arcot", ok.Cluster);
        Assert.Equal("https://merchant.test/arcot-done", ok.ActionUrl);
        Assert.Equal("cres_arcot", ok.Values["cres"]);
        Assert.Contains("selected_option=BANKAPP", server.Requests[1].Body);
        Assert.Equal("same-origin", server.Requests[1].Headers["sec-fetch-site"]);
        var cbsJson = JObject.Parse(server.Requests[2].Body);
        Assert.Equal("cbs_99", cbsJson["transaction_id"]?.ToString());
        Assert.Equal("OOB", cbsJson["transaction_type"]?.ToString());

        var fb = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://secure4.arcot.com/arcot/sms", null, ct: default);
        Assert.False(fb.Ok);
        Assert.True(fb.RequiresInteractiveVerification);
    }

    [Fact]
    public async Task Cluster11CapitalOneMutatesCreqRunsSseAndValidates()
    {
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/cap1/stepup")
            {
                if (req.ContentType?.Contains("application/json", StringComparison.OrdinalIgnoreCase) == true)
                    return new(200, "application/json", "{\"taskReferenceId\":\"cap_task_1\"}");
                return new(200, "text/html", "<html>stepup</html>");
            }
            if (req.Path == "/sse/mav/cap_task_1")
                return new(200, "text/event-stream", "data: ok\n\n");
            if (req.Path == "/cap1/validate")
            {
                return new(200, "application/json", """
                    {"transactionState":"VALIDATION_SUCCEEDED","notificationUrl":"https://merchant.test/cap1","encodedResponse":"cres_cap1"}
                    """);
            }
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);
        var creqB64 = Convert.ToBase64String(Encoding.UTF8.GetBytes("{\"acsTransID\":\"c1\"}"));

        var res = await CheckoutComAcsHandlers.ExecuteAsync(
            ctx,
            "https://acs.capitalone.com/cap1/stepup",
            new Dictionary<string, string> { ["creq"] = creqB64 },
            ct: default);

        Assert.True(res.Ok, res.Error);
        Assert.Equal("11_capitalone", res.Cluster);
        Assert.Equal("https://merchant.test/cap1", res.ActionUrl);
        Assert.Equal("cres_cap1", res.Values["cres"]);

        var step2Json = JObject.Parse(server.Requests[1].Body);
        Assert.Equal("MAV", step2Json["authMethodSelected"]?.ToString());
        var sseReq = Assert.Single(server.Requests, r => r.Path == "/sse/mav/cap_task_1");
        Assert.Equal("text/event-stream", sseReq.Headers["Accept"]);
        var valJson = JObject.Parse(server.Requests[3].Body);
        Assert.Equal(string.Empty, valJson["challengeHTMLDataEntry"]?.ToString());
    }

    [Fact]
    public async Task Cluster12ModirumNormalizesEyCreqAndPollsMptsPending()
    {
        var mptsCount = 0;
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/modirum/start")
                return new(200, "text/html", """<form action="/modirum/wait"></form>""");
            if (req.RawUrl == "/modirum/wait?polling=true")
            {
                mptsCount++;
                return new(200, "text/plain", mptsCount == 1 ? "VERIFICATION_PENDING" : "DONE");
            }
            if (req.Path == "/modirum/wait")
                return new(200, "text/html", """<form name="CResForm"><input name="cres" value="cres_mod_mpts" /></form>""");
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);
        var res = await CheckoutComAcsHandlers.ExecuteAsync(
            ctx,
            "https://acs1.mpts.modirum.com/modirum/start",
            new Dictionary<string, string> { ["creq"] = "eyA+b/+c==", ["threeDSSessionData"] = "drop" },
            stripThreeDsSessionData: true,
            ct: default);

        Assert.True(res.Ok, res.Error);
        Assert.Equal("12_modirum", res.Cluster);
        Assert.Equal("cres_mod_mpts", res.Values["cres"]);
        Assert.Contains("creq=eyA-b_-c", server.Requests[0].Body);
        Assert.DoesNotContain("threeDSSessionData", server.Requests[0].Body);
        Assert.Equal(2, mptsCount);
        var finalPost = Assert.Single(server.Requests, r => r.RawUrl == "/modirum/wait");
        Assert.Contains("continue=continue", finalPost.Body);
    }

    [Fact]
    public async Task Cluster13BunqHandlesBoth3ds1And3ds2()
    {
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/bunq/s1")
                return new(200, "text/html", """<script>var u = "https://api.secure-code.bunq.com/v1/secure-code/tok_b1";</script>""");
            if (req.Path == "/v1/secure-code/tok_b1")
                return new(200, "application/json", """{"Response":[{"MasterCardSecureCode":{"status":"ACCEPTED","return_url":"https://merchant.test/b1","merchant_data":"md_b1","authentication_response":"pares_b1"}}]}""");
            if (req.Path == "/bunq/s2")
                return new(200, "text/html", """<script>var u = "https://api.id.mastercard.bunq.com/v1/challenge-request/tok_b2";</script>""");
            if (req.Path == "/v1/challenge-request/tok_b2")
                return new(200, "application/json", """{"Response":[{"MasterCardIdentityCheckChallengeRequest":{"status":"ACCEPTED","return_url":"https://merchant.test/b2","challenge_result":"cres_b2","session_data":"sess_b2"}}]}""");
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);

        var r1 = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://api.secure-code.bunq.com/bunq/s1", null, ct: default);
        Assert.True(r1.Ok, r1.Error);
        Assert.Equal("https://merchant.test/b1", r1.ActionUrl);
        Assert.Equal("md_b1", r1.Values["MD"]);
        Assert.Equal("pares_b1", r1.Values["PaRes"]);

        var r2 = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://api.id.mastercard.bunq.com/bunq/s2", null, ct: default);
        Assert.True(r2.Ok, r2.Error);
        Assert.Equal("https://merchant.test/b2", r2.ActionUrl);
        Assert.Equal("cres_b2", r2.Values["cres"]);
        Assert.Equal("sess_b2", r2.Values["threeDSSessionData"]);
    }

    [Fact]
    public async Task Cluster14StarlingPollsReadyAndSubmitsAttempt()
    {
        var statusPolls = 0;
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/starling/start")
                return new(200, "text/html", """<input id="3ds-server-trans-id" value="st_tx_1" />""");
            if (req.Path == "/3ds/v2/challenge-browser/status")
            {
                statusPolls++;
                return new(200, "text/plain", statusPolls == 1 ? "WAITING" : "READY_TO_SUBMIT");
            }
            if (req.Path == "/3ds/v2/challenge-browser/attempt")
                return new(200, "text/html", """<form action="https://merchant.test/starling"><input name="cres" value="cres_starling" /></form>""");
            if (req.Path == "/starling/missing")
                return new(200, "text/html", "<html>no id</html>");
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);

        var res = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://3dsecure.starlingbank.com/starling/start", null, ct: default);
        Assert.True(res.Ok, res.Error);
        Assert.Equal("14_starling", res.Cluster);
        Assert.Equal("https://merchant.test/starling", res.ActionUrl);
        Assert.Equal("cres_starling", res.Values["cres"]);
        Assert.Equal(2, statusPolls);

        var fb = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://3dsecure.starlingbank.com/starling/missing", null, ct: default);
        Assert.False(fb.Ok);
        Assert.True(fb.RequiresInteractiveVerification);
    }

    [Fact]
    public async Task Cluster15EnfuceWaitsForWebSocketOkThenDispatchesPaSubmit()
    {
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/enfuce/start")
                return new(200, "text/html", """<script>var ws = new WebSocket("wss://3ds-a.live.ext.prod.enfuce.com/ws/jsess_42");</script>""");
            if (req.Path == "/acs/challengedispatcher")
                return new(200, "text/html", """<form name="CResForm"><input name="cres" value="cres_enfuce" /></form>""");
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);
        string? seenWsUrl = null;
        string? seenJsid = null;

        var res = await CheckoutComAcsHandlers.ExecuteAsync(
            ctx,
            "https://3ds-b.live.ext.prod.enfuce.com/enfuce/start",
            null,
            ct: default,
            webSocketClient: (wsUrl, jsid, _) =>
            {
                seenWsUrl = wsUrl;
                seenJsid = jsid;
                return Task.FromResult<string?>("OK");
            });

        Assert.True(res.Ok, res.Error);
        Assert.Equal("15_enfuce", res.Cluster);
        Assert.Equal("wss://3ds-a.live.ext.prod.enfuce.com/ws/jsess_42", seenWsUrl);
        Assert.Equal("jsess_42", seenJsid);
        Assert.Equal("cres_enfuce", res.Values["cres"]);
        var dispReq = Assert.Single(server.Requests, r => r.Path == "/acs/challengedispatcher");
        var dispJson = JObject.Parse(dispReq.Body);
        Assert.Equal("pa.submit", dispJson["formaction"]?.ToString());
        Assert.Equal("jsess_42", dispJson["jsessionid"]?.ToString());
    }

    [Fact]
    public async Task Cluster16MarqetaPollsNon200OobUrlThenPostsAutoSubmit()
    {
        var polls = 0;
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/marqeta/start")
            {
                return new(200, "text/html", """
                    <script>var oobPollUrl = "/marqeta/oob";</script>
                    <form id="MainForm" action="/marqeta/submit">
                      <input name="tx" value="mq_1" />
                      <input name="submit" value="Go" />
                    </form>
                    """);
            }
            if (req.Path == "/marqeta/oob")
            {
                polls++;
                return polls == 1 ? new(202, "application/json", "{}") : new(200, "application/json", "{}");
            }
            if (req.Path == "/marqeta/submit")
                return new(200, "text/html", """<form id="CResForm" action="https://merchant.test/mq"><input name="cres" value="cres_mq" /></form>""");
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);
        var res = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://authentication-acs.marqeta.com/marqeta/start", null, ct: default);

        Assert.True(res.Ok, res.Error);
        Assert.Equal("16_marqeta", res.Cluster);
        Assert.Equal("https://merchant.test/mq", res.ActionUrl);
        Assert.Equal("cres_mq", res.Values["cres"]);
        Assert.Equal(2, polls);
        var step3 = Assert.Single(server.Requests, r => r.Path == "/marqeta/submit");
        Assert.Contains("autoSubmit=true", step3.Body);
        Assert.DoesNotContain("submit=Go", step3.Body);
    }

    [Fact]
    public async Task Cluster17AmexRunsGravityAcs3ds1AndDefers3ds2CreqToFallback()
    {
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/amex/start")
                return new(200, "text/html", """<form><input name="PaReq" value="pareq_amex" /><input name="MD" value="md_amex" /></form>""");
            if (req.Path == "/GravityACS/payauth")
                return new(200, "application/json", "{\"sessionData\":\"sd_amex\"}");
            if (req.Path == "/GravityACS/response")
                return new(200, "text/html", """<form><input name="PaRes" value="pares_amex" /><input name="MD" value="overwritten" /></form>""");
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);

        var ok = await CheckoutComAcsHandlers.ExecuteAsync(
            ctx, "https://acs-safekey.americanexpress.com/amex/start",
            new Dictionary<string, string> { ["PaReq"] = "pareq_amex", ["MD"] = "md_amex" }, ct: default);
        Assert.True(ok.Ok, ok.Error);
        Assert.Equal("17_amex", ok.Cluster);
        Assert.Equal("pares_amex", ok.Values["PaRes"]);
        Assert.Equal("md_amex", ok.Values["MD"]);

        var fb = await CheckoutComAcsHandlers.ExecuteAsync(
            ctx, "https://acs-safekey.americanexpress.com/amex/start",
            new Dictionary<string, string> { ["creq"] = "creq_3ds2" }, ct: default);
        Assert.False(fb.Ok);
        Assert.True(fb.RequiresInteractiveVerification);
    }

    [Fact]
    public async Task Cluster18TouchtechPaymentsRoutesSelectPollConfirmAndRevolutOverride()
    {
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/ttp/wise")
                return new(200, "text/html", "<html><head><title>Wise</title></head><script>token: \"ttp_1\"</script></html>");
            if (req.Path == "/ttp/monese-revolut")
                return new(200, "text/html", "<html><head><title>Revolut</title></head><body>Monese <script>token: \"ttp_1\"</script></body></html>");
            if (req.Path == "/ttp/monese-only")
                return new(200, "text/html", "<html><head><title>Monese</title></head><body>Monese <script>token: \"ttp_1\"</script></body></html>");
            if (req.Path == "/api/v1/:select")
                return new(200, "application/json", "{\"status\":\"ok\"}");
            if (req.Path == "/poll")
                return new(200, "application/json", "{\"status\":\"success\",\"authToken\":\"auth_ttp_1\"}");
            if (req.Path == "/v1/confirmTransaction")
                return new(200, "application/json", "{\"Response\":\"pares_ttp_1\"}");
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);

        var wise = await CheckoutComAcsHandlers.ExecuteAsync(
            ctx, "https://idcheck.acs.touchtechpayments.com/ttp/wise",
            new Dictionary<string, string> { ["MD"] = "md_ttp" }, ct: default);
        Assert.True(wise.Ok, wise.Error);
        Assert.Equal("pares_ttp_1", wise.Values["PaRes"]);
        Assert.Equal("md_ttp", wise.Values["MD"]);
        Assert.Contains(server.Requests, r => r.Path == "/api/v1/:select");

        // Monese + Revolut title stays headless
        var rev = await CheckoutComAcsHandlers.ExecuteAsync(
            ctx, "https://verifiedbyvisa.acs.touchtechpayments.com/ttp/monese-revolut",
            new Dictionary<string, string> { ["MD"] = "md_rev" }, ct: default);
        Assert.True(rev.Ok, rev.Error);
        Assert.Equal("pares_ttp_1", rev.Values["PaRes"]);

        // Monese without Revolut falls back
        var mon = await CheckoutComAcsHandlers.ExecuteAsync(
            ctx, "https://idcheck.acs.touchtechpayments.com/ttp/monese-only", null, ct: default);
        Assert.False(mon.Ok);
        Assert.True(mon.RequiresInteractiveVerification);
    }

    [Fact]
    public async Task Cluster19CardinalHandlesProcessRiskAndBiometricOobAndFallback()
    {
        var oobPolls = 0;
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/cardinal/risk")
            {
                return new(200, "text/html", """
                    <form action="/Api/NextStep/ProcessRisk">
                      <input name="TransactionId" value="c_tx_1" />
                      <input name="IssuerId" value="c_iss_1" />
                    </form>
                    """);
            }
            if (req.Path == "/DeviceFingerprintWeb/V2/Browser/SaveBrowserData")
                return new(200, "application/json", "{}");
            if (req.Path == "/Api/NextStep/ProcessRisk")
                return new(200, "application/json", "{}");
            if (req.Path == "/api/nextstep/term")
                return new(200, "application/json", "{\"Payload\":{\"MD\":\"c_md\",\"PARes\":\"c_pares\"}}");

            if (req.Path == "/cardinal/oob")
            {
                return new(200, "text/html", """
                    <form id="ValidateOutOfBandCredentialForm">
                      <input name="TransactionId" value="c_tx_2" />
                      <input name="IssuerId" value="c_iss_2" />
                      <input name="ValidateReloadEnabled" value="true" />
                    </form>
                    """);
            }
            if (req.Path == "/Api/OutOfBand/ValidateOutOfBandCredential")
            {
                oobPolls++;
                return new(200, "application/json", oobPolls == 1 ? "{\"NextStep\":\"PENDING\"}" : "{\"NextStep\":\"TERM\"}");
            }
            if (req.Path == "/api/2_1_0/nextstep/term")
                return new(200, "application/json", "{\"Payload\":{\"NotificationUrl\":\"https://merchant.test/cardinal\",\"CRes\":\"c_cres\",\"ThreeDSSessionData\":\"c_sd\"}}");
            if (req.Path == "/cardinal/other")
                return new(200, "text/html", "<html>otp</html>");
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);

        var risk = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://authentication.cardinalcommerce.com/cardinal/risk", null, ct: default);
        Assert.True(risk.Ok, risk.Error);
        Assert.Equal("c_md", risk.Values["MD"]);
        Assert.Equal("c_pares", risk.Values["PaRes"]);
        var saveReq = Assert.Single(server.Requests, r => r.Path == "/DeviceFingerprintWeb/V2/Browser/SaveBrowserData");
        Assert.Equal("XMLHttpRequest", saveReq.Headers["X-Requested-With"]);
        Assert.Equal("FORM", saveReq.Headers["X-HTTP-Method-Override"]);
        Assert.Equal("c_tx_1", JObject.Parse(saveReq.Body)["ReferenceId"]?.ToString());

        var oob = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://authentication.cardinalcommerce.com/cardinal/oob", null, ct: default);
        Assert.True(oob.Ok, oob.Error);
        Assert.Equal("https://merchant.test/cardinal", oob.ActionUrl);
        Assert.Equal("c_cres", oob.Values["cres"]);
        Assert.Equal("c_sd", oob.Values["threeDSSessionData"]);
        Assert.Equal(2, oobPolls);
        var oobReq = server.Requests.First(r => r.Path == "/Api/OutOfBand/ValidateOutOfBandCredential");
        Assert.DoesNotContain("ValidateReloadEnabled", oobReq.Body);
        Assert.Contains("Type=BIOMETRIC", oobReq.Body);
        Assert.Contains("Origin=JAVASCRIPT_POLLING", oobReq.Body);

        var fb = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://authentication.cardinalcommerce.com/cardinal/other", null, ct: default);
        Assert.False(fb.Ok);
        Assert.True(fb.RequiresInteractiveVerification);
    }

    [Fact]
    public async Task UnknownHostFallbackAndGatewayWiringWorkCleanly()
    {
        using var server = new AcsLoopbackServer(req =>
        {
            if (req.Path == "/starling/start")
                return new(200, "text/html", """<input id="3ds-server-trans-id" value="gw_tx_1" />""");
            if (req.Path == "/3ds/v2/challenge-browser/status")
                return new(200, "text/plain", "READY_TO_SUBMIT");
            if (req.Path == "/3ds/v2/challenge-browser/attempt")
                return new(200, "text/html", """<form action="https://merchant.test/gw"><input name="cres" value="cres_gw" /></form>""");
            return new(404, "text/plain", "");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = NewAcsContext(http, server.BaseUrl);

        var unknown = await CheckoutComAcsHandlers.ExecuteAsync(ctx, "https://unknown-issuer.example/3ds", null, ct: default);
        Assert.False(unknown.Ok);
        Assert.True(unknown.RequiresInteractiveVerification);
        Assert.Equal("20_fallback", unknown.Cluster);
        Assert.Contains(ctx.Events, e => e.Name == "Click to finalize 3DS" && e.Type == "StatusInfo");
        Assert.Contains(ctx.Events, e => e.Type == "3DS verification required");

        // Gateway CompleteActionAsync routes known ACS host directly through CheckoutComAcsHandlers
        ctx.Session.Vars["checkoutcom.actionUrl"] = "https://3dsecure.starlingbank.com/starling/start";
        var gwRes = await new CheckoutComGateway().CompleteActionAsync(ctx, string.Empty, default);
        Assert.True(gwRes.Ok, gwRes.Error);
        Assert.Equal("https://merchant.test/gw", gwRes.GatewayReference);
        Assert.Equal("cres_gw", gwRes.Fields["cres"]);
    }
}
