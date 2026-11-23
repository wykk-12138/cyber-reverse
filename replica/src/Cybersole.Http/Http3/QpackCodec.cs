using System.Text;
using Cybersole.Http.Protocol;
using Cybersole.Http.Quic;

namespace Cybersole.Http.Http3;

/// <summary>RFC 9114 §8.1 HTTP/3 and RFC 9204 §8 QPACK wire error codes.</summary>
public static class Http3ErrorCode
{
    public const ulong NoError = 0x0100;
    public const ulong GeneralProtocolError = 0x0101;
    public const ulong InternalError = 0x0102;
    public const ulong StreamCreationError = 0x0103;
    public const ulong ClosedCriticalStream = 0x0104;
    public const ulong FrameUnexpected = 0x0105;
    public const ulong FrameError = 0x0106;
    public const ulong ExcessiveLoad = 0x0107;
    public const ulong IdError = 0x0108;
    public const ulong SettingsError = 0x0109;
    public const ulong MissingSettings = 0x010A;
    public const ulong RequestRejected = 0x010B;
    public const ulong RequestCancelled = 0x010C;
    public const ulong RequestIncomplete = 0x010D;
    public const ulong MessageError = 0x010E;
    public const ulong ConnectError = 0x010F;
    public const ulong VersionFallback = 0x0110;

    public const ulong QpackDecompressionFailed = 0x0200;
    public const ulong QpackEncoderStreamError = 0x0201;
    public const ulong QpackDecoderStreamError = 0x0202;
}

/// <summary>RFC 9204 Appendix A 99-entry QPACK Static Table (indices 0..98).</summary>
public static class QpackStaticTable
{
    public static readonly IReadOnlyList<PureHttpHeader> Entries = Array.AsReadOnly(new PureHttpHeader[]
    {
        new(":authority", ""),                                                         // 0
        new(":path", "/"),                                                             // 1
        new("age", "0"),                                                               // 2
        new("content-disposition", ""),                                                // 3
        new("content-length", "0"),                                                    // 4
        new("cookie", ""),                                                             // 5
        new("date", ""),                                                               // 6
        new("etag", ""),                                                               // 7
        new("if-modified-since", ""),                                                  // 8
        new("if-none-match", ""),                                                      // 9
        new("last-modified", ""),                                                      // 10
        new("link", ""),                                                               // 11
        new("location", ""),                                                           // 12
        new("referer", ""),                                                            // 13
        new("set-cookie", ""),                                                         // 14
        new(":method", "CONNECT"),                                                     // 15
        new(":method", "DELETE"),                                                      // 16
        new(":method", "GET"),                                                         // 17
        new(":method", "HEAD"),                                                        // 18
        new(":method", "OPTIONS"),                                                     // 19
        new(":method", "POST"),                                                        // 20
        new(":method", "PUT"),                                                         // 21
        new(":scheme", "http"),                                                        // 22
        new(":scheme", "https"),                                                       // 23
        new(":status", "103"),                                                         // 24
        new(":status", "200"),                                                         // 25
        new(":status", "304"),                                                         // 26
        new(":status", "404"),                                                         // 27
        new(":status", "503"),                                                         // 28
        new("accept", "*/*"),                                                          // 29
        new("accept", "application/dns-message"),                                      // 30
        new("accept-encoding", "gzip, deflate, br"),                                   // 31
        new("accept-ranges", "bytes"),                                                 // 32
        new("access-control-allow-headers", "cache-control"),                          // 33
        new("access-control-allow-headers", "content-type"),                           // 34
        new("access-control-allow-origin", "*"),                                       // 35
        new("cache-control", "max-age=0"),                                             // 36
        new("cache-control", "max-age=2592000"),                                       // 37
        new("cache-control", "max-age=604800"),                                        // 38
        new("cache-control", "no-cache"),                                              // 39
        new("cache-control", "no-store"),                                              // 40
        new("cache-control", "public, max-age=31536000"),                              // 41
        new("content-encoding", "br"),                                                 // 42
        new("content-encoding", "gzip"),                                               // 43
        new("content-type", "application/dns-message"),                                // 44
        new("content-type", "application/javascript"),                                 // 45
        new("content-type", "application/json"),                                       // 46
        new("content-type", "application/x-www-form-urlencoded"),                      // 47
        new("content-type", "image/gif"),                                              // 48
        new("content-type", "image/jpeg"),                                             // 49
        new("content-type", "image/png"),                                              // 50
        new("content-type", "text/css"),                                               // 51
        new("content-type", "text/html; charset=utf-8"),                               // 52
        new("content-type", "text/plain"),                                             // 53
        new("content-type", "text/plain;charset=utf-8"),                               // 54
        new("range", "bytes=0-"),                                                      // 55
        new("strict-transport-security", "max-age=31536000"),                          // 56
        new("strict-transport-security", "max-age=31536000; includesubdomains"),       // 57
        new("strict-transport-security", "max-age=31536000; includesubdomains; preload"), // 58
        new("vary", "accept-encoding"),                                                // 59
        new("vary", "origin"),                                                         // 60
        new("x-content-type-options", "nosniff"),                                      // 61
        new("x-xss-protection", "1; mode=block"),                                      // 62
        new(":status", "100"),                                                         // 63
        new(":status", "204"),                                                         // 64
        new(":status", "206"),                                                         // 65
        new(":status", "302"),                                                         // 66
        new(":status", "400"),                                                         // 67
        new(":status", "403"),                                                         // 68
        new(":status", "421"),                                                         // 69
        new(":status", "425"),                                                         // 70
        new(":status", "500"),                                                         // 71
        new("accept-language", ""),                                                    // 72
        new("access-control-allow-credentials", "FALSE"),                              // 73
        new("access-control-allow-credentials", "TRUE"),                               // 74
        new("access-control-allow-headers", "*"),                                      // 75
        new("access-control-allow-methods", "get"),                                    // 76
        new("access-control-allow-methods", "get, post, options"),                     // 77
        new("access-control-allow-methods", "options"),                                // 78
        new("access-control-expose-headers", "content-length"),                        // 79
        new("access-control-request-headers", "content-type"),                         // 80
        new("access-control-request-method", "get"),                                   // 81
        new("access-control-request-method", "post"),                                  // 82
        new("alt-svc", "clear"),                                                       // 83
        new("authorization", ""),                                                      // 84
        new("content-security-policy", "script-src 'none'; object-src 'none'; base-uri 'none'"), // 85
        new("early-data", "1"),                                                        // 86
        new("expect-ct", ""),                                                          // 87
        new("forwarded", ""),                                                          // 88
        new("if-range", ""),                                                           // 89
        new("origin", ""),                                                             // 90
        new("purpose", "prefetch"),                                                    // 91
        new("server", ""),                                                             // 92
        new("timing-allow-origin", "*"),                                               // 93
        new("upgrade-insecure-requests", "1"),                                         // 94
        new("user-agent", ""),                                                         // 95
        new("x-forwarded-for", ""),                                                    // 96
        new("x-frame-options", "deny"),                                                // 97
        new("x-frame-options", "sameorigin"),                                          // 98
    });

    private static readonly Dictionary<(string Name, string Value), int> ExactIndex = BuildExactIndex();
    private static readonly Dictionary<string, int> NameIndex = BuildNameIndex();

    private static Dictionary<(string Name, string Value), int> BuildExactIndex()
    {
        var map = new Dictionary<(string, string), int>(Entries.Count);
        for (int i = 0; i < Entries.Count; i++)
            map.TryAdd((Entries[i].Name, Entries[i].Value), i);
        return map;
    }

    private static Dictionary<string, int> BuildNameIndex()
    {
        var map = new Dictionary<string, int>(Entries.Count, StringComparer.Ordinal);
        for (int i = 0; i < Entries.Count; i++)
            map.TryAdd(Entries[i].Name, i);
        return map;
    }

    public static bool TryFindExact(string lowercaseName, string value, out int index) =>
        ExactIndex.TryGetValue((lowercaseName, value), out index);

    public static bool TryFindName(string lowercaseName, out int index) =>
        NameIndex.TryGetValue(lowercaseName, out index);
}

/// <summary>
/// RFC 7541 Appendix B Huffman encoder and strict RFC 9204 §4.1.2 decoder
/// (rejecting EOS symbols in payload and non-all-ones or >= 8 bit padding).
/// </summary>
public static class QpackHuffman
{
    private static readonly (uint Code, byte Bits)[] Table =
    {
        (0x1FF8, 13), (0x7FFFD8, 23), (0xFFFFFE2, 28), (0xFFFFFE3, 28),
        (0xFFFFFE4, 28), (0xFFFFFE5, 28), (0xFFFFFE6, 28), (0xFFFFFE7, 28),
        (0xFFFFFE8, 28), (0xFFFFEA, 24), (0x3FFFFFFC, 30), (0xFFFFFE9, 28),
        (0xFFFFFEA, 28), (0x3FFFFFFD, 30), (0xFFFFFEB, 28), (0xFFFFFEC, 28),
        (0xFFFFFED, 28), (0xFFFFFEE, 28), (0xFFFFFEF, 28), (0xFFFFFF0, 28),
        (0xFFFFFF1, 28), (0xFFFFFF2, 28), (0x3FFFFFFE, 30), (0xFFFFFF3, 28),
        (0xFFFFFF4, 28), (0xFFFFFF5, 28), (0xFFFFFF6, 28), (0xFFFFFF7, 28),
        (0xFFFFFF8, 28), (0xFFFFFF9, 28), (0xFFFFFFA, 28), (0xFFFFFFB, 28),
        (0x0014, 6), (0x03F8, 10), (0x03F9, 10), (0x0FFA, 12),
        (0x1FF9, 13), (0x0015, 6), (0x00F8, 8), (0x07FA, 11),
        (0x03FA, 10), (0x03FB, 10), (0x00F9, 8), (0x07FB, 11),
        (0x00FA, 8), (0x0016, 6), (0x0017, 6), (0x0018, 6),
        (0x0000, 5), (0x0001, 5), (0x0002, 5), (0x0019, 6),
        (0x001A, 6), (0x001B, 6), (0x001C, 6), (0x001D, 6),
        (0x001E, 6), (0x001F, 6), (0x005C, 7), (0x00FB, 8),
        (0x7FFC, 15), (0x0020, 6), (0x0FFB, 12), (0x03FC, 10),
        (0x1FFA, 13), (0x0021, 6), (0x005D, 7), (0x005E, 7),
        (0x005F, 7), (0x0060, 7), (0x0061, 7), (0x0062, 7),
        (0x0063, 7), (0x0064, 7), (0x0065, 7), (0x0066, 7),
        (0x0067, 7), (0x0068, 7), (0x0069, 7), (0x006A, 7),
        (0x006B, 7), (0x006C, 7), (0x006D, 7), (0x006E, 7),
        (0x006F, 7), (0x0070, 7), (0x0071, 7), (0x0072, 7),
        (0x00FC, 8), (0x0073, 7), (0x00FD, 8), (0x1FFB, 13),
        (0x7FFF0, 19), (0x1FFC, 13), (0x3FFC, 14), (0x0022, 6),
        (0x7FFD, 15), (0x0003, 5), (0x0023, 6), (0x0004, 5),
        (0x0024, 6), (0x0005, 5), (0x0025, 6), (0x0026, 6),
        (0x0027, 6), (0x0006, 5), (0x0074, 7), (0x0075, 7),
        (0x0028, 6), (0x0029, 6), (0x002A, 6), (0x0007, 5),
        (0x002B, 6), (0x0076, 7), (0x002C, 6), (0x0008, 5),
        (0x0009, 5), (0x002D, 6), (0x0077, 7), (0x0078, 7),
        (0x0079, 7), (0x007A, 7), (0x007B, 7), (0x7FFE, 15),
        (0x07FC, 11), (0x3FFD, 14), (0x1FFD, 13), (0xFFFFFFC, 28),
        (0xFFFE6, 20), (0x3FFFD2, 22), (0xFFFE7, 20), (0xFFFE8, 20),
        (0x3FFFD3, 22), (0x3FFFD4, 22), (0x3FFFD5, 22), (0x7FFFD9, 23),
        (0x3FFFD6, 22), (0x7FFFDA, 23), (0x7FFFDB, 23), (0x7FFFDC, 23),
        (0x7FFFDD, 23), (0x7FFFDE, 23), (0xFFFFEB, 24), (0x7FFFDF, 23),
        (0xFFFFEC, 24), (0xFFFFED, 24), (0x3FFFD7, 22), (0x7FFFE0, 23),
        (0xFFFFEE, 24), (0x7FFFE1, 23), (0x7FFFE2, 23), (0x7FFFE3, 23),
        (0x7FFFE4, 23), (0x1FFFDC, 21), (0x3FFFD8, 22), (0x7FFFE5, 23),
        (0x3FFFD9, 22), (0x7FFFE6, 23), (0x7FFFE7, 23), (0xFFFFEF, 24),
        (0x3FFFDA, 22), (0x1FFFDD, 21), (0xFFFE9, 20), (0x3FFFDB, 22),
        (0x3FFFDC, 22), (0x7FFFE8, 23), (0x7FFFE9, 23), (0x1FFFDE, 21),
        (0x7FFFEA, 23), (0x3FFFDD, 22), (0x3FFFDE, 22), (0xFFFFF0, 24),
        (0x1FFFDF, 21), (0x3FFFDF, 22), (0x7FFFEB, 23), (0x7FFFEC, 23),
        (0x1FFFE0, 21), (0x1FFFE1, 21), (0x3FFFE0, 22), (0x1FFFE2, 21),
        (0x7FFFED, 23), (0x3FFFE1, 22), (0x7FFFEE, 23), (0x7FFFEF, 23),
        (0xFFFEA, 20), (0x3FFFE2, 22), (0x3FFFE3, 22), (0x3FFFE4, 22),
        (0x7FFFF0, 23), (0x3FFFE5, 22), (0x3FFFE6, 22), (0x7FFFF1, 23),
        (0x3FFFFE0, 26), (0x3FFFFE1, 26), (0xFFFEB, 20), (0x7FFF1, 19),
        (0x3FFFE7, 22), (0x7FFFF2, 23), (0x3FFFE8, 22), (0x1FFFFEC, 25),
        (0x3FFFFE2, 26), (0x3FFFFE3, 26), (0x3FFFFE4, 26), (0x7FFFFDE, 27),
        (0x7FFFFDF, 27), (0x3FFFFE5, 26), (0xFFFFF1, 24), (0x1FFFFED, 25),
        (0x7FFF2, 19), (0x1FFFE3, 21), (0x3FFFFE6, 26), (0x7FFFFE0, 27),
        (0x7FFFFE1, 27), (0x3FFFFE7, 26), (0x7FFFFE2, 27), (0xFFFFF2, 24),
        (0x1FFFE4, 21), (0x1FFFE5, 21), (0x3FFFFE8, 26), (0x3FFFFE9, 26),
        (0xFFFFFFD, 28), (0x7FFFFE3, 27), (0x7FFFFE4, 27), (0x7FFFFE5, 27),
        (0xFFFEC, 20), (0xFFFFF3, 24), (0xFFFED, 20), (0x1FFFE6, 21),
        (0x3FFFE9, 22), (0x1FFFE7, 21), (0x1FFFE8, 21), (0x7FFFF3, 23),
        (0x3FFFEA, 22), (0x3FFFEB, 22), (0x1FFFFEE, 25), (0x1FFFFEF, 25),
        (0xFFFFF4, 24), (0xFFFFF5, 24), (0x3FFFFEA, 26), (0x7FFFF4, 23),
        (0x3FFFFEB, 26), (0x7FFFFE6, 27), (0x3FFFFEC, 26), (0x3FFFFED, 26),
        (0x7FFFFE7, 27), (0x7FFFFE8, 27), (0x7FFFFE9, 27), (0x7FFFFEA, 27),
        (0x7FFFFEB, 27), (0xFFFFFFE, 28), (0x7FFFFEC, 27), (0x7FFFFED, 27),
        (0x7FFFFEE, 27), (0x7FFFFEF, 27), (0x7FFFFF0, 27), (0x3FFFFEE, 26),
        (0x3FFFFFFF, 30),
    };

    private struct TrieNode
    {
        public int Left;
        public int Right;
        public int Symbol; // -1 for internal, 0..256 for leaf
    }

    private static readonly TrieNode[] Trie = BuildTrie();

    private static TrieNode[] BuildTrie()
    {
        var nodes = new List<TrieNode>(514)
        {
            new() { Left = -1, Right = -1, Symbol = -1 }
        };

        for (int sym = 0; sym < Table.Length; sym++)
        {
            (uint code, byte bits) = Table[sym];
            int cur = 0;
            for (int b = bits - 1; b >= 0; b--)
            {
                int bit = (int)((code >> b) & 1U);
                TrieNode n = nodes[cur];
                int next = bit == 0 ? n.Left : n.Right;
                if (next < 0)
                {
                    next = nodes.Count;
                    nodes.Add(new TrieNode { Left = -1, Right = -1, Symbol = -1 });
                    if (bit == 0)
                        n.Left = next;
                    else
                        n.Right = next;
                    nodes[cur] = n;
                }
                cur = next;
            }
            TrieNode leaf = nodes[cur];
            leaf.Symbol = sym;
            nodes[cur] = leaf;
        }

        return nodes.ToArray();
    }

    public static int GetEncodedLength(ReadOnlySpan<byte> raw)
    {
        long totalBits = 0;
        for (int i = 0; i < raw.Length; i++)
            totalBits += Table[raw[i]].Bits;
        return (int)((totalBits + 7L) >> 3);
    }

    public static byte[] Encode(ReadOnlySpan<byte> raw)
    {
        if (raw.IsEmpty)
            return Array.Empty<byte>();

        var result = new List<byte>(GetEncodedLength(raw));
        ulong accum = 0;
        int bitCount = 0;

        for (int i = 0; i < raw.Length; i++)
        {
            (uint code, byte bits) = Table[raw[i]];
            accum = (accum << bits) | code;
            bitCount += bits;
            while (bitCount >= 8)
            {
                bitCount -= 8;
                result.Add((byte)(accum >> bitCount));
                accum &= (1UL << bitCount) - 1UL;
            }
        }

        if (bitCount > 0)
        {
            int padBits = 8 - bitCount;
            accum = (accum << padBits) | ((1UL << padBits) - 1UL);
            result.Add((byte)accum);
        }

        return result.ToArray();
    }

    public static string Decode(ReadOnlySpan<byte> encoded)
    {
        if (encoded.IsEmpty)
            return string.Empty;

        var bytes = new List<byte>(encoded.Length * 2);
        int node = 0;
        int bitsSinceLeaf = 0;
        int allOnesTail = 1;

        for (int i = 0; i < encoded.Length; i++)
        {
            byte b = encoded[i];
            for (int bitIdx = 7; bitIdx >= 0; bitIdx--)
            {
                int bit = (b >> bitIdx) & 1;
                bitsSinceLeaf++;
                allOnesTail &= bit;
                node = bit == 0 ? Trie[node].Left : Trie[node].Right;
                if (node < 0)
                    throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "Invalid QPACK Huffman bit sequence.");

                int sym = Trie[node].Symbol;
                if (sym >= 0)
                {
                    if (sym == 256)
                        throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "Illegal EOS symbol in QPACK Huffman string.");
                    bytes.Add((byte)sym);
                    node = 0;
                    bitsSinceLeaf = 0;
                    allOnesTail = 1;
                }
            }
        }

        if (bitsSinceLeaf > 7 || (bitsSinceLeaf > 0 && allOnesTail == 0))
            throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "Invalid QPACK Huffman padding.");

        return Encoding.UTF8.GetString(bytes.ToArray());
    }
}

/// <summary>RFC 9204 §4.1 integer and string prefix helpers.</summary>
internal static class QpackWirePrimitives
{
    public static void WriteInt(List<byte> dst, int prefixBits, byte firstByteMask, ulong value)
    {
        ulong maxPrefix = (1UL << prefixBits) - 1UL;
        if (value < maxPrefix)
        {
            dst.Add((byte)(firstByteMask | (byte)value));
            return;
        }

        dst.Add((byte)(firstByteMask | (byte)maxPrefix));
        value -= maxPrefix;
        while (value >= 128UL)
        {
            dst.Add((byte)((value & 0x7FUL) | 0x80UL));
            value >>= 7;
        }
        dst.Add((byte)value);
    }

    public static bool TryReadInt(ReadOnlySpan<byte> src, ref int offset, int prefixBits, out ulong value, ulong overflowErrorCode)
    {
        if (offset >= src.Length)
        {
            value = 0;
            return false;
        }

        ulong maxPrefix = (1UL << prefixBits) - 1UL;
        ulong initial = src[offset] & maxPrefix;
        int cursor = offset + 1;

        if (initial < maxPrefix)
        {
            offset = cursor;
            value = initial;
            return true;
        }

        ulong val = maxPrefix;
        int shift = 0;
        while (cursor < src.Length)
        {
            byte b = src[cursor++];
            if (shift > 56)
                throw new Http3Exception(overflowErrorCode, "QPACK integer exceeds 62-bit limit.");

            ulong add = ((ulong)(b & 0x7F)) << shift;
            if (val > QuicVarInt.MaxValue - add)
                throw new Http3Exception(overflowErrorCode, "QPACK integer overflow.");

            val += add;
            shift += 7;

            if ((b & 0x80) == 0)
            {
                offset = cursor;
                value = val;
                return true;
            }
        }

        value = 0;
        return false;
    }

    public static void WriteString(
        List<byte> dst,
        int prefixBits,
        byte huffmanBitMask,
        byte baseMask,
        string value,
        bool allowHuffman)
    {
        byte[] utf8 = string.IsNullOrEmpty(value) ? Array.Empty<byte>() : Encoding.UTF8.GetBytes(value);
        if (allowHuffman && utf8.Length > 0)
        {
            int hufLen = QpackHuffman.GetEncodedLength(utf8);
            if (hufLen < utf8.Length)
            {
                byte[] encoded = QpackHuffman.Encode(utf8);
                WriteInt(dst, prefixBits, (byte)(baseMask | huffmanBitMask), (ulong)encoded.Length);
                dst.AddRange(encoded);
                return;
            }
        }

        WriteInt(dst, prefixBits, baseMask, (ulong)utf8.Length);
        if (utf8.Length > 0)
            dst.AddRange(utf8);
    }

    public static bool TryReadString(
        ReadOnlySpan<byte> src,
        ref int offset,
        int prefixBits,
        byte huffmanBitMask,
        out string value,
        ulong errorCode)
    {
        if (offset >= src.Length)
        {
            value = string.Empty;
            return false;
        }

        int saved = offset;
        bool isHuffman = (src[offset] & huffmanBitMask) != 0;
        if (!TryReadInt(src, ref offset, prefixBits, out ulong len, errorCode))
        {
            offset = saved;
            value = string.Empty;
            return false;
        }

        if (len > (ulong)(src.Length - offset))
        {
            offset = saved;
            value = string.Empty;
            return false;
        }

        ReadOnlySpan<byte> strBytes = src.Slice(offset, (int)len);
        offset += (int)len;
        value = isHuffman ? QpackHuffman.Decode(strBytes) : Encoding.UTF8.GetString(strBytes);
        return true;
    }
}

/// <summary>RFC 9204 §3.2 QPACK dynamic header table with FIFO eviction and capacity enforcement.</summary>
public sealed class QpackDynamicTable
{
    private readonly Queue<(string Name, string Value, ulong Size)> _entries = new();
    private readonly List<PureHttpHeader> _indexed = new();

    public QpackDynamicTable(ulong maxAllowedCapacity = 65_536)
    {
        MaxAllowedCapacity = maxAllowedCapacity;
    }

    public ulong MaxAllowedCapacity { get; }
    public ulong Capacity { get; private set; }
    public ulong CurrentSize { get; private set; }
    public ulong InsertCount { get; private set; }
    public ulong DroppedCount { get; private set; }
    public int EntryCount => _entries.Count;

    public static ulong EntrySize(string name, string value) =>
        (ulong)Encoding.UTF8.GetByteCount(name) + (ulong)Encoding.UTF8.GetByteCount(value) + 32UL;

    public void SetCapacity(ulong newCapacity)
    {
        if (newCapacity > MaxAllowedCapacity)
        {
            throw new Http3Exception(
                Http3ErrorCode.QpackEncoderStreamError,
                $"QPACK dynamic table capacity {newCapacity} exceeds SETTINGS_QPACK_MAX_TABLE_CAPACITY {MaxAllowedCapacity}.");
        }

        Capacity = newCapacity;
        EvictToCapacity();
    }

    public void Insert(string name, string value)
    {
        ulong size = EntrySize(name, value);
        if (size > Capacity)
        {
            throw new Http3Exception(
                Http3ErrorCode.QpackEncoderStreamError,
                $"QPACK dynamic table entry size {size} exceeds current capacity {Capacity}.");
        }

        while (CurrentSize + size > Capacity && _entries.Count > 0)
            EvictOldest();

        _entries.Enqueue((name, value, size));
        _indexed.Add(new PureHttpHeader(name, value));
        CurrentSize += size;
        InsertCount++;
    }

    public void Duplicate(ulong relativeIndex)
    {
        if (relativeIndex >= InsertCount)
        {
            throw new Http3Exception(
                Http3ErrorCode.QpackEncoderStreamError,
                $"QPACK duplicate relative index {relativeIndex} out of range (InsertCount={InsertCount}).");
        }

        ulong abs = InsertCount - 1UL - relativeIndex;
        PureHttpHeader entry = GetByAbsoluteIndex(abs, Http3ErrorCode.QpackEncoderStreamError);
        Insert(entry.Name, entry.Value);
    }

    public PureHttpHeader GetByAbsoluteIndex(ulong absoluteIndex, ulong errorCode = Http3ErrorCode.QpackDecompressionFailed)
    {
        if (absoluteIndex < DroppedCount || absoluteIndex >= InsertCount)
        {
            throw new Http3Exception(
                errorCode,
                $"QPACK dynamic index {absoluteIndex} out of live range [{DroppedCount}, {InsertCount}).");
        }

        int listIdx = (int)(absoluteIndex - DroppedCount);
        return _indexed[listIdx];
    }

    public PureHttpHeader GetByRelativeIndex(ulong baseIndex, ulong relativeIndex)
    {
        if (relativeIndex >= baseIndex)
        {
            throw new Http3Exception(
                Http3ErrorCode.QpackDecompressionFailed,
                $"QPACK relative index {relativeIndex} >= Base {baseIndex}.");
        }

        ulong abs = baseIndex - 1UL - relativeIndex;
        return GetByAbsoluteIndex(abs);
    }

    public PureHttpHeader GetByPostBaseIndex(ulong baseIndex, ulong postBaseIndex, ulong requiredInsertCount)
    {
        ulong abs = baseIndex + postBaseIndex;
        if (abs >= requiredInsertCount)
        {
            throw new Http3Exception(
                Http3ErrorCode.QpackDecompressionFailed,
                $"QPACK post-base index {abs} >= RequiredInsertCount {requiredInsertCount}.");
        }

        return GetByAbsoluteIndex(abs);
    }

    private void EvictToCapacity()
    {
        while (CurrentSize > Capacity && _entries.Count > 0)
            EvictOldest();
    }

    private void EvictOldest()
    {
        (_, _, ulong size) = _entries.Dequeue();
        _indexed.RemoveAt(0);
        CurrentSize -= size;
        DroppedCount++;
    }
}

/// <summary>
/// QPACK encoder operating in static-table-only mode (<c>RequiredInsertCount = 0</c>, <c>DeltaBase = 0</c>)
/// matching <c>QpackEncoder</c> (<c>0x1412C7FC0</c>), plus RFC 9204 encoder instruction builders.
/// </summary>
public sealed class QpackEncoder
{
    public byte[] Encode(IReadOnlyList<PureHttpHeader> headers, bool useHuffman = true)
    {
        ArgumentNullException.ThrowIfNull(headers);
        var buf = new List<byte>(headers.Count * 24 + 4);

        // Required Insert Count = 0, S = 0, Delta Base = 0
        buf.Add(0x00);
        buf.Add(0x00);

        for (int i = 0; i < headers.Count; i++)
        {
            string name = headers[i].Name.ToLowerInvariant();
            string value = headers[i].Value;

            if (QpackStaticTable.TryFindExact(name, value, out int exactIdx))
            {
                // 4.5.2 Indexed Field Line (1 | T=1 | Index(6+))
                QpackWirePrimitives.WriteInt(buf, 6, 0xC0, (ulong)exactIdx);
            }
            else if (QpackStaticTable.TryFindName(name, out int nameIdx))
            {
                // 4.5.4 Literal Field Line with Name Reference (01 | N=0 | T=1 | NameIndex(4+))
                QpackWirePrimitives.WriteInt(buf, 4, 0x50, (ulong)nameIdx);
                QpackWirePrimitives.WriteString(buf, 7, 0x80, 0x00, value, useHuffman);
            }
            else
            {
                // 4.5.6 Literal Field Line with Literal Name (001 | N=0 | H | NameLen(3+))
                QpackWirePrimitives.WriteString(buf, 3, 0x08, 0x20, name, useHuffman);
                QpackWirePrimitives.WriteString(buf, 7, 0x80, 0x00, value, useHuffman);
            }
        }

        return buf.ToArray();
    }

    public static byte[] EncodeSetCapacityInstruction(ulong capacity)
    {
        var buf = new List<byte>(4);
        QpackWirePrimitives.WriteInt(buf, 5, 0x20, capacity);
        return buf.ToArray();
    }

    public static byte[] EncodeInsertWithNameRefInstruction(bool isStatic, ulong nameIndex, string value, bool useHuffman = true)
    {
        var buf = new List<byte>(16 + value.Length);
        byte mask = isStatic ? (byte)0xC0 : (byte)0x80;
        QpackWirePrimitives.WriteInt(buf, 6, mask, nameIndex);
        QpackWirePrimitives.WriteString(buf, 7, 0x80, 0x00, value, useHuffman);
        return buf.ToArray();
    }

    public static byte[] EncodeInsertWithoutNameRefInstruction(string name, string value, bool useHuffman = true)
    {
        var buf = new List<byte>(16 + name.Length + value.Length);
        QpackWirePrimitives.WriteString(buf, 5, 0x20, 0x40, name.ToLowerInvariant(), useHuffman);
        QpackWirePrimitives.WriteString(buf, 7, 0x80, 0x00, value, useHuffman);
        return buf.ToArray();
    }

    public static byte[] EncodeDuplicateInstruction(ulong relativeIndex)
    {
        var buf = new List<byte>(4);
        QpackWirePrimitives.WriteInt(buf, 5, 0x00, relativeIndex);
        return buf.ToArray();
    }

    public static byte[] EncodeFieldSectionPrefix(ulong requiredInsertCount, ulong baseIndex, ulong maxTableCapacity)
    {
        var buf = new List<byte>(4);
        if (requiredInsertCount == 0)
        {
            buf.Add(0x00);
            buf.Add(0x00);
            return buf.ToArray();
        }

        ulong maxEntries = maxTableCapacity / 32UL;
        ulong encodedRic = (requiredInsertCount % (2UL * maxEntries)) + 1UL;
        QpackWirePrimitives.WriteInt(buf, 8, 0x00, encodedRic);

        if (baseIndex >= requiredInsertCount)
            QpackWirePrimitives.WriteInt(buf, 7, 0x00, baseIndex - requiredInsertCount);
        else
            QpackWirePrimitives.WriteInt(buf, 7, 0x80, requiredInsertCount - baseIndex - 1UL);

        return buf.ToArray();
    }
}

/// <summary>
/// Full RFC 9204 QPACK decoder supporting static + dynamic tables, streaming encoder instructions,
/// blocked-stream synchronization, and decoder feedback instructions matching <c>QpackDecoder</c>.
/// </summary>
public sealed class QpackDecoder
{
    private readonly object _lock = new();
    private readonly List<byte> _encoderStreamBuf = new();
    private readonly List<(ulong TargetInsertCount, TaskCompletionSource<bool> Tcs)> _insertWaiters = new();
    private int _blockedStreamsCount;
    private bool _encoderStreamClosed;

    public QpackDecoder(
        ulong maxTableCapacity = 65_536,
        ulong maxBlockedStreams = 100,
        ulong maxFieldSectionSize = 262_144)
    {
        DynamicTable = new QpackDynamicTable(maxTableCapacity);
        MaxBlockedStreams = maxBlockedStreams;
        MaxFieldSectionSize = maxFieldSectionSize;
    }

    public QpackDynamicTable DynamicTable { get; }
    public ulong MaxBlockedStreams { get; }
    public ulong MaxFieldSectionSize { get; }
    public ulong KnownReceivedCount { get; private set; }

    /// <summary>
    /// Feeds raw bytes from the peer's QPACK Encoder unidirectional stream (<c>0x02</c>),
    /// executing all complete instructions and returning any decoder <c>InsertCountIncrement</c> feedback bytes.
    /// </summary>
    public byte[] ProcessEncoderInstructions(ReadOnlySpan<byte> chunk)
    {
        ulong insertedDelta = 0;
        List<TaskCompletionSource<bool>>? readyWaiters = null;

        lock (_lock)
        {
            for (int i = 0; i < chunk.Length; i++)
                _encoderStreamBuf.Add(chunk[i]);

            ReadOnlySpan<byte> buf = _encoderStreamBuf.ToArray();
            int offset = 0;

            while (offset < buf.Length)
            {
                int saved = offset;
                byte first = buf[offset];

                if ((first & 0x80) != 0)
                {
                    // 4.3.2 Insert with Name Reference: 1 | T | NameIndex(6+) + Value
                    bool isStatic = (first & 0x40) != 0;
                    if (!QpackWirePrimitives.TryReadInt(buf, ref offset, 6, out ulong nameIdx, Http3ErrorCode.QpackEncoderStreamError) ||
                        !QpackWirePrimitives.TryReadString(buf, ref offset, 7, 0x80, out string val, Http3ErrorCode.QpackEncoderStreamError))
                    {
                        offset = saved;
                        break;
                    }

                    string name;
                    if (isStatic)
                    {
                        if (nameIdx >= (ulong)QpackStaticTable.Entries.Count)
                            throw new Http3Exception(Http3ErrorCode.QpackEncoderStreamError, $"Invalid QPACK static name index {nameIdx}.");
                        name = QpackStaticTable.Entries[(int)nameIdx].Name;
                    }
                    else
                    {
                        if (nameIdx >= DynamicTable.InsertCount)
                            throw new Http3Exception(Http3ErrorCode.QpackEncoderStreamError, $"Invalid QPACK dynamic relative name index {nameIdx}.");
                        ulong abs = DynamicTable.InsertCount - 1UL - nameIdx;
                        name = DynamicTable.GetByAbsoluteIndex(abs, Http3ErrorCode.QpackEncoderStreamError).Name;
                    }

                    DynamicTable.Insert(name, val);
                    insertedDelta++;
                }
                else if ((first & 0x40) != 0)
                {
                    // 4.3.3 Insert with Literal Name: 01 | H | NameLen(5+) + Name + Value
                    if (!QpackWirePrimitives.TryReadString(buf, ref offset, 5, 0x20, out string name, Http3ErrorCode.QpackEncoderStreamError) ||
                        !QpackWirePrimitives.TryReadString(buf, ref offset, 7, 0x80, out string val, Http3ErrorCode.QpackEncoderStreamError))
                    {
                        offset = saved;
                        break;
                    }

                    DynamicTable.Insert(name, val);
                    insertedDelta++;
                }
                else if ((first & 0x20) != 0)
                {
                    // 4.3.1 Set Dynamic Table Capacity: 001 | Capacity(5+)
                    if (!QpackWirePrimitives.TryReadInt(buf, ref offset, 5, out ulong capacity, Http3ErrorCode.QpackEncoderStreamError))
                    {
                        offset = saved;
                        break;
                    }
                    DynamicTable.SetCapacity(capacity);
                }
                else
                {
                    // 4.3.4 Duplicate: 000 | Index(5+)
                    if (!QpackWirePrimitives.TryReadInt(buf, ref offset, 5, out ulong relIdx, Http3ErrorCode.QpackEncoderStreamError))
                    {
                        offset = saved;
                        break;
                    }
                    DynamicTable.Duplicate(relIdx);
                    insertedDelta++;
                }
            }

            if (offset > 0)
                _encoderStreamBuf.RemoveRange(0, offset);

            if (insertedDelta > 0)
            {
                KnownReceivedCount = DynamicTable.InsertCount;
                for (int i = _insertWaiters.Count - 1; i >= 0; i--)
                {
                    if (DynamicTable.InsertCount >= _insertWaiters[i].TargetInsertCount)
                    {
                        readyWaiters ??= new List<TaskCompletionSource<bool>>();
                        readyWaiters.Add(_insertWaiters[i].Tcs);
                        _insertWaiters.RemoveAt(i);
                    }
                }
            }
        }

        if (readyWaiters is not null)
        {
            for (int i = 0; i < readyWaiters.Count; i++)
                readyWaiters[i].TrySetResult(true);
        }

        if (insertedDelta == 0)
            return Array.Empty<byte>();

        var feedback = new List<byte>(4);
        QpackWirePrimitives.WriteInt(feedback, 6, 0x00, insertedDelta); // 4.4.3 Insert Count Increment
        return feedback.ToArray();
    }

    public bool HasTrailingEncoderBytes
    {
        get { lock (_lock) return _encoderStreamBuf.Count > 0; }
    }

    public void MarkEncoderStreamClosed()
    {
        List<TaskCompletionSource<bool>> waiters;
        lock (_lock)
        {
            _encoderStreamClosed = true;
            waiters = new List<TaskCompletionSource<bool>>(_insertWaiters.Count);
            for (int i = 0; i < _insertWaiters.Count; i++)
                waiters.Add(_insertWaiters[i].Tcs);
            _insertWaiters.Clear();
        }

        var ex = new Http3Exception(Http3ErrorCode.ClosedCriticalStream, "http3: peer closed QPACK encoder stream.");
        for (int i = 0; i < waiters.Count; i++)
            waiters[i].TrySetException(ex);
    }

    public List<PureHttpHeader> DecodeFieldSection(ReadOnlySpan<byte> block, out ulong requiredInsertCount)
    {
        lock (_lock)
        {
            return DecodeFieldSectionCoreLocked(block, out requiredInsertCount);
        }
    }

    public async Task<(List<PureHttpHeader> Headers, ulong RequiredInsertCount)> DecodeFieldSectionWithCountAsync(
        ReadOnlyMemory<byte> block,
        CancellationToken cancellationToken = default)
    {
        ulong reqInsertCount;
        TaskCompletionSource<bool>? waiter = null;
        bool countedAsBlocked = false;

        List<PureHttpHeader>? immediate = null;
        lock (_lock)
        {
            int off = 0;
            reqInsertCount = DecodeRequiredInsertCountLocked(block.Span, ref off);
            if (reqInsertCount <= DynamicTable.InsertCount)
            {
                immediate = DecodeFieldSectionCoreLocked(block.Span, out reqInsertCount);
            }
            else
            {
                if (_encoderStreamClosed)
                    throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "QPACK encoder stream closed before required dynamic entries arrived.");

                if ((ulong)_blockedStreamsCount >= MaxBlockedStreams)
                    throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, $"QPACK blocked streams exceeded limit {MaxBlockedStreams}.");

                _blockedStreamsCount++;
                countedAsBlocked = true;
                waiter = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
                _insertWaiters.Add((reqInsertCount, waiter));
            }
        }

        if (immediate is not null)
            return (immediate, reqInsertCount);

        try
        {
            await waiter!.Task.WaitAsync(cancellationToken).ConfigureAwait(false);
        }
        finally
        {
            if (countedAsBlocked)
            {
                lock (_lock)
                    _blockedStreamsCount--;
            }
        }

        List<PureHttpHeader> headers;
        lock (_lock)
        {
            headers = DecodeFieldSectionCoreLocked(block.Span, out reqInsertCount);
        }

        return (headers, reqInsertCount);
    }

    public async Task<List<PureHttpHeader>> DecodeFieldSectionAsync(
        ulong streamId,
        ReadOnlyMemory<byte> block,
        Stream? decoderStream,
        CancellationToken cancellationToken = default)
    {
        (List<PureHttpHeader> headers, ulong reqInsertCount) = await DecodeFieldSectionWithCountAsync(block, cancellationToken).ConfigureAwait(false);
        if (reqInsertCount > 0 && decoderStream is not null)
        {
            byte[] ack = BuildSectionAcknowledgment(streamId);
            await decoderStream.WriteAsync(ack, cancellationToken).ConfigureAwait(false);
        }
        return headers;
    }

    public static byte[] BuildSectionAcknowledgment(ulong streamId)
    {
        var buf = new List<byte>(4);
        QpackWirePrimitives.WriteInt(buf, 7, 0x80, streamId);
        return buf.ToArray();
    }

    public static byte[] BuildStreamCancellation(ulong streamId)
    {
        var buf = new List<byte>(4);
        QpackWirePrimitives.WriteInt(buf, 6, 0x40, streamId);
        return buf.ToArray();
    }

    private ulong DecodeRequiredInsertCountLocked(ReadOnlySpan<byte> block, ref int offset)
    {
        if (!QpackWirePrimitives.TryReadInt(block, ref offset, 8, out ulong encodedRic, Http3ErrorCode.QpackDecompressionFailed))
            throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "Truncated QPACK Required Insert Count.");

        if (encodedRic == 0)
            return 0UL;

        ulong maxEntries = DynamicTable.MaxAllowedCapacity / 32UL;
        if (maxEntries == 0)
            throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "QPACK dynamic table references forbidden when max capacity < 32.");

        ulong fullRange = 2UL * maxEntries;
        if (encodedRic > fullRange)
            throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, $"Encoded Required Insert Count {encodedRic} exceeds 2*MaxEntries {fullRange}.");

        ulong maxValue = DynamicTable.InsertCount + maxEntries;
        ulong maxWrapped = (maxValue / fullRange) * fullRange;
        ulong ric = maxWrapped + encodedRic - 1UL;
        if (ric > maxValue)
        {
            if (ric <= fullRange)
                throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "Invalid wrapped QPACK Required Insert Count.");
            ric -= fullRange;
        }

        if (ric == 0)
            throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "Decoded non-zero QPACK Required Insert Count cannot be 0.");

        return ric;
    }

    private List<PureHttpHeader> DecodeFieldSectionCoreLocked(ReadOnlySpan<byte> block, out ulong requiredInsertCount)
    {
        int offset = 0;
        requiredInsertCount = DecodeRequiredInsertCountLocked(block, ref offset);
        if (requiredInsertCount > DynamicTable.InsertCount)
        {
            throw new Http3Exception(
                Http3ErrorCode.QpackDecompressionFailed,
                $"QPACK RequiredInsertCount {requiredInsertCount} exceeds current InsertCount {DynamicTable.InsertCount}.");
        }

        if (offset >= block.Length)
            throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "Truncated QPACK Delta Base.");

        bool sign = (block[offset] & 0x80) != 0;
        if (!QpackWirePrimitives.TryReadInt(block, ref offset, 7, out ulong deltaBase, Http3ErrorCode.QpackDecompressionFailed))
            throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "Truncated QPACK Delta Base.");

        ulong baseIndex;
        if (!sign)
        {
            baseIndex = requiredInsertCount + deltaBase;
        }
        else
        {
            if (deltaBase >= requiredInsertCount)
                throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "QPACK negative Delta Base underflows RequiredInsertCount.");
            baseIndex = requiredInsertCount - deltaBase - 1UL;
        }

        var headers = new List<PureHttpHeader>();
        ulong totalFieldSectionBytes = 0;

        while (offset < block.Length)
        {
            byte first = block[offset];
            PureHttpHeader header;

            if ((first & 0x80) != 0)
            {
                // 4.5.2 Indexed Field Line: 1 | T | Index(6+)
                bool isStatic = (first & 0x40) != 0;
                if (!QpackWirePrimitives.TryReadInt(block, ref offset, 6, out ulong idx, Http3ErrorCode.QpackDecompressionFailed))
                    throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "Truncated QPACK Indexed Field Line.");

                if (isStatic)
                {
                    if (idx >= (ulong)QpackStaticTable.Entries.Count)
                        throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, $"Invalid QPACK static index {idx}.");
                    header = QpackStaticTable.Entries[(int)idx];
                }
                else
                {
                    header = DynamicTable.GetByRelativeIndex(baseIndex, idx);
                }
            }
            else if ((first & 0x40) != 0)
            {
                // 4.5.4 Literal Field Line with Name Reference: 01 | N | T | NameIndex(4+) + Value
                bool isStatic = (first & 0x10) != 0;
                if (!QpackWirePrimitives.TryReadInt(block, ref offset, 4, out ulong nameIdx, Http3ErrorCode.QpackDecompressionFailed) ||
                    !QpackWirePrimitives.TryReadString(block, ref offset, 7, 0x80, out string val, Http3ErrorCode.QpackDecompressionFailed))
                {
                    throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "Truncated QPACK Literal Field Line with Name Reference.");
                }

                string name;
                if (isStatic)
                {
                    if (nameIdx >= (ulong)QpackStaticTable.Entries.Count)
                        throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, $"Invalid QPACK static name index {nameIdx}.");
                    name = QpackStaticTable.Entries[(int)nameIdx].Name;
                }
                else
                {
                    name = DynamicTable.GetByRelativeIndex(baseIndex, nameIdx).Name;
                }
                header = new PureHttpHeader(name, val);
            }
            else if ((first & 0x20) != 0)
            {
                // 4.5.6 Literal Field Line with Literal Name: 001 | N | H | NameLen(3+) + Value
                if (!QpackWirePrimitives.TryReadString(block, ref offset, 3, 0x08, out string name, Http3ErrorCode.QpackDecompressionFailed) ||
                    !QpackWirePrimitives.TryReadString(block, ref offset, 7, 0x80, out string val, Http3ErrorCode.QpackDecompressionFailed))
                {
                    throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "Truncated QPACK Literal Field Line with Literal Name.");
                }
                header = new PureHttpHeader(name, val);
            }
            else if ((first & 0x10) != 0)
            {
                // 4.5.3 Indexed Field Line with Post-Base Index: 0001 | Index(4+)
                if (!QpackWirePrimitives.TryReadInt(block, ref offset, 4, out ulong pbIdx, Http3ErrorCode.QpackDecompressionFailed))
                    throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "Truncated QPACK Post-Base Indexed Field Line.");
                header = DynamicTable.GetByPostBaseIndex(baseIndex, pbIdx, requiredInsertCount);
            }
            else
            {
                // 4.5.5 Literal Field Line with Post-Base Name Reference: 0000 | N | NameIndex(3+) + Value
                if (!QpackWirePrimitives.TryReadInt(block, ref offset, 3, out ulong pbNameIdx, Http3ErrorCode.QpackDecompressionFailed) ||
                    !QpackWirePrimitives.TryReadString(block, ref offset, 7, 0x80, out string val, Http3ErrorCode.QpackDecompressionFailed))
                {
                    throw new Http3Exception(Http3ErrorCode.QpackDecompressionFailed, "Truncated QPACK Post-Base Name Reference.");
                }
                string name = DynamicTable.GetByPostBaseIndex(baseIndex, pbNameIdx, requiredInsertCount).Name;
                header = new PureHttpHeader(name, val);
            }

            totalFieldSectionBytes += QpackDynamicTable.EntrySize(header.Name, header.Value);
            if (totalFieldSectionBytes > MaxFieldSectionSize)
            {
                throw new Http3Exception(
                    Http3ErrorCode.ExcessiveLoad,
                    $"HTTP/3 field section size {totalFieldSectionBytes} exceeds SETTINGS_MAX_FIELD_SECTION_SIZE {MaxFieldSectionSize}.");
            }

            headers.Add(header);
        }

        return headers;
    }
}
