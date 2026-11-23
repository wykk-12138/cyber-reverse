using System.Buffers;
using System.Buffers.Binary;
using Cybersole.Http.Profiles;
using Cybersole.Http.X509;

namespace Cybersole.Http.Tls;

/// <summary>
/// TLS specification used when tunneling HTTP CONNECT over an <c>https://</c> proxy
/// (<c>ProxyTlsSpec</c> at <c>0x1412C33A0</c> in <c>cybersole_http_architecture.md</c> §3.1).
/// </summary>
public static class ProxyTlsSpec
{
    private static readonly IReadOnlyList<ushort> ProxyCiphers = Array.AsReadOnly(new ushort[]
    {
        CipherSuiteId.TLS_AES_128_GCM_SHA256,
        CipherSuiteId.TLS_AES_256_GCM_SHA384,
        CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256,
        CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
        CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
        CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
        CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
        CipherSuiteId.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256,
    });

    private static readonly IReadOnlyList<ushort> ProxyGroups = Array.AsReadOnly(new ushort[]
    {
        NamedGroupId.X25519,
        NamedGroupId.Secp256r1,
        NamedGroupId.Secp384r1,
    });

    private static readonly IReadOnlyList<KeyShareEntry> ProxyKeyShares = Array.AsReadOnly(new[]
    {
        new KeyShareEntry(NamedGroupId.X25519, InitLength: 0),
    });

    private static readonly IReadOnlyList<string> ProxyAlpn = Array.AsReadOnly(new[] { "http/1.1" });
    private static readonly IReadOnlyList<byte> ProxyEcPointFormats = Array.AsReadOnly(new byte[] { 0 });
    private static readonly IReadOnlyList<byte> ProxyPskModes = Array.AsReadOnly(new byte[] { 1 });
    private static readonly IReadOnlyList<ushort> ProxyVersions = Array.AsReadOnly(new ushort[]
    {
        TlsVersion.Tls13,
        TlsVersion.Tls12,
    });

    private static readonly IReadOnlyList<ushort> ProxySignatureAlgorithms = Array.AsReadOnly(new ushort[]
    {
        SignatureSchemeId.EcdsaSecp256r1Sha256,
        SignatureSchemeId.RsaPssRsaeSha256,
        SignatureSchemeId.RsaPkcs1Sha256,
        SignatureSchemeId.EcdsaSecp384r1Sha384,
        SignatureSchemeId.RsaPssRsaeSha384,
        SignatureSchemeId.RsaPkcs1Sha384,
        SignatureSchemeId.RsaPssRsaeSha512,
        SignatureSchemeId.RsaPkcs1Sha512,
    });

    public static ClientHelloSpec CreateClientHelloSpec() => new(
        CipherSuites: ProxyCiphers,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            new SniExtension(),                                              // 0
            new StatusRequestExtension(),                                    // 5
            new SupportedGroupsExtension(ProxyGroups),                       // 10
            new EcPointFormatsExtension(ProxyEcPointFormats),                // 11
            new SignatureAlgorithmsExtension(ProxySignatureAlgorithms),      // 13
            new RenegotiationInfoExtension(1),                               // 65281 (0xFF01)
            new AlpnExtension(ProxyAlpn),                                    // 16
            new SignedCertificateTimestampExtension(),                       // 18
            new ExtendedMasterSecretExtension(),                             // 23
            new SupportedVersionsExtension(ProxyVersions),                   // 43
            new PskKeyExchangeModesExtension(ProxyPskModes),                 // 45
            new KeyShareExtension(ProxyKeyShares),                           // 51
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    public static ClientProfile Profile { get; } = new(
        Name: "proxy_tls",
        SlotIndex: -1,
        CreateClientHelloSpec: CreateClientHelloSpec,
        Http2Settings: new Http2SettingsSpec(
            Array.AsReadOnly(Array.Empty<(ushort Id, uint Value)>()),
            Http2SettingsSpec.DefaultConnectionFlow,
            Http2SettingsSpec.DefaultFallbackPseudoHeaderOrder),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: true);

    public static TlsConnectionOptions CreateConnectionOptions(
        string serverName,
        int port = 443,
        CertificateVerifyOptions? verifyOptions = null,
        TimeSpan? handshakeTimeout = null) => new()
    {
        ServerName = serverName,
        Port = port,
        Profile = Profile,
        VerifyOptions = verifyOptions,
        HandshakeTimeout = handshakeTimeout ?? TimeSpan.FromSeconds(15),
        ForceHttp11 = true,
    };
}

/// <summary>
/// Explicit TLS connection options consumed by <see cref="TlsStream"/>, Phase 3 dialers,
/// and Phase 4 <c>TlsClientCache</c>.
/// </summary>
public sealed record TlsConnectionOptions
{
    public required string ServerName { get; init; }
    public int Port { get; init; } = 443;
    public ClientProfile? Profile { get; init; }
    public ClientHelloSpec? SpecOverride { get; init; }
    public IReadOnlyList<string>? AlpnOverride { get; init; }
    public CertificateVerifyOptions? VerifyOptions { get; init; }
    public LruTlsSessionCache? SessionCache { get; init; }
    public TimeSpan HandshakeTimeout { get; init; } = TimeSpan.FromSeconds(15);
    public bool ForceHttp11 { get; init; }
    public bool RandomExtensionOrder { get; init; }
    public bool DisableSessionTickets { get; init; }
    public bool LeaveInnerStreamOpen { get; init; }
    public Action<string>? KeyLogSink { get; init; }
    public Random? Random { get; init; }
    public DateTimeOffset? NowUtc { get; init; }
}

/// <summary>
/// Pure managed TLS 1.2 &amp; TLS 1.3 <see cref="Stream"/> wrapping any underlying transport stream.
/// Handles async handshake, transparent post-handshake <c>NewSessionTicket</c>/<c>KeyUpdate</c>,
/// record coalescing (up to 4 records / 73,748B buffer), and graceful <c>close_notify</c> shutdown.
/// </summary>
public sealed class TlsStream : Stream
{
    private const int WriteBufferCapacity = 73_748;
    private const int MaxCoalescedRecords = 4;

    private readonly Stream _innerStream;
    private readonly TlsConnectionOptions _options;
    private readonly TlsRecordLayer _recordLayer;
    private readonly TlsHandshakeEngine _engine;
    private readonly SemaphoreSlim _readLock = new(1, 1);
    private readonly SemaphoreSlim _writeLock = new(1, 1);

    private byte[]? _decryptedBuffer;
    private int _decryptedOffset;
    private int _decryptedCount;
    private bool _receivedCloseNotify;
    private bool _sentCloseNotify;
    private bool _disposed;

    public TlsStream(Stream innerStream, TlsConnectionOptions options)
    {
        _innerStream = innerStream ?? throw new ArgumentNullException(nameof(innerStream));
        _options = options ?? throw new ArgumentNullException(nameof(options));

        _recordLayer = new TlsRecordLayer();
        _engine = new TlsHandshakeEngine(new TlsHandshakeOptions
        {
            ServerName = options.ServerName,
            Port = options.Port,
            Profile = options.Profile ?? ProfileRegistry.GetOrDefault(null),
            SpecOverride = options.SpecOverride,
            AlpnOverride = options.AlpnOverride,
            VerifyOptions = options.VerifyOptions,
            SessionCache = options.SessionCache,
            ForceHttp11 = options.ForceHttp11,
            RandomExtensionOrder = options.RandomExtensionOrder,
            DisableSessionTickets = options.DisableSessionTickets,
            KeyLogSink = options.KeyLogSink,
            Random = options.Random,
            NowUtc = options.NowUtc,
        });
    }

    public ushort NegotiatedVersion => _engine.NegotiatedVersion;
    public ushort NegotiatedCipherSuite => _engine.NegotiatedCipherSuite;
    public string? NegotiatedAlpn => _engine.NegotiatedAlpn;
    public IReadOnlyList<DerCertificate>? PeerCertificates => _engine.PeerCertificates;
    public DerCertificate? LeafCertificate => _engine.LeafCertificate;
    public bool UsedSessionResumption => _engine.UsedSessionResumption;
    public bool ExtendedMasterSecretUsed => _engine.ExtendedMasterSecretUsed;
    public bool HandshakeCompleted => _engine.HandshakeCompleted;
    public TlsHandshakeState HandshakeState => _engine.State;
    public long HandshakeBytesSent => _engine.HandshakeBytesSent;
    public long HandshakeBytesReceived => _engine.HandshakeBytesReceived;

    public override bool CanRead => !_disposed && _innerStream.CanRead;
    public override bool CanSeek => false;
    public override bool CanWrite => !_disposed && _innerStream.CanWrite;
    public override long Length => throw new NotSupportedException();
    public override long Position
    {
        get => throw new NotSupportedException();
        set => throw new NotSupportedException();
    }

    public async Task HandshakeAsync(CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        if (_engine.HandshakeCompleted)
            return;

        using CancellationTokenSource? timeoutCts =
            _options.HandshakeTimeout > TimeSpan.Zero && _options.HandshakeTimeout != Timeout.InfiniteTimeSpan
                ? new CancellationTokenSource(_options.HandshakeTimeout)
                : null;
        using CancellationTokenSource? linkedCts = timeoutCts is not null
            ? CancellationTokenSource.CreateLinkedTokenSource(cancellationToken, timeoutCts.Token)
            : null;
        CancellationToken effectiveCt = linkedCts?.Token ?? cancellationToken;

        try
        {
            byte[] clientHelloRecord = _engine.StartTcpHandshake();
            await _innerStream.WriteAsync(clientHelloRecord, effectiveCt).ConfigureAwait(false);
            await _innerStream.FlushAsync(effectiveCt).ConfigureAwait(false);

            while (!_engine.HandshakeCompleted)
            {
                (byte[] Header, byte[] Payload)? rawRecord = await ReadRawRecordAsync(effectiveCt).ConfigureAwait(false);
                if (rawRecord is null)
                    throw new EndOfStreamException("Connection closed unexpectedly during TLS handshake.");

                byte[] decrypted = _recordLayer.DecryptRecord(
                    rawRecord.Value.Header,
                    rawRecord.Value.Payload,
                    out TlsContentType innerType);

                List<TcpStepOperation> ops = _engine.ProcessTcpRecord(innerType, decrypted);
                await ExecuteStepOperationsAsync(ops, effectiveCt).ConfigureAwait(false);
            }
        }
        catch (OperationCanceledException) when (timeoutCts is not null && timeoutCts.IsCancellationRequested && !cancellationToken.IsCancellationRequested)
        {
            throw new TimeoutException($"TLS handshake timed out after {_options.HandshakeTimeout.TotalSeconds:0.###}s.");
        }
    }

    public async Task ShutdownAsync(CancellationToken cancellationToken = default)
    {
        if (_disposed)
            return;

        await _writeLock.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            if (!_sentCloseNotify && _engine.HandshakeCompleted && !_disposed)
            {
                _sentCloseNotify = true;
                byte[] alertRecord = _recordLayer.ProtectSingleRecord(TlsContentType.Alert, new byte[] { 0x01, 0x00 });
                await _innerStream.WriteAsync(alertRecord, cancellationToken).ConfigureAwait(false);
                await _innerStream.FlushAsync(cancellationToken).ConfigureAwait(false);
            }
        }
        finally
        {
            _writeLock.Release();
        }
    }

    public override void Flush() => _innerStream.Flush();

    public override Task FlushAsync(CancellationToken cancellationToken) => _innerStream.FlushAsync(cancellationToken);

    public override int Read(byte[] buffer, int offset, int count)
    {
        ValidateBufferArguments(buffer, offset, count);
        return ReadAsync(buffer.AsMemory(offset, count), CancellationToken.None).AsTask().GetAwaiter().GetResult();
    }

    public override int Read(Span<byte> buffer)
    {
        byte[] rented = ArrayPool<byte>.Shared.Rent(buffer.Length);
        try
        {
            int n = ReadAsync(rented.AsMemory(0, buffer.Length), CancellationToken.None).AsTask().GetAwaiter().GetResult();
            if (n > 0)
                rented.AsSpan(0, n).CopyTo(buffer);
            return n;
        }
        finally
        {
            ArrayPool<byte>.Shared.Return(rented);
        }
    }

    public override Task<int> ReadAsync(byte[] buffer, int offset, int count, CancellationToken cancellationToken)
    {
        ValidateBufferArguments(buffer, offset, count);
        return ReadAsync(buffer.AsMemory(offset, count), cancellationToken).AsTask();
    }

    public override async ValueTask<int> ReadAsync(Memory<byte> buffer, CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        if (!_engine.HandshakeCompleted)
            throw new InvalidOperationException("TLS handshake must complete before reading application data.");
        if (buffer.IsEmpty)
            return 0;

        await _readLock.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            if (_decryptedOffset < _decryptedCount && _decryptedBuffer is not null)
            {
                int avail = _decryptedCount - _decryptedOffset;
                int take = Math.Min(avail, buffer.Length);
                _decryptedBuffer.AsSpan(_decryptedOffset, take).CopyTo(buffer.Span);
                _decryptedOffset += take;
                if (_decryptedOffset == _decryptedCount)
                {
                    _decryptedOffset = 0;
                    _decryptedCount = 0;
                }
                return take;
            }

            if (_receivedCloseNotify)
                return 0;

            while (true)
            {
                (byte[] Header, byte[] Payload)? rawRecord = await ReadRawRecordAsync(cancellationToken).ConfigureAwait(false);
                if (rawRecord is null)
                    return 0;

                byte[] decrypted = _recordLayer.DecryptRecord(
                    rawRecord.Value.Header,
                    rawRecord.Value.Payload,
                    out TlsContentType innerType);

                switch (innerType)
                {
                    case TlsContentType.ApplicationData:
                    {
                        if (decrypted.Length == 0)
                            continue;

                        int take = Math.Min(decrypted.Length, buffer.Length);
                        decrypted.AsSpan(0, take).CopyTo(buffer.Span);
                        if (take < decrypted.Length)
                        {
                            int rem = decrypted.Length - take;
                            EnsureDecryptedBuffer(rem);
                            decrypted.AsSpan(take, rem).CopyTo(_decryptedBuffer!);
                            _decryptedOffset = 0;
                            _decryptedCount = rem;
                        }
                        return take;
                    }

                    case TlsContentType.Handshake:
                    {
                        await _writeLock.WaitAsync(cancellationToken).ConfigureAwait(false);
                        try
                        {
                            List<TcpStepOperation> ops = _engine.ProcessPostHandshake(decrypted);
                            await ExecuteStepOperationsAsync(ops, cancellationToken).ConfigureAwait(false);
                        }
                        finally
                        {
                            _writeLock.Release();
                        }
                        break;
                    }

                    case TlsContentType.Alert:
                    {
                        if (decrypted.Length < 2)
                            throw new TlsAlertException(TlsAlertDescription.DecodeError, "Truncated TLS alert record.");
                        var level = (TlsAlertLevel)decrypted[0];
                        var desc = (TlsAlertDescription)decrypted[1];
                        if (desc == TlsAlertDescription.CloseNotify)
                        {
                            _receivedCloseNotify = true;
                            return 0;
                        }
                        throw new TlsAlertException(desc, $"Peer sent TLS alert: {desc} ({(byte)desc})", isLocal: false, level: level);
                    }

                    case TlsContentType.ChangeCipherSpec:
                        if (_engine.NegotiatedVersion != TlsVersion.Tls13)
                            throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, "Unexpected ChangeCipherSpec on established TLS 1.2 stream.");
                        break;

                    default:
                        throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Unexpected TLS content type {innerType}.");
                }
            }
        }
        finally
        {
            _readLock.Release();
        }
    }

    public override void Write(byte[] buffer, int offset, int count)
    {
        ValidateBufferArguments(buffer, offset, count);
        WriteAsync(buffer.AsMemory(offset, count), CancellationToken.None).AsTask().GetAwaiter().GetResult();
    }

    public override void Write(ReadOnlySpan<byte> buffer)
    {
        byte[] copy = buffer.ToArray();
        WriteAsync(copy.AsMemory(), CancellationToken.None).AsTask().GetAwaiter().GetResult();
    }

    public override Task WriteAsync(byte[] buffer, int offset, int count, CancellationToken cancellationToken)
    {
        ValidateBufferArguments(buffer, offset, count);
        return WriteAsync(buffer.AsMemory(offset, count), cancellationToken).AsTask();
    }

    public override async ValueTask WriteAsync(ReadOnlyMemory<byte> buffer, CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        if (!_engine.HandshakeCompleted)
            throw new InvalidOperationException("TLS handshake must complete before writing application data.");
        if (_sentCloseNotify)
            throw new InvalidOperationException("Cannot write after TLS close_notify has been sent.");
        if (buffer.IsEmpty)
            return;

        await _writeLock.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            List<byte[]> records = _recordLayer.ProtectRecords(TlsContentType.ApplicationData, buffer.Span);
            await WriteCoalescedRecordsAsync(records, cancellationToken).ConfigureAwait(false);
        }
        finally
        {
            _writeLock.Release();
        }
    }

    public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
    public override void SetLength(long value) => throw new NotSupportedException();

    private async Task ExecuteStepOperationsAsync(List<TcpStepOperation> ops, CancellationToken cancellationToken)
    {
        if (ops.Count == 0)
            return;

        List<byte[]>? outboundBatch = null;
        for (int i = 0; i < ops.Count; i++)
        {
            TcpStepOperation op = ops[i];
            switch (op.Kind)
            {
                case TcpStepOperationKind.SendPlaintextRecord:
                    outboundBatch ??= new List<byte[]>(4);
                    outboundBatch.Add(_recordLayer.ProtectSingleRecord(
                        op.ContentType,
                        op.Payload ?? Array.Empty<byte>(),
                        op.RecordVersion));
                    break;

                case TcpStepOperationKind.SendProtectedRecord:
                    outboundBatch ??= new List<byte[]>(4);
                    List<byte[]> protectedRecs = _recordLayer.ProtectRecords(op.ContentType, op.Payload ?? Array.Empty<byte>());
                    outboundBatch.AddRange(protectedRecs);
                    break;

                case TcpStepOperationKind.InstallReadKeys:
                    _recordLayer.SetReadKeys(op.Keys!, op.IsTls13);
                    break;

                case TcpStepOperationKind.InstallWriteKeys:
                    _recordLayer.SetWriteKeys(op.Keys!, op.IsTls13);
                    break;

                case TcpStepOperationKind.SetMaxPlaintextFragment:
                    _recordLayer.MaxOutboundPlaintextFragment = op.MaxPlaintextFragment;
                    break;

                case TcpStepOperationKind.MarkHandshakeCompleted:
                    _recordLayer.MarkHandshakeCompleted();
                    break;
            }
        }

        if (outboundBatch is { Count: > 0 })
        {
            await WriteCoalescedRecordsAsync(outboundBatch, cancellationToken).ConfigureAwait(false);
            await _innerStream.FlushAsync(cancellationToken).ConfigureAwait(false);
        }
    }

    private async Task WriteCoalescedRecordsAsync(List<byte[]> records, CancellationToken cancellationToken)
    {
        int idx = 0;
        while (idx < records.Count)
        {
            int batchCount = 0;
            int totalBytes = 0;
            while (idx + batchCount < records.Count && batchCount < MaxCoalescedRecords)
            {
                int nextLen = records[idx + batchCount].Length;
                if (batchCount > 0 && totalBytes + nextLen > WriteBufferCapacity)
                    break;
                totalBytes += nextLen;
                batchCount++;
            }

            if (batchCount == 1)
            {
                await _innerStream.WriteAsync(records[idx], cancellationToken).ConfigureAwait(false);
            }
            else
            {
                byte[] rented = ArrayPool<byte>.Shared.Rent(totalBytes);
                try
                {
                    int offset = 0;
                    for (int k = 0; k < batchCount; k++)
                    {
                        byte[] rec = records[idx + k];
                        rec.CopyTo(rented, offset);
                        offset += rec.Length;
                    }
                    await _innerStream.WriteAsync(rented.AsMemory(0, totalBytes), cancellationToken).ConfigureAwait(false);
                }
                finally
                {
                    ArrayPool<byte>.Shared.Return(rented);
                }
            }

            idx += batchCount;
        }
    }

    private async Task<(byte[] Header, byte[] Payload)?> ReadRawRecordAsync(CancellationToken cancellationToken)
    {
        var header = new byte[5];
        int headerRead = 0;
        while (headerRead < 5)
        {
            int n = await _innerStream.ReadAsync(header.AsMemory(headerRead, 5 - headerRead), cancellationToken).ConfigureAwait(false);
            if (n == 0)
            {
                if (headerRead == 0)
                    return null;
                throw new EndOfStreamException("Unexpected EOF while reading TLS record header.");
            }
            headerRead += n;
        }

        TlsRecordLayer.ValidateRecordHeader(
            header,
            _recordLayer.HasReadCipher,
            _engine.NegotiatedVersion == TlsVersion.Tls13,
            out _,
            out int payloadLength);

        var payload = new byte[payloadLength];
        int offset = 0;
        while (offset < payloadLength)
        {
            int n = await _innerStream.ReadAsync(payload.AsMemory(offset, payloadLength - offset), cancellationToken).ConfigureAwait(false);
            if (n == 0)
                throw new EndOfStreamException("Unexpected EOF while reading TLS record payload.");
            offset += n;
        }

        return (header, payload);
    }

    private void EnsureDecryptedBuffer(int required)
    {
        if (_decryptedBuffer is null || _decryptedBuffer.Length < required)
            _decryptedBuffer = new byte[Math.Max(required, TlsRecordLayer.MaxPlaintextFragment)];
    }

    public override async ValueTask DisposeAsync()
    {
        if (_disposed)
            return;

        try
        {
            await ShutdownAsync(CancellationToken.None).ConfigureAwait(false);
        }
        catch
        {
            // Best-effort close_notify during disposal.
        }

        CleanupResources();
        if (!_options.LeaveInnerStreamOpen)
            await _innerStream.DisposeAsync().ConfigureAwait(false);

        await base.DisposeAsync().ConfigureAwait(false);
    }

    protected override void Dispose(bool disposing)
    {
        if (_disposed)
            return;

        if (disposing)
        {
            CleanupResources();
            if (!_options.LeaveInnerStreamOpen)
                _innerStream.Dispose();
        }

        base.Dispose(disposing);
    }

    private void CleanupResources()
    {
        _disposed = true;
        if (_decryptedBuffer is not null)
            Array.Clear(_decryptedBuffer);
        _engine.Dispose();
        _recordLayer.Dispose();
        _readLock.Dispose();
        _writeLock.Dispose();
    }
}
