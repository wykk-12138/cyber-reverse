using System.Buffers.Binary;
using System.Collections.Concurrent;
using System.IO.Compression;
using System.Net;
using System.Net.Sockets;
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

public sealed class QuicHttp3Tests
{
    private const string TestHost = "localhost";

    // ---- 1. RFC 9001 Appendix A Official Vectors & Key Schedule ----

    [Fact]
    public void Rfc9001AppendixA1InitialKeyDerivationMatchesOfficialVectors()
    {
        byte[] dcid = Convert.FromHexString("8394c8f03e515708");
        QuicCrypto.DeriveInitialSecrets(dcid, out byte[] initialSecret, out byte[] clientSecret, out byte[] serverSecret);

        Assert.Equal("7db5df06e7a69e432496adedb00851923595221596ae2ae9fb8115c1e9ed0a44", Convert.ToHexString(initialSecret).ToLowerInvariant());
        Assert.Equal("c00cf151ca5be075ed0ebfb5c80323c42d6b7db67881289af4008f1f6c357aea", Convert.ToHexString(clientSecret).ToLowerInvariant());
        Assert.Equal("3c199828fd139efd216c155ad844cc81fb82fa8d7446fa7d78be803acdda951b", Convert.ToHexString(serverSecret).ToLowerInvariant());

        QuicKeySet clientKeys = QuicCrypto.DeriveInitialKeys(dcid, isServer: false);
        Assert.Equal("1f369613dd76d5467730efcbe3b1a22d", Convert.ToHexString(clientKeys.Key).ToLowerInvariant());
        Assert.Equal("fa044b2f42a3fd3b46fb255c", Convert.ToHexString(clientKeys.Iv).ToLowerInvariant());
        Assert.Equal("9f50449e04a0e810283a1e9933adedd2", Convert.ToHexString(clientKeys.HpKey).ToLowerInvariant());

        QuicKeySet serverKeys = QuicCrypto.DeriveInitialKeys(dcid, isServer: true);
        Assert.Equal("cf3a5331653c364c88f0f379b6067e37", Convert.ToHexString(serverKeys.Key).ToLowerInvariant());
        Assert.Equal("0ac1493ca1905853b0bba03e", Convert.ToHexString(serverKeys.Iv).ToLowerInvariant());
        Assert.Equal("c206b8d9b9f0f37644430b490eeaa314", Convert.ToHexString(serverKeys.HpKey).ToLowerInvariant());
    }

    [Fact]
    public void Rfc9001AppendixA5ChaCha20ShortHeaderPacketMatchesOfficialVector()
    {
        byte[] secret = Convert.FromHexString("9ac312a7f877468ebe69422748ad00a15443f18203a07d6060f688f30f21632b");
        QuicKeySet keys = QuicCrypto.DerivePacketKeys(CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256, secret);

        Assert.Equal("c6d98ff3441c3fe1b2182094f69caa2ed4b716b65488960a7a984979fb23e1c8", Convert.ToHexString(keys.Key).ToLowerInvariant());
        Assert.Equal("e0459b3474bdd0e44a41c144", Convert.ToHexString(keys.Iv).ToLowerInvariant());
        Assert.Equal("25a282b9e82f06f21f488917a4fc8f1b73573685608597d0efcb076b0ab7a7a4", Convert.ToHexString(keys.HpKey).ToLowerInvariant());

        byte[] packet = QuicPacketCodec.BuildShortHeaderPacket(
            dcid: ReadOnlySpan<byte>.Empty,
            packetNumber: 654360564UL,
            pnLength: 3,
            keyPhase: false,
            plaintextFrames: new byte[] { 0x01 },
            writeKeys: keys);

        Assert.Equal("4cfe4189655e5cd55c41f69080575d7999c25a5bfb", Convert.ToHexString(packet).ToLowerInvariant());

        // Verify unprotect + key phase flip ("quic ku")
        Span<byte> rx = packet.ToArray();
        Assert.True(keys.TryRemoveHeaderProtection(rx, pnOffset: 1, out int pnLen, out bool keyPhase));
        Assert.Equal(3, pnLen);
        Assert.False(keyPhase);
        ulong truncPn = QuicPacketCodec.ReadTruncatedPacketNumber(rx.Slice(1, pnLen), pnLen);
        ulong decodedPn = QuicCrypto.DecodePacketNumber(654360560UL, truncPn, pnLen * 8);
        Assert.Equal(654360564UL, decodedPn);
        Assert.True(keys.TryPacketUnprotect(decodedPn, rx[..(1 + pnLen)], rx[(1 + pnLen)..], out byte[] pt));
        Assert.Equal(new byte[] { 0x01 }, pt);

        QuicKeySet nextGen = keys.UpdateKeys();
        Assert.NotEqual(keys.Key, nextGen.Key);
        Assert.NotEqual(keys.Iv, nextGen.Iv);
        byte[] gen1Pkt = QuicPacketCodec.BuildShortHeaderPacket(
            dcid: new byte[] { 1, 2, 3, 4 },
            packetNumber: 654360565UL,
            pnLength: 2,
            keyPhase: true,
            plaintextFrames: new byte[] { 0x01, 0x00 },
            writeKeys: nextGen);
        Span<byte> gen1Rx = gen1Pkt.ToArray();
        Assert.True(nextGen.TryRemoveHeaderProtection(gen1Rx, pnOffset: 5, out int pnLen2, out bool kp2));
        Assert.True(kp2);
        Assert.Equal(2, pnLen2);
        Assert.True(nextGen.TryPacketUnprotect(654360565UL, gen1Rx[..(5 + pnLen2)], gen1Rx[(5 + pnLen2)..], out byte[] pt2));
        Assert.Equal(new byte[] { 0x01, 0x00 }, pt2);
    }

    [Fact]
    public void Rfc9001AppendixA2ClientAndA3ServerInitialRoundtripAndA4RetryTagWork()
    {
        byte[] dcid = Convert.FromHexString("8394c8f03e515708");
        byte[] scid = Convert.FromHexString("f067a5502a4262b5");
        QuicKeySet clientKeys = QuicCrypto.DeriveInitialKeys(dcid, isServer: false);
        QuicKeySet serverKeys = QuicCrypto.DeriveInitialKeys(dcid, isServer: true);

        // Client Initial (1200 bytes, 4-byte PN = 2)
        byte[] clientFrames = ChaosFrames.BuildPaddedInitialPayload(new byte[241], minPlaintextBytes: 1162, enableChaos: false, includePing: false);
        byte[] clientInitial = QuicPacketCodec.BuildLongHeaderPacket(
            QuicLongPacketType.Initial, dcid, ReadOnlySpan<byte>.Empty, ReadOnlySpan<byte>.Empty, 2UL, 4, clientFrames, clientKeys);
        Assert.True(clientInitial.Length >= 1200);

        Span<byte> cRx = clientInitial.ToArray();
        int pnOffset = 5 + 1 + dcid.Length + 1 + 0 + 1 + 2; // flags+ver+dcidLen+dcid+scidLen+tokenLen(0)+lenVarint(2B)
        Assert.True(clientKeys.TryRemoveHeaderProtection(cRx, pnOffset, out int cPnLen, out _));
        Assert.Equal(4, cPnLen);
        ulong cPn = QuicCrypto.DecodePacketNumber(-1L, QuicPacketCodec.ReadTruncatedPacketNumber(cRx.Slice(pnOffset, cPnLen), cPnLen), 32);
        Assert.Equal(2UL, cPn);
        Assert.True(clientKeys.TryPacketUnprotect(cPn, cRx[..(pnOffset + cPnLen)], cRx[(pnOffset + cPnLen)..], out byte[] cPlain));
        Assert.Equal(clientFrames, cPlain);

        // Server Initial (2-byte PN = 1)
        byte[] srvFrames = QuicFrameCodec.Encode(new QuicFrame[]
        {
            QuicAckFrame.FromPacketNumbers(new[] { 2UL }),
            new QuicCryptoFrame(0, new byte[] { 0x02, 0x00, 0x00, 0x10 }),
        });
        byte[] srvInitial = QuicPacketCodec.BuildLongHeaderPacket(
            QuicLongPacketType.Initial, ReadOnlySpan<byte>.Empty, scid, ReadOnlySpan<byte>.Empty, 1UL, 2, srvFrames, serverKeys);
        Span<byte> sRx = srvInitial.ToArray();
        int sPnOffset = 5 + 1 + 0 + 1 + scid.Length + 1 + 1;
        Assert.True(serverKeys.TryRemoveHeaderProtection(sRx, sPnOffset, out int sPnLen, out _));
        Assert.Equal(2, sPnLen);
        ulong sPn = QuicCrypto.DecodePacketNumber(-1L, QuicPacketCodec.ReadTruncatedPacketNumber(sRx.Slice(sPnOffset, sPnLen), sPnLen), 16);
        Assert.Equal(1UL, sPn);
        Assert.True(serverKeys.TryPacketUnprotect(sPn, sRx[..(sPnOffset + sPnLen)], sRx[(sPnOffset + sPnLen)..], out byte[] sPlain));
        Assert.Equal(srvFrames, sPlain);

        // RFC 9001 Appendix A.4 official Retry packet
        byte[] officialRetry = Convert.FromHexString("ff000000010008f067a5502a4262b5746f6b656e04a265ba2eff4d829058fb3f0f2496ba");
        Assert.True(QuicCrypto.VerifyRetryIntegrityTag(dcid, officialRetry));

        byte[] builtRetry = QuicPacketCodec.BuildRetryPacket(dcid, ReadOnlySpan<byte>.Empty, scid, Encoding.ASCII.GetBytes("token"));
        Assert.Equal(officialRetry, builtRetry);

        byte[] tamperedRetry = officialRetry.ToArray();
        tamperedRetry[^1] ^= 0x01;
        Assert.False(QuicCrypto.VerifyRetryIntegrityTag(dcid, tamperedRetry));

        // RFC 9000 Appendix A.3 Packet Number Decoding
        Assert.Equal(0xa82f9b32UL, QuicCrypto.DecodePacketNumber(0xa82f30eaUL, 0x9b32UL, 16));
    }

    // ---- 2. VarInt, Transport Parameters, Frames & ChaosFrames ----

    [Fact]
    public void QuicVarIntAndNonMinimalEncodingRoundtrip()
    {
        ulong[] values = { 0, 37, 63, 64, 16_383, 16_384, 1_073_741_823, 1_073_741_824, QuicVarInt.MaxValue };
        foreach (ulong v in values)
        {
            byte[] enc = QuicVarInt.Encode(v);
            Assert.Equal(QuicVarInt.GetEncodedLength(v), enc.Length);
            Assert.True(QuicVarInt.TryDecode(enc, out ulong dec, out int read));
            Assert.Equal(v, dec);
            Assert.Equal(enc.Length, read);
        }

        // RFC 9000 §16 non-minimal 2-byte encoding of 37 (0x4025)
        var nonMinimal = new byte[2];
        Assert.Equal(2, QuicVarInt.EncodeFixedLength(37UL, 2, nonMinimal));
        Assert.Equal(new byte[] { 0x40, 0x25 }, nonMinimal);
        Assert.True(QuicVarInt.TryDecode(nonMinimal, out ulong nmDec, out int nmRead));
        Assert.Equal(37UL, nmDec);
        Assert.Equal(2, nmRead);
    }

    [Fact]
    public void TransportParametersRoundtripAndValidationWork()
    {
        var scid = new byte[] { 1, 2, 3, 4, 5, 6, 7, 8 };
        var rng = new Random(42);
        QuicTransportParameters tp = QuicTransportParametersCodec.FromSpec(ChromeQuicSpecs.DefaultTransportSpec, scid, initialRttUs: 12_345, random: rng);
        byte[] encoded = QuicTransportParametersCodec.Encode(tp, shuffle: true, random: rng);

        QuicTransportParameters decoded = QuicTransportParametersCodec.Decode(encoded, isServerParameters: false);
        Assert.Equal(scid, decoded.InitialSourceConnectionId);
        Assert.Equal(30_000UL, decoded.MaxIdleTimeoutMs);
        Assert.Equal(15_728_640UL, decoded.InitialMaxData);
        Assert.Equal(100UL, decoded.InitialMaxStreamsBidi);
        Assert.Equal(103UL, decoded.InitialMaxStreamsUni);
        Assert.Equal(65_536UL, decoded.MaxDatagramFrameSize);
        Assert.Equal(12_345UL, decoded.GoogleInitialRttUs);
        Assert.Contains(decoded.AdditionalParameters, p => QuicTransportParameterId.IsGrease(p.Id));

        // Reject invalid server transport parameters (max_ack_delay >= 16384, ack_delay_exponent > 20, max_udp_payload_size < 1200, reset token len != 16)
        byte[] badAckDelay = QuicTransportParametersCodec.Encode(new QuicTransportParameters { MaxAckDelayMs = 16_384 });
        Assert.Throws<QuicException>(() => QuicTransportParametersCodec.Decode(badAckDelay, isServerParameters: true));

        byte[] badResetToken = QuicTransportParametersCodec.Encode(new QuicTransportParameters { StatelessResetToken = new byte[15] });
        Assert.Throws<QuicException>(() => QuicTransportParametersCodec.Decode(badResetToken, isServerParameters: true));
    }

    [Fact]
    public void ChaosFramesSplitsIntoOneToElevenSlicesWithPingAndPadding()
    {
        byte[] ch = new byte[1600];
        for (int i = 0; i < ch.Length; i++)
            ch[i] = (byte)(i * 7 + 3);

        var rng = new Random(1337);
        List<List<QuicFrame>> packets = ChaosFrames.PackInitialFrameLists(
            ch,
            minPlaintextBytes: 1150,
            maxPlaintextBytes: 1180,
            enableChaos: true,
            includePing: true,
            fragmentCountOverride: 7,
            random: rng);

        Assert.True(packets.Count >= 2);
        var cryptoFrames = new List<QuicCryptoFrame>();
        bool hasPing = false;
        foreach (List<QuicFrame> pkt in packets)
        {
            byte[] encoded = QuicFrameCodec.Encode(pkt);
            Assert.True(encoded.Length >= 1150);
            Assert.True(encoded.Length <= 1180);

            List<QuicFrame> decoded = QuicFrameCodec.DecodeAll(encoded, QuicEncryptionLevel.Initial);
            foreach (QuicFrame f in decoded)
            {
                if (f is QuicCryptoFrame cf)
                    cryptoFrames.Add(cf);
                else if (f is QuicPingFrame)
                    hasPing = true;
            }
        }

        Assert.True(hasPing);
        Assert.InRange(cryptoFrames.Count, 2, 24);

        // Reassemble out-of-order CRYPTO fragments and verify exact payload equality
        var reassembled = new byte[ch.Length];
        foreach (QuicCryptoFrame cf in cryptoFrames)
            cf.Data.CopyTo(reassembled, (int)cf.Offset);
        Assert.Equal(ch, reassembled);
    }

    // ---- 3. RFC 9002 Loss Recovery & Congestion Control ----

    [Fact]
    public void QuicLossRecoveryRttPtoSlowStartAndLossHalvingWork()
    {
        var lr = new QuicLossRecovery();
        Assert.Equal(TimeSpan.FromMilliseconds(333), lr.SmoothedRtt);
        Assert.Equal(14_720UL, lr.CongestionWindow);
        Assert.Equal(2_400UL, lr.MinimumWindow);

        // Send packets 0..4 at t=0..4ms
        for (ulong pn = 0; pn <= 4; pn++)
            lr.OnPacketSent(QuicPacketNumberSpace.Application, pn, 1200, ackEliciting: true, inFlight: true, now: TimeSpan.FromMilliseconds(pn));

        Assert.Equal(6_000UL, lr.BytesInFlight);

        // ACK packet 0 at t=40ms -> first RTT sample = 40ms
        lr.OnAckReceived(QuicPacketNumberSpace.Application, QuicAckFrame.FromPacketNumbers(new[] { 0UL }), TimeSpan.FromMilliseconds(40));
        Assert.Equal(TimeSpan.FromMilliseconds(40), lr.MinRtt);
        Assert.Equal(TimeSpan.FromMilliseconds(40), lr.SmoothedRtt);
        Assert.Equal(14_720UL + 1200UL, lr.CongestionWindow); // slow start

        // Verify PTO calculation: (srtt + max(4*rttvar, 1ms) + maxAckDelay) << min(ptoCount, 10)
        TimeSpan expectedPto = lr.SmoothedRtt + TimeSpan.FromTicks(Math.Max(4 * lr.RttVar.Ticks, QuicLossRecovery.Granularity.Ticks)) + lr.MaxAckDelay;
        Assert.Equal(expectedPto, lr.GetPtoDuration(QuicPacketNumberSpace.Application));

        // ACK packet 4 at t=45ms -> packet 1 is 3 below largestAcked (4 >= 1 + 3), so packet 1 is declared lost!
        ulong cwndBeforeLoss = lr.CongestionWindow;
        QuicAckProcessResult lossRes = lr.OnAckReceived(QuicPacketNumberSpace.Application, QuicAckFrame.FromPacketNumbers(new[] { 4UL }), TimeSpan.FromMilliseconds(45));
        Assert.Contains(lossRes.LostPackets, p => p.PacketNumber == 1UL);
        Assert.Equal(Math.Max(cwndBeforeLoss / 2UL, lr.MinimumWindow), lr.Ssthresh);
        Assert.Equal(lr.Ssthresh, lr.CongestionWindow);

        // Packets 2 & 3 remain in-flight with a pending time-threshold loss timer; firing at t=55ms detects them via LossTimer.
        QuicLossTimerOutcome timeLossOutcome = lr.OnLossDetectionTimeout(TimeSpan.FromMilliseconds(55));
        Assert.True(timeLossOutcome.WasLossTimer);
        Assert.Contains(timeLossOutcome.LostPackets, p => p.PacketNumber == 2UL);
        Assert.Contains(timeLossOutcome.LostPackets, p => p.PacketNumber == 3UL);

        // Now confirm handshake, send packet 5 (no pending loss timer), and verify PTO backoff doubles on timeout.
        lr.MarkHandshakeConfirmed(TimeSpan.FromMilliseconds(55));
        lr.OnPacketSent(QuicPacketNumberSpace.Application, 5UL, 1200, ackEliciting: true, inFlight: true, now: TimeSpan.FromMilliseconds(60));
        TimeSpan ptoBeforeTimeout = lr.GetPtoDuration(QuicPacketNumberSpace.Application);
        QuicLossTimerOutcome ptoOutcome = lr.OnLossDetectionTimeout(TimeSpan.FromMilliseconds(500));
        Assert.False(ptoOutcome.WasLossTimer);
        Assert.Equal(1, lr.PtoCount);
        Assert.Equal(TimeSpan.FromTicks(ptoBeforeTimeout.Ticks << 1), lr.GetPtoDuration(QuicPacketNumberSpace.Application));
    }

    // ---- 4. SOCKS5 UDP ASSOCIATE + 66,048B Buffer + 30s DNS Cache TTL ----

    [Fact]
    public async Task Socks5UdpTransportNegotiatesUdpAssociateAndCachesDnsFor30Seconds()
    {
        // Verify 30s TTL DNS cache directly with deterministic clock
        DateTimeOffset now = new(2026, 11, 23, 7, 0, 0, TimeSpan.Zero);
        int dnsCalls = 0;
        var dnsCache = new QuicDnsCache(
            QuicDnsCache.DefaultTtl,
            clock: () => now,
            resolver: (host, _) =>
            {
                dnsCalls++;
                return ValueTask.FromResult(new[] { IPAddress.Loopback });
            });

        await dnsCache.ResolveAsync("quic.example.test");
        await dnsCache.ResolveAsync("quic.example.test");
        Assert.Equal(1, dnsCalls);
        now = now.AddSeconds(29);
        await dnsCache.ResolveAsync("quic.example.test");
        Assert.Equal(1, dnsCalls);
        now = now.AddSeconds(2); // 31s > 30s TTL
        await dnsCache.ResolveAsync("quic.example.test");
        Assert.Equal(2, dnsCalls);

        // Start real local TCP+UDP SOCKS5 mock relay
        using var tcpListener = new TcpListener(IPAddress.Loopback, 0);
        tcpListener.Start();
        int proxyTcpPort = ((IPEndPoint)tcpListener.LocalEndpoint).Port;

        using var relayUdp = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);
        relayUdp.Bind(new IPEndPoint(IPAddress.Loopback, 0));
        int relayUdpPort = ((IPEndPoint)relayUdp.LocalEndPoint!).Port;

        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(10));
        string? observedRelayDstIp = null;
        int observedRelayDstPort = 0;

        Task relayTask = Task.Run(async () =>
        {
            using Socket ctrl = await tcpListener.AcceptSocketAsync(cts.Token);
            var buf = new byte[256];
            int n = await ctrl.ReceiveAsync(buf, SocketFlags.None, cts.Token);
            Assert.Equal(0x05, buf[0]);
            Assert.Contains((byte)0x02, buf[2..n]);
            await ctrl.SendAsync(new byte[] { 0x05, 0x02 }, SocketFlags.None, cts.Token);

            // RFC 1929 user/pass
            n = await ctrl.ReceiveAsync(buf, SocketFlags.None, cts.Token);
            Assert.Equal(0x01, buf[0]);
            await ctrl.SendAsync(new byte[] { 0x01, 0x00 }, SocketFlags.None, cts.Token);

            // UDP ASSOCIATE
            n = await ctrl.ReceiveAsync(buf, SocketFlags.None, cts.Token);
            Assert.Equal(0x05, buf[0]);
            Assert.Equal(0x03, buf[1]);
            var rep = new byte[10];
            rep[0] = 0x05;
            rep[1] = 0x00;
            rep[2] = 0x00;
            rep[3] = 0x01; // IPv4 0.0.0.0 -> tests unspecified address substitution!
            BinaryPrimitives.WriteUInt16BigEndian(rep.AsSpan(8, 2), (ushort)relayUdpPort);
            await ctrl.SendAsync(rep, SocketFlags.None, cts.Token);

            // Relay 1 UDP datagram back as echo
            var udpBuf = new byte[4096];
            SocketReceiveFromResult rxRes = await relayUdp.ReceiveFromAsync(udpBuf, SocketFlags.None, new IPEndPoint(IPAddress.Any, 0), cts.Token);
            byte[] reply = BuildSocks5EchoReply(udpBuf, rxRes.ReceivedBytes, out string dstIp, out int dstPort);
            observedRelayDstIp = dstIp;
            observedRelayDstPort = dstPort;
            await relayUdp.SendToAsync(reply, SocketFlags.None, rxRes.RemoteEndPoint, cts.Token);

            // Hold TCP control channel open until client closes
            while (await ctrl.ReceiveAsync(buf, SocketFlags.None, cts.Token) > 0) { }
        }, cts.Token);

        var proxy = new ProxySpec(ProxyProtocolKind.Socks5, "127.0.0.1", proxyTcpPort, "cyber", "secret");
        await using Socks5UdpTransport socks5 = await Socks5UdpTransport.ConnectAsync(proxy, "quic.example.test", 8443, dnsCache, cts.Token);

        Assert.Equal(66_048, socks5.ReceiveBufferLength);
        Assert.Equal(relayUdpPort, socks5.RelayEndPoint.Port);
        Assert.Equal(IPAddress.Loopback, socks5.RelayEndPoint.Address);

        byte[] quicProbe = Encoding.UTF8.GetBytes("QUIC-PING-OVER-SOCKS5");
        await socks5.SendDatagramAsync(quicProbe, cts.Token);

        var rxBuf = new byte[2048];
        int rxLen = await socks5.ReceiveDatagramAsync(rxBuf, cts.Token);
        Assert.Equal(quicProbe, rxBuf[..rxLen]);
        Assert.Equal("127.0.0.1", observedRelayDstIp);
        Assert.Equal(8443, observedRelayDstPort);

        await socks5.DisposeAsync();
        await relayTask;
    }

    [Fact]
    public async Task Socks5UdpTransportRejectsDomainNameRelayAddress()
    {
        using var tcpListener = new TcpListener(IPAddress.Loopback, 0);
        tcpListener.Start();
        int port = ((IPEndPoint)tcpListener.LocalEndpoint).Port;
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));

        Task server = Task.Run(async () =>
        {
            using Socket s = await tcpListener.AcceptSocketAsync(cts.Token);
            var b = new byte[64];
            await s.ReceiveAsync(b, SocketFlags.None, cts.Token);
            await s.SendAsync(new byte[] { 0x05, 0x00 }, SocketFlags.None, cts.Token);
            await s.ReceiveAsync(b, SocketFlags.None, cts.Token);
            byte[] host = Encoding.ASCII.GetBytes("relay.bad");
            var rep = new byte[4 + 1 + host.Length + 2];
            rep[0] = 0x05;
            rep[1] = 0x00;
            rep[3] = 0x03; // ATYP domain
            rep[4] = (byte)host.Length;
            host.CopyTo(rep, 5);
            BinaryPrimitives.WriteUInt16BigEndian(rep.AsSpan(5 + host.Length, 2), 1080);
            await s.SendAsync(rep, SocketFlags.None, cts.Token);
        }, cts.Token);

        var proxy = new ProxySpec(ProxyProtocolKind.Socks5, "127.0.0.1", port);
        ProxyException ex = await Assert.ThrowsAsync<ProxyException>(() =>
            Socks5UdpTransport.ConnectAsync(proxy, "example.com", 443, cancellationToken: cts.Token));
        Assert.Contains("domain name relay address", ex.Message, StringComparison.OrdinalIgnoreCase);
        await server;
    }

    // ---- 5. RFC 9204 QPACK Static, Dynamic & Huffman KATs ----

    [Fact]
    public void QpackStaticDynamicTableAndStrictHuffmanWork()
    {
        Assert.Equal(99, QpackStaticTable.Entries.Count);
        Assert.Equal(new PureHttpHeader(":authority", ""), QpackStaticTable.Entries[0]);
        Assert.Equal(new PureHttpHeader(":method", "GET"), QpackStaticTable.Entries[17]);
        Assert.Equal(new PureHttpHeader("x-frame-options", "sameorigin"), QpackStaticTable.Entries[98]);

        // Static encoder KAT: RequiredInsertCount=0, DeltaBase=0
        var encoder = new QpackEncoder();
        var reqHeaders = new List<PureHttpHeader>
        {
            new(":method", "GET"),
            new(":scheme", "https"),
            new(":authority", "www.example.com"),
            new(":path", "/"),
            new("x-custom-token", "alpha-beta-123"),
        };
        byte[] wire = encoder.Encode(reqHeaders, useHuffman: true);
        Assert.Equal(0x00, wire[0]);
        Assert.Equal(0x00, wire[1]);

        var decoder = new QpackDecoder(maxTableCapacity: 4096, maxBlockedStreams: 16);
        List<PureHttpHeader> decodedStatic = decoder.DecodeFieldSection(wire, out ulong ric);
        Assert.Equal(0UL, ric);
        Assert.Equal(reqHeaders, decodedStatic);

        // Dynamic table instruction stream KAT: SetCapacity(512) -> InsertWithNameReference(static :status) -> InsertWithoutNameReference -> Duplicate
        var inst = new List<byte>();
        inst.AddRange(QpackEncoder.EncodeSetCapacityInstruction(512));
        inst.AddRange(QpackEncoder.EncodeInsertWithNameRefInstruction(isStatic: true, 25, "201", useHuffman: true));
        inst.AddRange(QpackEncoder.EncodeInsertWithoutNameRefInstruction("x-server-dyn", "edge-01", useHuffman: true));
        inst.AddRange(QpackEncoder.EncodeDuplicateInstruction(1)); // duplicates ":status: 201" at index 2

        byte[] incFeedback = decoder.ProcessEncoderInstructions(inst.ToArray());
        Assert.Equal(3UL, decoder.DynamicTable.InsertCount);
        Assert.NotEmpty(incFeedback);

        // Encode field section referencing dynamic relative index 0 (Duplicate ":status: 201") and 1 ("x-server-dyn: edge-01") with RIC=3, Base=3
        var dynBlock = new List<byte>();
        dynBlock.AddRange(QpackEncoder.EncodeFieldSectionPrefix(3, 3, 4096));
        dynBlock.Add(0x80 | 0x00); // Indexed Dynamic rel=0 -> :status: 201
        dynBlock.Add(0x80 | 0x01); // Indexed Dynamic rel=1 -> x-server-dyn: edge-01

        List<PureHttpHeader> dynHeaders = decoder.DecodeFieldSection(dynBlock.ToArray(), out ulong dynRic);
        Assert.Equal(3UL, dynRic);
        Assert.Equal(new PureHttpHeader(":status", "201"), dynHeaders[0]);
        Assert.Equal(new PureHttpHeader("x-server-dyn", "edge-01"), dynHeaders[1]);

        // Strict Huffman validation rejects >= 8 bit padding (0xFF) and non-all-1s padding (0x00)
        Assert.Throws<Http3Exception>(() => QpackHuffman.Decode(new byte[] { 0xFF }));
        Assert.Throws<Http3Exception>(() => QpackHuffman.Decode(new byte[] { 0x00 }));
    }

    // ---- 6. End-to-End Pure C# QUIC + HTTP/3 Loopback Tests ----

    [Theory]
    [InlineData("chrome_150", false)]
    [InlineData("chrome_144", true)]
    [InlineData("chrome_131", false)]
    public async Task EndToEndQuicHttp3HandshakeRetryMultiplexingCompressionTrailersAndDynamicQpack(
        string profileName,
        bool enableRetry)
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole QUIC Root CA");
        using X509Certificate2 leafCert = CreateTestLeaf(leafKey, caCert, TestHost);
        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);

        await using var pair = new LoopbackQuicTransportPair();
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));

        var server = new SyntheticQuicHttp3Server(
            pair.Server,
            leafKey,
            new[] { leafCert.RawData, caCert.RawData },
            requireRetry: enableRetry);
        Task serverTask = server.RunAsync(cts.Token);

        ClientProfile profile = ProfileRegistry.GetRequired(profileName);
        var quicOpts = new QuicConnectionOptions
        {
            Host = TestHost,
            Port = 443,
            Profile = profile,
            VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
            TransportOverride = pair.Client,
            UseChaosInitialFrames = true,
            ConnectTimeout = TimeSpan.FromSeconds(10),
        };

        ConnectionKey key = ConnectionKey.Create("https", TestHost, 443, profileName);
        await using Http3Connection h3 = await Http3Connection.ConnectAsync(quicOpts, key, cts.Token);

        Assert.Equal("HTTP/3", h3.ProtocolVersion);
        Assert.True(h3.IsUsable);
        Assert.True(h3.CanAcceptNewStream());
        Assert.Equal(enableRetry, h3.Quic.RetryReceived);
        Assert.Equal("h3", h3.Quic.NegotiatedAlpn);
        Assert.NotNull(h3.Quic.PeerCertificates);

        // Concurrent GET + POST + compressed (gzip, br, zstd) + 103 Early Hints + Trailers + Dynamic QPACK
        Task<PureHttpResponse> tHello = h3.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri("https://localhost/hello"),
        }, cts.Token);

        byte[] postPayload = Encoding.UTF8.GetBytes("{\"order\":\"cyber-h3-test\"}");
        Task<PureHttpResponse> tEcho = h3.SendAsync(new PureHttpRequest
        {
            Method = "POST",
            Uri = new Uri("https://localhost/echo"),
            Headers = new[] { new PureHttpHeader("content-type", "application/json") },
            Body = postPayload,
        }, cts.Token);

        Task<PureHttpResponse> tGzip = h3.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri("https://localhost/compressed/gzip"),
        }, cts.Token);

        Task<PureHttpResponse> tBr = h3.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri("https://localhost/compressed/br"),
        }, cts.Token);

        Task<PureHttpResponse> tZstd = h3.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri("https://localhost/compressed/zstd"),
        }, cts.Token);

        Task<PureHttpResponse> tTrailers = h3.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri("https://localhost/early-hints-and-trailers"),
        }, cts.Token);

        Task<PureHttpResponse> tDynQpack = h3.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri("https://localhost/dynamic-qpack"),
        }, cts.Token);

        await Task.WhenAll(tHello, tEcho, tGzip, tBr, tZstd, tTrailers, tDynQpack);

        PureHttpResponse rHello = await tHello;
        Assert.Equal(200, rHello.StatusCode);
        Assert.Equal("hello-h3", Encoding.UTF8.GetString(rHello.Body));

        PureHttpResponse rEcho = await tEcho;
        Assert.Equal(200, rEcho.StatusCode);
        Assert.Equal(postPayload, rEcho.Body);

        PureHttpResponse rGzip = await tGzip;
        Assert.Equal("compressed-payload-gzip-ok", Encoding.UTF8.GetString(rGzip.Body));

        PureHttpResponse rBr = await tBr;
        Assert.Equal("compressed-payload-br-ok", Encoding.UTF8.GetString(rBr.Body));

        PureHttpResponse rZstd = await tZstd;
        Assert.Equal("compressed-payload-zstd-ok", Encoding.UTF8.GetString(rZstd.Body));

        PureHttpResponse rTrailers = await tTrailers;
        Assert.Equal(200, rTrailers.StatusCode);
        Assert.Equal("body-after-103", Encoding.UTF8.GetString(rTrailers.Body));
        Assert.Contains(rTrailers.Trailers, t => t.Name == "x-trailer-digest" && t.Value == "sha256-ok");

        PureHttpResponse rDyn = await tDynQpack;
        Assert.Equal(201, rDyn.StatusCode);
        Assert.Equal("edge-dynamic-qpack", rDyn.GetFirstHeader("x-dyn-header"));

        // Verify server GOAWAY transitions CanAcceptNewStream() == false and rejects new requests
        await server.SendGoAwayAsync(0UL, cts.Token);
        await WaitUntilAsync(() => h3.GoAwayReceived, cts.Token);
        Assert.False(h3.CanAcceptNewStream());
        await Assert.ThrowsAsync<Http3Exception>(() => h3.SendAsync(new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri("https://localhost/after-goaway"),
        }, cts.Token));

        await h3.DisposeAsync();
        cts.Cancel();
        await server.DisposeAsync();
        try { await serverTask; } catch (OperationCanceledException) { }
    }

    [Fact]
    public async Task Http3CriticalStreamClosureAndInvalidSettingsTriggerExpectedErrors()
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole H3 Error Root");
        using X509Certificate2 leafCert = CreateTestLeaf(leafKey, caCert, TestHost);
        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);

        // Case 1: Server closes critical Control stream -> H3_CLOSED_CRITICAL_STREAM (260 = 0x0104)
        await using (var pair = new LoopbackQuicTransportPair())
        {
            using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(10));
            var server = new SyntheticQuicHttp3Server(pair.Server, leafKey, new[] { leafCert.RawData, caCert.RawData });
            Task serverTask = server.RunAsync(cts.Token);

            await using Http3Connection h3 = await Http3Connection.ConnectAsync(
                new QuicConnectionOptions
                {
                    Host = TestHost,
                    Port = 443,
                    Profile = ProfileRegistry.GetRequired("chrome_144"),
                    VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
                    TransportOverride = pair.Client,
                },
                ConnectionKey.Create("https", TestHost, 443, "chrome_144"),
                cts.Token);

            await server.CloseControlStreamAsync(cts.Token);
            Exception fatal = await h3.FatalErrorTask.WaitAsync(cts.Token);
            Http3Exception h3Ex = Assert.IsType<Http3Exception>(fatal);
            Assert.Equal(Http3ErrorCode.ClosedCriticalStream, h3Ex.H3ErrorCode);
            Assert.False(h3.IsUsable);

            cts.Cancel();
            await server.DisposeAsync();
            try { await serverTask; } catch (OperationCanceledException) { }
        }

        // Case 2: Server sends forbidden HTTP/2 setting (0x02 ENABLE_PUSH) -> H3_SETTINGS_ERROR (265 = 0x0109)
        await using (var pair = new LoopbackQuicTransportPair())
        {
            using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(10));
            var server = new SyntheticQuicHttp3Server(
                pair.Server,
                leafKey,
                new[] { leafCert.RawData, caCert.RawData },
                sendInvalidSetting: true);
            Task serverTask = server.RunAsync(cts.Token);

            await using Http3Connection h3 = await Http3Connection.ConnectAsync(
                new QuicConnectionOptions
                {
                    Host = TestHost,
                    Port = 443,
                    Profile = ProfileRegistry.GetRequired("chrome_144"),
                    VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
                    TransportOverride = pair.Client,
                },
                ConnectionKey.Create("https", TestHost, 443, "chrome_144"),
                cts.Token);

            Exception fatal = await h3.FatalErrorTask.WaitAsync(cts.Token);
            Http3Exception h3Ex = Assert.IsType<Http3Exception>(fatal);
            Assert.Equal(Http3ErrorCode.SettingsError, h3Ex.H3ErrorCode);

            cts.Cancel();
            await server.DisposeAsync();
            try { await serverTask; } catch (OperationCanceledException) { }
        }
    }

    // ---- Test Utilities & Pure C# QUIC+HTTP/3 Server Harness ----

    private static byte[] BuildSocks5EchoReply(byte[] udpBuf, int receivedBytes, out string dstIp, out int dstPort)
    {
        Assert.True(Socks5UdpTransport.TryDecodeUdpPacket(udpBuf.AsSpan(0, receivedBytes), out dstIp, out dstPort, out ReadOnlySpan<byte> inner));
        var reply = new byte[10 + inner.Length];
        Socks5UdpTransport.EncodeUdpHeader(IPAddress.Loopback, 443, reply);
        inner.CopyTo(reply.AsSpan(10));
        return reply;
    }

    private static async Task WaitUntilAsync(Func<bool> predicate, CancellationToken ct)
    {
        for (int i = 0; i < 200; i++)
        {
            if (predicate())
                return;
            await Task.Delay(10, ct);
        }
        Assert.True(predicate(), "Condition did not become true within timeout.");
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

        public void Reset()
        {
            _chunks.Clear();
            _readOffset = 0;
        }
    }

    /// <summary>
    /// Minimal pure managed RFC 9000/9001/9114 QUIC + HTTP/3 loopback test server.
    /// Implemented purely on top of Cybersole.Http managed primitives.
    /// </summary>
    private sealed class SyntheticQuicHttp3Server : IAsyncDisposable
    {
        private readonly IQuicDatagramTransport _transport;
        private readonly ECDsa _leafKey;
        private readonly byte[][] _derChain;
        private readonly bool _requireRetry;
        private readonly bool _sendInvalidSetting;
        private readonly byte[] _serverScid = RandomNumberGenerator.GetBytes(8);
        private readonly byte[] _retryScid = RandomNumberGenerator.GetBytes(8);
        private readonly byte[] _retryToken = Encoding.ASCII.GetBytes("cybersole-retry-token");
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

        private bool _sentRetry;
        private bool _handshakeReplied;
        private bool _handshakeDoneSent;
        private readonly ServerStreamAssembler _initCrypto = new();
        private readonly MemoryStream _chAccum = new();
        private readonly MemoryStream _hsCryptoAccum = new();
        private readonly MemoryStream _transcript = new();
        private byte[] _cHsSecret = Array.Empty<byte>();
        private byte[] _sHsSecret = Array.Empty<byte>();
        private byte[] _masterSecret = Array.Empty<byte>();

        // Server H3 streams
        private readonly ulong _srvControlStreamId = 3; // first server uni
        private readonly ulong _srvEncoderStreamId = 7;
        private readonly ulong _srvDecoderStreamId = 11;
        private ulong _srvControlOffset;
        private ulong _srvEncoderOffset;
        private ulong _srvDecoderOffset;
        private readonly ConcurrentDictionary<ulong, (ServerStreamAssembler Asm, MemoryStream Buf, ulong? FinSize, bool Handled)> _bidiStreams = new();
        private readonly ConcurrentDictionary<ulong, ServerStreamAssembler> _clientUniStreams = new();
        private readonly QpackDecoder _reqDecoder = new();
        private bool _dynamicTableInitialized;

        public SyntheticQuicHttp3Server(
            IQuicDatagramTransport transport,
            ECDsa leafKey,
            byte[][] derChain,
            bool requireRetry = false,
            bool sendInvalidSetting = false)
        {
            _transport = transport;
            _leafKey = leafKey;
            _derChain = derChain;
            _requireRetry = requireRetry;
            _sendInvalidSetting = sendInvalidSetting;
        }

        public async Task RunAsync(CancellationToken ct)
        {
            var buf = new byte[66_048];
            while (!ct.IsCancellationRequested)
            {
                int n = await _transport.ReceiveDatagramAsync(buf, ct);
                if (n == 0)
                    break;

                var outbound = new List<byte[]>();
                ProcessDatagram(buf.AsSpan(0, n), outbound);
                for (int i = 0; i < outbound.Count; i++)
                    await _transport.SendDatagramAsync(outbound[i], ct);
            }
        }

        public async Task SendGoAwayAsync(ulong streamId, CancellationToken ct)
        {
            byte[] frame = Http3FrameCodec.BuildFrame(Http3FrameType.GoAway, QuicVarInt.Encode(streamId));
            byte[] pkt = BuildServerControlPacket(frame, fin: false);
            await _transport.SendDatagramAsync(pkt, ct);
        }

        public async Task CloseControlStreamAsync(CancellationToken ct)
        {
            byte[] pkt = BuildServerControlPacket(Array.Empty<byte>(), fin: true);
            await _transport.SendDatagramAsync(pkt, ct);
        }

        private byte[] BuildServerControlPacket(byte[] data, bool fin)
        {
            lock (_txLock)
            {
                ulong off = _srvControlOffset;
                _srvControlOffset += (ulong)data.Length;
                byte[] pt = QuicFrameCodec.Encode(new QuicFrame[] { new QuicStreamFrame(_srvControlStreamId, off, data, fin) });
                return QuicPacketCodec.BuildShortHeaderPacket(_clientCid, _pnApp++, 1, keyPhase: false, pt, _appWrite!);
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
                    ReadOnlySpan<byte> token = ReadOnlySpan<byte>.Empty;
                    if (type == QuicLongPacketType.Initial)
                    {
                        QuicVarInt.TryRead(span, ref off, out ulong tLen);
                        token = span.Slice(off, (int)tLen);
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

                        if (_requireRetry && !_sentRetry && token.IsEmpty)
                        {
                            _sentRetry = true;
                            byte[] retryPkt = QuicPacketCodec.BuildRetryPacket(_originalDcid, _clientCid, _retryScid, _retryToken);
                            _initRead = QuicCrypto.DeriveInitialKeys(_retryScid, isServer: false);
                            _initWrite = QuicCrypto.DeriveInitialKeys(_retryScid, isServer: true);
                            _initCrypto.Reset();
                            _chAccum.SetLength(0);
                            _rxInitMax = -1;
                            outbound.Add(retryPkt);
                            return;
                        }

                        if (_requireRetry && !token.SequenceEqual(_retryToken))
                            return;

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
                RetrySourceConnectionId = _requireRetry ? _retryScid : null,
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

            var srvSettings = _sendInvalidSetting
                ? new List<(ulong, ulong)> { (0x02UL, 0UL) }
                : new List<(ulong, ulong)> { (Http3SettingId.QpackMaxTableCapacity, 65_536), (Http3SettingId.MaxFieldSectionSize, 262_144), (Http3SettingId.QpackBlockedStreams, 100), (Http3SettingId.H3Datagram, 1) };

            byte[] settingsFrame = Http3FrameCodec.BuildFrame(Http3FrameType.Settings, Http3FrameCodec.BuildSettingsPayload(srvSettings));
            byte[] ctrlStart = QuicVarInt.Encode(Http3StreamType.Control).Concat(settingsFrame).ToArray();
            outbound.Add(BuildServerControlPacket(ctrlStart, fin: false));

            lock (_txLock)
            {
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
                    byte[] h = qpack.Encode(new PureHttpHeader[]
                    {
                        new(":status", "200"),
                        new("content-type", "text/plain"),
                    });
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Headers, h));
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Data, Encoding.UTF8.GetBytes("hello-h3")));
                    break;
                }

                case "/echo":
                {
                    byte[] h = qpack.Encode(new PureHttpHeader[]
                    {
                        new(":status", "200"),
                        new("x-echo-method", method),
                    });
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Headers, h));
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Data, body.ToArray()));
                    break;
                }

                case "/compressed/gzip":
                {
                    byte[] raw = Encoding.UTF8.GetBytes("compressed-payload-gzip-ok");
                    byte[] gz;
                    using (var ms = new MemoryStream())
                    {
                        using (var g = new GZipStream(ms, CompressionLevel.Optimal, leaveOpen: true))
                            g.Write(raw);
                        gz = ms.ToArray();
                    }
                    byte[] h = qpack.Encode(new PureHttpHeader[] { new(":status", "200"), new("content-encoding", "gzip") });
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Headers, h));
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Data, gz));
                    break;
                }

                case "/compressed/br":
                {
                    byte[] raw = Encoding.UTF8.GetBytes("compressed-payload-br-ok");
                    byte[] br;
                    using (var ms = new MemoryStream())
                    {
                        using (var b = new BrotliStream(ms, CompressionLevel.Optimal, leaveOpen: true))
                            b.Write(raw);
                        br = ms.ToArray();
                    }
                    byte[] h = qpack.Encode(new PureHttpHeader[] { new(":status", "200"), new("content-encoding", "br") });
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Headers, h));
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Data, br));
                    break;
                }

                case "/compressed/zstd":
                {
                    byte[] raw = Encoding.UTF8.GetBytes("compressed-payload-zstd-ok");
                    using var comp = new ZstdSharp.Compressor();
                    byte[] zstd = comp.Wrap(raw).ToArray();
                    byte[] h = qpack.Encode(new PureHttpHeader[] { new(":status", "200"), new("content-encoding", "zstd") });
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Headers, h));
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Data, zstd));
                    break;
                }

                case "/early-hints-and-trailers":
                {
                    byte[] h103 = qpack.Encode(new PureHttpHeader[] { new(":status", "103"), new("link", "</style.css>; rel=preload") });
                    byte[] h200 = qpack.Encode(new PureHttpHeader[] { new(":status", "200") });
                    byte[] trailers = qpack.Encode(new PureHttpHeader[] { new("x-trailer-digest", "sha256-ok") });
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Headers, h103));
                    txPayload.Write(Http3FrameCodec.BuildFrame(188, new byte[] { 0xDE, 0xAD }));
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Headers, h200));
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Data, Encoding.UTF8.GetBytes("body-after-103")));
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Headers, trailers));
                    break;
                }

                case "/dynamic-qpack":
                {
                    if (!_dynamicTableInitialized)
                    {
                        _dynamicTableInitialized = true;
                        var inst = new List<byte>();
                        inst.AddRange(QpackEncoder.EncodeSetCapacityInstruction(4096));
                        inst.AddRange(QpackEncoder.EncodeInsertWithNameRefInstruction(isStatic: true, 25, "201"));
                        inst.AddRange(QpackEncoder.EncodeInsertWithoutNameRefInstruction("x-dyn-header", "edge-dynamic-qpack"));
                        byte[] instBytes = inst.ToArray();
                        lock (_txLock)
                        {
                            ulong eOff = _srvEncoderOffset;
                            _srvEncoderOffset += (ulong)instBytes.Length;
                            AddAppFramesLocked(new QuicFrame[] { new QuicStreamFrame(_srvEncoderStreamId, eOff, instBytes, Fin: false) }, outbound);
                        }
                    }

                    var block = new List<byte>();
                    block.AddRange(QpackEncoder.EncodeFieldSectionPrefix(2, 2, 65_536));
                    block.Add(0x80 | 0x01); // rel 1 = :status: 201
                    block.Add(0x80 | 0x00); // rel 0 = x-dyn-header: edge-dynamic-qpack
                    txPayload.Write(Http3FrameCodec.BuildFrame(Http3FrameType.Headers, block.ToArray()));
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
}
