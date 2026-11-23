using System.Buffers.Binary;
using System.IO.Compression;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
using Cybersole.Http.Crypto;
using Cybersole.Http.Profiles;
using Cybersole.Http.X509;

namespace Cybersole.Http.Tls;

/// <summary>
/// TLS handshake state machine values matching <c>TlsHandshake</c> (<c>0..12</c> in
/// <c>cybersole_http_architecture.md</c> §3.3).
/// </summary>
public enum TlsHandshakeState
{
    Init = 0,
    AwaitServerHello = 1,
    AwaitEncryptedExtensions = 2,
    AwaitCertificateRequest = 3,
    AwaitCertificate = 4,
    AwaitCertificateVerify = 5,
    AwaitServerFinished = 6,
    AwaitTls12Certificate = 7,
    AwaitTls12ServerKeyExchange = 8,
    AwaitTls12ServerHelloDone = 9,
    AwaitTls12NewSessionTicket = 10,
    AwaitTls12Finished = 11,
    Connected = 12,
    Closed = 13,
    Error = 14,
}

/// <summary>QUIC TLS encryption levels matching RFC 9001 §2.1 / §4.1.</summary>
public enum QuicEncryptionLevel
{
    Initial = 0,
    EarlyData = 1,
    Handshake = 2,
    Application = 3,
}

/// <summary>Configuration options for <see cref="TlsHandshakeEngine"/>.</summary>
public sealed class TlsHandshakeOptions
{
    public string? ServerName { get; init; }
    public int Port { get; init; } = 443;
    public ClientProfile Profile { get; init; } = ProfileRegistry.GetOrDefault(null);
    public ClientHelloSpec? SpecOverride { get; init; }
    public IReadOnlyList<string>? AlpnOverride { get; init; }
    public CertificateVerifyOptions? VerifyOptions { get; init; }
    public LruTlsSessionCache? SessionCache { get; init; }
    public bool ForceHttp11 { get; init; }
    public bool RandomExtensionOrder { get; init; }
    public bool DisableSessionTickets { get; init; }
    public Action<string>? KeyLogSink { get; init; }
    public Random? Random { get; init; }
    public DateTimeOffset? NowUtc { get; init; }
}

/// <summary>Output emitted by <see cref="TlsHandshakeEngine.ProcessQuicCryptoData"/> for Phase 3 QUIC.</summary>
public sealed class QuicHandshakeStepResult
{
    public byte[] OutboundInitialData { get; init; } = Array.Empty<byte>();
    public byte[] OutboundHandshakeData { get; init; } = Array.Empty<byte>();
    public byte[] OutboundCryptoData => OutboundInitialData.Length > 0 ? OutboundInitialData : OutboundHandshakeData;
    public QuicEncryptionLevel OutboundEncryptionLevel =>
        OutboundInitialData.Length > 0 ? QuicEncryptionLevel.Initial : QuicEncryptionLevel.Handshake;
    public TlsTrafficKeys? HandshakeReadKeys { get; init; }
    public TlsTrafficKeys? HandshakeWriteKeys { get; init; }
    public TlsTrafficKeys? ApplicationReadKeys { get; init; }
    public TlsTrafficKeys? ApplicationWriteKeys { get; init; }
    public bool HandshakeCompleted { get; init; }
    public ushort NegotiatedCipherSuite { get; init; }
    public string? NegotiatedAlpn { get; init; }
    public byte[]? PeerTransportParameters { get; init; }
    public IReadOnlyList<DerCertificate>? PeerCertificates { get; init; }
    public DerCertificate? LeafCertificate => PeerCertificates is { Count: > 0 } ? PeerCertificates[0] : null;
    public bool UsedSessionResumption { get; init; }
}

/// <summary>Instruction kinds emitted by <see cref="TlsHandshakeEngine"/> for TCP record framing.</summary>
public enum TcpStepOperationKind
{
    SendPlaintextRecord,
    SendProtectedRecord,
    InstallReadKeys,
    InstallWriteKeys,
    SetMaxPlaintextFragment,
    MarkHandshakeCompleted,
}

/// <summary>Ordered TCP transport action returned by <see cref="TlsHandshakeEngine"/>.</summary>
public readonly record struct TcpStepOperation(
    TcpStepOperationKind Kind,
    TlsContentType ContentType = default,
    byte[]? Payload = null,
    ushort RecordVersion = TlsVersion.Tls12,
    TlsTrafficKeys? Keys = null,
    bool IsTls13 = false,
    int MaxPlaintextFragment = TlsRecordLayer.MaxPlaintextFragment);

/// <summary>
/// Dual-transport TLS 1.2 &amp; TLS 1.3 handshake state machine (FSM states <c>0..12</c>)
/// shared by <see cref="TlsStream"/> (TCP) and Phase 3 <c>QuicConnection</c> (<c>CRYPTO</c> frames).
/// </summary>
public sealed class TlsHandshakeEngine : IDisposable
{
    private const int MaxHandshakeMessageBytes = 16 * 1024 * 1024 + 64;
    private const int MaxUncompressedCertificateBytes = 16 * 1024 * 1024;
    private const int MaxTotalTranscriptBytes = 16 * 1024 * 1024;

    // SHA-256("HelloRetryRequest") per RFC 8446 §4.1.3
    private static readonly byte[] HelloRetryRequestRandom =
    {
        0xCF, 0x21, 0xAD, 0x74, 0xE5, 0x9A, 0x61, 0x11,
        0xBE, 0x1D, 0x8C, 0x02, 0x1E, 0x65, 0xB8, 0x91,
        0xC2, 0xA2, 0x11, 0x16, 0x7A, 0xBB, 0x8C, 0x5E,
        0x07, 0x9E, 0x09, 0xE2, 0xC8, 0xA8, 0x33, 0x9C,
    };

    // RFC 8446 §4.1.3 TLS 1.3->1.2 downgrade sentinel ("DOWNGRD\x01")
    private static readonly byte[] Tls12DowngradeSentinel =
    {
        0x44, 0x4F, 0x57, 0x4E, 0x47, 0x52, 0x44, 0x01,
    };

    private readonly TlsHandshakeOptions _options;
    private readonly string _sessionCacheKey;
    private readonly MemoryStream _transcriptStream = new();
    private readonly List<byte> _rxHandshakeBuffer = new();
    private readonly List<CertCompressionAlgorithm> _offeredCertCompression = new();

    private bool _isQuicMode;
    private byte[]? _localQuicTransportParams;
    private ClientHelloBuildResult? _clientHello;
    private readonly Dictionary<ushort, AsymmetricKeyShareState> _ownedKeyShares = new();
    private bool _sentHelloRetry;

    // Negotiated state
    private CipherSuiteSpec? _suite;
    private ushort _negotiatedVersion;
    private string? _negotiatedAlpn;
    private byte[]? _peerTransportParameters;
    private IReadOnlyList<DerCertificate>? _peerCertificates;
    private bool _usedSessionResumption;
    private bool _extendedMasterSecretUsed;
    private bool _encryptThenMacUsed;
    private byte[]? _serverRandom;

    // TLS 1.3 key schedule secrets
    private byte[]? _handshakeSecret;
    private byte[]? _clientHandshakeTrafficSecret;
    private byte[]? _serverHandshakeTrafficSecret;
    private byte[]? _clientAppTrafficSecret;
    private byte[]? _serverAppTrafficSecret;
    private byte[]? _exporterMasterSecret;
    private byte[]? _resumptionMasterSecret;
    private byte[]? _tls13CertRequestContext;
    private bool _tls13ClientCertRequested;
    private bool _earlyDataAccepted;
    private byte[]? _clientEarlyTrafficSecret;
    private ushort _peerAlpsCodepoint;
    private byte[]? _peerAlpsSettings;

    // TLS 1.2 handshake state
    private byte[]? _tls12PreMasterSecret;
    private byte[]? _tls12MasterSecret;
    private bool _tls12CertRequested;
    private bool _tls12ReceivedCcs;
    private TlsTrafficKeys? _tls12PendingReadKeys;

    private bool _disposed;

    public TlsHandshakeEngine(TlsHandshakeOptions options)
    {
        _options = options ?? throw new ArgumentNullException(nameof(options));
        _sessionCacheKey = LruTlsSessionCache.MakeKey(
            options.ServerName ?? string.Empty,
            options.Port,
            options.Profile?.Name ?? string.Empty);
    }

    public TlsHandshakeState State { get; private set; } = TlsHandshakeState.Init;
    public ushort NegotiatedVersion => _negotiatedVersion;
    public ushort NegotiatedCipherSuite => _suite?.Id ?? 0;
    public string? NegotiatedAlpn => _negotiatedAlpn;
    public byte[]? PeerTransportParameters => _peerTransportParameters;
    public byte[]? PeerApplicationSettings => _peerAlpsSettings is null ? null : (byte[])_peerAlpsSettings.Clone();
    public IReadOnlyList<DerCertificate>? PeerCertificates => _peerCertificates;
    public DerCertificate? LeafCertificate => _peerCertificates is { Count: > 0 } ? _peerCertificates[0] : null;
    public bool UsedSessionResumption => _usedSessionResumption;
    public bool ExtendedMasterSecretUsed => _extendedMasterSecretUsed;
    public bool HandshakeCompleted => State == TlsHandshakeState.Connected;
    public int MaxPlaintextFragment { get; private set; } = TlsRecordLayer.MaxPlaintextFragment;
    public long HandshakeBytesSent { get; private set; }
    public long HandshakeBytesReceived { get; private set; }

    public byte[] StartTcpHandshake()
    {
        ThrowIfDisposed();
        if (State != TlsHandshakeState.Init)
            throw new InvalidOperationException($"Cannot start handshake in state {State}.");

        _isQuicMode = false;
        _localQuicTransportParams = null;

        ClientHelloBuildResult ch = BuildInitialClientHello(isQuic: false, quicTp: null);
        AppendTranscript(ch.HandshakeMessage);
        State = TlsHandshakeState.AwaitServerHello;

        byte[] record = ch.ToTlsRecord();
        HandshakeBytesSent += record.Length;
        return record;
    }

    public byte[] StartQuicHandshake(byte[] localTransportParameters)
    {
        ThrowIfDisposed();
        ArgumentNullException.ThrowIfNull(localTransportParameters);
        if (State != TlsHandshakeState.Init)
            throw new InvalidOperationException($"Cannot start QUIC handshake in state {State}.");

        _isQuicMode = true;
        _localQuicTransportParams = (byte[])localTransportParameters.Clone();

        ClientHelloBuildResult ch = BuildInitialClientHello(isQuic: true, quicTp: _localQuicTransportParams);
        AppendTranscript(ch.HandshakeMessage);
        State = TlsHandshakeState.AwaitServerHello;
        HandshakeBytesSent += ch.HandshakeMessage.Length;
        return ch.HandshakeMessage;
    }

    public List<TcpStepOperation> ProcessTcpRecord(TlsContentType contentType, ReadOnlySpan<byte> payload)
    {
        ThrowIfDisposed();
        if (_isQuicMode)
            throw new InvalidOperationException("ProcessTcpRecord cannot be called on a QUIC handshake engine.");

        HandshakeBytesReceived += payload.Length;
        var ops = new List<TcpStepOperation>();

        try
        {
            switch (contentType)
            {
                case TlsContentType.Alert:
                    HandleAlertPayload(payload);
                    return ops;

                case TlsContentType.ChangeCipherSpec:
                    HandleTcpChangeCipherSpec(payload, ops);
                    return ops;

                case TlsContentType.Handshake:
                    if (payload.IsEmpty)
                        throw new TlsAlertException(TlsAlertDescription.DecodeError, "Received empty TLS handshake record.");
                    ProcessHandshakeBytesInternal(payload, isQuic: false, tcpOps: ops, quicOut: null);
                    return ops;

                default:
                    throw new TlsAlertException(
                        TlsAlertDescription.UnexpectedMessage,
                        $"Unexpected record content type {contentType} in state {State}.");
            }
        }
        catch (Exception) when (State != TlsHandshakeState.Closed)
        {
            State = TlsHandshakeState.Error;
            throw;
        }
    }

    public List<TcpStepOperation> ProcessPostHandshake(ReadOnlySpan<byte> handshakePayload)
    {
        ThrowIfDisposed();
        if (_isQuicMode)
            throw new InvalidOperationException("Use ProcessQuicCryptoData in QUIC mode.");
        if (State != TlsHandshakeState.Connected)
            throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Post-handshake message received in state {State}.");
        if (handshakePayload.IsEmpty)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Empty post-handshake record.");

        HandshakeBytesReceived += handshakePayload.Length;
        var ops = new List<TcpStepOperation>();
        try
        {
            ProcessHandshakeBytesInternal(handshakePayload, isQuic: false, tcpOps: ops, quicOut: null);
            return ops;
        }
        catch
        {
            State = TlsHandshakeState.Error;
            throw;
        }
    }

    public QuicHandshakeStepResult ProcessQuicCryptoData(QuicEncryptionLevel level, ReadOnlySpan<byte> data)
    {
        ThrowIfDisposed();
        if (!_isQuicMode)
            throw new InvalidOperationException("ProcessQuicCryptoData can only be called on a QUIC handshake engine.");

        ValidateQuicEncryptionLevel(level);
        HandshakeBytesReceived += data.Length;

        var quicAcc = new QuicStepAccumulator();
        try
        {
            ProcessHandshakeBytesInternal(data, isQuic: true, tcpOps: null, quicOut: quicAcc);

            return new QuicHandshakeStepResult
            {
                OutboundInitialData = quicAcc.InitialOutbound.ToArray(),
                OutboundHandshakeData = quicAcc.HandshakeOutbound.ToArray(),
                HandshakeReadKeys = quicAcc.HandshakeReadKeys,
                HandshakeWriteKeys = quicAcc.HandshakeWriteKeys,
                ApplicationReadKeys = quicAcc.ApplicationReadKeys,
                ApplicationWriteKeys = quicAcc.ApplicationWriteKeys,
                HandshakeCompleted = State == TlsHandshakeState.Connected,
                NegotiatedCipherSuite = NegotiatedCipherSuite,
                NegotiatedAlpn = NegotiatedAlpn,
                PeerTransportParameters = PeerTransportParameters,
                PeerCertificates = PeerCertificates,
                UsedSessionResumption = UsedSessionResumption,
            };
        }
        catch
        {
            State = TlsHandshakeState.Error;
            throw;
        }
    }

    private void ValidateQuicEncryptionLevel(QuicEncryptionLevel level)
    {
        switch (State)
        {
            case TlsHandshakeState.AwaitServerHello:
                if (level != QuicEncryptionLevel.Initial)
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Expected QUIC Initial CRYPTO data in state {State}, got {level}.");
                break;

            case TlsHandshakeState.AwaitEncryptedExtensions:
            case TlsHandshakeState.AwaitCertificateRequest:
            case TlsHandshakeState.AwaitCertificate:
            case TlsHandshakeState.AwaitCertificateVerify:
            case TlsHandshakeState.AwaitServerFinished:
                if (level != QuicEncryptionLevel.Handshake)
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Expected QUIC Handshake CRYPTO data in state {State}, got {level}.");
                break;

            case TlsHandshakeState.Connected:
                if (level != QuicEncryptionLevel.Application)
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Expected QUIC Application CRYPTO data in state {State}, got {level}.");
                break;

            default:
                throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Received QUIC CRYPTO data in invalid state {State}.");
        }
    }

    private ClientHelloBuildResult BuildInitialClientHello(bool isQuic, byte[]? quicTp)
    {
        TlsSessionTicket? cachedTicket = null;
        if (_options.SessionCache is not null &&
            !_options.DisableSessionTickets &&
            !string.IsNullOrEmpty(_options.ServerName))
        {
            _options.SessionCache.TryTake(_sessionCacheKey, out cachedTicket, _options.NowUtc);
        }

        ClientHelloBuildResult ch = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
        {
            Profile = _options.Profile,
            SpecOverride = _options.SpecOverride,
            ServerName = _options.ServerName,
            SessionTicket = cachedTicket,
            IsQuicMode = isQuic,
            QuicTransportParameters = quicTp,
            AlpnOverride = _options.AlpnOverride,
            ForceHttp11 = _options.ForceHttp11,
            RandomExtensionOrderOverride = _options.RandomExtensionOrder ? true : null,
            DisableSessionTickets = _options.DisableSessionTickets,
            Random = _options.Random,
            NowUtc = _options.NowUtc,
        });

        _clientHello = ch;
        foreach (KeyValuePair<ushort, AsymmetricKeyShareState> kv in ch.KeyShares)
            _ownedKeyShares[kv.Key] = kv.Value;

        _offeredCertCompression.Clear();
        CompressCertificateExtension? cc = ch.MaterializedSpec.GetExtension<CompressCertificateExtension>();
        if (cc is not null)
            _offeredCertCompression.AddRange(cc.Algorithms);

        return ch;
    }

    private void HandleAlertPayload(ReadOnlySpan<byte> payload)
    {
        if (payload.Length < 2)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated TLS alert record.");

        var level = (TlsAlertLevel)payload[0];
        var desc = (TlsAlertDescription)payload[1];

        if (desc == TlsAlertDescription.CloseNotify)
        {
            State = TlsHandshakeState.Closed;
            throw new TlsAlertException(desc, "Peer sent close_notify during handshake.", isLocal: false, level: level);
        }

        throw new TlsAlertException(desc, $"Peer sent TLS alert: {desc} ({(byte)desc})", isLocal: false, level: level);
    }

    private void HandleTcpChangeCipherSpec(ReadOnlySpan<byte> payload, List<TcpStepOperation> ops)
    {
        if (payload.Length != 1 || payload[0] != 0x01)
            throw new TlsAlertException(TlsAlertDescription.IllegalParameter, "Invalid ChangeCipherSpec payload.");

        if (_negotiatedVersion == TlsVersion.Tls13)
        {
            // Middlebox compatibility mode permits CCS before ServerFinished; must not appear after Connected.
            if (State == TlsHandshakeState.Connected)
                throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, "Unexpected ChangeCipherSpec after TLS 1.3 handshake completed.");
            return;
        }

        if (State is TlsHandshakeState.AwaitTls12NewSessionTicket or TlsHandshakeState.AwaitTls12Finished)
        {
            if (_rxHandshakeBuffer.Count > 0)
                throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, "Incomplete handshake message before ChangeCipherSpec.");

            if (_tls12PendingReadKeys is null)
                throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, "Unexpected TLS 1.2 ChangeCipherSpec.");

            _tls12ReceivedCcs = true;
            ops.Add(new TcpStepOperation(TcpStepOperationKind.InstallReadKeys, Keys: _tls12PendingReadKeys, IsTls13: false));
            _tls12PendingReadKeys = null;
            State = TlsHandshakeState.AwaitTls12Finished;
            return;
        }

        throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Unexpected ChangeCipherSpec in state {State}.");
    }

    private void ProcessHandshakeBytesInternal(
        ReadOnlySpan<byte> data,
        bool isQuic,
        List<TcpStepOperation>? tcpOps,
        QuicStepAccumulator? quicOut)
    {
        for (int i = 0; i < data.Length; i++)
            _rxHandshakeBuffer.Add(data[i]);

        while (_rxHandshakeBuffer.Count >= 4)
        {
            byte msgType = _rxHandshakeBuffer[0];
            int bodyLen = (_rxHandshakeBuffer[1] << 16) | (_rxHandshakeBuffer[2] << 8) | _rxHandshakeBuffer[3];
            if (bodyLen > MaxHandshakeMessageBytes)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, $"TLS handshake message length {bodyLen} exceeds limit.");

            if (_rxHandshakeBuffer.Count < 4 + bodyLen)
                break;

            var fullMsg = new byte[4 + bodyLen];
            _rxHandshakeBuffer.CopyTo(0, fullMsg, 0, fullMsg.Length);
            _rxHandshakeBuffer.RemoveRange(0, fullMsg.Length);
            ReadOnlySpan<byte> body = fullMsg.AsSpan(4);

            DispatchHandshakeMessage(msgType, fullMsg, body, isQuic, tcpOps, quicOut);

            // In QUIC, RFC 9001 §4.1.3 prohibits handshake messages from spanning encryption level changes.
            if (isQuic && msgType is 0x02 or 0x14 && _rxHandshakeBuffer.Count > 0)
            {
                if (State != TlsHandshakeState.AwaitServerHello) // ServerHello (non-HRR) or ServerFinished changed level
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, "Trailing CRYPTO bytes after encryption-level boundary message.");
            }

            // In TLS 1.3 KeyUpdate, sender switches write keys immediately after KeyUpdate.
            if (msgType == 0x18 && _rxHandshakeBuffer.Count > 0)
                throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, "Trailing handshake bytes after KeyUpdate in same record.");
        }
    }

    private void DispatchHandshakeMessage(
        byte msgType,
        byte[] fullMsg,
        ReadOnlySpan<byte> body,
        bool isQuic,
        List<TcpStepOperation>? tcpOps,
        QuicStepAccumulator? quicOut)
    {
        switch (State)
        {
            case TlsHandshakeState.AwaitServerHello:
                if (msgType != 0x02)
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Expected ServerHello (2), got 0x{msgType:X2}.");
                HandleServerHello(fullMsg, body, isQuic, tcpOps, quicOut);
                break;

            // ---- TLS 1.3 Path (states 2..6) ----
            case TlsHandshakeState.AwaitEncryptedExtensions:
                if (msgType != 0x08)
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Expected EncryptedExtensions (8), got 0x{msgType:X2}.");
                HandleEncryptedExtensions(fullMsg, body, tcpOps);
                break;

            case TlsHandshakeState.AwaitCertificateRequest:
                if (msgType == 0x0D)
                {
                    HandleTls13CertificateRequest(fullMsg, body);
                }
                else if (msgType == 0x0B)
                {
                    HandleTls13Certificate(fullMsg, body);
                }
                else if (msgType == 0x19)
                {
                    HandleTls13CompressedCertificate(fullMsg, body);
                }
                else
                {
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Expected CertificateRequest/Certificate in state {State}, got 0x{msgType:X2}.");
                }
                break;

            case TlsHandshakeState.AwaitCertificate:
                if (msgType == 0x0B)
                    HandleTls13Certificate(fullMsg, body);
                else if (msgType == 0x19)
                    HandleTls13CompressedCertificate(fullMsg, body);
                else
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Expected Certificate (11) or CompressedCertificate (25), got 0x{msgType:X2}.");
                break;

            case TlsHandshakeState.AwaitCertificateVerify:
                if (msgType != 0x0F)
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Expected CertificateVerify (15), got 0x{msgType:X2}.");
                HandleTls13CertificateVerify(fullMsg, body);
                break;

            case TlsHandshakeState.AwaitServerFinished:
                if (msgType != 0x14)
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Expected Finished (20), got 0x{msgType:X2}.");
                HandleTls13ServerFinished(fullMsg, body, isQuic, tcpOps, quicOut);
                break;

            // ---- TLS 1.2 Fallback Path (states 7..11) ----
            case TlsHandshakeState.AwaitTls12Certificate:
                if (msgType != 0x0B)
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Expected TLS 1.2 Certificate (11), got 0x{msgType:X2}.");
                HandleTls12Certificate(fullMsg, body);
                break;

            case TlsHandshakeState.AwaitTls12ServerKeyExchange:
                if (msgType == 0x16) // CertificateStatus (OCSP stapling)
                {
                    AppendTranscript(fullMsg);
                }
                else if (msgType == 0x0C) // ServerKeyExchange
                {
                    HandleTls12ServerKeyExchange(fullMsg, body);
                }
                else
                {
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Expected ServerKeyExchange (12) in state {State}, got 0x{msgType:X2}.");
                }
                break;

            case TlsHandshakeState.AwaitTls12ServerHelloDone:
                if (msgType == 0x16) // CertificateStatus
                {
                    AppendTranscript(fullMsg);
                }
                else if (msgType == 0x0D) // CertificateRequest
                {
                    _tls12CertRequested = true;
                    AppendTranscript(fullMsg);
                }
                else if (msgType == 0x0E) // ServerHelloDone
                {
                    HandleTls12ServerHelloDone(fullMsg, body, tcpOps!);
                }
                else
                {
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Expected ServerHelloDone (14) in state {State}, got 0x{msgType:X2}.");
                }
                break;

            case TlsHandshakeState.AwaitTls12NewSessionTicket:
                if (msgType == 0x04 && !_tls12ReceivedCcs)
                {
                    // RFC 5077 §3.3: NewSessionTicket precedes CCS and is included in Finished transcript.
                    AppendTranscript(fullMsg);
                }
                else
                {
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Unexpected handshake message 0x{msgType:X2} before TLS 1.2 ChangeCipherSpec.");
                }
                break;

            case TlsHandshakeState.AwaitTls12Finished:
                if (msgType != 0x14 || !_tls12ReceivedCcs)
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Expected TLS 1.2 Finished (20), got 0x{msgType:X2}.");
                HandleTls12ServerFinished(fullMsg, body, tcpOps!);
                break;

            // ---- Post-Handshake (state 12) ----
            case TlsHandshakeState.Connected:
                if (_negotiatedVersion != TlsVersion.Tls13)
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, "Unexpected post-handshake message on TLS 1.2 connection.");

                if (msgType == 0x04)
                {
                    HandleTls13NewSessionTicket(body);
                }
                else if (msgType == 0x18)
                {
                    if (isQuic)
                        throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, "KeyUpdate is prohibited on QUIC TLS connections (RFC 9001 §6).");
                    HandleTls13KeyUpdate(body, tcpOps!);
                }
                else
                {
                    throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Rejected post-handshake message type 0x{msgType:X2}.");
                }
                break;

            default:
                throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Handshake message 0x{msgType:X2} received in state {State}.");
        }
    }

    private void HandleServerHello(
        byte[] fullMsg,
        ReadOnlySpan<byte> body,
        bool isQuic,
        List<TcpStepOperation>? tcpOps,
        QuicStepAccumulator? quicOut)
    {
        if (body.Length < 2 + 32 + 1 + 2 + 1)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "ServerHello is truncated.");

        int offset = 0;
        ushort legacyVersion = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(offset, 2));
        offset += 2;

        ReadOnlySpan<byte> serverRandom = body.Slice(offset, 32);
        offset += 32;

        byte sessionIdLen = body[offset++];
        if (sessionIdLen > 32 || offset + sessionIdLen + 3 > body.Length)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid ServerHello legacy_session_id_echo.");

        ReadOnlySpan<byte> sessionIdEcho = body.Slice(offset, sessionIdLen);
        offset += sessionIdLen;

        ushort cipherSuiteId = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(offset, 2));
        offset += 2;

        byte compressionMethod = body[offset++];
        if (compressionMethod != 0x00)
            throw new TlsAlertException(TlsAlertDescription.IllegalParameter, $"Unsupported ServerHello compression method 0x{compressionMethod:X2}.");

        var extensions = new Dictionary<ushort, byte[]>();
        if (offset < body.Length)
        {
            if (offset + 2 > body.Length)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated ServerHello extensions length.");
            ushort extTotalLen = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(offset, 2));
            offset += 2;
            if (offset + extTotalLen != body.Length)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "ServerHello extensions length mismatch.");

            ReadOnlySpan<byte> extSpan = body.Slice(offset, extTotalLen);
            ParseExtensionsBlock(extSpan, extensions);
        }

        if (!_clientHello!.OfferedCipherSuites.Contains(cipherSuiteId))
            throw new TlsAlertException(TlsAlertDescription.IllegalParameter, $"Server selected unoffered cipher suite 0x{cipherSuiteId:X4}.");

        if (!TryGetCipherSuiteSpec(cipherSuiteId, out CipherSuiteSpec? suite) || suite is null)
            throw new TlsAlertException(TlsAlertDescription.HandshakeFailure, $"Unsupported cipher suite 0x{cipherSuiteId:X4}.");

        ushort selectedVersion = legacyVersion;
        if (extensions.TryGetValue(TlsExtensionType.SupportedVersions, out byte[]? svBytes))
        {
            if (svBytes.Length != 2)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid ServerHello supported_versions length.");
            selectedVersion = BinaryPrimitives.ReadUInt16BigEndian(svBytes);
        }

        if (selectedVersion == TlsVersion.Tls13)
        {
            if (legacyVersion != TlsVersion.Tls12 || !suite.IsTls13)
                throw new TlsAlertException(TlsAlertDescription.IllegalParameter, "Invalid legacy_version or cipher suite for TLS 1.3.");
            if (!sessionIdEcho.SequenceEqual(_clientHello.LegacySessionId))
                throw new TlsAlertException(TlsAlertDescription.IllegalParameter, "ServerHello legacy_session_id_echo does not match ClientHello.");

            // Check for HelloRetryRequest magic random
            if (ConstantTime.Equals(serverRandom, HelloRetryRequestRandom))
            {
                HandleHelloRetryRequest(fullMsg, suite, extensions, isQuic, tcpOps, quicOut);
                return;
            }

            _suite = suite;
            _negotiatedVersion = TlsVersion.Tls13;
            _serverRandom = serverRandom.ToArray();

            AppendTranscript(fullMsg);
            CompleteTls13ServerHelloKeySchedule(suite, extensions, isQuic, tcpOps, quicOut);
            State = TlsHandshakeState.AwaitEncryptedExtensions;
            return;
        }

        // TLS 1.2 fallback
        if (isQuic)
            throw new TlsAlertException(TlsAlertDescription.ProtocolVersion, "QUIC requires TLS 1.3 (RFC 9001 §4.1).");

        if (selectedVersion != TlsVersion.Tls12 || suite.IsTls13)
            throw new TlsAlertException(TlsAlertDescription.ProtocolVersion, $"Unsupported TLS version 0x{selectedVersion:X4} or cipher suite 0x{cipherSuiteId:X4}.");

        if (_clientHello.MaxOfferedVersion >= TlsVersion.Tls13 &&
            ConstantTime.Equals(serverRandom.Slice(24, 8), Tls12DowngradeSentinel))
        {
            throw new TlsAlertException(TlsAlertDescription.IllegalParameter, "Detected TLS 1.3->1.2 downgrade sentinel in ServerHello.random.");
        }

        if (!_options.Profile.Tls12Supported)
            throw new TlsAlertException(TlsAlertDescription.ProtocolVersion, "Profile does not permit TLS 1.2 fallback.");

        _suite = suite;
        _negotiatedVersion = TlsVersion.Tls12;
        _serverRandom = serverRandom.ToArray();

        if (extensions.TryGetValue(TlsExtensionType.ExtendedMasterSecret, out byte[]? emsData))
        {
            if (emsData.Length != 0)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Non-empty extended_master_secret extension.");
            _extendedMasterSecretUsed = true;
        }

        if (extensions.TryGetValue(TlsExtensionType.EncryptThenMac, out byte[]? etmData))
        {
            if (etmData.Length != 0)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Non-empty encrypt_then_mac extension.");
            if (suite.IsCbc)
                _encryptThenMacUsed = true;
        }

        if (extensions.TryGetValue(TlsExtensionType.RenegotiationInfo, out byte[]? renegData))
        {
            if (renegData.Length != 1 || renegData[0] != 0x00)
                throw new TlsAlertException(TlsAlertDescription.HandshakeFailure, "Invalid ServerHello renegotiation_info.");
        }

        if (extensions.TryGetValue(TlsExtensionType.ApplicationLayerProtocolNegotiation, out byte[]? alpnData))
            _negotiatedAlpn = ParseServerAlpnExtension(alpnData);

        AppendTranscript(fullMsg);
        State = TlsHandshakeState.AwaitTls12Certificate;
    }

    private void HandleHelloRetryRequest(
        byte[] hrrFullMsg,
        CipherSuiteSpec suite,
        Dictionary<ushort, byte[]> extensions,
        bool isQuic,
        List<TcpStepOperation>? tcpOps,
        QuicStepAccumulator? quicOut)
    {
        if (_sentHelloRetry)
            throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, "Received a second HelloRetryRequest.");
        _sentHelloRetry = true;
        _negotiatedVersion = TlsVersion.Tls13;
        _suite = suite;

        ushort? selectedGroup = null;
        if (extensions.TryGetValue(TlsExtensionType.KeyShare, out byte[]? ksData))
        {
            if (ksData.Length != 2)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid HRR key_share extension length.");
            selectedGroup = BinaryPrimitives.ReadUInt16BigEndian(ksData);
            if (!AsymmetricKeyShareState.IsSupportedGroup(selectedGroup.Value) ||
                !_clientHello!.OfferedGroups.Contains(selectedGroup.Value))
            {
                throw new TlsAlertException(TlsAlertDescription.IllegalParameter, $"HRR selected unsupported or unoffered group 0x{selectedGroup.Value:X4}.");
            }
        }

        byte[]? cookie = null;
        if (extensions.TryGetValue(0x002C, out byte[]? cookieExt))
        {
            if (cookieExt.Length < 3)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid HRR cookie extension.");
            ushort cookieLen = BinaryPrimitives.ReadUInt16BigEndian(cookieExt.AsSpan(0, 2));
            if (cookieLen == 0 || 2 + cookieLen != cookieExt.Length)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid HRR cookie length.");
            cookie = cookieExt.AsSpan(2, cookieLen).ToArray();
        }

        if (selectedGroup is null && cookie is null)
            throw new TlsAlertException(TlsAlertDescription.MissingExtension, "HelloRetryRequest carried neither key_share nor cookie.");

        // RFC 8446 §4.4.1: replace ClientHello1 in transcript with synthetic message_hash || HRR
        int hashLen = HashPrimitives.DigestLength(suite.HashAlg);
        byte[] ch1Hash = HashPrimitives.Hash(suite.HashAlg, _clientHello!.HandshakeMessage);
        var messageHash = new byte[4 + hashLen];
        messageHash[0] = 0xFE; // message_hash
        messageHash[1] = 0x00;
        messageHash[2] = 0x00;
        messageHash[3] = (byte)hashLen;
        ch1Hash.CopyTo(messageHash, 4);

        var hrrTranscriptPrefix = new byte[messageHash.Length + hrrFullMsg.Length];
        messageHash.CopyTo(hrrTranscriptPrefix, 0);
        hrrFullMsg.CopyTo(hrrTranscriptPrefix, messageHash.Length);

        ResetTranscript(hrrTranscriptPrefix);

        TlsSessionTicket? reofferTicket = _clientHello.OfferedPsk ? _clientHello.OfferedTicket : null;
        ClientHelloBuildResult ch2 = TlsClientHelloBuilder.Build(new ClientHelloBuildOptions
        {
            Profile = _options.Profile,
            SpecOverride = _clientHello.MaterializedSpec,
            ServerName = _options.ServerName,
            SessionTicket = reofferTicket,
            IsQuicMode = isQuic,
            QuicTransportParameters = _localQuicTransportParams,
            AlpnOverride = _options.AlpnOverride,
            ForceHttp11 = _options.ForceHttp11,
            RandomExtensionOrderOverride = _options.RandomExtensionOrder ? true : null,
            DisableSessionTickets = _options.DisableSessionTickets,
            Random = _options.Random,
            NowUtc = _options.NowUtc,
            PreviousClientRandom = _clientHello.ClientRandom,
            PreviousLegacySessionId = _clientHello.LegacySessionId,
            HelloRetrySelectedGroup = selectedGroup,
            HelloRetryCookie = cookie,
            HelloRetryTranscriptPrefix = hrrTranscriptPrefix,
            ExistingKeyShares = _ownedKeyShares,
        });

        _clientHello = ch2;
        foreach (KeyValuePair<ushort, AsymmetricKeyShareState> kv in ch2.KeyShares)
            _ownedKeyShares[kv.Key] = kv.Value;

        AppendTranscript(ch2.HandshakeMessage);

        if (isQuic)
        {
            quicOut!.InitialOutbound.AddRange(ch2.HandshakeMessage);
            HandshakeBytesSent += ch2.HandshakeMessage.Length;
        }
        else
        {
            HandshakeBytesSent += 5 + ch2.HandshakeMessage.Length;
            tcpOps!.Add(new TcpStepOperation(
                TcpStepOperationKind.SendPlaintextRecord,
                TlsContentType.Handshake,
                ch2.HandshakeMessage,
                RecordVersion: TlsVersion.Tls12));
        }

        State = TlsHandshakeState.AwaitServerHello;
    }

    private void CompleteTls13ServerHelloKeySchedule(
        CipherSuiteSpec suite,
        Dictionary<ushort, byte[]> extensions,
        bool isQuic,
        List<TcpStepOperation>? tcpOps,
        QuicStepAccumulator? quicOut)
    {
        HashAlgorithmKind hashAlg = suite.HashAlg;
        int hashLen = HashPrimitives.DigestLength(hashAlg);

        byte[] earlySecret;
        if (extensions.TryGetValue(TlsExtensionType.PreSharedKey, out byte[]? pskExt))
        {
            if (pskExt.Length != 2)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid ServerHello pre_shared_key extension.");

            ushort selectedIdentity = BinaryPrimitives.ReadUInt16BigEndian(pskExt);
            if (!_clientHello!.OfferedPsk || selectedIdentity != 0 || _clientHello.OfferedEarlySecret is null)
                throw new TlsAlertException(TlsAlertDescription.IllegalParameter, "Server selected unoffered PSK identity.");

            HashAlgorithmKind ticketHash = _clientHello.OfferedTicket!.CipherSuite != 0
                ? (_clientHello.OfferedTicket.CipherSuite == CipherSuiteId.TLS_AES_256_GCM_SHA384 ? HashAlgorithmKind.Sha384 : HashAlgorithmKind.Sha256)
                : _clientHello.OfferedTicket.HashAlg;
            if (ticketHash != hashAlg)
                throw new TlsAlertException(TlsAlertDescription.IllegalParameter, "Server selected cipher suite with different KDF hash than resumed PSK.");

            earlySecret = (byte[])_clientHello.OfferedEarlySecret.Clone();
            _usedSessionResumption = true;
        }
        else
        {
            earlySecret = HashPrimitives.HkdfExtract(hashAlg, ReadOnlySpan<byte>.Empty, new byte[hashLen]);
            _usedSessionResumption = false;
        }

        byte[]? sharedSecret = null;
        if (extensions.TryGetValue(TlsExtensionType.KeyShare, out byte[]? ksData))
        {
            if (ksData.Length < 4)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated ServerHello key_share.");
            ushort group = BinaryPrimitives.ReadUInt16BigEndian(ksData.AsSpan(0, 2));
            ushort keyLen = BinaryPrimitives.ReadUInt16BigEndian(ksData.AsSpan(2, 2));
            if (4 + keyLen != ksData.Length)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "ServerHello key_share length mismatch.");
            if (!_ownedKeyShares.TryGetValue(group, out AsymmetricKeyShareState? state))
                throw new TlsAlertException(TlsAlertDescription.IllegalParameter, $"ServerHello selected unoffered key_share group 0x{group:X4}.");

            try
            {
                sharedSecret = state.DeriveSharedSecret(ksData.AsSpan(4, keyLen));
            }
            catch (Exception ex) when (ex is ArgumentException or CryptographicException)
            {
                throw new TlsAlertException(TlsAlertDescription.IllegalParameter, $"Invalid server key_share: {ex.Message}");
            }
        }
        else if (!_usedSessionResumption)
        {
            throw new TlsAlertException(TlsAlertDescription.MissingExtension, "ServerHello missing key_share for non-PSK handshake.");
        }
        else
        {
            sharedSecret = new byte[hashLen];
        }

        try
        {
            byte[] emptyHash = HashPrimitives.Hash(hashAlg, ReadOnlySpan<byte>.Empty);
            byte[] derived = HashPrimitives.HkdfExpandLabel(hashAlg, earlySecret, "derived", emptyHash, hashLen);
            _handshakeSecret = HashPrimitives.HkdfExtract(hashAlg, derived, sharedSecret);
            ConstantTime.ZeroMemory(derived);

            byte[] chToShHash = ComputeTranscriptHash(hashAlg);
            _clientHandshakeTrafficSecret = HashPrimitives.HkdfExpandLabel(hashAlg, _handshakeSecret, "c hs traffic", chToShHash, hashLen);
            _serverHandshakeTrafficSecret = HashPrimitives.HkdfExpandLabel(hashAlg, _handshakeSecret, "s hs traffic", chToShHash, hashLen);

            if (_clientHello!.OfferedPsk && _clientHello.OfferedTicket is { MaxEarlyDataSize: > 0 })
            {
                byte[] ch1Hash = HashPrimitives.Hash(hashAlg, _clientHello.HandshakeMessage);
                _clientEarlyTrafficSecret = HashPrimitives.HkdfExpandLabel(hashAlg, earlySecret, "c e traffic", ch1Hash, hashLen);
            }

            EmitKeyLog("CLIENT_HANDSHAKE_TRAFFIC_SECRET", _clientHandshakeTrafficSecret);
            EmitKeyLog("SERVER_HANDSHAKE_TRAFFIC_SECRET", _serverHandshakeTrafficSecret);

            TlsTrafficKeys hsReadKeys = DeriveTls13TrafficKeys(_serverHandshakeTrafficSecret, suite);
            TlsTrafficKeys hsWriteKeys = DeriveTls13TrafficKeys(_clientHandshakeTrafficSecret, suite);

            if (isQuic)
            {
                quicOut!.HandshakeReadKeys = hsReadKeys;
                quicOut.HandshakeWriteKeys = hsWriteKeys;
            }
            else
            {
                tcpOps!.Add(new TcpStepOperation(TcpStepOperationKind.InstallReadKeys, Keys: hsReadKeys, IsTls13: true));
                tcpOps.Add(new TcpStepOperation(TcpStepOperationKind.InstallWriteKeys, Keys: hsWriteKeys, IsTls13: true));
            }
        }
        finally
        {
            ConstantTime.ZeroMemory(earlySecret);
            if (sharedSecret is not null)
                ConstantTime.ZeroMemory(sharedSecret);
        }
    }

    private void HandleEncryptedExtensions(byte[] fullMsg, ReadOnlySpan<byte> body, List<TcpStepOperation>? tcpOps)
    {
        if (body.Length < 2)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated EncryptedExtensions.");
        ushort extLen = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(0, 2));
        if (2 + extLen != body.Length)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "EncryptedExtensions length mismatch.");

        var extensions = new Dictionary<ushort, byte[]>();
        ParseExtensionsBlock(body.Slice(2, extLen), extensions);

        if (extensions.TryGetValue(TlsExtensionType.ApplicationLayerProtocolNegotiation, out byte[]? alpnData))
            _negotiatedAlpn = ParseServerAlpnExtension(alpnData);

        if (extensions.TryGetValue(TlsExtensionType.QuicTransportParameters, out byte[]? tp) ||
            extensions.TryGetValue(0xFFA5, out tp))
        {
            if (!_isQuicMode)
                throw new TlsAlertException(TlsAlertDescription.UnsupportedExtension, "Server sent quic_transport_parameters over non-QUIC transport.");
            _peerTransportParameters = tp;
        }
        else if (_isQuicMode)
        {
            throw new TlsAlertException(TlsAlertDescription.MissingExtension, "Server EncryptedExtensions missing quic_transport_parameters in QUIC mode.");
        }

        if (extensions.TryGetValue(TlsExtensionType.RecordSizeLimit, out byte[]? rslData))
        {
            if (rslData.Length != 2)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid record_size_limit extension.");
            ushort limit = BinaryPrimitives.ReadUInt16BigEndian(rslData);
            if (limit < TlsRecordLayer.MinRecordSizeLimit)
                throw new TlsAlertException(TlsAlertDescription.IllegalParameter, $"Server record_size_limit {limit} < 64.");
            int clamped = Math.Min((int)limit, TlsRecordLayer.MaxPlaintextFragment);
            MaxPlaintextFragment = clamped;
            tcpOps?.Add(new TcpStepOperation(TcpStepOperationKind.SetMaxPlaintextFragment, MaxPlaintextFragment: clamped));
        }

        if (extensions.ContainsKey(TlsExtensionType.EarlyData))
        {
            if (!_clientHello!.OfferedPsk || _clientHello.OfferedTicket?.MaxEarlyDataSize is not > 0)
                throw new TlsAlertException(TlsAlertDescription.UnsupportedExtension, "Server sent early_data when not offered.");
            _earlyDataAccepted = true;
        }

        if (extensions.TryGetValue(TlsExtensionType.ApplicationSettingsNew, out byte[]? alpsNewData))
        {
            if (string.IsNullOrEmpty(_negotiatedAlpn))
                throw new TlsAlertException(TlsAlertDescription.IllegalParameter, "Server sent application_settings without ALPN.");
            _peerAlpsCodepoint = TlsExtensionType.ApplicationSettingsNew;
            _peerAlpsSettings = alpsNewData;
        }
        else if (extensions.TryGetValue(TlsExtensionType.ApplicationSettings, out byte[]? alpsOldData))
        {
            if (string.IsNullOrEmpty(_negotiatedAlpn))
                throw new TlsAlertException(TlsAlertDescription.IllegalParameter, "Server sent legacy application_settings without ALPN.");
            _peerAlpsCodepoint = TlsExtensionType.ApplicationSettings;
            _peerAlpsSettings = alpsOldData;
        }

        AppendTranscript(fullMsg);
        State = _usedSessionResumption
            ? TlsHandshakeState.AwaitServerFinished
            : TlsHandshakeState.AwaitCertificateRequest;
    }

    private void HandleTls13CertificateRequest(byte[] fullMsg, ReadOnlySpan<byte> body)
    {
        if (body.Length < 3)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated TLS 1.3 CertificateRequest.");
        byte ctxLen = body[0];
        if (1 + ctxLen + 2 > body.Length)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid CertificateRequest context length.");

        _tls13CertRequestContext = body.Slice(1, ctxLen).ToArray();
        _tls13ClientCertRequested = true;
        AppendTranscript(fullMsg);
        State = TlsHandshakeState.AwaitCertificate;
    }

    private void HandleTls13Certificate(byte[] fullMsg, ReadOnlySpan<byte> body)
    {
        List<byte[]> chain = ParseTls13CertificateBody(body);
        VerifyServerCertificateChain(chain);
        AppendTranscript(fullMsg);
        State = TlsHandshakeState.AwaitCertificateVerify;
    }

    private void HandleTls13CompressedCertificate(byte[] fullMsg, ReadOnlySpan<byte> body)
    {
        if (body.Length < 8)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated CompressedCertificate message.");

        ushort algId = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(0, 2));
        int uncompressedLen = (body[2] << 16) | (body[3] << 8) | body[4];
        int compressedLen = (body[5] << 16) | (body[6] << 8) | body[7];

        if (8 + compressedLen != body.Length || compressedLen == 0)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid CompressedCertificate lengths.");

        if (uncompressedLen == 0 || uncompressedLen > MaxUncompressedCertificateBytes)
            throw new TlsAlertException(TlsAlertDescription.BadCertificate, $"CompressedCertificate uncompressed_length {uncompressedLen} exceeds 16 MiB ceiling.");

        var alg = (CertCompressionAlgorithm)algId;
        if (!_offeredCertCompression.Contains(alg))
            throw new TlsAlertException(TlsAlertDescription.IllegalParameter, $"Server used unoffered certificate compression algorithm {algId}.");

        byte[] compressed = body.Slice(8, compressedLen).ToArray();
        byte[] decompressed = alg switch
        {
            CertCompressionAlgorithm.Zlib => DecompressZlibBounded(compressed, uncompressedLen),
            CertCompressionAlgorithm.Brotli => DecompressBrotliBounded(compressed, uncompressedLen),
            CertCompressionAlgorithm.Zstd => DecompressZstdBounded(compressed, uncompressedLen),
            _ => throw new TlsAlertException(TlsAlertDescription.IllegalParameter, $"Unsupported certificate compression algorithm {algId}."),
        };

        List<byte[]> chain = ParseTls13CertificateBody(decompressed);
        VerifyServerCertificateChain(chain);

        // RFC 8879 §4: CompressedCertificate wire message itself enters the transcript hash.
        AppendTranscript(fullMsg);
        State = TlsHandshakeState.AwaitCertificateVerify;
    }

    private void HandleTls13CertificateVerify(byte[] fullMsg, ReadOnlySpan<byte> body)
    {
        if (body.Length < 4)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated CertificateVerify.");

        ushort scheme = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(0, 2));
        ushort sigLen = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(2, 2));
        if (4 + sigLen != body.Length)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "CertificateVerify signature length mismatch.");

        DerCertificate leaf = LeafCertificate
            ?? throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, "Missing server certificate before CertificateVerify.");

        byte[] transcriptHash = ComputeTranscriptHash(_suite!.HashAlg);
        ReadOnlySpan<byte> prefix = "TLS 1.3, server CertificateVerify"u8;
        var signedContent = new byte[64 + prefix.Length + 1 + transcriptHash.Length];
        signedContent.AsSpan(0, 64).Fill(0x20);
        prefix.CopyTo(signedContent.AsSpan(64));
        signedContent[64 + prefix.Length] = 0x00;
        transcriptHash.CopyTo(signedContent.AsSpan(64 + prefix.Length + 1));

        ReadOnlySpan<byte> signature = body.Slice(4, sigLen);
        if (!VerifyTls13Signature(leaf, scheme, signedContent, signature))
        {
            throw new TlsAlertException(
                TlsAlertDescription.DecryptError,
                $"TLS 1.3 CertificateVerify signature verification failed for scheme 0x{scheme:X4}.");
        }

        AppendTranscript(fullMsg);
        State = TlsHandshakeState.AwaitServerFinished;
    }

    private void HandleTls13ServerFinished(
        byte[] fullMsg,
        ReadOnlySpan<byte> body,
        bool isQuic,
        List<TcpStepOperation>? tcpOps,
        QuicStepAccumulator? quicOut)
    {
        HashAlgorithmKind hashAlg = _suite!.HashAlg;
        int hashLen = HashPrimitives.DigestLength(hashAlg);
        if (body.Length != hashLen)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, $"Invalid Finished verify_data length {body.Length}; expected {hashLen}.");

        byte[] finishedKey = HashPrimitives.HkdfExpandLabel(
            hashAlg,
            _serverHandshakeTrafficSecret!,
            "finished",
            ReadOnlySpan<byte>.Empty,
            hashLen);
        byte[] transcriptBeforeFinished = ComputeTranscriptHash(hashAlg);
        byte[] expectedVerifyData = HashPrimitives.Hmac(hashAlg, finishedKey, transcriptBeforeFinished);
        ConstantTime.ZeroMemory(finishedKey);

        if (!ConstantTime.Equals(body, expectedVerifyData))
            throw new TlsAlertException(TlsAlertDescription.DecryptError, "TLS 1.3 server Finished verify_data mismatch.");

        AppendTranscript(fullMsg);

        byte[] serverFinishedHash = ComputeTranscriptHash(hashAlg);
        byte[] emptyHash = HashPrimitives.Hash(hashAlg, ReadOnlySpan<byte>.Empty);
        byte[] derivedMaster = HashPrimitives.HkdfExpandLabel(hashAlg, _handshakeSecret!, "derived", emptyHash, hashLen);
        byte[] masterSecret = HashPrimitives.HkdfExtract(hashAlg, derivedMaster, new byte[hashLen]);
        ConstantTime.ZeroMemory(derivedMaster);

        try
        {
            _clientAppTrafficSecret = HashPrimitives.HkdfExpandLabel(hashAlg, masterSecret, "c ap traffic", serverFinishedHash, hashLen);
            _serverAppTrafficSecret = HashPrimitives.HkdfExpandLabel(hashAlg, masterSecret, "s ap traffic", serverFinishedHash, hashLen);
            _exporterMasterSecret = HashPrimitives.HkdfExpandLabel(hashAlg, masterSecret, "exp master", serverFinishedHash, hashLen);

            EmitKeyLog("CLIENT_TRAFFIC_SECRET_0", _clientAppTrafficSecret);
            EmitKeyLog("SERVER_TRAFFIC_SECRET_0", _serverAppTrafficSecret);
            EmitKeyLog("EXPORTER_SECRET", _exporterMasterSecret);

            // Optional EndOfEarlyData if early_data was accepted (RFC 8446 §4.5)
            if (_earlyDataAccepted && _clientEarlyTrafficSecret is not null)
            {
                var eoed = new byte[] { 0x05, 0x00, 0x00, 0x00 };
                if (!isQuic)
                {
                    TlsTrafficKeys earlyKeys = DeriveTls13TrafficKeys(_clientEarlyTrafficSecret, _suite);
                    tcpOps!.Add(new TcpStepOperation(TcpStepOperationKind.InstallWriteKeys, Keys: earlyKeys, IsTls13: true));
                    tcpOps.Add(new TcpStepOperation(TcpStepOperationKind.SendProtectedRecord, TlsContentType.Handshake, eoed));
                    TlsTrafficKeys hsWriteKeys = DeriveTls13TrafficKeys(_clientHandshakeTrafficSecret!, _suite);
                    tcpOps.Add(new TcpStepOperation(TcpStepOperationKind.InstallWriteKeys, Keys: hsWriteKeys, IsTls13: true));
                }
                AppendTranscript(eoed);
            }

            // Send ALPS client EncryptedExtensions if server confirmed ApplicationSettings (draft-vv-tls-alps).
            if (_peerAlpsCodepoint != 0)
            {
                var clientEe = new byte[10];
                clientEe[0] = 0x08;
                clientEe[1] = 0x00;
                clientEe[2] = 0x00;
                clientEe[3] = 0x06;
                clientEe[4] = 0x00;
                clientEe[5] = 0x04;
                BinaryPrimitives.WriteUInt16BigEndian(clientEe.AsSpan(6, 2), _peerAlpsCodepoint);
                clientEe[8] = 0x00;
                clientEe[9] = 0x00;
                AppendTranscript(clientEe);

                if (isQuic)
                {
                    quicOut!.HandshakeOutbound.AddRange(clientEe);
                    HandshakeBytesSent += clientEe.Length;
                }
                else
                {
                    tcpOps!.Add(new TcpStepOperation(TcpStepOperationKind.SendProtectedRecord, TlsContentType.Handshake, clientEe));
                    HandshakeBytesSent += clientEe.Length;
                }
            }

            // If server requested a client certificate in TLS 1.3, send empty Certificate before client Finished.
            if (_tls13ClientCertRequested)
            {
                byte[] ctx = _tls13CertRequestContext ?? Array.Empty<byte>();
                int certBodyLen = 1 + ctx.Length + 3;
                var emptyCert = new byte[4 + certBodyLen];
                emptyCert[0] = 0x0B;
                emptyCert[1] = (byte)(certBodyLen >> 16);
                emptyCert[2] = (byte)(certBodyLen >> 8);
                emptyCert[3] = (byte)certBodyLen;
                emptyCert[4] = (byte)ctx.Length;
                ctx.CopyTo(emptyCert, 5);
                AppendTranscript(emptyCert);

                if (isQuic)
                {
                    quicOut!.HandshakeOutbound.AddRange(emptyCert);
                    HandshakeBytesSent += emptyCert.Length;
                }
                else
                {
                    tcpOps!.Add(new TcpStepOperation(TcpStepOperationKind.SendProtectedRecord, TlsContentType.Handshake, emptyCert));
                    HandshakeBytesSent += emptyCert.Length;
                }
            }

            // Build client Finished under client handshake traffic secret
            byte[] clientFinishedKey = HashPrimitives.HkdfExpandLabel(
                hashAlg,
                _clientHandshakeTrafficSecret!,
                "finished",
                ReadOnlySpan<byte>.Empty,
                hashLen);
            byte[] clientVerifyTranscript = ComputeTranscriptHash(hashAlg);
            byte[] clientVerifyData = HashPrimitives.Hmac(hashAlg, clientFinishedKey, clientVerifyTranscript);
            ConstantTime.ZeroMemory(clientFinishedKey);

            var clientFinishedMsg = new byte[4 + hashLen];
            clientFinishedMsg[0] = 0x14;
            clientFinishedMsg[1] = (byte)(hashLen >> 16);
            clientFinishedMsg[2] = (byte)(hashLen >> 8);
            clientFinishedMsg[3] = (byte)hashLen;
            clientVerifyData.CopyTo(clientFinishedMsg, 4);

            AppendTranscript(clientFinishedMsg);

            byte[] afterClientFinishedHash = ComputeTranscriptHash(hashAlg);
            _resumptionMasterSecret = HashPrimitives.HkdfExpandLabel(hashAlg, masterSecret, "res master", afterClientFinishedHash, hashLen);

            TlsTrafficKeys appReadKeys = DeriveTls13TrafficKeys(_serverAppTrafficSecret, _suite);
            TlsTrafficKeys appWriteKeys = DeriveTls13TrafficKeys(_clientAppTrafficSecret, _suite);

            if (isQuic)
            {
                quicOut!.HandshakeOutbound.AddRange(clientFinishedMsg);
                HandshakeBytesSent += clientFinishedMsg.Length;
                quicOut.ApplicationReadKeys = appReadKeys;
                quicOut.ApplicationWriteKeys = appWriteKeys;
            }
            else
            {
                tcpOps!.Add(new TcpStepOperation(TcpStepOperationKind.SendProtectedRecord, TlsContentType.Handshake, clientFinishedMsg));
                HandshakeBytesSent += clientFinishedMsg.Length;
                tcpOps.Add(new TcpStepOperation(TcpStepOperationKind.InstallReadKeys, Keys: appReadKeys, IsTls13: true));
                tcpOps.Add(new TcpStepOperation(TcpStepOperationKind.InstallWriteKeys, Keys: appWriteKeys, IsTls13: true));
                tcpOps.Add(new TcpStepOperation(TcpStepOperationKind.MarkHandshakeCompleted));
            }

            State = TlsHandshakeState.Connected;
        }
        finally
        {
            ConstantTime.ZeroMemory(masterSecret);
        }
    }

    private void HandleTls13NewSessionTicket(ReadOnlySpan<byte> body)
    {
        if (body.Length < 4 + 4 + 1 + 2 + 2)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated NewSessionTicket.");

        int offset = 0;
        uint lifetime = BinaryPrimitives.ReadUInt32BigEndian(body.Slice(offset, 4));
        offset += 4;
        uint ageAdd = BinaryPrimitives.ReadUInt32BigEndian(body.Slice(offset, 4));
        offset += 4;

        byte nonceLen = body[offset++];
        if (offset + nonceLen + 2 > body.Length)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid NewSessionTicket nonce length.");
        byte[] ticketNonce = body.Slice(offset, nonceLen).ToArray();
        offset += nonceLen;

        ushort ticketLen = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(offset, 2));
        offset += 2;
        if (offset + ticketLen + 2 > body.Length)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid NewSessionTicket ticket length.");
        byte[] ticketBytes = body.Slice(offset, ticketLen).ToArray();
        offset += ticketLen;

        ushort extLen = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(offset, 2));
        offset += 2;
        if (offset + extLen != body.Length)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid NewSessionTicket extensions length.");

        uint maxEarlyData = 0;
        if (extLen > 0)
        {
            var exts = new Dictionary<ushort, byte[]>();
            ParseExtensionsBlock(body.Slice(offset, extLen), exts);
            if (exts.TryGetValue(TlsExtensionType.EarlyData, out byte[]? earlyDataExt) && earlyDataExt.Length == 4)
                maxEarlyData = BinaryPrimitives.ReadUInt32BigEndian(earlyDataExt);
        }

        if (lifetime == 0 || ticketBytes.Length == 0 || _resumptionMasterSecret is null || _suite is null)
            return;

        if (_options.SessionCache is not null &&
            !_options.DisableSessionTickets &&
            !string.IsNullOrEmpty(_options.ServerName))
        {
            uint boundedLifetime = Math.Min(lifetime, 604_800u);
            byte[] psk = TlsSessionTicket.DerivePsk(_suite.HashAlg, _resumptionMasterSecret, ticketNonce);
            var cached = new TlsSessionTicket(
                ticket: ticketBytes,
                ticketAgeAdd: ageAdd,
                lifetimeSeconds: boundedLifetime,
                issuedAtUtc: _options.NowUtc ?? DateTimeOffset.UtcNow,
                resumptionMasterSecret: (byte[])_resumptionMasterSecret.Clone(),
                ticketNonce: ticketNonce,
                cipherSuite: _suite.Id,
                hashAlg: _suite.HashAlg,
                negotiatedAlpn: _negotiatedAlpn,
                maxEarlyDataSize: maxEarlyData,
                psk: psk);

            _options.SessionCache.Put(_sessionCacheKey, cached);
        }
    }

    private void HandleTls13KeyUpdate(ReadOnlySpan<byte> body, List<TcpStepOperation> ops)
    {
        if (body.Length != 1 || body[0] > 1)
            throw new TlsAlertException(TlsAlertDescription.IllegalParameter, "Invalid KeyUpdate request_update value.");

        byte requestUpdate = body[0];
        HashAlgorithmKind hashAlg = _suite!.HashAlg;
        int hashLen = HashPrimitives.DigestLength(hashAlg);

        byte[] nextServerSecret = HashPrimitives.HkdfExpandLabel(
            hashAlg,
            _serverAppTrafficSecret!,
            "traffic upd",
            ReadOnlySpan<byte>.Empty,
            hashLen);
        ConstantTime.ZeroMemory(_serverAppTrafficSecret!);
        _serverAppTrafficSecret = nextServerSecret;

        TlsTrafficKeys newReadKeys = DeriveTls13TrafficKeys(_serverAppTrafficSecret, _suite);
        ops.Add(new TcpStepOperation(TcpStepOperationKind.InstallReadKeys, Keys: newReadKeys, IsTls13: true));

        if (requestUpdate == 1)
        {
            // Reply KeyUpdate(update_not_requested=0) under current write key BEFORE updating write key.
            var reply = new byte[] { 0x18, 0x00, 0x00, 0x01, 0x00 };
            ops.Add(new TcpStepOperation(TcpStepOperationKind.SendProtectedRecord, TlsContentType.Handshake, reply));
            HandshakeBytesSent += reply.Length;

            byte[] nextClientSecret = HashPrimitives.HkdfExpandLabel(
                hashAlg,
                _clientAppTrafficSecret!,
                "traffic upd",
                ReadOnlySpan<byte>.Empty,
                hashLen);
            ConstantTime.ZeroMemory(_clientAppTrafficSecret!);
            _clientAppTrafficSecret = nextClientSecret;

            TlsTrafficKeys newWriteKeys = DeriveTls13TrafficKeys(_clientAppTrafficSecret, _suite);
            ops.Add(new TcpStepOperation(TcpStepOperationKind.InstallWriteKeys, Keys: newWriteKeys, IsTls13: true));
        }
    }

    // ---- TLS 1.2 Handlers ----

    private void HandleTls12Certificate(byte[] fullMsg, ReadOnlySpan<byte> body)
    {
        if (body.Length < 3)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated TLS 1.2 Certificate message.");

        int listLen = (body[0] << 16) | (body[1] << 8) | body[2];
        if (3 + listLen != body.Length)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "TLS 1.2 Certificate list length mismatch.");

        var derChain = new List<byte[]>();
        int offset = 3;
        while (offset < body.Length)
        {
            if (offset + 3 > body.Length)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated certificate entry length.");
            int certLen = (body[offset] << 16) | (body[offset + 1] << 8) | body[offset + 2];
            offset += 3;
            if (certLen == 0 || offset + certLen > body.Length)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid certificate entry length.");
            derChain.Add(body.Slice(offset, certLen).ToArray());
            offset += certLen;
        }

        VerifyServerCertificateChain(derChain);
        AppendTranscript(fullMsg);

        State = _suite!.UsesEcdhe
            ? TlsHandshakeState.AwaitTls12ServerKeyExchange
            : TlsHandshakeState.AwaitTls12ServerHelloDone;
    }

    private void HandleTls12ServerKeyExchange(byte[] fullMsg, ReadOnlySpan<byte> body)
    {
        if (body.Length < 4)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated TLS 1.2 ServerKeyExchange.");

        byte curveType = body[0];
        if (curveType != 3) // named_curve
            throw new TlsAlertException(TlsAlertDescription.IllegalParameter, $"Unsupported ECDHE curve_type {curveType}.");

        ushort namedCurve = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(1, 2));
        byte pubLen = body[3];
        if (pubLen == 0 || 4 + pubLen + 4 > body.Length)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid ServerKeyExchange ECDHE point.");

        ReadOnlySpan<byte> serverPub = body.Slice(4, pubLen);
        int sigOffset = 4 + pubLen;
        ushort sigAlg = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(sigOffset, 2));
        ushort sigLen = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(sigOffset + 2, 2));
        if (sigOffset + 4 + sigLen != body.Length)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "ServerKeyExchange signature length mismatch.");

        DerCertificate leaf = LeafCertificate
            ?? throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, "Missing leaf certificate before ServerKeyExchange.");

        // Signed payload: client_random(32) || server_random(32) || ec_params(4 + pubLen)
        var signedInput = new byte[32 + 32 + sigOffset];
        _clientHello!.ClientRandom.CopyTo(signedInput, 0);
        _serverRandom!.CopyTo(signedInput, 32);
        body.Slice(0, sigOffset).CopyTo(signedInput.AsSpan(64));

        ReadOnlySpan<byte> signature = body.Slice(sigOffset + 4, sigLen);
        if (!VerifyTls12Signature(leaf, sigAlg, signedInput, signature))
            throw new TlsAlertException(TlsAlertDescription.DecryptError, $"TLS 1.2 ServerKeyExchange signature verification failed for scheme 0x{sigAlg:X4}.");

        // Compute ephemeral client keyshare & pre-master secret
        byte[] clientPub;
        byte[] preMaster;
        switch (namedCurve)
        {
            case NamedGroupId.X25519:
            {
                X25519.GenerateKeyPair(out byte[] priv, out clientPub);
                try
                {
                    preMaster = X25519.ScalarMult(priv, serverPub);
                }
                catch (Exception ex) when (ex is ArgumentException or CryptographicException)
                {
                    throw new TlsAlertException(TlsAlertDescription.IllegalParameter, $"Invalid server X25519 point: {ex.Message}");
                }
                finally
                {
                    ConstantTime.ZeroMemory(priv);
                }
                break;
            }
            case NamedGroupId.Secp256r1:
            case NamedGroupId.Secp384r1:
            case NamedGroupId.Secp521r1:
            {
                EcCurveKind ecCurve = namedCurve switch
                {
                    NamedGroupId.Secp256r1 => EcCurveKind.P256,
                    NamedGroupId.Secp384r1 => EcCurveKind.P384,
                    _ => EcCurveKind.P521,
                };
                (byte[] priv, byte[] pub) = EcPrimitives.GenerateEcdheKeyPair(ecCurve);
                clientPub = pub;
                try
                {
                    preMaster = EcPrimitives.DeriveEcdheSharedSecret(ecCurve, priv, serverPub);
                }
                catch (Exception ex) when (ex is ArgumentException or CryptographicException)
                {
                    throw new TlsAlertException(TlsAlertDescription.IllegalParameter, $"Invalid server ECDHE point: {ex.Message}");
                }
                finally
                {
                    ConstantTime.ZeroMemory(priv);
                }
                break;
            }
            default:
                throw new TlsAlertException(TlsAlertDescription.IllegalParameter, $"Unsupported TLS 1.2 named_curve 0x{namedCurve:X4}.");
        }

        _tls12PreMasterSecret = preMaster;
        _tls12ClientEcdhePublic = clientPub;

        AppendTranscript(fullMsg);
        State = TlsHandshakeState.AwaitTls12ServerHelloDone;
    }

    private byte[]? _tls12ClientEcdhePublic;

    private void HandleTls12ServerHelloDone(byte[] fullMsg, ReadOnlySpan<byte> body, List<TcpStepOperation> ops)
    {
        if (body.Length != 0)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "ServerHelloDone must have empty body.");

        AppendTranscript(fullMsg);

        if (_tls12CertRequested)
        {
            var emptyCert = new byte[] { 0x0B, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00 };
            AppendTranscript(emptyCert);
            ops.Add(new TcpStepOperation(TcpStepOperationKind.SendPlaintextRecord, TlsContentType.Handshake, emptyCert));
            HandshakeBytesSent += emptyCert.Length;
        }

        byte[] clientKeyExchange;
        if (_suite!.UsesEcdhe)
        {
            byte[] pub = _tls12ClientEcdhePublic
                ?? throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, "Missing ServerKeyExchange before ServerHelloDone.");
            int ckeBodyLen = 1 + pub.Length;
            clientKeyExchange = new byte[4 + ckeBodyLen];
            clientKeyExchange[0] = 0x10;
            clientKeyExchange[1] = (byte)(ckeBodyLen >> 16);
            clientKeyExchange[2] = (byte)(ckeBodyLen >> 8);
            clientKeyExchange[3] = (byte)ckeBodyLen;
            clientKeyExchange[4] = (byte)pub.Length;
            pub.CopyTo(clientKeyExchange, 5);
        }
        else
        {
            // Static RSA key exchange
            DerCertificate leaf = LeafCertificate
                ?? throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, "Missing leaf certificate for RSA key exchange.");
            if (leaf.PublicKeyAlgorithmOid != "1.2.840.113549.1.1.1" ||
                !RsaPrimitives.TryParseRsaPublicKeyDer(leaf.PublicKeyBitString, out byte[] modulus, out byte[] exponent))
            {
                throw new TlsAlertException(TlsAlertDescription.UnsupportedCertificate, "Leaf certificate does not carry a valid RSA key.");
            }

            var preMaster = new byte[48];
            preMaster[0] = 0x03;
            preMaster[1] = 0x03;
            RandomNumberGenerator.Fill(preMaster.AsSpan(2, 46));
            _tls12PreMasterSecret = preMaster;

            byte[] encryptedPreMaster = EncryptRsaPkcs1(modulus, exponent, preMaster);
            int ckeBodyLen = 2 + encryptedPreMaster.Length;
            clientKeyExchange = new byte[4 + ckeBodyLen];
            clientKeyExchange[0] = 0x10;
            clientKeyExchange[1] = (byte)(ckeBodyLen >> 16);
            clientKeyExchange[2] = (byte)(ckeBodyLen >> 8);
            clientKeyExchange[3] = (byte)ckeBodyLen;
            BinaryPrimitives.WriteUInt16BigEndian(clientKeyExchange.AsSpan(4, 2), (ushort)encryptedPreMaster.Length);
            encryptedPreMaster.CopyTo(clientKeyExchange, 6);
        }

        AppendTranscript(clientKeyExchange);
        ops.Add(new TcpStepOperation(TcpStepOperationKind.SendPlaintextRecord, TlsContentType.Handshake, clientKeyExchange));
        HandshakeBytesSent += clientKeyExchange.Length;

        // Derive TLS 1.2 master secret (RFC 7627 Extended Master Secret when negotiated)
        HashAlgorithmKind prfHash = _suite.HashAlg;
        if (_extendedMasterSecretUsed)
        {
            byte[] sessionHash = ComputeTranscriptHash(prfHash);
            _tls12MasterSecret = HashPrimitives.Tls12Prf(prfHash, _tls12PreMasterSecret!, "extended master secret", sessionHash, 48);
        }
        else
        {
            var seed = new byte[64];
            _clientHello!.ClientRandom.CopyTo(seed, 0);
            _serverRandom!.CopyTo(seed, 32);
            _tls12MasterSecret = HashPrimitives.Tls12Prf(prfHash, _tls12PreMasterSecret!, "master secret", seed, 48);
        }

        ConstantTime.ZeroMemory(_tls12PreMasterSecret!);
        _tls12PreMasterSecret = null;

        EmitKeyLog("CLIENT_RANDOM", _tls12MasterSecret);

        (TlsTrafficKeys clientWriteKeys, TlsTrafficKeys serverReadKeys) = DeriveTls12TrafficKeys(
            _suite,
            _tls12MasterSecret,
            _clientHello!.ClientRandom,
            _serverRandom!,
            _encryptThenMacUsed);

        _tls12PendingReadKeys = serverReadKeys;

        // ChangeCipherSpec -> InstallWriteKeys -> encrypted Finished
        ops.Add(new TcpStepOperation(TcpStepOperationKind.SendPlaintextRecord, TlsContentType.ChangeCipherSpec, new byte[] { 0x01 }));
        ops.Add(new TcpStepOperation(TcpStepOperationKind.InstallWriteKeys, Keys: clientWriteKeys, IsTls13: false));

        byte[] handshakeHash = ComputeTranscriptHash(prfHash);
        byte[] verifyData = HashPrimitives.Tls12Prf(prfHash, _tls12MasterSecret, "client finished", handshakeHash, 12);
        var clientFinishedMsg = new byte[4 + 12];
        clientFinishedMsg[0] = 0x14;
        clientFinishedMsg[1] = 0x00;
        clientFinishedMsg[2] = 0x00;
        clientFinishedMsg[3] = 0x0C;
        verifyData.CopyTo(clientFinishedMsg, 4);

        AppendTranscript(clientFinishedMsg);
        ops.Add(new TcpStepOperation(TcpStepOperationKind.SendProtectedRecord, TlsContentType.Handshake, clientFinishedMsg));
        HandshakeBytesSent += clientFinishedMsg.Length;

        State = TlsHandshakeState.AwaitTls12NewSessionTicket;
    }

    private void HandleTls12ServerFinished(byte[] fullMsg, ReadOnlySpan<byte> body, List<TcpStepOperation> ops)
    {
        if (body.Length != 12)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, $"Invalid TLS 1.2 Finished length {body.Length}; expected 12.");

        HashAlgorithmKind prfHash = _suite!.HashAlg;
        byte[] handshakeHash = ComputeTranscriptHash(prfHash);
        byte[] expected = HashPrimitives.Tls12Prf(prfHash, _tls12MasterSecret!, "server finished", handshakeHash, 12);

        if (!ConstantTime.Equals(body, expected))
            throw new TlsAlertException(TlsAlertDescription.DecryptError, "TLS 1.2 server Finished verify_data mismatch.");

        AppendTranscript(fullMsg);
        ConstantTime.ZeroMemory(_tls12MasterSecret!);
        _tls12MasterSecret = null;

        ops.Add(new TcpStepOperation(TcpStepOperationKind.MarkHandshakeCompleted));
        State = TlsHandshakeState.Connected;
    }

    // ---- Shared Verification & Parsing Helpers ----

    private void VerifyServerCertificateChain(IReadOnlyList<byte[]> derChain)
    {
        CertificateVerifyOptions verifyOpts = _options.VerifyOptions ?? new CertificateVerifyOptions();
        _peerCertificates = CertificateVerifier.VerifyChain(derChain, _options.ServerName, verifyOpts);
    }

    private static List<byte[]> ParseTls13CertificateBody(ReadOnlySpan<byte> body)
    {
        if (body.Length < 4)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated TLS 1.3 Certificate message.");

        int offset = 0;
        byte reqCtxLen = body[offset++];
        if (offset + reqCtxLen + 3 > body.Length)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid TLS 1.3 certificate_request_context.");
        offset += reqCtxLen;

        int listLen = (body[offset] << 16) | (body[offset + 1] << 8) | body[offset + 2];
        offset += 3;
        if (offset + listLen != body.Length)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "TLS 1.3 certificate_list length mismatch.");

        var derChain = new List<byte[]>();
        while (offset < body.Length)
        {
            if (offset + 3 > body.Length)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated CertificateEntry length.");
            int certLen = (body[offset] << 16) | (body[offset + 1] << 8) | body[offset + 2];
            offset += 3;
            if (certLen == 0 || offset + certLen + 2 > body.Length)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid CertificateEntry data.");

            derChain.Add(body.Slice(offset, certLen).ToArray());
            offset += certLen;

            ushort entryExtLen = BinaryPrimitives.ReadUInt16BigEndian(body.Slice(offset, 2));
            offset += 2;
            if (offset + entryExtLen > body.Length)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid CertificateEntry extensions.");
            offset += entryExtLen;
        }

        if (derChain.Count == 0)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Server sent empty Certificate chain.");

        return derChain;
    }

    private static bool VerifyTls13Signature(
        DerCertificate leaf,
        ushort scheme,
        ReadOnlySpan<byte> signedContent,
        ReadOnlySpan<byte> signature)
    {
        switch (scheme)
        {
            case SignatureSchemeId.RsaPssRsaeSha256:
            case SignatureSchemeId.RsaPssRsaeSha384:
            case SignatureSchemeId.RsaPssRsaeSha512:
            {
                if (leaf.PublicKeyAlgorithmOid is not ("1.2.840.113549.1.1.1" or "1.2.840.113549.1.1.10"))
                    return false;
                if (!RsaPrimitives.TryParseRsaPublicKeyDer(leaf.PublicKeyBitString, out byte[] mod, out byte[] exp))
                    return false;
                HashAlgorithmKind hash = scheme switch
                {
                    SignatureSchemeId.RsaPssRsaeSha256 => HashAlgorithmKind.Sha256,
                    SignatureSchemeId.RsaPssRsaeSha384 => HashAlgorithmKind.Sha384,
                    _ => HashAlgorithmKind.Sha512,
                };
                return RsaPrimitives.VerifyPss(mod, exp, hash, signedContent, signature, saltLength: -1);
            }

            case SignatureSchemeId.RsaPssPssSha256:
            case SignatureSchemeId.RsaPssPssSha384:
            case SignatureSchemeId.RsaPssPssSha512:
            {
                if (leaf.PublicKeyAlgorithmOid != "1.2.840.113549.1.1.10")
                    return false;
                if (!RsaPrimitives.TryParseRsaPublicKeyDer(leaf.PublicKeyBitString, out byte[] mod, out byte[] exp))
                    return false;
                HashAlgorithmKind hash = scheme switch
                {
                    SignatureSchemeId.RsaPssPssSha256 => HashAlgorithmKind.Sha256,
                    SignatureSchemeId.RsaPssPssSha384 => HashAlgorithmKind.Sha384,
                    _ => HashAlgorithmKind.Sha512,
                };
                return RsaPrimitives.VerifyPss(mod, exp, hash, signedContent, signature, saltLength: -1);
            }

            case SignatureSchemeId.EcdsaSecp256r1Sha256:
            case SignatureSchemeId.EcdsaSecp384r1Sha384:
            case SignatureSchemeId.EcdsaSecp521r1Sha512:
            {
                if (leaf.PublicKeyAlgorithmOid != "1.2.840.10045.2.1" || string.IsNullOrEmpty(leaf.PublicKeyCurveOid))
                    return false;
                if (!EcPrimitives.TryCurveFromOid(leaf.PublicKeyCurveOid, out EcCurveKind certCurve))
                    return false;

                (EcCurveKind expectedCurve, HashAlgorithmKind hash) = scheme switch
                {
                    SignatureSchemeId.EcdsaSecp256r1Sha256 => (EcCurveKind.P256, HashAlgorithmKind.Sha256),
                    SignatureSchemeId.EcdsaSecp384r1Sha384 => (EcCurveKind.P384, HashAlgorithmKind.Sha384),
                    _ => (EcCurveKind.P521, HashAlgorithmKind.Sha512),
                };

                if (certCurve != expectedCurve)
                    return false;

                return EcPrimitives.VerifyEcdsa(certCurve, leaf.PublicKeyBitString, hash, signedContent, signature);
            }

            case SignatureSchemeId.Ed25519:
            {
                if (leaf.PublicKeyAlgorithmOid != "1.3.101.112" || leaf.PublicKeyBitString.Length != 32 || signature.Length != 64)
                    return false;
                return Ed25519.Verify(leaf.PublicKeyBitString, signedContent, signature);
            }

            default:
                return false;
        }
    }

    private static bool VerifyTls12Signature(
        DerCertificate leaf,
        ushort scheme,
        ReadOnlySpan<byte> signedContent,
        ReadOnlySpan<byte> signature)
    {
        switch (scheme)
        {
            case SignatureSchemeId.RsaPkcs1Sha1:
            case SignatureSchemeId.RsaPkcs1Sha256:
            case SignatureSchemeId.RsaPkcs1Sha384:
            case SignatureSchemeId.RsaPkcs1Sha512:
            {
                if (leaf.PublicKeyAlgorithmOid != "1.2.840.113549.1.1.1")
                    return false;
                if (!RsaPrimitives.TryParseRsaPublicKeyDer(leaf.PublicKeyBitString, out byte[] mod, out byte[] exp))
                    return false;
                HashAlgorithmKind hash = scheme switch
                {
                    SignatureSchemeId.RsaPkcs1Sha1 => HashAlgorithmKind.Sha1,
                    SignatureSchemeId.RsaPkcs1Sha256 => HashAlgorithmKind.Sha256,
                    SignatureSchemeId.RsaPkcs1Sha384 => HashAlgorithmKind.Sha384,
                    _ => HashAlgorithmKind.Sha512,
                };
                return RsaPrimitives.VerifyPkcs1(mod, exp, hash, signedContent, signature);
            }

            case SignatureSchemeId.RsaPssRsaeSha256:
            case SignatureSchemeId.RsaPssRsaeSha384:
            case SignatureSchemeId.RsaPssRsaeSha512:
            case SignatureSchemeId.RsaPssPssSha256:
            case SignatureSchemeId.RsaPssPssSha384:
            case SignatureSchemeId.RsaPssPssSha512:
                return VerifyTls13Signature(leaf, scheme, signedContent, signature);

            case SignatureSchemeId.EcdsaSha1:
            case SignatureSchemeId.EcdsaSecp256r1Sha256:
            case SignatureSchemeId.EcdsaSecp384r1Sha384:
            case SignatureSchemeId.EcdsaSecp521r1Sha512:
            {
                if (leaf.PublicKeyAlgorithmOid != "1.2.840.10045.2.1" || string.IsNullOrEmpty(leaf.PublicKeyCurveOid))
                    return false;
                if (!EcPrimitives.TryCurveFromOid(leaf.PublicKeyCurveOid, out EcCurveKind certCurve))
                    return false;
                HashAlgorithmKind hash = scheme switch
                {
                    SignatureSchemeId.EcdsaSha1 => HashAlgorithmKind.Sha1,
                    SignatureSchemeId.EcdsaSecp256r1Sha256 => HashAlgorithmKind.Sha256,
                    SignatureSchemeId.EcdsaSecp384r1Sha384 => HashAlgorithmKind.Sha384,
                    _ => HashAlgorithmKind.Sha512,
                };
                return EcPrimitives.VerifyEcdsa(certCurve, leaf.PublicKeyBitString, hash, signedContent, signature);
            }

            case SignatureSchemeId.Ed25519:
                return VerifyTls13Signature(leaf, scheme, signedContent, signature);

            default:
                return false;
        }
    }

    private static byte[] EncryptRsaPkcs1(byte[] modulus, byte[] exponent, ReadOnlySpan<byte> data)
    {
        int k = modulus.Length;
        int psLen = k - 3 - data.Length;
        if (psLen < 8)
            throw new TlsAlertException(TlsAlertDescription.BadCertificate, "RSA modulus too small for PKCS#1 pre_master_secret.");

        var em = new byte[k];
        em[0] = 0x00;
        em[1] = 0x02;

        // Generate strictly non-zero padding bytes
        int filled = 0;
        Span<byte> rnd = stackalloc byte[32];
        while (filled < psLen)
        {
            RandomNumberGenerator.Fill(rnd);
            for (int i = 0; i < rnd.Length && filled < psLen; i++)
            {
                if (rnd[i] != 0)
                    em[2 + filled++] = rnd[i];
            }
        }
        rnd.Clear();

        em[2 + psLen] = 0x00;
        data.CopyTo(em.AsSpan(3 + psLen));

        var m = new BigInteger(em, isUnsigned: true, isBigEndian: true);
        var e = new BigInteger(exponent, isUnsigned: true, isBigEndian: true);
        var n = new BigInteger(modulus, isUnsigned: true, isBigEndian: true);
        BigInteger c = BigInteger.ModPow(m, e, n);

        var output = new byte[k];
        int byteCount = c.IsZero ? 0 : c.GetByteCount(isUnsigned: true);
        if (byteCount > 0)
            c.TryWriteBytes(output.AsSpan(k - byteCount), out _, isUnsigned: true, isBigEndian: true);

        ConstantTime.ZeroMemory(em);
        return output;
    }

    private static void ParseExtensionsBlock(ReadOnlySpan<byte> extSpan, Dictionary<ushort, byte[]> target)
    {
        int offset = 0;
        while (offset < extSpan.Length)
        {
            if (offset + 4 > extSpan.Length)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated TLS extension header.");
            ushort type = BinaryPrimitives.ReadUInt16BigEndian(extSpan.Slice(offset, 2));
            ushort len = BinaryPrimitives.ReadUInt16BigEndian(extSpan.Slice(offset + 2, 2));
            offset += 4;
            if (offset + len > extSpan.Length)
                throw new TlsAlertException(TlsAlertDescription.DecodeError, $"Truncated TLS extension 0x{type:X4} payload.");
            if (!target.TryAdd(type, extSpan.Slice(offset, len).ToArray()))
                throw new TlsAlertException(TlsAlertDescription.IllegalParameter, $"Duplicate TLS extension 0x{type:X4}.");
            offset += len;
        }
    }

    private string ParseServerAlpnExtension(ReadOnlySpan<byte> alpnData)
    {
        if (alpnData.Length < 4)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated ALPN extension.");
        ushort listLen = BinaryPrimitives.ReadUInt16BigEndian(alpnData.Slice(0, 2));
        if (2 + listLen != alpnData.Length || listLen < 2)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Invalid ALPN extension list length.");

        byte protoLen = alpnData[2];
        if (protoLen == 0 || 3 + protoLen != alpnData.Length)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Server ALPN must select exactly one non-empty protocol.");

        string selected = Encoding.ASCII.GetString(alpnData.Slice(3, protoLen));
        if (_clientHello!.OfferedAlpn.Count == 0)
            throw new TlsAlertException(TlsAlertDescription.UnsupportedExtension, "Server sent ALPN when client did not offer ALPN.");

        bool found = false;
        for (int i = 0; i < _clientHello.OfferedAlpn.Count; i++)
        {
            if (string.Equals(_clientHello.OfferedAlpn[i], selected, StringComparison.Ordinal))
            {
                found = true;
                break;
            }
        }
        if (!found)
            throw new TlsAlertException(TlsAlertDescription.IllegalParameter, $"Server negotiated unoffered ALPN '{selected}'.");
        return selected;
    }

    private static byte[] DecompressZlibBounded(byte[] compressed, int expectedUncompressedLength)
    {
        try
        {
            using var src = new MemoryStream(compressed, writable: false);
            using var z = new ZLibStream(src, CompressionMode.Decompress);
            return ReadExactBounded(z, expectedUncompressedLength);
        }
        catch (TlsAlertException)
        {
            throw;
        }
        catch (Exception ex)
        {
            throw new TlsAlertException(TlsAlertDescription.BadCertificate, $"Failed to decompress zlib CompressedCertificate: {ex.Message}");
        }
    }

    private static byte[] DecompressBrotliBounded(byte[] compressed, int expectedUncompressedLength)
    {
        try
        {
            using var src = new MemoryStream(compressed, writable: false);
            using var br = new BrotliStream(src, CompressionMode.Decompress);
            return ReadExactBounded(br, expectedUncompressedLength);
        }
        catch (TlsAlertException)
        {
            throw;
        }
        catch (Exception ex)
        {
            throw new TlsAlertException(TlsAlertDescription.BadCertificate, $"Failed to decompress Brotli CompressedCertificate: {ex.Message}");
        }
    }

    private static byte[] DecompressZstdBounded(byte[] compressed, int expectedUncompressedLength)
    {
        var dst = new byte[expectedUncompressedLength];
        try
        {
            using var decompressor = new ZstdSharp.Decompressor();
            if (!decompressor.TryUnwrap(compressed, 0, compressed.Length, dst, 0, dst.Length, out int written) ||
                written != expectedUncompressedLength)
            {
                throw new TlsAlertException(TlsAlertDescription.BadCertificate, "Zstd CompressedCertificate decompression failed or size mismatched.");
            }
            return dst;
        }
        catch (TlsAlertException)
        {
            throw;
        }
        catch (Exception ex)
        {
            throw new TlsAlertException(TlsAlertDescription.BadCertificate, $"Failed to decompress Zstd CompressedCertificate: {ex.Message}");
        }
    }

    private static byte[] ReadExactBounded(Stream decompressor, int expectedLength)
    {
        var dst = new byte[expectedLength];
        int offset = 0;
        while (offset < expectedLength)
        {
            int n = decompressor.Read(dst, offset, expectedLength - offset);
            if (n == 0)
                throw new TlsAlertException(TlsAlertDescription.BadCertificate, "CompressedCertificate stream ended before declared uncompressed_length.");
            offset += n;
        }

        Span<byte> extra = stackalloc byte[1];
        if (decompressor.Read(extra) > 0)
            throw new TlsAlertException(TlsAlertDescription.BadCertificate, "CompressedCertificate exceeded declared uncompressed_length.");

        return dst;
    }

    private static TlsTrafficKeys DeriveTls13TrafficKeys(byte[] secret, CipherSuiteSpec suite)
    {
        byte[] key = HashPrimitives.HkdfExpandLabel(suite.HashAlg, secret, "key", ReadOnlySpan<byte>.Empty, suite.KeyLength);
        byte[] iv = HashPrimitives.HkdfExpandLabel(suite.HashAlg, secret, "iv", ReadOnlySpan<byte>.Empty, 12);
        return new TlsTrafficKeys((byte[])secret.Clone(), key, iv, suite.HashAlg, suite.Id, suite.IsChaCha);
    }

    private static (TlsTrafficKeys ClientWrite, TlsTrafficKeys ServerRead) DeriveTls12TrafficKeys(
        CipherSuiteSpec suite,
        byte[] masterSecret,
        byte[] clientRandom,
        byte[] serverRandom,
        bool encryptThenMac)
    {
        var seed = new byte[64];
        serverRandom.CopyTo(seed, 0);
        clientRandom.CopyTo(seed, 32);

        int macLen = suite.IsCbc ? HashPrimitives.DigestLength(suite.RecordMacAlg) : 0;
        int keyLen = suite.KeyLength;
        int ivLen = suite.IsCbc ? 0 : (suite.IsChaCha ? 12 : 4);
        int totalLen = 2 * macLen + 2 * keyLen + 2 * ivLen;

        byte[] keyBlock = HashPrimitives.Tls12Prf(suite.HashAlg, masterSecret, "key expansion", seed, totalLen);
        try
        {
            int pos = 0;
            byte[] clientMac = keyBlock.AsSpan(pos, macLen).ToArray(); pos += macLen;
            byte[] serverMac = keyBlock.AsSpan(pos, macLen).ToArray(); pos += macLen;
            byte[] clientKey = keyBlock.AsSpan(pos, keyLen).ToArray(); pos += keyLen;
            byte[] serverKey = keyBlock.AsSpan(pos, keyLen).ToArray(); pos += keyLen;
            byte[] clientIv = keyBlock.AsSpan(pos, ivLen).ToArray(); pos += ivLen;
            byte[] serverIv = keyBlock.AsSpan(pos, ivLen).ToArray();

            HashAlgorithmKind recHash = suite.IsCbc ? suite.RecordMacAlg : suite.HashAlg;

            var cw = new TlsTrafficKeys(Array.Empty<byte>(), clientKey, clientIv, recHash, suite.Id, suite.IsChaCha)
            {
                MacKey = suite.IsCbc ? clientMac : null,
                IsCbc = suite.IsCbc,
                EncryptThenMac = suite.IsCbc && encryptThenMac,
            };
            var sr = new TlsTrafficKeys(Array.Empty<byte>(), serverKey, serverIv, recHash, suite.Id, suite.IsChaCha)
            {
                MacKey = suite.IsCbc ? serverMac : null,
                IsCbc = suite.IsCbc,
                EncryptThenMac = suite.IsCbc && encryptThenMac,
            };
            return (cw, sr);
        }
        finally
        {
            ConstantTime.ZeroMemory(keyBlock);
        }
    }

    private void AppendTranscript(ReadOnlySpan<byte> msg)
    {
        if (_transcriptStream.Length + msg.Length > MaxTotalTranscriptBytes)
            throw new TlsAlertException(TlsAlertDescription.InternalError, "TLS handshake transcript exceeded maximum allowed size.");
        _transcriptStream.Write(msg);
    }

    private void ResetTranscript(ReadOnlySpan<byte> prefix)
    {
        _transcriptStream.SetLength(0);
        _transcriptStream.Position = 0;
        _transcriptStream.Write(prefix);
    }

    private byte[] ComputeTranscriptHash(HashAlgorithmKind alg)
    {
        ReadOnlySpan<byte> buf = _transcriptStream.GetBuffer().AsSpan(0, (int)_transcriptStream.Length);
        return HashPrimitives.Hash(alg, buf);
    }

    private void EmitKeyLog(string label, ReadOnlySpan<byte> secret)
    {
        if (_options.KeyLogSink is null || _clientHello is null)
            return;

        string line = $"{label} {Convert.ToHexString(_clientHello.ClientRandom).ToLowerInvariant()} {Convert.ToHexString(secret).ToLowerInvariant()}";
        _options.KeyLogSink(line);
    }

    private void ThrowIfDisposed() => ObjectDisposedException.ThrowIf(_disposed, this);

    public void Dispose()
    {
        if (_disposed)
            return;

        foreach (AsymmetricKeyShareState ks in _ownedKeyShares.Values)
            ks.Dispose();
        _ownedKeyShares.Clear();
        _clientHello?.Dispose();

        if (_handshakeSecret is not null) ConstantTime.ZeroMemory(_handshakeSecret);
        if (_clientHandshakeTrafficSecret is not null) ConstantTime.ZeroMemory(_clientHandshakeTrafficSecret);
        if (_serverHandshakeTrafficSecret is not null) ConstantTime.ZeroMemory(_serverHandshakeTrafficSecret);
        if (_clientAppTrafficSecret is not null) ConstantTime.ZeroMemory(_clientAppTrafficSecret);
        if (_serverAppTrafficSecret is not null) ConstantTime.ZeroMemory(_serverAppTrafficSecret);
        if (_exporterMasterSecret is not null) ConstantTime.ZeroMemory(_exporterMasterSecret);
        if (_resumptionMasterSecret is not null) ConstantTime.ZeroMemory(_resumptionMasterSecret);
        if (_clientEarlyTrafficSecret is not null) ConstantTime.ZeroMemory(_clientEarlyTrafficSecret);
        if (_tls12PreMasterSecret is not null) ConstantTime.ZeroMemory(_tls12PreMasterSecret);
        if (_tls12MasterSecret is not null) ConstantTime.ZeroMemory(_tls12MasterSecret);
        _tls12PendingReadKeys?.Clear();

        _transcriptStream.Dispose();
        _disposed = true;
    }

    private sealed class QuicStepAccumulator
    {
        public readonly List<byte> InitialOutbound = new();
        public readonly List<byte> HandshakeOutbound = new();
        public TlsTrafficKeys? HandshakeReadKeys;
        public TlsTrafficKeys? HandshakeWriteKeys;
        public TlsTrafficKeys? ApplicationReadKeys;
        public TlsTrafficKeys? ApplicationWriteKeys;
    }

    private sealed record CipherSuiteSpec(
        ushort Id,
        bool IsTls13,
        HashAlgorithmKind HashAlg,
        int KeyLength,
        bool IsChaCha,
        bool IsCbc,
        bool UsesEcdhe,
        HashAlgorithmKind RecordMacAlg);

    private static bool TryGetCipherSuiteSpec(ushort id, out CipherSuiteSpec? spec)
    {
        spec = id switch
        {
            // TLS 1.3
            CipherSuiteId.TLS_AES_128_GCM_SHA256 => new(id, true, HashAlgorithmKind.Sha256, 16, false, false, true, HashAlgorithmKind.Sha256),
            CipherSuiteId.TLS_AES_256_GCM_SHA384 => new(id, true, HashAlgorithmKind.Sha384, 32, false, false, true, HashAlgorithmKind.Sha384),
            CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256 => new(id, true, HashAlgorithmKind.Sha256, 32, true, false, true, HashAlgorithmKind.Sha256),

            // TLS 1.2 ECDHE AEAD
            CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 => new(id, false, HashAlgorithmKind.Sha256, 16, false, false, true, HashAlgorithmKind.Sha256),
            CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 => new(id, false, HashAlgorithmKind.Sha256, 16, false, false, true, HashAlgorithmKind.Sha256),
            CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 => new(id, false, HashAlgorithmKind.Sha384, 32, false, false, true, HashAlgorithmKind.Sha384),
            CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 => new(id, false, HashAlgorithmKind.Sha384, 32, false, false, true, HashAlgorithmKind.Sha384),
            CipherSuiteId.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256 => new(id, false, HashAlgorithmKind.Sha256, 32, true, false, true, HashAlgorithmKind.Sha256),
            CipherSuiteId.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256 => new(id, false, HashAlgorithmKind.Sha256, 32, true, false, true, HashAlgorithmKind.Sha256),

            // TLS 1.2 ECDHE CBC
            CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA => new(id, false, HashAlgorithmKind.Sha256, 16, false, true, true, HashAlgorithmKind.Sha1),
            CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA => new(id, false, HashAlgorithmKind.Sha256, 32, false, true, true, HashAlgorithmKind.Sha1),
            CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA => new(id, false, HashAlgorithmKind.Sha256, 16, false, true, true, HashAlgorithmKind.Sha1),
            CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA => new(id, false, HashAlgorithmKind.Sha256, 32, false, true, true, HashAlgorithmKind.Sha1),
            CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256 => new(id, false, HashAlgorithmKind.Sha256, 16, false, true, true, HashAlgorithmKind.Sha256),
            CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384 => new(id, false, HashAlgorithmKind.Sha384, 32, false, true, true, HashAlgorithmKind.Sha384),
            CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256 => new(id, false, HashAlgorithmKind.Sha256, 16, false, true, true, HashAlgorithmKind.Sha256),
            CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384 => new(id, false, HashAlgorithmKind.Sha384, 32, false, true, true, HashAlgorithmKind.Sha384),

            // TLS 1.2 RSA key exchange
            CipherSuiteId.TLS_RSA_WITH_AES_128_GCM_SHA256 => new(id, false, HashAlgorithmKind.Sha256, 16, false, false, false, HashAlgorithmKind.Sha256),
            CipherSuiteId.TLS_RSA_WITH_AES_256_GCM_SHA384 => new(id, false, HashAlgorithmKind.Sha384, 32, false, false, false, HashAlgorithmKind.Sha384),
            CipherSuiteId.TLS_RSA_WITH_AES_128_CBC_SHA => new(id, false, HashAlgorithmKind.Sha256, 16, false, true, false, HashAlgorithmKind.Sha1),
            CipherSuiteId.TLS_RSA_WITH_AES_256_CBC_SHA => new(id, false, HashAlgorithmKind.Sha256, 32, false, true, false, HashAlgorithmKind.Sha1),

            _ => null,
        };
        return spec is not null;
    }
}
