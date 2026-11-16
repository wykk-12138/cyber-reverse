using System.Buffers.Binary;

namespace Cybersole.Http;

public sealed record Tls12Flight(
    bool Ok,
    string? Error,
    Tls12ServerHello? ServerHello,
    int CertificateCount,
    byte[]? ServerEcdhePublicKey,
    int PreMasterLength);

/// <summary>
/// Reads the server's first flight (ServerHello → Certificate → ServerKeyExchange) and
/// computes the ECDHE pre-master secret. This is the key-agreement half of a TLS 1.2
/// client; the remaining half is ClientKeyExchange + CCS + Finished.
/// </summary>
public static class Tls12FlightReader
{
    public static async Task<Tls12Flight> ReadAsync(string host, int port, TlsProfile profile,
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
            return new Tls12Flight(false, $"connect failed: {ex.Message}", null, 0, null, 0);
        }

        await using var stream = tcp.GetStream();
        await stream.WriteAsync(Ja3.BuildClientHello(profile, host, out _), cts.Token).ConfigureAwait(false);
        await stream.FlushAsync(cts.Token).ConfigureAwait(false);

        Tls12ServerHello? serverHello = null;
        var certCount = 0;
        byte[]? serverEcdhe = null;

        try
        {
            var buffer = new List<byte>();
            var deadline = DateTime.UtcNow.AddSeconds(10);

            while (DateTime.UtcNow < deadline)
            {
                var record = await ReadRecordAsync(stream, cts.Token).ConfigureAwait(false);
                if (record.Type == 0x15)
                    return new Tls12Flight(false, $"alert {record.Payload[1]}", serverHello, certCount, null, 0);
                if (record.Type != 0x16) continue;

                buffer.AddRange(record.Payload);

                // consume every complete handshake message currently buffered
                while (buffer.Count >= 4)
                {
                    var msgType = buffer[0];
                    var len = (buffer[1] << 16) | (buffer[2] << 8) | buffer[3];
                    if (buffer.Count < 4 + len) break;

                    var body = buffer.GetRange(4, len).ToArray();
                    buffer.RemoveRange(0, 4 + len);

                    switch (msgType)
                    {
                        case 0x02:
                            serverHello = Tls12Handshake.ParseServerHello(body);
                            break;
                        case 0x0B: // Certificate
                            certCount = CountCertificates(body);
                            break;
                        case 0x0C: // ServerKeyExchange
                            serverEcdhe = ExtractEcdhePublicKey(body);
                            break;
                    }
                }

                if (serverHello is not null && serverEcdhe is not null)
                    break;
            }

            if (serverHello is null)
                return new Tls12Flight(false, "no ServerHello", null, 0, null, 0);

            if (serverEcdhe is null)
                return new Tls12Flight(true, "no ServerKeyExchange (non-ECDHE suite?)", serverHello, certCount, null, 0);

            // X25519 public keys are 32 raw bytes; NIST P-curves start with the 0x04 point marker
            if (serverEcdhe.Length == 32)
            {
                var (xkey, _) = Ecdhe.CreateX25519();
                var preMaster = Ecdhe.SharedSecretX25519(xkey, serverEcdhe);
                return new Tls12Flight(true, null, serverHello, certCount, serverEcdhe, preMaster.Length);
            }

            var (key, _) = Ecdhe.CreateP256();
            using (key)
            {
                var preMaster = Ecdhe.SharedSecret(key, serverEcdhe);
                return new Tls12Flight(true, null, serverHello, certCount, serverEcdhe, preMaster.Length);
            }
        }
        catch (OperationCanceledException)
        {
            return new Tls12Flight(false, "timeout", serverHello, certCount, serverEcdhe, 0);
        }
        catch (Exception ex)
        {
            return new Tls12Flight(false, ex.Message, serverHello, certCount, serverEcdhe, 0);
        }
    }

    private static int CountCertificates(byte[] body)
    {
        if (body.Length < 3) return 0;
        var listLen = (body[0] << 16) | (body[1] << 8) | body[2];
        var p = 3;
        var end = Math.Min(body.Length, 3 + listLen);
        var count = 0;
        while (p + 3 <= end)
        {
            var len = (body[p] << 16) | (body[p + 1] << 8) | body[p + 2];
            p += 3 + len;
            count++;
        }
        return count;
    }

    /// <summary>ServerKeyExchange (ECDHE): curve_type(1)=3, named_curve(2), pub_len(1), pub, sig_alg(2), sig_len(2), sig.</summary>
    private static byte[]? ExtractEcdhePublicKey(byte[] body)
    {
        if (body.Length < 4) return null;
        var curveType = body[0];
        if (curveType != 0x03) return null; // named_curve only

        var curve = BinaryPrimitives.ReadUInt16BigEndian(body.AsSpan(1, 2));
        var pubLen = body[3];
        if (body.Length < 4 + pubLen) return null;
        _ = curve;
        return body[4..(4 + pubLen)];
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
}
