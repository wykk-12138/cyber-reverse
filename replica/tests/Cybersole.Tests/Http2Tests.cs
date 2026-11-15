using System.Reflection;
using System.Text;
using Cybersole.Http;
using Xunit;

namespace Cybersole.Tests;

public class Http2Tests
{
    [Fact]
    public void Frame_Header_Is_Valid()
    {
        var payload = new byte[] { 0x01, 0x02, 0x03 };
        var frame = Http2.Frame(Http2.Data, 0x1, 7, payload);

        Assert.Equal(9 + payload.Length, frame.Length);
        Assert.Equal(3, frame[2]);            // length low byte
        Assert.Equal(Http2.Data, frame[3]);   // type
        Assert.Equal(0x1, frame[4]);          // flags
        Assert.Equal(7, frame[8]);            // stream id low byte
        Assert.Equal(payload, frame[9..]);
    }

    [Fact]
    public void EncodeHeaders_Starts_With_Method_And_Scheme_Indexes()
    {
        var block = Http2.EncodeHeaders("example.com", "/path",
            "Mozilla/5.0", "text/html", "en-US");

        Assert.Equal(0x82, block[0]); // :method GET
        Assert.Equal(0x87, block[1]); // :scheme https
        var text = Encoding.Latin1.GetString(block);
        Assert.Contains("example.com", text);
        Assert.Contains("/path", text);
        Assert.Contains("Mozilla/5.0", text);
        Assert.Contains("accept", text);
    }

    [Fact]
    public void DecodeStatus_Reads_Static_Indexes()
    {
        Assert.Equal(200, Http2.DecodeStatus(new byte[] { 0x88 }));
        Assert.Equal(404, Http2.DecodeStatus(new byte[] { 0x8D }));
        Assert.Equal(500, Http2.DecodeStatus(new byte[] { 0x8E }));
    }

    [Fact]
    public void DecodeStatus_Reads_Literal_Status()
    {
        // literal with indexed name (:status = 8): 0x08, len 3, "404"
        var block = new byte[] { 0x08, 0x03, (byte)'4', (byte)'0', (byte)'4' };
        Assert.Equal(404, Http2.DecodeStatus(block));
    }

    [Fact]
    public void DecodeHeaders_Parses_Static_And_Literals()
    {
        // :status 200 (indexed) + "server" (index 54) literal value "cloudflare"
        var block = new List<byte> { 0x88, 0x76, 0x0A };
        block.AddRange(Encoding.ASCII.GetBytes("cloudflare"));

        var headers = Http2.DecodeHeaders(block.ToArray());
        Assert.Equal("200", headers[":status"]);
        Assert.Equal("cloudflare", headers["server"]);
    }

    [Fact]
    public void DecodeHeaders_Marks_Huffman_Values()
    {
        // "server" literal with a Huffman-flagged value
        var block = new List<byte> { 0x76, 0x83, 0xAA, 0xBB, 0xCC };
        var headers = Http2.DecodeHeaders(block.ToArray());
        Assert.False(string.IsNullOrEmpty(headers["server"]));
        Assert.DoesNotContain("<huffman:", headers["server"]);
    }

    [Fact]
    public void SettingsFrame_Has_Fourteen_Bytes()
    {
        var frame = Http2.SettingsFrame();
        Assert.Equal(9 + 12, frame.Length);
        Assert.Equal(Http2.Settings, frame[3]);
    }
}

public class BouncyH2ClientTests
{
    [Fact]
    public void Client_Constructs_And_Disposes()
    {
        using var client = new BouncyH2Client();
        Assert.NotNull(client);
    }

public class TransportTests
{
    [Fact]
    public void NetClient_Transport_Defaults_To_SChannel()
    {
        using var client = new NetClient();
        Assert.Equal(TransportMode.SChannel, client.Transport);
    }

    [Fact]
    public void NetClient_Transport_Can_Be_Switched()
    {
        using var client = new NetClient { Transport = TransportMode.BouncyH2 };
        Assert.Equal(TransportMode.BouncyH2, client.Transport);
    }

    [Fact]
    public void EncodeHeaders_Post_Uses_Static_Index_3()
    {
        var block = Http2.EncodeHeaders("example.com", "/checkout", "UA", "text/html", "en-US", "POST");
        Assert.Equal(0x83, block[0]); // :method POST
    }

    [Fact]
    public void EncodeHeaders_Includes_Extra_Headers_But_Skips_Pseudo()
    {
        var extra = new List<KeyValuePair<string, string>>
        {
            new("cookie", "session=abc"),
            new("x-test", "yes"),
            new(":path", "/ignored"),
            new("connection", "close"),
        };
        var block = Http2.EncodeHeaders("example.com", "/", "UA", "text/html", "en-US", "GET", extra);
        var text = System.Text.Encoding.Latin1.GetString(block);

        Assert.Contains("cookie", text);
        Assert.Contains("session=abc", text);
        Assert.Contains("x-test", text);
        Assert.DoesNotContain("/ignored", text);
        Assert.DoesNotContain("connection", text);
    }
}
}
