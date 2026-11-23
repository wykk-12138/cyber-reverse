using System.Globalization;
using System.Text;
using Cybersole.Http.Profiles;

namespace Cybersole.Http.Protocol;

public enum HpackHuffmanMode
{
    IfSmaller = 0,
    Never = 1,
    Always = 2,
}

/// <summary>RFC 7541 Appendix A 61-entry static header table (1-based indices 1..61).</summary>
public static class HpackStaticTable
{
    public static readonly IReadOnlyList<PureHttpHeader> Entries = Array.AsReadOnly(new PureHttpHeader[]
    {
        new(":authority", string.Empty),                   // 1
        new(":method", "GET"),                             // 2
        new(":method", "POST"),                            // 3
        new(":path", "/"),                                 // 4
        new(":path", "/index.html"),                       // 5
        new(":scheme", "http"),                            // 6
        new(":scheme", "https"),                           // 7
        new(":status", "200"),                             // 8
        new(":status", "204"),                             // 9
        new(":status", "206"),                             // 10
        new(":status", "304"),                             // 11
        new(":status", "400"),                             // 12
        new(":status", "404"),                             // 13
        new(":status", "500"),                             // 14
        new("accept-charset", string.Empty),               // 15
        new("accept-encoding", "gzip, deflate"),           // 16
        new("accept-language", string.Empty),              // 17
        new("accept-ranges", string.Empty),                // 18
        new("accept", string.Empty),                       // 19
        new("access-control-allow-origin", string.Empty),  // 20
        new("age", string.Empty),                          // 21
        new("allow", string.Empty),                        // 22
        new("authorization", string.Empty),                // 23
        new("cache-control", string.Empty),                // 24
        new("content-disposition", string.Empty),          // 25
        new("content-encoding", string.Empty),             // 26
        new("content-language", string.Empty),             // 27
        new("content-length", string.Empty),               // 28
        new("content-location", string.Empty),             // 29
        new("content-range", string.Empty),                // 30
        new("content-type", string.Empty),                 // 31
        new("cookie", string.Empty),                       // 32
        new("date", string.Empty),                         // 33
        new("etag", string.Empty),                         // 34
        new("expect", string.Empty),                       // 35
        new("expires", string.Empty),                      // 36
        new("from", string.Empty),                         // 37
        new("host", string.Empty),                         // 38
        new("if-match", string.Empty),                     // 39
        new("if-modified-since", string.Empty),            // 40
        new("if-none-match", string.Empty),                // 41
        new("if-range", string.Empty),                     // 42
        new("if-unmodified-since", string.Empty),          // 43
        new("last-modified", string.Empty),                // 44
        new("link", string.Empty),                         // 45
        new("location", string.Empty),                     // 46
        new("max-forwards", string.Empty),                 // 47
        new("proxy-authenticate", string.Empty),           // 48
        new("proxy-authorization", string.Empty),          // 49
        new("range", string.Empty),                        // 50
        new("referer", string.Empty),                      // 51
        new("refresh", string.Empty),                      // 52
        new("retry-after", string.Empty),                  // 53
        new("server", string.Empty),                       // 54
        new("set-cookie", string.Empty),                   // 55
        new("strict-transport-security", string.Empty),    // 56
        new("transfer-encoding", string.Empty),            // 57
        new("user-agent", string.Empty),                   // 58
        new("vary", string.Empty),                         // 59
        new("via", string.Empty),                          // 60
        new("www-authenticate", string.Empty),             // 61
    });

    public const int Count = 61;

    private static readonly Dictionary<string, int> NameLookup = BuildNameLookup();

    private static Dictionary<string, int> BuildNameLookup()
    {
        var map = new Dictionary<string, int>(Count, StringComparer.Ordinal);
        for (int i = 0; i < Entries.Count; i++)
            map.TryAdd(Entries[i].Name, i + 1);
        return map;
    }

    public static bool TryGet(int oneBasedIndex, out PureHttpHeader entry)
    {
        if (oneBasedIndex >= 1 && oneBasedIndex <= Entries.Count)
        {
            entry = Entries[oneBasedIndex - 1];
            return true;
        }
        entry = default;
        return false;
    }

    public static int Find(string name, string value, out bool exactValueMatch)
    {
        for (int i = 0; i < Entries.Count; i++)
        {
            PureHttpHeader e = Entries[i];
            if (string.Equals(e.Name, name, StringComparison.Ordinal) &&
                string.Equals(e.Value, value, StringComparison.Ordinal))
            {
                exactValueMatch = true;
                return i + 1;
            }
        }

        if (NameLookup.TryGetValue(name, out int idx))
        {
            exactValueMatch = false;
            return idx;
        }

        exactValueMatch = false;
        return 0;
    }
}

/// <summary>
/// Full RFC 7541 Appendix B canonical Huffman encoder and strict validating decoder (256 symbols + EOS).
/// </summary>
public static class HpackHuffmanCodec
{
    private const uint H2CompressionError = 9;

    // 257 entries: symbols 0..255 + EOS symbol 256 (0x3FFFFFFF, 30 bits).
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
        (0x3FFFFFFF, 30), // 256 = EOS
    };

    private static readonly int[] TrieLeft;
    private static readonly int[] TrieRight;
    private static readonly short[] TrieSymbol;

    static HpackHuffmanCodec()
    {
        var left = new List<int>(520) { -1 };
        var right = new List<int>(520) { -1 };
        var sym = new List<short>(520) { -1 };

        for (int s = 0; s < Table.Length; s++)
        {
            (uint code, byte bits) = Table[s];
            int node = 0;
            for (int shift = bits - 1; shift >= 0; shift--)
            {
                int bit = (int)((code >> shift) & 1U);
                int next = bit == 0 ? left[node] : right[node];
                if (next < 0)
                {
                    next = sym.Count;
                    left.Add(-1);
                    right.Add(-1);
                    sym.Add(-1);
                    if (bit == 0)
                        left[node] = next;
                    else
                        right[node] = next;
                }
                node = next;
            }
            sym[node] = (short)s;
        }

        TrieLeft = left.ToArray();
        TrieRight = right.ToArray();
        TrieSymbol = sym.ToArray();
    }

    public static int GetEncodedLength(ReadOnlySpan<byte> input)
    {
        long totalBits = 0;
        for (int i = 0; i < input.Length; i++)
            totalBits += Table[input[i]].Bits;
        return (int)((totalBits + 7) >> 3);
    }

    public static byte[] Encode(ReadOnlySpan<byte> input)
    {
        int outLen = GetEncodedLength(input);
        var output = new byte[outLen];
        int outIdx = 0;
        ulong acc = 0;
        int accBits = 0;

        for (int i = 0; i < input.Length; i++)
        {
            (uint code, byte bits) = Table[input[i]];
            acc = (acc << bits) | code;
            accBits += bits;

            while (accBits >= 8)
            {
                accBits -= 8;
                output[outIdx++] = (byte)(acc >> accBits);
            }
        }

        if (accBits > 0)
        {
            int padBits = 8 - accBits;
            uint eosPrefix = (1U << padBits) - 1U;
            output[outIdx] = (byte)((acc << padBits) | eosPrefix);
        }

        return output;
    }

    public static byte[] Decode(ReadOnlySpan<byte> encoded)
    {
        if (encoded.IsEmpty)
            return Array.Empty<byte>();

        var output = new List<byte>(encoded.Length * 2);
        int node = 0;
        int bitsSinceSymbol = 0;
        bool allOnesSinceSymbol = true;

        for (int i = 0; i < encoded.Length; i++)
        {
            byte b = encoded[i];
            for (int shift = 7; shift >= 0; shift--)
            {
                int bit = (b >> shift) & 1;
                bitsSinceSymbol++;
                if (bit == 0)
                    allOnesSinceSymbol = false;

                node = bit == 0 ? TrieLeft[node] : TrieRight[node];
                if (node < 0)
                    throw new Http2Exception(H2CompressionError, isStreamReset: false, "Invalid HPACK Huffman code sequence.");

                short symbol = TrieSymbol[node];
                if (symbol >= 0)
                {
                    if (symbol == 256)
                        throw new Http2Exception(H2CompressionError, isStreamReset: false, "HPACK Huffman string contains forbidden EOS symbol.");

                    output.Add((byte)symbol);
                    node = 0;
                    bitsSinceSymbol = 0;
                    allOnesSinceSymbol = true;
                }
            }
        }

        if (bitsSinceSymbol >= 8)
            throw new Http2Exception(H2CompressionError, isStreamReset: false, "HPACK Huffman trailing padding exceeds 7 bits.");

        if (bitsSinceSymbol > 0 && !allOnesSinceSymbol)
            throw new Http2Exception(H2CompressionError, isStreamReset: false, "Invalid HPACK Huffman trailing padding (must be 1-bits).");

        return output.ToArray();
    }
}

/// <summary>RFC 7541 §5.1 integer prefix codec for N in [1..8].</summary>
public static class HpackIntegerCodec
{
    private const uint H2CompressionError = 9;

    public static void Encode(List<byte> destination, uint value, int prefixBits, byte prefixMask)
    {
        ArgumentNullException.ThrowIfNull(destination);
        if (prefixBits is < 1 or > 8)
            throw new ArgumentOutOfRangeException(nameof(prefixBits), "HPACK integer prefix must be between 1 and 8 bits.");

        uint maxPrefix = (1U << prefixBits) - 1U;
        if (value < maxPrefix)
        {
            destination.Add((byte)(prefixMask | value));
            return;
        }

        destination.Add((byte)(prefixMask | maxPrefix));
        value -= maxPrefix;
        while (value >= 128U)
        {
            destination.Add((byte)((value & 0x7FU) | 0x80U));
            value >>= 7;
        }
        destination.Add((byte)value);
    }

    public static uint Decode(ReadOnlySpan<byte> source, ref int offset, int prefixBits)
    {
        if (prefixBits is < 1 or > 8)
            throw new ArgumentOutOfRangeException(nameof(prefixBits), "HPACK integer prefix must be between 1 and 8 bits.");
        if (offset >= source.Length)
            throw new Http2Exception(H2CompressionError, isStreamReset: false, "Truncated HPACK integer.");

        uint maxPrefix = (1U << prefixBits) - 1U;
        uint value = source[offset++] & maxPrefix;
        if (value < maxPrefix)
            return value;

        int shift = 0;
        while (true)
        {
            if (offset >= source.Length)
                throw new Http2Exception(H2CompressionError, isStreamReset: false, "Truncated HPACK multi-byte integer.");

            byte b = source[offset++];
            if (shift >= 28 && ((b & 0x7FU) > 0x0FU || (ulong)value + ((ulong)(b & 0x7FU) << shift) > uint.MaxValue))
                throw new Http2Exception(H2CompressionError, isStreamReset: false, "HPACK integer overflow.");

            uint addend = (uint)(b & 0x7F) << shift;
            if (uint.MaxValue - value < addend)
                throw new Http2Exception(H2CompressionError, isStreamReset: false, "HPACK integer overflow.");

            value += addend;
            if ((b & 0x80) == 0)
                return value;

            shift += 7;
        }
    }
}

internal sealed class HpackDynamicTable
{
    private readonly List<(string Name, string Value, int Size)> _entries = new();
    private int _maxSize;
    private int _currentSize;

    public HpackDynamicTable(int maxSize = 4096)
    {
        if (maxSize < 0)
            throw new ArgumentOutOfRangeException(nameof(maxSize));
        _maxSize = maxSize;
    }

    public int MaxSize => _maxSize;
    public int CurrentSize => _currentSize;
    public int Count => _entries.Count;

    public void SetMaxSize(int newMaxSize)
    {
        if (newMaxSize < 0)
            throw new ArgumentOutOfRangeException(nameof(newMaxSize));

        _maxSize = newMaxSize;
        EvictToFit(0);
    }

    public void Insert(string name, string value)
    {
        int entrySize = ComputeEntrySize(name, value);
        if (entrySize > _maxSize)
        {
            _entries.Clear();
            _currentSize = 0;
            return;
        }

        EvictToFit(entrySize);
        _entries.Add((name, value, entrySize));
        _currentSize += entrySize;
    }

    public bool TryGet(int zeroBasedNewestFirstIndex, out PureHttpHeader header)
    {
        if (zeroBasedNewestFirstIndex >= 0 && zeroBasedNewestFirstIndex < _entries.Count)
        {
            var e = _entries[_entries.Count - 1 - zeroBasedNewestFirstIndex];
            header = new PureHttpHeader(e.Name, e.Value);
            return true;
        }

        header = default;
        return false;
    }

    public int Find(string name, string value, out bool exactValueMatch)
    {
        int nameMatchIndex = 0;
        for (int i = _entries.Count - 1; i >= 0; i--)
        {
            var e = _entries[i];
            int hpackIndex = HpackStaticTable.Count + (_entries.Count - i);
            if (string.Equals(e.Name, name, StringComparison.Ordinal))
            {
                if (string.Equals(e.Value, value, StringComparison.Ordinal))
                {
                    exactValueMatch = true;
                    return hpackIndex;
                }
                if (nameMatchIndex == 0)
                    nameMatchIndex = hpackIndex;
            }
        }

        exactValueMatch = false;
        return nameMatchIndex;
    }

    public List<PureHttpHeader> SnapshotNewestFirst()
    {
        var result = new List<PureHttpHeader>(_entries.Count);
        for (int i = _entries.Count - 1; i >= 0; i--)
            result.Add(new PureHttpHeader(_entries[i].Name, _entries[i].Value));
        return result;
    }

    public static int ComputeEntrySize(string name, string value)
        => Encoding.UTF8.GetByteCount(name) + Encoding.UTF8.GetByteCount(value) + 32;

    private void EvictToFit(int incomingSize)
    {
        while (_entries.Count > 0 && _currentSize + incomingSize > _maxSize)
        {
            _currentSize -= _entries[0].Size;
            _entries.RemoveAt(0);
        }
    }
}

/// <summary>
/// Full RFC 7541 HPACK header block decoder supporting dynamic table updates (<c>0x20..0x3F</c>),
/// Huffman &amp; literal strings, <c>MaxHeaderListSize</c> enforcement, and RFC 9113 header validation.
/// </summary>
public sealed class HpackDecoder
{
    private const uint H2ProtocolError = 1;
    private const uint H2CompressionError = 9;

    private readonly HpackDynamicTable _dynamicTable;
    private int _maxAllowedDynamicTableSize;

    public HpackDecoder(int maxAllowedDynamicTableSize = 4096, int maxHeaderListSize = 262_144)
    {
        if (maxAllowedDynamicTableSize < 0)
            throw new ArgumentOutOfRangeException(nameof(maxAllowedDynamicTableSize));
        if (maxHeaderListSize <= 0)
            throw new ArgumentOutOfRangeException(nameof(maxHeaderListSize));

        _maxAllowedDynamicTableSize = maxAllowedDynamicTableSize;
        MaxHeaderListSize = maxHeaderListSize;
        _dynamicTable = new HpackDynamicTable(maxAllowedDynamicTableSize);
    }

    public int MaxAllowedDynamicTableSize => _maxAllowedDynamicTableSize;
    public int CurrentDynamicTableMaxSize => _dynamicTable.MaxSize;
    public int CurrentDynamicTableSize => _dynamicTable.CurrentSize;
    public int DynamicTableCount => _dynamicTable.Count;
    public int MaxHeaderListSize { get; set; }

    public IReadOnlyList<PureHttpHeader> GetDynamicTableEntries() => _dynamicTable.SnapshotNewestFirst();

    public void SetMaxAllowedDynamicTableSize(int newMaxSize)
    {
        if (newMaxSize < 0)
            throw new ArgumentOutOfRangeException(nameof(newMaxSize));

        _maxAllowedDynamicTableSize = newMaxSize;
        if (_dynamicTable.MaxSize > newMaxSize)
            _dynamicTable.SetMaxSize(newMaxSize);
    }

    public List<PureHttpHeader> DecodeHeaderBlock(ReadOnlySpan<byte> block, bool validateHttp2Semantics = true)
    {
        var headers = new List<PureHttpHeader>();
        int offset = 0;
        bool allowDynamicTableSizeUpdate = true;
        bool seenRegularHeader = false;
        long totalHeaderListSize = 0;

        while (offset < block.Length)
        {
            byte first = block[offset];
            if ((first & 0x80) != 0)
            {
                // 6.1 Indexed Header Field Representation
                allowDynamicTableSizeUpdate = false;
                uint idx = HpackIntegerCodec.Decode(block, ref offset, 7);
                if (idx == 0)
                    throw new Http2Exception(H2CompressionError, isStreamReset: false, "HPACK indexed header field cannot reference index 0.");

                PureHttpHeader entry = ResolveIndex((int)idx);
                AddDecodedHeader(entry.Name, entry.Value, headers, validateHttp2Semantics, ref seenRegularHeader, ref totalHeaderListSize);
            }
            else if ((first & 0xC0) == 0x40)
            {
                // 6.2.1 Literal Header Field with Incremental Indexing
                allowDynamicTableSizeUpdate = false;
                uint nameIdx = HpackIntegerCodec.Decode(block, ref offset, 6);
                string name = nameIdx == 0 ? ReadString(block, ref offset) : ResolveIndex((int)nameIdx).Name;
                string value = ReadString(block, ref offset);
                _dynamicTable.Insert(name, value);
                AddDecodedHeader(name, value, headers, validateHttp2Semantics, ref seenRegularHeader, ref totalHeaderListSize);
            }
            else if ((first & 0xE0) == 0x20)
            {
                // 6.3 Dynamic Table Size Update
                if (!allowDynamicTableSizeUpdate)
                {
                    throw new Http2Exception(
                        H2CompressionError,
                        isStreamReset: false,
                        "HPACK dynamic table size update must occur at the start of a header block.");
                }

                uint newSize = HpackIntegerCodec.Decode(block, ref offset, 5);
                if (newSize > (uint)_maxAllowedDynamicTableSize)
                {
                    throw new Http2Exception(
                        H2CompressionError,
                        isStreamReset: false,
                        $"HPACK dynamic table size update {newSize} exceeds SETTINGS_HEADER_TABLE_SIZE {_maxAllowedDynamicTableSize}.");
                }

                _dynamicTable.SetMaxSize((int)newSize);
            }
            else
            {
                // 6.2.2 Without Indexing (0000xxxx) or 6.2.3 Never Indexed (0001xxxx)
                allowDynamicTableSizeUpdate = false;
                uint nameIdx = HpackIntegerCodec.Decode(block, ref offset, 4);
                string name = nameIdx == 0 ? ReadString(block, ref offset) : ResolveIndex((int)nameIdx).Name;
                string value = ReadString(block, ref offset);
                AddDecodedHeader(name, value, headers, validateHttp2Semantics, ref seenRegularHeader, ref totalHeaderListSize);
            }
        }

        return headers;
    }

    private PureHttpHeader ResolveIndex(int oneBasedIndex)
    {
        if (oneBasedIndex <= HpackStaticTable.Count)
        {
            if (HpackStaticTable.TryGet(oneBasedIndex, out PureHttpHeader staticEntry))
                return staticEntry;
        }
        else if (_dynamicTable.TryGet(oneBasedIndex - HpackStaticTable.Count - 1, out PureHttpHeader dynEntry))
        {
            return dynEntry;
        }

        throw new Http2Exception(H2CompressionError, isStreamReset: false, $"HPACK index {oneBasedIndex} is out of range.");
    }

    private static string ReadString(ReadOnlySpan<byte> block, ref int offset)
    {
        if (offset >= block.Length)
            throw new Http2Exception(H2CompressionError, isStreamReset: false, "Truncated HPACK string header.");

        bool huffman = (block[offset] & 0x80) != 0;
        uint byteLen = HpackIntegerCodec.Decode(block, ref offset, 7);
        if (byteLen > (uint)(block.Length - offset))
            throw new Http2Exception(H2CompressionError, isStreamReset: false, "HPACK string literal exceeds remaining block length.");

        ReadOnlySpan<byte> slice = block.Slice(offset, (int)byteLen);
        offset += (int)byteLen;

        if (!huffman)
            return Encoding.UTF8.GetString(slice);

        byte[] decoded = HpackHuffmanCodec.Decode(slice);
        return Encoding.UTF8.GetString(decoded);
    }

    private void AddDecodedHeader(
        string name,
        string value,
        List<PureHttpHeader> headers,
        bool validateHttp2Semantics,
        ref bool seenRegularHeader,
        ref long totalHeaderListSize)
    {
        if (validateHttp2Semantics)
        {
            if (string.IsNullOrEmpty(name))
                throw new Http2Exception(H2ProtocolError, isStreamReset: false, "HTTP/2 header name cannot be empty.");

            for (int i = 0; i < name.Length; i++)
            {
                char ch = name[i];
                if (ch is >= 'A' and <= 'Z')
                    throw new Http2Exception(H2ProtocolError, isStreamReset: false, $"HTTP/2 header name '{name}' contains uppercase characters.");
            }

            if (name[0] == ':')
            {
                if (name.Length == 1)
                    throw new Http2Exception(H2ProtocolError, isStreamReset: false, "Invalid empty HTTP/2 pseudo-header ':'.");
                if (seenRegularHeader)
                    throw new Http2Exception(H2ProtocolError, isStreamReset: false, $"HTTP/2 pseudo-header '{name}' appeared after regular header field.");
            }
            else
            {
                seenRegularHeader = true;
            }
        }

        totalHeaderListSize += HpackDynamicTable.ComputeEntrySize(name, value);
        if (totalHeaderListSize > MaxHeaderListSize)
        {
            throw new Http2Exception(
                H2CompressionError,
                isStreamReset: false,
                $"Decoded HTTP/2 header list size {totalHeaderListSize} exceeds MaxHeaderListSize ({MaxHeaderListSize}).");
        }

        headers.Add(new PureHttpHeader(name, value));
    }
}

/// <summary>
/// Full RFC 7541 HPACK encoder honoring <see cref="Http2SettingsSpec.PseudoHeaderOrder"/> and
/// <see cref="Http2SettingsSpec.HeaderOrder"/> with dynamic table indexing and Huffman compression.
/// </summary>
public sealed class HpackEncoder
{
    private readonly HpackDynamicTable _dynamicTable;
    private readonly int _maxProtocolCeiling;
    private readonly HpackHuffmanMode _huffmanMode;
    private bool _pendingSizeUpdate;
    private int _pendingMinIntermediateSize = -1;
    private int _targetMaxTableSize;

    public HpackEncoder(
        int maxDynamicTableSize = 4096,
        HpackHuffmanMode huffmanMode = HpackHuffmanMode.IfSmaller,
        int maxProtocolCeiling = 65_536)
    {
        if (maxDynamicTableSize < 0)
            throw new ArgumentOutOfRangeException(nameof(maxDynamicTableSize));

        _maxProtocolCeiling = Math.Max(maxDynamicTableSize, maxProtocolCeiling);
        _targetMaxTableSize = maxDynamicTableSize;
        _huffmanMode = huffmanMode;
        _dynamicTable = new HpackDynamicTable(maxDynamicTableSize);
    }

    public int CurrentDynamicTableMaxSize => _dynamicTable.MaxSize;
    public int CurrentDynamicTableSize => _dynamicTable.CurrentSize;
    public int DynamicTableCount => _dynamicTable.Count;

    public IReadOnlyList<PureHttpHeader> GetDynamicTableEntries() => _dynamicTable.SnapshotNewestFirst();

    public void SetMaxTableSize(int peerMaxHeaderTableSize)
    {
        if (peerMaxHeaderTableSize < 0)
            throw new ArgumentOutOfRangeException(nameof(peerMaxHeaderTableSize));

        int clamped = Math.Min(peerMaxHeaderTableSize, _maxProtocolCeiling);
        if (clamped == _targetMaxTableSize && !_pendingSizeUpdate)
            return;

        if (!_pendingSizeUpdate)
        {
            _pendingMinIntermediateSize = clamped < _dynamicTable.MaxSize ? clamped : -1;
        }
        else if (clamped < _pendingMinIntermediateSize || _pendingMinIntermediateSize < 0)
        {
            _pendingMinIntermediateSize = clamped;
        }

        _targetMaxTableSize = clamped;
        _dynamicTable.SetMaxSize(clamped);
        _pendingSizeUpdate = true;
    }

    public byte[] EncodeHeaders(
        PureHttpRequest request,
        Http2SettingsSpec? settingsSpec = null,
        IReadOnlyList<string>? pseudoHeaderOrderOverride = null,
        IReadOnlyList<string>? headerOrderOverride = null)
    {
        ArgumentNullException.ThrowIfNull(request);
        List<PureHttpHeader> ordered = BuildRequestHeaders(
            request,
            settingsSpec,
            pseudoHeaderOrderOverride,
            headerOrderOverride);

        return EncodeHeaderListInternal(ordered, indexLiterals: true, respectSensitiveHeaders: true);
    }

    public byte[] EncodeHeaderList(IReadOnlyList<PureHttpHeader> headers, bool indexLiterals = true)
    {
        ArgumentNullException.ThrowIfNull(headers);
        return EncodeHeaderListInternal(headers, indexLiterals, respectSensitiveHeaders: false);
    }

    /// <summary>
    /// Orders HTTP/2 pseudo-headers and regular headers according to <see cref="Http2SettingsSpec.PseudoHeaderOrder"/>
    /// and <see cref="Http2SettingsSpec.HeaderOrder"/> per Cybersole.Http BuildHeaders (0x1412CACA0).
    /// </summary>
    public static List<PureHttpHeader> BuildRequestHeaders(
        PureHttpRequest request,
        Http2SettingsSpec? settingsSpec = null,
        IReadOnlyList<string>? pseudoHeaderOrderOverride = null,
        IReadOnlyList<string>? headerOrderOverride = null)
    {
        ArgumentNullException.ThrowIfNull(request);

        string method = request.Method.Trim().ToUpperInvariant();
        if (string.IsNullOrEmpty(method))
            throw new PureHttpException(HttpErrorKind.Protocol, "HTTP/2 request method cannot be empty.");

        string? hostOverride = null;
        for (int i = 0; i < request.Headers.Count; i++)
        {
            if (string.Equals(request.Headers[i].Name, "host", StringComparison.OrdinalIgnoreCase) &&
                !string.IsNullOrWhiteSpace(request.Headers[i].Value))
            {
                hostOverride = request.Headers[i].Value.Trim();
                break;
            }
        }

        string authority = hostOverride ?? request.Uri.Authority;
        string scheme = request.Uri.Scheme.ToLowerInvariant();
        string path = string.IsNullOrEmpty(request.Uri.PathAndQuery) ? "/" : request.Uri.PathAndQuery;
        bool isConnect = string.Equals(method, "CONNECT", StringComparison.Ordinal);

        IReadOnlyList<string> pseudoOrder = pseudoHeaderOrderOverride
            ?? settingsSpec?.PseudoHeaderOrder
            ?? Http2SettingsSpec.DefaultFallbackPseudoHeaderOrder;

        var result = new List<PureHttpHeader>(request.Headers.Count + 6);
        var emittedPseudo = new HashSet<string>(StringComparer.Ordinal);

        void TryEmitPseudo(string token)
        {
            string normalized = NormalizePseudoToken(token);
            if (normalized.Length == 0 || !emittedPseudo.Add(normalized))
                return;

            switch (normalized)
            {
                case ":method":
                    result.Add(new PureHttpHeader(":method", method));
                    break;
                case ":authority":
                    result.Add(new PureHttpHeader(":authority", authority));
                    break;
                case ":scheme":
                    if (!isConnect)
                        result.Add(new PureHttpHeader(":scheme", scheme));
                    break;
                case ":path":
                    if (!isConnect)
                        result.Add(new PureHttpHeader(":path", path));
                    break;
            }
        }

        for (int i = 0; i < pseudoOrder.Count; i++)
            TryEmitPseudo(pseudoOrder[i]);

        // Ensure all required pseudo-headers are present even if a caller gave a partial PseudoHeaderOrder.
        TryEmitPseudo(":method");
        TryEmitPseudo(":authority");
        if (!isConnect)
        {
            TryEmitPseudo(":scheme");
            TryEmitPseudo(":path");
        }

        var regular = new List<PureHttpHeader>(request.Headers.Count + 2);
        bool hasUserAgent = false;

        for (int i = 0; i < request.Headers.Count; i++)
        {
            PureHttpHeader raw = request.Headers[i];
            if (string.IsNullOrWhiteSpace(raw.Name))
                continue;

            string trimmedName = raw.Name.Trim();
            if (trimmedName.StartsWith(':'))
                continue;

            string lowerName = trimmedName.ToLowerInvariant();
            ValidateHeaderField(lowerName, raw.Value);

            if (IsDisallowedHttp2Header(lowerName))
                continue;

            if (lowerName == "user-agent")
                hasUserAgent = true;

            if (lowerName == "cookie")
            {
                string[] parts = raw.Value.Split("; ", StringSplitOptions.RemoveEmptyEntries);
                if (parts.Length == 0 && raw.Value.Length > 0)
                {
                    regular.Add(new PureHttpHeader("cookie", raw.Value));
                }
                else
                {
                    for (int p = 0; p < parts.Length; p++)
                    {
                        string cookiePart = parts[p].TrimStart(' ');
                        if (cookiePart.Length > 0)
                            regular.Add(new PureHttpHeader("cookie", cookiePart));
                    }
                }
                continue;
            }

            regular.Add(new PureHttpHeader(lowerName, raw.Value));
        }

        if (request.Body.Length > 0 || method is "POST" or "PUT" or "PATCH")
            regular.Add(new PureHttpHeader("content-length", request.Body.Length.ToString(CultureInfo.InvariantCulture)));

        if (!hasUserAgent)
            regular.Add(new PureHttpHeader("user-agent", "Go-http-client/2.0"));

        IReadOnlyList<string>? headerOrder = headerOrderOverride ?? settingsSpec?.HeaderOrder;
        if (headerOrder is { Count: > 0 })
        {
            var emitted = new bool[regular.Count];
            for (int o = 0; o < headerOrder.Count; o++)
            {
                string target = headerOrder[o].Trim().ToLowerInvariant();
                if (target.Length == 0 || target.StartsWith(':'))
                    continue;

                for (int r = 0; r < regular.Count; r++)
                {
                    if (!emitted[r] && string.Equals(regular[r].Name, target, StringComparison.Ordinal))
                    {
                        result.Add(regular[r]);
                        emitted[r] = true;
                    }
                }
            }

            for (int r = 0; r < regular.Count; r++)
            {
                if (!emitted[r])
                    result.Add(regular[r]);
            }
        }
        else
        {
            result.AddRange(regular);
        }

        return result;
    }

    private byte[] EncodeHeaderListInternal(
        IReadOnlyList<PureHttpHeader> headers,
        bool indexLiterals,
        bool respectSensitiveHeaders)
    {
        var output = new List<byte>(256);

        if (_pendingSizeUpdate)
        {
            if (_pendingMinIntermediateSize >= 0 && _pendingMinIntermediateSize < _targetMaxTableSize)
                HpackIntegerCodec.Encode(output, (uint)_pendingMinIntermediateSize, 5, 0x20);
            HpackIntegerCodec.Encode(output, (uint)_targetMaxTableSize, 5, 0x20);
            _pendingSizeUpdate = false;
            _pendingMinIntermediateSize = -1;
        }

        for (int i = 0; i < headers.Count; i++)
        {
            PureHttpHeader h = headers[i];
            string name = h.Name;
            string value = h.Value ?? string.Empty;

            bool neverIndex = respectSensitiveHeaders && IsSensitiveHeader(name);
            int matchedIndex = FindInTables(name, value, out bool exactMatch);

            if (exactMatch)
            {
                HpackIntegerCodec.Encode(output, (uint)matchedIndex, 7, 0x80);
                continue;
            }

            if (neverIndex)
            {
                HpackIntegerCodec.Encode(output, (uint)matchedIndex, 4, 0x10);
                if (matchedIndex == 0)
                    WriteString(output, name);
                WriteString(output, value);
            }
            else if (indexLiterals)
            {
                HpackIntegerCodec.Encode(output, (uint)matchedIndex, 6, 0x40);
                if (matchedIndex == 0)
                    WriteString(output, name);
                WriteString(output, value);
                _dynamicTable.Insert(name, value);
            }
            else
            {
                HpackIntegerCodec.Encode(output, (uint)matchedIndex, 4, 0x00);
                if (matchedIndex == 0)
                    WriteString(output, name);
                WriteString(output, value);
            }
        }

        return output.ToArray();
    }

    private int FindInTables(string name, string value, out bool exactValueMatch)
    {
        int staticIdx = HpackStaticTable.Find(name, value, out bool staticExact);
        if (staticExact)
        {
            exactValueMatch = true;
            return staticIdx;
        }

        int dynIdx = _dynamicTable.Find(name, value, out bool dynExact);
        if (dynExact)
        {
            exactValueMatch = true;
            return dynIdx;
        }

        exactValueMatch = false;
        return staticIdx != 0 ? staticIdx : dynIdx;
    }

    private void WriteString(List<byte> output, string text)
    {
        byte[] raw = Encoding.UTF8.GetBytes(text);
        if (_huffmanMode == HpackHuffmanMode.Never)
        {
            HpackIntegerCodec.Encode(output, (uint)raw.Length, 7, 0x00);
            output.AddRange(raw);
            return;
        }

        if (_huffmanMode == HpackHuffmanMode.Always)
        {
            byte[] huff = HpackHuffmanCodec.Encode(raw);
            HpackIntegerCodec.Encode(output, (uint)huff.Length, 7, 0x80);
            output.AddRange(huff);
            return;
        }

        int huffLen = HpackHuffmanCodec.GetEncodedLength(raw);
        if (huffLen < raw.Length)
        {
            byte[] huff = HpackHuffmanCodec.Encode(raw);
            HpackIntegerCodec.Encode(output, (uint)huff.Length, 7, 0x80);
            output.AddRange(huff);
        }
        else
        {
            HpackIntegerCodec.Encode(output, (uint)raw.Length, 7, 0x00);
            output.AddRange(raw);
        }
    }

    private static string NormalizePseudoToken(string token)
    {
        string trimmed = token.Trim().ToLowerInvariant();
        return trimmed switch
        {
            "m" or ":method" => ":method",
            "a" or ":authority" => ":authority",
            "s" or ":scheme" => ":scheme",
            "p" or ":path" => ":path",
            _ => string.Empty,
        };
    }

    private static bool IsDisallowedHttp2Header(string lowerName) => lowerName is
        "host" or
        "upgrade" or
        "connection" or
        "keep-alive" or
        "proxy-connection" or
        "transfer-encoding" or
        "content-length";

    private static bool IsSensitiveHeader(string lowerName) => lowerName is
        "authorization" or
        "proxy-authorization";

    private static void ValidateHeaderField(string lowerName, string? value)
    {
        for (int i = 0; i < lowerName.Length; i++)
        {
            char c = lowerName[i];
            if (c <= ' ' || c >= 0x7F || c == ':')
                throw new PureHttpException(HttpErrorKind.Protocol, $"Invalid HTTP/2 header name '{lowerName}'.");
        }

        if (value is not null && value.IndexOfAny(new[] { '\r', '\n', '\0' }) >= 0)
            throw new PureHttpException(HttpErrorKind.Protocol, $"Invalid HTTP/2 header value for '{lowerName}'.");
    }
}
