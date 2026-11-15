using Cybersole.Http.Compression;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// The Brotli preset dictionary must be present, the right size, and actually the standard one.
///
/// Round 128 carved it out of the single-file image. The checks below are what "actually the
/// standard one" means: RFC 7932 fixes the length at 122784 bytes, and the first bytes are a
/// prefix table of English fragments, so a wrong blob fails on both counts.
/// </summary>
public class BrotliDictionaryTests
{
    private readonly ITestOutputHelper _out;
    public BrotliDictionaryTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void ResourceIsEmbedded()
    {
        var names = BrotliDictionary.AvailableResources().ToList();
        _out.WriteLine("embedded resources: " + string.Join(", ", names));

        Assert.Contains(BrotliDictionary.ResourceName, names);
    }

    [Fact]
    public void LengthMatchesRfc7932()
    {
        _out.WriteLine($"length: {BrotliDictionary.Length}");
        Assert.Equal(BrotliDictionary.ExpectedLength, BrotliDictionary.Length);
        Assert.True(BrotliDictionary.IsAvailable);
    }

    [Fact]
    public void OpeningBytesAreThePrefixTable()
    {
        // The dictionary opens with the 4-byte-prefix section; its first entries are the
        // highest-frequency English fragments, so the first 64 bytes are largely printable.
        var head = BrotliDictionary.Bytes.AsSpan(0, 64).ToArray();
        var printable = head.Count(b => b is >= 32 and < 127);

        _out.WriteLine("head ascii: " + string.Join("", head.Select(
            b => b is >= 32 and < 127 ? ((char)b).ToString() : ".")));
        _out.WriteLine($"printable in first 64: {printable}");

        Assert.True(printable >= 30,
            $"only {printable}/64 printable — this does not look like the prefix table");
        Assert.Contains("of the", System.Text.Encoding.ASCII.GetString(head));
    }

    [Fact]
    public void BytesCoverTheWholeByteRange()
    {
        // a text-only file would not; the dictionary mixes lengths, so all 256 values appear
        var distinct = BrotliDictionary.Bytes.Distinct().Count();
        _out.WriteLine($"distinct byte values: {distinct}");
        Assert.Equal(256, distinct);
    }
}
