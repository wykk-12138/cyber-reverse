using System.Collections.Concurrent;
using System.Text;
using Newtonsoft.Json;

namespace Cybersole.Http;

public sealed class HttpRequestEvent
{
    public string Url { get; init; } = string.Empty;
    public string Method { get; init; } = "GET";
    public int Status { get; init; }
    public int ElapsedMs { get; init; }
    public long Bytes { get; init; }
    public string Protocol { get; init; } = "h2";
    public string Profile { get; init; } = "chrome";
    public string? Proxy { get; init; }
    public string? Tag { get; init; }
    public DateTime At { get; init; } = DateTime.UtcNow;
    public string? RequestId { get; init; }
    public string? RedirectOf { get; init; }
    public string? ErrorKind { get; init; }
    public string? ErrorMessage { get; init; }
    public bool TimedOut { get; init; }
    public bool BodyTruncated { get; init; }
    public string? ContentType { get; init; }
    public string? ContentEncoding { get; init; }
    public int RequestHeaderBytes { get; init; }
    public long RequestBodyBytes { get; init; }
    public int ResponseHeaderBytes { get; init; }
    public int Attempts { get; init; } = 1;
    public string? ConnectionId { get; init; }
    public bool ConnectionReused { get; init; }
    public string? RemoteAddress { get; init; }
}

/// <summary>
/// Something the analytics flush can hand a session summary to.
///
/// <para>
/// R155: the payload builder lives in <c>Cybersole.Stores</c>, which references this assembly and not the
/// other way round. So the interface lives here and the implementation lives there — the direction of the
/// dependency is the reason, and it also keeps this class from knowing what a fingerprint is.
/// </para>
/// </summary>
public interface ISessionSink
{
    /// <summary>True when the sink has somewhere to send. A false sink is not called at all.</summary>
    bool IsConfigured { get; }

    /// <summary>Build and send one session payload. Never throws.</summary>
    Task<bool> SendAsync(CancellationToken ct = default);
}

public sealed class HttpConnectionEvent
{
    public string Endpoint { get; init; } = string.Empty;
    public string State { get; init; } = "opened"; // opened | failed | closed
    public string? Proxy { get; init; }
    public string? Reason { get; init; }
    public DateTime At { get; init; } = DateTime.UtcNow;
    public string? ConnectionId { get; init; }
    public string? Protocol { get; init; }
    public string? RemoteAddress { get; init; }
    public string? Profile { get; init; }
    public int DnsMs { get; init; }
    public int ConnectMs { get; init; }
    public int ProxyMs { get; init; }
    public int TlsMs { get; init; }
    public int TotalMs { get; init; }
    public int LifetimeMs { get; init; }
    public string? TlsVersion { get; init; }
    public string? CipherSuite { get; init; }
    public string? Alpn { get; init; }
    public bool TlsResumed { get; init; }
    public int HandshakeBytesSent { get; init; }
    public int HandshakeBytesReceived { get; init; }
    public int Requests { get; init; }
    public string? ErrorKind { get; init; }
}

/// <summary>
/// Request/connection analytics (Cybersole.Http.Analytics).
/// Mirrors the original: every request and connection is buffered and flushed in batches.
/// </summary>
public sealed class HttpAnalytics : IDisposable
{
    private readonly ConcurrentQueue<HttpRequestEvent> _requests = new();
    private readonly ConcurrentQueue<HttpConnectionEvent> _connections = new();
    private readonly ConcurrentQueue<string> _failures = new();
    private readonly Timer? _flushTimer;

    public event EventHandler<HttpRequestEvent>? RequestRecorded;
    public event EventHandler<HttpConnectionEvent>? ConnectionRecorded;

    /// <summary>Optional ClickHouse HTTP endpoint; when null, events stay in memory.</summary>
    public string? SinkUrl { get; set; }

    /// <summary>
    /// Optional session-payload sink, drained by the same flush (R155).
    ///
    /// <para>
    /// Separate from <see cref="SinkUrl"/> on purpose: the two send different documents to different hosts,
    /// and either can be configured without the other. A flush with neither does nothing at all, which is the
    /// offline case.
    /// </para>
    /// </summary>
    public ISessionSink? SessionSink { get; set; }
    /// <summary>Optional structured ClickHouse JSONEachRow + gzip sink backed by a bounded in-memory channel.</summary>
    public ClickHouseSink? ClickHouse { get; set; }

    public int BatchSize { get; set; } = 100;

    public ClickHouseSink ConfigureClickHouse(ClickHouseSinkOptions options, bool startBackgroundLoop = false)
    {
        var sink = new ClickHouseSink(options, startBackgroundLoop);
        ClickHouse = sink;
        return sink;
    }

    public HttpAnalytics(bool autoFlush = false)
    {
        if (autoFlush)
            _flushTimer = new Timer(_ => Flush(), null, TimeSpan.FromSeconds(10), TimeSpan.FromSeconds(10));
    }

    public IReadOnlyCollection<HttpRequestEvent> Snapshot => _requests.ToArray();
    public IReadOnlyCollection<HttpConnectionEvent> Connections => _connections.ToArray();
    public IReadOnlyCollection<string> Failures => _failures.ToArray();

    public void Record(HttpRequestEvent evt)
    {
        _requests.Enqueue(evt);
        ClickHouse?.TryEnqueue(evt);
        RequestRecorded?.Invoke(this, evt);
        if (_requests.Count >= BatchSize) Flush();
    }

    public void RecordConnection(HttpConnectionEvent evt)
    {
        _connections.Enqueue(evt);
        ClickHouse?.TryEnqueue(evt);
        ConnectionRecorded?.Invoke(this, evt);
    }

    public void RecordFailure(string url, string? proxy, string reason)
    {
        _failures.Enqueue($"{DateTime.UtcNow:O} {url} proxy={proxy ?? "-"} reason={reason}");
        if (_failures.Count > 2000) _failures.TryDequeue(out _);
        RecordConnection(new HttpConnectionEvent
        {
            Endpoint = url,
            State = "failed",
            Proxy = proxy,
            Reason = reason,
        });
    }

    /// <summary>
    /// Drain pending events and, when a sink is configured, post them as one ClickHouse
    /// JSONEachRow batch.
    ///
    /// Round 127: the body used to be
    /// <code>
    /// while (_requests.TryDequeue(out var req))
    /// {
    ///     // Sink integration point: POST req as JSON to ClickHouse in batches.
    ///     if (SinkUrl is null) break;
    /// }
    /// </code>
    /// — an empty loop that dequeued *before* testing SinkUrl, so calling Flush() with no sink
    /// silently destroyed every buffered event. The live build writes the batch to ClickHouse;
    /// this now does the same and leaves the queue alone when there is nowhere to send it.
    /// </summary>
    public void Flush()
    {
        // R155: the session sink is a second, independent destination. Returning early on `SinkUrl is null`
        // would have made a telemetry-only configuration silently never send — the same class of defect as
        // R127's dequeue-before-test.
        var session = SessionSink;
        if (session is not null && session.IsConfigured)
        {
            _ = Task.Run(async () =>
            {
                try { await session.SendAsync(CancellationToken.None).ConfigureAwait(false); }
                catch (Exception ex) { _failures.Enqueue($"{DateTime.UtcNow:O} session sink failed: {ex.Message}"); }
            });
        }

        if (ClickHouse is { IsConfigured: true } clickHouse)
        {
            _ = Task.Run(async () =>
            {
                try { await clickHouse.DrainLocalQueueAsync(CancellationToken.None).ConfigureAwait(false); }
                catch (Exception ex) { _failures.Enqueue($"{DateTime.UtcNow:O} clickhouse drain failed: {ex.Message}"); }
            });
        }

        if (SinkUrl is null) return;     // nothing to do on the request side, and nothing to lose

        var batch = new List<HttpRequestEvent>(Math.Min(BatchSize, 256));
        while (batch.Count < BatchSize && _requests.TryDequeue(out var req))
            batch.Add(req);

        if (batch.Count == 0) return;

        var body = new StringBuilder();
        foreach (var r in batch)
        {
            // ClickHouse JSONEachRow: one compact object per line, no wrapping array
            body.Append(JsonConvert.SerializeObject(new
            {
                at = r.At.ToUniversalTime().ToString("O"),
                method = r.Method,
                url = r.Url,
                status = r.Status,
                elapsed_ms = r.ElapsedMs,
                bytes = r.Bytes,
                protocol = r.Protocol,
                tag = r.Tag,
                profile = r.Profile,
                proxy = r.Proxy,
            }, Formatting.None)).Append('\n');
        }

        var target = SinkUrl;
        var payload = body.ToString();

        // fire and forget: analytics must never stall a request. A failure is recorded rather
        // than thrown, because the caller is the hot path of a checkout.
        _ = Task.Run(async () =>
        {
            try
            {
                using var http = new System.Net.Http.HttpClient { Timeout = TimeSpan.FromSeconds(15) };
                using var content = new System.Net.Http.StringContent(
                    payload, Encoding.UTF8, "application/x-ndjson");
                using var res = await http.PostAsync(target, content).ConfigureAwait(false);
                if (!res.IsSuccessStatusCode)
                    _failures.Enqueue($"{DateTime.UtcNow:O} sink {target} rejected batch: HTTP {(int)res.StatusCode}");
            }
            catch (Exception ex)
            {
                _failures.Enqueue($"{DateTime.UtcNow:O} sink {target} failed: {ex.Message}");
            }
        });
    }

    public void Dispose()
    {
        _flushTimer?.Dispose();
        ClickHouse?.Dispose();
    }
}
