using System.Buffers.Binary;
using System.Text;

namespace Cybersole.Http;

/// <summary>
/// JA3 fingerprint construction (Salesforce JA3, RFC 8701 GREASE aware).
/// Produces both the JA3 string and a fully hand-built ClientHello, so the
/// cipher order and extension order are exactly what the profile says —
/// something BouncyCastle's own ClientHello cannot guarantee.
/// </summary>
public static class Ja3
{
    public const int GreaseCipher = 0x0A0A;
    public const int GreaseExtension = 0x1A1A;

    /// <summary>Chrome 148 extension order (JA3 component 2).</summary>
    public static readonly int[] ChromeExtensionOrder =
    {
        0x0000, // server_name
        0x0017, // extended_master_secret
        0xFF01, // renegotiation_info
        0x000A, // supported_groups
        0x000B, // ec_point_formats
        0x0023, // session_ticket
        0x0010, // ALPN
        0x0005, // status_request
        0x000D, // signature_algorithms
        0x0012, // signed_certificate_timestamp
    };

    /// <summary>Build the JA3 string for a profile (GREASE excluded, per the JA3 spec).</summary>
    public static string FromProfile(TlsProfile profile, bool includeGrease = false)
    {
        var ciphers = profile.CipherSuiteNames
            .Select(TryMapCipher)
            .Where(id => id > 0)
            .Where(id => includeGrease || !IsGrease(id))
            .ToList();

        if (includeGrease) ciphers.Insert(0, GreaseCipher);

        var extensions = ChromeExtensionOrder
            .Where(e => includeGrease || e != GreaseExtension)
            .Select(e => (int)e)
            .ToList();
        if (includeGrease) extensions.Insert(0, GreaseExtension);
        if (profile.Alpn.Count > 0 && !extensions.Contains(0x0010)) extensions.Add(0x0010);
        if (!extensions.Contains(0x0000)) extensions.Insert(0, 0x0000);

        var curves = profile.Curves;
        return $"{771},{string.Join("-", ciphers)},{string.Join("-", extensions)},{string.Join("-", curves)},0";
    }

    /// <summary>
    /// Build a complete TLS 1.2 ClientHello record with hand-picked cipher/extension order.
    /// This is what a self-written TLS stack would put on the wire.
    /// </summary>
    public static byte[] BuildClientHello(TlsProfile profile, string host, out string ja3)
        => BuildClientHello(profile, host, out ja3, out _);

    /// <summary>Same as above, additionally returning the 32-byte ClientHello.random.</summary>
    public static byte[] BuildClientHello(TlsProfile profile, string host, out string ja3, out byte[] random)
    {
        ja3 = FromProfile(profile, includeGrease: false);
        random = BuildRandom();

        var ciphers = new List<int>();
        if (profile.Grease) ciphers.Add(GreaseCipher);
        foreach (var name in profile.CipherSuiteNames)
        {
            var id = TryMapCipher(name);
            if (id > 0 && !ciphers.Contains(id)) ciphers.Add(id);
        }
        ciphers.Add(0x00FF); // renegotiation SCSV, Chrome still sends it

        var extensions = new List<(int Type, byte[] Data)>();
        if (profile.Grease) extensions.Add((GreaseExtension, Array.Empty<byte>()));
        foreach (var type in ChromeExtensionOrder)
        {
            var data = BuildExtension(type, profile, host);
            if (data is not null) extensions.Add((type, data));
        }

        // ---- handshake body ----
        using var body = new MemoryStream();
        body.WriteByte(0x03); body.WriteByte(0x03);          // client_version TLS1.2
        body.Write(random);                                  // 32-byte random
        body.WriteByte(0x00);                                 // session id length
        body.WriteUInt16((ushort)(ciphers.Count * 2));
        foreach (var c in ciphers) body.WriteUInt16((ushort)c);
        body.WriteByte(0x01); body.WriteByte(0x00);           // compression: null

        using var extBlock = new MemoryStream();
        foreach (var (type, data) in extensions)
        {
            extBlock.WriteUInt16((ushort)type);
            extBlock.WriteUInt16((ushort)data.Length);
            extBlock.Write(data);
        }
        body.WriteUInt16((ushort)extBlock.Length);
        body.Write(extBlock.ToArray());

        // ---- handshake header + record header ----
        var bodyBytes = body.ToArray();
        var handshake = new byte[4 + bodyBytes.Length];
        handshake[0] = 0x01;
        handshake[1] = (byte)(bodyBytes.Length >> 16);
        handshake[2] = (byte)(bodyBytes.Length >> 8);
        handshake[3] = (byte)bodyBytes.Length;
        bodyBytes.CopyTo(handshake, 4);

        var record = new byte[5 + handshake.Length];
        record[0] = 0x16;
        record[1] = 0x03; record[2] = 0x01;
        BinaryPrimitives.WriteUInt16BigEndian(record.AsSpan(3), (ushort)handshake.Length);
        handshake.CopyTo(record, 5);
        return record;
    }

    private static byte[]? BuildExtension(int type, TlsProfile profile, string host)
    {
        switch (type)
        {
            case 0x0000: // server_name
            {
                var hostBytes = Encoding.ASCII.GetBytes(host);
                var listLen = 1 + 2 + hostBytes.Length;
                var data = new byte[2 + listLen];
                data[0] = (byte)(listLen >> 8);
                data[1] = (byte)listLen;
                data[2] = 0x00;
                data[3] = (byte)(hostBytes.Length >> 8);
                data[4] = (byte)hostBytes.Length;
                hostBytes.CopyTo(data, 5);
                return data;
            }
            case 0x0010: // ALPN
            {
                var entries = profile.Alpn.Select(a => Encoding.ASCII.GetBytes(a)).ToArray();
                var len = entries.Sum(e => 1 + e.Length);
                var data = new byte[2 + len];
                data[0] = (byte)(len >> 8);
                data[1] = (byte)len;
                var offset = 2;
                foreach (var e in entries)
                {
                    data[offset++] = (byte)e.Length;
                    e.CopyTo(data, offset);
                    offset += e.Length;
                }
                return data;
            }
            case 0x000A: // supported_groups
            {
                var curves = profile.Curves;
                var data = new byte[2 + curves.Count * 2];
                data[0] = (byte)((curves.Count * 2) >> 8);
                data[1] = (byte)(curves.Count * 2);
                for (var i = 0; i < curves.Count; i++)
                    BinaryPrimitives.WriteUInt16BigEndian(data.AsSpan(2 + i * 2), (ushort)curves[i]);
                return data;
            }
            case 0x000B: // ec_point_formats
                return new byte[] { 0x01, 0x00 };
            case 0xFF01: // renegotiation_info
                return new byte[] { 0x00 };
            case 0x0005: // status_request (OCSP)
                return new byte[] { 0x01, 0x00, 0x00, 0x00, 0x00 };
            case 0x000D: // signature_algorithms
            {
                ushort[] algs = { 0x0403, 0x0804, 0x0401, 0x0503, 0x0805, 0x0501, 0x0806, 0x0601 };
                var data = new byte[2 + algs.Length * 2];
                BinaryPrimitives.WriteUInt16BigEndian(data.AsSpan(0), (ushort)(algs.Length * 2));
                for (var i = 0; i < algs.Length; i++)
                    BinaryPrimitives.WriteUInt16BigEndian(data.AsSpan(2 + i * 2), algs[i]);
                return data;
            }
            case 0x0017: // extended_master_secret
            case 0x0023: // session_ticket
            case 0x0012: // SCT request
                return Array.Empty<byte>();
            default:
                return null;
        }
    }

    private static byte[] BuildRandom()
    {
        var random = new byte[32];
        System.Security.Cryptography.RandomNumberGenerator.Fill(random);
        return random;
    }

    private static int TryMapCipher(string name)
    {
        var field = typeof(Org.BouncyCastle.Tls.CipherSuite).GetField(name,
            System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static);
        return field?.GetValue(null) is int value ? value : 0;
    }

    public static bool IsGrease(int value)
        => (value & 0x0F0F) == 0x0A0A && (value >> 8) == (value & 0xFF);
}


internal static class Ja3StreamExtensions
{
    public static void WriteUInt16(this Stream stream, ushort value)
    {
        stream.WriteByte((byte)(value >> 8));
        stream.WriteByte((byte)value);
    }
}
