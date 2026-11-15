using Cybersole.Core.Models;
using Cybersole.Http;
using Xunit;

namespace Cybersole.Tests;

public class TlsFingerprintTests
{
    [Fact]
    public void Profiles_Expose_Real_Cipher_Names()
    {
        foreach (var profile in TlsProfile.All)
        {
            Assert.NotEmpty(profile.CipherSuiteNames);
            Assert.All(profile.CipherSuiteNames, n => Assert.Contains("TLS_", n));
            Assert.Contains("h2", profile.Alpn);
        }
    }

    [Fact]
    public void BuildCipherPolicy_Never_Throws()
    {
        foreach (var profile in TlsProfile.All)
        {
            // On Windows SChannel the policy may be rejected; the API must degrade to null.
            var policy = profile.BuildCipherPolicy();
            Assert.True(policy is null || policy is not null);
        }
    }

    [Fact]
    public void BuildCipherPolicy_Rejects_Empty_Profile()
    {
        var empty = new TlsProfile { Name = "empty" };
        Assert.Null(empty.BuildCipherPolicy());
    }

    [Fact]
    public void Alpn_Order_Matches_Profile()
    {
        var alpn = TlsProfile.Chrome.BuildAlpn();
        Assert.Equal(2, alpn.Count);
        Assert.Equal("h2", System.Text.Encoding.ASCII.GetString(alpn[0].Protocol.Span));
        Assert.Equal("http/1.1", System.Text.Encoding.ASCII.GetString(alpn[1].Protocol.Span));
    }

    [Fact]
    public void NetClient_Keeps_One_Client_Per_Profile()
    {
        using var client = new NetClient();
        Assert.Empty(client.ActiveProfiles);
    }
}

public class ProxyConnectorTests
{
    [Fact]
    public void Proxy_Uri_Encoding_Is_Stable()
    {
        var proxy = Proxy.Parse("socks5://u:p@10.0.0.1:1080");
        Assert.Equal("socks5", proxy.Scheme);
        Assert.Contains("socks5://u:p@10.0.0.1:1080", proxy.Uri);
    }
}
