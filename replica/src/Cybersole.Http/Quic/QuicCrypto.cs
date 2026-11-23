using System.Buffers.Binary;
using Cybersole.Http.Crypto;
using Cybersole.Http.Profiles;
using Cybersole.Http.Protocol;
using Cybersole.Http.Tls;

namespace Cybersole.Http.Quic;

/// <summary>
/// QUIC packet payload AEAD + header protection key material for a single direction and encryption level
/// (RFC 9001 §5.1–§5.4 &amp; §6).
/// </summary>
public sealed class QuicKeySet
{
    public const int AeadTagLength = 16;

    public QuicKeySet(
        byte[] trafficSecret,
        byte[] key,
        byte[] iv,
        byte[] hpKey,
        ushort cipherSuite,
        HashAlgorithmKind hashAlg,
        bool isChaCha)
    {
        TrafficSecret = trafficSecret ?? throw new ArgumentNullException(nameof(trafficSecret));
        Key = key ?? throw new ArgumentNullException(nameof(key));
        Iv = iv ?? throw new ArgumentNullException(nameof(iv));
        HpKey = hpKey ?? throw new ArgumentNullException(nameof(hpKey));
        CipherSuite = cipherSuite;
        HashAlg = hashAlg;
        IsChaCha = isChaCha;
    }

    public byte[] TrafficSecret { get; }
    public byte[] Key { get; }
    public byte[] Iv { get; }
    public byte[] HpKey { get; }
    public ushort CipherSuite { get; }
    public HashAlgorithmKind HashAlg { get; }
    public bool IsChaCha { get; }

    public void ComputeNonce(ulong packetNumber, Span<byte> nonce12)
    {
        if (nonce12.Length < 12)
            throw new ArgumentException("QUIC AEAD nonce buffer must be at least 12 bytes.", nameof(nonce12));

        Iv.AsSpan(0, 12).CopyTo(nonce12);
        Span<byte> pnBe = stackalloc byte[8];
        BinaryPrimitives.WriteUInt64BigEndian(pnBe, packetNumber);
        for (int i = 0; i < 8; i++)
            nonce12[4 + i] ^= pnBe[i];
    }

    public void PacketProtect(
        ulong packetNumber,
        ReadOnlySpan<byte> headerBytes,
        ReadOnlySpan<byte> plaintext,
        Span<byte> ciphertextWithTag)
    {
        if (ciphertextWithTag.Length != plaintext.Length + AeadTagLength)
            throw new ArgumentException($"Destination must be {plaintext.Length + AeadTagLength} bytes.", nameof(ciphertextWithTag));

        Span<byte> nonce = stackalloc byte[12];
        ComputeNonce(packetNumber, nonce);
        Span<byte> ct = ciphertextWithTag.Slice(0, plaintext.Length);
        Span<byte> tag = ciphertextWithTag.Slice(plaintext.Length, AeadTagLength);

        try
        {
            if (IsChaCha)
                ChaCha20Poly1305Primitives.Encrypt(Key, nonce, plaintext, headerBytes, ct, tag);
            else
                AesPrimitives.AesGcmEncrypt(Key, nonce, plaintext, headerBytes, ct, tag);
        }
        finally
        {
            nonce.Clear();
        }
    }

    public byte[] PacketProtect(ulong packetNumber, ReadOnlySpan<byte> headerBytes, ReadOnlySpan<byte> plaintext)
    {
        var output = new byte[plaintext.Length + AeadTagLength];
        PacketProtect(packetNumber, headerBytes, plaintext, output);
        return output;
    }

    public bool PacketUnprotect(
        ulong packetNumber,
        ReadOnlySpan<byte> headerBytes,
        ReadOnlySpan<byte> ciphertextWithTag,
        Span<byte> plaintext)
    {
        if (ciphertextWithTag.Length < AeadTagLength)
            return false;

        int ptLen = ciphertextWithTag.Length - AeadTagLength;
        if (plaintext.Length != ptLen)
            throw new ArgumentException($"Plaintext span must be {ptLen} bytes.", nameof(plaintext));

        Span<byte> nonce = stackalloc byte[12];
        ComputeNonce(packetNumber, nonce);
        ReadOnlySpan<byte> ct = ciphertextWithTag.Slice(0, ptLen);
        ReadOnlySpan<byte> tag = ciphertextWithTag.Slice(ptLen, AeadTagLength);

        try
        {
            return IsChaCha
                ? ChaCha20Poly1305Primitives.Decrypt(Key, nonce, ct, headerBytes, tag, plaintext)
                : AesPrimitives.AesGcmDecrypt(Key, nonce, ct, headerBytes, tag, plaintext);
        }
        finally
        {
            nonce.Clear();
        }
    }

    public bool TryPacketUnprotect(
        ulong packetNumber,
        ReadOnlySpan<byte> headerBytes,
        ReadOnlySpan<byte> ciphertextWithTag,
        out byte[] plaintext)
    {
        if (ciphertextWithTag.Length < AeadTagLength)
        {
            plaintext = Array.Empty<byte>();
            return false;
        }

        var buf = new byte[ciphertextWithTag.Length - AeadTagLength];
        if (!PacketUnprotect(packetNumber, headerBytes, ciphertextWithTag, buf))
        {
            plaintext = Array.Empty<byte>();
            return false;
        }

        plaintext = buf;
        return true;
    }

    public void ComputeHeaderProtectionMask(ReadOnlySpan<byte> sample16, Span<byte> mask5)
    {
        if (sample16.Length < 16)
            throw new ArgumentException("QUIC header protection sample must be 16 bytes.", nameof(sample16));
        if (mask5.Length < 5)
            throw new ArgumentException("QUIC header protection mask buffer must be at least 5 bytes.", nameof(mask5));

        if (IsChaCha)
        {
            uint counter = BinaryPrimitives.ReadUInt32LittleEndian(sample16.Slice(0, 4));
            ReadOnlySpan<byte> nonce12 = sample16.Slice(4, 12);
            Span<byte> block = stackalloc byte[64];
            ChaCha20Poly1305Primitives.ChaCha20Block(HpKey, counter, nonce12, block);
            block.Slice(0, 5).CopyTo(mask5);
            block.Clear();
        }
        else
        {
            Span<byte> block = stackalloc byte[16];
            AesPrimitives.EncryptBlock(HpKey, sample16.Slice(0, 16), block);
            block.Slice(0, 5).CopyTo(mask5);
            block.Clear();
        }
    }

    /// <summary>
    /// Applies RFC 9001 §5.4 header protection in-place using the 16-byte sample at <paramref name="pnOffset"/> + 4.
    /// </summary>
    public void ApplyHeaderProtection(Span<byte> packet, int pnOffset, int pnLength)
    {
        if (pnLength is < 1 or > 4)
            throw new ArgumentOutOfRangeException(nameof(pnLength), pnLength, "Packet number length must be 1..4 bytes.");
        if (pnOffset < 1 || pnOffset + 4 + 16 > packet.Length)
            throw new ArgumentException("Packet buffer too small for RFC 9001 header protection sample at pnOffset + 4.", nameof(packet));

        Span<byte> mask = stackalloc byte[5];
        ComputeHeaderProtectionMask(packet.Slice(pnOffset + 4, 16), mask);

        bool isLongHeader = (packet[0] & 0x80) != 0;
        packet[0] ^= isLongHeader ? (byte)(mask[0] & 0x0F) : (byte)(mask[0] & 0x1F);

        for (int i = 0; i < pnLength; i++)
            packet[pnOffset + i] ^= mask[1 + i];

        mask.Clear();
    }

    /// <summary>
    /// Removes RFC 9001 §5.4 header protection in-place using the 16-byte sample at <paramref name="pnOffset"/> + 4.
    /// </summary>
    public bool TryRemoveHeaderProtection(Span<byte> packet, int pnOffset, out int pnLength, out bool keyPhase)
    {
        if (pnOffset < 1 || pnOffset + 4 + 16 > packet.Length)
        {
            pnLength = 0;
            keyPhase = false;
            return false;
        }

        Span<byte> mask = stackalloc byte[5];
        ComputeHeaderProtectionMask(packet.Slice(pnOffset + 4, 16), mask);

        bool isLongHeader = (packet[0] & 0x80) != 0;
        packet[0] ^= isLongHeader ? (byte)(mask[0] & 0x0F) : (byte)(mask[0] & 0x1F);

        pnLength = (packet[0] & 0x03) + 1;
        keyPhase = !isLongHeader && (packet[0] & 0x04) != 0;

        if (pnOffset + pnLength + AeadTagLength > packet.Length)
        {
            mask.Clear();
            return false;
        }

        for (int i = 0; i < pnLength; i++)
            packet[pnOffset + i] ^= mask[1 + i];

        mask.Clear();
        return true;
    }

    public void RemoveHeaderProtection(Span<byte> packet, int pnOffset, out int pnLength, out bool keyPhase)
    {
        if (!TryRemoveHeaderProtection(packet, pnOffset, out pnLength, out keyPhase))
            throw new QuicException(QuicErrorCode.FrameEncodingError, isApplicationError: false, "Packet too short for QUIC header protection removal.");
    }

    /// <summary>Derives the next-generation 1-RTT packet protection key set (RFC 9001 §6.1, label "quic ku").</summary>
    public QuicKeySet UpdateKeys()
    {
        if (TrafficSecret.Length == 0)
            throw new InvalidOperationException("Cannot perform QUIC key update without a traffic secret.");

        int secretLen = HashPrimitives.DigestLength(HashAlg);
        byte[] nextSecret = HashPrimitives.HkdfExpandLabel(HashAlg, TrafficSecret, "quic ku", ReadOnlySpan<byte>.Empty, secretLen);
        return QuicCrypto.DerivePacketKeys(CipherSuite, nextSecret);
    }

    public void Clear()
    {
        ConstantTime.ZeroMemory(TrafficSecret);
        ConstantTime.ZeroMemory(Key);
        ConstantTime.ZeroMemory(Iv);
        ConstantTime.ZeroMemory(HpKey);
    }
}

/// <summary>
/// RFC 9001 QUIC v1 key derivation, packet number compression/recovery, and Retry integrity verification.
/// </summary>
public static class QuicCrypto
{
    public const uint QuicVersion1 = 0x0000_0001u;
    public const int AeadTagLength = QuicKeySet.AeadTagLength;

    /// <summary>RFC 9001 §5.2 QUIC v1 Initial Salt.</summary>
    public static ReadOnlySpan<byte> QuicV1InitialSalt => new byte[]
    {
        0x38, 0x76, 0x2C, 0xF7, 0xF5, 0x59, 0x34, 0xB3, 0x4D, 0x17,
        0x9A, 0xE6, 0xA4, 0xC8, 0x0C, 0xAD, 0xCC, 0xBB, 0x7F, 0x0A,
    };

    /// <summary>RFC 9001 §5.8 Retry Integrity Tag AEAD Key.</summary>
    public static ReadOnlySpan<byte> QuicV1RetryKey => new byte[]
    {
        0xBE, 0x0C, 0x69, 0x0B, 0x9F, 0x66, 0x57, 0x5A,
        0x1D, 0x76, 0x6B, 0x54, 0xE3, 0x68, 0xC8, 0x4E,
    };

    /// <summary>RFC 9001 §5.8 Retry Integrity Tag AEAD Nonce.</summary>
    public static ReadOnlySpan<byte> QuicV1RetryNonce => new byte[]
    {
        0x46, 0x15, 0x99, 0xD3, 0x5D, 0x63, 0x2B, 0xF2,
        0x23, 0x98, 0x25, 0xBB,
    };

    public static void DeriveInitialSecrets(
        ReadOnlySpan<byte> dcid,
        out byte[] initialSecret,
        out byte[] clientInitialSecret,
        out byte[] serverInitialSecret)
    {
        initialSecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, QuicV1InitialSalt, dcid);
        clientInitialSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, initialSecret, "client in", ReadOnlySpan<byte>.Empty, 32);
        serverInitialSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, initialSecret, "server in", ReadOnlySpan<byte>.Empty, 32);
    }

    public static QuicKeySet DeriveInitialKeys(ReadOnlySpan<byte> dcid, bool isServer)
    {
        byte[] initialSecret = HashPrimitives.HkdfExtract(HashAlgorithmKind.Sha256, QuicV1InitialSalt, dcid);
        try
        {
            string label = isServer ? "server in" : "client in";
            byte[] trafficSecret = HashPrimitives.HkdfExpandLabel(HashAlgorithmKind.Sha256, initialSecret, label, ReadOnlySpan<byte>.Empty, 32);
            return DerivePacketKeys(CipherSuiteId.TLS_AES_128_GCM_SHA256, trafficSecret);
        }
        finally
        {
            ConstantTime.ZeroMemory(initialSecret);
        }
    }

    public static QuicKeySet DerivePacketKeys(TlsTrafficKeys tlsKeys)
    {
        ArgumentNullException.ThrowIfNull(tlsKeys);
        return DerivePacketKeys(tlsKeys.CipherSuite, tlsKeys.TrafficSecret);
    }

    public static QuicKeySet DerivePacketKeys(ushort cipherSuite, ReadOnlySpan<byte> trafficSecret)
    {
        (HashAlgorithmKind hashAlg, int keyLen, int hpLen, bool isChaCha) = cipherSuite switch
        {
            CipherSuiteId.TLS_AES_128_GCM_SHA256 => (HashAlgorithmKind.Sha256, 16, 16, false),
            CipherSuiteId.TLS_AES_256_GCM_SHA384 => (HashAlgorithmKind.Sha384, 32, 32, false),
            CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256 => (HashAlgorithmKind.Sha256, 32, 32, true),
            _ => throw new QuicException(QuicErrorCode.InternalError, false, $"Unsupported QUIC cipher suite 0x{cipherSuite:X4}."),
        };

        byte[] key = HashPrimitives.HkdfExpandLabel(hashAlg, trafficSecret, "quic key", ReadOnlySpan<byte>.Empty, keyLen);
        byte[] iv = HashPrimitives.HkdfExpandLabel(hashAlg, trafficSecret, "quic iv", ReadOnlySpan<byte>.Empty, 12);
        byte[] hpKey = HashPrimitives.HkdfExpandLabel(hashAlg, trafficSecret, "quic hp", ReadOnlySpan<byte>.Empty, hpLen);

        return new QuicKeySet(
            trafficSecret.ToArray(),
            key,
            iv,
            hpKey,
            cipherSuite,
            hashAlg,
            isChaCha);
    }

    /// <summary>RFC 9000 §17.2.4 &amp; Appendix A.3 Packet Number Decoding.</summary>
    public static ulong DecodePacketNumber(ulong largestPn, ulong truncatedPn, int pnBitLength)
    {
        if (pnBitLength is not (8 or 16 or 24 or 32))
            throw new ArgumentOutOfRangeException(nameof(pnBitLength), pnBitLength, "Packet number bit length must be 8, 16, 24, or 32.");

        ulong expectedPn = largestPn == ulong.MaxValue ? 0UL : largestPn + 1UL;
        ulong pnWin = 1UL << pnBitLength;
        ulong pnHwin = pnWin >> 1;
        ulong pnMask = pnWin - 1UL;
        ulong candidatePn = (expectedPn & ~pnMask) | (truncatedPn & pnMask);

        if (expectedPn >= pnHwin && candidatePn <= expectedPn - pnHwin && candidatePn < (1UL << 62) - pnWin)
            return candidatePn + pnWin;

        if (candidatePn > expectedPn + pnHwin && candidatePn >= pnWin)
            return candidatePn - pnWin;

        return candidatePn;
    }

    public static ulong DecodePacketNumber(long largestPnOrMinusOne, ulong truncatedPn, int pnBitLength)
    {
        if (largestPnOrMinusOne < 0)
            return DecodePacketNumber(ulong.MaxValue, truncatedPn, pnBitLength);
        return DecodePacketNumber((ulong)largestPnOrMinusOne, truncatedPn, pnBitLength);
    }

    /// <summary>RFC 9000 Appendix A.2 minimal packet number byte width (1..4 bytes).</summary>
    public static int GetRequiredPacketNumberLength(ulong packetNumber, long largestAckedOrMinusOne)
    {
        ulong numUnacked = largestAckedOrMinusOne < 0
            ? packetNumber + 1UL
            : packetNumber >= (ulong)largestAckedOrMinusOne
                ? packetNumber - (ulong)largestAckedOrMinusOne
                : packetNumber + 1UL;

        if (numUnacked < (1UL << 7))
            return 1;
        if (numUnacked < (1UL << 15))
            return 2;
        if (numUnacked < (1UL << 23))
            return 3;
        return 4;
    }

    /// <summary>RFC 9001 §5.8 Retry Integrity Tag calculation.</summary>
    public static void ComputeRetryIntegrityTag(
        ReadOnlySpan<byte> originalDcid,
        ReadOnlySpan<byte> retryPacketWithoutTag,
        Span<byte> tag16)
    {
        if (originalDcid.Length > 255)
            throw new ArgumentOutOfRangeException(nameof(originalDcid), "ODCID length cannot exceed 255 bytes.");
        if (tag16.Length < AeadTagLength)
            throw new ArgumentException("Destination tag buffer must be at least 16 bytes.", nameof(tag16));

        var pseudo = new byte[1 + originalDcid.Length + retryPacketWithoutTag.Length];
        pseudo[0] = (byte)originalDcid.Length;
        originalDcid.CopyTo(pseudo.AsSpan(1));
        retryPacketWithoutTag.CopyTo(pseudo.AsSpan(1 + originalDcid.Length));

        AesPrimitives.AesGcmEncrypt(
            QuicV1RetryKey,
            QuicV1RetryNonce,
            ReadOnlySpan<byte>.Empty,
            pseudo,
            Span<byte>.Empty,
            tag16.Slice(0, AeadTagLength));
    }

    /// <summary>RFC 9001 §5.8 Retry Integrity Tag verification.</summary>
    public static bool VerifyRetryIntegrityTag(ReadOnlySpan<byte> originalDcid, ReadOnlySpan<byte> retryPacket)
    {
        // Minimum Retry packet: flags(1) + ver(4) + dcidLen(1) + scidLen(1) + tag(16) = 23 bytes
        if (retryPacket.Length < 23)
            return false;

        Span<byte> expectedTag = stackalloc byte[AeadTagLength];
        ComputeRetryIntegrityTag(originalDcid, retryPacket.Slice(0, retryPacket.Length - AeadTagLength), expectedTag);
        return ConstantTime.Equals(expectedTag, retryPacket.Slice(retryPacket.Length - AeadTagLength, AeadTagLength));
    }
}
