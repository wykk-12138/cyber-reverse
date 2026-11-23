using System.IO.Compression;
using System.Text;

namespace Cybersole.Http.Compression;

/// <summary>
/// Symmetric HTTP <c>Content-Encoding</c> codec supporting <c>identity</c>, <c>gzip</c>, <c>x-gzip</c>,
/// <c>deflate</c>, <c>br</c> (decode), and <c>zstd</c> (encode/decode via <see cref="ZstdSharp"/>).
/// Multi-value headers are decoded in reverse order and encoded in forward order.
/// </summary>
public static class ContentEncodingCodec
{
    public const string DefaultAcceptEncoding = "gzip, deflate, br, zstd";

    /// <summary>
    /// Decompress <paramref name="body"/> according to <paramref name="contentEncoding"/>.
    /// Comma-separated encodings (for example <c>"gzip, br"</c>) are decoded in reverse chain order.
    /// </summary>
    public static byte[] Decompress(byte[] body, string? contentEncoding)
    {
        ArgumentNullException.ThrowIfNull(body);
        if (body.Length == 0 || string.IsNullOrWhiteSpace(contentEncoding))
            return body;

        var encodings = ParseEncodings(contentEncoding);
        var current = body;

        // HTTP Content-Encoding lists transformations in application order, so decoding walks backwards.
        for (var i = encodings.Count - 1; i >= 0; i--)
        {
            var enc = encodings[i];
            current = enc switch
            {
                "identity" => current,
                "gzip" or "x-gzip" => DecompressGzip(current),
                "deflate" => DecompressDeflate(current),
                "br" => DecompressBrotli(current),
                "zstd" => DecompressZstd(current),
                _ => throw new NotSupportedException($"Unsupported Content-Encoding \"{enc}\"."),
            };
        }

        return current;
    }

    /// <summary>
    /// Compress <paramref name="body"/> according to <paramref name="contentEncoding"/>.
    /// Supports <c>identity</c>, <c>gzip</c>, <c>x-gzip</c>, <c>deflate</c>, and <c>zstd</c>.
    /// </summary>
    public static byte[] Compress(byte[] body, string? contentEncoding)
    {
        ArgumentNullException.ThrowIfNull(body);
        if (string.IsNullOrWhiteSpace(contentEncoding))
            return body;

        var encodings = ParseEncodings(contentEncoding);
        var current = body;

        foreach (var enc in encodings)
        {
            current = enc switch
            {
                "identity" => current,
                "gzip" or "x-gzip" => CompressGzip(current),
                "deflate" => CompressDeflate(current),
                "zstd" => CompressZstd(current),
                _ => throw new NotSupportedException(
                    $"No encoder for Content-Encoding \"{enc}\" (supported: gzip, deflate, zstd)."),
            };
        }

        return current;
    }

    /// <summary>
    /// Decode response bytes into UTF-8 text (stripping any UTF-8 BOM), honoring
    /// <paramref name="contentEncoding"/> while gracefully falling back to raw UTF-8 if a peer sends
    /// mislabeled/corrupt bytes.
    /// </summary>
    public static string DecompressToString(byte[] body, string? contentEncoding)
    {
        ArgumentNullException.ThrowIfNull(body);
        if (body.Length == 0)
            return string.Empty;

        if (string.IsNullOrWhiteSpace(contentEncoding))
            return DecodeUtf8WithBom(body);

        try
        {
            var decoded = Decompress(body, contentEncoding);
            return DecodeUtf8WithBom(decoded);
        }
        catch
        {
            return DecodeUtf8WithBom(body);
        }
    }

    /// <summary>
    /// Lookup <c>Content-Encoding</c> in <paramref name="headers"/> and decode <paramref name="body"/> to UTF-8 text.
    /// </summary>
    public static string DecompressToString(byte[] body, IDictionary<string, string>? headers)
    {
        string? encoding = null;
        if (headers is not null)
        {
            if (!headers.TryGetValue("Content-Encoding", out encoding))
            {
                foreach (var kv in headers)
                {
                    if (string.Equals(kv.Key, "Content-Encoding", StringComparison.OrdinalIgnoreCase))
                    {
                        encoding = kv.Value;
                        break;
                    }
                }
            }
        }

        return DecompressToString(body, encoding);
    }

    private static List<string> ParseEncodings(string contentEncoding)
    {
        var list = new List<string>();
        foreach (var part in contentEncoding.Split(','))
        {
            var token = part.Trim().ToLowerInvariant();
            if (token.Length > 0)
                list.Add(token);
        }
        return list;
    }

    private static byte[] DecompressGzip(byte[] input)
    {
        using var src = new MemoryStream(input);
        using var gz = new GZipStream(src, CompressionMode.Decompress);
        using var dst = new MemoryStream();
        gz.CopyTo(dst);
        return dst.ToArray();
    }

    private static byte[] DecompressDeflate(byte[] input)
    {
        try
        {
            using var src = new MemoryStream(input);
            using var deflate = new DeflateStream(src, CompressionMode.Decompress);
            using var dst = new MemoryStream();
            deflate.CopyTo(dst);
            return dst.ToArray();
        }
        catch (InvalidDataException)
        {
            // HTTP servers occasionally send RFC 1950 zlib-wrapped streams labeled "deflate".
            using var src = new MemoryStream(input);
            using var zlib = new ZLibStream(src, CompressionMode.Decompress);
            using var dst = new MemoryStream();
            zlib.CopyTo(dst);
            return dst.ToArray();
        }
    }

    private static byte[] DecompressBrotli(byte[] input)
    {
        using var src = new MemoryStream(input);
        using var br = new BrotliStream(src, CompressionMode.Decompress);
        using var dst = new MemoryStream();
        br.CopyTo(dst);
        return dst.ToArray();
    }

    private static byte[] DecompressZstd(byte[] input)
    {
        using var decompressor = new ZstdSharp.Decompressor();
        return decompressor.Unwrap(input).ToArray();
    }

    private static byte[] CompressGzip(byte[] input)
    {
        using var dst = new MemoryStream();
        using (var gz = new GZipStream(dst, CompressionLevel.Optimal, leaveOpen: true))
            gz.Write(input, 0, input.Length);
        return dst.ToArray();
    }

    private static byte[] CompressDeflate(byte[] input)
    {
        using var dst = new MemoryStream();
        using (var deflate = new DeflateStream(dst, CompressionLevel.Optimal, leaveOpen: true))
            deflate.Write(input, 0, input.Length);
        return dst.ToArray();
    }

    private static byte[] CompressZstd(byte[] input)
    {
        using var compressor = new ZstdSharp.Compressor();
        return compressor.Wrap(input).ToArray();
    }

    internal static string DecodeUtf8WithBom(byte[] bytes)
    {
        if (bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF)
            return Encoding.UTF8.GetString(bytes, 3, bytes.Length - 3);
        return Encoding.UTF8.GetString(bytes);
    }
}
