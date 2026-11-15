using Cybersole.Http;
using Xunit;

namespace Cybersole.Tests;

public class HpackHuffmanTests
{
    // Captured from a real Cloudflare response: the "server" header value.
    private static readonly byte[] CloudflareHuffman =
        { 0x25, 0x07, 0xB6, 0x49, 0x68, 0x1D, 0x85 };

    [Fact]
    public void Decodes_Cloudflare_Server_Header()
    {
        Assert.Equal("cloudflare", HpackHuffman.Decode(CloudflareHuffman));
    }

    [Fact]
    public void Decodes_Ascii_Range()
    {
        // "www.example.com" encoded with the canonical table (RFC 7541 C.4.1)
        var encoded = new byte[]
        {
            0xF1, 0xE3, 0xC2, 0xE5, 0xF2, 0x3A, 0x6B, 0xA0, 0xAB, 0x90, 0xF4, 0xFF,
        };
        Assert.Equal("www.example.com", HpackHuffman.Decode(encoded));
    }

    [Fact]
    public void Empty_Input_Returns_Empty()
    {
        Assert.Equal(string.Empty, HpackHuffman.Decode(ReadOnlySpan<byte>.Empty));
    }

    [Fact]
    public void Truncated_Input_Returns_Decoded_Prefix()
    {
        // first two bytes of "cloudflare" still decode to a valid prefix ("cl")
        var prefix = new byte[] { 0x25, 0x07 };
        var result = HpackHuffman.Decode(prefix);
        Assert.StartsWith("cl", result);
    }
}
