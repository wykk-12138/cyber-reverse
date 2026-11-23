using System.Buffers.Binary;
using System.Text;

namespace Cybersole.Http.X509;

/// <summary>
/// ASN.1 DER tag class (X.690 §8.1.2).
/// </summary>
public enum Asn1TagClass : byte
{
    Universal = 0,
    Application = 1,
    ContextSpecific = 2,
    Private = 3,
}

/// <summary>
/// Decoded ASN.1 DER tag identifier.
/// </summary>
public readonly record struct Asn1Tag(Asn1TagClass TagClass, bool IsConstructed, int TagNumber)
{
    public const int TagBoolean = 1;
    public const int TagInteger = 2;
    public const int TagBitString = 3;
    public const int TagOctetString = 4;
    public const int TagNull = 5;
    public const int TagObjectIdentifier = 6;
    public const int TagUtf8String = 12;
    public const int TagSequence = 16;
    public const int TagSet = 17;
    public const int TagNumericString = 18;
    public const int TagPrintableString = 19;
    public const int TagT61String = 20;
    public const int TagIA5String = 22;
    public const int TagUtcTime = 23;
    public const int TagGeneralizedTime = 24;
    public const int TagVisibleString = 26;
    public const int TagUniversalString = 28;
    public const int TagBmpString = 30;

    public bool IsUniversal(int tagNumber) =>
        TagClass == Asn1TagClass.Universal && TagNumber == tagNumber;

    public bool IsContextSpecific(int tagNumber) =>
        TagClass == Asn1TagClass.ContextSpecific && TagNumber == tagNumber;

    public bool Matches(Asn1TagClass tagClass, int tagNumber) =>
        TagClass == tagClass && TagNumber == tagNumber;

    public bool Matches(Asn1TagClass tagClass, bool isConstructed, int tagNumber) =>
        TagClass == tagClass && IsConstructed == isConstructed && TagNumber == tagNumber;

    public override string ToString() =>
        $"{TagClass}({TagNumber}, {(IsConstructed ? "C" : "P")})";
}

/// <summary>
/// Parsed ASN.1 DER TLV node preserving both the exact encoded TLV slice (<see cref="HeaderAndContent"/>)
/// and the inner value slice (<see cref="Content"/>).
/// </summary>
public readonly struct Asn1Node
{
    public Asn1Node(Asn1Tag tag, ReadOnlyMemory<byte> headerAndContent, ReadOnlyMemory<byte> content)
    {
        Tag = tag;
        HeaderAndContent = headerAndContent;
        Content = content;
    }

    public Asn1Tag Tag { get; }
    public Asn1TagClass TagClass => Tag.TagClass;
    public bool IsConstructed => Tag.IsConstructed;
    public int TagNumber => Tag.TagNumber;

    /// <summary>
    /// Exact tag + length + content bytes. Critical for computing TBSCertificate signature digests.
    /// </summary>
    public ReadOnlyMemory<byte> HeaderAndContent { get; }

    /// <summary>
    /// Value bytes inside the TLV.
    /// </summary>
    public ReadOnlyMemory<byte> Content { get; }

    public ReadOnlySpan<byte> HeaderAndContentSpan => HeaderAndContent.Span;
    public ReadOnlySpan<byte> ContentSpan => Content.Span;

    public Asn1ChildEnumerable EnumerateChildren()
    {
        if (!IsConstructed)
            throw new FormatException($"Cannot enumerate children of primitive ASN.1 node {Tag}.");
        return new Asn1ChildEnumerable(Content);
    }

    public IReadOnlyList<Asn1Node> ReadChildren()
    {
        if (!IsConstructed)
            throw new FormatException($"Cannot read children of primitive ASN.1 node {Tag}.");
        var list = new List<Asn1Node>();
        var cursor = new Asn1Cursor(Content);
        while (cursor.HasRemaining)
            list.Add(cursor.ReadNext());
        cursor.ExpectEnd();
        return list;
    }
}

/// <summary>
/// Zero-allocation enumerable over the direct child TLVs inside a constructed ASN.1 DER node.
/// </summary>
public readonly struct Asn1ChildEnumerable
{
    private readonly ReadOnlyMemory<byte> _content;

    internal Asn1ChildEnumerable(ReadOnlyMemory<byte> content)
    {
        _content = content;
    }

    public Asn1ChildEnumerator GetEnumerator() => new(_content);
}

/// <summary>
/// Enumerator over direct child TLVs inside a constructed ASN.1 DER node.
/// </summary>
public struct Asn1ChildEnumerator
{
    private readonly ReadOnlyMemory<byte> _content;
    private int _offset;
    private Asn1Node _current;

    internal Asn1ChildEnumerator(ReadOnlyMemory<byte> content)
    {
        _content = content;
        _offset = 0;
        _current = default;
    }

    public readonly Asn1Node Current => _current;

    public bool MoveNext()
    {
        if (_offset >= _content.Length)
            return false;

        _current = Asn1Reader.ReadNode(_content.Slice(_offset), out var consumed);
        _offset += consumed;
        return true;
    }
}

/// <summary>
/// Sequential cursor for parsing constructed ASN.1 DER containers and enforcing no trailing garbage.
/// </summary>
public struct Asn1Cursor
{
    private readonly ReadOnlyMemory<byte> _data;
    private int _offset;

    public Asn1Cursor(ReadOnlyMemory<byte> data)
    {
        _data = data;
        _offset = 0;
    }

    public readonly bool HasRemaining => _offset < _data.Length;
    public readonly int Remaining => _data.Length - _offset;

    public readonly Asn1Tag PeekTag()
    {
        if (!HasRemaining)
            throw new FormatException("Unexpected end of ASN.1 DER container.");
        return Asn1Reader.PeekTag(_data.Span.Slice(_offset));
    }

    public readonly bool TryPeekTag(out Asn1Tag tag)
    {
        if (!HasRemaining)
        {
            tag = default;
            return false;
        }

        tag = Asn1Reader.PeekTag(_data.Span.Slice(_offset));
        return true;
    }

    public Asn1Node ReadNext()
    {
        if (!HasRemaining)
            throw new FormatException("Unexpected end of ASN.1 DER container.");

        var node = Asn1Reader.ReadNode(_data.Slice(_offset), out var consumed);
        _offset += consumed;
        return node;
    }

    public Asn1Node ReadUniversal(int tagNumber, bool? expectedConstructed = null)
    {
        var node = ReadNext();
        if (!node.Tag.IsUniversal(tagNumber))
            throw new FormatException($"Expected Universal tag {tagNumber}, found {node.Tag}.");
        if (expectedConstructed.HasValue && node.IsConstructed != expectedConstructed.Value)
            throw new FormatException($"Unexpected constructed flag for tag {node.Tag}.");
        return node;
    }

    public Asn1Node ReadExpected(Asn1TagClass tagClass, bool isConstructed, int tagNumber)
    {
        var node = ReadNext();
        if (!node.Tag.Matches(tagClass, isConstructed, tagNumber))
            throw new FormatException($"Expected tag {new Asn1Tag(tagClass, isConstructed, tagNumber)}, found {node.Tag}.");
        return node;
    }

    public bool TryReadContextSpecific(int tagNumber, out Asn1Node node)
    {
        if (TryPeekTag(out var tag) && tag.IsContextSpecific(tagNumber))
        {
            node = ReadNext();
            return true;
        }

        node = default;
        return false;
    }

    public bool TryReadContextSpecific(int tagNumber, bool isConstructed, out Asn1Node node)
    {
        if (TryPeekTag(out var tag) && tag.Matches(Asn1TagClass.ContextSpecific, isConstructed, tagNumber))
        {
            node = ReadNext();
            return true;
        }

        node = default;
        return false;
    }

    public readonly void ExpectEnd()
    {
        if (_offset != _data.Length)
            throw new FormatException($"Trailing {Remaining} byte(s) inside ASN.1 DER container.");
    }
}

/// <summary>
/// Strict ASN.1 DER TLV parser and value decoder (X.690).
/// Rejects indefinite lengths, non-minimal length/tag encodings, and trailing garbage.
/// </summary>
public static class Asn1Reader
{
    private static readonly UTF8Encoding StrictUtf8 = new(encoderShouldEmitUTF8Identifier: false, throwOnInvalidBytes: true);
    private static readonly UTF32Encoding BigEndianUtf32 = new(bigEndian: true, byteOrderMark: false, throwOnInvalidCharacters: true);

    public static Asn1Node ReadSingle(ReadOnlyMemory<byte> der)
    {
        var node = ReadNode(der, out var consumed);
        if (consumed != der.Length)
            throw new FormatException($"Trailing {der.Length - consumed} byte(s) after ASN.1 DER root element.");
        return node;
    }

    public static Asn1Tag PeekTag(ReadOnlySpan<byte> data)
    {
        return ParseTag(data, out _);
    }

    public static Asn1Node ReadNode(ReadOnlyMemory<byte> data, out int bytesConsumed)
    {
        var span = data.Span;
        var tag = ParseTag(span, out var tagLen);
        var len = ParseDerLength(span.Slice(tagLen), out var lenLen);

        var headerLen = tagLen + lenLen;
        if (len > span.Length - headerLen)
            throw new FormatException("ASN.1 DER value length exceeds available input.");

        ValidateUniversalConstructed(tag);

        bytesConsumed = headerLen + len;
        return new Asn1Node(
            tag,
            data.Slice(0, bytesConsumed),
            data.Slice(headerLen, len));
    }

    private static Asn1Tag ParseTag(ReadOnlySpan<byte> data, out int tagLength)
    {
        if (data.IsEmpty)
            throw new FormatException("Unexpected end of ASN.1 DER tag.");

        var first = data[0];
        var tagClass = (Asn1TagClass)(first >> 6);
        var isConstructed = (first & 0x20) != 0;
        var low5 = first & 0x1F;

        if (low5 != 0x1F)
        {
            tagLength = 1;
            return new Asn1Tag(tagClass, isConstructed, low5);
        }

        if (data.Length < 2)
            throw new FormatException("Truncated high-tag-number ASN.1 tag.");

        if (data[1] == 0x80)
            throw new FormatException("Non-minimal leading zero in ASN.1 high-tag-number encoding.");

        var tagNumber = 0;
        var idx = 1;
        while (true)
        {
            if (idx >= data.Length)
                throw new FormatException("Unterminated ASN.1 high-tag-number encoding.");

            var b = data[idx++];
            if (tagNumber > (int.MaxValue >> 7))
                throw new FormatException("ASN.1 tag number overflows Int32.");

            tagNumber = (tagNumber << 7) | (b & 0x7F);
            if ((b & 0x80) == 0)
                break;
        }

        if (tagNumber < 31)
            throw new FormatException("Non-minimal ASN.1 high-tag-number encoding for tag < 31.");

        tagLength = idx;
        return new Asn1Tag(tagClass, isConstructed, tagNumber);
    }

    private static int ParseDerLength(ReadOnlySpan<byte> data, out int lengthOctetsCount)
    {
        if (data.IsEmpty)
            throw new FormatException("Unexpected end of ASN.1 DER length.");

        var first = data[0];
        if (first == 0x80)
            throw new FormatException("Indefinite-length ASN.1 encoding is not allowed in DER.");

        if ((first & 0x80) == 0)
        {
            lengthOctetsCount = 1;
            return first;
        }

        var numOctets = first & 0x7F;
        if (numOctets > 4)
            throw new FormatException("ASN.1 DER length exceeds 32-bit maximum.");

        if (data.Length < 1 + numOctets)
            throw new FormatException("Truncated ASN.1 DER long-form length.");

        if (data[1] == 0x00)
            throw new FormatException("Non-minimal ASN.1 DER length with leading zero octet.");

        uint len = 0;
        for (var i = 0; i < numOctets; i++)
            len = (len << 8) | data[1 + i];

        if (len < 128)
            throw new FormatException("Non-minimal ASN.1 DER long-form length for value < 128.");

        if (len > int.MaxValue)
            throw new FormatException("ASN.1 DER length exceeds Int32.MaxValue.");

        lengthOctetsCount = 1 + numOctets;
        return (int)len;
    }

    private static void ValidateUniversalConstructed(Asn1Tag tag)
    {
        if (tag.TagClass != Asn1TagClass.Universal)
            return;

        switch (tag.TagNumber)
        {
            case Asn1Tag.TagSequence:
            case Asn1Tag.TagSet:
                if (!tag.IsConstructed)
                    throw new FormatException($"DER requires {tag} to be constructed.");
                break;
            case Asn1Tag.TagBoolean:
            case Asn1Tag.TagInteger:
            case Asn1Tag.TagBitString:
            case Asn1Tag.TagOctetString:
            case Asn1Tag.TagNull:
            case Asn1Tag.TagObjectIdentifier:
            case Asn1Tag.TagUtf8String:
            case Asn1Tag.TagNumericString:
            case Asn1Tag.TagPrintableString:
            case Asn1Tag.TagT61String:
            case Asn1Tag.TagIA5String:
            case Asn1Tag.TagUtcTime:
            case Asn1Tag.TagGeneralizedTime:
            case Asn1Tag.TagVisibleString:
            case Asn1Tag.TagUniversalString:
            case Asn1Tag.TagBmpString:
                if (tag.IsConstructed)
                    throw new FormatException($"DER forbids constructed encoding on {tag}.");
                break;
        }
    }

    public static string ReadOid(ReadOnlySpan<byte> content)
    {
        if (content.IsEmpty)
            throw new FormatException("ASN.1 OID value cannot be empty.");

        if ((content[^1] & 0x80) != 0)
            throw new FormatException("Unterminated ASN.1 OID subidentifier.");

        var sb = new StringBuilder();
        var i = 0;

        var firstSubId = ReadOidSubIdentifier(content, ref i);
        ulong arc0;
        ulong arc1;
        if (firstSubId < 40)
        {
            arc0 = 0;
            arc1 = firstSubId;
        }
        else if (firstSubId < 80)
        {
            arc0 = 1;
            arc1 = firstSubId - 40;
        }
        else
        {
            arc0 = 2;
            arc1 = firstSubId - 80;
        }

        sb.Append(arc0);
        sb.Append('.');
        sb.Append(arc1);

        while (i < content.Length)
        {
            var subId = ReadOidSubIdentifier(content, ref i);
            sb.Append('.');
            sb.Append(subId);
        }

        return sb.ToString();
    }

    private static ulong ReadOidSubIdentifier(ReadOnlySpan<byte> content, ref int offset)
    {
        if (offset >= content.Length)
            throw new FormatException("Unexpected end of ASN.1 OID subidentifier.");

        if (content[offset] == 0x80)
            throw new FormatException("Non-minimal leading zero in ASN.1 OID subidentifier.");

        ulong value = 0;
        while (true)
        {
            if (offset >= content.Length)
                throw new FormatException("Unterminated ASN.1 OID subidentifier.");

            var b = content[offset++];
            if (value > (ulong.MaxValue >> 7))
                throw new FormatException("ASN.1 OID subidentifier overflows UInt64.");

            value = (value << 7) | (uint)(b & 0x7F);
            if ((b & 0x80) == 0)
                return value;
        }
    }

    public static byte[] ReadIntegerBytes(ReadOnlySpan<byte> content)
    {
        ValidateDerInteger(content);
        return content.ToArray();
    }

    public static int ReadSmallInt(ReadOnlySpan<byte> content)
    {
        ValidateDerInteger(content);
        if (content.Length > 4)
            throw new FormatException("ASN.1 INTEGER exceeds 32-bit signed integer range.");

        var isNegative = (content[0] & 0x80) != 0;
        uint value = isNegative ? uint.MaxValue : 0u;
        for (var i = 0; i < content.Length; i++)
            value = (value << 8) | content[i];

        return unchecked((int)value);
    }

    private static void ValidateDerInteger(ReadOnlySpan<byte> content)
    {
        if (content.IsEmpty)
            throw new FormatException("ASN.1 INTEGER cannot be empty.");

        if (content.Length >= 2)
        {
            if (content[0] == 0x00 && (content[1] & 0x80) == 0)
                throw new FormatException("Non-minimal positive ASN.1 DER INTEGER.");
            if (content[0] == 0xFF && (content[1] & 0x80) != 0)
                throw new FormatException("Non-minimal negative ASN.1 DER INTEGER.");
        }
    }

    public static bool ReadBoolean(ReadOnlySpan<byte> content)
    {
        if (content.Length != 1)
            throw new FormatException("ASN.1 BOOLEAN must be exactly 1 byte.");

        return content[0] switch
        {
            0x00 => false,
            0xFF => true,
            _ => throw new FormatException($"Non-canonical ASN.1 DER BOOLEAN value: 0x{content[0]:X2}."),
        };
    }

    public static void ReadNull(ReadOnlySpan<byte> content)
    {
        if (!content.IsEmpty)
            throw new FormatException("ASN.1 NULL must have zero length.");
    }

    public static ReadOnlySpan<byte> ReadBitString(ReadOnlySpan<byte> content, out int unusedBits)
    {
        if (content.IsEmpty)
            throw new FormatException("ASN.1 BIT STRING cannot be empty.");

        unusedBits = content[0];
        if (unusedBits > 7)
            throw new FormatException($"Invalid ASN.1 BIT STRING unused bits count: {unusedBits}.");

        var payload = content.Slice(1);
        if (payload.IsEmpty)
        {
            if (unusedBits != 0)
                throw new FormatException("Empty ASN.1 BIT STRING must have 0 unused bits.");
            return payload;
        }

        if (unusedBits > 0)
        {
            var mask = (1 << unusedBits) - 1;
            if ((payload[^1] & mask) != 0)
                throw new FormatException("ASN.1 DER BIT STRING has non-zero unused trailing bits.");
        }

        return payload;
    }

    public static string ReadStringValue(Asn1Node node)
    {
        if (node.TagClass != Asn1TagClass.Universal || node.IsConstructed)
            throw new FormatException($"Invalid ASN.1 string node {node.Tag}.");

        var bytes = node.ContentSpan;
        return node.TagNumber switch
        {
            Asn1Tag.TagUtf8String => DecodeStrictUtf8(bytes),
            Asn1Tag.TagPrintableString or Asn1Tag.TagNumericString or Asn1Tag.TagVisibleString => DecodeAscii(bytes),
            Asn1Tag.TagIA5String => DecodeAscii(bytes),
            Asn1Tag.TagT61String => Encoding.Latin1.GetString(bytes),
            Asn1Tag.TagBmpString => DecodeBmpString(bytes),
            Asn1Tag.TagUniversalString => DecodeUniversalString(bytes),
            _ => throw new FormatException($"Unsupported ASN.1 string tag: {node.Tag}."),
        };
    }

    private static string DecodeStrictUtf8(ReadOnlySpan<byte> bytes)
    {
        try
        {
            return StrictUtf8.GetString(bytes);
        }
        catch (DecoderFallbackException ex)
        {
            throw new FormatException("Invalid UTF-8 bytes inside ASN.1 UTF8String.", ex);
        }
    }

    private static string DecodeAscii(ReadOnlySpan<byte> bytes)
    {
        for (var i = 0; i < bytes.Length; i++)
        {
            if (bytes[i] > 0x7F)
                throw new FormatException($"Non-ASCII byte 0x{bytes[i]:X2} inside ASCII-based ASN.1 string.");
        }
        return Encoding.ASCII.GetString(bytes);
    }

    private static string DecodeBmpString(ReadOnlySpan<byte> bytes)
    {
        if ((bytes.Length & 1) != 0)
            throw new FormatException("ASN.1 BMPString byte length must be even.");
        return Encoding.BigEndianUnicode.GetString(bytes);
    }

    private static string DecodeUniversalString(ReadOnlySpan<byte> bytes)
    {
        if ((bytes.Length & 3) != 0)
            throw new FormatException("ASN.1 UniversalString byte length must be a multiple of 4.");
        try
        {
            return BigEndianUtf32.GetString(bytes);
        }
        catch (DecoderFallbackException ex)
        {
            throw new FormatException("Invalid UTF-32 bytes inside ASN.1 UniversalString.", ex);
        }
    }

    public static DateTimeOffset ParseTime(Asn1Node node)
    {
        if (node.TagClass != Asn1TagClass.Universal || node.IsConstructed)
            throw new FormatException($"Invalid ASN.1 time node {node.Tag}.");

        var span = node.ContentSpan;
        int year, month, day, hour, minute, second;

        if (node.TagNumber == Asn1Tag.TagUtcTime)
        {
            // DER UTCTime: YYMMDDHHMMSSZ (13 bytes, RFC 5280 §4.1.2.5.1)
            if (span.Length != 13 || span[12] != (byte)'Z')
                throw new FormatException("Invalid DER UTCTime format (expected YYMMDDHHMMSSZ).");

            var yy = ParseDigits(span, 0, 2);
            year = yy < 50 ? 2000 + yy : 1900 + yy;
            month = ParseDigits(span, 2, 2);
            day = ParseDigits(span, 4, 2);
            hour = ParseDigits(span, 6, 2);
            minute = ParseDigits(span, 8, 2);
            second = ParseDigits(span, 10, 2);
        }
        else if (node.TagNumber == Asn1Tag.TagGeneralizedTime)
        {
            // DER GeneralizedTime: YYYYMMDDHHMMSSZ (15 bytes, RFC 5280 §4.1.2.5.2)
            if (span.Length != 15 || span[14] != (byte)'Z')
                throw new FormatException("Invalid DER GeneralizedTime format (expected YYYYMMDDHHMMSSZ).");

            year = ParseDigits(span, 0, 4);
            month = ParseDigits(span, 4, 2);
            day = ParseDigits(span, 6, 2);
            hour = ParseDigits(span, 8, 2);
            minute = ParseDigits(span, 10, 2);
            second = ParseDigits(span, 12, 2);
        }
        else
        {
            throw new FormatException($"Expected UTCTime or GeneralizedTime, found {node.Tag}.");
        }

        try
        {
            return new DateTimeOffset(year, month, day, hour, minute, second, TimeSpan.Zero);
        }
        catch (ArgumentOutOfRangeException ex)
        {
            throw new FormatException("Invalid calendar timestamp in ASN.1 time value.", ex);
        }
    }

    private static int ParseDigits(ReadOnlySpan<byte> bytes, int offset, int count)
    {
        var result = 0;
        for (var i = 0; i < count; i++)
        {
            var b = bytes[offset + i];
            if (b is < (byte)'0' or > (byte)'9')
                throw new FormatException("Non-digit character inside ASN.1 time value.");
            result = result * 10 + (b - '0');
        }
        return result;
    }

    internal static uint ReadUInt32BigEndian(ReadOnlySpan<byte> bytes) =>
        BinaryPrimitives.ReadUInt32BigEndian(bytes);
}
