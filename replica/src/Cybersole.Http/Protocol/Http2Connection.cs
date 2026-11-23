using System.Buffers.Binary;
using System.Collections.Concurrent;
using Cybersole.Http.Profiles;

namespace Cybersole.Http.Protocol;

/// <summary>
/// Pure managed RFC 9113 multiplexed client HTTP/2 connection implementing <see cref="IMultiplexedConnection"/>.
/// Emits profile-ordered <c>SETTINGS</c>, <c>WINDOW_UPDATE</c>, startup <c>PRIORITY</c>, and HPACK <c>HEADERS</c>
/// frames, supports <c>CONTINUATION</c>, bi-directional flow control, <c>1xx</c> skipping, trailers,
/// <c>RST_STREAM</c>, <c>GOAWAY</c>, <c>PING</c>, and response decompression via <see cref="HttpContentDecoder"/>.
/// </summary>
public sealed class Http2Connection : IMultiplexedConnection
{
    public const int DefaultInitialWindowSize = 65_535;
    public const int DefaultMaxFrameSize = 16_384;
    public const int MaxAllowedFrameSize = 16_777_215;
    public const int DecoderMaxTableCeiling = 1_048_576;

    // RFC 9113 §3.5 Client Connection Preface (24 bytes)
    private static readonly byte[] ClientPreface = "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"u8.ToArray();

    // Frame Types (RFC 9113 §6)
    private const byte FrameData = 0x00;
    private const byte FrameHeaders = 0x01;
    private const byte FramePriority = 0x02;
    private const byte FrameRstStream = 0x03;
    private const byte FrameSettings = 0x04;
    private const byte FramePushPromise = 0x05;
    private const byte FramePing = 0x06;
    private const byte FrameGoAway = 0x07;
    private const byte FrameWindowUpdate = 0x08;
    private const byte FrameContinuation = 0x09;

    // Frame Flags
    private const byte FlagEndStream = 0x01;
    private const byte FlagAck = 0x01;
    private const byte FlagEndHeaders = 0x04;
    private const byte FlagPadded = 0x08;
    private const byte FlagPriority = 0x20;

    // Error Codes (RFC 9113 §7)
    private const uint ErrNoError = 0x00;
    private const uint ErrProtocolError = 0x01;
    private const uint ErrFlowControlError = 0x03;
    private const uint ErrFrameSizeError = 0x06;
    private const uint ErrRefusedStream = 0x07;
    private const uint ErrCancel = 0x08;

    private sealed class Http2StreamState
    {
        public Http2StreamState(int streamId, PureHttpRequest request, long sendWindow, long recvWindow)
        {
            StreamId = streamId;
            Request = request;
            SendWindow = sendWindow;
            RecvWindow = recvWindow;
        }

        public int StreamId { get; }
        public PureHttpRequest Request { get; }
        public TaskCompletionSource<PureHttpResponse> ResponseTcs { get; } =
            new(TaskCreationOptions.RunContinuationsAsynchronously);

        public long SendWindow;
        public long RecvWindow;
        public long ConsumedSinceUpdate;
        public Exception? TerminalError;

        public MemoryStream HeaderBlockBuffer { get; } = new();
        public bool PendingEndStreamOnHeaders;
        public bool HeadersReceived;
        public int StatusCode;
        public List<PureHttpHeader> ResponseHeaders { get; } = new();
        public List<PureHttpHeader> Trailers { get; } = new();
        public MemoryStream BodyBuffer { get; } = new();
        public bool Completed;
    }

    private readonly Stream _stream;
    private readonly BufferedStreamReader _reader;
    private readonly Http2SettingsSpec _settingsSpec;
    private readonly bool _leaveStreamOpen;
    private readonly HpackEncoder _encoder;
    private readonly HpackDecoder _decoder;

    private readonly SemaphoreSlim _startLock = new(1, 1);
    private readonly SemaphoreSlim _writeLock = new(1, 1);
    private readonly object _stateLock = new();
    private readonly object _flowLock = new();

    private readonly ConcurrentDictionary<int, Http2StreamState> _streams = new();
    private readonly List<TaskCompletionSource> _windowWaiters = new();
    private readonly List<TaskCompletionSource> _concurrencyWaiters = new();
    private readonly CancellationTokenSource _readLoopCts = new();

    private Task? _readLoopTask;
    private bool _started;
    private bool _disposed;
    private volatile bool _goAwayReceived;
    private volatile bool _connectionDead;
    private Exception? _fatalError;

    private long _nextStreamId;
    private int _peerMaxConcurrentStreams = 100;
    private int _peerInitialStreamWindowSize = DefaultInitialWindowSize;
    private int _peerMaxFrameSize = DefaultMaxFrameSize;
    private long _peerConnSendWindow = DefaultInitialWindowSize;

    private int _localMaxFrameSize = DefaultMaxFrameSize;
    private int _localInitialStreamWindowSize = DefaultInitialWindowSize;
    private long _localConnRecvWindowTarget = DefaultInitialWindowSize;
    private long _localConnRecvWindow = DefaultInitialWindowSize;
    private long _localConnConsumedSinceUpdate;

    private int _lastPeerStreamId;
    private DateTimeOffset _lastUsedUtc = DateTimeOffset.UtcNow;

    public Http2Connection(
        Stream stream,
        ConnectionKey key,
        Http2SettingsSpec? settingsSpec = null,
        bool leaveStreamOpen = false)
    {
        _stream = stream ?? throw new ArgumentNullException(nameof(stream));
        Key = key;
        _settingsSpec = settingsSpec ?? new Http2SettingsSpec(
            Array.AsReadOnly(Array.Empty<(ushort Id, uint Value)>()),
            Http2SettingsSpec.DefaultConnectionFlow,
            Http2SettingsSpec.DefaultFallbackPseudoHeaderOrder);
        _leaveStreamOpen = leaveStreamOpen;

        _reader = new BufferedStreamReader(_stream, BufferedStreamReader.DefaultBufferSize, leaveOpen: true);
        _encoder = new HpackEncoder(maxDynamicTableSize: 4096, huffmanMode: HpackHuffmanMode.IfSmaller);

        int localHeaderTableMax = 4096;
        int localMaxHeaderListSize = 262_144;
        for (int i = 0; i < _settingsSpec.Settings.Count; i++)
        {
            (ushort id, uint val) = _settingsSpec.Settings[i];
            switch (id)
            {
                case Http2SettingId.HeaderTableSize:
                    localHeaderTableMax = (int)Math.Clamp((long)val, 4096L, DecoderMaxTableCeiling);
                    break;
                case Http2SettingId.InitialWindowSize:
                    _localInitialStreamWindowSize = (int)Math.Min(val, int.MaxValue);
                    break;
                case Http2SettingId.MaxFrameSize:
                    if (val is >= DefaultMaxFrameSize and <= MaxAllowedFrameSize)
                        _localMaxFrameSize = (int)val;
                    break;
                case Http2SettingId.MaxHeaderListSize:
                    localMaxHeaderListSize = (int)Math.Clamp((long)val, 4096L, 16L * 1024 * 1024);
                    break;
            }
        }

        _decoder = new HpackDecoder(localHeaderTableMax, localMaxHeaderListSize);
        _nextStreamId = _settingsSpec.EffectiveInitialNextStreamId;
    }

    public static async Task<Http2Connection> ConnectAsync(
        Stream stream,
        ConnectionKey key,
        Http2SettingsSpec? settingsSpec = null,
        bool leaveStreamOpen = false,
        CancellationToken cancellationToken = default)
    {
        var conn = new Http2Connection(stream, key, settingsSpec, leaveStreamOpen);
        try
        {
            await conn.StartAsync(cancellationToken).ConfigureAwait(false);
            return conn;
        }
        catch
        {
            await conn.DisposeAsync().ConfigureAwait(false);
            throw;
        }
    }

    public string ProtocolVersion => "h2";
    public ConnectionKey Key { get; }
    public bool IsUsable => !_disposed && !_goAwayReceived && !_connectionDead;
    public bool SupportsMultiplexing => true;
    public int MaxConcurrentStreams => Volatile.Read(ref _peerMaxConcurrentStreams);
    public int ActiveStreams => _streams.Count;
    public DateTimeOffset LastUsedUtc => _lastUsedUtc;

    public bool CanAcceptNewStream()
        => IsUsable && _streams.Count < MaxConcurrentStreams && _nextStreamId <= 0x7FFF_FFFFL;

    public async Task StartAsync(CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        if (_started)
            return;

        await _startLock.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            if (_started)
                return;

            byte[] initialBurst = BuildConnectionPrefacePayload();
            await _writeLock.WaitAsync(cancellationToken).ConfigureAwait(false);
            try
            {
                await _stream.WriteAsync(initialBurst, cancellationToken).ConfigureAwait(false);
                await _stream.FlushAsync(cancellationToken).ConfigureAwait(false);
            }
            finally
            {
                _writeLock.Release();
            }

            _readLoopTask = Task.Run(() => ReadLoopAsync(_readLoopCts.Token), CancellationToken.None);
            _started = true;
        }
        finally
        {
            _startLock.Release();
        }
    }

    public async Task<PureHttpResponse> SendAsync(PureHttpRequest request, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(request);
        ObjectDisposedException.ThrowIf(_disposed, this);

        if (!_started)
            await StartAsync(cancellationToken).ConfigureAwait(false);

        using CancellationTokenSource? timeoutCts =
            request.RequestTimeout is { } reqTimeout && reqTimeout > TimeSpan.Zero && reqTimeout != Timeout.InfiniteTimeSpan
                ? new CancellationTokenSource(reqTimeout)
                : null;
        using CancellationTokenSource? linkedCts = timeoutCts is not null
            ? CancellationTokenSource.CreateLinkedTokenSource(cancellationToken, timeoutCts.Token)
            : null;
        CancellationToken effectiveCt = linkedCts?.Token ?? cancellationToken;

        Http2StreamState? streamState = null;
        bool registered = false;

        try
        {
            await WaitForStreamSlotAsync(effectiveCt).ConfigureAwait(false);

            await _writeLock.WaitAsync(effectiveCt).ConfigureAwait(false);
            try
            {
                if (_disposed || _goAwayReceived || _connectionDead)
                {
                    throw new Http2Exception(
                        ErrRefusedStream,
                        isStreamReset: false,
                        "HTTP/2 connection is no longer accepting new streams.",
                        _fatalError,
                        retryable: true);
                }

                if (_nextStreamId > 0x7FFF_FFFFL)
                {
                    _connectionDead = true;
                    throw new Http2Exception(
                        ErrRefusedStream,
                        isStreamReset: false,
                        "HTTP/2 client stream identifiers exhausted.",
                        retryable: true);
                }

                int streamId = (int)_nextStreamId;
                _nextStreamId += 2;
                _lastUsedUtc = DateTimeOffset.UtcNow;

                byte[] headerBlock = _encoder.EncodeHeaders(request, _settingsSpec);
                lock (_flowLock)
                {
                    streamState = new Http2StreamState(streamId, request, _peerInitialStreamWindowSize, _localInitialStreamWindowSize);
                    _streams[streamId] = streamState;
                }
                registered = true;

                bool endStreamOnHeaders = request.Body.IsEmpty;
                await WriteHeadersAndContinuationsAsync(streamId, headerBlock, endStreamOnHeaders, effectiveCt).ConfigureAwait(false);
                await _stream.FlushAsync(effectiveCt).ConfigureAwait(false);
            }
            finally
            {
                _writeLock.Release();
            }

            if (!request.Body.IsEmpty)
            {
                int bodyOffset = 0;
                while (bodyOffset < request.Body.Length)
                {
                    int remaining = request.Body.Length - bodyOffset;
                    int chunkLen = await ReserveSendWindowAsync(streamState, remaining, effectiveCt).ConfigureAwait(false);
                    bool isLastChunk = bodyOffset + chunkLen == request.Body.Length;

                    await _writeLock.WaitAsync(effectiveCt).ConfigureAwait(false);
                    try
                    {
                        byte flags = isLastChunk ? FlagEndStream : (byte)0;
                        await WriteFrameAsync(
                            FrameData,
                            flags,
                            streamState.StreamId,
                            request.Body.Span.Slice(bodyOffset, chunkLen),
                            effectiveCt).ConfigureAwait(false);
                        if (isLastChunk)
                            await _stream.FlushAsync(effectiveCt).ConfigureAwait(false);
                    }
                    finally
                    {
                        _writeLock.Release();
                    }

                    bodyOffset += chunkLen;
                }
            }

            PureHttpResponse response = await streamState.ResponseTcs.Task.WaitAsync(effectiveCt).ConfigureAwait(false);
            _lastUsedUtc = DateTimeOffset.UtcNow;
            return response;
        }
        catch (OperationCanceledException) when (timeoutCts is not null && timeoutCts.IsCancellationRequested && !cancellationToken.IsCancellationRequested)
        {
            if (streamState is not null)
                await TrySendBestEffortRstStreamAsync(streamState.StreamId, ErrCancel).ConfigureAwait(false);
            throw new TimeoutException($"HTTP/2 request timed out after {request.RequestTimeout!.Value.TotalSeconds:0.###}s.");
        }
        catch (OperationCanceledException)
        {
            if (streamState is not null)
                await TrySendBestEffortRstStreamAsync(streamState.StreamId, ErrCancel).ConfigureAwait(false);
            throw;
        }
        finally
        {
            if (registered && streamState is not null)
            {
                _streams.TryRemove(streamState.StreamId, out _);
                WakeConcurrencyWaiters();
            }
        }
    }

    private byte[] BuildConnectionPrefacePayload()
    {
        using var ms = new MemoryStream(256);
        ms.Write(ClientPreface);

        // SETTINGS frame in exact Http2SettingsSpec.Settings order
        var settingsPayload = new byte[_settingsSpec.Settings.Count * 6];
        for (int i = 0; i < _settingsSpec.Settings.Count; i++)
        {
            (ushort id, uint val) = _settingsSpec.Settings[i];
            int off = i * 6;
            BinaryPrimitives.WriteUInt16BigEndian(settingsPayload.AsSpan(off, 2), id);
            BinaryPrimitives.WriteUInt32BigEndian(settingsPayload.AsSpan(off + 2, 4), val);
        }
        AppendFrame(ms, FrameSettings, 0, 0, settingsPayload);

        if (_settingsSpec.ConnectionFlow > DefaultInitialWindowSize)
        {
            uint increment = _settingsSpec.ConnectionFlow - DefaultInitialWindowSize;
            Span<byte> wu = stackalloc byte[4];
            BinaryPrimitives.WriteUInt32BigEndian(wu, increment);
            AppendFrame(ms, FrameWindowUpdate, 0, 0, wu);
            _localConnRecvWindowTarget = _settingsSpec.ConnectionFlow;
            _localConnRecvWindow = _settingsSpec.ConnectionFlow;
        }

        Span<byte> pBytes = stackalloc byte[5];
        for (int i = 0; i < _settingsSpec.PriorityFrames.Count; i++)
        {
            Http2PriorityFrame pf = _settingsSpec.PriorityFrames[i];
            uint depField = (pf.StreamDep & 0x7FFF_FFFFu) | (pf.Exclusive ? 0x8000_0000u : 0u);
            BinaryPrimitives.WriteUInt32BigEndian(pBytes[..4], depField);
            pBytes[4] = pf.Weight;
            AppendFrame(ms, FramePriority, 0, (int)pf.StreamId, pBytes);
        }

        return ms.ToArray();
    }

    private async Task WriteHeadersAndContinuationsAsync(
        int streamId,
        byte[] headerBlock,
        bool endStream,
        CancellationToken cancellationToken)
    {
        Http2HeaderPriority hp = _settingsSpec.EffectiveHeaderPriority;
        bool emitPriority = !_settingsSpec.NoRfc7540Priorities && !hp.IsSuppressed;
        int priorityPrefixLen = emitPriority ? 5 : 0;

        int maxFirstPayload = Math.Max(1, _peerMaxFrameSize - priorityPrefixLen);
        int firstHeaderBytes = Math.Min(headerBlock.Length, maxFirstPayload);
        bool singleFrame = firstHeaderBytes == headerBlock.Length;

        byte firstFlags = 0;
        if (endStream)
            firstFlags |= FlagEndStream;
        if (emitPriority)
            firstFlags |= FlagPriority;
        if (singleFrame)
            firstFlags |= FlagEndHeaders;

        var firstPayload = new byte[priorityPrefixLen + firstHeaderBytes];
        if (emitPriority)
        {
            uint depField = (hp.StreamDep & 0x7FFF_FFFFu) | (hp.Exclusive ? 0x8000_0000u : 0u);
            BinaryPrimitives.WriteUInt32BigEndian(firstPayload.AsSpan(0, 4), depField);
            firstPayload[4] = hp.Weight;
        }
        if (firstHeaderBytes > 0)
            headerBlock.AsSpan(0, firstHeaderBytes).CopyTo(firstPayload.AsSpan(priorityPrefixLen));

        await WriteFrameAsync(FrameHeaders, firstFlags, streamId, firstPayload, cancellationToken).ConfigureAwait(false);

        int offset = firstHeaderBytes;
        while (offset < headerBlock.Length)
        {
            int chunkLen = Math.Min(headerBlock.Length - offset, _peerMaxFrameSize);
            bool isLast = offset + chunkLen == headerBlock.Length;
            byte contFlags = isLast ? FlagEndHeaders : (byte)0;
            await WriteFrameAsync(
                FrameContinuation,
                contFlags,
                streamId,
                headerBlock.AsSpan(offset, chunkLen),
                cancellationToken).ConfigureAwait(false);
            offset += chunkLen;
        }
    }

    private Task WriteFrameAsync(
        byte type,
        byte flags,
        int streamId,
        ReadOnlySpan<byte> payload,
        CancellationToken cancellationToken)
    {
        var frame = new byte[9 + payload.Length];
        int len = payload.Length;
        frame[0] = (byte)(len >> 16);
        frame[1] = (byte)(len >> 8);
        frame[2] = (byte)len;
        frame[3] = type;
        frame[4] = flags;
        BinaryPrimitives.WriteInt32BigEndian(frame.AsSpan(5, 4), streamId & 0x7FFF_FFFF);
        if (len > 0)
            payload.CopyTo(frame.AsSpan(9));

        return _stream.WriteAsync(frame, cancellationToken).AsTask();
    }

    private static void AppendFrame(MemoryStream ms, byte type, byte flags, int streamId, ReadOnlySpan<byte> payload)
    {
        Span<byte> hdr = stackalloc byte[9];
        int len = payload.Length;
        hdr[0] = (byte)(len >> 16);
        hdr[1] = (byte)(len >> 8);
        hdr[2] = (byte)len;
        hdr[3] = type;
        hdr[4] = flags;
        BinaryPrimitives.WriteInt32BigEndian(hdr.Slice(5, 4), streamId & 0x7FFF_FFFF);
        ms.Write(hdr);
        if (len > 0)
            ms.Write(payload);
    }

    private async Task WaitForStreamSlotAsync(CancellationToken cancellationToken)
    {
        while (true)
        {
            if (_disposed || _goAwayReceived || _connectionDead)
            {
                throw new Http2Exception(
                    ErrRefusedStream,
                    isStreamReset: false,
                    "HTTP/2 connection cannot accept new streams.",
                    _fatalError,
                    retryable: true);
            }

            if (_streams.Count < MaxConcurrentStreams)
                return;

            var waiter = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
            lock (_stateLock)
            {
                if (_disposed || _goAwayReceived || _connectionDead || _streams.Count < MaxConcurrentStreams)
                    continue;
                _concurrencyWaiters.Add(waiter);
            }

            try
            {
                await waiter.Task.WaitAsync(cancellationToken).ConfigureAwait(false);
            }
            finally
            {
                lock (_stateLock)
                    _concurrencyWaiters.Remove(waiter);
            }
        }
    }

    private async Task<int> ReserveSendWindowAsync(Http2StreamState streamState, int desiredBytes, CancellationToken cancellationToken)
    {
        while (true)
        {
            TaskCompletionSource? waiter = null;
            lock (_flowLock)
            {
                if (streamState.TerminalError is not null)
                    throw streamState.TerminalError;
                if (_connectionDead || _disposed)
                {
                    throw new Http2Exception(
                        ErrNoError,
                        isStreamReset: false,
                        "HTTP/2 connection closed while sending request body.",
                        _fatalError,
                        retryable: true);
                }

                long available = Math.Min(streamState.SendWindow, _peerConnSendWindow);
                if (available > 0)
                {
                    int take = (int)Math.Min(desiredBytes, Math.Min(_peerMaxFrameSize, available));
                    streamState.SendWindow -= take;
                    _peerConnSendWindow -= take;
                    return take;
                }

                waiter = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
                _windowWaiters.Add(waiter);
            }

            try
            {
                await waiter.Task.WaitAsync(cancellationToken).ConfigureAwait(false);
            }
            finally
            {
                lock (_flowLock)
                    _windowWaiters.Remove(waiter);
            }
        }
    }

    private async Task ReadLoopAsync(CancellationToken cancellationToken)
    {
        var headerBuf = new byte[9];
        int continuingStreamId = 0;
        Http2StreamState? orphanContinuingStream = null;

        try
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                int firstByte = await _reader.PeekByteAsync(cancellationToken).ConfigureAwait(false);
                if (firstByte < 0)
                    break;

                await _reader.ReadExactAsync(headerBuf, cancellationToken).ConfigureAwait(false);
                int length = (headerBuf[0] << 16) | (headerBuf[1] << 8) | headerBuf[2];
                byte type = headerBuf[3];
                byte flags = headerBuf[4];
                int streamId = BinaryPrimitives.ReadInt32BigEndian(headerBuf.AsSpan(5, 4)) & 0x7FFF_FFFF;

                if (length > _localMaxFrameSize)
                    throw new Http2Exception(ErrFrameSizeError, isStreamReset: false, $"http2: frame too large ({length} bytes)");

                byte[] payload = length > 0 ? new byte[length] : Array.Empty<byte>();
                if (length > 0)
                    await _reader.ReadExactAsync(payload, cancellationToken).ConfigureAwait(false);

                if (continuingStreamId != 0 && (type != FrameContinuation || streamId != continuingStreamId))
                {
                    throw new Http2Exception(
                        ErrProtocolError,
                        isStreamReset: false,
                        $"Expected CONTINUATION frame for stream {continuingStreamId}, received frame type {type} on stream {streamId}.");
                }

                switch (type)
                {
                    case FrameSettings:
                        await HandleSettingsFrameAsync(flags, streamId, payload, cancellationToken).ConfigureAwait(false);
                        break;

                    case FramePing:
                        await HandlePingFrameAsync(flags, streamId, payload, cancellationToken).ConfigureAwait(false);
                        break;

                    case FrameWindowUpdate:
                        HandleWindowUpdateFrame(streamId, payload);
                        break;

                    case FrameHeaders:
                        HandleHeadersFrame(
                            flags,
                            streamId,
                            payload,
                            ref continuingStreamId,
                            ref orphanContinuingStream);
                        break;

                    case FrameContinuation:
                        HandleContinuationFrame(
                            flags,
                            streamId,
                            payload,
                            ref continuingStreamId,
                            ref orphanContinuingStream);
                        break;

                    case FrameData:
                        await HandleDataFrameAsync(flags, streamId, payload, cancellationToken).ConfigureAwait(false);
                        break;

                    case FrameRstStream:
                        HandleRstStreamFrame(streamId, payload);
                        break;

                    case FrameGoAway:
                        HandleGoAwayFrame(streamId, payload);
                        break;

                    case FramePriority:
                        if (streamId == 0 || payload.Length != 5)
                            throw new Http2Exception(ErrFrameSizeError, isStreamReset: false, "Invalid HTTP/2 PRIORITY frame.");
                        break;

                    case FramePushPromise:
                        await HandlePushPromiseAsync(flags, streamId, payload, cancellationToken).ConfigureAwait(false);
                        break;

                    default:
                        // Unknown extension frames MUST be ignored per RFC 9113 §4.1.
                        break;
                }
            }

            if (continuingStreamId != 0)
                throw new Http2Exception(ErrProtocolError, isStreamReset: false, "http2: truncated header block at EOF");

            var eofError = new Http2Exception(
                ErrNoError,
                isStreamReset: false,
                "http2: server closed the connection",
                retryable: true);
            FailConnection(eofError);
        }
        catch (OperationCanceledException) when (_disposed || cancellationToken.IsCancellationRequested)
        {
            FailConnection(new Http2Exception(ErrCancel, isStreamReset: false, "HTTP/2 connection closed.", retryable: false));
        }
        catch (Http2Exception h2Ex)
        {
            if (!h2Ex.IsStreamReset)
                await TrySendBestEffortGoAwayAsync(h2Ex.H2ErrorCode).ConfigureAwait(false);
            FailConnection(h2Ex);
        }
        catch (Exception ex)
        {
            FailConnection(new Http2Exception(
                ErrNoError,
                isStreamReset: false,
                $"http2: server closed the connection ({ex.Message})",
                ex,
                retryable: true));
        }
    }

    private async Task HandleSettingsFrameAsync(byte flags, int streamId, byte[] payload, CancellationToken cancellationToken)
    {
        if (streamId != 0)
            throw new Http2Exception(ErrProtocolError, isStreamReset: false, "SETTINGS frame must have stream ID 0.");

        if ((flags & FlagAck) != 0)
        {
            if (payload.Length != 0)
                throw new Http2Exception(ErrFrameSizeError, isStreamReset: false, "SETTINGS ACK frame must have empty payload.");
            return;
        }

        if (payload.Length % 6 != 0)
            throw new Http2Exception(ErrFrameSizeError, isStreamReset: false, "SETTINGS payload length must be a multiple of 6.");

        bool wakeWaiters = false;
        for (int off = 0; off < payload.Length; off += 6)
        {
            ushort id = BinaryPrimitives.ReadUInt16BigEndian(payload.AsSpan(off, 2));
            uint val = BinaryPrimitives.ReadUInt32BigEndian(payload.AsSpan(off + 2, 4));

            switch (id)
            {
                case Http2SettingId.HeaderTableSize:
                    await _writeLock.WaitAsync(cancellationToken).ConfigureAwait(false);
                    try
                    {
                        _encoder.SetMaxTableSize((int)Math.Min(val, DecoderMaxTableCeiling));
                    }
                    finally
                    {
                        _writeLock.Release();
                    }
                    break;

                case Http2SettingId.MaxConcurrentStreams:
                    int prevMax = Interlocked.Exchange(ref _peerMaxConcurrentStreams, (int)Math.Min(val, int.MaxValue));
                    if ((int)Math.Min(val, int.MaxValue) > prevMax)
                        WakeConcurrencyWaiters();
                    break;

                case Http2SettingId.InitialWindowSize:
                    if (val > 0x7FFF_FFFFu)
                        throw new Http2Exception(ErrFlowControlError, isStreamReset: false, "SETTINGS_INITIAL_WINDOW_SIZE exceeded 2^31 - 1.");

                    lock (_flowLock)
                    {
                        long delta = (long)val - _peerInitialStreamWindowSize;
                        _peerInitialStreamWindowSize = (int)val;
                        foreach (Http2StreamState s in _streams.Values)
                        {
                            long updated = s.SendWindow + delta;
                            if (updated > 0x7FFF_FFFFL)
                                throw new Http2Exception(ErrFlowControlError, isStreamReset: false, "Stream send window overflow after SETTINGS update.");
                            s.SendWindow = updated;
                        }
                        if (delta > 0)
                            wakeWaiters = true;
                    }
                    break;

                case Http2SettingId.MaxFrameSize:
                    if (val is < DefaultMaxFrameSize or > MaxAllowedFrameSize)
                        throw new Http2Exception(ErrProtocolError, isStreamReset: false, $"Invalid SETTINGS_MAX_FRAME_SIZE {val}.");
                    _peerMaxFrameSize = (int)val;
                    break;
            }
        }

        if (wakeWaiters)
            WakeWindowWaiters();

        await _writeLock.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            await WriteFrameAsync(FrameSettings, FlagAck, 0, ReadOnlySpan<byte>.Empty, cancellationToken).ConfigureAwait(false);
            await _stream.FlushAsync(cancellationToken).ConfigureAwait(false);
        }
        finally
        {
            _writeLock.Release();
        }
    }

    private async Task HandlePingFrameAsync(byte flags, int streamId, byte[] payload, CancellationToken cancellationToken)
    {
        if (streamId != 0)
            throw new Http2Exception(ErrProtocolError, isStreamReset: false, "PING frame must have stream ID 0.");
        if (payload.Length != 8)
            throw new Http2Exception(ErrFrameSizeError, isStreamReset: false, "PING frame payload must be 8 bytes.");

        if ((flags & FlagAck) != 0)
            return;

        await _writeLock.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            await WriteFrameAsync(FramePing, FlagAck, 0, payload, cancellationToken).ConfigureAwait(false);
            await _stream.FlushAsync(cancellationToken).ConfigureAwait(false);
        }
        finally
        {
            _writeLock.Release();
        }
    }

    private void HandleWindowUpdateFrame(int streamId, byte[] payload)
    {
        if (payload.Length != 4)
            throw new Http2Exception(ErrFrameSizeError, isStreamReset: false, "WINDOW_UPDATE frame must be 4 bytes.");

        uint increment = BinaryPrimitives.ReadUInt32BigEndian(payload) & 0x7FFF_FFFFu;
        if (increment == 0)
        {
            if (streamId == 0)
                throw new Http2Exception(ErrProtocolError, isStreamReset: false, "Connection WINDOW_UPDATE increment cannot be 0.");

            if (_streams.TryRemove(streamId, out Http2StreamState? target))
            {
                var err = new Http2Exception(ErrProtocolError, isStreamReset: true, $"Stream {streamId} received zero WINDOW_UPDATE increment.");
                FailStream(target, err);
            }
            return;
        }

        if (streamId == 0)
        {
            lock (_flowLock)
            {
                if (_peerConnSendWindow + increment > 0x7FFF_FFFFL)
                    throw new Http2Exception(ErrFlowControlError, isStreamReset: false, "Connection send window overflow.");
                _peerConnSendWindow += increment;
            }
            WakeWindowWaiters();
            return;
        }

        if (_streams.TryGetValue(streamId, out Http2StreamState? streamState))
        {
            bool overflow = false;
            lock (_flowLock)
            {
                if (streamState.SendWindow + increment > 0x7FFF_FFFFL)
                    overflow = true;
                else
                    streamState.SendWindow += increment;
            }

            if (overflow)
            {
                if (_streams.TryRemove(streamId, out _))
                    FailStream(streamState, new Http2Exception(ErrFlowControlError, isStreamReset: true, $"Stream {streamId} send window overflow."));
                return;
            }

            WakeWindowWaiters();
        }
    }

    private void HandleHeadersFrame(
        byte flags,
        int streamId,
        byte[] payload,
        ref int continuingStreamId,
        ref Http2StreamState? orphanStream)
    {
        if (streamId == 0)
            throw new Http2Exception(ErrProtocolError, isStreamReset: false, "HEADERS frame cannot have stream ID 0.");

        ReadOnlySpan<byte> span = payload;
        int offset = 0;
        int padLength = 0;

        if ((flags & FlagPadded) != 0)
        {
            if (span.Length < 1)
                throw new Http2Exception(ErrFrameSizeError, isStreamReset: false, "Padded HEADERS frame missing pad length.");
            padLength = span[offset++];
        }

        if ((flags & FlagPriority) != 0)
        {
            if (span.Length - offset < 5)
                throw new Http2Exception(ErrFrameSizeError, isStreamReset: false, "Priority HEADERS frame truncated.");
            offset += 5;
        }

        int fragLen = span.Length - offset - padLength;
        if (fragLen < 0)
            throw new Http2Exception(ErrProtocolError, isStreamReset: false, "HEADERS padding exceeds frame payload length.");

        _lastPeerStreamId = Math.Max(_lastPeerStreamId, streamId);

        if (!_streams.TryGetValue(streamId, out Http2StreamState? streamState))
        {
            // Keep HPACK decoder synchronized even if client already cancelled this stream.
            streamState = new Http2StreamState(streamId, new PureHttpRequest { Method = "GET", Uri = new Uri("https://invalid.local/") }, 0, 0);
            orphanStream = streamState;
        }
        else
        {
            orphanStream = null;
        }

        streamState.HeaderBlockBuffer.SetLength(0);
        if (fragLen > 0)
            streamState.HeaderBlockBuffer.Write(span.Slice(offset, fragLen));
        streamState.PendingEndStreamOnHeaders = (flags & FlagEndStream) != 0;

        if ((flags & FlagEndHeaders) == 0)
        {
            continuingStreamId = streamId;
            return;
        }

        FinishHeaderBlock(streamState, isOrphan: orphanStream is not null);
        orphanStream = null;
    }

    private void HandleContinuationFrame(
        byte flags,
        int streamId,
        byte[] payload,
        ref int continuingStreamId,
        ref Http2StreamState? orphanStream)
    {
        if (continuingStreamId == 0 || streamId != continuingStreamId)
            throw new Http2Exception(ErrProtocolError, isStreamReset: false, $"Unexpected CONTINUATION frame on stream {streamId}.");

        Http2StreamState? streamState = orphanStream;
        bool isOrphan = streamState is not null;
        if (streamState is null && !_streams.TryGetValue(streamId, out streamState))
            throw new Http2Exception(ErrProtocolError, isStreamReset: false, $"Missing stream state for CONTINUATION {streamId}.");

        if (streamState.HeaderBlockBuffer.Length + payload.Length > Math.Max(_decoder.MaxHeaderListSize * 2L, 4L * 1024 * 1024))
            throw new Http2Exception(ErrFrameSizeError, isStreamReset: false, "Assembled HPACK header block exceeded safety limit.");

        if (payload.Length > 0)
            streamState.HeaderBlockBuffer.Write(payload);

        if ((flags & FlagEndHeaders) != 0)
        {
            continuingStreamId = 0;
            orphanStream = null;
            FinishHeaderBlock(streamState, isOrphan);
        }
    }

    private void FinishHeaderBlock(Http2StreamState streamState, bool isOrphan)
    {
        byte[] blockBytes = streamState.HeaderBlockBuffer.ToArray();
        streamState.HeaderBlockBuffer.SetLength(0);

        List<PureHttpHeader> decoded = _decoder.DecodeHeaderBlock(blockBytes, validateHttp2Semantics: true);
        if (isOrphan)
            return;

        if (!streamState.HeadersReceived)
        {
            int statusCode = 0;
            bool foundStatus = false;
            var regularHeaders = new List<PureHttpHeader>(decoded.Count);

            for (int i = 0; i < decoded.Count; i++)
            {
                PureHttpHeader h = decoded[i];
                if (h.Name.StartsWith(':'))
                {
                    if (!string.Equals(h.Name, ":status", StringComparison.Ordinal) || foundStatus)
                    {
                        FailAndRemoveStream(streamState, new Http2Exception(ErrProtocolError, isStreamReset: true, $"Invalid response pseudo-header '{h.Name}'."));
                        return;
                    }

                    if (!int.TryParse(h.Value, out statusCode) || statusCode is < 100 or > 999)
                    {
                        FailAndRemoveStream(streamState, new Http2Exception(ErrProtocolError, isStreamReset: true, $"Invalid HTTP/2 :status value '{h.Value}'."));
                        return;
                    }
                    foundStatus = true;
                }
                else
                {
                    regularHeaders.Add(h);
                }
            }

            if (!foundStatus)
            {
                FailAndRemoveStream(streamState, new Http2Exception(ErrProtocolError, isStreamReset: true, "HTTP/2 response headers missing :status."));
                return;
            }

            if (statusCode is >= 100 and < 200)
            {
                if (streamState.PendingEndStreamOnHeaders)
                {
                    FailAndRemoveStream(streamState, new Http2Exception(ErrProtocolError, isStreamReset: true, "HTTP/2 1xx interim response cannot carry END_STREAM."));
                    return;
                }
                // Discard interim 1xx headers and wait for the final response headers.
                return;
            }

            streamState.StatusCode = statusCode;
            streamState.ResponseHeaders.AddRange(regularHeaders);
            streamState.HeadersReceived = true;
        }
        else
        {
            // Trailers (RFC 9113 §8.1): no pseudo-headers permitted and must terminate stream.
            for (int i = 0; i < decoded.Count; i++)
            {
                PureHttpHeader h = decoded[i];
                if (h.Name.StartsWith(':'))
                {
                    FailAndRemoveStream(streamState, new Http2Exception(ErrProtocolError, isStreamReset: true, $"HTTP/2 trailers cannot contain pseudo-header '{h.Name}'."));
                    return;
                }
                streamState.Trailers.Add(h);
            }
        }

        if (streamState.PendingEndStreamOnHeaders)
            CompleteStreamSuccess(streamState);
    }

    private async Task HandleDataFrameAsync(byte flags, int streamId, byte[] payload, CancellationToken cancellationToken)
    {
        if (streamId == 0)
            throw new Http2Exception(ErrProtocolError, isStreamReset: false, "DATA frame cannot have stream ID 0.");

        int offset = 0;
        int padLength = 0;

        if ((flags & FlagPadded) != 0)
        {
            if (payload.Length < 1)
                throw new Http2Exception(ErrFrameSizeError, isStreamReset: false, "Padded DATA frame missing pad length.");
            padLength = payload[offset++];
        }

        int dataLen = payload.Length - offset - padLength;
        if (dataLen < 0)
            throw new Http2Exception(ErrProtocolError, isStreamReset: false, "DATA padding exceeds payload length.");

        // Connection-level flow control covers the full frame payload including padding (RFC 9113 §6.9).
        uint connWindowUpdate = 0;
        if (payload.Length > 0)
        {
            _localConnRecvWindow -= payload.Length;
            _localConnConsumedSinceUpdate += payload.Length;
            long connThreshold = Math.Min(65_536L, Math.Max(16_384L, _localConnRecvWindowTarget / 2));
            if (_localConnConsumedSinceUpdate >= connThreshold || _localConnRecvWindow < connThreshold)
            {
                connWindowUpdate = (uint)Math.Min(0x7FFF_FFFFL, _localConnConsumedSinceUpdate);
                _localConnRecvWindow += connWindowUpdate;
                _localConnConsumedSinceUpdate -= connWindowUpdate;
            }
        }

        uint streamWindowUpdate = 0;
        bool endStream = (flags & FlagEndStream) != 0;

        if (_streams.TryGetValue(streamId, out Http2StreamState? streamState))
        {
            if (!streamState.HeadersReceived)
            {
                await TrySendBestEffortRstStreamAsync(streamId, ErrProtocolError).ConfigureAwait(false);
                FailAndRemoveStream(streamState, new Http2Exception(ErrProtocolError, isStreamReset: true, "Received DATA frame before response HEADERS."));
            }
            else if (streamState.BodyBuffer.Length + dataLen > streamState.Request.MaxResponseBodyBytes)
            {
                await TrySendBestEffortRstStreamAsync(streamId, ErrCancel).ConfigureAwait(false);
                FailAndRemoveStream(streamState, new PureHttpException(
                    HttpErrorKind.ResponseTooLarge,
                    $"HTTP/2 response body exceeded {streamState.Request.MaxResponseBodyBytes} bytes."));
            }
            else
            {
                if (dataLen > 0)
                    streamState.BodyBuffer.Write(payload, offset, dataLen);

                if (!endStream && payload.Length > 0)
                {
                    streamState.RecvWindow -= payload.Length;
                    streamState.ConsumedSinceUpdate += payload.Length;
                    long streamThreshold = Math.Min(32_768L, Math.Max(8_192L, _localInitialStreamWindowSize / 2L));
                    if (streamState.ConsumedSinceUpdate >= streamThreshold || streamState.RecvWindow < streamThreshold)
                    {
                        streamWindowUpdate = (uint)Math.Min(0x7FFF_FFFFL, streamState.ConsumedSinceUpdate);
                        streamState.RecvWindow += streamWindowUpdate;
                        streamState.ConsumedSinceUpdate -= streamWindowUpdate;
                    }
                }

                if (endStream)
                    CompleteStreamSuccess(streamState);
            }
        }

        if (connWindowUpdate > 0 || streamWindowUpdate > 0)
        {
            await _writeLock.WaitAsync(cancellationToken).ConfigureAwait(false);
            try
            {
                byte[] wuBuf = new byte[4];
                if (connWindowUpdate > 0)
                {
                    BinaryPrimitives.WriteUInt32BigEndian(wuBuf, connWindowUpdate);
                    await WriteFrameAsync(FrameWindowUpdate, 0, 0, wuBuf, cancellationToken).ConfigureAwait(false);
                }
                if (streamWindowUpdate > 0)
                {
                    BinaryPrimitives.WriteUInt32BigEndian(wuBuf, streamWindowUpdate);
                    await WriteFrameAsync(FrameWindowUpdate, 0, streamId, wuBuf, cancellationToken).ConfigureAwait(false);
                }
                await _stream.FlushAsync(cancellationToken).ConfigureAwait(false);
            }
            finally
            {
                _writeLock.Release();
            }
        }
    }

    private void HandleRstStreamFrame(int streamId, byte[] payload)
    {
        if (streamId == 0)
            throw new Http2Exception(ErrProtocolError, isStreamReset: false, "RST_STREAM frame cannot have stream ID 0.");
        if (payload.Length != 4)
            throw new Http2Exception(ErrFrameSizeError, isStreamReset: false, "RST_STREAM frame must be 4 bytes.");

        uint errorCode = BinaryPrimitives.ReadUInt32BigEndian(payload);
        if (_streams.TryRemove(streamId, out Http2StreamState? streamState))
        {
            bool retryable = errorCode == ErrRefusedStream;
            var ex = new Http2Exception(
                errorCode,
                isStreamReset: true,
                $"HTTP/2 stream {streamId} reset by peer (error 0x{errorCode:X}).",
                retryable: retryable);
            FailStream(streamState, ex);
            WakeConcurrencyWaiters();
        }
    }

    private void HandleGoAwayFrame(int streamId, byte[] payload)
    {
        if (streamId != 0)
            throw new Http2Exception(ErrProtocolError, isStreamReset: false, "GOAWAY frame must have stream ID 0.");
        if (payload.Length < 8)
            throw new Http2Exception(ErrFrameSizeError, isStreamReset: false, "GOAWAY frame must be at least 8 bytes.");

        int lastStreamId = (int)(BinaryPrimitives.ReadUInt32BigEndian(payload.AsSpan(0, 4)) & 0x7FFF_FFFFu);
        uint errorCode = BinaryPrimitives.ReadUInt32BigEndian(payload.AsSpan(4, 4));

        _goAwayReceived = true;
        WakeConcurrencyWaiters();

        foreach (KeyValuePair<int, Http2StreamState> kv in _streams)
        {
            if (kv.Key > lastStreamId && _streams.TryRemove(kv.Key, out Http2StreamState? unstarted))
            {
                var ex = new Http2Exception(
                    errorCode,
                    isStreamReset: false,
                    $"HTTP/2 peer sent GOAWAY (lastStreamId={lastStreamId}, error=0x{errorCode:X}).",
                    retryable: true);
                FailStream(unstarted, ex);
            }
        }
    }

    private async Task HandlePushPromiseAsync(byte flags, int streamId, byte[] payload, CancellationToken cancellationToken)
    {
        if (streamId == 0)
            throw new Http2Exception(ErrProtocolError, isStreamReset: false, "PUSH_PROMISE cannot have stream ID 0.");

        int offset = 0;
        int padLen = 0;
        if ((flags & FlagPadded) != 0)
        {
            if (payload.Length < 1)
                throw new Http2Exception(ErrFrameSizeError, isStreamReset: false, "Padded PUSH_PROMISE missing pad length.");
            padLen = payload[offset++];
        }

        if (payload.Length - offset - padLen < 4)
            throw new Http2Exception(ErrFrameSizeError, isStreamReset: false, "PUSH_PROMISE missing promised stream ID.");

        int promisedStreamId = (int)(BinaryPrimitives.ReadUInt32BigEndian(payload.AsSpan(offset, 4)) & 0x7FFF_FFFFu);
        offset += 4;

        if ((flags & FlagEndHeaders) != 0)
        {
            int fragLen = payload.Length - offset - padLen;
            if (fragLen > 0)
                _decoder.DecodeHeaderBlock(payload.AsSpan(offset, fragLen), validateHttp2Semantics: false);
        }

        await TrySendBestEffortRstStreamAsync(promisedStreamId, ErrCancel, cancellationToken).ConfigureAwait(false);
    }

    private void CompleteStreamSuccess(Http2StreamState streamState)
    {
        if (streamState.Completed)
            return;
        streamState.Completed = true;
        _streams.TryRemove(streamState.StreamId, out _);

        try
        {
            byte[] rawBody = streamState.BodyBuffer.ToArray();
            byte[] finalBody = rawBody;

            if (streamState.Request.AllowAutoDecompression && rawBody.Length > 0)
            {
                string? contentEncoding = CombineHeaderValues(streamState.ResponseHeaders, "content-encoding");
                if (!string.IsNullOrWhiteSpace(contentEncoding))
                {
                    finalBody = HttpContentDecoder.DecodeIfNeeded(
                        rawBody,
                        contentEncoding,
                        streamState.Request.MaxResponseBodyBytes);
                }
            }

            var response = new PureHttpResponse
            {
                StatusCode = streamState.StatusCode,
                HttpVersion = "HTTP/2.0",
                Headers = streamState.ResponseHeaders.AsReadOnly(),
                Trailers = streamState.Trailers.AsReadOnly(),
                Body = finalBody,
            };

            streamState.ResponseTcs.TrySetResult(response);
        }
        catch (Exception ex)
        {
            streamState.ResponseTcs.TrySetException(ex);
        }
        finally
        {
            WakeConcurrencyWaiters();
        }
    }

    private void FailAndRemoveStream(Http2StreamState streamState, Exception ex)
    {
        _streams.TryRemove(streamState.StreamId, out _);
        FailStream(streamState, ex);
        WakeConcurrencyWaiters();
    }

    private void FailStream(Http2StreamState streamState, Exception ex)
    {
        lock (_flowLock)
            streamState.TerminalError ??= ex;

        streamState.ResponseTcs.TrySetException(ex);
        WakeWindowWaiters();
    }

    private void FailConnection(Exception error)
    {
        _connectionDead = true;
        _fatalError ??= error;

        foreach (int id in _streams.Keys)
        {
            if (_streams.TryRemove(id, out Http2StreamState? streamState))
                FailStream(streamState, error);
        }

        WakeWindowWaiters();
        WakeConcurrencyWaiters();
    }

    private void WakeWindowWaiters()
    {
        TaskCompletionSource[] waiters;
        lock (_flowLock)
        {
            if (_windowWaiters.Count == 0)
                return;
            waiters = _windowWaiters.ToArray();
            _windowWaiters.Clear();
        }

        for (int i = 0; i < waiters.Length; i++)
            waiters[i].TrySetResult();
    }

    private void WakeConcurrencyWaiters()
    {
        TaskCompletionSource[] waiters;
        lock (_stateLock)
        {
            if (_concurrencyWaiters.Count == 0)
                return;
            waiters = _concurrencyWaiters.ToArray();
            _concurrencyWaiters.Clear();
        }

        for (int i = 0; i < waiters.Length; i++)
            waiters[i].TrySetResult();
    }

    private async Task TrySendBestEffortRstStreamAsync(int streamId, uint errorCode, CancellationToken cancellationToken = default)
    {
        if (_disposed || _connectionDead)
            return;

        try
        {
            await _writeLock.WaitAsync(cancellationToken).ConfigureAwait(false);
            try
            {
                if (_disposed || _connectionDead)
                    return;

                var buf = new byte[4];
                BinaryPrimitives.WriteUInt32BigEndian(buf, errorCode);
                await WriteFrameAsync(FrameRstStream, 0, streamId, buf, cancellationToken).ConfigureAwait(false);
                await _stream.FlushAsync(cancellationToken).ConfigureAwait(false);
            }
            finally
            {
                _writeLock.Release();
            }
        }
        catch
        {
            // Best-effort control frame.
        }
    }

    private async Task TrySendBestEffortGoAwayAsync(uint errorCode)
    {
        if (_disposed || _connectionDead)
            return;

        try
        {
            await _writeLock.WaitAsync(CancellationToken.None).ConfigureAwait(false);
            try
            {
                if (_disposed || _connectionDead)
                    return;

                var buf = new byte[8];
                BinaryPrimitives.WriteUInt32BigEndian(buf.AsSpan(0, 4), (uint)_lastPeerStreamId & 0x7FFF_FFFFu);
                BinaryPrimitives.WriteUInt32BigEndian(buf.AsSpan(4, 4), errorCode);
                await WriteFrameAsync(FrameGoAway, 0, 0, buf, CancellationToken.None).ConfigureAwait(false);
                await _stream.FlushAsync(CancellationToken.None).ConfigureAwait(false);
            }
            finally
            {
                _writeLock.Release();
            }
        }
        catch
        {
            // Best-effort GOAWAY.
        }
    }

    private static string? CombineHeaderValues(List<PureHttpHeader> headers, string targetName)
    {
        string? single = null;
        List<string>? multi = null;
        for (int i = 0; i < headers.Count; i++)
        {
            if (string.Equals(headers[i].Name, targetName, StringComparison.OrdinalIgnoreCase))
            {
                if (single is null)
                {
                    single = headers[i].Value;
                }
                else
                {
                    multi ??= new List<string> { single };
                    multi.Add(headers[i].Value);
                }
            }
        }

        return multi is not null ? string.Join(", ", multi) : single;
    }

    public async ValueTask DisposeAsync()
    {
        if (_disposed)
            return;

        await TrySendBestEffortGoAwayAsync(ErrNoError).ConfigureAwait(false);

        _disposed = true;
        _readLoopCts.Cancel();
        FailConnection(new ObjectDisposedException(nameof(Http2Connection)));

        if (!_leaveStreamOpen)
        {
            try
            {
                await _stream.DisposeAsync().ConfigureAwait(false);
            }
            catch
            {
                // Ignore transport disposal faults during teardown.
            }
        }

        if (_readLoopTask is not null)
        {
            try
            {
                await _readLoopTask.ConfigureAwait(false);
            }
            catch
            {
                // Read loop errors were already propagated to pending streams.
            }
        }

        _reader.Dispose();
        _readLoopCts.Dispose();
        _startLock.Dispose();
        _writeLock.Dispose();
    }
}
