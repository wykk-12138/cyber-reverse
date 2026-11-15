using System.Reflection;
using Cybersole.Http;
using Xunit;

namespace Cybersole.Tests;

public class BouncyTlsTests
{
    [Fact]
    public void ProfileTlsClient_Is_Constructible()
    {
        var client = new ProfileTlsClient("example.com", TlsProfile.Chrome);
        Assert.False(client.ValidateCertificates);
    }

    [Fact]
    public void ProfileTlsClient_Maps_Profile_CipherSuites()
    {
        var client = new ProfileTlsClient("example.com", TlsProfile.Chrome);
        var method = typeof(ProfileTlsClient).GetMethod("GetSupportedCipherSuites",
            BindingFlags.NonPublic | BindingFlags.Instance);
        Assert.NotNull(method);

        var suites = (int[]?)method!.Invoke(client, null);
        Assert.NotNull(suites);
        Assert.NotEmpty(suites!);
        // Chrome profile advertises 6 TLS 1.2 suites + 1 GREASE
        Assert.Equal(7, suites!.Length);
    }

    [Fact]
    public void ProfileTlsClient_Supports_Only_Tls12()
    {
        var client = new ProfileTlsClient("example.com", TlsProfile.Chrome);
        var method = typeof(ProfileTlsClient).GetMethod("GetSupportedVersions",
            BindingFlags.NonPublic | BindingFlags.Instance);
        var versions = (Org.BouncyCastle.Tls.ProtocolVersion[]?)method!.Invoke(client, null);
        Assert.NotNull(versions);
        Assert.Single(versions!);
    }

    [Fact]
    public void WithAlpn_Clones_Profile_Without_Mutating_Original()
    {
        var clone = TlsProfile.Chrome.WithAlpn("http/1.1");
        Assert.Single(clone.Alpn);
        Assert.Equal("http/1.1", clone.Alpn[0]);
        Assert.Equal("h2", TlsProfile.Chrome.Alpn[0]);
        Assert.Equal(TlsProfile.Chrome.CipherSuiteNames.Count, clone.CipherSuiteNames.Count);
        Assert.Equal("chrome", clone.Name);
    }

    [Fact]
    public void BouncyHttpClient_Constructs_And_Disposes()
    {
        using var client = new BouncyHttpClient();
        Assert.NotNull(client);
    }
}
