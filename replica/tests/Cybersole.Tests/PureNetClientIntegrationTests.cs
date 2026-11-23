using System.Buffers.Binary;
using System.Collections.Concurrent;
using System.IO.Compression;
using System.Net;
using System.Net.Sockets;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using Cybersole.Http;
using Cybersole.Http.Compression;
using Cybersole.Http.Content;
using Cybersole.Http.Crypto;
using Cybersole.Http.Http3;
using Cybersole.Http.Profiles;
using Cybersole.Http.Protocol;
using Cybersole.Http.Quic;
using Cybersole.Http.Tls;
using Cybersole.Http.X509;
using Xunit;
using ZstdSharp;
using BcBc = Org.BouncyCastle.Tls.Crypto.Impl.BC;
using BcCrypto = Org.BouncyCastle.Tls.Crypto;
using BcSecurity = Org.BouncyCastle.Security;
using BcTls = Org.BouncyCastle.Tls;

namespace Cybersole.Tests;

public sealed class PureNetClientIntegrationTests
{
    private const string TestHost = "localhost";

    [Fact]
    public async Task NetClient_PureNetClient_ExecutesRealTls13Http2_And_Http11_WithCookiesRedirectsAndPins()
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole PureNetClient Root");
        using X509Certificate2 leafCert = CreateTestLeaf(leafKey, caCert, TestHost);

        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);

        DerCertificate parsedLeaf = DerCertificate.Parse(leafCert.RawData);
        string validPin = "sha256/" + parsedLeaf.PinSha256Base64;
        string wrongPin = "sha256/" + Convert.ToBase64String(new byte[32]);

        var h2Requests = new ConcurrentQueue<CapturedWireRequest>();
        var h1Requests = new ConcurrentQueue<CapturedWireRequest>();

        using var h2Listener = new TcpListener(IPAddress.Loopback, 0);
        h2Listener.Start();
        int h2Port = ((IPEndPoint)h2Listener.LocalEndpoint).Port;

        using var h1Listener = new TcpListener(IPAddress.Loopback, 0);
        h1Listener.Start();
        int h1Port = ((IPEndPoint)h1Listener.LocalEndpoint).Port;

        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(20));

        Task h2ServerTask = RunTls13H2ServerAsync(
            h2Listener,
            leafCert.RawData,
            caCert.RawData,
            leafKey.ExportPkcs8PrivateKey(),
            h1Port,
            h2Requests,
            cts.Token);

        Task h1ServerTask = RunTls13H1ServerAsync(
            h1Listener,
            leafCert.RawData,
            caCert.RawData,
            leafKey.ExportPkcs8PrivateKey(),
            h1Requests,
            cts.Token);

        try
        {
            var verifyOpts = new CertificateVerifyOptions
            {
                CustomRoots = roots,
                UseEmbeddedDefaultRoots = false,
            };

            using var client = new NetClient
            {
                Transport = TransportMode.PureNetClient,
                VerifyOptions = verifyOpts,
            };
            Assert.True(client.IsProductionTransport);
            Assert.False(client.IsExperimentalTransport);

            // 1. Default GET over real TLS 1.3 + HTTP/2 with off-wire Properties and Set-Cookie jar writeback
            var defaultOpts = new RequestOptions { Retries = 0 };
            defaultOpts.Properties["Akamai"] = "1";
            NetResponse getResp = await client.GetAsync($"https://{TestHost}:{h2Port}/default-get", defaultOpts, cts.Token);
            Assert.Equal(200, getResp.StatusCode);
            Assert.Equal("h2", getResp.Protocol);
            Assert.Equal("h2-get-ok", getResp.Body);
            Assert.Equal("pure_h2_sid", getResp.Cookies["sid"]);
            Assert.Equal("pure_h2_sid", defaultOpts.Cookies["sid"]);

            CapturedWireRequest wireGet = Assert.Single(h2Requests, r => r.Path == "/default-get");
            Assert.True(wireGet.HasHeader("user-agent"));
            Assert.True(wireGet.HasHeader("sec-ch-ua"));
            Assert.False(wireGet.HasHeader("akamai"));

            // 2. OverrideHeaders POST over TLS 1.3 + HTTP/2 (defaults suppressed, Properties off-wire, JSON body exact)
            var overrideOpts = new RequestOptions { OverrideHeaders = true, Retries = 0 };
            overrideOpts.Headers["x-custom-token"] = "pure-xyz";
            overrideOpts.Properties["Akamai"] = "secret";
            NetResponse postResp = await client.PostBodyAsync(
                $"https://{TestHost}:{h2Port}/override-post",
                new StringBody("{\"item\":42}", "application/json"),
                overrideOpts,
                cts.Token);
            Assert.Equal(200, postResp.StatusCode);
            Assert.Equal("h2", postResp.Protocol);
            Assert.Equal("{\"item\":42}", postResp.Body);

            CapturedWireRequest wirePost = Assert.Single(h2Requests, r => r.Path == "/override-post");
            Assert.Equal("POST", wirePost.Method);
            Assert.Equal("pure-xyz", wirePost.FirstHeader("x-custom-token"));
            Assert.False(wirePost.HasHeader("sec-ch-ua"));
            Assert.False(wirePost.HasHeader("accept-language"));
            Assert.False(wirePost.HasHeader("sec-fetch-site"));
            Assert.False(wirePost.HasHeader("akamai"));

            // 3. Subsequent request with empty RequestOptions automatically carries CookieJar cookie
            NetResponse cookieCheckResp = await client.GetAsync(
                $"https://{TestHost}:{h2Port}/cookie-check",
                new RequestOptions { Retries = 0 },
                cts.Token);
            Assert.Equal(200, cookieCheckResp.StatusCode);
            Assert.Contains("sid=pure_h2_sid", cookieCheckResp.Body, StringComparison.Ordinal);

            // 4. 302 redirect converts POST -> GET, drops body/Content-Type, and forwards Set-Cookie
            NetResponse r302 = await client.PostBodyAsync(
                $"https://{TestHost}:{h2Port}/start-302",
                new StringBody("drop-on-302", "application/json"),
                new RequestOptions { Retries = 0 },
                cts.Token);
            Assert.Equal(200, r302.StatusCode);
            Assert.Equal($"https://{TestHost}:{h2Port}/after-302", r302.Url.ToString());
            Assert.StartsWith("GET|", r302.Body, StringComparison.Ordinal);
            Assert.Contains("hop302=c302", r302.Body, StringComparison.Ordinal);
            Assert.EndsWith("|-", r302.Body, StringComparison.Ordinal);

            // 5. 307 redirect preserves POST method and body
            NetResponse r307 = await client.PostBodyAsync(
                $"https://{TestHost}:{h2Port}/start-307",
                new StringBody("keep-307", "text/plain"),
                new RequestOptions { Retries = 0 },
                cts.Token);
            Assert.Equal(200, r307.StatusCode);
            Assert.Equal("POST:keep-307", r307.Body);

            // 6. Cross-origin redirect (port h2Port -> port h1Port) strips Authorization and Cookie
            using (var xOriginClient = new NetClient { Transport = TransportMode.PureNetClient, VerifyOptions = verifyOpts })
            {
                var xOriginOpts = new RequestOptions { Retries = 0 };
                xOriginOpts.Headers["Authorization"] = "Bearer top-secret";
                xOriginOpts.Headers["Cookie"] = "manual=leak-check";
                NetResponse xOriginResp = await xOriginClient.GetAsync(
                    $"https://{TestHost}:{h2Port}/xorigin-start",
                    xOriginOpts,
                    cts.Token);
                Assert.Equal(200, xOriginResp.StatusCode);
                Assert.Equal("xorigin-arrived", xOriginResp.Body);

                CapturedWireRequest wireXOrigin = Assert.Single(h1Requests, r => r.Path == "/xorigin-target");
                Assert.False(wireXOrigin.HasHeader("authorization"));
                Assert.False(wireXOrigin.HasHeader("cookie"));
            }

            // 7. MaxRedirects exceeded throws TooManyRedirects NetException
            NetException tooManyEx = await Assert.ThrowsAsync<NetException>(() =>
                client.GetAsync(
                    $"https://{TestHost}:{h2Port}/loop",
                    new RequestOptions { MaxRedirects = 2, Retries = 0 },
                    cts.Token));
            Assert.Contains("TooManyRedirects", tooManyEx.Message, StringComparison.Ordinal);

            // 8. Real TLS 1.3 + HTTP/1.1 ALPN negotiation GET & POST
            NetResponse h1Get = await client.GetAsync(
                $"https://{TestHost}:{h1Port}/h1-get",
                new RequestOptions { Retries = 0 },
                cts.Token);
            Assert.Equal(200, h1Get.StatusCode);
            Assert.Equal("http/1.1", h1Get.Protocol);
            Assert.Equal("h1-tls13-ok", h1Get.Body);

            NetResponse h1Post = await client.PostBodyAsync(
                $"https://{TestHost}:{h1Port}/h1-post",
                new StringBody("h1-payload", "text/plain"),
                new RequestOptions { Retries = 0 },
                cts.Token);
            Assert.Equal(200, h1Post.StatusCode);
            Assert.Equal("http/1.1", h1Post.Protocol);
            Assert.Equal("POST:h1-payload", h1Post.Body);

            // 9. CertificatePinner matching pin succeeds; mismatch throws BadPinException
            var goodPinner = new CertificatePinner();
            goodPinner.AddPin(TestHost, validPin);
            using var pinnedOkClient = new NetClient
            {
                Transport = TransportMode.PureNetClient,
                VerifyOptions = new CertificateVerifyOptions
                {
                    CustomRoots = roots,
                    UseEmbeddedDefaultRoots = false,
                    Pinner = goodPinner,
                },
            };
            NetResponse pinOkResp = await pinnedOkClient.GetAsync(
                $"https://{TestHost}:{h2Port}/pin-ok",
                new RequestOptions { Retries = 0 },
                cts.Token);
            Assert.Equal(200, pinOkResp.StatusCode);
            Assert.Equal("pinned-ok", pinOkResp.Body);

            var badPinner = new CertificatePinner();
            badPinner.AddPin(TestHost, wrongPin);
            using var pinnedBadClient = new NetClient
            {
                Transport = TransportMode.PureNetClient,
                VerifyOptions = new CertificateVerifyOptions
                {
                    CustomRoots = roots,
                    UseEmbeddedDefaultRoots = false,
                    Pinner = badPinner,
                },
            };
            BadPinException badPinEx = await Assert.ThrowsAsync<BadPinException>(() =>
                pinnedBadClient.GetAsync(
                    $"https://{TestHost}:{h2Port}/pin-ok",
                    new RequestOptions { Retries = 0 },
                    cts.Token));
            Assert.Equal(HttpErrorKind.Certificate, HttpErrorClassifier.Classify(badPinEx));
        }
        finally
        {
            cts.Cancel();
            h2Listener.Stop();
            h1Listener.Stop();
            await Task.WhenAll(
                IgnoreCancelAsync(h2ServerTask),
                IgnoreCancelAsync(h1ServerTask));
        }
    }

    [Fact]
    public async Task NetClient_PureNetClient_ExecutesEndToEndQuicHttp3Loopback_And_Chrome150Profile()
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole PureNetClient H3 Root");
        using X509Certificate2 leafCert = CreateTestLeaf(leafKey, caCert, TestHost);

        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);
        var verifyOpts = new CertificateVerifyOptions
        {
            CustomRoots = roots,
            UseEmbeddedDefaultRoots = false,
        };

        await using var pair = new LoopbackQuicTransportPair();
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        var h3Server = new LoopbackQuicHttp3Server(pair.Server, leafKey, new[] { leafCert.RawData, caCert.RawData });
        Task serverTask = h3Server.RunAsync(cts.Token);

        try
        {
            Assert.True(TlsProfile.Chrome150.SupportsHttp3);
            Assert.True(ProfileRegistry.GetRequired("chrome_150").SupportsHttp3);

            int h3Connects = 0;
            using var client = new NetClient
            {
                Transport = TransportMode.PureNetClient,
                VerifyOptions = verifyOpts,
                PureClientOptions = new TlsHttpClientOptions
                {
                    CustomH3Connector = async (key, profile, ct) =>
                    {
                        Interlocked.Increment(ref h3Connects);
                        Assert.True(profile.SupportsHttp3);
                        var quicOpts = new QuicConnectionOptions
                        {
                            Host = key.Host,
                            Port = key.Port,
                            Profile = profile,
                            VerifyOptions = verifyOpts,
                            TransportOverride = pair.Client,
                            UseChaosInitialFrames = true,
                            ConnectTimeout = TimeSpan.FromSeconds(10),
                        };
                        return await Http3Connection.ConnectAsync(quicOpts, key, ct).ConfigureAwait(false);
                    },
                },
            };

            var h3Opts = new RequestOptions
            {
                Profile = TlsProfile.Chrome150,
                Retries = 0,
            };

            NetResponse rHello = await client.GetAsync($"https://{TestHost}/hello", h3Opts, cts.Token);
            Assert.Equal(200, rHello.StatusCode);
            Assert.Equal("h3", rHello.Protocol);
            Assert.Equal("hello-h3", rHello.Body);

            NetResponse rEcho = await client.PostJsonAsync(
                $"https://{TestHost}/echo",
                "{\"h3\":\"chrome_150\"}",
                new RequestOptions { Profile = TlsProfile.Chrome150, Retries = 0 },
                cts.Token);
            Assert.Equal(200, rEcho.StatusCode);
            Assert.Equal("h3", rEcho.Protocol);
            Assert.Equal("{\"h3\":\"chrome_150\"}", rEcho.Body);

            NetResponse rGzip = await client.GetAsync($"https://{TestHost}/compressed/gzip", new RequestOptions { Profile = TlsProfile.Chrome150, Retries = 0 }, cts.Token);
            Assert.Equal("compressed-payload-gzip-ok", rGzip.Body);
            Assert.Equal("h3", rGzip.Protocol);

            NetResponse rBr = await client.GetAsync($"https://{TestHost}/compressed/br", new RequestOptions { Profile = TlsProfile.Chrome150, Retries = 0 }, cts.Token);
            Assert.Equal("compressed-payload-br-ok", rBr.Body);
            Assert.Equal("h3", rBr.Protocol);

            NetResponse rZstd = await client.GetAsync($"https://{TestHost}/compressed/zstd", new RequestOptions { Profile = TlsProfile.Chrome150, Retries = 0 }, cts.Token);
            Assert.Equal("compressed-payload-zstd-ok", rZstd.Body);
            Assert.Equal("h3", rZstd.Protocol);

            // Multiplexed HTTP/3 connection reused across all 5 requests
            Assert.Equal(1, Volatile.Read(ref h3Connects));
        }
        finally
        {
            cts.Cancel();
            await h3Server.DisposeAsync();
            await pair.DisposeAsync();
            await IgnoreCancelAsync(serverTask);
        }
    }

    [Fact]
    public async Task ProtocolRacer_RacesHttp3AndHttp2_PrefersWinnerStaggersFallbackAndRespectsCooldown()
    {
        Assert.Equal(TimeSpan.FromMilliseconds(300), ProtocolRacer.DefaultRaceDelay);
        Assert.Equal(3, ProtocolRacer.DefaultMaxRaceAttempts);

        var clock = new FakeClock(new DateTimeOffset(2026, 11, 23, 12, 0, 0, TimeSpan.Zero));
        ClientProfile chrome150 = ProfileRegistry.GetRequired("chrome_150");

        // 1. Fast H3 wins before 300ms stagger -> TCP connector is never called
        {
            int h3Calls = 0;
            int tcpCalls = 0;
            var racer = new ProtocolRacer(new ProtocolRacerOptions
            {
                Clock = () => clock.UtcNow,
                CustomH3Connector = (key, _, _) =>
                {
                    Interlocked.Increment(ref h3Calls);
                    return Task.FromResult<IMultiplexedConnection>(new StubConnection(key, "HTTP/3", true));
                },
                CustomTcpTlsConnector = (key, _, _) =>
                {
                    Interlocked.Increment(ref tcpCalls);
                    return Task.FromResult<IMultiplexedConnection>(new StubConnection(key, "h2", true));
                },
            });

            ConnectionKey key = ConnectionKey.Create("https", "fast-h3.example", 443, chrome150.Name);
            await using IMultiplexedConnection winner = await racer.ConnectAsync(key, chrome150);
            Assert.Equal("HTTP/3", winner.ProtocolVersion);
            Assert.Equal(1, h3Calls);
            Assert.Equal(0, tcpCalls);
            Assert.Equal("h3", racer.GetPreferredProtocol(key));
        }

        // 2. Stalled H3 (>300ms) falls back to H2 after 300ms stagger, cancels H3, and disposes losing H3 if it finishes later
        {
            var losingH3Gate = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
            var losingH3Conn = new StubConnection(ConnectionKey.Create("https", "stalled-h3.example", 443, chrome150.Name), "HTTP/3", true);
            bool h3SawCancel = false;
            int tcpCalls = 0;

            var racer = new ProtocolRacer(new ProtocolRacerOptions
            {
                Clock = () => clock.UtcNow,
                CustomH3Connector = async (_, _, ct) =>
                {
                    using var reg = ct.Register(() => h3SawCancel = true);
                    await losingH3Gate.Task.ConfigureAwait(false);
                    return losingH3Conn;
                },
                CustomTcpTlsConnector = (key, _, _) =>
                {
                    Interlocked.Increment(ref tcpCalls);
                    return Task.FromResult<IMultiplexedConnection>(new StubConnection(key, "h2", true));
                },
            });

            ConnectionKey key = ConnectionKey.Create("https", "stalled-h3.example", 443, chrome150.Name);
            await using IMultiplexedConnection winner = await racer.ConnectAsync(key, chrome150);
            Assert.Equal("h2", winner.ProtocolVersion);
            Assert.Equal(1, tcpCalls);
            Assert.True(h3SawCancel);
            Assert.Equal("tcp", racer.GetPreferredProtocol(key));

            // Release stalled H3 task after TCP won -> losing H3 connection must be disposed automatically
            losingH3Gate.SetResult();
            await WaitUntilAsync(() => losingH3Conn.Disposed, CancellationToken.None);
            Assert.True(losingH3Conn.Disposed);
        }

        // 3. Failing H3 enters 5-minute cooldown; skips H3 during cooldown, retries after cooldown expires, and honors Alt-Svc
        {
            int h3Calls = 0;
            int tcpCalls = 0;
            bool failH3 = true;

            var racer = new ProtocolRacer(new ProtocolRacerOptions
            {
                Clock = () => clock.UtcNow,
                Http3Cooldown = TimeSpan.FromMinutes(5),
                CustomH3Connector = (key, _, _) =>
                {
                    Interlocked.Increment(ref h3Calls);
                    if (failH3)
                        throw new QuicException(1, isApplicationError: false, "simulated UDP blocked");
                    return Task.FromResult<IMultiplexedConnection>(new StubConnection(key, "HTTP/3", true));
                },
                CustomTcpTlsConnector = (key, _, _) =>
                {
                    Interlocked.Increment(ref tcpCalls);
                    return Task.FromResult<IMultiplexedConnection>(new StubConnection(key, "h2", true));
                },
            });

            ConnectionKey key = ConnectionKey.Create("https", "cooldown.example", 443, chrome150.Name);
            await using (IMultiplexedConnection c1 = await racer.ConnectAsync(key, chrome150))
                Assert.Equal("h2", c1.ProtocolVersion);
            Assert.Equal(1, h3Calls);
            Assert.Equal(1, tcpCalls);
            Assert.True(racer.IsInHttp3Cooldown(key));

            // Subsequent connect within 5-minute cooldown skips H3 entirely
            clock.Advance(TimeSpan.FromMinutes(4));
            await using (IMultiplexedConnection c2 = await racer.ConnectAsync(key, chrome150))
                Assert.Equal("h2", c2.ProtocolVersion);
            Assert.Equal(1, h3Calls);
            Assert.Equal(2, tcpCalls);

            // Advance past 5-minute cooldown -> H3 is eligible and wins again
            clock.Advance(TimeSpan.FromMinutes(2));
            Assert.False(racer.IsInHttp3Cooldown(key));
            failH3 = false;
            racer.RecordAltSvc("cooldown.example", 443, "h3=\":443\"; ma=3600", key.ProxyKey);
            Assert.True(racer.HasAltSvcHttp3Hint("cooldown.example", 443, key.ProxyKey));

            await using (IMultiplexedConnection c3 = await racer.ConnectAsync(key, chrome150))
                Assert.Equal("HTTP/3", c3.ProtocolVersion);
            Assert.Equal(2, h3Calls);
            Assert.Equal(2, tcpCalls);
        }

        // 4. ForceHttp11 and non-SOCKS5 HTTP proxy disable H3 racing; SOCKS5 allows it
        {
            int h3Calls = 0;
            var racer = new ProtocolRacer(new ProtocolRacerOptions
            {
                CustomH3Connector = (key, _, _) =>
                {
                    Interlocked.Increment(ref h3Calls);
                    return Task.FromResult<IMultiplexedConnection>(new StubConnection(key, "HTTP/3", true));
                },
                CustomTcpTlsConnector = (key, _, _) =>
                    Task.FromResult<IMultiplexedConnection>(new StubConnection(key, key.ForceHttp11 ? "http/1.1" : "h2", !key.ForceHttp11)),
            });

            ConnectionKey forceH1Key = ConnectionKey.Create("https", "h1only.example", 443, chrome150.Name, forceHttp11: true);
            Assert.False(racer.CanAttemptHttp3(forceH1Key, chrome150));
            await using (IMultiplexedConnection cForceH1 = await racer.ConnectAsync(forceH1Key, chrome150))
                Assert.Equal("http/1.1", cForceH1.ProtocolVersion);
            Assert.Equal(0, h3Calls);

            var httpProxy = new ProxySpec(ProxyProtocolKind.Http, "127.0.0.1", 8080);
            ConnectionKey httpProxyKey = ConnectionKey.Create("https", "proxied.example", 443, chrome150.Name, httpProxy.CanonicalKey);
            Assert.False(racer.CanAttemptHttp3(httpProxyKey, chrome150, httpProxy));
            await using (IMultiplexedConnection cHttpProxy = await racer.ConnectAsync(httpProxyKey, chrome150, httpProxy))
                Assert.Equal("h2", cHttpProxy.ProtocolVersion);
            Assert.Equal(0, h3Calls);

            var socks5Proxy = new ProxySpec(ProxyProtocolKind.Socks5, "127.0.0.1", 1080);
            ConnectionKey socks5Key = ConnectionKey.Create("https", "proxied.example", 443, chrome150.Name, socks5Proxy.CanonicalKey);
            Assert.True(racer.CanAttemptHttp3(socks5Key, chrome150, socks5Proxy));
            await using (IMultiplexedConnection cSocks5 = await racer.ConnectAsync(socks5Key, chrome150, socks5Proxy))
                Assert.Equal("HTTP/3", cSocks5.ProtocolVersion);
            Assert.Equal(1, h3Calls);
        }
    }

    [Fact]
    public async Task OriginPool_ReusesMultiplexedH2_ExclusivelyChecksOutH1_AndRetriesOnStaleEof()
    {
        Assert.Equal(TimeSpan.FromSeconds(90), OriginPool.DefaultIdleTimeout);

        var clock = new FakeClock(new DateTimeOffset(2026, 11, 23, 12, 0, 0, TimeSpan.Zero));

        // 1. Multiplexed H2 shares connection until MaxConcurrentStreams, then opens a second
        {
            int h2Created = 0;
            var createdConns = new List<StubConnection>();
            await using var pool = new OriginPool(
                (key, _) =>
                {
                    int id = Interlocked.Increment(ref h2Created);
                    var conn = new StubConnection(key, "h2", supportsMultiplexing: true, maxConcurrentStreams: 2)
                    {
                        Id = id,
                    };
                    lock (createdConns)
                        createdConns.Add(conn);
                    return Task.FromResult<IMultiplexedConnection>(conn);
                },
                idleTimeout: OriginPool.DefaultIdleTimeout,
                clock: () => clock.UtcNow);

            ConnectionKey h2Key = ConnectionKey.Create("https", "mux.example", 443, "chrome_133");
            await using PooledConnectionLease l1 = await pool.CheckoutAsync(h2Key);
            Assert.False(l1.WasReused);

            await using PooledConnectionLease l2 = await pool.CheckoutAsync(h2Key);
            Assert.True(l2.WasReused);
            Assert.Same(l1.Connection, l2.Connection);

            // MaxConcurrentStreams == 2 saturated -> 3rd concurrent checkout opens a 2nd H2 connection
            await using PooledConnectionLease l3 = await pool.CheckoutAsync(h2Key);
            Assert.False(l3.WasReused);
            Assert.NotSame(l1.Connection, l3.Connection);
            Assert.Equal(2, h2Created);
        }

        // 2. HTTP/1.1 exclusive leasing + deterministic 90s idle eviction
        {
            int h1Created = 0;
            var h1Conns = new List<StubConnection>();
            await using var pool = new OriginPool(
                (key, _) =>
                {
                    int id = Interlocked.Increment(ref h1Created);
                    var conn = new StubConnection(key, "http/1.1", supportsMultiplexing: false, maxConcurrentStreams: 1)
                    {
                        Id = id,
                    };
                    lock (h1Conns)
                        h1Conns.Add(conn);
                    return Task.FromResult<IMultiplexedConnection>(conn);
                },
                idleTimeout: TimeSpan.FromSeconds(90),
                clock: () => clock.UtcNow);

            ConnectionKey h1Key = ConnectionKey.Create("http", "h1.example", 80, "chrome_133", forceHttp11: true);

            PooledConnectionLease lease1 = await pool.CheckoutAsync(h1Key);
            PooledConnectionLease lease2 = await pool.CheckoutAsync(h1Key);
            Assert.NotSame(lease1.Connection, lease2.Connection);
            Assert.Equal(2, h1Created);

            await lease1.DisposeAsync();
            await lease2.DisposeAsync();
            Assert.Equal(2, pool.PooledConnectionCount);

            // At +89s idle, connection is still reusable
            clock.Advance(TimeSpan.FromSeconds(89));
            Assert.Equal(0, await pool.PruneIdleAsync());
            await using (PooledConnectionLease lease3 = await pool.CheckoutAsync(h1Key))
            {
                Assert.True(lease3.WasReused);
                Assert.Equal(2, h1Created);
            }

            // Advance +91s -> both idle H1 connections exceed 90s idle timeout, get evicted & disposed
            clock.Advance(TimeSpan.FromSeconds(91));
            int pruned = await pool.PruneIdleAsync();
            Assert.Equal(2, pruned);
            Assert.True(h1Conns[0].Disposed);
            Assert.True(h1Conns[1].Disposed);
            Assert.Equal(0, pool.PooledConnectionCount);

            await using PooledConnectionLease lease4 = await pool.CheckoutAsync(h1Key);
            Assert.False(lease4.WasReused);
            Assert.Equal(3, h1Created);
        }

        // 3. Stale EOF / GOAWAY transparent retry vs non-retryable 500 & unsafe POST body
        {
            int created = 0;
            var queue = new Queue<Func<PureHttpRequest, Task<PureHttpResponse>>>();

            await using var pool = new OriginPool(
                (key, _) =>
                {
                    int id = Interlocked.Increment(ref created);
                    Func<PureHttpRequest, Task<PureHttpResponse>> handler = queue.Dequeue();
                    return Task.FromResult<IMultiplexedConnection>(
                        new StubConnection(key, "http/1.1", supportsMultiplexing: false, maxConcurrentStreams: 1, sendHandler: handler)
                        {
                            Id = id,
                        });
                },
                idleTimeout: TimeSpan.FromSeconds(90),
                clock: () => clock.UtcNow);

            ConnectionKey key = ConnectionKey.Create("https", "retry.example", 443, "chrome_133");

            // Prime conn #1 (succeeds once, then throws EndOfStreamException on reused GET), conn #2 succeeds
            int c1Calls = 0;
            queue.Enqueue(req =>
            {
                c1Calls++;
                if (c1Calls == 1)
                    return Task.FromResult(new PureHttpResponse { StatusCode = 200, HttpVersion = "http/1.1", Body = "primed"u8.ToArray() });
                throw new EndOfStreamException("stale idle EOF");
            });
            queue.Enqueue(_ => Task.FromResult(new PureHttpResponse { StatusCode = 200, HttpVersion = "http/1.1", Body = "retried-ok"u8.ToArray() }));

            PureHttpResponse primedResp = await pool.SendWithRetryAsync(key, new PureHttpRequest { Method = "GET", Uri = new Uri("https://retry.example/prime") });
            Assert.Equal("primed", Encoding.UTF8.GetString(primedResp.Body));

            PureHttpResponse retriedGet = await pool.SendWithRetryAsync(key, new PureHttpRequest { Method = "GET", Uri = new Uri("https://retry.example/get") });
            Assert.Equal(200, retriedGet.StatusCode);
            Assert.Equal("retried-ok", Encoding.UTF8.GetString(retriedGet.Body));
            Assert.Equal(2, created);
        }

        // Isolated GOAWAY retry, HTTP 500 no-retry, and POST body non-retry assertions
        {
            int muxCreated = 0;
            int conn2Sends = 0;
            await using var muxPool = new OriginPool(
                (key, _) =>
                {
                    int id = Interlocked.Increment(ref muxCreated);
                    int calls = 0;
                    return Task.FromResult<IMultiplexedConnection>(
                        new StubConnection(key, "h2", supportsMultiplexing: true, maxConcurrentStreams: 100, sendHandler: req =>
                        {
                            calls++;
                            if (id == 1 && calls == 1)
                                return Task.FromResult(new PureHttpResponse { StatusCode = 200, HttpVersion = "HTTP/2.0", Body = "init"u8.ToArray() });
                            if (id == 1 && calls == 2)
                                throw new Http2Exception(0, isStreamReset: false, "HTTP/2 peer sent GOAWAY (lastStreamId=1, error=0x0).", retryable: true);

                            conn2Sends++;
                            if (req.Uri.AbsolutePath == "/status-500")
                                return Task.FromResult(new PureHttpResponse { StatusCode = 500, HttpVersion = "HTTP/2.0", Body = "err-500-body"u8.ToArray() });
                            if (req.Uri.AbsolutePath == "/unsafe-post-eof")
                                throw new EndOfStreamException("eof after post body");
                            return Task.FromResult(new PureHttpResponse { StatusCode = 200, HttpVersion = "HTTP/2.0", Body = req.Body.ToArray() });
                        })
                        { Id = id });
                },
                clock: () => clock.UtcNow);

            ConnectionKey k = ConnectionKey.Create("https", "goaway.example", 443, "chrome_133");
            await muxPool.SendWithRetryAsync(k, new PureHttpRequest { Method = "GET", Uri = new Uri("https://goaway.example/init") });

            // Reused conn #1 throws GOAWAY on POST with body -> retries cleanly on conn #2
            PureHttpResponse goawayPost = await muxPool.SendWithRetryAsync(k, new PureHttpRequest
            {
                Method = "POST",
                Uri = new Uri("https://goaway.example/order"),
                Body = "order-payload"u8.ToArray(),
            });
            Assert.Equal("order-payload", Encoding.UTF8.GetString(goawayPost.Body));
            Assert.Equal(2, muxCreated);
            Assert.Equal(1, conn2Sends);

            // HTTP 500 does NOT retry
            PureHttpResponse resp500 = await muxPool.SendWithRetryAsync(k, new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri("https://goaway.example/status-500"),
            });
            Assert.Equal(500, resp500.StatusCode);
            Assert.Equal("err-500-body", Encoding.UTF8.GetString(resp500.Body));
            Assert.Equal(2, conn2Sends);
            Assert.Equal(2, muxCreated);

            // Reused non-idempotent POST with body throwing EndOfStreamException does NOT retry/resend body
            int sendsBeforePostEof = conn2Sends;
            await Assert.ThrowsAsync<EndOfStreamException>(() => muxPool.SendWithRetryAsync(k, new PureHttpRequest
            {
                Method = "POST",
                Uri = new Uri("https://goaway.example/unsafe-post-eof"),
                Body = "do-not-duplicate"u8.ToArray(),
            }));
            Assert.Equal(sendsBeforePostEof + 1, conn2Sends);
            Assert.Equal(2, muxCreated);
        }
    }

    [Fact]
    public async Task TlsClientCache_Enforces4096Capacity_600sEviction_AndOptionDefaults()
    {
        var defaults = new TlsHttpClientOptions();
        Assert.Equal("chrome_133", defaults.ProfileName);
        Assert.Equal(TimeSpan.FromSeconds(30), defaults.ConnectTimeout);
        Assert.Equal(TimeSpan.FromSeconds(30), defaults.RequestTimeout);
        Assert.Equal(TimeSpan.FromSeconds(90), defaults.IdleTimeout);
        Assert.Equal(256L * 1024 * 1024, defaults.MaxResponseBodyBytes);
        Assert.Equal(10, defaults.MaxRedirects);
        Assert.False(defaults.RandomExtensionOrder);
        Assert.False(defaults.DisableSessionTickets);
        Assert.False(defaults.ForceHttp11);
        Assert.False(defaults.DisableHttp3);
        Assert.False(defaults.InsecureSkipVerify);
        Assert.True(defaults.UseCookieJar);

        Assert.Equal(4096, TlsClientCache.DefaultMaxCapacity);
        Assert.Equal(TimeSpan.FromSeconds(600), TlsClientCache.DefaultIdleEvictionTimeout);

        var clock = new FakeClock(new DateTimeOffset(2026, 11, 23, 12, 0, 0, TimeSpan.Zero));
        await using var cache = new TlsClientCache(clock: () => clock.UtcNow);
        Assert.Equal(4096, cache.MaxCapacity);
        Assert.Equal(TimeSpan.FromSeconds(600), cache.IdleEvictionTimeout);

        // SessionCache ownership based on DisableSessionTickets
        TlsHttpClient withTickets = cache.GetOrCreate(new TlsHttpClientOptions { PinScope = "tickets-on" });
        Assert.NotNull(withTickets.SessionCache);
        Assert.Equal(32, withTickets.SessionCache!.Capacity);

        TlsHttpClient withoutTickets = cache.GetOrCreate(new TlsHttpClientOptions { DisableSessionTickets = true, PinScope = "tickets-off" });
        Assert.Null(withoutTickets.SessionCache);

        // Reset into fresh cache for exact 4096-entry LRU capacity test
        await using var capCache = new TlsClientCache(clock: () => clock.UtcNow);
        var clients = new TlsHttpClient[4096];
        for (int i = 0; i < 4096; i++)
        {
            clients[i] = capCache.GetOrCreate(new TlsHttpClientOptions { PinScope = $"slot-{i}" });
        }
        Assert.Equal(4096, capCache.Count);

        // Touch slot-0 so slot-1 becomes LRU tail
        Assert.Same(clients[0], capCache.GetOrCreate(new TlsHttpClientOptions { PinScope = "slot-0" }));

        // Insert 4097th entry -> slot-1 evicted & disposed, slot-0 preserved
        TlsHttpClient extra = capCache.GetOrCreate(new TlsHttpClientOptions { PinScope = "slot-4096" });
        Assert.Equal(4096, capCache.Count);
        Assert.True(clients[1].IsDisposed);
        Assert.False(clients[0].IsDisposed);
        Assert.Same(clients[0], capCache.GetOrCreate(new TlsHttpClientOptions { PinScope = "slot-0" }));
        Assert.False(extra.IsDisposed);

        // Deterministic 600s idle eviction
        clock.Advance(TimeSpan.FromSeconds(599));
        Assert.Equal(0, await capCache.EvictIdleAsync());
        Assert.Equal(4096, capCache.Count);

        clock.Advance(TimeSpan.FromSeconds(2)); // total 601s idle
        int evicted = await capCache.EvictIdleAsync();
        Assert.Equal(4096, evicted);
        Assert.Equal(0, capCache.Count);
        Assert.True(clients[0].IsDisposed);
        Assert.True(extra.IsDisposed);

        TlsHttpClient recreated = capCache.GetOrCreate(new TlsHttpClientOptions { PinScope = "slot-0" });
        Assert.NotSame(clients[0], recreated);
        Assert.Equal(1, capCache.Count);
    }

    [Fact]
    public void NetClient_CompatibilityPins_Preserved()
    {
        using var client = new NetClient();
        Assert.Equal(TransportMode.SChannel, client.Transport);

        Assert.Equal(0, (int)TransportMode.SChannel);
        Assert.Equal(1, (int)TransportMode.BouncyH2);
        Assert.Equal(2, (int)TransportMode.BouncyHttp11);
        Assert.Equal(3, (int)TransportMode.OwnTls);
        Assert.Equal(4, (int)TransportMode.PureNetClient);

        var matrix = new (TransportMode Mode, bool ExpectedProduction, bool ExpectedExperimental)[]
        {
            (TransportMode.SChannel, true, false),
            (TransportMode.PureNetClient, true, false),
            (TransportMode.BouncyH2, false, true),
            (TransportMode.BouncyHttp11, false, true),
            (TransportMode.OwnTls, false, true),
        };

        foreach ((TransportMode mode, bool expectedProd, bool expectedExp) in matrix)
        {
            client.Transport = mode;
            Assert.Equal(expectedProd, client.IsProductionTransport);
            Assert.Equal(expectedExp, client.IsExperimentalTransport);
        }

        Assert.Equal(3, TlsProfile.All.Count);
        Assert.Same(TlsProfile.Chrome, TlsProfile.All[0]);
        Assert.Same(TlsProfile.Firefox, TlsProfile.All[1]);
        Assert.Same(TlsProfile.Safari, TlsProfile.All[2]);

        Assert.Same(TlsProfile.Chrome, TlsProfile.ByName("chrome_131"));
        Assert.Same(TlsProfile.Chrome150, TlsProfile.ByName("chrome_150"));
        Assert.False(TlsProfile.Chrome.SupportsHttp3);
        Assert.True(TlsProfile.Chrome150.SupportsHttp3);
    }

    // ---- Test Support Infrastructure ----

    private sealed class FakeClock
    {
        private DateTimeOffset _utcNow;
        private readonly object _gate = new();

        public FakeClock(DateTimeOffset initialUtc) => _utcNow = initialUtc;

        public DateTimeOffset UtcNow
        {
            get { lock (_gate) return _utcNow; }
        }

        public void Advance(TimeSpan delta)
        {
            lock (_gate) _utcNow += delta;
        }
    }

    private sealed class StubConnection : IMultiplexedConnection
    {
        private readonly Func<PureHttpRequest, Task<PureHttpResponse>>? _sendHandler;
        private int _activeStreams;
        private int _disposed;

        public StubConnection(
            ConnectionKey key,
            string protocolVersion,
            bool supportsMultiplexing,
            int maxConcurrentStreams = 100,
            Func<PureHttpRequest, Task<PureHttpResponse>>? sendHandler = null)
        {
            Key = key;
            ProtocolVersion = protocolVersion;
            SupportsMultiplexing = supportsMultiplexing;
            MaxConcurrentStreams = maxConcurrentStreams;
            _sendHandler = sendHandler;
        }

        public int Id { get; init; }
        public string ProtocolVersion { get; }
        public ConnectionKey Key { get; }
        public bool IsUsable => Volatile.Read(ref _disposed) == 0;
        public bool Disposed => Volatile.Read(ref _disposed) != 0;
        public bool SupportsMultiplexing { get; }
        public int MaxConcurrentStreams { get; }
        public int ActiveStreams => Volatile.Read(ref _activeStreams);
        public DateTimeOffset LastUsedUtc { get; private set; } = DateTimeOffset.UtcNow;

        public bool CanAcceptNewStream() => IsUsable && ActiveStreams < MaxConcurrentStreams;

        public async Task<PureHttpResponse> SendAsync(PureHttpRequest request, CancellationToken cancellationToken = default)
        {
            LastUsedUtc = DateTimeOffset.UtcNow;
            Interlocked.Increment(ref _activeStreams);
            try
            {
                if (_sendHandler is not null)
                    return await _sendHandler(request).ConfigureAwait(false);

                return new PureHttpResponse
                {
                    StatusCode = 200,
                    HttpVersion = ProtocolVersion,
                    Body = "ok"u8.ToArray(),
                };
            }
            finally
            {
                Interlocked.Decrement(ref _activeStreams);
            }
        }

        public ValueTask DisposeAsync()
        {
            Interlocked.Exchange(ref _disposed, 1);
            return ValueTask.CompletedTask;
        }
    }

    private sealed record CapturedWireRequest(
        string Method,
        string Path,
        List<PureHttpHeader> Headers,
        byte[] Body)
    {
        public bool HasHeader(string name)
            => Headers.Any(h => string.Equals(h.Name, name, StringComparison.OrdinalIgnoreCase));

        public string? FirstHeader(string name)
        {
            for (int i = 0; i < Headers.Count; i++)
            {
                if (string.Equals(Headers[i].Name, name, StringComparison.OrdinalIgnoreCase))
                    return Headers[i].Value;
            }
            return null;
        }

        public string JoinedHeaders(string name)
            => string.Join("; ", Headers
                .Where(h => string.Equals(h.Name, name, StringComparison.OrdinalIgnoreCase))
                .Select(h => h.Value));
    }

    private sealed class H2StreamAccum
    {
        public MemoryStream Headers { get; } = new();
        public MemoryStream Body { get; } = new();
        public bool HeadersComplete { get; set; }
        public bool EndStreamSeen { get; set; }
        public bool Dispatched { get; set; }
    }

    private static async Task RunTls13H2ServerAsync(
        TcpListener listener,
        byte[] leafDer,
        byte[] caDer,
        byte[] leafPkcs8,
        int h1Port,
        ConcurrentQueue<CapturedWireRequest> recorded,
        CancellationToken ct)
    {
        var activeHandlers = new List<Task>();
        while (!ct.IsCancellationRequested)
        {
            TcpClient accepted;
            try
            {
                accepted = await listener.AcceptTcpClientAsync(ct).ConfigureAwait(false);
            }
            catch
            {
                break;
            }

            Task handler = HandleH2ClientAsync(accepted, leafDer, caDer, leafPkcs8, h1Port, recorded, ct);
            activeHandlers.Add(handler);
        }

        await Task.WhenAll(activeHandlers.Select(IgnoreCancelAsync)).ConfigureAwait(false);
    }

    private static async Task HandleH2ClientAsync(
        TcpClient accepted,
        byte[] leafDer,
        byte[] caDer,
        byte[] leafPkcs8,
        int h1Port,
        ConcurrentQueue<CapturedWireRequest> recorded,
        CancellationToken ct)
    {
        using (accepted)
        await using (NetworkStream net = accepted.GetStream())
        using (CancellationTokenRegistration reg = ct.Register(() => net.Dispose()))
        {
            try
            {
                var protocol = new BcTls.TlsServerProtocol(net);
                var bcServer = new BcTestTls13Server(leafDer, caDer, leafPkcs8, BcTls.ProtocolName.Http_2_Tls);
                protocol.Accept(bcServer);

                using var tlsStream = new AsyncFriendlyBcStream(protocol.Stream);
                var h2 = new H2LoopbackHelper(tlsStream);
                if (!await h2.ReadAndVerifyPrefaceAsync(ct).ConfigureAwait(false))
                    return;

                await h2.WriteSettingsAsync(new (ushort, uint)[] { (3, 100), (4, 65535), (5, 16384) }, ct).ConfigureAwait(false);

                var decoder = new HpackDecoder(4096, 1_048_576);
                var encoder = new HpackEncoder(4096, HpackHuffmanMode.IfSmaller);
                var streams = new Dictionary<int, H2StreamAccum>();

                while (!ct.IsCancellationRequested)
                {
                    (byte type, byte flags, int streamId, byte[] payload) frame;
                    try
                    {
                        frame = await h2.ReadFrameAsync(ct).ConfigureAwait(false);
                    }
                    catch
                    {
                        break;
                    }

                    switch (frame.type)
                    {
                        case 0x04: // SETTINGS
                            if ((frame.flags & 0x01) == 0)
                                await h2.WriteSettingsAckAsync(ct).ConfigureAwait(false);
                            break;

                        case 0x06: // PING
                            if ((frame.flags & 0x01) == 0)
                                await h2.WriteFrameAsync(0x06, 0x01, 0, frame.payload, ct).ConfigureAwait(false);
                            break;

                        case 0x01: // HEADERS
                        {
                            int off = 0;
                            int padLen = 0;
                            if ((frame.flags & 0x08) != 0)
                                padLen = frame.payload[off++];
                            if ((frame.flags & 0x20) != 0)
                                off += 5;
                            int fragLen = Math.Max(0, frame.payload.Length - off - padLen);

                            var acc = new H2StreamAccum();
                            if (fragLen > 0)
                                acc.Headers.Write(frame.payload, off, fragLen);
                            acc.HeadersComplete = (frame.flags & 0x04) != 0;
                            acc.EndStreamSeen = (frame.flags & 0x01) != 0;
                            streams[frame.streamId] = acc;

                            if (acc.HeadersComplete && acc.EndStreamSeen && !acc.Dispatched)
                            {
                                acc.Dispatched = true;
                                await RespondH2Async(frame.streamId, acc, h2, decoder, encoder, h1Port, recorded, ct).ConfigureAwait(false);
                            }
                            break;
                        }

                        case 0x09: // CONTINUATION
                        {
                            if (streams.TryGetValue(frame.streamId, out H2StreamAccum? acc))
                            {
                                acc.Headers.Write(frame.payload);
                                if ((frame.flags & 0x04) != 0)
                                    acc.HeadersComplete = true;
                                if (acc.HeadersComplete && acc.EndStreamSeen && !acc.Dispatched)
                                {
                                    acc.Dispatched = true;
                                    await RespondH2Async(frame.streamId, acc, h2, decoder, encoder, h1Port, recorded, ct).ConfigureAwait(false);
                                }
                            }
                            break;
                        }

                        case 0x00: // DATA
                        {
                            if (streams.TryGetValue(frame.streamId, out H2StreamAccum? acc))
                            {
                                int off = 0;
                                int padLen = 0;
                                if ((frame.flags & 0x08) != 0)
                                    padLen = frame.payload[off++];
                                int dataLen = Math.Max(0, frame.payload.Length - off - padLen);
                                if (dataLen > 0)
                                    acc.Body.Write(frame.payload, off, dataLen);
                                if ((frame.flags & 0x01) != 0)
                                    acc.EndStreamSeen = true;
                                if (acc.HeadersComplete && acc.EndStreamSeen && !acc.Dispatched)
                                {
                                    acc.Dispatched = true;
                                    await RespondH2Async(frame.streamId, acc, h2, decoder, encoder, h1Port, recorded, ct).ConfigureAwait(false);
                                }
                            }
                            break;
                        }
                    }
                }
            }
            catch
            {
                // Ignore teardown exceptions.
            }
        }
    }

    private static async Task RespondH2Async(
        int streamId,
        H2StreamAccum acc,
        H2LoopbackHelper h2,
        HpackDecoder decoder,
        HpackEncoder encoder,
        int h1Port,
        ConcurrentQueue<CapturedWireRequest> recorded,
        CancellationToken ct)
    {
        List<PureHttpHeader> hdrs = decoder.DecodeHeaderBlock(acc.Headers.ToArray(), validateHttp2Semantics: false);
        string method = hdrs.FirstOrDefault(h => h.Name == ":method").Value ?? "GET";
        string path = hdrs.FirstOrDefault(h => h.Name == ":path").Value ?? "/";
        byte[] bodyBytes = acc.Body.ToArray();

        var wire = new CapturedWireRequest(method, path, hdrs, bodyBytes);
        recorded.Enqueue(wire);

        int status = 200;
        var respHeaders = new List<PureHttpHeader>();
        byte[] respBody = Array.Empty<byte>();

        switch (path)
        {
            case "/default-get":
                respHeaders.Add(new(":status", "200"));
                respHeaders.Add(new("set-cookie", "sid=pure_h2_sid; Path=/"));
                respBody = "h2-get-ok"u8.ToArray();
                break;

            case "/override-post":
                respHeaders.Add(new(":status", "200"));
                respBody = bodyBytes;
                break;

            case "/cookie-check":
                respHeaders.Add(new(":status", "200"));
                respBody = Encoding.UTF8.GetBytes(wire.JoinedHeaders("cookie"));
                break;

            case "/start-302":
                status = 302;
                respHeaders.Add(new(":status", "302"));
                respHeaders.Add(new("location", "/after-302"));
                respHeaders.Add(new("set-cookie", "hop302=c302; Path=/"));
                break;

            case "/after-302":
                respHeaders.Add(new(":status", "200"));
                respBody = Encoding.UTF8.GetBytes($"{method}|{wire.JoinedHeaders("cookie")}|{wire.FirstHeader("content-type") ?? "-"}");
                break;

            case "/start-307":
                status = 307;
                respHeaders.Add(new(":status", "307"));
                respHeaders.Add(new("location", "/after-307"));
                break;

            case "/after-307":
                respHeaders.Add(new(":status", "200"));
                respBody = Encoding.UTF8.GetBytes($"{method}:{Encoding.UTF8.GetString(bodyBytes)}");
                break;

            case "/xorigin-start":
                status = 302;
                respHeaders.Add(new(":status", "302"));
                respHeaders.Add(new("location", $"https://{TestHost}:{h1Port}/xorigin-target"));
                break;

            case "/loop":
                status = 302;
                respHeaders.Add(new(":status", "302"));
                respHeaders.Add(new("location", "/loop"));
                break;

            case "/pin-ok":
                respHeaders.Add(new(":status", "200"));
                respBody = "pinned-ok"u8.ToArray();
                break;

            default:
                status = 404;
                respHeaders.Add(new(":status", "404"));
                break;
        }

        _ = status;
        byte[] encodedResp = encoder.EncodeHeaderList(respHeaders, indexLiterals: false);
        bool noBody = respBody.Length == 0;
        await h2.WriteFrameAsync(0x01, noBody ? (byte)0x05 : (byte)0x04, streamId, encodedResp, ct).ConfigureAwait(false);
        if (!noBody)
            await h2.WriteFrameAsync(0x00, 0x01, streamId, respBody, ct).ConfigureAwait(false);
    }

    private static async Task RunTls13H1ServerAsync(
        TcpListener listener,
        byte[] leafDer,
        byte[] caDer,
        byte[] leafPkcs8,
        ConcurrentQueue<CapturedWireRequest> recorded,
        CancellationToken ct)
    {
        var activeHandlers = new List<Task>();
        while (!ct.IsCancellationRequested)
        {
            TcpClient accepted;
            try
            {
                accepted = await listener.AcceptTcpClientAsync(ct).ConfigureAwait(false);
            }
            catch
            {
                break;
            }

            activeHandlers.Add(HandleH1ClientAsync(accepted, leafDer, caDer, leafPkcs8, recorded, ct));
        }

        await Task.WhenAll(activeHandlers.Select(IgnoreCancelAsync)).ConfigureAwait(false);
    }

    private static async Task HandleH1ClientAsync(
        TcpClient accepted,
        byte[] leafDer,
        byte[] caDer,
        byte[] leafPkcs8,
        ConcurrentQueue<CapturedWireRequest> recorded,
        CancellationToken ct)
    {
        using (accepted)
        await using (NetworkStream net = accepted.GetStream())
        using (CancellationTokenRegistration reg = ct.Register(() => net.Dispose()))
        {
            try
            {
                var protocol = new BcTls.TlsServerProtocol(net);
                var bcServer = new BcTestTls13Server(leafDer, caDer, leafPkcs8, BcTls.ProtocolName.Http_1_1);
                protocol.Accept(bcServer);

                using var tlsStream = new AsyncFriendlyBcStream(protocol.Stream);
                var reader = new BufferedStreamReader(tlsStream, leaveOpen: true);

                while (!ct.IsCancellationRequested)
                {
                    string? requestLine;
                    try
                    {
                        requestLine = await reader.ReadLineAsciiAsync(64 * 1024, ct).ConfigureAwait(false);
                    }
                    catch
                    {
                        break;
                    }

                    if (string.IsNullOrEmpty(requestLine))
                        break;

                    string[] parts = requestLine.Split(' ', 3);
                    string method = parts[0];
                    string path = parts.Length > 1 ? parts[1] : "/";
                    var headers = new List<PureHttpHeader>();
                    int contentLength = 0;

                    while (true)
                    {
                        string? line = await reader.ReadLineAsciiAsync(64 * 1024, ct).ConfigureAwait(false);
                        if (line is null || line.Length == 0)
                            break;
                        int colon = line.IndexOf(':');
                        if (colon > 0)
                        {
                            string hName = line[..colon].Trim();
                            string hVal = line[(colon + 1)..].Trim();
                            headers.Add(new PureHttpHeader(hName, hVal));
                            if (string.Equals(hName, "content-length", StringComparison.OrdinalIgnoreCase))
                                int.TryParse(hVal, out contentLength);
                        }
                    }

                    byte[] bodyBytes = contentLength > 0 ? new byte[contentLength] : Array.Empty<byte>();
                    if (contentLength > 0)
                        await reader.ReadExactAsync(bodyBytes, ct).ConfigureAwait(false);

                    recorded.Enqueue(new CapturedWireRequest(method, path, headers, bodyBytes));

                    string respBodyText = path switch
                    {
                        "/h1-get" => "h1-tls13-ok",
                        "/h1-post" => $"{method}:{Encoding.UTF8.GetString(bodyBytes)}",
                        "/xorigin-target" => "xorigin-arrived",
                        _ => "h1-default",
                    };
                    byte[] respBytes = Encoding.UTF8.GetBytes(respBodyText);
                    string extraCookie = path == "/h1-get" ? "Set-Cookie: h1c=v1; Path=/\r\n" : string.Empty;
                    string head = $"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n{extraCookie}Content-Length: {respBytes.Length}\r\nConnection: keep-alive\r\n\r\n";

                    await tlsStream.WriteAsync(Encoding.ASCII.GetBytes(head), ct).ConfigureAwait(false);
                    await tlsStream.WriteAsync(respBytes, ct).ConfigureAwait(false);
                    await tlsStream.FlushAsync(ct).ConfigureAwait(false);
                }
            }
            catch
            {
                // Ignore teardown exceptions.
            }
        }
    }

    private sealed class H2LoopbackHelper
    {
        private readonly Stream _stream;

        public H2LoopbackHelper(Stream stream) => _stream = stream;

        public async Task<bool> ReadAndVerifyPrefaceAsync(CancellationToken ct)
        {
            var buf = new byte[24];
            await ReadExactStreamAsync(_stream, buf, ct).ConfigureAwait(false);
            return Encoding.ASCII.GetString(buf) == "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n";
        }

        public async Task<(byte Type, byte Flags, int StreamId, byte[] Payload)> ReadFrameAsync(CancellationToken ct)
        {
            var hdr = new byte[9];
            await ReadExactStreamAsync(_stream, hdr, ct).ConfigureAwait(false);
            int len = (hdr[0] << 16) | (hdr[1] << 8) | hdr[2];
            var payload = len > 0 ? new byte[len] : Array.Empty<byte>();
            if (len > 0)
                await ReadExactStreamAsync(_stream, payload, ct).ConfigureAwait(false);
            int streamId = BinaryPrimitives.ReadInt32BigEndian(hdr.AsSpan(5, 4)) & 0x7FFF_FFFF;
            return (hdr[3], hdr[4], streamId, payload);
        }

        public async Task WriteFrameAsync(byte type, byte flags, int streamId, ReadOnlyMemory<byte> payload, CancellationToken ct)
        {
            var frame = new byte[9 + payload.Length];
            int len = payload.Length;
            frame[0] = (byte)(len >> 16);
            frame[1] = (byte)(len >> 8);
            frame[2] = (byte)len;
            frame[3] = type;
            frame[4] = flags;
            BinaryPrimitives.WriteInt32BigEndian(frame.AsSpan(5, 4), streamId & 0x7FFF_FFFF);
            if (len > 0)
                payload.Span.CopyTo(frame.AsSpan(9));
            await _stream.WriteAsync(frame, ct).ConfigureAwait(false);
            await _stream.FlushAsync(ct).ConfigureAwait(false);
        }

        public Task WriteSettingsAsync((ushort Id, uint Value)[] settings, CancellationToken ct)
        {
            var buf = new byte[settings.Length * 6];
            for (int i = 0; i < settings.Length; i++)
            {
                BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(i * 6, 2), settings[i].Id);
                BinaryPrimitives.WriteUInt32BigEndian(buf.AsSpan(i * 6 + 2, 4), settings[i].Value);
            }
            return WriteFrameAsync(0x04, 0x00, 0, buf, ct);
        }

        public Task WriteSettingsAckAsync(CancellationToken ct)
            => WriteFrameAsync(0x04, 0x01, 0, ReadOnlyMemory<byte>.Empty, ct);

        private static async Task ReadExactStreamAsync(Stream stream, byte[] buf, CancellationToken ct)
        {
            int off = 0;
            while (off < buf.Length)
            {
                int n = await stream.ReadAsync(buf.AsMemory(off, buf.Length - off), ct).ConfigureAwait(false);
                if (n == 0)
                    throw new EndOfStreamException();
                off += n;
            }
        }
    }

    private sealed class AsyncFriendlyBcStream : Stream
    {
        private readonly Stream _inner;
        private readonly object _writeLock = new();

        public AsyncFriendlyBcStream(Stream inner) => _inner = inner;

        public override bool CanRead => _inner.CanRead;
        public override bool CanSeek => false;
        public override bool CanWrite => _inner.CanWrite;
        public override long Length => throw new NotSupportedException();
        public override long Position { get => throw new NotSupportedException(); set => throw new NotSupportedException(); }

        public override int Read(byte[] buffer, int offset, int count) => _inner.Read(buffer, offset, count);

        public override ValueTask<int> ReadAsync(Memory<byte> buffer, CancellationToken cancellationToken = default)
        {
            byte[] tmp = new byte[buffer.Length];
            return new ValueTask<int>(Task.Run(() =>
            {
                int n = _inner.Read(tmp, 0, tmp.Length);
                if (n > 0)
                    tmp.AsSpan(0, n).CopyTo(buffer.Span);
                return n;
            }, cancellationToken));
        }

        public override Task<int> ReadAsync(byte[] buffer, int offset, int count, CancellationToken cancellationToken) =>
            Task.Run(() => _inner.Read(buffer, offset, count), cancellationToken);

        public override void Write(byte[] buffer, int offset, int count)
        {
            lock (_writeLock)
                _inner.Write(buffer, offset, count);
        }

        public override ValueTask WriteAsync(ReadOnlyMemory<byte> buffer, CancellationToken cancellationToken = default)
        {
            byte[] copy = buffer.ToArray();
            return new ValueTask(Task.Run(() =>
            {
                lock (_writeLock)
                {
                    _inner.Write(copy, 0, copy.Length);
                    _inner.Flush();
                }
            }, cancellationToken));
        }

        public override Task WriteAsync(byte[] buffer, int offset, int count, CancellationToken cancellationToken)
        {
            byte[] copy = buffer.AsSpan(offset, count).ToArray();
            return Task.Run(() =>
            {
                lock (_writeLock)
                {
                    _inner.Write(copy, 0, copy.Length);
                    _inner.Flush();
                }
            }, cancellationToken);
        }

        public override void Flush()
        {
            lock (_writeLock)
                _inner.Flush();
        }

        public override Task FlushAsync(CancellationToken cancellationToken) => Task.Run(Flush, cancellationToken);
        public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
        public override void SetLength(long value) => throw new NotSupportedException();

        protected override void Dispose(bool disposing)
        {
            if (disposing)
                _inner.Dispose();
            base.Dispose(disposing);
        }
    }

    private sealed class BcTestTls13Server : BcTls.DefaultTlsServer
    {
        private readonly byte[] _leafDer;
        private readonly byte[] _caDer;
        private readonly byte[] _leafPkcs8;
        private readonly BcTls.ProtocolName[] _protocols;
        private readonly BcBc.BcTlsCrypto _bcCrypto;

        public BcTestTls13Server(byte[] leafDer, byte[] caDer, byte[] leafPkcs8, params BcTls.ProtocolName[] protocols)
            : this(new BcBc.BcTlsCrypto(new BcSecurity.SecureRandom()), leafDer, caDer, leafPkcs8, protocols)
        {
        }

        private BcTestTls13Server(
            BcBc.BcTlsCrypto crypto,
            byte[] leafDer,
            byte[] caDer,
            byte[] leafPkcs8,
            BcTls.ProtocolName[] protocols)
            : base(crypto)
        {
            _bcCrypto = crypto;
            _leafDer = leafDer;
            _caDer = caDer;
            _leafPkcs8 = leafPkcs8;
            _protocols = protocols;
        }

        protected override BcTls.ProtocolVersion[] GetSupportedVersions() =>
            new[] { BcTls.ProtocolVersion.TLSv13 };

        protected override int[] GetSupportedCipherSuites() =>
            new[] { BcTls.CipherSuite.TLS_AES_128_GCM_SHA256, BcTls.CipherSuite.TLS_AES_256_GCM_SHA384 };

        protected override IList<BcTls.ProtocolName> GetProtocolNames() =>
            new List<BcTls.ProtocolName>(_protocols);

        public override BcTls.TlsCredentials GetCredentials() => GetECDsaSignerCredentials();

        protected override BcTls.TlsCredentialedSigner GetECDsaSignerCredentials()
        {
            var chain = new BcTls.Certificate(
                Array.Empty<byte>(),
                new BcTls.CertificateEntry[]
                {
                    new(new BcBc.BcTlsCertificate(_bcCrypto, _leafDer), null),
                    new(new BcBc.BcTlsCertificate(_bcCrypto, _caDer), null),
                });
            var privKey = BcSecurity.PrivateKeyFactory.CreateKey(_leafPkcs8);
            return new BcBc.BcDefaultTlsCredentialedSigner(
                new BcCrypto.TlsCryptoParameters(m_context),
                _bcCrypto,
                privKey,
                chain,
                new BcTls.SignatureAndHashAlgorithm(BcTls.HashAlgorithm.sha256, BcTls.SignatureAlgorithm.ecdsa));
        }
    }

    private sealed class ServerStreamAssembler
    {
        private readonly SortedDictionary<ulong, byte[]> _chunks = new();
        private ulong _readOffset;

        public void Add(ulong offset, byte[] data)
        {
            if (data.Length == 0 || offset + (ulong)data.Length <= _readOffset)
                return;
            _chunks[offset] = data;
        }

        public byte[] Drain()
        {
            var ms = new MemoryStream();
            while (_chunks.Count > 0)
            {
                using SortedDictionary<ulong, byte[]>.Enumerator en = _chunks.GetEnumerator();
                en.MoveNext();
                ulong off = en.Current.Key;
                byte[] data = en.Current.Value;
                if (off > _readOffset)
                    break;
                _chunks.Remove(off);
                ulong end = off + (ulong)data.Length;
                if (end <= _readOffset)
                    continue;
                int trim = (int)(_readOffset - off);
                ms.Write(data, trim, data.Length - trim);
                _readOffset = end;
            }
            return ms.ToArray();
        }
    }

    private sealed class LoopbackQuicHttp3Server : IAsyncDisposable
    {
        private readonly IQuicDatagramTransport _transport;
        private readonly ECDsa _leafKey;
        private readonly byte[][] _derChain;
        private readonly byte[] _serverScid = RandomNumberGenerator.GetBytes(8);
        private readonly object _txLock = new();

        private byte[] _clientCid = Array.Empty<byte>();
        private byte[] _originalDcid = Array.Empty<byte>();
        private QuicKeySet? _initRead;
        private QuicKeySet? _initWrite;
        private QuicKeySet? _hsRead;
        private QuicKeySet? _hsWrite;
        private QuicKeySet? _appRead;
        private QuicKeySet? _appWrite;
        private ulong _pnInit;
        private ulong _pnHs;
        private ulong _pnApp;
        private long _rxInitMax = -1;
        private long _rxHsMax = -1;
        private long _rxAppMax = -1;

        private bool _handshakeReplied;
        private bool _handshakeDoneSent;
        private readonly ServerStreamAssembler _initCrypto = new();
        private readonly MemoryStream _chAccum = new();
        private readonly MemoryStream _hsCryptoAccum = new();
        private readonly MemoryStream _transcript = new();
        private byte[] _cHsSecret = Array.Empty<byte>();
        private byte[] _sHsSecret = Array.Empty<byte>();
        private byte[] _masterSecret = Array.Empty<byte>();

        private readonly ulong _srvControlStreamId = 3;
        private readonly ulong _srvEncoderStreamId = 7;
        private readonly ulong _srvDecoderStreamId = 11;
        private ulong _srvControlOffset;
        private ulong _srvEncoderOffset;
        private ulong _srvDecoderOffset;
        private readonly ConcurrentDictionary<ulong, (ServerStreamAssembler Asm, MemoryStream Buf, ulong? FinSize, bool Handled)> _bidiStreams = new();
        private readonly ConcurrentDictionary<ulong, ServerStreamAssembler> _clientUniStreams = new();
        private readonly QpackDecoder _reqDecoder = new();

        public LoopbackQuicHttp3Server(IQuicDatagramTransport transport, ECDsa leafKey, byte[][] derChain)
        {
            _transport = transport;
            _leafKey = leafKey;
            _derChain = derChain;
        }

        public async Task RunAsync(CancellationToken ct)
        {
            var buf = new byte[66_048];
            while (!ct.IsCancellationRequested)
            {
                int n = await _transport.ReceiveDatagramAsync(buf, ct).ConfigureAwait(false);
                if (n == 0)
                    break;

                var outbound = new List<byte[]>();
                ProcessDatagram(buf.AsSpan(0, n), outbound);
                for (int i = 0; i < outbound.Count; i++)
                    await _transport.SendDatagramAsync(outbound[i], ct).ConfigureAwait(false);
            }
        }

        private void ProcessDatagram(ReadOnlySpan<byte> datagram, List<byte[]> outbound)
        {
            int offset = 0;
            while (offset < datagram.Length)
            {
                ReadOnlySpan<byte> span = datagram.Slice(offset);
                byte first = span[0];
                if ((first & 0x80) != 0)
                {
                    if (span.Length < 7)
                        return;
                    int off = 5;
                    byte dcidLen = span[off++];
                    ReadOnlySpan<byte> dcid = span.Slice(off, dcidLen);
                    off += dcidLen;
                    byte scidLen = span[off++];
                    ReadOnlySpan<byte> scid = span.Slice(off, scidLen);
                    off += scidLen;

                    var type = (QuicLongPacketType)((first >> 4) & 0x03);
                    if (type == QuicLongPacketType.Initial)
                    {
                        QuicVarInt.TryRead(span, ref off, out ulong tLen);
                        off += (int)tLen;
                    }
                    QuicVarInt.TryRead(span, ref off, out ulong pktLen);
                    int pnOffset = off;
                    int totalLen = pnOffset + (int)pktLen;

                    if (type == QuicLongPacketType.Initial)
                    {
                        if (_originalDcid.Length == 0)
                        {
                            _originalDcid = dcid.ToArray();
                            _clientCid = scid.ToArray();
                            _initRead = QuicCrypto.DeriveInitialKeys(_originalDcid, isServer: false);
                            _initWrite = QuicCrypto.DeriveInitialKeys(_originalDcid, isServer: true);
                        }

                        byte[] copy = span.Slice(0, totalLen).ToArray();
                        if (_initRead!.TryRemoveHeaderProtection(copy, pnOffset, out int pnLen, out _))
                        {
                            ulong pn = QuicCrypto.DecodePacketNumber(_rxInitMax, QuicPacketCodec.ReadTruncatedPacketNumber(copy.AsSpan(pnOffset, pnLen), pnLen), pnLen * 8);
                            if ((long)pn > _rxInitMax) _rxInitMax = (long)pn;
                            if (_initRead.TryPacketUnprotect(pn, copy.AsSpan(0, pnOffset + pnLen), copy.AsSpan(pnOffset + pnLen), out byte[] pt))
                                HandleInitialFrames(pn, QuicFrameCodec.DecodeAll(pt), outbound);
                        }
                    }
                    else if (type == QuicLongPacketType.Handshake && _hsRead is not null)
                    {
                        byte[] copy = span.Slice(0, totalLen).ToArray();
                        if (_hsRead.TryRemoveHeaderProtection(copy, pnOffset, out int pnLen, out _))
                        {
                            ulong pn = QuicCrypto.DecodePacketNumber(_rxHsMax, QuicPacketCodec.ReadTruncatedPacketNumber(copy.AsSpan(pnOffset, pnLen), pnLen), pnLen * 8);
                            if ((long)pn > _rxHsMax) _rxHsMax = (long)pn;
                            if (_hsRead.TryPacketUnprotect(pn, copy.AsSpan(0, pnOffset + pnLen), copy.AsSpan(pnOffset + pnLen), out byte[] pt))
                                HandleHandshakeFrames(pn, QuicFrameCodec.DecodeAll(pt), outbound);
                        }
                    }

                    offset += totalLen;
                }
                else
                {
                    if (_appRead is null)
                        return;

                    int pnOffset = 1 + _serverScid.Length;
                    byte[] copy = span.ToArray();
                    if (_appRead.TryRemoveHeaderProtection(copy, pnOffset, out int pnLen, out _))
                    {
                        ulong pn = QuicCrypto.DecodePacketNumber(_rxAppMax, QuicPacketCodec.ReadTruncatedPacketNumber(copy.AsSpan(pnOffset, pnLen), pnLen), pnLen * 8);
                        if ((long)pn > _rxAppMax) _rxAppMax = (long)pn;
                        if (_appRead.TryPacketUnprotect(pn, copy.AsSpan(0, pnOffset + pnLen), copy.AsSpan(pnOffset + pnLen), out byte[] pt))
                            HandleAppFrames(pn, QuicFrameCodec.DecodeAll(pt), outbound);
                    }
                    return;
                }
            }
        }

        private void HandleInitialFrames(ulong pn, List<QuicFrame> frames, List<byte[]> outbound)
        {
            foreach (QuicFrame f in frames)
            {
                if (f is QuicCryptoFrame cf)
                    _initCrypto.Add(cf.Offset, cf.Data);
            }

            byte[] chBytes = _initCrypto.Drain();
            if (chBytes.Length > 0)
                _chAccum.Write(chBytes);

            if (_handshakeReplied || _chAccum.Length < 4)
                return;

            byte[] allCh = _chAccum.ToArray();
            int bodyLen = (allCh[1] << 16) | (allCh[2] << 8) | allCh[3];
            if (allCh.Length < 4 + bodyLen)
                return;

            _handshakeReplied = true;
            byte[] chMsg = allCh.AsSpan(0, 4 + bodyLen).ToArray();
            (byte[] clientXPub, byte[] sessionId) = ParseClientHelloMinimal(chMsg);

            X25519.GenerateKeyPair(out byte[] sPriv, out byte[] sPub);
            byte[] sharedSecret = X25519.ScalarMult(sPriv, clientXPub);

            byte[] sh = BuildServerHello(RandomNumberGenerator.GetBytes(32), sessionId, CipherSuiteId.TLS_AES_128_GCM_SHA256, sPub);
            _transcript.Write(chMsg);
            _transcript.Write(sh);

            byte[] zeros = new byte[32];
            byte[] earlySecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, ReadOnlySpan<byte>.Empty, zeros);
            byte[] emptyHash = HashPrimitives.Sha256(ReadOnlySpan<byte>.Empty);
            byte[] derived = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, earlySecret, "derived", emptyHash, 32);
            byte[] hsSecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, derived, sharedSecret);
            byte[] shHash = HashPrimitives.Sha256(_transcript.ToArray());

            _cHsSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, hsSecret, "c hs traffic", shHash, 32);
            _sHsSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, hsSecret, "s hs traffic", shHash, 32);
            _hsRead = QuicCrypto.DerivePacketKeys(CipherSuiteId.TLS_AES_128_GCM_SHA256, _cHsSecret);
            _hsWrite = QuicCrypto.DerivePacketKeys(CipherSuiteId.TLS_AES_128_GCM_SHA256, _sHsSecret);

            var srvTp = new QuicTransportParameters
            {
                OriginalDestinationConnectionId = _originalDcid,
                InitialSourceConnectionId = _serverScid,
                MaxIdleTimeoutMs = 30_000,
                MaxUdpPayloadSize = 1472,
                InitialMaxData = 10_485_760,
                InitialMaxStreamDataBidiLocal = 4_194_304,
                InitialMaxStreamDataBidiRemote = 4_194_304,
                InitialMaxStreamDataUni = 4_194_304,
                InitialMaxStreamsBidi = 100,
                InitialMaxStreamsUni = 100,
                MaxDatagramFrameSize = 65_536,
            };
            byte[] ee = BuildEncryptedExtensions("h3", QuicTransportParametersCodec.Encode(srvTp));
            _transcript.Write(ee);

            byte[] cert = BuildCertificateMessage(_derChain);
            _transcript.Write(cert);

            byte[] cv = BuildCertificateVerify(_leafKey, HashPrimitives.Sha256(_transcript.ToArray()));
            _transcript.Write(cv);

            byte[] sFinKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, _sHsSecret, "finished", ReadOnlySpan<byte>.Empty, 32);
            byte[] sFinVerify = HashPrimitives.Hmac(HashAlgorithmKind.Sha256, sFinKey, HashPrimitives.Sha256(_transcript.ToArray()));
            byte[] sFin = WrapHandshakeMsg(0x14, sFinVerify);
            _transcript.Write(sFin);

            byte[] finHash = HashPrimitives.Sha256(_transcript.ToArray());
            byte[] dMaster = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, hsSecret, "derived", emptyHash, 32);
            _masterSecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, dMaster, zeros);

            byte[] cAppSec = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, _masterSecret, "c ap traffic", finHash, 32);
            byte[] sAppSec = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, _masterSecret, "s ap traffic", finHash, 32);
            _appRead = QuicCrypto.DerivePacketKeys(CipherSuiteId.TLS_AES_128_GCM_SHA256, cAppSec);
            _appWrite = QuicCrypto.DerivePacketKeys(CipherSuiteId.TLS_AES_128_GCM_SHA256, sAppSec);

            byte[] initPayload = QuicFrameCodec.Encode(new QuicFrame[]
            {
                QuicAckFrame.FromPacketNumbers(new[] { pn }),
                new QuicCryptoFrame(0, sh),
            });
            outbound.Add(QuicPacketCodec.BuildLongHeaderPacket(QuicLongPacketType.Initial, _clientCid, _serverScid, ReadOnlySpan<byte>.Empty, _pnInit++, 1, initPayload, _initWrite!));

            byte[] flight = ee.Concat(cert).Concat(cv).Concat(sFin).ToArray();
            int pos = 0;
            while (pos < flight.Length)
            {
                int take = Math.Min(1000, flight.Length - pos);
                byte[] hsPayload = QuicFrameCodec.Encode(new QuicFrame[]
                {
                    new QuicCryptoFrame((ulong)pos, flight.AsSpan(pos, take).ToArray()),
                });
                outbound.Add(QuicPacketCodec.BuildLongHeaderPacket(QuicLongPacketType.Handshake, _clientCid, _serverScid, ReadOnlySpan<byte>.Empty, _pnHs++, 1, hsPayload, _hsWrite!));
                pos += take;
            }
        }

        private void HandleHandshakeFrames(ulong pn, List<QuicFrame> frames, List<byte[]> outbound)
        {
            foreach (QuicFrame f in frames)
            {
                if (f is QuicCryptoFrame cf)
                    _hsCryptoAccum.Write(cf.Data);
            }

            if (_handshakeDoneSent || _hsCryptoAccum.Length < 4)
                return;

            byte[] cFin = _hsCryptoAccum.ToArray();
            int finLen = (cFin[1] << 16) | (cFin[2] << 8) | cFin[3];
            if (cFin[0] != 0x14 || cFin.Length < 4 + finLen)
                return;

            _handshakeDoneSent = true;
            byte[] hsAck = QuicFrameCodec.Encode(new QuicFrame[] { QuicAckFrame.FromPacketNumbers(new[] { pn }) });
            outbound.Add(QuicPacketCodec.BuildLongHeaderPacket(QuicLongPacketType.Handshake, _clientCid, _serverScid, ReadOnlySpan<byte>.Empty, _pnHs++, 1, hsAck, _hsWrite!));

            AddAppFrames(new QuicFrame[] { QuicHandshakeDoneFrame.Instance }, outbound);

            var srvSettings = new List<(ulong, ulong)>
            {
                (Http3SettingId.QpackMaxTableCapacity, 65_536),
                (Http3SettingId.MaxFieldSectionSize, 262_144),
                (Http3SettingId.QpackBlockedStreams, 100),
                (Http3SettingId.H3Datagram, 1),
            };
            byte[] settingsFrame = Http3FrameCodec.BuildFrame(Http3FrameType.Settings, Http3FrameCodec.BuildSettingsPayload(srvSettings));
            byte[] ctrlStart = QuicVarInt.Encode(Http3StreamType.Control).Concat(settingsFrame).ToArray();
            lock (_txLock)
            {
                ulong cOff = _srvControlOffset;
                _srvControlOffset += (ulong)ctrlStart.Length;
                AddAppFramesLocked(new QuicFrame[] { new QuicStreamFrame(_srvControlStreamId, cOff, ctrlStart, Fin: false) }, outbound);

                byte[] encHdr = QuicVarInt.Encode(Http3StreamType.QpackEncoder);
                ulong eOff = _srvEncoderOffset;
                _srvEncoderOffset += (ulong)encHdr.Length;
                AddAppFramesLocked(new QuicFrame[] { new QuicStreamFrame(_srvEncoderStreamId, eOff, encHdr, Fin: false) }, outbound);

                byte[] decHdr = QuicVarInt.Encode(Http3StreamType.QpackDecoder);
                ulong dOff = _srvDecoderOffset;
                _srvDecoderOffset += (ulong)decHdr.Length;
                AddAppFramesLocked(new QuicFrame[] { new QuicStreamFrame(_srvDecoderStreamId, dOff, decHdr, Fin: false) }, outbound);
            }
        }

        private void HandleAppFrames(ulong pn, List<QuicFrame> frames, List<byte[]> outbound)
        {
            if (frames.Any(f => f.IsAckEliciting))
                AddAppFrames(new QuicFrame[] { QuicAckFrame.FromPacketNumbers(new[] { pn }) }, outbound);

            foreach (QuicFrame frame in frames)
            {
                if (frame is not QuicStreamFrame sf)
                    continue;

                if ((sf.StreamId & 0x02UL) != 0)
                {
                    ServerStreamAssembler asm = _clientUniStreams.GetOrAdd(sf.StreamId, _ => new ServerStreamAssembler());
                    asm.Add(sf.Offset, sf.Data);
                    _ = asm.Drain();
                    continue;
                }

                (ServerStreamAssembler Asm, MemoryStream Buf, ulong? FinSize, bool Handled) entry = _bidiStreams.GetOrAdd(
                    sf.StreamId,
                    _ => (new ServerStreamAssembler(), new MemoryStream(), null, false));

                entry.Asm.Add(sf.Offset, sf.Data);
                byte[] chunk = entry.Asm.Drain();
                if (chunk.Length > 0)
                    entry.Buf.Write(chunk);

                ulong? finSize = entry.FinSize;
                if (sf.Fin)
                    finSize = sf.Offset + (ulong)sf.Data.Length;

                bool handled = entry.Handled;
                if (!handled && finSize.HasValue && (ulong)entry.Buf.Length >= finSize.Value)
                {
                    handled = true;
                    _bidiStreams[sf.StreamId] = (entry.Asm, entry.Buf, finSize, handled);
                    HandleHttp3RequestStream(sf.StreamId, entry.Buf.ToArray(), outbound);
                }
                else
                {
                    _bidiStreams[sf.StreamId] = (entry.Asm, entry.Buf, finSize, handled);
                }
            }
        }

        private void HandleHttp3RequestStream(ulong streamId, byte[] requestBytes, List<byte[]> outbound)
        {
            string path = "/";
            string method = "GET";
            var body = new MemoryStream();

            int offset = 0;
            while (offset < requestBytes.Length)
            {
                QuicVarInt.TryRead(requestBytes, ref offset, out ulong frameType);
                QuicVarInt.TryRead(requestBytes, ref offset, out ulong frameLen);
                byte[] payload = requestBytes.AsSpan(offset, (int)frameLen).ToArray();
                offset += (int)frameLen;

                if (frameType == Http3FrameType.Headers)
                {
                    List<PureHttpHeader> hdrs = _reqDecoder.DecodeFieldSection(payload, out _);
                    foreach (PureHttpHeader h in hdrs)
                    {
                        if (h.Name == ":path") path = h.Value;
                        if (h.Name == ":method") method = h.Value;
                    }
                }
                else if (frameType == Http3FrameType.Data)
                {
                    body.Write(payload);
                }
            }

            var qpack = new QpackEncoder();
            var txPayload = new MemoryStream();

            switch (path)
            {
                case "/hello":
                {
                    byte[] h = qpack.Encode(new PureHttpHeader[] { new(":status", "200"), new("content-type", "text/plain") });
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Headers, h));
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Data, "hello-h3"u8.ToArray()));
                    break;
                }

                case "/echo":
                {
                    byte[] h = qpack.Encode(new PureHttpHeader[] { new(":status", "200"), new("x-echo-method", method) });
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Headers, h));
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Data, body.ToArray()));
                    break;
                }

                case "/compressed/gzip":
                {
                    byte[] gz = ContentEncodingCodec.Compress("compressed-payload-gzip-ok"u8.ToArray(), "gzip");
                    byte[] h = qpack.Encode(new PureHttpHeader[] { new(":status", "200"), new("content-encoding", "gzip") });
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Headers, h));
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Data, gz));
                    break;
                }

                case "/compressed/br":
                {
                    byte[] br;
                    using (var ms = new MemoryStream())
                    {
                        using (var b = new BrotliStream(ms, CompressionLevel.Optimal, leaveOpen: true))
                            b.Write("compressed-payload-br-ok"u8);
                        br = ms.ToArray();
                    }
                    byte[] h = qpack.Encode(new PureHttpHeader[] { new(":status", "200"), new("content-encoding", "br") });
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Headers, h));
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Data, br));
                    break;
                }

                case "/compressed/zstd":
                {
                    using var comp = new Compressor();
                    byte[] zstd = comp.Wrap("compressed-payload-zstd-ok"u8).ToArray();
                    byte[] h = qpack.Encode(new PureHttpHeader[] { new(":status", "200"), new("content-encoding", "zstd") });
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Headers, h));
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Data, zstd));
                    break;
                }
            }

            byte[] respBytes = txPayload.ToArray();
            int pos = 0;
            while (pos < respBytes.Length || pos == 0)
            {
                int take = Math.Min(1000, respBytes.Length - pos);
                bool last = pos + take == respBytes.Length;
                AddAppFrames(new QuicFrame[] { new QuicStreamFrame(streamId, (ulong)pos, respBytes.AsSpan(pos, take).ToArray(), last) }, outbound);
                pos += take;
                if (respBytes.Length == 0)
                    break;
            }
        }

        private void AddAppFrames(IReadOnlyList<QuicFrame> frames, List<byte[]> outbound)
        {
            lock (_txLock)
                AddAppFramesLocked(frames, outbound);
        }

        private void AddAppFramesLocked(IReadOnlyList<QuicFrame> frames, List<byte[]> outbound)
        {
            byte[] pt = QuicFrameCodec.Encode(frames);
            outbound.Add(QuicPacketCodec.BuildShortHeaderPacket(_clientCid, _pnApp++, 1, keyPhase: false, pt, _appWrite!));
        }

        private static (byte[] X25519Pub, byte[] SessionId) ParseClientHelloMinimal(ReadOnlySpan<byte> ch)
        {
            int off = 4 + 2 + 32;
            byte sidLen = ch[off++];
            byte[] sid = ch.Slice(off, sidLen).ToArray();
            off += sidLen;
            ushort cLen = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(off, 2));
            off += 2 + cLen;
            byte compLen = ch[off++];
            off += compLen;
            ushort extTotal = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(off, 2));
            off += 2;
            int end = off + extTotal;
            byte[]? xPub = null;
            while (off < end)
            {
                ushort type = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(off, 2));
                ushort len = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(off + 2, 2));
                off += 4;
                if (type == TlsExtensionType.KeyShare)
                {
                    int ksLen = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(off, 2));
                    int kOff = off + 2;
                    while (kOff < off + 2 + ksLen)
                    {
                        ushort grp = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(kOff, 2));
                        ushort kLen = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(kOff + 2, 2));
                        if (grp == NamedGroupId.X25519)
                            xPub = ch.Slice(kOff + 4, kLen).ToArray();
                        kOff += 4 + kLen;
                    }
                }
                off += len;
            }
            return (xPub!, sid);
        }

        private static byte[] BuildServerHello(byte[] random, byte[] sessionId, ushort cipher, byte[] sPub)
        {
            var ks = new byte[4 + sPub.Length];
            BinaryPrimitives.WriteUInt16BigEndian(ks.AsSpan(0, 2), NamedGroupId.X25519);
            BinaryPrimitives.WriteUInt16BigEndian(ks.AsSpan(2, 2), (ushort)sPub.Length);
            sPub.CopyTo(ks, 4);

            using var exts = new MemoryStream();
            WriteExt(exts, TlsExtensionType.SupportedVersions, new byte[] { 0x03, 0x04 });
            WriteExt(exts, TlsExtensionType.KeyShare, ks);
            byte[] extBytes = exts.ToArray();

            using var body = new MemoryStream();
            Span<byte> u16 = stackalloc byte[2];
            BinaryPrimitives.WriteUInt16BigEndian(u16, TlsVersion.Tls12);
            body.Write(u16);
            body.Write(random);
            body.WriteByte((byte)sessionId.Length);
            body.Write(sessionId);
            BinaryPrimitives.WriteUInt16BigEndian(u16, cipher);
            body.Write(u16);
            body.WriteByte(0x00);
            BinaryPrimitives.WriteUInt16BigEndian(u16, (ushort)extBytes.Length);
            body.Write(u16);
            body.Write(extBytes);
            return WrapHandshakeMsg(0x02, body.ToArray());
        }

        private static byte[] BuildEncryptedExtensions(string alpn, byte[] quicTp)
        {
            byte[] pBytes = Encoding.ASCII.GetBytes(alpn);
            var alpnExt = new byte[3 + pBytes.Length];
            BinaryPrimitives.WriteUInt16BigEndian(alpnExt.AsSpan(0, 2), (ushort)(1 + pBytes.Length));
            alpnExt[2] = (byte)pBytes.Length;
            pBytes.CopyTo(alpnExt, 3);

            using var exts = new MemoryStream();
            WriteExt(exts, TlsExtensionType.ApplicationLayerProtocolNegotiation, alpnExt);
            WriteExt(exts, TlsExtensionType.QuicTransportParameters, quicTp);
            byte[] extBytes = exts.ToArray();
            var body = new byte[2 + extBytes.Length];
            BinaryPrimitives.WriteUInt16BigEndian(body.AsSpan(0, 2), (ushort)extBytes.Length);
            extBytes.CopyTo(body, 2);
            return WrapHandshakeMsg(0x08, body);
        }

        private static byte[] BuildCertificateMessage(byte[][] derChain)
        {
            using var listMs = new MemoryStream();
            Span<byte> u16 = stackalloc byte[2];
            foreach (byte[] der in derChain)
            {
                listMs.WriteByte((byte)(der.Length >> 16));
                listMs.WriteByte((byte)(der.Length >> 8));
                listMs.WriteByte((byte)der.Length);
                listMs.Write(der);
                BinaryPrimitives.WriteUInt16BigEndian(u16, 0);
                listMs.Write(u16);
            }
            byte[] listBytes = listMs.ToArray();
            var body = new byte[4 + listBytes.Length];
            body[0] = 0x00;
            body[1] = (byte)(listBytes.Length >> 16);
            body[2] = (byte)(listBytes.Length >> 8);
            body[3] = (byte)listBytes.Length;
            listBytes.CopyTo(body, 4);
            return WrapHandshakeMsg(0x0B, body);
        }

        private static byte[] BuildCertificateVerify(ECDsa leafKey, byte[] transcriptHash)
        {
            ReadOnlySpan<byte> prefix = "TLS 1.3, server CertificateVerify"u8;
            var signedContent = new byte[64 + prefix.Length + 1 + transcriptHash.Length];
            signedContent.AsSpan(0, 64).Fill(0x20);
            prefix.CopyTo(signedContent.AsSpan(64));
            signedContent[64 + prefix.Length] = 0x00;
            transcriptHash.CopyTo(signedContent.AsSpan(64 + prefix.Length + 1));

            byte[] sig = leafKey.SignData(signedContent, HashAlgorithmName.SHA256, DSASignatureFormat.Rfc3279DerSequence);
            var body = new byte[4 + sig.Length];
            BinaryPrimitives.WriteUInt16BigEndian(body.AsSpan(0, 2), SignatureSchemeId.EcdsaSecp256r1Sha256);
            BinaryPrimitives.WriteUInt16BigEndian(body.AsSpan(2, 2), (ushort)sig.Length);
            sig.CopyTo(body, 4);
            return WrapHandshakeMsg(0x0F, body);
        }

        private static void WriteExt(MemoryStream ms, ushort type, byte[] data)
        {
            Span<byte> u16 = stackalloc byte[2];
            BinaryPrimitives.WriteUInt16BigEndian(u16, type);
            ms.Write(u16);
            BinaryPrimitives.WriteUInt16BigEndian(u16, (ushort)data.Length);
            ms.Write(u16);
            ms.Write(data);
        }

        private static byte[] WrapHandshakeMsg(byte msgType, ReadOnlySpan<byte> body)
        {
            var msg = new byte[4 + body.Length];
            msg[0] = msgType;
            msg[1] = (byte)(body.Length >> 16);
            msg[2] = (byte)(body.Length >> 8);
            msg[3] = (byte)body.Length;
            body.CopyTo(msg.AsSpan(4));
            return msg;
        }

        public ValueTask DisposeAsync() => ValueTask.CompletedTask;
    }

    private static async Task WaitUntilAsync(Func<bool> predicate, CancellationToken ct)
    {
        for (int i = 0; i < 200; i++)
        {
            if (predicate())
                return;
            await Task.Delay(10, ct).ConfigureAwait(false);
        }
        Assert.True(predicate(), "Condition did not become true within timeout.");
    }

    private static async Task IgnoreCancelAsync(Task task)
    {
        try
        {
            await task.ConfigureAwait(false);
        }
        catch
        {
            // Ignore shutdown cancellations on test server tasks.
        }
    }

    private static X509Certificate2 CreateTestCa(ECDsa key, string subject)
    {
        var req = new CertificateRequest(subject, key, HashAlgorithmName.SHA256);
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(true, false, 0, true));
        req.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.KeyCertSign | X509KeyUsageFlags.DigitalSignature | X509KeyUsageFlags.CrlSign, true));
        req.CertificateExtensions.Add(new X509SubjectKeyIdentifierExtension(req.PublicKey, false));
        DateTimeOffset now = DateTimeOffset.UtcNow;
        return req.CreateSelfSigned(now.AddDays(-1), now.AddDays(30));
    }

    private static X509Certificate2 CreateTestLeaf(ECDsa leafKey, X509Certificate2 caCert, string dnsName)
    {
        var req = new CertificateRequest($"CN={dnsName}", leafKey, HashAlgorithmName.SHA256);
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, true));
        req.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.DigitalSignature | X509KeyUsageFlags.KeyEncipherment, true));
        req.CertificateExtensions.Add(new X509EnhancedKeyUsageExtension(new OidCollection { new Oid("1.3.6.1.5.5.7.3.1") }, false));
        var san = new SubjectAlternativeNameBuilder();
        san.AddDnsName(dnsName);
        san.AddIpAddress(IPAddress.Loopback);
        req.CertificateExtensions.Add(san.Build());
        req.CertificateExtensions.Add(new X509SubjectKeyIdentifierExtension(req.PublicKey, false));

        DateTimeOffset now = DateTimeOffset.UtcNow;
        Span<byte> serial = stackalloc byte[16];
        RandomNumberGenerator.Fill(serial);
        serial[0] = (byte)((serial[0] & 0x7F) | 0x01);
        using X509Certificate2 rawLeaf = req.Create(caCert, now.AddHours(-1), now.AddDays(7), serial);
        using X509Certificate2 withKey = rawLeaf.CopyWithPrivateKey(leafKey);
        byte[] pfx = withKey.Export(X509ContentType.Pfx);
        return new X509Certificate2(pfx, (string?)null, X509KeyStorageFlags.Exportable);
    }
}
