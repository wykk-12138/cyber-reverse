using System;
using System.Buffers.Binary;
using System.Formats.Asn1;
using System.Globalization;
using System.Numerics;
using System.Security.Cryptography;

namespace Cybersole.Http.Crypto;

/// <summary>
/// 5x51-bit limb arithmetic over GF(2^255 - 19), shared by X25519 and Ed25519.
/// </summary>
internal struct Fe25519
{
    private const ulong Mask51 = (1UL << 51) - 1UL;
    private const ulong P4_0 = (1UL << 53) - 76UL;
    private const ulong P4_1 = (1UL << 53) - 4UL;

    public ulong L0, L1, L2, L3, L4;

    public static readonly Fe25519 Zero = default;
    public static readonly Fe25519 One = new() { L0 = 1UL };

    public static Fe25519 FromUInt(ulong v) => new() { L0 = v & Mask51, L1 = v >> 51 };

    public static Fe25519 FromBytes(ReadOnlySpan<byte> s32)
    {
        ulong u0 = BinaryPrimitives.ReadUInt64LittleEndian(s32.Slice(0, 8));
        ulong u1 = BinaryPrimitives.ReadUInt64LittleEndian(s32.Slice(8, 8));
        ulong u2 = BinaryPrimitives.ReadUInt64LittleEndian(s32.Slice(16, 8));
        ulong u3 = BinaryPrimitives.ReadUInt64LittleEndian(s32.Slice(24, 8));

        return new Fe25519
        {
            L0 = u0 & Mask51,
            L1 = ((u0 >> 51) | (u1 << 13)) & Mask51,
            L2 = ((u1 >> 38) | (u2 << 26)) & Mask51,
            L3 = ((u2 >> 25) | (u3 << 39)) & Mask51,
            L4 = (u3 >> 12) & Mask51
        };
    }

    public static void ToBytes(in Fe25519 a, Span<byte> out32)
    {
        ulong t0 = a.L0, t1 = a.L1, t2 = a.L2, t3 = a.L3, t4 = a.L4;

        for (int pass = 0; pass < 2; pass++)
        {
            ulong c = t0 >> 51; t0 &= Mask51; t1 += c;
            c = t1 >> 51; t1 &= Mask51; t2 += c;
            c = t2 >> 51; t2 &= Mask51; t3 += c;
            c = t3 >> 51; t3 &= Mask51; t4 += c;
            c = t4 >> 51; t4 &= Mask51; t0 += c * 19UL;
        }

        // Canonical reduction mod 2^255 - 19: q = 1 iff t >= 2^255 - 19
        ulong q = (t0 + 19UL) >> 51;
        q = (t1 + q) >> 51;
        q = (t2 + q) >> 51;
        q = (t3 + q) >> 51;
        q = (t4 + q) >> 51;

        t0 += 19UL * q;
        ulong carry = t0 >> 51; t0 &= Mask51; t1 += carry;
        carry = t1 >> 51; t1 &= Mask51; t2 += carry;
        carry = t2 >> 51; t2 &= Mask51; t3 += carry;
        carry = t3 >> 51; t3 &= Mask51; t4 += carry;
        t4 &= Mask51;

        BinaryPrimitives.WriteUInt64LittleEndian(out32.Slice(0, 8), t0 | (t1 << 51));
        BinaryPrimitives.WriteUInt64LittleEndian(out32.Slice(8, 8), (t1 >> 13) | (t2 << 38));
        BinaryPrimitives.WriteUInt64LittleEndian(out32.Slice(16, 8), (t2 >> 26) | (t3 << 25));
        BinaryPrimitives.WriteUInt64LittleEndian(out32.Slice(24, 8), (t3 >> 39) | (t4 << 12));
    }

    public static Fe25519 Add(in Fe25519 a, in Fe25519 b)
    {
        ulong t0 = a.L0 + b.L0;
        ulong t1 = a.L1 + b.L1 + (t0 >> 51); t0 &= Mask51;
        ulong t2 = a.L2 + b.L2 + (t1 >> 51); t1 &= Mask51;
        ulong t3 = a.L3 + b.L3 + (t2 >> 51); t2 &= Mask51;
        ulong t4 = a.L4 + b.L4 + (t3 >> 51); t3 &= Mask51;
        ulong c = t4 >> 51; t4 &= Mask51;
        t0 += c * 19UL;
        t1 += t0 >> 51; t0 &= Mask51;
        return new Fe25519 { L0 = t0, L1 = t1, L2 = t2, L3 = t3, L4 = t4 };
    }

    public static Fe25519 Sub(in Fe25519 a, in Fe25519 b)
    {
        ulong t0 = P4_0 + a.L0 - b.L0;
        ulong t1 = P4_1 + a.L1 - b.L1 + (t0 >> 51); t0 &= Mask51;
        ulong t2 = P4_1 + a.L2 - b.L2 + (t1 >> 51); t1 &= Mask51;
        ulong t3 = P4_1 + a.L3 - b.L3 + (t2 >> 51); t2 &= Mask51;
        ulong t4 = P4_1 + a.L4 - b.L4 + (t3 >> 51); t3 &= Mask51;
        ulong c = t4 >> 51; t4 &= Mask51;
        t0 += c * 19UL;
        t1 += t0 >> 51; t0 &= Mask51;
        return new Fe25519 { L0 = t0, L1 = t1, L2 = t2, L3 = t3, L4 = t4 };
    }

    public static Fe25519 Neg(in Fe25519 a) => Sub(Zero, a);

    public static Fe25519 Mul(in Fe25519 a, in Fe25519 b)
    {
        ulong a0 = a.L0, a1 = a.L1, a2 = a.L2, a3 = a.L3, a4 = a.L4;
        ulong b0 = b.L0, b1 = b.L1, b2 = b.L2, b3 = b.L3, b4 = b.L4;
        ulong b1_19 = b1 * 19UL, b2_19 = b2 * 19UL, b3_19 = b3 * 19UL, b4_19 = b4 * 19UL;

        UInt128 t0 = (UInt128)a0 * b0 + (UInt128)a1 * b4_19 + (UInt128)a2 * b3_19 + (UInt128)a3 * b2_19 + (UInt128)a4 * b1_19;
        UInt128 t1 = (UInt128)a0 * b1 + (UInt128)a1 * b0    + (UInt128)a2 * b4_19 + (UInt128)a3 * b3_19 + (UInt128)a4 * b2_19;
        UInt128 t2 = (UInt128)a0 * b2 + (UInt128)a1 * b1    + (UInt128)a2 * b0    + (UInt128)a3 * b4_19 + (UInt128)a4 * b3_19;
        UInt128 t3 = (UInt128)a0 * b3 + (UInt128)a1 * b2    + (UInt128)a2 * b1    + (UInt128)a3 * b0    + (UInt128)a4 * b4_19;
        UInt128 t4 = (UInt128)a0 * b4 + (UInt128)a1 * b3    + (UInt128)a2 * b2    + (UInt128)a3 * b1    + (UInt128)a4 * b0;

        t1 += (ulong)(t0 >> 51); ulong r0 = (ulong)t0 & Mask51;
        t2 += (ulong)(t1 >> 51); ulong r1 = (ulong)t1 & Mask51;
        t3 += (ulong)(t2 >> 51); ulong r2 = (ulong)t2 & Mask51;
        t4 += (ulong)(t3 >> 51); ulong r3 = (ulong)t3 & Mask51;
        ulong c = (ulong)(t4 >> 51); ulong r4 = (ulong)t4 & Mask51;

        r0 += c * 19UL;
        r1 += r0 >> 51; r0 &= Mask51;

        return new Fe25519 { L0 = r0, L1 = r1, L2 = r2, L3 = r3, L4 = r4 };
    }

    public static Fe25519 Sqr(in Fe25519 a) => Mul(a, a);

    public static Fe25519 MulSmall(in Fe25519 a, ulong k)
    {
        UInt128 t0 = (UInt128)a.L0 * k;
        UInt128 t1 = (UInt128)a.L1 * k + (t0 >> 51); ulong r0 = (ulong)t0 & Mask51;
        UInt128 t2 = (UInt128)a.L2 * k + (t1 >> 51); ulong r1 = (ulong)t1 & Mask51;
        UInt128 t3 = (UInt128)a.L3 * k + (t2 >> 51); ulong r2 = (ulong)t2 & Mask51;
        UInt128 t4 = (UInt128)a.L4 * k + (t3 >> 51); ulong r3 = (ulong)t3 & Mask51;
        ulong c = (ulong)(t4 >> 51); ulong r4 = (ulong)t4 & Mask51;
        r0 += c * 19UL;
        r1 += r0 >> 51; r0 &= Mask51;
        return new Fe25519 { L0 = r0, L1 = r1, L2 = r2, L3 = r3, L4 = r4 };
    }

    public static void CSwap(uint swap, ref Fe25519 a, ref Fe25519 b)
    {
        ulong mask = 0UL - (ulong)(swap & 1U);
        ulong x0 = mask & (a.L0 ^ b.L0); a.L0 ^= x0; b.L0 ^= x0;
        ulong x1 = mask & (a.L1 ^ b.L1); a.L1 ^= x1; b.L1 ^= x1;
        ulong x2 = mask & (a.L2 ^ b.L2); a.L2 ^= x2; b.L2 ^= x2;
        ulong x3 = mask & (a.L3 ^ b.L3); a.L3 ^= x3; b.L3 ^= x3;
        ulong x4 = mask & (a.L4 ^ b.L4); a.L4 ^= x4; b.L4 ^= x4;
    }

    private static Fe25519 SqrN(Fe25519 a, int count)
    {
        for (int i = 0; i < count; i++)
            a = Sqr(a);
        return a;
    }

    private static void Pow2250_1(in Fe25519 z, out Fe25519 z11, out Fe25519 z2_250_1)
    {
        Fe25519 t0 = Sqr(z);
        Fe25519 t1 = Mul(Sqr(Sqr(t0)), z);
        z11 = Mul(t0, t1);
        Fe25519 z5 = Mul(t1, Sqr(z11));
        Fe25519 z10 = Mul(SqrN(z5, 5), z5);
        Fe25519 z20 = Mul(SqrN(z10, 10), z10);
        Fe25519 z40 = Mul(SqrN(z20, 20), z20);
        Fe25519 z50 = Mul(SqrN(z40, 10), z10);
        Fe25519 z100 = Mul(SqrN(z50, 50), z50);
        Fe25519 z200 = Mul(SqrN(z100, 100), z100);
        z2_250_1 = Mul(SqrN(z200, 50), z50);
    }

    public static Fe25519 Invert(in Fe25519 z)
    {
        Pow2250_1(z, out Fe25519 z11, out Fe25519 z2_250_1);
        return Mul(SqrN(z2_250_1, 5), z11);
    }

    public static Fe25519 Pow22523(in Fe25519 z)
    {
        Pow2250_1(z, out _, out Fe25519 z2_250_1);
        return Mul(SqrN(z2_250_1, 2), z);
    }
}

/// <summary>
/// Pure managed RFC 7748 X25519 ECDH key exchange with constant-time Montgomery ladder
/// and all-zero shared secret rejection.
/// </summary>
public static class X25519
{
    public static void GenerateKeyPair(out byte[] privateKey32, out byte[] publicKey32)
    {
        privateKey32 = new byte[32];
        RandomNumberGenerator.Fill(privateKey32);
        privateKey32[0] &= 248;
        privateKey32[31] &= 127;
        privateKey32[31] |= 64;
        publicKey32 = PublicFromPrivate(privateKey32);
    }

    public static byte[] PublicFromPrivate(ReadOnlySpan<byte> privateKey32)
    {
        if (privateKey32.Length != 32)
            throw new ArgumentException("X25519 private key must be 32 bytes.", nameof(privateKey32));

        Span<byte> basepoint = stackalloc byte[32];
        basepoint[0] = 9;
        return ScalarMultCore(privateKey32, basepoint, rejectAllZero: false);
    }

    public static byte[] ScalarMult(ReadOnlySpan<byte> privateKey32, ReadOnlySpan<byte> peerPublicKey32)
    {
        if (privateKey32.Length != 32)
            throw new ArgumentException("X25519 private key must be 32 bytes.", nameof(privateKey32));
        if (peerPublicKey32.Length != 32)
            throw new ArgumentException("X25519 peer public key must be 32 bytes.", nameof(peerPublicKey32));

        return ScalarMultCore(privateKey32, peerPublicKey32, rejectAllZero: true);
    }

    private static byte[] ScalarMultCore(ReadOnlySpan<byte> privateKey32, ReadOnlySpan<byte> uBytes32, bool rejectAllZero)
    {
        Span<byte> k = stackalloc byte[32];
        privateKey32.CopyTo(k);
        k[0] &= 248;
        k[31] &= 127;
        k[31] |= 64;

        Fe25519 x1 = Fe25519.FromBytes(uBytes32);
        Fe25519 x2 = Fe25519.One;
        Fe25519 z2 = Fe25519.Zero;
        Fe25519 x3 = x1;
        Fe25519 z3 = Fe25519.One;
        uint swap = 0;

        for (int t = 254; t >= 0; t--)
        {
            uint kt = (uint)((k[t >> 3] >> (t & 7)) & 1);
            swap ^= kt;
            Fe25519.CSwap(swap, ref x2, ref x3);
            Fe25519.CSwap(swap, ref z2, ref z3);
            swap = kt;

            Fe25519 a = Fe25519.Add(x2, z2);
            Fe25519 aa = Fe25519.Sqr(a);
            Fe25519 b = Fe25519.Sub(x2, z2);
            Fe25519 bb = Fe25519.Sqr(b);
            Fe25519 e = Fe25519.Sub(aa, bb);
            Fe25519 c = Fe25519.Add(x3, z3);
            Fe25519 d = Fe25519.Sub(x3, z3);
            Fe25519 da = Fe25519.Mul(d, a);
            Fe25519 cb = Fe25519.Mul(c, b);

            x3 = Fe25519.Sqr(Fe25519.Add(da, cb));
            z3 = Fe25519.Mul(x1, Fe25519.Sqr(Fe25519.Sub(da, cb)));
            x2 = Fe25519.Mul(aa, bb);
            z2 = Fe25519.Mul(e, Fe25519.Add(aa, Fe25519.MulSmall(e, 121665UL)));
        }

        Fe25519.CSwap(swap, ref x2, ref x3);
        Fe25519.CSwap(swap, ref z2, ref z3);
        k.Clear();

        Fe25519 resultFe = Fe25519.Mul(x2, Fe25519.Invert(z2));
        var output = new byte[32];
        Fe25519.ToBytes(resultFe, output);

        if (rejectAllZero)
        {
            byte acc = 0;
            for (int i = 0; i < 32; i++)
                acc |= output[i];
            if (acc == 0)
                throw new CryptographicException("X25519 shared secret is all zeros.");
        }

        return output;
    }
}

/// <summary>
/// Pure managed RFC 8032 Ed25519 signature verification using SHA-512.
/// </summary>
public static class Ed25519
{
    private readonly struct EdPoint
    {
        public readonly Fe25519 X, Y, Z, T;

        public EdPoint(in Fe25519 x, in Fe25519 y, in Fe25519 z, in Fe25519 t)
        {
            X = x; Y = y; Z = z; T = t;
        }
    }

    private static readonly BigInteger OrderL =
        (BigInteger.One << 252) + BigInteger.Parse("27742317777372353535851937790883648493", CultureInfo.InvariantCulture);

    private static readonly Fe25519 D;
    private static readonly Fe25519 TwoD;
    private static readonly Fe25519 SqrtM1;
    private static readonly EdPoint BasePoint;
    private static readonly EdPoint Identity = new(Fe25519.Zero, Fe25519.One, Fe25519.One, Fe25519.Zero);

    static Ed25519()
    {
        D = Fe25519.Sub(Fe25519.Zero, Fe25519.Mul(Fe25519.FromUInt(121665UL), Fe25519.Invert(Fe25519.FromUInt(121666UL))));
        TwoD = Fe25519.Add(D, D);

        Fe25519 two = Fe25519.FromUInt(2UL);
        Fe25519 t = Fe25519.Pow22523(two);
        SqrtM1 = Fe25519.Mul(Fe25519.Sqr(t), two);

        Fe25519 by = Fe25519.Mul(Fe25519.FromUInt(4UL), Fe25519.Invert(Fe25519.FromUInt(5UL)));
        if (!TryRecoverX(by, 0, out Fe25519 bx))
            throw new InvalidOperationException("Failed to initialize Ed25519 base point.");
        BasePoint = new EdPoint(bx, by, Fe25519.One, Fe25519.Mul(bx, by));
    }

    private static bool FeEqual(in Fe25519 a, in Fe25519 b)
    {
        Span<byte> ab = stackalloc byte[32];
        Span<byte> bb = stackalloc byte[32];
        Fe25519.ToBytes(a, ab);
        Fe25519.ToBytes(b, bb);
        return ab.SequenceEqual(bb);
    }

    private static bool TryRecoverX(in Fe25519 y, int xSign, out Fe25519 x)
    {
        Fe25519 y2 = Fe25519.Sqr(y);
        Fe25519 u = Fe25519.Sub(y2, Fe25519.One);
        Fe25519 v = Fe25519.Add(Fe25519.Mul(D, y2), Fe25519.One);

        Fe25519 v3 = Fe25519.Mul(Fe25519.Sqr(v), v);
        Fe25519 v7 = Fe25519.Mul(Fe25519.Sqr(v3), v);
        Fe25519 uv7 = Fe25519.Mul(u, v7);
        x = Fe25519.Mul(Fe25519.Mul(u, v3), Fe25519.Pow22523(uv7));

        Fe25519 vxx = Fe25519.Mul(v, Fe25519.Sqr(x));
        if (!FeEqual(vxx, u))
        {
            Fe25519 negU = Fe25519.Neg(u);
            if (!FeEqual(vxx, negU))
            {
                x = default;
                return false;
            }
            x = Fe25519.Mul(x, SqrtM1);
        }

        Span<byte> xBytes = stackalloc byte[32];
        Fe25519.ToBytes(x, xBytes);

        bool isZero = true;
        for (int i = 0; i < 32; i++)
        {
            if (xBytes[i] != 0)
            {
                isZero = false;
                break;
            }
        }
        if (isZero && xSign == 1)
        {
            x = default;
            return false;
        }

        if ((xBytes[0] & 1) != xSign)
            x = Fe25519.Neg(x);

        return true;
    }

    private static bool TryDecodePoint(ReadOnlySpan<byte> encoded32, out EdPoint point)
    {
        Fe25519 y = Fe25519.FromBytes(encoded32);
        Span<byte> canonicalY = stackalloc byte[32];
        Fe25519.ToBytes(y, canonicalY);

        Span<byte> expectedY = stackalloc byte[32];
        encoded32.CopyTo(expectedY);
        int xSign = (expectedY[31] >> 7) & 1;
        expectedY[31] &= 0x7F;

        if (!canonicalY.SequenceEqual(expectedY))
        {
            point = default;
            return false;
        }

        if (!TryRecoverX(y, xSign, out Fe25519 x))
        {
            point = default;
            return false;
        }

        point = new EdPoint(x, y, Fe25519.One, Fe25519.Mul(x, y));
        return true;
    }

    private static EdPoint Add(in EdPoint p1, in EdPoint p2)
    {
        Fe25519 a = Fe25519.Mul(Fe25519.Sub(p1.Y, p1.X), Fe25519.Sub(p2.Y, p2.X));
        Fe25519 b = Fe25519.Mul(Fe25519.Add(p1.Y, p1.X), Fe25519.Add(p2.Y, p2.X));
        Fe25519 c = Fe25519.Mul(Fe25519.Mul(p1.T, TwoD), p2.T);
        Fe25519 d = Fe25519.Mul(Fe25519.Add(p1.Z, p1.Z), p2.Z);
        Fe25519 e = Fe25519.Sub(b, a);
        Fe25519 f = Fe25519.Sub(d, c);
        Fe25519 g = Fe25519.Add(d, c);
        Fe25519 h = Fe25519.Add(b, a);

        return new EdPoint(
            Fe25519.Mul(e, f),
            Fe25519.Mul(g, h),
            Fe25519.Mul(f, g),
            Fe25519.Mul(e, h));
    }

    private static EdPoint Double(in EdPoint p1)
    {
        Fe25519 a = Fe25519.Sqr(p1.X);
        Fe25519 b = Fe25519.Sqr(p1.Y);
        Fe25519 z2 = Fe25519.Sqr(p1.Z);
        Fe25519 c = Fe25519.Add(z2, z2);
        Fe25519 h = Fe25519.Add(a, b);
        Fe25519 e = Fe25519.Sub(h, Fe25519.Sqr(Fe25519.Add(p1.X, p1.Y)));
        Fe25519 g = Fe25519.Sub(a, b);
        Fe25519 f = Fe25519.Add(c, g);

        return new EdPoint(
            Fe25519.Mul(e, f),
            Fe25519.Mul(g, h),
            Fe25519.Mul(f, g),
            Fe25519.Mul(e, h));
    }

    private static EdPoint DoubleScalarMult(ReadOnlySpan<byte> sLe32, in EdPoint b, ReadOnlySpan<byte> kLe32, in EdPoint negA)
    {
        EdPoint bPlusNegA = Add(b, negA);
        EdPoint r = Identity;

        for (int i = 252; i >= 0; i--)
        {
            r = Double(r);
            int sBit = (sLe32[i >> 3] >> (i & 7)) & 1;
            int kBit = (kLe32[i >> 3] >> (i & 7)) & 1;

            if (sBit != 0 && kBit != 0)
                r = Add(r, bPlusNegA);
            else if (sBit != 0)
                r = Add(r, b);
            else if (kBit != 0)
                r = Add(r, negA);
        }

        return r;
    }

    private static void EncodePoint(in EdPoint p, Span<byte> out32)
    {
        Fe25519 zInv = Fe25519.Invert(p.Z);
        Fe25519 x = Fe25519.Mul(p.X, zInv);
        Fe25519 y = Fe25519.Mul(p.Y, zInv);

        Span<byte> xBytes = stackalloc byte[32];
        Fe25519.ToBytes(x, xBytes);
        Fe25519.ToBytes(y, out32);
        out32[31] |= (byte)((xBytes[0] & 1) << 7);
    }

    public static bool Verify(ReadOnlySpan<byte> publicKey32, ReadOnlySpan<byte> message, ReadOnlySpan<byte> signature64)
    {
        if (publicKey32.Length != 32 || signature64.Length != 64)
            return false;

        if (!TryDecodePoint(publicKey32, out EdPoint a))
            return false;

        ReadOnlySpan<byte> rBytes = signature64[..32];
        ReadOnlySpan<byte> sBytes = signature64[32..64];
        var s = new BigInteger(sBytes, isUnsigned: true, isBigEndian: false);
        if (s >= OrderL)
            return false;

        Span<byte> digest = stackalloc byte[64];
        using (var sha512 = IncrementalHash.CreateHash(HashAlgorithmName.SHA512))
        {
            sha512.AppendData(rBytes);
            sha512.AppendData(publicKey32);
            sha512.AppendData(message);
            sha512.GetHashAndReset(digest);
        }

        var k = new BigInteger(digest, isUnsigned: true, isBigEndian: false) % OrderL;
        Span<byte> kLe32 = stackalloc byte[32];
        k.TryWriteBytes(kLe32, out _, isUnsigned: true, isBigEndian: false);

        var negA = new EdPoint(Fe25519.Neg(a.X), a.Y, a.Z, Fe25519.Neg(a.T));
        EdPoint rCalc = DoubleScalarMult(sBytes, BasePoint, kLe32, negA);

        Span<byte> rEncoded = stackalloc byte[32];
        EncodePoint(rCalc, rEncoded);
        return ConstantTime.Equals(rEncoded, rBytes);
    }
}

public enum EcCurveKind
{
    P256,
    P384,
    P521
}

/// <summary>
/// NIST P-256 / P-384 / P-521 ECDHE key agreement and ECDSA DER verification.
/// </summary>
public static class EcPrimitives
{
    private sealed class CurveParams
    {
        public readonly int CoordSize;
        public readonly int BitLength;
        public readonly BigInteger P;
        public readonly BigInteger B;
        public readonly BigInteger N;
        public readonly BigInteger Gx;
        public readonly BigInteger Gy;
        public readonly ECCurve BclCurve;

        public CurveParams(int coordSize, int bitLength, string pHex, string bHex, string nHex, string gxHex, string gyHex, ECCurve bclCurve)
        {
            CoordSize = coordSize;
            BitLength = bitLength;
            P = ParseHex(pHex);
            B = ParseHex(bHex);
            N = ParseHex(nHex);
            Gx = ParseHex(gxHex);
            Gy = ParseHex(gyHex);
            BclCurve = bclCurve;
        }

        private static BigInteger ParseHex(string hex) =>
            new(Convert.FromHexString(hex), isUnsigned: true, isBigEndian: true);
    }

    private readonly struct JacobianPoint
    {
        public readonly BigInteger X, Y, Z;

        public JacobianPoint(BigInteger x, BigInteger y, BigInteger z)
        {
            X = x; Y = y; Z = z;
        }

        public static JacobianPoint Infinity => new(BigInteger.One, BigInteger.One, BigInteger.Zero);
    }

    private static readonly CurveParams P256Params = new(
        coordSize: 32,
        bitLength: 256,
        pHex: "ffffffff00000001000000000000000000000000ffffffffffffffffffffffff",
        bHex: "5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b",
        nHex: "ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551",
        gxHex: "6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296",
        gyHex: "4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5",
        bclCurve: ECCurve.NamedCurves.nistP256);

    private static readonly CurveParams P384Params = new(
        coordSize: 48,
        bitLength: 384,
        pHex: "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff",
        bHex: "b3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f5013875ac656398d8a2ed19d2a85c8edd3ec2aef",
        nHex: "ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973",
        gxHex: "aa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7",
        gyHex: "3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f",
        bclCurve: ECCurve.NamedCurves.nistP384);

    private static readonly CurveParams P521Params = new(
        coordSize: 66,
        bitLength: 521,
        pHex: "01ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        bHex: "0051953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3b8b489918ef109e156193951ec7e937b1652c0bd3bb1bf073573df883d2c34f1ef451fd46b503f00",
        nHex: "01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409",
        gxHex: "00c6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3dbaa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66",
        gyHex: "011839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e662c97ee72995ef42640c550b9013fad0761353c7086a272c24088be94769fd16650",
        bclCurve: ECCurve.NamedCurves.nistP521);

    private static CurveParams GetParams(EcCurveKind curve) => curve switch
    {
        EcCurveKind.P256 => P256Params,
        EcCurveKind.P384 => P384Params,
        EcCurveKind.P521 => P521Params,
        _ => throw new ArgumentOutOfRangeException(nameof(curve), curve, "Unsupported EC curve.")
    };

    public static bool TryCurveFromOid(string oid, out EcCurveKind curve)
    {
        switch (oid)
        {
            case "1.2.840.10045.3.1.7":
                curve = EcCurveKind.P256;
                return true;
            case "1.3.132.0.34":
                curve = EcCurveKind.P384;
                return true;
            case "1.3.132.0.35":
                curve = EcCurveKind.P521;
                return true;
            default:
                curve = default;
                return false;
        }
    }

    private static BigInteger Mod(BigInteger x, BigInteger p)
    {
        BigInteger r = x % p;
        return r.Sign < 0 ? r + p : r;
    }

    private static JacobianPoint Double(in JacobianPoint pt, BigInteger p)
    {
        if (pt.Z.IsZero || pt.Y.IsZero)
            return JacobianPoint.Infinity;

        BigInteger delta = Mod(pt.Z * pt.Z, p);
        BigInteger gamma = Mod(pt.Y * pt.Y, p);
        BigInteger beta = Mod(pt.X * gamma, p);
        BigInteger alpha = Mod(3 * (pt.X - delta) * (pt.X + delta), p);
        BigInteger x3 = Mod(alpha * alpha - 8 * beta, p);
        BigInteger yz = pt.Y + pt.Z;
        BigInteger z3 = Mod(yz * yz - gamma - delta, p);
        BigInteger y3 = Mod(alpha * (4 * beta - x3) - 8 * gamma * gamma, p);
        return new JacobianPoint(x3, y3, z3);
    }

    private static JacobianPoint Add(in JacobianPoint p1, in JacobianPoint p2, BigInteger p)
    {
        if (p1.Z.IsZero)
            return p2;
        if (p2.Z.IsZero)
            return p1;

        BigInteger z1z1 = Mod(p1.Z * p1.Z, p);
        BigInteger z2z2 = Mod(p2.Z * p2.Z, p);
        BigInteger u1 = Mod(p1.X * z2z2, p);
        BigInteger u2 = Mod(p2.X * z1z1, p);
        BigInteger s1 = Mod(p1.Y * p2.Z * z2z2, p);
        BigInteger s2 = Mod(p2.Y * p1.Z * z1z1, p);

        if (u1 == u2)
            return s1 == s2 ? Double(p1, p) : JacobianPoint.Infinity;

        BigInteger h = Mod(u2 - u1, p);
        BigInteger twoH = h << 1;
        BigInteger i = Mod(twoH * twoH, p);
        BigInteger j = Mod(h * i, p);
        BigInteger r = Mod((s2 - s1) << 1, p);
        BigInteger v = Mod(u1 * i, p);
        BigInteger x3 = Mod(r * r - j - (v << 1), p);
        BigInteger y3 = Mod(r * (v - x3) - ((s1 * j) << 1), p);
        BigInteger zSum = p1.Z + p2.Z;
        BigInteger z3 = Mod((zSum * zSum - z1z1 - z2z2) * h, p);
        return new JacobianPoint(x3, y3, z3);
    }

    private static JacobianPoint ScalarMult(CurveParams cp, BigInteger scalar, BigInteger px, BigInteger py)
    {
        var r0 = JacobianPoint.Infinity;
        var r1 = new JacobianPoint(px, py, BigInteger.One);

        for (int bit = cp.BitLength - 1; bit >= 0; bit--)
        {
            if (((scalar >> bit) & BigInteger.One).IsZero)
            {
                r1 = Add(r0, r1, cp.P);
                r0 = Double(r0, cp.P);
            }
            else
            {
                r0 = Add(r0, r1, cp.P);
                r1 = Double(r1, cp.P);
            }
        }

        return r0;
    }

    private static void WriteFixedBigEndian(BigInteger value, Span<byte> dest)
    {
        dest.Clear();
        if (!value.IsZero)
        {
            int count = value.GetByteCount(isUnsigned: true);
            value.TryWriteBytes(dest.Slice(dest.Length - count), out _, isUnsigned: true, isBigEndian: true);
        }
    }

    private static bool IsOnCurve(CurveParams cp, BigInteger x, BigInteger y)
    {
        if (x.Sign < 0 || x >= cp.P || y.Sign < 0 || y >= cp.P)
            return false;
        BigInteger lhs = Mod(y * y, cp.P);
        BigInteger rhs = Mod(x * x * x - 3 * x + cp.B, cp.P);
        return lhs == rhs;
    }

    public static (byte[] PrivateKey, byte[] PublicUncompressedPoint) GenerateEcdheKeyPair(EcCurveKind curve)
    {
        CurveParams cp = GetParams(curve);
        var priv = new byte[cp.CoordSize];
        BigInteger d;
        int topMask = (1 << (cp.BitLength - (cp.CoordSize - 1) * 8)) - 1;

        while (true)
        {
            RandomNumberGenerator.Fill(priv);
            priv[0] &= (byte)topMask;
            d = new BigInteger(priv, isUnsigned: true, isBigEndian: true);
            if (d > BigInteger.Zero && d < cp.N)
                break;
        }

        JacobianPoint q = ScalarMult(cp, d, cp.Gx, cp.Gy);
        BigInteger zInv = BigInteger.ModPow(q.Z, cp.P - 2, cp.P);
        BigInteger zInv2 = Mod(zInv * zInv, cp.P);
        BigInteger zInv3 = Mod(zInv2 * zInv, cp.P);
        BigInteger qx = Mod(q.X * zInv2, cp.P);
        BigInteger qy = Mod(q.Y * zInv3, cp.P);

        var pub = new byte[1 + 2 * cp.CoordSize];
        pub[0] = 0x04;
        WriteFixedBigEndian(qx, pub.AsSpan(1, cp.CoordSize));
        WriteFixedBigEndian(qy, pub.AsSpan(1 + cp.CoordSize, cp.CoordSize));
        return (priv, pub);
    }

    public static byte[] DeriveEcdheSharedSecret(
        EcCurveKind curve,
        ReadOnlySpan<byte> privateKey,
        ReadOnlySpan<byte> peerUncompressedPoint)
    {
        CurveParams cp = GetParams(curve);
        if (privateKey.Length != cp.CoordSize)
            throw new ArgumentException($"Private key must be {cp.CoordSize} bytes for {curve}.", nameof(privateKey));
        if (peerUncompressedPoint.Length != 1 + 2 * cp.CoordSize || peerUncompressedPoint[0] != 0x04)
            throw new ArgumentException($"Peer public point must be an uncompressed 0x04 point of {1 + 2 * cp.CoordSize} bytes.", nameof(peerUncompressedPoint));

        var d = new BigInteger(privateKey, isUnsigned: true, isBigEndian: true);
        if (d <= BigInteger.Zero || d >= cp.N)
            throw new CryptographicException("EC private scalar is out of valid range [1, n-1].");

        var px = new BigInteger(peerUncompressedPoint.Slice(1, cp.CoordSize), isUnsigned: true, isBigEndian: true);
        var py = new BigInteger(peerUncompressedPoint.Slice(1 + cp.CoordSize, cp.CoordSize), isUnsigned: true, isBigEndian: true);
        if (!IsOnCurve(cp, px, py))
            throw new CryptographicException("Peer EC point is not on the expected curve.");

        JacobianPoint shared = ScalarMult(cp, d, px, py);
        if (shared.Z.IsZero)
            throw new CryptographicException("ECDH derived the point at infinity.");

        BigInteger zInv = BigInteger.ModPow(shared.Z, cp.P - 2, cp.P);
        BigInteger zInv2 = Mod(zInv * zInv, cp.P);
        BigInteger xAff = Mod(shared.X * zInv2, cp.P);

        var secret = new byte[cp.CoordSize];
        WriteFixedBigEndian(xAff, secret);
        return secret;
    }

    private static bool TryParseDerIntegerToFixed(ReadOnlySpan<byte> asnInt, int width, Span<byte> dest)
    {
        if (asnInt.IsEmpty || (asnInt[0] & 0x80) != 0)
            return false;

        if (asnInt.Length > 1 && asnInt[0] == 0x00)
            asnInt = asnInt[1..];

        bool allZero = true;
        for (int i = 0; i < asnInt.Length; i++)
        {
            if (asnInt[i] != 0)
            {
                allZero = false;
                break;
            }
        }
        if (allZero || asnInt.Length > width)
            return false;

        dest.Clear();
        asnInt.CopyTo(dest.Slice(width - asnInt.Length));
        return true;
    }

    public static bool VerifyEcdsa(
        EcCurveKind curve,
        ReadOnlySpan<byte> publicUncompressedPoint,
        HashAlgorithmKind hashAlg,
        ReadOnlySpan<byte> data,
        ReadOnlySpan<byte> derSignature)
    {
        CurveParams cp = GetParams(curve);
        if (publicUncompressedPoint.Length != 1 + 2 * cp.CoordSize || publicUncompressedPoint[0] != 0x04)
            return false;

        var px = new BigInteger(publicUncompressedPoint.Slice(1, cp.CoordSize), isUnsigned: true, isBigEndian: true);
        var py = new BigInteger(publicUncompressedPoint.Slice(1 + cp.CoordSize, cp.CoordSize), isUnsigned: true, isBigEndian: true);
        if (!IsOnCurve(cp, px, py))
            return false;

        Span<byte> ieeeSig = stackalloc byte[2 * cp.CoordSize];
        try
        {
            var reader = new AsnReader(derSignature.ToArray(), AsnEncodingRules.DER);
            AsnReader seq = reader.ReadSequence();
            if (reader.HasData)
                return false;

            ReadOnlyMemory<byte> rBytes = seq.ReadIntegerBytes();
            ReadOnlyMemory<byte> sBytes = seq.ReadIntegerBytes();
            if (seq.HasData)
                return false;

            if (!TryParseDerIntegerToFixed(rBytes.Span, cp.CoordSize, ieeeSig[..cp.CoordSize]))
                return false;
            if (!TryParseDerIntegerToFixed(sBytes.Span, cp.CoordSize, ieeeSig[cp.CoordSize..]))
                return false;
        }
        catch (AsnContentException)
        {
            return false;
        }

        try
        {
            var ecParams = new ECParameters
            {
                Curve = cp.BclCurve,
                Q = new ECPoint
                {
                    X = publicUncompressedPoint.Slice(1, cp.CoordSize).ToArray(),
                    Y = publicUncompressedPoint.Slice(1 + cp.CoordSize, cp.CoordSize).ToArray()
                }
            };
            using var ecdsa = ECDsa.Create(ecParams);
            return ecdsa.VerifyData(data, ieeeSig, HashPrimitives.ToBclName(hashAlg), DSASignatureFormat.IeeeP1363FixedFieldConcatenation);
        }
        catch (CryptographicException)
        {
            return false;
        }
    }
}
