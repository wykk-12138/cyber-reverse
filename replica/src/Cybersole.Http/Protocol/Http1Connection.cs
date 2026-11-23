using System.Buffers;
using System.Globalization;
using System.Text;

namespace Cybersole.Http.Protocol;

/// <summary>
/// Pure managed RFC 9112 HTTP/1.1 connection implementing <see cref="IMultiplexedConnection"/>
/// (<see cref="SupportsMultiplexing"/> = false, <see cref="MaxConcurrentStreams"/> = 1).
/// Supports profile <c>HeaderOrder</c>, <c>Expect: 100-continue</c>, <c>1xx</c> skipping,
/// <c>obs-fold</c> continuation lines, duplicate headers, chunked transfer-encoding with trailers,
/// <c>Content-Length</c>, close-delimited bodies, <c>HEAD</c>/204/304, and <see cref="HttpContentDecoder"/>.
/// </summary>
public sealed class Http1Connection : IMultiplexedConnection
{
    public const int MaxResponseHeaderLineBytes = 64 * 1024;
    public const int MaxResponseHeaderBytes = 0x100000; // 1 MiB per Cybersole.Http 0x14136F700

    private readonly Stream _stream;
    private readonly BufferedStreamReader _reader;
    private readonly IReadOnlyList<string>? _headerOrder;
    private readonly bool _closeConnection;
    private readonly bool _leaveStreamOpen;
    private readonly SemaphoreSlim _ioLock = new(1, 1);

    private int _activeStreams;
    private bool _isUsable = true;
    private bool _disposed;
    private DateTimeOffset _lastUsedUtc = DateTimeOffset.UtcNow;

    public Http1Connection(
        Stream stream,
        ConnectionKey key,
        IReadOnlyList<string>? headerOrder = null,
        bool closeConnection = false,
        bool leaveStreamOpen = false)
    {
        _stream = stream ?? throw new ArgumentNullException(nameof(stream));
        Key = key;
        _headerOrder = headerOrder;
        _closeConnection = closeConnection;
        _leaveStreamOpen = leaveStreamOpen;
        _reader = new BufferedStreamReader(_stream, BufferedStreamReader.DefaultBufferSize, leaveOpen: true);
    }

    public string ProtocolVersion => "http/1.1";
    public ConnectionKey Key { get; }
    public bool IsUsable => !_disposed && Volatile.Read(ref _isUsable);
    public bool SupportsMultiplexing => false;
    public int MaxConcurrentStreams => 1;
    public int ActiveStreams => Volatile.Read(ref _activeStreams);
    public DateTimeOffset LastUsedUtc => _lastUsedUtc;

    public bool CanAcceptNewStream() => IsUsable && ActiveStreams == 0;

    public async Task<PureHttpResponse> SendAsync(PureHttpRequest request, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(request);
        ObjectDisposedException.ThrowIf(_disposed, this);

        using CancellationTokenSource? timeoutCts =
            request.RequestTimeout is { } reqTimeout && reqTimeout > TimeSpan.Zero && reqTimeout != Timeout.InfiniteTimeSpan
                ? new CancellationTokenSource(reqTimeout)
                : null;
        using CancellationTokenSource? linkedCts = timeoutCts is not null
            ? CancellationTokenSource.CreateLinkedTokenSource(cancellationToken, timeoutCts.Token)
            : null;
        CancellationToken effectiveCt = linkedCts?.Token ?? cancellationToken;

        try
        {
            await _ioLock.WaitAsync(effectiveCt).ConfigureAwait(false);
        }
        catch (OperationCanceledException) when (timeoutCts is not null && timeoutCts.IsCancellationRequested && !cancellationToken.IsCancellationRequested)
        {
            throw new TimeoutException($"HTTP/1.1 request timed out after {request.RequestTimeout!.Value.TotalSeconds:0.###}s.");
        }

        Interlocked.Exchange(ref _activeStreams, 1);
        try
        {
            if (!IsUsable)
            {
                throw new PureHttpException(
                    HttpErrorKind.TransportIo,
                    "HTTP/1.1 connection is no longer usable.",
                    isRetryableOnFreshConnection: true);
            }

            _lastUsedUtc = DateTimeOffset.UtcNow;
            string method = request.Method.Trim().ToUpperInvariant();
            if (string.IsNullOrEmpty(method))
                throw new PureHttpException(HttpErrorKind.Protocol, "HTTP/1.1 request method cannot be empty.");

            byte[] requestHead = BuildRequestHeadBytes(
                request,
                method,
                out bool expect100Continue,
                out bool clientRequestedClose);

            await _stream.WriteAsync(requestHead, effectiveCt).ConfigureAwait(false);

            bool sentBody = false;
            ResponseHead head;

            if (expect100Continue && !request.Body.IsEmpty)
            {
                await _stream.FlushAsync(effectiveCt).ConfigureAwait(false);

                while (true)
                {
                    head = await ReadResponseHeadAsync(effectiveCt).ConfigureAwait(false);
                    if (head.StatusCode == 100)
                    {
                        await WriteBodyAsync(request.Body, effectiveCt).ConfigureAwait(false);
                        sentBody = true;
                        break;
                    }
                    if (head.StatusCode is > 100 and < 200)
                        continue;

                    // Server answered directly (e.g. 417 Expectation Failed) without expecting body.
                    Volatile.Write(ref _isUsable, false);
                    goto ReadBody;
                }
            }

            if (!sentBody && !request.Body.IsEmpty)
                await WriteBodyAsync(request.Body, effectiveCt).ConfigureAwait(false);
            else if (!expect100Continue || request.Body.IsEmpty)
                await _stream.FlushAsync(effectiveCt).ConfigureAwait(false);

            while (true)
            {
                head = await ReadResponseHeadAsync(effectiveCt).ConfigureAwait(false);
                if (head.StatusCode is >= 100 and < 200)
                    continue;
                break;
            }

        ReadBody:
            bool noBody = string.Equals(method, "HEAD", StringComparison.OrdinalIgnoreCase) ||
                          head.StatusCode is 204 or 304 ||
                          (head.StatusCode >= 100 && head.StatusCode < 200);

            var trailers = new List<PureHttpHeader>();
            byte[] rawBody = noBody
                ? Array.Empty<byte>()
                : await ReadResponseBodyAsync(head.Headers, trailers, request.MaxResponseBodyBytes, effectiveCt).ConfigureAwait(false);

            if (ShouldCloseConnection(head.HttpVersion, head.Headers, clientRequestedClose))
                Volatile.Write(ref _isUsable, false);

            byte[] finalBody = rawBody;
            if (request.AllowAutoDecompression && rawBody.Length > 0)
            {
                string? contentEncoding = CombineHeaderValues(head.Headers, "content-encoding");
                if (!string.IsNullOrWhiteSpace(contentEncoding))
                    finalBody = HttpContentDecoder.DecodeIfNeeded(rawBody, contentEncoding, request.MaxResponseBodyBytes);
            }

            _lastUsedUtc = DateTimeOffset.UtcNow;
            return new PureHttpResponse
            {
                StatusCode = head.StatusCode,
                HttpVersion = head.HttpVersion,
                Headers = head.Headers.AsReadOnly(),
                Trailers = trailers.AsReadOnly(),
                Body = finalBody,
            };
        }
        catch (OperationCanceledException) when (timeoutCts is not null && timeoutCts.IsCancellationRequested && !cancellationToken.IsCancellationRequested)
        {
            Volatile.Write(ref _isUsable, false);
            throw new TimeoutException($"HTTP/1.1 request timed out after {request.RequestTimeout!.Value.TotalSeconds:0.###}s.");
        }
        catch
        {
            Volatile.Write(ref _isUsable, false);
            throw;
        }
        finally
        {
            Interlocked.Exchange(ref _activeStreams, 0);
            _ioLock.Release();
        }
    }

    private async Task WriteBodyAsync(ReadOnlyMemory<byte> body, CancellationToken cancellationToken)
    {
        await _stream.WriteAsync(body, cancellationToken).ConfigureAwait(false);
        await _stream.FlushAsync(cancellationToken).ConfigureAwait(false);
    }

    private byte[] BuildRequestHeadBytes(
        PureHttpRequest request,
        string method,
        out bool expect100Continue,
        out bool clientRequestedClose)
    {
        string path = string.IsNullOrEmpty(request.Uri.PathAndQuery) ? "/" : request.Uri.PathAndQuery;
        string? explicitHost = null;
        bool hasUserAgent = false;
        bool hasContentLength = false;
        bool hasTransferEncoding = false;
        bool hasConnection = false;
        expect100Continue = false;
        clientRequestedClose = _closeConnection;

        var rawHeaders = new List<PureHttpHeader>(request.Headers.Count + 4);
        for (int i = 0; i < request.Headers.Count; i++)
        {
            PureHttpHeader h = request.Headers[i];
            if (string.IsNullOrWhiteSpace(h.Name))
                continue;

            string name = h.Name.Trim();
            if (name.StartsWith(':'))
                continue;

            ValidateHeaderNameAndValue(name, h.Value);
            string value = h.Value ?? string.Empty;

            if (string.Equals(name, "host", StringComparison.OrdinalIgnoreCase))
            {
                if (!string.IsNullOrWhiteSpace(value))
                    explicitHost = value.Trim();
                continue;
            }

            if (string.Equals(name, "user-agent", StringComparison.OrdinalIgnoreCase))
                hasUserAgent = true;
            else if (string.Equals(name, "content-length", StringComparison.OrdinalIgnoreCase))
                hasContentLength = true;
            else if (string.Equals(name, "transfer-encoding", StringComparison.OrdinalIgnoreCase))
                hasTransferEncoding = true;
            else if (string.Equals(name, "connection", StringComparison.OrdinalIgnoreCase))
            {
                hasConnection = true;
                if (ContainsToken(value, "close"))
                    clientRequestedClose = true;
                else if (ContainsToken(value, "keep-alive"))
                    clientRequestedClose = false;
            }
            else if (string.Equals(name, "expect", StringComparison.OrdinalIgnoreCase) &&
                     ContainsToken(value, "100-continue"))
            {
                expect100Continue = true;
            }

            rawHeaders.Add(new PureHttpHeader(name, value));
        }

        string hostValue = explicitHost ?? request.Uri.Authority;
        ValidateHeaderNameAndValue("Host", hostValue);

        if (!hasUserAgent)
            rawHeaders.Add(new PureHttpHeader("User-Agent", "Go-http-client/1.1"));

        if (!hasContentLength && !hasTransferEncoding &&
            (request.Body.Length > 0 || method is "POST" or "PUT" or "PATCH"))
        {
            rawHeaders.Add(new PureHttpHeader("Content-Length", request.Body.Length.ToString(CultureInfo.InvariantCulture)));
        }

        if (!hasConnection)
            rawHeaders.Add(new PureHttpHeader("Connection", _closeConnection ? "close" : "keep-alive"));

        bool hostInOrder = false;
        if (_headerOrder is { Count: > 0 })
        {
            for (int i = 0; i < _headerOrder.Count; i++)
            {
                if (string.Equals(_headerOrder[i].Trim(), "host", StringComparison.OrdinalIgnoreCase))
                {
                    hostInOrder = true;
                    break;
                }
            }
        }

        var ordered = new List<PureHttpHeader>(rawHeaders.Count + 1);
        if (hostInOrder)
            rawHeaders.Insert(0, new PureHttpHeader("Host", hostValue));
        else
            ordered.Add(new PureHttpHeader("Host", hostValue));

        if (_headerOrder is { Count: > 0 })
        {
            var emitted = new bool[rawHeaders.Count];
            for (int o = 0; o < _headerOrder.Count; o++)
            {
                string target = _headerOrder[o].Trim();
                if (target.Length == 0 || target.StartsWith(':'))
                    continue;

                for (int r = 0; r < rawHeaders.Count; r++)
                {
                    if (!emitted[r] && string.Equals(rawHeaders[r].Name, target, StringComparison.OrdinalIgnoreCase))
                    {
                        ordered.Add(rawHeaders[r]);
                        emitted[r] = true;
                    }
                }
            }

            for (int r = 0; r < rawHeaders.Count; r++)
            {
                if (!emitted[r])
                    ordered.Add(rawHeaders[r]);
            }
        }
        else
        {
            ordered.AddRange(rawHeaders);
        }

        var sb = new StringBuilder(512);
        sb.Append(method).Append(' ').Append(path).Append(" HTTP/1.1\r\n");
        for (int i = 0; i < ordered.Count; i++)
            sb.Append(ordered[i].Name).Append(": ").Append(ordered[i].Value).Append("\r\n");
        sb.Append("\r\n");
        return Encoding.Latin1.GetBytes(sb.ToString());
    }

    private readonly record struct ResponseHead(string HttpVersion, int StatusCode, List<PureHttpHeader> Headers);

    private async Task<ResponseHead> ReadResponseHeadAsync(CancellationToken cancellationToken)
    {
        long startOffset = _reader.TotalBytesConsumed;
        string? statusLine = await _reader.ReadLineAsciiAsync(MaxResponseHeaderLineBytes, cancellationToken).ConfigureAwait(false);
        if (statusLine is null)
        {
            throw new PureHttpException(
                HttpErrorKind.TransportIo,
                "Server closed connection before sending HTTP/1.1 status line.",
                isRetryableOnFreshConnection: true);
        }

        if (_reader.TotalBytesConsumed - startOffset > MaxResponseHeaderBytes)
            throw new PureHttpException(HttpErrorKind.Protocol, "server response headers exceeded the maximum size");

        ParseStatusLine(statusLine, out string httpVersion, out int statusCode);

        var headers = new List<PureHttpHeader>();
        while (true)
        {
            string? line = await _reader.ReadLineAsciiAsync(MaxResponseHeaderLineBytes, cancellationToken).ConfigureAwait(false);
            if (line is null)
            {
                throw new PureHttpException(
                    HttpErrorKind.TransportIo,
                    "Unexpected EOF while reading HTTP/1.1 response headers.",
                    isRetryableOnFreshConnection: true);
            }

            if (_reader.TotalBytesConsumed - startOffset > MaxResponseHeaderBytes)
                throw new PureHttpException(HttpErrorKind.Protocol, "server response headers exceeded the maximum size");

            if (line.Length == 0)
                break;

            if (line[0] is ' ' or '\t')
            {
                // HTTP/1.x obs-fold continuation line
                if (headers.Count == 0)
                    throw new PureHttpException(HttpErrorKind.Protocol, "Unexpected HTTP/1.1 obs-fold line before any header.");

                PureHttpHeader prev = headers[^1];
                string foldedValue = string.IsNullOrEmpty(prev.Value)
                    ? line.Trim()
                    : prev.Value + " " + line.Trim();
                headers[^1] = new PureHttpHeader(prev.Name, foldedValue);
                continue;
            }

            int colon = line.IndexOf(':');
            if (colon <= 0)
                throw new PureHttpException(HttpErrorKind.Protocol, $"Malformed HTTP/1.1 response header line: '{line}'.");

            string name = line[..colon];
            for (int i = 0; i < name.Length; i++)
            {
                if (name[i] <= ' ')
                    throw new PureHttpException(HttpErrorKind.Protocol, $"Invalid whitespace in HTTP/1.1 header name '{name}'.");
            }

            string value = line[(colon + 1)..].Trim();
            headers.Add(new PureHttpHeader(name, value));
        }

        return new ResponseHead(httpVersion, statusCode, headers);
    }

    private async Task<byte[]> ReadResponseBodyAsync(
        List<PureHttpHeader> headers,
        List<PureHttpHeader> trailers,
        long maxResponseBodyBytes,
        CancellationToken cancellationToken)
    {
        bool isChunked = false;
        for (int i = 0; i < headers.Count; i++)
        {
            if (string.Equals(headers[i].Name, "transfer-encoding", StringComparison.OrdinalIgnoreCase) &&
                ContainsToken(headers[i].Value, "chunked"))
            {
                isChunked = true;
            }
        }

        if (isChunked)
            return await ReadChunkedBodyAsync(trailers, maxResponseBodyBytes, cancellationToken).ConfigureAwait(false);

        if (TryParseContentLength(headers, out long? contentLength))
        {
            if (contentLength is not null)
                return await ReadExactLengthBodyAsync(contentLength.Value, maxResponseBodyBytes, cancellationToken).ConfigureAwait(false);
        }

        // Close-delimited response body (RFC 9112 §6.3 rule 7).
        Volatile.Write(ref _isUsable, false);
        return await ReadCloseDelimitedBodyAsync(maxResponseBodyBytes, cancellationToken).ConfigureAwait(false);
    }

    private async Task<byte[]> ReadChunkedBodyAsync(
        List<PureHttpHeader> trailers,
        long maxResponseBodyBytes,
        CancellationToken cancellationToken)
    {
        using var body = new MemoryStream();
        long trailerHeaderStart = 0;

        while (true)
        {
            string? sizeLine = await _reader.ReadLineAsciiAsync(MaxResponseHeaderLineBytes, cancellationToken).ConfigureAwait(false);
            if (sizeLine is null)
                throw new EndOfStreamException("Unexpected EOF while reading HTTP/1.1 chunk size.");

            int semiIdx = sizeLine.IndexOf(';');
            string hexPart = (semiIdx >= 0 ? sizeLine[..semiIdx] : sizeLine).Trim();
            if (hexPart.Length == 0 || !IsPureHexDigits(hexPart) ||
                !long.TryParse(hexPart, NumberStyles.AllowHexSpecifier, CultureInfo.InvariantCulture, out long chunkSize) ||
                chunkSize < 0)
            {
                throw new PureHttpException(HttpErrorKind.Protocol, $"Invalid HTTP/1.1 chunk size '{sizeLine}'.");
            }

            if (chunkSize == 0)
            {
                trailerHeaderStart = _reader.TotalBytesConsumed;
                while (true)
                {
                    string? trailerLine = await _reader.ReadLineAsciiAsync(MaxResponseHeaderLineBytes, cancellationToken).ConfigureAwait(false);
                    if (trailerLine is null)
                        throw new EndOfStreamException("Unexpected EOF while reading HTTP/1.1 chunked trailers.");
                    if (_reader.TotalBytesConsumed - trailerHeaderStart > MaxResponseHeaderBytes)
                        throw new PureHttpException(HttpErrorKind.Protocol, "HTTP/1.1 chunked trailers exceeded maximum header size.");
                    if (trailerLine.Length == 0)
                        break;

                    if (trailerLine[0] is ' ' or '\t')
                    {
                        if (trailers.Count == 0)
                            throw new PureHttpException(HttpErrorKind.Protocol, "Unexpected obs-fold line in HTTP/1.1 trailers.");
                        PureHttpHeader prev = trailers[^1];
                        trailers[^1] = new PureHttpHeader(prev.Name, prev.Value + " " + trailerLine.Trim());
                        continue;
                    }

                    int colon = trailerLine.IndexOf(':');
                    if (colon <= 0)
                        throw new PureHttpException(HttpErrorKind.Protocol, $"Malformed HTTP/1.1 trailer line: '{trailerLine}'.");

                    trailers.Add(new PureHttpHeader(trailerLine[..colon].Trim(), trailerLine[(colon + 1)..].Trim()));
                }
                break;
            }

            if (body.Length + chunkSize > maxResponseBodyBytes)
            {
                throw new PureHttpException(
                    HttpErrorKind.ResponseTooLarge,
                    $"HTTP/1.1 chunked response body exceeded {maxResponseBodyBytes} bytes.");
            }

            byte[] scratch = ArrayPool<byte>.Shared.Rent((int)Math.Min(chunkSize, 64 * 1024));
            try
            {
                long remaining = chunkSize;
                while (remaining > 0)
                {
                    int toRead = (int)Math.Min(remaining, scratch.Length);
                    await _reader.ReadExactAsync(scratch.AsMemory(0, toRead), cancellationToken).ConfigureAwait(false);
                    body.Write(scratch, 0, toRead);
                    remaining -= toRead;
                }
            }
            finally
            {
                ArrayPool<byte>.Shared.Return(scratch);
            }

            string? chunkCrLf = await _reader.ReadLineAsciiAsync(16, cancellationToken).ConfigureAwait(false);
            if (chunkCrLf is null)
                throw new EndOfStreamException("Unexpected EOF after HTTP/1.1 chunk payload.");
            if (chunkCrLf.Length != 0)
                throw new PureHttpException(HttpErrorKind.Protocol, "Missing CRLF terminator after HTTP/1.1 chunk payload.");
        }

        return body.ToArray();
    }

    private async Task<byte[]> ReadExactLengthBodyAsync(
        long contentLength,
        long maxResponseBodyBytes,
        CancellationToken cancellationToken)
    {
        if (contentLength > maxResponseBodyBytes)
        {
            throw new PureHttpException(
                HttpErrorKind.ResponseTooLarge,
                $"HTTP/1.1 Content-Length ({contentLength}) exceeds MaxResponseBodyBytes ({maxResponseBodyBytes}).");
        }

        if (contentLength == 0)
            return Array.Empty<byte>();

        using var body = new MemoryStream((int)Math.Min(contentLength, 64 * 1024));
        byte[] scratch = ArrayPool<byte>.Shared.Rent((int)Math.Min(contentLength, 64 * 1024));
        try
        {
            long remaining = contentLength;
            while (remaining > 0)
            {
                int toRead = (int)Math.Min(remaining, scratch.Length);
                await _reader.ReadExactAsync(scratch.AsMemory(0, toRead), cancellationToken).ConfigureAwait(false);
                body.Write(scratch, 0, toRead);
                remaining -= toRead;
            }
        }
        finally
        {
            ArrayPool<byte>.Shared.Return(scratch);
        }

        return body.ToArray();
    }

    private async Task<byte[]> ReadCloseDelimitedBodyAsync(long maxResponseBodyBytes, CancellationToken cancellationToken)
    {
        using var body = new MemoryStream();
        byte[] scratch = ArrayPool<byte>.Shared.Rent(64 * 1024);
        try
        {
            while (true)
            {
                int read = await _reader.ReadUpToAsync(scratch.AsMemory(), cancellationToken).ConfigureAwait(false);
                if (read == 0)
                    break;

                if (body.Length + read > maxResponseBodyBytes)
                {
                    throw new PureHttpException(
                        HttpErrorKind.ResponseTooLarge,
                        $"HTTP/1.1 close-delimited response body exceeded {maxResponseBodyBytes} bytes.");
                }

                body.Write(scratch, 0, read);
            }
        }
        finally
        {
            ArrayPool<byte>.Shared.Return(scratch);
        }

        return body.ToArray();
    }

    private static void ParseStatusLine(string statusLine, out string httpVersion, out int statusCode)
    {
        if (!statusLine.StartsWith("HTTP/1.", StringComparison.Ordinal) ||
            statusLine.Length < 12 ||
            statusLine[7] is < '0' or > '9' ||
            statusLine[8] != ' ')
        {
            throw new PureHttpException(HttpErrorKind.Protocol, $"Malformed HTTP/1.x status line: '{statusLine}'.");
        }

        if (statusLine[9] is < '0' or > '9' ||
            statusLine[10] is < '0' or > '9' ||
            statusLine[11] is < '0' or > '9' ||
            (statusLine.Length > 12 && statusLine[12] != ' '))
        {
            throw new PureHttpException(HttpErrorKind.Protocol, $"Malformed HTTP/1.x status code in '{statusLine}'.");
        }

        statusCode = (statusLine[9] - '0') * 100 + (statusLine[10] - '0') * 10 + (statusLine[11] - '0');
        if (statusCode < 100)
            throw new PureHttpException(HttpErrorKind.Protocol, $"Invalid HTTP/1.x status code {statusCode}.");

        httpVersion = statusLine[..8];
    }

    private static bool TryParseContentLength(List<PureHttpHeader> headers, out long? parsedLength)
    {
        parsedLength = null;
        for (int i = 0; i < headers.Count; i++)
        {
            if (!string.Equals(headers[i].Name, "content-length", StringComparison.OrdinalIgnoreCase))
                continue;

            string[] parts = headers[i].Value.Split(',', StringSplitOptions.TrimEntries);
            for (int p = 0; p < parts.Length; p++)
            {
                string part = parts[p];
                if (part.Length == 0 || !IsPureAsciiDigits(part) ||
                    !long.TryParse(part, NumberStyles.None, CultureInfo.InvariantCulture, out long val))
                {
                    throw new PureHttpException(HttpErrorKind.Protocol, $"Invalid HTTP/1.1 Content-Length value '{headers[i].Value}'.");
                }

                if (parsedLength is null)
                    parsedLength = val;
                else if (parsedLength.Value != val)
                    throw new PureHttpException(HttpErrorKind.Protocol, "Conflicting Content-Length headers in HTTP/1.1 response.");
            }
        }

        return parsedLength is not null;
    }

    private static bool ShouldCloseConnection(string httpVersion, List<PureHttpHeader> headers, bool clientRequestedClose)
    {
        if (clientRequestedClose)
            return true;

        bool serverExplicitClose = false;
        bool serverExplicitKeepAlive = false;
        for (int i = 0; i < headers.Count; i++)
        {
            if (string.Equals(headers[i].Name, "connection", StringComparison.OrdinalIgnoreCase))
            {
                if (ContainsToken(headers[i].Value, "close"))
                    serverExplicitClose = true;
                if (ContainsToken(headers[i].Value, "keep-alive"))
                    serverExplicitKeepAlive = true;
            }
        }

        if (serverExplicitClose)
            return true;

        if (string.Equals(httpVersion, "HTTP/1.0", StringComparison.Ordinal) && !serverExplicitKeepAlive)
            return true;

        return false;
    }

    private static bool ContainsToken(string headerValue, string targetToken)
    {
        string[] parts = headerValue.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        for (int i = 0; i < parts.Length; i++)
        {
            if (string.Equals(parts[i], targetToken, StringComparison.OrdinalIgnoreCase))
                return true;
        }
        return false;
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

    private static bool IsPureAsciiDigits(string text)
    {
        for (int i = 0; i < text.Length; i++)
        {
            if (text[i] is < '0' or > '9')
                return false;
        }
        return true;
    }

    private static bool IsPureHexDigits(string text)
    {
        for (int i = 0; i < text.Length; i++)
        {
            char c = text[i];
            bool ok = c is (>= '0' and <= '9') or (>= 'a' and <= 'f') or (>= 'A' and <= 'F');
            if (!ok)
                return false;
        }
        return true;
    }

    private static void ValidateHeaderNameAndValue(string name, string? value)
    {
        for (int i = 0; i < name.Length; i++)
        {
            char c = name[i];
            if (c <= ' ' || c >= 0x7F || c == ':')
                throw new PureHttpException(HttpErrorKind.Protocol, $"Invalid HTTP/1.1 header name '{name}'.");
        }

        if (value is not null && value.IndexOfAny(new[] { '\r', '\n', '\0' }) >= 0)
            throw new PureHttpException(HttpErrorKind.Protocol, $"Invalid HTTP/1.1 header value for '{name}'.");
    }

    public async ValueTask DisposeAsync()
    {
        if (_disposed)
            return;
        _disposed = true;
        Volatile.Write(ref _isUsable, false);

        if (!_leaveStreamOpen)
        {
            try
            {
                await _stream.DisposeAsync().ConfigureAwait(false);
            }
            catch
            {
                // Ignore transport teardown errors.
            }
        }

        _reader.Dispose();
        _ioLock.Dispose();
    }
}
