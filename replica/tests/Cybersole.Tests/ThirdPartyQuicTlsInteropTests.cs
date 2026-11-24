using System.Diagnostics;
using System.Net;
using System.Net.Sockets;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
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
public sealed class ThirdPartyQuicTlsInteropTests : IClassFixture<ThirdPartyQuicTlsInteropTests.QuicGoFixture>
{
    private readonly QuicGoFixture _fixture;
    private readonly ITestOutputHelper _output;

    public ThirdPartyQuicTlsInteropTests(QuicGoFixture fixture, ITestOutputHelper output)
    {
        _fixture = fixture;
        _output = output;
    }

    [Fact]
    public async Task GoTls13_Chrome150_MlKem768_MatchesWireClientHelloAndAkamaiH2()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        ClientProfile profile = ProfileRegistry.GetRequired("chrome_150");

        using ClientHelloBuildResult localCh = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
        {
            Profile = profile,
            ServerName = "localhost",
            Random = new Random(77),
        });
        TlsWireFingerprintResult expectedTlsFp = WireFingerprint.AnalyzeClientHello(localCh.HandshakeMessage, isQuic: false);
        Http2WireFingerprintResult expectedH2Fp = WireFingerprint.AnalyzeHttp2Spec(profile.Http2Settings);

        await using var client = CreateClient("chrome_150", disableHttp3: true);
        PureHttpResponse resp = await client.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri($"https://localhost:{_fixture.TcpPort}/inspect"),
        }, cts.Token);

        Assert.Equal(200, resp.StatusCode);
        Assert.Equal("HTTP/2.0", resp.HttpVersion);

        InspectPayload payload = JsonSerializer.Deserialize<InspectPayload>(resp.Body)!;
        _output.WriteLine($"Go tcp /inspect: version=0x{payload.TlsVersion:x4} cipher=0x{payload.CipherSuite:x4} curve=0x{payload.CurveId:x4} ({payload.CurveName}) hrr={payload.HelloRetryRequest} alpn={payload.NegotiatedProtocol}");

        Assert.Equal("tcp-h2", payload.ServerRole);
        Assert.Equal("HTTP/2.0", payload.Proto);
        Assert.Equal(0x0304, payload.TlsVersion);
        Assert.Equal(4588, payload.CurveId); // tls.X25519MLKEM768
        Assert.Equal("h2", payload.NegotiatedProtocol);
        Assert.False(payload.DidResume);
        Assert.False(payload.HelloRetryRequest);

        Assert.False(string.IsNullOrEmpty(payload.ClientHelloHex));
        byte[] wireCh = Convert.FromHexString(payload.ClientHelloHex!);
        TlsWireFingerprintResult wireTlsFp = WireFingerprint.AnalyzeClientHello(wireCh, isQuic: false);
        _output.WriteLine($"Wire JA4={wireTlsFp.Ja4} JA4_r={wireTlsFp.Ja4Raw} JA3={wireTlsFp.Ja3Hash}");

        Assert.Equal(expectedTlsFp.Ja4, wireTlsFp.Ja4);
        Assert.Equal(expectedTlsFp.Ja4Raw, wireTlsFp.Ja4Raw);
        Assert.Equal(expectedTlsFp.Ja3nHash, wireTlsFp.Ja3nHash);
        Assert.Equal(32, wireTlsFp.Ja3Hash.Length);

        Assert.False(string.IsNullOrEmpty(payload.H2PrefaceHex));
        byte[] wireH2Preface = Convert.FromHexString(payload.H2PrefaceHex!);
        Http2WireFingerprintResult wireH2Fp = WireFingerprint.AnalyzeRawHttp2Preface(
            wireH2Preface,
            profile.Http2Settings.PseudoHeaderOrder);
        _output.WriteLine($"Wire Akamai H2={wireH2Fp.AkamaiText}");

        Assert.Equal(expectedH2Fp.AkamaiText, wireH2Fp.AkamaiText);
        Assert.Equal("1:65536;2:0;4:6291456;6:262144|15663105|0|m,a,s,p", wireH2Fp.AkamaiText);
    }

    [Fact]
    public async Task GoTls13_Chrome150_P256OnlyServer_ForcesHelloRetryRequestAndSucceeds()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        await using var client = CreateClient("chrome_150", disableHttp3: true);

        PureHttpResponse resp = await client.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri($"https://localhost:{_fixture.HrrPort}/inspect"),
        }, cts.Token);

        Assert.Equal(200, resp.StatusCode);
        Assert.Equal("HTTP/2.0", resp.HttpVersion);

        InspectPayload payload = JsonSerializer.Deserialize<InspectPayload>(resp.Body)!;
        _output.WriteLine($"Go hrr /inspect: version=0x{payload.TlsVersion:x4} curve=0x{payload.CurveId:x4} ({payload.CurveName}) hrr={payload.HelloRetryRequest}");

        Assert.Equal("hrr-p256", payload.ServerRole);
        Assert.Equal(0x0304, payload.TlsVersion);
        Assert.Equal(23, payload.CurveId); // CurveP256
        Assert.True(payload.HelloRetryRequest);
        Assert.Equal("h2", payload.NegotiatedProtocol);
    }

    [Fact]
    public async Task GoTls13_Chrome150Psk_SessionResumption_SetsDidResumeTrueOnSecondConnection()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        ClientProfile profile = ProfileRegistry.GetRequired("chrome_150_PSK");
        var sessionCache = new LruTlsSessionCache();
        ConnectionKey key = ConnectionKey.Create("https", "localhost", _fixture.TcpPort, profile.Name);

        // Connection 1: full handshake + wait briefly for server NewSessionTicket arrival
        using (var tcp1 = new TcpClient())
        {
            await tcp1.ConnectAsync(IPAddress.Loopback, _fixture.TcpPort, cts.Token);
            await using var tls1 = new TlsStream(tcp1.GetStream(), new TlsConnectionOptions
            {
                ServerName = "localhost",
                Port = _fixture.TcpPort,
                Profile = profile,
                VerifyOptions = _fixture.VerifyOptions,
                SessionCache = sessionCache,
            });
            await tls1.HandshakeAsync(cts.Token);
            Assert.Equal("h2", tls1.NegotiatedAlpn);

            await using var h2_1 = await Http2Connection.ConnectAsync(
                tls1,
                key,
                profile.Http2Settings,
                leaveStreamOpen: true,
                cts.Token);

            PureHttpResponse r1 = await h2_1.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"https://localhost:{_fixture.TcpPort}/inspect"),
            }, cts.Token);
            Assert.Equal(200, r1.StatusCode);
            InspectPayload p1 = JsonSerializer.Deserialize<InspectPayload>(r1.Body)!;
            Assert.False(p1.DidResume);

            // Give the background reader frame loop a brief moment to ingest Go's TLS 1.3 NewSessionTicket.
            for (int i = 0; i < 20 && sessionCache.Count == 0; i++)
                await Task.Delay(25, cts.Token);
        }

        Assert.True(sessionCache.Count > 0, "Expected TLS 1.3 NewSessionTicket to be stored in sessionCache.");

        // Connection 2: separate TCP socket using same LruTlsSessionCache -> must resume via PSK
        using (var tcp2 = new TcpClient())
        {
            await tcp2.ConnectAsync(IPAddress.Loopback, _fixture.TcpPort, cts.Token);
            await using var tls2 = new TlsStream(tcp2.GetStream(), new TlsConnectionOptions
            {
                ServerName = "localhost",
                Port = _fixture.TcpPort,
                Profile = profile,
                VerifyOptions = _fixture.VerifyOptions,
                SessionCache = sessionCache,
            });
            await tls2.HandshakeAsync(cts.Token);
            Assert.Equal("h2", tls2.NegotiatedAlpn);

            await using var h2_2 = await Http2Connection.ConnectAsync(
                tls2,
                key,
                profile.Http2Settings,
                leaveStreamOpen: true,
                cts.Token);

            PureHttpResponse r2 = await h2_2.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"https://localhost:{_fixture.TcpPort}/inspect"),
            }, cts.Token);
            Assert.Equal(200, r2.StatusCode);
            InspectPayload p2 = JsonSerializer.Deserialize<InspectPayload>(r2.Body)!;
            _output.WriteLine($"Go PSK conn2 /inspect: didResume={p2.DidResume} curve=0x{p2.CurveId:x4}");
            Assert.True(p2.DidResume);
            Assert.Equal(4588, p2.CurveId);
        }
    }

    [Fact]
    public async Task QuicGoV061_Http3_ZeroScid_NoSyntheticUa_FlowControl512KB_And_ConcurrentStreams()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(25));
        ClientProfile chrome150 = ProfileRegistry.GetRequired("chrome_150");
        ConnectionKey key = ConnectionKey.Create("https", "localhost", _fixture.UdpPort, chrome150.Name);

        await using var quic = await QuicConnection.ConnectAsync(new QuicConnectionOptions
        {
            Host = "localhost",
            Port = _fixture.UdpPort,
            Profile = chrome150,
            TransportSpec = chrome150.QuicSpec,
            VerifyOptions = _fixture.VerifyOptions,
            DnsResolver = static (_, _) => ValueTask.FromResult(new[] { IPAddress.Loopback }),
            ConnectTimeout = TimeSpan.FromSeconds(10),
        }, cts.Token);

        await using var h3 = new Http3Connection(quic, key, chrome150);
        await h3.StartAsync(cts.Token);

        PureHttpResponse inspectResp = await h3.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri($"https://localhost:{_fixture.UdpPort}/inspect"),
        }, cts.Token);
        Assert.Equal(200, inspectResp.StatusCode);
        Assert.Equal("HTTP/3", inspectResp.HttpVersion);

        InspectPayload payload = JsonSerializer.Deserialize<InspectPayload>(inspectResp.Body)!;
        _output.WriteLine($"quic-go /inspect: version=0x{payload.TlsVersion:x4} curve=0x{payload.CurveId:x4} ({payload.CurveName}) hasUA={payload.HasUserAgent} scidLen={payload.Quic?.FirstScidLen} dcidLen={payload.Quic?.FirstDcidLen}");

        Assert.Equal("quic-h3", payload.ServerRole);
        Assert.Equal(0x0304, payload.TlsVersion);
        Assert.Equal(4588, payload.CurveId); // X25519MLKEM768 over QUIC!
        Assert.Equal("h3", payload.NegotiatedProtocol);
        Assert.False(payload.HasUserAgent);
        Assert.DoesNotContain(payload.Headers.Keys, k => k.Equals("User-Agent", StringComparison.OrdinalIgnoreCase));
        Assert.NotNull(payload.Quic);
        Assert.Equal(0, payload.Quic!.FirstScidLen);
        Assert.Equal(8, payload.Quic.FirstDcidLen);

        // Large 512 KB download over HTTP/3 + SHA-256 verification
        PureHttpResponse largeResp = await h3.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri($"https://localhost:{_fixture.UdpPort}/large?bytes=524288"),
        }, cts.Token);
        Assert.Equal(200, largeResp.StatusCode);
        Assert.Equal(524_288, largeResp.Body.Length);
        string expectedSha = Convert.ToHexString(SHA256.HashData(largeResp.Body)).ToLowerInvariant();
        Assert.Equal(expectedSha, largeResp.GetFirstHeader("X-Payload-Sha256"));

        // Large POST echo over HTTP/3
        byte[] postBytes = CreateDeterministicPayload(32 * 1024);
        PureHttpResponse echoResp = await h3.SendAsync(new PureHttpRequest
        {
            Method = "POST",
            Uri = new Uri($"https://localhost:{_fixture.UdpPort}/echo"),
            Body = postBytes,
        }, cts.Token);
        Assert.Equal(200, echoResp.StatusCode);
        Assert.Equal(postBytes, echoResp.Body);
        Assert.Equal(Convert.ToHexString(SHA256.HashData(postBytes)).ToLowerInvariant(), echoResp.GetFirstHeader("X-Echo-Sha256"));

        // 8 concurrent multiplexed H3 streams
        Task<PureHttpResponse>[] h3Tasks = Enumerable.Range(0, 8)
            .Select(i => h3.SendAsync(new PureHttpRequest
            {
                Method = (i % 2 == 0) ? "GET" : "POST",
                Uri = new Uri((i % 2 == 0)
                    ? $"https://localhost:{_fixture.UdpPort}/large?bytes=65536&stream={i}"
                    : $"https://localhost:{_fixture.UdpPort}/echo?stream={i}"),
                Body = (i % 2 == 0) ? null : CreateDeterministicPayload(4096 + i * 257),
            }, cts.Token))
            .ToArray();
        PureHttpResponse[] h3Results = await Task.WhenAll(h3Tasks);
        for (int i = 0; i < 8; i++)
        {
            Assert.Equal(200, h3Results[i].StatusCode);
            Assert.Equal("HTTP/3", h3Results[i].HttpVersion);
            if (i % 2 == 0)
                Assert.Equal(65_536, h3Results[i].Body.Length);
            else
                Assert.Equal(CreateDeterministicPayload(4096 + i * 257), h3Results[i].Body);
        }
    }

    [Fact]
    public async Task GoHttp2_FlowControl512KB_And_8ConcurrentMultiplexedStreams_Succeed()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(20));
        await using var client = CreateClient("chrome_150", disableHttp3: true);

        PureHttpResponse largeResp = await client.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri($"https://localhost:{_fixture.TcpPort}/large?bytes=524288"),
        }, cts.Token);
        Assert.Equal(200, largeResp.StatusCode);
        Assert.Equal("HTTP/2.0", largeResp.HttpVersion);
        Assert.Equal(524_288, largeResp.Body.Length);
        Assert.Equal(
            Convert.ToHexString(SHA256.HashData(largeResp.Body)).ToLowerInvariant(),
            largeResp.GetFirstHeader("X-Payload-Sha256"));

        Task<PureHttpResponse>[] h2Tasks = Enumerable.Range(0, 8)
            .Select(i => client.SendAsync(new PureHttpRequest
            {
                Method = (i % 2 == 0) ? "GET" : "POST",
                Uri = new Uri((i % 2 == 0)
                    ? $"https://localhost:{_fixture.TcpPort}/large?bytes=65536&s={i}"
                    : $"https://localhost:{_fixture.TcpPort}/echo?s={i}"),
                Body = (i % 2 == 0) ? null : CreateDeterministicPayload(3072 + i * 199),
            }, cts.Token))
            .ToArray();
        PureHttpResponse[] h2Results = await Task.WhenAll(h2Tasks);
        for (int i = 0; i < 8; i++)
        {
            Assert.Equal(200, h2Results[i].StatusCode);
            Assert.Equal("HTTP/2.0", h2Results[i].HttpVersion);
            if (i % 2 == 0)
                Assert.Equal(65_536, h2Results[i].Body.Length);
            else
                Assert.Equal(CreateDeterministicPayload(3072 + i * 199), h2Results[i].Body);
        }
    }

    [Fact]
    public async Task QuicGoV061_VerifySourceAddress_ForcesQuicRetryPacket_AndCompletesHttp3()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        ClientProfile chrome150 = ProfileRegistry.GetRequired("chrome_150");
        ConnectionKey key = ConnectionKey.Create("https", "localhost", _fixture.RetryUdpPort, chrome150.Name);

        await using var quic = await QuicConnection.ConnectAsync(new QuicConnectionOptions
        {
            Host = "localhost",
            Port = _fixture.RetryUdpPort,
            Profile = chrome150,
            TransportSpec = chrome150.QuicSpec,
            VerifyOptions = _fixture.VerifyOptions,
            DnsResolver = static (_, _) => ValueTask.FromResult(new[] { IPAddress.Loopback }),
            ConnectTimeout = TimeSpan.FromSeconds(10),
        }, cts.Token);

        await using var h3 = new Http3Connection(quic, key, chrome150);
        await h3.StartAsync(cts.Token);

        PureHttpResponse inspectResp = await h3.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri($"https://localhost:{_fixture.RetryUdpPort}/inspect"),
        }, cts.Token);
        Assert.Equal(200, inspectResp.StatusCode);
        Assert.Equal("HTTP/3", inspectResp.HttpVersion);

        InspectPayload payload = JsonSerializer.Deserialize<InspectPayload>(inspectResp.Body)!;
        _output.WriteLine($"quic-go retry /inspect: initialCount={payload.Quic?.InitialCount} sawRetryToken={payload.Quic?.SawRetryTokenInitial} lastTokenLen={payload.Quic?.LastInitialTokenLen}");
        Assert.Equal("quic-retry-h3", payload.ServerRole);
        Assert.NotNull(payload.Quic);
        Assert.True(payload.Quic!.SawRetryTokenInitial);
        Assert.True(payload.Quic.InitialCount >= 2);
        Assert.True(payload.Quic.LastInitialTokenLen > 0);

        byte[] postBytes = CreateDeterministicPayload(8192);
        PureHttpResponse echoResp = await h3.SendAsync(new PureHttpRequest
        {
            Method = "POST",
            Uri = new Uri($"https://localhost:{_fixture.RetryUdpPort}/echo"),
            Body = postBytes,
        }, cts.Token);
        Assert.Equal(200, echoResp.StatusCode);
        Assert.Equal(postBytes, echoResp.Body);
    }

    [Fact]
    public async Task ProtocolRacer_DualWinsHttp3_And_UdpBlackholeFallsBackToHttp2()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(20));

        // 1) Dual TCP+UDP port: H3 completes faster than stagger -> HTTP/3 wins
        await using (var dualClient = CreateClient("chrome_150", disableHttp3: false))
        {
            PureHttpResponse winResp = await dualClient.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"https://localhost:{_fixture.DualPort}/inspect"),
            }, cts.Token);

            Assert.Equal(200, winResp.StatusCode);
            Assert.Equal("HTTP/3", winResp.HttpVersion);
            InspectPayload winPayload = JsonSerializer.Deserialize<InspectPayload>(winResp.Body)!;
            Assert.Equal("dual-h3", winPayload.ServerRole);
        }

        // 2) Blackholed UDP port: silent UDP packet drop + working TCP H2 -> racer falls back to HTTP/2 quickly
        await using (var bhClient = CreateClient(
            "chrome_150",
            disableHttp3: false,
            raceDelay: TimeSpan.FromMilliseconds(200),
            connectTimeout: TimeSpan.FromSeconds(5)))
        {
            PureHttpResponse fbResp = await bhClient.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"https://localhost:{_fixture.BlackholePort}/inspect"),
            }, cts.Token);

            Assert.Equal(200, fbResp.StatusCode);
            Assert.Equal("HTTP/2.0", fbResp.HttpVersion);
            InspectPayload fbPayload = JsonSerializer.Deserialize<InspectPayload>(fbResp.Body)!;
            Assert.Equal("blackhole-fallback-tcp", fbPayload.ServerRole);
        }
    }

    [Fact]
    public async Task QuicGoV061_ClientInitiatedKeyUpdate_MultiGeneration_CompletesHttp3()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(20));
        ClientProfile chrome152 = ProfileRegistry.GetRequired("chrome_152");
        ConnectionKey key = ConnectionKey.Create("https", "localhost", _fixture.UdpPort, chrome152.Name);

        await using var quic = await QuicConnection.ConnectAsync(new QuicConnectionOptions
        {
            Host = "localhost",
            Port = _fixture.UdpPort,
            Profile = chrome152,
            TransportSpec = chrome152.QuicSpec,
            VerifyOptions = _fixture.VerifyOptions,
            DnsResolver = static (_, _) => ValueTask.FromResult(new[] { IPAddress.Loopback }),
            ConnectTimeout = TimeSpan.FromSeconds(10),
        }, cts.Token);

        await using var h3 = new Http3Connection(quic, key, chrome152);
        await h3.StartAsync(cts.Token);

        // Request 1 before key update
        PureHttpResponse inspectResp = await h3.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri($"https://localhost:{_fixture.UdpPort}/inspect"),
        }, cts.Token);
        Assert.Equal(200, inspectResp.StatusCode);
        Assert.Equal("HTTP/3", inspectResp.HttpVersion);

        await quic.WaitForHandshakeConfirmedAsync(cts.Token);

        // Client-initiated KeyUpdate Generation 1 (phase 0 -> 1)
        quic.InitiateKeyUpdate();
        Assert.Equal(1, quic.ClientInitiatedKeyUpdates);
        Assert.Equal(1, quic.WriteKeyPhaseGeneration);

        PureHttpResponse gen1Resp = await h3.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri($"https://localhost:{_fixture.UdpPort}/large?bytes=16384"),
        }, cts.Token);
        Assert.Equal(200, gen1Resp.StatusCode);
        Assert.Equal("HTTP/3", gen1Resp.HttpVersion);
        Assert.Equal(16_384, gen1Resp.Body.Length);
        Assert.Equal(
            Convert.ToHexString(SHA256.HashData(gen1Resp.Body)).ToLowerInvariant(),
            gen1Resp.GetFirstHeader("X-Payload-Sha256"));
        Assert.Equal(1, quic.ClientInitiatedKeyUpdates);
        Assert.True(quic.WriteKeyPhaseGeneration >= 1);
        Assert.True(quic.ReadKeyPhaseGeneration >= 1);

        // Client-initiated KeyUpdate Generation 2 (phase 1 -> 0)
        quic.InitiateKeyUpdate();
        Assert.Equal(2, quic.ClientInitiatedKeyUpdates);
        Assert.True(quic.WriteKeyPhaseGeneration >= 2);

        byte[] echoPayload = CreateDeterministicPayload(8192);
        PureHttpResponse gen2Resp = await h3.SendAsync(new PureHttpRequest
        {
            Method = "POST",
            Uri = new Uri($"https://localhost:{_fixture.UdpPort}/echo"),
            Body = echoPayload,
        }, cts.Token);
        Assert.Equal(200, gen2Resp.StatusCode);
        Assert.Equal("HTTP/3", gen2Resp.HttpVersion);
        Assert.Equal(echoPayload, gen2Resp.Body);
        Assert.Equal(Convert.ToHexString(SHA256.HashData(echoPayload)).ToLowerInvariant(), gen2Resp.GetFirstHeader("X-Echo-Sha256"));
        Assert.Equal(2, quic.ClientInitiatedKeyUpdates);
        Assert.True(quic.WriteKeyPhaseGeneration >= 2);
        Assert.True(quic.ReadKeyPhaseGeneration >= 2);
    }

    private TlsHttpClient CreateClient(
        string profileName,
        bool disableHttp3,
        TimeSpan? raceDelay = null,
        TimeSpan? connectTimeout = null)
    {
        return new TlsHttpClient(new TlsHttpClientOptions
        {
            ProfileName = profileName,
            DisableHttp3 = disableHttp3,
            ConnectTimeout = connectTimeout ?? TimeSpan.FromSeconds(10),
            RequestTimeout = TimeSpan.FromSeconds(15),
            RaceDelay = raceDelay,
            VerifyOptions = _fixture.VerifyOptions,
            DnsResolver = static (_, _) => Task.FromResult(new[] { IPAddress.Loopback }),
        });
    }

    private static byte[] CreateDeterministicPayload(int size)
    {
        var buf = new byte[size];
        for (int i = 0; i < buf.Length; i++)
            buf[i] = (byte)((i * 31 + 17) & 0xFF);
        return buf;
    }

    public sealed class QuicGoFixture : IAsyncLifetime
    {
        private Process? _proc;
        private string? _exePath;
        private string? _caPemPath;
        private readonly Queue<string> _stderrTail = new();

        public string[] GetStderrTail()
        {
            lock (_stderrTail)
                return _stderrTail.ToArray();
        }

        public int TcpPort { get; private set; }
        public int HrrPort { get; private set; }
        public int UdpPort { get; private set; }
        public int RetryUdpPort { get; private set; }
        public int DualPort { get; private set; }
        public int BlackholePort { get; private set; }
        public CertificateVerifyOptions VerifyOptions { get; private set; } = default!;

        public async Task InitializeAsync()
        {
            string fixtureDir = FindFixtureDirectory();
            string token = Guid.NewGuid().ToString("N");
            _exePath = Path.Combine(Path.GetTempPath(), $"cybersole-quicgo-interop-{token}.exe");
            _caPemPath = Path.Combine(Path.GetTempPath(), $"cybersole-quicgo-ca-{token}.pem");

            var buildPsi = new ProcessStartInfo
            {
                FileName = "go",
                Arguments = $"build -o \"{_exePath}\" .",
                WorkingDirectory = fixtureDir,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
            };
            buildPsi.Environment["GOPROXY"] = "off";
            buildPsi.Environment["GOSUMDB"] = "off";

            using (Process buildProc = Process.Start(buildPsi) ?? throw new InvalidOperationException("Failed to start go build."))
            {
                string buildStdout = await buildProc.StandardOutput.ReadToEndAsync();
                string buildStderr = await buildProc.StandardError.ReadToEndAsync();
                await buildProc.WaitForExitAsync();
                if (buildProc.ExitCode != 0)
                {
                    throw new InvalidOperationException(
                        $"Offline Go build of QuicGoServer failed (exit {buildProc.ExitCode}):\n{buildStdout}\n{buildStderr}");
                }
            }

            var runPsi = new ProcessStartInfo
            {
                FileName = _exePath,
                Arguments = $"-ca-out \"{_caPemPath}\"",
                WorkingDirectory = fixtureDir,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
            };
            _proc = Process.Start(runPsi) ?? throw new InvalidOperationException("Failed to start compiled QuicGoServer binary.");
            _proc.ErrorDataReceived += (_, e) =>
            {
                if (e.Data is not null)
                {
                    lock (_stderrTail)
                    {
                        _stderrTail.Enqueue(e.Data);
                        while (_stderrTail.Count > 120)
                            _stderrTail.Dequeue();
                    }
                }
            };
            _proc.BeginErrorReadLine();

            using var startupCts = new CancellationTokenSource(TimeSpan.FromSeconds(15));
            string? readyLine = await _proc.StandardOutput.ReadLineAsync(startupCts.Token);
            if (string.IsNullOrWhiteSpace(readyLine))
            {
                string stderr = await _proc.StandardError.ReadToEndAsync();
                throw new InvalidOperationException($"QuicGoServer exited before emitting startup JSON. stderr={stderr}");
            }

            ReadyPayload ready = JsonSerializer.Deserialize<ReadyPayload>(readyLine)
                ?? throw new InvalidOperationException($"Invalid startup JSON from QuicGoServer: {readyLine}");

            TcpPort = IPEndPoint.Parse(ready.TcpAddr).Port;
            HrrPort = IPEndPoint.Parse(ready.HrrAddr).Port;
            UdpPort = IPEndPoint.Parse(ready.UdpAddr).Port;
            RetryUdpPort = IPEndPoint.Parse(ready.RetryUdpAddr).Port;
            DualPort = IPEndPoint.Parse(ready.DualAddr).Port;
            BlackholePort = IPEndPoint.Parse(ready.BlackholeAddr).Port;

            using var caCert = new X509Certificate2(_caPemPath);
            var roots = new RootCertificateDatabase();
            roots.AddDer(caCert.RawData);
            VerifyOptions = new CertificateVerifyOptions
            {
                CustomRoots = roots,
                UseEmbeddedDefaultRoots = false,
            };
        }

        public async Task DisposeAsync()
        {
            if (_proc is not null)
            {
                try
                {
                    if (!_proc.HasExited)
                        _proc.Kill(entireProcessTree: true);
                    await _proc.WaitForExitAsync().WaitAsync(TimeSpan.FromSeconds(5));
                }
                catch { }
                finally
                {
                    _proc.Dispose();
                    _proc = null;
                }
            }

            TryDeleteFile(_exePath);
            TryDeleteFile(_caPemPath);
        }

        private static string FindFixtureDirectory()
        {
            foreach (string root in new[] { AppContext.BaseDirectory, Directory.GetCurrentDirectory() })
            {
                var dir = new DirectoryInfo(root);
                while (dir is not null)
                {
                    string candidate = Path.Combine(dir.FullName, "TestFixtures", "QuicGoServer", "main.go");
                    if (File.Exists(candidate))
                        return Path.GetDirectoryName(candidate)!;

                    string testsCandidate = Path.Combine(dir.FullName, "tests", "Cybersole.Tests", "TestFixtures", "QuicGoServer", "main.go");
                    if (File.Exists(testsCandidate))
                        return Path.GetDirectoryName(testsCandidate)!;

                    string replicaCandidate = Path.Combine(dir.FullName, "replica", "tests", "Cybersole.Tests", "TestFixtures", "QuicGoServer", "main.go");
                    if (File.Exists(replicaCandidate))
                        return Path.GetDirectoryName(replicaCandidate)!;

                    dir = dir.Parent;
                }
            }

            throw new DirectoryNotFoundException("Could not locate TestFixtures/QuicGoServer/main.go");
        }

        private static void TryDeleteFile(string? path)
        {
            if (string.IsNullOrEmpty(path))
                return;
            try
            {
                if (File.Exists(path))
                    File.Delete(path);
            }
            catch { }
        }

        private sealed class ReadyPayload
        {
            [JsonPropertyName("tcpAddr")] public string TcpAddr { get; set; } = string.Empty;
            [JsonPropertyName("hrrAddr")] public string HrrAddr { get; set; } = string.Empty;
            [JsonPropertyName("udpAddr")] public string UdpAddr { get; set; } = string.Empty;
            [JsonPropertyName("retryUdpAddr")] public string RetryUdpAddr { get; set; } = string.Empty;
            [JsonPropertyName("dualAddr")] public string DualAddr { get; set; } = string.Empty;
            [JsonPropertyName("blackholeAddr")] public string BlackholeAddr { get; set; } = string.Empty;
        }
    }

    private sealed class InspectPayload
    {
        [JsonPropertyName("serverRole")] public string ServerRole { get; set; } = string.Empty;
        [JsonPropertyName("proto")] public string Proto { get; set; } = string.Empty;
        [JsonPropertyName("method")] public string Method { get; set; } = string.Empty;
        [JsonPropertyName("path")] public string Path { get; set; } = string.Empty;
        [JsonPropertyName("remoteAddr")] public string RemoteAddr { get; set; } = string.Empty;
        [JsonPropertyName("userAgent")] public string UserAgent { get; set; } = string.Empty;
        [JsonPropertyName("hasUserAgent")] public bool HasUserAgent { get; set; }
        [JsonPropertyName("tlsVersion")] public ushort TlsVersion { get; set; }
        [JsonPropertyName("cipherSuite")] public ushort CipherSuite { get; set; }
        [JsonPropertyName("curveId")] public ushort CurveId { get; set; }
        [JsonPropertyName("curveName")] public string CurveName { get; set; } = string.Empty;
        [JsonPropertyName("didResume")] public bool DidResume { get; set; }
        [JsonPropertyName("helloRetryRequest")] public bool HelloRetryRequest { get; set; }
        [JsonPropertyName("negotiatedProtocol")] public string NegotiatedProtocol { get; set; } = string.Empty;
        [JsonPropertyName("serverName")] public string ServerName { get; set; } = string.Empty;
        [JsonPropertyName("clientHelloHex")] public string? ClientHelloHex { get; set; }
        [JsonPropertyName("h2PrefaceHex")] public string? H2PrefaceHex { get; set; }
        [JsonPropertyName("quic")] public QuicInspectInfo? Quic { get; set; }
        [JsonPropertyName("headers")] public Dictionary<string, string[]> Headers { get; set; } = new();
    }

    private sealed class QuicInspectInfo
    {
        [JsonPropertyName("InitialCount")] public int InitialCount { get; set; }
        [JsonPropertyName("FirstDatagramLen")] public int FirstDatagramLen { get; set; }
        [JsonPropertyName("FirstDcidLen")] public int FirstDcidLen { get; set; }
        [JsonPropertyName("FirstScidLen")] public int FirstScidLen { get; set; }
        [JsonPropertyName("SawRetryTokenInitial")] public bool SawRetryTokenInitial { get; set; }
        [JsonPropertyName("LastInitialTokenLen")] public int LastInitialTokenLen { get; set; }
    }
}
