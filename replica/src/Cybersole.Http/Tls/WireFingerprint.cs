using System.Buffers.Binary;
using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using Cybersole.Http.Profiles;
using Cybersole.Http.Quic;

namespace Cybersole.Http.Tls;

/// <summary>Parsed raw TLS ClientHello wire fields and computed JA3 / JA4 fingerprints.</summary>
public sealed record TlsWireFingerprintResult
{
    public required ushort LegacyVersion { get; init; }
    public required ushort EffectiveVersion { get; init; }
    public required bool IsQuic { get; init; }
    public required bool HasSni { get; init; }
    public required string? ServerName { get; init; }
    public required IReadOnlyList<ushort> CipherSuites { get; init; }
    public required IReadOnlyList<ushort> ExtensionTypes { get; init; }
    public required IReadOnlyList<ushort> SupportedGroups { get; init; }
    public required IReadOnlyList<byte> EcPointFormats { get; init; }
    public required IReadOnlyList<ushort> SignatureAlgorithms { get; init; }
    public required IReadOnlyList<string> AlpnProtocols { get; init; }
    public required string Ja4 { get; init; }
    public required string Ja4Raw { get; init; }
    public required string Ja4Original { get; init; }
    public required string Ja4RawOriginal { get; init; }
    public required string Ja3Text { get; init; }
    public required string Ja3Hash { get; init; }
    public required string Ja3nText { get; init; }
    public required string Ja3nHash { get; init; }
    public byte[]? RawQuicTransportParameters { get; init; }
}

/// <summary>Parsed HTTP/2 wire preface and Akamai HTTP/2 fingerprint.</summary>
public sealed record Http2WireFingerprintResult
{
    public required IReadOnlyList<(ushort Id, uint Value)> Settings { get; init; }
    public required uint WindowUpdateIncrement { get; init; }
    public required IReadOnlyList<Http2PriorityFrame> PriorityFrames { get; init; }
    public required IReadOnlyList<string> PseudoHeaderOrder { get; init; }
    public required string AkamaiText { get; init; }
    public required string AkamaiHash { get; init; }
}

/// <summary>Parsed QUIC v1 Client Initial packet wire summary.</summary>
public sealed record QuicInitialWireFingerprintResult
{
    public required uint Version { get; init; }
    public required int DatagramLength { get; init; }
    public required byte[] Dcid { get; init; }
    public required byte[] Scid { get; init; }
    public required ulong TokenLength { get; init; }
    public required ulong PacketNumber { get; init; }
    public required bool HasPingFrame { get; init; }
    public required int CryptoFrameCount { get; init; }
    public required int PaddingBytes { get; init; }
    public required TlsWireFingerprintResult ClientHelloFingerprint { get; init; }
    public required QuicTransportParameters? TransportParameters { get; init; }
}

/// <summary>
/// Wire-level TLS (JA4 / JA4_r / JA4_o / JA4_ro / JA3 / JA3n), HTTP/2 (Akamai), and QUIC v1
/// Initial packet fingerprint inspector operating directly on serialized wire bytes.
/// </summary>
public static class WireFingerprint
{
    private static ReadOnlySpan<byte> Http2PrefaceBytes => "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"u8;

    public static TlsWireFingerprintResult AnalyzeClientHello(ReadOnlySpan<byte> rawRecordOrHandshake, bool isQuic = false)
    {
        ReadOnlySpan<byte> msg = UnwrapTlsRecordIfPresent(rawRecordOrHandshake);
        if (msg.Length < 4 + 2 + 32 + 1 + 2 + 1 + 2 || msg[0] != 0x01)
            throw new FormatException("Input is not a valid TLS ClientHello handshake message.");

        int bodyLen = (msg[1] << 16) | (msg[2] << 8) | msg[3];
        if (4 + bodyLen > msg.Length)
            throw new FormatException("Truncated TLS ClientHello handshake body.");

        ReadOnlySpan<byte> body = msg.Slice(4, bodyLen);
        int off = 0;

        ushort legacyVersion = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(off, 2));
        off += 2;

        // skip client_random (32 bytes)
        off += 32;

        byte sidLen = body[off++];
        if (off + sidLen + 2 > body.Length)
            throw new FormatException("Truncated ClientHello session ID.");
        off += sidLen;

        ushort cipherLen = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(off, 2));
        off += 2;
        if (cipherLen % 2 != 0 || off + cipherLen + 1 > body.Length)
            throw new FormatException("Invalid ClientHello cipher suites length.");

        var ciphers = new List<ushort>(cipherLen / 2);
        for (int i = 0; i < cipherLen; i += 2)
            ciphers.Add(BinaryPrimitives.ReadUInt16BigEndian(body.Slice(off + i, 2)));
        off += cipherLen;

        byte compLen = body[off++];
        if (off + compLen + 2 > body.Length)
            throw new FormatException("Truncated ClientHello compression methods.");
        off += compLen;

        ushort extTotal = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(off, 2));
        off += 2;
        if (off + extTotal != body.Length)
            throw new FormatException("ClientHello extensions length mismatch.");

        var extensionTypes = new List<ushort>();
        var supportedVersions = new List<ushort>();
        var supportedGroups = new List<ushort>();
        var ecPointFormats = new List<byte>();
        var signatureAlgorithms = new List<ushort>();
        var alpnProtocols = new List<string>();
        string? serverName = null;
        byte[]? rawQuicTp = null;

        int extEnd = off + extTotal;
        while (off < extEnd)
        {
            if (off + 4 > extEnd)
                throw new FormatException("Truncated ClientHello extension header.");
            ushort extType = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(off, 2));
            ushort extLen = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(off + 2, 2));
            off += 4;
            if (off + extLen > extEnd)
                throw new FormatException($"Truncated ClientHello extension 0x{extType:X4}.");

            ReadOnlySpan<byte> extData = body.Slice(off, extLen);
            off += extLen;
            extensionTypes.Add(extType);

            switch (extType)
            {
                case TlsExtensionType.ServerName:
                    serverName ??= ParseFirstSni(extData);
                    break;

                case TlsExtensionType.SupportedGroups:
                    ParseUInt16PrefixedList(extData, supportedGroups, skipGrease: true);
                    break;

                case TlsExtensionType.EcPointFormats:
                    if (extData.Length >= 1)
                    {
                        byte listLen = extData[0];
                        for (int i = 1; i < Math.Min(1 + listLen, extData.Length); i++)
                            ecPointFormats.Add(extData[i]);
                    }
                    break;

                case TlsExtensionType.SignatureAlgorithms:
                    ParseUInt16PrefixedList(extData, signatureAlgorithms, skipGrease: true);
                    break;

                case TlsExtensionType.ApplicationLayerProtocolNegotiation:
                    ParseAlpn(extData, alpnProtocols);
                    break;

                case TlsExtensionType.SupportedVersions:
                    if (extData.Length >= 1)
                    {
                        byte vLen = extData[0];
                        for (int i = 1; i + 1 < Math.Min(1 + vLen, extData.Length); i += 2)
                        {
                            ushort ver = BinaryPrimitives.ReadUInt16BigEndian(extData.Slice(i, 2));
                            if (!GreaseHelper.IsGrease(ver))
                                supportedVersions.Add(ver);
                        }
                    }
                    break;

                case TlsExtensionType.QuicTransportParameters:
                    rawQuicTp = extData.ToArray();
                    break;
            }
        }

        ushort effectiveVersion = supportedVersions.Count > 0 ? supportedVersions.Max() : legacyVersion;

        var nonGreaseCiphers = ciphers.Where(c => !GreaseHelper.IsGrease(c)).ToList();
        var nonGreaseExtensions = extensionTypes.Where(e => !GreaseHelper.IsGrease(e)).ToList();

        // FoxIO JA4 specification:
        // a = proto(t/q) + version(13/12/11/10) + sni(d/i) + cipher_count(00..99) + ext_count(00..99) + alpn(first+last or "00")
        char proto = isQuic ? 'q' : 't';
        string verTag = effectiveVersion switch
        {
            0x0304 => "13",
            0x0303 => "12",
            0x0302 => "11",
            0x0301 => "10",
            0x0300 => "s3",
            _ => "00",
        };
        bool hasSni = !string.IsNullOrEmpty(serverName);
        char sniTag = hasSni ? 'd' : 'i';
        string cipherCountTag = Math.Min(nonGreaseCiphers.Count, 99).ToString("00", CultureInfo.InvariantCulture);
        string extCountTag = Math.Min(nonGreaseExtensions.Count, 99).ToString("00", CultureInfo.InvariantCulture);
        string alpnTag = FormatJa4Alpn(alpnProtocols);
        string ja4a = $"{proto}{verTag}{sniTag}{cipherCountTag}{extCountTag}{alpnTag}";

        // b = ciphers
        string ciphersSorted = string.Join(",", nonGreaseCiphers.OrderBy(x => x).Select(x => x.ToString("x4", CultureInfo.InvariantCulture)));
        string ciphersOriginal = string.Join(",", nonGreaseCiphers.Select(x => x.ToString("x4", CultureInfo.InvariantCulture)));
        string ja4b = nonGreaseCiphers.Count == 0 ? "000000000000" : Sha256Hex12(ciphersSorted);
        string ja4bo = nonGreaseCiphers.Count == 0 ? "000000000000" : Sha256Hex12(ciphersOriginal);

        // c = extensions (sorted omits SNI 0x0000 and ALPN 0x0010; original preserves them) + optional _sig_algs
        var sortedExtList = nonGreaseExtensions
            .Where(e => e != TlsExtensionType.ServerName && e != TlsExtensionType.ApplicationLayerProtocolNegotiation)
            .OrderBy(e => e)
            .Select(e => e.ToString("x4", CultureInfo.InvariantCulture))
            .ToList();
        var originalExtList = nonGreaseExtensions
            .Select(e => e.ToString("x4", CultureInfo.InvariantCulture))
            .ToList();

        string sigAlgsStr = string.Join(",", signatureAlgorithms.Select(s => s.ToString("x4", CultureInfo.InvariantCulture)));
        string sortedExtPart = string.Join(",", sortedExtList);
        string origExtPart = string.Join(",", originalExtList);

        string ja4cRaw = signatureAlgorithms.Count > 0 ? $"{sortedExtPart}_{sigAlgsStr}" : sortedExtPart;
        string ja4coRaw = signatureAlgorithms.Count > 0 ? $"{origExtPart}_{sigAlgsStr}" : origExtPart;

        string ja4c = string.IsNullOrEmpty(ja4cRaw) ? "000000000000" : Sha256Hex12(ja4cRaw);
        string ja4co = string.IsNullOrEmpty(ja4coRaw) ? "000000000000" : Sha256Hex12(ja4coRaw);

        string ja4 = $"{ja4a}_{ja4b}_{ja4c}";
        string ja4r = $"{ja4a}_{ciphersSorted}_{ja4cRaw}";
        string ja4o = $"{ja4a}_{ja4bo}_{ja4co}";
        string ja4ro = $"{ja4a}_{ciphersOriginal}_{ja4coRaw}";

        // JA3 / JA3n
        string ja3Ciphers = string.Join("-", nonGreaseCiphers.Select(c => c.ToString(CultureInfo.InvariantCulture)));
        string ja3Exts = string.Join("-", nonGreaseExtensions.Select(e => e.ToString(CultureInfo.InvariantCulture)));
        string ja3nExts = string.Join("-", nonGreaseExtensions.OrderBy(e => e).Select(e => e.ToString(CultureInfo.InvariantCulture)));
        string ja3Groups = string.Join("-", supportedGroups.Select(g => g.ToString(CultureInfo.InvariantCulture)));
        string ja3Formats = string.Join("-", ecPointFormats.Select(f => f.ToString(CultureInfo.InvariantCulture)));

        string ja3Text = $"{legacyVersion.ToString(CultureInfo.InvariantCulture)},{ja3Ciphers},{ja3Exts},{ja3Groups},{ja3Formats}";
        string ja3nText = $"{legacyVersion.ToString(CultureInfo.InvariantCulture)},{ja3Ciphers},{ja3nExts},{ja3Groups},{ja3Formats}";

        return new TlsWireFingerprintResult
        {
            LegacyVersion = legacyVersion,
            EffectiveVersion = effectiveVersion,
            IsQuic = isQuic,
            HasSni = hasSni,
            ServerName = serverName,
            CipherSuites = Array.AsReadOnly(ciphers.ToArray()),
            ExtensionTypes = Array.AsReadOnly(extensionTypes.ToArray()),
            SupportedGroups = Array.AsReadOnly(supportedGroups.ToArray()),
            EcPointFormats = Array.AsReadOnly(ecPointFormats.ToArray()),
            SignatureAlgorithms = Array.AsReadOnly(signatureAlgorithms.ToArray()),
            AlpnProtocols = Array.AsReadOnly(alpnProtocols.ToArray()),
            Ja4 = ja4,
            Ja4Raw = ja4r,
            Ja4Original = ja4o,
            Ja4RawOriginal = ja4ro,
            Ja3Text = ja3Text,
            Ja3Hash = Md5Hex(ja3Text),
            Ja3nText = ja3nText,
            Ja3nHash = Md5Hex(ja3nText),
            RawQuicTransportParameters = rawQuicTp,
        };
    }

    public static Http2WireFingerprintResult AnalyzeHttp2Spec(Http2SettingsSpec spec)
    {
        ArgumentNullException.ThrowIfNull(spec);
        return FormatAkamaiHttp2(spec.Settings, spec.ConnectionFlow, spec.PriorityFrames, spec.PseudoHeaderOrder);
    }

    /// <summary>
    /// Parses a raw HTTP/2 client connection preface burst (<c>PRI * HTTP/2.0...</c> + SETTINGS/WINDOW_UPDATE/PRIORITY frames)
    /// together with the decoded pseudo-header order from the first HEADERS frame.
    /// </summary>
    public static Http2WireFingerprintResult AnalyzeRawHttp2Preface(
        ReadOnlySpan<byte> wireBurst,
        IReadOnlyList<string> pseudoHeaderOrder)
    {
        ArgumentNullException.ThrowIfNull(pseudoHeaderOrder);
        if (wireBurst.Length < Http2PrefaceBytes.Length || !wireBurst.Slice(0, Http2PrefaceBytes.Length).SequenceEqual(Http2PrefaceBytes))
            throw new FormatException("Input does not start with RFC 9113 HTTP/2 connection preface.");

        var settings = new List<(ushort Id, uint Value)>();
        uint windowUpdate = 0;
        var priorities = new List<Http2PriorityFrame>();

        int off = Http2PrefaceBytes.Length;
        while (off + 9 <= wireBurst.Length)
        {
            int len = (wireBurst[off] << 16) | (wireBurst[off + 1] << 8) | wireBurst[off + 2];
            byte type = wireBurst[off + 3];
            byte flags = wireBurst[off + 4];
            uint streamId = BinaryPrimitives.ReadUInt32BigEndian(wireBurst.Slice(off + 5, 4)) & 0x7FFF_FFFFu;
            off += 9;
            if (off + len > wireBurst.Length)
                throw new FormatException("Truncated HTTP/2 frame inside preface burst.");

            ReadOnlySpan<byte> payload = wireBurst.Slice(off, len);
            off += len;

            if (type == 0x04 && (flags & 0x01) == 0) // SETTINGS
            {
                for (int i = 0; i + 6 <= payload.Length; i += 6)
                {
                    ushort id = BinaryPrimitives.ReadUInt16BigEndian(payload.Slice(i, 2));
                    uint val = BinaryPrimitives.ReadUInt32BigEndian(payload.Slice(i + 2, 4));
                    settings.Add((id, val));
                }
            }
            else if (type == 0x08 && streamId == 0 && payload.Length == 4) // WINDOW_UPDATE
            {
                windowUpdate = BinaryPrimitives.ReadUInt32BigEndian(payload) & 0x7FFF_FFFFu;
            }
            else if (type == 0x02 && payload.Length == 5) // PRIORITY
            {
                uint depRaw = BinaryPrimitives.ReadUInt32BigEndian(payload.Slice(0, 4));
                bool excl = (depRaw & 0x8000_0000u) != 0;
                uint dep = depRaw & 0x7FFF_FFFFu;
                byte weight = payload[4];
                priorities.Add(new Http2PriorityFrame(streamId, dep, excl, weight));
            }
            else
            {
                break;
            }
        }

        return FormatAkamaiHttp2(settings, windowUpdate, priorities, pseudoHeaderOrder);
    }

    /// <summary>
    /// Decrypts and inspects a wire QUIC v1 Client Initial UDP datagram serialized by <see cref="QuicConnection"/>.
    /// </summary>
    public static QuicInitialWireFingerprintResult AnalyzeQuicClientInitial(ReadOnlySpan<byte> datagram)
    {
        if (datagram.Length < 1200)
            throw new FormatException($"QUIC Initial datagram must be >= 1200 bytes (got {datagram.Length}).");

        if ((datagram[0] & 0x80) == 0 || ((datagram[0] >> 4) & 0x03) != 0)
            throw new FormatException("First packet in datagram is not a QUIC Long Header Initial packet.");

        uint version = BinaryPrimitives.ReadUInt32BigEndian(datagram.Slice(1, 4));
        int off = 5;
        byte dcidLen = datagram[off++];
        byte[] dcid = datagram.Slice(off, dcidLen).ToArray();
        off += dcidLen;
        byte scidLen = datagram[off++];
        byte[] scid = datagram.Slice(off, scidLen).ToArray();
        off += scidLen;

        if (!QuicVarInt.TryRead(datagram, ref off, out ulong tokenLen))
            throw new FormatException("Truncated QUIC Initial token length.");
        off += (int)tokenLen;
        if (!QuicVarInt.TryRead(datagram, ref off, out ulong pktLen))
            throw new FormatException("Truncated QUIC Initial length.");

        int pnOffset = off;
        int totalPktLen = pnOffset + (int)pktLen;
        if (totalPktLen > datagram.Length)
            throw new FormatException("Truncated QUIC Initial packet.");

        byte[] copy = datagram.Slice(0, totalPktLen).ToArray();
        QuicKeySet clientKeys = QuicCrypto.DeriveInitialKeys(dcid, isServer: false);
        if (!clientKeys.TryRemoveHeaderProtection(copy, pnOffset, out int pnLen, out _))
            throw new FormatException("Failed to remove QUIC Initial header protection.");

        ulong pn = QuicPacketCodec.ReadTruncatedPacketNumber(copy.AsSpan(pnOffset, pnLen), pnLen);
        if (!clientKeys.TryPacketUnprotect(pn, copy.AsSpan(0, pnOffset + pnLen), copy.AsSpan(pnOffset + pnLen), out byte[] plaintext))
            throw new FormatException("Failed to decrypt QUIC Initial payload.");

        List<QuicFrame> frames = QuicFrameCodec.DecodeAll(plaintext, QuicEncryptionLevel.Initial);
        bool hasPing = false;
        int paddingBytes = 0;
        var cryptoFragments = new SortedDictionary<ulong, byte[]>();
        foreach (QuicFrame f in frames)
        {
            switch (f)
            {
                case QuicPingFrame:
                    hasPing = true;
                    break;
                case QuicPaddingFrame p:
                    paddingBytes += p.Count;
                    break;
                case QuicCryptoFrame cf:
                    cryptoFragments[cf.Offset] = cf.Data;
                    break;
            }
        }

        using var chStream = new MemoryStream();
        ulong cursor = 0;
        foreach (KeyValuePair<ulong, byte[]> kv in cryptoFragments)
        {
            if (kv.Key != cursor)
                break;
            chStream.Write(kv.Value, 0, kv.Value.Length);
            cursor += (ulong)kv.Value.Length;
        }

        TlsWireFingerprintResult chFp = AnalyzeClientHello(chStream.ToArray(), isQuic: true);
        QuicTransportParameters? tp = chFp.RawQuicTransportParameters is { Length: > 0 }
            ? QuicTransportParametersCodec.Decode(chFp.RawQuicTransportParameters, isServerParameters: false)
            : null;

        return new QuicInitialWireFingerprintResult
        {
            Version = version,
            DatagramLength = datagram.Length,
            Dcid = dcid,
            Scid = scid,
            TokenLength = tokenLen,
            PacketNumber = pn,
            HasPingFrame = hasPing,
            CryptoFrameCount = cryptoFragments.Count,
            PaddingBytes = paddingBytes,
            ClientHelloFingerprint = chFp,
            TransportParameters = tp,
        };
    }

    private static Http2WireFingerprintResult FormatAkamaiHttp2(
        IReadOnlyList<(ushort Id, uint Value)> settings,
        uint windowUpdateIncrement,
        IReadOnlyList<Http2PriorityFrame> priorities,
        IReadOnlyList<string> pseudoHeaderOrder)
    {
        string settingsStr = string.Join(";", settings.Select(s => $"{s.Id}:{s.Value}"));
        string wuStr = windowUpdateIncrement > 0 ? windowUpdateIncrement.ToString(CultureInfo.InvariantCulture) : "00";
        string prioStr = priorities.Count == 0
            ? "0"
            : string.Join(",", priorities.Select(p => $"{p.StreamId}:{(p.Exclusive ? 1 : 0)}:{p.StreamDep}:{p.Weight}"));
        string pseudoStr = string.Join(",", pseudoHeaderOrder.Select(PseudoInitial));

        string akamaiText = $"{settingsStr}|{wuStr}|{prioStr}|{pseudoStr}";
        return new Http2WireFingerprintResult
        {
            Settings = Array.AsReadOnly(settings.ToArray()),
            WindowUpdateIncrement = windowUpdateIncrement,
            PriorityFrames = Array.AsReadOnly(priorities.ToArray()),
            PseudoHeaderOrder = Array.AsReadOnly(pseudoHeaderOrder.ToArray()),
            AkamaiText = akamaiText,
            AkamaiHash = Md5Hex(akamaiText),
        };
    }

    private static string PseudoInitial(string pseudoHeader) => pseudoHeader switch
    {
        ":method" => "m",
        ":authority" => "a",
        ":scheme" => "s",
        ":path" => "p",
        _ => pseudoHeader.TrimStart(':')[..1].ToLowerInvariant(),
    };

    private static ReadOnlySpan<byte> UnwrapTlsRecordIfPresent(ReadOnlySpan<byte> input)
    {
        if (input.Length >= 9 && input[0] == 0x16 && input[1] == 0x03 && input[5] == 0x01)
        {
            int recLen = BinaryPrimitives.ReadUInt16BigEndian(input.Slice(3, 2));
            if (5 + recLen <= input.Length)
                return input.Slice(5, recLen);
        }
        return input;
    }

    private static string? ParseFirstSni(ReadOnlySpan<byte> extData)
    {
        if (extData.Length < 5)
            return null;
        ushort listLen = BinaryPrimitives.ReadUInt16BigEndian(extData.Slice(0, 2));
        if (2 + listLen > extData.Length || extData[2] != 0x00)
            return null;
        ushort nameLen = BinaryPrimitives.ReadUInt16BigEndian(extData.Slice(3, 2));
        if (5 + nameLen > extData.Length)
            return null;
        return Encoding.ASCII.GetString(extData.Slice(5, nameLen));
    }

    private static void ParseUInt16PrefixedList(ReadOnlySpan<byte> extData, List<ushort> dst, bool skipGrease)
    {
        if (extData.Length < 2)
            return;
        ushort len = BinaryPrimitives.ReadUInt16BigEndian(extData.Slice(0, 2));
        int limit = Math.Min(2 + len, extData.Length);
        for (int i = 2; i + 1 < limit; i += 2)
        {
            ushort val = BinaryPrimitives.ReadUInt16BigEndian(extData.Slice(i, 2));
            if (!skipGrease || !GreaseHelper.IsGrease(val))
                dst.Add(val);
        }
    }

    private static void ParseAlpn(ReadOnlySpan<byte> extData, List<string> dst)
    {
        if (extData.Length < 2)
            return;
        ushort listLen = BinaryPrimitives.ReadUInt16BigEndian(extData.Slice(0, 2));
        int off = 2;
        int end = Math.Min(2 + listLen, extData.Length);
        while (off < end)
        {
            byte pLen = extData[off++];
            if (off + pLen > end)
                break;
            dst.Add(Encoding.ASCII.GetString(extData.Slice(off, pLen)));
            off += pLen;
        }
    }

    private static string FormatJa4Alpn(IReadOnlyList<string> protocols)
    {
        if (protocols.Count == 0 || string.IsNullOrEmpty(protocols[0]))
            return "00";

        string first = protocols[0];
        char c0 = first[0];
        char c1 = first[^1];
        if (IsAsciiAlphaNum(c0) && IsAsciiAlphaNum(c1))
            return new string(new[] { c0, c1 });

        byte[] utf8 = Encoding.UTF8.GetBytes(first);
        string hexFirst = utf8[0].ToString("x2", CultureInfo.InvariantCulture);
        string hexLast = utf8[^1].ToString("x2", CultureInfo.InvariantCulture);
        return new string(new[] { hexFirst[0], hexLast[1] });
    }

    private static bool IsAsciiAlphaNum(char c)
        => c is (>= '0' and <= '9') or (>= 'a' and <= 'z') or (>= 'A' and <= 'Z');

    private static string Sha256Hex12(string text)
    {
        byte[] hash = SHA256.HashData(Encoding.ASCII.GetBytes(text));
        return Convert.ToHexString(hash.AsSpan(0, 6)).ToLowerInvariant();
    }

    private static string Md5Hex(string text)
    {
        byte[] hash = MD5.HashData(Encoding.ASCII.GetBytes(text));
        return Convert.ToHexString(hash).ToLowerInvariant();
    }
}
