using Cybersole.Http;
using Xunit;

namespace Cybersole.Tests;

public class Ja3Tests
{
    [Fact]
    public void Ja3_String_Has_Four_Comma_Separated_Parts()
    {
        var ja3 = Ja3.FromProfile(TlsProfile.Chrome);
        var parts = ja3.Split(',');
        Assert.Equal(5, parts.Length);          // version,ciphers,extensions,curves,point-formats
        Assert.Equal("771", parts[0]);
        Assert.EndsWith("0", parts[4]);
        Assert.StartsWith("49195", parts[1]);   // profile leads with TLS_ECDHE_ECDSA_AES128_GCM
    }

    [Fact]
    public void Ja3_Can_Include_Grease()
    {
        var withGrease = Ja3.FromProfile(TlsProfile.Chrome, includeGrease: true);
        Assert.StartsWith("771,2570-", withGrease); // 0x0A0A == 2570 leads the cipher list
    }

    [Fact]
    public void ClientHello_Has_Tls12_Record_And_Handshake_Headers()
    {
        var record = Ja3.BuildClientHello(TlsProfile.Chrome, "example.com", out _);
        Assert.Equal(0x16, record[0]);                       // handshake record
        Assert.Equal(0x03, record[1]);
        Assert.Equal(0x01, record[2]);
        Assert.Equal(0x01, record[5]);                       // ClientHello
        var length = (record[6] << 16) | (record[7] << 8) | record[8];
        Assert.Equal(record.Length - 9, length);
    }

    [Fact]
    public void ClientHello_Leads_With_Grease_Cipher()
    {
        var record = Ja3.BuildClientHello(TlsProfile.Chrome, "example.com", out _);
        var p = 5 + 4 + 2 + 32;
        var sidLen = record[p]; p += 1 + sidLen;
        var csLen = (record[p] << 8) | record[p + 1];
        p += 2;
        var first = (record[p] << 8) | record[p + 1];
        Assert.Equal(0x0A0A, first);
        Assert.True(csLen >= 2 * 7);
    }

    [Fact]
    public void ClientHello_Extensions_Follow_Chrome_Order()
    {
        var record = Ja3.BuildClientHello(TlsProfile.Chrome, "example.com", out _);
        var types = ParseExtensionTypes(record);

        Assert.Equal(new[]
        {
            0x1A1A, 0x0000, 0x0017, 0xFF01, 0x000A, 0x000B,
            0x0023, 0x0010, 0x0005, 0x000D, 0x0012,
        }, types.ToArray());
    }

    [Fact]
    public void ClientHello_Sni_Contains_Hostname()
    {
        var record = Ja3.BuildClientHello(TlsProfile.Chrome, "shop.example.com", out _);
        var text = System.Text.Encoding.ASCII.GetString(record);
        Assert.Contains("shop.example.com", text);
    }

    private static List<int> ParseExtensionTypes(byte[] record)
    {
        var p = 5 + 4 + 2 + 32;
        var sidLen = record[p]; p += 1 + sidLen;
        var csLen = (record[p] << 8) | record[p + 1]; p += 2 + csLen;
        var compLen = record[p]; p += 1 + compLen;
        var extLen = (record[p] << 8) | record[p + 1]; p += 2;
        var end = p + extLen;

        var types = new List<int>();
        while (p + 4 <= end)
        {
            var type = (record[p] << 8) | record[p + 1];
            var len = (record[p + 2] << 8) | record[p + 3];
            types.Add(type);
            p += 4 + len;
        }
        return types;
    }
}
