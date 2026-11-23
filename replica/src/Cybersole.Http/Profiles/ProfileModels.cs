using System.Buffers.Binary;
using System.Net;

namespace Cybersole.Http.Profiles;

/// <summary>TLS protocol version wire constants.</summary>
public static class TlsVersion
{
    public const ushort Tls10 = 0x0301;
    public const ushort Tls11 = 0x0302;
    public const ushort Tls12 = 0x0303;
    public const ushort Tls13 = 0x0304;
}

/// <summary>RFC 8701 GREASE constants and BoringSSL-compatible 6-slot resolver.</summary>
public static class GreaseHelper
{
    /// <summary>All 16 valid RFC 8701 GREASE code points (0x0A0A..0xFAFA).</summary>
    public static readonly IReadOnlyList<ushort> AllValues = Array.AsReadOnly(new ushort[]
    {
        0x0A0A, 0x1A1A, 0x2A2A, 0x3A3A,
        0x4A4A, 0x5A5A, 0x6A6A, 0x7A7A,
        0x8A8A, 0x9A9A, 0xAAAA, 0xBABA,
        0xCACA, 0xDADA, 0xEAEA, 0xFAFA,
    });

    /// <summary>Returns true if <paramref name="value"/> is one of the 16 RFC 8701 GREASE code points.</summary>
    public static bool IsGrease(ushort value)
    {
        byte hi = (byte)(value >> 8);
        byte lo = (byte)(value & 0xFF);
        return hi == lo && (lo & 0x0F) == 0x0A;
    }

    /// <summary>Builds a GREASE code point from nibble 0..15: (nibble &lt;&lt; 4) | 0x0A repeated in both bytes.</summary>
    public static ushort FromNibble(int nibble)
    {
        byte b = (byte)(((nibble & 0x0F) << 4) | 0x0A);
        return (ushort)((b << 8) | b);
    }

    /// <summary>Returns a uniformly chosen RFC 8701 GREASE code point.</summary>
    public static ushort RandomGrease(Random? random = null)
    {
        int index = (random ?? Random.Shared).Next(16);
        return FromNibble(index);
    }

    /// <summary>
    /// Allocates the 6 per-handshake GREASE slots matching sub_141297880 / sub_141299D30..E20,
    /// enforcing Extension2 != Extension1 via XOR 0x1010.
    /// </summary>
    public static GreaseSet GenerateSet(Random? random = null)
    {
        Random rng = random ?? Random.Shared;
        ushort g0 = RandomGrease(rng);
        ushort g1 = RandomGrease(rng);
        ushort g2 = RandomGrease(rng);
        ushort g3 = RandomGrease(rng);
        if (g3 == g2)
        {
            g3 ^= 0x1010;
        }
        ushort g4 = RandomGrease(rng);
        ushort g5 = RandomGrease(rng);
        return new GreaseSet(g0, g1, g2, g3, g4, g5);
    }

    /// <summary>
    /// Resolves all GREASE placeholders in a <see cref="ClientHelloSpec"/> into concrete RFC 8701 code points.
    /// Throws <see cref="InvalidOperationException"/> if more than two <see cref="GreaseExtension"/> entries exist.
    /// </summary>
    public static ClientHelloSpec ResolveGrease(ClientHelloSpec spec, Random? random = null)
    {
        ArgumentNullException.ThrowIfNull(spec);
        GreaseSet set = GenerateSet(random);

        var resolvedCiphers = new ushort[spec.CipherSuites.Count];
        for (int i = 0; i < spec.CipherSuites.Count; i++)
        {
            ushort c = spec.CipherSuites[i];
            resolvedCiphers[i] = IsGrease(c) ? set.CipherSuite : c;
        }

        var resolvedExts = new TlsExtensionSpec[spec.Extensions.Count];
        int greaseExtIndex = 0;
        for (int i = 0; i < spec.Extensions.Count; i++)
        {
            TlsExtensionSpec ext = spec.Extensions[i];
            switch (ext)
            {
                case GreaseExtension g:
                    ushort target = greaseExtIndex switch
                    {
                        0 => set.Extension1,
                        1 => set.Extension2,
                        _ => throw new InvalidOperationException("ClientHelloSpec cannot contain more than two GreaseExtension entries."),
                    };
                    greaseExtIndex++;
                    resolvedExts[i] = g with { ResolvedType = target };
                    break;

                case SupportedGroupsExtension sg:
                    var groups = new ushort[sg.Groups.Count];
                    for (int k = 0; k < sg.Groups.Count; k++)
                    {
                        ushort grp = sg.Groups[k];
                        groups[k] = IsGrease(grp) ? set.GroupAndKeyShare : grp;
                    }
                    resolvedExts[i] = new SupportedGroupsExtension(Array.AsReadOnly(groups));
                    break;

                case KeyShareExtension ks:
                    var entries = new KeyShareEntry[ks.Entries.Count];
                    for (int k = 0; k < ks.Entries.Count; k++)
                    {
                        KeyShareEntry e = ks.Entries[k];
                        entries[k] = IsGrease(e.Group)
                            ? e with { Group = set.GroupAndKeyShare }
                            : e;
                    }
                    resolvedExts[i] = new KeyShareExtension(Array.AsReadOnly(entries));
                    break;

                case SupportedVersionsExtension sv:
                    var versions = new ushort[sv.Versions.Count];
                    for (int k = 0; k < sv.Versions.Count; k++)
                    {
                        ushort v = sv.Versions[k];
                        versions[k] = IsGrease(v) ? set.SupportedVersion : v;
                    }
                    resolvedExts[i] = new SupportedVersionsExtension(Array.AsReadOnly(versions));
                    break;

                case SignatureAlgorithmsExtension sa:
                    var schemes = new ushort[sa.Schemes.Count];
                    for (int k = 0; k < sa.Schemes.Count; k++)
                    {
                        ushort s = sa.Schemes[k];
                        schemes[k] = IsGrease(s) ? set.SignatureAlgorithm : s;
                    }
                    resolvedExts[i] = new SignatureAlgorithmsExtension(Array.AsReadOnly(schemes));
                    break;

                default:
                    resolvedExts[i] = ext;
                    break;
            }
        }

        return new ClientHelloSpec(
            CipherSuites: Array.AsReadOnly(resolvedCiphers),
            CompressionMethods: spec.CompressionMethods,
            Extensions: Array.AsReadOnly(resolvedExts),
            ShuffleExtensions: spec.ShuffleExtensions,
            BoringPaddingStyle: spec.BoringPaddingStyle);
    }
}

/// <summary>The 6 per-ClientHello GREASE code points generated by sub_141297880.</summary>
public readonly record struct GreaseSet(
    ushort CipherSuite,
    ushort GroupAndKeyShare,
    ushort Extension1,
    ushort Extension2,
    ushort SupportedVersion,
    ushort SignatureAlgorithm);

/// <summary>TLS cipher suite wire IDs referenced across all 68 UtlsPresets builders.</summary>
public static class CipherSuiteId
{
    public const ushort GreasePlaceholder = 0x0A0A;

    // TLS 1.3
    public const ushort TLS_AES_128_GCM_SHA256 = 0x1301;
    public const ushort TLS_AES_256_GCM_SHA384 = 0x1302;
    public const ushort TLS_CHACHA20_POLY1305_SHA256 = 0x1303;

    // TLS 1.2 ECDHE-ECDSA / ECDHE-RSA AEAD
    public const ushort TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 = 0xC02B;
    public const ushort TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 = 0xC02C;
    public const ushort TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 = 0xC02F;
    public const ushort TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 = 0xC030;
    public const ushort TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256 = 0xCCA9;
    public const ushort TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256 = 0xCCA8;

    // TLS 1.2/1.0 ECDHE CBC & 3DES
    public const ushort TLS_ECDHE_ECDSA_WITH_3DES_EDE_CBC_SHA = 0xC008;
    public const ushort TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA = 0xC009;
    public const ushort TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA = 0xC00A;
    public const ushort TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA = 0xC012;
    public const ushort TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA = 0xC013;
    public const ushort TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA = 0xC014;
    public const ushort TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256 = 0xC023;
    public const ushort TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384 = 0xC024;
    public const ushort TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256 = 0xC027;
    public const ushort TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384 = 0xC028;

    // DHE-RSA
    public const ushort TLS_DHE_RSA_WITH_AES_128_CBC_SHA = 0x0033;
    public const ushort TLS_DHE_RSA_WITH_AES_256_CBC_SHA = 0x0039;

    // RSA key exchange
    public const ushort TLS_RSA_WITH_3DES_EDE_CBC_SHA = 0x000A;
    public const ushort TLS_RSA_WITH_AES_128_CBC_SHA = 0x002F;
    public const ushort TLS_RSA_WITH_AES_256_CBC_SHA = 0x0035;
    public const ushort TLS_RSA_WITH_AES_128_GCM_SHA256 = 0x009C;
    public const ushort TLS_RSA_WITH_AES_256_GCM_SHA384 = 0x009D;

    // SCSV
    public const ushort TLS_EMPTY_RENEGOTIATION_INFO_SCSV = 0x00FF;
}

/// <summary>TLS named group (supported_groups / key_share) wire IDs.</summary>
public static class NamedGroupId
{
    public const ushort GreasePlaceholder = 0x0A0A;
    public const ushort Secp256r1 = 0x0017;
    public const ushort Secp384r1 = 0x0018;
    public const ushort Secp521r1 = 0x0019;
    public const ushort X25519 = 0x001D;
    public const ushort Ffdhe2048 = 0x0100;
    public const ushort Ffdhe3072 = 0x0101;
    public const ushort X25519MLKEM768 = 0x11EC;
    public const ushort X25519Kyber768Draft00 = 0x6399;
}

/// <summary>TLS signature_algorithms / delegated_credentials wire IDs.</summary>
public static class SignatureSchemeId
{
    public const ushort GreasePlaceholder = 0x0A0A;
    public const ushort RsaPkcs1Sha1 = 0x0201;
    public const ushort DsaSha1 = 0x0202;
    public const ushort EcdsaSha1 = 0x0203;
    public const ushort RsaPkcs1Sha224 = 0x0301;
    public const ushort DsaSha224 = 0x0302;
    public const ushort EcdsaSha224 = 0x0303;
    public const ushort RsaPkcs1Sha256 = 0x0401;
    public const ushort DsaSha256 = 0x0402;
    public const ushort EcdsaSecp256r1Sha256 = 0x0403;
    public const ushort RsaPkcs1Sha384 = 0x0501;
    public const ushort DsaSha384 = 0x0502;
    public const ushort EcdsaSecp384r1Sha384 = 0x0503;
    public const ushort RsaPkcs1Sha512 = 0x0601;
    public const ushort DsaSha512 = 0x0602;
    public const ushort EcdsaSecp521r1Sha512 = 0x0603;
    public const ushort RsaPssRsaeSha256 = 0x0804;
    public const ushort RsaPssRsaeSha384 = 0x0805;
    public const ushort RsaPssRsaeSha512 = 0x0806;
    public const ushort Ed25519 = 0x0807;
    public const ushort Ed448 = 0x0808;
    public const ushort RsaPssPssSha256 = 0x0809;
    public const ushort RsaPssPssSha384 = 0x080A;
    public const ushort RsaPssPssSha512 = 0x080B;
    public const ushort MlDsa44 = 0x0904;
    public const ushort MlDsa65 = 0x0905;
    public const ushort MlDsa87 = 0x0906;
}

/// <summary>RFC 8879 certificate compression algorithms.</summary>
public enum CertCompressionAlgorithm : ushort
{
    Zlib = 1,
    Brotli = 2,
    Zstd = 3,
}

/// <summary>TLS ClientHello extension type code points.</summary>
public static class TlsExtensionType
{
    public const ushort ServerName = 0x0000;
    public const ushort StatusRequest = 0x0005;
    public const ushort SupportedGroups = 0x000A;
    public const ushort EcPointFormats = 0x000B;
    public const ushort SignatureAlgorithms = 0x000D;
    public const ushort ApplicationLayerProtocolNegotiation = 0x0010;
    public const ushort SignedCertificateTimestamp = 0x0012;
    public const ushort Padding = 0x0015;
    public const ushort EncryptThenMac = 0x0016;
    public const ushort ExtendedMasterSecret = 0x0017;
    public const ushort CompressCertificate = 0x001B;
    public const ushort RecordSizeLimit = 0x001C;
    public const ushort DelegatedCredentials = 0x0022;
    public const ushort SessionTicket = 0x0023;
    public const ushort PreSharedKey = 0x0029;
    public const ushort EarlyData = 0x002A;
    public const ushort SupportedVersions = 0x002B;
    public const ushort PskKeyExchangeModes = 0x002D;
    public const ushort KeyShare = 0x0033;
    public const ushort QuicTransportParameters = 0x0039;
    public const ushort ApplicationSettings = 0x4469;
    public const ushort ApplicationSettingsNew = 0x44CD;
    public const ushort TrustAnchors = 0xCA34;
    public const ushort EncryptedClientHello = 0xFE0D;
    public const ushort RenegotiationInfo = 0xFF01;
    public const ushort GreasePlaceholder = 0x0A0A;
}

/// <summary>Base type for strongly typed TLS ClientHello extensions.</summary>
public abstract record TlsExtensionSpec
{
    public abstract ushort ExtensionType { get; }
    public virtual bool IsGrease => false;
    public virtual bool IsPinnedDuringShuffle => false;
}

/// <summary>Extension 0x0000: server_name (SNI), with sub_141299BE0 sanitization helper.</summary>
public sealed record SniExtension(string? HostName = null) : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.ServerName;

    /// <summary>
    /// Sanitizes an SNI hostname per sub_141299BE0: strips IPv6 brackets and zone ID,
    /// returns null for IP literals (omitting SNI), and trims trailing dots.
    /// </summary>
    public static string? SanitizeHostName(string? host)
    {
        if (string.IsNullOrWhiteSpace(host))
        {
            return null;
        }

        string trimmed = host.Trim();
        if (trimmed.StartsWith('[') && trimmed.EndsWith(']') && trimmed.Length >= 2)
        {
            trimmed = trimmed[1..^1];
        }

        int zoneIdx = trimmed.IndexOf('%');
        if (zoneIdx >= 0)
        {
            trimmed = trimmed[..zoneIdx];
        }

        if (IPAddress.TryParse(trimmed, out _))
        {
            return null;
        }

        trimmed = trimmed.TrimEnd('.');
        return trimmed.Length == 0 ? null : trimmed;
    }
}

/// <summary>Extension 0x0005: status_request (OCSP type=1, empty responder/exts).</summary>
public sealed record StatusRequestExtension(byte StatusType = 1) : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.StatusRequest;
}

/// <summary>Extension 0x000A: supported_groups.</summary>
public sealed record SupportedGroupsExtension(IReadOnlyList<ushort> Groups) : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.SupportedGroups;
}

/// <summary>Extension 0x000B: ec_point_formats.</summary>
public sealed record EcPointFormatsExtension(IReadOnlyList<byte> Formats) : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.EcPointFormats;
}

/// <summary>Extension 0x000D: signature_algorithms.</summary>
public sealed record SignatureAlgorithmsExtension(IReadOnlyList<ushort> Schemes) : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.SignatureAlgorithms;
}

/// <summary>Extension 0x0010: application_layer_protocol_negotiation (ALPN).</summary>
public sealed record AlpnExtension(IReadOnlyList<string> Protocols) : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.ApplicationLayerProtocolNegotiation;
}

/// <summary>Extension 0x0012: signed_certificate_timestamp.</summary>
public sealed record SignedCertificateTimestampExtension() : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.SignedCertificateTimestamp;
}

/// <summary>Extension 0x0015: padding (BoringPaddingStyle, sub_14129A020 / sub_14129A060).</summary>
public sealed record PaddingExtension(int TargetLength = PaddingExtension.BoringPaddingTarget) : TlsExtensionSpec
{
    public const int BoringPaddingTarget = 512;
    public const int BoringMinUnpaddedLength = 256;
    public const int BoringMaxUnpaddedLength = 511;

    public override ushort ExtensionType => TlsExtensionType.Padding;
    public override bool IsPinnedDuringShuffle => true;

    /// <summary>
    /// Computes padding payload length using BoringPaddingStyle (sub_14129A020):
    /// when unpadded ClientHello body length L is in [256, 511] (or &lt; TargetLength),
    /// returns max(1, TargetLength - L - 4); otherwise returns 0 (no padding extension emitted).
    /// </summary>
    public int CalculatePaddingBytes(int unpaddedLength)
        => CalculatePaddingBytes(unpaddedLength, TargetLength);

    public static int CalculatePaddingBytes(int unpaddedLength, int targetLength = BoringPaddingTarget)
    {
        if (unpaddedLength < BoringMinUnpaddedLength)
        {
            return 0;
        }

        int maxUnpadded = targetLength == BoringPaddingTarget ? BoringMaxUnpaddedLength : targetLength - 1;
        if (unpaddedLength > maxUnpadded)
        {
            return 0;
        }

        return Math.Max(1, targetLength - unpaddedLength - 4);
    }
}

/// <summary>Extension 0x0016: encrypt_then_mac (empty payload).</summary>
public sealed record EncryptThenMacExtension() : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.EncryptThenMac;
}

/// <summary>Extension 0x0017: extended_master_secret.</summary>
public sealed record ExtendedMasterSecretExtension() : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.ExtendedMasterSecret;
}

/// <summary>Extension 0x001B: compress_certificate.</summary>
public sealed record CompressCertificateExtension(IReadOnlyList<CertCompressionAlgorithm> Algorithms) : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.CompressCertificate;
}

/// <summary>Extension 0x001C: record_size_limit.</summary>
public sealed record RecordSizeLimitExtension(ushort Limit = 16385) : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.RecordSizeLimit;
}

/// <summary>Extension 0x0022: delegated_credentials.</summary>
public sealed record DelegatedCredentialsExtension(IReadOnlyList<ushort> Schemes) : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.DelegatedCredentials;
}

/// <summary>Extension 0x0023: session_ticket.</summary>
public sealed record SessionTicketExtension() : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.SessionTicket;
}

/// <summary>Extension 0x0029: pre_shared_key (always last when present).</summary>
public sealed record PreSharedKeyExtension() : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.PreSharedKey;
    public override bool IsPinnedDuringShuffle => true;
}

/// <summary>Extension 0x002A: early_data (resumption-only).</summary>
public sealed record EarlyDataExtension() : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.EarlyData;
}

/// <summary>Extension 0x002B: supported_versions.</summary>
public sealed record SupportedVersionsExtension(IReadOnlyList<ushort> Versions) : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.SupportedVersions;
}

/// <summary>Extension 0x002D: psk_key_exchange_modes.</summary>
public sealed record PskKeyExchangeModesExtension(IReadOnlyList<byte> Modes) : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.PskKeyExchangeModes;
}

/// <summary>Single key share group entry preserving wire order and initial placeholder length (1 for GREASE, 0 for real groups).</summary>
public readonly record struct KeyShareEntry(ushort Group, int InitLength = 0);

/// <summary>Extension 0x0033: key_share.</summary>
public sealed record KeyShareExtension(IReadOnlyList<KeyShareEntry> Entries) : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.KeyShare;
}

/// <summary>Extension 0x0039: quic_transport_parameters.</summary>
public sealed record QuicTransportParametersExtension() : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.QuicTransportParameters;
}

/// <summary>Extension 0x4469 (ALPS old) or 0x44CD (ALPS new): application_settings.</summary>
public sealed record ApplicationSettingsExtension(ushort CodePoint, IReadOnlyList<string> AlpnProtocols) : TlsExtensionSpec
{
    public override ushort ExtensionType => CodePoint;
}

/// <summary>
/// Extension 0xCA34: TrustAnchors.
/// Chrome_146* emits empty 0x0000 (2 bytes); Chrome_152* emits 0x00B8 + 28 Fisher-Yates shuffled Trust Anchor IDs (186 bytes).
/// </summary>
public sealed record TrustAnchorsExtension(IReadOnlyList<byte[]> AnchorIds, byte[] RawPayload) : TlsExtensionSpec
{
    private static readonly byte[][] Chrome152CanonicalIds =
    {
        new byte[] { 0x82, 0xDF, 0x13, 0x02, 0x01 },
        new byte[] { 0x83, 0x9A, 0x64, 0x8C, 0x9B, 0x2D, 0x01, 0x0C },
        new byte[] { 0x83, 0x9A, 0x64, 0x8C, 0x9B, 0x2D, 0x01, 0x07 },
        new byte[] { 0xD6, 0x79, 0x09, 0x0C },
        new byte[] { 0x83, 0x9A, 0x64, 0x8C, 0x9B, 0x2D, 0x01, 0x0A },
        new byte[] { 0xD6, 0x79, 0x09, 0x0B },
        new byte[] { 0x83, 0x9A, 0x64, 0x8C, 0x9B, 0x2D, 0x01, 0x0D },
        new byte[] { 0x82, 0xDF, 0x13, 0x02, 0x0E },
        new byte[] { 0x83, 0x9A, 0x64, 0x8C, 0x9B, 0x2D, 0x01, 0x0B },
        new byte[] { 0xD6, 0x79, 0x09, 0x05 },
        new byte[] { 0x82, 0xDF, 0x13, 0x02, 0x0D },
        new byte[] { 0x82, 0xDF, 0x13, 0x02, 0x14 },
        new byte[] { 0xD6, 0x79, 0x09, 0x04 },
        new byte[] { 0xD6, 0x79, 0x09, 0x08 },
        new byte[] { 0xD6, 0x79, 0x09, 0x0D },
        new byte[] { 0xD6, 0x79, 0x09, 0x0A },
        new byte[] { 0xD6, 0x79, 0x09, 0x07 },
        new byte[] { 0x83, 0x9A, 0x64, 0x8C, 0x9B, 0x2D, 0x01, 0x12 },
        new byte[] { 0xD6, 0x79, 0x09, 0x01 },
        new byte[] { 0x82, 0xDF, 0x13, 0x02, 0x06 },
        new byte[] { 0x83, 0x9A, 0x64, 0x8C, 0x9B, 0x2D, 0x01, 0x08 },
        new byte[] { 0x82, 0xDF, 0x13, 0x02, 0x12 },
        new byte[] { 0x83, 0x9A, 0x64, 0x8C, 0x9B, 0x2D, 0x01, 0x13 },
        new byte[] { 0xD6, 0x79, 0x09, 0x0F },
        new byte[] { 0x82, 0xDF, 0x13, 0x02, 0x13 },
        new byte[] { 0x83, 0x9A, 0x64, 0x8C, 0x9B, 0x2D, 0x01, 0x09 },
        new byte[] { 0x82, 0xDF, 0x13, 0x02, 0x0F },
        new byte[] { 0xD6, 0x79, 0x09, 0x06 },
    };

    public override ushort ExtensionType => TlsExtensionType.TrustAnchors;

    /// <summary>Empty TrustAnchors extension (0x0000), used by Chrome_146 and Chrome_146_PSK.</summary>
    public static TrustAnchorsExtension Empty { get; } = new(
        Array.AsReadOnly(Array.Empty<byte[]>()),
        new byte[] { 0x00, 0x00 });

    /// <summary>Static shuffled 28 Trust Anchor IDs initialized once (sub_1412BA740 + sub_1412BA940), used by Chrome_152 and Chrome_152_PSK.</summary>
    public static TrustAnchorsExtension Chrome152 { get; } = CreateChrome152();

    public static TrustAnchorsExtension CreateChrome152(Random? random = null)
    {
        var ids = new byte[Chrome152CanonicalIds.Length][];
        for (int i = 0; i < Chrome152CanonicalIds.Length; i++)
        {
            ids[i] = (byte[])Chrome152CanonicalIds[i].Clone();
        }

        Random rng = random ?? Random.Shared;
        for (int i = ids.Length - 1; i >= 1; i--)
        {
            int j = rng.Next(0, i + 1);
            (ids[i], ids[j]) = (ids[j], ids[i]);
        }

        return new TrustAnchorsExtension(Array.AsReadOnly(ids), BuildWirePayload(ids));
    }

    public static byte[] BuildWirePayload(IReadOnlyList<byte[]> anchorIds)
    {
        int bodyLen = 0;
        for (int i = 0; i < anchorIds.Count; i++)
        {
            bodyLen += 1 + anchorIds[i].Length;
        }

        var payload = new byte[2 + bodyLen];
        BinaryPrimitives.WriteUInt16BigEndian(payload.AsSpan(0, 2), (ushort)bodyLen);
        int offset = 2;
        for (int i = 0; i < anchorIds.Count; i++)
        {
            byte[] id = anchorIds[i];
            payload[offset++] = (byte)id.Length;
            id.CopyTo(payload, offset);
            offset += id.Length;
        }
        return payload;
    }
}

/// <summary>HPKE cipher suite pair (KDF, AEAD) advertised inside GREASE ECH (0xFE0D).</summary>
public readonly record struct GreaseEchCipherSuite(ushort KdfId, ushort AeadId);

/// <summary>Extension 0xFE0D: encrypted_client_hello (GREASE ECH).</summary>
public sealed record GreaseEchExtension(
    IReadOnlyList<GreaseEchCipherSuite> CipherSuites,
    IReadOnlyList<int> PayloadLengths,
    bool IsPayloadLengthRange = false) : TlsExtensionSpec
{
    public override ushort ExtensionType => TlsExtensionType.EncryptedClientHello;

    public static GreaseEchExtension ChromePreset { get; } = new(
        Array.AsReadOnly(new[] { new GreaseEchCipherSuite(1, 1) }),
        Array.AsReadOnly(new[] { 128, 160, 192, 224 }),
        IsPayloadLengthRange: false);

    public static GreaseEchExtension Firefox132PlusPreset { get; } = new(
        Array.AsReadOnly(new[]
        {
            new GreaseEchCipherSuite(1, 1),
            new GreaseEchCipherSuite(1, 2),
            new GreaseEchCipherSuite(1, 3),
        }),
        Array.AsReadOnly(new[] { 128, 223 }),
        IsPayloadLengthRange: true);

    public int PickPayloadLength(Random? random = null)
    {
        Random rng = random ?? Random.Shared;
        if (IsPayloadLengthRange && PayloadLengths.Count >= 2)
        {
            return rng.Next(PayloadLengths[0], PayloadLengths[1] + 1);
        }
        return PayloadLengths[rng.Next(PayloadLengths.Count)];
    }
}

/// <summary>Extension 0xFF01: renegotiation_info. Always emits [0x00] regardless of ConstructorArg.</summary>
public sealed record RenegotiationInfoExtension(int ConstructorArg = 1) : TlsExtensionSpec
{
    private static readonly byte[] EmptyRenegotiationInfoWire = { 0x00 };

    public override ushort ExtensionType => TlsExtensionType.RenegotiationInfo;
    public byte[] WirePayload => EmptyRenegotiationInfoWire;
}

/// <summary>Dynamic GREASE placeholder extension (resolved per handshake to grease[2] and grease[3]).</summary>
public sealed record GreaseExtension(ushort ResolvedType = TlsExtensionType.GreasePlaceholder, byte[]? Payload = null)
    : TlsExtensionSpec
{
    public override ushort ExtensionType => ResolvedType;
    public override bool IsGrease => true;
    public override bool IsPinnedDuringShuffle => true;
}

/// <summary>Opaque raw extension for custom or unrecognized extension types.</summary>
public sealed record CustomRawExtension(ushort ExtensionTypeValue, byte[] Payload) : TlsExtensionSpec
{
    public override ushort ExtensionType => ExtensionTypeValue;
}

/// <summary>
/// Implements Chrome/BoringSSL ClientHello extension permutation (sub_141299EE0 + sub_141299FE0):
/// Fisher-Yates from Count-1 down to 1, skipping any swap where either slot is pinned
/// (GreaseExtension, PaddingExtension, PreSharedKeyExtension).
/// </summary>
public static class ExtensionShuffler
{
    public static bool IsPinned(TlsExtensionSpec extension)
        => extension.IsPinnedDuringShuffle || extension is GreaseExtension or PaddingExtension or PreSharedKeyExtension;

    public static void ShuffleInPlace(IList<TlsExtensionSpec> extensions, Random? random = null)
    {
        ArgumentNullException.ThrowIfNull(extensions);
        Random rng = random ?? Random.Shared;
        for (int i = extensions.Count - 1; i >= 1; i--)
        {
            int j = rng.Next(0, i + 1);
            if (!IsPinned(extensions[i]) && !IsPinned(extensions[j]))
            {
                (extensions[i], extensions[j]) = (extensions[j], extensions[i]);
            }
        }
    }

    public static IReadOnlyList<TlsExtensionSpec> Shuffle(IReadOnlyList<TlsExtensionSpec> extensions, Random? random = null)
    {
        ArgumentNullException.ThrowIfNull(extensions);
        var copy = new TlsExtensionSpec[extensions.Count];
        for (int i = 0; i < extensions.Count; i++)
        {
            copy[i] = extensions[i];
        }

        ShuffleInPlace(copy, random);
        return Array.AsReadOnly(copy);
    }

    public static ClientHelloSpec Apply(ClientHelloSpec spec, Random? random = null)
    {
        ArgumentNullException.ThrowIfNull(spec);
        if (!spec.ShuffleExtensions)
        {
            return spec;
        }

        return new ClientHelloSpec(
            CipherSuites: spec.CipherSuites,
            CompressionMethods: spec.CompressionMethods,
            Extensions: Shuffle(spec.Extensions, random),
            ShuffleExtensions: spec.ShuffleExtensions,
            BoringPaddingStyle: spec.BoringPaddingStyle);
    }
}

/// <summary>Full ClientHello blueprint returned by each preset's factory delegate.</summary>
public sealed class ClientHelloSpec
{
    private static readonly IReadOnlyList<byte> DefaultCompressionMethods = Array.AsReadOnly(new byte[] { 0x00 });

    public ClientHelloSpec(
        IReadOnlyList<ushort> CipherSuites,
        IReadOnlyList<TlsExtensionSpec> Extensions,
        bool ShuffleExtensions = false,
        bool? BoringPaddingStyle = null,
        IReadOnlyList<byte>? CompressionMethods = null)
    {
        this.CipherSuites = CipherSuites ?? throw new ArgumentNullException(nameof(CipherSuites));
        this.Extensions = Extensions ?? throw new ArgumentNullException(nameof(Extensions));
        this.CompressionMethods = CompressionMethods ?? DefaultCompressionMethods;
        this.ShuffleExtensions = ShuffleExtensions;
        this.BoringPaddingStyle = BoringPaddingStyle ?? HasExtensionType(Extensions, TlsExtensionType.Padding);
        (MinVersion, MaxVersion) = ComputeVersionBounds(Extensions);
        AlpnProtocols = ExtractAlpn(Extensions);
    }

    public IReadOnlyList<ushort> CipherSuites { get; }
    public IReadOnlyList<byte> CompressionMethods { get; }
    public IReadOnlyList<TlsExtensionSpec> Extensions { get; }
    public bool ShuffleExtensions { get; }
    public bool BoringPaddingStyle { get; }
    public ushort MinVersion { get; }
    public ushort MaxVersion { get; }
    public IReadOnlyList<string> AlpnProtocols { get; }

    public bool HasExtension(ushort extensionType)
    {
        if (GreaseHelper.IsGrease(extensionType))
        {
            for (int i = 0; i < Extensions.Count; i++)
            {
                if (Extensions[i].IsGrease)
                {
                    return true;
                }
            }
            return false;
        }

        return HasExtensionType(Extensions, extensionType);
    }

    public T? GetExtension<T>() where T : TlsExtensionSpec
    {
        for (int i = 0; i < Extensions.Count; i++)
        {
            if (Extensions[i] is T match)
            {
                return match;
            }
        }
        return null;
    }

    /// <summary>Resolves dynamic GREASE code points and applies ExtensionShuffler when enabled.</summary>
    public ClientHelloSpec Materialize(Random? random = null)
    {
        Random rng = random ?? Random.Shared;
        ClientHelloSpec resolved = GreaseHelper.ResolveGrease(this, rng);
        return ExtensionShuffler.Apply(resolved, rng);
    }

    private static bool HasExtensionType(IReadOnlyList<TlsExtensionSpec> extensions, ushort extensionType)
    {
        for (int i = 0; i < extensions.Count; i++)
        {
            if (!extensions[i].IsGrease && extensions[i].ExtensionType == extensionType)
            {
                return true;
            }
        }
        return false;
    }

    private static (ushort Min, ushort Max) ComputeVersionBounds(IReadOnlyList<TlsExtensionSpec> extensions)
    {
        for (int i = 0; i < extensions.Count; i++)
        {
            if (extensions[i] is SupportedVersionsExtension sv)
            {
                ushort min = ushort.MaxValue;
                ushort max = 0;
                bool foundNonGrease = false;
                for (int k = 0; k < sv.Versions.Count; k++)
                {
                    ushort v = sv.Versions[k];
                    if (GreaseHelper.IsGrease(v))
                    {
                        continue;
                    }
                    foundNonGrease = true;
                    if (v < min) min = v;
                    if (v > max) max = v;
                }
                if (foundNonGrease)
                {
                    return (min, max);
                }
            }
        }

        return (TlsVersion.Tls10, TlsVersion.Tls12);
    }

    private static IReadOnlyList<string> ExtractAlpn(IReadOnlyList<TlsExtensionSpec> extensions)
    {
        for (int i = 0; i < extensions.Count; i++)
        {
            if (extensions[i] is AlpnExtension alpn)
            {
                return alpn.Protocols;
            }
        }
        return Array.AsReadOnly(Array.Empty<string>());
    }
}

/// <summary>HTTP/2 SETTINGS parameter identifiers observed across UtlsPresets.</summary>
public static class Http2SettingId
{
    public const ushort HeaderTableSize = 1;
    public const ushort EnablePush = 2;
    public const ushort MaxConcurrentStreams = 3;
    public const ushort InitialWindowSize = 4;
    public const ushort MaxFrameSize = 5;
    public const ushort MaxHeaderListSize = 6;
    public const ushort EnableConnectProtocol = 8;
    public const ushort NoRfc7540Priorities = 9;
}

/// <summary>HTTP/2 HEADERS priority tuple (StreamDep, Exclusive, raw Weight byte).</summary>
public readonly record struct Http2HeaderPriority(uint StreamDep, bool Exclusive, byte Weight)
{
    public static readonly Http2HeaderPriority Default = new(0, Exclusive: true, Weight: 255);
    public static readonly Http2HeaderPriority Suppressed = new(0, Exclusive: false, Weight: 0);

    public bool IsSuppressed => StreamDep == 0 && !Exclusive && Weight == 0;
}

/// <summary>HTTP/2 startup PRIORITY frame descriptor (12-byte struct at ClientProfile +0x38).</summary>
public readonly record struct Http2PriorityFrame(uint StreamId, uint StreamDep, bool Exclusive, byte Weight);

/// <summary>HTTP/2 connection fingerprint specification.</summary>
public sealed class Http2SettingsSpec
{
    public const uint DefaultConnectionFlow = 15663105;

    public static readonly IReadOnlyList<string> DefaultFallbackPseudoHeaderOrder =
        Array.AsReadOnly(new[] { ":authority", ":method", ":path", ":scheme" });

    public Http2SettingsSpec(
        IReadOnlyList<(ushort Id, uint Value)> Settings,
        uint ConnectionFlow,
        IReadOnlyList<string> PseudoHeaderOrder,
        Http2HeaderPriority? HeaderPriority = null,
        IReadOnlyList<Http2PriorityFrame>? PriorityFrames = null,
        IReadOnlyList<string>? HeaderOrder = null,
        uint NextStreamIdOverride = 0,
        bool StartAtStream3 = false)
    {
        this.Settings = Settings ?? throw new ArgumentNullException(nameof(Settings));
        this.ConnectionFlow = ConnectionFlow == 0 ? DefaultConnectionFlow : ConnectionFlow;
        this.PseudoHeaderOrder = PseudoHeaderOrder ?? DefaultFallbackPseudoHeaderOrder;
        this.HeaderPriority = HeaderPriority;
        this.PriorityFrames = PriorityFrames ?? Array.AsReadOnly(Array.Empty<Http2PriorityFrame>());
        this.HeaderOrder = HeaderOrder;
        this.NextStreamIdOverride = NextStreamIdOverride;
        this.StartAtStream3 = StartAtStream3;

        bool noRfc7540 = false;
        for (int i = 0; i < this.Settings.Count; i++)
        {
            if (this.Settings[i].Id == Http2SettingId.NoRfc7540Priorities && this.Settings[i].Value != 0)
            {
                noRfc7540 = true;
                break;
            }
        }
        NoRfc7540Priorities = noRfc7540;
    }

    public IReadOnlyList<(ushort Id, uint Value)> Settings { get; }
    public uint ConnectionFlow { get; }
    public Http2HeaderPriority? HeaderPriority { get; }
    public Http2HeaderPriority EffectiveHeaderPriority => HeaderPriority ?? Http2HeaderPriority.Default;
    public bool IsHeaderPrioritySuppressed => HeaderPriority is { IsSuppressed: true };
    public IReadOnlyList<string> PseudoHeaderOrder { get; }
    public IReadOnlyList<string>? HeaderOrder { get; }
    public IReadOnlyList<Http2PriorityFrame> PriorityFrames { get; }
    public bool NoRfc7540Priorities { get; }
    public uint NextStreamIdOverride { get; }
    public bool StartAtStream3 { get; }

    public uint EffectiveInitialNextStreamId
    {
        get
        {
            if (PriorityFrames.Count > 0)
            {
                return PriorityFrames[^1].StreamId + 2;
            }
            if (NextStreamIdOverride != 0)
            {
                return NextStreamIdOverride;
            }
            return StartAtStream3 ? 3u : 1u;
        }
    }
}

/// <summary>HTTP/3 settings identifiers observed in UtlsPresets and sub_1412C5B60.</summary>
public static class Http3SettingId
{
    public const ulong QpackMaxTableCapacity = 1;
    public const ulong MaxFieldSectionSize = 6;
    public const ulong QpackBlockedStreams = 7;
    public const ulong EnableConnectProtocol = 8;
    public const ulong H3Datagram = 51;
    public const ulong FirefoxCustom0 = 0x2B603742;
    public const ulong FirefoxCustom1 = 0x00FFD277;
}

/// <summary>HTTP/3 connection fingerprint specification (ClientProfile +0x40..+0x65).</summary>
public sealed class Http3SettingsSpec
{
    public static readonly IReadOnlyList<string> DefaultFallbackPseudoHeaderOrder =
        Array.AsReadOnly(new[] { ":method", ":authority", ":scheme", ":path" });

    public Http3SettingsSpec(
        IReadOnlyList<(ulong Id, ulong Value)> Settings,
        IReadOnlyList<ulong> SettingsOrder,
        IReadOnlyList<string> PseudoHeaderOrder,
        uint ChromeH3Flag = 0,
        bool SendGreaseFrame = false,
        ulong? GreaseSettingValue = null,
        IReadOnlyList<string>? HeaderOrder = null)
    {
        this.Settings = Settings ?? throw new ArgumentNullException(nameof(Settings));
        this.SettingsOrder = SettingsOrder ?? throw new ArgumentNullException(nameof(SettingsOrder));
        this.PseudoHeaderOrder = PseudoHeaderOrder ?? DefaultFallbackPseudoHeaderOrder;
        this.ChromeH3Flag = ChromeH3Flag;
        this.SendGreaseFrame = SendGreaseFrame;
        this.GreaseSettingValue = GreaseSettingValue;
        this.HeaderOrder = HeaderOrder;

        SendGreaseSettings = ChromeH3Flag != 0;

        ulong? qpackMax = null;
        ulong? maxField = null;
        ulong? qpackBlocked = null;
        bool h3Datagram = false;
        bool enableConnect = false;

        for (int i = 0; i < this.Settings.Count; i++)
        {
            (ulong id, ulong val) = this.Settings[i];
            switch (id)
            {
                case Http3SettingId.QpackMaxTableCapacity:
                    qpackMax = val;
                    break;
                case Http3SettingId.MaxFieldSectionSize:
                    maxField = val;
                    break;
                case Http3SettingId.QpackBlockedStreams:
                    qpackBlocked = val;
                    break;
                case Http3SettingId.H3Datagram:
                    h3Datagram = val != 0;
                    break;
                case Http3SettingId.EnableConnectProtocol:
                    enableConnect = val != 0;
                    break;
            }
        }

        QpackMaxTableCapacity = qpackMax;
        MaxFieldSectionSize = maxField;
        QpackBlockedStreams = qpackBlocked;
        EnableH3Datagram = h3Datagram;
        EnableConnectProtocol = enableConnect;
    }

    public IReadOnlyList<(ulong Id, ulong Value)> Settings { get; }
    public ulong? QpackMaxTableCapacity { get; }
    public ulong? MaxFieldSectionSize { get; }
    public ulong? QpackBlockedStreams { get; }
    public bool EnableH3Datagram { get; }
    public bool EnableConnectProtocol { get; }
    public IReadOnlyList<ulong> SettingsOrder { get; }
    public ulong? GreaseSettingValue { get; }
    public bool SendGreaseSettings { get; }
    public bool SendGreaseFrame { get; }
    public uint ChromeH3Flag { get; }
    public IReadOnlyList<string> PseudoHeaderOrder { get; }
    public IReadOnlyList<string>? HeaderOrder { get; }

    /// <summary>
    /// Builds the wire HTTP/3 SETTINGS sequence matching sub_1412C5B60:
    /// emits settings in SettingsOrder, optionally appending a GREASE setting when ChromeH3Flag != 0.
    /// </summary>
    public IReadOnlyList<(ulong Id, ulong Value)> BuildWireSettings(Random? random = null)
        => BuildWireSettings(this, random);

    public static IReadOnlyList<(ulong Id, ulong Value)> BuildWireSettings(Http3SettingsSpec? spec, Random? random = null)
    {
        var map = new Dictionary<ulong, ulong>();
        uint flag = spec?.ChromeH3Flag ?? 0;
        if (flag != 0)
        {
            map[Http3SettingId.MaxFieldSectionSize] = 262144;
        }
        map[Http3SettingId.H3Datagram] = 1;

        var order = new List<ulong>();
        if (spec is not null)
        {
            for (int i = 0; i < spec.Settings.Count; i++)
            {
                map[spec.Settings[i].Id] = spec.Settings[i].Value;
            }
            for (int i = 0; i < spec.SettingsOrder.Count; i++)
            {
                order.Add(spec.SettingsOrder[i]);
            }
        }

        if (flag != 0)
        {
            Random rng = random ?? Random.Shared;
            ulong greaseId = spec?.GreaseSettingValue ?? (31UL * (ulong)rng.Next(0x8421083) + 33UL);
            ulong greaseVal = (ulong)rng.Next(1, 0x40000000);
            map[greaseId] = greaseVal;
            if (!order.Contains(greaseId))
            {
                order.Add(greaseId);
            }
        }

        var result = new List<(ulong Id, ulong Value)>(map.Count);
        for (int i = 0; i < order.Count; i++)
        {
            ulong key = order[i];
            if (map.Remove(key, out ulong val))
            {
                result.Add((key, val));
            }
        }

        foreach (KeyValuePair<ulong, ulong> kv in map)
        {
            result.Add((kv.Key, kv.Value));
        }

        return Array.AsReadOnly(result.ToArray());
    }
}

/// <summary>QUIC transport parameters and connection options matching ClientTransportParameters (sub_1412B00B0 / sub_1412A3DD0).</summary>
public sealed class QuicTransportSpec
{
    public Func<ClientHelloSpec> CreateClientHelloSpec { get; init; } = ChromeQuicSpecs.CreateClientHelloSpec;
    public ulong InitialMaxData { get; init; } = 15_728_640;
    public ulong InitialMaxStreamDataBidiLocal { get; init; } = 6_291_456;
    public ulong InitialMaxStreamDataBidiRemote { get; init; } = 6_291_456;
    public ulong InitialMaxStreamDataUni { get; init; } = 6_291_456;
    public ulong InitialMaxStreamsBidi { get; init; } = 100;
    public ulong InitialMaxStreamsUni { get; init; } = 103;
    public ulong MaxIdleTimeoutMs { get; init; } = 30_000;
    public ulong MaxUdpPayloadSize { get; init; } = 1_250;
    public ulong ClientTransportDefaultMaxUdpPayloadSize { get; init; } = 1_472;
    public ulong MaxDatagramFrameSize { get; init; } = 65_536;
    public ulong AckDelayExponent { get; init; } = 3;
    public ulong MaxAckDelayMs { get; init; } = 25;
    public bool DisableActiveMigration { get; init; }
    public bool GreaseTransportParameters { get; init; } = true;
    public bool ShuffleTransportParameters { get; init; } = true;
    public int InitialPacketSize { get; init; } = 1_200;
    public uint QuicVersion { get; init; } = 0x00000001;
    public bool SendGreaseVersionInformation { get; init; } = true;
    public string GoogleConnectionOptions { get; init; } = "ORIG";
    public ulong? GoogleInitialRttUs { get; init; }
    public int ScidLength { get; init; }
    public int DcidLength { get; init; } = 8;
    public TimeSpan HandshakeTimeout { get; init; } = TimeSpan.FromSeconds(10);
}

/// <summary>Complete browser fingerprint profile matching ClientProfile (MT 0x144CB65F0).</summary>
public sealed class ClientProfile
{
    private readonly Lazy<bool> _supportsSessionResumption;
    private readonly Lazy<(bool Tls12, bool Tls13, IReadOnlyList<ushort> Ciphers)> _tcpSummary;

    public ClientProfile(
        string Name,
        int SlotIndex,
        Func<ClientHelloSpec> CreateClientHelloSpec,
        Http2SettingsSpec Http2Settings,
        Http3SettingsSpec? Http3Settings = null,
        QuicTransportSpec? QuicSpec = null,
        bool ShuffleExtensions = false,
        bool DisableHttp2 = false)
    {
        this.Name = Name ?? throw new ArgumentNullException(nameof(Name));
        this.SlotIndex = SlotIndex;
        this.CreateClientHelloSpec = CreateClientHelloSpec ?? throw new ArgumentNullException(nameof(CreateClientHelloSpec));
        this.Http2Settings = Http2Settings ?? throw new ArgumentNullException(nameof(Http2Settings));
        this.Http3Settings = Http3Settings;
        this.QuicSpec = QuicSpec;
        this.ShuffleExtensions = ShuffleExtensions;
        this.DisableHttp2 = DisableHttp2;

        _supportsSessionResumption = new Lazy<bool>(
            () => this.CreateClientHelloSpec().HasExtension(TlsExtensionType.PreSharedKey),
            LazyThreadSafetyMode.ExecutionAndPublication);

        _tcpSummary = new Lazy<(bool, bool, IReadOnlyList<ushort>)>(
            () =>
            {
                ClientHelloSpec spec = this.CreateClientHelloSpec();
                bool tls12 = spec.MinVersion <= TlsVersion.Tls12 && spec.MaxVersion >= TlsVersion.Tls12;
                bool tls13 = spec.MaxVersion >= TlsVersion.Tls13;
                return (tls12, tls13, spec.CipherSuites);
            },
            LazyThreadSafetyMode.ExecutionAndPublication);
    }

    public string Name { get; }
    public int SlotIndex { get; }
    public Func<ClientHelloSpec> CreateClientHelloSpec { get; }
    public Http2SettingsSpec Http2Settings { get; }
    public Http3SettingsSpec? Http3Settings { get; }
    public QuicTransportSpec? QuicSpec { get; }
    public Func<ClientHelloSpec>? CreateQuicClientHelloSpec => QuicSpec?.CreateClientHelloSpec;
    public bool ShuffleExtensions { get; }
    public bool DisableHttp2 { get; }
    public bool SupportsHttp3 => QuicSpec is not null && !DisableHttp2;
    public bool SupportsSessionResumption => _supportsSessionResumption.Value;
    public bool Tls12Supported => _tcpSummary.Value.Tls12;
    public bool Tls13Supported => _tcpSummary.Value.Tls13;
    public IReadOnlyList<ushort> CipherSuites => _tcpSummary.Value.Ciphers;

    /// <summary>
    /// Computes effective ALPN list per sub_141297880 lines 242-304:
    /// forceHttp11 returns ["http/1.1"]; DisableHttp2 strips "h2".
    /// </summary>
    public IReadOnlyList<string> GetEffectiveAlpn(bool forceHttp11 = false)
    {
        if (forceHttp11)
        {
            return Array.AsReadOnly(new[] { "http/1.1" });
        }

        IReadOnlyList<string> baseAlpn = CreateClientHelloSpec().AlpnProtocols;
        if (!DisableHttp2)
        {
            return baseAlpn;
        }

        var filtered = new List<string>(baseAlpn.Count);
        for (int i = 0; i < baseAlpn.Count; i++)
        {
            if (!string.Equals(baseAlpn[i], "h2", StringComparison.Ordinal))
            {
                filtered.Add(baseAlpn[i]);
            }
        }
        return Array.AsReadOnly(filtered.ToArray());
    }
}

/// <summary>Thrown by ProfileRegistry.GetRequired when a profile key is not found (sub_1412BB5B0, E_INVALIDARG).</summary>
public sealed class UnknownProfileException : ArgumentException
{
    public UnknownProfileException(string? profileName)
        : base($"Unknown profile \"{profileName}\"")
    {
        ProfileName = profileName ?? string.Empty;
        HResult = unchecked((int)0x80070057);
    }

    public string ProfileName { get; }
}
