using System.Text;
using Cybersole.Http.Protocol;
using Cybersole.Http.Tls;

namespace Cybersole.Http.Quic;

public static class QuicFrameType
{
    public const ulong Padding = 0x00;
    public const ulong Ping = 0x01;
    public const ulong Ack = 0x02;
    public const ulong AckEcn = 0x03;
    public const ulong ResetStream = 0x04;
    public const ulong StopSending = 0x05;
    public const ulong Crypto = 0x06;
    public const ulong NewToken = 0x07;
    public const ulong StreamBase = 0x08;
    public const ulong StreamMax = 0x0F;
    public const ulong MaxData = 0x10;
    public const ulong MaxStreamData = 0x11;
    public const ulong MaxStreamsBidi = 0x12;
    public const ulong MaxStreamsUni = 0x13;
    public const ulong DataBlocked = 0x14;
    public const ulong StreamDataBlocked = 0x15;
    public const ulong StreamsBlockedBidi = 0x16;
    public const ulong StreamsBlockedUni = 0x17;
    public const ulong NewConnectionId = 0x18;
    public const ulong RetireConnectionId = 0x19;
    public const ulong PathChallenge = 0x1A;
    public const ulong PathResponse = 0x1B;
    public const ulong ConnectionCloseTransport = 0x1C;
    public const ulong ConnectionCloseApplication = 0x1D;
    public const ulong HandshakeDone = 0x1E;
    public const ulong DatagramNoLen = 0x30;
    public const ulong DatagramWithLen = 0x31;
}

public readonly record struct QuicAckRange(ulong Gap, ulong AckRangeLength);

public abstract record QuicFrame
{
    public abstract ulong FrameType { get; }
    public virtual bool IsAckEliciting => true;
    public abstract int GetEncodedLength();
    public abstract void WriteTo(List<byte> destination);

    public byte[] ToArray()
    {
        var list = new List<byte>(GetEncodedLength());
        WriteTo(list);
        return list.ToArray();
    }
}

public sealed record QuicPaddingFrame(int Count = 1) : QuicFrame
{
    public override ulong FrameType => QuicFrameType.Padding;
    public override bool IsAckEliciting => false;
    public override int GetEncodedLength() => Math.Max(0, Count);

    public override void WriteTo(List<byte> destination)
    {
        for (int i = 0; i < Count; i++)
            destination.Add(0x00);
    }
}

public sealed record QuicPingFrame : QuicFrame
{
    public static readonly QuicPingFrame Instance = new();
    public override ulong FrameType => QuicFrameType.Ping;
    public override int GetEncodedLength() => 1;
    public override void WriteTo(List<byte> destination) => destination.Add(0x01);
}

public sealed record QuicAckFrame(
    ulong LargestAcknowledged,
    ulong AckDelay,
    ulong FirstAckRange,
    IReadOnlyList<QuicAckRange> AdditionalRanges,
    ulong Ect0Count = 0,
    ulong Ect1Count = 0,
    ulong EcnCeCount = 0,
    bool HasEcn = false) : QuicFrame
{
    public override ulong FrameType => HasEcn ? QuicFrameType.AckEcn : QuicFrameType.Ack;
    public override bool IsAckEliciting => false;

    public override int GetEncodedLength()
    {
        int len = 1
            + QuicVarInt.GetEncodedLength(LargestAcknowledged)
            + QuicVarInt.GetEncodedLength(AckDelay)
            + QuicVarInt.GetEncodedLength((ulong)AdditionalRanges.Count)
            + QuicVarInt.GetEncodedLength(FirstAckRange);
        for (int i = 0; i < AdditionalRanges.Count; i++)
        {
            len += QuicVarInt.GetEncodedLength(AdditionalRanges[i].Gap);
            len += QuicVarInt.GetEncodedLength(AdditionalRanges[i].AckRangeLength);
        }
        if (HasEcn)
        {
            len += QuicVarInt.GetEncodedLength(Ect0Count);
            len += QuicVarInt.GetEncodedLength(Ect1Count);
            len += QuicVarInt.GetEncodedLength(EcnCeCount);
        }
        return len;
    }

    public override void WriteTo(List<byte> destination)
    {
        destination.Add(HasEcn ? (byte)0x03 : (byte)0x02);
        QuicVarInt.Write(destination, LargestAcknowledged);
        QuicVarInt.Write(destination, AckDelay);
        QuicVarInt.Write(destination, (ulong)AdditionalRanges.Count);
        QuicVarInt.Write(destination, FirstAckRange);
        for (int i = 0; i < AdditionalRanges.Count; i++)
        {
            QuicVarInt.Write(destination, AdditionalRanges[i].Gap);
            QuicVarInt.Write(destination, AdditionalRanges[i].AckRangeLength);
        }
        if (HasEcn)
        {
            QuicVarInt.Write(destination, Ect0Count);
            QuicVarInt.Write(destination, Ect1Count);
            QuicVarInt.Write(destination, EcnCeCount);
        }
    }

    public List<(ulong Start, ulong End)> GetAcknowledgedRanges()
    {
        var result = new List<(ulong Start, ulong End)>(1 + AdditionalRanges.Count);
        if (FirstAckRange > LargestAcknowledged)
            throw new QuicException(QuicErrorCode.FrameEncodingError, false, "ACK first_ack_range exceeds largest_acknowledged.");

        ulong smallest = LargestAcknowledged - FirstAckRange;
        result.Add((smallest, LargestAcknowledged));

        for (int i = 0; i < AdditionalRanges.Count; i++)
        {
            QuicAckRange r = AdditionalRanges[i];
            if (smallest < r.Gap + 2UL)
                throw new QuicException(QuicErrorCode.FrameEncodingError, false, "ACK range gap underflows packet number space.");
            ulong largest = smallest - r.Gap - 2UL;
            if (r.AckRangeLength > largest)
                throw new QuicException(QuicErrorCode.FrameEncodingError, false, "ACK range length underflows packet number space.");
            smallest = largest - r.AckRangeLength;
            result.Add((smallest, largest));
        }

        return result;
    }

    public static QuicAckFrame FromPacketNumbers(IReadOnlyCollection<ulong> packetNumbers, ulong ackDelayEncoded = 0)
    {
        if (packetNumbers.Count == 0)
            throw new ArgumentException("ACK frame requires at least one packet number.", nameof(packetNumbers));

        var sorted = new List<ulong>(packetNumbers);
        sorted.Sort((a, b) => b.CompareTo(a)); // descending

        var ranges = new List<(ulong Start, ulong End)>();
        ulong rangeEnd = sorted[0];
        ulong rangeStart = sorted[0];
        for (int i = 1; i < sorted.Count; i++)
        {
            ulong pn = sorted[i];
            if (pn == rangeStart)
                continue;
            if (pn + 1UL == rangeStart)
            {
                rangeStart = pn;
            }
            else
            {
                ranges.Add((rangeStart, rangeEnd));
                rangeEnd = pn;
                rangeStart = pn;
            }
        }
        ranges.Add((rangeStart, rangeEnd));

        ulong largest = ranges[0].End;
        ulong firstRange = ranges[0].End - ranges[0].Start;
        var additional = new List<QuicAckRange>(Math.Max(0, ranges.Count - 1));
        ulong prevSmallest = ranges[0].Start;
        for (int i = 1; i < ranges.Count; i++)
        {
            (ulong s, ulong e) = ranges[i];
            ulong gap = prevSmallest - e - 2UL;
            ulong len = e - s;
            additional.Add(new QuicAckRange(gap, len));
            prevSmallest = s;
        }

        return new QuicAckFrame(largest, ackDelayEncoded, firstRange, additional);
    }
}

public sealed record QuicResetStreamFrame(ulong StreamId, ulong ApplicationErrorCode, ulong FinalSize) : QuicFrame
{
    public override ulong FrameType => QuicFrameType.ResetStream;

    public override int GetEncodedLength() =>
        1 + QuicVarInt.GetEncodedLength(StreamId)
        + QuicVarInt.GetEncodedLength(ApplicationErrorCode)
        + QuicVarInt.GetEncodedLength(FinalSize);

    public override void WriteTo(List<byte> destination)
    {
        destination.Add(0x04);
        QuicVarInt.Write(destination, StreamId);
        QuicVarInt.Write(destination, ApplicationErrorCode);
        QuicVarInt.Write(destination, FinalSize);
    }
}

public sealed record QuicStopSendingFrame(ulong StreamId, ulong ApplicationErrorCode) : QuicFrame
{
    public override ulong FrameType => QuicFrameType.StopSending;

    public override int GetEncodedLength() =>
        1 + QuicVarInt.GetEncodedLength(StreamId) + QuicVarInt.GetEncodedLength(ApplicationErrorCode);

    public override void WriteTo(List<byte> destination)
    {
        destination.Add(0x05);
        QuicVarInt.Write(destination, StreamId);
        QuicVarInt.Write(destination, ApplicationErrorCode);
    }
}

public sealed record QuicCryptoFrame(ulong Offset, byte[] Data) : QuicFrame
{
    public override ulong FrameType => QuicFrameType.Crypto;

    public override int GetEncodedLength() =>
        1 + QuicVarInt.GetEncodedLength(Offset) + QuicVarInt.GetEncodedLength((ulong)Data.Length) + Data.Length;

    public override void WriteTo(List<byte> destination)
    {
        destination.Add(0x06);
        QuicVarInt.Write(destination, Offset);
        QuicVarInt.Write(destination, (ulong)Data.Length);
        destination.AddRange(Data);
    }
}

public sealed record QuicNewTokenFrame(byte[] Token) : QuicFrame
{
    public override ulong FrameType => QuicFrameType.NewToken;

    public override int GetEncodedLength() =>
        1 + QuicVarInt.GetEncodedLength((ulong)Token.Length) + Token.Length;

    public override void WriteTo(List<byte> destination)
    {
        destination.Add(0x07);
        QuicVarInt.Write(destination, (ulong)Token.Length);
        destination.AddRange(Token);
    }
}

public sealed record QuicStreamFrame(
    ulong StreamId,
    ulong Offset,
    byte[] Data,
    bool Fin,
    bool HasLength = true) : QuicFrame
{
    public override ulong FrameType
    {
        get
        {
            ulong t = QuicFrameType.StreamBase;
            if (Offset > 0) t |= 0x04;
            if (HasLength) t |= 0x02;
            if (Fin) t |= 0x01;
            return t;
        }
    }

    public override int GetEncodedLength()
    {
        int len = 1 + QuicVarInt.GetEncodedLength(StreamId);
        if (Offset > 0)
            len += QuicVarInt.GetEncodedLength(Offset);
        if (HasLength)
            len += QuicVarInt.GetEncodedLength((ulong)Data.Length);
        return len + Data.Length;
    }

    public override void WriteTo(List<byte> destination)
    {
        destination.Add((byte)FrameType);
        QuicVarInt.Write(destination, StreamId);
        if (Offset > 0)
            QuicVarInt.Write(destination, Offset);
        if (HasLength)
            QuicVarInt.Write(destination, (ulong)Data.Length);
        if (Data.Length > 0)
            destination.AddRange(Data);
    }
}

public sealed record QuicMaxDataFrame(ulong MaximumData) : QuicFrame
{
    public override ulong FrameType => QuicFrameType.MaxData;
    public override int GetEncodedLength() => 1 + QuicVarInt.GetEncodedLength(MaximumData);

    public override void WriteTo(List<byte> destination)
    {
        destination.Add(0x10);
        QuicVarInt.Write(destination, MaximumData);
    }
}

public sealed record QuicMaxStreamDataFrame(ulong StreamId, ulong MaximumStreamData) : QuicFrame
{
    public override ulong FrameType => QuicFrameType.MaxStreamData;

    public override int GetEncodedLength() =>
        1 + QuicVarInt.GetEncodedLength(StreamId) + QuicVarInt.GetEncodedLength(MaximumStreamData);

    public override void WriteTo(List<byte> destination)
    {
        destination.Add(0x11);
        QuicVarInt.Write(destination, StreamId);
        QuicVarInt.Write(destination, MaximumStreamData);
    }
}

public sealed record QuicMaxStreamsFrame(ulong MaximumStreams, bool IsBidirectional) : QuicFrame
{
    public override ulong FrameType => IsBidirectional ? QuicFrameType.MaxStreamsBidi : QuicFrameType.MaxStreamsUni;
    public override int GetEncodedLength() => 1 + QuicVarInt.GetEncodedLength(MaximumStreams);

    public override void WriteTo(List<byte> destination)
    {
        destination.Add(IsBidirectional ? (byte)0x12 : (byte)0x13);
        QuicVarInt.Write(destination, MaximumStreams);
    }
}

public sealed record QuicDataBlockedFrame(ulong MaximumData) : QuicFrame
{
    public override ulong FrameType => QuicFrameType.DataBlocked;
    public override int GetEncodedLength() => 1 + QuicVarInt.GetEncodedLength(MaximumData);

    public override void WriteTo(List<byte> destination)
    {
        destination.Add(0x14);
        QuicVarInt.Write(destination, MaximumData);
    }
}

public sealed record QuicStreamDataBlockedFrame(ulong StreamId, ulong MaximumStreamData) : QuicFrame
{
    public override ulong FrameType => QuicFrameType.StreamDataBlocked;

    public override int GetEncodedLength() =>
        1 + QuicVarInt.GetEncodedLength(StreamId) + QuicVarInt.GetEncodedLength(MaximumStreamData);

    public override void WriteTo(List<byte> destination)
    {
        destination.Add(0x15);
        QuicVarInt.Write(destination, StreamId);
        QuicVarInt.Write(destination, MaximumStreamData);
    }
}

public sealed record QuicStreamsBlockedFrame(ulong MaximumStreams, bool IsBidirectional) : QuicFrame
{
    public override ulong FrameType => IsBidirectional ? QuicFrameType.StreamsBlockedBidi : QuicFrameType.StreamsBlockedUni;
    public override int GetEncodedLength() => 1 + QuicVarInt.GetEncodedLength(MaximumStreams);

    public override void WriteTo(List<byte> destination)
    {
        destination.Add(IsBidirectional ? (byte)0x16 : (byte)0x17);
        QuicVarInt.Write(destination, MaximumStreams);
    }
}

public sealed record QuicNewConnectionIdFrame(
    ulong SequenceNumber,
    ulong RetirePriorTo,
    byte[] ConnectionId,
    byte[] StatelessResetToken) : QuicFrame
{
    public override ulong FrameType => QuicFrameType.NewConnectionId;

    public override int GetEncodedLength() =>
        1 + QuicVarInt.GetEncodedLength(SequenceNumber)
        + QuicVarInt.GetEncodedLength(RetirePriorTo)
        + 1 + ConnectionId.Length + 16;

    public override void WriteTo(List<byte> destination)
    {
        if (ConnectionId.Length is < 1 or > 20)
            throw new ArgumentOutOfRangeException(nameof(ConnectionId), "NEW_CONNECTION_ID length must be 1..20 bytes.");
        if (StatelessResetToken.Length != 16)
            throw new ArgumentOutOfRangeException(nameof(StatelessResetToken), "Stateless reset token must be 16 bytes.");

        destination.Add(0x18);
        QuicVarInt.Write(destination, SequenceNumber);
        QuicVarInt.Write(destination, RetirePriorTo);
        destination.Add((byte)ConnectionId.Length);
        destination.AddRange(ConnectionId);
        destination.AddRange(StatelessResetToken);
    }
}

public sealed record QuicRetireConnectionIdFrame(ulong SequenceNumber) : QuicFrame
{
    public override ulong FrameType => QuicFrameType.RetireConnectionId;
    public override int GetEncodedLength() => 1 + QuicVarInt.GetEncodedLength(SequenceNumber);

    public override void WriteTo(List<byte> destination)
    {
        destination.Add(0x19);
        QuicVarInt.Write(destination, SequenceNumber);
    }
}

public sealed record QuicPathChallengeFrame(byte[] Data) : QuicFrame
{
    public override ulong FrameType => QuicFrameType.PathChallenge;
    public override int GetEncodedLength() => 9;

    public override void WriteTo(List<byte> destination)
    {
        if (Data.Length != 8)
            throw new ArgumentOutOfRangeException(nameof(Data), "PATH_CHALLENGE data must be 8 bytes.");
        destination.Add(0x1A);
        destination.AddRange(Data);
    }
}

public sealed record QuicPathResponseFrame(byte[] Data) : QuicFrame
{
    public override ulong FrameType => QuicFrameType.PathResponse;
    public override int GetEncodedLength() => 9;

    public override void WriteTo(List<byte> destination)
    {
        if (Data.Length != 8)
            throw new ArgumentOutOfRangeException(nameof(Data), "PATH_RESPONSE data must be 8 bytes.");
        destination.Add(0x1B);
        destination.AddRange(Data);
    }
}

public sealed record QuicConnectionCloseFrame(
    ulong ErrorCode,
    ulong OffendingFrameType,
    string ReasonPhrase,
    bool IsApplicationError) : QuicFrame
{
    public override ulong FrameType => IsApplicationError
        ? QuicFrameType.ConnectionCloseApplication
        : QuicFrameType.ConnectionCloseTransport;

    public override bool IsAckEliciting => false;

    public override int GetEncodedLength()
    {
        int reasonLen = string.IsNullOrEmpty(ReasonPhrase) ? 0 : Encoding.UTF8.GetByteCount(ReasonPhrase);
        int len = 1 + QuicVarInt.GetEncodedLength(ErrorCode);
        if (!IsApplicationError)
            len += QuicVarInt.GetEncodedLength(OffendingFrameType);
        len += QuicVarInt.GetEncodedLength((ulong)reasonLen) + reasonLen;
        return len;
    }

    public override void WriteTo(List<byte> destination)
    {
        byte[] reasonBytes = string.IsNullOrEmpty(ReasonPhrase)
            ? Array.Empty<byte>()
            : Encoding.UTF8.GetBytes(ReasonPhrase);

        destination.Add(IsApplicationError ? (byte)0x1D : (byte)0x1C);
        QuicVarInt.Write(destination, ErrorCode);
        if (!IsApplicationError)
            QuicVarInt.Write(destination, OffendingFrameType);
        QuicVarInt.Write(destination, (ulong)reasonBytes.Length);
        if (reasonBytes.Length > 0)
            destination.AddRange(reasonBytes);
    }
}

public sealed record QuicHandshakeDoneFrame : QuicFrame
{
    public static readonly QuicHandshakeDoneFrame Instance = new();
    public override ulong FrameType => QuicFrameType.HandshakeDone;
    public override int GetEncodedLength() => 1;
    public override void WriteTo(List<byte> destination) => destination.Add(0x1E);
}

public sealed record QuicDatagramFrame(byte[] Data, bool HasLength = true) : QuicFrame
{
    public override ulong FrameType => HasLength ? QuicFrameType.DatagramWithLen : QuicFrameType.DatagramNoLen;

    public override int GetEncodedLength() =>
        1 + (HasLength ? QuicVarInt.GetEncodedLength((ulong)Data.Length) : 0) + Data.Length;

    public override void WriteTo(List<byte> destination)
    {
        destination.Add(HasLength ? (byte)0x31 : (byte)0x30);
        if (HasLength)
            QuicVarInt.Write(destination, (ulong)Data.Length);
        if (Data.Length > 0)
            destination.AddRange(Data);
    }
}

/// <summary>RFC 9000 §19 &amp; RFC 9221 QUIC frame wire codec.</summary>
public static class QuicFrameCodec
{
    public static byte[] Encode(IReadOnlyList<QuicFrame> frames)
    {
        ArgumentNullException.ThrowIfNull(frames);
        int cap = 0;
        for (int i = 0; i < frames.Count; i++)
            cap += frames[i].GetEncodedLength();

        var buf = new List<byte>(cap);
        for (int i = 0; i < frames.Count; i++)
            frames[i].WriteTo(buf);
        return buf.ToArray();
    }

    public static List<QuicFrame> DecodeAll(ReadOnlySpan<byte> payload, QuicEncryptionLevel? validateLevel = null)
    {
        var frames = new List<QuicFrame>();
        int offset = 0;
        while (offset < payload.Length)
        {
            QuicFrame frame = DecodeNext(payload, ref offset);
            if (validateLevel.HasValue && !IsAllowedAtLevel(frame, validateLevel.Value))
            {
                throw new QuicException(
                    QuicErrorCode.ProtocolViolation,
                    false,
                    $"QUIC frame type 0x{frame.FrameType:X} is not allowed at encryption level {validateLevel.Value}.");
            }
            frames.Add(frame);
        }
        return frames;
    }

    public static bool IsAllowedAtLevel(QuicFrame frame, QuicEncryptionLevel level) => level switch
    {
        QuicEncryptionLevel.Initial or QuicEncryptionLevel.Handshake =>
            frame is QuicPaddingFrame or QuicPingFrame or QuicAckFrame or QuicCryptoFrame
            or QuicConnectionCloseFrame { IsApplicationError: false },
        QuicEncryptionLevel.Application => true,
        QuicEncryptionLevel.EarlyData =>
            frame is not (QuicAckFrame or QuicCryptoFrame or QuicNewTokenFrame or QuicHandshakeDoneFrame or QuicPathResponseFrame or QuicRetireConnectionIdFrame),
        _ => false,
    };

    public static QuicFrame DecodeNext(ReadOnlySpan<byte> payload, ref int offset)
    {
        if (!QuicVarInt.TryRead(payload, ref offset, out ulong frameType))
            throw new QuicException(QuicErrorCode.FrameEncodingError, false, "Truncated QUIC frame type.");

        if (frameType == QuicFrameType.Padding)
        {
            int count = 1;
            while (offset < payload.Length && payload[offset] == 0x00)
            {
                count++;
                offset++;
            }
            return new QuicPaddingFrame(count);
        }

        if (frameType == QuicFrameType.Ping)
            return QuicPingFrame.Instance;

        if (frameType is QuicFrameType.Ack or QuicFrameType.AckEcn)
        {
            bool hasEcn = frameType == QuicFrameType.AckEcn;
            ulong largest = ReadVarInt(payload, ref offset, "ACK largest_acknowledged");
            ulong ackDelay = ReadVarInt(payload, ref offset, "ACK ack_delay");
            ulong rangeCount = ReadVarInt(payload, ref offset, "ACK ack_range_count");
            ulong firstRange = ReadVarInt(payload, ref offset, "ACK first_ack_range");

            if (firstRange > largest)
                throw new QuicException(QuicErrorCode.FrameEncodingError, false, "ACK first_ack_range exceeds largest_acknowledged.");
            if (rangeCount > (ulong)(payload.Length - offset))
                throw new QuicException(QuicErrorCode.FrameEncodingError, false, "ACK range count exceeds remaining payload.");

            var additional = rangeCount == 0
                ? (IReadOnlyList<QuicAckRange>)Array.Empty<QuicAckRange>()
                : new List<QuicAckRange>((int)rangeCount);

            var additionalList = additional as List<QuicAckRange>;
            ulong smallest = largest - firstRange;
            for (ulong i = 0; i < rangeCount; i++)
            {
                ulong gap = ReadVarInt(payload, ref offset, "ACK gap");
                ulong rangeLen = ReadVarInt(payload, ref offset, "ACK ack_range_length");
                if (smallest < gap + 2UL)
                    throw new QuicException(QuicErrorCode.FrameEncodingError, false, "ACK gap underflows packet number space.");
                ulong rangeLargest = smallest - gap - 2UL;
                if (rangeLen > rangeLargest)
                    throw new QuicException(QuicErrorCode.FrameEncodingError, false, "ACK range length underflows packet number space.");
                smallest = rangeLargest - rangeLen;
                additionalList!.Add(new QuicAckRange(gap, rangeLen));
            }

            ulong ect0 = 0, ect1 = 0, ecnCe = 0;
            if (hasEcn)
            {
                ect0 = ReadVarInt(payload, ref offset, "ACK ect0");
                ect1 = ReadVarInt(payload, ref offset, "ACK ect1");
                ecnCe = ReadVarInt(payload, ref offset, "ACK ecn_ce");
            }

            return new QuicAckFrame(largest, ackDelay, firstRange, additional, ect0, ect1, ecnCe, hasEcn);
        }

        if (frameType == QuicFrameType.ResetStream)
        {
            ulong streamId = ReadVarInt(payload, ref offset, "RESET_STREAM stream_id");
            ulong errCode = ReadVarInt(payload, ref offset, "RESET_STREAM error_code");
            ulong finalSize = ReadVarInt(payload, ref offset, "RESET_STREAM final_size");
            return new QuicResetStreamFrame(streamId, errCode, finalSize);
        }

        if (frameType == QuicFrameType.StopSending)
        {
            ulong streamId = ReadVarInt(payload, ref offset, "STOP_SENDING stream_id");
            ulong errCode = ReadVarInt(payload, ref offset, "STOP_SENDING error_code");
            return new QuicStopSendingFrame(streamId, errCode);
        }

        if (frameType == QuicFrameType.Crypto)
        {
            ulong cryptoOffset = ReadVarInt(payload, ref offset, "CRYPTO offset");
            byte[] data = ReadLengthPrefixedBytes(payload, ref offset, "CRYPTO data");
            return new QuicCryptoFrame(cryptoOffset, data);
        }

        if (frameType == QuicFrameType.NewToken)
        {
            byte[] token = ReadLengthPrefixedBytes(payload, ref offset, "NEW_TOKEN token");
            if (token.Length == 0)
                throw new QuicException(QuicErrorCode.FrameEncodingError, false, "NEW_TOKEN token length cannot be 0.");
            return new QuicNewTokenFrame(token);
        }

        if (frameType >= QuicFrameType.StreamBase && frameType <= QuicFrameType.StreamMax)
        {
            bool hasOff = (frameType & 0x04) != 0;
            bool hasLen = (frameType & 0x02) != 0;
            bool fin = (frameType & 0x01) != 0;

            ulong streamId = ReadVarInt(payload, ref offset, "STREAM stream_id");
            ulong streamOffset = hasOff ? ReadVarInt(payload, ref offset, "STREAM offset") : 0UL;
            byte[] data;
            if (hasLen)
            {
                data = ReadLengthPrefixedBytes(payload, ref offset, "STREAM data");
            }
            else
            {
                data = payload.Slice(offset).ToArray();
                offset = payload.Length;
            }

            if (streamOffset + (ulong)data.Length > QuicVarInt.MaxValue)
                throw new QuicException(QuicErrorCode.FrameEncodingError, false, "STREAM offset + length exceeds 2^62 - 1.");

            return new QuicStreamFrame(streamId, streamOffset, data, fin, hasLen);
        }

        switch (frameType)
        {
            case QuicFrameType.MaxData:
                return new QuicMaxDataFrame(ReadVarInt(payload, ref offset, "MAX_DATA"));

            case QuicFrameType.MaxStreamData:
                return new QuicMaxStreamDataFrame(
                    ReadVarInt(payload, ref offset, "MAX_STREAM_DATA stream_id"),
                    ReadVarInt(payload, ref offset, "MAX_STREAM_DATA max_stream_data"));

            case QuicFrameType.MaxStreamsBidi:
            case QuicFrameType.MaxStreamsUni:
            {
                ulong maxStreams = ReadVarInt(payload, ref offset, "MAX_STREAMS");
                if (maxStreams > (1UL << 60))
                    throw new QuicException(QuicErrorCode.FrameEncodingError, false, "MAX_STREAMS exceeds 2^60.");
                return new QuicMaxStreamsFrame(maxStreams, frameType == QuicFrameType.MaxStreamsBidi);
            }

            case QuicFrameType.DataBlocked:
                return new QuicDataBlockedFrame(ReadVarInt(payload, ref offset, "DATA_BLOCKED"));

            case QuicFrameType.StreamDataBlocked:
                return new QuicStreamDataBlockedFrame(
                    ReadVarInt(payload, ref offset, "STREAM_DATA_BLOCKED stream_id"),
                    ReadVarInt(payload, ref offset, "STREAM_DATA_BLOCKED max_stream_data"));

            case QuicFrameType.StreamsBlockedBidi:
            case QuicFrameType.StreamsBlockedUni:
            {
                ulong maxStreams = ReadVarInt(payload, ref offset, "STREAMS_BLOCKED");
                if (maxStreams > (1UL << 60))
                    throw new QuicException(QuicErrorCode.FrameEncodingError, false, "STREAMS_BLOCKED exceeds 2^60.");
                return new QuicStreamsBlockedFrame(maxStreams, frameType == QuicFrameType.StreamsBlockedBidi);
            }

            case QuicFrameType.NewConnectionId:
            {
                ulong seq = ReadVarInt(payload, ref offset, "NEW_CONNECTION_ID sequence_number");
                ulong retirePriorTo = ReadVarInt(payload, ref offset, "NEW_CONNECTION_ID retire_prior_to");
                if (retirePriorTo > seq)
                    throw new QuicException(QuicErrorCode.FrameEncodingError, false, "NEW_CONNECTION_ID retire_prior_to exceeds sequence_number.");
                if (offset >= payload.Length)
                    throw new QuicException(QuicErrorCode.FrameEncodingError, false, "Truncated NEW_CONNECTION_ID length.");
                byte cidLen = payload[offset++];
                if (cidLen is < 1 or > 20)
                    throw new QuicException(QuicErrorCode.FrameEncodingError, false, $"NEW_CONNECTION_ID length {cidLen} out of range 1..20.");
                if (offset + cidLen + 16 > payload.Length)
                    throw new QuicException(QuicErrorCode.FrameEncodingError, false, "Truncated NEW_CONNECTION_ID payload.");
                byte[] cid = payload.Slice(offset, cidLen).ToArray();
                offset += cidLen;
                byte[] resetToken = payload.Slice(offset, 16).ToArray();
                offset += 16;
                return new QuicNewConnectionIdFrame(seq, retirePriorTo, cid, resetToken);
            }

            case QuicFrameType.RetireConnectionId:
                return new QuicRetireConnectionIdFrame(ReadVarInt(payload, ref offset, "RETIRE_CONNECTION_ID"));

            case QuicFrameType.PathChallenge:
            {
                if (offset + 8 > payload.Length)
                    throw new QuicException(QuicErrorCode.FrameEncodingError, false, "Truncated PATH_CHALLENGE frame.");
                byte[] data = payload.Slice(offset, 8).ToArray();
                offset += 8;
                return new QuicPathChallengeFrame(data);
            }

            case QuicFrameType.PathResponse:
            {
                if (offset + 8 > payload.Length)
                    throw new QuicException(QuicErrorCode.FrameEncodingError, false, "Truncated PATH_RESPONSE frame.");
                byte[] data = payload.Slice(offset, 8).ToArray();
                offset += 8;
                return new QuicPathResponseFrame(data);
            }

            case QuicFrameType.ConnectionCloseTransport:
            case QuicFrameType.ConnectionCloseApplication:
            {
                bool isApp = frameType == QuicFrameType.ConnectionCloseApplication;
                ulong errorCode = ReadVarInt(payload, ref offset, "CONNECTION_CLOSE error_code");
                ulong offendingType = isApp ? 0UL : ReadVarInt(payload, ref offset, "CONNECTION_CLOSE frame_type");
                byte[] reasonBytes = ReadLengthPrefixedBytes(payload, ref offset, "CONNECTION_CLOSE reason");
                string reason = reasonBytes.Length == 0 ? string.Empty : Encoding.UTF8.GetString(reasonBytes);
                return new QuicConnectionCloseFrame(errorCode, offendingType, reason, isApp);
            }

            case QuicFrameType.HandshakeDone:
                return QuicHandshakeDoneFrame.Instance;

            case QuicFrameType.DatagramNoLen:
            {
                byte[] data = payload.Slice(offset).ToArray();
                offset = payload.Length;
                return new QuicDatagramFrame(data, HasLength: false);
            }

            case QuicFrameType.DatagramWithLen:
            {
                byte[] data = ReadLengthPrefixedBytes(payload, ref offset, "DATAGRAM data");
                return new QuicDatagramFrame(data, HasLength: true);
            }

            default:
                throw new QuicException(QuicErrorCode.FrameEncodingError, false, $"Unsupported QUIC frame type 0x{frameType:X}.");
        }
    }

    private static ulong ReadVarInt(ReadOnlySpan<byte> payload, ref int offset, string field)
    {
        if (!QuicVarInt.TryRead(payload, ref offset, out ulong val))
            throw new QuicException(QuicErrorCode.FrameEncodingError, false, $"Truncated QUIC {field}.");
        return val;
    }

    private static byte[] ReadLengthPrefixedBytes(ReadOnlySpan<byte> payload, ref int offset, string field)
    {
        ulong len = ReadVarInt(payload, ref offset, $"{field} length");
        if (len > (ulong)(payload.Length - offset))
            throw new QuicException(QuicErrorCode.FrameEncodingError, false, $"Truncated QUIC {field} bytes.");
        byte[] bytes = len == 0 ? Array.Empty<byte>() : payload.Slice(offset, (int)len).ToArray();
        offset += (int)len;
        return bytes;
    }
}

/// <summary>
/// Chrome QUIC Initial CRYPTO packetizer matching <c>ChaosFrames</c> (<c>0x1412AC240</c>):
/// splits ClientHello <c>CRYPTO</c> data into 1..11 randomized out-of-order slices,
/// interleaves <c>PING</c>, and pads Initial packets to at least 1200 bytes.
/// </summary>
public static class ChaosFrames
{
    public const int MinInitialDatagramBytes = 1200;
    public const int MaxChaosFragments = 11;

    public static List<QuicCryptoFrame> SplitCryptoFragments(
        ReadOnlySpan<byte> cryptoPayload,
        bool enableChaos = true,
        int? fragmentCountOverride = null,
        Random? random = null)
    {
        if (!enableChaos || cryptoPayload.Length <= 1)
            return new List<QuicCryptoFrame>(1) { new(0, cryptoPayload.ToArray()) };

        Random rng = random ?? Random.Shared;
        int maxPossible = Math.Min(MaxChaosFragments, cryptoPayload.Length);
        int count = fragmentCountOverride.HasValue
            ? Math.Clamp(fragmentCountOverride.Value, 1, maxPossible)
            : rng.Next(1, maxPossible + 1);

        if (count == 1)
            return new List<QuicCryptoFrame>(1) { new(0, cryptoPayload.ToArray()) };

        // Choose count - 1 distinct cut points in [1, cryptoPayload.Length - 1].
        var cuts = new SortedSet<int>();
        while (cuts.Count < count - 1)
            cuts.Add(rng.Next(1, cryptoPayload.Length));

        var fragments = new List<QuicCryptoFrame>(count);
        int prev = 0;
        foreach (int cut in cuts)
        {
            fragments.Add(new QuicCryptoFrame((ulong)prev, cryptoPayload.Slice(prev, cut - prev).ToArray()));
            prev = cut;
        }
        fragments.Add(new QuicCryptoFrame((ulong)prev, cryptoPayload.Slice(prev).ToArray()));

        // Shuffle slices out-of-order to perturb stateless DPI inspection.
        for (int i = fragments.Count - 1; i >= 1; i--)
        {
            int j = rng.Next(0, i + 1);
            (fragments[i], fragments[j]) = (fragments[j], fragments[i]);
        }

        return fragments;
    }

    /// <summary>
    /// Packs <paramref name="cryptoPayload"/> into one or more Initial packet frame lists,
    /// interleaving <c>PING</c> and adding <c>PADDING</c> so every packet reaches at least
    /// <paramref name="minPlaintextBytes"/> while respecting <paramref name="maxPlaintextBytes"/>.
    /// </summary>
    public static List<List<QuicFrame>> PackInitialFrameLists(
        ReadOnlySpan<byte> cryptoPayload,
        int minPlaintextBytes = 1150,
        int maxPlaintextBytes = 1190,
        bool enableChaos = true,
        bool includePing = true,
        int? fragmentCountOverride = null,
        Random? random = null)
    {
        if (maxPlaintextBytes < 64)
            throw new ArgumentOutOfRangeException(nameof(maxPlaintextBytes), "Max Initial plaintext per packet must be >= 64 bytes.");

        Random rng = random ?? Random.Shared;
        List<QuicCryptoFrame> rawSlices = SplitCryptoFragments(cryptoPayload, enableChaos, fragmentCountOverride, rng);

        // Ensure no single CRYPTO frame exceeds maxPlaintextBytes (e.g., X25519MLKEM768 ClientHello ~1600B).
        int maxCryptoChunk = Math.Max(32, maxPlaintextBytes - 16);
        var queue = new Queue<QuicCryptoFrame>(rawSlices.Count + 2);
        for (int i = 0; i < rawSlices.Count; i++)
        {
            QuicCryptoFrame f = rawSlices[i];
            if (f.GetEncodedLength() <= maxPlaintextBytes - 4)
            {
                queue.Enqueue(f);
                continue;
            }

            int pos = 0;
            while (pos < f.Data.Length)
            {
                int take = Math.Min(maxCryptoChunk, f.Data.Length - pos);
                queue.Enqueue(new QuicCryptoFrame(f.Offset + (ulong)pos, f.Data.AsSpan(pos, take).ToArray()));
                pos += take;
            }
        }

        var packets = new List<List<QuicFrame>>();
        while (queue.Count > 0)
        {
            var packetFrames = new List<QuicFrame>();
            int currentBytes = 0;
            bool addedPing = false;

            while (queue.Count > 0)
            {
                QuicCryptoFrame next = queue.Peek();
                int nextLen = next.GetEncodedLength();
                if (currentBytes + nextLen <= maxPlaintextBytes)
                {
                    packetFrames.Add(queue.Dequeue());
                    currentBytes += nextLen;

                    if (includePing && enableChaos && !addedPing && currentBytes + 1 <= maxPlaintextBytes && (queue.Count == 0 || rng.Next(2) == 0))
                    {
                        packetFrames.Add(QuicPingFrame.Instance);
                        currentBytes += 1;
                        addedPing = true;
                    }
                }
                else
                {
                    // Split remaining slice to fill current packet cleanly when needed.
                    int remainingBudget = maxPlaintextBytes - currentBytes - 10;
                    if (next.Data.Length > 1 && (packetFrames.Count == 0 || remainingBudget >= 32))
                    {
                        int splitBytes = Math.Clamp(remainingBudget, 1, next.Data.Length - 1);
                        QuicCryptoFrame head = new(next.Offset, next.Data.AsSpan(0, splitBytes).ToArray());
                        QuicCryptoFrame tail = new(next.Offset + (ulong)splitBytes, next.Data.AsSpan(splitBytes).ToArray());
                        queue.Dequeue();
                        // Put tail back at front by rotating or rebuilding; simplest is requeuing tail after splitting.
                        var rest = new List<QuicCryptoFrame>(queue.Count + 1) { tail };
                        while (queue.Count > 0)
                            rest.Add(queue.Dequeue());
                        for (int k = 0; k < rest.Count; k++)
                            queue.Enqueue(rest[k]);

                        packetFrames.Add(head);
                        currentBytes += head.GetEncodedLength();
                    }
                    break;
                }
            }

            if (includePing && !addedPing && currentBytes + 1 <= maxPlaintextBytes)
            {
                int insertIdx = packetFrames.Count > 1 ? rng.Next(packetFrames.Count + 1) : packetFrames.Count;
                packetFrames.Insert(insertIdx, QuicPingFrame.Instance);
                currentBytes += 1;
            }

            if (currentBytes < minPlaintextBytes)
                packetFrames.Add(new QuicPaddingFrame(minPlaintextBytes - currentBytes));

            packets.Add(packetFrames);
        }

        if (packets.Count == 0)
        {
            var fallback = new List<QuicFrame>();
            if (includePing)
                fallback.Add(QuicPingFrame.Instance);
            int pad = minPlaintextBytes - (includePing ? 1 : 0);
            if (pad > 0)
                fallback.Add(new QuicPaddingFrame(pad));
            packets.Add(fallback);
        }

        return packets;
    }

    public static byte[] BuildPaddedInitialPayload(
        ReadOnlySpan<byte> cryptoPayload,
        int minPlaintextBytes = MinInitialDatagramBytes,
        bool enableChaos = true,
        bool includePing = true,
        int? fragmentCountOverride = null,
        Random? random = null)
    {
        List<List<QuicFrame>> lists = PackInitialFrameLists(
            cryptoPayload,
            minPlaintextBytes: minPlaintextBytes,
            maxPlaintextBytes: Math.Max(minPlaintextBytes, cryptoPayload.Length + 256),
            enableChaos: enableChaos,
            includePing: includePing,
            fragmentCountOverride: fragmentCountOverride,
            random: random);
        return QuicFrameCodec.Encode(lists[0]);
    }
}
