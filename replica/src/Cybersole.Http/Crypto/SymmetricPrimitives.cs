using System;
using System.Buffers.Binary;
using System.Numerics;
using System.Security.Cryptography;

namespace Cybersole.Http.Crypto;

/// <summary>
/// Pure managed AES-128 / AES-192 / AES-256 block cipher (FIPS 197),
/// GF(2^128) GHASH + AES-GCM (NIST SP 800-38D), and AES-CBC with constant-time PKCS#7 padding.
/// </summary>
public static class AesPrimitives
{
    private static readonly byte[] SBox = new byte[256];
    private static readonly byte[] InvSBox = new byte[256];

    private static readonly uint[] Rcon =
    {
        0x01000000u, 0x02000000u, 0x04000000u, 0x08000000u, 0x10000000u,
        0x20000000u, 0x40000000u, 0x80000000u, 0x1B000000u, 0x36000000u
    };

    static AesPrimitives()
    {
        for (int x = 0; x < 256; x++)
        {
            byte inv = Gf256Inverse((byte)x);
            byte s = (byte)(inv
                ^ RotL8(inv, 1)
                ^ RotL8(inv, 2)
                ^ RotL8(inv, 3)
                ^ RotL8(inv, 4)
                ^ 0x63);
            SBox[x] = s;
            InvSBox[s] = (byte)x;
        }
    }

    private static byte RotL8(byte v, int shift) => (byte)((v << shift) | (v >> (8 - shift)));

    private static byte Gf256Mul(byte a, byte b)
    {
        byte p = 0;
        for (int i = 0; i < 8; i++)
        {
            if ((b & 1) != 0)
                p ^= a;
            bool hi = (a & 0x80) != 0;
            a <<= 1;
            if (hi)
                a ^= 0x1B;
            b >>= 1;
        }
        return p;
    }

    private static byte Gf256Inverse(byte a)
    {
        if (a == 0)
            return 0;
        byte a2 = Gf256Mul(a, a);
        byte a3 = Gf256Mul(a2, a);
        byte a6 = Gf256Mul(a3, a3);
        byte a12 = Gf256Mul(a6, a6);
        byte a15 = Gf256Mul(a12, a3);
        byte a30 = Gf256Mul(a15, a15);
        byte a60 = Gf256Mul(a30, a30);
        byte a120 = Gf256Mul(a60, a60);
        byte a127 = Gf256Mul(a120, Gf256Mul(a6, a));
        return Gf256Mul(a127, a127);
    }

    private static uint SubWord(uint w) =>
        ((uint)SBox[(w >> 24) & 0xFF] << 24)
        | ((uint)SBox[(w >> 16) & 0xFF] << 16)
        | ((uint)SBox[(w >> 8) & 0xFF] << 8)
        | SBox[w & 0xFF];

    private static int ExpandKey(ReadOnlySpan<byte> key, Span<uint> roundKeys)
    {
        if (key.Length is not (16 or 24 or 32))
            throw new ArgumentException("AES key must be 16, 24, or 32 bytes.", nameof(key));

        int nk = key.Length >> 2;
        int nr = nk + 6;
        int totalWords = 4 * (nr + 1);

        for (int i = 0; i < nk; i++)
            roundKeys[i] = BinaryPrimitives.ReadUInt32BigEndian(key.Slice(i * 4, 4));

        for (int i = nk; i < totalWords; i++)
        {
            uint temp = roundKeys[i - 1];
            if (i % nk == 0)
                temp = SubWord(BitOperations.RotateLeft(temp, 8)) ^ Rcon[(i / nk) - 1];
            else if (nk > 6 && i % nk == 4)
                temp = SubWord(temp);
            roundKeys[i] = roundKeys[i - nk] ^ temp;
        }

        return nr;
    }

    private static byte XTime(byte b) => (byte)((b << 1) ^ ((b >> 7) * 0x1B));

    private static void AddRoundKey(Span<byte> s, ReadOnlySpan<uint> rk, int round)
    {
        int baseIdx = round * 4;
        for (int c = 0; c < 4; c++)
        {
            uint k = rk[baseIdx + c];
            int o = c * 4;
            s[o + 0] ^= (byte)(k >> 24);
            s[o + 1] ^= (byte)(k >> 16);
            s[o + 2] ^= (byte)(k >> 8);
            s[o + 3] ^= (byte)k;
        }
    }

    private static void SubBytes(Span<byte> s)
    {
        for (int i = 0; i < 16; i++)
            s[i] = SBox[s[i]];
    }

    private static void InvSubBytes(Span<byte> s)
    {
        for (int i = 0; i < 16; i++)
            s[i] = InvSBox[s[i]];
    }

    private static void ShiftRows(Span<byte> s)
    {
        byte t = s[1]; s[1] = s[5]; s[5] = s[9]; s[9] = s[13]; s[13] = t;
        (s[2], s[10]) = (s[10], s[2]);
        (s[6], s[14]) = (s[14], s[6]);
        t = s[15]; s[15] = s[11]; s[11] = s[7]; s[7] = s[3]; s[3] = t;
    }

    private static void InvShiftRows(Span<byte> s)
    {
        byte t = s[13]; s[13] = s[9]; s[9] = s[5]; s[5] = s[1]; s[1] = t;
        (s[2], s[10]) = (s[10], s[2]);
        (s[6], s[14]) = (s[14], s[6]);
        t = s[3]; s[3] = s[7]; s[7] = s[11]; s[11] = s[15]; s[15] = t;
    }

    private static void MixColumns(Span<byte> s)
    {
        for (int c = 0; c < 16; c += 4)
        {
            byte s0 = s[c], s1 = s[c + 1], s2 = s[c + 2], s3 = s[c + 3];
            byte t = (byte)(s0 ^ s1 ^ s2 ^ s3);
            s[c + 0] = (byte)(s0 ^ t ^ XTime((byte)(s0 ^ s1)));
            s[c + 1] = (byte)(s1 ^ t ^ XTime((byte)(s1 ^ s2)));
            s[c + 2] = (byte)(s2 ^ t ^ XTime((byte)(s2 ^ s3)));
            s[c + 3] = (byte)(s3 ^ t ^ XTime((byte)(s3 ^ s0)));
        }
    }

    private static void InvMixColumns(Span<byte> s)
    {
        for (int c = 0; c < 16; c += 4)
        {
            byte u = XTime(XTime((byte)(s[c] ^ s[c + 2])));
            byte v = XTime(XTime((byte)(s[c + 1] ^ s[c + 3])));
            s[c + 0] ^= u;
            s[c + 1] ^= v;
            s[c + 2] ^= u;
            s[c + 3] ^= v;
        }
        MixColumns(s);
    }

    private static void EncryptBlockCore(ReadOnlySpan<uint> rk, int nr, ReadOnlySpan<byte> input16, Span<byte> output16)
    {
        Span<byte> s = stackalloc byte[16];
        input16.CopyTo(s);

        AddRoundKey(s, rk, 0);
        for (int r = 1; r < nr; r++)
        {
            SubBytes(s);
            ShiftRows(s);
            MixColumns(s);
            AddRoundKey(s, rk, r);
        }
        SubBytes(s);
        ShiftRows(s);
        AddRoundKey(s, rk, nr);

        s.CopyTo(output16);
        s.Clear();
    }

    private static void DecryptBlockCore(ReadOnlySpan<uint> rk, int nr, ReadOnlySpan<byte> input16, Span<byte> output16)
    {
        Span<byte> s = stackalloc byte[16];
        input16.CopyTo(s);

        AddRoundKey(s, rk, nr);
        for (int r = nr - 1; r >= 1; r--)
        {
            InvShiftRows(s);
            InvSubBytes(s);
            AddRoundKey(s, rk, r);
            InvMixColumns(s);
        }
        InvShiftRows(s);
        InvSubBytes(s);
        AddRoundKey(s, rk, 0);

        s.CopyTo(output16);
        s.Clear();
    }

    public static void EncryptBlock(ReadOnlySpan<byte> key, ReadOnlySpan<byte> plaintext16, Span<byte> ciphertext16)
    {
        if (plaintext16.Length != 16)
            throw new ArgumentException("Plaintext block must be 16 bytes.", nameof(plaintext16));
        if (ciphertext16.Length < 16)
            throw new ArgumentException("Ciphertext buffer must be at least 16 bytes.", nameof(ciphertext16));

        Span<uint> rk = stackalloc uint[60];
        try
        {
            int nr = ExpandKey(key, rk);
            EncryptBlockCore(rk, nr, plaintext16, ciphertext16[..16]);
        }
        finally
        {
            rk.Clear();
        }
    }

    public static void DecryptBlock(ReadOnlySpan<byte> key, ReadOnlySpan<byte> ciphertext16, Span<byte> plaintext16)
    {
        if (ciphertext16.Length != 16)
            throw new ArgumentException("Ciphertext block must be 16 bytes.", nameof(ciphertext16));
        if (plaintext16.Length < 16)
            throw new ArgumentException("Plaintext buffer must be at least 16 bytes.", nameof(plaintext16));

        Span<uint> rk = stackalloc uint[60];
        try
        {
            int nr = ExpandKey(key, rk);
            DecryptBlockCore(rk, nr, ciphertext16, plaintext16[..16]);
        }
        finally
        {
            rk.Clear();
        }
    }

    private static void Gf128Mul(ref ulong xHi, ref ulong xLo, ulong hHi, ulong hLo)
    {
        ulong zHi = 0, zLo = 0;
        ulong vHi = hHi, vLo = hLo;

        for (int i = 0; i < 64; i++)
        {
            ulong mask = 0UL - ((xHi >> (63 - i)) & 1UL);
            zHi ^= vHi & mask;
            zLo ^= vLo & mask;

            ulong lsbMask = 0UL - (vLo & 1UL);
            vLo = (vLo >> 1) | (vHi << 63);
            vHi = (vHi >> 1) ^ (0xE100000000000000UL & lsbMask);
        }

        for (int i = 0; i < 64; i++)
        {
            ulong mask = 0UL - ((xLo >> (63 - i)) & 1UL);
            zHi ^= vHi & mask;
            zLo ^= vLo & mask;

            ulong lsbMask = 0UL - (vLo & 1UL);
            vLo = (vLo >> 1) | (vHi << 63);
            vHi = (vHi >> 1) ^ (0xE100000000000000UL & lsbMask);
        }

        xHi = zHi;
        xLo = zLo;
    }

    private static void GhashFeed(ref ulong sHi, ref ulong sLo, ulong hHi, ulong hLo, ReadOnlySpan<byte> data)
    {
        int offset = 0;
        while (offset + 16 <= data.Length)
        {
            sHi ^= BinaryPrimitives.ReadUInt64BigEndian(data.Slice(offset, 8));
            sLo ^= BinaryPrimitives.ReadUInt64BigEndian(data.Slice(offset + 8, 8));
            Gf128Mul(ref sHi, ref sLo, hHi, hLo);
            offset += 16;
        }

        int rem = data.Length - offset;
        if (rem > 0)
        {
            Span<byte> last = stackalloc byte[16];
            data.Slice(offset).CopyTo(last);
            sHi ^= BinaryPrimitives.ReadUInt64BigEndian(last[..8]);
            sLo ^= BinaryPrimitives.ReadUInt64BigEndian(last[8..16]);
            Gf128Mul(ref sHi, ref sLo, hHi, hLo);
        }
    }

    private static void ComputeGcmTag(
        ReadOnlySpan<byte> h,
        ReadOnlySpan<byte> s0,
        ReadOnlySpan<byte> aad,
        ReadOnlySpan<byte> ciphertext,
        Span<byte> tag16)
    {
        ulong hHi = BinaryPrimitives.ReadUInt64BigEndian(h[..8]);
        ulong hLo = BinaryPrimitives.ReadUInt64BigEndian(h[8..16]);
        ulong sHi = 0, sLo = 0;

        GhashFeed(ref sHi, ref sLo, hHi, hLo, aad);
        GhashFeed(ref sHi, ref sLo, hHi, hLo, ciphertext);

        sHi ^= (ulong)aad.Length << 3;
        sLo ^= (ulong)ciphertext.Length << 3;
        Gf128Mul(ref sHi, ref sLo, hHi, hLo);

        sHi ^= BinaryPrimitives.ReadUInt64BigEndian(s0[..8]);
        sLo ^= BinaryPrimitives.ReadUInt64BigEndian(s0[8..16]);

        BinaryPrimitives.WriteUInt64BigEndian(tag16[..8], sHi);
        BinaryPrimitives.WriteUInt64BigEndian(tag16[8..16], sLo);
    }

    private static void Gctr(
        ReadOnlySpan<uint> rk,
        int nr,
        ReadOnlySpan<byte> j0,
        ReadOnlySpan<byte> input,
        Span<byte> output)
    {
        Span<byte> ctrBlock = stackalloc byte[16];
        Span<byte> keystream = stackalloc byte[16];
        j0.CopyTo(ctrBlock);
        uint ctr = BinaryPrimitives.ReadUInt32BigEndian(j0[12..16]);

        int offset = 0;
        while (offset < input.Length)
        {
            ctr++;
            BinaryPrimitives.WriteUInt32BigEndian(ctrBlock[12..16], ctr);
            EncryptBlockCore(rk, nr, ctrBlock, keystream);

            int take = Math.Min(16, input.Length - offset);
            for (int i = 0; i < take; i++)
                output[offset + i] = (byte)(input[offset + i] ^ keystream[i]);
            offset += take;
        }

        ctrBlock.Clear();
        keystream.Clear();
    }

    public static void AesGcmEncrypt(
        ReadOnlySpan<byte> key,
        ReadOnlySpan<byte> nonce12,
        ReadOnlySpan<byte> plaintext,
        ReadOnlySpan<byte> aad,
        Span<byte> ciphertext,
        Span<byte> tag16)
    {
        if (nonce12.Length != 12)
            throw new ArgumentException("AES-GCM nonce must be 12 bytes.", nameof(nonce12));
        if (tag16.Length != 16)
            throw new ArgumentException("AES-GCM tag must be 16 bytes.", nameof(tag16));
        if (ciphertext.Length != plaintext.Length)
            throw new ArgumentException("Ciphertext length must equal plaintext length.", nameof(ciphertext));

        Span<uint> rk = stackalloc uint[60];
        Span<byte> h = stackalloc byte[16];
        Span<byte> j0 = stackalloc byte[16];
        Span<byte> s0 = stackalloc byte[16];
        try
        {
            int nr = ExpandKey(key, rk);
            EncryptBlockCore(rk, nr, h, h);

            nonce12.CopyTo(j0);
            BinaryPrimitives.WriteUInt32BigEndian(j0[12..16], 1);
            EncryptBlockCore(rk, nr, j0, s0);

            Gctr(rk, nr, j0, plaintext, ciphertext);
            ComputeGcmTag(h, s0, aad, ciphertext, tag16);
        }
        finally
        {
            rk.Clear();
            h.Clear();
            j0.Clear();
            s0.Clear();
        }
    }

    public static bool AesGcmDecrypt(
        ReadOnlySpan<byte> key,
        ReadOnlySpan<byte> nonce12,
        ReadOnlySpan<byte> ciphertext,
        ReadOnlySpan<byte> aad,
        ReadOnlySpan<byte> tag16,
        Span<byte> plaintext)
    {
        if (nonce12.Length != 12)
            throw new ArgumentException("AES-GCM nonce must be 12 bytes.", nameof(nonce12));
        if (tag16.Length != 16)
            throw new ArgumentException("AES-GCM tag must be 16 bytes.", nameof(tag16));
        if (plaintext.Length != ciphertext.Length)
            throw new ArgumentException("Plaintext length must equal ciphertext length.", nameof(plaintext));

        Span<uint> rk = stackalloc uint[60];
        Span<byte> h = stackalloc byte[16];
        Span<byte> j0 = stackalloc byte[16];
        Span<byte> s0 = stackalloc byte[16];
        Span<byte> expectedTag = stackalloc byte[16];
        try
        {
            int nr = ExpandKey(key, rk);
            EncryptBlockCore(rk, nr, h, h);

            nonce12.CopyTo(j0);
            BinaryPrimitives.WriteUInt32BigEndian(j0[12..16], 1);
            EncryptBlockCore(rk, nr, j0, s0);

            ComputeGcmTag(h, s0, aad, ciphertext, expectedTag);
            if (!ConstantTime.Equals(expectedTag, tag16))
            {
                ConstantTime.ZeroMemory(plaintext);
                return false;
            }

            Gctr(rk, nr, j0, ciphertext, plaintext);
            return true;
        }
        finally
        {
            rk.Clear();
            h.Clear();
            j0.Clear();
            s0.Clear();
            expectedTag.Clear();
        }
    }

    public static byte[] AesCbcEncrypt(
        ReadOnlySpan<byte> key,
        ReadOnlySpan<byte> iv16,
        ReadOnlySpan<byte> plaintext,
        bool pkcs7Padding = true)
    {
        if (iv16.Length != 16)
            throw new ArgumentException("AES-CBC IV must be 16 bytes.", nameof(iv16));
        if (!pkcs7Padding && plaintext.Length % 16 != 0)
            throw new ArgumentException("Unpadded AES-CBC plaintext must be a multiple of 16 bytes.", nameof(plaintext));

        int padLen = pkcs7Padding ? 16 - (plaintext.Length % 16) : 0;
        var output = new byte[plaintext.Length + padLen];
        Span<uint> rk = stackalloc uint[60];
        Span<byte> chain = stackalloc byte[16];
        Span<byte> block = stackalloc byte[16];
        try
        {
            int nr = ExpandKey(key, rk);
            iv16.CopyTo(chain);

            int fullLen = (plaintext.Length / 16) * 16;
            for (int offset = 0; offset < fullLen; offset += 16)
            {
                for (int i = 0; i < 16; i++)
                    block[i] = (byte)(plaintext[offset + i] ^ chain[i]);
                EncryptBlockCore(rk, nr, block, chain);
                chain.CopyTo(output.AsSpan(offset, 16));
            }

            if (pkcs7Padding)
            {
                int rem = plaintext.Length - fullLen;
                for (int i = 0; i < rem; i++)
                    block[i] = (byte)(plaintext[fullLen + i] ^ chain[i]);
                for (int i = rem; i < 16; i++)
                    block[i] = (byte)(padLen ^ chain[i]);
                EncryptBlockCore(rk, nr, block, output.AsSpan(fullLen, 16));
            }

            return output;
        }
        finally
        {
            rk.Clear();
            chain.Clear();
            block.Clear();
        }
    }

    public static byte[] AesCbcDecrypt(
        ReadOnlySpan<byte> key,
        ReadOnlySpan<byte> iv16,
        ReadOnlySpan<byte> ciphertext,
        bool pkcs7Padding = true)
    {
        if (iv16.Length != 16)
            throw new ArgumentException("AES-CBC IV must be 16 bytes.", nameof(iv16));
        if (ciphertext.Length % 16 != 0)
            throw new ArgumentException("AES-CBC ciphertext must be a multiple of 16 bytes.", nameof(ciphertext));
        if (ciphertext.IsEmpty)
        {
            if (pkcs7Padding)
                throw new CryptographicException("PKCS#7 padded ciphertext cannot be empty.");
            return Array.Empty<byte>();
        }

        var decrypted = new byte[ciphertext.Length];
        Span<uint> rk = stackalloc uint[60];
        Span<byte> block = stackalloc byte[16];
        try
        {
            int nr = ExpandKey(key, rk);
            ReadOnlySpan<byte> prev = iv16;

            for (int offset = 0; offset < ciphertext.Length; offset += 16)
            {
                ReadOnlySpan<byte> ctBlock = ciphertext.Slice(offset, 16);
                DecryptBlockCore(rk, nr, ctBlock, block);
                for (int i = 0; i < 16; i++)
                    decrypted[offset + i] = (byte)(block[i] ^ prev[i]);
                prev = ctBlock;
            }

            if (!pkcs7Padding)
                return decrypted;

            int pad = decrypted[^1];
            int bad = ((pad - 1) >> 31) | ((16 - pad) >> 31);
            for (int i = 0; i < 16; i++)
            {
                int inPad = (i - pad) >> 31;
                bad |= inPad & (decrypted[decrypted.Length - 1 - i] ^ pad);
            }

            if (bad != 0)
                throw new CryptographicException("Invalid PKCS#7 padding.");

            return decrypted.AsSpan(0, decrypted.Length - pad).ToArray();
        }
        catch (CryptographicException)
        {
            ConstantTime.ZeroMemory(decrypted);
            throw;
        }
        finally
        {
            rk.Clear();
            block.Clear();
            if (pkcs7Padding)
                ConstantTime.ZeroMemory(decrypted);
        }
    }
}

/// <summary>
/// Pure managed RFC 8439 ChaCha20 and Poly1305 AEAD primitives.
/// </summary>
public static class ChaCha20Poly1305Primitives
{
    private static void QuarterRound(Span<uint> s, int a, int b, int c, int d)
    {
        s[a] += s[b]; s[d] = BitOperations.RotateLeft(s[d] ^ s[a], 16);
        s[c] += s[d]; s[b] = BitOperations.RotateLeft(s[b] ^ s[c], 12);
        s[a] += s[b]; s[d] = BitOperations.RotateLeft(s[d] ^ s[a], 8);
        s[c] += s[d]; s[b] = BitOperations.RotateLeft(s[b] ^ s[c], 7);
    }

    public static void ChaCha20Block(
        ReadOnlySpan<byte> key32,
        uint counter,
        ReadOnlySpan<byte> nonce12,
        Span<byte> output64)
    {
        if (key32.Length != 32)
            throw new ArgumentException("ChaCha20 key must be 32 bytes.", nameof(key32));
        if (nonce12.Length != 12)
            throw new ArgumentException("ChaCha20 nonce must be 12 bytes.", nameof(nonce12));
        if (output64.Length < 64)
            throw new ArgumentException("ChaCha20 output buffer must be at least 64 bytes.", nameof(output64));

        Span<uint> init = stackalloc uint[16];
        Span<uint> state = stackalloc uint[16];
        try
        {
            init[0] = 0x61707865u;
            init[1] = 0x3320646Eu;
            init[2] = 0x79622D32u;
            init[3] = 0x6B206574u;
            for (int i = 0; i < 8; i++)
                init[4 + i] = BinaryPrimitives.ReadUInt32LittleEndian(key32.Slice(i * 4, 4));
            init[12] = counter;
            init[13] = BinaryPrimitives.ReadUInt32LittleEndian(nonce12.Slice(0, 4));
            init[14] = BinaryPrimitives.ReadUInt32LittleEndian(nonce12.Slice(4, 4));
            init[15] = BinaryPrimitives.ReadUInt32LittleEndian(nonce12.Slice(8, 4));

            init.CopyTo(state);
            for (int i = 0; i < 10; i++)
            {
                QuarterRound(state, 0, 4, 8, 12);
                QuarterRound(state, 1, 5, 9, 13);
                QuarterRound(state, 2, 6, 10, 14);
                QuarterRound(state, 3, 7, 11, 15);
                QuarterRound(state, 0, 5, 10, 15);
                QuarterRound(state, 1, 6, 11, 12);
                QuarterRound(state, 2, 7, 8, 13);
                QuarterRound(state, 3, 4, 9, 14);
            }

            for (int i = 0; i < 16; i++)
                BinaryPrimitives.WriteUInt32LittleEndian(output64.Slice(i * 4, 4), state[i] + init[i]);
        }
        finally
        {
            init.Clear();
            state.Clear();
        }
    }

    public static void ChaCha20Xor(
        ReadOnlySpan<byte> key32,
        uint counter,
        ReadOnlySpan<byte> nonce12,
        ReadOnlySpan<byte> input,
        Span<byte> output)
    {
        if (output.Length != input.Length)
            throw new ArgumentException("Output length must equal input length.", nameof(output));

        Span<byte> keystream = stackalloc byte[64];
        try
        {
            int offset = 0;
            while (offset < input.Length)
            {
                ChaCha20Block(key32, counter, nonce12, keystream);
                counter++;
                int take = Math.Min(64, input.Length - offset);
                for (int i = 0; i < take; i++)
                    output[offset + i] = (byte)(input[offset + i] ^ keystream[i]);
                offset += take;
            }
        }
        finally
        {
            keystream.Clear();
        }
    }

    private static void Poly1305UpdateBlock(
        ReadOnlySpan<byte> block16,
        ulong r0, ulong r1, ulong r2, ulong r3, ulong r4,
        ulong s1, ulong s2, ulong s3, ulong s4,
        ref ulong h0, ref ulong h1, ref ulong h2, ref ulong h3, ref ulong h4)
    {
        uint w0 = BinaryPrimitives.ReadUInt32LittleEndian(block16.Slice(0, 4));
        uint w1 = BinaryPrimitives.ReadUInt32LittleEndian(block16.Slice(4, 4));
        uint w2 = BinaryPrimitives.ReadUInt32LittleEndian(block16.Slice(8, 4));
        uint w3 = BinaryPrimitives.ReadUInt32LittleEndian(block16.Slice(12, 4));

        h0 += w0 & 0x3FFFFFFUL;
        h1 += ((w0 >> 26) | (w1 << 6)) & 0x3FFFFFFUL;
        h2 += ((w1 >> 20) | (w2 << 12)) & 0x3FFFFFFUL;
        h3 += ((w2 >> 14) | (w3 << 18)) & 0x3FFFFFFUL;
        h4 += (w3 >> 8) | (1UL << 24);

        ulong d0 = h0 * r0 + h1 * s4 + h2 * s3 + h3 * s2 + h4 * s1;
        ulong d1 = h0 * r1 + h1 * r0 + h2 * s4 + h3 * s3 + h4 * s2;
        ulong d2 = h0 * r2 + h1 * r1 + h2 * r0 + h3 * s4 + h4 * s3;
        ulong d3 = h0 * r3 + h1 * r2 + h2 * r1 + h3 * r0 + h4 * s4;
        ulong d4 = h0 * r4 + h1 * r3 + h2 * r2 + h3 * r1 + h4 * r0;

        ulong c = d0 >> 26; h0 = d0 & 0x3FFFFFFUL; d1 += c;
        c = d1 >> 26; h1 = d1 & 0x3FFFFFFUL; d2 += c;
        c = d2 >> 26; h2 = d2 & 0x3FFFFFFUL; d3 += c;
        c = d3 >> 26; h3 = d3 & 0x3FFFFFFUL; d4 += c;
        c = d4 >> 26; h4 = d4 & 0x3FFFFFFUL; h0 += c * 5UL;
        c = h0 >> 26; h0 &= 0x3FFFFFFUL; h1 += c;
    }

    private static void ComputePoly1305AeadTag(
        ReadOnlySpan<byte> otk32,
        ReadOnlySpan<byte> aad,
        ReadOnlySpan<byte> ciphertext,
        Span<byte> tag16)
    {
        uint k0 = BinaryPrimitives.ReadUInt32LittleEndian(otk32.Slice(0, 4));
        uint k1 = BinaryPrimitives.ReadUInt32LittleEndian(otk32.Slice(4, 4));
        uint k2 = BinaryPrimitives.ReadUInt32LittleEndian(otk32.Slice(8, 4));
        uint k3 = BinaryPrimitives.ReadUInt32LittleEndian(otk32.Slice(12, 4));

        ulong r0 = k0 & 0x3FFFFFFUL;
        ulong r1 = ((k0 >> 26) | (k1 << 6)) & 0x3FFFF03UL;
        ulong r2 = ((k1 >> 20) | (k2 << 12)) & 0x3FFC0FFUL;
        ulong r3 = ((k2 >> 14) | (k3 << 18)) & 0x3F03FFFUL;
        ulong r4 = (k3 >> 8) & 0x00FFFFFUL;

        ulong s1 = r1 * 5UL, s2 = r2 * 5UL, s3 = r3 * 5UL, s4 = r4 * 5UL;
        ulong h0 = 0, h1 = 0, h2 = 0, h3 = 0, h4 = 0;

        Span<byte> padded = stackalloc byte[16];

        void FeedPadded16(ReadOnlySpan<byte> data, Span<byte> padBuf)
        {
            int offset = 0;
            while (offset + 16 <= data.Length)
            {
                Poly1305UpdateBlock(data.Slice(offset, 16), r0, r1, r2, r3, r4, s1, s2, s3, s4, ref h0, ref h1, ref h2, ref h3, ref h4);
                offset += 16;
            }
            int rem = data.Length - offset;
            if (rem > 0)
            {
                padBuf.Clear();
                data.Slice(offset).CopyTo(padBuf);
                Poly1305UpdateBlock(padBuf, r0, r1, r2, r3, r4, s1, s2, s3, s4, ref h0, ref h1, ref h2, ref h3, ref h4);
            }
        }

        FeedPadded16(aad, padded);
        FeedPadded16(ciphertext, padded);

        BinaryPrimitives.WriteUInt64LittleEndian(padded[..8], (ulong)aad.Length);
        BinaryPrimitives.WriteUInt64LittleEndian(padded[8..16], (ulong)ciphertext.Length);
        Poly1305UpdateBlock(padded, r0, r1, r2, r3, r4, s1, s2, s3, s4, ref h0, ref h1, ref h2, ref h3, ref h4);
        padded.Clear();

        // Full carry propagation
        ulong c = h1 >> 26; h1 &= 0x3FFFFFFUL; h2 += c;
        c = h2 >> 26; h2 &= 0x3FFFFFFUL; h3 += c;
        c = h3 >> 26; h3 &= 0x3FFFFFFUL; h4 += c;
        c = h4 >> 26; h4 &= 0x3FFFFFFUL; h0 += c * 5UL;
        c = h0 >> 26; h0 &= 0x3FFFFFFUL; h1 += c;
        c = h1 >> 26; h1 &= 0x3FFFFFFUL; h2 += c;
        c = h2 >> 26; h2 &= 0x3FFFFFFUL; h3 += c;
        c = h3 >> 26; h3 &= 0x3FFFFFFUL; h4 += c;

        // Constant-time conditional subtract (2^130 - 5) via compute h + 5 - 2^130
        ulong g0 = h0 + 5UL; c = g0 >> 26; g0 &= 0x3FFFFFFUL;
        ulong g1 = h1 + c; c = g1 >> 26; g1 &= 0x3FFFFFFUL;
        ulong g2 = h2 + c; c = g2 >> 26; g2 &= 0x3FFFFFFUL;
        ulong g3 = h3 + c; c = g3 >> 26; g3 &= 0x3FFFFFFUL;
        ulong g4 = unchecked(h4 + c - (1UL << 26));

        // If g4 bit 63 == 0, h + 5 >= 2^130 -> mask = all 1s; else mask = 0.
        ulong mask = (g4 >> 63) - 1UL;
        h0 = (h0 & ~mask) | (g0 & mask);
        h1 = (h1 & ~mask) | (g1 & mask);
        h2 = (h2 & ~mask) | (g2 & mask);
        h3 = (h3 & ~mask) | (g3 & mask);
        h4 = (h4 & ~mask) | (g4 & mask);

        uint f0 = (uint)(h0 | (h1 << 26));
        uint f1 = (uint)((h1 >> 6) | (h2 << 20));
        uint f2 = (uint)((h2 >> 12) | (h3 << 14));
        uint f3 = (uint)((h3 >> 18) | (h4 << 8));

        ulong t0 = (ulong)f0 + BinaryPrimitives.ReadUInt32LittleEndian(otk32.Slice(16, 4));
        ulong t1 = (ulong)f1 + BinaryPrimitives.ReadUInt32LittleEndian(otk32.Slice(20, 4)) + (t0 >> 32);
        ulong t2 = (ulong)f2 + BinaryPrimitives.ReadUInt32LittleEndian(otk32.Slice(24, 4)) + (t1 >> 32);
        ulong t3 = (ulong)f3 + BinaryPrimitives.ReadUInt32LittleEndian(otk32.Slice(28, 4)) + (t2 >> 32);

        BinaryPrimitives.WriteUInt32LittleEndian(tag16.Slice(0, 4), (uint)t0);
        BinaryPrimitives.WriteUInt32LittleEndian(tag16.Slice(4, 4), (uint)t1);
        BinaryPrimitives.WriteUInt32LittleEndian(tag16.Slice(8, 4), (uint)t2);
        BinaryPrimitives.WriteUInt32LittleEndian(tag16.Slice(12, 4), (uint)t3);
    }

    public static void Encrypt(
        ReadOnlySpan<byte> key32,
        ReadOnlySpan<byte> nonce12,
        ReadOnlySpan<byte> plaintext,
        ReadOnlySpan<byte> aad,
        Span<byte> ciphertext,
        Span<byte> tag16)
    {
        if (key32.Length != 32)
            throw new ArgumentException("ChaCha20-Poly1305 key must be 32 bytes.", nameof(key32));
        if (nonce12.Length != 12)
            throw new ArgumentException("ChaCha20-Poly1305 nonce must be 12 bytes.", nameof(nonce12));
        if (ciphertext.Length != plaintext.Length)
            throw new ArgumentException("Ciphertext length must equal plaintext length.", nameof(ciphertext));
        if (tag16.Length != 16)
            throw new ArgumentException("ChaCha20-Poly1305 tag must be 16 bytes.", nameof(tag16));

        Span<byte> polyBlock = stackalloc byte[64];
        try
        {
            ChaCha20Block(key32, 0, nonce12, polyBlock);
            ChaCha20Xor(key32, 1, nonce12, plaintext, ciphertext);
            ComputePoly1305AeadTag(polyBlock[..32], aad, ciphertext, tag16);
        }
        finally
        {
            polyBlock.Clear();
        }
    }

    public static bool Decrypt(
        ReadOnlySpan<byte> key32,
        ReadOnlySpan<byte> nonce12,
        ReadOnlySpan<byte> ciphertext,
        ReadOnlySpan<byte> aad,
        ReadOnlySpan<byte> tag16,
        Span<byte> plaintext)
    {
        if (key32.Length != 32)
            throw new ArgumentException("ChaCha20-Poly1305 key must be 32 bytes.", nameof(key32));
        if (nonce12.Length != 12)
            throw new ArgumentException("ChaCha20-Poly1305 nonce must be 12 bytes.", nameof(nonce12));
        if (plaintext.Length != ciphertext.Length)
            throw new ArgumentException("Plaintext length must equal ciphertext length.", nameof(plaintext));
        if (tag16.Length != 16)
            throw new ArgumentException("ChaCha20-Poly1305 tag must be 16 bytes.", nameof(tag16));

        Span<byte> polyBlock = stackalloc byte[64];
        Span<byte> expectedTag = stackalloc byte[16];
        try
        {
            ChaCha20Block(key32, 0, nonce12, polyBlock);
            ComputePoly1305AeadTag(polyBlock[..32], aad, ciphertext, expectedTag);

            if (!ConstantTime.Equals(expectedTag, tag16))
            {
                ConstantTime.ZeroMemory(plaintext);
                return false;
            }

            ChaCha20Xor(key32, 1, nonce12, ciphertext, plaintext);
            return true;
        }
        finally
        {
            polyBlock.Clear();
            expectedTag.Clear();
        }
    }
}
