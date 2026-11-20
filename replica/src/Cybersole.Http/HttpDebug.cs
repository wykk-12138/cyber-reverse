using System.Buffers.Binary;
using System.Collections.Concurrent;
using System.Net.Sockets;
using System.Text;
using System.Threading.Channels;
using Newtonsoft.Json;

namespace Cybersole.Http;

public enum HttpDebugFrameType : byte
{
    Hello = 1,
    Request = 2,
    Response = 3,
    Error = 4,
    Dropped = 5,
}

public sealed record DebugEntry(
    DateTime At, string Method, string Url, int Status,
    int ElapsedMs, long Bytes, string Protocol, string? Proxy, string? Tag);

/// <summary>
/// Live request stream and CSHD v1 binary TCP telemetry streamer (<c>Cybersole.Http.Debug</c>).
/// Keeps the original in-memory buffer API while supporting the binary <c>CSHD\x01</c> wire protocol
/// activated via <see cref="EnableStream"/> or <c>CYBERSOLE_HTTP_DEBUG</c>.
/// </summary>
public static class HttpDebug
{
    public const string EnvVar = "CYBERSOLE_HTTP_DEBUG";
    public const string DefaultEndpoint = "127.0.0.1:8889";
    public const int DefaultMaxBodyBytes = 4 * 1024 * 1024;
    public const int DefaultBufferBudget = 64 * 1024 * 1024;
    public static ReadOnlySpan<byte> GreetingBytes => "CSHD\x01"u8;

    private static readonly object Gate = new();
    private static readonly List<DebugEntry> Buffer = new();
    private static readonly ConcurrentDictionary<int, bool> AttachedAnalytics = new();
    private static bool _enabled;

    private static Channel<(HttpDebugFrameType Type, string Json, byte[] Body, int Cost)>? _streamQueue;
    private static CancellationTokenSource? _streamCts;
    private static Thread? _streamThread;
    private static int _queuedBytes;
    private static int _droppedFrames;
    private static int _maxBodyBytes = DefaultMaxBodyBytes;
    private static int _bufferBudget = DefaultBufferBudget;
    private static TimeSpan _connectTimeout = TimeSpan.FromSeconds(3);
    private static TimeSpan _reconnectDelay = TimeSpan.FromSeconds(2);
    private static string _endpoint = DefaultEndpoint;
    private static bool _streamEnabled;

    public static bool Enabled => _enabled;
    public static bool StreamEnabled => _streamEnabled;
    public static int MaxBodyBytes => _maxBodyBytes;
    public static event EventHandler<DebugEntry>? Entry;

    public static void Enable() { lock (Gate) _enabled = true; }
    public static void Disable() { lock (Gate) _enabled = false; }

    public static void Attach(HttpAnalytics analytics)
    {
        if (AttachedAnalytics.TryAdd(analytics.GetHashCode(), true))
        {
            analytics.RequestRecorded += (_, e) => Push(new DebugEntry(
                e.At, e.Method, e.Url, e.Status, e.ElapsedMs, e.Bytes, e.Protocol, e.Proxy, e.Tag));
        }

        EnableFromEnvironment();
    }

    public static bool EnableFromEnvironment()
    {
        var raw = Environment.GetEnvironmentVariable(EnvVar);
        if (string.IsNullOrWhiteSpace(raw) ||
            raw.Equals("0", StringComparison.OrdinalIgnoreCase) ||
            raw.Equals("false", StringComparison.OrdinalIgnoreCase))
            return false;

        var target = raw.Equals("1", StringComparison.Ordinal) || raw.Equals("true", StringComparison.OrdinalIgnoreCase)
            ? DefaultEndpoint
            : raw.Trim();
        EnableStream(target);
        return true;
    }

    public static void EnableStream(
        string? endpoint = null,
        int maxBodyBytes = DefaultMaxBodyBytes,
        int bufferBudget = DefaultBufferBudget,
        TimeSpan? connectTimeout = null,
        TimeSpan? reconnectDelay = null)
    {
        lock (Gate)
        {
            DisableStreamLocked();
            _endpoint = string.IsNullOrWhiteSpace(endpoint) ? DefaultEndpoint : endpoint.Trim();
            _maxBodyBytes = Math.Max(0, maxBodyBytes);
            _bufferBudget = Math.Max(1024, bufferBudget);
            _connectTimeout = connectTimeout ?? TimeSpan.FromSeconds(3);
            _reconnectDelay = reconnectDelay ?? TimeSpan.FromSeconds(2);
            _queuedBytes = 0;
            _droppedFrames = 0;
            _streamQueue = Channel.CreateUnbounded<(HttpDebugFrameType, string, byte[], int)>(
                new UnboundedChannelOptions { SingleReader = true, SingleWriter = false });
            _streamCts = new CancellationTokenSource();
            _streamEnabled = true;

            var ct = _streamCts.Token;
            var queue = _streamQueue;
            _streamThread = new Thread(() => StreamLoop(queue, ct))
            {
                Name = "Cybersole.Http.Debug",
                IsBackground = true,
            };
            _streamThread.Start();
        }
    }

    public static void DisableStream()
    {
        lock (Gate) DisableStreamLocked();
    }

    private static void DisableStreamLocked()
    {
        _streamEnabled = false;
        _streamQueue?.Writer.TryComplete();
        try { _streamCts?.Cancel(); } catch { }
        if (_streamThread is { IsAlive: true })
            _streamThread.Join(TimeSpan.FromMilliseconds(500));
        _streamCts?.Dispose();
        _streamCts = null;
        _streamQueue = null;
        _streamThread = null;
    }

    public static void RecordWireRequest(
        string id, string method, string url, IReadOnlyDictionary<string, string>? headers,
        string profile, string? proxy, string? tag, byte[]? body, string? redirectOf = null)
    {
        if (!_streamEnabled) return;
        var raw = body ?? Array.Empty<byte>();
        var slice = raw.Length > _maxBodyBytes ? raw.AsSpan(0, _maxBodyBytes).ToArray() : raw;
        var json = JsonConvert.SerializeObject(new
        {
            id,
            redirectOf,
            started = DateTimeOffset.UtcNow.ToString("O"),
            method,
            url,
            headers = headers ?? new Dictionary<string, string>(),
            profile,
            proxy,
            tags = tag is null ? null : new[] { tag },
            client = "NetClient",
            bodyLength = raw.Length,
        }, Formatting.None);
        EnqueueFrame(HttpDebugFrameType.Request, json, slice);
    }

    public static void RecordWireResponse(
        string id, int status, string statusText, string protocol,
        IReadOnlyDictionary<string, string>? headers, TimeSpan elapsed, byte[]? body,
        int attempts = 1)
    {
        if (!_streamEnabled) return;
        var raw = body ?? Array.Empty<byte>();
        var truncated = raw.Length > _maxBodyBytes;
        var slice = truncated ? raw.AsSpan(0, _maxBodyBytes).ToArray() : raw;
        var json = JsonConvert.SerializeObject(new
        {
            id,
            status,
            statusText,
            protocol,
            headers = headers ?? new Dictionary<string, string>(),
            elapsed = elapsed.TotalMilliseconds,
            bodyLength = raw.Length,
            bodyTruncated = truncated ? (bool?)true : null,
            timing = new
            {
                metrics = new
                {
                    queue = 0.0,
                    send = 0.0,
                    wait = elapsed.TotalMilliseconds,
                    receive = 0.0,
                    requestHeaders = 0,
                    requestBody = 0,
                    requestBodyUncompressed = 0,
                    responseHeaders = 0,
                    responseBody = raw.Length,
                    attempts,
                },
            },
        }, Formatting.None);
        EnqueueFrame(HttpDebugFrameType.Response, json, slice);
    }

    public static void RecordWireError(
        string id, TimeSpan elapsed, Exception error, bool timedOut = false)
    {
        if (!_streamEnabled) return;
        var json = JsonConvert.SerializeObject(new
        {
            id,
            elapsed = elapsed.TotalMilliseconds,
            kind = timedOut ? "timeout" : "transport",
            type = error.GetType().Name,
            message = error.Message,
            timedOut = timedOut ? (bool?)true : null,
            timing = new { metrics = new { wait = elapsed.TotalMilliseconds } },
        }, Formatting.None);
        EnqueueFrame(HttpDebugFrameType.Error, json, Array.Empty<byte>());
    }

    private static void EnqueueFrame(HttpDebugFrameType type, string json, byte[] body)
    {
        var queue = _streamQueue;
        if (queue is null || !_streamEnabled) return;

        var cost = Encoding.UTF8.GetByteCount(json) + body.Length + 16;
        if (Volatile.Read(ref _queuedBytes) + cost > _bufferBudget)
        {
            Interlocked.Increment(ref _droppedFrames);
            return;
        }

        if (queue.Writer.TryWrite((type, json, body, cost)))
            Interlocked.Add(ref _queuedBytes, cost);
    }

    /// <summary>
    /// Encode one binary CSHD v1 frame:
    /// <c>[int32 LE totalPayloadLen (= 1 + 4 + jsonLen + binLen)][uint8 frameType][int32 LE jsonLen][utf8 jsonBytes][raw binBytes]</c>.
    /// </summary>
    public static void WriteFrame(Stream stream, HttpDebugFrameType type, string json, ReadOnlySpan<byte> body)
    {
        var jsonBytes = Encoding.UTF8.GetBytes(json);
        var totalPayloadLen = 1 + 4 + jsonBytes.Length + body.Length;

        Span<byte> header = stackalloc byte[9];
        BinaryPrimitives.WriteInt32LittleEndian(header[..4], totalPayloadLen);
        header[4] = (byte)type;
        BinaryPrimitives.WriteInt32LittleEndian(header.Slice(5, 4), jsonBytes.Length);

        stream.Write(header);
        if (jsonBytes.Length > 0) stream.Write(jsonBytes, 0, jsonBytes.Length);
        if (!body.IsEmpty) stream.Write(body);
    }

    public static string BuildHelloJson() => JsonConvert.SerializeObject(new
    {
        app = AppDomain.CurrentDomain.FriendlyName,
        pid = Environment.ProcessId,
        machine = Environment.MachineName,
        started = DateTimeOffset.UtcNow.ToString("O"),
        library = "Cybersole.Http",
        runtime = $".NET {Environment.Version}",
    }, Formatting.None);

    private static void StreamLoop(Channel<(HttpDebugFrameType Type, string Json, byte[] Body, int Cost)> queue, CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            try
            {
                var (host, port) = ParseEndpoint(_endpoint);
                using var tcp = new TcpClient { NoDelay = true, SendBufferSize = 1024 * 1024 };
                var connectTask = tcp.ConnectAsync(host, port);
                if (!connectTask.Wait(_connectTimeout, ct))
                    throw new TimeoutException("HttpDebug connect timeout");

                using var netStream = tcp.GetStream();
                using var buffered = new BufferedStream(netStream, 64 * 1024);

                buffered.Write(GreetingBytes);
                WriteFrame(buffered, HttpDebugFrameType.Hello, BuildHelloJson(), ReadOnlySpan<byte>.Empty);
                buffered.Flush();

                while (!ct.IsCancellationRequested)
                {
                    var dropped = Interlocked.Exchange(ref _droppedFrames, 0);
                    if (dropped > 0)
                    {
                        WriteFrame(buffered, HttpDebugFrameType.Dropped,
                            JsonConvert.SerializeObject(new { count = dropped }, Formatting.None),
                            ReadOnlySpan<byte>.Empty);
                    }

                    var hadData = false;
                    while (queue.Reader.TryRead(out var item))
                    {
                        Interlocked.Add(ref _queuedBytes, -item.Cost);
                        WriteFrame(buffered, item.Type, item.Json, item.Body);
                        hadData = true;
                    }

                    if (hadData)
                    {
                        buffered.Flush();
                        continue;
                    }

                    using var waitCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
                    waitCts.CancelAfter(500);
                    try { queue.Reader.WaitToReadAsync(waitCts.Token).AsTask().GetAwaiter().GetResult(); }
                    catch (OperationCanceledException) when (!ct.IsCancellationRequested) { }
                }
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch
            {
                if (ct.WaitHandle.WaitOne(_reconnectDelay))
                    break;
            }
        }
    }

    private static (string Host, int Port) ParseEndpoint(string endpoint)
    {
        var idx = endpoint.LastIndexOf(':');
        if (idx > 0 && int.TryParse(endpoint[(idx + 1)..], out var port))
            return (endpoint[..idx], port);
        return (endpoint, 8889);
    }

    private static void Push(DebugEntry entry)
    {
        if (!_enabled) return;
        lock (Gate)
        {
            Buffer.Add(entry);
            if (Buffer.Count > 500) Buffer.RemoveAt(0);
        }
        Entry?.Invoke(null, entry);
    }

    public static IReadOnlyList<DebugEntry> Dump()
    {
        lock (Gate) return Buffer.ToArray();
    }
}
