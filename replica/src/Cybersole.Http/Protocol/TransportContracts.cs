using System.IO.Compression;
using System.Net;
using System.Net.Sockets;
using Cybersole.Http.Tls;
using Cybersole.Http.X509;
using ZstdSharp;

namespace Cybersole.Http.Protocol;

/// <summary>Error taxonomy matching Cybersole.Http (0..14).</summary>
public enum HttpErrorKind
{
    None = 0,
    Canceled = 1,
    Timeout = 2,
    DnsResolution = 3,
    ConnectFailed = 4,
    Proxy = 5,
    Certificate = 6,
    TlsHandshake = 7,
    Protocol = 8,
    Reserved9 = 9,
    QuicTransport = 10,
    ResponseTooLarge = 11,
    TooManyRedirects = 12,
    ContentDecoding = 13,
    TransportIo = 14,
}

public class PureHttpException : Exception
{
    public PureHttpException(
        HttpErrorKind errorKind,
        string message,
        Exception? innerException = null,
        bool isRetryableOnFreshConnection = false,
        long? protocolErrorCode = null)
        : base(message, innerException)
    {
        ErrorKind = errorKind;
        IsRetryableOnFreshConnection = isRetryableOnFreshConnection;
        ProtocolErrorCode = protocolErrorCode;
    }

    public HttpErrorKind ErrorKind { get; }
    public bool IsRetryableOnFreshConnection { get; }
    public long? ProtocolErrorCode { get; }
}

public sealed class ProxyException : PureHttpException
{
    public ProxyException(string message, Exception? innerException = null, int? proxyStatusCode = null)
        : base(HttpErrorKind.Proxy, message, innerException, isRetryableOnFreshConnection: false, protocolErrorCode: proxyStatusCode)
    {
        ProxyStatusCode = proxyStatusCode;
    }

    public int? ProxyStatusCode { get; }
}

public sealed class QuicException : PureHttpException
{
    public QuicException(ulong errorCode, bool isApplicationError, string message, Exception? innerException = null, bool retryable = false)
        : base(HttpErrorKind.QuicTransport, message, innerException, isRetryableOnFreshConnection: retryable, protocolErrorCode: unchecked((long)errorCode))
    {
        ErrorCode = errorCode;
        IsApplicationError = isApplicationError;
    }

    public ulong ErrorCode { get; }
    public bool IsApplicationError { get; }
}

public sealed class Http3Exception : PureHttpException
{
    public Http3Exception(ulong h3ErrorCode, string message, Exception? innerException = null, bool retryable = false)
        : base(HttpErrorKind.Protocol, message, innerException, isRetryableOnFreshConnection: retryable, protocolErrorCode: unchecked((long)h3ErrorCode))
    {
        H3ErrorCode = h3ErrorCode;
    }

    public ulong H3ErrorCode { get; }
}

public sealed class Http2Exception : PureHttpException
{
    public Http2Exception(uint h2ErrorCode, bool isStreamReset, string message, Exception? innerException = null, bool retryable = false)
        : base(HttpErrorKind.Protocol, message, innerException, isRetryableOnFreshConnection: retryable, protocolErrorCode: h2ErrorCode)
    {
        H2ErrorCode = h2ErrorCode;
        IsStreamReset = isStreamReset;
    }

    public uint H2ErrorCode { get; }
    public bool IsStreamReset { get; }
}

/// <summary>Deterministic exception-to-<see cref="HttpErrorKind"/> classifier.</summary>
public static class HttpErrorClassifier
{
    public static HttpErrorKind Classify(Exception? exception)
    {
        for (Exception? cur = exception; cur is not null; cur = cur.InnerException)
        {
            switch (cur)
            {
                case PureHttpException pure:
                    return pure.ErrorKind;
                case CertificateValidationException:
                    return HttpErrorKind.Certificate;
                case TlsException:
                    return HttpErrorKind.TlsHandshake;
                case TimeoutException:
                    return HttpErrorKind.Timeout;
                case OperationCanceledException:
                    return HttpErrorKind.Canceled;
                case SocketException se when se.SocketErrorCode is SocketError.HostNotFound or SocketError.TryAgain or SocketError.NoData or SocketError.NoRecovery:
                    return HttpErrorKind.DnsResolution;
                case SocketException se when se.SocketErrorCode == SocketError.TimedOut:
                    return HttpErrorKind.Timeout;
                case SocketException se when se.SocketErrorCode is SocketError.ConnectionRefused or SocketError.HostUnreachable or SocketError.NetworkUnreachable or SocketError.AddressNotAvailable:
                    return HttpErrorKind.ConnectFailed;
                case SocketException:
                    return HttpErrorKind.TransportIo;
                case EndOfStreamException:
                case IOException:
                    return HttpErrorKind.TransportIo;
            }
        }

        return HttpErrorKind.TransportIo;
    }

    public static bool CanRetryOnFreshConnection(Exception? exception)
    {
        for (Exception? cur = exception; cur is not null; cur = cur.InnerException)
        {
            if (cur is PureHttpException pure && pure.IsRetryableOnFreshConnection)
                return true;
            if (cur is EndOfStreamException)
                return true;
            if (cur is SocketException se && se.SocketErrorCode is SocketError.ConnectionReset or SocketError.ConnectionAborted or SocketError.Shutdown)
                return true;
        }
        return false;
    }
}

public readonly record struct PureHttpHeader(string Name, string Value);

public sealed class PureHttpRequest
{
    public required string Method { get; init; }
    public required Uri Uri { get; init; }
    public IReadOnlyList<PureHttpHeader> Headers { get; init; } = Array.Empty<PureHttpHeader>();
    public ReadOnlyMemory<byte> Body { get; init; } = ReadOnlyMemory<byte>.Empty;
    public bool ForceHttp11 { get; init; }
    public bool AllowAutoDecompression { get; init; } = true;
    public long MaxResponseBodyBytes { get; init; } = 256L * 1024 * 1024;
    public TimeSpan? RequestTimeout { get; init; }
    public CertificateVerifyOptions? VerifyOptions { get; init; }
}

public sealed class PureHttpResponse
{
    public required int StatusCode { get; init; }
    public required string HttpVersion { get; init; }
    public IReadOnlyList<PureHttpHeader> Headers { get; init; } = Array.Empty<PureHttpHeader>();
    public IReadOnlyList<PureHttpHeader> Trailers { get; init; } = Array.Empty<PureHttpHeader>();
    public byte[] Body { get; init; } = Array.Empty<byte>();
    public string? AltSvcHeader => GetFirstHeader("alt-svc");

    public string? GetFirstHeader(string name)
    {
        foreach (PureHttpHeader h in Headers)
        {
            if (string.Equals(h.Name, name, StringComparison.OrdinalIgnoreCase))
                return h.Value;
        }
        return null;
    }

    public IEnumerable<string> GetHeaderValues(string name)
    {
        foreach (PureHttpHeader h in Headers)
        {
            if (string.Equals(h.Name, name, StringComparison.OrdinalIgnoreCase))
                yield return h.Value;
        }
    }
}

public enum ProxyProtocolKind
{
    None = 0,
    Http = 1,
    Https = 2,
    Socks5 = 3,
}

public sealed record ProxySpec(
    ProxyProtocolKind Kind,
    string Host,
    int Port,
    string? Username = null,
    string? Password = null,
    bool RemoteDns = true)
{
    public bool SupportsUdp => Kind == ProxyProtocolKind.Socks5;

    public string CanonicalKey => Kind == ProxyProtocolKind.None
        ? "direct"
        : $"{Kind.ToString().ToLowerInvariant()}://{Host.ToLowerInvariant()}:{Port}:{Username ?? string.Empty}";
}

/// <summary>Pool and race partition key matching IDA ConnectionKey fields and flags mask.</summary>
public readonly record struct ConnectionKey(
    string Scheme,
    string Host,
    int Port,
    string ProfileName,
    string ProxyKey,
    int OptionsFlagsMask,
    string PinScope)
{
    public const int FlagForceHttp11 = 1 << 0;
    public const int FlagDisableHttp3 = 1 << 1;
    public const int FlagInsecureSkipVerify = 1 << 2;
    public const int FlagDisableSessionTickets = 1 << 3;
    public const int FlagRandomExtensionOrder = 1 << 4;

    public static ConnectionKey Create(
        string scheme,
        string host,
        int port,
        string profileName,
        string? proxyKey = null,
        bool forceHttp11 = false,
        bool disableHttp3 = false,
        bool insecureSkipVerify = false,
        bool disableSessionTickets = false,
        bool randomExtensionOrder = false,
        string? pinScope = null)
    {
        int mask = 0;
        if (forceHttp11) mask |= FlagForceHttp11;
        if (disableHttp3) mask |= FlagDisableHttp3;
        if (insecureSkipVerify) mask |= FlagInsecureSkipVerify;
        if (disableSessionTickets) mask |= FlagDisableSessionTickets;
        if (randomExtensionOrder) mask |= FlagRandomExtensionOrder;

        return new ConnectionKey(
            scheme.ToLowerInvariant(),
            host.ToLowerInvariant(),
            port,
            profileName,
            proxyKey ?? "direct",
            mask,
            pinScope ?? string.Empty);
    }

    public bool ForceHttp11 => (OptionsFlagsMask & FlagForceHttp11) != 0;
    public bool DisableHttp3 => (OptionsFlagsMask & FlagDisableHttp3) != 0;
    public bool InsecureSkipVerify => (OptionsFlagsMask & FlagInsecureSkipVerify) != 0;
}

public sealed class DialedConnection : IAsyncDisposable, IDisposable
{
    public DialedConnection(Stream stream, IPEndPoint? remoteEndPoint, bool isProxied)
    {
        Stream = stream ?? throw new ArgumentNullException(nameof(stream));
        RemoteEndPoint = remoteEndPoint;
        IsProxied = isProxied;
    }

    public Stream Stream { get; }
    public IPEndPoint? RemoteEndPoint { get; }
    public bool IsProxied { get; }

    public void Dispose() => Stream.Dispose();
    public ValueTask DisposeAsync() => Stream.DisposeAsync();
}

/// <summary>Common multiplexed transport abstraction implemented by H3, H2, and H1/1.1 connections.</summary>
public interface IMultiplexedConnection : IAsyncDisposable
{
    string ProtocolVersion { get; }
    ConnectionKey Key { get; }
    bool IsUsable { get; }
    bool SupportsMultiplexing { get; }
    int MaxConcurrentStreams { get; }
    int ActiveStreams { get; }
    DateTimeOffset LastUsedUtc { get; }
    bool CanAcceptNewStream();
    Task<PureHttpResponse> SendAsync(PureHttpRequest request, CancellationToken cancellationToken = default);
}

/// <summary>Shared response Content-Encoding decoder (gzip, deflate, br, zstd) with bounded output limit.</summary>
public static class HttpContentDecoder
{
    public static byte[] DecodeIfNeeded(ReadOnlySpan<byte> payload, string? contentEncoding, long maxOutputBytes)
    {
        if (payload.Length == 0 || string.IsNullOrWhiteSpace(contentEncoding))
            return payload.ToArray();

        string[] parts = contentEncoding.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        byte[] current = payload.ToArray();

        // Applied in reverse wire order per RFC 9110 §8.4.
        for (int i = parts.Length - 1; i >= 0; i--)
        {
            string enc = parts[i].ToLowerInvariant();
            if (enc is "identity" or "")
                continue;

            try
            {
                current = enc switch
                {
                    "gzip" or "x-gzip" => DecompressWithStream(current, s => new GZipStream(s, CompressionMode.Decompress, leaveOpen: false), maxOutputBytes),
                    "deflate" => DecompressDeflate(current, maxOutputBytes),
                    "br" => DecompressWithStream(current, s => new BrotliStream(s, CompressionMode.Decompress, leaveOpen: false), maxOutputBytes),
                    "zstd" => DecompressZstd(current, maxOutputBytes),
                    _ => current,
                };
            }
            catch (PureHttpException)
            {
                throw;
            }
            catch (Exception ex)
            {
                throw new PureHttpException(HttpErrorKind.ContentDecoding, $"Failed to decode HTTP content-encoding '{enc}': {ex.Message}", ex);
            }
        }

        return current;
    }

    private static byte[] DecompressDeflate(byte[] compressed, long maxOutputBytes)
    {
        // RFC 9110 notes "deflate" may be zlib-wrapped or raw deflate.
        try
        {
            return DecompressWithStream(compressed, s => new ZLibStream(s, CompressionMode.Decompress, leaveOpen: false), maxOutputBytes);
        }
        catch (InvalidDataException)
        {
            return DecompressWithStream(compressed, s => new DeflateStream(s, CompressionMode.Decompress, leaveOpen: false), maxOutputBytes);
        }
    }

    private static byte[] DecompressZstd(byte[] compressed, long maxOutputBytes)
    {
        using var decompressor = new Decompressor();
        byte[] decompressed = decompressor.Unwrap(compressed).ToArray();
        if (decompressed.LongLength > maxOutputBytes)
            throw new PureHttpException(HttpErrorKind.ResponseTooLarge, $"Decompressed zstd response exceeds {maxOutputBytes} bytes.");
        return decompressed;
    }

    private static byte[] DecompressWithStream(byte[] input, Func<MemoryStream, Stream> factory, long maxOutputBytes)
    {
        using var src = new MemoryStream(input, writable: false);
        using Stream decoder = factory(src);
        using var dst = new MemoryStream();
        byte[] buffer = new byte[16_384];
        long total = 0;
        while (true)
        {
            int read = decoder.Read(buffer, 0, buffer.Length);
            if (read == 0)
                break;
            total += read;
            if (total > maxOutputBytes)
                throw new PureHttpException(HttpErrorKind.ResponseTooLarge, $"Decompressed response exceeds {maxOutputBytes} bytes.");
            dst.Write(buffer, 0, read);
        }
        return dst.ToArray();
    }
}
