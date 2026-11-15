using System.Text;
using Cybersole.Http;
using Xunit;

namespace Cybersole.Tests;

public class Tls12PrfTests
{
    // Reference values produced with Python hmac/hashlib (RFC 5246 §5 P_SHA256).
    [Fact]
    public void Prf_Matches_Reference_Short_Output()
    {
        var result = Tls12Prf.Prf(
            Encoding.ASCII.GetBytes("secret"),
            "test label",
            Encoding.ASCII.GetBytes("seed data"),
            32);

        Assert.Equal("8058B604C897AD3CB5B06DCD9A5F6AFD157BD7B8B5D7B563F91F64D1BA0AF38B",
            Convert.ToHexString(result));
    }

    [Fact]
    public void Prf_Matches_Reference_Long_Output()
    {
        var secret = Enumerable.Range(0, 16).Select(i => (byte)i).ToArray();
        var seed = Enumerable.Range(0, 32).Select(i => (byte)i)
            .Concat(Enumerable.Range(32, 32).Select(i => (byte)i)).ToArray();

        var result = Tls12Prf.Prf(secret, "master secret", seed, 48);

        Assert.Equal("24D21A554EFED0D5946466E0F60BC3EA8F753DADCC46173FA571518734A02F1E" +
                     "C03FE89475E39974714047EB1FE2E261", Convert.ToHexString(result));
    }

    [Fact]
    public void Finished_Verify_Data_Matches_Reference()
    {
        var master = new byte[48];
        var handshakeHash = Enumerable.Range(0, 32).Select(i => (byte)i).ToArray();

        var result = Tls12Prf.FinishedVerifyData(master, fromClient: true, handshakeHash);

        Assert.Equal("2B72F0A155A86D789CD6641F", Convert.ToHexString(result));
        Assert.Equal(12, result.Length);
    }

    [Fact]
    public void MasterSecret_Is_48_Bytes()
    {
        var preMaster = new byte[32];
        var master = Tls12Prf.MasterSecret(preMaster, new byte[32], new byte[32]);
        Assert.Equal(48, master.Length);
    }

    [Fact]
    public void KeyBlock_Has_Requested_Length()
    {
        var block = Tls12Prf.KeyBlock(new byte[48], new byte[32], new byte[32], 72);
        Assert.Equal(72, block.Length);
    }
}

public class EcdheTests
{
    [Fact]
    public void Public_Key_Is_Uncompressed_P256_Point()
    {
        var (key, publicKey) = Ecdhe.CreateP256();
        using (key)
        {
            Assert.Equal(65, publicKey.Length);       // 04 || X(32) || Y(32)
            Assert.Equal(0x04, publicKey[0]);
        }
    }

    [Fact]
    public void Shared_Secret_Matches_On_Both_Sides()
    {
        var (a, aPub) = Ecdhe.CreateP256();
        var (b, bPub) = Ecdhe.CreateP256();
        using (a)
        using (b)
        {
            var ab = Ecdhe.SharedSecret(a, bPub);
            var ba = Ecdhe.SharedSecret(b, aPub);
            Assert.Equal(ab, ba);
            Assert.Equal(32, ab.Length);
        }
    }

    [Fact]
    public void X25519_Shared_Secret_Matches_On_Both_Sides()
    {
        var (a, aPub) = Ecdhe.CreateX25519();
        var (b, bPub) = Ecdhe.CreateX25519();

        Assert.Equal(32, aPub.Length);
        Assert.Equal(32, bPub.Length);

        var ab = Ecdhe.SharedSecretX25519(a, bPub);
        var ba = Ecdhe.SharedSecretX25519(b, aPub);

        Assert.Equal(ab, ba);
        Assert.Equal(32, ab.Length);
    }
}
