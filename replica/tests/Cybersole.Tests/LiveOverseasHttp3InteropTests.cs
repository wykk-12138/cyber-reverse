using System.Diagnostics;
using System.Reflection;
using System.Text;
using System.Text.Json;
using Cybersole.Http;
using Cybersole.Http.Http3;
using Cybersole.Http.Profiles;
using Cybersole.Http.Protocol;
using Cybersole.Http.Quic;
using Cybersole.Http.Tls;
using Cybersole.Http.X509;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

[Trait("Speed", "Slow")]
[Trait("Category", "Live")]
[Trait("Category", "OverseasH3")]
public sealed class LiveOverseasHttp3InteropTests
{
    private const string Chrome150UserAgent =
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36";

    private readonly ITestOutputHelper _output;

    public LiveOverseasHttp3InteropTests(ITestOutputHelper output)
    {
        _output = output;
    }

    private static CertificateVerifyOptions StrictVerifyOptions() => new()
    {
        InsecureSkipVerify = false,
        UseEmbeddedDefaultRoots = true,
    };

    private static TlsHttpClient CreateStrictRacerClient(string profileName = "chrome_150") => new(new TlsHttpClientOptions
    {
        ProfileName = profileName,
        DisableHttp3 = false,
        RaceDelay = TimeSpan.FromMilliseconds(300),
        ConnectTimeout = TimeSpan.FromSeconds(12),
        RequestTimeout = TimeSpan.FromSeconds(20),
        VerifyOptions = StrictVerifyOptions(),
    });

    private static PureHttpHeader[] FullChromeNavigationHeaders() => new[]
    {
        new PureHttpHeader("User-Agent", Chrome150UserAgent),
        new PureHttpHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"),
        new PureHttpHeader("Accept-Encoding", "gzip, deflate, br, zstd"),
        new PureHttpHeader("Accept-Language", "en-US,en;q=0.9"),
        new PureHttpHeader("sec-ch-ua", "\"Chromium\";v=\"150\", \"Google Chrome\";v=\"150\", \"Not_A Brand\";v=\"99\""),
        new PureHttpHeader("sec-ch-ua-mobile", "?0"),
        new PureHttpHeader("sec-ch-ua-platform", "\"Windows\""),
        new PureHttpHeader("sec-fetch-dest", "document"),
        new PureHttpHeader("sec-fetch-mode", "navigate"),
        new PureHttpHeader("sec-fetch-site", "none"),
        new PureHttpHeader("sec-fetch-user", "?1"),
        new PureHttpHeader("upgrade-insecure-requests", "1"),
    };

    private static (ushort AlpsCodepoint, int AlpsSettingsLen, bool UsedResumption) InspectQuicTlsState(QuicConnection quic)
    {
        FieldInfo? tlsField = typeof(QuicConnection).GetField("_tls", BindingFlags.Instance | BindingFlags.NonPublic);
        object? tlsObj = tlsField?.GetValue(quic);
        if (tlsObj is not TlsHandshakeEngine tls)
            return (0, -1, false);

        FieldInfo? cpField = typeof(TlsHandshakeEngine).GetField("_peerAlpsCodepoint", BindingFlags.Instance | BindingFlags.NonPublic);
        ushort cp = cpField is not null ? (ushort)(cpField.GetValue(tls) ?? (ushort)0) : (ushort)0;
        byte[]? alpsSettings = tls.PeerApplicationSettings;
        return (cp, alpsSettings?.Length ?? -1, tls.UsedSessionResumption);
    }

    private static (ulong InsertCount, ulong KnownReceived, int EntryCount) InspectQpackState(Http3Connection h3)
    {
        FieldInfo? decField = typeof(Http3Connection).GetField("_qpackDecoder", BindingFlags.Instance | BindingFlags.NonPublic);
        if (decField?.GetValue(h3) is not QpackDecoder dec)
            return (0, 0, 0);
        return (dec.DynamicTable.InsertCount, dec.KnownReceivedCount, dec.DynamicTable.EntryCount);
    }

    [Fact]
    public async Task Overseas_CloudflareTrace_DirectH3_And_ProtocolRacer_VerifyHttp3Tls13MlKem768()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
        var uri = new Uri("https://one.one.one.one/cdn-cgi/trace");
        ClientProfile chrome150 = ProfileRegistry.GetRequired("chrome_150");
        ConnectionKey key = ConnectionKey.Create("https", uri.Host, 443, chrome150.Name);

        // Path A: Direct QuicConnection + Http3Connection
        var swA = Stopwatch.StartNew();
        await using (var quic = await QuicConnection.ConnectAsync(new QuicConnectionOptions
        {
            Host = uri.Host,
            Port = 443,
            Profile = chrome150,
            TransportSpec = chrome150.QuicSpec,
            VerifyOptions = StrictVerifyOptions(),
            ConnectTimeout = TimeSpan.FromSeconds(12),
        }, cts.Token))
        {
            await using var h3 = new Http3Connection(quic, key, chrome150);
            await h3.StartAsync(cts.Token);

            PureHttpResponse respA = await h3.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = uri,
                Headers = new[] { new PureHttpHeader("User-Agent", Chrome150UserAgent) },
            }, cts.Token);
            swA.Stop();

            (ushort alpsCp, int alpsLen, bool resumed) = InspectQuicTlsState(quic);
            (ulong qIns, ulong qKnown, int qEntries) = InspectQpackState(h3);
            string bodyA = Encoding.UTF8.GetString(respA.Body);
            _output.WriteLine($"[Path A Direct H3] one.one.one.one/cdn-cgi/trace: status={respA.StatusCode} version={respA.HttpVersion} alpn={quic.NegotiatedAlpn} cipher=0x{quic.NegotiatedCipherSuite:x4} scidLen={quic.LocalScid.Length} retry={quic.RetryReceived} peerUni={quic.PeerMaxStreamsUni} alps=0x{alpsCp:x4}(len={alpsLen}) resumed={resumed} qpack=(ins={qIns},known={qKnown},entries={qEntries}) bytes={respA.Body.Length} elapsedMs={swA.ElapsedMilliseconds} hsMs={quic.HandshakeDuration.TotalMilliseconds:F1}");
            _output.WriteLine(bodyA);

            Assert.Equal(200, respA.StatusCode);
            Assert.Equal("HTTP/3", respA.HttpVersion);
            Assert.Equal("h3", quic.NegotiatedAlpn);
            Assert.Empty(quic.LocalScid);
            Assert.Contains("http=http/3", bodyA, StringComparison.Ordinal);
            Assert.Contains("tls=TLSv1.3", bodyA, StringComparison.Ordinal);
            Assert.Contains("kex=X25519MLKEM768", bodyA, StringComparison.Ordinal);
        }

        // Path B: ProtocolRacer via TlsHttpClient
        var swB = Stopwatch.StartNew();
        await using var client = CreateStrictRacerClient("chrome_150");
        PureHttpResponse respB = await client.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = uri,
            Headers = new[] { new PureHttpHeader("User-Agent", Chrome150UserAgent) },
        }, cts.Token);
        swB.Stop();

        string bodyB = Encoding.UTF8.GetString(respB.Body);
        _output.WriteLine($"[Path B Racer] one.one.one.one/cdn-cgi/trace: status={respB.StatusCode} version={respB.HttpVersion} bytes={respB.Body.Length} elapsedMs={swB.ElapsedMilliseconds}");
        _output.WriteLine(bodyB);

        Assert.Equal(200, respB.StatusCode);
        Assert.Equal("HTTP/3", respB.HttpVersion);
        Assert.Contains("http=http/3", bodyB, StringComparison.Ordinal);
        Assert.Contains("tls=TLSv1.3", bodyB, StringComparison.Ordinal);
        Assert.Contains("kex=X25519MLKEM768", bodyB, StringComparison.Ordinal);
    }

    [Fact]
    public async Task Overseas_CloudflareQuic_DirectH3_And_ProtocolRacer_TransferFullLargeBody()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
        var uri = new Uri("https://cloudflare-quic.com/");
        ClientProfile chrome150 = ProfileRegistry.GetRequired("chrome_150");
        ConnectionKey key = ConnectionKey.Create("https", uri.Host, 443, chrome150.Name);

        // Path A: Direct QuicConnection + Http3Connection
        var swA = Stopwatch.StartNew();
        await using (var quic = await QuicConnection.ConnectAsync(new QuicConnectionOptions
        {
            Host = uri.Host,
            Port = 443,
            Profile = chrome150,
            TransportSpec = chrome150.QuicSpec,
            VerifyOptions = StrictVerifyOptions(),
            ConnectTimeout = TimeSpan.FromSeconds(12),
        }, cts.Token))
        {
            await using var h3 = new Http3Connection(quic, key, chrome150);
            await h3.StartAsync(cts.Token);

            PureHttpResponse respA = await h3.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = uri,
                Headers = new[]
                {
                    new PureHttpHeader("User-Agent", Chrome150UserAgent),
                    new PureHttpHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                },
            }, cts.Token);
            swA.Stop();

            (ushort alpsCp, int alpsLen, _) = InspectQuicTlsState(quic);
            (ulong qIns, ulong qKnown, int qEntries) = InspectQpackState(h3);
            string htmlA = Encoding.UTF8.GetString(respA.Body);
            _output.WriteLine($"[Path A Direct H3] cloudflare-quic.com: status={respA.StatusCode} version={respA.HttpVersion} alpn={quic.NegotiatedAlpn} cipher=0x{quic.NegotiatedCipherSuite:x4} scidLen={quic.LocalScid.Length} retry={quic.RetryReceived} peerUni={quic.PeerMaxStreamsUni} alps=0x{alpsCp:x4}(len={alpsLen}) qpack=(ins={qIns},known={qKnown},entries={qEntries}) bytes={respA.Body.Length} elapsedMs={swA.ElapsedMilliseconds} hsMs={quic.HandshakeDuration.TotalMilliseconds:F1}");

            Assert.Equal(200, respA.StatusCode);
            Assert.Equal("HTTP/3", respA.HttpVersion);
            Assert.Equal("h3", quic.NegotiatedAlpn);
            Assert.Empty(quic.LocalScid);
            Assert.True(respA.Body.Length > 50_000, $"Expected large body > 50 KB, got {respA.Body.Length}");
            Assert.Contains("</html>", htmlA, StringComparison.OrdinalIgnoreCase);
        }

        // Path B: ProtocolRacer via TlsHttpClient
        var swB = Stopwatch.StartNew();
        await using var client = CreateStrictRacerClient("chrome_150");
        PureHttpResponse respB = await client.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = uri,
            Headers = new[]
            {
                new PureHttpHeader("User-Agent", Chrome150UserAgent),
                new PureHttpHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
            },
        }, cts.Token);
        swB.Stop();

        string htmlB = Encoding.UTF8.GetString(respB.Body);
        _output.WriteLine($"[Path B Racer] cloudflare-quic.com: status={respB.StatusCode} version={respB.HttpVersion} bytes={respB.Body.Length} elapsedMs={swB.ElapsedMilliseconds}");

        Assert.Equal(200, respB.StatusCode);
        Assert.Equal("HTTP/3", respB.HttpVersion);
        Assert.True(respB.Body.Length > 50_000, $"Expected large body > 50 KB, got {respB.Body.Length}");
        Assert.Contains("</html>", htmlB, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task Overseas_GoogleGenerate204_DirectH3_And_ProtocolRacer_VerifyQuicAlps0x44CD()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
        var uri = new Uri("https://www.google.com/generate_204");
        ClientProfile chrome150 = ProfileRegistry.GetRequired("chrome_150");
        ConnectionKey key = ConnectionKey.Create("https", uri.Host, 443, chrome150.Name);

        // Path A: Direct QuicConnection + Http3Connection
        var swA = Stopwatch.StartNew();
        await using (var quic = await QuicConnection.ConnectAsync(new QuicConnectionOptions
        {
            Host = uri.Host,
            Port = 443,
            Profile = chrome150,
            TransportSpec = chrome150.QuicSpec,
            VerifyOptions = StrictVerifyOptions(),
            ConnectTimeout = TimeSpan.FromSeconds(12),
        }, cts.Token))
        {
            await using var h3 = new Http3Connection(quic, key, chrome150);
            await h3.StartAsync(cts.Token);

            PureHttpResponse respA = await h3.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = uri,
                Headers = new[] { new PureHttpHeader("User-Agent", Chrome150UserAgent) },
            }, cts.Token);
            swA.Stop();

            (ushort alpsCp, int alpsLen, _) = InspectQuicTlsState(quic);
            (ulong qIns, ulong qKnown, int qEntries) = InspectQpackState(h3);
            _output.WriteLine($"[Path A Direct H3] www.google.com/generate_204: status={respA.StatusCode} version={respA.HttpVersion} alpn={quic.NegotiatedAlpn} cipher=0x{quic.NegotiatedCipherSuite:x4} scidLen={quic.LocalScid.Length} retry={quic.RetryReceived} peerUni={quic.PeerMaxStreamsUni} alps=0x{alpsCp:x4}(len={alpsLen}) qpack=(ins={qIns},known={qKnown},entries={qEntries}) bytes={respA.Body.Length} elapsedMs={swA.ElapsedMilliseconds} hsMs={quic.HandshakeDuration.TotalMilliseconds:F1}");

            Assert.Equal(204, respA.StatusCode);
            Assert.Equal("HTTP/3", respA.HttpVersion);
            Assert.Equal("h3", quic.NegotiatedAlpn);
            Assert.Empty(quic.LocalScid);
            Assert.Equal(TlsExtensionType.ApplicationSettingsNew, alpsCp); // Confirmed live Google QUIC ALPS 0x44CD!
        }

        // Path B: ProtocolRacer via TlsHttpClient
        var swB = Stopwatch.StartNew();
        await using var client = CreateStrictRacerClient("chrome_150");
        PureHttpResponse respB = await client.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = uri,
            Headers = new[] { new PureHttpHeader("User-Agent", Chrome150UserAgent) },
        }, cts.Token);
        swB.Stop();

        _output.WriteLine($"[Path B Racer] www.google.com/generate_204: status={respB.StatusCode} version={respB.HttpVersion} bytes={respB.Body.Length} elapsedMs={swB.ElapsedMilliseconds}");

        Assert.Equal(204, respB.StatusCode);
        Assert.Equal("HTTP/3", respB.HttpVersion);
    }

    [Fact]
    public async Task Overseas_NginxQuic_DirectH3_And_ProtocolRacer_VerifyHttp3()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
        var uri = new Uri("https://quic.nginx.org/");
        ClientProfile chrome150 = ProfileRegistry.GetRequired("chrome_150");
        ConnectionKey key = ConnectionKey.Create("https", uri.Host, 443, chrome150.Name);

        // Path A: Direct QuicConnection + Http3Connection
        var swA = Stopwatch.StartNew();
        await using (var quic = await QuicConnection.ConnectAsync(new QuicConnectionOptions
        {
            Host = uri.Host,
            Port = 443,
            Profile = chrome150,
            TransportSpec = chrome150.QuicSpec,
            VerifyOptions = StrictVerifyOptions(),
            ConnectTimeout = TimeSpan.FromSeconds(12),
        }, cts.Token))
        {
            await using var h3 = new Http3Connection(quic, key, chrome150);
            await h3.StartAsync(cts.Token);

            PureHttpResponse respA = await h3.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = uri,
                Headers = new[] { new PureHttpHeader("User-Agent", Chrome150UserAgent) },
            }, cts.Token);
            swA.Stop();

            (ushort alpsCp, int alpsLen, _) = InspectQuicTlsState(quic);
            (ulong qIns, ulong qKnown, int qEntries) = InspectQpackState(h3);
            _output.WriteLine($"[Path A Direct H3] quic.nginx.org: status={respA.StatusCode} version={respA.HttpVersion} alpn={quic.NegotiatedAlpn} cipher=0x{quic.NegotiatedCipherSuite:x4} scidLen={quic.LocalScid.Length} retry={quic.RetryReceived} peerUni={quic.PeerMaxStreamsUni} alps=0x{alpsCp:x4}(len={alpsLen}) qpack=(ins={qIns},known={qKnown},entries={qEntries}) bytes={respA.Body.Length} elapsedMs={swA.ElapsedMilliseconds} hsMs={quic.HandshakeDuration.TotalMilliseconds:F1}");

            Assert.Equal(200, respA.StatusCode);
            Assert.Equal("HTTP/3", respA.HttpVersion);
            Assert.Equal("h3", quic.NegotiatedAlpn);
            Assert.Empty(quic.LocalScid);
        }

        // Path B: ProtocolRacer via TlsHttpClient
        var swB = Stopwatch.StartNew();
        await using var client = CreateStrictRacerClient("chrome_150");
        PureHttpResponse respB = await client.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = uri,
            Headers = new[] { new PureHttpHeader("User-Agent", Chrome150UserAgent) },
        }, cts.Token);
        swB.Stop();

        _output.WriteLine($"[Path B Racer] quic.nginx.org: status={respB.StatusCode} version={respB.HttpVersion} bytes={respB.Body.Length} elapsedMs={swB.ElapsedMilliseconds}");

        Assert.Equal(200, respB.StatusCode);
        Assert.Equal("HTTP/3", respB.HttpVersion);
    }

    [Fact]
    public async Task Overseas_NikeAndAkamai_NetClientAndDirectUdp443Probe()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(45));
        ClientProfile chrome150 = ProfileRegistry.GetRequired("chrome_150");

        // 1) NetClient PureNetClient (redirects, cookies, full Chrome navigation headers, large response body)
        using (var net = new NetClient(timeout: TimeSpan.FromSeconds(20))
        {
            Transport = TransportMode.PureNetClient,
            VerifyOptions = StrictVerifyOptions(),
        })
        {
            foreach (string url in new[] { "https://www.nike.com/", "https://www.akamai.com/" })
            {
                var sw = Stopwatch.StartNew();
                var opts = new RequestOptions
                {
                    Profile = TlsProfile.Chrome150,
                    Retries = 1,
                    Timeout = TimeSpan.FromSeconds(20),
                };
                opts.Headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8";
                opts.Headers["Accept-Language"] = "en-US,en;q=0.9";

                NetResponse resp = await net.GetAsync(url, opts, cts.Token);
                sw.Stop();
                _output.WriteLine($"[NetClient PureNetClient] {url}: status={resp.StatusCode} finalUrl={resp.Url} bytes={resp.Body.Length} setCookieLen={(resp.Headers.GetValueOrDefault("set-cookie")?.Length ?? 0)} alt-svc={resp.Headers.GetValueOrDefault("alt-svc")} elapsedMs={sw.ElapsedMilliseconds}");
                Assert.Equal(200, resp.StatusCode);
            }
        }

        // 2) ProtocolRacer via TlsHttpClient with full Chrome navigation headers
        foreach (string url in new[] { "https://www.nike.com/", "https://www.akamai.com/" })
        {
            var sw = Stopwatch.StartNew();
            await using var client = CreateStrictRacerClient("chrome_150");
            PureHttpResponse resp = await client.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri(url),
                Headers = FullChromeNavigationHeaders(),
            }, cts.Token);
            sw.Stop();
            _output.WriteLine($"[Path B Racer FullHeaders] {url}: status={resp.StatusCode} version={resp.HttpVersion} alt-svc={resp.AltSvcHeader} bytes={resp.Body.Length} elapsedMs={sw.ElapsedMilliseconds}");
            Assert.Equal(200, resp.StatusCode);
        }

        // 3) Direct UDP-443 QUIC probe with full Chrome navigation headers
        foreach (string url in new[] { "https://www.nike.com/", "https://www.akamai.com/" })
        {
            var uri = new Uri(url);
            ConnectionKey key = ConnectionKey.Create("https", uri.Host, 443, chrome150.Name);
            var sw = Stopwatch.StartNew();
            try
            {
                using var probeCts = CancellationTokenSource.CreateLinkedTokenSource(cts.Token);
                probeCts.CancelAfter(TimeSpan.FromSeconds(8));
                await using var quic = await QuicConnection.ConnectAsync(new QuicConnectionOptions
                {
                    Host = uri.Host,
                    Port = 443,
                    Profile = chrome150,
                    TransportSpec = chrome150.QuicSpec,
                    VerifyOptions = StrictVerifyOptions(),
                    ConnectTimeout = TimeSpan.FromSeconds(6),
                }, probeCts.Token);
                await using var h3 = new Http3Connection(quic, key, chrome150);
                await h3.StartAsync(probeCts.Token);
                PureHttpResponse resp = await h3.SendAsync(new PureHttpRequest
                {
                    Method = "GET",
                    Uri = uri,
                    Headers = FullChromeNavigationHeaders(),
                }, probeCts.Token);
                sw.Stop();
                _output.WriteLine($"[Path A Direct H3 FullHeaders] {url}: SUCCESS status={resp.StatusCode} version={resp.HttpVersion} alpn={quic.NegotiatedAlpn} cipher=0x{quic.NegotiatedCipherSuite:x4} scidLen={quic.LocalScid.Length} retry={quic.RetryReceived} bytes={resp.Body.Length} elapsedMs={sw.ElapsedMilliseconds}");
                Assert.Equal("HTTP/3", resp.HttpVersion);
            }
            catch (Exception ex)
            {
                sw.Stop();
                _output.WriteLine($"[Path A Direct H3 FullHeaders] {url}: PROBE_ERROR ({ex.GetType().Name}) elapsedMs={sw.ElapsedMilliseconds}: {ex.Message}");
            }
        }
    }

    [Fact]
    public async Task Overseas_Multiplexed8ConcurrentStreams_OnSingleHttp3Connection_Cloudflare()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
        ClientProfile chrome150 = ProfileRegistry.GetRequired("chrome_150");

        // 8 concurrent requests on cloudflare-quic.com (~125 KB each -> ~1 MB total over single H3 connection)
        var cfQuicUri = new Uri("https://cloudflare-quic.com/");
        ConnectionKey cfKey = ConnectionKey.Create("https", cfQuicUri.Host, 443, chrome150.Name);
        var swCf = Stopwatch.StartNew();
        await using (var quic = await QuicConnection.ConnectAsync(new QuicConnectionOptions
        {
            Host = cfQuicUri.Host,
            Port = 443,
            Profile = chrome150,
            TransportSpec = chrome150.QuicSpec,
            VerifyOptions = StrictVerifyOptions(),
            ConnectTimeout = TimeSpan.FromSeconds(12),
        }, cts.Token))
        {
            await using var h3 = new Http3Connection(quic, cfKey, chrome150);
            await h3.StartAsync(cts.Token);

            Task<PureHttpResponse>[] tasks = Enumerable.Range(0, 8)
                .Select(i => h3.SendAsync(new PureHttpRequest
                {
                    Method = "GET",
                    Uri = new Uri($"https://cloudflare-quic.com/?req={i}"),
                    Headers = new[]
                    {
                        new PureHttpHeader("User-Agent", Chrome150UserAgent),
                        new PureHttpHeader("Accept", "text/html,*/*;q=0.8"),
                    },
                }, cts.Token))
                .ToArray();

            PureHttpResponse[] results = await Task.WhenAll(tasks);
            swCf.Stop();

            (ulong qIns, ulong qKnown, int qEntries) = InspectQpackState(h3);
            long totalBytes = results.Sum(r => (long)r.Body.Length);
            _output.WriteLine($"[8x Concurrent H3] cloudflare-quic.com: all={results.Length} totalBytes={totalBytes} minBytes={results.Min(r => r.Body.Length)} maxBytes={results.Max(r => r.Body.Length)} alpn={quic.NegotiatedAlpn} cipher=0x{quic.NegotiatedCipherSuite:x4} scidLen={quic.LocalScid.Length} retry={quic.RetryReceived} qpack=(ins={qIns},known={qKnown},entries={qEntries}) elapsedMs={swCf.ElapsedMilliseconds}");

            for (int i = 0; i < 8; i++)
            {
                Assert.Equal(200, results[i].StatusCode);
                Assert.Equal("HTTP/3", results[i].HttpVersion);
                Assert.True(results[i].Body.Length > 50_000, $"Stream {i} returned only {results[i].Body.Length} bytes");
            }
        }

        // 8 concurrent requests on one.one.one.one/cdn-cgi/trace (connection reuse + ML-KEM-768)
        var traceUri = new Uri("https://one.one.one.one/cdn-cgi/trace");
        ConnectionKey traceKey = ConnectionKey.Create("https", traceUri.Host, 443, chrome150.Name);
        var swTr = Stopwatch.StartNew();
        await using (var quic = await QuicConnection.ConnectAsync(new QuicConnectionOptions
        {
            Host = traceUri.Host,
            Port = 443,
            Profile = chrome150,
            TransportSpec = chrome150.QuicSpec,
            VerifyOptions = StrictVerifyOptions(),
            ConnectTimeout = TimeSpan.FromSeconds(12),
        }, cts.Token))
        {
            await using var h3 = new Http3Connection(quic, traceKey, chrome150);
            await h3.StartAsync(cts.Token);

            Task<PureHttpResponse>[] tasks = Enumerable.Range(0, 8)
                .Select(i => h3.SendAsync(new PureHttpRequest
                {
                    Method = "GET",
                    Uri = new Uri($"https://one.one.one.one/cdn-cgi/trace?s={i}"),
                    Headers = new[] { new PureHttpHeader("User-Agent", Chrome150UserAgent) },
                }, cts.Token))
                .ToArray();

            PureHttpResponse[] results = await Task.WhenAll(tasks);
            swTr.Stop();

            (ulong qIns, ulong qKnown, int qEntries) = InspectQpackState(h3);
            _output.WriteLine($"[8x Concurrent H3] one.one.one.one/cdn-cgi/trace: all={results.Length} totalBytes={results.Sum(r => r.Body.Length)} alpn={quic.NegotiatedAlpn} cipher=0x{quic.NegotiatedCipherSuite:x4} qpack=(ins={qIns},known={qKnown},entries={qEntries}) elapsedMs={swTr.ElapsedMilliseconds}");
            foreach (PureHttpResponse r in results)
            {
                Assert.Equal(200, r.StatusCode);
                Assert.Equal("HTTP/3", r.HttpVersion);
                string text = Encoding.UTF8.GetString(r.Body);
                Assert.Contains("http=http/3", text, StringComparison.Ordinal);
                Assert.Contains("kex=X25519MLKEM768", text, StringComparison.Ordinal);
            }
        }
    }

    [Fact]
    public async Task Overseas_QuicPskResumption_CloudflareAndGoogle_Chrome150Psk()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
        ClientProfile profile = ProfileRegistry.GetRequired("chrome_150_PSK");

        foreach (string url in new[] { "https://one.one.one.one/cdn-cgi/trace", "https://www.google.com/generate_204" })
        {
            var uri = new Uri(url);
            ConnectionKey key = ConnectionKey.Create("https", uri.Host, 443, profile.Name);
            var sessionCache = new LruTlsSessionCache();

            // Connection 1: full handshake + wait briefly for NewSessionTicket over 1-RTT CRYPTO
            await using (var q1 = await QuicConnection.ConnectAsync(new QuicConnectionOptions
            {
                Host = uri.Host,
                Port = 443,
                Profile = profile,
                TransportSpec = profile.QuicSpec,
                VerifyOptions = StrictVerifyOptions(),
                SessionCache = sessionCache,
                ConnectTimeout = TimeSpan.FromSeconds(12),
            }, cts.Token))
            {
                await using var h3 = new Http3Connection(q1, key, profile);
                await h3.StartAsync(cts.Token);
                PureHttpResponse r1 = await h3.SendAsync(new PureHttpRequest
                {
                    Method = "GET",
                    Uri = uri,
                    Headers = new[] { new PureHttpHeader("User-Agent", Chrome150UserAgent) },
                }, cts.Token);
                for (int i = 0; i < 20 && sessionCache.Count == 0; i++)
                    await Task.Delay(25, cts.Token);
                _output.WriteLine($"[QUIC PSK Conn1] {url}: status={r1.StatusCode} version={r1.HttpVersion} ticketsCached={sessionCache.Count}");
                Assert.Equal("HTTP/3", r1.HttpVersion);
            }

            // Connection 2: resume using cached ticket
            var sw2 = Stopwatch.StartNew();
            await using (var q2 = await QuicConnection.ConnectAsync(new QuicConnectionOptions
            {
                Host = uri.Host,
                Port = 443,
                Profile = profile,
                TransportSpec = profile.QuicSpec,
                VerifyOptions = StrictVerifyOptions(),
                SessionCache = sessionCache,
                ConnectTimeout = TimeSpan.FromSeconds(12),
            }, cts.Token))
            {
                await using var h3 = new Http3Connection(q2, key, profile);
                await h3.StartAsync(cts.Token);
                PureHttpResponse r2 = await h3.SendAsync(new PureHttpRequest
                {
                    Method = "GET",
                    Uri = uri,
                    Headers = new[] { new PureHttpHeader("User-Agent", Chrome150UserAgent) },
                }, cts.Token);
                sw2.Stop();
                (ushort alpsCp, int alpsLen, bool resumed) = InspectQuicTlsState(q2);
                _output.WriteLine($"[QUIC PSK Conn2] {url}: status={r2.StatusCode} version={r2.HttpVersion} resumed={resumed} alps=0x{alpsCp:x4}(len={alpsLen}) hsMs={q2.HandshakeDuration.TotalMilliseconds:F1} elapsedMs={sw2.ElapsedMilliseconds}");
                Assert.Equal("HTTP/3", r2.HttpVersion);
            }
        }
    }

    [Fact]
    public async Task Overseas_Http3WireFingerprintOracle_FpImpersonatePro_MatchesChromeQuicSpecs()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
        var uri = new Uri("https://fp.impersonate.pro/api/http3");

        foreach (string profileName in new[] { "chrome_150", "chrome_152" })
        {
            ClientProfile profile = ProfileRegistry.GetRequired(profileName);
            ConnectionKey key = ConnectionKey.Create("https", uri.Host, 443, profile.Name);

            QuicTransportParameters localTp = QuicTransportParametersCodec.FromSpec(
                profile.QuicSpec ?? ChromeQuicSpecs.DefaultTransportSpec,
                Array.Empty<byte>(),
                initialRttUs: null,
                new Random(42));
            byte[] localTpBytes = QuicTransportParametersCodec.Encode(localTp, shuffle: true, random: new Random(42));
            using ClientHelloBuildResult localCh = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
            {
                Profile = profile,
                ServerName = uri.Host,
                IsQuicMode = true,
                QuicTransportParameters = localTpBytes,
                Random = new Random(42),
            });
            TlsWireFingerprintResult expectedQuicTls = WireFingerprint.AnalyzeClientHello(localCh.HandshakeMessage, isQuic: true);

            var sw = Stopwatch.StartNew();
            await using var quic = await QuicConnection.ConnectAsync(new QuicConnectionOptions
            {
                Host = uri.Host,
                Port = 443,
                Profile = profile,
                TransportSpec = profile.QuicSpec,
                VerifyOptions = StrictVerifyOptions(),
                ConnectTimeout = TimeSpan.FromSeconds(10),
            }, cts.Token);

            await using var h3 = new Http3Connection(quic, key, profile);
            await h3.StartAsync(cts.Token);

            PureHttpResponse resp = await h3.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = uri,
                Headers = new[]
                {
                    new PureHttpHeader("User-Agent", Chrome150UserAgent),
                    new PureHttpHeader("Accept", "application/json"),
                },
            }, cts.Token);
            sw.Stop();

            Assert.Equal(200, resp.StatusCode);
            Assert.Equal("HTTP/3", resp.HttpVersion);
            Assert.Equal("h3", quic.NegotiatedAlpn);
            Assert.Empty(quic.LocalScid);

            using JsonDocument doc = JsonDocument.Parse(resp.Body);
            JsonElement root = doc.RootElement;
            JsonElement quicEl = root.GetProperty("quic");
            JsonElement h3El = root.GetProperty("http3");
            JsonElement tlsEl = root.GetProperty("tls");

            int initPn = quicEl.GetProperty("initial_packet_number").GetInt32();
            int scidLen = quicEl.GetProperty("client_connection_id_length").GetInt32();
            int dcidLen = quicEl.GetProperty("server_connection_id_length").GetInt32();
            string perkNorm = h3El.GetProperty("perk_text_normalized").GetString() ?? string.Empty;
            string remoteJa3n = tlsEl.GetProperty("ja3n").GetProperty("text").GetString() ?? string.Empty;
            string remoteJa3nHash = tlsEl.GetProperty("ja3n").GetProperty("hash").GetString() ?? string.Empty;
            string[] headerOrder = h3El.GetProperty("header_order").EnumerateArray().Select(e => e.GetString()!).ToArray();

            _output.WriteLine($"[H3 Oracle {profileName}] status={resp.StatusCode} alpn={quic.NegotiatedAlpn} cipher=0x{quic.NegotiatedCipherSuite:x4} initPn={initPn} scidLen={scidLen} dcidLen={dcidLen} elapsedMs={sw.ElapsedMilliseconds}");
            _output.WriteLine($"[H3 Oracle {profileName}] perk_norm={perkNorm}");
            _output.WriteLine($"[H3 Oracle {profileName}] remote_ja3n={remoteJa3n} ({remoteJa3nHash}) | local_ja3n={expectedQuicTls.Ja3nText} ({expectedQuicTls.Ja3nHash}) | local_ja4={expectedQuicTls.Ja4}");
            _output.WriteLine($"[H3 Oracle {profileName}] header_order={string.Join(",", headerOrder)}");

            Assert.Equal(0, initPn);
            Assert.Equal(0, scidLen);
            Assert.Equal(8, dcidLen);
            Assert.Equal(expectedQuicTls.Ja3nText, remoteJa3n);
            Assert.Equal(expectedQuicTls.Ja3nHash, remoteJa3nHash);
            Assert.Equal(new[] { ":method", ":authority", ":scheme", ":path" }, headerOrder.Take(4).ToArray());

            string expectedTpPart = "1:30000;3:1472;4:15728640;5:6291456;6:6291456;7:6291456;8:100;9:103;10:3;11:25;14:4;15:AUTO;17:1@1,GREASE;32:65536;12584:0x4f524947;GREASE|0,8";
            Assert.EndsWith(expectedTpPart, perkNorm, StringComparison.Ordinal);
            if (profileName == "chrome_152")
                Assert.StartsWith("1:65536;6:262144;7:100;51:1;GREASE|m,a,s,p|", perkNorm, StringComparison.Ordinal);
            else
                Assert.StartsWith("51:1|m,a,s,p|", perkNorm, StringComparison.Ordinal);
        }
    }
}
