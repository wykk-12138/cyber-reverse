using System;
using System.Security.Cryptography;

namespace Cybersole.Http.Crypto;

/// <summary>
/// Pure managed NIST FIPS 203 ML-KEM-768 (k=3, n=256, q=3329, eta1=2, eta2=2, du=10, dv=4).
/// </summary>
public static class MlKem768
{
    public const int EncapsulationKeySize = 1184;
    public const int DecapsulationKeySize = 2400;
    public const int CiphertextSize = 1088;
    public const int SharedSecretSize = 32;

    private const int K = 3;
    private const int N = 256;
    private const int Q = 3329;
    private const int Du = 10;
    private const int Dv = 4;
    private const int Inv128ModQ = 3303;

    private static readonly int[] Zetas = new int[128];
    private static readonly int[] BaseCaseGamma = new int[128];

    static MlKem768()
    {
        for (int i = 0; i < 128; i++)
        {
            int br = BitRev7(i);
            Zetas[i] = PowModQ(17, br);
            BaseCaseGamma[i] = PowModQ(17, 2 * br + 1);
        }
    }

    private static int BitRev7(int x)
    {
        int r = 0;
        for (int i = 0; i < 7; i++)
        {
            r = (r << 1) | (x & 1);
            x >>= 1;
        }
        return r;
    }

    private static int PowModQ(int b, int exp)
    {
        int result = 1;
        int cur = b % Q;
        while (exp > 0)
        {
            if ((exp & 1) != 0)
                result = (result * cur) % Q;
            cur = (cur * cur) % Q;
            exp >>= 1;
        }
        return result;
    }

    private static int ModQ(long x)
    {
        long t = (x * 1290167L) >> 32;
        int r = (int)(x - t * Q);
        r -= Q;
        r += (r >> 31) & Q;
        return r;
    }

    private static int AddModQ(int a, int b)
    {
        int s = a + b - Q;
        return s + ((s >> 31) & Q);
    }

    private static int SubModQ(int a, int b)
    {
        int d = a - b;
        return d + ((d >> 31) & Q);
    }

    private static int Compress(int x, int d)
    {
        ulong val = ((ulong)x << d) + 1664UL;
        int q = (int)((val * 10321340UL) >> 35);
        return q & ((1 << d) - 1);
    }

    private static int Decompress(int y, int d) => ((y * Q) + (1 << (d - 1))) >> d;

    private static void Ntt(Span<int> f)
    {
        int i = 1;
        for (int len = 128; len >= 2; len >>= 1)
        {
            for (int start = 0; start < N; start += 2 * len)
            {
                int zeta = Zetas[i++];
                for (int j = start; j < start + len; j++)
                {
                    int t = ModQ((long)zeta * f[j + len]);
                    f[j + len] = SubModQ(f[j], t);
                    f[j] = AddModQ(f[j], t);
                }
            }
        }
    }

    private static void InvNtt(Span<int> f)
    {
        int i = 127;
        for (int len = 2; len <= 128; len <<= 1)
        {
            for (int start = 0; start < N; start += 2 * len)
            {
                int zeta = Zetas[i--];
                for (int j = start; j < start + len; j++)
                {
                    int t = f[j];
                    f[j] = AddModQ(t, f[j + len]);
                    f[j + len] = ModQ((long)zeta * SubModQ(f[j + len], t));
                }
            }
        }

        for (int j = 0; j < N; j++)
            f[j] = ModQ((long)f[j] * Inv128ModQ);
    }

    private static void MultiplyNttsAdd(ReadOnlySpan<int> f, ReadOnlySpan<int> g, Span<int> acc)
    {
        for (int i = 0; i < 128; i++)
        {
            int idx = 2 * i;
            int a0 = f[idx], a1 = f[idx + 1];
            int b0 = g[idx], b1 = g[idx + 1];
            int gamma = BaseCaseGamma[i];

            int c0 = AddModQ(ModQ((long)a0 * b0), ModQ((long)ModQ((long)a1 * b1) * gamma));
            int c1 = AddModQ(ModQ((long)a0 * b1), ModQ((long)a1 * b0));

            acc[idx] = AddModQ(acc[idx], c0);
            acc[idx + 1] = AddModQ(acc[idx + 1], c1);
        }
    }

    private static void SampleNtt(ReadOnlySpan<byte> rho32, byte b1, byte b2, Span<int> a)
    {
        Span<byte> seed = stackalloc byte[34];
        rho32.CopyTo(seed);
        seed[32] = b1;
        seed[33] = b2;

        using XofReader xof = HashPrimitives.CreateShake128Reader(seed);
        Span<byte> buf = stackalloc byte[3];
        int j = 0;
        while (j < N)
        {
            xof.Squeeze(buf);
            int d1 = buf[0] + ((buf[1] & 0x0F) << 8);
            int d2 = (buf[1] >> 4) + (buf[2] << 4);
            if (d1 < Q)
                a[j++] = d1;
            if (d2 < Q && j < N)
                a[j++] = d2;
        }
        seed.Clear();
    }

    private static void SamplePolyCbd2(ReadOnlySpan<byte> s32, byte nByte, Span<int> f)
    {
        Span<byte> input = stackalloc byte[33];
        Span<byte> prf = stackalloc byte[128];
        s32.CopyTo(input);
        input[32] = nByte;
        HashPrimitives.Shake256(input, prf);

        for (int i = 0; i < N; i++)
        {
            int nib = (prf[i >> 1] >> ((i & 1) * 4)) & 0x0F;
            int x = (nib & 1) + ((nib >> 1) & 1);
            int y = ((nib >> 2) & 1) + ((nib >> 3) & 1);
            f[i] = SubModQ(x, y);
        }

        input.Clear();
        prf.Clear();
    }

    private static void ByteEncode1(ReadOnlySpan<int> f, Span<byte> out32)
    {
        out32.Clear();
        for (int i = 0; i < N; i++)
            out32[i >> 3] |= (byte)((f[i] & 1) << (i & 7));
    }

    private static void ByteDecode1(ReadOnlySpan<byte> in32, Span<int> f)
    {
        for (int i = 0; i < N; i++)
            f[i] = (in32[i >> 3] >> (i & 7)) & 1;
    }

    private static void ByteEncode4(ReadOnlySpan<int> f, Span<byte> out128)
    {
        for (int i = 0; i < 128; i++)
            out128[i] = (byte)((f[2 * i] & 0x0F) | ((f[2 * i + 1] & 0x0F) << 4));
    }

    private static void ByteDecode4(ReadOnlySpan<byte> in128, Span<int> f)
    {
        for (int i = 0; i < 128; i++)
        {
            f[2 * i] = in128[i] & 0x0F;
            f[2 * i + 1] = in128[i] >> 4;
        }
    }

    private static void ByteEncode10(ReadOnlySpan<int> f, Span<byte> out320)
    {
        for (int i = 0; i < 64; i++)
        {
            int c0 = f[4 * i];
            int c1 = f[4 * i + 1];
            int c2 = f[4 * i + 2];
            int c3 = f[4 * i + 3];
            int o = 5 * i;
            out320[o + 0] = (byte)c0;
            out320[o + 1] = (byte)((c0 >> 8) | (c1 << 2));
            out320[o + 2] = (byte)((c1 >> 6) | (c2 << 4));
            out320[o + 3] = (byte)((c2 >> 4) | (c3 << 6));
            out320[o + 4] = (byte)(c3 >> 2);
        }
    }

    private static void ByteDecode10(ReadOnlySpan<byte> in320, Span<int> f)
    {
        for (int i = 0; i < 64; i++)
        {
            int o = 5 * i;
            byte b0 = in320[o + 0], b1 = in320[o + 1], b2 = in320[o + 2], b3 = in320[o + 3], b4 = in320[o + 4];
            f[4 * i + 0] = (b0 | (b1 << 8)) & 0x3FF;
            f[4 * i + 1] = ((b1 >> 2) | (b2 << 6)) & 0x3FF;
            f[4 * i + 2] = ((b2 >> 4) | (b3 << 4)) & 0x3FF;
            f[4 * i + 3] = ((b3 >> 6) | (b4 << 2)) & 0x3FF;
        }
    }

    private static void ByteEncode12(ReadOnlySpan<int> f, Span<byte> out384)
    {
        for (int i = 0; i < 128; i++)
        {
            int c0 = f[2 * i];
            int c1 = f[2 * i + 1];
            int o = 3 * i;
            out384[o + 0] = (byte)c0;
            out384[o + 1] = (byte)((c0 >> 8) | (c1 << 4));
            out384[o + 2] = (byte)(c1 >> 4);
        }
    }

    private static bool ByteDecode12Checked(ReadOnlySpan<byte> in384, Span<int> f, bool enforceModQ)
    {
        for (int i = 0; i < 128; i++)
        {
            int o = 3 * i;
            int c0 = in384[o + 0] | ((in384[o + 1] & 0x0F) << 8);
            int c1 = (in384[o + 1] >> 4) | (in384[o + 2] << 4);
            if (enforceModQ && (c0 >= Q || c1 >= Q))
                return false;
            f[2 * i + 0] = c0;
            f[2 * i + 1] = c1;
        }
        return true;
    }

    private static void KPkeKeyGen(ReadOnlySpan<byte> d32, Span<byte> ekPke, Span<byte> dkPke)
    {
        Span<byte> dDomain = stackalloc byte[33];
        Span<byte> gOut = stackalloc byte[64];
        d32.CopyTo(dDomain);
        dDomain[32] = K;
        HashPrimitives.Sha3_512(dDomain, gOut);

        ReadOnlySpan<byte> rho = gOut[..32];
        ReadOnlySpan<byte> sigma = gOut[32..64];

        int[] sHat = new int[K * N];
        int[] eHat = new int[K * N];
        int[] aHat = new int[N];
        int[] tHat = new int[N];

        try
        {
            byte nCounter = 0;
            for (int i = 0; i < K; i++)
            {
                Span<int> si = sHat.AsSpan(i * N, N);
                SamplePolyCbd2(sigma, nCounter++, si);
                Ntt(si);
            }

            for (int i = 0; i < K; i++)
            {
                Span<int> ei = eHat.AsSpan(i * N, N);
                SamplePolyCbd2(sigma, nCounter++, ei);
                Ntt(ei);
            }

            for (int i = 0; i < K; i++)
            {
                Array.Clear(tHat);
                for (int j = 0; j < K; j++)
                {
                    SampleNtt(rho, (byte)j, (byte)i, aHat);
                    MultiplyNttsAdd(aHat, sHat.AsSpan(j * N, N), tHat);
                }

                Span<int> ei = eHat.AsSpan(i * N, N);
                for (int c = 0; c < N; c++)
                    tHat[c] = AddModQ(tHat[c], ei[c]);

                ByteEncode12(tHat, ekPke.Slice(i * 384, 384));
                ByteEncode12(sHat.AsSpan(i * N, N), dkPke.Slice(i * 384, 384));
            }

            rho.CopyTo(ekPke.Slice(K * 384, 32));
        }
        finally
        {
            dDomain.Clear();
            gOut.Clear();
            Array.Clear(sHat);
            Array.Clear(eHat);
            Array.Clear(aHat);
            Array.Clear(tHat);
        }
    }

    private static void KPkeEncrypt(ReadOnlySpan<byte> ekPke, ReadOnlySpan<byte> m32, ReadOnlySpan<byte> r32, Span<byte> ciphertext)
    {
        int[] tHat = new int[K * N];
        int[] yHat = new int[K * N];
        int[] aHat = new int[N];
        int[] poly = new int[N];
        int[] noise = new int[N];
        int[] compressed = new int[N];

        try
        {
            for (int i = 0; i < K; i++)
                ByteDecode12Checked(ekPke.Slice(i * 384, 384), tHat.AsSpan(i * N, N), enforceModQ: false);

            ReadOnlySpan<byte> rho = ekPke.Slice(K * 384, 32);

            byte nCounter = 0;
            for (int i = 0; i < K; i++)
            {
                Span<int> yi = yHat.AsSpan(i * N, N);
                SamplePolyCbd2(r32, nCounter++, yi);
                Ntt(yi);
            }

            for (int i = 0; i < K; i++)
            {
                Array.Clear(poly);
                for (int j = 0; j < K; j++)
                {
                    SampleNtt(rho, (byte)i, (byte)j, aHat);
                    MultiplyNttsAdd(aHat, yHat.AsSpan(j * N, N), poly);
                }
                InvNtt(poly);
                SamplePolyCbd2(r32, nCounter++, noise);
                for (int c = 0; c < N; c++)
                    compressed[c] = Compress(AddModQ(poly[c], noise[c]), Du);
                ByteEncode10(compressed, ciphertext.Slice(i * 320, 320));
            }

            Array.Clear(poly);
            for (int i = 0; i < K; i++)
                MultiplyNttsAdd(tHat.AsSpan(i * N, N), yHat.AsSpan(i * N, N), poly);
            InvNtt(poly);

            SamplePolyCbd2(r32, nCounter, noise);
            ByteDecode1(m32, aHat);
            for (int c = 0; c < N; c++)
            {
                int mu = Decompress(aHat[c], 1);
                int v = AddModQ(AddModQ(poly[c], noise[c]), mu);
                compressed[c] = Compress(v, Dv);
            }
            ByteEncode4(compressed, ciphertext.Slice(K * 320, 128));
        }
        finally
        {
            Array.Clear(tHat);
            Array.Clear(yHat);
            Array.Clear(aHat);
            Array.Clear(poly);
            Array.Clear(noise);
            Array.Clear(compressed);
        }
    }

    private static void KPkeDecrypt(ReadOnlySpan<byte> dkPke, ReadOnlySpan<byte> ciphertext, Span<byte> mOut32)
    {
        int[] u = new int[N];
        int[] sHat = new int[N];
        int[] acc = new int[N];
        int[] v = new int[N];

        try
        {
            for (int i = 0; i < K; i++)
            {
                ByteDecode10(ciphertext.Slice(i * 320, 320), u);
                for (int c = 0; c < N; c++)
                    u[c] = Decompress(u[c], Du);
                Ntt(u);
                ByteDecode12Checked(dkPke.Slice(i * 384, 384), sHat, enforceModQ: false);
                MultiplyNttsAdd(sHat, u, acc);
            }

            InvNtt(acc);
            ByteDecode4(ciphertext.Slice(K * 320, 128), v);
            for (int c = 0; c < N; c++)
            {
                int vc = Decompress(v[c], Dv);
                v[c] = Compress(SubModQ(vc, acc[c]), 1);
            }
            ByteEncode1(v, mOut32);
        }
        finally
        {
            Array.Clear(u);
            Array.Clear(sHat);
            Array.Clear(acc);
            Array.Clear(v);
        }
    }

    public static (byte[] EncapsulationKey, byte[] DecapsulationKey) KeyGen()
    {
        Span<byte> d = stackalloc byte[32];
        Span<byte> z = stackalloc byte[32];
        try
        {
            RandomNumberGenerator.Fill(d);
            RandomNumberGenerator.Fill(z);
            return KeyGenDeterministic(d, z);
        }
        finally
        {
            d.Clear();
            z.Clear();
        }
    }

    public static (byte[] EncapsulationKey, byte[] DecapsulationKey) KeyGenDeterministic(
        ReadOnlySpan<byte> d32,
        ReadOnlySpan<byte> z32)
    {
        if (d32.Length != 32)
            throw new ArgumentException("Seed d must be 32 bytes.", nameof(d32));
        if (z32.Length != 32)
            throw new ArgumentException("Seed z must be 32 bytes.", nameof(z32));

        var ek = new byte[EncapsulationKeySize];
        var dk = new byte[DecapsulationKeySize];
        KPkeKeyGen(d32, ek, dk.AsSpan(0, K * 384));

        ek.CopyTo(dk.AsSpan(K * 384));
        HashPrimitives.Sha3_256(ek, dk.AsSpan(2 * K * 384 + 32, 32));
        z32.CopyTo(dk.AsSpan(2 * K * 384 + 64));
        return (ek, dk);
    }

    public static (byte[] Ciphertext, byte[] SharedSecret) Encaps(ReadOnlySpan<byte> encapsulationKey)
    {
        Span<byte> m = stackalloc byte[32];
        try
        {
            RandomNumberGenerator.Fill(m);
            return Encaps(encapsulationKey, (ReadOnlySpan<byte>)m);
        }
        finally
        {
            m.Clear();
        }
    }

    public static (byte[] Ciphertext, byte[] SharedSecret) Encaps(
        ReadOnlySpan<byte> encapsulationKey,
        byte[]? randomM32 = null)
    {
        if (randomM32 is null)
            return Encaps(encapsulationKey);
        return Encaps(encapsulationKey, (ReadOnlySpan<byte>)randomM32);
    }

    public static (byte[] Ciphertext, byte[] SharedSecret) Encaps(
        ReadOnlySpan<byte> encapsulationKey,
        ReadOnlySpan<byte> randomM32)
    {
        if (encapsulationKey.Length != EncapsulationKeySize)
            throw new ArgumentException($"Encapsulation key must be {EncapsulationKeySize} bytes.", nameof(encapsulationKey));
        if (randomM32.Length != 32)
            throw new ArgumentException("Randomness m must be 32 bytes.", nameof(randomM32));

        // FIPS 203 §7.2 encapsulation key modulus check
        Span<int> checkPoly = stackalloc int[N];
        for (int i = 0; i < K; i++)
        {
            if (!ByteDecode12Checked(encapsulationKey.Slice(i * 384, 384), checkPoly, enforceModQ: true))
                throw new ArgumentException("Invalid ML-KEM-768 encapsulation key: coefficient >= 3329.", nameof(encapsulationKey));
        }

        Span<byte> gInput = stackalloc byte[64];
        Span<byte> gOut = stackalloc byte[64];
        try
        {
            randomM32.CopyTo(gInput[..32]);
            HashPrimitives.Sha3_256(encapsulationKey, gInput[32..64]);
            HashPrimitives.Sha3_512(gInput, gOut);

            var sharedSecret = gOut[..32].ToArray();
            var ciphertext = new byte[CiphertextSize];
            KPkeEncrypt(encapsulationKey, randomM32, gOut[32..64], ciphertext);
            return (ciphertext, sharedSecret);
        }
        finally
        {
            gInput.Clear();
            gOut.Clear();
        }
    }

    public static byte[] Decaps(ReadOnlySpan<byte> decapsulationKey, ReadOnlySpan<byte> ciphertext)
    {
        if (decapsulationKey.Length != DecapsulationKeySize)
            throw new ArgumentException($"Decapsulation key must be {DecapsulationKeySize} bytes.", nameof(decapsulationKey));
        if (ciphertext.Length != CiphertextSize)
            throw new ArgumentException($"Ciphertext must be {CiphertextSize} bytes.", nameof(ciphertext));

        ReadOnlySpan<byte> dkPke = decapsulationKey[..1152];
        ReadOnlySpan<byte> ekPke = decapsulationKey.Slice(1152, EncapsulationKeySize);
        ReadOnlySpan<byte> h = decapsulationKey.Slice(2336, 32);
        ReadOnlySpan<byte> z = decapsulationKey.Slice(2368, 32);

        // FIPS 203 §7.3 hash check
        Span<byte> hActual = stackalloc byte[32];
        HashPrimitives.Sha3_256(ekPke, hActual);
        if (!ConstantTime.Equals(hActual, h))
            throw new ArgumentException("Invalid ML-KEM-768 decapsulation key: H(ek) check failed.", nameof(decapsulationKey));

        Span<byte> mPrime = stackalloc byte[32];
        Span<byte> gInput = stackalloc byte[64];
        Span<byte> gOut = stackalloc byte[64];
        Span<byte> jInput = stackalloc byte[32 + CiphertextSize];
        Span<byte> kBar = stackalloc byte[SharedSecretSize];
        var cPrime = new byte[CiphertextSize];

        try
        {
            KPkeDecrypt(dkPke, ciphertext, mPrime);

            mPrime.CopyTo(gInput[..32]);
            h.CopyTo(gInput[32..64]);
            HashPrimitives.Sha3_512(gInput, gOut);

            z.CopyTo(jInput[..32]);
            ciphertext.CopyTo(jInput[32..]);
            HashPrimitives.Shake256(jInput, kBar);

            KPkeEncrypt(ekPke, mPrime, gOut[32..64], cPrime);

            int diff = 0;
            for (int i = 0; i < CiphertextSize; i++)
                diff |= ciphertext[i] ^ cPrime[i];

            byte selectBar = (byte)((diff | -diff) >> 31);
            var sharedSecret = new byte[SharedSecretSize];
            for (int i = 0; i < SharedSecretSize; i++)
                sharedSecret[i] = (byte)(gOut[i] ^ (selectBar & (gOut[i] ^ kBar[i])));

            return sharedSecret;
        }
        finally
        {
            mPrime.Clear();
            gInput.Clear();
            gOut.Clear();
            jInput.Clear();
            kBar.Clear();
            ConstantTime.ZeroMemory(cPrime);
        }
    }
}

public sealed class HybridKeyState : IDisposable
{
    internal byte[] MlKemDecapsulationKey { get; }
    internal byte[] X25519PrivateKey { get; }
    internal bool IsX25519First { get; }
    private bool _disposed;

    internal HybridKeyState(byte[] mlKemDecapsulationKey, byte[] x25519PrivateKey, bool isX25519First)
    {
        MlKemDecapsulationKey = mlKemDecapsulationKey;
        X25519PrivateKey = x25519PrivateKey;
        IsX25519First = isX25519First;
    }

    internal void ThrowIfDisposed() => ObjectDisposedException.ThrowIf(_disposed, this);

    public void Dispose()
    {
        if (!_disposed)
        {
            ConstantTime.ZeroMemory(MlKemDecapsulationKey);
            ConstantTime.ZeroMemory(X25519PrivateKey);
            _disposed = true;
        }
    }
}

/// <summary>
/// Post-quantum hybrid KEM combiners for TLS 1.3 (X25519MLKEM768 and X25519Kyber768Draft00).
/// </summary>
public static class HybridKem
{
    public static (byte[] ClientKeyShare, HybridKeyState State) GenerateX25519MlKem768()
    {
        (byte[] ek, byte[] dk) = MlKem768.KeyGen();
        X25519.GenerateKeyPair(out byte[] xPriv, out byte[] xPub);

        var share = new byte[MlKem768.EncapsulationKeySize + 32];
        ek.CopyTo(share.AsSpan(0, MlKem768.EncapsulationKeySize));
        xPub.CopyTo(share.AsSpan(MlKem768.EncapsulationKeySize, 32));
        return (share, new HybridKeyState(dk, xPriv, isX25519First: false));
    }

    public static (byte[] ClientKeyShare, HybridKeyState State) GenerateX25519Kyber768Draft00()
    {
        (byte[] ek, byte[] dk) = MlKem768.KeyGen();
        X25519.GenerateKeyPair(out byte[] xPriv, out byte[] xPub);

        var share = new byte[32 + MlKem768.EncapsulationKeySize];
        xPub.CopyTo(share.AsSpan(0, 32));
        ek.CopyTo(share.AsSpan(32, MlKem768.EncapsulationKeySize));
        return (share, new HybridKeyState(dk, xPriv, isX25519First: true));
    }

    public static byte[] CompleteX25519MlKem768(HybridKeyState state, ReadOnlySpan<byte> serverKeyShare)
    {
        ArgumentNullException.ThrowIfNull(state);
        state.ThrowIfDisposed();

        const int expectedLen = MlKem768.CiphertextSize + 32;
        if (serverKeyShare.Length != expectedLen)
            throw new ArgumentException($"Server hybrid key share must be {expectedLen} bytes.", nameof(serverKeyShare));

        if (!state.IsX25519First)
        {
            byte[] mlKemSs = MlKem768.Decaps(state.MlKemDecapsulationKey, serverKeyShare[..MlKem768.CiphertextSize]);
            byte[] x25519Ss = X25519.ScalarMult(state.X25519PrivateKey, serverKeyShare.Slice(MlKem768.CiphertextSize, 32));
            var combined = new byte[64];
            mlKemSs.CopyTo(combined.AsSpan(0, 32));
            x25519Ss.CopyTo(combined.AsSpan(32, 32));
            ConstantTime.ZeroMemory(mlKemSs);
            ConstantTime.ZeroMemory(x25519Ss);
            return combined;
        }
        else
        {
            byte[] x25519Ss = X25519.ScalarMult(state.X25519PrivateKey, serverKeyShare[..32]);
            byte[] mlKemSs = MlKem768.Decaps(state.MlKemDecapsulationKey, serverKeyShare.Slice(32, MlKem768.CiphertextSize));
            var combined = new byte[64];
            x25519Ss.CopyTo(combined.AsSpan(0, 32));
            mlKemSs.CopyTo(combined.AsSpan(32, 32));
            ConstantTime.ZeroMemory(x25519Ss);
            ConstantTime.ZeroMemory(mlKemSs);
            return combined;
        }
    }
}
