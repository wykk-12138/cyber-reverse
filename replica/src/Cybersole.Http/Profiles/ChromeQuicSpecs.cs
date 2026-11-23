namespace Cybersole.Http.Profiles;

/// <summary>
/// Shared QUIC ClientHello spec (0x1412B9F20) and HTTP/3 presets for H3-enabled Chrome profiles
/// (Chrome_144..Chrome_152_PSK) plus Firefox 147/148 HTTP/3 settings metadata.
/// </summary>
public static class ChromeQuicSpecs
{
    private static readonly IReadOnlyList<ushort> QuicCipherSuites = Array.AsReadOnly(new ushort[]
    {
        CipherSuiteId.TLS_AES_128_GCM_SHA256,
        CipherSuiteId.TLS_AES_256_GCM_SHA384,
        CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256,
    });

    private static readonly IReadOnlyList<string> H3Alpn = Array.AsReadOnly(new[] { "h3" });

    private static readonly IReadOnlyList<ushort> Tls13OnlyVersions = Array.AsReadOnly(new ushort[]
    {
        TlsVersion.Tls13,
    });

    private static readonly IReadOnlyList<KeyShareEntry> ChromeQuicKeyShares = Array.AsReadOnly(new[]
    {
        new KeyShareEntry(NamedGroupId.X25519MLKEM768, InitLength: 0),
        new KeyShareEntry(NamedGroupId.X25519, InitLength: 0),
    });

    private static readonly IReadOnlyList<byte> PskModes = Array.AsReadOnly(new byte[] { 1 });

    private static readonly IReadOnlyList<CertCompressionAlgorithm> BrotliCompression =
        Array.AsReadOnly(new[] { CertCompressionAlgorithm.Brotli });

    private static readonly IReadOnlyList<ushort> ChromeQuicSignatureAlgorithms = Array.AsReadOnly(new ushort[]
    {
        SignatureSchemeId.EcdsaSecp256r1Sha256,
        SignatureSchemeId.RsaPssRsaeSha256,
        SignatureSchemeId.RsaPkcs1Sha256,
        SignatureSchemeId.EcdsaSecp384r1Sha384,
        SignatureSchemeId.RsaPssRsaeSha384,
        SignatureSchemeId.RsaPkcs1Sha384,
        SignatureSchemeId.RsaPssRsaeSha512,
        SignatureSchemeId.RsaPkcs1Sha512,
        SignatureSchemeId.RsaPkcs1Sha1,
    });

    private static readonly IReadOnlyList<ushort> ChromeQuicSupportedGroups = Array.AsReadOnly(new ushort[]
    {
        NamedGroupId.X25519MLKEM768,
        NamedGroupId.X25519,
        NamedGroupId.Secp256r1,
        NamedGroupId.Secp384r1,
    });

    private static readonly IReadOnlyList<(ulong Id, ulong Value)> ChromeHttp3SettingsPairs =
        Array.AsReadOnly(new (ulong, ulong)[]
        {
            (Http3SettingId.QpackMaxTableCapacity, 65536),
            (Http3SettingId.MaxFieldSectionSize, 262144),
            (Http3SettingId.QpackBlockedStreams, 100),
            (Http3SettingId.H3Datagram, 1),
        });

    private static readonly IReadOnlyList<ulong> ChromeHttp3SettingsOrder =
        Array.AsReadOnly(new ulong[]
        {
            Http3SettingId.QpackMaxTableCapacity,
            Http3SettingId.MaxFieldSectionSize,
            Http3SettingId.QpackBlockedStreams,
            Http3SettingId.H3Datagram,
        });

    private static readonly IReadOnlyList<string> ChromeHttp3PseudoHeaderOrder =
        Array.AsReadOnly(new[] { ":method", ":authority", ":scheme", ":path" });

    private static readonly IReadOnlyList<(ulong Id, ulong Value)> FirefoxHttp3SettingsPairs =
        Array.AsReadOnly(new (ulong, ulong)[]
        {
            (Http3SettingId.QpackMaxTableCapacity, 65536),
            (Http3SettingId.QpackBlockedStreams, 20),
            (Http3SettingId.FirefoxCustom0, 0),
            (Http3SettingId.FirefoxCustom1, 1),
            (Http3SettingId.H3Datagram, 1),
            (Http3SettingId.EnableConnectProtocol, 1),
        });

    private static readonly IReadOnlyList<ulong> FirefoxHttp3SettingsOrder =
        Array.AsReadOnly(new ulong[]
        {
            Http3SettingId.QpackMaxTableCapacity,
            Http3SettingId.QpackBlockedStreams,
            Http3SettingId.FirefoxCustom0,
            Http3SettingId.FirefoxCustom1,
            Http3SettingId.H3Datagram,
            Http3SettingId.EnableConnectProtocol,
        });

    private static readonly IReadOnlyList<string> FirefoxHttp3PseudoHeaderOrder =
        Array.AsReadOnly(new[] { ":method", ":scheme", ":authority", ":path" });

    /// <summary>Default QUIC transport parameters matching ClientTransportParameters (sub_1412B00B0 / sub_1412A3DD0).</summary>
    public static QuicTransportSpec DefaultTransportSpec { get; } = new()
    {
        CreateClientHelloSpec = CreateClientHelloSpec,
        InitialMaxData = 15_728_640,
        InitialMaxStreamDataBidiLocal = 6_291_456,
        InitialMaxStreamDataBidiRemote = 6_291_456,
        InitialMaxStreamDataUni = 6_291_456,
        InitialMaxStreamsBidi = 100,
        InitialMaxStreamsUni = 103,
        MaxIdleTimeoutMs = 30_000,
        MaxUdpPayloadSize = 1_250,
        ClientTransportDefaultMaxUdpPayloadSize = 1_472,
        MaxDatagramFrameSize = 65_536,
        AckDelayExponent = 3,
        MaxAckDelayMs = 25,
        DisableActiveMigration = false,
        GreaseTransportParameters = true,
        ShuffleTransportParameters = true,
        InitialPacketSize = 1_200,
        QuicVersion = 0x00000001,
        SendGreaseVersionInformation = true,
        GoogleConnectionOptions = "ORIG",
        ScidLength = 0,
        DcidLength = 8,
        HandshakeTimeout = TimeSpan.FromSeconds(10),
    };

    /// <summary>
    /// Builder 5.1 (0x1412B9F20): Shared QUIC ClientHello used by Chrome_144, Chrome_144_PSK,
    /// Chrome_146, Chrome_146_PSK, Chrome_150, Chrome_150_PSK, Chrome_152, Chrome_152_PSK.
    /// </summary>
    public static ClientHelloSpec CreateClientHelloSpec() => new(
        CipherSuites: QuicCipherSuites,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            new AlpnExtension(H3Alpn),
            new SupportedVersionsExtension(Tls13OnlyVersions),
            new KeyShareExtension(ChromeQuicKeyShares),
            new SniExtension(),
            new PskKeyExchangeModesExtension(PskModes),
            new CompressCertificateExtension(BrotliCompression),
            GreaseEchExtension.ChromePreset,
            new QuicTransportParametersExtension(),
            new SignatureAlgorithmsExtension(ChromeQuicSignatureAlgorithms),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettingsNew, H3Alpn),
            new SupportedGroupsExtension(ChromeQuicSupportedGroups),
            new EarlyDataExtension(),
            new PreSharedKeyExtension(),
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>
    /// Full Chrome HTTP/3 settings spec (+96=984832, +101=1) used by Chrome_144, Chrome_144_PSK,
    /// Chrome_146_PSK, Chrome_150_PSK, Chrome_152, and Chrome_152_PSK.
    /// (Chrome_146 and Chrome_150 intentionally keep Http3Settings null per sub_1412B05A0.)
    /// </summary>
    public static Http3SettingsSpec CreateChromeHttp3Settings() => new(
        Settings: ChromeHttp3SettingsPairs,
        SettingsOrder: ChromeHttp3SettingsOrder,
        PseudoHeaderOrder: ChromeHttp3PseudoHeaderOrder,
        ChromeH3Flag: 984832,
        SendGreaseFrame: true);

    /// <summary>
    /// Firefox 147 / 147_PSK / 148 HTTP/3 settings metadata (+96=0, +101=1),
    /// populated in UtlsPresets even though their QuicSpec (+24) is null.
    /// </summary>
    public static Http3SettingsSpec CreateFirefoxHttp3Settings() => new(
        Settings: FirefoxHttp3SettingsPairs,
        SettingsOrder: FirefoxHttp3SettingsOrder,
        PseudoHeaderOrder: FirefoxHttp3PseudoHeaderOrder,
        ChromeH3Flag: 0,
        SendGreaseFrame: true);
}
