using System.Reflection;

namespace Cybersole.Http.Compression;

/// <summary>
/// The RFC 7932 preset dictionary, embedded under the same resource name the live build uses
/// (<c>Cybersole.Http.Compression.BrotliDictionary.bin</c>).
///
/// Round 128 recovered it from the single-file image: the assembly manifest names the resource,
/// and the payload sits at offset 0x62dd580 behind an 8-byte length of 122784 — the exact size
/// RFC 7932 specifies. Its opening bytes decode to " of the ", " of ", " and ", " in ", which is
/// the standard prefix table, so the blob is the real thing rather than a coincidence.
///
/// Why the bytes are carried but not yet used for decompression: a Brotli stream that was
/// compressed *with* this dictionary can only be read with it, and .NET 8's
/// <c>BrotliDecoder</c> / <c>BrotliStream</c> expose no dictionary parameter. Reading such a body
/// would need a full decoder with dictionary support. What this type provides today is parity of
/// the resource and of its accessor, which is what the ledger can actually check.
/// </summary>
public static class BrotliDictionary
{
    public const string ResourceName = "Cybersole.Http.Compression.BrotliDictionary.bin";

    /// <summary>Length RFC 7932 fixes for the dictionary; used to sanity-check the resource.</summary>
    public const int ExpectedLength = 122_784;

    private static readonly Lazy<byte[]> Cached = new(Load, isThreadSafe: true);

    /// <summary>The dictionary bytes. Never null; empty only if the resource is missing.</summary>
    public static byte[] Bytes => Cached.Value;

    public static int Length => Bytes.Length;

    public static bool IsAvailable => Bytes.Length == ExpectedLength;

    private static byte[] Load()
    {
        var asm = typeof(BrotliDictionary).Assembly;
        using var stream = asm.GetManifestResourceStream(ResourceName);
        if (stream is null) return Array.Empty<byte>();

        var buffer = new byte[stream.Length];
        var read = 0;
        while (read < buffer.Length)
        {
            var n = stream.Read(buffer, read, buffer.Length - read);
            if (n <= 0) break;
            read += n;
        }

        return read == buffer.Length ? buffer : buffer[..read];
    }

    /// <summary>Every embedded resource name in this assembly, for diagnostics.</summary>
    public static IEnumerable<string> AvailableResources() =>
        typeof(BrotliDictionary).Assembly.GetManifestResourceNames();
}
