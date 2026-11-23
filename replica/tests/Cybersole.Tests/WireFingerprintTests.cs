using System.Buffers.Binary;
using System.Collections.Concurrent;
using System.Net;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using Cybersole.Http.Crypto;
using Cybersole.Http.Http3;
using Cybersole.Http.Profiles;
using Cybersole.Http.Protocol;
using Cybersole.Http.Quic;
using Cybersole.Http.Tls;
using Cybersole.Http.X509;
using Xunit;

namespace Cybersole.Tests;

public sealed class WireFingerprintTests
{
    [Fact]
    public void WireFingerprint_MatchesObservedBrowserleaksCurlVectorExactly()
    {
        // Exact curl/8.13.0 ClientHello fields observed on live https://tls.browserleaks.com/json
        ushort[] ciphers =
        {
            0xC02C, 0xC02B, 0xC030, 0xC02F, 0x009F, 0x009E, 0xC024, 0xC023,
            0xC028, 0xC027, 0xC00A, 0xC009, 0xC014, 0xC013, 0x009D, 0x009C,
            0x003D, 0x003C, 0x0035, 0x002F, 0x000A,
        };
        ushort[] sigAlgs =
        {
            0x0804, 0x0805, 0x0806, 0x0401, 0x0501, 0x0201,
            0x0403, 0x0503, 0x0203, 0x0202, 0x0601, 0x0603,
        };
        ushort[] groups = { 29, 23, 24 };

        var exts = new List<(ushort Type, byte[] Data)>
        {
            (0x0000, EncodeSni("tls.browserleaks.com")),
            (0x0005, new byte[] { 0x01, 0x00, 0x00, 0x00, 0x00 }),
            (0x000A, EncodeU16List(groups)),
            (0x000B, new byte[] { 0x01, 0x00 }),
            (0x000D, EncodeU16List(sigAlgs)),
            (0x0023, Array.Empty<byte>()),
            (0x0010, EncodeAlpn("http/1.1")),
            (0x0017, Array.Empty<byte>()),
            (0xFF01, new byte[] { 0x00 }),
        };

        byte[] ch = BuildSyntheticClientHello(0x0303, ciphers, exts);
        TlsWireFingerprintResult fp = WireFingerprint.AnalyzeClientHello(ch, isQuic: false);

        Assert.Equal("t12d2109h1_76e208dd3e22_7af1ed941c26", fp.Ja4);
        Assert.Equal("t12d2109h1_000a,002f,0035,003c,003d,009c,009d,009e,009f,c009,c00a,c013,c014,c023,c024,c027,c028,c02b,c02c,c02f,c030_0005,000a,000b,000d,0017,0023,ff01_0804,0805,0806,0401,0501,0201,0403,0503,0203,0202,0601,0603", fp.Ja4Raw);
        Assert.Equal("t12d2109h1_93eee3d26c42_5da3d607c71a", fp.Ja4Original);
        Assert.Equal("t12d2109h1_c02c,c02b,c030,c02f,009f,009e,c024,c023,c028,c027,c00a,c009,c014,c013,009d,009c,003d,003c,0035,002f,000a_0000,0005,000a,000b,000d,0023,0010,0017,ff01_0804,0805,0806,0401,0501,0201,0403,0503,0203,0202,0601,0603", fp.Ja4RawOriginal);
        Assert.Equal("771,49196-49195-49200-49199-159-158-49188-49187-49192-49191-49162-49161-49172-49171-157-156-61-60-53-47-10,0-5-10-11-13-35-16-23-65281,29-23-24,0", fp.Ja3Text);
        Assert.Equal("bd0bf25947d4a37404f0424edf4db9ad", fp.Ja3Hash);
        Assert.Equal("771,49196-49195-49200-49199-159-158-49188-49187-49192-49191-49162-49161-49172-49171-157-156-61-60-53-47-10,0-5-10-11-13-16-23-35-65281,29-23-24,0", fp.Ja3nText);
        Assert.Equal("6dc58b02765223a5015e36b7f7ad469c", fp.Ja3nHash);
    }

    [Theory]
    [InlineData("chrome_150", "h2", "1:65536;2:0;4:6291456;6:262144|15663105|0|m,a,s,p", true)]
    [InlineData("chrome_152", "h2", "1:65536;2:0;4:6291456;6:262144|15663105|0|m,a,s,p", true)]
    [InlineData("chrome_133", "h3", "1:65536;2:0;4:6291456;6:262144|15663105|0|m,a,s,p", true)]
    [InlineData("firefox_148", "h2", "1:65536;2:0;4:131072;5:16384|12517377|0|m,p,a,s", false)]
    [InlineData("safari_ios_18_0", "h2", "2:0;3:100;4:2097152;8:1;9:1|10420225|0|m,s,a,p", true)]
    public void BuiltInProfiles_ProduceDeterministicSortedJa4AndExactAkamaiH2(
        string profileName,
        string expectedAlpn,
        string expectedAkamaiH2,
        bool expectGrease)
    {
        ClientProfile profile = ProfileRegistry.GetRequired(profileName);

        using ClientHelloBuildResult r1 = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
        {
            Profile = profile,
            ServerName = "example.com",
            Random = new Random(101),
        });
        using ClientHelloBuildResult r2 = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
        {
            Profile = profile,
            ServerName = "example.com",
            Random = new Random(202),
        });

        TlsWireFingerprintResult fp1 = WireFingerprint.AnalyzeClientHello(r1.HandshakeMessage, isQuic: false);
        TlsWireFingerprintResult fp2 = WireFingerprint.AnalyzeClientHello(r2.HandshakeMessage, isQuic: false);

        Assert.Equal(expectedAlpn, fp1.AlpnProtocols[0]);
        Assert.Equal("example.com", fp1.ServerName);
        Assert.Equal(0x0304, fp1.EffectiveVersion);
        Assert.Equal(fp1.Ja4, fp2.Ja4);
        Assert.Equal(fp1.Ja4Raw, fp2.Ja4Raw);
        Assert.Equal(expectGrease, fp1.CipherSuites.Any(GreaseHelper.IsGrease));
        Assert.DoesNotContain(fp1.SupportedGroups, GreaseHelper.IsGrease);

        Http2WireFingerprintResult h2 = WireFingerprint.AnalyzeHttp2Spec(profile.Http2Settings);
        Assert.Equal(expectedAkamaiH2, h2.AkamaiText);
    }

    [Fact]
    public void QuicInitialWireFingerprint_VerifiesZeroByteScidChaosFramesAndTransportParams()
    {
        ClientProfile chrome150 = ProfileRegistry.GetRequired("chrome_150_PSK");
        byte[] localScid = Array.Empty<byte>();
        byte[] dcid = Convert.FromHexString("1020304050607080");

        QuicTransportParameters tp = QuicTransportParametersCodec.FromSpec(
            chrome150.QuicSpec!,
            localScid,
            initialRttUs: 25_000,
            random: new Random(42));
        byte[] tpBytes = QuicTransportParametersCodec.Encode(tp, shuffle: true, random: new Random(42));

        using ClientHelloBuildResult chBuilt = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
        {
            Profile = chrome150,
            ServerName = "cloudflare-quic.com",
            IsQuicMode = true,
            QuicTransportParameters = tpBytes,
            Random = new Random(42),
        });
        byte[] chMsg = chBuilt.HandshakeMessage;

        // Manually build one 1200+ byte Initial datagram carrying ClientHello slices + PING + PADDING
        List<List<QuicFrame>> lists = ChaosFrames.PackInitialFrameLists(
            chMsg,
            minPlaintextBytes: 1200,
            maxPlaintextBytes: 2200,
            enableChaos: true,
            includePing: true,
            fragmentCountOverride: 4,
            random: new Random(7));
        Assert.Single(lists);
        byte[] plaintext = QuicFrameCodec.Encode(lists[0]);

        QuicKeySet writeKeys = QuicCrypto.DeriveInitialKeys(dcid, isServer: false);
        byte[] datagram = QuicPacketCodec.BuildLongHeaderPacket(
            QuicLongPacketType.Initial, dcid, localScid, ReadOnlySpan<byte>.Empty, 0UL, 1, plaintext, writeKeys);

        QuicInitialWireFingerprintResult parsed = WireFingerprint.AnalyzeQuicClientInitial(datagram);
        Assert.Equal(QuicCrypto.QuicVersion1, parsed.Version);
        Assert.True(parsed.DatagramLength >= 1200);
        Assert.Equal(dcid, parsed.Dcid);
        Assert.Empty(parsed.Scid);
        Assert.True(parsed.HasPingFrame);
        Assert.Equal(4, parsed.CryptoFrameCount);
        Assert.Equal("q13d", parsed.ClientHelloFingerprint.Ja4[..4]);
        Assert.EndsWith("h3", parsed.ClientHelloFingerprint.Ja4.Split('_')[0]);
        Assert.Equal("cloudflare-quic.com", parsed.ClientHelloFingerprint.ServerName);
        Assert.NotNull(parsed.TransportParameters);
        Assert.Empty(parsed.TransportParameters!.InitialSourceConnectionId!);
        Assert.Equal(25_000UL, parsed.TransportParameters.GoogleInitialRttUs);
    }

    [Fact]
    public async Task QuicConnection_ZeroByteScid_And_OutOfOrderEarlyOneRttPacket_CompleteCleanly()
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=ZeroSCID Root");
        using X509Certificate2 leafCert = CreateTestLeaf(leafKey, caCert, "localhost");

        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);

        var bus = new EarlyOneRttTransportPair();
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        var server = new EarlyOneRttServer(bus.ServerSide, leafKey, new[] { leafCert.RawData });
        Task serverTask = Task.Run(() => server.RunAsync(cts.Token));

        ClientProfile chrome150 = ProfileRegistry.GetRequired("chrome_150");
        Assert.Equal(0, chrome150.QuicSpec!.ScidLength);

        await using var quic = await QuicConnection.ConnectAsync(new QuicConnectionOptions
        {
            Host = "localhost",
            Port = 443,
            Profile = chrome150,
            VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
            TransportOverride = bus.ClientSide,
            ConnectTimeout = TimeSpan.FromSeconds(5),
        }, cts.Token);

        Assert.Empty(quic.LocalScid);
        Assert.True(server.ObservedZeroLengthClientScid);
        Assert.False(server.ObservedUserAgentInH3Request);

        await using var h3 = new Http3Connection(quic, ConnectionKey.Create("https", "localhost", 443, chrome150.Name), chrome150);
        await h3.StartAsync(cts.Token);

        PureHttpResponse resp = await h3.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri("https://localhost/ping"),
        }, cts.Token);

        Assert.Equal(200, resp.StatusCode);
        Assert.Equal("HTTP/3", resp.HttpVersion);
        Assert.Equal("pong-zero-scid", Encoding.UTF8.GetString(resp.Body));
        Assert.False(server.ObservedUserAgentInH3Request);

        cts.Cancel();
        try { await serverTask; } catch (OperationCanceledException) { }
    }

    [Fact]
    public async Task Chrome133_NegotiatesH2CleanlyOverTcpWhenServerSelectsH2()
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Chrome133 Test CA");
        using X509Certificate2 leafCert = CreateTestLeaf(leafKey, caCert, "localhost");

        using var listener = new System.Net.Sockets.TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        int port = ((IPEndPoint)listener.LocalEndpoint).Port;
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(10));

        string? serverSelectedAlpn = null;
        Task serverTask = Task.Run(async () =>
        {
            using var client = await listener.AcceptTcpClientAsync(cts.Token);
            using var ssl = new System.Net.Security.SslStream(client.GetStream(), leaveInnerStreamOpen: false);
            await ssl.AuthenticateAsServerAsync(new System.Net.Security.SslServerAuthenticationOptions
            {
                ServerCertificate = leafCert,
                EnabledSslProtocols = System.Security.Authentication.SslProtocols.Tls12 | System.Security.Authentication.SslProtocols.Tls13,
                ApplicationProtocols = new List<System.Net.Security.SslApplicationProtocol>
                {
                    System.Net.Security.SslApplicationProtocol.Http2,
                    System.Net.Security.SslApplicationProtocol.Http11,
                },
            }, cts.Token);
            serverSelectedAlpn = Encoding.ASCII.GetString(ssl.NegotiatedApplicationProtocol.Protocol.Span);
        }, cts.Token);

        using var tcp = new System.Net.Sockets.TcpClient();
        await tcp.ConnectAsync(IPAddress.Loopback, port, cts.Token);
        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);
        await using var tls = new TlsStream(tcp.GetStream(), new TlsConnectionOptions
        {
            ServerName = "localhost",
            Port = port,
            Profile = ProfileRegistry.GetRequired("chrome_133"),
            VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
        });
        await tls.HandshakeAsync(cts.Token);
        await serverTask;

        Assert.Equal("h2", serverSelectedAlpn);
        Assert.Equal("h2", tls.NegotiatedAlpn);
    }

    private sealed class EarlyOneRttTransportPair
    {
        private readonly System.Threading.Channels.Channel<byte[]> _c2s = System.Threading.Channels.Channel.CreateUnbounded<byte[]>();
        private readonly System.Threading.Channels.Channel<byte[]> _s2c = System.Threading.Channels.Channel.CreateUnbounded<byte[]>();

        public EarlyOneRttTransportPair()
        {
            ClientSide = new ChannelEndpoint(_c2s.Writer, _s2c.Reader);
            ServerSide = new ChannelEndpoint(_s2c.Writer, _c2s.Reader);
        }

        public IQuicDatagramTransport ClientSide { get; }
        public IQuicDatagramTransport ServerSide { get; }

        private sealed class ChannelEndpoint : IQuicDatagramTransport
        {
            private readonly System.Threading.Channels.ChannelWriter<byte[]> _tx;
            private readonly System.Threading.Channels.ChannelReader<byte[]> _rx;

            public EndPoint? RemoteEndPoint => new IPEndPoint(IPAddress.Loopback, 443);

            public ChannelEndpoint(System.Threading.Channels.ChannelWriter<byte[]> tx, System.Threading.Channels.ChannelReader<byte[]> rx)
            {
                _tx = tx;
                _rx = rx;
            }

            public ValueTask SendDatagramAsync(ReadOnlyMemory<byte> datagram, CancellationToken ct)
            {
                _tx.TryWrite(datagram.ToArray());
                return ValueTask.CompletedTask;
            }

            public async ValueTask<int> ReceiveDatagramAsync(Memory<byte> buffer, CancellationToken ct)
            {
                if (!await _rx.WaitToReadAsync(ct))
                    return 0;
                if (!_rx.TryRead(out byte[]? pkt))
                    return 0;
                pkt.CopyTo(buffer.Span);
                return pkt.Length;
            }

            public ValueTask DisposeAsync() => ValueTask.CompletedTask;
        }
    }

    private sealed class EarlyOneRttServer
    {
        private readonly IQuicDatagramTransport _transport;
        private readonly ECDsa _leafKey;
        private readonly byte[][] _derChain;
        private readonly byte[] _serverScid = RandomNumberGenerator.GetBytes(8);
        private QuicKeySet? _initRead;
        private QuicKeySet? _initWrite;
        private QuicKeySet? _hsRead;
        private QuicKeySet? _hsWrite;
        private QuicKeySet? _appRead;
        private QuicKeySet? _appWrite;
        private readonly MemoryStream _initCrypto = new();
        private readonly SortedDictionary<ulong, byte[]> _initSegs = new();
        private ulong _initReadOff;
        private readonly MemoryStream _hsCrypto = new();
        private readonly MemoryStream _transcript = new();
        private ulong _pnInit, _pnHs, _pnApp;
        private ulong _srvCtrlOff;
        private bool _replied;
        private bool _hsDoneSent;
        private bool _sentEarlyAppSettingsBeforeClientFinished;

        public EarlyOneRttServer(IQuicDatagramTransport transport, ECDsa leafKey, byte[][] derChain)
        {
            _transport = transport;
            _leafKey = leafKey;
            _derChain = derChain;
        }

        public bool ObservedZeroLengthClientScid { get; private set; }
        public bool ObservedUserAgentInH3Request { get; private set; }

        public async Task RunAsync(CancellationToken ct)
        {
            var buf = new byte[66_048];
            while (!ct.IsCancellationRequested)
            {
                int n = await _transport.ReceiveDatagramAsync(buf, ct);
                if (n == 0)
                    break;
                Process(buf.AsSpan(0, n), ct);
            }
        }

        private void Process(ReadOnlySpan<byte> datagram, CancellationToken ct)
        {
            int offset = 0;
            while (offset < datagram.Length)
            {
                ReadOnlySpan<byte> span = datagram.Slice(offset);
                byte first = span[0];
                if ((first & 0x80) != 0)
                {
                    int off = 5;
                    byte dcidLen = span[off++];
                    byte[] dcid = span.Slice(off, dcidLen).ToArray();
                    off += dcidLen;
                    byte scidLen = span[off++];
                    byte[] scid = span.Slice(off, scidLen).ToArray();
                    off += scidLen;

                    var type = (QuicLongPacketType)((first >> 4) & 0x03);
                    if (type == QuicLongPacketType.Initial)
                    {
                        ObservedZeroLengthClientScid = scid.Length == 0;
                        QuicVarInt.TryRead(span, ref off, out ulong tLen);
                        off += (int)tLen;
                        QuicVarInt.TryRead(span, ref off, out ulong pktLen);
                        int pnOff = off;
                        int total = pnOff + (int)pktLen;

                        _initRead ??= QuicCrypto.DeriveInitialKeys(dcid, isServer: false);
                        _initWrite ??= QuicCrypto.DeriveInitialKeys(dcid, isServer: true);
                        byte[] copy = span.Slice(0, total).ToArray();
                        if (_initRead.TryRemoveHeaderProtection(copy, pnOff, out int pnLen, out _))
                        {
                            ulong pn = QuicPacketCodec.ReadTruncatedPacketNumber(copy.AsSpan(pnOff, pnLen), pnLen);
                            if (_initRead.TryPacketUnprotect(pn, copy.AsSpan(0, pnOff + pnLen), copy.AsSpan(pnOff + pnLen), out byte[] pt))
                            {
                                foreach (QuicFrame f in QuicFrameCodec.DecodeAll(pt))
                                {
                                    if (f is QuicCryptoFrame cf)
                                        _initSegs[cf.Offset] = cf.Data;
                                }
                                while (_initSegs.Count > 0)
                                {
                                    ulong k = _initSegs.Keys.First();
                                    if (k > _initReadOff) break;
                                    byte[] d = _initSegs[k];
                                    _initSegs.Remove(k);
                                    _initCrypto.Write(d);
                                    _initReadOff += (ulong)d.Length;
                                }
                                TryReplyHandshake(dcid, scid, pn, ct);
                            }
                        }
                        offset += total;
                        continue;
                    }
                    if (type == QuicLongPacketType.Handshake)
                    {
                        QuicVarInt.TryRead(span, ref off, out ulong pktLen);
                        int pnOff = off;
                        int total = pnOff + (int)pktLen;
                        byte[] copy = span.Slice(0, total).ToArray();
                        if (_hsRead is not null && _hsRead.TryRemoveHeaderProtection(copy, pnOff, out int pnLen, out _))
                        {
                            ulong pn = QuicPacketCodec.ReadTruncatedPacketNumber(copy.AsSpan(pnOff, pnLen), pnLen);
                            if (_hsRead.TryPacketUnprotect(pn, copy.AsSpan(0, pnOff + pnLen), copy.AsSpan(pnOff + pnLen), out byte[] pt))
                            {
                                foreach (QuicFrame f in QuicFrameCodec.DecodeAll(pt))
                                    if (f is QuicCryptoFrame cf) _hsCrypto.Write(cf.Data);
                                if (!_hsDoneSent && _hsCrypto.Length >= 4)
                                {
                                    _hsDoneSent = true;
                                    byte[] done = QuicFrameCodec.Encode(new QuicFrame[] { QuicHandshakeDoneFrame.Instance });
                                    _ = _transport.SendDatagramAsync(
                                        QuicPacketCodec.BuildShortHeaderPacket(ReadOnlySpan<byte>.Empty, _pnApp++, 1, false, done, _appWrite!),
                                        ct);
                                }
                            }
                        }
                        offset += total;
                        continue;
                    }
                    return;
                }
                else
                {
                    if (_appRead is null)
                        return;
                    int pnOff = 1 + _serverScid.Length;
                    byte[] copy = span.ToArray();
                    if (_appRead.TryRemoveHeaderProtection(copy, pnOff, out int pnLen, out _))
                    {
                        ulong pn = QuicPacketCodec.ReadTruncatedPacketNumber(copy.AsSpan(pnOff, pnLen), pnLen);
                        if (_appRead.TryPacketUnprotect(pn, copy.AsSpan(0, pnOff + pnLen), copy.AsSpan(pnOff + pnLen), out byte[] pt))
                        {
                            foreach (QuicFrame f in QuicFrameCodec.DecodeAll(pt))
                            {
                                if (f is QuicStreamFrame sf && (sf.StreamId & 0x02) == 0 && sf.Fin)
                                {
                                    int rOff = 0;
                                    while (rOff < sf.Data.Length)
                                    {
                                        QuicVarInt.TryRead(sf.Data, ref rOff, out ulong ft);
                                        QuicVarInt.TryRead(sf.Data, ref rOff, out ulong fl);
                                        byte[] pl = sf.Data.AsSpan(rOff, (int)fl).ToArray();
                                        rOff += (int)fl;
                                        if (ft == Http3FrameType.Headers)
                                        {
                                            List<PureHttpHeader> hdrs = new QpackDecoder().DecodeFieldSection(pl, out _);
                                            if (hdrs.Any(h => h.Name.Equals("user-agent", StringComparison.OrdinalIgnoreCase)))
                                                ObservedUserAgentInH3Request = true;
                                        }
                                    }

                                    var enc = new QpackEncoder();
                                    byte[] h = enc.Encode(new PureHttpHeader[] { new(":status", "200") });
                                    byte[] body = Encoding.UTF8.GetBytes("pong-zero-scid");
                                    byte[] resp = Http3FrameCodec.BuildFrame(Http3FrameType.Headers, h)
                                        .Concat(Http3FrameCodec.BuildFrame(Http3FrameType.Data, body)).ToArray();
                                    byte[] ptResp = QuicFrameCodec.Encode(new QuicFrame[] { new QuicStreamFrame(sf.StreamId, 0, resp, Fin: true) });
                                    _ = _transport.SendDatagramAsync(
                                        QuicPacketCodec.BuildShortHeaderPacket(ReadOnlySpan<byte>.Empty, _pnApp++, 1, false, ptResp, _appWrite!),
                                        ct);
                                }
                            }
                        }
                    }
                    return;
                }
            }
        }

        private void TryReplyHandshake(byte[] origDcid, byte[] clientScid, ulong clientPn, CancellationToken ct)
        {
            if (_replied || _initCrypto.Length < 4)
                return;
            byte[] allCh = _initCrypto.ToArray();
            int len = (allCh[1] << 16) | (allCh[2] << 8) | allCh[3];
            if (allCh.Length < 4 + len)
                return;
            _replied = true;

            byte[] chMsg = allCh.AsSpan(0, 4 + len).ToArray();
            TlsWireFingerprintResult chParsed = WireFingerprint.AnalyzeClientHello(chMsg, isQuic: true);
            byte[] clientXPub = ExtractX25519KeyShare(chMsg);
            byte[] sid = ExtractSessionId(chMsg);

            X25519.GenerateKeyPair(out byte[] sPriv, out byte[] sPub);
            byte[] shared = X25519.ScalarMult(sPriv, clientXPub);
            byte[] sh = BuildServerHello(RandomNumberGenerator.GetBytes(32), sid, CipherSuiteId.TLS_AES_128_GCM_SHA256, sPub);

            _transcript.Write(chMsg);
            _transcript.Write(sh);

            byte[] zeros = new byte[32];
            byte[] early = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, ReadOnlySpan<byte>.Empty, zeros);
            byte[] emptyH = HashPrimitives.Sha256(ReadOnlySpan<byte>.Empty);
            byte[] derived = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, early, "derived", emptyH, 32);
            byte[] hsSec = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, derived, shared);
            byte[] shHash = HashPrimitives.Sha256(_transcript.ToArray());

            byte[] cHs = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, hsSec, "c hs traffic", shHash, 32);
            byte[] sHs = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, hsSec, "s hs traffic", shHash, 32);
            _hsRead = QuicCrypto.DerivePacketKeys(CipherSuiteId.TLS_AES_128_GCM_SHA256, cHs);
            _hsWrite = QuicCrypto.DerivePacketKeys(CipherSuiteId.TLS_AES_128_GCM_SHA256, sHs);

            byte[] tpBytes = QuicTransportParametersCodec.Encode(new QuicTransportParameters
            {
                OriginalDestinationConnectionId = origDcid,
                InitialSourceConnectionId = _serverScid,
                InitialMaxData = 4_194_304,
                InitialMaxStreamDataBidiLocal = 1_048_576,
                InitialMaxStreamDataBidiRemote = 1_048_576,
                InitialMaxStreamDataUni = 1_048_576,
                InitialMaxStreamsBidi = 100,
                InitialMaxStreamsUni = 100,
            });
            byte[] ee = BuildEe(tpBytes);
            _transcript.Write(ee);
            byte[] cert = BuildCert(_derChain);
            _transcript.Write(cert);
            byte[] cv = BuildCv(_leafKey, HashPrimitives.Sha256(_transcript.ToArray()));
            _transcript.Write(cv);
            byte[] sFinK = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, sHs, "finished", ReadOnlySpan<byte>.Empty, 32);
            byte[] sFin = Wrap(0x14, HashPrimitives.Hmac(HashAlgorithmKind.Sha256, sFinK, HashPrimitives.Sha256(_transcript.ToArray())));
            _transcript.Write(sFin);

            byte[] finH = HashPrimitives.Sha256(_transcript.ToArray());
            byte[] dM = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, hsSec, "derived", emptyH, 32);
            byte[] mSec = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, dM, zeros);
            _appRead = QuicCrypto.DerivePacketKeys(CipherSuiteId.TLS_AES_128_GCM_SHA256, HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, mSec, "c ap traffic", finH, 32));
            _appWrite = QuicCrypto.DerivePacketKeys(CipherSuiteId.TLS_AES_128_GCM_SHA256, HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, mSec, "s ap traffic", finH, 32));

            // Intentionally send a 1-RTT HTTP/3 SETTINGS stream packet out-of-order BEFORE the Handshake packet finishes!
            if (!_sentEarlyAppSettingsBeforeClientFinished)
            {
                _sentEarlyAppSettingsBeforeClientFinished = true;
                byte[] sFrame = Http3FrameCodec.BuildFrame(Http3FrameType.Settings, Http3FrameCodec.BuildSettingsPayload(Array.Empty<(ulong, ulong)>()));
                byte[] ctrlData = QuicVarInt.Encode(Http3StreamType.Control).Concat(sFrame).ToArray();
                _srvCtrlOff += (ulong)ctrlData.Length;
                byte[] early1Rtt = QuicPacketCodec.BuildShortHeaderPacket(
                    clientScid, _pnApp++, 1, false,
                    QuicFrameCodec.Encode(new QuicFrame[] { new QuicStreamFrame(3, 0, ctrlData, false) }),
                    _appWrite);
                _ = _transport.SendDatagramAsync(early1Rtt, ct);
            }

            // Now send Initial (ServerHello) packet first...
            byte[] initPkt = QuicPacketCodec.BuildLongHeaderPacket(
                QuicLongPacketType.Initial, clientScid, _serverScid, ReadOnlySpan<byte>.Empty, _pnInit++, 1,
                QuicFrameCodec.Encode(new QuicFrame[] { QuicAckFrame.FromPacketNumbers(new[] { clientPn }), new QuicCryptoFrame(0, sh) }),
                _initWrite!);
            _ = _transport.SendDatagramAsync(initPkt, ct);

            // Then send Handshake flight separately so RetryDeferredPackets runs after Initial AND after Handshake!
            byte[] flight = ee.Concat(cert).Concat(cv).Concat(sFin).ToArray();
            int pos = 0;
            while (pos < flight.Length)
            {
                int take = Math.Min(1000, flight.Length - pos);
                byte[] hsPkt = QuicPacketCodec.BuildLongHeaderPacket(
                    QuicLongPacketType.Handshake, clientScid, _serverScid, ReadOnlySpan<byte>.Empty, _pnHs++, 1,
                    QuicFrameCodec.Encode(new QuicFrame[] { new QuicCryptoFrame((ulong)pos, flight.AsSpan(pos, take).ToArray()) }),
                    _hsWrite);
                _ = _transport.SendDatagramAsync(hsPkt, ct);
                pos += take;
            }

            _ = chParsed;
        }

        private static byte[] ExtractSessionId(ReadOnlySpan<byte> ch)
        {
            int off = 4 + 2 + 32;
            byte len = ch[off++];
            return ch.Slice(off, len).ToArray();
        }

        private static byte[] ExtractX25519KeyShare(ReadOnlySpan<byte> ch)
        {
            int off = 4 + 2 + 32;
            off += 1 + ch[off];
            off += 2 + BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(off, 2));
            off += 1 + ch[off];
            ushort extTotal = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(off, 2));
            off += 2;
            int end = off + extTotal;
            while (off < end)
            {
                ushort t = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(off, 2));
                ushort l = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(off + 2, 2));
                off += 4;
                if (t == TlsExtensionType.KeyShare)
                {
                    int kOff = off + 2;
                    while (kOff < off + l)
                    {
                        ushort g = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(kOff, 2));
                        ushort kl = BinaryPrimitives.ReadUInt16BigEndian(ch.Slice(kOff + 2, 2));
                        if (g == NamedGroupId.X25519)
                            return ch.Slice(kOff + 4, kl).ToArray();
                        kOff += 4 + kl;
                    }
                }
                off += l;
            }
            throw new InvalidOperationException("Missing X25519 share.");
        }

        private static byte[] BuildServerHello(byte[] rnd, byte[] sid, ushort cipher, byte[] pub)
        {
            var ks = new byte[4 + pub.Length];
            BinaryPrimitives.WriteUInt16BigEndian(ks.AsSpan(0, 2), NamedGroupId.X25519);
            BinaryPrimitives.WriteUInt16BigEndian(ks.AsSpan(2, 2), (ushort)pub.Length);
            pub.CopyTo(ks, 4);

            using var exts = new MemoryStream();
            WExt(exts, TlsExtensionType.SupportedVersions, new byte[] { 0x03, 0x04 });
            WExt(exts, TlsExtensionType.KeyShare, ks);
            byte[] eb = exts.ToArray();
            using var body = new MemoryStream();
            body.Write(new byte[] { 0x03, 0x03 });
            body.Write(rnd);
            body.WriteByte((byte)sid.Length);
            body.Write(sid);
            Span<byte> u16 = stackalloc byte[2];
            BinaryPrimitives.WriteUInt16BigEndian(u16, cipher);
            body.Write(u16);
            body.WriteByte(0x00);
            BinaryPrimitives.WriteUInt16BigEndian(u16, (ushort)eb.Length);
            body.Write(u16);
            body.Write(eb);
            return Wrap(0x02, body.ToArray());
        }

        private static byte[] BuildEe(byte[] tp)
        {
            using var exts = new MemoryStream();
            WExt(exts, TlsExtensionType.ApplicationLayerProtocolNegotiation, new byte[] { 0x00, 0x03, 0x02, (byte)'h', (byte)'3' });
            WExt(exts, TlsExtensionType.QuicTransportParameters, tp);
            byte[] eb = exts.ToArray();
            var b = new byte[2 + eb.Length];
            BinaryPrimitives.WriteUInt16BigEndian(b, (ushort)eb.Length);
            eb.CopyTo(b, 2);
            return Wrap(0x08, b);
        }

        private static byte[] BuildCert(byte[][] chain)
        {
            using var ms = new MemoryStream();
            foreach (byte[] d in chain)
            {
                ms.WriteByte((byte)(d.Length >> 16));
                ms.WriteByte((byte)(d.Length >> 8));
                ms.WriteByte((byte)d.Length);
                ms.Write(d);
                ms.Write(new byte[2]);
            }
            byte[] lb = ms.ToArray();
            var b = new byte[4 + lb.Length];
            b[1] = (byte)(lb.Length >> 16);
            b[2] = (byte)(lb.Length >> 8);
            b[3] = (byte)lb.Length;
            lb.CopyTo(b, 4);
            return Wrap(0x0B, b);
        }

        private static byte[] BuildCv(ECDsa key, byte[] hash)
        {
            ReadOnlySpan<byte> p = "TLS 1.3, server CertificateVerify"u8;
            var s = new byte[64 + p.Length + 1 + hash.Length];
            s.AsSpan(0, 64).Fill(0x20);
            p.CopyTo(s.AsSpan(64));
            hash.CopyTo(s.AsSpan(64 + p.Length + 1));
            byte[] sig = key.SignData(s, HashAlgorithmName.SHA256, DSASignatureFormat.Rfc3279DerSequence);
            var b = new byte[4 + sig.Length];
            BinaryPrimitives.WriteUInt16BigEndian(b.AsSpan(0, 2), SignatureSchemeId.EcdsaSecp256r1Sha256);
            BinaryPrimitives.WriteUInt16BigEndian(b.AsSpan(2, 2), (ushort)sig.Length);
            sig.CopyTo(b, 4);
            return Wrap(0x0F, b);
        }

        private static void WExt(MemoryStream ms, ushort t, byte[] d)
        {
            Span<byte> u = stackalloc byte[2];
            BinaryPrimitives.WriteUInt16BigEndian(u, t); ms.Write(u);
            BinaryPrimitives.WriteUInt16BigEndian(u, (ushort)d.Length); ms.Write(u);
            ms.Write(d);
        }

        private static byte[] Wrap(byte t, byte[] b)
        {
            var m = new byte[4 + b.Length];
            m[0] = t; m[1] = (byte)(b.Length >> 16); m[2] = (byte)(b.Length >> 8); m[3] = (byte)b.Length;
            b.CopyTo(m, 4);
            return m;
        }
    }

    private static byte[] EncodeSni(string host)
    {
        byte[] h = Encoding.ASCII.GetBytes(host);
        var buf = new byte[5 + h.Length];
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(0, 2), (ushort)(3 + h.Length));
        buf[2] = 0;
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(3, 2), (ushort)h.Length);
        h.CopyTo(buf, 5);
        return buf;
    }

    private static byte[] EncodeU16List(ushort[] values)
    {
        var buf = new byte[2 + values.Length * 2];
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(0, 2), (ushort)(values.Length * 2));
        for (int i = 0; i < values.Length; i++)
            BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(2 + i * 2, 2), values[i]);
        return buf;
    }

    private static byte[] EncodeAlpn(string proto)
    {
        byte[] p = Encoding.ASCII.GetBytes(proto);
        var buf = new byte[3 + p.Length];
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(0, 2), (ushort)(1 + p.Length));
        buf[2] = (byte)p.Length;
        p.CopyTo(buf, 3);
        return buf;
    }

    private static byte[] BuildSyntheticClientHello(ushort version, ushort[] ciphers, List<(ushort Type, byte[] Data)> exts)
    {
        using var extMs = new MemoryStream();
        Span<byte> u16 = stackalloc byte[2];
        foreach ((ushort t, byte[] d) in exts)
        {
            BinaryPrimitives.WriteUInt16BigEndian(u16, t); extMs.Write(u16);
            BinaryPrimitives.WriteUInt16BigEndian(u16, (ushort)d.Length); extMs.Write(u16);
            extMs.Write(d);
        }
        byte[] extBytes = extMs.ToArray();

        using var body = new MemoryStream();
        BinaryPrimitives.WriteUInt16BigEndian(u16, version); body.Write(u16);
        body.Write(new byte[32]);
        body.WriteByte(0);
        BinaryPrimitives.WriteUInt16BigEndian(u16, (ushort)(ciphers.Length * 2)); body.Write(u16);
        foreach (ushort c in ciphers)
        {
            BinaryPrimitives.WriteUInt16BigEndian(u16, c); body.Write(u16);
        }
        body.WriteByte(1); body.WriteByte(0);
        BinaryPrimitives.WriteUInt16BigEndian(u16, (ushort)extBytes.Length); body.Write(u16);
        body.Write(extBytes);

        byte[] bodyArr = body.ToArray();
        var msg = new byte[4 + bodyArr.Length];
        msg[0] = 0x01;
        msg[1] = (byte)(bodyArr.Length >> 16);
        msg[2] = (byte)(bodyArr.Length >> 8);
        msg[3] = (byte)bodyArr.Length;
        bodyArr.CopyTo(msg, 4);
        return msg;
    }

    private static X509Certificate2 CreateTestCa(AsymmetricAlgorithm key, string subject)
    {
        CertificateRequest req = new(subject, (ECDsa)key, HashAlgorithmName.SHA256);
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(true, false, 0, true));
        req.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.KeyCertSign | X509KeyUsageFlags.DigitalSignature, true));
        req.CertificateExtensions.Add(new X509SubjectKeyIdentifierExtension(req.PublicKey, false));
        DateTimeOffset now = DateTimeOffset.UtcNow;
        return req.CreateSelfSigned(now.AddDays(-1), now.AddDays(30));
    }

    private static X509Certificate2 CreateTestLeaf(AsymmetricAlgorithm leafKey, X509Certificate2 caCert, string dnsName)
    {
        CertificateRequest req = new($"CN={dnsName}", (ECDsa)leafKey, HashAlgorithmName.SHA256);
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, true));
        req.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.DigitalSignature, true));
        req.CertificateExtensions.Add(new X509EnhancedKeyUsageExtension(new OidCollection { new Oid("1.3.6.1.5.5.7.3.1") }, false));
        var san = new SubjectAlternativeNameBuilder();
        san.AddDnsName(dnsName);
        san.AddIpAddress(IPAddress.Loopback);
        req.CertificateExtensions.Add(san.Build());
        DateTimeOffset now = DateTimeOffset.UtcNow;
        byte[] serial = RandomNumberGenerator.GetBytes(16);
        serial[0] = (byte)((serial[0] & 0x7F) | 0x01);
        using X509Certificate2 raw = req.Create(caCert, now.AddHours(-1), now.AddDays(7), serial);
        using X509Certificate2 withKey = raw.CopyWithPrivateKey((ECDsa)leafKey);
        return new X509Certificate2(withKey.Export(X509ContentType.Pfx), (string?)null, X509KeyStorageFlags.Exportable);
    }
}
