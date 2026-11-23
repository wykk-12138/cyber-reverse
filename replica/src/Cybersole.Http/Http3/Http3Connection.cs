using Cybersole.Http.Profiles;
using Cybersole.Http.Protocol;
using Cybersole.Http.Quic;

namespace Cybersole.Http.Http3;

/// <summary>RFC 9114 §7.2 HTTP/3 frame type identifiers.</summary>
public static class Http3FrameType
{
    public const ulong Data = 0x00;
    public const ulong Headers = 0x01;
    public const ulong ReservedH2Priority = 0x02;
    public const ulong CancelPush = 0x03;
    public const ulong Settings = 0x04;
    public const ulong PushPromise = 0x05;
    public const ulong ReservedH2Ping = 0x06;
    public const ulong GoAway = 0x07;
    public const ulong ReservedH2WindowUpdate = 0x08;
    public const ulong ReservedH2Continuation = 0x09;
    public const ulong MaxPushId = 0x0D;

    public static bool IsGrease(ulong frameType) => frameType >= 33UL && (frameType - 33UL) % 31UL == 0UL;
    public static bool IsReservedH2(ulong frameType) => frameType is 0x02 or 0x06 or 0x08 or 0x09;
}

/// <summary>RFC 9114 §6.2 HTTP/3 unidirectional stream type identifiers.</summary>
public static class Http3StreamType
{
    public const ulong Control = 0x00;
    public const ulong Push = 0x01;
    public const ulong QpackEncoder = 0x02;
    public const ulong QpackDecoder = 0x03;

    public static bool IsGrease(ulong streamType) => streamType >= 33UL && (streamType - 33UL) % 31UL == 0UL;
}

/// <summary>RFC 9114 §7 HTTP/3 frame wire serializer and parser.</summary>
public static class Http3FrameCodec
{
    public const int MaxFramePayloadBytes = 16 * 1024 * 1024; // 0x1000000 per cybersole_http_architecture.md §5.3

    public static byte[] BuildFrame(ulong frameType, ReadOnlySpan<byte> payload)
    {
        int tLen = QuicVarInt.GetEncodedLength(frameType);
        int lLen = QuicVarInt.GetEncodedLength((ulong)payload.Length);
        var buf = new byte[tLen + lLen + payload.Length];
        QuicVarInt.Encode(frameType, buf.AsSpan(0, tLen));
        QuicVarInt.Encode((ulong)payload.Length, buf.AsSpan(tLen, lLen));
        if (!payload.IsEmpty)
            payload.CopyTo(buf.AsSpan(tLen + lLen));
        return buf;
    }

    public static ValueTask WriteFrameAsync(Stream stream, ulong frameType, ReadOnlyMemory<byte> payload, CancellationToken ct = default)
    {
        byte[] frame = BuildFrame(frameType, payload.Span);
        return stream.WriteAsync(frame, ct);
    }

    public static byte[] BuildSettingsPayload(IReadOnlyList<(ulong Id, ulong Value)> settings)
    {
        var buf = new List<byte>(settings.Count * 8);
        for (int i = 0; i < settings.Count; i++)
        {
            QuicVarInt.Write(buf, settings[i].Id);
            QuicVarInt.Write(buf, settings[i].Value);
        }
        return buf.ToArray();
    }

    public static Dictionary<ulong, ulong> ParseSettingsPayload(ReadOnlySpan<byte> payload)
    {
        var result = new Dictionary<ulong, ulong>();
        int offset = 0;
        while (offset < payload.Length)
        {
            if (!QuicVarInt.TryRead(payload, ref offset, out ulong id) ||
                !QuicVarInt.TryRead(payload, ref offset, out ulong value))
            {
                throw new Http3Exception(Http3ErrorCode.FrameError, "http3: truncated SETTINGS entry");
            }

            // RFC 9114 §7.2.4.1 forbidden HTTP/2 settings
            if (id is 0x00 or 0x02 or 0x03 or 0x04 or 0x05)
                throw new Http3Exception(Http3ErrorCode.SettingsError, $"http3: forbidden HTTP/2 setting 0x{id:X} in SETTINGS");

            if (!result.TryAdd(id, value))
                throw new Http3Exception(Http3ErrorCode.SettingsError, $"http3: duplicate setting 0x{id:X} in SETTINGS");
        }
        return result;
    }

    public static async Task<(bool Eof, ulong FrameType, byte[] Payload)> ReadFrameAsync(
        Stream stream,
        int maxFrameBytes = MaxFramePayloadBytes,
        CancellationToken cancellationToken = default)
    {
        (bool eofType, ulong frameType) = await TryReadVarIntAsync(stream, allowCleanEofOnFirstByte: true, cancellationToken).ConfigureAwait(false);
        if (eofType)
            return (true, 0UL, Array.Empty<byte>());

        (bool eofLen, ulong frameLen) = await TryReadVarIntAsync(stream, allowCleanEofOnFirstByte: false, cancellationToken).ConfigureAwait(false);
        if (eofLen)
            throw new Http3Exception(Http3ErrorCode.FrameError, "http3: truncated frame");

        if (frameLen > (ulong)maxFrameBytes)
            throw new Http3Exception(Http3ErrorCode.FrameError, $"http3: frame too large ({frameLen} > {maxFrameBytes})");

        var payload = frameLen == 0 ? Array.Empty<byte>() : new byte[(int)frameLen];
        int readTotal = 0;
        while (readTotal < payload.Length)
        {
            int n = await stream.ReadAsync(payload.AsMemory(readTotal, payload.Length - readTotal), cancellationToken).ConfigureAwait(false);
            if (n == 0)
                throw new Http3Exception(Http3ErrorCode.FrameError, "http3: truncated frame");
            readTotal += n;
        }

        return (false, frameType, payload);
    }

    internal static async Task<(bool CleanEof, ulong Value)> TryReadVarIntAsync(
        Stream stream,
        bool allowCleanEofOnFirstByte,
        CancellationToken cancellationToken)
    {
        var first = new byte[1];
        int n = await stream.ReadAsync(first.AsMemory(0, 1), cancellationToken).ConfigureAwait(false);
        if (n == 0)
        {
            if (allowCleanEofOnFirstByte)
                return (true, 0UL);
            throw new Http3Exception(Http3ErrorCode.FrameError, "http3: truncated frame");
        }

        int len = 1 << (first[0] >> 6);
        var buf = new byte[len];
        buf[0] = first[0];
        int pos = 1;
        while (pos < len)
        {
            int r = await stream.ReadAsync(buf.AsMemory(pos, len - pos), cancellationToken).ConfigureAwait(false);
            if (r == 0)
                throw new Http3Exception(Http3ErrorCode.FrameError, "http3: truncated frame");
            pos += r;
        }

        ulong value = QuicVarInt.Decode(buf, out _);
        return (false, value);
    }
}

/// <summary>
/// Pure managed RFC 9114 HTTP/3 multiplexed connection over <see cref="QuicConnection"/>
/// matching <c>Http3Connection</c> (<c>0x1412C5990</c> / <c>0x141364900</c> / <c>0x141361D20</c>).
/// </summary>
public sealed class Http3Connection : IMultiplexedConnection
{
    private static readonly HashSet<string> DisallowedRequestHeaders = new(StringComparer.OrdinalIgnoreCase)
    {
        "host",
        "upgrade",
        "connection",
        "keep-alive",
        "proxy-connection",
        "transfer-encoding",
        "te",
    };

    private readonly QuicConnection _quic;
    private readonly ClientProfile _profile;
    private readonly QpackEncoder _qpackEncoder = new();
    private readonly QpackDecoder _qpackDecoder;
    private readonly Random _rng;
    private readonly CancellationTokenSource _connCts = new();
    private readonly TaskCompletionSource<Exception> _fatalErrorTcs = new(TaskCreationOptions.RunContinuationsAsynchronously);
    private readonly SemaphoreSlim _decoderWriteLock = new(1, 1);

    private QuicStream? _clientControlStream;
    private QuicStream? _clientEncoderStream;
    private QuicStream? _clientDecoderStream;
    private Task? _uniAcceptTask;

    private int _serverControlSeen;
    private int _serverEncoderSeen;
    private int _serverDecoderSeen;
    private volatile bool _goawayReceived;
    private ulong _goawayStreamId = ulong.MaxValue;
    private IReadOnlyDictionary<ulong, ulong>? _peerSettings;
    private Exception? _terminalError;
    private int _activeStreams;
    private DateTimeOffset _lastUsedUtc = DateTimeOffset.UtcNow;
    private int _started;
    private int _disposed;

    public Http3Connection(
        QuicConnection quic,
        ConnectionKey key,
        ClientProfile? profile = null,
        Random? random = null)
    {
        _quic = quic ?? throw new ArgumentNullException(nameof(quic));
        Key = key;
        _profile = profile ?? ProfileRegistry.GetOrDefault(key.ProfileName);
        _rng = random ?? Random.Shared;

        Http3SettingsSpec? h3Spec = _profile.Http3Settings;
        ulong maxTable = h3Spec?.QpackMaxTableCapacity ?? 65_536UL;
        ulong maxBlocked = h3Spec?.QpackBlockedStreams ?? 100UL;
        ulong maxFieldSection = h3Spec?.MaxFieldSectionSize ?? 262_144UL;
        _qpackDecoder = new QpackDecoder(maxTable, maxBlocked, maxFieldSection);
    }

    public string ProtocolVersion => "HTTP/3";
    public ConnectionKey Key { get; }
    public bool SupportsMultiplexing => true;
    public int MaxConcurrentStreams => (int)Math.Min(Math.Max(_quic.PeerMaxStreamsBidi, 1UL), int.MaxValue);
    public int ActiveStreams => Volatile.Read(ref _activeStreams);
    public DateTimeOffset LastUsedUtc => _lastUsedUtc;
    public bool GoAwayReceived => _goawayReceived;
    public ulong GoAwayStreamId => _goawayStreamId;
    public IReadOnlyDictionary<ulong, ulong>? PeerSettings => _peerSettings;
    public Exception? FatalError => _terminalError;
    public QuicConnection Quic => _quic;
    public Task<Exception> FatalErrorTask => _fatalErrorTcs.Task;

    public bool IsUsable =>
        Volatile.Read(ref _disposed) == 0 &&
        _terminalError is null &&
        !_goawayReceived &&
        _quic.IsConnected;

    public bool CanAcceptNewStream() => IsUsable && ActiveStreams < MaxConcurrentStreams;

    public static async Task<Http3Connection> ConnectAsync(
        QuicConnectionOptions quicOptions,
        ConnectionKey key,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(quicOptions);
        QuicConnection quic = await QuicConnection.ConnectAsync(quicOptions, cancellationToken).ConfigureAwait(false);
        var h3 = new Http3Connection(quic, key, quicOptions.Profile, quicOptions.Random);
        try
        {
            await h3.StartAsync(cancellationToken).ConfigureAwait(false);
            return h3;
        }
        catch
        {
            await h3.DisposeAsync().ConfigureAwait(false);
            throw;
        }
    }

    public async Task StartAsync(CancellationToken cancellationToken = default)
    {
        if (Interlocked.Exchange(ref _started, 1) != 0)
            throw new InvalidOperationException("Http3Connection.StartAsync can only be called once.");

        // 1. Open mandatory critical unidirectional streams FIRST (RFC 9114 §6.2 requires peers to allow >= 3):
        //    Control Stream (0x00), QPACK Encoder Stream (0x02), and QPACK Decoder Stream (0x03).
        _clientControlStream = await _quic.OpenUniDirectionalStreamAsync(cancellationToken).ConfigureAwait(false);
        IReadOnlyList<(ulong Id, ulong Value)> wireSettings = Http3SettingsSpec.BuildWireSettings(_profile.Http3Settings, _rng);
        byte[] settingsPayload = Http3FrameCodec.BuildSettingsPayload(wireSettings);
        byte[] settingsFrame = Http3FrameCodec.BuildFrame(Http3FrameType.Settings, settingsPayload);
        byte[] ctrlHead = QuicVarInt.Encode(Http3StreamType.Control);
        var ctrlInit = new byte[ctrlHead.Length + settingsFrame.Length];
        ctrlHead.CopyTo(ctrlInit, 0);
        settingsFrame.CopyTo(ctrlInit, ctrlHead.Length);
        await _clientControlStream.WriteAsync(ctrlInit, fin: false, cancellationToken).ConfigureAwait(false);

        _clientEncoderStream = await _quic.OpenUniDirectionalStreamAsync(cancellationToken).ConfigureAwait(false);
        await _clientEncoderStream.WriteAsync(QuicVarInt.Encode(Http3StreamType.QpackEncoder), fin: false, cancellationToken).ConfigureAwait(false);

        _clientDecoderStream = await _quic.OpenUniDirectionalStreamAsync(cancellationToken).ConfigureAwait(false);
        await _clientDecoderStream.WriteAsync(QuicVarInt.Encode(Http3StreamType.QpackDecoder), fin: false, cancellationToken).ConfigureAwait(false);

        // 2. Optional Chrome GREASE unidirectional stream (31 * N + 33) only when the peer grants > 3 uni streams;
        //    peers advertising initial_max_streams_uni == 3 (e.g. Cloudflare edges) only budget the 3 critical streams.
        if (_profile.Http3Settings?.SendGreaseFrame == true && _quic.PeerMaxStreamsUni > 3UL)
        {
            QuicStream greaseStream = await _quic.OpenUniDirectionalStreamAsync(cancellationToken).ConfigureAwait(false);
            ulong greaseType = 31UL * (ulong)_rng.Next(1, 0x10_0000) + 33UL;
            byte[] typeBytes = QuicVarInt.Encode(greaseType);
            int extraLen = _rng.Next(1, 5);
            var payload = new byte[typeBytes.Length + extraLen];
            typeBytes.CopyTo(payload, 0);
            _rng.NextBytes(payload.AsSpan(typeBytes.Length, extraLen));
            await greaseStream.WriteAsync(payload, fin: true, cancellationToken).ConfigureAwait(false);
        }

        // 3. Launch server unidirectional stream accept loop
        _uniAcceptTask = Task.Run(AcceptServerUniStreamsLoopAsync);
    }

    public async Task<PureHttpResponse> SendAsync(PureHttpRequest request, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(request);
        ObjectDisposedException.ThrowIf(Volatile.Read(ref _disposed) != 0, this);

        if (_terminalError is not null)
            throw _terminalError;
        if (_goawayReceived)
            throw new Http3Exception(Http3ErrorCode.RequestRejected, "http3: peer sent GOAWAY", retryable: true);

        _lastUsedUtc = DateTimeOffset.UtcNow;
        Interlocked.Increment(ref _activeStreams);

        QuicStream? stream = null;
        try
        {
            stream = await _quic.OpenBiDirectionalStreamAsync(cancellationToken).ConfigureAwait(false);
            if (_goawayReceived && stream.StreamId >= _goawayStreamId)
            {
                await stream.ResetAsync(Http3ErrorCode.RequestCancelled, CancellationToken.None).ConfigureAwait(false);
                throw new Http3Exception(Http3ErrorCode.RequestRejected, $"http3: stream {stream.StreamId} rejected by GOAWAY({_goawayStreamId})", retryable: true);
            }

            List<PureHttpHeader> wireHeaders = BuildWireRequestHeaders(request);
            byte[] encodedHeaders = _qpackEncoder.Encode(wireHeaders, useHuffman: true);
            byte[] headersFrame = Http3FrameCodec.BuildFrame(Http3FrameType.Headers, encodedHeaders);

            bool hasBody = !request.Body.IsEmpty;
            if (!hasBody)
            {
                await stream.WriteAsync(headersFrame, fin: true, cancellationToken).ConfigureAwait(false);
            }
            else
            {
                await stream.WriteAsync(headersFrame, fin: false, cancellationToken).ConfigureAwait(false);
                byte[] dataFrame = Http3FrameCodec.BuildFrame(Http3FrameType.Data, request.Body.Span);
                await stream.WriteAsync(dataFrame, fin: true, cancellationToken).ConfigureAwait(false);
            }

            int? finalStatus = null;
            List<PureHttpHeader>? responseHeaders = null;
            List<PureHttpHeader>? trailers = null;
            using var bodyStream = new MemoryStream();
            bool seenTrailers = false;

            while (true)
            {
                (bool eof, ulong frameType, byte[] payload) = await Http3FrameCodec.ReadFrameAsync(stream, cancellationToken: cancellationToken).ConfigureAwait(false);
                if (eof)
                    break;

                if (Http3FrameType.IsReservedH2(frameType) ||
                    frameType is Http3FrameType.Settings or Http3FrameType.GoAway or Http3FrameType.MaxPushId or Http3FrameType.CancelPush)
                {
                    var protoErr = new Http3Exception(Http3ErrorCode.FrameUnexpected, $"http3: unexpected frame type 0x{frameType:X} on request stream");
                    await stream.StopSendingAsync(Http3ErrorCode.FrameUnexpected, CancellationToken.None).ConfigureAwait(false);
                    throw protoErr;
                }

                if (frameType == Http3FrameType.PushPromise)
                {
                    var idErr = new Http3Exception(Http3ErrorCode.IdError, "http3: PUSH_PROMISE received without MAX_PUSH_ID");
                    await stream.StopSendingAsync(Http3ErrorCode.IdError, CancellationToken.None).ConfigureAwait(false);
                    throw idErr;
                }

                if (frameType == Http3FrameType.Headers)
                {
                    if (seenTrailers)
                        throw new Http3Exception(Http3ErrorCode.FrameUnexpected, "http3: unexpected HEADERS frame after trailers");

                    List<PureHttpHeader> decoded = await DecodeHeadersSerializedAsync(stream.StreamId, payload, cancellationToken).ConfigureAwait(false);
                    if (finalStatus is null)
                    {
                        int parsedStatus = ExtractStatusCode(decoded);
                        if (parsedStatus is >= 100 and <= 199)
                        {
                            // Interim 1xx informational response (e.g., 103 Early Hints): skip and continue awaiting final HEADERS.
                            continue;
                        }

                        finalStatus = parsedStatus;
                        responseHeaders = StripPseudoHeaders(decoded);
                    }
                    else
                    {
                        for (int i = 0; i < decoded.Count; i++)
                        {
                            if (decoded[i].Name.StartsWith(':'))
                                throw new Http3Exception(Http3ErrorCode.MessageError, $"http3: pseudo-header '{decoded[i].Name}' forbidden in trailers");
                        }
                        seenTrailers = true;
                        trailers = decoded;
                    }
                }
                else if (frameType == Http3FrameType.Data)
                {
                    if (finalStatus is null || seenTrailers)
                    {
                        await stream.StopSendingAsync(Http3ErrorCode.FrameUnexpected, CancellationToken.None).ConfigureAwait(false);
                        throw new Http3Exception(Http3ErrorCode.FrameUnexpected, "http3: DATA frame received outside response body state");
                    }

                    if (bodyStream.Length + payload.Length > request.MaxResponseBodyBytes)
                    {
                        await stream.StopSendingAsync(Http3ErrorCode.ExcessiveLoad, CancellationToken.None).ConfigureAwait(false);
                        throw new PureHttpException(HttpErrorKind.ResponseTooLarge, $"HTTP/3 response body exceeded {request.MaxResponseBodyBytes} bytes.");
                    }

                    if (payload.Length > 0)
                        bodyStream.Write(payload, 0, payload.Length);
                }
                else
                {
                    // GREASE or unknown HTTP/3 extension frame: safely ignore per RFC 9114 §9.
                }
            }

            if (_terminalError is not null && finalStatus is null)
                throw _terminalError;

            if (finalStatus is null || responseHeaders is null)
                throw new Http3Exception(Http3ErrorCode.MessageError, "http3: response stream ended before receiving final HEADERS");

            byte[] rawBody = bodyStream.ToArray();
            string? contentEncoding = null;
            for (int i = 0; i < responseHeaders.Count; i++)
            {
                if (string.Equals(responseHeaders[i].Name, "content-encoding", StringComparison.OrdinalIgnoreCase))
                {
                    contentEncoding = string.IsNullOrEmpty(contentEncoding)
                        ? responseHeaders[i].Value
                        : $"{contentEncoding}, {responseHeaders[i].Value}";
                }
            }

            byte[] finalBody = request.AllowAutoDecompression && !string.IsNullOrWhiteSpace(contentEncoding)
                ? HttpContentDecoder.DecodeIfNeeded(rawBody, contentEncoding, request.MaxResponseBodyBytes)
                : rawBody;

            _lastUsedUtc = DateTimeOffset.UtcNow;
            return new PureHttpResponse
            {
                StatusCode = finalStatus.Value,
                HttpVersion = "HTTP/3",
                Headers = responseHeaders,
                Trailers = trailers ?? (IReadOnlyList<PureHttpHeader>)Array.Empty<PureHttpHeader>(),
                Body = finalBody,
            };
        }
        catch (OperationCanceledException) when (_terminalError is not null && !cancellationToken.IsCancellationRequested)
        {
            throw _terminalError;
        }
        catch (QuicException) when (_terminalError is not null)
        {
            throw _terminalError;
        }
        finally
        {
            Interlocked.Decrement(ref _activeStreams);
        }
    }

    private async Task<List<PureHttpHeader>> DecodeHeadersSerializedAsync(ulong streamId, byte[] payload, CancellationToken ct)
    {
        (List<PureHttpHeader> headers, ulong reqInsertCount) = await _qpackDecoder.DecodeFieldSectionWithCountAsync(payload, ct).ConfigureAwait(false);
        if (reqInsertCount > 0 && _clientDecoderStream is not null)
        {
            byte[] ack = QpackDecoder.BuildSectionAcknowledgment(streamId);
            await _decoderWriteLock.WaitAsync(ct).ConfigureAwait(false);
            try
            {
                await _clientDecoderStream.WriteAsync(ack, ct).ConfigureAwait(false);
            }
            finally
            {
                _decoderWriteLock.Release();
            }
        }
        return headers;
    }

    private async Task AcceptServerUniStreamsLoopAsync()
    {
        CancellationToken ct = _connCts.Token;
        try
        {
            while (!ct.IsCancellationRequested && Volatile.Read(ref _disposed) == 0)
            {
                QuicStream? stream = await _quic.AcceptServerUniStreamAsync(ct).ConfigureAwait(false);
                if (stream is null)
                    break;

                _ = Task.Run(() => HandleServerUniStreamAsync(stream), ct);
            }
        }
        catch (OperationCanceledException)
        {
            // Normal shutdown
        }
        catch (Exception ex)
        {
            if (Volatile.Read(ref _disposed) == 0 && _terminalError is null)
                await AbortConnectionAsync(Http3ErrorCode.InternalError, $"http3: unidirectional accept loop failed: {ex.Message}", ex).ConfigureAwait(false);
        }
    }

    private async Task HandleServerUniStreamAsync(QuicStream stream)
    {
        CancellationToken ct = _connCts.Token;
        try
        {
            (bool eof, ulong streamType) = await Http3FrameCodec.TryReadVarIntAsync(stream, allowCleanEofOnFirstByte: true, ct).ConfigureAwait(false);
            if (eof)
                return;

            switch (streamType)
            {
                case Http3StreamType.Control:
                    if (Interlocked.Exchange(ref _serverControlSeen, 1) != 0)
                    {
                        await AbortConnectionAsync(Http3ErrorCode.StreamCreationError, "http3: duplicate server control stream").ConfigureAwait(false);
                        return;
                    }
                    await HandleServerControlStreamAsync(stream, ct).ConfigureAwait(false);
                    break;

                case Http3StreamType.QpackEncoder:
                    if (Interlocked.Exchange(ref _serverEncoderSeen, 1) != 0)
                    {
                        await AbortConnectionAsync(Http3ErrorCode.StreamCreationError, "http3: duplicate server QPACK encoder stream").ConfigureAwait(false);
                        return;
                    }
                    await HandleServerQpackEncoderStreamAsync(stream, ct).ConfigureAwait(false);
                    break;

                case Http3StreamType.QpackDecoder:
                    if (Interlocked.Exchange(ref _serverDecoderSeen, 1) != 0)
                    {
                        await AbortConnectionAsync(Http3ErrorCode.StreamCreationError, "http3: duplicate server QPACK decoder stream").ConfigureAwait(false);
                        return;
                    }
                    await HandleServerQpackDecoderStreamAsync(stream, ct).ConfigureAwait(false);
                    break;

                case Http3StreamType.Push:
                    await AbortConnectionAsync(Http3ErrorCode.IdError, "http3: server initiated push stream without MAX_PUSH_ID").ConfigureAwait(false);
                    break;

                default:
                    // Unrecognized / GREASE unidirectional stream types (RFC 9114 §6.2.3): consume and ignore cleanly.
                    var drain = new byte[1024];
                    while (!ct.IsCancellationRequested)
                    {
                        int n = await stream.ReadAsync(drain, ct).ConfigureAwait(false);
                        if (n == 0)
                            break;
                    }
                    break;
            }
        }
        catch (OperationCanceledException)
        {
            // Shutdown
        }
        catch (Http3Exception h3ex)
        {
            await AbortConnectionAsync(h3ex.H3ErrorCode, h3ex.Message, h3ex).ConfigureAwait(false);
        }
        catch (QuicException qex) when (Volatile.Read(ref _disposed) == 0)
        {
            await AbortConnectionAsync(Http3ErrorCode.ClosedCriticalStream, $"http3: critical stream error: {qex.Message}", qex).ConfigureAwait(false);
        }
        catch (Exception ex) when (Volatile.Read(ref _disposed) == 0)
        {
            await AbortConnectionAsync(Http3ErrorCode.GeneralProtocolError, $"http3: unidirectional stream failed: {ex.Message}", ex).ConfigureAwait(false);
        }
    }

    private async Task HandleServerControlStreamAsync(QuicStream stream, CancellationToken ct)
    {
        bool seenSettings = false;
        while (!ct.IsCancellationRequested)
        {
            (bool eof, ulong frameType, byte[] payload) = await Http3FrameCodec.ReadFrameAsync(stream, cancellationToken: ct).ConfigureAwait(false);
            if (eof)
            {
                await AbortConnectionAsync(Http3ErrorCode.ClosedCriticalStream, "http3: server closed critical control stream (0x00)").ConfigureAwait(false);
                return;
            }

            if (!seenSettings)
            {
                if (frameType != Http3FrameType.Settings)
                {
                    await AbortConnectionAsync(Http3ErrorCode.MissingSettings, $"http3: first frame on control stream must be SETTINGS (got 0x{frameType:X})").ConfigureAwait(false);
                    return;
                }

                Dictionary<ulong, ulong> parsed = Http3FrameCodec.ParseSettingsPayload(payload);
                _peerSettings = parsed;
                seenSettings = true;
                continue;
            }

            if (frameType == Http3FrameType.Settings)
            {
                await AbortConnectionAsync(Http3ErrorCode.FrameUnexpected, "http3: duplicate SETTINGS frame on control stream").ConfigureAwait(false);
                return;
            }

            if (Http3FrameType.IsReservedH2(frameType) ||
                frameType is Http3FrameType.Data or Http3FrameType.Headers or Http3FrameType.PushPromise)
            {
                await AbortConnectionAsync(Http3ErrorCode.FrameUnexpected, $"http3: forbidden frame 0x{frameType:X} on control stream").ConfigureAwait(false);
                return;
            }

            switch (frameType)
            {
                case Http3FrameType.GoAway:
                {
                    if (!QuicVarInt.TryDecode(payload, out ulong id, out int read) || read != payload.Length)
                    {
                        await AbortConnectionAsync(Http3ErrorCode.FrameError, "http3: invalid GOAWAY payload").ConfigureAwait(false);
                        return;
                    }
                    if (_goawayReceived && id > _goawayStreamId)
                    {
                        await AbortConnectionAsync(Http3ErrorCode.IdError, $"http3: GOAWAY stream ID {id} increased above {_goawayStreamId}").ConfigureAwait(false);
                        return;
                    }
                    _goawayStreamId = id;
                    _goawayReceived = true;
                    break;
                }

                case Http3FrameType.CancelPush:
                case Http3FrameType.MaxPushId:
                {
                    if (!QuicVarInt.TryDecode(payload, out _, out int read) || read != payload.Length)
                    {
                        await AbortConnectionAsync(Http3ErrorCode.FrameError, $"http3: invalid control frame 0x{frameType:X} payload").ConfigureAwait(false);
                        return;
                    }
                    break;
                }

                default:
                    // GREASE or unknown control frames skipped safely.
                    break;
            }
        }
    }

    private async Task HandleServerQpackEncoderStreamAsync(QuicStream stream, CancellationToken ct)
    {
        var buf = new byte[4096]; // 4096B buffer matching 0x141361D20
        while (!ct.IsCancellationRequested)
        {
            int n = await stream.ReadAsync(buf, ct).ConfigureAwait(false);
            if (n == 0)
            {
                _qpackDecoder.MarkEncoderStreamClosed();
                await AbortConnectionAsync(Http3ErrorCode.ClosedCriticalStream, "http3: server closed critical QPACK encoder stream (0x02)").ConfigureAwait(false);
                return;
            }

            byte[] feedback = _qpackDecoder.ProcessEncoderInstructions(buf.AsSpan(0, n));
            if (feedback.Length > 0 && _clientDecoderStream is not null)
            {
                await _decoderWriteLock.WaitAsync(ct).ConfigureAwait(false);
                try
                {
                    await _clientDecoderStream.WriteAsync(feedback, ct).ConfigureAwait(false);
                }
                finally
                {
                    _decoderWriteLock.Release();
                }
            }
        }
    }

    private async Task HandleServerQpackDecoderStreamAsync(QuicStream stream, CancellationToken ct)
    {
        var buf = new byte[256]; // 256B buffer matching 0x141361D20
        while (!ct.IsCancellationRequested)
        {
            int n = await stream.ReadAsync(buf, ct).ConfigureAwait(false);
            if (n == 0)
            {
                await AbortConnectionAsync(Http3ErrorCode.ClosedCriticalStream, "http3: server closed critical QPACK decoder stream (0x03)").ConfigureAwait(false);
                return;
            }
        }
    }

    private async Task AbortConnectionAsync(ulong h3ErrorCode, string message, Exception? cause = null)
    {
        if (Volatile.Read(ref _disposed) != 0)
            return;

        var h3Ex = new Http3Exception(h3ErrorCode, $"{message}, Http3Code = {h3ErrorCode}", cause);
        if (Interlocked.CompareExchange(ref _terminalError, h3Ex, null) is null)
        {
            _fatalErrorTcs.TrySetResult(h3Ex);
            _connCts.Cancel();
            await _quic.CloseAsync(h3ErrorCode, isApplicationError: true, message).ConfigureAwait(false);
        }
    }

    private List<PureHttpHeader> BuildWireRequestHeaders(PureHttpRequest request)
    {
        string method = request.Method.ToUpperInvariant();
        string scheme = request.Uri.Scheme.ToLowerInvariant();
        string path = string.IsNullOrEmpty(request.Uri.PathAndQuery) ? "/" : request.Uri.PathAndQuery;
        string authority = request.Uri.Authority;

        var regular = new List<PureHttpHeader>(request.Headers.Count + 2);
        for (int i = 0; i < request.Headers.Count; i++)
        {
            PureHttpHeader h = request.Headers[i];
            if (string.Equals(h.Name, "host", StringComparison.OrdinalIgnoreCase))
            {
                if (!string.IsNullOrWhiteSpace(h.Value))
                    authority = h.Value;
                continue;
            }
            if (DisallowedRequestHeaders.Contains(h.Name) || string.Equals(h.Name, "content-length", StringComparison.OrdinalIgnoreCase))
                continue;
            if (h.Name.StartsWith(':'))
                continue;

            string lower = h.Name.ToLowerInvariant();

            if (lower == "cookie" && h.Value.Contains("; ", StringComparison.Ordinal))
            {
                string[] parts = h.Value.Split("; ", StringSplitOptions.RemoveEmptyEntries);
                for (int p = 0; p < parts.Length; p++)
                    regular.Add(new PureHttpHeader("cookie", parts[p]));
            }
            else
            {
                regular.Add(new PureHttpHeader(lower, h.Value));
            }
        }

        if (!request.Body.IsEmpty || method is "POST" or "PUT" or "PATCH")
            regular.Add(new PureHttpHeader("content-length", request.Body.Length.ToString(System.Globalization.CultureInfo.InvariantCulture)));

        IReadOnlyList<string>? headerOrder = _profile.Http3Settings?.HeaderOrder ?? _profile.Http2Settings.HeaderOrder;
        if (headerOrder is { Count: > 0 })
        {
            var rank = new Dictionary<string, int>(headerOrder.Count, StringComparer.OrdinalIgnoreCase);
            for (int i = 0; i < headerOrder.Count; i++)
                rank.TryAdd(headerOrder[i], i);

            regular = regular
                .Select((h, idx) => (Header: h, Rank: rank.TryGetValue(h.Name, out int r) ? r : int.MaxValue, Index: idx))
                .OrderBy(x => x.Rank)
                .ThenBy(x => x.Index)
                .Select(x => x.Header)
                .ToList();
        }

        IReadOnlyList<string> pseudoOrder = _profile.Http3Settings?.PseudoHeaderOrder ?? Http3SettingsSpec.DefaultFallbackPseudoHeaderOrder;
        var result = new List<PureHttpHeader>(4 + regular.Count);
        for (int i = 0; i < pseudoOrder.Count; i++)
        {
            switch (pseudoOrder[i])
            {
                case ":method":
                    result.Add(new PureHttpHeader(":method", method));
                    break;
                case ":authority":
                    result.Add(new PureHttpHeader(":authority", authority));
                    break;
                case ":scheme":
                    if (method != "CONNECT")
                        result.Add(new PureHttpHeader(":scheme", scheme));
                    break;
                case ":path":
                    if (method != "CONNECT")
                        result.Add(new PureHttpHeader(":path", path));
                    break;
            }
        }

        result.AddRange(regular);
        return result;
    }

    private static int ExtractStatusCode(List<PureHttpHeader> headers)
    {
        string? statusVal = null;
        bool seenRegular = false;
        for (int i = 0; i < headers.Count; i++)
        {
            string name = headers[i].Name;
            if (name.StartsWith(':'))
            {
                if (seenRegular)
                    throw new Http3Exception(Http3ErrorCode.MessageError, $"http3: pseudo-header '{name}' appeared after regular header");
                if (name == ":status")
                {
                    if (statusVal is not null)
                        throw new Http3Exception(Http3ErrorCode.MessageError, "http3: duplicate :status pseudo-header");
                    statusVal = headers[i].Value;
                }
                else
                {
                    throw new Http3Exception(Http3ErrorCode.MessageError, $"http3: invalid response pseudo-header '{name}'");
                }
            }
            else
            {
                seenRegular = true;
            }
        }

        if (statusVal is null || !int.TryParse(statusVal, System.Globalization.NumberStyles.None, System.Globalization.CultureInfo.InvariantCulture, out int code) || code is < 100 or > 999)
            throw new Http3Exception(Http3ErrorCode.MessageError, $"http3: missing or invalid :status '{statusVal}'");

        return code;
    }

    private static List<PureHttpHeader> StripPseudoHeaders(List<PureHttpHeader> decoded)
    {
        var list = new List<PureHttpHeader>(decoded.Count);
        for (int i = 0; i < decoded.Count; i++)
        {
            if (!decoded[i].Name.StartsWith(':'))
                list.Add(decoded[i]);
        }
        return list;
    }

    public async ValueTask DisposeAsync()
    {
        if (Interlocked.Exchange(ref _disposed, 1) != 0)
            return;

        _connCts.Cancel();
        await _quic.DisposeAsync().ConfigureAwait(false);

        if (_uniAcceptTask is not null)
        {
            try { await _uniAcceptTask.ConfigureAwait(false); } catch { }
        }

        _decoderWriteLock.Dispose();
        _connCts.Dispose();
    }
}
