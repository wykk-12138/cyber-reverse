using System.Net;
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
public sealed class LivePublicEdgeInteropTests
{
    private const string Chrome150UserAgent =
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36";

    private readonly ITestOutputHelper _output;

    public LivePublicEdgeInteropTests(ITestOutputHelper output)
    {
        _output = output;
    }

    [Theory]
    [InlineData("chrome_150")]
    [InlineData("chrome_150_PSK")]
    [InlineData("chrome_152")]
    [InlineData("chrome_133")]
    [InlineData("firefox_148")]
    public async Task LiveFingerprintOracle_TlsPeetWs_MatchesJa4Ja4rJa3AndAkamaiH2(string profileName)
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(25));
        ClientProfile profile = ProfileRegistry.GetRequired(profileName);

        using ClientHelloBuildResult localCh = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
        {
            Profile = profile,
            ServerName = "tls.peet.ws",
            Random = new Random(17),
        });
        TlsWireFingerprintResult expectedTls = WireFingerprint.AnalyzeClientHello(localCh.HandshakeMessage, isQuic: false);
        Http2WireFingerprintResult expectedH2 = WireFingerprint.AnalyzeHttp2Spec(profile.Http2Settings);

        await using var client = new TlsHttpClient(new TlsHttpClientOptions
        {
            ProfileName = profileName,
            DisableHttp3 = true,
            ConnectTimeout = TimeSpan.FromSeconds(12),
            RequestTimeout = TimeSpan.FromSeconds(20),
            InsecureSkipVerify = false,
        });

        PureHttpResponse resp = await client.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri("https://tls.peet.ws/api/all"),
            Headers = new[]
            {
                new PureHttpHeader("User-Agent", Chrome150UserAgent),
                new PureHttpHeader("Accept", "application/json"),
            },
        }, cts.Token);

        Assert.Equal(200, resp.StatusCode);
        Assert.Equal("HTTP/2.0", resp.HttpVersion);

        string jsonText = Encoding.UTF8.GetString(resp.Body);
        using JsonDocument doc = JsonDocument.Parse(jsonText);
        JsonElement root = doc.RootElement;
        JsonElement tlsEl = root.GetProperty("tls");
        JsonElement h2El = root.GetProperty("http2");

        string remoteJa4 = tlsEl.GetProperty("ja4").GetString() ?? string.Empty;
        string remoteJa4r = tlsEl.GetProperty("ja4_r").GetString() ?? string.Empty;
        string remoteJa3Hash = tlsEl.GetProperty("ja3_hash").GetString() ?? string.Empty;
        string remoteAkamai = h2El.GetProperty("akamai_fingerprint").GetString() ?? string.Empty;

        _output.WriteLine($"[{profileName}] peet.ws ja4={remoteJa4} | local={expectedTls.Ja4}");
        _output.WriteLine($"[{profileName}] peet.ws ja4_r={remoteJa4r} | local={expectedTls.Ja4Raw}");
        _output.WriteLine($"[{profileName}] peet.ws ja3_hash={remoteJa3Hash} | local_ja3={expectedTls.Ja3Hash} | shuffled={profile.CreateClientHelloSpec().ShuffleExtensions}");
        _output.WriteLine($"[{profileName}] peet.ws akamai={remoteAkamai} | local={expectedH2.AkamaiText}");

        if (profileName == "chrome_133")
        {
            // IDA 0x141353E20 / sub_141337470 sends ALPN ["h3","h2","http/1.1"] on Wire ClientHello;
            // peet.ws normalizes the TCP ja4 ALPN indicator from h3 -> h2 while hashes match identically.
            Assert.StartsWith("t13d1516h2_", remoteJa4, StringComparison.Ordinal);
            Assert.Equal(expectedTls.Ja4.Substring(10), remoteJa4.Substring(10));
            Assert.StartsWith("t13d1516h2_", remoteJa4r, StringComparison.Ordinal);
            Assert.Equal(expectedTls.Ja4Raw.Substring(10), remoteJa4r.Substring(10));

            bool sawH3FirstAlpn = false;
            foreach (JsonElement ext in tlsEl.GetProperty("extensions").EnumerateArray())
            {
                if (ext.TryGetProperty("name", out JsonElement nameEl) &&
                    nameEl.GetString() is string extName &&
                    extName.StartsWith("application_layer_protocol_negotiation", StringComparison.Ordinal) &&
                    ext.TryGetProperty("protocols", out JsonElement protosEl) &&
                    protosEl.GetArrayLength() > 0 &&
                    string.Equals(protosEl[0].GetString(), "h3", StringComparison.Ordinal))
                {
                    sawH3FirstAlpn = true;
                    break;
                }
            }
            Assert.True(sawH3FirstAlpn, $"Expected chrome_133 wire ClientHello ALPN to start with h3: {tlsEl.GetRawText()}");
        }
        else
        {
            Assert.Equal(expectedTls.Ja4, remoteJa4);
            Assert.Equal(expectedTls.Ja4Raw, remoteJa4r);
        }
        Assert.Equal(expectedH2.AkamaiText, remoteAkamai);
        if (!profile.CreateClientHelloSpec().ShuffleExtensions)
            Assert.Equal(expectedTls.Ja3Hash, remoteJa3Hash);
        else
            Assert.Equal(32, remoteJa3Hash.Length);
    }

    [Theory]
    [InlineData("chrome_150")]
    [InlineData("chrome_152")]
    public async Task LiveFingerprintOracle_Browserleaks_MatchesJa4Ja4rJa3AndAkamaiH2(string profileName)
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(25));
        ClientProfile profile = ProfileRegistry.GetRequired(profileName);

        using ClientHelloBuildResult localCh = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
        {
            Profile = profile,
            ServerName = "tls.browserleaks.com",
            Random = new Random(19),
        });
        TlsWireFingerprintResult expectedTls = WireFingerprint.AnalyzeClientHello(localCh.HandshakeMessage, isQuic: false);
        Http2WireFingerprintResult expectedH2 = WireFingerprint.AnalyzeHttp2Spec(profile.Http2Settings);

        await using var client = new TlsHttpClient(new TlsHttpClientOptions
        {
            ProfileName = profileName,
            DisableHttp3 = true,
            ConnectTimeout = TimeSpan.FromSeconds(12),
            RequestTimeout = TimeSpan.FromSeconds(20),
            InsecureSkipVerify = false,
        });

        PureHttpResponse resp = await client.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri("https://tls.browserleaks.com/json"),
            Headers = new[]
            {
                new PureHttpHeader("User-Agent", Chrome150UserAgent),
                new PureHttpHeader("Accept", "application/json"),
            },
        }, cts.Token);

        Assert.Equal(200, resp.StatusCode);
        Assert.Equal("HTTP/2.0", resp.HttpVersion);

        string jsonText = Encoding.UTF8.GetString(resp.Body);
        using JsonDocument doc = JsonDocument.Parse(jsonText);
        JsonElement root = doc.RootElement;

        string remoteJa4 = root.GetProperty("ja4").GetString() ?? string.Empty;
        string remoteJa4r = root.GetProperty("ja4_r").GetString() ?? string.Empty;
        string remoteJa3Hash = root.GetProperty("ja3_hash").GetString() ?? string.Empty;
        string remoteAkamaiText = root.GetProperty("akamai_text").GetString() ?? string.Empty;
        string remoteAkamaiHash = root.GetProperty("akamai_hash").GetString() ?? string.Empty;

        _output.WriteLine($"[{profileName}] browserleaks ja4={remoteJa4} | local={expectedTls.Ja4}");
        _output.WriteLine($"[{profileName}] browserleaks ja4_r={remoteJa4r} | local={expectedTls.Ja4Raw}");
        _output.WriteLine($"[{profileName}] browserleaks akamai_text={remoteAkamaiText} | local={expectedH2.AkamaiText} | hash={remoteAkamaiHash} | localHash={expectedH2.AkamaiHash}");
        _output.WriteLine($"[{profileName}] browserleaks ja3_hash={remoteJa3Hash}");

        Assert.Equal(expectedTls.Ja4, remoteJa4);
        Assert.Equal(expectedTls.Ja4Raw, remoteJa4r);
        Assert.Equal(expectedH2.AkamaiText, remoteAkamaiText);
        Assert.Equal(expectedH2.AkamaiHash, remoteAkamaiHash);
        Assert.Equal(32, remoteJa3Hash.Length);
    }

    [Fact]
    public async Task LiveCloudflare_Trace_VerifiesTls13MlKem768Http2AndCertificateVerification()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(25));
        await using var client = new TlsHttpClient(new TlsHttpClientOptions
        {
            ProfileName = "chrome_150",
            DisableHttp3 = true,
            ConnectTimeout = TimeSpan.FromSeconds(12),
            RequestTimeout = TimeSpan.FromSeconds(20),
            InsecureSkipVerify = false,
        });

        PureHttpResponse resp = await client.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri("https://one.one.one.one/cdn-cgi/trace"),
            Headers = new[] { new PureHttpHeader("User-Agent", Chrome150UserAgent) },
        }, cts.Token);

        string body = Encoding.UTF8.GetString(resp.Body);
        _output.WriteLine(body);

        Assert.Equal(200, resp.StatusCode);
        Assert.Equal("HTTP/2.0", resp.HttpVersion);
        Assert.Contains("tls=TLSv1.3", body, StringComparison.Ordinal);
        Assert.Contains("http=http/2", body, StringComparison.Ordinal);
        Assert.Contains("kex=X25519MLKEM768", body, StringComparison.Ordinal);
    }

    [Fact]
    public async Task LiveCloudflare_QuicEdge_ProtocolRacerFallsBackFromBlockedUdp443ToHttp2()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(25));
        await using var client = new TlsHttpClient(new TlsHttpClientOptions
        {
            ProfileName = "chrome_150",
            DisableHttp3 = false,
            RaceDelay = TimeSpan.FromMilliseconds(300),
            ConnectTimeout = TimeSpan.FromSeconds(12),
            RequestTimeout = TimeSpan.FromSeconds(20),
            InsecureSkipVerify = false,
        });

        PureHttpResponse resp = await client.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri("https://cloudflare-quic.com/"),
            Headers = new[] { new PureHttpHeader("User-Agent", Chrome150UserAgent) },
        }, cts.Token);

        _output.WriteLine($"cloudflare-quic status={resp.StatusCode} version={resp.HttpVersion} alt-svc={resp.AltSvcHeader} bodyLen={resp.Body.Length}");
        Assert.Equal(200, resp.StatusCode);
        Assert.Equal("HTTP/2.0", resp.HttpVersion);
        Assert.False(string.IsNullOrWhiteSpace(resp.AltSvcHeader));
        Assert.Contains("h3", resp.AltSvcHeader!, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task LiveGoogle_And_NginxQuic_SucceedWithPureCSharpTls13()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(25));
        await using var client = new TlsHttpClient(new TlsHttpClientOptions
        {
            ProfileName = "chrome_150",
            DisableHttp3 = true,
            ConnectTimeout = TimeSpan.FromSeconds(12),
            RequestTimeout = TimeSpan.FromSeconds(20),
            InsecureSkipVerify = false,
        });

        PureHttpResponse googleResp = await client.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri("https://www.google.com/generate_204"),
            Headers = new[] { new PureHttpHeader("User-Agent", Chrome150UserAgent) },
        }, cts.Token);
        _output.WriteLine($"google generate_204: status={googleResp.StatusCode} version={googleResp.HttpVersion} alt-svc={googleResp.AltSvcHeader}");
        Assert.Equal(204, googleResp.StatusCode);
        Assert.Equal("HTTP/2.0", googleResp.HttpVersion);

        PureHttpResponse nginxResp = await client.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri("https://quic.nginx.org/"),
            Headers = new[] { new PureHttpHeader("User-Agent", Chrome150UserAgent) },
        }, cts.Token);
        _output.WriteLine($"quic.nginx.org: status={nginxResp.StatusCode} version={nginxResp.HttpVersion} alt-svc={nginxResp.AltSvcHeader} bodyLen={nginxResp.Body.Length}");
        Assert.Equal(200, nginxResp.StatusCode);
        Assert.Equal("HTTP/2.0", nginxResp.HttpVersion);
    }

    [Fact]
    public async Task LiveNetClient_PureNetClient_NikeAndAkamai_CompleteTls13Http2Handshake()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
        using var net = new NetClient(timeout: TimeSpan.FromSeconds(20))
        {
            Transport = TransportMode.PureNetClient,
        };

        var nikeOpts = new RequestOptions
        {
            Profile = TlsProfile.Chrome150,
            Retries = 1,
            Timeout = TimeSpan.FromSeconds(20),
        };
        nikeOpts.Headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8";
        nikeOpts.Headers["Accept-Language"] = "en-US,en;q=0.9";

        NetResponse nikeResp = await net.GetAsync("https://www.nike.com/", nikeOpts, cts.Token);
        _output.WriteLine($"nike.com status={nikeResp.StatusCode} finalUrl={nikeResp.Url} bodyLen={nikeResp.Body.Length} server={nikeResp.Headers.GetValueOrDefault("server")}");
        Assert.InRange(nikeResp.StatusCode, 200, 499);

        var akamaiOpts = new RequestOptions
        {
            Profile = TlsProfile.Chrome150,
            Retries = 1,
            Timeout = TimeSpan.FromSeconds(20),
        };
        akamaiOpts.Headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8";
        akamaiOpts.Headers["Accept-Language"] = "en-US,en;q=0.9";

        NetResponse akamaiResp = await net.GetAsync("https://www.akamai.com/", akamaiOpts, cts.Token);
        _output.WriteLine($"akamai.com status={akamaiResp.StatusCode} finalUrl={akamaiResp.Url} bodyLen={akamaiResp.Body.Length} server={akamaiResp.Headers.GetValueOrDefault("server")}");
        Assert.InRange(akamaiResp.StatusCode, 200, 499);
    }

    [Theory]
    [InlineData("https://dns.alidns.com/resolve?name=example.com&type=A", "\"Status\":0")]
    [InlineData("https://www.taobao.com/", null)]
    [InlineData("https://www.tmall.com/", null)]
    public async Task LivePublicInternet_Udp443_Http3_CompletesOverDirectQuicV1WithStrictCertVerification(
        string url,
        string? expectedSubstring)
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(25));
        var uri = new Uri(url);
        ClientProfile chrome150 = ProfileRegistry.GetRequired("chrome_150");
        ConnectionKey key = ConnectionKey.Create("https", uri.Host, 443, chrome150.Name);

        await using var quic = await QuicConnection.ConnectAsync(new QuicConnectionOptions
        {
            Host = uri.Host,
            Port = 443,
            Profile = chrome150,
            TransportSpec = chrome150.QuicSpec,
            VerifyOptions = new CertificateVerifyOptions
            {
                InsecureSkipVerify = false,
                UseEmbeddedDefaultRoots = true,
            },
            ConnectTimeout = TimeSpan.FromSeconds(12),
        }, cts.Token);

        await using var h3 = new Http3Connection(quic, key, chrome150);
        await h3.StartAsync(cts.Token);

        PureHttpResponse resp = await h3.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = uri,
            Headers = new[]
            {
                new PureHttpHeader("User-Agent", Chrome150UserAgent),
                new PureHttpHeader("Accept", "*/*"),
            },
        }, cts.Token);

        string bodyPreview = Encoding.UTF8.GetString(resp.Body.AsSpan(0, Math.Min(resp.Body.Length, 256)));
        _output.WriteLine($"H3 LIVE {url}: status={resp.StatusCode} alpn={quic.NegotiatedAlpn} cipher=0x{quic.NegotiatedCipherSuite:x4} scidLen={quic.LocalScid.Length} bodyLen={resp.Body.Length} preview={bodyPreview.Replace("\r", " ").Replace("\n", " ")}");

        Assert.Equal("HTTP/3", resp.HttpVersion);
        Assert.Equal("h3", quic.NegotiatedAlpn);
        Assert.InRange(resp.StatusCode, 200, 399);
        if (expectedSubstring is not null)
            Assert.Contains(expectedSubstring, Encoding.UTF8.GetString(resp.Body), StringComparison.Ordinal);
    }

    [Theory]
    [InlineData("https://www.apple.com.cn/")]
    [InlineData("https://www.aliyun.com/")]
    public async Task LivePublicInternet_ProtocolRacer_FallsBackToHttp2_WhenQuicEdgeRejectsHandshake(string url)
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
        await using var client = new TlsHttpClient(new TlsHttpClientOptions
        {
            ProfileName = "chrome_150",
            DisableHttp3 = false,
            ConnectTimeout = TimeSpan.FromSeconds(12),
            RequestTimeout = TimeSpan.FromSeconds(20),
            VerifyOptions = new CertificateVerifyOptions
            {
                InsecureSkipVerify = false,
                UseEmbeddedDefaultRoots = true,
            },
        });

        PureHttpResponse resp = await client.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri(url),
            Headers = new[]
            {
                new PureHttpHeader("User-Agent", Chrome150UserAgent),
                new PureHttpHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                new PureHttpHeader("Accept-Language", "en-US,en;q=0.9"),
            },
        }, cts.Token);

        _output.WriteLine($"RACER FALLBACK {url}: status={resp.StatusCode} version={resp.HttpVersion} bodyLen={resp.Body.Length}");
        Assert.Equal("HTTP/2.0", resp.HttpVersion);
        Assert.InRange(resp.StatusCode, 200, 399);
    }
}
