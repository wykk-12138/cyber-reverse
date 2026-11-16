using System.Buffers.Binary;
using System.Text;

namespace Cybersole.Http;

/// <summary>
/// Minimal HTTP/2 (RFC 9113) client: connection preface, SETTINGS, a HEADERS frame
/// with hand-rolled HPACK (static-table indexes + literals), then read DATA until
/// END_STREAM. Enough to talk to h2-only edges (Cloudflare, Fastly).
/// </summary>
public static class Http2
{
    // ---- frame types ----
    public const byte Data = 0x0;
    public const byte Headers = 0x1;
    public const byte Priority = 0x2;
    public const byte RstStream = 0x3;
    public const byte Settings = 0x4;
    public const byte PushPromise = 0x5;
    public const byte Ping = 0x6;
    public const byte GoAway = 0x7;
    public const byte WindowUpdate = 0x8;
    public const byte Continuation = 0x9;

    // ---- flags ----
    public const byte FlagEndStream = 0x1;
    public const byte FlagAck = 0x1;
    public const byte FlagEndHeaders = 0x4;
    public const byte FlagPadded = 0x8;
    public const byte FlagPriority = 0x20;

    public const string Preface = "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n";

    /// <summary>Encode a frame header + payload.</summary>
    public static byte[] Frame(byte type, byte flags, int streamId, ReadOnlySpan<byte> payload)
    {
        var frame = new byte[9 + payload.Length];
        var len = payload.Length;
        frame[0] = (byte)(len >> 16);
        frame[1] = (byte)(len >> 8);
        frame[2] = (byte)len;
        frame[3] = type;
        frame[4] = flags;
        BinaryPrimitives.WriteInt32BigEndian(frame.AsSpan(5), streamId & 0x7FFF_FFFF);
        payload.CopyTo(frame.AsSpan(9));
        return frame;
    }

    /// <summary>SETTINGS frame with default-ish values (initial window 1 MiB, max concurrent 100).</summary>
    public static byte[] SettingsFrame()
    {
        var payload = new byte[12];
        BinaryPrimitives.WriteUInt16BigEndian(payload.AsSpan(0), 0x4); // INITIAL_WINDOW_SIZE
        BinaryPrimitives.WriteUInt32BigEndian(payload.AsSpan(2), 1_048_576);
        BinaryPrimitives.WriteUInt16BigEndian(payload.AsSpan(6), 0x3); // MAX_CONCURRENT_STREAMS
        BinaryPrimitives.WriteUInt32BigEndian(payload.AsSpan(8), 100);
        return Frame(Settings, 0, 0, payload);
    }

    /// <summary>HPACK-encode the request pseudo-headers (+ user-agent / accept / accept-language).</summary>
    public static byte[] EncodeHeaders(string authority, string path, string userAgent,
        string accept, string acceptLanguage, string method = "GET",
        IEnumerable<KeyValuePair<string, string>>? extra = null)
    {
        var buffer = new MemoryStream();

        // :method — static index 2 (GET) / 3 (POST)
        buffer.WriteByte(method.Equals("POST", StringComparison.OrdinalIgnoreCase) ? (byte)0x83 : (byte)0x82);
        buffer.WriteByte(0x87); // :scheme https (static index 7)

        // :authority (static index 1) — literal with indexed name
        WriteIndexedName(buffer, 0x01, authority);
        // :path (static index 4)
        WriteIndexedName(buffer, 0x04, path);
        // user-agent (static index 58)
        WriteIndexedName(buffer, 0x3A, userAgent);
        // accept / accept-language — literal with new name
        WriteLiteral(buffer, "accept", accept);
        WriteLiteral(buffer, "accept-language", acceptLanguage);

        if (extra is not null)
        {
            foreach (var kv in extra)
            {
                var name = kv.Key.ToLowerInvariant();
                if (name is ":method" or ":path" or ":scheme" or ":authority" or "user-agent"
                    or "accept" or "accept-language" or "host" or "connection")
                    continue;
                WriteLiteral(buffer, name, kv.Value);
            }
        }

        return buffer.ToArray();
    }

    /// <summary>Literal header field with an indexed name (HPACK integer + string).</summary>
    private static void WriteIndexedName(MemoryStream s, int nameIndex, string value)
    {
        WriteHpackInt(s, nameIndex, 4, 0x00); // 0000 prefix
        WriteString(s, value);
    }

    /// <summary>Literal header field with a literal name.</summary>
    private static void WriteLiteral(MemoryStream s, string name, string value)
    {
        WriteHpackInt(s, 0, 4, 0x00); // index 0 = new name, 0000 prefix
        WriteString(s, name);
        WriteString(s, value);
    }

    private static void WriteHpackInt(MemoryStream s, int value, int prefixBits, byte mask)
    {
        var max = (1 << prefixBits) - 1;
        if (value < max)
        {
            s.WriteByte((byte)(mask | value));
            return;
        }

        s.WriteByte((byte)(mask | max));
        value -= max;
        while (value >= 128)
        {
            s.WriteByte((byte)((value % 128) + 128));
            value /= 128;
        }
        s.WriteByte((byte)value);
    }

    private static void WriteString(MemoryStream s, string value)
    {
        var bytes = Encoding.UTF8.GetBytes(value);
        WriteHpackInt(s, bytes.Length, 7, 0x00); // no Huffman
        s.Write(bytes);
    }

    /// <summary>Read one frame: returns (type, flags, streamId, payload).</summary>
    public static async Task<(byte Type, byte Flags, int StreamId, byte[] Payload)> ReadFrameAsync(
        Stream stream, CancellationToken ct)
    {
        var header = new byte[9];
        await ReadExactlyAsync(stream, header, ct).ConfigureAwait(false);
        var length = (header[0] << 16) | (header[1] << 8) | header[2];
        var payload = new byte[length];
        if (length > 0)
            await ReadExactlyAsync(stream, payload, ct).ConfigureAwait(false);
        var streamId = BinaryPrimitives.ReadInt32BigEndian(header.AsSpan(5)) & 0x7FFF_FFFF;
        return (header[3], header[4], streamId, payload);
    }

    private static async Task ReadExactlyAsync(Stream stream, byte[] buffer, CancellationToken ct)
    {
        var offset = 0;
        while (offset < buffer.Length)
        {
            var read = await stream.ReadAsync(buffer.AsMemory(offset), ct).ConfigureAwait(false);
            if (read <= 0) throw new EndOfStreamException("connection closed mid-frame");
            offset += read;
        }
    }

    /// <summary>Decode the :status pseudo-header from a response HPACK block (indexed or literal).</summary>
    public static int DecodeStatus(byte[] block)
    {
        if (block.Length == 0) return 0;

        // indexed header field (1xxxxxxx)
        if ((block[0] & 0x80) != 0)
        {
            var index = block[0] & 0x7F;
            return index switch
            {
                8 => 200,
                9 => 204,
                10 => 206,
                11 => 304,
                12 => 400,
                13 => 404,
                14 => 500,
                _ => 0,
            };
        }

        // literal with indexed name (:status = 8) -> 0000xxxx where xxxx == 8
        var pos = 0;
        var prefix = block[pos] & 0x0F;
        if (prefix == 8)
        {
            pos++;
            var len = block[pos] & 0x7F;
            pos++;
            if (block.Length >= pos + len)
                return int.TryParse(Encoding.ASCII.GetString(block, pos, len), out var code) ? code : 0;
        }

        // literal with new name (0000 + 0)
        if ((block[0] & 0x0F) == 0)
        {
            pos = 1;
            var nameLen = block[pos] & 0x7F;
            pos++;
            var name = Encoding.ASCII.GetString(block, pos, nameLen);
            pos += nameLen;
            var valLen = block[pos] & 0x7F;
            pos++;
            var value = Encoding.ASCII.GetString(block, pos, valLen);
            if (name == ":status")
                return int.TryParse(value, out var code2) ? code2 : 0;
        }

        return 0;
    }

    private static readonly string[] StaticNames =
    {
        "", ":authority", ":method", ":method", ":path", ":path", ":scheme", ":scheme",
        ":status", ":status", ":status", ":status", ":status", ":status", ":status",
        "accept-charset", "accept-encoding", "accept-language", "accept-ranges", "accept",
        "access-control-allow-origin", "age", "allow", "authorization", "cache-control",
        "content-disposition", "content-encoding", "content-language", "content-length",
        "content-location", "content-range", "content-type", "cookie", "date", "etag",
        "expect", "expires", "from", "host", "if-match", "if-modified-since", "if-none-match",
        "if-range", "if-unmodified-since", "last-modified", "link", "location", "max-forwards",
        "proxy-authenticate", "proxy-authorization", "range", "referer", "refresh", "retry-after",
        "server", "set-cookie", "strict-transport-security", "transfer-encoding", "user-agent",
        "vary", "via", "www-authenticate",
    };

    private static readonly Dictionary<int, string> StaticValues = new()
    {
        [2] = "GET", [3] = "POST", [4] = "/", [5] = "/index.html", [6] = "http", [7] = "https",
        [8] = "200", [9] = "204", [10] = "206", [11] = "304", [12] = "400", [13] = "404", [14] = "500",
    };

    /// <summary>
    /// Decode a response HPACK block (static table + literals, no dynamic-table lookups).
    /// Huffman-encoded values are surfaced as raw markers — headers are best-effort here;
    /// the status code and DATA payload are the authoritative outputs.
    /// </summary>
    public static Dictionary<string, string> DecodeHeaders(byte[] block)
    {
        var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        var pos = 0;
        while (pos < block.Length)
        {
            var b = block[pos];
            if ((b & 0x80) != 0)
            {
                var index = b & 0x7F;
                pos++;
                if (index > 0 && index < StaticNames.Length && StaticValues.TryGetValue(index, out var v))
                    headers[StaticNames[index]] = v;
                continue;
            }

            int nameIndex;
            if ((b & 0x40) != 0) { nameIndex = b & 0x3F; pos++; }
            else if ((b & 0x20) != 0) { pos += 1; continue; }
            else if ((b & 0x10) != 0) { nameIndex = b & 0x0F; pos++; }
            else { nameIndex = b & 0x0F; pos++; }

            string? name = null;
            if (nameIndex == 0)
            {
                if (!TryReadString(block, ref pos, out name)) break;
            }
            else if (nameIndex < StaticNames.Length)
            {
                name = StaticNames[nameIndex];
            }
            else
            {
                break;
            }

            if (!TryReadString(block, ref pos, out var value)) break;
            if (name is not null && value is not null) headers[name] = value;
        }
        return headers;
    }

    private static bool TryReadString(byte[] block, ref int pos, out string? value)
    {
        value = null;
        if (pos >= block.Length) return false;
        var len = block[pos];
        var huffman = (len & 0x80) != 0;
        len &= 0x7F;
        pos++;
        if (pos + len > block.Length) return false;
        value = huffman
            ? HpackHuffman.Decode(block.AsSpan(pos, len))
            : Encoding.ASCII.GetString(block, pos, len);
        pos += len;
        return true;
    }
}
