using System;
using System.Buffers.Binary;
using System.Formats.Asn1;
using System.Numerics;
using System.Security.Cryptography;

namespace Cybersole.Http.Crypto;

/// <summary>
/// PKCS#1 public key DER parsing and RSASSA-PKCS1-v1_5 / RSASSA-PSS signature verification.
/// </summary>
public static class RsaPrimitives
{
    public static bool TryParseRsaPublicKeyDer(ReadOnlySpan<byte> pkcs1Der, out byte[] modulus, out byte[] exponent)
    {
        modulus = Array.Empty<byte>();
        exponent = Array.Empty<byte>();
        if (pkcs1Der.IsEmpty)
            return false;

        try
        {
            var reader = new AsnReader(pkcs1Der.ToArray(), AsnEncodingRules.DER);
            AsnReader seq = reader.ReadSequence();
            if (reader.HasData)
                return false;

            ReadOnlySpan<byte> mSpan = seq.ReadIntegerBytes().Span;
            ReadOnlySpan<byte> eSpan = seq.ReadIntegerBytes().Span;
            if (seq.HasData)
                return false;

            if (!TryTrimUnsignedPositive(mSpan, out byte[] m))
                return false;
            if (!TryTrimUnsignedPositive(eSpan, out byte[] e))
                return false;

            modulus = m;
            exponent = e;
            return true;
        }
        catch (AsnContentException)
        {
            modulus = Array.Empty<byte>();
            exponent = Array.Empty<byte>();
            return false;
        }
    }

    private static bool TryTrimUnsignedPositive(ReadOnlySpan<byte> asnInt, out byte[] result)
    {
        result = Array.Empty<byte>();
        if (asnInt.IsEmpty || (asnInt[0] & 0x80) != 0)
            return false;

        if (asnInt.Length > 1 && asnInt[0] == 0x00)
            asnInt = asnInt[1..];

        if (asnInt.IsEmpty || asnInt[0] == 0x00)
            return false;

        result = asnInt.ToArray();
        return true;
    }

    public static bool VerifyPkcs1(
        ReadOnlySpan<byte> modulus,
        ReadOnlySpan<byte> exponent,
        HashAlgorithmKind hashAlg,
        ReadOnlySpan<byte> data,
        ReadOnlySpan<byte> signature)
    {
        if (modulus.IsEmpty || modulus[0] == 0 || exponent.IsEmpty || exponent[0] == 0)
            return false;
        if (signature.Length != modulus.Length)
            return false;

        try
        {
            using var rsa = RSA.Create();
            rsa.ImportParameters(new RSAParameters
            {
                Modulus = modulus.ToArray(),
                Exponent = exponent.ToArray()
            });
            return rsa.VerifyData(data, signature, HashPrimitives.ToBclName(hashAlg), RSASignaturePadding.Pkcs1);
        }
        catch (CryptographicException)
        {
            return false;
        }
    }

    public static bool VerifyPss(
        ReadOnlySpan<byte> modulus,
        ReadOnlySpan<byte> exponent,
        HashAlgorithmKind hashAlg,
        ReadOnlySpan<byte> data,
        ReadOnlySpan<byte> signature,
        int saltLength = -1)
    {
        if (modulus.IsEmpty || modulus[0] == 0 || exponent.IsEmpty || exponent[0] == 0)
            return false;
        if (signature.Length != modulus.Length || saltLength < -1)
            return false;

        int hashLen = HashPrimitives.DigestLength(hashAlg);
        int modBits = (modulus.Length - 1) * 8 + BitOperations.Log2(modulus[0]) + 1;
        int emBits = modBits - 1;
        int emLen = (emBits + 7) / 8;
        int expectedSaltLen = saltLength == -1 ? hashLen : saltLength;

        if (emLen < hashLen + expectedSaltLen + 2)
            return false;

        if (expectedSaltLen == hashLen)
        {
            try
            {
                using var rsa = RSA.Create();
                rsa.ImportParameters(new RSAParameters
                {
                    Modulus = modulus.ToArray(),
                    Exponent = exponent.ToArray()
                });
                return rsa.VerifyData(data, signature, HashPrimitives.ToBclName(hashAlg), RSASignaturePadding.Pss);
            }
            catch (CryptographicException)
            {
                return false;
            }
        }

        return VerifyPssExplicitSalt(modulus, exponent, hashAlg, hashLen, emBits, emLen, expectedSaltLen, data, signature);
    }

    private static bool VerifyPssExplicitSalt(
        ReadOnlySpan<byte> modulus,
        ReadOnlySpan<byte> exponent,
        HashAlgorithmKind hashAlg,
        int hashLen,
        int emBits,
        int emLen,
        int saltLen,
        ReadOnlySpan<byte> data,
        ReadOnlySpan<byte> signature)
    {
        var n = new BigInteger(modulus, isUnsigned: true, isBigEndian: true);
        var e = new BigInteger(exponent, isUnsigned: true, isBigEndian: true);
        var s = new BigInteger(signature, isUnsigned: true, isBigEndian: true);
        if (s >= n)
            return false;

        BigInteger m = BigInteger.ModPow(s, e, n);
        int mByteCount = m.IsZero ? 0 : m.GetByteCount(isUnsigned: true);
        if (mByteCount > emLen)
            return false;

        byte[] em = new byte[emLen];
        if (mByteCount > 0)
            m.TryWriteBytes(em.AsSpan(emLen - mByteCount), out _, isUnsigned: true, isBigEndian: true);

        if (em[^1] != 0xBC)
            return false;

        int unusedBits = 8 * emLen - emBits;
        if (unusedBits > 0 && (em[0] >> (8 - unusedBits)) != 0)
            return false;

        int dbLen = emLen - hashLen - 1;
        ReadOnlySpan<byte> maskedDb = em.AsSpan(0, dbLen);
        ReadOnlySpan<byte> h = em.AsSpan(dbLen, hashLen);

        byte[] dbMask = Mgf1(hashAlg, h, dbLen);
        byte[] db = new byte[dbLen];
        for (int i = 0; i < dbLen; i++)
            db[i] = (byte)(maskedDb[i] ^ dbMask[i]);

        if (unusedBits > 0)
            db[0] &= (byte)(0xFF >> unusedBits);

        int psLen = emLen - hashLen - saltLen - 2;
        for (int i = 0; i < psLen; i++)
        {
            if (db[i] != 0x00)
                return false;
        }
        if (db[psLen] != 0x01)
            return false;

        ReadOnlySpan<byte> salt = db.AsSpan(psLen + 1, saltLen);
        byte[] mHash = HashPrimitives.Hash(hashAlg, data);
        byte[] mPrime = new byte[8 + hashLen + saltLen];
        mHash.CopyTo(mPrime.AsSpan(8));
        salt.CopyTo(mPrime.AsSpan(8 + hashLen));
        byte[] hPrime = HashPrimitives.Hash(hashAlg, mPrime);

        return ConstantTime.Equals(h, hPrime);
    }

    private static byte[] Mgf1(HashAlgorithmKind hashAlg, ReadOnlySpan<byte> seed, int maskLen)
    {
        int hashLen = HashPrimitives.DigestLength(hashAlg);
        byte[] mask = new byte[maskLen];
        byte[] input = new byte[seed.Length + 4];
        seed.CopyTo(input);

        int offset = 0;
        uint counter = 0;
        while (offset < maskLen)
        {
            BinaryPrimitives.WriteUInt32BigEndian(input.AsSpan(seed.Length, 4), counter++);
            byte[] block = HashPrimitives.Hash(hashAlg, input);
            int take = Math.Min(hashLen, maskLen - offset);
            block.AsSpan(0, take).CopyTo(mask.AsSpan(offset));
            offset += take;
        }

        return mask;
    }
}
