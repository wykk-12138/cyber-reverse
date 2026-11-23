using System.Buffers;
using System.Buffers.Binary;
using System.Security.Cryptography;
using Cybersole.Http.Crypto;
using Cybersole.Http.Profiles;

namespace Cybersole.Http.Tls;

/// <summary>TLS record layer content types (RFC 5246 §6.2.1 / RFC 8446 §5.1).</summary>
public enum TlsContentType : byte
{
    ChangeCipherSpec = 20,
    Alert = 21,
    Handshake = 22,
    ApplicationData = 23,
}

/// <summary>TLS alert severity levels.</summary>
public enum TlsAlertLevel : byte
{
    Warning = 1,
    Fatal = 2,
}

/// <summary>TLS alert descriptions (RFC 5246 §7.2 / RFC 8446 §6).</summary>
public enum TlsAlertDescription : byte
{
    CloseNotify = 0,
    UnexpectedMessage = 10,
    BadRecordMac = 20,
    RecordOverflow = 22,
    HandshakeFailure = 40,
    BadCertificate = 42,
    UnsupportedCertificate = 43,
    CertificateRevoked = 44,
    CertificateExpired = 45,
    CertificateUnknown = 46,
    IllegalParameter = 47,
    UnknownCa = 48,
    AccessDenied = 49,
    DecodeError = 50,
    DecryptError = 51,
    ProtocolVersion = 70,
    InsufficientSecurity = 71,
    InternalError = 80,
    InappropriateFallback = 86,
    UserCanceled = 90,
    MissingExtension = 109,
    UnsupportedExtension = 110,
    UnrecognizedName = 112,
    BadCertificateStatusResponse = 113,
    UnknownPskIdentity = 115,
    CertificateRequired = 116,
    NoApplicationProtocol = 120,
}

/// <summary>Base TLS protocol/handshake exception.</summary>
public class TlsException : Exception
{
    public TlsException(string message)
        : base(message)
    {
    }

    public TlsException(string message, Exception? innerException)
        : base(message, innerException)
    {
    }
}

/// <summary>TLS alert exception carrying the wire alert level and description.</summary>
public sealed class TlsAlertException : TlsException
{
    public TlsAlertException(TlsAlertDescription description, string? message = null, bool isLocal = true, TlsAlertLevel level = TlsAlertLevel.Fatal)
        : base(message ?? $"TLS {(isLocal ? "local" : "remote")} alert: {description} ({(byte)description})")
    {
        Level = level;
        Description = description;
        IsLocal = isLocal;
    }

    public TlsAlertLevel Level { get; }
    public TlsAlertDescription Description { get; }
    public bool IsLocal { get; }
}

/// <summary>
/// Derived TLS traffic secret and record/QUIC packet protection key material.
/// </summary>
public sealed record TlsTrafficKeys(
    byte[] TrafficSecret,
    byte[] Key,
    byte[] Iv,
    HashAlgorithmKind HashAlg,
    ushort CipherSuite,
    bool IsChaCha)
{
    public byte[]? MacKey { get; init; }
    public bool IsCbc { get; init; }
    public bool EncryptThenMac { get; init; }

    public void Clear()
    {
        ConstantTime.ZeroMemory(TrafficSecret);
        ConstantTime.ZeroMemory(Key);
        ConstantTime.ZeroMemory(Iv);
        if (MacKey is not null)
            ConstantTime.ZeroMemory(MacKey);
    }
}

/// <summary>
/// Pure managed TLS 1.2 &amp; TLS 1.3 record framing, encryption, decryption,
/// zero-padding removal, and fragment limit enforcement (RFC 5246 §6.2 / RFC 8446 §5).
/// </summary>
public sealed class TlsRecordLayer : IDisposable
{
    public const int MaxPlaintextFragment = 16_384;
    public const int MaxTls13CiphertextLength = MaxPlaintextFragment + 256;
    public const int MaxTls12CiphertextLength = MaxPlaintextFragment + 2_048;
    public const int MinRecordSizeLimit = 64;

    private TlsTrafficKeys? _readKeys;
    private TlsTrafficKeys? _writeKeys;
    private ulong _readSeq;
    private ulong _writeSeq;
    private bool _readIsTls13;
    private bool _writeIsTls13;
    private bool _handshakeCompleted;
    private int _maxOutboundPlaintext = MaxPlaintextFragment;

    public int MaxOutboundPlaintextFragment
    {
        get => _maxOutboundPlaintext;
        set => _maxOutboundPlaintext = Math.Clamp(value, MinRecordSizeLimit, MaxPlaintextFragment);
    }

    public ulong ReadSequence => _readSeq;
    public ulong WriteSequence => _writeSeq;
    public bool HasReadCipher => _readKeys is not null;
    public bool HasWriteCipher => _writeKeys is not null;

    public void MarkHandshakeCompleted() => _handshakeCompleted = true;

    public void SetReadKeys(TlsTrafficKeys keys, bool isTls13)
    {
        ArgumentNullException.ThrowIfNull(keys);
        _readKeys?.Clear();
        _readKeys = keys;
        _readSeq = 0;
        _readIsTls13 = isTls13;
    }

    public void SetWriteKeys(TlsTrafficKeys keys, bool isTls13)
    {
        ArgumentNullException.ThrowIfNull(keys);
        _writeKeys?.Clear();
        _writeKeys = keys;
        _writeSeq = 0;
        _writeIsTls13 = isTls13;
    }

    public static void ValidateRecordHeader(ReadOnlySpan<byte> header5, bool readEncrypted, bool isTls13, out TlsContentType contentType, out int payloadLength)
    {
        if (header5.Length < 5)
            throw new ArgumentException("TLS record header must be 5 bytes.", nameof(header5));

        byte typeByte = header5[0];
        if (typeByte is < 20 or > 23)
            throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Invalid TLS record content type: 0x{typeByte:X2}.");

        byte verMajor = header5[1];
        byte verMinor = header5[2];
        if (verMajor != 0x03 || verMinor > 0x04)
            throw new TlsAlertException(TlsAlertDescription.ProtocolVersion, $"Invalid TLS record legacy version: 0x{verMajor:X2}{verMinor:X2}.");

        payloadLength = BinaryPrimitives.ReadUInt16BigEndian(header5.Slice(3, 2));
        contentType = (TlsContentType)typeByte;

        int maxAllowed = !readEncrypted
            ? MaxPlaintextFragment
            : isTls13
                ? MaxTls13CiphertextLength
                : MaxTls12CiphertextLength;

        if (payloadLength > maxAllowed)
        {
            throw new TlsAlertException(
                TlsAlertDescription.RecordOverflow,
                $"TLS record payload length {payloadLength} exceeds maximum {maxAllowed}.");
        }
    }

    /// <summary>
    /// Encrypts (or frames if unencrypted) <paramref name="plaintext"/> into one or more
    /// wire TLS records honoring <see cref="MaxOutboundPlaintextFragment"/>.
    /// </summary>
    public List<byte[]> ProtectRecords(TlsContentType contentType, ReadOnlySpan<byte> plaintext, ushort unencryptedRecordVersion = TlsVersion.Tls12)
    {
        var records = new List<byte[]>(Math.Max(1, (plaintext.Length / _maxOutboundPlaintext) + 1));

        if (plaintext.IsEmpty)
        {
            records.Add(ProtectSingleRecord(contentType, ReadOnlySpan<byte>.Empty, unencryptedRecordVersion));
            return records;
        }

        int offset = 0;
        while (offset < plaintext.Length)
        {
            int chunkLen = Math.Min(_maxOutboundPlaintext, plaintext.Length - offset);
            records.Add(ProtectSingleRecord(contentType, plaintext.Slice(offset, chunkLen), unencryptedRecordVersion));
            offset += chunkLen;
        }

        return records;
    }

    public byte[] ProtectSingleRecord(TlsContentType contentType, ReadOnlySpan<byte> plaintextChunk, ushort unencryptedRecordVersion = TlsVersion.Tls12)
    {
        if (plaintextChunk.Length > MaxPlaintextFragment)
        {
            throw new TlsAlertException(
                TlsAlertDescription.RecordOverflow,
                $"Plaintext fragment length {plaintextChunk.Length} exceeds {MaxPlaintextFragment}.");
        }

        if (_writeKeys is null || (!_writeIsTls13 && contentType == TlsContentType.ChangeCipherSpec))
        {
            var plainRec = new byte[5 + plaintextChunk.Length];
            plainRec[0] = (byte)contentType;
            BinaryPrimitives.WriteUInt16BigEndian(plainRec.AsSpan(1, 2), unencryptedRecordVersion);
            BinaryPrimitives.WriteUInt16BigEndian(plainRec.AsSpan(3, 2), (ushort)plaintextChunk.Length);
            plaintextChunk.CopyTo(plainRec.AsSpan(5));
            return plainRec;
        }

        if (_writeSeq == ulong.MaxValue)
            throw new TlsAlertException(TlsAlertDescription.InternalError, "TLS write sequence number exhausted.");

        if (_writeIsTls13)
            return EncryptTls13Record(_writeKeys, ref _writeSeq, contentType, plaintextChunk);

        return EncryptTls12Record(_writeKeys, ref _writeSeq, contentType, plaintextChunk);
    }

    public byte[] DecryptRecord(ReadOnlySpan<byte> header5, ReadOnlySpan<byte> payload, out TlsContentType innerContentType)
    {
        ValidateRecordHeader(header5, _readKeys is not null, _readIsTls13, out TlsContentType outerType, out int expectedLen);
        if (payload.Length != expectedLen)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "TLS record payload length mismatch.");

        if (_readKeys is null)
        {
            innerContentType = outerType;
            return payload.ToArray();
        }

        if (_readIsTls13)
        {
            // Middlebox compatibility permits unencrypted ChangeCipherSpec(1) before handshake completes.
            if (!_handshakeCompleted && outerType == TlsContentType.ChangeCipherSpec && payload.Length == 1 && payload[0] == 0x01)
            {
                innerContentType = TlsContentType.ChangeCipherSpec;
                return payload.ToArray();
            }

            // Unencrypted alert before handshake finishes (e.g., server rejected ClientHello/ServerHello).
            if (!_handshakeCompleted && outerType == TlsContentType.Alert && payload.Length == 2)
            {
                innerContentType = TlsContentType.Alert;
                return payload.ToArray();
            }

            if (outerType != TlsContentType.ApplicationData)
            {
                throw new TlsAlertException(
                    TlsAlertDescription.UnexpectedMessage,
                    $"Expected encrypted TLS 1.3 record type 0x17, got 0x{(byte)outerType:X2}.");
            }

            if (_readSeq == ulong.MaxValue)
                throw new TlsAlertException(TlsAlertDescription.InternalError, "TLS read sequence number exhausted.");

            return DecryptTls13Record(_readKeys, ref _readSeq, header5, payload, out innerContentType);
        }

        if (_readSeq == ulong.MaxValue)
            throw new TlsAlertException(TlsAlertDescription.InternalError, "TLS read sequence number exhausted.");

        innerContentType = outerType;
        return DecryptTls12Record(_readKeys, ref _readSeq, outerType, payload);
    }

    private static byte[] EncryptTls13Record(TlsTrafficKeys keys, ref ulong seq, TlsContentType innerType, ReadOnlySpan<byte> plaintext)
    {
        int innerLen = plaintext.Length + 1;
        int encryptedLen = innerLen + 16;
        if (encryptedLen > MaxTls13CiphertextLength)
            throw new TlsAlertException(TlsAlertDescription.RecordOverflow, "TLS 1.3 ciphertext would exceed maximum length.");

        var record = new byte[5 + encryptedLen];
        record[0] = (byte)TlsContentType.ApplicationData;
        record[1] = 0x03;
        record[2] = 0x03;
        BinaryPrimitives.WriteUInt16BigEndian(record.AsSpan(3, 2), (ushort)encryptedLen);

        byte[] innerBuf = ArrayPool<byte>.Shared.Rent(innerLen);
        Span<byte> nonce = stackalloc byte[12];
        try
        {
            plaintext.CopyTo(innerBuf);
            innerBuf[plaintext.Length] = (byte)innerType;
            ReadOnlySpan<byte> innerSpan = innerBuf.AsSpan(0, innerLen);

            ComputeXorNonce(keys.Iv, seq, nonce);
            ReadOnlySpan<byte> aad = record.AsSpan(0, 5);
            Span<byte> ct = record.AsSpan(5, innerLen);
            Span<byte> tag = record.AsSpan(5 + innerLen, 16);

            if (keys.IsChaCha)
                ChaCha20Poly1305Primitives.Encrypt(keys.Key, nonce, innerSpan, aad, ct, tag);
            else
                AesPrimitives.AesGcmEncrypt(keys.Key, nonce, innerSpan, aad, ct, tag);

            seq++;
            return record;
        }
        finally
        {
            nonce.Clear();
            ConstantTime.ZeroMemory(innerBuf.AsSpan(0, innerLen));
            ArrayPool<byte>.Shared.Return(innerBuf);
        }
    }

    private static byte[] DecryptTls13Record(
        TlsTrafficKeys keys,
        ref ulong seq,
        ReadOnlySpan<byte> header5,
        ReadOnlySpan<byte> payload,
        out TlsContentType innerContentType)
    {
        if (payload.Length < 1 + 16)
            throw new TlsAlertException(TlsAlertDescription.DecodeError, "TLS 1.3 encrypted record is too short.");
        if (payload.Length > MaxTls13CiphertextLength)
            throw new TlsAlertException(TlsAlertDescription.RecordOverflow, "TLS 1.3 ciphertext exceeds maximum length.");

        int innerLen = payload.Length - 16;
        byte[] decrypted = ArrayPool<byte>.Shared.Rent(innerLen);
        Span<byte> nonce = stackalloc byte[12];
        try
        {
            ComputeXorNonce(keys.Iv, seq, nonce);
            ReadOnlySpan<byte> ct = payload.Slice(0, innerLen);
            ReadOnlySpan<byte> tag = payload.Slice(innerLen, 16);
            Span<byte> ptSpan = decrypted.AsSpan(0, innerLen);

            bool ok = keys.IsChaCha
                ? ChaCha20Poly1305Primitives.Decrypt(keys.Key, nonce, ct, header5, tag, ptSpan)
                : AesPrimitives.AesGcmDecrypt(keys.Key, nonce, ct, header5, tag, ptSpan);

            if (!ok)
                throw new TlsAlertException(TlsAlertDescription.BadRecordMac, "TLS 1.3 AEAD authentication tag verification failed.");

            seq++;

            // RFC 8446 §5.4: strip trailing zero padding to locate ContentType byte.
            int typeIndex = innerLen - 1;
            while (typeIndex >= 0 && ptSpan[typeIndex] == 0)
                typeIndex--;

            if (typeIndex < 0)
                throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, "TLS 1.3 inner plaintext had no non-zero ContentType byte.");

            byte contentTypeByte = ptSpan[typeIndex];
            if (contentTypeByte is < 20 or > 23)
                throw new TlsAlertException(TlsAlertDescription.UnexpectedMessage, $"Invalid TLS 1.3 inner content type: 0x{contentTypeByte:X2}.");

            if (typeIndex > MaxPlaintextFragment)
                throw new TlsAlertException(TlsAlertDescription.RecordOverflow, $"TLS 1.3 unpadded plaintext length {typeIndex} exceeds {MaxPlaintextFragment}.");

            innerContentType = (TlsContentType)contentTypeByte;
            return ptSpan.Slice(0, typeIndex).ToArray();
        }
        finally
        {
            nonce.Clear();
            ConstantTime.ZeroMemory(decrypted.AsSpan(0, innerLen));
            ArrayPool<byte>.Shared.Return(decrypted);
        }
    }

    private static byte[] EncryptTls12Record(TlsTrafficKeys keys, ref ulong seq, TlsContentType contentType, ReadOnlySpan<byte> plaintext)
    {
        if (keys.IsCbc)
            return EncryptTls12CbcRecord(keys, ref seq, contentType, plaintext);

        Span<byte> aad = stackalloc byte[13];
        BuildTls12Aad(seq, contentType, (ushort)plaintext.Length, aad);

        if (keys.IsChaCha)
        {
            var record = new byte[5 + plaintext.Length + 16];
            record[0] = (byte)contentType;
            record[1] = 0x03;
            record[2] = 0x03;
            BinaryPrimitives.WriteUInt16BigEndian(record.AsSpan(3, 2), (ushort)(plaintext.Length + 16));

            Span<byte> nonce = stackalloc byte[12];
            try
            {
                ComputeXorNonce(keys.Iv, seq, nonce);
                ChaCha20Poly1305Primitives.Encrypt(
                    keys.Key,
                    nonce,
                    plaintext,
                    aad,
                    record.AsSpan(5, plaintext.Length),
                    record.AsSpan(5 + plaintext.Length, 16));
                seq++;
                return record;
            }
            finally
            {
                nonce.Clear();
            }
        }
        else
        {
            // RFC 5288 AES-GCM: 8-byte explicit nonce + ciphertext + 16-byte tag
            var record = new byte[5 + 8 + plaintext.Length + 16];
            record[0] = (byte)contentType;
            record[1] = 0x03;
            record[2] = 0x03;
            BinaryPrimitives.WriteUInt16BigEndian(record.AsSpan(3, 2), (ushort)(8 + plaintext.Length + 16));

            Span<byte> explicitNonce = record.AsSpan(5, 8);
            BinaryPrimitives.WriteUInt64BigEndian(explicitNonce, seq);

            Span<byte> nonce = stackalloc byte[12];
            keys.Iv.AsSpan(0, 4).CopyTo(nonce.Slice(0, 4));
            explicitNonce.CopyTo(nonce.Slice(4, 8));

            try
            {
                AesPrimitives.AesGcmEncrypt(
                    keys.Key,
                    nonce,
                    plaintext,
                    aad,
                    record.AsSpan(13, plaintext.Length),
                    record.AsSpan(13 + plaintext.Length, 16));
                seq++;
                return record;
            }
            finally
            {
                nonce.Clear();
            }
        }
    }

    private static byte[] DecryptTls12Record(TlsTrafficKeys keys, ref ulong seq, TlsContentType contentType, ReadOnlySpan<byte> payload)
    {
        if (keys.IsCbc)
            return DecryptTls12CbcRecord(keys, ref seq, contentType, payload);

        Span<byte> aad = stackalloc byte[13];
        if (keys.IsChaCha)
        {
            if (payload.Length < 16)
                throw new TlsAlertException(TlsAlertDescription.BadRecordMac, "TLS 1.2 ChaCha20 record too short.");

            int ptLen = payload.Length - 16;
            if (ptLen > MaxPlaintextFragment)
                throw new TlsAlertException(TlsAlertDescription.RecordOverflow, "TLS 1.2 decrypted record exceeds max fragment size.");

            BuildTls12Aad(seq, contentType, (ushort)ptLen, aad);
            var plaintext = new byte[ptLen];
            Span<byte> nonce = stackalloc byte[12];
            try
            {
                ComputeXorNonce(keys.Iv, seq, nonce);
                bool ok = ChaCha20Poly1305Primitives.Decrypt(
                    keys.Key,
                    nonce,
                    payload.Slice(0, ptLen),
                    aad,
                    payload.Slice(ptLen, 16),
                    plaintext);

                if (!ok)
                    throw new TlsAlertException(TlsAlertDescription.BadRecordMac, "TLS 1.2 ChaCha20-Poly1305 tag verification failed.");

                seq++;
                return plaintext;
            }
            finally
            {
                nonce.Clear();
            }
        }
        else
        {
            if (payload.Length < 8 + 16)
                throw new TlsAlertException(TlsAlertDescription.BadRecordMac, "TLS 1.2 AES-GCM record too short.");

            int ptLen = payload.Length - 8 - 16;
            if (ptLen > MaxPlaintextFragment)
                throw new TlsAlertException(TlsAlertDescription.RecordOverflow, "TLS 1.2 decrypted record exceeds max fragment size.");

            BuildTls12Aad(seq, contentType, (ushort)ptLen, aad);
            var plaintext = new byte[ptLen];
            Span<byte> nonce = stackalloc byte[12];
            keys.Iv.AsSpan(0, 4).CopyTo(nonce.Slice(0, 4));
            payload.Slice(0, 8).CopyTo(nonce.Slice(4, 8));

            try
            {
                bool ok = AesPrimitives.AesGcmDecrypt(
                    keys.Key,
                    nonce,
                    payload.Slice(8, ptLen),
                    aad,
                    payload.Slice(8 + ptLen, 16),
                    plaintext);

                if (!ok)
                    throw new TlsAlertException(TlsAlertDescription.BadRecordMac, "TLS 1.2 AES-GCM tag verification failed.");

                seq++;
                return plaintext;
            }
            finally
            {
                nonce.Clear();
            }
        }
    }

    private static byte[] EncryptTls12CbcRecord(TlsTrafficKeys keys, ref ulong seq, TlsContentType contentType, ReadOnlySpan<byte> plaintext)
    {
        byte[] macKey = keys.MacKey ?? throw new InvalidOperationException("CBC keys require MacKey.");
        int macLen = HashPrimitives.DigestLength(keys.HashAlg);

        Span<byte> explicitIv = stackalloc byte[16];
        RandomNumberGenerator.Fill(explicitIv);

        if (keys.EncryptThenMac)
        {
            int padVal = (16 - ((plaintext.Length + 1) % 16)) % 16;
            int blockLen = plaintext.Length + 1 + padVal;
            byte[] padded = ArrayPool<byte>.Shared.Rent(blockLen);
            try
            {
                plaintext.CopyTo(padded);
                padded.AsSpan(plaintext.Length, padVal + 1).Fill((byte)padVal);

                byte[] ct = AesPrimitives.AesCbcEncrypt(keys.Key, explicitIv, padded.AsSpan(0, blockLen), pkcs7Padding: false);
                int ivAndCtLen = 16 + ct.Length;

                byte[] macInput = new byte[13 + ivAndCtLen];
                BuildTls12Aad(seq, contentType, (ushort)ivAndCtLen, macInput.AsSpan(0, 13));
                explicitIv.CopyTo(macInput.AsSpan(13, 16));
                ct.CopyTo(macInput.AsSpan(29));
                byte[] mac = HashPrimitives.Hmac(keys.HashAlg, macKey, macInput);

                var record = new byte[5 + ivAndCtLen + macLen];
                record[0] = (byte)contentType;
                record[1] = 0x03;
                record[2] = 0x03;
                BinaryPrimitives.WriteUInt16BigEndian(record.AsSpan(3, 2), (ushort)(ivAndCtLen + macLen));
                explicitIv.CopyTo(record.AsSpan(5, 16));
                ct.CopyTo(record.AsSpan(21));
                mac.CopyTo(record.AsSpan(5 + ivAndCtLen));
                seq++;
                return record;
            }
            finally
            {
                ConstantTime.ZeroMemory(padded.AsSpan(0, blockLen));
                ArrayPool<byte>.Shared.Return(padded);
            }
        }
        else
        {
            byte[] macInput = new byte[13 + plaintext.Length];
            BuildTls12Aad(seq, contentType, (ushort)plaintext.Length, macInput.AsSpan(0, 13));
            plaintext.CopyTo(macInput.AsSpan(13));
            byte[] mac = HashPrimitives.Hmac(keys.HashAlg, macKey, macInput);

            int totalBeforePad = plaintext.Length + macLen;
            int padVal = (16 - ((totalBeforePad + 1) % 16)) % 16;
            int blockLen = totalBeforePad + 1 + padVal;
            byte[] block = ArrayPool<byte>.Shared.Rent(blockLen);
            try
            {
                plaintext.CopyTo(block);
                mac.CopyTo(block.AsSpan(plaintext.Length));
                block.AsSpan(totalBeforePad, padVal + 1).Fill((byte)padVal);

                byte[] ct = AesPrimitives.AesCbcEncrypt(keys.Key, explicitIv, block.AsSpan(0, blockLen), pkcs7Padding: false);
                var record = new byte[5 + 16 + ct.Length];
                record[0] = (byte)contentType;
                record[1] = 0x03;
                record[2] = 0x03;
                BinaryPrimitives.WriteUInt16BigEndian(record.AsSpan(3, 2), (ushort)(16 + ct.Length));
                explicitIv.CopyTo(record.AsSpan(5, 16));
                ct.CopyTo(record.AsSpan(21));
                seq++;
                return record;
            }
            finally
            {
                ConstantTime.ZeroMemory(macInput);
                ConstantTime.ZeroMemory(block.AsSpan(0, blockLen));
                ArrayPool<byte>.Shared.Return(block);
            }
        }
    }

    private static byte[] DecryptTls12CbcRecord(TlsTrafficKeys keys, ref ulong seq, TlsContentType contentType, ReadOnlySpan<byte> payload)
    {
        byte[] macKey = keys.MacKey ?? throw new InvalidOperationException("CBC keys require MacKey.");
        int macLen = HashPrimitives.DigestLength(keys.HashAlg);

        if (keys.EncryptThenMac)
        {
            if (payload.Length < 16 + 16 + macLen)
                throw new TlsAlertException(TlsAlertDescription.BadRecordMac, "TLS 1.2 EtM CBC record too short.");

            int ivAndCtLen = payload.Length - macLen;
            if ((ivAndCtLen - 16) % 16 != 0)
                throw new TlsAlertException(TlsAlertDescription.BadRecordMac, "TLS 1.2 EtM CBC ciphertext length is not block-aligned.");

            byte[] macInput = new byte[13 + ivAndCtLen];
            BuildTls12Aad(seq, contentType, (ushort)ivAndCtLen, macInput.AsSpan(0, 13));
            payload.Slice(0, ivAndCtLen).CopyTo(macInput.AsSpan(13));
            byte[] expectedMac = HashPrimitives.Hmac(keys.HashAlg, macKey, macInput);

            if (!ConstantTime.Equals(expectedMac, payload.Slice(ivAndCtLen, macLen)))
                throw new TlsAlertException(TlsAlertDescription.BadRecordMac, "TLS 1.2 EtM CBC MAC verification failed.");

            byte[] decrypted = AesPrimitives.AesCbcDecrypt(keys.Key, payload.Slice(0, 16), payload.Slice(16, ivAndCtLen - 16), pkcs7Padding: false);
            try
            {
                int padVal = decrypted[^1];
                int padTotal = padVal + 1;
                if (padTotal > decrypted.Length)
                    throw new TlsAlertException(TlsAlertDescription.BadRecordMac, "Invalid TLS 1.2 EtM CBC padding.");

                int bad = 0;
                for (int i = 0; i < padTotal; i++)
                    bad |= decrypted[decrypted.Length - 1 - i] ^ padVal;
                if (bad != 0)
                    throw new TlsAlertException(TlsAlertDescription.BadRecordMac, "Invalid TLS 1.2 EtM CBC padding bytes.");

                int ptLen = decrypted.Length - padTotal;
                if (ptLen > MaxPlaintextFragment)
                    throw new TlsAlertException(TlsAlertDescription.RecordOverflow, "TLS 1.2 decrypted record exceeds max fragment size.");

                seq++;
                return decrypted.AsSpan(0, ptLen).ToArray();
            }
            finally
            {
                ConstantTime.ZeroMemory(decrypted);
            }
        }
        else
        {
            if (payload.Length < 32 || (payload.Length - 16) % 16 != 0)
                throw new TlsAlertException(TlsAlertDescription.BadRecordMac, "TLS 1.2 CBC record length invalid.");

            byte[] decrypted = AesPrimitives.AesCbcDecrypt(keys.Key, payload.Slice(0, 16), payload.Slice(16), pkcs7Padding: false);
            try
            {
                int padVal = decrypted[^1];
                int padTotal = padVal + 1;
                int maxPlain = decrypted.Length - macLen - 1;

                // Constant-time padding validation (avoid padding oracle timing leak)
                int padInvalid = maxPlain < 0 ? 1 : 0;
                int clampedPadTotal = Math.Min(padTotal, decrypted.Length);
                if (padTotal > decrypted.Length - macLen)
                    padInvalid |= 1;

                int checkLimit = Math.Min(256, decrypted.Length);
                for (int i = 0; i < checkLimit; i++)
                {
                    int inPad = (i - clampedPadTotal) >> 31;
                    padInvalid |= inPad & (decrypted[decrypted.Length - 1 - i] ^ padVal);
                }

                int effectivePtLen = padInvalid == 0 ? decrypted.Length - padTotal - macLen : 0;
                int effectiveMacOffset = padInvalid == 0 ? effectivePtLen : Math.Max(0, decrypted.Length - macLen);

                byte[] macInput = new byte[13 + effectivePtLen];
                BuildTls12Aad(seq, contentType, (ushort)effectivePtLen, macInput.AsSpan(0, 13));
                decrypted.AsSpan(0, effectivePtLen).CopyTo(macInput.AsSpan(13));
                byte[] expectedMac = HashPrimitives.Hmac(keys.HashAlg, macKey, macInput);

                bool macMatch = decrypted.Length >= macLen &&
                    ConstantTime.Equals(expectedMac, decrypted.AsSpan(effectiveMacOffset, macLen));

                if (padInvalid != 0 || !macMatch)
                    throw new TlsAlertException(TlsAlertDescription.BadRecordMac, "TLS 1.2 CBC padding/MAC verification failed.");

                if (effectivePtLen > MaxPlaintextFragment)
                    throw new TlsAlertException(TlsAlertDescription.RecordOverflow, "TLS 1.2 decrypted record exceeds max fragment size.");

                seq++;
                return decrypted.AsSpan(0, effectivePtLen).ToArray();
            }
            finally
            {
                ConstantTime.ZeroMemory(decrypted);
            }
        }
    }

    private static void ComputeXorNonce(ReadOnlySpan<byte> iv12, ulong seq, Span<byte> nonce12)
    {
        iv12.CopyTo(nonce12);
        Span<byte> seqBuf = stackalloc byte[8];
        BinaryPrimitives.WriteUInt64BigEndian(seqBuf, seq);
        for (int i = 0; i < 8; i++)
            nonce12[4 + i] ^= seqBuf[i];
    }

    private static void BuildTls12Aad(ulong seq, TlsContentType contentType, ushort plaintextLen, Span<byte> aad13)
    {
        BinaryPrimitives.WriteUInt64BigEndian(aad13.Slice(0, 8), seq);
        aad13[8] = (byte)contentType;
        aad13[9] = 0x03;
        aad13[10] = 0x03;
        BinaryPrimitives.WriteUInt16BigEndian(aad13.Slice(11, 2), plaintextLen);
    }

    public void Dispose()
    {
        _readKeys?.Clear();
        _writeKeys?.Clear();
        _readKeys = null;
        _writeKeys = null;
    }
}
