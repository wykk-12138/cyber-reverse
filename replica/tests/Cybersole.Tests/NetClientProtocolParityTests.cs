using System.Buffers.Binary;
using System.IO.Compression;
using System.Net;
using System.Net.Security;
using System.Net.Sockets;
using System.Security.Authentication;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using Cybersole.Http;
using Cybersole.Http.Compression;
using Cybersole.Http.Content;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Xunit;
using ZstdSharp;

namespace Cybersole.Tests;

/// <summary>
/// Batch 3C Part 1 verification: AngleSharp <see cref="HtmlFormDom"/> DOM parsing,
/// <see cref="ContentEncodingCodec"/> (gzip/deflate/br/zstd + reverse-order multi-encoding + outbound compress),
/// <see cref="BouncyH2Client"/>/<see cref="BouncyHttpClient"/> zstd decoding, and <see cref="NetClient"/>
/// non-evasion protocol parity (SChannel proxy &amp; pool keying, header replacement, outbound Content-Encoding,
/// <see cref="RequestOptions.Cookies"/> writeback, and single-layer redirect loop).
/// </summary>
public sealed class NetClientProtocolParityTests
{
    [Fact]
    public void HtmlFormDomHandlesEntitiesFormsControlsCheckboxesRadiosSelectsAndMalformedMarkup()
    {
        const string html = """
            <html>
              <head><title>  Verify &amp; Approve  </title></head>
              <body>
                <script id="__NEXT_DATA__" type="application/json">{"pk":"pk_live_1&2","id":"sess_\"99\""}</script>
                <div class="ignored">
                  <form id="wrong" action="/other"><input name="x" value="0" /></form>
                </div>
                <form id="challenge" name="authForm" method="post" action="/acs/submit?a=1&amp;b=2">
                  <input type="hidden" name="csrf" value="tok&#x27;123&quot;" />
                  <input type="text" name="ignored_disabled" value="nope" disabled />
                  <fieldset disabled>
                    <input type="hidden" name="inside_disabled_fieldset" value="nope2" />
                  </fieldset>
                  <input type="radio" name="channel" value="sms" />
                  <input type="radio" name="channel" value="app" checked />
                  <input type="checkbox" name="opt_unchecked" value="yes" />
                  <input type="checkbox" name="opt_default_checked" checked />
                  <input type="checkbox" name="opt_custom_checked" value="42" checked />
                  <select name="country">
                    <option value="US">United States</option>
                    <option value="GB" selected>United Kingdom</option>
                  </select>
                  <select name="fallback_select">
                    <option value="disabled_first" disabled>Disabled</option>
                    <option value="first_enabled">First Enabled</option>
                    <option value="second">Second</option>
                  </select>
                  <textarea name="notes">hello &amp; world</textarea>
                  <button type="button" name="btn_ignored" value="ignore">Ignore</button>
                  <button type="submit" name="action_btn" value="Approve">Approve</button>
                  <!-- unclosed div and p inside malformed HTML -->
                  <div class="tail"><p><span>still parsed
                </form>
              </body>
            </html>
            """;

        Assert.Equal("Verify & Approve", HtmlFormDom.ExtractTitle(html));
        Assert.Equal("{\"pk\":\"pk_live_1&2\",\"id\":\"sess_\\\"99\\\"\"}",
            HtmlFormDom.ExtractElementText(html, "script#__NEXT_DATA__"));

        var forms = HtmlFormDom.ExtractAllForms(html);
        Assert.Equal(2, forms.Count);

        var (action, inputs) = HtmlFormDom.ExtractForm(html, formName: "authForm", formId: "challenge");
        Assert.Equal("/acs/submit?a=1&b=2", action);
        Assert.Equal("tok'123\"", inputs["csrf"]);
        Assert.Equal("app", inputs["channel"]);
        Assert.False(inputs.ContainsKey("opt_unchecked"));
        Assert.Equal("on", inputs["opt_default_checked"]);
        Assert.Equal("42", inputs["opt_custom_checked"]);
        Assert.Equal("GB", inputs["country"]);
        Assert.Equal("first_enabled", inputs["fallback_select"]);
        Assert.Equal("hello & world", inputs["notes"]);
        Assert.Equal("Approve", inputs["action_btn"]);
        Assert.False(inputs.ContainsKey("btn_ignored"));
        Assert.False(inputs.ContainsKey("ignored_disabled"));
        Assert.False(inputs.ContainsKey("inside_disabled_fieldset"));

        // Attribute lookup handles unescaped IDs with colons and leading digits
        const string colonIdHtml = "<input id=\"3ds-server-trans-id\" value=\"tx_1\" />" +
                                   "<input id=\"j_id1:javax.faces.ViewState:0\" value=\"vs_0\" />";
        Assert.Equal("tx_1", HtmlFormDom.ExtractElementAttributeById(colonIdHtml, "3ds-server-trans-id", "value"));
        Assert.Equal("vs_0", HtmlFormDom.ExtractElementAttributeById(colonIdHtml, "j_id1:javax.faces.ViewState:0", "value"));
    }

    [Fact]
    public void ContentEncodingCodecRoundTripsAllEncodingsAndEnforcesReverseChainAndErrorContract()
    {
        var original = Encoding.UTF8.GetBytes("{\"step\":\"3ds\",\"ok\":true,\"note\":\"hello zstd + gzip + br\"}");

        foreach (var enc in new[] { "identity", "gzip", "x-gzip", "deflate", "zstd" })
        {
            var compressed = ContentEncodingCodec.Compress(original, enc);
            var restored = ContentEncodingCodec.Decompress(compressed, enc);
            Assert.Equal(original, restored);
        }

        // Brotli decode + zlib-wrapped deflate fallback
        byte[] brotliBytes;
        using (var ms = new MemoryStream())
        {
            using (var br = new BrotliStream(ms, CompressionLevel.Optimal, leaveOpen: true))
                br.Write(original, 0, original.Length);
            brotliBytes = ms.ToArray();
        }
        Assert.Equal(original, ContentEncodingCodec.Decompress(brotliBytes, "br"));

        byte[] zlibDeflateBytes;
        using (var ms = new MemoryStream())
        {
            using (var zlib = new ZLibStream(ms, CompressionLevel.Optimal, leaveOpen: true))
                zlib.Write(original, 0, original.Length);
            zlibDeflateBytes = ms.ToArray();
        }
        Assert.Equal(original, ContentEncodingCodec.Decompress(zlibDeflateBytes, "deflate"));

        // Chained "gzip, br": first gzip, then brotli. Decoding must apply reverse order: br then gzip.
        var gzipped = ContentEncodingCodec.Compress(original, "gzip");
        byte[] gzipThenBr;
        using (var ms = new MemoryStream())
        {
            using (var br = new BrotliStream(ms, CompressionLevel.Optimal, leaveOpen: true))
                br.Write(gzipped, 0, gzipped.Length);
            gzipThenBr = ms.ToArray();
        }
        Assert.Equal(original, ContentEncodingCodec.Decompress(gzipThenBr, "gzip, br"));

        // Wrong chain order ("br, gzip") fails strict Decompress
        Assert.ThrowsAny<Exception>(() => ContentEncodingCodec.Decompress(gzipThenBr, "br, gzip"));

        // Unsupported outbound encoder contract
        var ex = Assert.Throws<NotSupportedException>(() => ContentEncodingCodec.Compress(original, "br"));
        Assert.Equal("No encoder for Content-Encoding \"br\" (supported: gzip, deflate, zstd).", ex.Message);

        // Safe DecompressToString falls back gracefully when payload is invalid
        Assert.Equal("plain-not-zstd", ContentEncodingCodec.DecompressToString("plain-not-zstd"u8.ToArray(), "zstd"));
    }

    [Fact]
    public async Task BouncyHttpClientAndBouncyH2ClientAdvertiseAndDecodeZstd()
    {
        using var cert = CreateSelfSignedCert("127.0.0.1");
        const string expectedPayload = "{\"decoded\":\"zstd-ok\"}";
        var compressedPayload = ContentEncodingCodec.Compress(Encoding.UTF8.GetBytes(expectedPayload), "zstd");

        // 1) BouncyHttpClient (TLS 1.2 + HTTP/1.1)
        string? h1RequestText = null;
        using (var h1Listener = new TcpListener(IPAddress.Loopback, 0))
        {
            h1Listener.Start();
            var h1Port = ((IPEndPoint)h1Listener.LocalEndpoint).Port;

            var serverTask = Task.Run(async () =>
            {
                using var tcp = await h1Listener.AcceptTcpClientAsync();
                using var ssl = new SslStream(tcp.GetStream(), false);
                await ssl.AuthenticateAsServerAsync(new SslServerAuthenticationOptions
                {
                    ServerCertificate = cert,
                    EnabledSslProtocols = SslProtocols.Tls12,
                });

                h1RequestText = await ReadHttpHeaderBlockAsync(ssl);
                var hdr = $"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Encoding: zstd\r\nContent-Length: {compressedPayload.Length}\r\nConnection: close\r\n\r\n";
                await ssl.WriteAsync(Encoding.ASCII.GetBytes(hdr));
                await ssl.WriteAsync(compressedPayload);
                await ssl.FlushAsync();
            });

            using var h1 = new BouncyHttpClient();
            var res = await h1.GetAsync($"https://127.0.0.1:{h1Port}/zstd-h1");
            await serverTask.WaitAsync(TimeSpan.FromSeconds(5));

            Assert.Contains("Accept-Encoding: gzip, deflate, br, zstd", h1RequestText);
            Assert.Equal(200, res.StatusCode);
            Assert.Equal(expectedPayload, res.Body);
        }

        // 2) BouncyH2Client (TLS 1.2 + HTTP/2)
        Dictionary<string, string>? h2ReqHeaders = null;
        using (var h2Listener = new TcpListener(IPAddress.Loopback, 0))
        {
            h2Listener.Start();
            var h2Port = ((IPEndPoint)h2Listener.LocalEndpoint).Port;
            var clientDone = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);

            var serverTask = Task.Run(async () =>
            {
                using var tcp = await h2Listener.AcceptTcpClientAsync();
                using var ssl = new SslStream(tcp.GetStream(), false);
                await ssl.AuthenticateAsServerAsync(new SslServerAuthenticationOptions
                {
                    ServerCertificate = cert,
                    EnabledSslProtocols = SslProtocols.Tls12,
                    ApplicationProtocols = new List<SslApplicationProtocol> { SslApplicationProtocol.Http2 },
                });

                var prefaceBuf = new byte[Http2.Preface.Length];
                await ReadExactlyAsync(ssl, prefaceBuf);

                // Read client SETTINGS + HEADERS frames
                var headerBlock = new MemoryStream();
                while (true)
                {
                    var (type, flags, streamId, payload) = await Http2.ReadFrameAsync(ssl, CancellationToken.None);
                    if (type == Http2.Headers)
                    {
                        headerBlock.Write(payload);
                        if ((flags & Http2.FlagEndHeaders) != 0)
                            break;
                    }
                }
                h2ReqHeaders = DecodeRequestHpackHeaders(headerBlock.ToArray());

                // Server sends SETTINGS + HEADERS(:status=200, content-encoding=zstd) + DATA + END_STREAM
                await ssl.WriteAsync(Http2.Frame(Http2.Settings, 0, 0, Array.Empty<byte>()));
                var respHpack = EncodeSimpleResponseHeaders(200, ("content-encoding", "zstd"), ("content-type", "application/json"));
                await ssl.WriteAsync(Http2.Frame(Http2.Headers, Http2.FlagEndHeaders, 1, respHpack));
                await ssl.WriteAsync(Http2.Frame(Http2.Data, Http2.FlagEndStream, 1, compressedPayload));
                await ssl.FlushAsync();

                // Keep TLS stream open while BouncyH2Client replies with SETTINGS ACK and reads END_STREAM.
                await clientDone.Task.WaitAsync(TimeSpan.FromSeconds(5));
            });

            using var h2 = new BouncyH2Client();
            NetResponse res;
            try
            {
                res = await h2.SendAsync("GET", $"https://127.0.0.1:{h2Port}/zstd-h2");
            }
            finally
            {
                clientDone.TrySetResult();
            }
            await serverTask.WaitAsync(TimeSpan.FromSeconds(5));

            Assert.NotNull(h2ReqHeaders);
            Assert.Contains("zstd", h2ReqHeaders!["accept-encoding"], StringComparison.OrdinalIgnoreCase);
            Assert.Equal(200, res.StatusCode);
            Assert.Equal(expectedPayload, res.Body);
        }
    }

    [Fact]
    public async Task NetClientRoutesProxyPerPoolKeyAndKeepsActiveProfilesDistinct()
    {
        var seenProxyAuths = new List<string?>();
        var seenTargets = new List<string>();

        using var targetServer = new TinyServer((req, _) => (200, "{\"via\":\"proxy\"}"));
        using var proxyListener = new TcpListener(IPAddress.Loopback, 0);
        proxyListener.Start();
        var proxyPort = ((IPEndPoint)proxyListener.LocalEndpoint).Port;

        using var forwarderCts = new CancellationTokenSource();
        var proxyLoop = Task.Run(async () =>
        {
            while (!forwarderCts.IsCancellationRequested)
            {
                TcpClient client;
                try { client = await proxyListener.AcceptTcpClientAsync(forwarderCts.Token); }
                catch { break; }

                _ = Task.Run(async () =>
                {
                    using (client)
                    using (var stream = client.GetStream())
                    {
                        var rawReq = await ReadHttpHeaderBlockAsync(stream);
                        var lines = rawReq.Split("\r\n");
                        var firstLineParts = lines[0].Split(' ');
                        string? auth = null;
                        foreach (var l in lines.Skip(1))
                        {
                            if (l.StartsWith("Proxy-Authorization:", StringComparison.OrdinalIgnoreCase))
                                auth = l["Proxy-Authorization:".Length..].Trim();
                        }

                        if (string.IsNullOrEmpty(auth))
                        {
                            const string challenge =
                                "HTTP/1.1 407 Proxy Authentication Required\r\n" +
                                "Proxy-Authenticate: Basic realm=\"cyb-proxy\"\r\n" +
                                "Content-Length: 0\r\nConnection: close\r\n\r\n";
                            await stream.WriteAsync(Encoding.ASCII.GetBytes(challenge));
                            await stream.FlushAsync();
                            return;
                        }

                        lock (seenTargets)
                        {
                            seenTargets.Add(firstLineParts.Length >= 2 ? firstLineParts[1] : string.Empty);
                            seenProxyAuths.Add(auth);
                        }

                        const string respBody = "{\"proxied\":true}";
                        var resp = $"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {respBody.Length}\r\nConnection: close\r\n\r\n{respBody}";
                        await stream.WriteAsync(Encoding.ASCII.GetBytes(resp));
                        await stream.FlushAsync();
                    }
                });
            }
        });

        try
        {
            using var client = new NetClient();
            var rDirect = await client.GetAsync(targetServer.BaseUrl + "/direct", new RequestOptions { Retries = 0 });
            Assert.Equal(200, rDirect.StatusCode);

            var rProxied = await client.GetAsync(
                targetServer.BaseUrl + "/via-proxy",
                new RequestOptions { Proxy = $"http://user1:pass1@127.0.0.1:{proxyPort}", Retries = 0 });
            Assert.Equal(200, rProxied.StatusCode);
            Assert.Contains("proxied", rProxied.Body);

            var expectedAuth = "Basic " + Convert.ToBase64String(Encoding.UTF8.GetBytes("user1:pass1"));
            Assert.Single(seenProxyAuths);
            Assert.Equal(expectedAuth, seenProxyAuths[0]);
            Assert.Single(seenTargets);
            Assert.Equal(targetServer.BaseUrl + "/via-proxy", seenTargets[0]);

            // Distinct profile names even with multiple proxy pool entries under the same profile
            Assert.Single(client.ActiveProfiles);
            Assert.Contains("chrome", client.ActiveProfiles, StringComparer.OrdinalIgnoreCase);
        }
        finally
        {
            forwarderCts.Cancel();
            proxyListener.Stop();
            await Task.WhenAny(proxyLoop, Task.Delay(500));
        }
    }

    [Fact]
    public async Task NetClientReplacesCustomHeadersCompressesOutboundZstdAndSyncsCookies()
    {
        byte[]? seenBodyBytes = null;
        string? seenContentEncoding = null;
        Dictionary<string, string>? seenHeaders = null;
        var seenHeaderRawCounts = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);

        var port = FreePort();
        var baseUrl = $"http://127.0.0.1:{port}";
        using var listener = new HttpListener();
        listener.Prefixes.Add(baseUrl + "/");
        listener.Start();

        var serverTask = Task.Run(async () =>
        {
            for (var i = 0; i < 4; i++)
            {
                var ctx = await listener.GetContextAsync();
                using var ms = new MemoryStream();
                await ctx.Request.InputStream.CopyToAsync(ms);
                seenBodyBytes = ms.ToArray();

                seenHeaders = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
                seenHeaderRawCounts.Clear();
                foreach (string key in ctx.Request.Headers.AllKeys!)
                {
                    var vals = ctx.Request.Headers.GetValues(key) ?? Array.Empty<string>();
                    seenHeaderRawCounts[key] = vals.Length;
                    seenHeaders[key] = string.Join(", ", vals);
                }
                seenContentEncoding = ctx.Request.Headers["Content-Encoding"];

                if (ctx.Request.Url?.AbsolutePath == "/echo-zstd")
                {
                    var decoded = ContentEncodingCodec.Decompress(seenBodyBytes, "zstd");
                    ctx.Response.AddHeader("Set-Cookie", "sid=from_server; Path=/; HttpOnly");
                    ctx.Response.AddHeader("Content-Encoding", "zstd");
                    ctx.Response.StatusCode = 200;
                    var zstdOut = ContentEncodingCodec.Compress(decoded, "zstd");
                    await ctx.Response.OutputStream.WriteAsync(zstdOut);
                }
                else
                {
                    ctx.Response.AddHeader("Set-Cookie", "jar_cookie=persisted; Path=/");
                    ctx.Response.StatusCode = 200;
                    var okBytes = Encoding.UTF8.GetBytes(seenHeaders.GetValueOrDefault("Cookie") ?? "");
                    await ctx.Response.OutputStream.WriteAsync(okBytes);
                }
                ctx.Response.Close();
            }
        });

        using var http = new NetClient();

        // 1) Outbound zstd + header replace (not append) + Cookies injection + Set-Cookie writeback + zstd response
        var opts = new RequestOptions { OverrideHeaders = false };
        opts.Headers["User-Agent"] = "CustomAgent/1.0";
        opts.Headers["Accept"] = "application/vnd.cyb+json";
        opts.Headers["Content-Encoding"] = "zstd";
        opts.Cookies["session"] = "init_cookie";
        opts.Properties["Akamai"] = "1";

        var res1 = await http.PostJsonAsync(baseUrl + "/echo-zstd", "{\"item\":1}", opts);
        Assert.Equal(200, res1.StatusCode);
        Assert.Equal("{\"item\":1}", res1.Body);
        Assert.Equal("zstd", seenContentEncoding);
        Assert.Equal("CustomAgent/1.0", seenHeaders!["User-Agent"]);
        Assert.Equal("application/vnd.cyb+json", seenHeaders["Accept"]);
        Assert.Equal(1, seenHeaderRawCounts["User-Agent"]);
        Assert.Equal(1, seenHeaderRawCounts["Accept"]);
        Assert.False(seenHeaders.ContainsKey("Akamai"));
        Assert.Contains("session=init_cookie", seenHeaders["Cookie"]);
        Assert.Equal("from_server", res1.Cookies["sid"]);
        Assert.Equal("from_server", opts.Cookies["sid"]);

        // 2) Jar cookie persists to subsequent request + request Cookies merges on top
        var opts2 = new RequestOptions();
        opts2.Cookies["extra"] = "v2";
        var res2 = await http.GetAsync(baseUrl + "/cookies", opts2);
        Assert.Contains("sid=from_server", res2.Body);
        Assert.Contains("extra=v2", res2.Body);
        Assert.Equal("persisted", opts2.Cookies["jar_cookie"]);

        // 3) Explicit Cookie header beats jar and RequestOptions.Cookies cleanly (no double Cookie header)
        var opts3 = new RequestOptions();
        opts3.Cookies["ignored"] = "x";
        opts3.Headers["Cookie"] = "manual=only_this";
        var res3 = await http.GetAsync(baseUrl + "/manual", opts3);
        Assert.Equal("manual=only_this", res3.Body);
        Assert.Equal(1, seenHeaderRawCounts["Cookie"]);

        // 4) Fourth ping so server loop completes cleanly + verify uncompressed error via unsupported encoding
        await http.GetAsync(baseUrl + "/done");
        await serverTask.WaitAsync(TimeSpan.FromSeconds(5));

        var badEncOpts = new RequestOptions();
        badEncOpts.Headers["Content-Encoding"] = "br";
        await Assert.ThrowsAsync<NotSupportedException>(() =>
            http.PostJsonAsync(baseUrl + "/never-sent", "{}", badEncOpts));
    }

    [Fact]
    public async Task NetClientSingleLayerRedirectsHandleMethodSwitchBodyPreservationPathsCookiesAndLimits()
    {
        var port = FreePort();
        var baseUrl = $"http://127.0.0.1:{port}";
        var hits = new List<(string Method, string PathAndQuery, string Body, string? Cookie, string? ContentType, string? ContentEncoding)>();

        using var listener = new HttpListener();
        listener.Prefixes.Add(baseUrl + "/");
        listener.Start();

        using var cts = new CancellationTokenSource();
        var acceptLoop = Task.Run(async () =>
        {
            while (!cts.IsCancellationRequested)
            {
                HttpListenerContext ctx;
                try { ctx = await listener.GetContextAsync(); }
                catch { break; }

                using var ms = new MemoryStream();
                await ctx.Request.InputStream.CopyToAsync(ms);
                var rawBytes = ms.ToArray();
                var bodyStr = string.Equals(ctx.Request.Headers["Content-Encoding"], "gzip", StringComparison.OrdinalIgnoreCase)
                    ? ContentEncodingCodec.DecompressToString(rawBytes, "gzip")
                    : Encoding.UTF8.GetString(rawBytes);

                var path = ctx.Request.Url?.AbsolutePath ?? "/";
                hits.Add((
                    ctx.Request.HttpMethod,
                    path,
                    bodyStr,
                    ctx.Request.Headers["Cookie"],
                    ctx.Request.ContentType,
                    ctx.Request.Headers["Content-Encoding"]));

                switch (path)
                {
                    case "/dir/start302":
                        ctx.Response.StatusCode = 302;
                        ctx.Response.RedirectLocation = "next"; // relative -> /dir/next
                        ctx.Response.AddHeader("Set-Cookie", "c1=v1; Path=/scoped-path");
                        break;
                    case "/dir/next":
                        ctx.Response.StatusCode = 302;
                        ctx.Response.RedirectLocation = $"/http://127.0.0.1:{port}/done"; // strips leading /http
                        ctx.Response.AddHeader("Set-Cookie", "c2=v2; Path=/");
                        break;
                    case "/done":
                        ctx.Response.StatusCode = 200;
                        await ctx.Response.OutputStream.WriteAsync("{\"finished\":true}"u8.ToArray());
                        break;
                    case "/start307":
                        ctx.Response.StatusCode = 307;
                        ctx.Response.RedirectLocation = "/keep307";
                        break;
                    case "/keep307":
                        ctx.Response.StatusCode = 200;
                        await ctx.Response.OutputStream.WriteAsync(Encoding.UTF8.GetBytes("kept:" + bodyStr));
                        break;
                    case "/loop":
                        ctx.Response.StatusCode = 302;
                        ctx.Response.RedirectLocation = "/loop";
                        break;
                }
                ctx.Response.Close();
            }
        });

        try
        {
            using var http = new NetClient();

            // 1) POST + gzip -> 302 relative -> GET /dir/next (drops body & Content-Encoding) -> /http strip -> /done + Set-Cookie carry
            hits.Clear();
            var opts302 = new RequestOptions { Retries = 0 };
            opts302.Headers["Content-Encoding"] = "gzip";
            var r302 = await http.PostJsonAsync(baseUrl + "/dir/start302", "{\"hello\":\"world\"}", opts302);

            Assert.Equal(200, r302.StatusCode);
            Assert.Equal(baseUrl + "/done", r302.Url.ToString());
            Assert.Equal(3, hits.Count);

            Assert.Equal("POST", hits[0].Method);
            Assert.Equal("{\"hello\":\"world\"}", hits[0].Body);
            Assert.Equal("gzip", hits[0].ContentEncoding);

            Assert.Equal("GET", hits[1].Method);
            Assert.Equal("/dir/next", hits[1].PathAndQuery);
            Assert.Equal(string.Empty, hits[1].Body);
            Assert.Null(hits[1].ContentEncoding);
            Assert.Contains("c1=v1", hits[1].Cookie);

            Assert.Equal("GET", hits[2].Method);
            Assert.Equal("/done", hits[2].PathAndQuery);
            Assert.Contains("c1=v1", hits[2].Cookie);
            Assert.Contains("c2=v2", hits[2].Cookie);
            Assert.Equal("v1", r302.Cookies["c1"]);
            Assert.Equal("v2", r302.Cookies["c2"]);
            Assert.Equal("v1", opts302.Cookies["c1"]);
            Assert.Equal("v2", opts302.Cookies["c2"]);

            // 2) POST -> 307 preserves POST method and FormUrlEncodedContent body
            hits.Clear();
            var r307 = await http.PostFormAsync(baseUrl + "/start307",
                new Dictionary<string, string> { ["k"] = "v307" },
                new RequestOptions { Retries = 0 });
            Assert.Equal(200, r307.StatusCode);
            Assert.Equal("kept:k=v307", r307.Body);
            Assert.Equal(2, hits.Count);
            Assert.Equal("POST", hits[0].Method);
            Assert.Equal("POST", hits[1].Method);
            Assert.Equal("k=v307", hits[1].Body);

            // 3) MaxRedirects <= 0 stops without following
            hits.Clear();
            var rDisabled = await http.GetAsync(baseUrl + "/dir/start302",
                new RequestOptions { MaxRedirects = 0, Retries = 0 });
            Assert.Equal(302, rDisabled.StatusCode);
            Assert.Single(hits);

            // 4) MaxRedirects exceeded throws TooManyRedirects NetException
            hits.Clear();
            var ex = await Assert.ThrowsAsync<NetException>(() =>
                http.GetAsync(baseUrl + "/loop", new RequestOptions { MaxRedirects = 2, Retries = 0 }));
            Assert.Contains("TooManyRedirects", ex.Message);
            Assert.Equal(3, hits.Count); // initial request + 2 hops before aborting on 3rd redirect
        }
        finally
        {
            cts.Cancel();
            listener.Close();
            await Task.WhenAny(acceptLoop, Task.Delay(500));
        }
    }

    private static X509Certificate2 CreateSelfSignedCert(string cn)
    {
        using var rsa = RSA.Create(2048);
        var req = new CertificateRequest($"CN={cn}", rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, false));
        using var ephemeral = req.CreateSelfSigned(DateTimeOffset.UtcNow.AddDays(-1), DateTimeOffset.UtcNow.AddDays(7));
        return new X509Certificate2(ephemeral.Export(X509ContentType.Pfx));
    }

    private static byte[] EncodeSimpleResponseHeaders(int status, params (string Name, string Value)[] headers)
    {
        using var ms = new MemoryStream();
        var statusStr = status.ToString();
        WriteHpackLiteral(ms, ":status", statusStr);
        foreach (var (name, value) in headers)
            WriteHpackLiteral(ms, name.ToLowerInvariant(), value);
        return ms.ToArray();
    }

    private static void WriteHpackLiteral(MemoryStream ms, string name, string value)
    {
        ms.WriteByte(0x00);
        var nBytes = Encoding.ASCII.GetBytes(name);
        ms.WriteByte((byte)nBytes.Length);
        ms.Write(nBytes);
        var vBytes = Encoding.ASCII.GetBytes(value);
        ms.WriteByte((byte)vBytes.Length);
        ms.Write(vBytes);
    }

    private static Dictionary<string, string> DecodeRequestHpackHeaders(byte[] block)
    {
        var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        var pos = 0;
        while (pos < block.Length)
        {
            var b = block[pos];
            if ((b & 0x80) != 0)
            {
                var idx = ReadHpackInt(block, ref pos, 7);
                if (idx == 2) headers[":method"] = "GET";
                else if (idx == 3) headers[":method"] = "POST";
                else if (idx == 7) headers[":scheme"] = "https";
                continue;
            }
            if ((b & 0xE0) == 0x20)
            {
                ReadHpackInt(block, ref pos, 5);
                continue;
            }

            var prefixBits = (b & 0x40) != 0 ? 6 : 4;
            var nameIdx = ReadHpackInt(block, ref pos, prefixBits);
            string name = nameIdx switch
            {
                0 => ReadHpackString(block, ref pos),
                1 => ":authority",
                4 => ":path",
                58 => "user-agent",
                _ => $"#{nameIdx}",
            };
            var value = ReadHpackString(block, ref pos);
            headers[name] = value;
        }
        return headers;
    }

    private static int ReadHpackInt(byte[] buf, ref int pos, int prefixBits)
    {
        var max = (1 << prefixBits) - 1;
        var val = buf[pos++] & max;
        if (val < max) return val;

        var shift = 0;
        while (pos < buf.Length)
        {
            var b = buf[pos++];
            val += (b & 0x7F) << shift;
            if ((b & 0x80) == 0) break;
            shift += 7;
        }
        return val;
    }

    private static string ReadHpackString(byte[] buf, ref int pos)
    {
        var first = buf[pos];
        var huffman = (first & 0x80) != 0;
        var len = ReadHpackInt(buf, ref pos, 7);
        var slice = buf.AsSpan(pos, len);
        pos += len;
        return huffman ? HpackHuffman.Decode(slice) : Encoding.ASCII.GetString(slice);
    }

    private static async Task<string> ReadHttpHeaderBlockAsync(Stream stream)
    {
        using var ms = new MemoryStream();
        var one = new byte[1];
        var tail = new byte[4];
        var count = 0;
        while (true)
        {
            var n = await stream.ReadAsync(one.AsMemory(0, 1));
            if (n <= 0) break;
            ms.WriteByte(one[0]);
            tail[0] = tail[1];
            tail[1] = tail[2];
            tail[2] = tail[3];
            tail[3] = one[0];
            count++;
            if (count >= 4 && tail[0] == '\r' && tail[1] == '\n' && tail[2] == '\r' && tail[3] == '\n')
                break;
        }
        return Encoding.ASCII.GetString(ms.ToArray());
    }

    private static async Task ReadExactlyAsync(Stream stream, byte[] buffer)
    {
        var offset = 0;
        while (offset < buffer.Length)
        {
            var n = await stream.ReadAsync(buffer.AsMemory(offset, buffer.Length - offset));
            if (n <= 0) throw new EndOfStreamException();
            offset += n;
        }
    }

    private static int FreePort()
    {
        using var tcp = new TcpListener(IPAddress.Loopback, 0);
        tcp.Start();
        return ((IPEndPoint)tcp.LocalEndpoint).Port;
    }
}
