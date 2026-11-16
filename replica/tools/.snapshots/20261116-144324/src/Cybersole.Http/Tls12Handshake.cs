using System.Buffers.Binary;
using System.Text;

namespace Cybersole.Http;

public sealed record Tls12ServerHello(
    string Version,
    string CipherSuite,
    string? Alpn,
    int ExtensionCount,
    bool Ok,
    string? Error,
    IReadOnlyList<int>? Extensions = null)
{
    /// <summary>True when the server agreed to the extended_master_secret extension (RFC 7627).</summary>
    public bool UsesExtendedMasterSecret => Extensions?.Contains(0x0017) ?? false;
}

/// <summary>
/// Minimal TLS 1.2 handshake reader: sends the hand-built ClientHello from
/// <see cref="Ja3"/> and parses the server's first flight (ServerHello / Certificate /
/// ServerKeyExchange). This proves the custom ClientHello is accepted by a real edge
/// before wiring the full key-exchange state machine.
/// </summary>
public static class Tls12Handshake
{
    private const byte Handshake = 0x16;
    private const byte Alert = 0x15;

    public static async Task<Tls12ServerHello> ProbeAsync(string host, int port, TlsProfile profile,
        TimeSpan? timeout = null, CancellationToken ct = default)
    {
        using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        cts.CancelAfter(timeout ?? TimeSpan.FromSeconds(15));

        using var tcp = new System.Net.Sockets.TcpClient();
        try
        {
            await tcp.ConnectAsync(host, port, cts.Token).ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            return new Tls12ServerHello("-", "-", null, 0, false, $"connect failed: {ex.Message}");
        }

        await using var stream = tcp.GetStream();

        var hello = Ja3.BuildClientHello(profile, host, out _);
        await stream.WriteAsync(hello, cts.Token).ConfigureAwait(false);
        await stream.FlushAsync(cts.Token).ConfigureAwait(false);

        try
        {
            while (true)
            {
                var (type, payload) = await ReadRecordAsync(stream, cts.Token).ConfigureAwait(false);

                if (type == Alert)
                {
                    var level = payload.Length > 0 ? payload[0] : (byte)0;
                    var desc = payload.Length > 1 ? payload[1] : (byte)0;
                    return new Tls12ServerHello("-", "-", null, 0, false,
                        $"alert level={level} description={desc} ({AlertName(desc)})");
                }

                if (type != Handshake || payload.Length < 4) continue;

                var msgType = payload[0];
                var length = (payload[1] << 16) | (payload[2] << 8) | payload[3];
                var body = payload[4..Math.Min(length, payload.Length - 4)];

                if (msgType != 0x02) continue; // wait for ServerHello

                return ParseServerHello(body);
            }
        }
        catch (OperationCanceledException)
        {
            return new Tls12ServerHello("-", "-", null, 0, false, "timeout");
        }
        catch (Exception ex)
        {
            return new Tls12ServerHello("-", "-", null, 0, false, ex.Message);
        }
    }

    private static async Task<(byte Type, byte[] Payload)> ReadRecordAsync(Stream stream, CancellationToken ct)
    {
        var header = new byte[5];
        await ReadExactlyAsync(stream, header, ct).ConfigureAwait(false);
        var length = (header[3] << 8) | header[4];
        var payload = new byte[length];
        if (length > 0)
            await ReadExactlyAsync(stream, payload, ct).ConfigureAwait(false);
        return (header[0], payload);
    }

    private static async Task ReadExactlyAsync(Stream stream, byte[] buffer, CancellationToken ct)
    {
        var offset = 0;
        while (offset < buffer.Length)
        {
            var read = await stream.ReadAsync(buffer.AsMemory(offset), ct).ConfigureAwait(false);
            if (read <= 0) throw new EndOfStreamException("connection closed");
            offset += read;
        }
    }

    private static string CipherSuiteName(int id) => id switch
    {
        0xC02B => "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
        0xC02F => "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
        0xC02C => "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
        0xC030 => "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
        0xCCA9 => "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
        0xCCA8 => "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
        0x1301 => "TLS_AES_128_GCM_SHA256",
        0x1302 => "TLS_AES_256_GCM_SHA384",
        _ => $"0x{id:X4}",
    };

    private static string AlertName(byte desc) => desc switch
    {
        40 => "handshake_failure",
        42 => "bad_record_mac",
        47 => "illegal_parameter",
        70 => "protocol_version",
        71 => "insufficient_security",
        80 => "internal_error",
        _ => "?",
    };

    /// <summary>Parse a ServerHello handshake body (after the 4-byte handshake header).</summary>
    public static Tls12ServerHello ParseServerHello(byte[] body)
    {
        if (body.Length < 38)
            return new Tls12ServerHello("-", "-", null, 0, false, "short ServerHello");

        var version = body[0] == 0x03 && body[1] == 0x03 ? "TLS1.2" : $"0x{body[0]:X2}{body[1]:X2}";

        // version(2) random(32) session_id_len(1) session_id cipher(2) compression(1) ext_len(2) ...
        var sidLen = body[34];
        var cipherOffset = 35 + sidLen;
        if (cipherOffset + 3 > body.Length)
            return new Tls12ServerHello(version, "-", null, 0, false, "short ServerHello body");

        var cipher = BinaryPrimitives.ReadUInt16BigEndian(body.AsSpan(cipherOffset, 2));
        var p = cipherOffset + 2;
        if (p >= body.Length)
            return new Tls12ServerHello(version, CipherSuiteName(cipher), null, 0, true, null);
        var compLen = body[p]; p += 1 + compLen;
        if (p >= body.Length)
            return new Tls12ServerHello(version, CipherSuiteName(cipher), null, 0, true, null);

        var extCount = 0;
        string? alpn = null;
        var extIds = new List<int>();
        if (p + 2 <= body.Length)
        {
            var extLen = BinaryPrimitives.ReadUInt16BigEndian(body.AsSpan(p, 2));
            p += 2;
            var end = Math.Min(body.Length, p + extLen);
            while (p + 4 <= end)
            {
                var etype = BinaryPrimitives.ReadUInt16BigEndian(body.AsSpan(p, 2));
                var elen = BinaryPrimitives.ReadUInt16BigEndian(body.AsSpan(p + 2, 2));
                extCount++;
                extIds.Add(etype);
                if (etype == 0x0010 && elen >= 3 && p + 7 < body.Length)
                {
                    // ALPN body: list_len(2) proto_len(1) proto...
                    var protoLen = body[p + 6];
                    if (p + 7 + protoLen <= body.Length)
                        alpn = Encoding.ASCII.GetString(body, p + 7, protoLen);
                }
                p += 4 + elen;
            }
        }

        return new Tls12ServerHello(version, CipherSuiteName(cipher), alpn, extCount, true, null, extIds);
    }
}
