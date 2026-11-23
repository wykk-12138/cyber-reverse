using System;
using System.Security.Cryptography;
using System.Text;
using Cybersole.Http.Crypto;
using Xunit;

namespace Cybersole.Tests;

public class CryptoPrimitivesTests
{
    private static byte[] Hex(string s) => Convert.FromHexString(s);

    [Fact]
    public void Sha3_256_OfficialFips202Kats()
    {
        Assert.Equal(
            Hex("a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"),
            HashPrimitives.Sha3_256(ReadOnlySpan<byte>.Empty));

        Assert.Equal(
            Hex("3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532"),
            HashPrimitives.Sha3_256("abc"u8));

        Span<byte> dest = stackalloc byte[32];
        HashPrimitives.Sha3_256("abc"u8, dest);
        Assert.Equal(
            Hex("3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532"),
            dest.ToArray());
    }

    [Fact]
    public void Sha3_512_OfficialFips202Kats()
    {
        Assert.Equal(
            Hex("a69f73cca23a9ac5c8b567dc185a756e97c982164fe25859e0d1dcc1475c80a615b2123af1f5f94c11e3e9402c3ac558f500199d95b6d3e301758586281dcd26"),
            HashPrimitives.Sha3_512(ReadOnlySpan<byte>.Empty));

        Assert.Equal(
            Hex("b751850b1a57168a5693cd924b6b096e08f621827444f70d884f5d0240d2712e10e116e9192af3c91a7ec57647e3934057340b4cf408d5a56592f8274eec53f0"),
            HashPrimitives.Sha3_512("abc"u8));
    }

    [Fact]
    public void Shake128_And_Shake256_OfficialFips202Kats_And_StreamingReader()
    {
        Span<byte> shake128Empty = stackalloc byte[32];
        HashPrimitives.Shake128(ReadOnlySpan<byte>.Empty, shake128Empty);
        Assert.Equal(
            Hex("7f9c2ba4e88f827d616045507605853ed73b8093f6efbc88eb1a6eacfa66ef26"),
            shake128Empty.ToArray());

        Span<byte> shake128Abc = stackalloc byte[32];
        HashPrimitives.Shake128("abc"u8, shake128Abc);
        Assert.Equal(
            Hex("5881092dd818bf5cf8a3ddb793fbcba74097d5c526a6d35f97b83351940f2cc8"),
            shake128Abc.ToArray());

        Span<byte> shake256Empty = stackalloc byte[64];
        HashPrimitives.Shake256(ReadOnlySpan<byte>.Empty, shake256Empty);
        Assert.Equal(
            Hex("46b9dd2b0ba88d13233b3feb743eeb243fcd52ea62b81b82b50c27646ed5762fd75dc4ddd8c0f200cb05019d67b592f6fc821c49479ab48640292eacb3b7c4be"),
            shake256Empty.ToArray());

        Span<byte> shake256Abc = stackalloc byte[64];
        HashPrimitives.Shake256("abc"u8, shake256Abc);
        Assert.Equal(
            Hex("483366601360a8771c6863080cc4114d8db44530f8f1e1ee4f94ea37e78b5739d5a15bef186a5386c75744c0527e1faa9f8726e462a12a4feb06bd8801e751e4"),
            shake256Abc.ToArray());

        // Verify multi-block streaming XofReader equals single-shot SHAKE128/256
        byte[] oneShot128 = new byte[400];
        HashPrimitives.Shake128("stream-test"u8, oneShot128);
        using (XofReader reader = HashPrimitives.CreateShake128Reader("stream-test"u8))
        {
            byte[] part1 = reader.Squeeze(1);
            byte[] part2 = reader.Squeeze(167);
            byte[] part3 = reader.Squeeze(232);
            byte[] combined = new byte[400];
            part1.CopyTo(combined, 0);
            part2.CopyTo(combined, 1);
            part3.CopyTo(combined, 168);
            Assert.Equal(oneShot128, combined);
        }

        byte[] oneShot256 = new byte[350];
        HashPrimitives.Shake256("stream-test-256"u8, oneShot256);
        using (XofReader reader256 = HashPrimitives.CreateShake256Reader("stream-test-256"u8))
        {
            byte[] partA = reader256.Squeeze(136);
            byte[] partB = reader256.Squeeze(214);
            byte[] combined256 = new byte[350];
            partA.CopyTo(combined256, 0);
            partB.CopyTo(combined256, 136);
            Assert.Equal(oneShot256, combined256);
        }
    }

    [Fact]
    public void Hkdf_Rfc5869_And_Rfc8448_Tls13KeyScheduleKats()
    {
        // RFC 5869 Appendix A.1
        byte[] ikm = Hex("0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b");
        byte[] salt = Hex("000102030405060708090a0b0c");
        byte[] info = Hex("f0f1f2f3f4f5f6f7f8f9");
        byte[] prk = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, salt, ikm);
        Assert.Equal(Hex("077709362c2e32df0ddc3f0dc47bba6390b6c73bb50f9c3122ec844ad7c2b3e5"), prk);
        Assert.Equal(
            Hex("3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56ecc4c5bf34007208d5b887185865"),
            HashPrimitives.HkdfExpand(HashAlgorithmKind.Sha256, prk, info, 42));

        // RFC 8448 Section 3 (TLS 1.3 1-RTT Handshake)
        byte[] zeros32 = new byte[32];
        byte[] earlySecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, zeros32, zeros32);
        Assert.Equal(Hex("33ad0a1c607ec03b09e6cd9893680ce210adf300aa1f2660e1b22e10f170f92a"), earlySecret);

        byte[] emptyHash = HashPrimitives.Sha256(ReadOnlySpan<byte>.Empty);
        byte[] derivedSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, earlySecret, "derived", emptyHash, 32);
        Assert.Equal(Hex("6f2615a108c702c5678f54fc9dbab69716c076189c48250cebeac3576c3611ba"), derivedSecret);

        byte[] ecdheShared = Hex("8bd4054fb55b9d63fdfbacf9f04b9f0d35e6d63f537563efd46272900f89492d");
        byte[] handshakeSecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, derivedSecret, ecdheShared);
        Assert.Equal(Hex("1dc826e93606aa6fdc0aadc12f741b01046aa6b99f691ed221a9f0ca043fbeac"), handshakeSecret);
    }

    [Fact]
    public void Tls12Prf_MatchesRfc5246P_Hash()
    {
        byte[] secret = Hex("0102030405060708090a0b0c0d0e0f10");
        byte[] seed = Hex("aabbccddeeff00112233445566778899");
        byte[] outBytes = HashPrimitives.Tls12Prf(HashAlgorithmKind.Sha256, secret, "master secret", seed, 48);

        byte[] labelAndSeed = Encoding.ASCII.GetBytes("master secret").Concat(seed).ToArray();
        byte[] a1 = HMACSHA256.HashData(secret, labelAndSeed);
        byte[] a2 = HMACSHA256.HashData(secret, a1);
        byte[] p1 = HMACSHA256.HashData(secret, a1.Concat(labelAndSeed).ToArray());
        byte[] p2 = HMACSHA256.HashData(secret, a2.Concat(labelAndSeed).ToArray());
        byte[] expected = p1.Concat(p2[..16]).ToArray();

        Assert.Equal(expected, outBytes);
        Assert.Empty(HashPrimitives.Tls12Prf(HashAlgorithmKind.Sha256, secret, "empty", seed, 0));
    }

    [Fact]
    public void AesBlock_And_AesCbc_OfficialFips197AndNist800_38AKats()
    {
        // FIPS 197 Appendix B (AES-128)
        byte[] key128 = Hex("2b7e151628aed2a6abf7158809cf4f3c");
        byte[] pt128 = Hex("3243f6a8885a308d313198a2e0370734");
        byte[] ct128 = Hex("3925841d02dc09fbdc118597196a0b32");
        Span<byte> block = stackalloc byte[16];
        AesPrimitives.EncryptBlock(key128, pt128, block);
        Assert.Equal(ct128, block.ToArray());
        AesPrimitives.DecryptBlock(key128, ct128, block);
        Assert.Equal(pt128, block.ToArray());

        // FIPS 197 Appendix C.3 (AES-256)
        byte[] key256 = Hex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f");
        byte[] pt256 = Hex("00112233445566778899aabbccddeeff");
        byte[] ct256 = Hex("8ea2b7ca516745bfeafc49904b496089");
        AesPrimitives.EncryptBlock(key256, pt256, block);
        Assert.Equal(ct256, block.ToArray());
        AesPrimitives.DecryptBlock(key256, ct256, block);
        Assert.Equal(pt256, block.ToArray());

        // NIST SP 800-38A F.2.1 CBC-AES128
        byte[] cbcIv = Hex("000102030405060708090a0b0c0d0e0f");
        byte[] cbcPt = Hex("6bc1bee22e409f96e93d7e117393172aae2d8a571e03ac9c9eb76fac45af8e5130c81c46a35ce411e5fbc1191a0a52eff69f2445df4f9b17ad2b417be66c3710");
        byte[] cbcCt = Hex("7649abac8119b246cee98e9b12e9197d5086cb9b507219ee95db113a917678b273bed6b8e3c1743b7116e69e222295163ff1caa1681fac09120eca307586e1a7");
        Assert.Equal(cbcCt, AesPrimitives.AesCbcEncrypt(key128, cbcIv, cbcPt, pkcs7Padding: false));
        Assert.Equal(cbcPt, AesPrimitives.AesCbcDecrypt(key128, cbcIv, cbcCt, pkcs7Padding: false));

        // PKCS#7 padding roundtrip and invalid padding rejection
        byte[] msg = Encoding.UTF8.GetBytes("Cybersole AES-CBC PKCS7 test!");
        byte[] paddedCt = AesPrimitives.AesCbcEncrypt(key256, cbcIv, msg, pkcs7Padding: true);
        Assert.Equal(msg, AesPrimitives.AesCbcDecrypt(key256, cbcIv, paddedCt, pkcs7Padding: true));
        paddedCt[^1] ^= 0xFF;
        Assert.Throws<CryptographicException>(() => AesPrimitives.AesCbcDecrypt(key256, cbcIv, paddedCt, pkcs7Padding: true));
    }

    [Fact]
    public void AesGcm_OfficialNistSp800_38DKats_And_TagRejection()
    {
        // Test Case 3 (AES-128-GCM, 64-byte PT, empty AAD)
        byte[] key128 = Hex("feffe9928665731c6d6a8f9467308308");
        byte[] iv = Hex("cafebabefacedbaddecaf888");
        byte[] pt64 = Hex("d9313225f88406e5a55909c5aff5269a86a7a9531534f7da2e4c303d8a318a721c3c0c95956809532fcf0e2449a6b525b16aedf5aa0de657ba637b391aafd255");
        byte[] ct3 = Hex("42831ec2217774244b7221b784d0d49ce3aa212f2c02a4e035c17e2329aca12e21d514b25466931c7d8f6a5aac84aa051ba30b396a0aac973d58e091473f5985");
        byte[] tag3 = Hex("4d5c2af327cd64a62cf35abd2ba6fab4");

        byte[] actualCt = new byte[pt64.Length];
        byte[] actualTag = new byte[16];
        AesPrimitives.AesGcmEncrypt(key128, iv, pt64, ReadOnlySpan<byte>.Empty, actualCt, actualTag);
        Assert.Equal(ct3, actualCt);
        Assert.Equal(tag3, actualTag);

        byte[] decrypted = new byte[pt64.Length];
        Assert.True(AesPrimitives.AesGcmDecrypt(key128, iv, ct3, ReadOnlySpan<byte>.Empty, tag3, decrypted));
        Assert.Equal(pt64, decrypted);

        // Test Case 4 (AES-128-GCM, 60-byte PT, 20-byte AAD)
        byte[] pt60 = pt64[..60];
        byte[] aad20 = Hex("feedfacedeadbeeffeedfacedeadbeefabaddad2");
        byte[] ct4 = ct3[..60];
        byte[] tag4 = Hex("5bc94fbc3221a5db94fae95ae7121a47");
        actualCt = new byte[60];
        AesPrimitives.AesGcmEncrypt(key128, iv, pt60, aad20, actualCt, actualTag);
        Assert.Equal(ct4, actualCt);
        Assert.Equal(tag4, actualTag);
        decrypted = new byte[60];
        Assert.True(AesPrimitives.AesGcmDecrypt(key128, iv, ct4, aad20, tag4, decrypted));
        Assert.Equal(pt60, decrypted);

        // Tamper tag -> must return false AND zero plaintext buffer
        Array.Fill(decrypted, (byte)0xAA);
        byte[] badTag = (byte[])tag4.Clone();
        badTag[0] ^= 0x01;
        Assert.False(AesPrimitives.AesGcmDecrypt(key128, iv, ct4, aad20, badTag, decrypted));
        Assert.All(decrypted, b => Assert.Equal((byte)0, b));

        // Test Case 15 & 16 (AES-256-GCM)
        byte[] key256 = Hex("feffe9928665731c6d6a8f9467308308feffe9928665731c6d6a8f9467308308");
        byte[] ct15 = Hex("522dc1f099567d07f47f37a32a84427d643a8cdcbfe5c0c97598a2bd2555d1aa8cb08e48590dbb3da7b08b1056828838c5f61e6393ba7a0abcc9f662898015ad");
        byte[] tag15 = Hex("b094dac5d93471bdec1a502270e3cc6c");
        actualCt = new byte[64];
        AesPrimitives.AesGcmEncrypt(key256, iv, pt64, ReadOnlySpan<byte>.Empty, actualCt, actualTag);
        Assert.Equal(ct15, actualCt);
        Assert.Equal(tag15, actualTag);

        byte[] ct16 = ct15[..60];
        byte[] tag16 = Hex("76fc6ece0f4e1768cddf8853bb2d551b");
        actualCt = new byte[60];
        AesPrimitives.AesGcmEncrypt(key256, iv, pt60, aad20, actualCt, actualTag);
        Assert.Equal(ct16, actualCt);
        Assert.Equal(tag16, actualTag);
        decrypted = new byte[60];
        Assert.True(AesPrimitives.AesGcmDecrypt(key256, iv, ct16, aad20, tag16, decrypted));
        Assert.Equal(pt60, decrypted);
    }

    [Fact]
    public void ChaCha20Poly1305_OfficialRfc8439Kats_And_TagRejection()
    {
        // RFC 8439 §2.3.2 ChaCha20 Block KAT
        byte[] key232 = Hex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f");
        byte[] nonce232 = Hex("000000090000004a00000000");
        byte[] block = new byte[64];
        ChaCha20Poly1305Primitives.ChaCha20Block(key232, 1u, nonce232, block);
        Assert.Equal(
            Hex("10f1e7e4d13b5915500fdd1fa32071c4c7d1f4c733c068030422aa9ac3d46c4ed2826446079faa0914c2d705d98b02a2b5129cd1de164eb9cbd083e8a2503c4e"),
            block);

        // RFC 8439 §2.4.2 ChaCha20 Encryption KAT
        byte[] nonce242 = Hex("000000000000004a00000000");
        byte[] pt = Encoding.ASCII.GetBytes("Ladies and Gentlemen of the class of '99: If I could offer you only one tip for the future, sunscreen would be it.");
        byte[] expectedXorCt = Hex("6e2e359a2568f98041ba0728dd0d6981e97e7aec1d4360c20a27afccfd9fae0bf91b65c5524733ab8f593dabcd62b3571639d624e65152ab8f530c359f0861d807ca0dbf500d6a6156a38e088a22b65e52bc514d16ccf806818ce91ab77937365af90bbf74a35be6b40b8eedf2785e42874d");
        byte[] actualXorCt = new byte[pt.Length];
        ChaCha20Poly1305Primitives.ChaCha20Xor(key232, 1u, nonce242, pt, actualXorCt);
        Assert.Equal(expectedXorCt, actualXorCt);

        // RFC 8439 §2.8.2 AEAD KAT
        byte[] aeadKey = Hex("808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9f");
        byte[] aeadNonce = Hex("070000004041424344454647");
        byte[] aad = Hex("50515253c0c1c2c3c4c5c6c7");
        byte[] expectedCt = Hex("d31a8d34648e60db7b86afbc53ef7ec2a4aded51296e08fea9e2b5a736ee62d63dbea45e8ca9671282fafb69da92728b1a71de0a9e060b2905d6a5b67ecd3b3692ddbd7f2d778b8c9803aee328091b58fab324e4fad675945585808b4831d7bc3ff4def08e4b7a9de576d26586cec64b6116");
        byte[] expectedTag = Hex("1ae10b594f09e26a7e902ecbd0600691");

        byte[] actualCt = new byte[pt.Length];
        byte[] actualTag = new byte[16];
        ChaCha20Poly1305Primitives.Encrypt(aeadKey, aeadNonce, pt, aad, actualCt, actualTag);
        Assert.Equal(expectedCt, actualCt);
        Assert.Equal(expectedTag, actualTag);

        byte[] decrypted = new byte[pt.Length];
        Assert.True(ChaCha20Poly1305Primitives.Decrypt(aeadKey, aeadNonce, expectedCt, aad, expectedTag, decrypted));
        Assert.Equal(pt, decrypted);

        Array.Fill(decrypted, (byte)0x55);
        byte[] badTag = (byte[])expectedTag.Clone();
        badTag[15] ^= 0x80;
        Assert.False(ChaCha20Poly1305Primitives.Decrypt(aeadKey, aeadNonce, expectedCt, aad, badTag, decrypted));
        Assert.All(decrypted, b => Assert.Equal((byte)0, b));
    }

    [Fact]
    public void X25519_OfficialRfc7748Vectors_And_AllZeroRejection()
    {
        byte[] alicePriv = Hex("77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a");
        byte[] alicePub = Hex("8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a");
        byte[] bobPriv = Hex("5dab087e624a8a4b79e17f8b83800ee66f3bb1292618b6fd1c2f8b27ff88e0eb");
        byte[] bobPub = Hex("de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f");
        byte[] expectedShared = Hex("4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742");

        Assert.Equal(alicePub, X25519.PublicFromPrivate(alicePriv));
        Assert.Equal(bobPub, X25519.PublicFromPrivate(bobPriv));
        Assert.Equal(expectedShared, X25519.ScalarMult(alicePriv, bobPub));
        Assert.Equal(expectedShared, X25519.ScalarMult(bobPriv, alicePub));

        // Reject all-zero point and low-order point
        Assert.Throws<CryptographicException>(() => X25519.ScalarMult(alicePriv, new byte[32]));
        byte[] lowOrderOne = new byte[32];
        lowOrderOne[0] = 1;
        Assert.Throws<CryptographicException>(() => X25519.ScalarMult(alicePriv, lowOrderOne));

        X25519.GenerateKeyPair(out byte[] genPriv1, out byte[] genPub1);
        X25519.GenerateKeyPair(out byte[] genPriv2, out byte[] genPub2);
        Assert.Equal(X25519.ScalarMult(genPriv1, genPub2), X25519.ScalarMult(genPriv2, genPub1));
    }

    [Fact]
    public void Ed25519_OfficialRfc8032Vectors_And_Rejections()
    {
        // RFC 8032 §7.1 TEST 1
        byte[] pk1 = Hex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a");
        byte[] sig1 = Hex("e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b");
        Assert.True(Ed25519.Verify(pk1, ReadOnlySpan<byte>.Empty, sig1));
        Assert.False(Ed25519.Verify(pk1, new byte[] { 0x00 }, sig1));

        // RFC 8032 §7.1 TEST 2
        byte[] pk2 = Hex("3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c");
        byte[] msg2 = Hex("72");
        byte[] sig2 = Hex("92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00");
        Assert.True(Ed25519.Verify(pk2, msg2, sig2));

        // Tamper signature & test S >= L rejection
        byte[] badSig = (byte[])sig2.Clone();
        badSig[10] ^= 0x01;
        Assert.False(Ed25519.Verify(pk2, msg2, badSig));

        byte[] malleableSig = (byte[])sig2.Clone();
        malleableSig[63] |= 0x80; // forces S >= L
        Assert.False(Ed25519.Verify(pk2, msg2, malleableSig));

        // Non-canonical y >= p public key (all 0xFF except sign bit)
        byte[] nonCanonicalPk = new byte[32];
        Array.Fill(nonCanonicalPk, (byte)0xFF);
        nonCanonicalPk[31] = 0x7F;
        Assert.False(Ed25519.Verify(nonCanonicalPk, msg2, sig2));
    }

    [Theory]
    [InlineData(EcCurveKind.P256, "1.2.840.10045.3.1.7", 65)]
    [InlineData(EcCurveKind.P384, "1.3.132.0.34", 97)]
    [InlineData(EcCurveKind.P521, "1.3.132.0.35", 133)]
    public void EcPrimitives_Ecdhe_And_Ecdsa_CrossVerifyWithBcl(EcCurveKind curve, string oid, int pubLen)
    {
        Assert.True(EcPrimitives.TryCurveFromOid(oid, out EcCurveKind parsedCurve));
        Assert.Equal(curve, parsedCurve);
        Assert.False(EcPrimitives.TryCurveFromOid("1.2.3.4", out _));

        // ECDHE mutual shared secret + BCL ECDiffieHellman interop
        (byte[] privA, byte[] pubA) = EcPrimitives.GenerateEcdheKeyPair(curve);
        Assert.Equal(pubLen, pubA.Length);
        Assert.Equal(0x04, pubA[0]);

        ECCurve bclCurve = curve switch
        {
            EcCurveKind.P256 => ECCurve.NamedCurves.nistP256,
            EcCurveKind.P384 => ECCurve.NamedCurves.nistP384,
            EcCurveKind.P521 => ECCurve.NamedCurves.nistP521,
            _ => throw new ArgumentOutOfRangeException(nameof(curve))
        };

        using var bclEcdh = ECDiffieHellman.Create(bclCurve);
        ECParameters bclParams = bclEcdh.ExportParameters(includePrivateParameters: true);
        int coordSize = (pubLen - 1) / 2;
        byte[] pubB = new byte[pubLen];
        pubB[0] = 0x04;
        bclParams.Q.X!.CopyTo(pubB, 1 + coordSize - bclParams.Q.X.Length);
        bclParams.Q.Y!.CopyTo(pubB, 1 + coordSize + coordSize - bclParams.Q.Y.Length);

        byte[] shared1 = EcPrimitives.DeriveEcdheSharedSecret(curve, privA, pubB);
        byte[] shared2 = EcPrimitives.DeriveEcdheSharedSecret(curve, bclParams.D!, pubA);
        Assert.Equal(shared1, shared2);

        using var peerBcl = ECDiffieHellman.Create(new ECParameters
        {
            Curve = bclCurve,
            Q = new ECPoint { X = pubA[1..(1 + coordSize)], Y = pubA[(1 + coordSize)..] }
        });
        byte[] bclHashed = bclEcdh.DeriveKeyFromHash(peerBcl.PublicKey, HashAlgorithmName.SHA256);
        Assert.Equal(bclHashed, HashPrimitives.Sha256(shared1));

        // Off-curve point must throw CryptographicException
        byte[] invalidPoint = (byte[])pubB.Clone();
        invalidPoint[^1] ^= 0x01;
        Assert.Throws<CryptographicException>(() => EcPrimitives.DeriveEcdheSharedSecret(curve, privA, invalidPoint));

        // ECDSA cross-verification with BCL ECDsa (DER signature)
        using var ecdsa = ECDsa.Create(bclCurve);
        ECParameters sigParams = ecdsa.ExportParameters(includePrivateParameters: false);
        byte[] sigPub = new byte[pubLen];
        sigPub[0] = 0x04;
        sigParams.Q.X!.CopyTo(sigPub, 1 + coordSize - sigParams.Q.X.Length);
        sigParams.Q.Y!.CopyTo(sigPub, 1 + coordSize + coordSize - sigParams.Q.Y.Length);

        byte[] msg = Encoding.UTF8.GetBytes("Cybersole ECDSA DER verification test");
        byte[] derSig = ecdsa.SignData(msg, HashAlgorithmName.SHA256, DSASignatureFormat.Rfc3279DerSequence);
        Assert.True(EcPrimitives.VerifyEcdsa(curve, sigPub, HashAlgorithmKind.Sha256, msg, derSig));
        Assert.False(EcPrimitives.VerifyEcdsa(curve, sigPub, HashAlgorithmKind.Sha256, "tampered"u8, derSig));

        // Trailing byte after DER signature must be rejected
        byte[] trailingDer = derSig.Concat(new byte[] { 0x00 }).ToArray();
        Assert.False(EcPrimitives.VerifyEcdsa(curve, sigPub, HashAlgorithmKind.Sha256, msg, trailingDer));
    }

    [Fact]
    public void RsaPrimitives_Pkcs1Der_Pkcs1Verify_And_PssVerify_CrossVerifyWithBcl()
    {
        using var rsa = RSA.Create(2048);
        byte[] pkcs1Der = rsa.ExportRSAPublicKey();

        Assert.True(RsaPrimitives.TryParseRsaPublicKeyDer(pkcs1Der, out byte[] modulus, out byte[] exponent));
        Assert.False(RsaPrimitives.TryParseRsaPublicKeyDer(pkcs1Der.Concat(new byte[] { 0x00 }).ToArray(), out _, out _));

        RSAParameters expectedParams = rsa.ExportParameters(false);
        Assert.Equal(expectedParams.Modulus, modulus);
        Assert.Equal(expectedParams.Exponent, exponent);

        byte[] msg = Encoding.UTF8.GetBytes("Cybersole TLS 1.3 RSA-PSS & PKCS#1 verification");

        byte[] pkcs1Sig = rsa.SignData(msg, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        Assert.True(RsaPrimitives.VerifyPkcs1(modulus, exponent, HashAlgorithmKind.Sha256, msg, pkcs1Sig));
        Assert.False(RsaPrimitives.VerifyPkcs1(modulus, exponent, HashAlgorithmKind.Sha256, "wrong"u8, pkcs1Sig));

        byte[] pssSig = rsa.SignData(msg, HashAlgorithmName.SHA256, RSASignaturePadding.Pss);
        Assert.True(RsaPrimitives.VerifyPss(modulus, exponent, HashAlgorithmKind.Sha256, msg, pssSig));
        Assert.True(RsaPrimitives.VerifyPss(modulus, exponent, HashAlgorithmKind.Sha256, msg, pssSig, saltLength: 32));
        Assert.False(RsaPrimitives.VerifyPss(modulus, exponent, HashAlgorithmKind.Sha256, msg, pssSig, saltLength: 0));
        Assert.False(RsaPrimitives.VerifyPss(modulus, exponent, HashAlgorithmKind.Sha256, msg, pssSig, saltLength: 500));
        Assert.False(RsaPrimitives.VerifyPss(modulus, exponent, HashAlgorithmKind.Sha256, msg, pssSig, saltLength: -2));

        byte[] badPss = (byte[])pssSig.Clone();
        badPss[^1] ^= 0x01;
        Assert.False(RsaPrimitives.VerifyPss(modulus, exponent, HashAlgorithmKind.Sha256, msg, badPss));
    }

    [Fact]
    public void MlKem768_And_HybridKem_Fips203_Roundtrip_ImplicitRejection_And_WireFormat()
    {
        byte[] d = Enumerable.Range(0, 32).Select(i => (byte)i).ToArray();
        byte[] z = Enumerable.Range(100, 32).Select(i => (byte)i).ToArray();
        byte[] m = Enumerable.Range(200, 32).Select(i => (byte)i).ToArray();

        (byte[] ek, byte[] dk) = MlKem768.KeyGenDeterministic(d, z);
        Assert.Equal(MlKem768.EncapsulationKeySize, ek.Length);
        Assert.Equal(MlKem768.DecapsulationKeySize, dk.Length);

        // Verify dk stores H(ek) at [2336..2368] and z at [2368..2400] per FIPS 203
        Assert.Equal(HashPrimitives.Sha3_256(ek), dk[2336..2368]);
        Assert.Equal(z, dk[2368..2400]);

        (byte[] ct, byte[] ssEnc) = MlKem768.Encaps(ek, m);
        Assert.Equal(MlKem768.CiphertextSize, ct.Length);
        Assert.Equal(MlKem768.SharedSecretSize, ssEnc.Length);

        byte[] ssDec = MlKem768.Decaps(dk, ct);
        Assert.Equal(ssEnc, ssDec);

        // Flip 1 bit of ciphertext -> implicit rejection returns J(z || flippedCt)
        byte[] flippedCt = (byte[])ct.Clone();
        flippedCt[17] ^= 0x04;
        byte[] ssRejected = MlKem768.Decaps(dk, flippedCt);
        byte[] expectedImplicit = new byte[32];
        HashPrimitives.Shake256(z.Concat(flippedCt).ToArray(), expectedImplicit);
        Assert.Equal(expectedImplicit, ssRejected);
        Assert.NotEqual(ssEnc, ssRejected);

        // Reject invalid ek with coefficient >= 3329 (0x0D01 = 3329 LE: [0x01, 0x0D])
        byte[] badEk = (byte[])ek.Clone();
        badEk[0] = 0x01;
        badEk[1] = (byte)((badEk[1] & 0xF0) | 0x0D);
        Assert.Throws<ArgumentException>(() => MlKem768.Encaps(badEk, m));

        // Reject invalid dk with tampered H(ek)
        byte[] badDk = (byte[])dk.Clone();
        badDk[2336] ^= 0xFF;
        Assert.Throws<ArgumentException>(() => MlKem768.Decaps(badDk, ct));

        // Hybrid X25519MLKEM768 wire format (1216 -> 1120 -> 64)
        (byte[] clientShare, HybridKeyState state) = HybridKem.GenerateX25519MlKem768();
        using (state)
        {
            Assert.Equal(1216, clientShare.Length);
            (byte[] serverCt, byte[] serverMlKemSs) = MlKem768.Encaps(clientShare[..1184]);
            X25519.GenerateKeyPair(out byte[] serverXPriv, out byte[] serverXPub);
            byte[] serverXSs = X25519.ScalarMult(serverXPriv, clientShare[1184..]);

            byte[] serverShare = new byte[1120];
            serverCt.CopyTo(serverShare, 0);
            serverXPub.CopyTo(serverShare, 1088);

            byte[] clientShared = HybridKem.CompleteX25519MlKem768(state, serverShare);
            Assert.Equal(64, clientShared.Length);
            Assert.Equal(serverMlKemSs, clientShared[..32]);
            Assert.Equal(serverXSs, clientShared[32..64]);
        }

        // Hybrid X25519Kyber768Draft00 wire format (X25519 pk first: 1216 -> 1120 -> 64)
        (byte[] draftClientShare, HybridKeyState draftState) = HybridKem.GenerateX25519Kyber768Draft00();
        using (draftState)
        {
            Assert.Equal(1216, draftClientShare.Length);
            X25519.GenerateKeyPair(out byte[] serverXPriv, out byte[] serverXPub);
            byte[] serverXSs = X25519.ScalarMult(serverXPriv, draftClientShare[..32]);
            (byte[] serverCt, byte[] serverMlKemSs) = MlKem768.Encaps(draftClientShare[32..]);

            byte[] serverShare = new byte[1120];
            serverXPub.CopyTo(serverShare, 0);
            serverCt.CopyTo(serverShare, 32);

            byte[] clientShared = HybridKem.CompleteX25519MlKem768(draftState, serverShare);
            Assert.Equal(64, clientShared.Length);
            Assert.Equal(serverXSs, clientShared[..32]);
            Assert.Equal(serverMlKemSs, clientShared[32..64]);
        }
    }
}
