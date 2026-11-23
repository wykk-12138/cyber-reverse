using System.Buffers;
using System.Buffers.Binary;
using System.Text;
using Cybersole.Http.Profiles;
using Cybersole.Http.Protocol;
using Cybersole.Http.Tls;

namespace Cybersole.Http.Quic;

/// <summary>RFC 9000 §20.1 QUIC transport error codes.</summary>
public static class QuicErrorCode
{
    public const ulong NoError = 0x00;
    public const ulong InternalError = 0x01;
    public const ulong ConnectionRefused = 0x02;
    public const ulong FlowControlError = 0x03;
    public const ulong StreamLimitError = 0x04;
    public const ulong StreamStateError = 0x05;
    public const ulong FinalSizeError = 0x06;
    public const ulong FrameEncodingError = 0x07;
    public const ulong TransportParameterError = 0x08;
    public const ulong ConnectionIdLimitError = 0x09;
    public const ulong ProtocolViolation = 0x0A;
    public const ulong InvalidToken = 0x0B;
    public const ulong ApplicationError = 0x0C;
    public const ulong CryptoBufferExceeded = 0x0D;
    public const ulong KeyUpdateError = 0x0E;
    public const ulong AeadLimitReached = 0x0F;
    public const ulong CryptoErrorBase = 0x0100;

    public static ulong CryptoError(TlsAlertDescription alert) => CryptoErrorBase + (ulong)alert;
}

/// <summary>
/// RFC 9000 §16 62-bit Variable-Length Integer codec (1, 2, 4, or 8 bytes).
/// </summary>
public static class QuicVarInt
{
    public const ulong MaxValue = (1UL << 62) - 1UL;

    public static int GetEncodedLength(ulong value)
    {
        if (value <= 0x3FUL)
            return 1;
        if (value <= 0x3FFFUL)
            return 2;
        if (value <= 0x3FFF_FFFFUL)
            return 4;
        if (value <= MaxValue)
            return 8;
        throw new ArgumentOutOfRangeException(nameof(value), value, "QUIC variable-length integer exceeds 62-bit maximum.");
    }

    public static int Encode(ulong value, Span<byte> destination)
    {
        int len = GetEncodedLength(value);
        return EncodeFixedLength(value, len, destination);
    }

    public static byte[] Encode(ulong value)
    {
        int len = GetEncodedLength(value);
        var buf = new byte[len];
        EncodeFixedLength(value, len, buf);
        return buf;
    }

    public static int EncodeFixedLength(ulong value, int encodedLength, Span<byte> destination)
    {
        if (value > MaxValue)
            throw new ArgumentOutOfRangeException(nameof(value), value, "QUIC variable-length integer exceeds 62-bit maximum.");

        switch (encodedLength)
        {
            case 1:
                if (value > 0x3FUL)
                    throw new ArgumentOutOfRangeException(nameof(value), "Value does not fit in 1-byte VarInt.");
                if (destination.Length < 1)
                    throw new ArgumentException("Destination buffer too small for 1-byte VarInt.", nameof(destination));
                destination[0] = (byte)value;
                return 1;

            case 2:
                if (value > 0x3FFFUL)
                    throw new ArgumentOutOfRangeException(nameof(value), "Value does not fit in 2-byte VarInt.");
                if (destination.Length < 2)
                    throw new ArgumentException("Destination buffer too small for 2-byte VarInt.", nameof(destination));
                BinaryPrimitives.WriteUInt16BigEndian(destination, (ushort)(value | 0x4000UL));
                return 2;

            case 4:
                if (value > 0x3FFF_FFFFUL)
                    throw new ArgumentOutOfRangeException(nameof(value), "Value does not fit in 4-byte VarInt.");
                if (destination.Length < 4)
                    throw new ArgumentException("Destination buffer too small for 4-byte VarInt.", nameof(destination));
                BinaryPrimitives.WriteUInt32BigEndian(destination, (uint)(value | 0x8000_0000UL));
                return 4;

            case 8:
                if (destination.Length < 8)
                    throw new ArgumentException("Destination buffer too small for 8-byte VarInt.", nameof(destination));
                BinaryPrimitives.WriteUInt64BigEndian(destination, value | 0xC000_0000_0000_0000UL);
                return 8;

            default:
                throw new ArgumentOutOfRangeException(nameof(encodedLength), encodedLength, "VarInt encoded length must be 1, 2, 4, or 8.");
        }
    }

    public static void Write(List<byte> target, ulong value)
    {
        ArgumentNullException.ThrowIfNull(target);
        Span<byte> buf = stackalloc byte[8];
        int len = Encode(value, buf);
        for (int i = 0; i < len; i++)
            target.Add(buf[i]);
    }

    public static void Write(Stream target, ulong value)
    {
        ArgumentNullException.ThrowIfNull(target);
        Span<byte> buf = stackalloc byte[8];
        int len = Encode(value, buf);
        target.Write(buf[..len]);
    }

    public static void Write(IBufferWriter<byte> writer, ulong value)
    {
        ArgumentNullException.ThrowIfNull(writer);
        int len = GetEncodedLength(value);
        Span<byte> span = writer.GetSpan(len);
        EncodeFixedLength(value, len, span);
        writer.Advance(len);
    }

    public static bool TryDecode(ReadOnlySpan<byte> source, out ulong value, out int bytesRead)
    {
        if (source.IsEmpty)
        {
            value = 0;
            bytesRead = 0;
            return false;
        }

        byte first = source[0];
        int prefix = first >> 6;
        int len = 1 << prefix;
        if (source.Length < len)
        {
            value = 0;
            bytesRead = 0;
            return false;
        }

        value = len switch
        {
            1 => (ulong)(first & 0x3F),
            2 => (ulong)(BinaryPrimitives.ReadUInt16BigEndian(source) & 0x3FFF),
            4 => (ulong)(BinaryPrimitives.ReadUInt32BigEndian(source) & 0x3FFF_FFFFu),
            8 => BinaryPrimitives.ReadUInt64BigEndian(source) & 0x3FFF_FFFF_FFFF_FFFFUL,
            _ => 0,
        };
        bytesRead = len;
        return true;
    }

    public static bool TryRead(ReadOnlySpan<byte> source, ref int offset, out ulong value)
    {
        if (offset < 0 || offset >= source.Length)
        {
            value = 0;
            return false;
        }

        if (!TryDecode(source.Slice(offset), out value, out int bytesRead))
            return false;

        offset += bytesRead;
        return true;
    }

    public static ulong Decode(ReadOnlySpan<byte> source, out int bytesRead)
    {
        if (!TryDecode(source, out ulong value, out bytesRead))
            throw new QuicException(QuicErrorCode.FrameEncodingError, isApplicationError: false, "Truncated QUIC variable-length integer.");
        return value;
    }
}

/// <summary>RFC 9000 §18.2, RFC 9221, RFC 9368, and Google QUIC transport parameter identifiers.</summary>
public static class QuicTransportParameterId
{
    public const ulong OriginalDestinationConnectionId = 0x00;
    public const ulong MaxIdleTimeout = 0x01;
    public const ulong StatelessResetToken = 0x02;
    public const ulong MaxUdpPayloadSize = 0x03;
    public const ulong InitialMaxData = 0x04;
    public const ulong InitialMaxStreamDataBidiLocal = 0x05;
    public const ulong InitialMaxStreamDataBidiRemote = 0x06;
    public const ulong InitialMaxStreamDataUni = 0x07;
    public const ulong InitialMaxStreamsBidi = 0x08;
    public const ulong InitialMaxStreamsUni = 0x09;
    public const ulong AckDelayExponent = 0x0A;
    public const ulong MaxAckDelay = 0x0B;
    public const ulong DisableActiveMigration = 0x0C;
    public const ulong PreferredAddress = 0x0D;
    public const ulong ActiveConnectionIdLimit = 0x0E;
    public const ulong InitialSourceConnectionId = 0x0F;
    public const ulong RetrySourceConnectionId = 0x10;
    public const ulong VersionInformation = 0x11;
    public const ulong MaxDatagramFrameSize = 0x20;
    public const ulong GoogleInitialRtt = 0x3127;
    public const ulong GoogleConnectionOptions = 0x3128;

    public static bool IsGrease(ulong parameterId) => parameterId >= 27UL && (parameterId - 27UL) % 31UL == 0UL;
}

public sealed record QuicVersionInformation(uint ChosenVersion, IReadOnlyList<uint> AvailableVersions);

/// <summary>Decoded or outbound RFC 9000 §18.2 QUIC transport parameters.</summary>
public sealed class QuicTransportParameters
{
    public byte[]? OriginalDestinationConnectionId { get; set; }
    public ulong? MaxIdleTimeoutMs { get; set; }
    public byte[]? StatelessResetToken { get; set; }
    public ulong? MaxUdpPayloadSize { get; set; }
    public ulong? InitialMaxData { get; set; }
    public ulong? InitialMaxStreamDataBidiLocal { get; set; }
    public ulong? InitialMaxStreamDataBidiRemote { get; set; }
    public ulong? InitialMaxStreamDataUni { get; set; }
    public ulong? InitialMaxStreamsBidi { get; set; }
    public ulong? InitialMaxStreamsUni { get; set; }
    public ulong? AckDelayExponent { get; set; }
    public ulong? MaxAckDelayMs { get; set; }
    public bool DisableActiveMigration { get; set; }
    public byte[]? PreferredAddress { get; set; }
    public ulong? ActiveConnectionIdLimit { get; set; }
    public byte[]? InitialSourceConnectionId { get; set; }
    public byte[]? RetrySourceConnectionId { get; set; }
    public QuicVersionInformation? VersionInfo { get; set; }
    public ulong? MaxDatagramFrameSize { get; set; }
    public ulong? GoogleInitialRttUs { get; set; }
    public byte[]? GoogleConnectionOptions { get; set; }
    public List<(ulong Id, byte[] Value)> AdditionalParameters { get; } = new();
}

/// <summary>
/// Wire codec for RFC 9000 §18.2 QUIC transport parameters (<c>quic_transport_parameters</c> TLS extension <c>0x0039</c>).
/// </summary>
public static class QuicTransportParametersCodec
{
    public const int MaxConnectionIdLength = 20;

    public static QuicTransportParameters FromSpec(
        QuicTransportSpec spec,
        ReadOnlySpan<byte> initialSourceConnectionId,
        ulong? initialRttUs = null,
        Random? random = null)
    {
        ArgumentNullException.ThrowIfNull(spec);
        Random rng = random ?? Random.Shared;

        var tp = new QuicTransportParameters
        {
            MaxIdleTimeoutMs = spec.MaxIdleTimeoutMs,
            MaxUdpPayloadSize = spec.ClientTransportDefaultMaxUdpPayloadSize > 0
                ? spec.ClientTransportDefaultMaxUdpPayloadSize
                : spec.MaxUdpPayloadSize,
            InitialMaxData = spec.InitialMaxData,
            InitialMaxStreamDataBidiLocal = spec.InitialMaxStreamDataBidiLocal,
            InitialMaxStreamDataBidiRemote = spec.InitialMaxStreamDataBidiRemote,
            InitialMaxStreamDataUni = spec.InitialMaxStreamDataUni,
            InitialMaxStreamsBidi = spec.InitialMaxStreamsBidi,
            InitialMaxStreamsUni = spec.InitialMaxStreamsUni,
            AckDelayExponent = spec.AckDelayExponent,
            MaxAckDelayMs = spec.MaxAckDelayMs,
            DisableActiveMigration = spec.DisableActiveMigration,
            ActiveConnectionIdLimit = 4,
            InitialSourceConnectionId = initialSourceConnectionId.ToArray(),
            MaxDatagramFrameSize = spec.MaxDatagramFrameSize,
            GoogleInitialRttUs = spec.GoogleInitialRttUs ?? initialRttUs,
            GoogleConnectionOptions = string.IsNullOrEmpty(spec.GoogleConnectionOptions)
                ? null
                : Encoding.ASCII.GetBytes(spec.GoogleConnectionOptions),
        };

        if (spec.QuicVersion != 0)
        {
            var avail = new List<uint>(2) { spec.QuicVersion };
            if (spec.SendGreaseVersionInformation)
                avail.Add(GenerateGreaseVersion(rng));
            tp.VersionInfo = new QuicVersionInformation(spec.QuicVersion, avail);
        }

        if (spec.GreaseTransportParameters)
        {
            ulong greaseId = 31UL * (ulong)rng.Next(1, 0x10_0000) + 27UL;
            int valLen = rng.Next(0, 5);
            var val = new byte[valLen];
            if (valLen > 0)
                rng.NextBytes(val);
            tp.AdditionalParameters.Add((greaseId, val));
        }

        return tp;
    }

    public static byte[] Encode(QuicTransportParameters parameters, bool shuffle = false, Random? random = null)
    {
        ArgumentNullException.ThrowIfNull(parameters);
        var entries = new List<(ulong Id, byte[] Value)>(16);

        void AddBytes(ulong id, byte[]? value)
        {
            if (value is not null)
                entries.Add((id, value));
        }

        void AddVarInt(ulong id, ulong? value)
        {
            if (value.HasValue)
                entries.Add((id, QuicVarInt.Encode(value.Value)));
        }

        AddBytes(QuicTransportParameterId.OriginalDestinationConnectionId, parameters.OriginalDestinationConnectionId);
        AddVarInt(QuicTransportParameterId.MaxIdleTimeout, parameters.MaxIdleTimeoutMs);
        AddBytes(QuicTransportParameterId.StatelessResetToken, parameters.StatelessResetToken);
        AddVarInt(QuicTransportParameterId.MaxUdpPayloadSize, parameters.MaxUdpPayloadSize);
        AddVarInt(QuicTransportParameterId.InitialMaxData, parameters.InitialMaxData);
        AddVarInt(QuicTransportParameterId.InitialMaxStreamDataBidiLocal, parameters.InitialMaxStreamDataBidiLocal);
        AddVarInt(QuicTransportParameterId.InitialMaxStreamDataBidiRemote, parameters.InitialMaxStreamDataBidiRemote);
        AddVarInt(QuicTransportParameterId.InitialMaxStreamDataUni, parameters.InitialMaxStreamDataUni);
        AddVarInt(QuicTransportParameterId.InitialMaxStreamsBidi, parameters.InitialMaxStreamsBidi);
        AddVarInt(QuicTransportParameterId.InitialMaxStreamsUni, parameters.InitialMaxStreamsUni);
        AddVarInt(QuicTransportParameterId.AckDelayExponent, parameters.AckDelayExponent);
        AddVarInt(QuicTransportParameterId.MaxAckDelay, parameters.MaxAckDelayMs);
        if (parameters.DisableActiveMigration)
            entries.Add((QuicTransportParameterId.DisableActiveMigration, Array.Empty<byte>()));
        AddBytes(QuicTransportParameterId.PreferredAddress, parameters.PreferredAddress);
        AddVarInt(QuicTransportParameterId.ActiveConnectionIdLimit, parameters.ActiveConnectionIdLimit);
        AddBytes(QuicTransportParameterId.InitialSourceConnectionId, parameters.InitialSourceConnectionId);
        AddBytes(QuicTransportParameterId.RetrySourceConnectionId, parameters.RetrySourceConnectionId);

        if (parameters.VersionInfo is { } vi)
        {
            var buf = new byte[4 + vi.AvailableVersions.Count * 4];
            BinaryPrimitives.WriteUInt32BigEndian(buf.AsSpan(0, 4), vi.ChosenVersion);
            for (int i = 0; i < vi.AvailableVersions.Count; i++)
                BinaryPrimitives.WriteUInt32BigEndian(buf.AsSpan(4 + i * 4, 4), vi.AvailableVersions[i]);
            entries.Add((QuicTransportParameterId.VersionInformation, buf));
        }

        AddVarInt(QuicTransportParameterId.MaxDatagramFrameSize, parameters.MaxDatagramFrameSize);
        AddVarInt(QuicTransportParameterId.GoogleInitialRtt, parameters.GoogleInitialRttUs);
        AddBytes(QuicTransportParameterId.GoogleConnectionOptions, parameters.GoogleConnectionOptions);

        for (int i = 0; i < parameters.AdditionalParameters.Count; i++)
            entries.Add(parameters.AdditionalParameters[i]);

        if (shuffle && entries.Count > 1)
        {
            Random rng = random ?? Random.Shared;
            for (int i = entries.Count - 1; i >= 1; i--)
            {
                int j = rng.Next(0, i + 1);
                (entries[i], entries[j]) = (entries[j], entries[i]);
            }
        }

        var ms = new MemoryStream(entries.Count * 8);
        for (int i = 0; i < entries.Count; i++)
        {
            (ulong id, byte[] val) = entries[i];
            QuicVarInt.Write(ms, id);
            QuicVarInt.Write(ms, (ulong)val.Length);
            if (val.Length > 0)
                ms.Write(val);
        }

        return ms.ToArray();
    }

    public static QuicTransportParameters Decode(ReadOnlySpan<byte> data, bool isServerParameters = true)
    {
        var tp = new QuicTransportParameters();
        var seenIds = new HashSet<ulong>();
        int offset = 0;

        while (offset < data.Length)
        {
            if (!QuicVarInt.TryRead(data, ref offset, out ulong paramId) ||
                !QuicVarInt.TryRead(data, ref offset, out ulong len))
            {
                throw new QuicException(QuicErrorCode.TransportParameterError, false, "Truncated QUIC transport parameter header.");
            }

            if (len > (ulong)(data.Length - offset))
                throw new QuicException(QuicErrorCode.TransportParameterError, false, $"Truncated QUIC transport parameter 0x{paramId:X}.");

            if (!seenIds.Add(paramId))
                throw new QuicException(QuicErrorCode.TransportParameterError, false, $"Duplicate QUIC transport parameter 0x{paramId:X}.");

            ReadOnlySpan<byte> val = data.Slice(offset, (int)len);
            offset += (int)len;

            switch (paramId)
            {
                case QuicTransportParameterId.OriginalDestinationConnectionId:
                    if (!isServerParameters)
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, "Client must not send original_destination_connection_id.");
                    if (val.Length > MaxConnectionIdLength)
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, "original_destination_connection_id exceeds 20 bytes.");
                    tp.OriginalDestinationConnectionId = val.ToArray();
                    break;

                case QuicTransportParameterId.MaxIdleTimeout:
                    tp.MaxIdleTimeoutMs = DecodeExactVarInt(val, paramId);
                    break;

                case QuicTransportParameterId.StatelessResetToken:
                    if (!isServerParameters)
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, "Client must not send stateless_reset_token.");
                    if (val.Length != 16)
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, $"stateless_reset_token must be 16 bytes (got {val.Length}).");
                    tp.StatelessResetToken = val.ToArray();
                    break;

                case QuicTransportParameterId.MaxUdpPayloadSize:
                {
                    ulong maxUdp = DecodeExactVarInt(val, paramId);
                    if (maxUdp < 1200)
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, $"max_udp_payload_size {maxUdp} < 1200.");
                    tp.MaxUdpPayloadSize = maxUdp;
                    break;
                }

                case QuicTransportParameterId.InitialMaxData:
                    tp.InitialMaxData = DecodeExactVarInt(val, paramId);
                    break;

                case QuicTransportParameterId.InitialMaxStreamDataBidiLocal:
                    tp.InitialMaxStreamDataBidiLocal = DecodeExactVarInt(val, paramId);
                    break;

                case QuicTransportParameterId.InitialMaxStreamDataBidiRemote:
                    tp.InitialMaxStreamDataBidiRemote = DecodeExactVarInt(val, paramId);
                    break;

                case QuicTransportParameterId.InitialMaxStreamDataUni:
                    tp.InitialMaxStreamDataUni = DecodeExactVarInt(val, paramId);
                    break;

                case QuicTransportParameterId.InitialMaxStreamsBidi:
                {
                    ulong maxStreams = DecodeExactVarInt(val, paramId);
                    if (maxStreams > (1UL << 60))
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, "initial_max_streams_bidi exceeds 2^60.");
                    tp.InitialMaxStreamsBidi = maxStreams;
                    break;
                }

                case QuicTransportParameterId.InitialMaxStreamsUni:
                {
                    ulong maxStreams = DecodeExactVarInt(val, paramId);
                    if (maxStreams > (1UL << 60))
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, "initial_max_streams_uni exceeds 2^60.");
                    tp.InitialMaxStreamsUni = maxStreams;
                    break;
                }

                case QuicTransportParameterId.AckDelayExponent:
                {
                    ulong exp = DecodeExactVarInt(val, paramId);
                    if (exp > 20)
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, $"ack_delay_exponent {exp} > 20.");
                    tp.AckDelayExponent = exp;
                    break;
                }

                case QuicTransportParameterId.MaxAckDelay:
                {
                    ulong delay = DecodeExactVarInt(val, paramId);
                    if (delay >= 16_384)
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, $"max_ack_delay {delay} >= 16384.");
                    tp.MaxAckDelayMs = delay;
                    break;
                }

                case QuicTransportParameterId.DisableActiveMigration:
                    if (!val.IsEmpty)
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, "disable_active_migration must have zero-length value.");
                    tp.DisableActiveMigration = true;
                    break;

                case QuicTransportParameterId.PreferredAddress:
                    if (!isServerParameters)
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, "Client must not send preferred_address.");
                    tp.PreferredAddress = val.ToArray();
                    break;

                case QuicTransportParameterId.ActiveConnectionIdLimit:
                {
                    ulong limit = DecodeExactVarInt(val, paramId);
                    if (limit < 2)
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, $"active_connection_id_limit {limit} < 2.");
                    tp.ActiveConnectionIdLimit = limit;
                    break;
                }

                case QuicTransportParameterId.InitialSourceConnectionId:
                    if (val.Length > MaxConnectionIdLength)
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, "initial_source_connection_id exceeds 20 bytes.");
                    tp.InitialSourceConnectionId = val.ToArray();
                    break;

                case QuicTransportParameterId.RetrySourceConnectionId:
                    if (!isServerParameters)
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, "Client must not send retry_source_connection_id.");
                    if (val.Length > MaxConnectionIdLength)
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, "retry_source_connection_id exceeds 20 bytes.");
                    tp.RetrySourceConnectionId = val.ToArray();
                    break;

                case QuicTransportParameterId.VersionInformation:
                {
                    if (val.Length < 4 || val.Length % 4 != 0)
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, "Invalid version_information length.");
                    uint chosen = BinaryPrimitives.ReadUInt32BigEndian(val.Slice(0, 4));
                    if (chosen == 0)
                        throw new QuicException(QuicErrorCode.TransportParameterError, false, "version_information chosen_version must be non-zero.");
                    var avail = new uint[(val.Length - 4) / 4];
                    for (int i = 0; i < avail.Length; i++)
                        avail[i] = BinaryPrimitives.ReadUInt32BigEndian(val.Slice(4 + i * 4, 4));
                    tp.VersionInfo = new QuicVersionInformation(chosen, avail);
                    break;
                }

                case QuicTransportParameterId.MaxDatagramFrameSize:
                    tp.MaxDatagramFrameSize = DecodeExactVarInt(val, paramId);
                    break;

                case QuicTransportParameterId.GoogleInitialRtt:
                    tp.GoogleInitialRttUs = DecodeExactVarInt(val, paramId);
                    break;

                case QuicTransportParameterId.GoogleConnectionOptions:
                    tp.GoogleConnectionOptions = val.ToArray();
                    break;

                default:
                    tp.AdditionalParameters.Add((paramId, val.ToArray()));
                    break;
            }
        }

        return tp;
    }

    private static ulong DecodeExactVarInt(ReadOnlySpan<byte> valueBytes, ulong paramId)
    {
        if (!QuicVarInt.TryDecode(valueBytes, out ulong val, out int bytesRead) || bytesRead != valueBytes.Length)
            throw new QuicException(QuicErrorCode.TransportParameterError, false, $"Invalid integer encoding for transport parameter 0x{paramId:X}.");
        return val;
    }

    private static uint GenerateGreaseVersion(Random rng)
    {
        byte b0 = (byte)((rng.Next(16) << 4) | 0x0A);
        byte b1 = (byte)((rng.Next(16) << 4) | 0x0A);
        byte b2 = (byte)((rng.Next(16) << 4) | 0x0A);
        byte b3 = (byte)((rng.Next(16) << 4) | 0x0A);
        return ((uint)b0 << 24) | ((uint)b1 << 16) | ((uint)b2 << 8) | b3;
    }
}
