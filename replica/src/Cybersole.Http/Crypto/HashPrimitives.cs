using System;
using System.Buffers.Binary;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;

namespace Cybersole.Http.Crypto;

/// <summary>
/// Constant-time comparison and memory sanitization helpers.
/// </summary>
public static class ConstantTime
{
    public static bool Equals(ReadOnlySpan<byte> a, ReadOnlySpan<byte> b)
    {
        if (a.Length != b.Length)
            return false;
        return CryptographicOperations.FixedTimeEquals(a, b);
    }

    public static void ZeroMemory(Span<byte> buffer)
    {
        CryptographicOperations.ZeroMemory(buffer);
    }
}

public enum HashAlgorithmKind
{
    Sha1,
    Sha256,
    Sha384,
    Sha512
}

/// <summary>
/// Streaming squeeze reader for FIPS 202 extendable-output functions (SHAKE128/SHAKE256).
/// </summary>
public sealed class XofReader : IDisposable
{
    private readonly ulong[] _state;
    private readonly int _rateBytes;
    private int _pos;
    private bool _disposed;

    internal XofReader(ulong[] state, int rateBytes)
    {
        _state = state;
        _rateBytes = rateBytes;
        _pos = 0;
    }

    public void Squeeze(Span<byte> output)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        int offset = 0;
        while (offset < output.Length)
        {
            if (_pos == _rateBytes)
            {
                HashPrimitives.KeccakF1600(_state);
                _pos = 0;
            }

            int take = Math.Min(output.Length - offset, _rateBytes - _pos);
            for (int i = 0; i < take; i++)
            {
                int p = _pos + i;
                output[offset + i] = (byte)(_state[p >> 3] >> ((p & 7) * 8));
            }

            _pos += take;
            offset += take;
        }
    }

    public byte[] Squeeze(int length)
    {
        if (length < 0)
            throw new ArgumentOutOfRangeException(nameof(length));
        if (length == 0)
            return Array.Empty<byte>();
        var result = new byte[length];
        Squeeze(result);
        return result;
    }

    public void Dispose()
    {
        if (!_disposed)
        {
            Array.Clear(_state);
            _disposed = true;
        }
    }
}

/// <summary>
/// Pure managed hash primitives (SHA-1/2, MD5, FIPS 202 SHA-3/SHAKE via Keccak-f[1600]),
/// HMAC, HKDF (RFC 5869 / RFC 8446), and TLS 1.2 PRF (RFC 5246).
/// </summary>
public static class HashPrimitives
{
    private static readonly int[] PiLane =
    {
        10, 7, 11, 17, 18, 3, 5, 16, 8, 21, 24, 4,
        15, 23, 19, 13, 12, 2, 20, 14, 22, 9, 6, 1
    };

    private static readonly int[] RhoOffsets =
    {
        1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 2, 14,
        27, 41, 56, 8, 25, 43, 62, 18, 39, 61, 20, 44
    };

    private static readonly ulong[] RoundConstants = BuildRoundConstants();

    private static ulong[] BuildRoundConstants()
    {
        var rc = new ulong[24];
        byte r = 0x01;
        for (int round = 0; round < 24; round++)
        {
            ulong val = 0;
            for (int j = 0; j < 7; j++)
            {
                if ((r & 1) != 0)
                    val |= 1UL << ((1 << j) - 1);
                bool hi = (r & 0x80) != 0;
                r <<= 1;
                if (hi)
                    r ^= 0x71;
            }
            rc[round] = val;
        }
        return rc;
    }

    public static int DigestLength(HashAlgorithmKind alg) => alg switch
    {
        HashAlgorithmKind.Sha1 => 20,
        HashAlgorithmKind.Sha256 => 32,
        HashAlgorithmKind.Sha384 => 48,
        HashAlgorithmKind.Sha512 => 64,
        _ => throw new ArgumentOutOfRangeException(nameof(alg), alg, "Unsupported hash algorithm.")
    };

    public static HashAlgorithmName ToBclName(HashAlgorithmKind alg) => alg switch
    {
        HashAlgorithmKind.Sha1 => HashAlgorithmName.SHA1,
        HashAlgorithmKind.Sha256 => HashAlgorithmName.SHA256,
        HashAlgorithmKind.Sha384 => HashAlgorithmName.SHA384,
        HashAlgorithmKind.Sha512 => HashAlgorithmName.SHA512,
        _ => throw new ArgumentOutOfRangeException(nameof(alg), alg, "Unsupported hash algorithm.")
    };

    public static byte[] Hash(HashAlgorithmKind alg, ReadOnlySpan<byte> data) => alg switch
    {
        HashAlgorithmKind.Sha1 => SHA1.HashData(data),
        HashAlgorithmKind.Sha256 => SHA256.HashData(data),
        HashAlgorithmKind.Sha384 => SHA384.HashData(data),
        HashAlgorithmKind.Sha512 => SHA512.HashData(data),
        _ => throw new ArgumentOutOfRangeException(nameof(alg), alg, "Unsupported hash algorithm.")
    };

    public static byte[] Sha1(ReadOnlySpan<byte> data) => SHA1.HashData(data);

    public static byte[] Sha256(ReadOnlySpan<byte> data) => SHA256.HashData(data);

    public static void Sha256(ReadOnlySpan<byte> data, Span<byte> destination)
    {
        if (destination.Length < 32)
            throw new ArgumentException("Destination buffer must be at least 32 bytes.", nameof(destination));
        SHA256.HashData(data, destination[..32]);
    }

    public static byte[] Sha384(ReadOnlySpan<byte> data) => SHA384.HashData(data);

    public static void Sha384(ReadOnlySpan<byte> data, Span<byte> destination)
    {
        if (destination.Length < 48)
            throw new ArgumentException("Destination buffer must be at least 48 bytes.", nameof(destination));
        SHA384.HashData(data, destination[..48]);
    }

    public static byte[] Sha512(ReadOnlySpan<byte> data) => SHA512.HashData(data);

    public static void Sha512(ReadOnlySpan<byte> data, Span<byte> destination)
    {
        if (destination.Length < 64)
            throw new ArgumentException("Destination buffer must be at least 64 bytes.", nameof(destination));
        SHA512.HashData(data, destination[..64]);
    }

    public static byte[] Md5(ReadOnlySpan<byte> data) => MD5.HashData(data);

    public static byte[] Sha3_256(ReadOnlySpan<byte> data)
    {
        var output = new byte[32];
        Sha3_256(data, output);
        return output;
    }

    public static void Sha3_256(ReadOnlySpan<byte> data, Span<byte> destination)
    {
        if (destination.Length < 32)
            throw new ArgumentException("Destination buffer must be at least 32 bytes.", nameof(destination));
        KeccakOneShot(data, rateBytes: 136, domainSep: 0x06, destination[..32]);
    }

    public static byte[] Sha3_512(ReadOnlySpan<byte> data)
    {
        var output = new byte[64];
        Sha3_512(data, output);
        return output;
    }

    public static void Sha3_512(ReadOnlySpan<byte> data, Span<byte> destination)
    {
        if (destination.Length < 64)
            throw new ArgumentException("Destination buffer must be at least 64 bytes.", nameof(destination));
        KeccakOneShot(data, rateBytes: 72, domainSep: 0x06, destination[..64]);
    }

    public static void Shake128(ReadOnlySpan<byte> input, Span<byte> output)
    {
        if (output.IsEmpty)
            return;
        KeccakOneShot(input, rateBytes: 168, domainSep: 0x1F, output);
    }

    public static void Shake256(ReadOnlySpan<byte> input, Span<byte> output)
    {
        if (output.IsEmpty)
            return;
        KeccakOneShot(input, rateBytes: 136, domainSep: 0x1F, output);
    }

    public static XofReader CreateShake128Reader(ReadOnlySpan<byte> input)
    {
        var state = new ulong[25];
        AbsorbAndFinalize(state, input, rateBytes: 168, domainSep: 0x1F);
        return new XofReader(state, rateBytes: 168);
    }

    public static XofReader CreateShake256Reader(ReadOnlySpan<byte> input)
    {
        var state = new ulong[25];
        AbsorbAndFinalize(state, input, rateBytes: 136, domainSep: 0x1F);
        return new XofReader(state, rateBytes: 136);
    }

    private static void KeccakOneShot(ReadOnlySpan<byte> input, int rateBytes, byte domainSep, Span<byte> output)
    {
        Span<ulong> state = stackalloc ulong[25];
        AbsorbAndFinalize(state, input, rateBytes, domainSep);

        int pos = 0;
        int offset = 0;
        while (offset < output.Length)
        {
            if (pos == rateBytes)
            {
                KeccakF1600(state);
                pos = 0;
            }

            int take = Math.Min(output.Length - offset, rateBytes - pos);
            for (int i = 0; i < take; i++)
            {
                int p = pos + i;
                output[offset + i] = (byte)(state[p >> 3] >> ((p & 7) * 8));
            }

            pos += take;
            offset += take;
        }

        state.Clear();
    }

    private static void AbsorbAndFinalize(Span<ulong> state, ReadOnlySpan<byte> input, int rateBytes, byte domainSep)
    {
        int rateLanes = rateBytes >> 3;
        while (input.Length >= rateBytes)
        {
            for (int i = 0; i < rateLanes; i++)
                state[i] ^= BinaryPrimitives.ReadUInt64LittleEndian(input.Slice(i * 8, 8));
            KeccakF1600(state);
            input = input.Slice(rateBytes);
        }

        for (int i = 0; i < input.Length; i++)
            state[i >> 3] ^= (ulong)input[i] << ((i & 7) * 8);

        int pos = input.Length;
        state[pos >> 3] ^= (ulong)domainSep << ((pos & 7) * 8);
        state[(rateBytes - 1) >> 3] ^= 0x80UL << (((rateBytes - 1) & 7) * 8);
        KeccakF1600(state);
    }

    internal static void KeccakF1600(Span<ulong> state)
    {
        Span<ulong> c = stackalloc ulong[5];
        Span<ulong> d = stackalloc ulong[5];

        for (int round = 0; round < 24; round++)
        {
            // Theta
            for (int x = 0; x < 5; x++)
                c[x] = state[x] ^ state[x + 5] ^ state[x + 10] ^ state[x + 15] ^ state[x + 20];

            for (int x = 0; x < 5; x++)
                d[x] = c[(x + 4) % 5] ^ BitOperations.RotateLeft(c[(x + 1) % 5], 1);

            for (int y = 0; y < 25; y += 5)
            {
                state[y + 0] ^= d[0];
                state[y + 1] ^= d[1];
                state[y + 2] ^= d[2];
                state[y + 3] ^= d[3];
                state[y + 4] ^= d[4];
            }

            // Rho and Pi
            ulong t = state[1];
            for (int i = 0; i < 24; i++)
            {
                int j = PiLane[i];
                ulong temp = state[j];
                state[j] = BitOperations.RotateLeft(t, RhoOffsets[i]);
                t = temp;
            }

            // Chi
            for (int y = 0; y < 25; y += 5)
            {
                ulong b0 = state[y + 0];
                ulong b1 = state[y + 1];
                ulong b2 = state[y + 2];
                ulong b3 = state[y + 3];
                ulong b4 = state[y + 4];
                state[y + 0] = b0 ^ ((~b1) & b2);
                state[y + 1] = b1 ^ ((~b2) & b3);
                state[y + 2] = b2 ^ ((~b3) & b4);
                state[y + 3] = b3 ^ ((~b4) & b0);
                state[y + 4] = b4 ^ ((~b0) & b1);
            }

            // Iota
            state[0] ^= RoundConstants[round];
        }
    }

    public static byte[] Hmac(HashAlgorithmKind alg, ReadOnlySpan<byte> key, ReadOnlySpan<byte> data) => alg switch
    {
        HashAlgorithmKind.Sha1 => HMACSHA1.HashData(key, data),
        HashAlgorithmKind.Sha256 => HMACSHA256.HashData(key, data),
        HashAlgorithmKind.Sha384 => HMACSHA384.HashData(key, data),
        HashAlgorithmKind.Sha512 => HMACSHA512.HashData(key, data),
        _ => throw new ArgumentOutOfRangeException(nameof(alg), alg, "Unsupported hash algorithm.")
    };

    private static void HmacTo(HashAlgorithmKind alg, ReadOnlySpan<byte> key, ReadOnlySpan<byte> data, Span<byte> destination)
    {
        switch (alg)
        {
            case HashAlgorithmKind.Sha1:
                HMACSHA1.HashData(key, data, destination);
                break;
            case HashAlgorithmKind.Sha256:
                HMACSHA256.HashData(key, data, destination);
                break;
            case HashAlgorithmKind.Sha384:
                HMACSHA384.HashData(key, data, destination);
                break;
            case HashAlgorithmKind.Sha512:
                HMACSHA512.HashData(key, data, destination);
                break;
            default:
                throw new ArgumentOutOfRangeException(nameof(alg), alg, "Unsupported hash algorithm.");
        }
    }

    public static byte[] HmacSha256(ReadOnlySpan<byte> key, ReadOnlySpan<byte> data) =>
        HMACSHA256.HashData(key, data);

    public static byte[] HmacSha384(ReadOnlySpan<byte> key, ReadOnlySpan<byte> data) =>
        HMACSHA384.HashData(key, data);

    public static byte[] HmacSha512(ReadOnlySpan<byte> key, ReadOnlySpan<byte> data) =>
        HMACSHA512.HashData(key, data);

    public static byte[] HkdfExtract(HashAlgorithmKind alg, ReadOnlySpan<byte> salt, ReadOnlySpan<byte> ikm)
    {
        if (salt.IsEmpty)
        {
            Span<byte> zeroSalt = stackalloc byte[DigestLength(alg)];
            zeroSalt.Clear();
            return Hmac(alg, zeroSalt, ikm);
        }
        return Hmac(alg, salt, ikm);
    }

    public static byte[] HkdfExpand(HashAlgorithmKind alg, ReadOnlySpan<byte> prk, ReadOnlySpan<byte> info, int length)
    {
        int hashLen = DigestLength(alg);
        if (length < 0 || length > 255 * hashLen)
            throw new ArgumentOutOfRangeException(nameof(length), "HKDF output length must be between 0 and 255 * HashLen.");
        if (length == 0)
            return Array.Empty<byte>();

        var okm = new byte[length];
        var input = new byte[hashLen + info.Length + 1];
        var block = new byte[hashLen];
        try
        {
            info.CopyTo(input.AsSpan(hashLen));
            int offset = 0;
            byte counter = 1;
            while (offset < length)
            {
                input[^1] = counter;
                ReadOnlySpan<byte> msg = counter == 1
                    ? input.AsSpan(hashLen, info.Length + 1)
                    : input.AsSpan();
                HmacTo(alg, prk, msg, block);

                int take = Math.Min(hashLen, length - offset);
                block.AsSpan(0, take).CopyTo(okm.AsSpan(offset));
                block.AsSpan().CopyTo(input.AsSpan(0, hashLen));
                offset += take;
                counter++;
            }
            return okm;
        }
        finally
        {
            ConstantTime.ZeroMemory(input);
            ConstantTime.ZeroMemory(block);
        }
    }

    public static byte[] HkdfExpandLabel(
        HashAlgorithmKind alg,
        ReadOnlySpan<byte> secret,
        string label,
        ReadOnlySpan<byte> context,
        int length)
    {
        ArgumentNullException.ThrowIfNull(label);
        if (length < 0 || length > ushort.MaxValue)
            throw new ArgumentOutOfRangeException(nameof(length));

        byte[] fullLabel = Encoding.UTF8.GetBytes("tls13 " + label);
        if (fullLabel.Length > byte.MaxValue)
            throw new ArgumentException("TLS 1.3 HKDF label exceeds 255 bytes.", nameof(label));
        if (context.Length > byte.MaxValue)
            throw new ArgumentException("TLS 1.3 HKDF context exceeds 255 bytes.", nameof(context));

        Span<byte> hkdfLabel = stackalloc byte[2 + 1 + fullLabel.Length + 1 + context.Length];
        BinaryPrimitives.WriteUInt16BigEndian(hkdfLabel[..2], (ushort)length);
        hkdfLabel[2] = (byte)fullLabel.Length;
        fullLabel.CopyTo(hkdfLabel.Slice(3));
        hkdfLabel[3 + fullLabel.Length] = (byte)context.Length;
        context.CopyTo(hkdfLabel.Slice(4 + fullLabel.Length));

        return HkdfExpand(alg, secret, hkdfLabel, length);
    }

    public static byte[] Tls12Prf(
        HashAlgorithmKind alg,
        ReadOnlySpan<byte> secret,
        string label,
        ReadOnlySpan<byte> seed,
        int length)
    {
        ArgumentNullException.ThrowIfNull(label);
        if (length < 0)
            throw new ArgumentOutOfRangeException(nameof(length));
        if (length == 0)
            return Array.Empty<byte>();

        int hashLen = DigestLength(alg);
        byte[] labelBytes = Encoding.ASCII.GetBytes(label);
        var result = new byte[length];
        var input = new byte[hashLen + labelBytes.Length + seed.Length];
        var a = new byte[hashLen];
        var block = new byte[hashLen];
        try
        {
            labelBytes.CopyTo(input.AsSpan(hashLen));
            seed.CopyTo(input.AsSpan(hashLen + labelBytes.Length));

            // A(1) = HMAC(secret, label || seed)
            HmacTo(alg, secret, input.AsSpan(hashLen), a);

            int offset = 0;
            while (offset < length)
            {
                a.AsSpan().CopyTo(input.AsSpan(0, hashLen));
                HmacTo(alg, secret, input, block);

                int take = Math.Min(hashLen, length - offset);
                block.AsSpan(0, take).CopyTo(result.AsSpan(offset));
                offset += take;

                if (offset < length)
                    HmacTo(alg, secret, a, a);
            }
            return result;
        }
        finally
        {
            ConstantTime.ZeroMemory(input);
            ConstantTime.ZeroMemory(a);
            ConstantTime.ZeroMemory(block);
        }
    }
}
