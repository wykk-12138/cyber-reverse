using System.Text;
using Cybersole.Core.Models;
using Cybersole.Http.Compression;

namespace Cybersole.Http;

/// <summary>
/// Minimal HTTP/1.1 client running on top of the BouncyCastle TLS channel
/// (<see cref="BouncyTls"/>). This is the "own stack" path: the ClientHello is
/// fully controlled, so the request no longer depends on SChannel behaviour.
/// </summary>
public sealed class BouncyHttpClient : IDisposable, IAsyncDisposable
{
    private readonly HttpAnalytics? _analytics;

    public BouncyHttpClient(HttpAnalytics? analytics = null) => _analytics = analytics;

    public async Task<NetResponse> GetAsync(string url, TlsProfile? profile = null, bool forceHttp11 = false,
        Proxy? proxy = null, TimeSpan? timeout = null, string? tag = null, CancellationToken ct = default)
    {
        profile ??= TlsProfile.Chrome;
        if (forceHttp11) profile = profile.WithAlpn("http/1.1");
        var uri = new Uri(url);
        var port = uri.Port > 0 ? uri.Port : (uri.Scheme == "https" ? 443 : 80);

        if (uri.Scheme != "https")
            throw new NetException("BouncyHttpClient only supports https://");

        var sw = System.Diagnostics.Stopwatch.StartNew();
        var (protocol, probe) = await BouncyTls.ConnectAsync(uri.Host, port, profile, proxy, ct)
            .ConfigureAwait(false);
        if (protocol is null)
            throw new NetException($"TLS handshake failed: {probe.Error}");

        try
        {
            using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
            cts.CancelAfter(timeout ?? TimeSpan.FromSeconds(30));

            var stream = protocol.Stream;
            var request = BuildRequest(uri, profile);
            await stream.WriteAsync(request, cts.Token).ConfigureAwait(false);
            await stream.FlushAsync(cts.Token).ConfigureAwait(false);

            var raw = await ReadResponseAsync(stream, cts.Token).ConfigureAwait(false);
            sw.Stop();

            var response = HandleResponse(raw);

            _analytics?.Record(new HttpRequestEvent
            {
                Url = uri.ToString(),
                Method = "GET",
                Status = response.StatusCode,
                ElapsedMs = (int)sw.Elapsed.TotalMilliseconds,
                Bytes = response.Bytes,
                Protocol = "tls-bc/1.1",
                Profile = profile.Name,
                Proxy = proxy?.Uri,
                Tag = tag,
                At = DateTime.UtcNow,
            });

            return new NetResponse
            {
                StatusCode = response.StatusCode,
                Body = response.Body,
                Url = uri,
                Headers = response.Headers,
                Cookies = response.Cookies,
                Elapsed = sw.Elapsed,
                Bytes = response.Bytes,
                Protocol = "http/1.1",
            };
        }
        finally
        {
            try { protocol.Close(); } catch { /* closing a dead channel */ }
        }
    }

    /// <summary>
    /// Read until Content-Length is satisfied or the peer closes.
    /// BouncyCastle throws "No close_notify alert received before connection closed" when
    /// the server closes without a TLS close_notify; the bytes already buffered are valid.
    /// </summary>
    private static async Task<byte[]> ReadResponseAsync(Stream stream, CancellationToken ct)
    {
        using var buffer = new MemoryStream();
        var chunk = new byte[8192];
        var expected = -1;

        try
        {
            while (true)
            {
                var read = await stream.ReadAsync(chunk, ct).ConfigureAwait(false);
                if (read <= 0) break;
                buffer.Write(chunk, 0, read);

                if (expected < 0)
                {
                    var sofar = buffer.ToArray();
                    var sep = IndexOf(sofar, "\r\n\r\n"u8.ToArray());
                    if (sep >= 0)
                    {
                        var headerText = Encoding.ASCII.GetString(sofar, 0, sep);
                        var match = System.Text.RegularExpressions.Regex.Match(headerText,
                            @"Content-Length:\s*(\d+)",
                            System.Text.RegularExpressions.RegexOptions.IgnoreCase);
                        if (match.Success && int.TryParse(match.Groups[1].Value, out var len))
                            expected = sep + 4 + len;
                    }
                }

                if (expected > 0 && buffer.Length >= expected) break;
                if (buffer.Length > 16 * 1024 * 1024) break; // safety cap
            }
        }
        catch (Exception ex) when (IsCloseWithoutNotify(ex))
        {
            // peer closed the TCP stream without close_notify — everything read so far is valid
        }

        var data = buffer.ToArray();
        return expected > 0 && data.Length >= expected ? data[..expected] : data;
    }

    private static bool IsCloseWithoutNotify(Exception ex)
    {
        for (var e = ex; e is not null; e = e.InnerException)
        {
            if (e.Message.Contains("close_notify", StringComparison.OrdinalIgnoreCase))
                return true;
        }
        return ex is EndOfStreamException;
    }

    private static byte[] BuildRequest(Uri uri, TlsProfile profile)
    {
        var path = string.IsNullOrEmpty(uri.PathAndQuery) ? "/" : uri.PathAndQuery;
        var sb = new StringBuilder();
        sb.Append("GET ").Append(path).Append(" HTTP/1.1\r\n");
        sb.Append("Host: ").Append(uri.Host).Append("\r\n");
        sb.Append("User-Agent: ").Append(profile.UserAgent).Append("\r\n");
        sb.Append("Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\n");
        sb.Append("Accept-Language: ").Append(profile.AcceptLanguage).Append("\r\n");
        sb.Append("Accept-Encoding: ").Append(ContentEncodingCodec.DefaultAcceptEncoding).Append("\r\n");
        sb.Append("sec-ch-ua: ").Append(profile.SecChUa).Append("\r\n");
        sb.Append("sec-ch-ua-mobile: ").Append(profile.SecChUaMobile).Append("\r\n");
        sb.Append("sec-ch-ua-platform: ").Append(profile.SecChUaPlatform).Append("\r\n");
        sb.Append("sec-fetch-dest: document\r\nsec-fetch-mode: navigate\r\nsec-fetch-site: none\r\nsec-fetch-user: ?1\r\n");
        sb.Append("upgrade-insecure-requests: 1\r\n");
        sb.Append("Connection: close\r\n\r\n");
        return Encoding.ASCII.GetBytes(sb.ToString());
    }

    private static (int StatusCode, string Body, Dictionary<string, string> Headers,
        Dictionary<string, string> Cookies, long Bytes) HandleResponse(byte[] raw)
    {
        var separator = IndexOf(raw, "\r\n\r\n"u8.ToArray());
        if (separator < 0)
            throw new NetException("malformed HTTP response (no header terminator)");

        var headerText = Encoding.ASCII.GetString(raw, 0, separator);
        var lines = headerText.Split("\r\n");
        var status = 0;
        if (lines.Length > 0)
        {
            var parts = lines[0].Split(' ');
            if (parts.Length >= 2) int.TryParse(parts[1], out status);
        }

        var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        var cookies = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        foreach (var line in lines.Skip(1))
        {
            var idx = line.IndexOf(':');
            if (idx <= 0) continue;
            var key = line[..idx].Trim();
            var value = line[(idx + 1)..].Trim();
            headers[key] = value;
            if (key.Equals("Set-Cookie", StringComparison.OrdinalIgnoreCase))
            {
                var pair = value.Split(';')[0];
                var eq = pair.IndexOf('=');
                if (eq > 0) cookies[pair[..eq].Trim()] = pair[(eq + 1)..].Trim();
            }
        }

        var bodyBytes = raw.AsSpan(separator + 4).ToArray();

        if (headers.TryGetValue("Transfer-Encoding", out var te) &&
            te.Contains("chunked", StringComparison.OrdinalIgnoreCase))
        {
            bodyBytes = Dechunk(bodyBytes);
        }
        else if (headers.TryGetValue("Content-Length", out var cl) &&
                 int.TryParse(cl, out var len) && len <= bodyBytes.Length)
        {
            bodyBytes = bodyBytes[..len];
        }

        var body = Decode(bodyBytes, headers);
        return (status, body, headers, cookies, bodyBytes.LongLength);
    }

    private static byte[] Dechunk(byte[] data)
    {
        using var output = new MemoryStream();
        var pos = 0;
        while (pos < data.Length)
        {
            var lineEnd = IndexOf(data, "\r\n"u8.ToArray(), pos);
            if (lineEnd < 0) break;
            var sizeText = Encoding.ASCII.GetString(data, pos, lineEnd - pos).Split(';')[0].Trim();
            if (!int.TryParse(sizeText, System.Globalization.NumberStyles.HexNumber, null, out var size) || size == 0)
                break;
            pos = lineEnd + 2;
            if (pos + size > data.Length) size = data.Length - pos;
            output.Write(data, pos, size);
            pos += size + 2;
        }
        return output.ToArray();
    }

    private static string Decode(byte[] body, Dictionary<string, string> headers) =>
        ContentEncodingCodec.DecompressToString(body, headers);

    private static int IndexOf(byte[] haystack, byte[] needle, int start = 0)
    {
        for (var i = start; i <= haystack.Length - needle.Length; i++)
        {
            var match = true;
            for (var j = 0; j < needle.Length; j++)
            {
                if (haystack[i + j] != needle[j]) { match = false; break; }
            }
            if (match) return i;
        }
        return -1;
    }

    public void Dispose() { }

    // ── lifecycle ─────────────────────────────────────────────────────────────
    //
    // R910. The image names StartAsync, StopAsync and DisposeAsyncCore on its HTTP client and this class had none of
    // them: Dispose was an empty body, which is R850's shape without content wearing a different name. Four of the
    // five highest-leverage absent names in the whole replica were these, counted by how many places the original
    // references them -- StartAsync nineteen, HandleResponse eighteen, StopAsync fourteen, DisposeAsyncCore seven.
    //
    // What the lifecycle does here is what the state allows rather than what the original might do. Start marks the
    // client usable, Stop marks it not and releases anything held, and DisposeAsyncCore is Stop plus the synchronous
    // dispose. GetAsync refuses after Stop rather than opening a socket that nothing will close.
    //
    // Unknown: whether the original's StartAsync warms a connection pool, negotiates TLS ahead of the first request,
    // or does something else. The name says a lifecycle exists; it does not say what is in it, so this implements the
    // part that can be stated -- a state the client's own methods respect.

    private bool _started = true;
    private bool _stopped;

    /// <summary>True until <see cref="StopAsync"/> runs. A client that was never started still counts as usable,
    /// because the original's constructor path has to work before any explicit start.</summary>
    public bool IsRunning => _started && !_stopped;

    /// <summary>
    /// Marks the client usable. Idempotent, and refusing to start a stopped client keeps the state monotonic rather
    /// than letting a stray call reopen something already released.
    /// </summary>
    public Task StartAsync(CancellationToken ct = default)
    {
        ct.ThrowIfCancellationRequested();
        if (_stopped)
            throw new NetException("BouncyHttpClient cannot be restarted after StopAsync");
        _started = true;
        return Task.CompletedTask;
    }

    /// <summary>
    /// Marks the client unusable and releases what it holds. Idempotent. Requests begun before this call run to
    /// completion; requests begun after it are refused by <see cref="GetAsync"/>.
    /// </summary>
    public Task StopAsync(CancellationToken ct = default)
    {
        _stopped = true;
        _started = false;
        _analytics?.Flush();
        return Task.CompletedTask;
    }

    /// <summary>
    /// The asynchronous half of disposal, named as the image names it. Not virtual: this class is sealed, so the
    /// pattern's usual override point does not exist here and marking it virtual was a compile error.
    /// </summary>
    private async ValueTask DisposeAsyncCore()
    {
        await StopAsync().ConfigureAwait(false);
        Dispose();
    }

    /// <summary>Stop, then dispose, then suppress finalisation.</summary>
    public async ValueTask DisposeAsync()
    {
        await DisposeAsyncCore().ConfigureAwait(false);
        GC.SuppressFinalize(this);
    }
}
