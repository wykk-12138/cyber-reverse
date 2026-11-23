using System.Buffers.Binary;
using System.Collections.Concurrent;
using System.Diagnostics;
using System.Net;
using System.Security.Cryptography;
using System.Threading.Channels;
using Cybersole.Http.Crypto;
using Cybersole.Http.Profiles;
using Cybersole.Http.Protocol;
using Cybersole.Http.Tls;
using Cybersole.Http.X509;

namespace Cybersole.Http.Quic;

/// <summary>Configuration options for dialing a <see cref="QuicConnection"/>.</summary>
public sealed class QuicConnectionOptions
{
    public required string Host { get; init; }
    public int Port { get; init; } = 443;
    public ClientProfile Profile { get; init; } = ProfileRegistry.GetOrDefault(null);
    public QuicTransportSpec? TransportSpec { get; init; }
    public ProxySpec? Proxy { get; init; }
    public CertificateVerifyOptions? VerifyOptions { get; init; }
    public LruTlsSessionCache? SessionCache { get; init; }
    public TimeSpan ConnectTimeout { get; init; } = TimeSpan.FromSeconds(10);
    public TimeSpan MaxIdleTimeout { get; init; } = TimeSpan.FromSeconds(30);
    public bool UseChaosInitialFrames { get; init; } = true;
    public int MaxDatagramPayload { get; init; } = 1250;
    public bool RandomExtensionOrder { get; init; }
    public bool DisableSessionTickets { get; init; }
    public Action<string>? KeyLogSink { get; init; }
    public IQuicDatagramTransport? TransportOverride { get; init; }
    public ulong? InitialRttUs { get; init; }
    public Random? Random { get; init; }
}

public enum QuicLongPacketType : byte
{
    Initial = 0,
    ZeroRtt = 1,
    Handshake = 2,
    Retry = 3,
}

/// <summary>
/// RFC 9000 §17 QUIC v1 packet header serializer/parser supporting Long Header,
/// Short Header (1-RTT), Retry, Version Negotiation, and coalesced UDP datagrams.
/// </summary>
public static class QuicPacketCodec
{
    public static byte[] BuildLongHeaderPacket(
        QuicLongPacketType type,
        ReadOnlySpan<byte> dcid,
        ReadOnlySpan<byte> scid,
        ReadOnlySpan<byte> token,
        ulong packetNumber,
        int pnLength,
        ReadOnlySpan<byte> plaintextFrames,
        QuicKeySet writeKeys)
    {
        if (pnLength is < 1 or > 4)
            throw new ArgumentOutOfRangeException(nameof(pnLength));

        // RFC 9001 §5.4.2 requires at least 4 - pnLength bytes of ciphertext before tag for 16B HP sample.
        int minPlaintext = Math.Max(0, 4 - pnLength);
        int paddedPlaintextLen = Math.Max(plaintextFrames.Length, minPlaintext);
        int payloadWithTagLen = pnLength + paddedPlaintextLen + QuicKeySet.AeadTagLength;

        int headerBaseLen = 1 + 4 + 1 + dcid.Length + 1 + scid.Length
            + (type == QuicLongPacketType.Initial ? QuicVarInt.GetEncodedLength((ulong)token.Length) + token.Length : 0)
            + QuicVarInt.GetEncodedLength((ulong)payloadWithTagLen);

        int pnOffset = headerBaseLen;
        int headerLen = pnOffset + pnLength;
        var packet = new byte[headerLen + paddedPlaintextLen + QuicKeySet.AeadTagLength];

        packet[0] = (byte)(0xC0 | ((int)type << 4) | (pnLength - 1));
        BinaryPrimitives.WriteUInt32BigEndian(packet.AsSpan(1, 4), QuicCrypto.QuicVersion1);
        int off = 5;
        packet[off++] = (byte)dcid.Length;
        dcid.CopyTo(packet.AsSpan(off));
        off += dcid.Length;
        packet[off++] = (byte)scid.Length;
        scid.CopyTo(packet.AsSpan(off));
        off += scid.Length;

        if (type == QuicLongPacketType.Initial)
        {
            off += QuicVarInt.Encode((ulong)token.Length, packet.AsSpan(off));
            if (!token.IsEmpty)
            {
                token.CopyTo(packet.AsSpan(off));
                off += token.Length;
            }
        }

        off += QuicVarInt.Encode((ulong)payloadWithTagLen, packet.AsSpan(off));
        WritePacketNumber(packet.AsSpan(pnOffset, pnLength), packetNumber, pnLength);

        byte[] paddedPlaintext;
        if (paddedPlaintextLen == plaintextFrames.Length)
        {
            paddedPlaintext = plaintextFrames.ToArray();
        }
        else
        {
            paddedPlaintext = new byte[paddedPlaintextLen];
            plaintextFrames.CopyTo(paddedPlaintext);
        }

        writeKeys.PacketProtect(
            packetNumber,
            packet.AsSpan(0, headerLen),
            paddedPlaintext,
            packet.AsSpan(headerLen));

        writeKeys.ApplyHeaderProtection(packet, pnOffset, pnLength);
        return packet;
    }

    public static byte[] BuildShortHeaderPacket(
        ReadOnlySpan<byte> dcid,
        ulong packetNumber,
        int pnLength,
        bool keyPhase,
        ReadOnlySpan<byte> plaintextFrames,
        QuicKeySet writeKeys)
    {
        if (pnLength is < 1 or > 4)
            throw new ArgumentOutOfRangeException(nameof(pnLength));

        int minPlaintext = Math.Max(0, 4 - pnLength);
        int paddedPlaintextLen = Math.Max(plaintextFrames.Length, minPlaintext);
        int pnOffset = 1 + dcid.Length;
        int headerLen = pnOffset + pnLength;
        var packet = new byte[headerLen + paddedPlaintextLen + QuicKeySet.AeadTagLength];

        packet[0] = (byte)(0x40 | (keyPhase ? 0x04 : 0x00) | (pnLength - 1));
        dcid.CopyTo(packet.AsSpan(1));
        WritePacketNumber(packet.AsSpan(pnOffset, pnLength), packetNumber, pnLength);

        byte[] paddedPlaintext;
        if (paddedPlaintextLen == plaintextFrames.Length)
        {
            paddedPlaintext = plaintextFrames.ToArray();
        }
        else
        {
            paddedPlaintext = new byte[paddedPlaintextLen];
            plaintextFrames.CopyTo(paddedPlaintext);
        }

        writeKeys.PacketProtect(
            packetNumber,
            packet.AsSpan(0, headerLen),
            paddedPlaintext,
            packet.AsSpan(headerLen));

        writeKeys.ApplyHeaderProtection(packet, pnOffset, pnLength);
        return packet;
    }

    public static byte[] BuildRetryPacket(
        ReadOnlySpan<byte> originalDcid,
        ReadOnlySpan<byte> dcid,
        ReadOnlySpan<byte> scid,
        ReadOnlySpan<byte> retryToken,
        byte unusedBits = 0x0F)
    {
        int bodyLen = 1 + 4 + 1 + dcid.Length + 1 + scid.Length + retryToken.Length;
        var packet = new byte[bodyLen + QuicKeySet.AeadTagLength];
        packet[0] = (byte)(0xF0 | (unusedBits & 0x0F));
        BinaryPrimitives.WriteUInt32BigEndian(packet.AsSpan(1, 4), QuicCrypto.QuicVersion1);
        int off = 5;
        packet[off++] = (byte)dcid.Length;
        dcid.CopyTo(packet.AsSpan(off));
        off += dcid.Length;
        packet[off++] = (byte)scid.Length;
        scid.CopyTo(packet.AsSpan(off));
        off += scid.Length;
        retryToken.CopyTo(packet.AsSpan(off));

        QuicCrypto.ComputeRetryIntegrityTag(originalDcid, packet.AsSpan(0, bodyLen), packet.AsSpan(bodyLen, QuicKeySet.AeadTagLength));
        return packet;
    }

    public static void WritePacketNumber(Span<byte> dest, ulong packetNumber, int pnLength)
    {
        for (int i = pnLength - 1; i >= 0; i--)
        {
            dest[i] = (byte)(packetNumber & 0xFF);
            packetNumber >>= 8;
        }
    }

    public static ulong ReadTruncatedPacketNumber(ReadOnlySpan<byte> src, int pnLength)
    {
        ulong val = 0;
        for (int i = 0; i < pnLength; i++)
            val = (val << 8) | src[i];
        return val;
    }
}

/// <summary>Ordered out-of-order reassembly buffer for QUIC CRYPTO or STREAM offsets.</summary>
internal sealed class QuicOffsetReassembler
{
    public const int MaxBufferedGapBytes = 4 * 1024 * 1024;

    private readonly SortedDictionary<ulong, byte[]> _segments = new();
    private ulong _readOffset;
    private int _bufferedBytes;

    public ulong ReadOffset => _readOffset;
    public int BufferedBytes => _bufferedBytes;

    public bool TryEnqueue(ulong offset, ReadOnlySpan<byte> data, int maxAllowedBuffer = MaxBufferedGapBytes)
    {
        if (data.IsEmpty)
            return true;

        ulong end = offset + (ulong)data.Length;
        if (end <= _readOffset)
            return true;

        if (offset < _readOffset)
        {
            int skip = (int)(_readOffset - offset);
            data = data.Slice(skip);
            offset = _readOffset;
        }

        // Trim against existing overlapping segments if exact offset exists.
        if (_segments.TryGetValue(offset, out byte[]? existing))
        {
            if (existing.Length >= data.Length)
                return true;
            _bufferedBytes -= existing.Length;
            _segments[offset] = data.ToArray();
            _bufferedBytes += data.Length;
        }
        else
        {
            if (_bufferedBytes + data.Length > maxAllowedBuffer)
                return false;
            _segments[offset] = data.ToArray();
            _bufferedBytes += data.Length;
        }

        return true;
    }

    public byte[] DrainContiguous()
    {
        if (_segments.Count == 0)
            return Array.Empty<byte>();

        MemoryStream? ms = null;
        while (_segments.Count > 0)
        {
            using SortedDictionary<ulong, byte[]>.Enumerator en = _segments.GetEnumerator();
            if (!en.MoveNext())
                break;

            ulong segOffset = en.Current.Key;
            byte[] segData = en.Current.Value;

            if (segOffset > _readOffset)
                break;

            _segments.Remove(segOffset);
            _bufferedBytes -= segData.Length;

            ulong segEnd = segOffset + (ulong)segData.Length;
            if (segEnd <= _readOffset)
                continue;

            int trim = (int)(_readOffset - segOffset);
            int take = segData.Length - trim;
            ms ??= new MemoryStream(take);
            ms.Write(segData, trim, take);
            _readOffset = segEnd;
        }

        return ms is null ? Array.Empty<byte>() : ms.ToArray();
    }

    public void Clear()
    {
        _segments.Clear();
        _readOffset = 0;
        _bufferedBytes = 0;
    }
}

/// <summary>
/// Full-duplex or unidirectional QUIC stream with out-of-order offset reassembly,
/// flow control (<c>MAX_STREAM_DATA</c>/<c>MAX_DATA</c>), and <c>RESET_STREAM</c>/<c>STOP_SENDING</c>.
/// </summary>
public sealed class QuicStream : Stream
{
    private readonly QuicConnection _conn;
    private readonly ulong _localWindowSize;
    private readonly object _rxLock = new();
    private readonly QuicOffsetReassembler _rxReassembler = new();
    private readonly Queue<byte[]> _rxReadyChunks = new();
    private int _rxReadyOffset;
    private ulong? _finalSize;
    private ulong _highestRxEnd;
    private ulong _localMaxStreamData;
    private ulong _rxConsumedBytes;
    private bool _rxCompleted;
    private Exception? _rxError;
    private TaskCompletionSource<bool>? _rxWaiter;

    private readonly object _txLock = new();
    private readonly Queue<byte> _txBuffer = new();
    private ulong _txQueuedTotal;
    private ulong _txSentOffset;
    private ulong _peerMaxStreamData;
    private bool _txFinRequested;
    private bool _txFinSent;
    private bool _txBlockedSent;
    private Exception? _txError;
    private TaskCompletionSource<bool>? _txSpaceWaiter;

    internal QuicStream(
        QuicConnection conn,
        ulong streamId,
        ulong initialLocalMaxStreamData,
        ulong initialPeerMaxStreamData)
    {
        _conn = conn;
        StreamId = streamId;
        _localWindowSize = Math.Max(65_536UL, initialLocalMaxStreamData);
        _localMaxStreamData = initialLocalMaxStreamData;
        _peerMaxStreamData = initialPeerMaxStreamData;
    }

    public ulong StreamId { get; }
    public bool IsBidirectional => (StreamId & 0x02UL) == 0UL;
    public bool IsClientInitiated => (StreamId & 0x01UL) == 0UL;
    public ulong? RemoteResetErrorCode { get; private set; }
    public ulong? RemoteStopSendingErrorCode { get; private set; }
    public bool IsRemoteClosed { get { lock (_rxLock) return _rxCompleted; } }
    public bool IsLocalClosed { get { lock (_txLock) return _txFinRequested; } }

    public override bool CanRead => IsBidirectional || !IsClientInitiated;
    public override bool CanWrite => IsBidirectional || IsClientInitiated;
    public override bool CanSeek => false;
    public override long Length => throw new NotSupportedException();
    public override long Position { get => throw new NotSupportedException(); set => throw new NotSupportedException(); }

    public override void Flush() { }
    public override Task FlushAsync(CancellationToken cancellationToken) => Task.CompletedTask;
    public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
    public override void SetLength(long value) => throw new NotSupportedException();

    public override int Read(byte[] buffer, int offset, int count) =>
        ReadAsync(buffer.AsMemory(offset, count), CancellationToken.None).AsTask().GetAwaiter().GetResult();

    public override void Write(byte[] buffer, int offset, int count) =>
        WriteAsync(buffer.AsMemory(offset, count), CancellationToken.None).AsTask().GetAwaiter().GetResult();

    public override Task<int> ReadAsync(byte[] buffer, int offset, int count, CancellationToken cancellationToken) =>
        ReadAsync(buffer.AsMemory(offset, count), cancellationToken).AsTask();

    public override async ValueTask<int> ReadAsync(Memory<byte> buffer, CancellationToken cancellationToken = default)
    {
        if (!CanRead)
            throw new InvalidOperationException($"QUIC stream {StreamId} is write-only.");
        if (buffer.IsEmpty)
            return 0;

        while (true)
        {
            cancellationToken.ThrowIfCancellationRequested();
            TaskCompletionSource<bool>? waiter = null;
            ulong? windowUpdateToSend = null;

            int copiedResult = 0;
            bool hasResult = false;

            lock (_rxLock)
            {
                if (_rxReadyChunks.Count > 0)
                {
                    int copied = 0;
                    while (copied < buffer.Length && _rxReadyChunks.Count > 0)
                    {
                        byte[] head = _rxReadyChunks.Peek();
                        int avail = head.Length - _rxReadyOffset;
                        int take = Math.Min(avail, buffer.Length - copied);
                        head.AsSpan(_rxReadyOffset, take).CopyTo(buffer.Span.Slice(copied));
                        copied += take;
                        _rxReadyOffset += take;
                        if (_rxReadyOffset >= head.Length)
                        {
                            _rxReadyChunks.Dequeue();
                            _rxReadyOffset = 0;
                        }
                    }

                    _rxConsumedBytes += (ulong)copied;
                    if (_finalSize is null && _localMaxStreamData - _rxConsumedBytes <= _localWindowSize / 2)
                    {
                        _localMaxStreamData = _rxConsumedBytes + _localWindowSize;
                        windowUpdateToSend = _localMaxStreamData;
                    }

                    if (_finalSize.HasValue && _rxReassembler.ReadOffset >= _finalSize.Value && _rxReadyChunks.Count == 0)
                        _rxCompleted = true;

                    copiedResult = copied;
                    hasResult = true;
                }
                else
                {
                    if (_rxError is not null)
                        throw _rxError;

                    if (_rxCompleted)
                        return 0;

                    _rxWaiter ??= new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
                    waiter = _rxWaiter;
                }
            }

            if (hasResult)
            {
                if (windowUpdateToSend.HasValue)
                    _conn.QueueStreamMaxData(StreamId, windowUpdateToSend.Value);
                _conn.ReportConnectionBytesConsumed(copiedResult);
                return copiedResult;
            }

            await waiter!.Task.WaitAsync(cancellationToken).ConfigureAwait(false);
        }
    }

    public override Task WriteAsync(byte[] buffer, int offset, int count, CancellationToken cancellationToken) =>
        WriteAsync(buffer.AsMemory(offset, count), cancellationToken).AsTask();

    public override ValueTask WriteAsync(ReadOnlyMemory<byte> buffer, CancellationToken cancellationToken = default) =>
        WriteAsync(buffer, fin: false, cancellationToken);

    public async ValueTask WriteAsync(ReadOnlyMemory<byte> buffer, bool fin, CancellationToken cancellationToken = default)
    {
        if (!CanWrite)
            throw new InvalidOperationException($"QUIC stream {StreamId} is read-only.");

        cancellationToken.ThrowIfCancellationRequested();

        int pos = 0;
        while (pos < buffer.Length || (fin && pos == buffer.Length))
        {
            if (TryEnqueueWriteSlice(buffer.Span, ref pos, fin, out TaskCompletionSource<bool>? waiter, out ulong? blockedLimit))
                return;

            if (blockedLimit.HasValue)
                _conn.QueueFrame(new QuicStreamDataBlockedFrame(StreamId, blockedLimit.Value));

            if (waiter is not null)
                await waiter.Task.WaitAsync(cancellationToken).ConfigureAwait(false);
        }
    }

    private bool TryEnqueueWriteSlice(
        ReadOnlySpan<byte> fullBuffer,
        ref int pos,
        bool fin,
        out TaskCompletionSource<bool>? waiter,
        out ulong? blockedLimit)
    {
        waiter = null;
        blockedLimit = null;
        bool notifyReady = false;
        bool done = false;

        lock (_txLock)
        {
            if (_txError is not null)
                throw _txError;
            if (_txFinRequested && pos == 0 && (fullBuffer.Length > 0 || fin))
                throw new InvalidOperationException($"QUIC stream {StreamId} writes already completed.");

            if (fullBuffer.Length == 0 && fin)
            {
                _txFinRequested = true;
                notifyReady = true;
                done = true;
            }
            else
            {
                // Bound local outbound queue to avoid unbounded buffering beyond peer flow control + 256 KiB.
                ulong maxBuffered = _peerMaxStreamData + 262_144UL;
                if (_txQueuedTotal < maxBuffered)
                {
                    int chunk = (int)Math.Min((ulong)(fullBuffer.Length - pos), maxBuffered - _txQueuedTotal);
                    ReadOnlySpan<byte> slice = fullBuffer.Slice(pos, chunk);
                    for (int i = 0; i < slice.Length; i++)
                        _txBuffer.Enqueue(slice[i]);
                    _txQueuedTotal += (ulong)chunk;
                    pos += chunk;

                    if (pos == fullBuffer.Length && fin)
                        _txFinRequested = true;

                    notifyReady = true;
                    if (pos == fullBuffer.Length)
                        done = true;
                }
                else
                {
                    if (!_txBlockedSent && _txSentOffset >= _peerMaxStreamData)
                    {
                        _txBlockedSent = true;
                        blockedLimit = _peerMaxStreamData;
                    }
                    _txSpaceWaiter ??= new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
                    waiter = _txSpaceWaiter;
                }
            }
        }

        if (notifyReady)
            _conn.NotifyStreamWriteReady(this);

        return done;
    }

    public ValueTask CompleteWritesAsync(CancellationToken cancellationToken = default) =>
        WriteAsync(ReadOnlyMemory<byte>.Empty, fin: true, cancellationToken);

    public ValueTask ResetAsync(ulong applicationErrorCode, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        ulong finalSize;
        lock (_txLock)
        {
            finalSize = _txSentOffset;
            _txBuffer.Clear();
            _txFinRequested = true;
            _txFinSent = true;
            _txError ??= new QuicException(applicationErrorCode, isApplicationError: true, $"Stream {StreamId} reset locally.");
            _txSpaceWaiter?.TrySetResult(false);
            _txSpaceWaiter = null;
        }
        _conn.QueueFrame(new QuicResetStreamFrame(StreamId, applicationErrorCode, finalSize));
        return ValueTask.CompletedTask;
    }

    public ValueTask StopSendingAsync(ulong applicationErrorCode, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        _conn.QueueFrame(new QuicStopSendingFrame(StreamId, applicationErrorCode));
        return ValueTask.CompletedTask;
    }

    internal bool HasPendingOutboundData(ulong connSendAvailable)
    {
        lock (_txLock)
        {
            if (_txError is not null)
                return false;
            ulong streamAvail = _peerMaxStreamData > _txSentOffset ? _peerMaxStreamData - _txSentOffset : 0UL;
            if (_txBuffer.Count > 0 && streamAvail > 0 && connSendAvailable > 0)
                return true;
            return _txFinRequested && !_txFinSent && _txBuffer.Count == 0;
        }
    }

    internal QuicStreamFrame? DequeueOutboundFrame(int maxFramePayloadBytes, ulong connSendAvailable, out QuicStreamDataBlockedFrame? streamBlockedFrame)
    {
        streamBlockedFrame = null;
        lock (_txLock)
        {
            if (_txError is not null)
                return null;

            if (_txBuffer.Count == 0)
            {
                if (_txFinRequested && !_txFinSent)
                {
                    _txFinSent = true;
                    return new QuicStreamFrame(StreamId, _txSentOffset, Array.Empty<byte>(), Fin: true, HasLength: true);
                }
                return null;
            }

            ulong streamAvail = _peerMaxStreamData > _txSentOffset ? _peerMaxStreamData - _txSentOffset : 0UL;
            ulong allowed = Math.Min(streamAvail, connSendAvailable);
            if (allowed == 0)
            {
                if (!_txBlockedSent && streamAvail == 0)
                {
                    _txBlockedSent = true;
                    streamBlockedFrame = new QuicStreamDataBlockedFrame(StreamId, _peerMaxStreamData);
                }
                return null;
            }

            int overhead = 1 + QuicVarInt.GetEncodedLength(StreamId)
                + (_txSentOffset > 0 ? QuicVarInt.GetEncodedLength(_txSentOffset) : 0)
                + 2;
            int maxData = Math.Max(1, maxFramePayloadBytes - overhead);
            int take = (int)Math.Min((ulong)_txBuffer.Count, Math.Min(allowed, (ulong)maxData));
            if (take <= 0)
                return null;

            var payload = new byte[take];
            for (int i = 0; i < take; i++)
                payload[i] = _txBuffer.Dequeue();

            ulong offset = _txSentOffset;
            _txSentOffset += (ulong)take;

            bool fin = _txFinRequested && _txBuffer.Count == 0;
            if (fin)
                _txFinSent = true;

            _txSpaceWaiter?.TrySetResult(true);
            _txSpaceWaiter = null;
            return new QuicStreamFrame(StreamId, offset, payload, fin, HasLength: true);
        }
    }

    internal ulong OnStreamDataReceived(ulong offset, ReadOnlySpan<byte> data, bool fin, out QuicException? protocolError)
    {
        protocolError = null;
        ulong end = offset + (ulong)data.Length;

        lock (_rxLock)
        {
            if (_rxError is not null || RemoteResetErrorCode.HasValue)
                return 0;

            if (end > _localMaxStreamData)
            {
                protocolError = new QuicException(QuicErrorCode.FlowControlError, false, $"Stream {StreamId} exceeded max_stream_data.");
                return 0;
            }

            if (_finalSize.HasValue)
            {
                if (end > _finalSize.Value || (fin && end != _finalSize.Value))
                {
                    protocolError = new QuicException(QuicErrorCode.FinalSizeError, false, $"Stream {StreamId} final_size mismatch.");
                    return 0;
                }
            }
            else if (fin)
            {
                if (end < _highestRxEnd)
                {
                    protocolError = new QuicException(QuicErrorCode.FinalSizeError, false, $"Stream {StreamId} final_size {end} < highest offset {_highestRxEnd}.");
                    return 0;
                }
                _finalSize = end;
            }

            ulong deltaBytes = end > _highestRxEnd ? end - _highestRxEnd : 0UL;
            if (end > _highestRxEnd)
                _highestRxEnd = end;

            if (!data.IsEmpty)
            {
                if (!_rxReassembler.TryEnqueue(offset, data))
                {
                    protocolError = new QuicException(QuicErrorCode.FlowControlError, false, $"Stream {StreamId} receive buffer overflow.");
                    return 0;
                }

                byte[] contiguous = _rxReassembler.DrainContiguous();
                if (contiguous.Length > 0)
                    _rxReadyChunks.Enqueue(contiguous);
            }

            if (_finalSize.HasValue && _rxReassembler.ReadOffset >= _finalSize.Value && _rxReadyChunks.Count == 0)
                _rxCompleted = true;

            _rxWaiter?.TrySetResult(true);
            _rxWaiter = null;
            return deltaBytes;
        }
    }

    internal void OnRemoteMaxStreamData(ulong newMax)
    {
        bool notifyReady = false;
        lock (_txLock)
        {
            if (newMax > _peerMaxStreamData)
            {
                _peerMaxStreamData = newMax;
                _txBlockedSent = false;
                _txSpaceWaiter?.TrySetResult(true);
                _txSpaceWaiter = null;
                notifyReady = true;
            }
        }
        if (notifyReady)
            _conn.NotifyStreamWriteReady(this);
    }

    internal void OnRemoteReset(ulong appErrorCode, ulong finalSize)
    {
        lock (_rxLock)
        {
            RemoteResetErrorCode = appErrorCode;
            _finalSize ??= finalSize;
            _rxError ??= new QuicException(appErrorCode, isApplicationError: true, $"Stream {StreamId} reset by peer (code=0x{appErrorCode:X}).");
            _rxCompleted = true;
            _rxWaiter?.TrySetResult(true);
            _rxWaiter = null;
        }
    }

    internal void OnRemoteStopSending(ulong appErrorCode)
    {
        lock (_txLock)
        {
            RemoteStopSendingErrorCode = appErrorCode;
            _txError ??= new QuicException(appErrorCode, isApplicationError: true, $"Peer sent STOP_SENDING on stream {StreamId} (code=0x{appErrorCode:X}).");
            _txBuffer.Clear();
            _txFinRequested = true;
            _txFinSent = true;
            _txSpaceWaiter?.TrySetResult(true);
            _txSpaceWaiter = null;
        }
    }

    internal void FailConnection(Exception error)
    {
        lock (_rxLock)
        {
            _rxError ??= error;
            _rxCompleted = true;
            _rxWaiter?.TrySetResult(true);
            _rxWaiter = null;
        }
        lock (_txLock)
        {
            _txError ??= error;
            _txSpaceWaiter?.TrySetResult(true);
            _txSpaceWaiter = null;
        }
    }
}

/// <summary>
/// Pure managed RFC 9000/9001/9002 QUIC v1 client connection supporting Retry, Version Negotiation,
/// coalesced datagrams, 1-RTT key updates, ChaosFrames Initial packetization, stream multiplexing,
/// flow control, loss recovery, and SOCKS5 UDP association.
/// </summary>
public sealed class QuicConnection : IAsyncDisposable
{
    private sealed class PacketSpaceRxState
    {
        public readonly QuicCryptoReceiveBufferWrapper Crypto = new();
        public readonly SortedSet<ulong> AckPending = new();
        public long LargestRxPn = -1;
        public bool NeedAck;
        public TimeSpan? FirstAckElicitingRxTime;
    }

    private sealed class QuicCryptoReceiveBufferWrapper
    {
        public readonly QuicOffsetReassembler Reassembler = new();
    }

    private readonly QuicConnectionOptions _options;
    private readonly QuicTransportSpec _spec;
    private readonly IQuicDatagramTransport _transport;
    private readonly bool _ownsTransport;
    private readonly TlsHandshakeEngine _tls;
    private readonly QuicLossRecovery _lossRecovery;
    private readonly Stopwatch _clock = Stopwatch.StartNew();
    private readonly Random _rng;

    private readonly byte[] _localScid;
    private readonly byte[] _originalDcid;
    private byte[] _remoteDcid;
    private byte[] _retryToken = Array.Empty<byte>();
    private byte[]? _retryScid;
    private bool _receivedServerInitial;
    private bool _receivedRetry;

    // Packet protection keys per space
    private QuicKeySet? _initialWriteKeys;
    private QuicKeySet? _initialReadKeys;
    private QuicKeySet? _handshakeWriteKeys;
    private QuicKeySet? _handshakeReadKeys;
    private QuicKeySet? _appWriteKeys;
    private QuicKeySet? _appReadKeys;
    private QuicKeySet? _appPrevReadKeys;
    private QuicKeySet? _appNextReadKeys;
    private bool _appWriteKeyPhase;
    private bool _appReadKeyPhase;
    private bool _initialDiscarded;
    private bool _handshakeDiscarded;
    private bool _handshakeMarkedComplete;
    private bool _handshakeConfirmed;

    // Packet number / RX tracking per space
    private readonly PacketSpaceRxState[] _rxSpaces = { new(), new(), new() };
    private readonly ulong[] _txNextPn = new ulong[3];
    private readonly List<byte[]> _deferredPackets = new();

    // TX state guarded by _stateLock
    private readonly object _stateLock = new();
    private readonly Queue<QuicCryptoFrame>[] _txCrypto = { new(), new(), new() };
    private readonly ulong[] _cryptoTxOffset = new ulong[3];
    private readonly Queue<QuicFrame> _txAppControlFrames = new();
    private readonly Queue<QuicStream> _txReadyStreams = new();
    private readonly HashSet<ulong> _txReadyStreamIds = new();
    private readonly SemaphoreSlim _txWake = new(0, int.MaxValue);
    private byte[] _clientHelloBytes = Array.Empty<byte>();

    // Streams & flow control
    private readonly ConcurrentDictionary<ulong, QuicStream> _streams = new();
    private readonly Channel<QuicStream> _serverUniAccept = Channel.CreateUnbounded<QuicStream>();
    private readonly Channel<QuicStream> _serverBiAccept = Channel.CreateUnbounded<QuicStream>();
    private long _nextClientBidiId = 0;
    private long _nextClientUniId = 2;
    private ulong _peerMaxStreamsBidi;
    private ulong _peerMaxStreamsUni;
    private ulong _peerMaxData;
    private ulong _connBytesSent;
    private bool _connDataBlockedSent;
    private readonly ulong _localMaxDataWindow;
    private ulong _localMaxData;
    private ulong _connBytesReceived;
    private ulong _connBytesConsumed;
    private readonly ulong _localMaxStreamsBidiWindow;
    private readonly ulong _localMaxStreamsUniWindow;
    private ulong _localMaxStreamsBidi;
    private ulong _localMaxStreamsUni;
    private ulong _serverStreamsBidiCount;
    private ulong _serverStreamsUniCount;
    private TaskCompletionSource<bool>? _bidiStreamLimitWaiter;
    private TaskCompletionSource<bool>? _uniStreamLimitWaiter;

    // Lifecycle
    private readonly CancellationTokenSource _connCts = new();
    private readonly TaskCompletionSource<bool> _handshakeTcs = new(TaskCreationOptions.RunContinuationsAsynchronously);
    private Task? _recvTask;
    private Task? _txTask;
    private Exception? _terminalError;
    private TimeSpan _lastActivity;
    private int _closed;

    private QuicConnection(
        QuicConnectionOptions options,
        QuicTransportSpec spec,
        IQuicDatagramTransport transport,
        bool ownsTransport,
        TlsHandshakeEngine tls,
        byte[] localScid,
        byte[] originalDcid,
        Random rng)
    {
        _options = options;
        _spec = spec;
        _transport = transport;
        _ownsTransport = ownsTransport;
        _tls = tls;
        _rng = rng;

        _localScid = localScid;
        _originalDcid = originalDcid;
        _remoteDcid = (byte[])originalDcid.Clone();

        int maxDatagram = Math.Clamp(options.MaxDatagramPayload > 0 ? options.MaxDatagramPayload : (int)spec.MaxUdpPayloadSize, 1200, 1452);
        MaxDatagramPayload = maxDatagram;
        TimeSpan? initRtt = options.InitialRttUs.HasValue && options.InitialRttUs.Value > 0
            ? TimeSpan.FromTicks((long)options.InitialRttUs.Value * 10L)
            : null;
        _lossRecovery = new QuicLossRecovery(maxDatagram, initialRtt: initRtt);

        _localMaxDataWindow = Math.Max(65_536UL, spec.InitialMaxData);
        _localMaxData = _localMaxDataWindow;
        _localMaxStreamsBidiWindow = Math.Max(16UL, spec.InitialMaxStreamsBidi);
        _localMaxStreamsUniWindow = Math.Max(16UL, spec.InitialMaxStreamsUni);
        _localMaxStreamsBidi = _localMaxStreamsBidiWindow;
        _localMaxStreamsUni = _localMaxStreamsUniWindow;
        _lastActivity = TimeSpan.Zero;
    }

    public int MaxDatagramPayload { get; }
    public byte[] LocalScid => (byte[])_localScid.Clone();
    public byte[] RemoteDcid => (byte[])_remoteDcid.Clone();
    public byte[] OriginalDcid => (byte[])_originalDcid.Clone();
    public bool RetryReceived => _receivedRetry;
    public byte[] RetryToken => (byte[])_retryToken.Clone();
    public string? NegotiatedAlpn => _tls.NegotiatedAlpn;
    public ushort NegotiatedCipherSuite => _tls.NegotiatedCipherSuite;
    public QuicTransportParameters? PeerTransportParameters { get; private set; }
    public IReadOnlyList<DerCertificate>? PeerCertificates => _tls.PeerCertificates;
    public QuicLossRecovery LossRecovery => _lossRecovery;
    public ulong PeerMaxStreamsBidi => Volatile.Read(ref _peerMaxStreamsBidi);
    public ulong PeerMaxStreamsUni => Volatile.Read(ref _peerMaxStreamsUni);
    public bool HandshakeConfirmed => _handshakeConfirmed;
    public bool IsConnected => Volatile.Read(ref _closed) == 0 && _terminalError is null && _handshakeMarkedComplete;
    public Exception? TerminalError => _terminalError;
    public TimeSpan HandshakeDuration { get; private set; }

    public static async Task<QuicConnection> ConnectAsync(
        QuicConnectionOptions options,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(options);
        ArgumentException.ThrowIfNullOrWhiteSpace(options.Host);

        QuicTransportSpec spec = options.TransportSpec ?? options.Profile.QuicSpec ?? ChromeQuicSpecs.DefaultTransportSpec;
        Random rng = options.Random ?? Random.Shared;

        IQuicDatagramTransport transport;
        bool ownsTransport;
        if (options.TransportOverride is not null)
        {
            transport = options.TransportOverride;
            ownsTransport = false;
        }
        else if (options.Proxy is { Kind: ProxyProtocolKind.Socks5 } proxy)
        {
            transport = await Socks5UdpTransport.ConnectAsync(proxy, options.Host, options.Port, cancellationToken: cancellationToken).ConfigureAwait(false);
            ownsTransport = true;
        }
        else
        {
            transport = await DirectUdpTransport.ConnectAsync(options.Host, options.Port, cancellationToken: cancellationToken).ConfigureAwait(false);
            ownsTransport = true;
        }

        int scidLen = spec.ScidLength > 0 ? Math.Min(spec.ScidLength, 20) : 8;
        int dcidLen = spec.DcidLength > 0 ? Math.Min(spec.DcidLength, 20) : 8;
        var localScid = new byte[scidLen];
        var originalDcid = new byte[dcidLen];
        RandomNumberGenerator.Fill(localScid);
        RandomNumberGenerator.Fill(originalDcid);

        var tls = new TlsHandshakeEngine(new TlsHandshakeOptions
        {
            ServerName = options.Host,
            Port = options.Port,
            Profile = options.Profile,
            SpecOverride = options.Profile.CreateQuicClientHelloSpec is null ? ChromeQuicSpecs.CreateClientHelloSpec() : null,
            AlpnOverride = options.Profile.CreateQuicClientHelloSpec is null ? new[] { "h3" } : null,
            VerifyOptions = options.VerifyOptions,
            SessionCache = options.SessionCache,
            RandomExtensionOrder = options.RandomExtensionOrder,
            DisableSessionTickets = options.DisableSessionTickets,
            KeyLogSink = options.KeyLogSink,
            Random = rng,
        });

        var conn = new QuicConnection(options, spec, transport, ownsTransport, tls, localScid, originalDcid, rng);
        try
        {
            await conn.HandshakeAsync(cancellationToken).ConfigureAwait(false);
            return conn;
        }
        catch
        {
            await conn.DisposeAsync().ConfigureAwait(false);
            throw;
        }
    }

    private async Task HandshakeAsync(CancellationToken cancellationToken)
    {
        QuicTransportParameters localTp = QuicTransportParametersCodec.FromSpec(_spec, _localScid, _options.InitialRttUs, _rng);
        byte[] tpBytes = QuicTransportParametersCodec.Encode(localTp, shuffle: _spec.ShuffleTransportParameters, random: _rng);

        _initialWriteKeys = QuicCrypto.DeriveInitialKeys(_remoteDcid, isServer: false);
        _initialReadKeys = QuicCrypto.DeriveInitialKeys(_remoteDcid, isServer: true);

        _clientHelloBytes = _tls.StartQuicHandshake(tpBytes);
        EnqueueClientHelloInitialPackets();

        _recvTask = Task.Run(ReceiveLoopAsync);
        _txTask = Task.Run(TransmitLoopAsync);
        _txWake.Release();

        using var timeoutCts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken, _connCts.Token);
        timeoutCts.CancelAfter(_options.ConnectTimeout);

        try
        {
            await _handshakeTcs.Task.WaitAsync(timeoutCts.Token).ConfigureAwait(false);
            HandshakeDuration = _clock.Elapsed;
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested && _terminalError is null)
        {
            throw new TimeoutException($"QUIC handshake to {_options.Host}:{_options.Port} timed out after {_options.ConnectTimeout.TotalMilliseconds:F0} ms.");
        }
        catch (OperationCanceledException) when (_terminalError is not null)
        {
            throw _terminalError;
        }
    }

    private void EnqueueClientHelloInitialPackets()
    {
        lock (_stateLock)
        {
            _txCrypto[0].Clear();
            _cryptoTxOffset[0] = (ulong)_clientHelloBytes.Length;
            List<QuicCryptoFrame> slices = ChaosFrames.SplitCryptoFragments(
                _clientHelloBytes,
                enableChaos: _options.UseChaosInitialFrames,
                random: _rng);
            for (int i = 0; i < slices.Count; i++)
                _txCrypto[0].Enqueue(slices[i]);
        }
    }

    public async ValueTask<QuicStream> OpenBiDirectionalStreamAsync(CancellationToken cancellationToken = default)
    {
        ThrowIfClosedOrFailed();
        ulong streamId = (ulong)Interlocked.Add(ref _nextClientBidiId, 4) - 4UL;
        ulong neededStreams = (streamId / 4UL) + 1UL;

        while (Volatile.Read(ref _peerMaxStreamsBidi) < neededStreams)
        {
            ThrowIfClosedOrFailed();
            TaskCompletionSource<bool>? waiter = null;
            bool sendBlocked = false;
            lock (_stateLock)
            {
                if (_peerMaxStreamsBidi >= neededStreams)
                    break;
                _bidiStreamLimitWaiter ??= new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
                waiter = _bidiStreamLimitWaiter;
                sendBlocked = true;
            }
            if (sendBlocked)
                QueueFrame(new QuicStreamsBlockedFrame(Volatile.Read(ref _peerMaxStreamsBidi), IsBidirectional: true));
            await waiter.Task.WaitAsync(cancellationToken).ConfigureAwait(false);
        }

        ulong peerStreamWindow = PeerTransportParameters?.InitialMaxStreamDataBidiRemote ?? 6_291_456UL;
        var stream = new QuicStream(this, streamId, _spec.InitialMaxStreamDataBidiLocal, peerStreamWindow);
        _streams[streamId] = stream;
        return stream;
    }

    public async ValueTask<QuicStream> OpenUniDirectionalStreamAsync(CancellationToken cancellationToken = default)
    {
        ThrowIfClosedOrFailed();
        ulong streamId = (ulong)Interlocked.Add(ref _nextClientUniId, 4) - 4UL;
        ulong neededStreams = ((streamId - 2UL) / 4UL) + 1UL;

        while (Volatile.Read(ref _peerMaxStreamsUni) < neededStreams)
        {
            ThrowIfClosedOrFailed();
            TaskCompletionSource<bool>? waiter = null;
            bool sendBlocked = false;
            lock (_stateLock)
            {
                if (_peerMaxStreamsUni >= neededStreams)
                    break;
                _uniStreamLimitWaiter ??= new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
                waiter = _uniStreamLimitWaiter;
                sendBlocked = true;
            }
            if (sendBlocked)
                QueueFrame(new QuicStreamsBlockedFrame(Volatile.Read(ref _peerMaxStreamsUni), IsBidirectional: false));
            await waiter.Task.WaitAsync(cancellationToken).ConfigureAwait(false);
        }

        ulong peerStreamWindow = PeerTransportParameters?.InitialMaxStreamDataUni ?? 6_291_456UL;
        var stream = new QuicStream(this, streamId, 0UL, peerStreamWindow);
        _streams[streamId] = stream;
        return stream;
    }

    public async ValueTask<QuicStream?> AcceptServerUniStreamAsync(CancellationToken cancellationToken = default)
    {
        while (await _serverUniAccept.Reader.WaitToReadAsync(cancellationToken).ConfigureAwait(false))
        {
            if (_serverUniAccept.Reader.TryRead(out QuicStream? stream))
                return stream;
        }
        return null;
    }

    public async ValueTask<QuicStream?> AcceptServerBiStreamAsync(CancellationToken cancellationToken = default)
    {
        while (await _serverBiAccept.Reader.WaitToReadAsync(cancellationToken).ConfigureAwait(false))
        {
            if (_serverBiAccept.Reader.TryRead(out QuicStream? stream))
                return stream;
        }
        return null;
    }

    /// <summary>Initiates a 1-RTT Key Phase rotation (RFC 9001 §6).</summary>
    public void InitiateKeyUpdate()
    {
        lock (_stateLock)
        {
            if (_appWriteKeys is null || _appReadKeys is null)
                throw new InvalidOperationException("Cannot rotate 1-RTT keys before Application keys are established.");

            _appWriteKeys = _appWriteKeys.UpdateKeys();
            _appWriteKeyPhase = !_appWriteKeyPhase;
            _appReadKeys = _appReadKeys.UpdateKeys();
            _appReadKeyPhase = !_appReadKeyPhase;
            _appNextReadKeys = _appReadKeys.UpdateKeys();
        }
    }

    public ValueTask SendApplicationDatagramAsync(ReadOnlyMemory<byte> payload, CancellationToken cancellationToken = default)
    {
        ThrowIfClosedOrFailed();
        cancellationToken.ThrowIfCancellationRequested();
        QueueFrame(new QuicDatagramFrame(payload.ToArray(), HasLength: true));
        return ValueTask.CompletedTask;
    }

    public async Task CloseAsync(
        ulong errorCode = QuicErrorCode.NoError,
        bool isApplicationError = true,
        string reason = "",
        CancellationToken cancellationToken = default)
    {
        if (Interlocked.Exchange(ref _closed, 1) != 0)
            return;

        try
        {
            byte[] closeFrame = new QuicConnectionCloseFrame(errorCode, 0, reason, isApplicationError).ToArray();
            byte[]? packet = null;
            lock (_stateLock)
            {
                if (_appWriteKeys is not null)
                {
                    ulong pn = _txNextPn[2]++;
                    int pnLen = QuicCrypto.GetRequiredPacketNumberLength(pn, _lossRecovery.GetLargestAckedPacket(QuicPacketNumberSpace.Application) is { } la ? (long)la : -1L);
                    packet = QuicPacketCodec.BuildShortHeaderPacket(_remoteDcid, pn, pnLen, _appWriteKeyPhase, closeFrame, _appWriteKeys);
                }
                else if (_handshakeWriteKeys is not null)
                {
                    ulong pn = _txNextPn[1]++;
                    byte[] transportClose = new QuicConnectionCloseFrame(
                        isApplicationError ? QuicErrorCode.ApplicationError : errorCode,
                        0, reason, IsApplicationError: false).ToArray();
                    packet = QuicPacketCodec.BuildLongHeaderPacket(
                        QuicLongPacketType.Handshake, _remoteDcid, _localScid, ReadOnlySpan<byte>.Empty,
                        pn, 1, transportClose, _handshakeWriteKeys);
                }
                else if (_initialWriteKeys is not null)
                {
                    ulong pn = _txNextPn[0]++;
                    byte[] transportClose = new QuicConnectionCloseFrame(
                        isApplicationError ? QuicErrorCode.ApplicationError : errorCode,
                        0, reason, IsApplicationError: false).ToArray();
                    packet = QuicPacketCodec.BuildLongHeaderPacket(
                        QuicLongPacketType.Initial, _remoteDcid, _localScid, _retryToken,
                        pn, 1, transportClose, _initialWriteKeys);
                }
            }

            if (packet is not null)
                await _transport.SendDatagramAsync(packet, cancellationToken).ConfigureAwait(false);
        }
        catch
        {
            // Best-effort close notification
        }
        finally
        {
            FailAllWaiters(new QuicException(errorCode, isApplicationError, string.IsNullOrEmpty(reason) ? "QUIC connection closed." : reason));
        }
    }

    internal void QueueFrame(QuicFrame frame)
    {
        lock (_stateLock)
        {
            if (Volatile.Read(ref _closed) != 0)
                return;
            _txAppControlFrames.Enqueue(frame);
        }
        SignalTx();
    }

    internal void QueueStreamMaxData(ulong streamId, ulong newMaxStreamData) =>
        QueueFrame(new QuicMaxStreamDataFrame(streamId, newMaxStreamData));

    internal void ReportConnectionBytesConsumed(int consumed)
    {
        if (consumed <= 0)
            return;

        ulong? newMaxData = null;
        lock (_stateLock)
        {
            _connBytesConsumed += (ulong)consumed;
            if (_localMaxData - _connBytesConsumed <= _localMaxDataWindow / 2UL)
            {
                _localMaxData = _connBytesConsumed + _localMaxDataWindow;
                newMaxData = _localMaxData;
            }
        }
        if (newMaxData.HasValue)
            QueueFrame(new QuicMaxDataFrame(newMaxData.Value));
    }

    internal void NotifyStreamWriteReady(QuicStream stream)
    {
        lock (_stateLock)
        {
            if (_txReadyStreamIds.Add(stream.StreamId))
                _txReadyStreams.Enqueue(stream);
        }
        SignalTx();
    }

    private void SignalTx()
    {
        try { _txWake.Release(); } catch { }
    }

    private async Task ReceiveLoopAsync()
    {
        var buffer = new byte[Socks5UdpTransport.UdpBufferSize];
        CancellationToken ct = _connCts.Token;

        try
        {
            while (!ct.IsCancellationRequested && Volatile.Read(ref _closed) == 0)
            {
                int len = await _transport.ReceiveDatagramAsync(buffer.AsMemory(), ct).ConfigureAwait(false);
                if (len == 0)
                {
                    FailWithProtocolError(new EndOfStreamException("Underlying QUIC UDP transport closed."));
                    break;
                }

                _lastActivity = _clock.Elapsed;
                ProcessDatagram(buffer.AsSpan(0, len));
                RetryDeferredPackets();
            }
        }
        catch (OperationCanceledException)
        {
            // Normal shutdown
        }
        catch (Exception ex)
        {
            FailWithProtocolError(ex);
        }
    }

    private void RetryDeferredPackets()
    {
        while (true)
        {
            byte[]? next = null;
            lock (_stateLock)
            {
                if (_deferredPackets.Count > 0)
                {
                    next = _deferredPackets[0];
                    _deferredPackets.RemoveAt(0);
                }
            }
            if (next is null)
                break;

            ProcessDatagram(next, allowDefer: false);
        }
    }

    private void ProcessDatagram(ReadOnlySpan<byte> datagram, bool allowDefer = true)
    {
        int offset = 0;
        while (offset < datagram.Length && Volatile.Read(ref _closed) == 0)
        {
            ReadOnlySpan<byte> span = datagram.Slice(offset);
            byte firstByte = span[0];

            if ((firstByte & 0x80) != 0)
            {
                // Long header packet
                if (span.Length < 7)
                    return;

                uint version = BinaryPrimitives.ReadUInt32BigEndian(span.Slice(1, 4));
                int off = 5;
                byte dcidLen = span[off++];
                if (off + dcidLen + 1 > span.Length)
                    return;
                ReadOnlySpan<byte> dcid = span.Slice(off, dcidLen);
                off += dcidLen;

                byte scidLen = span[off++];
                if (off + scidLen > span.Length)
                    return;
                ReadOnlySpan<byte> scid = span.Slice(off, scidLen);
                off += scidLen;

                if (version == 0)
                {
                    HandleVersionNegotiation(dcid, span.Slice(off));
                    return;
                }

                if (version != QuicCrypto.QuicVersion1)
                    return;

                var type = (QuicLongPacketType)((firstByte >> 4) & 0x03);
                if (type == QuicLongPacketType.Retry)
                {
                    HandleRetry(datagram.Slice(offset), dcid, scid);
                    return;
                }

                if ((firstByte & 0x40) == 0)
                    return; // Fixed bit must be 1

                if (type == QuicLongPacketType.Initial)
                {
                    if (!QuicVarInt.TryRead(span, ref off, out ulong tokenLen) || tokenLen > (ulong)(span.Length - off))
                        return;
                    if (tokenLen != 0)
                    {
                        FailAndCloseTransport(QuicErrorCode.ProtocolViolation, "Server Initial packet contained non-empty token.");
                        return;
                    }
                }

                if (!QuicVarInt.TryRead(span, ref off, out ulong pktLen) || pktLen > (ulong)(span.Length - off))
                    return;

                int pnOffset = off;
                int totalPacketLen = pnOffset + (int)pktLen;

                if (type == QuicLongPacketType.Initial)
                {
                    QuicKeySet? readKeys;
                    lock (_stateLock)
                        readKeys = _initialDiscarded ? null : _initialReadKeys;

                    if (readKeys is not null)
                        DecryptAndProcessPacket(QuicPacketNumberSpace.Initial, QuicEncryptionLevel.Initial, datagram.Slice(offset, totalPacketLen), pnOffset, readKeys, scid);
                }
                else if (type == QuicLongPacketType.Handshake)
                {
                    QuicKeySet? readKeys;
                    lock (_stateLock)
                        readKeys = _handshakeDiscarded ? null : _handshakeReadKeys;

                    if (readKeys is null)
                    {
                        if (allowDefer)
                            BufferDeferredPacket(datagram.Slice(offset, totalPacketLen));
                    }
                    else
                    {
                        DecryptAndProcessPacket(QuicPacketNumberSpace.Handshake, QuicEncryptionLevel.Handshake, datagram.Slice(offset, totalPacketLen), pnOffset, readKeys, scid);
                    }
                }

                offset += totalPacketLen;
            }
            else
            {
                // Short header (1-RTT) packet extends to end of UDP datagram.
                if ((firstByte & 0x40) == 0)
                    return;

                int pnOffset = 1 + _localScid.Length;
                if (span.Length < pnOffset + 4 + QuicKeySet.AeadTagLength)
                    return;

                QuicKeySet? readKeys;
                lock (_stateLock)
                    readKeys = _appReadKeys;

                if (readKeys is null)
                {
                    if (allowDefer)
                        BufferDeferredPacket(span);
                    return;
                }

                DecryptAndProcessShortPacket(span, pnOffset);
                return;
            }
        }
    }

    private void BufferDeferredPacket(ReadOnlySpan<byte> packetBytes)
    {
        lock (_stateLock)
        {
            if (_deferredPackets.Count < 64)
                _deferredPackets.Add(packetBytes.ToArray());
        }
    }

    private void HandleVersionNegotiation(ReadOnlySpan<byte> dcid, ReadOnlySpan<byte> versionsBytes)
    {
        if (_receivedServerInitial || !dcid.SequenceEqual(_localScid))
            return;

        for (int i = 0; i + 4 <= versionsBytes.Length; i += 4)
        {
            uint ver = BinaryPrimitives.ReadUInt32BigEndian(versionsBytes.Slice(i, 4));
            if (ver == QuicCrypto.QuicVersion1)
                return; // QUIC v1 supported, ignore VN
        }

        FailWithProtocolError(new QuicException(QuicErrorCode.ProtocolViolation, false, "Server rejected QUIC v1 via Version Negotiation."));
    }

    private void HandleRetry(ReadOnlySpan<byte> rawRetryPacket, ReadOnlySpan<byte> dcid, ReadOnlySpan<byte> scid)
    {
        if (_receivedServerInitial || _receivedRetry)
            return;
        if (!dcid.SequenceEqual(_localScid) || scid.IsEmpty || scid.Length > 20)
            return;
        if (scid.SequenceEqual(_originalDcid))
            return;

        if (!QuicCrypto.VerifyRetryIntegrityTag(_originalDcid, rawRetryPacket))
            return;

        int tokenStart = 5 + 1 + dcid.Length + 1 + scid.Length;
        int tokenLen = rawRetryPacket.Length - QuicKeySet.AeadTagLength - tokenStart;
        if (tokenLen <= 0)
            return;

        lock (_stateLock)
        {
            _receivedRetry = true;
            _retryScid = scid.ToArray();
            _remoteDcid = (byte[])_retryScid.Clone();
            _retryToken = rawRetryPacket.Slice(tokenStart, tokenLen).ToArray();

            _initialWriteKeys?.Clear();
            _initialReadKeys?.Clear();
            _initialWriteKeys = QuicCrypto.DeriveInitialKeys(_remoteDcid, isServer: false);
            _initialReadKeys = QuicCrypto.DeriveInitialKeys(_remoteDcid, isServer: true);
            _rxSpaces[0].Crypto.Reassembler.Clear();
            _rxSpaces[0].AckPending.Clear();
            _rxSpaces[0].NeedAck = false;
            _rxSpaces[0].LargestRxPn = -1;
            _rxSpaces[0].FirstAckElicitingRxTime = null;
            _lossRecovery.ResetSpace(QuicPacketNumberSpace.Initial);
            _initialDiscarded = false;
        }

        // Re-create clean loss recovery Initial space by instantiating fresh tracker? No, reset by re-queuing ClientHello frames.
        EnqueueClientHelloInitialPackets();
        SignalTx();
    }

    private void DecryptAndProcessPacket(
        QuicPacketNumberSpace space,
        QuicEncryptionLevel level,
        ReadOnlySpan<byte> packetBytes,
        int pnOffset,
        QuicKeySet readKeys,
        ReadOnlySpan<byte> scid)
    {
        Span<byte> copy = packetBytes.Length <= 2048 ? stackalloc byte[packetBytes.Length] : new byte[packetBytes.Length];
        packetBytes.CopyTo(copy);

        if (!readKeys.TryRemoveHeaderProtection(copy, pnOffset, out int pnLen, out _))
            return;

        ulong truncPn = QuicPacketCodec.ReadTruncatedPacketNumber(copy.Slice(pnOffset, pnLen), pnLen);
        long largestRx = _rxSpaces[(int)space].LargestRxPn;
        ulong fullPn = QuicCrypto.DecodePacketNumber(largestRx, truncPn, pnLen * 8);

        int headerLen = pnOffset + pnLen;
        if (!readKeys.TryPacketUnprotect(fullPn, copy.Slice(0, headerLen), copy.Slice(headerLen), out byte[] plaintext))
            return;

        if (space == QuicPacketNumberSpace.Initial && !_receivedServerInitial)
        {
            _receivedServerInitial = true;
            if (!scid.IsEmpty && !scid.SequenceEqual(_remoteDcid))
                _remoteDcid = scid.ToArray();
        }

        ProcessDecryptedFrames(space, level, fullPn, plaintext);
    }

    private void DecryptAndProcessShortPacket(ReadOnlySpan<byte> packetBytes, int pnOffset)
    {
        QuicKeySet curRead;
        QuicKeySet? prevRead;
        QuicKeySet? nextRead;
        bool curPhase;

        lock (_stateLock)
        {
            curRead = _appReadKeys!;
            prevRead = _appPrevReadKeys;
            nextRead = _appNextReadKeys;
            curPhase = _appReadKeyPhase;
        }

        Span<byte> copy = packetBytes.Length <= 2048 ? stackalloc byte[packetBytes.Length] : new byte[packetBytes.Length];
        packetBytes.CopyTo(copy);

        if (!curRead.TryRemoveHeaderProtection(copy, pnOffset, out int pnLen, out bool rxKeyPhase))
            return;

        ulong truncPn = QuicPacketCodec.ReadTruncatedPacketNumber(copy.Slice(pnOffset, pnLen), pnLen);
        long largestRx = _rxSpaces[(int)QuicPacketNumberSpace.Application].LargestRxPn;
        ulong fullPn = QuicCrypto.DecodePacketNumber(largestRx, truncPn, pnLen * 8);
        int headerLen = pnOffset + pnLen;

        byte[] plaintext;
        if (rxKeyPhase == curPhase)
        {
            if (!curRead.TryPacketUnprotect(fullPn, copy.Slice(0, headerLen), copy.Slice(headerLen), out plaintext))
            {
                if (prevRead is null || !prevRead.TryPacketUnprotect(fullPn, copy.Slice(0, headerLen), copy.Slice(headerLen), out plaintext))
                    return;
            }
        }
        else
        {
            nextRead ??= curRead.UpdateKeys();
            if (!nextRead.TryPacketUnprotect(fullPn, copy.Slice(0, headerLen), copy.Slice(headerLen), out plaintext))
                return;

            // Commit peer-initiated 1-RTT key phase rotation (RFC 9001 §6.2).
            lock (_stateLock)
            {
                _appPrevReadKeys?.Clear();
                _appPrevReadKeys = _appReadKeys;
                _appReadKeys = nextRead;
                _appNextReadKeys = nextRead.UpdateKeys();
                _appReadKeyPhase = rxKeyPhase;
                if (_appWriteKeys is not null && _appWriteKeyPhase != rxKeyPhase)
                {
                    _appWriteKeys = _appWriteKeys.UpdateKeys();
                    _appWriteKeyPhase = rxKeyPhase;
                }
            }
        }

        ProcessDecryptedFrames(QuicPacketNumberSpace.Application, QuicEncryptionLevel.Application, fullPn, plaintext);
    }

    private void ProcessDecryptedFrames(
        QuicPacketNumberSpace space,
        QuicEncryptionLevel level,
        ulong fullPn,
        byte[] plaintext)
    {
        List<QuicFrame> frames;
        try
        {
            frames = QuicFrameCodec.DecodeAll(plaintext, level);
        }
        catch (QuicException ex)
        {
            FailAndCloseTransport(ex.ErrorCode, ex.Message);
            return;
        }

        bool anyAckEliciting = false;
        for (int i = 0; i < frames.Count; i++)
        {
            if (frames[i].IsAckEliciting)
            {
                anyAckEliciting = true;
                break;
            }
        }

        TimeSpan now = _clock.Elapsed;
        PacketSpaceRxState rxState = _rxSpaces[(int)space];
        lock (_stateLock)
        {
            if ((long)fullPn > rxState.LargestRxPn)
                rxState.LargestRxPn = (long)fullPn;
            rxState.AckPending.Add(fullPn);
            while (rxState.AckPending.Count > 1024)
                rxState.AckPending.Remove(rxState.AckPending.Min);

            if (anyAckEliciting)
            {
                rxState.NeedAck = true;
                rxState.FirstAckElicitingRxTime ??= now;
            }
        }

        for (int i = 0; i < frames.Count; i++)
        {
            QuicFrame frame = frames[i];
            switch (frame)
            {
                case QuicPaddingFrame:
                case QuicPingFrame:
                    break;

                case QuicAckFrame ack:
                {
                    QuicAckProcessResult res;
                    lock (_stateLock)
                        res = _lossRecovery.OnAckReceived(space, ack, now);
                    RequeueLostFrames(space, res.LostPackets);
                    break;
                }

                case QuicCryptoFrame cf:
                    HandleCryptoFrame(space, level, cf);
                    break;

                case QuicHandshakeDoneFrame:
                    lock (_stateLock)
                    {
                        _handshakeConfirmed = true;
                        _handshakeDiscarded = true;
                        _lossRecovery.MarkHandshakeConfirmed(now);
                        _lossRecovery.DiscardSpace(QuicPacketNumberSpace.Handshake);
                        _handshakeReadKeys?.Clear();
                        _handshakeWriteKeys?.Clear();
                        _handshakeReadKeys = null;
                        _handshakeWriteKeys = null;
                    }
                    break;

                case QuicStreamFrame sf:
                    HandleStreamFrame(sf);
                    break;

                case QuicResetStreamFrame rf:
                    if (_streams.TryGetValue(rf.StreamId, out QuicStream? rStream))
                        rStream.OnRemoteReset(rf.ApplicationErrorCode, rf.FinalSize);
                    break;

                case QuicStopSendingFrame ss:
                    if (_streams.TryGetValue(ss.StreamId, out QuicStream? sStream))
                        sStream.OnRemoteStopSending(ss.ApplicationErrorCode);
                    break;

                case QuicMaxDataFrame md:
                    lock (_stateLock)
                    {
                        if (md.MaximumData > _peerMaxData)
                        {
                            _peerMaxData = md.MaximumData;
                            _connDataBlockedSent = false;
                            foreach (QuicStream st in _streams.Values)
                            {
                                if (st.HasPendingOutboundData(_peerMaxData - _connBytesSent) && _txReadyStreamIds.Add(st.StreamId))
                                    _txReadyStreams.Enqueue(st);
                            }
                        }
                    }
                    SignalTx();
                    break;

                case QuicMaxStreamDataFrame msd:
                    if (_streams.TryGetValue(msd.StreamId, out QuicStream? mStream))
                        mStream.OnRemoteMaxStreamData(msd.MaximumStreamData);
                    break;

                case QuicMaxStreamsFrame ms:
                    lock (_stateLock)
                    {
                        if (ms.IsBidirectional && ms.MaximumStreams > _peerMaxStreamsBidi)
                        {
                            Volatile.Write(ref _peerMaxStreamsBidi, ms.MaximumStreams);
                            _bidiStreamLimitWaiter?.TrySetResult(true);
                            _bidiStreamLimitWaiter = null;
                        }
                        else if (!ms.IsBidirectional && ms.MaximumStreams > _peerMaxStreamsUni)
                        {
                            Volatile.Write(ref _peerMaxStreamsUni, ms.MaximumStreams);
                            _uniStreamLimitWaiter?.TrySetResult(true);
                            _uniStreamLimitWaiter = null;
                        }
                    }
                    break;

                case QuicPathChallengeFrame pc:
                    QueueFrame(new QuicPathResponseFrame(pc.Data));
                    break;

                case QuicConnectionCloseFrame cc:
                {
                    var closeEx = new QuicException(
                        cc.ErrorCode,
                        cc.IsApplicationError,
                        string.IsNullOrEmpty(cc.ReasonPhrase)
                            ? $"Peer closed QUIC connection with {(cc.IsApplicationError ? "application" : "transport")} error 0x{cc.ErrorCode:X}."
                            : cc.ReasonPhrase);
                    FailAllWaiters(closeEx);
                    return;
                }
            }
        }

        if (anyAckEliciting)
            SignalTx();
    }

    private void HandleCryptoFrame(QuicPacketNumberSpace space, QuicEncryptionLevel level, QuicCryptoFrame frame)
    {
        PacketSpaceRxState rx = _rxSpaces[(int)space];
        if (!rx.Crypto.Reassembler.TryEnqueue(frame.Offset, frame.Data, 1024 * 1024))
        {
            FailAndCloseTransport(QuicErrorCode.CryptoBufferExceeded, "QUIC CRYPTO receive buffer exceeded.");
            return;
        }

        byte[] contiguous = rx.Crypto.Reassembler.DrainContiguous();
        if (contiguous.Length == 0)
            return;

        QuicHandshakeStepResult step;
        try
        {
            step = _tls.ProcessQuicCryptoData(level, contiguous);
        }
        catch (CertificateValidationException ex)
        {
            FailAndCloseTransport(QuicErrorCode.CryptoError(TlsAlertDescription.BadCertificate), ex.Message, ex);
            return;
        }
        catch (TlsAlertException ex)
        {
            FailAndCloseTransport(QuicErrorCode.CryptoError(ex.Description), ex.Message, ex);
            return;
        }
        catch (Exception ex)
        {
            FailAndCloseTransport(QuicErrorCode.CryptoError(TlsAlertDescription.InternalError), ex.Message, ex);
            return;
        }

        lock (_stateLock)
        {
            if (step.HandshakeReadKeys is not null)
            {
                _handshakeReadKeys = QuicCrypto.DerivePacketKeys(step.HandshakeReadKeys);
                _handshakeWriteKeys = QuicCrypto.DerivePacketKeys(step.HandshakeWriteKeys!);
            }

            if (step.ApplicationReadKeys is not null)
            {
                _appReadKeys = QuicCrypto.DerivePacketKeys(step.ApplicationReadKeys);
                _appWriteKeys = QuicCrypto.DerivePacketKeys(step.ApplicationWriteKeys!);
                _appNextReadKeys = _appReadKeys.UpdateKeys();
            }

            if (step.OutboundInitialData.Length > 0)
                EnqueueCryptoBytes(0, step.OutboundInitialData);

            if (step.OutboundHandshakeData.Length > 0)
                EnqueueCryptoBytes(1, step.OutboundHandshakeData);
        }

        if (step.HandshakeCompleted && !_handshakeMarkedComplete)
        {
            try
            {
                ValidateAndApplyPeerTransportParameters(step.PeerTransportParameters);
            }
            catch (QuicException qex)
            {
                FailAndCloseTransport(qex.ErrorCode, qex.Message, qex);
                return;
            }

            lock (_stateLock)
            {
                _handshakeMarkedComplete = true;
                _initialDiscarded = true;
                _lossRecovery.DiscardSpace(QuicPacketNumberSpace.Initial);
                _initialReadKeys?.Clear();
                _initialWriteKeys?.Clear();
                _initialReadKeys = null;
                _initialWriteKeys = null;
            }

            SignalTx();
            _handshakeTcs.TrySetResult(true);
        }
        else if (step.OutboundInitialData.Length > 0 || step.OutboundHandshakeData.Length > 0)
        {
            SignalTx();
        }
    }

    private void EnqueueCryptoBytes(int spaceIdx, byte[] data)
    {
        ulong startOffset = _cryptoTxOffset[spaceIdx];
        _cryptoTxOffset[spaceIdx] += (ulong)data.Length;

        int pos = 0;
        while (pos < data.Length)
        {
            int take = Math.Min(MaxDatagramPayload - 120, data.Length - pos);
            _txCrypto[spaceIdx].Enqueue(new QuicCryptoFrame(startOffset + (ulong)pos, data.AsSpan(pos, take).ToArray()));
            pos += take;
        }
    }

    private void ValidateAndApplyPeerTransportParameters(byte[]? rawTp)
    {
        if (rawTp is null || rawTp.Length == 0)
            throw new QuicException(QuicErrorCode.TransportParameterError, false, "Server did not supply QUIC transport parameters.");

        QuicTransportParameters tp = QuicTransportParametersCodec.Decode(rawTp, isServerParameters: true);
        if (tp.OriginalDestinationConnectionId is null || !tp.OriginalDestinationConnectionId.AsSpan().SequenceEqual(_originalDcid))
            throw new QuicException(QuicErrorCode.TransportParameterError, false, "Server original_destination_connection_id mismatch.");

        if (_receivedRetry)
        {
            if (tp.RetrySourceConnectionId is null || !tp.RetrySourceConnectionId.AsSpan().SequenceEqual(_retryScid))
                throw new QuicException(QuicErrorCode.TransportParameterError, false, "Server retry_source_connection_id mismatch after Retry.");
        }

        PeerTransportParameters = tp;
        _peerMaxData = tp.InitialMaxData ?? 0UL;
        Volatile.Write(ref _peerMaxStreamsBidi, tp.InitialMaxStreamsBidi ?? 0UL);
        Volatile.Write(ref _peerMaxStreamsUni, tp.InitialMaxStreamsUni ?? 0UL);

        if (tp.MaxAckDelayMs.HasValue)
            _lossRecovery.MaxAckDelay = TimeSpan.FromMilliseconds(tp.MaxAckDelayMs.Value);
        if (tp.AckDelayExponent.HasValue)
            _lossRecovery.AckDelayExponent = (int)tp.AckDelayExponent.Value;
    }

    private void HandleStreamFrame(QuicStreamFrame sf)
    {
        if (!_streams.TryGetValue(sf.StreamId, out QuicStream? stream))
        {
            bool isServerInitiated = (sf.StreamId & 0x01UL) == 1UL;
            if (!isServerInitiated)
            {
                FailAndCloseTransport(QuicErrorCode.StreamStateError, $"Received frame for unknown client stream {sf.StreamId}.");
                return;
            }

            bool isUni = (sf.StreamId & 0x02UL) != 0UL;
            ulong index = (sf.StreamId >> 2) + 1UL;
            if (isUni)
            {
                if (index > _localMaxStreamsUni)
                {
                    FailAndCloseTransport(QuicErrorCode.StreamLimitError, $"Server unidirectional stream {sf.StreamId} exceeds max_streams_uni.");
                    return;
                }
                _serverStreamsUniCount = Math.Max(_serverStreamsUniCount, index);
                stream = new QuicStream(this, sf.StreamId, _spec.InitialMaxStreamDataUni, 0UL);
                if (_streams.TryAdd(sf.StreamId, stream))
                {
                    _serverUniAccept.Writer.TryWrite(stream);
                    if (_localMaxStreamsUni - _serverStreamsUniCount <= _localMaxStreamsUniWindow / 2UL)
                    {
                        _localMaxStreamsUni = _serverStreamsUniCount + _localMaxStreamsUniWindow;
                        QueueFrame(new QuicMaxStreamsFrame(_localMaxStreamsUni, IsBidirectional: false));
                    }
                }
                else
                {
                    stream = _streams[sf.StreamId];
                }
            }
            else
            {
                if (index > _localMaxStreamsBidi)
                {
                    FailAndCloseTransport(QuicErrorCode.StreamLimitError, $"Server bidirectional stream {sf.StreamId} exceeds max_streams_bidi.");
                    return;
                }
                _serverStreamsBidiCount = Math.Max(_serverStreamsBidiCount, index);
                stream = new QuicStream(this, sf.StreamId, _spec.InitialMaxStreamDataBidiRemote, PeerTransportParameters?.InitialMaxStreamDataBidiLocal ?? 6_291_456UL);
                if (_streams.TryAdd(sf.StreamId, stream))
                {
                    _serverBiAccept.Writer.TryWrite(stream);
                    if (_localMaxStreamsBidi - _serverStreamsBidiCount <= _localMaxStreamsBidiWindow / 2UL)
                    {
                        _localMaxStreamsBidi = _serverStreamsBidiCount + _localMaxStreamsBidiWindow;
                        QueueFrame(new QuicMaxStreamsFrame(_localMaxStreamsBidi, IsBidirectional: true));
                    }
                }
                else
                {
                    stream = _streams[sf.StreamId];
                }
            }
        }

        ulong delta = stream.OnStreamDataReceived(sf.Offset, sf.Data, sf.Fin, out QuicException? protoErr);
        if (protoErr is not null)
        {
            FailAndCloseTransport(protoErr.ErrorCode, protoErr.Message, protoErr);
            return;
        }

        if (delta > 0)
        {
            lock (_stateLock)
            {
                _connBytesReceived += delta;
                if (_connBytesReceived > _localMaxData)
                {
                    FailAndCloseTransport(QuicErrorCode.FlowControlError, "Peer exceeded connection initial_max_data.");
                    return;
                }
            }
        }
    }

    private void RequeueLostFrames(QuicPacketNumberSpace space, IReadOnlyList<QuicSentPacket> lostPackets)
    {
        if (lostPackets.Count == 0)
            return;

        lock (_stateLock)
        {
            for (int p = 0; p < lostPackets.Count; p++)
            {
                IReadOnlyList<QuicFrame> frames = lostPackets[p].Frames;
                for (int f = 0; f < frames.Count; f++)
                {
                    switch (frames[f])
                    {
                        case QuicCryptoFrame cf:
                            _txCrypto[(int)space].Enqueue(cf);
                            break;
                        case QuicStreamFrame sf when space == QuicPacketNumberSpace.Application:
                            _txAppControlFrames.Enqueue(sf);
                            break;
                        case QuicMaxDataFrame or QuicMaxStreamDataFrame or QuicMaxStreamsFrame or QuicResetStreamFrame or QuicStopSendingFrame or QuicPathResponseFrame:
                            if (space == QuicPacketNumberSpace.Application)
                                _txAppControlFrames.Enqueue(frames[f]);
                            break;
                    }
                }
            }
        }
        SignalTx();
    }

    private async Task TransmitLoopAsync()
    {
        CancellationToken ct = _connCts.Token;
        try
        {
            while (!ct.IsCancellationRequested && Volatile.Read(ref _closed) == 0)
            {
                await FlushAllSpacesAsync(ct).ConfigureAwait(false);

                int waitMs = ComputeNextWakeupMs();
                try
                {
                    await _txWake.WaitAsync(waitMs, ct).ConfigureAwait(false);
                }
                catch (OperationCanceledException)
                {
                    break;
                }

                // Check loss / PTO / idle timeout
                TimeSpan now = _clock.Elapsed;
                if (_options.MaxIdleTimeout > TimeSpan.Zero &&
                    now - _lastActivity > _options.MaxIdleTimeout &&
                    _handshakeMarkedComplete)
                {
                    FailAllWaiters(new TimeoutException($"QUIC connection idle timeout exceeded ({_options.MaxIdleTimeout.TotalSeconds:F1}s)."));
                    break;
                }

                (TimeSpan? deadline, _, _) = _lossRecovery.GetLossDetectionTimeout();
                if (deadline.HasValue && now >= deadline.Value)
                {
                    QuicLossTimerOutcome outcome;
                    lock (_stateLock)
                        outcome = _lossRecovery.OnLossDetectionTimeout(now);

                    if (outcome.WasLossTimer)
                    {
                        RequeueLostFrames(outcome.Space, outcome.LostPackets);
                    }
                    else if (outcome.ProbePacketCount > 0)
                    {
                        await SendPtoProbeAsync(outcome.Space, ct).ConfigureAwait(false);
                    }
                }
            }
        }
        catch (OperationCanceledException)
        {
            // Shutdown
        }
        catch (Exception ex)
        {
            FailWithProtocolError(ex);
        }
    }

    private int ComputeNextWakeupMs()
    {
        TimeSpan now = _clock.Elapsed;
        int minMs = 200;

        lock (_stateLock)
        {
            for (int i = 0; i < 3; i++)
            {
                if (_rxSpaces[i].NeedAck)
                {
                    minMs = i < 2 ? 1 : Math.Min(minMs, 5);
                }
            }

            (TimeSpan? deadline, _, _) = _lossRecovery.GetLossDetectionTimeout();
            if (deadline.HasValue)
            {
                int deltaMs = (int)Math.Max(1, (deadline.Value - now).TotalMilliseconds);
                minMs = Math.Min(minMs, deltaMs);
            }
        }

        return minMs;
    }

    private async Task SendPtoProbeAsync(QuicPacketNumberSpace space, CancellationToken ct)
    {
        byte[]? pkt = null;
        lock (_stateLock)
        {
            QuicKeySet? keys = space switch
            {
                QuicPacketNumberSpace.Initial => _initialWriteKeys,
                QuicPacketNumberSpace.Handshake => _handshakeWriteKeys,
                _ => _appWriteKeys,
            };
            if (keys is null)
                return;

            var frames = new List<QuicFrame> { QuicPingFrame.Instance };
            if (space == QuicPacketNumberSpace.Initial)
                frames.Add(new QuicPaddingFrame(Math.Max(0, ChaosFrames.MinInitialDatagramBytes - 64)));

            pkt = BuildAndRecordPacketLocked(space, keys, frames);
        }

        if (pkt is not null)
            await _transport.SendDatagramAsync(pkt, ct).ConfigureAwait(false);
    }

    private async Task FlushAllSpacesAsync(CancellationToken ct)
    {
        while (Volatile.Read(ref _closed) == 0)
        {
            var datagram = new List<byte>();

            lock (_stateLock)
            {
                // 1. Initial space
                if (!_initialDiscarded && _initialWriteKeys is not null)
                    AppendSpacePacketsLocked(QuicPacketNumberSpace.Initial, _initialWriteKeys, datagram);

                // 2. Handshake space
                if (!_handshakeDiscarded && _handshakeWriteKeys is not null)
                    AppendSpacePacketsLocked(QuicPacketNumberSpace.Handshake, _handshakeWriteKeys, datagram);

                // 3. Application 1-RTT space
                if (_appWriteKeys is not null)
                    AppendSpacePacketsLocked(QuicPacketNumberSpace.Application, _appWriteKeys, datagram);
            }

            if (datagram.Count == 0)
                break;

            await _transport.SendDatagramAsync(datagram.ToArray(), ct).ConfigureAwait(false);
        }
    }

    private void AppendSpacePacketsLocked(QuicPacketNumberSpace space, QuicKeySet writeKeys, List<byte> coalescedDatagram)
    {
        int spaceIdx = (int)space;
        PacketSpaceRxState rx = _rxSpaces[spaceIdx];
        bool hasCrypto = _txCrypto[spaceIdx].Count > 0;
        bool hasControl = space == QuicPacketNumberSpace.Application && _txAppControlFrames.Count > 0;
        bool hasStreams = space == QuicPacketNumberSpace.Application && _txReadyStreams.Count > 0;
        bool hasAck = rx.NeedAck && rx.AckPending.Count > 0;

        if (!hasCrypto && !hasControl && !hasStreams && !hasAck)
            return;

        int remainingDatagramSpace = MaxDatagramPayload - coalescedDatagram.Count;
        if (remainingDatagramSpace < 80)
            return;

        ulong pn = _txNextPn[spaceIdx];
        long largestAcked = _lossRecovery.GetLargestAckedPacket(space) is { } la ? (long)la : -1L;
        int pnLen = QuicCrypto.GetRequiredPacketNumberLength(pn, largestAcked);
        int exactFixedOverhead = space == QuicPacketNumberSpace.Application
            ? 1 + _remoteDcid.Length + pnLen + QuicKeySet.AeadTagLength
            : 1 + 4 + 1 + _remoteDcid.Length + 1 + _localScid.Length
              + (space == QuicPacketNumberSpace.Initial ? QuicVarInt.GetEncodedLength((ulong)_retryToken.Length) + _retryToken.Length : 0)
              + 2 + pnLen + QuicKeySet.AeadTagLength;

        var frames = new List<QuicFrame>();
        int maxFramesBytes = Math.Max(32, remainingDatagramSpace - exactFixedOverhead);
        int usedBytes = 0;

        if (hasAck)
        {
            TimeSpan delay = rx.FirstAckElicitingRxTime.HasValue ? _clock.Elapsed - rx.FirstAckElicitingRxTime.Value : TimeSpan.Zero;
            ulong us = (ulong)Math.Max(0, delay.Ticks / 10L);
            ulong encodedDelay = us >> Math.Clamp(_lossRecovery.AckDelayExponent, 0, 20);
            var ackFrame = QuicAckFrame.FromPacketNumbers(rx.AckPending, encodedDelay);
            int ackLen = ackFrame.GetEncodedLength();
            if (usedBytes + ackLen <= maxFramesBytes)
            {
                frames.Add(ackFrame);
                usedBytes += ackLen;
                rx.NeedAck = false;
                rx.FirstAckElicitingRxTime = null;
            }
        }

        while (_txCrypto[spaceIdx].Count > 0)
        {
            QuicCryptoFrame next = _txCrypto[spaceIdx].Peek();
            int len = next.GetEncodedLength();
            if (usedBytes + len <= maxFramesBytes)
            {
                frames.Add(_txCrypto[spaceIdx].Dequeue());
                usedBytes += len;
                if (space == QuicPacketNumberSpace.Initial && _options.UseChaosInitialFrames && usedBytes + 1 <= maxFramesBytes)
                {
                    frames.Add(QuicPingFrame.Instance);
                    usedBytes += 1;
                }
            }
            else if (next.Data.Length > 1 && maxFramesBytes - usedBytes >= 24)
            {
                int splitTake = Math.Clamp(maxFramesBytes - usedBytes - 10, 1, next.Data.Length - 1);
                _txCrypto[spaceIdx].Dequeue();
                var head = new QuicCryptoFrame(next.Offset, next.Data.AsSpan(0, splitTake).ToArray());
                var tail = new QuicCryptoFrame(next.Offset + (ulong)splitTake, next.Data.AsSpan(splitTake).ToArray());
                // Re-insert tail at front
                var rest = new List<QuicCryptoFrame>(_txCrypto[spaceIdx].Count + 1) { tail };
                while (_txCrypto[spaceIdx].Count > 0)
                    rest.Add(_txCrypto[spaceIdx].Dequeue());
                for (int k = 0; k < rest.Count; k++)
                    _txCrypto[spaceIdx].Enqueue(rest[k]);

                frames.Add(head);
                usedBytes += head.GetEncodedLength();
                break;
            }
            else
            {
                break;
            }
        }

        if (space == QuicPacketNumberSpace.Application)
        {
            while (_txAppControlFrames.Count > 0)
            {
                QuicFrame ctrl = _txAppControlFrames.Peek();
                int len = ctrl.GetEncodedLength();
                if (usedBytes + len > maxFramesBytes)
                    break;
                frames.Add(_txAppControlFrames.Dequeue());
                usedBytes += len;
            }

            int checkedCount = _txReadyStreams.Count;
            while (checkedCount-- > 0 && usedBytes + 16 < maxFramesBytes && _txReadyStreams.Count > 0)
            {
                QuicStream st = _txReadyStreams.Dequeue();
                _txReadyStreamIds.Remove(st.StreamId);

                ulong connAvail = _peerMaxData > _connBytesSent ? _peerMaxData - _connBytesSent : 0UL;
                QuicStreamFrame? sf = st.DequeueOutboundFrame(maxFramesBytes - usedBytes, connAvail, out QuicStreamDataBlockedFrame? streamBlockedFrame);
                if (streamBlockedFrame is not null)
                    _txAppControlFrames.Enqueue(streamBlockedFrame);
                if (sf is not null)
                {
                    frames.Add(sf);
                    usedBytes += sf.GetEncodedLength();
                    _connBytesSent += (ulong)sf.Data.Length;
                }
                else if (connAvail == 0 && !_connDataBlockedSent)
                {
                    _connDataBlockedSent = true;
                    var blocked = new QuicDataBlockedFrame(_peerMaxData);
                    if (usedBytes + blocked.GetEncodedLength() <= maxFramesBytes)
                    {
                        frames.Add(blocked);
                        usedBytes += blocked.GetEncodedLength();
                    }
                }

                if (st.HasPendingOutboundData(_peerMaxData > _connBytesSent ? _peerMaxData - _connBytesSent : 0UL) &&
                    _txReadyStreamIds.Add(st.StreamId))
                {
                    _txReadyStreams.Enqueue(st);
                }
            }
        }

        if (frames.Count == 0)
            return;

        if (space == QuicPacketNumberSpace.Initial)
        {
            int actualTotal = coalescedDatagram.Count + exactFixedOverhead + usedBytes;
            if (actualTotal < ChaosFrames.MinInitialDatagramBytes)
            {
                int padLen = ChaosFrames.MinInitialDatagramBytes - actualTotal;
                frames.Add(new QuicPaddingFrame(padLen));
            }
            else if (usedBytes < 4 - pnLen)
            {
                frames.Add(new QuicPaddingFrame((4 - pnLen) - usedBytes));
            }
        }

        byte[] packet = BuildAndRecordPacketLocked(space, writeKeys, frames);
        coalescedDatagram.AddRange(packet);
    }

    private byte[] BuildAndRecordPacketLocked(QuicPacketNumberSpace space, QuicKeySet writeKeys, List<QuicFrame> frames)
    {
        int spaceIdx = (int)space;
        ulong pn = _txNextPn[spaceIdx]++;
        long largestAcked = _lossRecovery.GetLargestAckedPacket(space) is { } la ? (long)la : -1L;
        int pnLen = QuicCrypto.GetRequiredPacketNumberLength(pn, largestAcked);
        byte[] payload = QuicFrameCodec.Encode(frames);

        byte[] packet = space switch
        {
            QuicPacketNumberSpace.Initial => QuicPacketCodec.BuildLongHeaderPacket(
                QuicLongPacketType.Initial, _remoteDcid, _localScid, _retryToken, pn, pnLen, payload, writeKeys),
            QuicPacketNumberSpace.Handshake => QuicPacketCodec.BuildLongHeaderPacket(
                QuicLongPacketType.Handshake, _remoteDcid, _localScid, ReadOnlySpan<byte>.Empty, pn, pnLen, payload, writeKeys),
            _ => QuicPacketCodec.BuildShortHeaderPacket(_remoteDcid, pn, pnLen, _appWriteKeyPhase, payload, writeKeys),
        };

        bool ackEliciting = false;
        bool inFlight = false;
        for (int i = 0; i < frames.Count; i++)
        {
            if (frames[i].IsAckEliciting)
                ackEliciting = true;
            if (frames[i] is not QuicAckFrame)
                inFlight = true;
        }

        _lossRecovery.OnPacketSent(space, pn, packet.Length, ackEliciting, inFlight, _clock.Elapsed, frames);
        return packet;
    }

    private void FailAndCloseTransport(ulong quicErrorCode, string message, Exception? inner = null)
    {
        Exception ex = inner is CertificateValidationException or TlsException
            ? inner
            : new QuicException(quicErrorCode, false, message, inner);

        _ = CloseAsync(quicErrorCode, isApplicationError: false, reason: message);
        FailAllWaiters(ex);
    }

    private void FailWithProtocolError(Exception ex)
    {
        if (Volatile.Read(ref _closed) != 0)
            return;
        FailAllWaiters(ex);
    }

    private void FailAllWaiters(Exception ex)
    {
        Interlocked.CompareExchange(ref _terminalError, ex, null);
        _handshakeTcs.TrySetException(ex);

        lock (_stateLock)
        {
            _bidiStreamLimitWaiter?.TrySetException(ex);
            _bidiStreamLimitWaiter = null;
            _uniStreamLimitWaiter?.TrySetException(ex);
            _uniStreamLimitWaiter = null;
        }

        foreach (QuicStream stream in _streams.Values)
            stream.FailConnection(ex);

        _serverUniAccept.Writer.TryComplete();
        _serverBiAccept.Writer.TryComplete();
        _connCts.Cancel();
    }

    private void ThrowIfClosedOrFailed()
    {
        if (_terminalError is not null)
            throw _terminalError;
        if (Volatile.Read(ref _closed) != 0)
            throw new QuicException(QuicErrorCode.NoError, true, "QUIC connection is closed.");
    }

    public async ValueTask DisposeAsync()
    {
        if (Volatile.Read(ref _closed) == 0)
            await CloseAsync(QuicErrorCode.NoError, isApplicationError: true, reason: "disposed").ConfigureAwait(false);

        _connCts.Cancel();
        SignalTx();

        if (_recvTask is not null)
        {
            try { await _recvTask.ConfigureAwait(false); } catch { }
        }
        if (_txTask is not null)
        {
            try { await _txTask.ConfigureAwait(false); } catch { }
        }

        _initialReadKeys?.Clear();
        _initialWriteKeys?.Clear();
        _handshakeReadKeys?.Clear();
        _handshakeWriteKeys?.Clear();
        _appReadKeys?.Clear();
        _appWriteKeys?.Clear();
        _appPrevReadKeys?.Clear();
        _appNextReadKeys?.Clear();

        _tls.Dispose();
        if (_ownsTransport)
            await _transport.DisposeAsync().ConfigureAwait(false);

        _txWake.Dispose();
        _connCts.Dispose();
    }
}
