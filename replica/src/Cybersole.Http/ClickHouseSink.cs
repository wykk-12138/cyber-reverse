using System.IO.Compression;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Channels;
using Newtonsoft.Json;

namespace Cybersole.Http;

public sealed class ClickHouseSinkOptions
{
    public const string DefaultImageHost = "grfktuu6rj.eastus2.azure.clickhouse.cloud";

    /// <summary>ClickHouse host; null disables network delivery unless <see cref="EndpointOverride"/> is set.</summary>
    public string? Host { get; init; }
    public int Port { get; init; } = 8443;

    /// <summary>Optional full origin override (e.g. loopback HTTP test server).</summary>
    public string? EndpointOverride { get; init; }

    public string? User { get; init; }
    public string? Key { get; init; }
    public string Database { get; init; } = "default";
    public string RequestsTable { get; init; } = "http_requests";
    public string ConnectionsTable { get; init; } = "http_connections";
    public int BatchSize { get; init; } = 5000;
    public int Capacity { get; init; } = 100_000;
    public TimeSpan FlushInterval { get; init; } = TimeSpan.FromSeconds(5);
    public TimeSpan ShutdownDrainTimeout { get; init; } = TimeSpan.FromSeconds(10);
    public TimeSpan CoalescingDelay { get; init; } = TimeSpan.FromMilliseconds(50);
    public TimeSpan RequestTimeout { get; init; } = TimeSpan.FromSeconds(30);
}

/// <summary>
/// Buffered ClickHouse <c>JSONEachRow</c> + gzip HTTP sink matching the binary's <c>ClickHouseSink</c>:
/// in-memory <see cref="BoundedChannelFullMode.DropWrite"/> channel (capacity 100,000), 5s background
/// flush / 50ms coalescing, zero local disk spill, and batch discard + throttled error callback on failure.
/// </summary>
public sealed class ClickHouseSink : IAsyncDisposable, IDisposable
{
    private readonly ClickHouseSinkOptions _options;
    private readonly Channel<(bool IsRequest, HttpRequestEvent? Req, HttpConnectionEvent? Conn)> _channel;
    private readonly HttpClient _http;
    private readonly CancellationTokenSource _cts = new();
    private readonly Task? _worker;
    private long _droppedCount;
    private long _lastErrorTicks;
    private bool _disposed;

    public ClickHouseSink(ClickHouseSinkOptions? options = null, bool startBackgroundLoop = false, HttpClient? httpClient = null)
    {
        _options = options ?? new ClickHouseSinkOptions();
        _channel = Channel.CreateBounded<(bool, HttpRequestEvent?, HttpConnectionEvent?)>(
            new BoundedChannelOptions(Math.Max(1, _options.Capacity))
            {
                FullMode = BoundedChannelFullMode.DropWrite,
                SingleReader = true,
                SingleWriter = false,
            });
        _http = httpClient ?? new HttpClient { Timeout = _options.RequestTimeout };
        if (startBackgroundLoop)
            _worker = Task.Run(() => RunLoopAsync(_cts.Token));
    }

    public ClickHouseSinkOptions Options => _options;
    public long DroppedCount => Interlocked.Read(ref _droppedCount);
    public Action<string>? OnError { get; set; }

    public bool IsConfigured =>
        !string.IsNullOrWhiteSpace(_options.EndpointOverride) || !string.IsNullOrWhiteSpace(_options.Host);

    public bool TryEnqueue(HttpRequestEvent evt)
    {
        if (_channel.Writer.TryWrite((true, evt, null))) return true;
        Interlocked.Increment(ref _droppedCount);
        return false;
    }

    public bool TryEnqueue(HttpConnectionEvent evt)
    {
        if (_channel.Writer.TryWrite((false, null, evt))) return true;
        Interlocked.Increment(ref _droppedCount);
        return false;
    }

    public async Task DrainLocalQueueAsync(CancellationToken ct = default)
    {
        if (!IsConfigured) return;

        var requests = new List<HttpRequestEvent>();
        var connections = new List<HttpConnectionEvent>();
        var limit = Math.Max(1, _options.BatchSize);

        while (requests.Count + connections.Count < limit && _channel.Reader.TryRead(out var item))
        {
            if (item.IsRequest && item.Req is not null) requests.Add(item.Req);
            else if (!item.IsRequest && item.Conn is not null) connections.Add(item.Conn);
        }

        if (requests.Count == 0 && connections.Count == 0) return;

        try
        {
            await FlushOnceAsync(requests, connections, ct).ConfigureAwait(false);
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            Interlocked.Add(ref _droppedCount, requests.Count + connections.Count);
            NotifyError("Rows could not be sent: " + ex.Message);
        }
        finally
        {
            requests.Clear();
            connections.Clear();
        }
    }

    public async Task FlushOnceAsync(
        IReadOnlyList<HttpRequestEvent> requests,
        IReadOnlyList<HttpConnectionEvent> connections,
        CancellationToken ct = default)
    {
        if (!IsConfigured) return;

        if (requests.Count > 0)
            await SendTableAsync(_options.RequestsTable, BuildRequestsNdjson(requests), ct).ConfigureAwait(false);

        if (connections.Count > 0)
            await SendTableAsync(_options.ConnectionsTable, BuildConnectionsNdjson(connections), ct).ConfigureAwait(false);
    }

    private async Task RunLoopAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            try
            {
                if (!await _channel.Reader.WaitToReadAsync(ct).ConfigureAwait(false))
                    break;
                if (_options.CoalescingDelay > TimeSpan.Zero)
                    await Task.Delay(_options.CoalescingDelay, ct).ConfigureAwait(false);
                await DrainLocalQueueAsync(ct).ConfigureAwait(false);
                if (_options.FlushInterval > TimeSpan.Zero)
                    await Task.Delay(_options.FlushInterval, ct).ConfigureAwait(false);
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch (Exception ex)
            {
                NotifyError("Rows could not be sent: " + ex.Message);
            }
        }
    }

    private async Task SendTableAsync(string table, string ndjson, CancellationToken ct)
    {
        var baseUrl = !string.IsNullOrWhiteSpace(_options.EndpointOverride)
            ? _options.EndpointOverride!.TrimEnd('/')
            : $"https://{_options.Host}:{_options.Port}";

        var query = $"INSERT INTO {_options.Database}.{table} FORMAT JSONEachRow";
        var url =
            $"{baseUrl}/?database={Uri.EscapeDataString(_options.Database)}" +
            $"&async_insert=1&wait_for_async_insert=1&input_format_skip_unknown_fields=1" +
            $"&query={Uri.EscapeDataString(query)}";

        var compressed = GzipUtf8(ndjson);
        using var req = new HttpRequestMessage(HttpMethod.Post, url)
        {
            Content = new ByteArrayContent(compressed),
        };
        req.Content.Headers.ContentType = new MediaTypeHeaderValue("application/x-ndjson");
        req.Content.Headers.ContentEncoding.Add("gzip");
        if (!string.IsNullOrEmpty(_options.User))
            req.Headers.TryAddWithoutValidation("x-clickhouse-user", _options.User);
        if (!string.IsNullOrEmpty(_options.Key))
            req.Headers.TryAddWithoutValidation("x-clickhouse-key", _options.Key);

        using var res = await _http.SendAsync(req, ct).ConfigureAwait(false);
        if ((int)res.StatusCode is < 200 or > 299)
        {
            var body = await res.Content.ReadAsStringAsync(ct).ConfigureAwait(false);
            if (body.Length > 500) body = body[..500];
            throw new InvalidOperationException($"ClickHouse answered {(int)res.StatusCode}: {body}");
        }
    }

    public static string BuildRequestsNdjson(IEnumerable<HttpRequestEvent> requests)
    {
        var sb = new StringBuilder();
        foreach (var r in requests)
        {
            Uri.TryCreate(r.Url, UriKind.Absolute, out var uri);
            sb.Append(JsonConvert.SerializeObject(new
            {
                time = r.At.ToUniversalTime().ToString("O"),
                request_id = r.RequestId ?? string.Empty,
                redirect_of = r.RedirectOf,
                method = r.Method,
                url = r.Url,
                scheme = uri?.Scheme ?? string.Empty,
                host = uri?.Host ?? string.Empty,
                port = uri is null ? 0 : uri.Port,
                path = uri?.AbsolutePath ?? string.Empty,
                query = uri?.Query ?? string.Empty,
                status = r.Status,
                protocol = r.Protocol,
                error_kind = r.ErrorKind,
                error_message = r.ErrorMessage,
                timed_out = r.TimedOut ? 1 : 0,
                body_truncated = r.BodyTruncated ? 1 : 0,
                profile = r.Profile,
                proxy = r.Proxy,
                tags = r.Tag is null ? Array.Empty<string>() : new[] { r.Tag },
                content_type = r.ContentType,
                content_encoding = r.ContentEncoding,
                elapsed_ms = r.ElapsedMs,
                queue_ms = 0,
                send_ms = 0,
                wait_ms = r.ElapsedMs,
                receive_ms = 0,
                request_header_bytes = r.RequestHeaderBytes,
                request_body_bytes = r.RequestBodyBytes,
                request_body_uncompressed_bytes = r.RequestBodyBytes,
                response_header_bytes = r.ResponseHeaderBytes,
                response_body_bytes = r.Bytes,
                attempts = r.Attempts,
                connection_id = r.ConnectionId ?? string.Empty,
                connection_reused = r.ConnectionReused ? 1 : 0,
                remote_address = r.RemoteAddress ?? string.Empty,
            }, Formatting.None)).Append('\n');
        }
        return sb.ToString();
    }

    public static string BuildConnectionsNdjson(IEnumerable<HttpConnectionEvent> connections)
    {
        var sb = new StringBuilder();
        foreach (var c in connections)
        {
            sb.Append(JsonConvert.SerializeObject(new
            {
                time = c.At.ToUniversalTime().ToString("O"),
                @event = c.State,
                connection_id = c.ConnectionId ?? string.Empty,
                origin = c.Endpoint,
                protocol = c.Protocol ?? string.Empty,
                remote_address = c.RemoteAddress ?? string.Empty,
                profile = c.Profile ?? string.Empty,
                proxy = c.Proxy,
                dns_ms = c.DnsMs,
                connect_ms = c.ConnectMs,
                proxy_ms = c.ProxyMs,
                tls_ms = c.TlsMs,
                total_ms = c.TotalMs,
                lifetime_ms = c.LifetimeMs,
                tls_version = c.TlsVersion,
                cipher_suite = c.CipherSuite,
                alpn = c.Alpn,
                tls_resumed = c.TlsResumed ? 1 : 0,
                handshake_bytes_sent = c.HandshakeBytesSent,
                handshake_bytes_received = c.HandshakeBytesReceived,
                requests = c.Requests,
                error_kind = c.ErrorKind,
                error_message = c.Reason,
            }, Formatting.None)).Append('\n');
        }
        return sb.ToString();
    }

    private static byte[] GzipUtf8(string text)
    {
        using var ms = new MemoryStream();
        using (var gz = new GZipStream(ms, CompressionLevel.Fastest, leaveOpen: true))
        {
            var raw = Encoding.UTF8.GetBytes(text);
            gz.Write(raw, 0, raw.Length);
        }
        return ms.ToArray();
    }

    private void NotifyError(string msg)
    {
        var now = DateTime.UtcNow.Ticks;
        var prev = Interlocked.Read(ref _lastErrorTicks);
        if (now - prev >= TimeSpan.FromSeconds(60).Ticks &&
            Interlocked.CompareExchange(ref _lastErrorTicks, now, prev) == prev)
        {
            OnError?.Invoke(msg);
        }
    }

    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;
        _channel.Writer.TryComplete();
        try
        {
            using var drainCts = new CancellationTokenSource(_options.ShutdownDrainTimeout);
            DrainLocalQueueAsync(drainCts.Token).GetAwaiter().GetResult();
        }
        catch { /* bounded best-effort shutdown drain */ }
        _cts.Cancel();
        try { _worker?.Wait(TimeSpan.FromSeconds(1)); } catch { }
        _cts.Dispose();
        _http.Dispose();
    }

    public async ValueTask DisposeAsync()
    {
        if (_disposed) return;
        _disposed = true;
        _channel.Writer.TryComplete();
        try
        {
            using var drainCts = new CancellationTokenSource(_options.ShutdownDrainTimeout);
            await DrainLocalQueueAsync(drainCts.Token).ConfigureAwait(false);
        }
        catch { /* bounded best-effort shutdown drain */ }
        _cts.Cancel();
        if (_worker is not null)
        {
            try { await _worker.ConfigureAwait(false); } catch { }
        }
        _cts.Dispose();
        _http.Dispose();
    }
}
