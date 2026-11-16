using System.Buffers.Binary;
using System.Security.Cryptography;

namespace Cybersole.Http;

/// <summary>
/// A TLS 1.2 client built on the hand-crafted ClientHello from <see cref="Ja3"/>.
/// Completes the full handshake (ClientKeyExchange → CCS → Finished → server Finished)
/// and provides an AES-GCM record layer, so requests no longer depend on SChannel
/// or BouncyCastle's ClientHello builder.
/// </summary>
public sealed class Tls12Client : IDisposable
{
    private readonly System.Net.Sockets.TcpClient _tcp;
    private readonly Stream _stream;
    private readonly byte[] _clientKey;
    private readonly byte[] _serverKey;
    private readonly byte[] _clientIv;
    private readonly byte[] _serverIv;
    private ulong _writeSeq;
    private ulong _readSeq;

    public string Version { get; }
    public string CipherSuite { get; }
    public string? Alpn { get; }
    public byte[] MasterSecret { get; }

    private Tls12Client(System.Net.Sockets.TcpClient tcp, Stream stream, string version, string cipher,
        string? alpn, byte[] master, byte[] clientKey, byte[] serverKey, byte[] clientIv, byte[] serverIv)
    {
        _tcp = tcp;
        _stream = stream;
        Version = version;
        CipherSuite = cipher;
        Alpn = alpn;
        MasterSecret = master;
        _clientKey = clientKey;
        _serverKey = serverKey;
        _clientIv = clientIv;
        _serverIv = serverIv;
    }

    public static async Task<Tls12Client> ConnectAsync(string host, int port, TlsProfile profile,
        TimeSpan? timeout = null, CancellationToken ct = default)
    {
        using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        cts.CancelAfter(timeout ?? TimeSpan.FromSeconds(20));

        var tcp = new System.Net.Sockets.TcpClient();
        await tcp.ConnectAsync(host, port, cts.Token).ConfigureAwait(false);
        var stream = tcp.GetStream();

        try
        {
            var hello = Ja3.BuildClientHello(profile, host, out _, out var clientRandom);
            var handshake = new List<byte>(hello[5..]);  // handshake bytes (without record header)
            await stream.WriteAsync(hello, cts.Token).ConfigureAwait(false);
            await stream.FlushAsync(cts.Token).ConfigureAwait(false);

            // ---- server flight ----
            Tls12ServerHello? serverHello = null;
            byte[]? serverEcdhe = null;
            int serverCurve = 0;
            var serverRandom = Array.Empty<byte>();

            var pending = new List<byte>();
            var done = false;

            while (!done)
            {
                var record = await ReadRecordAsync(stream, cts.Token).ConfigureAwait(false);
                if (Environment.GetEnvironmentVariable("CYB_TLS_TRACE") == "1")
                    Console.Error.WriteLine($"TRACE flight_rec type=0x{record.Type:X2} len={record.Payload.Length} done={done}");
                if (record.Type == 0x15)
                    throw new NetException($"server alert {record.Payload[1]}");
                if (record.Type == 0x14) continue;   // CCS never belongs to the handshake flight
                if (record.Type != 0x16) continue;

                pending.AddRange(record.Payload);
                while (pending.Count >= 4)
                {
                    var msgType = pending[0];
                    var len = (pending[1] << 16) | (pending[2] << 8) | pending[3];
                    if (pending.Count < 4 + len) break;

                    var msg = pending.GetRange(0, 4 + len).ToArray();
                    var body = msg[4..];
                    pending.RemoveRange(0, 4 + len);
                    handshake.AddRange(msg);

                    switch (msgType)
                    {
                        case 0x02:
                            if (Environment.GetEnvironmentVariable("CYB_TLS_TRACE") == "1")
                                Console.Error.WriteLine($"TRACE server_hello={Convert.ToHexString(body)}");
                            serverHello = Tls12Handshake.ParseServerHello(body);
                            serverRandom = body.Length >= 34 ? body[2..34] : Array.Empty<byte>();
                            break;
                        case 0x0C:
                            if (Environment.GetEnvironmentVariable("CYB_TLS_TRACE") == "1")
                                Console.Error.WriteLine($"TRACE ske_body={Convert.ToHexString(body)}");
                            (serverEcdhe, serverCurve) = ExtractEcdhePublicKey(body);
                            break;
                        case 0x0E: // ServerHelloDone
                            done = true;
                            break;
                    }
                }
            }

            if (serverHello is null || serverEcdhe is null)
                throw new NetException("incomplete server flight");

            // ---- key agreement ----
            byte[] preMaster;
            byte[] clientPub;
            if (serverEcdhe.Length == 32)
            {
                var (xkey, xpub) = Ecdhe.CreateX25519();
                clientPub = xpub;
                preMaster = Ecdhe.SharedSecretX25519(xkey, serverEcdhe);
                if (Environment.GetEnvironmentVariable("CYB_TLS_TRACE") == "1")
                {
                    Console.Error.WriteLine($"TRACE client_priv={Convert.ToHexString(xkey.GetEncoded())}");
                    Console.Error.WriteLine($"TRACE server_ecdhe={Convert.ToHexString(serverEcdhe)}");
                }
            }
            else
            {
                var (pkey, ppub) = Ecdhe.CreateP256();
                using (pkey)
                {
                    clientPub = ppub;
                    preMaster = Ecdhe.SharedSecret(pkey, serverEcdhe);
                }
            }

            // ---- ClientKeyExchange ----
            var handshakeBeforeCke = handshake.Count;
            var cke = BuildClientKeyExchange(clientPub);
            if (Environment.GetEnvironmentVariable("CYB_TLS_TRACE") == "1")
                Console.Error.WriteLine($"TRACE cke={Convert.ToHexString(cke)}");
            await stream.WriteAsync(cke, cts.Token).ConfigureAwait(false);
            handshake.AddRange(cke[5..]);

            // ---- master secret ----
            // RFC 7627: when the server echoes extended_master_secret, the master secret is
            // PRF(pre_master, "extended master secret", session_hash) where session_hash covers
            // every handshake message up to and including ClientKeyExchange.
            byte[] master;
            if (serverHello.UsesExtendedMasterSecret)
            {
                var sessionHash = SHA256.HashData(handshake.ToArray());
                master = Tls12Prf.Prf(preMaster, "extended master secret", sessionHash, 48);
                if (Environment.GetEnvironmentVariable("CYB_TLS_EMS_NO_CKE") == "1")
                {
                    var withoutCke = handshake.Take(handshakeBeforeCke).ToArray();
                    master = Tls12Prf.Prf(preMaster, "extended master secret", SHA256.HashData(withoutCke), 48);
                }
            }
            else
            {
                master = Tls12Prf.MasterSecret(preMaster, clientRandom, serverRandom);
            }

            var keyBlock = Tls12Prf.KeyBlock(master, clientRandom, serverRandom, 40);
            var clientKey = keyBlock[..16];
            var serverKey = keyBlock[16..32];
            var clientIv = keyBlock[32..36];
            var serverIv = keyBlock[36..40];

            // ---- CCS ----
            var ccsVersion = Environment.GetEnvironmentVariable("CYB_TLS_CCS_VER") == "301" ? (byte)0x01 : (byte)0x03;
            await stream.WriteAsync(new byte[] { 0x14, 0x03, ccsVersion, 0x00, 0x01, 0x01 }, cts.Token)
                .ConfigureAwait(false);

            if (Environment.GetEnvironmentVariable("CYB_TLS_TRACE") == "1")
            {
                Console.Error.WriteLine($"TRACE client_pub={Convert.ToHexString(clientPub)}");
                Console.Error.WriteLine($"TRACE server_pub={Convert.ToHexString(serverEcdhe)}");
                Console.Error.WriteLine($"TRACE client_random={Convert.ToHexString(clientRandom)}");
                Console.Error.WriteLine($"TRACE server_random={Convert.ToHexString(serverRandom)}");
                Console.Error.WriteLine($"TRACE pre_master={Convert.ToHexString(preMaster)}");
                Console.Error.WriteLine($"TRACE master={Convert.ToHexString(master)}");
                Console.Error.WriteLine($"TRACE key_block={Convert.ToHexString(keyBlock)}");
                Console.Error.WriteLine($"TRACE hs_len={handshake.Count} cipher={serverHello.CipherSuite} ems={serverHello.UsesExtendedMasterSecret}");
            }

            // ---- Finished (encrypted) ----
            var handshakeHash = SHA256.HashData(handshake.ToArray());
            var verifyData = Tls12Prf.FinishedVerifyData(master, fromClient: true, handshakeHash);

            // Finished is a handshake message: the 4-byte header goes inside the encrypted record
            // (RFC 5246 §7.4.9 + §6.2.3.3). Sending bare verify_data makes a real stack answer
            // "unexpected_message" because the decrypted plaintext is not a valid handshake.
            var finishedMessage = new byte[4 + verifyData.Length];
            finishedMessage[0] = 0x14;
            finishedMessage[1] = 0;
            finishedMessage[2] = 0;
            finishedMessage[3] = (byte)verifyData.Length;
            verifyData.CopyTo(finishedMessage, 4);
            var finishedRecord = EncryptRecord(clientKey, clientIv, 0, 0x16, finishedMessage);
            if (Environment.GetEnvironmentVariable("CYB_TLS_TRACE") == "1")
            {
                Console.Error.WriteLine($"TRACE hs_hash={Convert.ToHexString(handshakeHash)}");
                Console.Error.WriteLine($"TRACE verify={Convert.ToHexString(verifyData)}");
                Console.Error.WriteLine($"TRACE finished_record={Convert.ToHexString(finishedRecord)}");
            }
            await stream.WriteAsync(finishedRecord, cts.Token).ConfigureAwait(false);
            await stream.FlushAsync(cts.Token).ConfigureAwait(false);

            // ---- server CCS + Finished ----
            // A real stack may send CCS, NewSessionTicket and Finished back to back; consume
            // records until the encrypted Finished handshake record shows up.
            (byte Type, byte[] Payload) serverFinished = default;
            var preCcsHandshake = new List<byte>();
            var sawCcs = false;
            while (true)
            {
                var rec = await ReadRecordAsync(stream, cts.Token).ConfigureAwait(false);
                if (Environment.GetEnvironmentVariable("CYB_TLS_TRACE") == "1")
                    Console.Error.WriteLine($"TRACE srv_rec type=0x{rec.Type:X2} len={rec.Payload.Length}");

                if (rec.Type == 0x15)
                    throw new NetException(
                        "server alert during handshake: level=0x" + (rec.Payload.Length > 0 ? rec.Payload[0] : 0).ToString("X2") +
                        " description=" + (rec.Payload.Length > 1 ? rec.Payload[1].ToString() : "-"));

                if (rec.Type == 0x14)
                {
                    sawCcs = true;
                    continue;
                }

                if (rec.Type == 0x16)
                {
                    // OpenSSL (and thus most servers) emit NewSessionTicket as a plaintext
                    // handshake record *before* ChangeCipherSpec (RFC 5077 §3.3).
                    if (!sawCcs)
                    {
                        preCcsHandshake.AddRange(rec.Payload);   // e.g. NewSessionTicket
                        continue;
                    }
                    serverFinished = rec;
                    break;
                }
            }

            if (!sawCcs)
                throw new NetException("server never sent ChangeCipherSpec");

            var client = new Tls12Client(tcp, stream, serverHello.Version, serverHello.CipherSuite,
                serverHello.Alpn, master, clientKey, serverKey, clientIv, serverIv)
            {
                _writeSeq = 1,
                _readSeq = 0,
            };

            // decrypt + verify the server's Finished (optional but catches key-derivation bugs)
            var serverVerify = client.DecryptRecord(serverFinished.Payload, 0x16);
            // the server's Finished covers every handshake message plus OUR Finished
            var transcriptWithClientFinished = handshake
                .Concat(finishedMessage)
                .Concat(preCcsHandshake)
                .ToArray();
            var expected = Tls12Prf.FinishedVerifyData(master, fromClient: false,
                SHA256.HashData(transcriptWithClientFinished));

            // the decrypted plaintext is a handshake message: type(1) length(3) verify_data(12)
            var serverVerifyData = serverVerify.Content.Length == 4 + expected.Length
                ? serverVerify.Content[4..]
                : serverVerify.Content;

            if (!serverVerifyData.SequenceEqual(expected))
                throw new NetException("server Finished did not verify");

            return client;
        }
        catch
        {
            stream.Dispose();
            tcp.Dispose();
            throw;
        }
    }

    private static byte[] BuildClientKeyExchange(byte[] publicKey)
    {
        var body = new byte[1 + publicKey.Length];
        body[0] = (byte)publicKey.Length;
        publicKey.CopyTo(body, 1);

        var handshake = new byte[4 + body.Length];
        handshake[0] = 0x10; // ClientKeyExchange
        handshake[1] = (byte)(body.Length >> 16);
        handshake[2] = (byte)(body.Length >> 8);
        handshake[3] = (byte)body.Length;
        body.CopyTo(handshake, 4);

        var record = new byte[5 + handshake.Length];
        record[0] = 0x16;
        record[1] = 0x03; record[2] = 0x03;
        BinaryPrimitives.WriteUInt16BigEndian(record.AsSpan(3), (ushort)handshake.Length);
        handshake.CopyTo(record, 5);
        return record;
    }

    private static (byte[]? Key, int Curve) ExtractEcdhePublicKey(byte[] body)
    {
        if (body.Length < 4 || body[0] != 0x03) return (null, 0);
        var curve = (body[1] << 8) | body[2];
        var pubLen = body[3];
        if (body.Length < 4 + pubLen) return (null, curve);
        return (body[4..(4 + pubLen)], curve);
    }

    // ---------------- record layer ----------------

    private static byte[] EncryptRecord(byte[] key, byte[] fixedIv, ulong seq, byte type, byte[] plaintext)
    {
        var explicitNonce = new byte[8];
        BinaryPrimitives.WriteUInt64BigEndian(explicitNonce, seq);

        var nonce = new byte[12];
        fixedIv.CopyTo(nonce, 0);
        explicitNonce.CopyTo(nonce, 4);

        var aad = new byte[13];
        BinaryPrimitives.WriteUInt64BigEndian(aad.AsSpan(0), seq);
        aad[8] = type;
        aad[9] = 0x03;
        aad[10] = 0x03;
        BinaryPrimitives.WriteUInt16BigEndian(aad.AsSpan(11), (ushort)plaintext.Length);

        var cipher = new byte[plaintext.Length];
        var tag = new byte[16];
        using (var aes = new AesGcm(key, 16))
            aes.Encrypt(nonce, plaintext, cipher, tag, aad);

        var payload = new byte[8 + cipher.Length + 16];
        explicitNonce.CopyTo(payload, 0);
        cipher.CopyTo(payload, 8);
        tag.CopyTo(payload, 8 + cipher.Length);

        var record = new byte[5 + payload.Length];
        record[0] = type;
        record[1] = 0x03;
        record[2] = Environment.GetEnvironmentVariable("CYB_TLS_REC_VER") == "301" ? (byte)0x01 : (byte)0x03;
        BinaryPrimitives.WriteUInt16BigEndian(record.AsSpan(3), (ushort)payload.Length);
        payload.CopyTo(record, 5);
        return record;
    }

    private (byte[] Content, byte Type) DecryptRecord(byte[] payload, byte type)
    {
        var explicitNonce = payload[..8];
        var cipher = payload[8..^16];
        var tag = payload[^16..];

        var nonce = new byte[12];
        _serverIv.CopyTo(nonce, 0);
        explicitNonce.CopyTo(nonce, 4);

        var aad = new byte[13];
        BinaryPrimitives.WriteUInt64BigEndian(aad.AsSpan(0), _readSeq);
        aad[8] = type;
        aad[9] = 0x03;
        aad[10] = 0x03;
        BinaryPrimitives.WriteUInt16BigEndian(aad.AsSpan(11), (ushort)cipher.Length);

        var plaintext = new byte[cipher.Length];
        using (var aes = new AesGcm(_serverKey, 16))
            aes.Decrypt(nonce, cipher, tag, plaintext, aad);

        _readSeq++;
        return (plaintext, type);
    }

    private static async Task<(byte Type, byte[] Payload)> ReadRecordAsync(Stream stream, CancellationToken ct)
    {
        var header = new byte[5];
        var offset = 0;
        while (offset < 5)
        {
            var read = await stream.ReadAsync(header.AsMemory(offset), ct).ConfigureAwait(false);
            if (read <= 0) throw new EndOfStreamException("connection closed");
            offset += read;
        }

        var length = (header[3] << 8) | header[4];
        if (Environment.GetEnvironmentVariable("CYB_TLS_TRACE") == "1")
            Console.Error.WriteLine($"TRACE raw_header={Convert.ToHexString(header)} length={length}");
        var payload = new byte[length];
        offset = 0;
        while (offset < length)
        {
            var read = await stream.ReadAsync(payload.AsMemory(offset), ct).ConfigureAwait(false);
            if (read <= 0) throw new EndOfStreamException("connection closed");
            offset += read;
        }
        return (header[0], payload);
    }

    /// <summary>Encrypted GET over the established session (HTTP/2 when ALPN picked h2).</summary>
    public Task<NetResponse> GetAsync(string path, string host, CancellationToken ct = default)
        => SendAsync("GET", path, host, null, ct);

    /// <summary>Encrypted request over the established session; supports bodies on both h2 and 1.1.</summary>
    public async Task<NetResponse> SendAsync(string method, string path, string host, string? body,
        CancellationToken ct = default)
    {
        if (string.Equals(Alpn, "h2", StringComparison.OrdinalIgnoreCase))
            return await SendH2Async(method, path, host, body, ct).ConfigureAwait(false);

        var request = System.Text.Encoding.ASCII.GetBytes(
            $"{method} {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0\r\nAccept: */*\r\n" +
            (body is null ? string.Empty : $"Content-Length: {System.Text.Encoding.UTF8.GetByteCount(body)}\r\n") +
            "Connection: close\r\n\r\n" + (body ?? string.Empty));

        var record = EncryptRecord(_clientKey, _clientIv, _writeSeq++, 0x17, request);
        await _stream.WriteAsync(record, ct).ConfigureAwait(false);
        await _stream.FlushAsync(ct).ConfigureAwait(false);

        var responseBody = new MemoryStream();
        var status = 0;
        while (true)
        {
            (byte Type, byte[] Payload) rec;
            try
            {
                rec = await ReadRecordAsync(_stream, ct).ConfigureAwait(false);
            }
            catch (EndOfStreamException)
            {
                break;
            }

            if (rec.Type == 0x17)
            {
                var (plain, _) = DecryptRecord(rec.Payload, 0x17);
                responseBody.Write(plain);
            }
            else if (rec.Type == 0x15)
            {
                break;
            }
        }

        var text = System.Text.Encoding.UTF8.GetString(responseBody.ToArray());
        var space = text.IndexOf(' ');
        if (space > 0 && int.TryParse(text.Substring(space + 1, Math.Min(3, text.Length - space - 1)), out var code))
            status = code;

        return new NetResponse
        {
            StatusCode = status,
            Body = text,
            Url = new Uri($"https://{host}{path}"),
            Protocol = "tls12/1.1",
            Bytes = text.Length,
        };
    }

    // ---------------- HTTP/2 over the encrypted record layer ----------------

    private readonly List<byte> _h2Inbox = new();

    private async Task WriteAppAsync(byte[] payload, CancellationToken ct)
    {
        var record = EncryptRecord(_clientKey, _clientIv, _writeSeq++, 0x17, payload);
        await _stream.WriteAsync(record, ct).ConfigureAwait(false);
        await _stream.FlushAsync(ct).ConfigureAwait(false);
    }

    /// <summary>Reads one HTTP/2 frame, decrypting application-data records as needed.</summary>
    private async Task<(byte Type, byte Flags, int StreamId, byte[] Payload)> ReadH2FrameAsync(CancellationToken ct)
    {
        while (true)
        {
            if (_h2Inbox.Count >= 9)
            {
                var length = (_h2Inbox[0] << 16) | (_h2Inbox[1] << 8) | _h2Inbox[2];
                if (_h2Inbox.Count >= 9 + length)
                {
                    var type = _h2Inbox[3];
                    var flags = _h2Inbox[4];
                    var streamId = ((_h2Inbox[5] & 0x7F) << 24) | (_h2Inbox[6] << 16) | (_h2Inbox[7] << 8) | _h2Inbox[8];
                    var payload = _h2Inbox.GetRange(9, length).ToArray();
                    _h2Inbox.RemoveRange(0, 9 + length);
                    return (type, flags, streamId, payload);
                }
            }

            var rec = await ReadRecordAsync(_stream, ct).ConfigureAwait(false);
            if (rec.Type == 0x15)
                throw new NetException("server alert while reading HTTP/2 frames");
            if (rec.Type != 0x17) continue;

            var (plain, _) = DecryptRecord(rec.Payload, 0x17);
            _h2Inbox.AddRange(plain);
        }
    }

    private async Task<NetResponse> SendH2Async(string method, string path, string host, string? body,
        CancellationToken ct)
    {
        await WriteAppAsync(System.Text.Encoding.ASCII.GetBytes(Http2.Preface), ct).ConfigureAwait(false);
        await WriteAppAsync(Http2.SettingsFrame(), ct).ConfigureAwait(false);

        const string ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                          "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36";
        var payloadBytes = body is null ? Array.Empty<byte>() : System.Text.Encoding.UTF8.GetBytes(body);
        var block = Http2.EncodeHeaders(host, path, ua, "*/*", "en-US,en;q=0.9", method, null);
        var headersFlags = (byte)(Http2.FlagEndHeaders | (payloadBytes.Length == 0 ? Http2.FlagEndStream : 0));
        await WriteAppAsync(Http2.Frame(Http2.Headers, headersFlags, 1, block), ct).ConfigureAwait(false);

        if (payloadBytes.Length > 0)
            await WriteAppAsync(Http2.Frame(Http2.Data, Http2.FlagEndStream, 1, payloadBytes), ct)
                .ConfigureAwait(false);

        var responseBody = new MemoryStream();
        var status = 0;
        var finished = false;

        while (!finished)
        {
            (byte Type, byte Flags, int StreamId, byte[] Payload) frame;
            try
            {
                frame = await ReadH2FrameAsync(ct).ConfigureAwait(false);
            }
            catch (EndOfStreamException)
            {
                break;
            }

            switch (frame.Type)
            {
                case Http2.Settings:
                    if ((frame.Flags & Http2.FlagAck) == 0)
                        await WriteAppAsync(
                            Http2.Frame(Http2.Settings, Http2.FlagAck, 0, Array.Empty<byte>()), ct).ConfigureAwait(false);
                    break;

                case Http2.Headers:
                    if (status == 0)
                    {
                        var decoded = Http2.DecodeStatus(frame.Payload);
                        if (decoded > 0) status = decoded;
                    }
                    if (frame.StreamId == 1 && (frame.Flags & Http2.FlagEndStream) != 0) finished = true;
                    break;

                case Http2.Data:
                    responseBody.Write(frame.Payload);
                    if (frame.StreamId == 1 && (frame.Flags & Http2.FlagEndStream) != 0) finished = true;
                    break;

                case Http2.GoAway:
                    finished = true;
                    break;
            }
        }

        return new NetResponse
        {
            StatusCode = status,
            Body = System.Text.Encoding.UTF8.GetString(responseBody.ToArray()),
            Url = new Uri($"https://{host}{path}"),
            Protocol = "h2",
            Bytes = (int)responseBody.Length,
        };
    }

    public void Dispose()
    {
        _stream.Dispose();
        _tcp.Dispose();
    }

}
