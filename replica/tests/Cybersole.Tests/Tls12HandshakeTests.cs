using Cybersole.Http;
using Xunit;

namespace Cybersole.Tests;

public class Tls12HandshakeTests
{
    private static byte[] BuildServerHello(ushort cipher, bool withAlpn = false, string alpn = "h2")
    {
        var sidLen = 32;
        var ext = new List<byte>();
        if (withAlpn)
        {
            var proto = System.Text.Encoding.ASCII.GetBytes(alpn);
            ext.AddRange(new byte[] { 0x00, 0x10 });                    // ALPN
            ext.AddRange(new byte[] { 0x00, (byte)(3 + proto.Length) }); // extension length
            ext.AddRange(new byte[] { 0x00, (byte)(1 + proto.Length) }); // protocol list length
            ext.Add((byte)proto.Length);
            ext.AddRange(proto);
        }

        var body = new List<byte>();
        body.AddRange(new byte[] { 0x03, 0x03 });       // TLS1.2
        body.AddRange(new byte[32]);                    // random
        body.Add((byte)sidLen);                         // session id length
        body.AddRange(new byte[sidLen]);                // session id
        body.Add((byte)(cipher >> 8)); body.Add((byte)cipher);
        body.Add(0x00);                                 // compression = null
        body.Add((byte)(ext.Count >> 8)); body.Add((byte)ext.Count);
        body.AddRange(ext);
        return body.ToArray();
    }

    [Fact]
    public void Parses_Cipher_And_Version()
    {
        var body = BuildServerHello(0xC02F);
        var result = Tls12Handshake.ParseServerHello(body);

        Assert.True(result.Ok);
        Assert.Equal("TLS1.2", result.Version);
        Assert.Equal("TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256", result.CipherSuite);
        Assert.Equal(0, result.ExtensionCount);
    }

    [Fact]
    public void Parses_Alpn_Extension()
    {
        var body = BuildServerHello(0xC02B, withAlpn: true, alpn: "h2");
        var result = Tls12Handshake.ParseServerHello(body);

        Assert.True(result.Ok);
        Assert.Equal(1, result.ExtensionCount);
        Assert.Equal("h2", result.Alpn);
    }

    [Fact]
    public void Handles_Empty_Session_Id()
    {
        var body = BuildServerHello(0xC02F);
        // re-build with zero-length session id
        var shortBody = new List<byte>();
        shortBody.AddRange(new byte[] { 0x03, 0x03 });
        shortBody.AddRange(new byte[32]);
        shortBody.Add(0x00);
        shortBody.AddRange(new byte[] { 0xC0, 0x2F, 0x00, 0x00, 0x00 });
        var result = Tls12Handshake.ParseServerHello(shortBody.ToArray());

        Assert.True(result.Ok);
        Assert.Equal(0, result.ExtensionCount);
    }

    [Fact]
    public void Rejects_Short_Body()
    {
        var result = Tls12Handshake.ParseServerHello(new byte[10]);
        Assert.False(result.Ok);
        Assert.NotNull(result.Error);
    }
}
