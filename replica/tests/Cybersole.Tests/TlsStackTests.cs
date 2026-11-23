using System.Buffers.Binary;
using System.IO.Compression;
using System.Net;
using System.Net.Security;
using System.Net.Sockets;
using System.Security.Authentication;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using Cybersole.Http.Crypto;
using Cybersole.Http.Profiles;
using Cybersole.Http.Tls;
using Cybersole.Http.X509;
using BcSecurity = Org.BouncyCastle.Security;
using BcTls = Org.BouncyCastle.Tls;
using BcCrypto = Org.BouncyCastle.Tls.Crypto;
using BcBc = Org.BouncyCastle.Tls.Crypto.Impl.BC;
using Xunit;

namespace Cybersole.Tests;

public sealed class TlsStackTests
{
    private const string TestHost = "localhost";

    // ---- 1. Real SslStream Server Loopback Tests (TLS 1.3 & TLS 1.2 EMS) ----

    [Theory]
    [InlineData("chrome_131")]
    [InlineData("chrome_150")]
    public async Task Tls13LoopbackAgainstBouncyCastleServerSucceedsAndEchoesLargePayload(string profileName)
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole Test Root CA");
        using X509Certificate2 serverCert = CreateTestLeaf(leafKey, caCert, TestHost);

        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);

        using var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        int port = ((IPEndPoint)listener.LocalEndpoint).Port;

        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        byte[] requestPayload = CreatePatternPayload(24_576); // > 16384 to exercise multi-record coalescing

        Exception? serverError = null;
        Task serverTask = Task.Run(async () =>
        {
            try
            {
                using TcpClient accepted = await listener.AcceptTcpClientAsync(cts.Token);
                using NetworkStream net = accepted.GetStream();
                var protocol = new BcTls.TlsServerProtocol(net);
                var server = new BcTestTls13Server(serverCert.RawData, caCert.RawData, leafKey.ExportPkcs8PrivateKey());
                protocol.Accept(server);

                using Stream tlsBody = protocol.Stream;
                var rx = new byte[requestPayload.Length];
                await ReadExactlyAsync(tlsBody, rx, cts.Token);
                await tlsBody.WriteAsync(rx, cts.Token);
                await tlsBody.FlushAsync(cts.Token);
                protocol.Close();
            }
            catch (Exception ex)
            {
                serverError = ex;
            }
        }, cts.Token);

        using var tcp = new TcpClient();
        await tcp.ConnectAsync(IPAddress.Loopback, port, cts.Token);
        var options = new TlsConnectionOptions
        {
            ServerName = TestHost,
            Port = port,
            Profile = ProfileRegistry.GetRequired(profileName),
            VerifyOptions = new CertificateVerifyOptions
            {
                CustomRoots = roots,
                UseEmbeddedDefaultRoots = false,
            },
        };

        await using var tls = new TlsStream(tcp.GetStream(), options);
        try
        {
            await tls.HandshakeAsync(cts.Token);
        }
        catch (Exception clientEx)
        {
            await serverTask;
            if (serverError is not null)
                throw new AggregateException("Client handshake failed; BouncyCastle server also failed.", clientEx, serverError);
            throw;
        }

        Assert.True(tls.HandshakeCompleted);
        Assert.Equal(TlsVersion.Tls13, tls.NegotiatedVersion);
        Assert.Equal("h2", tls.NegotiatedAlpn);
        Assert.NotNull(tls.LeafCertificate);
        Assert.Equal(serverCert.RawData, tls.LeafCertificate!.RawDer.ToArray());

        await tls.WriteAsync(requestPayload, cts.Token);
        await tls.FlushAsync(cts.Token);

        var responsePayload = new byte[requestPayload.Length];
        await ReadExactlyAsync(tls, responsePayload, cts.Token);
        Assert.Equal(requestPayload, responsePayload);

        // Drain server close_notify cleanly
        var eofBuf = new byte[16];
        int trailing = await tls.ReadAsync(eofBuf, cts.Token);
        Assert.Equal(0, trailing);
        await tls.ShutdownAsync(cts.Token);

        await serverTask;
        Assert.Null(serverError);
    }

    private sealed class BcTestTls13Server : BcTls.DefaultTlsServer
    {
        private readonly byte[] _leafDer;
        private readonly byte[] _caDer;
        private readonly byte[] _leafPkcs8;
        private readonly BcBc.BcTlsCrypto _bcCrypto;

        public BcTestTls13Server(byte[] leafDer, byte[] caDer, byte[] leafPkcs8)
            : this(new BcBc.BcTlsCrypto(new BcSecurity.SecureRandom()), leafDer, caDer, leafPkcs8)
        {
        }

        private BcTestTls13Server(BcBc.BcTlsCrypto crypto, byte[] leafDer, byte[] caDer, byte[] leafPkcs8)
            : base(crypto)
        {
            _bcCrypto = crypto;
            _leafDer = leafDer;
            _caDer = caDer;
            _leafPkcs8 = leafPkcs8;
        }

        protected override BcTls.ProtocolVersion[] GetSupportedVersions() =>
            new[] { BcTls.ProtocolVersion.TLSv13 };

        protected override int[] GetSupportedCipherSuites() =>
            new[] { BcTls.CipherSuite.TLS_AES_128_GCM_SHA256, BcTls.CipherSuite.TLS_AES_256_GCM_SHA384 };

        protected override IList<BcTls.ProtocolName> GetProtocolNames() =>
            new List<BcTls.ProtocolName>
            {
                BcTls.ProtocolName.Http_2_Tls,
                BcTls.ProtocolName.Http_1_1,
            };

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

    [Fact]
    public async Task Tls12WithExtendedMasterSecretLoopbackAgainstSslStreamSucceeds()
    {
        using var caKey = RSA.Create(2048);
        using var leafKey = RSA.Create(2048);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole RSA Test Root CA");
        using X509Certificate2 serverCert = CreateTestLeaf(leafKey, caCert, TestHost);

        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);

        using var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        int port = ((IPEndPoint)listener.LocalEndpoint).Port;

        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        byte[] requestPayload = Encoding.UTF8.GetBytes("GET /tls12-ems HTTP/1.1\r\nHost: localhost\r\n\r\n");
        byte[] responsePayload = CreatePatternPayload(19_000);

        Task serverTask = Task.Run(async () =>
        {
            using TcpClient accepted = await listener.AcceptTcpClientAsync(cts.Token);
            using NetworkStream net = accepted.GetStream();
            using var ssl = new SslStream(net, leaveInnerStreamOpen: false);

            var serverOpts = new SslServerAuthenticationOptions
            {
                ServerCertificateContext = SslStreamCertificateContext.Create(
                    serverCert,
                    new X509Certificate2Collection(caCert)),
                EnabledSslProtocols = SslProtocols.Tls12,
                ClientCertificateRequired = false,
                ApplicationProtocols = new List<SslApplicationProtocol>
                {
                    SslApplicationProtocol.Http11,
                },
            };

            await ssl.AuthenticateAsServerAsync(serverOpts, cts.Token);
            Assert.Equal(SslProtocols.Tls12, ssl.SslProtocol);

            var req = new byte[requestPayload.Length];
            await ReadExactlyAsync(ssl, req, cts.Token);
            Assert.Equal(requestPayload, req);

            await ssl.WriteAsync(responsePayload, cts.Token);
            await ssl.FlushAsync(cts.Token);
            await ssl.ShutdownAsync();
        }, cts.Token);

        using var tcp = new TcpClient();
        await tcp.ConnectAsync(IPAddress.Loopback, port, cts.Token);
        var options = new TlsConnectionOptions
        {
            ServerName = TestHost,
            Port = port,
            Profile = ProfileRegistry.GetRequired("chrome_131"),
            VerifyOptions = new CertificateVerifyOptions
            {
                CustomRoots = roots,
                UseEmbeddedDefaultRoots = false,
            },
        };

        await using var tls = new TlsStream(tcp.GetStream(), options);
        await tls.HandshakeAsync(cts.Token);

        Assert.True(tls.HandshakeCompleted);
        Assert.Equal(TlsVersion.Tls12, tls.NegotiatedVersion);
        Assert.True(tls.ExtendedMasterSecretUsed);
        Assert.Equal("http/1.1", tls.NegotiatedAlpn);

        await tls.WriteAsync(requestPayload, cts.Token);
        await tls.FlushAsync(cts.Token);

        var actualResp = new byte[responsePayload.Length];
        await ReadExactlyAsync(tls, actualResp, cts.Token);
        Assert.Equal(responsePayload, actualResp);

        await tls.ShutdownAsync(cts.Token);
        await serverTask;
    }

    // ---- 2. TLS 1.3 Session Resumption (NewSessionTicket + PSK "res binder") ----

    [Fact]
    public async Task Tls13SessionResumptionNewSessionTicketAndPskBinderAccepted()
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole PSK Test Root");
        using X509Certificate2 serverCert = CreateTestLeaf(leafKey, caCert, TestHost);

        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);
        var sessionCache = new LruTlsSessionCache(32);

        using var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        int port = ((IPEndPoint)listener.LocalEndpoint).Port;

        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        byte[] ticketBytes = "cybersole-session-ticket-opaque-payload"u8.ToArray();
        byte[] ticketNonce = { 0x01, 0x02, 0x03, 0x04 };
        const uint ticketAgeAdd = 0x7A6B5C4Du;
        byte[]? issuedPsk = null;
        bool secondConnVerifiedBinder = false;

        Task serverTask = Task.Run(async () =>
        {
            // Connection 1: full handshake + emit NewSessionTicket
            using (TcpClient c1 = await listener.AcceptTcpClientAsync(cts.Token))
            using (NetworkStream s1 = c1.GetStream())
            {
                var srv1 = new SyntheticTls13Server(s1, leafKey, new[] { serverCert.RawData, caCert.RawData });
                await srv1.AcceptFullHandshakeAsync(alpn: "h2", ct: cts.Token);

                issuedPsk = TlsSessionTicket.DerivePsk(HashAlgorithmKind.Sha256, srv1.ResumptionMasterSecret!, ticketNonce);
                await srv1.SendNewSessionTicketAsync(3600, ticketAgeAdd, ticketNonce, ticketBytes, maxEarlyDataSize: 0, cts.Token);
                await srv1.SendAppDataAsync("HELLO-1"u8.ToArray(), cts.Token);

                byte[] echo = await srv1.ReadAppDataAsync(cts.Token);
                Assert.Equal("PING-1", Encoding.UTF8.GetString(echo));
                await srv1.SendCloseNotifyAsync(cts.Token);
            }

            // Connection 2: resume using PSK + validate real RFC 8446 "res binder"
            using (TcpClient c2 = await listener.AcceptTcpClientAsync(cts.Token))
            using (NetworkStream s2 = c2.GetStream())
            {
                var srv2 = new SyntheticTls13Server(s2, leafKey, new[] { serverCert.RawData, caCert.RawData });
                secondConnVerifiedBinder = await srv2.AcceptResumedPskHandshakeAsync(
                    expectedTicket: ticketBytes,
                    psk: issuedPsk!,
                    alpn: "h2",
                    ct: cts.Token);

                byte[] ping = await srv2.ReadAppDataAsync(cts.Token);
                Assert.Equal("PING-2", Encoding.UTF8.GetString(ping));
                await srv2.SendAppDataAsync("RESUMED-OK"u8.ToArray(), cts.Token);
                await srv2.SendCloseNotifyAsync(cts.Token);
            }
        }, cts.Token);

        ClientProfile profile = ProfileRegistry.GetRequired("chrome_131_PSK");
        var verifyOpts = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false };

        // Client Connection 1
        using (var tcp1 = new TcpClient())
        {
            await tcp1.ConnectAsync(IPAddress.Loopback, port, cts.Token);
            await using var tls1 = new TlsStream(tcp1.GetStream(), new TlsConnectionOptions
            {
                ServerName = TestHost,
                Port = port,
                Profile = profile,
                VerifyOptions = verifyOpts,
                SessionCache = sessionCache,
            });

            await tls1.HandshakeAsync(cts.Token);
            Assert.False(tls1.UsedSessionResumption);

            var buf = new byte[32];
            int n = await tls1.ReadAsync(buf, cts.Token);
            Assert.Equal("HELLO-1", Encoding.UTF8.GetString(buf, 0, n));
            Assert.Equal(1, sessionCache.Count);

            await tls1.WriteAsync("PING-1"u8.ToArray(), cts.Token);
            Assert.Equal(0, await tls1.ReadAsync(buf, cts.Token));
        }

        // Client Connection 2 (PSK resumption)
        using (var tcp2 = new TcpClient())
        {
            await tcp2.ConnectAsync(IPAddress.Loopback, port, cts.Token);
            await using var tls2 = new TlsStream(tcp2.GetStream(), new TlsConnectionOptions
            {
                ServerName = TestHost,
                Port = port,
                Profile = profile,
                VerifyOptions = verifyOpts,
                SessionCache = sessionCache,
            });

            await tls2.HandshakeAsync(cts.Token);
            Assert.True(tls2.UsedSessionResumption);
            Assert.Equal(TlsVersion.Tls13, tls2.NegotiatedVersion);
            Assert.Equal("h2", tls2.NegotiatedAlpn);
            Assert.Equal(0, sessionCache.Count);

            await tls2.WriteAsync("PING-2"u8.ToArray(), cts.Token);
            var buf = new byte[32];
            int n = await tls2.ReadAsync(buf, cts.Token);
            Assert.Equal("RESUMED-OK", Encoding.UTF8.GetString(buf, 0, n));
        }

        await serverTask;
        Assert.True(secondConnVerifiedBinder);
    }

    // ---- 3. Synthetic HRR, CompressedCertificate (zlib/brotli/zstd + >16 MiB), KeyUpdate, Rejections ----

    [Fact]
    public async Task Tls13HelloRetryRequestX25519RejectedRetriesSecp256r1InTcpAndQuic()
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole HRR Test Root");
        using X509Certificate2 serverCert = CreateTestLeaf(leafKey, caCert, TestHost);

        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);

        using var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        int port = ((IPEndPoint)listener.LocalEndpoint).Port;

        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        byte[] cookie = "hrr-cookie-token-42"u8.ToArray();

        Task serverTask = Task.Run(async () =>
        {
            using TcpClient c = await listener.AcceptTcpClientAsync(cts.Token);
            using NetworkStream s = c.GetStream();
            var srv = new SyntheticTls13Server(s, leafKey, new[] { serverCert.RawData, caCert.RawData });
            await srv.AcceptFullHandshakeWithHrrAsync(
                hrrSelectedGroup: NamedGroupId.Secp256r1,
                cookie: cookie,
                alpn: "h2",
                ct: cts.Token);

            byte[] msg = await srv.ReadAppDataAsync(cts.Token);
            Assert.Equal("PING-HRR", Encoding.UTF8.GetString(msg));
            await srv.SendAppDataAsync("HRR-OK"u8.ToArray(), cts.Token);
            await srv.SendCloseNotifyAsync(cts.Token);
        }, cts.Token);

        using (var tcp = new TcpClient())
        {
            await tcp.ConnectAsync(IPAddress.Loopback, port, cts.Token);
            await using var tls = new TlsStream(tcp.GetStream(), new TlsConnectionOptions
            {
                ServerName = TestHost,
                Port = port,
                Profile = ProfileRegistry.GetRequired("chrome_131"),
                VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
            });

            await tls.HandshakeAsync(cts.Token);
            Assert.True(tls.HandshakeCompleted);
            await tls.WriteAsync("PING-HRR"u8.ToArray(), cts.Token);

            var buf = new byte[32];
            int n = await tls.ReadAsync(buf, cts.Token);
            Assert.Equal("HRR-OK", Encoding.UTF8.GetString(buf, 0, n));
        }

        await serverTask;

        // Verify QUIC-mode TlsHandshakeEngine HRR handling (Initial CRYPTO level ClientHello2)
        using var quicEngine = new TlsHandshakeEngine(new TlsHandshakeOptions
        {
            ServerName = TestHost,
            Profile = ProfileRegistry.GetRequired("chrome_150"),
            SpecOverride = ChromeQuicSpecs.CreateClientHelloSpec(),
        });
        byte[] ch1 = quicEngine.StartQuicHandshake(new byte[] { 0x01, 0x02, 0x03, 0x04 });
        ParsedClientHello parsedCh1 = SyntheticTls13Server.ParseClientHello(ch1);

        byte[] hrrMsg = SyntheticTls13Server.BuildServerHelloMessage(
            random: SyntheticTls13Server.HrrMagicRandom,
            sessionId: parsedCh1.SessionId,
            cipherSuite: CipherSuiteId.TLS_AES_128_GCM_SHA256,
            extensions: new List<(ushort, byte[])>
            {
                (TlsExtensionType.SupportedVersions, new byte[] { 0x03, 0x04 }),
                (TlsExtensionType.KeyShare, new byte[] { 0x00, 0x17 }),
                (0x002C, PrependUInt16Len(cookie)),
            });

        QuicHandshakeStepResult step = quicEngine.ProcessQuicCryptoData(QuicEncryptionLevel.Initial, hrrMsg);
        Assert.Equal(QuicEncryptionLevel.Initial, step.OutboundEncryptionLevel);
        Assert.NotEmpty(step.OutboundInitialData);
        Assert.Empty(step.OutboundHandshakeData);

        ParsedClientHello parsedCh2 = SyntheticTls13Server.ParseClientHello(step.OutboundInitialData);
        Assert.Equal(parsedCh1.Random, parsedCh2.Random);
        Assert.Empty(parsedCh2.SessionId);
        Assert.True(parsedCh2.Extensions.ContainsKey(0x002C));
        Assert.Equal(PrependUInt16Len(cookie), parsedCh2.Extensions[0x002C]);
        Assert.Equal(1, parsedCh2.KeyShares.Count);
        Assert.True(parsedCh2.KeyShares.ContainsKey(NamedGroupId.Secp256r1));
    }

    [Fact]
    public void Tls13HrrWithChrome150_AcceptsMiddleboxCcs_UsesTls12RecordVersion_AndPreservesGreaseAndOrder()
    {
        using var engine = new TlsHandshakeEngine(new TlsHandshakeOptions
        {
            ServerName = TestHost,
            Profile = ProfileRegistry.GetRequired("chrome_150"),
        });

        byte[] ch1Record = engine.StartTcpHandshake();
        Assert.Equal(0x16, ch1Record[0]);
        TlsWireFingerprintResult fp1 = WireFingerprint.AnalyzeClientHello(ch1Record.AsSpan(5), isQuic: false);
        ParsedClientHello parsed1 = SyntheticTls13Server.ParseClientHello(ch1Record.AsSpan(5));

        byte[] hrrMsg = SyntheticTls13Server.BuildServerHelloMessage(
            random: SyntheticTls13Server.HrrMagicRandom,
            sessionId: parsed1.SessionId,
            cipherSuite: CipherSuiteId.TLS_AES_128_GCM_SHA256,
            extensions: new List<(ushort, byte[])>
            {
                (TlsExtensionType.SupportedVersions, new byte[] { 0x03, 0x04 }),
                (TlsExtensionType.KeyShare, new byte[] { 0x00, 0x17 }),
            });

        List<TcpStepOperation> ops = engine.ProcessTcpRecord(TlsContentType.Handshake, hrrMsg);
        TcpStepOperation ch2Op = Assert.Single(ops, o => o.Kind == TcpStepOperationKind.SendPlaintextRecord);
        Assert.Equal(TlsContentType.Handshake, ch2Op.ContentType);
        Assert.Equal(TlsVersion.Tls12, ch2Op.RecordVersion);

        // Server middlebox compatibility ChangeCipherSpec sent immediately after HRR must be accepted cleanly.
        List<TcpStepOperation> ccsOps = engine.ProcessTcpRecord(TlsContentType.ChangeCipherSpec, new byte[] { 0x01 });
        Assert.Empty(ccsOps);

        TlsWireFingerprintResult fp2 = WireFingerprint.AnalyzeClientHello(ch2Op.Payload, isQuic: false);
        Assert.Equal(fp1.CipherSuites, fp2.CipherSuites);
        Assert.Equal(fp1.SupportedGroups, fp2.SupportedGroups);
        Assert.Equal(fp1.ExtensionTypes, fp2.ExtensionTypes);
        Assert.Equal(fp1.Ja4, fp2.Ja4);
        Assert.Equal(fp1.Ja3Hash, fp2.Ja3Hash);
    }

    [Theory]
    [InlineData(CertCompressionAlgorithm.Zlib)]
    [InlineData(CertCompressionAlgorithm.Brotli)]
    [InlineData(CertCompressionAlgorithm.Zstd)]
    public async Task Tls13CompressedCertificateDecodesAllAlgorithmsAndVerifiesTranscript(CertCompressionAlgorithm algorithm)
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole CompCert Root");
        using X509Certificate2 serverCert = CreateTestLeaf(leafKey, caCert, TestHost);

        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);

        using var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        int port = ((IPEndPoint)listener.LocalEndpoint).Port;

        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        Task serverTask = Task.Run(async () =>
        {
            using TcpClient c = await listener.AcceptTcpClientAsync(cts.Token);
            using NetworkStream s = c.GetStream();
            var srv = new SyntheticTls13Server(s, leafKey, new[] { serverCert.RawData, caCert.RawData });
            await srv.AcceptFullHandshakeAsync(alpn: "h2", certCompression: algorithm, ct: cts.Token);
            await srv.SendAppDataAsync("COMP-OK"u8.ToArray(), cts.Token);
            await srv.SendCloseNotifyAsync(cts.Token);
        }, cts.Token);

        using (var tcp = new TcpClient())
        {
            await tcp.ConnectAsync(IPAddress.Loopback, port, cts.Token);
            // firefox_148 advertises [Zlib, Brotli, Zstd]
            await using var tls = new TlsStream(tcp.GetStream(), new TlsConnectionOptions
            {
                ServerName = TestHost,
                Port = port,
                Profile = ProfileRegistry.GetRequired("firefox_148"),
                VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
            });

            await tls.HandshakeAsync(cts.Token);
            Assert.True(tls.HandshakeCompleted);

            var buf = new byte[32];
            int n = await tls.ReadAsync(buf, cts.Token);
            Assert.Equal("COMP-OK", Encoding.UTF8.GetString(buf, 0, n));
        }

        await serverTask;
    }

    [Fact]
    public async Task Tls13CompressedCertificateRejectsOver16MiBAndDecompressionLengthMismatch()
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole CompBomb Root");
        using X509Certificate2 serverCert = CreateTestLeaf(leafKey, caCert, TestHost);

        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);

        // Case 1: Declared uncompressed_length = 16 MiB + 1 -> rejected without allocating 16 MiB
        await RunNegativeServerAttemptAsync<TlsAlertException>(
            async (s, ct) =>
            {
                var srv = new SyntheticTls13Server(s, leafKey, new[] { serverCert.RawData });
                await srv.SendCompressedCertificateWithDeclaredSizeAsync(
                    CertCompressionAlgorithm.Brotli,
                    declaredUncompressedSize: 16 * 1024 * 1024 + 1,
                    compressedPayload: new byte[] { 0x06 },
                    ct);
            },
            port => new TlsConnectionOptions
            {
                ServerName = TestHost,
                Port = port,
                Profile = ProfileRegistry.GetRequired("firefox_148"),
                VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
            });

        // Case 2: Declared uncompressed_length smaller than actual decompressed output -> rejected
        byte[] oversizedData = new byte[512];
        byte[] compressed = CompressWith(CertCompressionAlgorithm.Brotli, oversizedData);
        await RunNegativeServerAttemptAsync<TlsAlertException>(
            async (s, ct) =>
            {
                var srv = new SyntheticTls13Server(s, leafKey, new[] { serverCert.RawData });
                await srv.SendCompressedCertificateWithDeclaredSizeAsync(
                    CertCompressionAlgorithm.Brotli,
                    declaredUncompressedSize: 64,
                    compressedPayload: compressed,
                    ct);
            },
            port => new TlsConnectionOptions
            {
                ServerName = TestHost,
                Port = port,
                Profile = ProfileRegistry.GetRequired("firefox_148"),
                VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
            });
    }

    [Fact]
    public async Task Tls13KeyUpdateUpdateRequestedRotatesBothDirectionsAndIsRejectedInQuic()
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole KeyUpdate Root");
        using X509Certificate2 serverCert = CreateTestLeaf(leafKey, caCert, TestHost);

        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);

        using var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        int port = ((IPEndPoint)listener.LocalEndpoint).Port;
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));

        byte[]? serverReceivedAfterKeyUpdate = null;

        Task serverTask = Task.Run(async () =>
        {
            using TcpClient c = await listener.AcceptTcpClientAsync(cts.Token);
            using NetworkStream s = c.GetStream();
            var srv = new SyntheticTls13Server(s, leafKey, new[] { serverCert.RawData, caCert.RawData });
            await srv.AcceptFullHandshakeAsync(alpn: "h2", ct: cts.Token);

            // Server initiates KeyUpdate(update_requested = 1), rotates server write key, sends new encrypted message
            await srv.SendKeyUpdateAndRotateWriteKeyAsync(updateRequested: true, cts.Token);
            await srv.SendAppDataAsync("AFTER-SERVER-KU"u8.ToArray(), cts.Token);

            // Server expects client's KeyUpdate(update_not_requested = 0) under OLD client key, then rotates read key
            await srv.ExpectClientKeyUpdateAndRotateReadKeyAsync(cts.Token);
            serverReceivedAfterKeyUpdate = await srv.ReadAppDataAsync(cts.Token);
            await srv.SendCloseNotifyAsync(cts.Token);
        }, cts.Token);

        using (var tcp = new TcpClient())
        {
            await tcp.ConnectAsync(IPAddress.Loopback, port, cts.Token);
            await using var tls = new TlsStream(tcp.GetStream(), new TlsConnectionOptions
            {
                ServerName = TestHost,
                Port = port,
                Profile = ProfileRegistry.GetRequired("chrome_131"),
                VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
            });

            await tls.HandshakeAsync(cts.Token);

            var buf = new byte[64];
            int n = await tls.ReadAsync(buf, cts.Token);
            Assert.Equal("AFTER-SERVER-KU", Encoding.UTF8.GetString(buf, 0, n));

            await tls.WriteAsync("CLIENT-AFTER-KU"u8.ToArray(), cts.Token);
            await tls.FlushAsync(cts.Token);
            Assert.Equal(0, await tls.ReadAsync(buf, cts.Token));
        }

        await serverTask;
        Assert.Equal("CLIENT-AFTER-KU", Encoding.UTF8.GetString(serverReceivedAfterKeyUpdate!));

        // Verify QUIC rejects KeyUpdate per RFC 9001 §6
        var (quicEngine, _) = CompleteSyntheticQuicHandshake(leafKey, serverCert.RawData, caCert.RawData, roots);
        using (quicEngine)
        {
            var kuEx = Assert.Throws<TlsAlertException>(() =>
                quicEngine.ProcessQuicCryptoData(QuicEncryptionLevel.Application, new byte[] { 0x18, 0x00, 0x00, 0x01, 0x01 }));
            Assert.Equal(TlsAlertDescription.UnexpectedMessage, kuEx.Description);
        }
    }

    [Fact]
    public async Task Tls13RejectsInvalidCertificateVerifyUntrustedCertHostnameMismatchAndBadPin()
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole Security Reject Root");
        using X509Certificate2 serverCert = CreateTestLeaf(leafKey, caCert, TestHost);

        var trustedRoots = new RootCertificateDatabase();
        trustedRoots.AddDer(caCert.RawData);

        // 1. Corrupt CertificateVerify signature -> DecryptError
        await RunNegativeServerAttemptAsync<TlsAlertException>(
            async (s, ct) =>
            {
                var srv = new SyntheticTls13Server(s, leafKey, new[] { serverCert.RawData, caCert.RawData });
                await srv.AcceptFullHandshakeAsync(corruptCertVerify: true, ct: ct);
            },
            port => new TlsConnectionOptions
            {
                ServerName = TestHost,
                Port = port,
                Profile = ProfileRegistry.GetRequired("chrome_131"),
                VerifyOptions = new CertificateVerifyOptions { CustomRoots = trustedRoots, UseEmbeddedDefaultRoots = false },
            });

        // 2. Untrusted root (empty roots) -> CertificateValidationException
        await RunNegativeServerAttemptAsync<CertificateValidationException>(
            async (s, ct) =>
            {
                var srv = new SyntheticTls13Server(s, leafKey, new[] { serverCert.RawData, caCert.RawData });
                await srv.AcceptFullHandshakeAsync(ct: ct);
            },
            port => new TlsConnectionOptions
            {
                ServerName = TestHost,
                Port = port,
                Profile = ProfileRegistry.GetRequired("chrome_131"),
                VerifyOptions = new CertificateVerifyOptions { UseEmbeddedDefaultRoots = false },
            });

        // 3. Hostname mismatch -> CertificateValidationException
        await RunNegativeServerAttemptAsync<CertificateValidationException>(
            async (s, ct) =>
            {
                var srv = new SyntheticTls13Server(s, leafKey, new[] { serverCert.RawData, caCert.RawData });
                await srv.AcceptFullHandshakeAsync(ct: ct);
            },
            port => new TlsConnectionOptions
            {
                ServerName = "wrong-host.example.com",
                Port = port,
                Profile = ProfileRegistry.GetRequired("chrome_131"),
                VerifyOptions = new CertificateVerifyOptions { CustomRoots = trustedRoots, UseEmbeddedDefaultRoots = false },
            });

        // 4. Pin mismatch -> BadPinException
        var badPinner = new CertificatePinner();
        badPinner.AddPin(TestHost, "sha256/" + Convert.ToBase64String(new byte[32]));
        await RunNegativeServerAttemptAsync<BadPinException>(
            async (s, ct) =>
            {
                var srv = new SyntheticTls13Server(s, leafKey, new[] { serverCert.RawData, caCert.RawData });
                await srv.AcceptFullHandshakeAsync(ct: ct);
            },
            port => new TlsConnectionOptions
            {
                ServerName = TestHost,
                Port = port,
                Profile = ProfileRegistry.GetRequired("chrome_131"),
                VerifyOptions = new CertificateVerifyOptions
                {
                    CustomRoots = trustedRoots,
                    UseEmbeddedDefaultRoots = false,
                    Pinner = badPinner,
                },
            });
    }

    private static async Task RunNegativeServerAttemptAsync<TException>(
        Func<NetworkStream, CancellationToken, Task> serverAction,
        Func<int, TlsConnectionOptions> optionsFactory) where TException : Exception
    {
        using var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        int port = ((IPEndPoint)listener.LocalEndpoint).Port;
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(10));

        Task srvTask = Task.Run(async () =>
        {
            using TcpClient c = await listener.AcceptTcpClientAsync(cts.Token);
            using NetworkStream s = c.GetStream();
            try
            {
                await serverAction(s, cts.Token);
            }
            catch (IOException)
            {
            }
        }, cts.Token);

        try
        {
            await Assert.ThrowsAsync<TException>(async () =>
            {
                using var tcp = new TcpClient();
                await tcp.ConnectAsync(IPAddress.Loopback, port, cts.Token);
                await using var tls = new TlsStream(tcp.GetStream(), optionsFactory(port));
                await tls.HandshakeAsync(cts.Token);
            });
        }
        finally
        {
            await srvTask;
        }
    }

    // ---- 4. ClientHelloBuilder Fingerprint Invariants & Session Cache Tests ----

    [Fact]
    public void ClientHelloBuilderHonorsGreaseShufflingBoringPaddingPostQuantumAndQuicWireFormat()
    {
        // 1. GREASE placement in chrome_150
        using (ClientHelloBuildResult ch150 = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
        {
            Profile = ProfileRegistry.GetRequired("chrome_150"),
            ServerName = "www.nike.com",
            Random = new Random(1337),
        }))
        {
            ParsedClientHello parsed = SyntheticTls13Server.ParseClientHello(ch150.HandshakeMessage);
            Assert.True(GreaseHelper.IsGrease(parsed.CipherSuites[0]));
            Assert.True(GreaseHelper.IsGrease(parsed.ExtensionOrder[0]));
            Assert.True(GreaseHelper.IsGrease(parsed.ExtensionOrder[^1]));
            Assert.NotEqual(parsed.ExtensionOrder[0], parsed.ExtensionOrder[^1]);

            // X25519MLKEM768 (0x11EC) wire key share must be 1216 bytes (1184 + 32)
            Assert.True(parsed.KeyShares.TryGetValue(NamedGroupId.X25519MLKEM768, out byte[]? pqShare));
            Assert.Equal(1216, pqShare!.Length);
            Assert.True(parsed.KeyShares.TryGetValue(NamedGroupId.X25519, out byte[]? xShare));
            Assert.Equal(32, xShare!.Length);

            // Verify HybridKem encapsulation/decapsulation works against generated 1216-byte wire keyshare
            AsymmetricKeyShareState clientPqState = ch150.KeyShares[NamedGroupId.X25519MLKEM768];
            (byte[] mlKemCt, byte[] mlKemPeerSs) = MlKem768.Encaps(pqShare.AsSpan(0, MlKem768.EncapsulationKeySize));
            X25519.GenerateKeyPair(out byte[] srvXPriv, out byte[] srvXPub);
            byte[] xPeerSs = X25519.ScalarMult(srvXPriv, pqShare.AsSpan(MlKem768.EncapsulationKeySize, 32));
            var serverShare = new byte[MlKem768.CiphertextSize + 32];
            mlKemCt.CopyTo(serverShare, 0);
            srvXPub.CopyTo(serverShare, MlKem768.CiphertextSize);
            byte[] clientSs = clientPqState.DeriveSharedSecret(serverShare);
            byte[] expectedCombined = new byte[64];
            mlKemPeerSs.CopyTo(expectedCombined, 0);
            xPeerSs.CopyTo(expectedCombined, 32);
            Assert.Equal(expectedCombined, clientSs);
        }

        // Legacy PQ chrome_124 advertises X25519Kyber768Draft00 (0x6399) with 1216-byte share
        using (ClientHelloBuildResult ch124 = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
        {
            Profile = ProfileRegistry.GetRequired("chrome_124"),
            ServerName = "www.nike.com",
            Random = new Random(7),
        }))
        {
            ParsedClientHello parsed = SyntheticTls13Server.ParseClientHello(ch124.HandshakeMessage);
            Assert.True(parsed.KeyShares.TryGetValue(NamedGroupId.X25519Kyber768Draft00, out byte[]? kyberShare));
            Assert.Equal(1216, kyberShare!.Length);
        }

        // 2. RandomExtensionOrder permutes interior extensions across seeds while keeping GREASE pinned
        var observedOrders = new HashSet<string>(StringComparer.Ordinal);
        for (int seed = 10; seed < 30; seed++)
        {
            using ClientHelloBuildResult r = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
            {
                Profile = ProfileRegistry.GetRequired("chrome_150"),
                ServerName = "example.com",
                Random = new Random(seed),
            });
            observedOrders.Add(string.Join(",", r.OfferedExtensionTypes.Select(x => x.ToString("X4"))));
        }
        Assert.True(observedOrders.Count > 1);

        // 3. BoringPaddingStyle pads ClientHello body in [256..511] to exactly 512 bytes, keeping PSK strictly LAST
        using (ClientHelloBuildResult paddedNoPsk = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
        {
            Profile = ProfileRegistry.GetRequired("chrome_117"),
            ServerName = "example.com",
            Random = new Random(123),
        }))
        {
            Assert.Equal(512, paddedNoPsk.HandshakeBody.Length);
            Assert.Equal(TlsExtensionType.Padding, paddedNoPsk.OfferedExtensionTypes[^1]);
            Assert.True(paddedNoPsk.PaddingPayloadBytes > 0);
        }

        var dummyTicket = new TlsSessionTicket(
            ticket: new byte[32],
            ticketAgeAdd: 0x11223344,
            lifetimeSeconds: 3600,
            issuedAtUtc: DateTimeOffset.UtcNow.AddSeconds(-5),
            resumptionMasterSecret: new byte[32],
            ticketNonce: new byte[] { 0x01 },
            cipherSuite: CipherSuiteId.TLS_AES_128_GCM_SHA256,
            hashAlg: HashAlgorithmKind.Sha256);

        using (ClientHelloBuildResult paddedWithPsk = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
        {
            Profile = ProfileRegistry.GetRequired("chrome_116_PSK"),
            ServerName = "example.com",
            SessionTicket = dummyTicket,
            Random = new Random(123),
        }))
        {
            Assert.True(paddedWithPsk.OfferedPsk);
            Assert.Equal(512, paddedWithPsk.HandshakeBody.Length);
            Assert.Equal(TlsExtensionType.PreSharedKey, paddedWithPsk.OfferedExtensionTypes[^1]);
            Assert.Equal(TlsExtensionType.Padding, paddedWithPsk.OfferedExtensionTypes[^2]);
        }

        // 4. QUIC mode ClientHello: empty legacy_session_id, 0x0039 quic_transport_parameters, no 5B record header
        byte[] tpBytes = { 0x01, 0x02, 0xAA, 0xBB, 0xCC };
        byte[] quicMsg = TlsClientHelloBuilder.SerializeClientHelloMessage(
            ProfileRegistry.GetRequired("chrome_150"),
            serverName: "quic.example.com",
            isQuicMode: true,
            quicTransportParameters: tpBytes);
        Assert.Equal(0x01, quicMsg[0]); // HandshakeType.ClientHello
        ParsedClientHello parsedQuic = SyntheticTls13Server.ParseClientHello(quicMsg);
        Assert.Empty(parsedQuic.SessionId);
        Assert.True(parsedQuic.Extensions.TryGetValue(TlsExtensionType.QuicTransportParameters, out byte[]? parsedTp));
        Assert.Equal(tpBytes, parsedTp);
        Assert.All(parsedQuic.CipherSuites, c => Assert.True(c is 0x1301 or 0x1302 or 0x1303));

        // 5. ProxyTlsSpec alignment + every single one of 82 slot profiles builds cleanly
        byte[] proxyRec = TlsClientHelloBuilder.BuildClientHelloRecord(ProxyTlsSpec.Profile, "proxy.internal.local");
        Assert.Equal(0x16, proxyRec[0]);
        ParsedClientHello parsedProxy = SyntheticTls13Server.ParseClientHello(proxyRec.AsSpan(5));
        Assert.Equal(
            new ushort[] { 0, 5, 10, 11, 13, 65281, 16, 18, 23, 43, 45, 51 },
            parsedProxy.ExtensionOrder);

        foreach (ClientProfile p in ProfileRegistry.AllSlotProfiles)
        {
            byte[] rec = TlsClientHelloBuilder.BuildClientHelloRecord(p, "checkout.example.com");
            Assert.Equal(0x16, rec[0]);
            Assert.Equal(0x03, rec[1]);
            Assert.Equal(0x01, rec[2]);
            int recLen = BinaryPrimitives.ReadUInt16BigEndian(rec.AsSpan(3, 2));
            Assert.Equal(rec.Length - 5, recLen);
            Assert.Equal(0x01, rec[5]);
        }
    }

    [Fact]
    public void LruTlsSessionCacheEvictsLruAndPrunesExpiredEntries()
    {
        var cache = new LruTlsSessionCache(capacity: 2);
        Assert.Equal(2, cache.Capacity);

        DateTimeOffset t0 = new(2026, 11, 23, 6, 0, 0, TimeSpan.Zero);
        TlsSessionTicket MakeTicket(byte tag, uint lifetimeSec = 600) => new(
            ticket: new byte[] { tag, 0x01 },
            ticketAgeAdd: 42,
            lifetimeSeconds: lifetimeSec,
            issuedAtUtc: t0,
            resumptionMasterSecret: new byte[32],
            ticketNonce: new byte[] { tag },
            cipherSuite: CipherSuiteId.TLS_AES_128_GCM_SHA256,
            hashAlg: HashAlgorithmKind.Sha256);

        cache.Put("a.com", 443, "chrome_131_PSK", MakeTicket(1));
        cache.Put("b.com", 443, "chrome_131_PSK", MakeTicket(2));
        Assert.Equal(2, cache.Count);

        // Promote a.com to MRU via TryPeek
        Assert.True(cache.TryPeek("a.com", 443, "chrome_131_PSK", out _, t0.AddSeconds(10)));

        // Adding c.com evicts b.com (LRU tail)
        cache.Put("c.com", 443, "chrome_131_PSK", MakeTicket(3));
        Assert.Equal(2, cache.Count);
        Assert.False(cache.TryPeek("b.com", 443, "chrome_131_PSK", out _, t0.AddSeconds(10)));
        Assert.True(cache.TryPeek("a.com", 443, "chrome_131_PSK", out _, t0.AddSeconds(10)));

        // Expired ticket on d.com is pruned on TryTake
        cache.Put("d.com", 443, "chrome_131_PSK", MakeTicket(4, lifetimeSec: 5));
        Assert.False(cache.TryTake("d.com", 443, "chrome_131_PSK", out _, t0.AddSeconds(10)));
        cache.Clear();
        Assert.Equal(0, cache.Count);
    }

    [Theory]
    [InlineData("chrome_150", (ushort)0x44CD)]
    [InlineData("chrome_133", (ushort)0x4469)]
    public async Task Tls13Alps_TcpAndQuic_SendsClientEncryptedExtensionsBeforeFinishedAndVerifiesTranscript(
        string profileName,
        ushort alpsCodepoint)
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole Test Root CA");
        using X509Certificate2 serverCert = CreateTestLeaf(leafKey, caCert, TestHost);

        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);
        byte[] serverAlpsData = { 0xDE, 0xAD, 0xBE, 0xEF };
        byte[] expectedClientEe =
        {
            0x08, 0x00, 0x00, 0x06,
            0x00, 0x04,
            (byte)(alpsCodepoint >> 8), (byte)alpsCodepoint,
            0x00, 0x00,
        };

        // Part A: TCP path (SyntheticTls13Server asserts exact 10-byte client EE, Finished transcript including client EE, and bidirectional AppData using serverFinHash traffic keys)
        using var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        int port = ((IPEndPoint)listener.LocalEndpoint).Port;
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));

        Exception? serverError = null;
        Task serverTask = Task.Run(async () =>
        {
            try
            {
                using TcpClient accepted = await listener.AcceptTcpClientAsync(cts.Token);
                using NetworkStream ns = accepted.GetStream();
                var srv = new SyntheticTls13Server(ns, leafKey, new[] { serverCert.RawData, caCert.RawData });
                await srv.AcceptFullHandshakeAsync(
                    alpn: "h2",
                    alpsCodepoint: alpsCodepoint,
                    serverAlpsData: serverAlpsData,
                    ct: cts.Token);

                byte[] rx = await srv.ReadAppDataAsync(cts.Token);
                await srv.SendAppDataAsync(rx, cts.Token);
                await srv.SendCloseNotifyAsync(cts.Token);
            }
            catch (Exception ex)
            {
                serverError = ex;
            }
        }, cts.Token);

        using (var tcp = new TcpClient())
        {
            await tcp.ConnectAsync(IPAddress.Loopback, port, cts.Token);
            var tcpOptions = new TlsConnectionOptions
            {
                ServerName = TestHost,
                Port = port,
                Profile = ProfileRegistry.GetRequired(profileName),
                VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
            };
            await using var tls = new TlsStream(tcp.GetStream(), tcpOptions);
            await tls.HandshakeAsync(cts.Token);
            Assert.True(tls.HandshakeCompleted);
            Assert.Equal("h2", tls.NegotiatedAlpn);

            byte[] ping = Encoding.ASCII.GetBytes("alps-ping-payload");
            await tls.WriteAsync(ping, cts.Token);
            await tls.FlushAsync(cts.Token);
            var pong = new byte[ping.Length];
            await ReadExactlyAsync(tls, pong, cts.Token);
            Assert.Equal(ping, pong);

            var eof = new byte[8];
            Assert.Equal(0, await tls.ReadAsync(eof, cts.Token));
            await tls.ShutdownAsync(cts.Token);
        }

        await serverTask;
        Assert.Null(serverError);

        // Part B: QUIC path (TlsHandshakeEngine emits 10-byte client EE + 36-byte Finished with updated transcript and stores PeerApplicationSettings)
        var clientTp = new byte[] { 0x01, 0x02, 0x03 };
        var serverTp = new byte[] { 0x0A, 0x0B, 0x0C, 0x0D };
        var engine = new TlsHandshakeEngine(new TlsHandshakeOptions
        {
            ServerName = TestHost,
            Profile = ProfileRegistry.GetRequired(profileName),
            SpecOverride = ChromeQuicSpecs.CreateClientHelloSpec(),
            VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
        });

        byte[] ch = engine.StartQuicHandshake(clientTp);
        ParsedClientHello parsedCh = SyntheticTls13Server.ParseClientHello(ch);
        byte[] clientXPub = parsedCh.KeyShares[NamedGroupId.X25519];
        X25519.GenerateKeyPair(out byte[] sPriv, out byte[] sPub);
        byte[] sharedSecret = X25519.ScalarMult(sPriv, clientXPub);

        byte[] sh = SyntheticTls13Server.BuildServerHelloMessage(
            RandomNumberGenerator.GetBytes(32),
            parsedCh.SessionId,
            CipherSuiteId.TLS_AES_128_GCM_SHA256,
            new List<(ushort, byte[])>
            {
                (TlsExtensionType.SupportedVersions, new byte[] { 0x03, 0x04 }),
                (TlsExtensionType.KeyShare, SyntheticTls13Server.BuildServerKeyShare(NamedGroupId.X25519, sPub)),
            });

        QuicHandshakeStepResult shRes = engine.ProcessQuicCryptoData(QuicEncryptionLevel.Initial, sh);
        Assert.NotNull(shRes.HandshakeReadKeys);

        var transcript = new MemoryStream();
        transcript.Write(ch);
        transcript.Write(sh);

        byte[] ee = SyntheticTls13Server.BuildEncryptedExtensions("h3", serverTp, alpsCodepoint, serverAlpsData);
        transcript.Write(ee);
        byte[] certMsg = SyntheticTls13Server.BuildCertificateMessage(new[] { serverCert.RawData, caCert.RawData });
        transcript.Write(certMsg);
        byte[] cvMsg = SyntheticTls13Server.BuildCertificateVerifyMessage(leafKey, HashPrimitives.Sha256(transcript.ToArray()));
        transcript.Write(cvMsg);

        byte[] earlySecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, ReadOnlySpan<byte>.Empty, new byte[32]);
        byte[] emptyHash = HashPrimitives.Sha256(ReadOnlySpan<byte>.Empty);
        byte[] derived = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, earlySecret, "derived", emptyHash, 32);
        byte[] hsSecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, derived, sharedSecret);
        byte[] shHash = HashPrimitives.Sha256(ch.Concat(sh).ToArray());
        byte[] sHsSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, hsSecret, "s hs traffic", shHash, 32);
        byte[] cHsSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, hsSecret, "c hs traffic", shHash, 32);
        byte[] sFinKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, sHsSecret, "finished", ReadOnlySpan<byte>.Empty, 32);
        byte[] sFinMsg = SyntheticTls13Server.WrapHandshakeMessage(0x14, HashPrimitives.Hmac(HashAlgorithmKind.Sha256, sFinKey, HashPrimitives.Sha256(transcript.ToArray())));
        transcript.Write(sFinMsg);

        byte[] flight = ee.Concat(certMsg).Concat(cvMsg).Concat(sFinMsg).ToArray();
        QuicHandshakeStepResult finalRes = engine.ProcessQuicCryptoData(QuicEncryptionLevel.Handshake, flight);
        Assert.True(finalRes.HandshakeCompleted);
        Assert.Equal("h3", finalRes.NegotiatedAlpn);
        Assert.Equal(serverAlpsData, engine.PeerApplicationSettings);

        byte[] clientFlight = finalRes.OutboundHandshakeData;
        Assert.Equal(10 + 36, clientFlight.Length);
        Assert.Equal(expectedClientEe, clientFlight.AsSpan(0, 10).ToArray());
        transcript.Write(clientFlight, 0, 10);

        byte[] cFinMsg = clientFlight.AsSpan(10).ToArray();
        Assert.Equal(0x14, cFinMsg[0]);
        byte[] cFinKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, cHsSecret, "finished", ReadOnlySpan<byte>.Empty, 32);
        byte[] expectedCFin = HashPrimitives.Hmac(HashAlgorithmKind.Sha256, cFinKey, HashPrimitives.Sha256(transcript.ToArray()));
        Assert.Equal(expectedCFin, cFinMsg.AsSpan(4).ToArray());
    }

    [Fact]
    public void Tls13EarlyDataAccepted_InQuicMode_OmitsEndOfEarlyDataFromTranscriptPerRfc9001Section83()
    {
        DateTimeOffset now = DateTimeOffset.UtcNow;
        ClientProfile profile = ProfileRegistry.GetRequired("chrome_150_PSK");
        byte[] psk = RandomNumberGenerator.GetBytes(32);
        byte[] ticketBytes = RandomNumberGenerator.GetBytes(24);
        var ticket = new TlsSessionTicket(
            ticket: ticketBytes,
            ticketAgeAdd: 0x01020304,
            lifetimeSeconds: 3600,
            issuedAtUtc: now.AddSeconds(-2),
            resumptionMasterSecret: RandomNumberGenerator.GetBytes(32),
            ticketNonce: new byte[] { 0x01 },
            cipherSuite: CipherSuiteId.TLS_AES_128_GCM_SHA256,
            hashAlg: HashAlgorithmKind.Sha256,
            negotiatedAlpn: "h3",
            maxEarlyDataSize: 16384,
            psk: psk);

        var sessionCache = new LruTlsSessionCache();
        sessionCache.Put(TestHost, 443, profile.Name, ticket);

        var engine = new TlsHandshakeEngine(new TlsHandshakeOptions
        {
            ServerName = TestHost,
            Port = 443,
            Profile = profile,
            SpecOverride = ChromeQuicSpecs.CreateClientHelloSpec(),
            SessionCache = sessionCache,
            NowUtc = now,
        });

        byte[] ch = engine.StartQuicHandshake(new byte[] { 0x01, 0x02, 0x03 });
        ParsedClientHello parsedCh = SyntheticTls13Server.ParseClientHello(ch);
        Assert.True(parsedCh.Extensions.ContainsKey(TlsExtensionType.PreSharedKey));
        Assert.True(parsedCh.Extensions.ContainsKey(TlsExtensionType.EarlyData));

        byte[] clientXPub = parsedCh.KeyShares[NamedGroupId.X25519];
        X25519.GenerateKeyPair(out byte[] sPriv, out byte[] sPub);
        byte[] sharedSecret = X25519.ScalarMult(sPriv, clientXPub);

        byte[] sh = SyntheticTls13Server.BuildServerHelloMessage(
            RandomNumberGenerator.GetBytes(32),
            parsedCh.SessionId,
            CipherSuiteId.TLS_AES_128_GCM_SHA256,
            new List<(ushort, byte[])>
            {
                (TlsExtensionType.SupportedVersions, new byte[] { 0x03, 0x04 }),
                (TlsExtensionType.KeyShare, SyntheticTls13Server.BuildServerKeyShare(NamedGroupId.X25519, sPub)),
                (TlsExtensionType.PreSharedKey, new byte[] { 0x00, 0x00 }),
            });

        QuicHandshakeStepResult shRes = engine.ProcessQuicCryptoData(QuicEncryptionLevel.Initial, sh);
        Assert.NotNull(shRes.HandshakeReadKeys);
        Assert.True(shRes.UsedSessionResumption);

        var transcript = new MemoryStream();
        transcript.Write(ch);
        transcript.Write(sh);

        // Build EncryptedExtensions with ALPN "h3", QUIC transport parameters, and early_data (0x002A) accepted
        var eeExtBuf = new List<byte>();
        byte[] alpnVal = { 0x00, 0x03, 0x02, (byte)'h', (byte)'3' };
        eeExtBuf.Add((byte)(TlsExtensionType.ApplicationLayerProtocolNegotiation >> 8));
        eeExtBuf.Add((byte)TlsExtensionType.ApplicationLayerProtocolNegotiation);
        eeExtBuf.Add((byte)(alpnVal.Length >> 8));
        eeExtBuf.Add((byte)alpnVal.Length);
        eeExtBuf.AddRange(alpnVal);

        byte[] serverTp = { 0x0A, 0x0B, 0x0C, 0x0D };
        eeExtBuf.Add((byte)(TlsExtensionType.QuicTransportParameters >> 8));
        eeExtBuf.Add((byte)TlsExtensionType.QuicTransportParameters);
        eeExtBuf.Add((byte)(serverTp.Length >> 8));
        eeExtBuf.Add((byte)serverTp.Length);
        eeExtBuf.AddRange(serverTp);

        eeExtBuf.Add((byte)(TlsExtensionType.EarlyData >> 8));
        eeExtBuf.Add((byte)TlsExtensionType.EarlyData);
        eeExtBuf.Add(0x00);
        eeExtBuf.Add(0x00);

        var eeBody = new byte[2 + eeExtBuf.Count];
        BinaryPrimitives.WriteUInt16BigEndian(eeBody.AsSpan(0, 2), (ushort)eeExtBuf.Count);
        eeExtBuf.CopyTo(eeBody, 2);
        byte[] ee = SyntheticTls13Server.WrapHandshakeMessage(0x08, eeBody);
        transcript.Write(ee);

        byte[] earlySecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, ReadOnlySpan<byte>.Empty, psk);
        byte[] emptyHash = HashPrimitives.Sha256(ReadOnlySpan<byte>.Empty);
        byte[] derived = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, earlySecret, "derived", emptyHash, 32);
        byte[] hsSecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, derived, sharedSecret);
        byte[] shHash = HashPrimitives.Sha256(ch.Concat(sh).ToArray());
        byte[] sHsSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, hsSecret, "s hs traffic", shHash, 32);
        byte[] cHsSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, hsSecret, "c hs traffic", shHash, 32);
        byte[] sFinKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, sHsSecret, "finished", ReadOnlySpan<byte>.Empty, 32);
        byte[] sFinMsg = SyntheticTls13Server.WrapHandshakeMessage(0x14, HashPrimitives.Hmac(HashAlgorithmKind.Sha256, sFinKey, HashPrimitives.Sha256(transcript.ToArray())));
        transcript.Write(sFinMsg);

        byte[] flight = ee.Concat(sFinMsg).ToArray();
        QuicHandshakeStepResult finalRes = engine.ProcessQuicCryptoData(QuicEncryptionLevel.Handshake, flight);
        Assert.True(finalRes.HandshakeCompleted);
        Assert.True(finalRes.UsedSessionResumption);
        Assert.Equal("h3", finalRes.NegotiatedAlpn);

        // RFC 9001 §8.3: QUIC does NOT send EndOfEarlyData and MUST NOT include it in Finished transcript.
        byte[] cFinMsg = finalRes.OutboundHandshakeData;
        Assert.Equal(36, cFinMsg.Length);
        Assert.Equal(0x14, cFinMsg[0]);
        byte[] cFinKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, cHsSecret, "finished", ReadOnlySpan<byte>.Empty, 32);
        byte[] expectedCFin = HashPrimitives.Hmac(HashAlgorithmKind.Sha256, cFinKey, HashPrimitives.Sha256(transcript.ToArray()));
        Assert.Equal(expectedCFin, cFinMsg.AsSpan(4).ToArray());
    }

    [Fact]
    public void TlsClientHello_EarlyData_MatchesOriginalCybersolePskAndStripsOnHelloRetryRequest()
    {
        DateTimeOffset now = DateTimeOffset.UtcNow;
        ClientProfile quicPskProfile = ProfileRegistry.GetRequired("chrome_150_PSK");
        ClientProfile tcp150PskProfile = ProfileRegistry.GetRequired("chrome_150_PSK");
        ClientProfile tcp152PskProfile = ProfileRegistry.GetRequired("chrome_152_PSK");
        byte[] psk = RandomNumberGenerator.GetBytes(32);
        var zeroMaxEarlyDataTicket = new TlsSessionTicket(
            ticket: RandomNumberGenerator.GetBytes(24),
            ticketAgeAdd: 0x11223344,
            lifetimeSeconds: 3600,
            issuedAtUtc: now.AddSeconds(-2),
            resumptionMasterSecret: RandomNumberGenerator.GetBytes(32),
            ticketNonce: new byte[] { 0x01 },
            cipherSuite: CipherSuiteId.TLS_AES_128_GCM_SHA256,
            hashAlg: HashAlgorithmKind.Sha256,
            negotiatedAlpn: "h3",
            maxEarlyDataSize: 0,
            psk: psk);

        // (1) QUIC + valid PSK ticket emits 0x002A even when maxEarlyDataSize == 0 (matches sub_141298FA0 a3 gate), empty payload, before PSK
        using (ClientHelloBuildResult withTicket = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
        {
            Profile = quicPskProfile,
            SpecOverride = ChromeQuicSpecs.CreateClientHelloSpec(),
            ServerName = TestHost,
            IsQuicMode = true,
            QuicTransportParameters = new byte[] { 0x01, 0x02, 0x03 },
            SessionTicket = zeroMaxEarlyDataTicket,
            NowUtc = now,
        }))
        {
            Assert.True(withTicket.OfferedPsk);
            Assert.True(withTicket.OfferedEarlyData);
            ParsedClientHello parsed = SyntheticTls13Server.ParseClientHello(withTicket.HandshakeMessage);
            Assert.True(parsed.Extensions.TryGetValue(TlsExtensionType.EarlyData, out byte[]? edPayload));
            Assert.Empty(edPayload!);
            int edIdx = parsed.ExtensionOrder.IndexOf(TlsExtensionType.EarlyData);
            int pskIdx = parsed.ExtensionOrder.IndexOf(TlsExtensionType.PreSharedKey);
            Assert.True(edIdx >= 0 && pskIdx > edIdx);
            Assert.Equal(parsed.ExtensionOrder.Count - 1, pskIdx);
        }

        // (2) QUIC without PSK ticket omits 0x002A
        using (ClientHelloBuildResult withoutTicket = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
        {
            Profile = quicPskProfile,
            SpecOverride = ChromeQuicSpecs.CreateClientHelloSpec(),
            ServerName = TestHost,
            IsQuicMode = true,
            QuicTransportParameters = new byte[] { 0x01, 0x02, 0x03 },
            SessionTicket = null,
            NowUtc = now,
        }))
        {
            Assert.False(withoutTicket.OfferedPsk);
            Assert.False(withoutTicket.OfferedEarlyData);
            ParsedClientHello parsed = SyntheticTls13Server.ParseClientHello(withoutTicket.HandshakeMessage);
            Assert.False(parsed.Extensions.ContainsKey(TlsExtensionType.EarlyData));
            Assert.False(parsed.Extensions.ContainsKey(TlsExtensionType.PreSharedKey));
        }

        // (3) QUIC ClientHello2 after HRR strips 0x002A while retaining PSK last (matches sub_141298420 predicate 0x141337520 & RFC 8446 §4.1.2)
        using (ClientHelloBuildResult ch2 = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
        {
            Profile = quicPskProfile,
            SpecOverride = ChromeQuicSpecs.CreateClientHelloSpec(),
            ServerName = TestHost,
            IsQuicMode = true,
            QuicTransportParameters = new byte[] { 0x01, 0x02, 0x03 },
            SessionTicket = zeroMaxEarlyDataTicket,
            HelloRetrySelectedGroup = NamedGroupId.Secp256r1,
            NowUtc = now,
        }))
        {
            Assert.True(ch2.OfferedPsk);
            Assert.False(ch2.OfferedEarlyData);
            ParsedClientHello parsed = SyntheticTls13Server.ParseClientHello(ch2.HandshakeMessage);
            Assert.False(parsed.Extensions.ContainsKey(TlsExtensionType.EarlyData));
            Assert.True(parsed.Extensions.ContainsKey(TlsExtensionType.PreSharedKey));
            Assert.Equal(TlsExtensionType.PreSharedKey, parsed.ExtensionOrder[^1]);
        }

        // (4) TCP chrome_150_PSK & chrome_152_PSK with ticket NEVER emit 0x002A
        foreach (ClientProfile tcpProfile in new[] { tcp150PskProfile, tcp152PskProfile })
        {
            using ClientHelloBuildResult tcpCh = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
            {
                Profile = tcpProfile,
                ServerName = TestHost,
                IsQuicMode = false,
                SessionTicket = zeroMaxEarlyDataTicket,
                NowUtc = now,
            });
            Assert.False(tcpCh.OfferedEarlyData);
            ParsedClientHello parsed = SyntheticTls13Server.ParseClientHello(tcpCh.HandshakeMessage);
            Assert.False(parsed.Extensions.ContainsKey(TlsExtensionType.EarlyData));
        }

        // (5) TlsHandshakeEngine QUIC HRR: server echoing 0x002A in EncryptedExtensions after ClientHello2 must throw UnsupportedExtension
        var sessionCache = new LruTlsSessionCache();
        sessionCache.Put(TestHost, 443, quicPskProfile.Name, zeroMaxEarlyDataTicket);
        using var engine = new TlsHandshakeEngine(new TlsHandshakeOptions
        {
            ServerName = TestHost,
            Port = 443,
            Profile = quicPskProfile,
            SpecOverride = ChromeQuicSpecs.CreateClientHelloSpec(),
            SessionCache = sessionCache,
            NowUtc = now,
        });

        byte[] ch1 = engine.StartQuicHandshake(new byte[] { 0x01, 0x02, 0x03 });
        ParsedClientHello parsedCh1 = SyntheticTls13Server.ParseClientHello(ch1);
        Assert.True(parsedCh1.Extensions.ContainsKey(TlsExtensionType.EarlyData));

        byte[] hrrMsg = SyntheticTls13Server.BuildServerHelloMessage(
            random: SyntheticTls13Server.HrrMagicRandom,
            sessionId: parsedCh1.SessionId,
            cipherSuite: CipherSuiteId.TLS_AES_128_GCM_SHA256,
            extensions: new List<(ushort, byte[])>
            {
                (TlsExtensionType.SupportedVersions, new byte[] { 0x03, 0x04 }),
                (0x002C, new byte[] { 0x00, 0x02, 0xCA, 0xFE }),
            });
        QuicHandshakeStepResult hrrStep = engine.ProcessQuicCryptoData(QuicEncryptionLevel.Initial, hrrMsg);
        ParsedClientHello parsedCh2 = SyntheticTls13Server.ParseClientHello(hrrStep.OutboundInitialData);
        Assert.False(parsedCh2.Extensions.ContainsKey(TlsExtensionType.EarlyData));
        Assert.True(parsedCh2.Extensions.ContainsKey(TlsExtensionType.PreSharedKey));

        X25519.GenerateKeyPair(out _, out byte[] sPub);
        byte[] sh2 = SyntheticTls13Server.BuildServerHelloMessage(
            random: RandomNumberGenerator.GetBytes(32),
            sessionId: parsedCh2.SessionId,
            cipherSuite: CipherSuiteId.TLS_AES_128_GCM_SHA256,
            extensions: new List<(ushort, byte[])>
            {
                (TlsExtensionType.SupportedVersions, new byte[] { 0x03, 0x04 }),
                (TlsExtensionType.KeyShare, SyntheticTls13Server.BuildServerKeyShare(NamedGroupId.X25519, sPub)),
                (TlsExtensionType.PreSharedKey, new byte[] { 0x00, 0x00 }),
            });
        engine.ProcessQuicCryptoData(QuicEncryptionLevel.Initial, sh2);

        var badEeExtBuf = new List<byte>();
        byte[] alpnVal = { 0x00, 0x03, 0x02, (byte)'h', (byte)'3' };
        badEeExtBuf.Add((byte)(TlsExtensionType.ApplicationLayerProtocolNegotiation >> 8));
        badEeExtBuf.Add((byte)TlsExtensionType.ApplicationLayerProtocolNegotiation);
        badEeExtBuf.Add((byte)(alpnVal.Length >> 8));
        badEeExtBuf.Add((byte)alpnVal.Length);
        badEeExtBuf.AddRange(alpnVal);

        byte[] serverTp = { 0x0A, 0x0B, 0x0C, 0x0D };
        badEeExtBuf.Add((byte)(TlsExtensionType.QuicTransportParameters >> 8));
        badEeExtBuf.Add((byte)TlsExtensionType.QuicTransportParameters);
        badEeExtBuf.Add((byte)(serverTp.Length >> 8));
        badEeExtBuf.Add((byte)serverTp.Length);
        badEeExtBuf.AddRange(serverTp);

        badEeExtBuf.Add((byte)(TlsExtensionType.EarlyData >> 8));
        badEeExtBuf.Add((byte)TlsExtensionType.EarlyData);
        badEeExtBuf.Add(0x00);
        badEeExtBuf.Add(0x00);

        var badEeBody = new byte[2 + badEeExtBuf.Count];
        BinaryPrimitives.WriteUInt16BigEndian(badEeBody.AsSpan(0, 2), (ushort)badEeExtBuf.Count);
        badEeExtBuf.CopyTo(badEeBody, 2);
        byte[] badEe = SyntheticTls13Server.WrapHandshakeMessage(0x08, badEeBody);

        TlsAlertException alert = Assert.Throws<TlsAlertException>(() => engine.ProcessQuicCryptoData(QuicEncryptionLevel.Handshake, badEe));
        Assert.Equal(TlsAlertDescription.UnsupportedExtension, alert.Description);
    }

    [Fact]
    public void Tls13Alps_WithoutAlpn_ThrowsIllegalParameter()
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole Test Root CA");
        using X509Certificate2 serverCert = CreateTestLeaf(leafKey, caCert, TestHost);

        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);

        var engine = new TlsHandshakeEngine(new TlsHandshakeOptions
        {
            ServerName = TestHost,
            Profile = ProfileRegistry.GetRequired("chrome_150"),
            SpecOverride = ChromeQuicSpecs.CreateClientHelloSpec(),
            VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
        });

        byte[] ch = engine.StartQuicHandshake(new byte[] { 0x01, 0x02 });
        ParsedClientHello parsedCh = SyntheticTls13Server.ParseClientHello(ch);
        X25519.GenerateKeyPair(out byte[] sPriv, out byte[] sPub);

        byte[] sh = SyntheticTls13Server.BuildServerHelloMessage(
            RandomNumberGenerator.GetBytes(32),
            parsedCh.SessionId,
            CipherSuiteId.TLS_AES_128_GCM_SHA256,
            new List<(ushort, byte[])>
            {
                (TlsExtensionType.SupportedVersions, new byte[] { 0x03, 0x04 }),
                (TlsExtensionType.KeyShare, SyntheticTls13Server.BuildServerKeyShare(NamedGroupId.X25519, sPub)),
            });

        engine.ProcessQuicCryptoData(QuicEncryptionLevel.Initial, sh);
        byte[] eeWithoutAlpn = SyntheticTls13Server.BuildEncryptedExtensions(
            alpn: null,
            quicTp: new byte[] { 0x0A, 0x0B },
            alpsCodepoint: TlsExtensionType.ApplicationSettingsNew,
            alpsData: Array.Empty<byte>());

        TlsAlertException ex = Assert.Throws<TlsAlertException>(() =>
            engine.ProcessQuicCryptoData(QuicEncryptionLevel.Handshake, eeWithoutAlpn));
        Assert.Equal(TlsAlertDescription.IllegalParameter, ex.Description);
    }

    // ---- Test Helpers & Compliant Synthetic TLS 1.3 Server ----

    private static (TlsHandshakeEngine Engine, byte[] PeerTransportParams) CompleteSyntheticQuicHandshake(
        ECDsa leafKey,
        byte[] leafDer,
        byte[] caDer,
        RootCertificateDatabase roots)
    {
        var clientTp = new byte[] { 0x01, 0x02, 0x03 };
        var serverTp = new byte[] { 0x0A, 0x0B, 0x0C, 0x0D };

        var engine = new TlsHandshakeEngine(new TlsHandshakeOptions
        {
            ServerName = TestHost,
            Profile = ProfileRegistry.GetRequired("chrome_150"),
            SpecOverride = ChromeQuicSpecs.CreateClientHelloSpec(),
            VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
        });

        byte[] ch = engine.StartQuicHandshake(clientTp);
        ParsedClientHello parsedCh = SyntheticTls13Server.ParseClientHello(ch);
        byte[] clientXPub = parsedCh.KeyShares[NamedGroupId.X25519];
        X25519.GenerateKeyPair(out byte[] sPriv, out byte[] sPub);
        byte[] sharedSecret = X25519.ScalarMult(sPriv, clientXPub);

        byte[] sh = SyntheticTls13Server.BuildServerHelloMessage(
            RandomNumberGenerator.GetBytes(32),
            parsedCh.SessionId,
            CipherSuiteId.TLS_AES_128_GCM_SHA256,
            new List<(ushort, byte[])>
            {
                (TlsExtensionType.SupportedVersions, new byte[] { 0x03, 0x04 }),
                (TlsExtensionType.KeyShare, SyntheticTls13Server.BuildServerKeyShare(NamedGroupId.X25519, sPub)),
            });

        QuicHandshakeStepResult shRes = engine.ProcessQuicCryptoData(QuicEncryptionLevel.Initial, sh);
        Assert.NotNull(shRes.HandshakeReadKeys);

        var transcript = new MemoryStream();
        transcript.Write(ch);
        transcript.Write(sh);

        byte[] ee = SyntheticTls13Server.BuildEncryptedExtensions("h3", serverTp);
        transcript.Write(ee);

        byte[] certMsg = SyntheticTls13Server.BuildCertificateMessage(new[] { leafDer, caDer });
        transcript.Write(certMsg);

        byte[] cvMsg = SyntheticTls13Server.BuildCertificateVerifyMessage(leafKey, HashPrimitives.Sha256(transcript.ToArray()));
        transcript.Write(cvMsg);

        byte[] zeros32 = new byte[32];
        byte[] earlySecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, ReadOnlySpan<byte>.Empty, zeros32);
        byte[] emptyHash = HashPrimitives.Sha256(ReadOnlySpan<byte>.Empty);
        byte[] derived = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, earlySecret, "derived", emptyHash, 32);
        byte[] hsSecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, derived, sharedSecret);
        byte[] shHash = HashPrimitives.Sha256(ch.Concat(sh).ToArray());
        byte[] sHsSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, hsSecret, "s hs traffic", shHash, 32);
        byte[] sFinKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, sHsSecret, "finished", ReadOnlySpan<byte>.Empty, 32);
        byte[] finVerify = HashPrimitives.Hmac(HashAlgorithmKind.Sha256, sFinKey, HashPrimitives.Sha256(transcript.ToArray()));
        byte[] finMsg = SyntheticTls13Server.WrapHandshakeMessage(0x14, finVerify);

        byte[] flight = ee.Concat(certMsg).Concat(cvMsg).Concat(finMsg).ToArray();
        QuicHandshakeStepResult finalRes = engine.ProcessQuicCryptoData(QuicEncryptionLevel.Handshake, flight);
        Assert.True(finalRes.HandshakeCompleted);
        Assert.Equal("h3", finalRes.NegotiatedAlpn);
        Assert.Equal(serverTp, finalRes.PeerTransportParameters);
        return (engine, finalRes.PeerTransportParameters!);
    }

    private static X509Certificate2 CreateTestCa(AsymmetricAlgorithm key, string subject)
    {
        CertificateRequest req = key switch
        {
            ECDsa ecdsa => new CertificateRequest(subject, ecdsa, HashAlgorithmName.SHA256),
            RSA rsa => new CertificateRequest(subject, rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1),
            _ => throw new NotSupportedException(),
        };
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(true, false, 0, true));
        req.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.KeyCertSign | X509KeyUsageFlags.DigitalSignature | X509KeyUsageFlags.CrlSign, true));
        req.CertificateExtensions.Add(new X509SubjectKeyIdentifierExtension(req.PublicKey, false));
        DateTimeOffset now = DateTimeOffset.UtcNow;
        return req.CreateSelfSigned(now.AddDays(-1), now.AddDays(30));
    }

    private static X509Certificate2 CreateTestLeaf(AsymmetricAlgorithm leafKey, X509Certificate2 caCert, string dnsName)
    {
        CertificateRequest req = leafKey switch
        {
            ECDsa ecdsa => new CertificateRequest($"CN={dnsName}", ecdsa, HashAlgorithmName.SHA256),
            RSA rsa => new CertificateRequest($"CN={dnsName}", rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1),
            _ => throw new NotSupportedException(),
        };
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
        using X509Certificate2 withKey = leafKey switch
        {
            ECDsa e => rawLeaf.CopyWithPrivateKey(e),
            RSA r => rawLeaf.CopyWithPrivateKey(r),
            _ => throw new NotSupportedException(),
        };
        byte[] pfx = withKey.Export(X509ContentType.Pfx);
        return new X509Certificate2(pfx, (string?)null, X509KeyStorageFlags.Exportable);
    }

    private static byte[] CreatePatternPayload(int length)
    {
        var data = new byte[length];
        for (int i = 0; i < data.Length; i++)
            data[i] = (byte)((i * 31 + 17) & 0xFF);
        return data;
    }

    private static byte[] PrependUInt16Len(byte[] data)
    {
        var buf = new byte[2 + data.Length];
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(0, 2), (ushort)data.Length);
        data.CopyTo(buf, 2);
        return buf;
    }

    private static byte[] CompressWith(CertCompressionAlgorithm alg, byte[] raw)
    {
        using var dst = new MemoryStream();
        switch (alg)
        {
            case CertCompressionAlgorithm.Zlib:
                using (var z = new ZLibStream(dst, CompressionLevel.Optimal, leaveOpen: true))
                    z.Write(raw, 0, raw.Length);
                return dst.ToArray();

            case CertCompressionAlgorithm.Brotli:
                using (var br = new BrotliStream(dst, CompressionLevel.Optimal, leaveOpen: true))
                    br.Write(raw, 0, raw.Length);
                return dst.ToArray();

            case CertCompressionAlgorithm.Zstd:
                using (var zstd = new ZstdSharp.Compressor())
                    return zstd.Wrap(raw).ToArray();

            default:
                throw new NotSupportedException();
        }
    }

    private static async Task ReadExactlyAsync(Stream stream, byte[] buffer, CancellationToken ct)
    {
        int offset = 0;
        while (offset < buffer.Length)
        {
            int n = await stream.ReadAsync(buffer.AsMemory(offset, buffer.Length - offset), ct);
            if (n == 0)
                throw new EndOfStreamException($"Stream ended after {offset}/{buffer.Length} bytes.");
            offset += n;
        }
    }

    private sealed record ParsedClientHello(
        byte[] Random,
        byte[] SessionId,
        List<ushort> CipherSuites,
        List<ushort> ExtensionOrder,
        Dictionary<ushort, byte[]> Extensions,
        Dictionary<ushort, byte[]> KeyShares);

    private sealed class SyntheticTls13Server
    {
        public static readonly byte[] HrrMagicRandom =
        {
            0xCF, 0x21, 0xAD, 0x74, 0xE5, 0x9A, 0x61, 0x11,
            0xBE, 0x1D, 0x8C, 0x02, 0x1E, 0x65, 0xB8, 0x91,
            0xC2, 0xA2, 0x11, 0x16, 0x7A, 0xBB, 0x8C, 0x5E,
            0x07, 0x9E, 0x09, 0xE2, 0xC8, 0xA8, 0x33, 0x9C,
        };

        private readonly Stream _stream;
        private readonly ECDsa _leafKey;
        private readonly byte[][] _derChain;
        private byte[] _sAppKey = Array.Empty<byte>();
        private byte[] _sAppIv = Array.Empty<byte>();
        private byte[] _sAppSecret = Array.Empty<byte>();
        private ulong _sWriteSeq;
        private byte[] _cAppKey = Array.Empty<byte>();
        private byte[] _cAppIv = Array.Empty<byte>();
        private byte[] _cAppSecret = Array.Empty<byte>();
        private ulong _cReadSeq;

        public byte[]? ResumptionMasterSecret { get; private set; }

        public SyntheticTls13Server(Stream stream, ECDsa leafKey, byte[][] derChain)
        {
            _stream = stream;
            _leafKey = leafKey;
            _derChain = derChain;
        }

        public async Task AcceptFullHandshakeAsync(
            string? alpn = "h2",
            CertCompressionAlgorithm? certCompression = null,
            bool corruptCertVerify = false,
            CancellationToken ct = default,
            ushort? alpsCodepoint = null,
            byte[]? serverAlpsData = null)
        {
            byte[] ch1 = await ReadPlainHandshakeRecordAsync(ct);
            ParsedClientHello parsed = ParseClientHello(ch1);
            byte[] clientPub = parsed.KeyShares[NamedGroupId.X25519];
            X25519.GenerateKeyPair(out byte[] sPriv, out byte[] sPub);
            byte[] sharedSecret = X25519.ScalarMult(sPriv, clientPub);

            var transcript = new MemoryStream();
            transcript.Write(ch1);

            await CompleteHandshakeCoreAsync(
                transcript,
                parsed,
                NamedGroupId.X25519,
                sPub,
                sharedSecret,
                earlySecret: HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, ReadOnlySpan<byte>.Empty, new byte[32]),
                acceptedPskIdentity: null,
                alpn,
                certCompression,
                corruptCertVerify,
                ct,
                alpsCodepoint,
                serverAlpsData);
        }

        public async Task AcceptFullHandshakeWithHrrAsync(
            ushort hrrSelectedGroup,
            byte[] cookie,
            string? alpn = "h2",
            CancellationToken ct = default)
        {
            byte[] ch1 = await ReadPlainHandshakeRecordAsync(ct);
            ParsedClientHello parsed1 = ParseClientHello(ch1);

            byte[] ch1Hash = HashPrimitives.Sha256(ch1);
            var msgHash = new byte[4 + 32];
            msgHash[0] = 0xFE;
            msgHash[3] = 32;
            ch1Hash.CopyTo(msgHash, 4);

            byte[] hrr = BuildServerHelloMessage(
                HrrMagicRandom,
                parsed1.SessionId,
                CipherSuiteId.TLS_AES_128_GCM_SHA256,
                new List<(ushort, byte[])>
                {
                    (TlsExtensionType.SupportedVersions, new byte[] { 0x03, 0x04 }),
                    (TlsExtensionType.KeyShare, new byte[] { (byte)(hrrSelectedGroup >> 8), (byte)hrrSelectedGroup }),
                    (0x002C, PrependUInt16Len(cookie)),
                });

            await WritePlainRecordAsync(TlsContentType.Handshake, hrr, 0x0303, ct);

            byte[] ch2 = await ReadPlainHandshakeRecordAsync(ct);
            ParsedClientHello parsed2 = ParseClientHello(ch2);
            Assert.Equal(parsed1.Random, parsed2.Random);
            Assert.Equal(parsed1.SessionId, parsed2.SessionId);
            Assert.Equal(PrependUInt16Len(cookie), parsed2.Extensions[0x002C]);
            Assert.Single(parsed2.KeyShares);
            Assert.True(parsed2.KeyShares.ContainsKey(hrrSelectedGroup));

            (byte[] sPriv, byte[] sPub) = EcPrimitives.GenerateEcdheKeyPair(EcCurveKind.P256);
            byte[] sharedSecret = EcPrimitives.DeriveEcdheSharedSecret(EcCurveKind.P256, sPriv, parsed2.KeyShares[hrrSelectedGroup]);

            var transcript = new MemoryStream();
            transcript.Write(msgHash);
            transcript.Write(hrr);
            transcript.Write(ch2);

            await CompleteHandshakeCoreAsync(
                transcript,
                parsed2,
                hrrSelectedGroup,
                sPub,
                sharedSecret,
                earlySecret: HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, ReadOnlySpan<byte>.Empty, new byte[32]),
                acceptedPskIdentity: null,
                alpn,
                certCompression: null,
                corruptCertVerify: false,
                ct);
        }

        public async Task<bool> AcceptResumedPskHandshakeAsync(
            byte[] expectedTicket,
            byte[] psk,
            string? alpn,
            CancellationToken ct)
        {
            byte[] ch = await ReadPlainHandshakeRecordAsync(ct);
            ParsedClientHello parsed = ParseClientHello(ch);
            Assert.Equal(TlsExtensionType.PreSharedKey, parsed.ExtensionOrder[^1]);

            byte[] pskExt = parsed.Extensions[TlsExtensionType.PreSharedKey];
            int idListLen = BinaryPrimitives.ReadUInt16BigEndian(pskExt.AsSpan(0, 2));
            int idLen = BinaryPrimitives.ReadUInt16BigEndian(pskExt.AsSpan(2, 2));
            byte[] offeredTicket = pskExt.AsSpan(4, idLen).ToArray();
            Assert.Equal(expectedTicket, offeredTicket);

            int bindersOffset = 2 + idListLen;
            int bindersLen = BinaryPrimitives.ReadUInt16BigEndian(pskExt.AsSpan(bindersOffset, 2));
            byte binderLen = pskExt[bindersOffset + 2];
            byte[] offeredBinder = pskExt.AsSpan(bindersOffset + 3, binderLen).ToArray();

            byte[] earlySecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, ReadOnlySpan<byte>.Empty, psk);
            byte[] binderKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, earlySecret, "res binder", HashPrimitives.Sha256(ReadOnlySpan<byte>.Empty), 32);
            byte[] finKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, binderKey, "finished", ReadOnlySpan<byte>.Empty, 32);
            byte[] truncHash = HashPrimitives.Sha256(ch.AsSpan(0, ch.Length - (2 + 1 + 32)));
            byte[] expectedBinder = HashPrimitives.Hmac(HashAlgorithmKind.Sha256, finKey, truncHash);
            bool binderOk = ConstantTime.Equals(offeredBinder, expectedBinder);
            Assert.True(binderOk);

            byte[] clientPub = parsed.KeyShares[NamedGroupId.X25519];
            X25519.GenerateKeyPair(out byte[] sPriv, out byte[] sPub);
            byte[] sharedSecret = X25519.ScalarMult(sPriv, clientPub);

            var transcript = new MemoryStream();
            transcript.Write(ch);

            await CompleteHandshakeCoreAsync(
                transcript,
                parsed,
                NamedGroupId.X25519,
                sPub,
                sharedSecret,
                earlySecret,
                acceptedPskIdentity: 0,
                alpn,
                certCompression: null,
                corruptCertVerify: false,
                ct);

            return binderOk;
        }

        public async Task SendCompressedCertificateWithDeclaredSizeAsync(
            CertCompressionAlgorithm alg,
            int declaredUncompressedSize,
            byte[] compressedPayload,
            CancellationToken ct)
        {
            byte[] ch1 = await ReadPlainHandshakeRecordAsync(ct);
            ParsedClientHello parsed = ParseClientHello(ch1);
            byte[] clientPub = parsed.KeyShares[NamedGroupId.X25519];
            X25519.GenerateKeyPair(out byte[] sPriv, out byte[] sPub);
            byte[] sharedSecret = X25519.ScalarMult(sPriv, clientPub);

            byte[] sh = BuildServerHelloMessage(
                RandomNumberGenerator.GetBytes(32),
                parsed.SessionId,
                CipherSuiteId.TLS_AES_128_GCM_SHA256,
                new List<(ushort, byte[])>
                {
                    (TlsExtensionType.SupportedVersions, new byte[] { 0x03, 0x04 }),
                    (TlsExtensionType.KeyShare, BuildServerKeyShare(NamedGroupId.X25519, sPub)),
                });
            await WritePlainRecordAsync(TlsContentType.Handshake, sh, 0x0303, ct);

            byte[] earlySecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, ReadOnlySpan<byte>.Empty, new byte[32]);
            byte[] derived = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, earlySecret, "derived", HashPrimitives.Sha256(ReadOnlySpan<byte>.Empty), 32);
            byte[] hsSecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, derived, sharedSecret);
            byte[] shHash = HashPrimitives.Sha256(ch1.Concat(sh).ToArray());
            byte[] sHsSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, hsSecret, "s hs traffic", shHash, 32);
            byte[] sHsKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, sHsSecret, "key", ReadOnlySpan<byte>.Empty, 16);
            byte[] sHsIv = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, sHsSecret, "iv", ReadOnlySpan<byte>.Empty, 12);

            ulong seq = 0;
            byte[] ee = BuildEncryptedExtensions(null, null);
            await WriteTls13RecordAsync(sHsKey, sHsIv, seq++, TlsContentType.Handshake, ee, ct);

            byte[] badCompCert = BuildCompressedCertificateMessage(alg, declaredUncompressedSize, compressedPayload);
            await WriteTls13RecordAsync(sHsKey, sHsIv, seq++, TlsContentType.Handshake, badCompCert, ct);
        }

        private async Task CompleteHandshakeCoreAsync(
            MemoryStream transcript,
            ParsedClientHello parsed,
            ushort selectedGroup,
            byte[] serverKeySharePub,
            byte[] sharedSecret,
            byte[] earlySecret,
            ushort? acceptedPskIdentity,
            string? alpn,
            CertCompressionAlgorithm? certCompression,
            bool corruptCertVerify,
            CancellationToken ct,
            ushort? alpsCodepoint = null,
            byte[]? serverAlpsData = null)
        {
            var shExts = new List<(ushort, byte[])>
            {
                (TlsExtensionType.SupportedVersions, new byte[] { 0x03, 0x04 }),
                (TlsExtensionType.KeyShare, BuildServerKeyShare(selectedGroup, serverKeySharePub)),
            };
            if (acceptedPskIdentity is { } pskId)
            {
                var idBuf = new byte[2];
                BinaryPrimitives.WriteUInt16BigEndian(idBuf, pskId);
                shExts.Add((TlsExtensionType.PreSharedKey, idBuf));
            }

            byte[] sh = BuildServerHelloMessage(RandomNumberGenerator.GetBytes(32), parsed.SessionId, CipherSuiteId.TLS_AES_128_GCM_SHA256, shExts);
            transcript.Write(sh);
            await WritePlainRecordAsync(TlsContentType.Handshake, sh, 0x0303, ct);

            byte[] derived = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, earlySecret, "derived", HashPrimitives.Sha256(ReadOnlySpan<byte>.Empty), 32);
            byte[] hsSecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, derived, sharedSecret);
            byte[] shHash = HashPrimitives.Sha256(transcript.ToArray());

            byte[] cHsSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, hsSecret, "c hs traffic", shHash, 32);
            byte[] sHsSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, hsSecret, "s hs traffic", shHash, 32);
            byte[] cHsKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, cHsSecret, "key", ReadOnlySpan<byte>.Empty, 16);
            byte[] cHsIv = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, cHsSecret, "iv", ReadOnlySpan<byte>.Empty, 12);
            byte[] sHsKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, sHsSecret, "key", ReadOnlySpan<byte>.Empty, 16);
            byte[] sHsIv = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, sHsSecret, "iv", ReadOnlySpan<byte>.Empty, 12);

            ulong sHsSeq = 0;
            byte[] ee = BuildEncryptedExtensions(alpn, null, alpsCodepoint, serverAlpsData);
            transcript.Write(ee);
            await WriteTls13RecordAsync(sHsKey, sHsIv, sHsSeq++, TlsContentType.Handshake, ee, ct);

            if (acceptedPskIdentity is null)
            {
                byte[] rawCertMsg = BuildCertificateMessage(_derChain);
                byte[] wireCertMsg;
                if (certCompression is { } alg)
                {
                    byte[] rawBody = rawCertMsg.AsSpan(4).ToArray();
                    byte[] compressed = CompressWith(alg, rawBody);
                    wireCertMsg = BuildCompressedCertificateMessage(alg, rawBody.Length, compressed);
                }
                else
                {
                    wireCertMsg = rawCertMsg;
                }

                transcript.Write(wireCertMsg);
                await WriteTls13RecordAsync(sHsKey, sHsIv, sHsSeq++, TlsContentType.Handshake, wireCertMsg, ct);

                byte[] cv = BuildCertificateVerifyMessage(_leafKey, HashPrimitives.Sha256(transcript.ToArray()), corruptCertVerify);
                transcript.Write(cv);
                await WriteTls13RecordAsync(sHsKey, sHsIv, sHsSeq++, TlsContentType.Handshake, cv, ct);
            }

            byte[] sFinKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, sHsSecret, "finished", ReadOnlySpan<byte>.Empty, 32);
            byte[] sFinVerify = HashPrimitives.Hmac(HashAlgorithmKind.Sha256, sFinKey, HashPrimitives.Sha256(transcript.ToArray()));
            byte[] sFin = WrapHandshakeMessage(0x14, sFinVerify);
            transcript.Write(sFin);
            await WriteTls13RecordAsync(sHsKey, sHsIv, sHsSeq++, TlsContentType.Handshake, sFin, ct);

            byte[] serverFinHash = HashPrimitives.Sha256(transcript.ToArray());
            byte[] dMaster = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, hsSecret, "derived", HashPrimitives.Sha256(ReadOnlySpan<byte>.Empty), 32);
            byte[] masterSecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, dMaster, new byte[32]);

            _cAppSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, masterSecret, "c ap traffic", serverFinHash, 32);
            _sAppSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, masterSecret, "s ap traffic", serverFinHash, 32);
            _cAppKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, _cAppSecret, "key", ReadOnlySpan<byte>.Empty, 16);
            _cAppIv = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, _cAppSecret, "iv", ReadOnlySpan<byte>.Empty, 12);
            _sAppKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, _sAppSecret, "key", ReadOnlySpan<byte>.Empty, 16);
            _sAppIv = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, _sAppSecret, "iv", ReadOnlySpan<byte>.Empty, 12);
            _sWriteSeq = 0;
            _cReadSeq = 0;

            ulong cHsSeq = 0;
            (TlsContentType cType, byte[] cFlight) = await ReadTls13RecordAsync(cHsKey, cHsIv, cHsSeq++, ct);
            Assert.Equal(TlsContentType.Handshake, cType);
            int cOff = 0;
            if (alpsCodepoint is { } expectedAlps)
            {
                Assert.True(cFlight.Length >= 10, $"Expected 10-byte client EncryptedExtensions for ALPS 0x{expectedAlps:X4}, got {cFlight.Length} bytes");
                byte[] clientEe = cFlight.AsSpan(0, 10).ToArray();
                Assert.Equal(new byte[]
                {
                    0x08, 0x00, 0x00, 0x06,
                    0x00, 0x04,
                    (byte)(expectedAlps >> 8), (byte)expectedAlps,
                    0x00, 0x00,
                }, clientEe);
                transcript.Write(clientEe);
                cOff = 10;
                if (cOff == cFlight.Length)
                {
                    (cType, cFlight) = await ReadTls13RecordAsync(cHsKey, cHsIv, cHsSeq++, ct);
                    Assert.Equal(TlsContentType.Handshake, cType);
                    cOff = 0;
                }
            }
            byte[] cFinMsg = cOff == 0 ? cFlight : cFlight.AsSpan(cOff).ToArray();
            Assert.Equal(0x14, cFinMsg[0]);

            byte[] cFinKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, cHsSecret, "finished", ReadOnlySpan<byte>.Empty, 32);
            byte[] expectedCFin = HashPrimitives.Hmac(HashAlgorithmKind.Sha256, cFinKey, HashPrimitives.Sha256(transcript.ToArray()));
            Assert.Equal(expectedCFin, cFinMsg.AsSpan(4).ToArray());

            transcript.Write(cFinMsg);
            ResumptionMasterSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, masterSecret, "res master", HashPrimitives.Sha256(transcript.ToArray()), 32);
        }

        public Task SendNewSessionTicketAsync(
            uint lifetime,
            uint ageAdd,
            byte[] nonce,
            byte[] ticket,
            uint maxEarlyDataSize,
            CancellationToken ct)
        {
            byte[] bodyBytes = BuildNewSessionTicketBody(lifetime, ageAdd, nonce, ticket, maxEarlyDataSize);
            byte[] msg = WrapHandshakeMessage(0x04, bodyBytes);
            return WriteTls13RecordAsync(_sAppKey, _sAppIv, _sWriteSeq++, TlsContentType.Handshake, msg, ct);
        }

        private static byte[] BuildNewSessionTicketBody(
            uint lifetime,
            uint ageAdd,
            byte[] nonce,
            byte[] ticket,
            uint maxEarlyDataSize)
        {
            using var body = new MemoryStream();
            Span<byte> u32 = stackalloc byte[4];
            BinaryPrimitives.WriteUInt32BigEndian(u32, lifetime);
            body.Write(u32);
            BinaryPrimitives.WriteUInt32BigEndian(u32, ageAdd);
            body.Write(u32);
            body.WriteByte((byte)nonce.Length);
            body.Write(nonce);
            Span<byte> u16 = stackalloc byte[2];
            BinaryPrimitives.WriteUInt16BigEndian(u16, (ushort)ticket.Length);
            body.Write(u16);
            body.Write(ticket);

            if (maxEarlyDataSize > 0)
            {
                BinaryPrimitives.WriteUInt16BigEndian(u16, 8);
                body.Write(u16);
                BinaryPrimitives.WriteUInt16BigEndian(u16, TlsExtensionType.EarlyData);
                body.Write(u16);
                BinaryPrimitives.WriteUInt16BigEndian(u16, 4);
                body.Write(u16);
                BinaryPrimitives.WriteUInt32BigEndian(u32, maxEarlyDataSize);
                body.Write(u32);
            }
            else
            {
                BinaryPrimitives.WriteUInt16BigEndian(u16, 0);
                body.Write(u16);
            }

            return body.ToArray();
        }

        public async Task SendKeyUpdateAndRotateWriteKeyAsync(bool updateRequested, CancellationToken ct)
        {
            byte[] ku = { 0x18, 0x00, 0x00, 0x01, updateRequested ? (byte)1 : (byte)0 };
            await WriteTls13RecordAsync(_sAppKey, _sAppIv, _sWriteSeq++, TlsContentType.Handshake, ku, ct);

            _sAppSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, _sAppSecret, "traffic upd", ReadOnlySpan<byte>.Empty, 32);
            _sAppKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, _sAppSecret, "key", ReadOnlySpan<byte>.Empty, 16);
            _sAppIv = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, _sAppSecret, "iv", ReadOnlySpan<byte>.Empty, 12);
            _sWriteSeq = 0;
        }

        public async Task ExpectClientKeyUpdateAndRotateReadKeyAsync(CancellationToken ct)
        {
            (TlsContentType t, byte[] payload) = await ReadTls13RecordAsync(_cAppKey, _cAppIv, _cReadSeq++, ct);
            Assert.Equal(TlsContentType.Handshake, t);
            Assert.Equal(new byte[] { 0x18, 0x00, 0x00, 0x01, 0x00 }, payload);

            _cAppSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, _cAppSecret, "traffic upd", ReadOnlySpan<byte>.Empty, 32);
            _cAppKey = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, _cAppSecret, "key", ReadOnlySpan<byte>.Empty, 16);
            _cAppIv = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, _cAppSecret, "iv", ReadOnlySpan<byte>.Empty, 12);
            _cReadSeq = 0;
        }

        public Task SendAppDataAsync(byte[] data, CancellationToken ct) =>
            WriteTls13RecordAsync(_sAppKey, _sAppIv, _sWriteSeq++, TlsContentType.ApplicationData, data, ct);

        public Task SendCloseNotifyAsync(CancellationToken ct) =>
            WriteTls13RecordAsync(_sAppKey, _sAppIv, _sWriteSeq++, TlsContentType.Alert, new byte[] { 0x01, 0x00 }, ct);

        public async Task<byte[]> ReadAppDataAsync(CancellationToken ct)
        {
            while (true)
            {
                (TlsContentType t, byte[] data) = await ReadTls13RecordAsync(_cAppKey, _cAppIv, _cReadSeq++, ct);
                if (t == TlsContentType.ApplicationData)
                    return data;
            }
        }

        private async Task<byte[]> ReadPlainHandshakeRecordAsync(CancellationToken ct)
        {
            var hdr = new byte[5];
            await ReadExactlyAsync(_stream, hdr, ct);
            Assert.Equal((byte)TlsContentType.Handshake, hdr[0]);
            int len = BinaryPrimitives.ReadUInt16BigEndian(hdr.AsSpan(3, 2));
            var payload = new byte[len];
            await ReadExactlyAsync(_stream, payload, ct);
            return payload;
        }

        private async Task WritePlainRecordAsync(TlsContentType type, byte[] payload, ushort ver, CancellationToken ct)
        {
            var rec = new byte[5 + payload.Length];
            rec[0] = (byte)type;
            BinaryPrimitives.WriteUInt16BigEndian(rec.AsSpan(1, 2), ver);
            BinaryPrimitives.WriteUInt16BigEndian(rec.AsSpan(3, 2), (ushort)payload.Length);
            payload.CopyTo(rec, 5);
            await _stream.WriteAsync(rec, ct);
            await _stream.FlushAsync(ct);
        }

        private async Task WriteTls13RecordAsync(byte[] key, byte[] iv, ulong seq, TlsContentType innerType, byte[] pt, CancellationToken ct)
        {
            byte[] rec = EncryptTls13Record(key, iv, seq, innerType, pt);
            await _stream.WriteAsync(rec, ct);
            await _stream.FlushAsync(ct);
        }

        private static byte[] EncryptTls13Record(byte[] key, byte[] iv, ulong seq, TlsContentType innerType, byte[] pt)
        {
            byte[] inner = new byte[pt.Length + 1];
            pt.CopyTo(inner, 0);
            inner[pt.Length] = (byte)innerType;

            int encLen = inner.Length + 16;
            var rec = new byte[5 + encLen];
            rec[0] = 0x17;
            rec[1] = 0x03;
            rec[2] = 0x03;
            BinaryPrimitives.WriteUInt16BigEndian(rec.AsSpan(3, 2), (ushort)encLen);

            Span<byte> nonce = stackalloc byte[12];
            iv.CopyTo(nonce);
            Span<byte> seqBe = stackalloc byte[8];
            BinaryPrimitives.WriteUInt64BigEndian(seqBe, seq);
            for (int i = 0; i < 8; i++)
                nonce[4 + i] ^= seqBe[i];

            AesPrimitives.AesGcmEncrypt(key, nonce, inner, rec.AsSpan(0, 5), rec.AsSpan(5, inner.Length), rec.AsSpan(5 + inner.Length, 16));
            return rec;
        }

        private async Task<(TlsContentType InnerType, byte[] Payload)> ReadTls13RecordAsync(byte[] key, byte[] iv, ulong seq, CancellationToken ct)
        {
            while (true)
            {
                var hdr = new byte[5];
                await ReadExactlyAsync(_stream, hdr, ct);
                int len = BinaryPrimitives.ReadUInt16BigEndian(hdr.AsSpan(3, 2));
                var payload = new byte[len];
                await ReadExactlyAsync(_stream, payload, ct);

                if (hdr[0] == (byte)TlsContentType.ChangeCipherSpec)
                    continue;

                return DecryptTls13Record(key, iv, seq, hdr, payload);
            }
        }

        private static (TlsContentType InnerType, byte[] Payload) DecryptTls13Record(byte[] key, byte[] iv, ulong seq, byte[] hdr, byte[] payload)
        {
            Span<byte> nonce = stackalloc byte[12];
            iv.CopyTo(nonce);
            Span<byte> seqBe = stackalloc byte[8];
            BinaryPrimitives.WriteUInt64BigEndian(seqBe, seq);
            for (int i = 0; i < 8; i++)
                nonce[4 + i] ^= seqBe[i];

            var pt = new byte[payload.Length - 16];
            bool ok = AesPrimitives.AesGcmDecrypt(key, nonce, payload.AsSpan(0, payload.Length - 16), hdr, payload.AsSpan(payload.Length - 16, 16), pt);
            Assert.True(ok);

            int idx = pt.Length - 1;
            while (idx >= 0 && pt[idx] == 0) idx--;
            return ((TlsContentType)pt[idx], pt.AsSpan(0, idx).ToArray());
        }

        public static ParsedClientHello ParseClientHello(ReadOnlySpan<byte> ch)
        {
            Assert.Equal(0x01, ch[0]);
            int bodyLen = (ch[1] << 16) | (ch[2] << 8) | ch[3];
            Assert.Equal(ch.Length - 4, bodyLen);

            int off = 4;
            ushort legacyVer = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(off, 2));
            Assert.Equal(TlsVersion.Tls12, legacyVer);
            off += 2;

            byte[] random = ch.Slice(off, 32).ToArray();
            off += 32;

            byte sidLen = ch[off++];
            byte[] sid = ch.Slice(off, sidLen).ToArray();
            off += sidLen;

            ushort cipherLen = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(off, 2));
            off += 2;
            var ciphers = new List<ushort>();
            for (int i = 0; i < cipherLen; i += 2)
                ciphers.Add(BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(off + i, 2)));
            off += cipherLen;

            byte compLen = ch[off++];
            off += compLen;

            ushort extTotalLen = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(off, 2));
            off += 2;
            Assert.Equal(ch.Length, off + extTotalLen);

            var extOrder = new List<ushort>();
            var exts = new Dictionary<ushort, byte[]>();
            var keyShares = new Dictionary<ushort, byte[]>();

            int end = off + extTotalLen;
            while (off < end)
            {
                ushort type = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(off, 2));
                ushort len = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(off + 2, 2));
                off += 4;
                byte[] data = ch.Slice(off, len).ToArray();
                extOrder.Add(type);
                exts[type] = data;
                if (type == TlsExtensionType.KeyShare)
                {
                    int ksLen = BinaryPrimitives.ReadUInt16BigEndian(data.AsSpan(0, 2));
                    int kOff = 2;
                    while (kOff < 2 + ksLen)
                    {
                        ushort grp = BinaryPrimitives.ReadUInt16BigEndian(data.AsSpan(kOff, 2));
                        ushort kLen = BinaryPrimitives.ReadUInt16BigEndian(data.AsSpan(kOff + 2, 2));
                        keyShares[grp] = data.AsSpan(kOff + 4, kLen).ToArray();
                        kOff += 4 + kLen;
                    }
                }
                off += len;
            }

            return new ParsedClientHello(random, sid, ciphers, extOrder, exts, keyShares);
        }

        public static byte[] BuildServerHelloMessage(byte[] random, byte[] sessionId, ushort cipherSuite, List<(ushort Type, byte[] Data)> extensions)
        {
            using var extMs = new MemoryStream();
            Span<byte> u16 = stackalloc byte[2];
            foreach ((ushort t, byte[] d) in extensions)
            {
                BinaryPrimitives.WriteUInt16BigEndian(u16, t);
                extMs.Write(u16);
                BinaryPrimitives.WriteUInt16BigEndian(u16, (ushort)d.Length);
                extMs.Write(u16);
                extMs.Write(d);
            }
            byte[] extBytes = extMs.ToArray();

            using var body = new MemoryStream();
            BinaryPrimitives.WriteUInt16BigEndian(u16, TlsVersion.Tls12);
            body.Write(u16);
            body.Write(random);
            body.WriteByte((byte)sessionId.Length);
            body.Write(sessionId);
            BinaryPrimitives.WriteUInt16BigEndian(u16, cipherSuite);
            body.Write(u16);
            body.WriteByte(0x00);
            BinaryPrimitives.WriteUInt16BigEndian(u16, (ushort)extBytes.Length);
            body.Write(u16);
            body.Write(extBytes);
            return WrapHandshakeMessage(0x02, body.ToArray());
        }

        public static byte[] BuildServerKeyShare(ushort group, byte[] pub)
        {
            var buf = new byte[4 + pub.Length];
            BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(0, 2), group);
            BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(2, 2), (ushort)pub.Length);
            pub.CopyTo(buf, 4);
            return buf;
        }

        public static byte[] BuildEncryptedExtensions(string? alpn, byte[]? quicTp, ushort? alpsCodepoint = null, byte[]? alpsData = null)
        {
            using var extMs = new MemoryStream();
            Span<byte> u16 = stackalloc byte[2];
            if (!string.IsNullOrEmpty(alpn))
            {
                byte[] pBytes = Encoding.ASCII.GetBytes(alpn);
                BinaryPrimitives.WriteUInt16BigEndian(u16, TlsExtensionType.ApplicationLayerProtocolNegotiation);
                extMs.Write(u16);
                BinaryPrimitives.WriteUInt16BigEndian(u16, (ushort)(3 + pBytes.Length));
                extMs.Write(u16);
                BinaryPrimitives.WriteUInt16BigEndian(u16, (ushort)(1 + pBytes.Length));
                extMs.Write(u16);
                extMs.WriteByte((byte)pBytes.Length);
                extMs.Write(pBytes);
            }
            if (quicTp is not null)
            {
                BinaryPrimitives.WriteUInt16BigEndian(u16, TlsExtensionType.QuicTransportParameters);
                extMs.Write(u16);
                BinaryPrimitives.WriteUInt16BigEndian(u16, (ushort)quicTp.Length);
                extMs.Write(u16);
                extMs.Write(quicTp);
            }
            if (alpsCodepoint is { } alpsCp)
            {
                byte[] payload = alpsData ?? Array.Empty<byte>();
                BinaryPrimitives.WriteUInt16BigEndian(u16, alpsCp);
                extMs.Write(u16);
                BinaryPrimitives.WriteUInt16BigEndian(u16, (ushort)payload.Length);
                extMs.Write(u16);
                extMs.Write(payload);
            }
            byte[] extBytes = extMs.ToArray();
            var body = new byte[2 + extBytes.Length];
            BinaryPrimitives.WriteUInt16BigEndian(body.AsSpan(0, 2), (ushort)extBytes.Length);
            extBytes.CopyTo(body, 2);
            return WrapHandshakeMessage(0x08, body);
        }

        public static byte[] BuildCertificateMessage(byte[][] derChain)
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
            var body = new byte[1 + 3 + listBytes.Length];
            body[0] = 0x00;
            body[1] = (byte)(listBytes.Length >> 16);
            body[2] = (byte)(listBytes.Length >> 8);
            body[3] = (byte)listBytes.Length;
            listBytes.CopyTo(body, 4);
            return WrapHandshakeMessage(0x0B, body);
        }

        public static byte[] BuildCompressedCertificateMessage(CertCompressionAlgorithm alg, int uncompressedLength, byte[] compressedBytes)
        {
            var body = new byte[8 + compressedBytes.Length];
            BinaryPrimitives.WriteUInt16BigEndian(body.AsSpan(0, 2), (ushort)alg);
            body[2] = (byte)(uncompressedLength >> 16);
            body[3] = (byte)(uncompressedLength >> 8);
            body[4] = (byte)uncompressedLength;
            body[5] = (byte)(compressedBytes.Length >> 16);
            body[6] = (byte)(compressedBytes.Length >> 8);
            body[7] = (byte)compressedBytes.Length;
            compressedBytes.CopyTo(body, 8);
            return WrapHandshakeMessage(0x19, body);
        }

        public static byte[] BuildCertificateVerifyMessage(ECDsa leafKey, byte[] transcriptHash, bool corrupt = false)
        {
            ReadOnlySpan<byte> prefix = "TLS 1.3, server CertificateVerify"u8;
            var signedContent = new byte[64 + prefix.Length + 1 + transcriptHash.Length];
            signedContent.AsSpan(0, 64).Fill(0x20);
            prefix.CopyTo(signedContent.AsSpan(64));
            signedContent[64 + prefix.Length] = 0x00;
            transcriptHash.CopyTo(signedContent.AsSpan(64 + prefix.Length + 1));

            byte[] sig = leafKey.SignData(signedContent, HashAlgorithmName.SHA256, DSASignatureFormat.Rfc3279DerSequence);
            if (corrupt)
                sig[^1] ^= 0xFF;

            var body = new byte[4 + sig.Length];
            BinaryPrimitives.WriteUInt16BigEndian(body.AsSpan(0, 2), SignatureSchemeId.EcdsaSecp256r1Sha256);
            BinaryPrimitives.WriteUInt16BigEndian(body.AsSpan(2, 2), (ushort)sig.Length);
            sig.CopyTo(body, 4);
            return WrapHandshakeMessage(0x0F, body);
        }

        public static byte[] WrapHandshakeMessage(byte msgType, ReadOnlySpan<byte> body)
        {
            var msg = new byte[4 + body.Length];
            msg[0] = msgType;
            msg[1] = (byte)(body.Length >> 16);
            msg[2] = (byte)(body.Length >> 8);
            msg[3] = (byte)body.Length;
            body.CopyTo(msg.AsSpan(4));
            return msg;
        }
    }
}
