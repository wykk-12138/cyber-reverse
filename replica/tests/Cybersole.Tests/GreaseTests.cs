using System.Reflection;
using Cybersole.Http;
using Xunit;

namespace Cybersole.Tests;

public class GreaseTests
{
    [Fact]
    public void Grease_Cipher_Is_First_In_ClientHello()
    {
        var client = new ProfileTlsClient("example.com", TlsProfile.Chrome);
        var method = typeof(ProfileTlsClient).GetMethod("GetSupportedCipherSuites",
            BindingFlags.NonPublic | BindingFlags.Instance);
        var suites = (int[])method!.Invoke(client, null)!;

        Assert.Equal(0x0A0A, suites[0]);      // RFC 8701 GREASE
        Assert.Equal(7, suites.Length);      // cream + 6 chrome suites
    }

    [Fact]
    public void Grease_Can_Be_Disabled_Per_Profile()
    {
        var noGrease = new TlsProfile
        {
            Name = "no-grease",
            Grease = false,
            CipherSuiteNames = TlsProfile.Chrome.CipherSuiteNames,
            Alpn = TlsProfile.Chrome.Alpn,
        };
        var client = new ProfileTlsClient("example.com", noGrease);
        var method = typeof(ProfileTlsClient).GetMethod("GetSupportedCipherSuites",
            BindingFlags.NonPublic | BindingFlags.Instance);
        var suites = (int[])method!.Invoke(client, null)!;

        Assert.DoesNotContain(0x0A0A, suites);
        Assert.Equal(6, suites.Length);
    }

    [Fact]
    public void Grease_Extension_And_Sni_Are_Present()
    {
        var client = new ProfileTlsClient("example.com", TlsProfile.Chrome);
        var extensions = client.GetClientExtensions();

        Assert.True(extensions.ContainsKey(0x1A1A));  // GREASE extension
        Assert.True(extensions.ContainsKey(0x0000));  // server_name
        Assert.True(extensions.ContainsKey(0x0010));  // ALPN
    }

    [Fact]
    public void Sni_Extension_Encodes_Hostname()
    {
        var client = new ProfileTlsClient("shop.example.com", TlsProfile.Chrome);
        var extensions = client.GetClientExtensions();
        var sni = extensions[0x0000];

        var text = System.Text.Encoding.ASCII.GetString(sni);
        Assert.Contains("shop.example.com", text);
        Assert.Equal(0x00, sni[2]); // host_name type
    }

public class ExtensionOrderTests
{
    [Fact]
    public void OrderedExtensions_Preserves_Insertion_Order()
    {
        var d = new OrderedExtensions();
        d[0x000D] = Array.Empty<byte>();
        d[0x0000] = Array.Empty<byte>();
        d[0x0010] = Array.Empty<byte>();

        Assert.Equal(new[] { 0x000D, 0x0000, 0x0010 }, d.Keys.ToArray());
        Assert.Equal(3, d.Count);
    }

    [Fact]
    public void OrderedExtensions_Replaces_Without_Moving()
    {
        var d = new OrderedExtensions();
        d[1] = new byte[] { 1 };
        d[2] = new byte[] { 2 };
        d[1] = new byte[] { 9 };

        Assert.Equal(new[] { 1, 2 }, d.Keys.ToArray());
        Assert.Equal(9, d[1][0]);
    }

    [Fact]
    public void ClientHello_Requests_SignedCertificateTimestamps()
    {
        var client = new ProfileTlsClient("example.com", TlsProfile.Chrome);
        var extensions = client.GetClientExtensions();

        Assert.True(extensions.ContainsKey(0x0012));       // SCT request
        Assert.Empty(extensions[0x0012]);                  // empty body = "send me SCTs"
    }

    [Fact]
    public void ClientHello_Has_Chrome_Like_Extension_Set()
    {
        var client = new ProfileTlsClient("example.com", TlsProfile.Chrome);
        var extensions = client.GetClientExtensions();

        foreach (var type in new[] { 0x0000, 0x0010, 0x0012, 0x1A1A })
            Assert.True(extensions.ContainsKey(type), $"missing extension 0x{type:X4}");
    }
}
}
