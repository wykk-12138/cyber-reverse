using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text;
using Cybersole.Http.Crypto;
using Cybersole.Http.Profiles;

namespace Cybersole.Http.Tls;

/// <summary>
/// Ephemeral private key material generated for a single ClientHello <c>key_share</c> entry.
/// </summary>
public sealed class AsymmetricKeyShareState : IDisposable
{
    private bool _disposed;

    private AsymmetricKeyShareState(
        ushort group,
        byte[] publicKey,
        byte[]? privateKey,
        HybridKeyState? hybridState)
    {
        Group = group;
        PublicKey = publicKey;
        PrivateKey = privateKey;
        HybridState = hybridState;
    }

    public ushort Group { get; }
    public byte[] PublicKey { get; }
    public byte[]? PrivateKey { get; }
    public HybridKeyState? HybridState { get; }

    public static AsymmetricKeyShareState Create(ushort group)
    {
        switch (group)
        {
            case NamedGroupId.X25519:
            {
                X25519.GenerateKeyPair(out byte[] priv, out byte[] pub);
                return new AsymmetricKeyShareState(group, pub, priv, null);
            }
            case NamedGroupId.Secp256r1:
            {
                (byte[] priv, byte[] pub) = EcPrimitives.GenerateEcdheKeyPair(EcCurveKind.P256);
                return new AsymmetricKeyShareState(group, pub, priv, null);
            }
            case NamedGroupId.Secp384r1:
            {
                (byte[] priv, byte[] pub) = EcPrimitives.GenerateEcdheKeyPair(EcCurveKind.P384);
                return new AsymmetricKeyShareState(group, pub, priv, null);
            }
            case NamedGroupId.Secp521r1:
            {
                (byte[] priv, byte[] pub) = EcPrimitives.GenerateEcdheKeyPair(EcCurveKind.P521);
                return new AsymmetricKeyShareState(group, pub, priv, null);
            }
            case NamedGroupId.X25519MLKEM768:
            {
                (byte[] share, HybridKeyState state) = HybridKem.GenerateX25519MlKem768();
                return new AsymmetricKeyShareState(group, share, null, state);
            }
            case NamedGroupId.X25519Kyber768Draft00:
            {
                (byte[] share, HybridKeyState state) = HybridKem.GenerateX25519Kyber768Draft00();
                return new AsymmetricKeyShareState(group, share, null, state);
            }
            default:
                throw new NotSupportedException($"Unsupported TLS named group for key_share: 0x{group:X4}.");
        }
    }

    public static bool IsSupportedGroup(ushort group) => group is
        NamedGroupId.X25519 or
        NamedGroupId.Secp256r1 or
        NamedGroupId.Secp384r1 or
        NamedGroupId.Secp521r1 or
        NamedGroupId.X25519MLKEM768 or
        NamedGroupId.X25519Kyber768Draft00;

    public byte[] DeriveSharedSecret(ReadOnlySpan<byte> serverKeyShare)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        return Group switch
        {
            NamedGroupId.X25519 => X25519.ScalarMult(PrivateKey!, serverKeyShare),
            NamedGroupId.Secp256r1 => EcPrimitives.DeriveEcdheSharedSecret(EcCurveKind.P256, PrivateKey!, serverKeyShare),
            NamedGroupId.Secp384r1 => EcPrimitives.DeriveEcdheSharedSecret(EcCurveKind.P384, PrivateKey!, serverKeyShare),
            NamedGroupId.Secp521r1 => EcPrimitives.DeriveEcdheSharedSecret(EcCurveKind.P521, PrivateKey!, serverKeyShare),
            NamedGroupId.X25519MLKEM768 or NamedGroupId.X25519Kyber768Draft00 => HybridKem.CompleteX25519MlKem768(HybridState!, serverKeyShare),
            _ => throw new NotSupportedException($"Unsupported TLS named group: 0x{Group:X4}.")
        };
    }

    public void Dispose()
    {
        if (_disposed)
            return;

        if (PrivateKey is not null)
            ConstantTime.ZeroMemory(PrivateKey);

        HybridState?.Dispose();
        _disposed = true;
    }
}

/// <summary>
/// Options controlling <see cref="TlsClientHelloBuilder.Build"/>.
/// </summary>
public sealed class ClientHelloBuildOptions
{
    public ClientProfile Profile { get; init; } = ProfileRegistry.GetOrDefault(null);
    public ClientHelloSpec? SpecOverride { get; init; }
    public string? ServerName { get; init; }
    public TlsSessionTicket? SessionTicket { get; init; }
    public bool IsQuicMode { get; init; }
    public byte[]? QuicTransportParameters { get; init; }
    public IReadOnlyList<string>? AlpnOverride { get; init; }
    public bool ForceHttp11 { get; init; }
    public bool? RandomExtensionOrderOverride { get; init; }
    public bool DisableSessionTickets { get; init; }
    public Random? Random { get; init; }
    public DateTimeOffset? NowUtc { get; init; }

    // HelloRetryRequest continuation fields
    public byte[]? PreviousClientRandom { get; init; }
    public byte[]? PreviousLegacySessionId { get; init; }
    public ushort? HelloRetrySelectedGroup { get; init; }
    public byte[]? HelloRetryCookie { get; init; }
    public byte[]? HelloRetryTranscriptPrefix { get; init; }
    public Dictionary<ushort, AsymmetricKeyShareState>? ExistingKeyShares { get; init; }
}

/// <summary>
/// Serialized ClientHello message together with generated key-share states and PSK binder secrets.
/// </summary>
public sealed class ClientHelloBuildResult : IDisposable
{
    private bool _disposed;

    internal ClientHelloBuildResult(
        byte[] handshakeMessage,
        byte[] clientRandom,
        byte[] legacySessionId,
        Dictionary<ushort, AsymmetricKeyShareState> keyShares,
        ClientHelloSpec materializedSpec,
        IReadOnlyList<ushort> offeredExtensionTypes,
        IReadOnlyList<ushort> offeredCipherSuites,
        IReadOnlyList<ushort> offeredGroups,
        IReadOnlyList<string> offeredAlpn,
        ushort minOfferedVersion,
        ushort maxOfferedVersion,
        bool offeredPsk,
        TlsSessionTicket? offeredTicket,
        byte[]? offeredEarlySecret,
        int paddingPayloadBytes)
    {
        HandshakeMessage = handshakeMessage;
        ClientRandom = clientRandom;
        LegacySessionId = legacySessionId;
        KeyShares = keyShares;
        MaterializedSpec = materializedSpec;
        OfferedExtensionTypes = offeredExtensionTypes;
        OfferedCipherSuites = offeredCipherSuites;
        OfferedGroups = offeredGroups;
        OfferedAlpn = offeredAlpn;
        MinOfferedVersion = minOfferedVersion;
        MaxOfferedVersion = maxOfferedVersion;
        OfferedPsk = offeredPsk;
        OfferedTicket = offeredTicket;
        OfferedEarlySecret = offeredEarlySecret;
        PaddingPayloadBytes = paddingPayloadBytes;
    }

    public byte[] HandshakeMessage { get; }
    public ReadOnlySpan<byte> HandshakeBody => HandshakeMessage.AsSpan(4);
    public byte[] ClientRandom { get; }
    public byte[] LegacySessionId { get; }
    public Dictionary<ushort, AsymmetricKeyShareState> KeyShares { get; }
    public ClientHelloSpec MaterializedSpec { get; }
    public IReadOnlyList<ushort> OfferedExtensionTypes { get; }
    public IReadOnlyList<ushort> OfferedCipherSuites { get; }
    public IReadOnlyList<ushort> OfferedGroups { get; }
    public IReadOnlyList<string> OfferedAlpn { get; }
    public ushort MinOfferedVersion { get; }
    public ushort MaxOfferedVersion { get; }
    public bool OfferedPsk { get; }
    public TlsSessionTicket? OfferedTicket { get; }
    public byte[]? OfferedEarlySecret { get; }
    public int PaddingPayloadBytes { get; }

    /// <summary>
    /// Wraps <see cref="HandshakeMessage"/> in a plain TLS 1.0 compatibility record header
    /// (<c>[0x16, 0x03, 0x01, uint16_be len]</c>) per RFC 8446 §5.1.
    /// </summary>
    public byte[] ToTlsRecord()
    {
        var record = new byte[5 + HandshakeMessage.Length];
        record[0] = 0x16;
        record[1] = 0x03;
        record[2] = 0x01;
        BinaryPrimitives.WriteUInt16BigEndian(record.AsSpan(3, 2), (ushort)HandshakeMessage.Length);
        HandshakeMessage.CopyTo(record, 5);
        return record;
    }

    public void Dispose()
    {
        if (_disposed)
            return;

        foreach (AsymmetricKeyShareState state in KeyShares.Values)
            state.Dispose();

        if (OfferedEarlySecret is not null)
            ConstantTime.ZeroMemory(OfferedEarlySecret);

        _disposed = true;
    }
}

/// <summary>
/// Profile-driven TLS 1.2 / TLS 1.3 / QUIC ClientHello wire builder matching
/// <c>ClientHelloBuilder</c> / <c>SerializeClientHello</c> (<c>0x141297880</c>, <c>0x141298620</c>, <c>0x141298FA0</c>).
/// </summary>
public static class TlsClientHelloBuilder
{
    public static ClientHelloBuildResult Build(ClientHelloBuildOptions options)
    {
        ArgumentNullException.ThrowIfNull(options);
        ClientProfile profile = options.Profile ?? ProfileRegistry.GetOrDefault(null);
        Random rng = options.Random ?? Random.Shared;
        DateTimeOffset nowUtc = options.NowUtc ?? DateTimeOffset.UtcNow;

        ClientHelloSpec baseSpec = options.SpecOverride
            ?? (options.IsQuicMode && profile.CreateQuicClientHelloSpec is not null
                ? profile.CreateQuicClientHelloSpec()
                : profile.CreateClientHelloSpec());

        bool isHrrRetry = options.HelloRetrySelectedGroup.HasValue || options.HelloRetryCookie is not null;
        bool shuffle = !isHrrRetry && (options.RandomExtensionOrderOverride ?? baseSpec.ShuffleExtensions);
        ClientHelloSpec greaselessSpec = isHrrRetry && options.SpecOverride is not null
            ? baseSpec
            : GreaseHelper.ResolveGrease(baseSpec, rng);
        IReadOnlyList<TlsExtensionSpec> orderedExtensions = shuffle
            ? ExtensionShuffler.Shuffle(greaselessSpec.Extensions, rng)
            : greaselessSpec.Extensions;

        var materialized = new ClientHelloSpec(
            CipherSuites: greaselessSpec.CipherSuites,
            CompressionMethods: greaselessSpec.CompressionMethods,
            Extensions: orderedExtensions,
            ShuffleExtensions: shuffle,
            BoringPaddingStyle: greaselessSpec.BoringPaddingStyle);

        // Effective ciphers (QUIC requires TLS 1.3 suites)
        var ciphers = new List<ushort>(materialized.CipherSuites.Count);
        for (int i = 0; i < materialized.CipherSuites.Count; i++)
        {
            ushort c = materialized.CipherSuites[i];
            if (options.IsQuicMode && !GreaseHelper.IsGrease(c) && !IsTls13CipherSuite(c))
                continue;
            ciphers.Add(c);
        }

        if (ciphers.Count == 0)
            throw new InvalidOperationException("ClientHelloSpec produced zero compatible cipher suites.");

        // Effective versions
        ushort minVer = materialized.MinVersion;
        ushort maxVer = materialized.MaxVersion;
        if (options.IsQuicMode)
        {
            minVer = TlsVersion.Tls13;
            maxVer = TlsVersion.Tls13;
        }

        // Effective ALPN
        AlpnExtension? specAlpn = materialized.GetExtension<AlpnExtension>();
        IReadOnlyList<string> effectiveAlpn = ResolveEffectiveAlpn(profile, options, specAlpn);

        // Effective PSK eligibility (cybersole_http_architecture.md §3.2)
        TlsSessionTicket? ticket = options.SessionTicket;
        HashAlgorithmKind pskHashAlg = default;
        bool canOfferPsk = !options.DisableSessionTickets
            && ticket is not null
            && ticket.IsValidForUse(nowUtc)
            && maxVer >= TlsVersion.Tls13
            && materialized.HasExtension(TlsExtensionType.PreSharedKey)
            && ResolvePskHash(ticket, ciphers, out pskHashAlg);

        bool offerEarlyData = canOfferPsk && ticket!.MaxEarlyDataSize > 0;

        // Client random & legacy session id
        var clientRandom = new byte[32];
        if (options.PreviousClientRandom is { Length: 32 })
            options.PreviousClientRandom.CopyTo(clientRandom, 0);
        else
            RandomNumberGenerator.Fill(clientRandom);

        byte[] legacySessionId;
        if (options.IsQuicMode)
        {
            legacySessionId = Array.Empty<byte>();
        }
        else if (options.PreviousLegacySessionId is not null)
        {
            legacySessionId = (byte[])options.PreviousLegacySessionId.Clone();
        }
        else if (maxVer >= TlsVersion.Tls13)
        {
            legacySessionId = new byte[32];
            RandomNumberGenerator.Fill(legacySessionId);
        }
        else
        {
            legacySessionId = Array.Empty<byte>();
        }

        var keyShares = new Dictionary<ushort, AsymmetricKeyShareState>();
        var offeredGroups = new List<ushort>();
        var serializedExtensions = new List<(ushort Type, byte[] Data)>(materialized.Extensions.Count + 2);
        PaddingExtension? paddingSpec = null;
        bool emittedAlpn = false;
        bool emittedQuicTp = false;

        for (int i = 0; i < materialized.Extensions.Count; i++)
        {
            TlsExtensionSpec ext = materialized.Extensions[i];
            switch (ext)
            {
                case PaddingExtension pad:
                    paddingSpec = pad;
                    break;

                case PreSharedKeyExtension:
                    // Strictly last when canOfferPsk is true; omitted otherwise.
                    break;

                case EarlyDataExtension:
                    if (offerEarlyData)
                        serializedExtensions.Add((TlsExtensionType.EarlyData, Array.Empty<byte>()));
                    break;

                case SniExtension sni:
                {
                    string? sanitized = SniExtension.SanitizeHostName(options.ServerName ?? sni.HostName);
                    if (!string.IsNullOrEmpty(sanitized))
                        serializedExtensions.Add((TlsExtensionType.ServerName, EncodeSni(sanitized)));
                    break;
                }

                case StatusRequestExtension sr:
                    serializedExtensions.Add((TlsExtensionType.StatusRequest, new byte[] { sr.StatusType, 0x00, 0x00, 0x00, 0x00 }));
                    break;

                case SupportedGroupsExtension sg:
                    for (int g = 0; g < sg.Groups.Count; g++)
                    {
                        if (!GreaseHelper.IsGrease(sg.Groups[g]))
                            offeredGroups.Add(sg.Groups[g]);
                    }
                    serializedExtensions.Add((TlsExtensionType.SupportedGroups, EncodeUInt16List(sg.Groups)));
                    break;

                case EcPointFormatsExtension ecpf:
                    serializedExtensions.Add((TlsExtensionType.EcPointFormats, EncodeByteList(ecpf.Formats)));
                    break;

                case SignatureAlgorithmsExtension sa:
                    serializedExtensions.Add((TlsExtensionType.SignatureAlgorithms, EncodeUInt16List(sa.Schemes)));
                    break;

                case AlpnExtension:
                    emittedAlpn = true;
                    if (effectiveAlpn.Count > 0)
                        serializedExtensions.Add((TlsExtensionType.ApplicationLayerProtocolNegotiation, EncodeAlpn(effectiveAlpn)));
                    break;

                case SignedCertificateTimestampExtension:
                    serializedExtensions.Add((TlsExtensionType.SignedCertificateTimestamp, Array.Empty<byte>()));
                    break;

                case EncryptThenMacExtension:
                    serializedExtensions.Add((TlsExtensionType.EncryptThenMac, Array.Empty<byte>()));
                    break;

                case ExtendedMasterSecretExtension:
                    serializedExtensions.Add((TlsExtensionType.ExtendedMasterSecret, Array.Empty<byte>()));
                    break;

                case CompressCertificateExtension cc:
                    serializedExtensions.Add((TlsExtensionType.CompressCertificate, EncodeCompressCertificate(cc.Algorithms)));
                    break;

                case RecordSizeLimitExtension rsl:
                {
                    var payload = new byte[2];
                    BinaryPrimitives.WriteUInt16BigEndian(payload, rsl.Limit);
                    serializedExtensions.Add((TlsExtensionType.RecordSizeLimit, payload));
                    break;
                }

                case DelegatedCredentialsExtension dc:
                    serializedExtensions.Add((TlsExtensionType.DelegatedCredentials, EncodeUInt16List(dc.Schemes)));
                    break;

                case SessionTicketExtension:
                    serializedExtensions.Add((TlsExtensionType.SessionTicket, Array.Empty<byte>()));
                    break;

                case SupportedVersionsExtension sv:
                {
                    var vers = new List<ushort>(sv.Versions.Count);
                    for (int v = 0; v < sv.Versions.Count; v++)
                    {
                        ushort ver = sv.Versions[v];
                        if (options.IsQuicMode && !GreaseHelper.IsGrease(ver) && ver < TlsVersion.Tls13)
                            continue;
                        vers.Add(ver);
                    }
                    if (options.IsQuicMode && !vers.Contains(TlsVersion.Tls13))
                        vers.Add(TlsVersion.Tls13);
                    serializedExtensions.Add((TlsExtensionType.SupportedVersions, EncodeSupportedVersions(vers)));
                    break;
                }

                case PskKeyExchangeModesExtension pkem:
                    serializedExtensions.Add((TlsExtensionType.PskKeyExchangeModes, EncodeByteList(pkem.Modes)));
                    break;

                case KeyShareExtension ks:
                    serializedExtensions.Add((
                        TlsExtensionType.KeyShare,
                        EncodeKeyShare(ks, options.HelloRetrySelectedGroup, options.ExistingKeyShares, keyShares)));
                    break;

                case QuicTransportParametersExtension:
                    if (options.IsQuicMode && options.QuicTransportParameters is not null)
                    {
                        serializedExtensions.Add((TlsExtensionType.QuicTransportParameters, (byte[])options.QuicTransportParameters.Clone()));
                        emittedQuicTp = true;
                    }
                    break;

                case ApplicationSettingsExtension alps:
                {
                    byte[]? alpsPayload = EncodeApplicationSettings(alps, effectiveAlpn, options.AlpnOverride is not null || options.ForceHttp11 || profile.DisableHttp2);
                    if (alpsPayload is not null)
                        serializedExtensions.Add((alps.CodePoint, alpsPayload));
                    break;
                }

                case TrustAnchorsExtension ta:
                    serializedExtensions.Add((TlsExtensionType.TrustAnchors, (byte[])ta.RawPayload.Clone()));
                    break;

                case GreaseEchExtension ech:
                    serializedExtensions.Add((TlsExtensionType.EncryptedClientHello, EncodeGreaseEch(ech, rng)));
                    break;

                case RenegotiationInfoExtension reneg:
                    serializedExtensions.Add((TlsExtensionType.RenegotiationInfo, (byte[])reneg.WirePayload.Clone()));
                    break;

                case GreaseExtension grease:
                    serializedExtensions.Add((grease.ResolvedType, grease.Payload is not null ? (byte[])grease.Payload.Clone() : Array.Empty<byte>()));
                    break;

                case CustomRawExtension custom:
                    serializedExtensions.Add((custom.ExtensionTypeValue, (byte[])custom.Payload.Clone()));
                    break;

                default:
                    throw new NotSupportedException($"Unsupported TlsExtensionSpec type: {ext.GetType().Name}.");
            }
        }

        if (!emittedAlpn && effectiveAlpn.Count > 0)
            serializedExtensions.Add((TlsExtensionType.ApplicationLayerProtocolNegotiation, EncodeAlpn(effectiveAlpn)));

        if (options.IsQuicMode && options.QuicTransportParameters is not null && !emittedQuicTp)
            serializedExtensions.Add((TlsExtensionType.QuicTransportParameters, (byte[])options.QuicTransportParameters.Clone()));

        if (options.HelloRetryCookie is { Length: > 0 } hrrCookie)
            serializedExtensions.Add((0x002C, EncodeCookie(hrrCookie)));

        byte[]? pskPayload = null;
        byte[]? offeredEarlySecret = null;
        byte[]? binderFinishedKey = null;
        int pskHashLen = 0;

        if (canOfferPsk)
        {
            pskHashLen = HashPrimitives.DigestLength(pskHashAlg);
            byte[] psk = ticket!.ResolvePsk();
            offeredEarlySecret = HashPrimitives.HkdfExtract(pskHashAlg, ReadOnlySpan<byte>.Empty, psk);
            byte[] emptyHash = HashPrimitives.Hash(pskHashAlg, ReadOnlySpan<byte>.Empty);
            byte[] binderKey = HashPrimitives.HkdfExpandLabel(pskHashAlg, offeredEarlySecret, "res binder", emptyHash, pskHashLen);
            binderFinishedKey = HashPrimitives.HkdfExpandLabel(pskHashAlg, binderKey, "finished", ReadOnlySpan<byte>.Empty, pskHashLen);
            ConstantTime.ZeroMemory(binderKey);

            uint obfuscatedAge = ticket.ComputeObfuscatedTicketAge(nowUtc);
            pskPayload = EncodePreSharedKeyPlaceholder(ticket.Ticket, obfuscatedAge, pskHashLen);
        }

        int unpaddedBodyLength = ComputeClientHelloBodyLength(
            legacySessionId.Length,
            ciphers.Count,
            materialized.CompressionMethods.Count,
            serializedExtensions,
            pskPayload);

        int paddingPayloadBytes = 0;
        if (materialized.BoringPaddingStyle || paddingSpec is not null)
        {
            int targetLength = paddingSpec?.TargetLength ?? PaddingExtension.BoringPaddingTarget;
            paddingPayloadBytes = PaddingExtension.CalculatePaddingBytes(unpaddedBodyLength, targetLength);
            if (paddingPayloadBytes > 0)
                serializedExtensions.Add((TlsExtensionType.Padding, new byte[paddingPayloadBytes]));
        }

        if (pskPayload is not null)
            serializedExtensions.Add((TlsExtensionType.PreSharedKey, pskPayload));

        byte[] handshakeMessage = SerializeClientHelloBytes(
            clientRandom,
            legacySessionId,
            ciphers,
            materialized.CompressionMethods,
            serializedExtensions);

        if (canOfferPsk && binderFinishedKey is not null)
        {
            int truncatedLen = handshakeMessage.Length - (2 + 1 + pskHashLen);
            byte[] transcriptHash;
            if (options.HelloRetryTranscriptPrefix is { Length: > 0 } hrrPrefix)
            {
                using var inc = IncrementalHash.CreateHash(HashPrimitives.ToBclName(pskHashAlg));
                inc.AppendData(hrrPrefix);
                inc.AppendData(handshakeMessage.AsSpan(0, truncatedLen));
                transcriptHash = inc.GetHashAndReset();
            }
            else
            {
                transcriptHash = HashPrimitives.Hash(pskHashAlg, handshakeMessage.AsSpan(0, truncatedLen));
            }

            byte[] binder = HashPrimitives.Hmac(pskHashAlg, binderFinishedKey, transcriptHash);
            binder.CopyTo(handshakeMessage.AsSpan(handshakeMessage.Length - pskHashLen, pskHashLen));
            ConstantTime.ZeroMemory(binderFinishedKey);
            ConstantTime.ZeroMemory(binder);
        }

        var offeredExtTypes = new ushort[serializedExtensions.Count];
        for (int i = 0; i < serializedExtensions.Count; i++)
            offeredExtTypes[i] = serializedExtensions[i].Type;

        return new ClientHelloBuildResult(
            handshakeMessage: handshakeMessage,
            clientRandom: clientRandom,
            legacySessionId: legacySessionId,
            keyShares: keyShares,
            materializedSpec: materialized,
            offeredExtensionTypes: Array.AsReadOnly(offeredExtTypes),
            offeredCipherSuites: Array.AsReadOnly(ciphers.ToArray()),
            offeredGroups: Array.AsReadOnly(offeredGroups.ToArray()),
            offeredAlpn: effectiveAlpn,
            minOfferedVersion: minVer,
            maxOfferedVersion: maxVer,
            offeredPsk: canOfferPsk,
            offeredTicket: canOfferPsk ? ticket : null,
            offeredEarlySecret: offeredEarlySecret,
            paddingPayloadBytes: paddingPayloadBytes);
    }

    public static byte[] SerializeClientHelloMessage(ClientHelloBuildOptions options, out ClientHelloBuildResult result)
    {
        result = Build(options);
        return result.HandshakeMessage;
    }

    public static byte[] SerializeClientHelloMessage(
        ClientProfile profile,
        string? serverName = null,
        TlsSessionTicket? ticket = null,
        bool isQuicMode = false,
        byte[]? quicTransportParameters = null,
        IReadOnlyList<string>? alpnOverride = null)
    {
        using ClientHelloBuildResult res = Build(new ClientHelloBuildOptions
        {
            Profile = profile,
            ServerName = serverName,
            SessionTicket = ticket,
            IsQuicMode = isQuicMode,
            QuicTransportParameters = quicTransportParameters,
            AlpnOverride = alpnOverride,
        });
        return res.HandshakeMessage;
    }

    public static byte[] BuildClientHelloRecord(ClientHelloBuildOptions options, out ClientHelloBuildResult result)
    {
        result = Build(options);
        return result.ToTlsRecord();
    }

    public static byte[] BuildClientHelloRecord(
        ClientProfile profile,
        string? serverName = null,
        TlsSessionTicket? ticket = null,
        IReadOnlyList<string>? alpnOverride = null)
    {
        using ClientHelloBuildResult res = Build(new ClientHelloBuildOptions
        {
            Profile = profile,
            ServerName = serverName,
            SessionTicket = ticket,
            AlpnOverride = alpnOverride,
        });
        return res.ToTlsRecord();
    }

    private static bool IsTls13CipherSuite(ushort cipher) => cipher is
        CipherSuiteId.TLS_AES_128_GCM_SHA256 or
        CipherSuiteId.TLS_AES_256_GCM_SHA384 or
        CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256;

    private static bool ResolvePskHash(
        TlsSessionTicket ticket,
        List<ushort> offeredCiphers,
        out HashAlgorithmKind hashAlg)
    {
        if (ticket.CipherSuite != 0)
        {
            hashAlg = ticket.CipherSuite == CipherSuiteId.TLS_AES_256_GCM_SHA384
                ? HashAlgorithmKind.Sha384
                : HashAlgorithmKind.Sha256;
        }
        else
        {
            hashAlg = ticket.HashAlg;
        }

        for (int i = 0; i < offeredCiphers.Count; i++)
        {
            ushort c = offeredCiphers[i];
            if (c == CipherSuiteId.TLS_AES_256_GCM_SHA384 && hashAlg == HashAlgorithmKind.Sha384)
                return true;
            if ((c is CipherSuiteId.TLS_AES_128_GCM_SHA256 or CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256) &&
                hashAlg == HashAlgorithmKind.Sha256)
                return true;
        }

        return false;
    }

    private static IReadOnlyList<string> ResolveEffectiveAlpn(
        ClientProfile profile,
        ClientHelloBuildOptions options,
        AlpnExtension? specAlpn)
    {
        if (options.ForceHttp11)
            return Array.AsReadOnly(new[] { "http/1.1" });

        if (options.AlpnOverride is not null)
            return options.AlpnOverride;

        if (specAlpn is null)
            return Array.AsReadOnly(Array.Empty<string>());

        if (!profile.DisableHttp2)
            return specAlpn.Protocols;

        var filtered = new List<string>(specAlpn.Protocols.Count);
        for (int i = 0; i < specAlpn.Protocols.Count; i++)
        {
            if (!string.Equals(specAlpn.Protocols[i], "h2", StringComparison.Ordinal))
                filtered.Add(specAlpn.Protocols[i]);
        }
        return Array.AsReadOnly(filtered.ToArray());
    }

    private static byte[] EncodeSni(string host)
    {
        byte[] hostBytes = Encoding.ASCII.GetBytes(host);
        int listLen = 1 + 2 + hostBytes.Length;
        var buf = new byte[2 + listLen];
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(0, 2), (ushort)listLen);
        buf[2] = 0x00;
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(3, 2), (ushort)hostBytes.Length);
        hostBytes.CopyTo(buf, 5);
        return buf;
    }

    private static byte[] EncodeUInt16List(IReadOnlyList<ushort> values)
    {
        int listLen = values.Count * 2;
        var buf = new byte[2 + listLen];
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(0, 2), (ushort)listLen);
        for (int i = 0; i < values.Count; i++)
            BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(2 + i * 2, 2), values[i]);
        return buf;
    }

    private static byte[] EncodeSupportedVersions(IReadOnlyList<ushort> versions)
    {
        int listLen = versions.Count * 2;
        var buf = new byte[1 + listLen];
        buf[0] = (byte)listLen;
        for (int i = 0; i < versions.Count; i++)
            BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(1 + i * 2, 2), versions[i]);
        return buf;
    }

    private static byte[] EncodeByteList(IReadOnlyList<byte> values)
    {
        var buf = new byte[1 + values.Count];
        buf[0] = (byte)values.Count;
        for (int i = 0; i < values.Count; i++)
            buf[1 + i] = values[i];
        return buf;
    }

    private static byte[] EncodeAlpn(IReadOnlyList<string> protocols)
    {
        int listLen = 0;
        var encoded = new byte[protocols.Count][];
        for (int i = 0; i < protocols.Count; i++)
        {
            encoded[i] = Encoding.ASCII.GetBytes(protocols[i]);
            listLen += 1 + encoded[i].Length;
        }

        var buf = new byte[2 + listLen];
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(0, 2), (ushort)listLen);
        int offset = 2;
        for (int i = 0; i < encoded.Length; i++)
        {
            buf[offset++] = (byte)encoded[i].Length;
            encoded[i].CopyTo(buf, offset);
            offset += encoded[i].Length;
        }
        return buf;
    }

    private static byte[]? EncodeApplicationSettings(
        ApplicationSettingsExtension alps,
        IReadOnlyList<string> effectiveAlpn,
        bool alpnWasFiltered)
    {
        if (alps.AlpnProtocols.Count == 0)
            return new byte[] { 0x00, 0x00 };

        if (!alpnWasFiltered)
            return EncodeAlpn(alps.AlpnProtocols);

        var filtered = new List<string>(alps.AlpnProtocols.Count);
        for (int i = 0; i < alps.AlpnProtocols.Count; i++)
        {
            string p = alps.AlpnProtocols[i];
            for (int k = 0; k < effectiveAlpn.Count; k++)
            {
                if (string.Equals(p, effectiveAlpn[k], StringComparison.Ordinal))
                {
                    filtered.Add(p);
                    break;
                }
            }
        }

        return filtered.Count > 0 ? EncodeAlpn(filtered) : null;
    }

    private static byte[] EncodeCompressCertificate(IReadOnlyList<CertCompressionAlgorithm> algorithms)
    {
        int listLen = algorithms.Count * 2;
        var buf = new byte[1 + listLen];
        buf[0] = (byte)listLen;
        for (int i = 0; i < algorithms.Count; i++)
            BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(1 + i * 2, 2), (ushort)algorithms[i]);
        return buf;
    }

    private static byte[] EncodeKeyShare(
        KeyShareExtension ks,
        ushort? helloRetrySelectedGroup,
        Dictionary<ushort, AsymmetricKeyShareState>? existingKeyShares,
        Dictionary<ushort, AsymmetricKeyShareState> outKeyShares)
    {
        var entries = new List<(ushort Group, byte[] Payload)>();

        if (helloRetrySelectedGroup is { } selectedGroup)
        {
            AsymmetricKeyShareState state = GetOrCreateKeyShare(selectedGroup, existingKeyShares);
            outKeyShares[selectedGroup] = state;
            entries.Add((selectedGroup, state.PublicKey));
        }
        else
        {
            for (int i = 0; i < ks.Entries.Count; i++)
            {
                KeyShareEntry entry = ks.Entries[i];
                if (GreaseHelper.IsGrease(entry.Group))
                {
                    int len = entry.InitLength > 0 ? entry.InitLength : 1;
                    entries.Add((entry.Group, new byte[len]));
                }
                else
                {
                    AsymmetricKeyShareState state = GetOrCreateKeyShare(entry.Group, existingKeyShares);
                    outKeyShares[entry.Group] = state;
                    entries.Add((entry.Group, state.PublicKey));
                }
            }
        }

        int listLen = 0;
        for (int i = 0; i < entries.Count; i++)
            listLen += 4 + entries[i].Payload.Length;

        var buf = new byte[2 + listLen];
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(0, 2), (ushort)listLen);
        int offset = 2;
        for (int i = 0; i < entries.Count; i++)
        {
            (ushort group, byte[] pub) = entries[i];
            BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(offset, 2), group);
            BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(offset + 2, 2), (ushort)pub.Length);
            pub.CopyTo(buf, offset + 4);
            offset += 4 + pub.Length;
        }
        return buf;
    }

    private static AsymmetricKeyShareState GetOrCreateKeyShare(
        ushort group,
        Dictionary<ushort, AsymmetricKeyShareState>? existing)
    {
        if (existing is not null && existing.TryGetValue(group, out AsymmetricKeyShareState? state))
            return state;
        return AsymmetricKeyShareState.Create(group);
    }

    private static byte[] EncodeGreaseEch(GreaseEchExtension ech, Random rng)
    {
        GreaseEchCipherSuite suite = ech.CipherSuites[rng.Next(ech.CipherSuites.Count)];
        int payloadLen = ech.PickPayloadLength(rng);
        X25519.GenerateKeyPair(out byte[] priv, out byte[] enc);
        ConstantTime.ZeroMemory(priv);

        // type(1) + kdf(2) + aead(2) + config_id(1) + enc_len(2) + enc(32) + payload_len(2) + payload
        var buf = new byte[1 + 4 + 1 + 2 + enc.Length + 2 + payloadLen];
        int offset = 0;
        buf[offset++] = 0x00; // outer(0)
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(offset, 2), suite.KdfId);
        offset += 2;
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(offset, 2), suite.AeadId);
        offset += 2;
        buf[offset++] = (byte)rng.Next(256);
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(offset, 2), (ushort)enc.Length);
        offset += 2;
        enc.CopyTo(buf, offset);
        offset += enc.Length;
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(offset, 2), (ushort)payloadLen);
        offset += 2;
        RandomNumberGenerator.Fill(buf.AsSpan(offset, payloadLen));
        return buf;
    }

    private static byte[] EncodeCookie(byte[] cookie)
    {
        var buf = new byte[2 + cookie.Length];
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(0, 2), (ushort)cookie.Length);
        cookie.CopyTo(buf, 2);
        return buf;
    }

    private static byte[] EncodePreSharedKeyPlaceholder(byte[] ticket, uint obfuscatedAge, int hashLen)
    {
        int identitiesLen = 2 + ticket.Length + 4;
        int bindersLen = 1 + hashLen;
        var buf = new byte[2 + identitiesLen + 2 + bindersLen];

        int offset = 0;
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(offset, 2), (ushort)identitiesLen);
        offset += 2;
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(offset, 2), (ushort)ticket.Length);
        offset += 2;
        ticket.CopyTo(buf, offset);
        offset += ticket.Length;
        BinaryPrimitives.WriteUInt32BigEndian(buf.AsSpan(offset, 4), obfuscatedAge);
        offset += 4;
        BinaryPrimitives.WriteUInt16BigEndian(buf.AsSpan(offset, 2), (ushort)bindersLen);
        offset += 2;
        buf[offset] = (byte)hashLen;
        // remaining hashLen bytes remain 0x00 until patched
        return buf;
    }

    private static int ComputeClientHelloBodyLength(
        int sessionIdLen,
        int cipherCount,
        int compMethodCount,
        List<(ushort Type, byte[] Data)> nonPskExtensions,
        byte[]? pskPayload)
    {
        int len = 2 + 32 + 1 + sessionIdLen + 2 + cipherCount * 2 + 1 + compMethodCount + 2;
        for (int i = 0; i < nonPskExtensions.Count; i++)
            len += 4 + nonPskExtensions[i].Data.Length;
        if (pskPayload is not null)
            len += 4 + pskPayload.Length;
        return len;
    }

    private static byte[] SerializeClientHelloBytes(
        byte[] clientRandom,
        byte[] legacySessionId,
        List<ushort> ciphers,
        IReadOnlyList<byte> compressionMethods,
        List<(ushort Type, byte[] Data)> extensions)
    {
        int extBytesLen = 0;
        for (int i = 0; i < extensions.Count; i++)
            extBytesLen += 4 + extensions[i].Data.Length;

        int bodyLen = 2
            + 32
            + 1 + legacySessionId.Length
            + 2 + ciphers.Count * 2
            + 1 + compressionMethods.Count
            + 2 + extBytesLen;

        var msg = new byte[4 + bodyLen];
        msg[0] = 0x01; // ClientHello
        msg[1] = (byte)(bodyLen >> 16);
        msg[2] = (byte)(bodyLen >> 8);
        msg[3] = (byte)bodyLen;

        int offset = 4;
        BinaryPrimitives.WriteUInt16BigEndian(msg.AsSpan(offset, 2), TlsVersion.Tls12);
        offset += 2;

        clientRandom.CopyTo(msg, offset);
        offset += 32;

        msg[offset++] = (byte)legacySessionId.Length;
        if (legacySessionId.Length > 0)
        {
            legacySessionId.CopyTo(msg, offset);
            offset += legacySessionId.Length;
        }

        BinaryPrimitives.WriteUInt16BigEndian(msg.AsSpan(offset, 2), (ushort)(ciphers.Count * 2));
        offset += 2;
        for (int i = 0; i < ciphers.Count; i++)
        {
            BinaryPrimitives.WriteUInt16BigEndian(msg.AsSpan(offset, 2), ciphers[i]);
            offset += 2;
        }

        msg[offset++] = (byte)compressionMethods.Count;
        for (int i = 0; i < compressionMethods.Count; i++)
            msg[offset++] = compressionMethods[i];

        BinaryPrimitives.WriteUInt16BigEndian(msg.AsSpan(offset, 2), (ushort)extBytesLen);
        offset += 2;

        for (int i = 0; i < extensions.Count; i++)
        {
            (ushort type, byte[] data) = extensions[i];
            BinaryPrimitives.WriteUInt16BigEndian(msg.AsSpan(offset, 2), type);
            offset += 2;
            BinaryPrimitives.WriteUInt16BigEndian(msg.AsSpan(offset, 2), (ushort)data.Length);
            offset += 2;
            if (data.Length > 0)
            {
                data.CopyTo(msg, offset);
                offset += data.Length;
            }
        }

        return msg;
    }
}
