using System.Buffers.Binary;
using System.IO.Compression;
using System.Net;
using System.Net.Sockets;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using Cybersole.Http.Compression;
using Cybersole.Http.Profiles;
using Cybersole.Http.Protocol;
using Cybersole.Http.Tls;
using Cybersole.Http.X509;
using Xunit;
using BcBc = Org.BouncyCastle.Tls.Crypto.Impl.BC;
using BcCrypto = Org.BouncyCastle.Tls.Crypto;
using BcSecurity = Org.BouncyCastle.Security;
using BcTls = Org.BouncyCastle.Tls;

namespace Cybersole.Tests;

public sealed class ProtocolLayerTests
{
    private const string TestHost = "localhost";

    // ---- 1. RFC 7541 Appendix C KATs & Strict HPACK Validation ----

    [Fact]
    public void HpackAppendixC_IntegerAndLiteralAndRequestResponseKats_MatchRfc7541()
    {
        // RFC 7541 Appendix C.1 Integer Representations
        AssertIntegerRoundTrip(10, 5, 0x00, "0a");
        AssertIntegerRoundTrip(1337, 5, 0x00, "1f9a0a");
        AssertIntegerRoundTrip(42, 8, 0x00, "2a");

        // RFC 7541 Appendix C.2.1 Literal Header Field with Indexing
        var decC2 = new HpackDecoder();
        List<PureHttpHeader> c21 = decC2.DecodeHeaderBlock(
            Convert.FromHexString("400a637573746f6d2d6b65790d637573746f6d2d686561646572"),
            validateHttp2Semantics: true);
        Assert.Equal(new[] { new PureHttpHeader("custom-key", "custom-header") }, c21);
        Assert.Equal(55, decC2.CurrentDynamicTableSize);

        // RFC 7541 Appendix C.2.2 Literal Header Field without Indexing
        List<PureHttpHeader> c22 = decC2.DecodeHeaderBlock(
            Convert.FromHexString("040c2f73616d706c652f70617468"),
            validateHttp2Semantics: true);
        Assert.Equal(new[] { new PureHttpHeader(":path", "/sample/path") }, c22);
        Assert.Equal(55, decC2.CurrentDynamicTableSize); // unchanged

        // RFC 7541 Appendix C.2.3 Literal Header Field Never Indexed
        List<PureHttpHeader> c23 = decC2.DecodeHeaderBlock(
            Convert.FromHexString("100870617373776f726406736563726574"),
            validateHttp2Semantics: true);
        Assert.Equal(new[] { new PureHttpHeader("password", "secret") }, c23);
        Assert.Equal(55, decC2.CurrentDynamicTableSize);

        // RFC 7541 Appendix C.2.4 Indexed Header Field
        List<PureHttpHeader> c24 = decC2.DecodeHeaderBlock(
            Convert.FromHexString("82"),
            validateHttp2Semantics: true);
        Assert.Equal(new[] { new PureHttpHeader(":method", "GET") }, c24);

        // RFC 7541 Appendix C.3 Request Examples without Huffman
        var encC3 = new HpackEncoder(4096, HpackHuffmanMode.Never);
        var decC3 = new HpackDecoder(4096);

        var req31 = new[]
        {
            new PureHttpHeader(":method", "GET"),
            new PureHttpHeader(":scheme", "http"),
            new PureHttpHeader(":path", "/"),
            new PureHttpHeader(":authority", "www.example.com"),
        };
        byte[] wire31 = encC3.EncodeHeaderList(req31, indexLiterals: true);
        Assert.Equal(Convert.FromHexString("828684410f7777772e6578616d706c652e636f6d"), wire31);
        Assert.Equal(req31, decC3.DecodeHeaderBlock(wire31));
        Assert.Equal(57, decC3.CurrentDynamicTableSize);

        var req32 = new[]
        {
            new PureHttpHeader(":method", "GET"),
            new PureHttpHeader(":scheme", "http"),
            new PureHttpHeader(":path", "/"),
            new PureHttpHeader(":authority", "www.example.com"),
            new PureHttpHeader("cache-control", "no-cache"),
        };
        byte[] wire32 = encC3.EncodeHeaderList(req32, indexLiterals: true);
        Assert.Equal(Convert.FromHexString("828684be58086e6f2d6361636865"), wire32);
        Assert.Equal(req32, decC3.DecodeHeaderBlock(wire32));
        Assert.Equal(110, decC3.CurrentDynamicTableSize);

        var req33 = new[]
        {
            new PureHttpHeader(":method", "GET"),
            new PureHttpHeader(":scheme", "https"),
            new PureHttpHeader(":path", "/index.html"),
            new PureHttpHeader(":authority", "www.example.com"),
            new PureHttpHeader("custom-key", "custom-value"),
        };
        byte[] wire33 = encC3.EncodeHeaderList(req33, indexLiterals: true);
        Assert.Equal(Convert.FromHexString("828785bf400a637573746f6d2d6b65790c637573746f6d2d76616c7565"), wire33);
        Assert.Equal(req33, decC3.DecodeHeaderBlock(wire33));
        Assert.Equal(164, decC3.CurrentDynamicTableSize);
        Assert.Equal(3, decC3.DynamicTableCount);

        // RFC 7541 Appendix C.4 Request Examples with Huffman
        var encC4 = new HpackEncoder(4096, HpackHuffmanMode.Always);
        var decC4 = new HpackDecoder(4096);

        byte[] wire41 = encC4.EncodeHeaderList(req31, indexLiterals: true);
        Assert.Equal(Convert.FromHexString("828684418cf1e3c2e5f23a6ba0ab90f4ff"), wire41);
        Assert.Equal(req31, decC4.DecodeHeaderBlock(wire41));

        byte[] wire42 = encC4.EncodeHeaderList(req32, indexLiterals: true);
        Assert.Equal(Convert.FromHexString("828684be5886a8eb10649cbf"), wire42);
        Assert.Equal(req32, decC4.DecodeHeaderBlock(wire42));

        byte[] wire43 = encC4.EncodeHeaderList(req33, indexLiterals: true);
        Assert.Equal(Convert.FromHexString("828785bf408825a849e95ba97d7f8925a849e95bb8e8b4bf"), wire43);
        Assert.Equal(req33, decC4.DecodeHeaderBlock(wire43));
        Assert.Equal(164, decC4.CurrentDynamicTableSize);

        // RFC 7541 Appendix C.5 Response Examples without Huffman + 256-byte dynamic table eviction
        VerifyAppendixC5AndC6ResponseSequence(HpackHuffmanMode.Never, expectedFirstStatusHexPrefix: "4803333032");

        // RFC 7541 Appendix C.6 Response Examples with Huffman + 256-byte dynamic table eviction
        VerifyAppendixC5AndC6ResponseSequence(HpackHuffmanMode.Always, expectedFirstStatusHexPrefix: "48826402");

        // Dynamic table size update (0x20..0x3F) + shrink/evict + reject exceeding SETTINGS_HEADER_TABLE_SIZE
        var encResize = new HpackEncoder(4096, HpackHuffmanMode.Never);
        var decResize = new HpackDecoder(4096);
        _ = decResize.DecodeHeaderBlock(encResize.EncodeHeaderList(req31));
        Assert.Equal(57, decResize.CurrentDynamicTableSize);
        encResize.SetMaxTableSize(32);
        byte[] resizedBlock = encResize.EncodeHeaderList(new[] { new PureHttpHeader(":method", "GET") });
        Assert.Equal(0x20, resizedBlock[0] & 0xE0);
        Assert.Equal(new[] { new PureHttpHeader(":method", "GET") }, decResize.DecodeHeaderBlock(resizedBlock));
        Assert.Equal(32, decResize.CurrentDynamicTableMaxSize);
        Assert.Equal(0, decResize.DynamicTableCount);

        // Error validations:
        // 1) Invalid Huffman padding (0 bit in padding)
        Assert.Throws<Http2Exception>(() => HpackHuffmanCodec.Decode(Convert.FromHexString("f1e3c2e5f23a6ba0ab90f4fe")));
        // 2) >7 bits padding
        Assert.Throws<Http2Exception>(() => HpackHuffmanCodec.Decode(Convert.FromHexString("f1e3c2e5f23a6ba0ab90f4ffff")));
        // 3) Explicit EOS symbol (30 one-bits + padding)
        Assert.Throws<Http2Exception>(() => HpackHuffmanCodec.Decode(new byte[] { 0xFF, 0xFF, 0xFF, 0xFF }));
        // 4) Dynamic table size update after header field
        Assert.Throws<Http2Exception>(() => new HpackDecoder().DecodeHeaderBlock(new byte[] { 0x82, 0x20 }));
        // 5) Pseudo-header after regular header
        Assert.Throws<Http2Exception>(() => new HpackDecoder().DecodeHeaderBlock(
            new byte[] { 0x40, 0x01, (byte)'x', 0x01, (byte)'1', 0x82 }));
        // 6) Uppercase header name
        Assert.Throws<Http2Exception>(() => new HpackDecoder().DecodeHeaderBlock(
            new byte[] { 0x40, 0x01, (byte)'X', 0x01, (byte)'1' }));
        // 7) MaxHeaderListSize exceeded
        var smallListDecoder = new HpackDecoder(4096, maxHeaderListSize: 40);
        Assert.Throws<Http2Exception>(() => smallListDecoder.DecodeHeaderBlock(
            Convert.FromHexString("400a637573746f6d2d6b65790d637573746f6d2d686561646572")));
    }

    private static void AssertIntegerRoundTrip(uint value, int prefixBits, byte mask, string expectedHex)
    {
        var list = new List<byte>();
        HpackIntegerCodec.Encode(list, value, prefixBits, mask);
        Assert.Equal(Convert.FromHexString(expectedHex), list.ToArray());

        int off = 0;
        uint decoded = HpackIntegerCodec.Decode(list.ToArray(), ref off, prefixBits);
        Assert.Equal(value, decoded);
        Assert.Equal(list.Count, off);
    }

    private static void VerifyAppendixC5AndC6ResponseSequence(HpackHuffmanMode mode, string expectedFirstStatusHexPrefix)
    {
        var enc = new HpackEncoder(256, mode);
        var dec = new HpackDecoder(256);

        var r1 = new[]
        {
            new PureHttpHeader(":status", "302"),
            new PureHttpHeader("cache-control", "private"),
            new PureHttpHeader("date", "Mon, 21 Oct 2013 20:13:21 GMT"),
            new PureHttpHeader("location", "https://www.example.com"),
        };
        byte[] w1 = enc.EncodeHeaderList(r1, indexLiterals: true);
        Assert.StartsWith(expectedFirstStatusHexPrefix, Convert.ToHexString(w1).ToLowerInvariant(), StringComparison.Ordinal);
        Assert.Equal(r1, dec.DecodeHeaderBlock(w1));
        Assert.Equal(222, dec.CurrentDynamicTableSize);
        Assert.Equal(4, dec.DynamicTableCount);

        var r2 = new[]
        {
            new PureHttpHeader(":status", "307"),
            new PureHttpHeader("cache-control", "private"),
            new PureHttpHeader("date", "Mon, 21 Oct 2013 20:13:21 GMT"),
            new PureHttpHeader("location", "https://www.example.com"),
        };
        byte[] w2 = enc.EncodeHeaderList(r2, indexLiterals: true);
        Assert.Equal(r2, dec.DecodeHeaderBlock(w2));
        Assert.Equal(222, dec.CurrentDynamicTableSize);
        Assert.Equal(4, dec.DynamicTableCount);
        Assert.Equal(":status", dec.GetDynamicTableEntries()[0].Name);
        Assert.Equal("307", dec.GetDynamicTableEntries()[0].Value);

        var r3 = new[]
        {
            new PureHttpHeader(":status", "200"),
            new PureHttpHeader("cache-control", "private"),
            new PureHttpHeader("date", "Mon, 21 Oct 2013 20:13:22 GMT"),
            new PureHttpHeader("location", "https://www.example.com"),
            new PureHttpHeader("content-encoding", "gzip"),
            new PureHttpHeader("set-cookie", "foo=ASDJKHQKBZXOQWEOPIUAXQWEOIU; max-age=3600; version=1"),
        };
        byte[] w3 = enc.EncodeHeaderList(r3, indexLiterals: true);
        Assert.Equal(r3, dec.DecodeHeaderBlock(w3));
        Assert.Equal(215, dec.CurrentDynamicTableSize);
        Assert.Equal(3, dec.DynamicTableCount);
        IReadOnlyList<PureHttpHeader> entries = dec.GetDynamicTableEntries();
        Assert.Equal("set-cookie", entries[0].Name);
        Assert.Equal("content-encoding", entries[1].Name);
        Assert.Equal("date", entries[2].Name);
    }

    // ---- 2. HPACK Header Order (Chrome vs Firefox Profile Specs) ----

    [Fact]
    public void HpackEncodeHeaders_HonorsChromeAndFirefoxPseudoAndHeaderOrderAndCookieSplitting()
    {
        ClientProfile chrome = ProfileRegistry.GetRequired("chrome_131");
        ClientProfile firefox = ProfileRegistry.GetRequired("firefox_117");

        var chromeOrder = new[] { "sec-ch-ua", "user-agent", "accept", "accept-encoding", "accept-language" };
        var firefoxOrder = new[] { "user-agent", "accept", "accept-language", "accept-encoding" };

        var chromeSpecWithOrder = new Http2SettingsSpec(
            chrome.Http2Settings.Settings,
            chrome.Http2Settings.ConnectionFlow,
            chrome.Http2Settings.PseudoHeaderOrder,
            chrome.Http2Settings.HeaderPriority,
            chrome.Http2Settings.PriorityFrames,
            chromeOrder);

        var firefoxSpecWithOrder = new Http2SettingsSpec(
            firefox.Http2Settings.Settings,
            firefox.Http2Settings.ConnectionFlow,
            firefox.Http2Settings.PseudoHeaderOrder,
            firefox.Http2Settings.HeaderPriority,
            firefox.Http2Settings.PriorityFrames,
            firefoxOrder);

        var req = new PureHttpRequest
        {
            Method = "POST",
            Uri = new Uri("https://shop.example.com/checkout?step=1"),
            Body = "{\"ok\":true}"u8.ToArray(),
            Headers = new[]
            {
                new PureHttpHeader("Host", "ignored-host-only-for-authority-override.example.com"),
                new PureHttpHeader("Connection", "keep-alive"),
                new PureHttpHeader("Transfer-Encoding", "chunked"),
                new PureHttpHeader("X-Custom-B", "2"),
                new PureHttpHeader("Accept-Language", "en-GB"),
                new PureHttpHeader("Cookie", "sid=abc;  theme=dark"),
                new PureHttpHeader("Accept-Encoding", "gzip, deflate, br"),
                new PureHttpHeader("Accept", "application/json"),
                new PureHttpHeader("Sec-Ch-Ua", "\"Chromium\";v=\"131\""),
                new PureHttpHeader("User-Agent", "CustomAgent/1.0"),
                new PureHttpHeader("X-Custom-A", "1"),
                new PureHttpHeader("Authorization", "Bearer top-secret"),
            },
        };

        // Chrome order: m,a,s,p + chromeOrder
        var chromeEncoder = new HpackEncoder();
        byte[] chromeBlock = chromeEncoder.EncodeHeaders(req, chromeSpecWithOrder);
        List<PureHttpHeader> chromeDecoded = new HpackDecoder().DecodeHeaderBlock(chromeBlock);

        Assert.Equal(new[] { ":method", ":authority", ":scheme", ":path" },
            chromeDecoded.Take(4).Select(h => h.Name).ToArray());
        Assert.Equal("ignored-host-only-for-authority-override.example.com", chromeDecoded[1].Value);

        string[] chromeRegularNames = chromeDecoded.Skip(4).Select(h => h.Name).ToArray();
        Assert.Equal(
            new[]
            {
                "sec-ch-ua", "user-agent", "accept", "accept-encoding", "accept-language",
                "x-custom-b", "cookie", "cookie", "x-custom-a", "authorization", "content-length",
            },
            chromeRegularNames);
        Assert.Equal("sid=abc", chromeDecoded.First(h => h.Name == "cookie").Value);
        Assert.Equal("theme=dark", chromeDecoded.Last(h => h.Name == "cookie").Value);
        Assert.Equal("11", chromeDecoded.Single(h => h.Name == "content-length").Value);

        // Firefox order: m,p,a,s + firefoxOrder
        var firefoxEncoder = new HpackEncoder();
        byte[] firefoxBlock = firefoxEncoder.EncodeHeaders(req, firefoxSpecWithOrder);
        List<PureHttpHeader> firefoxDecoded = new HpackDecoder().DecodeHeaderBlock(firefoxBlock);

        Assert.Equal(new[] { ":method", ":path", ":authority", ":scheme" },
            firefoxDecoded.Take(4).Select(h => h.Name).ToArray());
        Assert.Equal(
            new[]
            {
                "user-agent", "accept", "accept-language", "accept-encoding",
                "x-custom-b", "cookie", "cookie", "sec-ch-ua", "x-custom-a", "authorization", "content-length",
            },
            firefoxDecoded.Skip(4).Select(h => h.Name).ToArray());

        // Fallback User-Agent when omitted
        var bareReq = new PureHttpRequest
        {
            Method = "GET",
            Uri = new Uri("https://shop.example.com/"),
        };
        List<PureHttpHeader> bareDecoded = new HpackDecoder().DecodeHeaderBlock(
            new HpackEncoder().EncodeHeaders(bareReq, chrome.Http2Settings));
        Assert.Equal("Go-http-client/2.0", bareDecoded.Single(h => h.Name == "user-agent").Value);
    }

    // ---- 3. HTTP/2 over Real Loopback TLS 1.3 (Chrome_131 + Firefox_117) ----

    [Fact]
    public async Task Http2OverTls13Loopback_Chrome131_EnforcesSettingsContinuationMultiplexingPingRstGoAwayAndDecompression()
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole H2 Test Root");
        using X509Certificate2 serverCert = CreateTestLeaf(leafKey, caCert, TestHost);

        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);

        ClientProfile chrome131 = ProfileRegistry.GetRequired("chrome_131");

        using var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        int port = ((IPEndPoint)listener.LocalEndpoint).Port;

        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(20));
        bool prefaceMatched = false;
        List<(ushort Id, uint Value)> observedSettings = new();
        uint? observedConnWindowUpdate = null;
        bool observedPingAck = false;
        byte[] pingPayload = { 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88 };
        bool sawHeadersContinuationFromClient = false;
        bool sawFirstRequestPriority = false;
        var chromeClientDone = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        Exception? serverError = null;

        Task serverTask = Task.Run(async () =>
        {
            try
            {
                using TcpClient accepted = await listener.AcceptTcpClientAsync(cts.Token);
                using NetworkStream net = accepted.GetStream();
                var protocol = new BcTls.TlsServerProtocol(net);
                var bcServer = new BcTestTls13Server(
                    serverCert.RawData,
                    caCert.RawData,
                    leafKey.ExportPkcs8PrivateKey(),
                    BcTls.ProtocolName.Http_2_Tls);
                protocol.Accept(bcServer);

                using var tlsStream = new AsyncFriendlyBcStream(protocol.Stream);
                var h2Server = new H2TestServer(tlsStream);

                prefaceMatched = await h2Server.ReadAndVerifyPrefaceAsync(cts.Token);

                // Read client SETTINGS + WINDOW_UPDATE
                var settingsFrame = await h2Server.ReadFrameAsync(cts.Token);
                Assert.Equal(0x04, settingsFrame.Type);
                Assert.Equal(0, settingsFrame.StreamId);
                for (int off = 0; off < settingsFrame.Payload.Length; off += 6)
                {
                    observedSettings.Add((
                        BinaryPrimitives.ReadUInt16BigEndian(settingsFrame.Payload.AsSpan(off, 2)),
                        BinaryPrimitives.ReadUInt32BigEndian(settingsFrame.Payload.AsSpan(off + 2, 4))));
                }

                var wuFrame = await h2Server.ReadFrameAsync(cts.Token);
                Assert.Equal(0x08, wuFrame.Type);
                Assert.Equal(0, wuFrame.StreamId);
                observedConnWindowUpdate = BinaryPrimitives.ReadUInt32BigEndian(wuFrame.Payload);

                // Server sends SETTINGS + ACK + PING
                await h2Server.WriteSettingsAsync(
                    new (ushort, uint)[] { (3, 100), (4, 65535), (5, 16384) },
                    cts.Token);
                await h2Server.WriteSettingsAckAsync(cts.Token);
                await h2Server.WriteFrameAsync(0x06, 0x00, 0, pingPayload, cts.Token);

                var serverEncoder = new HpackEncoder(4096, HpackHuffmanMode.IfSmaller);
                var serverDecoder = new HpackDecoder(4096, 1_048_576);
                var openRequests = new Dictionary<int, (MemoryStream HeaderBuf, bool HasPriority)>();
                int streamsSeen = 0;
                int[] pendingGoAwayKeepStreamId = new int[1];

                while (streamsSeen < 14 || !observedPingAck)
                {
                    var frame = await h2Server.ReadFrameAsync(cts.Token);
                    if (frame.Type == 0x04 && (frame.Flags & 0x01) != 0)
                        continue; // SETTINGS ACK
                    if (frame.Type == 0x06 && (frame.Flags & 0x01) != 0)
                    {
                        Assert.Equal(pingPayload, frame.Payload);
                        observedPingAck = true;
                        continue;
                    }
                    if (frame.Type == 0x08)
                        continue; // WINDOW_UPDATE

                    if (frame.Type == 0x01) // HEADERS
                    {
                        int off = 0;
                        bool hasPrio = (frame.Flags & 0x20) != 0;
                        if (hasPrio)
                        {
                            uint dep = BinaryPrimitives.ReadUInt32BigEndian(frame.Payload.AsSpan(0, 4));
                            byte weight = frame.Payload[4];
                            if (frame.StreamId == 1 && (dep & 0x8000_0000u) != 0 && (dep & 0x7FFF_FFFFu) == 0 && weight == 255)
                                sawFirstRequestPriority = true;
                            off = 5;
                        }
                        var ms = new MemoryStream();
                        ms.Write(frame.Payload, off, frame.Payload.Length - off);
                        openRequests[frame.StreamId] = (ms, hasPrio);
                        if ((frame.Flags & 0x04) != 0)
                        {
                            streamsSeen++;
                            await DispatchServerRequestAsync(
                                frame.StreamId,
                                ms.ToArray(),
                                h2Server,
                                serverDecoder,
                                serverEncoder,
                                pendingGoAwayKeepStreamId,
                                cts.Token);
                        }
                    }
                    else if (frame.Type == 0x09) // CONTINUATION
                    {
                        sawHeadersContinuationFromClient = true;
                        var entry = openRequests[frame.StreamId];
                        entry.HeaderBuf.Write(frame.Payload);
                        if ((frame.Flags & 0x04) != 0)
                        {
                            streamsSeen++;
                            await DispatchServerRequestAsync(
                                frame.StreamId,
                                entry.HeaderBuf.ToArray(),
                                h2Server,
                                serverDecoder,
                                serverEncoder,
                                pendingGoAwayKeepStreamId,
                                cts.Token);
                        }
                    }
                }

                await chromeClientDone.Task.WaitAsync(cts.Token);
                protocol.Close();
            }
            catch (Exception ex)
            {
                serverError = ex;
            }
        }, cts.Token);

        using var tcp = new TcpClient();
        await tcp.ConnectAsync(IPAddress.Loopback, port, cts.Token);
        await using var tls = new TlsStream(tcp.GetStream(), new TlsConnectionOptions
        {
            ServerName = TestHost,
            Port = port,
            Profile = chrome131,
            VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
        });
        await tls.HandshakeAsync(cts.Token);
        Assert.Equal("h2", tls.NegotiatedAlpn);

        ConnectionKey key = ConnectionKey.Create("https", TestHost, port, chrome131.Name);
        await using var h2 = await Http2Connection.ConnectAsync(tls, key, chrome131.Http2Settings, leaveStreamOpen: true, cts.Token);

        try
        {
            // Stream 1: large headers (36000 'a's > 16384 even after Huffman -> CONTINUATION) + large response headers + gzip
            string bigVal = new string('a', 36_000);
            PureHttpResponse resp1 = await h2.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"https://{TestHost}:{port}/gzip-large"),
                Headers = new[] { new PureHttpHeader("x-huge-client-hdr", bigVal) },
            }, cts.Token);
            Assert.Equal(200, resp1.StatusCode);
            Assert.Equal("gzip-payload-ok", Encoding.UTF8.GetString(resp1.Body));
            Assert.Equal("trail-done", resp1.Trailers.Single(t => t.Name == "x-trailer").Value);

            // Stream 3: br + 103 interim skip
            PureHttpResponse respBr = await h2.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"https://{TestHost}:{port}/br"),
            }, cts.Token);
            Assert.Equal(200, respBr.StatusCode);
            Assert.Equal("brotli-payload-ok", Encoding.UTF8.GetString(respBr.Body));

            // Stream 5: zstd
            PureHttpResponse respZstd = await h2.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"https://{TestHost}:{port}/zstd"),
            }, cts.Token);
            Assert.Equal(200, respZstd.StatusCode);
            Assert.Equal("zstd-payload-ok", Encoding.UTF8.GetString(respZstd.Body));

            // Streams 7..21 (8 multiplexed concurrent requests via Task.WhenAll!)
            Task<PureHttpResponse>[] muxTasks = Enumerable.Range(0, 8).Select(i => h2.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"https://{TestHost}:{port}/mux/{i}"),
            }, cts.Token)).ToArray();
            PureHttpResponse[] muxResponses = await Task.WhenAll(muxTasks);
            for (int i = 0; i < 8; i++)
            {
                Assert.Equal(200, muxResponses[i].StatusCode);
                Assert.Equal($"mux-{i}", Encoding.UTF8.GetString(muxResponses[i].Body));
            }

            // Stream 23: RST_STREAM fails ONLY this stream with Http2Exception(IsStreamReset=true)
            Http2Exception rstEx = await Assert.ThrowsAsync<Http2Exception>(() => h2.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"https://{TestHost}:{port}/rst"),
            }, cts.Token));
            Assert.True(rstEx.IsStreamReset);
            Assert.Equal(0x8u, rstEx.H2ErrorCode); // CANCEL

            // Connection is still usable after single-stream RST_STREAM!
            Assert.True(h2.IsUsable);

            // Stream 25 (<= LastStreamId=25) succeeds while Stream 27 (> LastStreamId=25) receives GOAWAY(25)
            Task<PureHttpResponse> okBeforeGoAway = h2.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"https://{TestHost}:{port}/goaway-keep"),
            }, cts.Token);
            Task<PureHttpResponse> rejectedByGoAway = h2.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"https://{TestHost}:{port}/goaway-drop"),
            }, cts.Token);

            PureHttpResponse kept = await okBeforeGoAway;
            Assert.Equal("kept-ok", Encoding.UTF8.GetString(kept.Body));

            Http2Exception goAwayEx = await Assert.ThrowsAsync<Http2Exception>(() => rejectedByGoAway);
            Assert.True(goAwayEx.IsRetryableOnFreshConnection);
            Assert.False(h2.IsUsable);
            Assert.False(h2.CanAcceptNewStream());

            // Subsequent SendAsync after GOAWAY also fails with retryable Http2Exception
            Http2Exception postGoAway = await Assert.ThrowsAsync<Http2Exception>(() => h2.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"https://{TestHost}:{port}/after-goaway"),
            }, cts.Token));
            Assert.True(postGoAway.IsRetryableOnFreshConnection);
        }
        finally
        {
            chromeClientDone.TrySetResult();
        }

        await serverTask;
        Assert.Null(serverError);
        Assert.True(prefaceMatched);
        Assert.Equal(chrome131.Http2Settings.Settings, observedSettings);
        Assert.Equal(15_663_105u, observedConnWindowUpdate);
        Assert.True(observedPingAck);
        Assert.True(sawHeadersContinuationFromClient);
        Assert.True(sawFirstRequestPriority);
    }

    private static async Task DispatchServerRequestAsync(
        int streamId,
        byte[] headerBlock,
        H2TestServer server,
        HpackDecoder decoder,
        HpackEncoder encoder,
        int[] pendingGoAwayKeepStreamId,
        CancellationToken ct)
    {
        List<PureHttpHeader> reqHeaders = decoder.DecodeHeaderBlock(headerBlock, validateHttp2Semantics: false);
        string path = reqHeaders.Single(h => h.Name == ":path").Value;

        if (path == "/gzip-large")
        {
            byte[] gz = ContentEncodingCodec.Compress("gzip-payload-ok"u8.ToArray(), "gzip");
            byte[] respHdr = encoder.EncodeHeaderList(new[]
            {
                new PureHttpHeader(":status", "200"),
                new PureHttpHeader("content-encoding", "gzip"),
                new PureHttpHeader("x-big-server-hdr", new string('b', 36_000)),
            }, indexLiterals: false);
            await server.WriteHeadersWithContinuationAsync(streamId, respHdr, endStream: false, maxFrameSize: 16384, ct);
            await server.WriteFrameAsync(0x00, 0x00, streamId, gz, ct);
            byte[] trl = encoder.EncodeHeaderList(new[] { new PureHttpHeader("x-trailer", "trail-done") }, indexLiterals: false);
            await server.WriteFrameAsync(0x01, 0x05, streamId, trl, ct); // END_STREAM | END_HEADERS
            return;
        }

        if (path == "/br")
        {
            byte[] interim = encoder.EncodeHeaderList(new[] { new PureHttpHeader(":status", "103") }, indexLiterals: false);
            await server.WriteFrameAsync(0x01, 0x04, streamId, interim, ct);

            byte[] brBytes;
            using (var ms = new MemoryStream())
            {
                using (var br = new BrotliStream(ms, CompressionLevel.Fastest, leaveOpen: true))
                    br.Write("brotli-payload-ok"u8);
                brBytes = ms.ToArray();
            }

            byte[] respHdr = encoder.EncodeHeaderList(new[]
            {
                new PureHttpHeader(":status", "200"),
                new PureHttpHeader("content-encoding", "br"),
            }, indexLiterals: false);
            await server.WriteFrameAsync(0x01, 0x04, streamId, respHdr, ct);
            await server.WriteFrameAsync(0x00, 0x01, streamId, brBytes, ct);
            return;
        }

        if (path == "/zstd")
        {
            byte[] zstdBytes = ContentEncodingCodec.Compress("zstd-payload-ok"u8.ToArray(), "zstd");
            byte[] respHdr = encoder.EncodeHeaderList(new[]
            {
                new PureHttpHeader(":status", "200"),
                new PureHttpHeader("content-encoding", "zstd"),
            }, indexLiterals: false);
            await server.WriteFrameAsync(0x01, 0x04, streamId, respHdr, ct);
            await server.WriteFrameAsync(0x00, 0x01, streamId, zstdBytes, ct);
            return;
        }

        if (path.StartsWith("/mux/", StringComparison.Ordinal))
        {
            string idxStr = path["/mux/".Length..];
            byte[] respHdr = encoder.EncodeHeaderList(new[] { new PureHttpHeader(":status", "200") }, indexLiterals: false);
            await server.WriteFrameAsync(0x01, 0x04, streamId, respHdr, ct);
            await server.WriteFrameAsync(0x00, 0x01, streamId, Encoding.UTF8.GetBytes($"mux-{idxStr}"), ct);
            return;
        }

        if (path == "/rst")
        {
            var rst = new byte[4];
            BinaryPrimitives.WriteUInt32BigEndian(rst, 0x8u); // CANCEL
            await server.WriteFrameAsync(0x03, 0x00, streamId, rst, ct);
            return;
        }

        if (path == "/goaway-keep")
        {
            pendingGoAwayKeepStreamId[0] = streamId;
            return;
        }

        if (path == "/goaway-drop")
        {
            int lastAccepted = pendingGoAwayKeepStreamId[0] > 0 ? pendingGoAwayKeepStreamId[0] : streamId - 2;
            var goAway = new byte[8];
            BinaryPrimitives.WriteUInt32BigEndian(goAway.AsSpan(0, 4), (uint)lastAccepted);
            BinaryPrimitives.WriteUInt32BigEndian(goAway.AsSpan(4, 4), 0u);
            await server.WriteFrameAsync(0x07, 0x00, 0, goAway, ct);

            if (pendingGoAwayKeepStreamId[0] > 0)
            {
                byte[] respHdr = encoder.EncodeHeaderList(new[] { new PureHttpHeader(":status", "200") }, indexLiterals: false);
                await server.WriteFrameAsync(0x01, 0x04, pendingGoAwayKeepStreamId[0], respHdr, ct);
                await server.WriteFrameAsync(0x00, 0x01, pendingGoAwayKeepStreamId[0], "kept-ok"u8.ToArray(), ct);
                pendingGoAwayKeepStreamId[0] = 0;
            }
        }
    }

    [Fact]
    public async Task Http2OverTls13Loopback_Firefox117_EmitsStartupPriorityFramesAndStream15WithFlowControl()
    {
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole Firefox H2 Root");
        using X509Certificate2 serverCert = CreateTestLeaf(leafKey, caCert, TestHost);

        var roots = new RootCertificateDatabase();
        roots.AddDer(caCert.RawData);

        ClientProfile firefox117 = ProfileRegistry.GetRequired("firefox_117");

        using var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        int port = ((IPEndPoint)listener.LocalEndpoint).Port;

        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        var observedPriorityFrames = new List<Http2PriorityFrame>();
        var observedSettings = new List<(ushort Id, uint Value)>();
        int firstRequestStreamId = 0;
        uint firstHeadersDep = 0;
        byte firstHeadersWeight = 0;
        string[] firstPseudoOrder = Array.Empty<string>();
        int firstDataChunkLength = 0;
        byte[]? serverReceivedBody = null;
        var ffClientDone = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        Exception? serverError = null;

        Task serverTask = Task.Run(async () =>
        {
            try
            {
                using TcpClient accepted = await listener.AcceptTcpClientAsync(cts.Token);
                using NetworkStream net = accepted.GetStream();
                var protocol = new BcTls.TlsServerProtocol(net);
                var bcServer = new BcTestTls13Server(
                    serverCert.RawData,
                    caCert.RawData,
                    leafKey.ExportPkcs8PrivateKey(),
                    BcTls.ProtocolName.Http_2_Tls);
                protocol.Accept(bcServer);

                using var tlsStream = new AsyncFriendlyBcStream(protocol.Stream);
                var h2Server = new H2TestServer(tlsStream);

                Assert.True(await h2Server.ReadAndVerifyPrefaceAsync(cts.Token));

                // SETTINGS + WINDOW_UPDATE
                var settingsFrame = await h2Server.ReadFrameAsync(cts.Token);
                Assert.Equal(0x04, settingsFrame.Type);
                for (int off = 0; off < settingsFrame.Payload.Length; off += 6)
                {
                    observedSettings.Add((
                        BinaryPrimitives.ReadUInt16BigEndian(settingsFrame.Payload.AsSpan(off, 2)),
                        BinaryPrimitives.ReadUInt32BigEndian(settingsFrame.Payload.AsSpan(off + 2, 4))));
                }
                var wuFrame = await h2Server.ReadFrameAsync(cts.Token);
                Assert.Equal(0x08, wuFrame.Type);
                Assert.Equal(12_517_377u, BinaryPrimitives.ReadUInt32BigEndian(wuFrame.Payload));

                // 6 startup PRIORITY frames for Firefox_117
                for (int i = 0; i < 6; i++)
                {
                    var pf = await h2Server.ReadFrameAsync(cts.Token);
                    Assert.Equal(0x02, pf.Type);
                    uint rawDep = BinaryPrimitives.ReadUInt32BigEndian(pf.Payload.AsSpan(0, 4));
                    observedPriorityFrames.Add(new Http2PriorityFrame(
                        (uint)pf.StreamId,
                        rawDep & 0x7FFF_FFFFu,
                        (rawDep & 0x8000_0000u) != 0,
                        pf.Payload[4]));
                }

                // Advertise small peer InitialWindowSize = 1024 before answering stream 15 (/init).
                await h2Server.WriteSettingsAsync(new (ushort, uint)[] { (4, 1024) }, cts.Token);

                var dec = new HpackDecoder();
                var enc = new HpackEncoder();
                var rxBody = new MemoryStream();
                int uploadStreamId = 0;
                bool done = false;
                while (!done)
                {
                    var f = await h2Server.ReadFrameAsync(cts.Token);
                    if (f.Type == 0x04 && (f.Flags & 0x01) != 0)
                        continue;

                    if (f.Type == 0x01)
                    {
                        uint dep = BinaryPrimitives.ReadUInt32BigEndian(f.Payload.AsSpan(0, 4));
                        byte weight = f.Payload[4];
                        List<PureHttpHeader> decoded = dec.DecodeHeaderBlock(f.Payload.AsSpan(5), validateHttp2Semantics: false);
                        if (firstRequestStreamId == 0)
                        {
                            firstRequestStreamId = f.StreamId;
                            firstHeadersDep = dep;
                            firstHeadersWeight = weight;
                            firstPseudoOrder = decoded.Take(4).Select(h => h.Name).ToArray();

                            byte[] initHdr = enc.EncodeHeaderList(new[] { new PureHttpHeader(":status", "200") }, indexLiterals: false);
                            await h2Server.WriteFrameAsync(0x01, 0x04, f.StreamId, initHdr, cts.Token);
                            await h2Server.WriteFrameAsync(0x00, 0x01, f.StreamId, "init-ok"u8.ToArray(), cts.Token);
                        }
                        else
                        {
                            uploadStreamId = f.StreamId;
                        }
                    }
                    else if (f.Type == 0x00)
                    {
                        if (firstDataChunkLength == 0)
                            firstDataChunkLength = f.Payload.Length;
                        rxBody.Write(f.Payload);

                        // Grant flow-control window after first chunk so remaining body arrives.
                        if ((f.Flags & 0x01) == 0)
                        {
                            var wu = new byte[4];
                            BinaryPrimitives.WriteUInt32BigEndian(wu, 4096u);
                            await h2Server.WriteFrameAsync(0x08, 0x00, f.StreamId, wu, cts.Token);
                        }
                        else
                        {
                            done = true;
                        }
                    }
                }

                serverReceivedBody = rxBody.ToArray();
                byte[] respHdr = enc.EncodeHeaderList(new[] { new PureHttpHeader(":status", "200") }, indexLiterals: false);
                await h2Server.WriteFrameAsync(0x01, 0x04, uploadStreamId, respHdr, cts.Token);
                await h2Server.WriteFrameAsync(0x00, 0x01, uploadStreamId, "upload-ok"u8.ToArray(), cts.Token);
                await ffClientDone.Task.WaitAsync(cts.Token);
                protocol.Close();
            }
            catch (Exception ex)
            {
                serverError = ex;
            }
        }, cts.Token);

        using var tcp = new TcpClient();
        await tcp.ConnectAsync(IPAddress.Loopback, port, cts.Token);
        await using var tls = new TlsStream(tcp.GetStream(), new TlsConnectionOptions
        {
            ServerName = TestHost,
            Port = port,
            Profile = firefox117,
            VerifyOptions = new CertificateVerifyOptions { CustomRoots = roots, UseEmbeddedDefaultRoots = false },
        });
        await tls.HandshakeAsync(cts.Token);

        byte[] payload = CreatePatternPayload(4096);
        ConnectionKey key = ConnectionKey.Create("https", TestHost, port, firefox117.Name);
        await using var h2 = await Http2Connection.ConnectAsync(tls, key, firefox117.Http2Settings, leaveStreamOpen: true, cts.Token);

        try
        {
            PureHttpResponse initResp = await h2.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"https://{TestHost}:{port}/init"),
            }, cts.Token);
            Assert.Equal(200, initResp.StatusCode);
            Assert.Equal("init-ok", Encoding.UTF8.GetString(initResp.Body));

            PureHttpResponse resp = await h2.SendAsync(new PureHttpRequest
            {
                Method = "POST",
                Uri = new Uri($"https://{TestHost}:{port}/upload"),
                Body = payload,
            }, cts.Token);

            Assert.Equal(200, resp.StatusCode);
            Assert.Equal("upload-ok", Encoding.UTF8.GetString(resp.Body));
        }
        finally
        {
            ffClientDone.TrySetResult();
        }

        await serverTask;
        Assert.Null(serverError);
        Assert.Equal(firefox117.Http2Settings.Settings, observedSettings);
        Assert.Equal(firefox117.Http2Settings.PriorityFrames, observedPriorityFrames);
        Assert.Equal(15, firstRequestStreamId);
        Assert.Equal(13u, firstHeadersDep & 0x7FFF_FFFFu);
        Assert.Equal(0u, firstHeadersDep & 0x8000_0000u);
        Assert.Equal((byte)41, firstHeadersWeight);
        Assert.Equal(new[] { ":method", ":path", ":authority", ":scheme" }, firstPseudoOrder);
        Assert.Equal(1024, firstDataChunkLength);
        Assert.Equal(payload, serverReceivedBody);
    }

    // ---- 4. HTTP/1.1 Loopback Tests ----

    [Fact]
    public async Task Http1Loopback_KeepAliveReuseChunkedTrailers100ContinueCloseAndErrors()
    {
        using var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        int port = ((IPEndPoint)listener.LocalEndpoint).Port;
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));

        var capturedReqHeaders = new List<string>();
        var h1Conn1Done = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);

        Task serverTask = Task.Run(async () =>
        {
            // Connection 1: 4 keep-alive requests (GET, chunked+trailers, 100-continue POST, HEAD)
            using (TcpClient c1 = await listener.AcceptTcpClientAsync(cts.Token))
            await using (NetworkStream s1 = c1.GetStream())
            {
                var r1 = new BufferedStreamReader(s1, leaveOpen: true);

                // Req 1: GET -> 200 Content-Length + duplicate Set-Cookie + Alt-Svc
                capturedReqHeaders.Add(await ReadHttp1HeadTextAsync(r1, cts.Token));
                byte[] body1 = "first-ok"u8.ToArray();
                await s1.WriteAsync(Encoding.ASCII.GetBytes(
                    $"HTTP/1.1 200 OK\r\nContent-Length: {body1.Length}\r\nSet-Cookie: a=1\r\nSet-Cookie: b=2\r\nAlt-Svc: h3=\":443\"\r\n\r\n"), cts.Token);
                await s1.WriteAsync(body1, cts.Token);

                // Req 2: GET -> Chunked + extension + trailers
                capturedReqHeaders.Add(await ReadHttp1HeadTextAsync(r1, cts.Token));
                await s1.WriteAsync(Encoding.ASCII.GetBytes(
                    "HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n" +
                    "5;ext=1\r\nhello\r\n" +
                    "6\r\n world\r\n" +
                    "0\r\nX-Trailer: chunk-end\r\n\r\n"), cts.Token);

                // Req 3: Expect: 100-continue POST -> 100 Continue -> read body -> 200
                string req3Head = await ReadHttp1HeadTextAsync(r1, cts.Token);
                capturedReqHeaders.Add(req3Head);
                await s1.WriteAsync("HTTP/1.1 100 Continue\r\n\r\n"u8.ToArray(), cts.Token);
                await s1.FlushAsync(cts.Token);

                var postBuf = new byte[9];
                await r1.ReadExactAsync(postBuf, cts.Token);
                Assert.Equal("post-data", Encoding.ASCII.GetString(postBuf));
                await s1.WriteAsync("HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\ndone"u8.ToArray(), cts.Token);
                await s1.FlushAsync(cts.Token);

                // Req 4: HEAD with non-zero Content-Length (must NOT wait for body)
                capturedReqHeaders.Add(await ReadHttp1HeadTextAsync(r1, cts.Token));
                await s1.WriteAsync("HTTP/1.1 200 OK\r\nContent-Length: 99999\r\n\r\n"u8.ToArray(), cts.Token);
                await s1.FlushAsync(cts.Token);
                await h1Conn1Done.Task.WaitAsync(cts.Token);
            }

            // Connection 2: close-delimited body (no Content-Length) + Connection: close
            using (TcpClient c2 = await listener.AcceptTcpClientAsync(cts.Token))
            await using (NetworkStream s2 = c2.GetStream())
            {
                var r2 = new BufferedStreamReader(s2, leaveOpen: true);
                _ = await ReadHttp1HeadTextAsync(r2, cts.Token);
                await s2.WriteAsync("HTTP/1.1 200 OK\r\nConnection: close\r\n\r\nclose-delimited-body"u8.ToArray(), cts.Token);
                await s2.FlushAsync(cts.Token);
            }

            // Connection 3: exceeds MaxResponseBodyBytes
            using (TcpClient c3 = await listener.AcceptTcpClientAsync(cts.Token))
            await using (NetworkStream s3 = c3.GetStream())
            {
                var r3 = new BufferedStreamReader(s3, leaveOpen: true);
                _ = await ReadHttp1HeadTextAsync(r3, cts.Token);
                await s3.WriteAsync("HTTP/1.1 200 OK\r\nContent-Length: 1024\r\n\r\n"u8.ToArray(), cts.Token);
                await s3.FlushAsync(cts.Token);
            }

            // Connection 4: premature EOF during Content-Length
            using (TcpClient c4 = await listener.AcceptTcpClientAsync(cts.Token))
            await using (NetworkStream s4 = c4.GetStream())
            {
                var r4 = new BufferedStreamReader(s4, leaveOpen: true);
                _ = await ReadHttp1HeadTextAsync(r4, cts.Token);
                await s4.WriteAsync("HTTP/1.1 200 OK\r\nContent-Length: 20\r\n\r\nshort"u8.ToArray(), cts.Token);
                await s4.FlushAsync(cts.Token);
            }
        }, cts.Token);

        ConnectionKey key = ConnectionKey.Create("http", "127.0.0.1", port, "chrome_131", forceHttp11: true);

        // Connection 1: reused requests
        using (var tcp1 = new TcpClient())
        {
            await tcp1.ConnectAsync(IPAddress.Loopback, port, cts.Token);
            await using var h1 = new Http1Connection(tcp1.GetStream(), key, new[] { "User-Agent", "Accept" });
            Assert.False(h1.SupportsMultiplexing);
            Assert.Equal(1, h1.MaxConcurrentStreams);

            try
            {
                PureHttpResponse r1 = await h1.SendAsync(new PureHttpRequest
                {
                    Method = "GET",
                    Uri = new Uri($"http://127.0.0.1:{port}/one"),
                    Headers = new[] { new PureHttpHeader("Accept", "text/plain"), new PureHttpHeader("User-Agent", "TestH1/1.0") },
                }, cts.Token);
                Assert.Equal(200, r1.StatusCode);
                Assert.Equal("first-ok", Encoding.UTF8.GetString(r1.Body));
                Assert.Equal(new[] { "a=1", "b=2" }, r1.GetHeaderValues("Set-Cookie").ToArray());
                Assert.Equal("h3=\":443\"", r1.AltSvcHeader);
                Assert.True(h1.IsUsable);

                PureHttpResponse r2 = await h1.SendAsync(new PureHttpRequest
                {
                    Method = "GET",
                    Uri = new Uri($"http://127.0.0.1:{port}/two"),
                }, cts.Token);
                Assert.Equal("hello world", Encoding.UTF8.GetString(r2.Body));
                Assert.Equal("chunk-end", r2.Trailers.Single(t => t.Name == "X-Trailer").Value);
                Assert.True(h1.IsUsable);

                PureHttpResponse r3 = await h1.SendAsync(new PureHttpRequest
                {
                    Method = "POST",
                    Uri = new Uri($"http://127.0.0.1:{port}/three"),
                    Headers = new[] { new PureHttpHeader("Expect", "100-continue") },
                    Body = "post-data"u8.ToArray(),
                }, cts.Token);
                Assert.Equal("done", Encoding.UTF8.GetString(r3.Body));
                Assert.True(h1.IsUsable);

                PureHttpResponse r4 = await h1.SendAsync(new PureHttpRequest
                {
                    Method = "HEAD",
                    Uri = new Uri($"http://127.0.0.1:{port}/head"),
                }, cts.Token);
                Assert.Equal(200, r4.StatusCode);
                Assert.Empty(r4.Body);
                Assert.True(h1.IsUsable);
            }
            finally
            {
                h1Conn1Done.TrySetResult();
            }
        }

        // Verify Host first and HeaderOrder honored on req 1
        Assert.Contains($"Host: 127.0.0.1:{port}\r\nUser-Agent: TestH1/1.0\r\nAccept: text/plain\r\n", capturedReqHeaders[0], StringComparison.Ordinal);

        // Connection 2: close-delimited marks IsUsable = false
        using (var tcp2 = new TcpClient())
        {
            await tcp2.ConnectAsync(IPAddress.Loopback, port, cts.Token);
            await using var h1Close = new Http1Connection(tcp2.GetStream(), key);
            PureHttpResponse rClose = await h1Close.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"http://127.0.0.1:{port}/close"),
            }, cts.Token);
            Assert.Equal("close-delimited-body", Encoding.UTF8.GetString(rClose.Body));
            Assert.False(h1Close.IsUsable);
        }

        // Connection 3: MaxResponseBodyBytes overflow
        using (var tcp3 = new TcpClient())
        {
            await tcp3.ConnectAsync(IPAddress.Loopback, port, cts.Token);
            await using var h1Big = new Http1Connection(tcp3.GetStream(), key);
            PureHttpException tooBig = await Assert.ThrowsAsync<PureHttpException>(() => h1Big.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"http://127.0.0.1:{port}/too-big"),
                MaxResponseBodyBytes = 128,
            }, cts.Token));
            Assert.Equal(HttpErrorKind.ResponseTooLarge, tooBig.ErrorKind);
        }

        // Connection 4: premature EOF on Content-Length -> EndOfStreamException -> TransportIo
        using (var tcp4 = new TcpClient())
        {
            await tcp4.ConnectAsync(IPAddress.Loopback, port, cts.Token);
            await using var h1Eof = new Http1Connection(tcp4.GetStream(), key);
            EndOfStreamException eofEx = await Assert.ThrowsAsync<EndOfStreamException>(() => h1Eof.SendAsync(new PureHttpRequest
            {
                Method = "GET",
                Uri = new Uri($"http://127.0.0.1:{port}/eof"),
            }, cts.Token));
            Assert.Equal(HttpErrorKind.TransportIo, HttpErrorClassifier.Classify(eofEx));
            Assert.False(h1Eof.IsUsable);
        }

        await serverTask;
    }

    // ---- 5. Dialers: DnsCache, DirectDialer (Happy Eyeballs), ProxyUriParser, HttpConnectDialer (http+https), Socks5Dialer ----

    [Fact]
    public async Task DnsCacheAndDirectDialer_LruEvictionIpLiteralBypassAndHappyEyeballsFallback()
    {
        int resolverCalls = 0;
        var dnsCache = new DnsCache(
            DnsCache.DefaultMaxCapacity,
            TimeSpan.FromSeconds(30),
            (host, _) =>
            {
                Interlocked.Increment(ref resolverCalls);
                return Task.FromResult(new[] { IPAddress.IPv6Loopback, IPAddress.Loopback });
            });

        Assert.Equal(4096, dnsCache.MaxCapacity);

        // IP literals bypass DNS resolver completely
        IPAddress[] lit4 = await dnsCache.ResolveAsync("127.0.0.1");
        IPAddress[] lit6 = await dnsCache.ResolveAsync("[::1]");
        Assert.Equal(new[] { IPAddress.Loopback }, lit4);
        Assert.Equal(new[] { IPAddress.IPv6Loopback }, lit6);
        Assert.Equal(0, resolverCalls);

        // Fill 4096 entries, touch host-0, add host-4096 -> host-1 evicted, host-0 retained, Count == 4096
        for (int i = 0; i < 4096; i++)
            await dnsCache.ResolveAsync($"host-{i}.example.test");
        Assert.Equal(4096, dnsCache.Count);
        Assert.Equal(4096, resolverCalls);

        await dnsCache.ResolveAsync("host-0.example.test"); // LRU touch
        Assert.Equal(4096, resolverCalls);

        await dnsCache.ResolveAsync("host-4096.example.test"); // triggers eviction of host-1
        Assert.Equal(4096, dnsCache.Count);
        Assert.Equal(4097, resolverCalls);

        await dnsCache.ResolveAsync("host-0.example.test"); // still cached!
        Assert.Equal(4097, resolverCalls);
        await dnsCache.ResolveAsync("host-1.example.test"); // was evicted -> triggers re-resolve
        Assert.Equal(4098, resolverCalls);

        // TTL expiry test
        var shortTtlCache = new DnsCache(16, TimeSpan.FromMilliseconds(40), (_, _) =>
        {
            Interlocked.Increment(ref resolverCalls);
            return Task.FromResult(new[] { IPAddress.Loopback });
        });
        await shortTtlCache.ResolveAsync("ttl.example.test");
        int countAfterFirst = resolverCalls;
        await Task.Delay(80);
        await shortTtlCache.ResolveAsync("ttl.example.test");
        Assert.Equal(countAfterFirst + 1, resolverCalls);

        // DirectDialer Happy Eyeballs 300ms fallback: IPv4 listener on 127.0.0.1 while ::1 is unbound
        using var v4Listener = new TcpListener(IPAddress.Loopback, 0);
        v4Listener.Start();
        int port = ((IPEndPoint)v4Listener.LocalEndpoint).Port;

        var dialDns = new DnsCache(16, TimeSpan.FromSeconds(30), (_, _) =>
            Task.FromResult(new[] { IPAddress.IPv6Loopback, IPAddress.Loopback }));
        var dialer = new DirectDialer(dialDns);
        Assert.Equal(TimeSpan.FromMilliseconds(300), dialer.HappyEyeballsDelay);
        Assert.Equal(TimeSpan.FromSeconds(30), dialer.ConnectTimeout);

        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(10));
        Task<TcpClient> acceptTask = v4Listener.AcceptTcpClientAsync(cts.Token).AsTask();
        await using DialedConnection conn = await dialer.DialAsync("dual.example.test", port, cts.Token);
        using TcpClient accepted = await acceptTask;

        Assert.False(conn.IsProxied);
        Assert.NotNull(conn.RemoteEndPoint);
        Assert.Equal(AddressFamily.InterNetwork, conn.RemoteEndPoint!.AddressFamily);
        Assert.True(((NetworkStream)conn.Stream).Socket.NoDelay);
    }

    [Fact]
    public async Task ProxyUriParser_HttpConnectDialerHttpAndHttps_AndSocks5Dialer_WorkAndReportExactErrors()
    {
        // ProxyUriParser coverage
        ProxySpec pHttp = ProxyUriParser.Parse("http://user%401:p%3Ass@proxy.local:8080");
        Assert.Equal(ProxyProtocolKind.Http, pHttp.Kind);
        Assert.Equal("proxy.local", pHttp.Host);
        Assert.Equal(8080, pHttp.Port);
        Assert.Equal("user@1", pHttp.Username);
        Assert.Equal("p:ss", pHttp.Password);

        ProxySpec pHttps = ProxyUriParser.Parse("https://tls-proxy.local");
        Assert.Equal(ProxyProtocolKind.Https, pHttps.Kind);
        Assert.Equal(443, pHttps.Port);

        ProxySpec pSocks5 = ProxyUriParser.Parse("socks5://s5.local");
        Assert.Equal(ProxyProtocolKind.Socks5, pSocks5.Kind);
        Assert.Equal(1080, pSocks5.Port);
        Assert.False(pSocks5.RemoteDns);

        ProxySpec pSocks5h = ProxyUriParser.Parse("socks5h://u:pw@[::1]:1085");
        Assert.Equal(ProxyProtocolKind.Socks5, pSocks5h.Kind);
        Assert.Equal("::1", pSocks5h.Host);
        Assert.Equal(1085, pSocks5h.Port);
        Assert.True(pSocks5h.RemoteDns);

        ProxySpec pShort = ProxyUriParser.Parse("127.0.0.1:8888:alice:secret");
        Assert.Equal(ProxyProtocolKind.Http, pShort.Kind);
        Assert.Equal("127.0.0.1", pShort.Host);
        Assert.Equal(8888, pShort.Port);
        Assert.Equal("alice", pShort.Username);
        Assert.Equal("secret", pShort.Password);

        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        var dialer = new ConnectionDialer();

        // 1) HTTP CONNECT proxy with coalesced trailing bytes preserved by BufferedStreamReader + 407 failure
        using (var httpProxyListener = new TcpListener(IPAddress.Loopback, 0))
        {
            httpProxyListener.Start();
            int pPort = ((IPEndPoint)httpProxyListener.LocalEndpoint).Port;
            string? capturedConnect = null;

            Task proxySrv = Task.Run(async () =>
            {
                // Request 1: 200 OK with immediate coalesced backend bytes in the same packet!
                using (TcpClient c = await httpProxyListener.AcceptTcpClientAsync(cts.Token))
                await using (NetworkStream s = c.GetStream())
                {
                    var r = new BufferedStreamReader(s, leaveOpen: true);
                    capturedConnect = await ReadHttp1HeadTextAsync(r, cts.Token);
                    await s.WriteAsync(
                        "HTTP/1.1 200 Connection Established\r\nProxy-Agent: test\r\n\r\nCOALESCED-HELLO"u8.ToArray(),
                        cts.Token);
                    await s.FlushAsync(cts.Token);

                    var echo = new byte[4];
                    await r.ReadExactAsync(echo, cts.Token);
                    Assert.Equal("PING", Encoding.ASCII.GetString(echo));
                }

                // Request 2: 407 Proxy Authentication Required
                using (TcpClient c407 = await httpProxyListener.AcceptTcpClientAsync(cts.Token))
                await using (NetworkStream s407 = c407.GetStream())
                {
                    var r407 = new BufferedStreamReader(s407, leaveOpen: true);
                    _ = await ReadHttp1HeadTextAsync(r407, cts.Token);
                    await s407.WriteAsync("HTTP/1.1 407 Proxy Authentication Required\r\n\r\n"u8.ToArray(), cts.Token);
                    await s407.FlushAsync(cts.Token);
                }
            }, cts.Token);

            var httpProxySpec = new ProxySpec(ProxyProtocolKind.Http, "127.0.0.1", pPort, "alice", "secret");
            await using (DialedConnection tunneled = await dialer.DialAsync("target.example.com", 443, httpProxySpec, cancellationToken: cts.Token))
            {
                Assert.True(tunneled.IsProxied);
                var rx = new byte[15];
                int n = await tunneled.Stream.ReadAsync(rx, cts.Token);
                Assert.Equal("COALESCED-HELLO", Encoding.ASCII.GetString(rx, 0, n));
                await tunneled.Stream.WriteAsync("PING"u8.ToArray(), cts.Token);
                await tunneled.Stream.FlushAsync(cts.Token);
            }

            Assert.Contains("CONNECT target.example.com:443 HTTP/1.1\r\n", capturedConnect!, StringComparison.Ordinal);
            string expectedBasic = Convert.ToBase64String(Encoding.UTF8.GetBytes("alice:secret"));
            Assert.Contains($"Proxy-Authorization: Basic {expectedBasic}\r\n", capturedConnect!, StringComparison.Ordinal);

            ProxyException ex407 = await Assert.ThrowsAsync<ProxyException>(() =>
                dialer.DialAsync("target.example.com", 443, httpProxySpec, cancellationToken: cts.Token));
            Assert.Equal(407, ex407.ProxyStatusCode);
            Assert.Equal(HttpErrorKind.Proxy, ex407.ErrorKind);

            await proxySrv;
        }

        // 2) HTTPS CONNECT proxy using ProxyTlsSpec + TlsStream!
        using var caKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
        using X509Certificate2 caCert = CreateTestCa(caKey, "CN=Cybersole HTTPS Proxy Root");
        using X509Certificate2 proxyCert = CreateTestLeaf(leafKey, caCert, TestHost);
        var proxyRoots = new RootCertificateDatabase();
        proxyRoots.AddDer(caCert.RawData);

        using (var httpsProxyListener = new TcpListener(IPAddress.Loopback, 0))
        {
            httpsProxyListener.Start();
            int hpPort = ((IPEndPoint)httpsProxyListener.LocalEndpoint).Port;
            var httpsClientDone = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);

            Task httpsProxySrv = Task.Run(async () =>
            {
                using TcpClient c = await httpsProxyListener.AcceptTcpClientAsync(cts.Token);
                using NetworkStream net = c.GetStream();
                var protocol = new BcTls.TlsServerProtocol(net);
                var bcServer = new BcTestTls13Server(
                    proxyCert.RawData,
                    caCert.RawData,
                    leafKey.ExportPkcs8PrivateKey(),
                    BcTls.ProtocolName.Http_1_1);
                protocol.Accept(bcServer);

                using var tlsProxyStream = new AsyncFriendlyBcStream(protocol.Stream);
                var r = new BufferedStreamReader(tlsProxyStream, leaveOpen: true);
                string connectReq = await ReadHttp1HeadTextAsync(r, cts.Token);
                Assert.StartsWith("CONNECT origin.example.com:8443 HTTP/1.1", connectReq, StringComparison.Ordinal);

                await tlsProxyStream.WriteAsync("HTTP/1.1 200 Connection Established\r\n\r\n"u8.ToArray(), cts.Token);
                var payload = new byte[9];
                await r.ReadExactAsync(payload, cts.Token);
                Assert.Equal("TLS-PROXY", Encoding.ASCII.GetString(payload));
                await tlsProxyStream.WriteAsync("TUNNEL-OK"u8.ToArray(), cts.Token);
                await httpsClientDone.Task.WaitAsync(cts.Token);
                protocol.Close();
            }, cts.Token);

            var httpsProxySpec = new ProxySpec(ProxyProtocolKind.Https, TestHost, hpPort);
            var verifyOpts = new CertificateVerifyOptions { CustomRoots = proxyRoots, UseEmbeddedDefaultRoots = false };
            try
            {
                await using DialedConnection tunneled = await dialer.DialAsync("origin.example.com", 8443, httpsProxySpec, verifyOpts, cancellationToken: cts.Token);
                await tunneled.Stream.WriteAsync("TLS-PROXY"u8.ToArray(), cts.Token);
                await tunneled.Stream.FlushAsync(cts.Token);
                var reply = new byte[9];
                int rLen = 0;
                while (rLen < 9)
                    rLen += await tunneled.Stream.ReadAsync(reply.AsMemory(rLen, 9 - rLen), cts.Token);
                Assert.Equal("TUNNEL-OK", Encoding.ASCII.GetString(reply));
            }
            finally
            {
                httpsClientDone.TrySetResult();
            }
            await httpsProxySrv;
        }

        // 3) SOCKS5 Dialer: NoAuth + RemoteDns (0x03), Username/Password (RFC 1929) + LocalDns (0x01), and RFC 1928 reply error
        using (var socksListener = new TcpListener(IPAddress.Loopback, 0))
        {
            socksListener.Start();
            int sPort = ((IPEndPoint)socksListener.LocalEndpoint).Port;
            var s5Conn1Done = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
            var s5Conn2Done = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
            var s5Conn3Done = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);

            Task socksSrv = Task.Run(async () =>
            {
                // Conn A: NoAuth + RemoteDns (ATYP=0x03)
                using (TcpClient c1 = await socksListener.AcceptTcpClientAsync(cts.Token))
                await using (NetworkStream s1 = c1.GetStream())
                {
                    var g = new byte[3];
                    await ReadExactlyAsync(s1, g, cts.Token);
                    Assert.Equal(new byte[] { 0x05, 0x01, 0x00 }, g);
                    await s1.WriteAsync(new byte[] { 0x05, 0x00 }, cts.Token);

                    var head = new byte[5];
                    await ReadExactlyAsync(s1, head, cts.Token);
                    Assert.Equal(0x05, head[0]);
                    Assert.Equal(0x01, head[1]);
                    Assert.Equal(0x03, head[3]); // RemoteDns domain name
                    var dom = new byte[head[4] + 2];
                    await ReadExactlyAsync(s1, dom, cts.Token);
                    Assert.Equal("remote.example.com", Encoding.ASCII.GetString(dom, 0, head[4]));
                    Assert.Equal(443, (dom[head[4]] << 8) | dom[head[4] + 1]);

                    await s1.WriteAsync(new byte[] { 0x05, 0x00, 0x00, 0x01, 127, 0, 0, 1, 0x01, 0xBB }, cts.Token);
                    var ping = new byte[2];
                    await ReadExactlyAsync(s1, ping, cts.Token);
                    await s1.WriteAsync("OK"u8.ToArray(), cts.Token);
                    await s5Conn1Done.Task.WaitAsync(cts.Token);
                }

                // Conn B: RFC 1929 Username/Password + LocalDns (ATYP=0x01 IPv4)
                using (TcpClient c2 = await socksListener.AcceptTcpClientAsync(cts.Token))
                await using (NetworkStream s2 = c2.GetStream())
                {
                    var g = new byte[4];
                    await ReadExactlyAsync(s2, g, cts.Token);
                    Assert.Equal(new byte[] { 0x05, 0x02, 0x00, 0x02 }, g);
                    await s2.WriteAsync(new byte[] { 0x05, 0x02 }, cts.Token);

                    var authHead = new byte[2];
                    await ReadExactlyAsync(s2, authHead, cts.Token);
                    Assert.Equal(0x01, authHead[0]);
                    var user = new byte[authHead[1]];
                    await ReadExactlyAsync(s2, user, cts.Token);
                    var passLen = new byte[1];
                    await ReadExactlyAsync(s2, passLen, cts.Token);
                    var pass = new byte[passLen[0]];
                    await ReadExactlyAsync(s2, pass, cts.Token);
                    Assert.Equal("bob", Encoding.UTF8.GetString(user));
                    Assert.Equal("hunter2", Encoding.UTF8.GetString(pass));
                    await s2.WriteAsync(new byte[] { 0x01, 0x00 }, cts.Token);

                    var req = new byte[10];
                    await ReadExactlyAsync(s2, req, cts.Token);
                    Assert.Equal(0x01, req[3]); // LocalDns resolved IPv4
                    Assert.Equal(new byte[] { 127, 0, 0, 1 }, req[4..8]);
                    await s2.WriteAsync(new byte[] { 0x05, 0x00, 0x00, 0x01, 127, 0, 0, 1, 0x00, 0x50 }, cts.Token);
                    await s5Conn2Done.Task.WaitAsync(cts.Token);
                }

                // Conn C: RFC 1928 Reply Error 0x05 (Connection refused)
                using (TcpClient c3 = await socksListener.AcceptTcpClientAsync(cts.Token))
                await using (NetworkStream s3 = c3.GetStream())
                {
                    var g = new byte[3];
                    await ReadExactlyAsync(s3, g, cts.Token);
                    await s3.WriteAsync(new byte[] { 0x05, 0x00 }, cts.Token);
                    var reqHead = new byte[5];
                    await ReadExactlyAsync(s3, reqHead, cts.Token);
                    var rest = new byte[reqHead[4] + 2];
                    await ReadExactlyAsync(s3, rest, cts.Token);
                    await s3.WriteAsync(new byte[] { 0x05, 0x05, 0x00, 0x01, 0, 0, 0, 0, 0, 0 }, cts.Token);
                    await s5Conn3Done.Task.WaitAsync(cts.Token);
                }
            }, cts.Token);

            var s5Remote = new ProxySpec(ProxyProtocolKind.Socks5, "127.0.0.1", sPort, RemoteDns: true);
            try
            {
                await using (DialedConnection c1 = await dialer.DialAsync("remote.example.com", 443, s5Remote, cancellationToken: cts.Token))
                {
                    await c1.Stream.WriteAsync("HI"u8.ToArray(), cts.Token);
                    var ok = new byte[2];
                    await ReadExactlyAsync(c1.Stream, ok, cts.Token);
                    Assert.Equal("OK", Encoding.ASCII.GetString(ok));
                }
            }
            finally
            {
                s5Conn1Done.TrySetResult();
            }

            var customDns = new DnsCache(16, TimeSpan.FromSeconds(30), (_, _) => Task.FromResult(new[] { IPAddress.Loopback }));
            var s5DialerLocal = new Socks5Dialer(new DirectDialer(customDns), customDns);
            var s5AuthLocal = new ProxySpec(ProxyProtocolKind.Socks5, "127.0.0.1", sPort, "bob", "hunter2", RemoteDns: false);
            try
            {
                await using (DialedConnection c2 = await s5DialerLocal.DialAsync(s5AuthLocal, "local-resolved.example.test", 80, cancellationToken: cts.Token))
                {
                    Assert.True(c2.IsProxied);
                }
            }
            finally
            {
                s5Conn2Done.TrySetResult();
            }

            try
            {
                ProxyException refusedEx = await Assert.ThrowsAsync<ProxyException>(() =>
                    dialer.DialAsync("blocked.example.com", 443, s5Remote, cancellationToken: cts.Token));
                Assert.Equal(5, refusedEx.ProxyStatusCode);
                Assert.Contains("Connection refused", refusedEx.Message, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                s5Conn3Done.TrySetResult();
            }

            await socksSrv;
        }
    }

    // ---- Test Infrastructure Helpers ----

    private sealed class H2TestServer
    {
        private readonly Stream _stream;

        public H2TestServer(Stream stream) => _stream = stream;

        public async Task<bool> ReadAndVerifyPrefaceAsync(CancellationToken ct)
        {
            var buf = new byte[24];
            await ReadExactlyAsync(_stream, buf, ct);
            return Encoding.ASCII.GetString(buf) == "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n";
        }

        public async Task<(byte Type, byte Flags, int StreamId, byte[] Payload)> ReadFrameAsync(CancellationToken ct)
        {
            var hdr = new byte[9];
            await ReadExactlyAsync(_stream, hdr, ct);
            int len = (hdr[0] << 16) | (hdr[1] << 8) | hdr[2];
            var payload = len > 0 ? new byte[len] : Array.Empty<byte>();
            if (len > 0)
                await ReadExactlyAsync(_stream, payload, ct);
            int streamId = BinaryPrimitives.ReadInt32BigEndian(hdr.AsSpan(5, 4)) & 0x7FFF_FFFF;
            return (hdr[3], hdr[4], streamId, payload);
        }

        public Task WriteFrameAsync(byte type, byte flags, int streamId, ReadOnlySpan<byte> payload, CancellationToken ct)
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
                payload.CopyTo(frame.AsSpan(9));
            return WriteAndFlushAsync(frame, ct);
        }

        private async Task WriteAndFlushAsync(byte[] frame, CancellationToken ct)
        {
            await _stream.WriteAsync(frame, ct);
            await _stream.FlushAsync(ct);
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

        public Task WriteSettingsAckAsync(CancellationToken ct) =>
            WriteFrameAsync(0x04, 0x01, 0, ReadOnlySpan<byte>.Empty, ct);

        public async Task WriteHeadersWithContinuationAsync(
            int streamId,
            byte[] headerBlock,
            bool endStream,
            int maxFrameSize,
            CancellationToken ct)
        {
            int first = Math.Min(headerBlock.Length, maxFrameSize);
            bool single = first == headerBlock.Length;
            byte flags = (byte)((endStream ? 0x01 : 0x00) | (single ? 0x04 : 0x00));
            await WriteFrameAsync(0x01, flags, streamId, headerBlock.AsSpan(0, first), ct);

            int off = first;
            while (off < headerBlock.Length)
            {
                int chunk = Math.Min(headerBlock.Length - off, maxFrameSize);
                bool last = off + chunk == headerBlock.Length;
                await WriteFrameAsync(0x09, last ? (byte)0x04 : (byte)0x00, streamId, headerBlock.AsSpan(off, chunk), ct);
                off += chunk;
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

    private static async Task<string> ReadHttp1HeadTextAsync(BufferedStreamReader reader, CancellationToken ct)
    {
        var sb = new StringBuilder();
        while (true)
        {
            string? line = await reader.ReadLineAsciiAsync(64 * 1024, ct);
            if (line is null)
                throw new EndOfStreamException();
            sb.Append(line).Append("\r\n");
            if (line.Length == 0)
                return sb.ToString();
        }
    }

    private static async Task ReadExactlyAsync(Stream stream, byte[] buffer, CancellationToken ct)
    {
        int off = 0;
        while (off < buffer.Length)
        {
            int n = await stream.ReadAsync(buffer.AsMemory(off, buffer.Length - off), ct);
            if (n == 0)
                throw new EndOfStreamException();
            off += n;
        }
    }

    private static byte[] CreatePatternPayload(int length)
    {
        var data = new byte[length];
        for (int i = 0; i < data.Length; i++)
            data[i] = (byte)((i * 31 + 17) & 0xFF);
        return data;
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
        req.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.DigitalSignature, true));
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
