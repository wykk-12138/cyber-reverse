namespace Cybersole.Http.Quic;

public enum QuicPacketNumberSpace
{
    Initial = 0,
    Handshake = 1,
    Application = 2,
}

public sealed class QuicSentPacket
{
    public QuicSentPacket(
        ulong packetNumber,
        QuicPacketNumberSpace space,
        TimeSpan timeSent,
        int sentBytes,
        bool ackEliciting,
        bool inFlight,
        IReadOnlyList<QuicFrame>? frames = null)
    {
        PacketNumber = packetNumber;
        Space = space;
        TimeSent = timeSent;
        SentBytes = sentBytes;
        AckEliciting = ackEliciting;
        InFlight = inFlight;
        Frames = frames ?? Array.Empty<QuicFrame>();
    }

    public ulong PacketNumber { get; }
    public QuicPacketNumberSpace Space { get; }
    public TimeSpan TimeSent { get; }
    public int SentBytes { get; }
    public bool AckEliciting { get; }
    public bool InFlight { get; }
    public IReadOnlyList<QuicFrame> Frames { get; }
}

public sealed record QuicAckProcessResult(
    IReadOnlyList<QuicSentPacket> AckedPackets,
    IReadOnlyList<QuicSentPacket> LostPackets);

public sealed record QuicLossTimerOutcome(
    bool WasLossTimer,
    QuicPacketNumberSpace Space,
    IReadOnlyList<QuicSentPacket> LostPackets,
    int ProbePacketCount);

/// <summary>
/// RFC 9002 QUIC loss detection, RTT estimation, PTO calculation, and NewReno congestion control
/// matching <c>cybersole_http_architecture.md</c> §5.1.
/// </summary>
public sealed class QuicLossRecovery
{
    public const ulong PacketThreshold = 3UL;
    public const int TimeThresholdNumerator = 9;
    public const int TimeThresholdDenominator = 8;
    public const int DefaultMaxDatagramSize = 1200;
    public const ulong DefaultInitialWindow = 14_720UL;
    public const ulong DefaultMinimumWindow = 2_400UL;
    public static readonly TimeSpan InitialRtt = TimeSpan.FromMilliseconds(333);
    public static readonly TimeSpan Granularity = TimeSpan.FromMilliseconds(1);

    private sealed class SpaceState
    {
        public readonly SortedDictionary<ulong, QuicSentPacket> SentPackets = new();
        public ulong? LargestAckedPacket;
        public TimeSpan? LossTime;
        public TimeSpan? TimeOfLastAckElicitingPacket;
        public int AckElicitingInFlight;
        public bool Discarded;
    }

    private readonly SpaceState[] _spaces =
    {
        new(), // Initial
        new(), // Handshake
        new(), // Application
    };

    private TimeSpan _congestionRecoveryStartTime = TimeSpan.MinValue;
    private ulong _congestionAvoidanceAckedBytes;

    public QuicLossRecovery(
        int maxDatagramSize = DefaultMaxDatagramSize,
        ulong initialWindow = DefaultInitialWindow,
        ulong minimumWindow = DefaultMinimumWindow,
        TimeSpan? initialRtt = null)
    {
        if (maxDatagramSize < 1200)
            throw new ArgumentOutOfRangeException(nameof(maxDatagramSize), maxDatagramSize, "Max datagram size must be >= 1200.");

        MaxDatagramSize = maxDatagramSize;
        MinimumWindow = Math.Max(minimumWindow, 2UL * (ulong)maxDatagramSize);
        InitialWindow = Math.Max(initialWindow, MinimumWindow);
        CongestionWindow = InitialWindow;
        Ssthresh = ulong.MaxValue;

        TimeSpan initRtt = initialRtt.HasValue && initialRtt.Value > TimeSpan.Zero ? initialRtt.Value : InitialRtt;
        SmoothedRtt = initRtt;
        RttVar = TimeSpan.FromTicks(initRtt.Ticks / 2);
        MinRtt = TimeSpan.Zero;
        LatestRtt = TimeSpan.Zero;
    }

    public int MaxDatagramSize { get; }
    public ulong InitialWindow { get; }
    public ulong MinimumWindow { get; }
    public ulong CongestionWindow { get; private set; }
    public ulong Ssthresh { get; private set; }
    public ulong BytesInFlight { get; private set; }
    public TimeSpan SmoothedRtt { get; private set; }
    public TimeSpan RttVar { get; private set; }
    public TimeSpan MinRtt { get; private set; }
    public TimeSpan LatestRtt { get; private set; }
    public bool HasRttSample { get; private set; }
    public TimeSpan MaxAckDelay { get; set; } = TimeSpan.FromMilliseconds(25);
    public int AckDelayExponent { get; set; } = 3;
    public int PtoCount { get; private set; }
    public bool HandshakeConfirmed { get; private set; }

    public ulong? GetLargestAckedPacket(QuicPacketNumberSpace space) => _spaces[(int)space].LargestAckedPacket;

    public int GetInFlightCount(QuicPacketNumberSpace space) => _spaces[(int)space].SentPackets.Count;

    public bool CanSend(int packetBytes, bool inFlight = true)
    {
        if (!inFlight || packetBytes <= 0)
            return true;
        return BytesInFlight == 0 || BytesInFlight + (ulong)packetBytes <= CongestionWindow;
    }

    public ulong AvailableCongestionWindow() =>
        CongestionWindow > BytesInFlight ? CongestionWindow - BytesInFlight : 0UL;

    public void MarkHandshakeConfirmed(TimeSpan now)
    {
        HandshakeConfirmed = true;
        _ = now;
    }

    public void DiscardSpace(QuicPacketNumberSpace space)
    {
        SpaceState st = _spaces[(int)space];
        if (st.Discarded)
            return;

        foreach (QuicSentPacket pkt in st.SentPackets.Values)
        {
            if (pkt.InFlight && BytesInFlight >= (ulong)pkt.SentBytes)
                BytesInFlight -= (ulong)pkt.SentBytes;
            else if (pkt.InFlight)
                BytesInFlight = 0;
        }

        st.SentPackets.Clear();
        st.LossTime = null;
        st.TimeOfLastAckElicitingPacket = null;
        st.AckElicitingInFlight = 0;
        st.Discarded = true;
    }

    public void ResetSpace(QuicPacketNumberSpace space)
    {
        SpaceState st = _spaces[(int)space];
        foreach (QuicSentPacket pkt in st.SentPackets.Values)
        {
            if (pkt.InFlight && BytesInFlight >= (ulong)pkt.SentBytes)
                BytesInFlight -= (ulong)pkt.SentBytes;
            else if (pkt.InFlight)
                BytesInFlight = 0;
        }

        st.SentPackets.Clear();
        st.LargestAckedPacket = null;
        st.LossTime = null;
        st.TimeOfLastAckElicitingPacket = null;
        st.AckElicitingInFlight = 0;
        st.Discarded = false;
    }

    public void OnPacketSent(
        QuicPacketNumberSpace space,
        ulong packetNumber,
        int sentBytes,
        bool ackEliciting,
        bool inFlight,
        TimeSpan now,
        IReadOnlyList<QuicFrame>? frames = null)
    {
        SpaceState st = _spaces[(int)space];
        if (st.Discarded)
            return;

        var sent = new QuicSentPacket(packetNumber, space, now, sentBytes, ackEliciting, inFlight, frames);
        st.SentPackets[packetNumber] = sent;

        if (inFlight)
        {
            BytesInFlight += (ulong)Math.Max(0, sentBytes);
            if (ackEliciting)
            {
                st.TimeOfLastAckElicitingPacket = now;
                st.AckElicitingInFlight++;
            }
        }
    }

    public QuicAckProcessResult OnAckReceived(
        QuicPacketNumberSpace space,
        QuicAckFrame ackFrame,
        TimeSpan now)
    {
        ArgumentNullException.ThrowIfNull(ackFrame);
        SpaceState st = _spaces[(int)space];
        if (st.Discarded)
            return new QuicAckProcessResult(Array.Empty<QuicSentPacket>(), Array.Empty<QuicSentPacket>());

        bool prevLargestWasLess = !st.LargestAckedPacket.HasValue || ackFrame.LargestAcknowledged > st.LargestAckedPacket.Value;
        if (!st.LargestAckedPacket.HasValue || ackFrame.LargestAcknowledged > st.LargestAckedPacket.Value)
            st.LargestAckedPacket = ackFrame.LargestAcknowledged;

        List<(ulong Start, ulong End)> ranges = ackFrame.GetAcknowledgedRanges();
        var newlyAcked = new List<QuicSentPacket>();
        bool includesAckEliciting = false;
        QuicSentPacket? largestNewlyAcked = null;

        // Collect matching keys from sent packets.
        var ackedKeys = new List<ulong>();
        foreach (KeyValuePair<ulong, QuicSentPacket> kv in st.SentPackets)
        {
            ulong pn = kv.Key;
            if (pn > ackFrame.LargestAcknowledged)
                break;

            if (IsInRanges(pn, ranges))
                ackedKeys.Add(pn);
        }

        for (int i = 0; i < ackedKeys.Count; i++)
        {
            ulong pn = ackedKeys[i];
            if (!st.SentPackets.Remove(pn, out QuicSentPacket? pkt))
                continue;

            newlyAcked.Add(pkt);
            if (pkt.InFlight)
            {
                BytesInFlight = BytesInFlight >= (ulong)pkt.SentBytes ? BytesInFlight - (ulong)pkt.SentBytes : 0UL;
                if (pkt.AckEliciting && st.AckElicitingInFlight > 0)
                    st.AckElicitingInFlight--;
            }

            if (pkt.AckEliciting)
                includesAckEliciting = true;

            if (largestNewlyAcked is null || pkt.PacketNumber > largestNewlyAcked.PacketNumber)
                largestNewlyAcked = pkt;
        }

        if (newlyAcked.Count == 0)
            return new QuicAckProcessResult(newlyAcked, Array.Empty<QuicSentPacket>());

        if (largestNewlyAcked is not null &&
            largestNewlyAcked.PacketNumber == st.LargestAckedPacket &&
            includesAckEliciting &&
            prevLargestWasLess)
        {
            TimeSpan latestRtt = now >= largestNewlyAcked.TimeSent ? now - largestNewlyAcked.TimeSent : TimeSpan.Zero;
            TimeSpan ackDelay = DecodeAckDelay(ackFrame.AckDelay, AckDelayExponent);
            UpdateRtt(latestRtt, ackDelay, isApplicationAndConfirmed: space == QuicPacketNumberSpace.Application && HandshakeConfirmed);
        }

        // Reset PTO backoff once progress is acknowledged.
        PtoCount = 0;

        List<QuicSentPacket> lost = DetectLostPackets(space, now);
        if (lost.Count > 0)
            OnPacketsLost(lost, now);

        OnPacketsAckedCongestion(newlyAcked);

        return new QuicAckProcessResult(newlyAcked, lost);
    }

    public void UpdateRtt(TimeSpan latestRtt, TimeSpan ackDelay, bool isApplicationAndConfirmed = true)
    {
        if (latestRtt < TimeSpan.Zero)
            latestRtt = TimeSpan.Zero;

        LatestRtt = latestRtt;

        if (!HasRttSample)
        {
            MinRtt = latestRtt;
            SmoothedRtt = latestRtt;
            RttVar = TimeSpan.FromTicks(latestRtt.Ticks / 2);
            HasRttSample = true;
            return;
        }

        if (latestRtt < MinRtt)
            MinRtt = latestRtt;

        TimeSpan clampedAckDelay = ackDelay;
        if (isApplicationAndConfirmed && clampedAckDelay > MaxAckDelay)
            clampedAckDelay = MaxAckDelay;

        TimeSpan adjustedRtt = latestRtt;
        if (isApplicationAndConfirmed && latestRtt >= MinRtt + clampedAckDelay)
            adjustedRtt = latestRtt - clampedAckDelay;

        long diffTicks = Math.Abs(SmoothedRtt.Ticks - adjustedRtt.Ticks);
        RttVar = TimeSpan.FromTicks((3L * RttVar.Ticks + diffTicks) / 4L);
        SmoothedRtt = TimeSpan.FromTicks((7L * SmoothedRtt.Ticks + adjustedRtt.Ticks) / 8L);
    }

    public TimeSpan GetPtoDuration(QuicPacketNumberSpace space)
    {
        long fourRttVar = Math.Max(4L * RttVar.Ticks, Granularity.Ticks);
        long baseTicks = SmoothedRtt.Ticks + fourRttVar + (space == QuicPacketNumberSpace.Application ? MaxAckDelay.Ticks : 0L);
        int shift = Math.Min(PtoCount, 10);
        long shifted = baseTicks > (long.MaxValue >> shift) ? long.MaxValue : baseTicks << shift;
        return TimeSpan.FromTicks(shifted);
    }

    public (TimeSpan? Deadline, QuicPacketNumberSpace Space, bool IsLossTimer) GetLossDetectionTimeout()
    {
        TimeSpan? earliestLoss = null;
        QuicPacketNumberSpace lossSpace = QuicPacketNumberSpace.Initial;

        for (int i = 0; i < _spaces.Length; i++)
        {
            TimeSpan? lt = _spaces[i].LossTime;
            if (lt.HasValue && (!earliestLoss.HasValue || lt.Value < earliestLoss.Value))
            {
                earliestLoss = lt.Value;
                lossSpace = (QuicPacketNumberSpace)i;
            }
        }

        if (earliestLoss.HasValue)
            return (earliestLoss, lossSpace, true);

        TimeSpan? earliestPto = null;
        QuicPacketNumberSpace ptoSpace = QuicPacketNumberSpace.Initial;
        for (int i = 0; i < _spaces.Length; i++)
        {
            SpaceState st = _spaces[i];
            if (st.Discarded || st.AckElicitingInFlight == 0)
                continue;

            var sp = (QuicPacketNumberSpace)i;
            if (sp == QuicPacketNumberSpace.Application && !HandshakeConfirmed)
                continue;

            if (st.TimeOfLastAckElicitingPacket.HasValue)
            {
                TimeSpan deadline = st.TimeOfLastAckElicitingPacket.Value + GetPtoDuration(sp);
                if (!earliestPto.HasValue || deadline < earliestPto.Value)
                {
                    earliestPto = deadline;
                    ptoSpace = sp;
                }
            }
        }

        return earliestPto.HasValue
            ? (earliestPto, ptoSpace, false)
            : (null, QuicPacketNumberSpace.Application, false);
    }

    public QuicLossTimerOutcome OnLossDetectionTimeout(TimeSpan now)
    {
        (TimeSpan? earliestLoss, QuicPacketNumberSpace lossSpace, bool isLoss) = GetLossDetectionTimeout();
        if (isLoss && earliestLoss.HasValue)
        {
            List<QuicSentPacket> lost = DetectLostPackets(lossSpace, now);
            if (lost.Count > 0)
                OnPacketsLost(lost, now);
            return new QuicLossTimerOutcome(true, lossSpace, lost, 0);
        }

        PtoCount++;
        QuicPacketNumberSpace ptoSpace = lossSpace;
        if (!earliestLoss.HasValue)
        {
            if (!_spaces[(int)QuicPacketNumberSpace.Initial].Discarded && _spaces[(int)QuicPacketNumberSpace.Initial].SentPackets.Count > 0)
                ptoSpace = QuicPacketNumberSpace.Initial;
            else if (!_spaces[(int)QuicPacketNumberSpace.Handshake].Discarded && _spaces[(int)QuicPacketNumberSpace.Handshake].SentPackets.Count > 0)
                ptoSpace = QuicPacketNumberSpace.Handshake;
            else
                ptoSpace = QuicPacketNumberSpace.Application;
        }

        return new QuicLossTimerOutcome(false, ptoSpace, Array.Empty<QuicSentPacket>(), 2);
    }

    public List<QuicSentPacket> DetectLostPackets(QuicPacketNumberSpace space, TimeSpan now)
    {
        SpaceState st = _spaces[(int)space];
        st.LossTime = null;
        if (!st.LargestAckedPacket.HasValue || st.SentPackets.Count == 0)
            return new List<QuicSentPacket>();

        ulong largestAcked = st.LargestAckedPacket.Value;
        long maxRttTicks = Math.Max(LatestRtt.Ticks, SmoothedRtt.Ticks);
        long lossDelayTicks = Math.Max((maxRttTicks * TimeThresholdNumerator) / TimeThresholdDenominator, Granularity.Ticks);
        TimeSpan lossDelay = TimeSpan.FromTicks(lossDelayTicks);
        TimeSpan lostSendTime = now - lossDelay;

        var lost = new List<QuicSentPacket>();
        var lostKeys = new List<ulong>();

        foreach (KeyValuePair<ulong, QuicSentPacket> kv in st.SentPackets)
        {
            ulong pn = kv.Key;
            if (pn > largestAcked)
                break;

            QuicSentPacket pkt = kv.Value;
            if (pkt.TimeSent <= lostSendTime || largestAcked >= pn + PacketThreshold)
            {
                lostKeys.Add(pn);
                lost.Add(pkt);
            }
            else
            {
                TimeSpan candidateLossTime = pkt.TimeSent + lossDelay;
                if (!st.LossTime.HasValue || candidateLossTime < st.LossTime.Value)
                    st.LossTime = candidateLossTime;
            }
        }

        for (int i = 0; i < lostKeys.Count; i++)
        {
            if (st.SentPackets.Remove(lostKeys[i], out QuicSentPacket? pkt) && pkt.InFlight)
            {
                BytesInFlight = BytesInFlight >= (ulong)pkt.SentBytes ? BytesInFlight - (ulong)pkt.SentBytes : 0UL;
                if (pkt.AckEliciting && st.AckElicitingInFlight > 0)
                    st.AckElicitingInFlight--;
            }
        }

        return lost;
    }

    private void OnPacketsLost(List<QuicSentPacket> lostPackets, TimeSpan now)
    {
        TimeSpan largestTimeSent = TimeSpan.MinValue;
        bool anyInFlight = false;
        for (int i = 0; i < lostPackets.Count; i++)
        {
            if (lostPackets[i].InFlight)
            {
                anyInFlight = true;
                if (lostPackets[i].TimeSent > largestTimeSent)
                    largestTimeSent = lostPackets[i].TimeSent;
            }
        }

        if (!anyInFlight)
            return;

        // Enter congestion recovery once per RTT (RFC 9002 §7.3.2).
        if (largestTimeSent > _congestionRecoveryStartTime)
        {
            _congestionRecoveryStartTime = now;
            Ssthresh = Math.Max(CongestionWindow / 2UL, MinimumWindow);
            CongestionWindow = Ssthresh;
            _congestionAvoidanceAckedBytes = 0;
        }
    }

    private void OnPacketsAckedCongestion(List<QuicSentPacket> ackedPackets)
    {
        for (int i = 0; i < ackedPackets.Count; i++)
        {
            QuicSentPacket pkt = ackedPackets[i];
            if (!pkt.InFlight || pkt.SentBytes <= 0)
                continue;

            // Do not increase cwnd while in congestion recovery.
            if (pkt.TimeSent <= _congestionRecoveryStartTime)
                continue;

            if (CongestionWindow < Ssthresh)
            {
                // Slow start
                CongestionWindow += (ulong)pkt.SentBytes;
            }
            else
            {
                // Congestion avoidance
                _congestionAvoidanceAckedBytes += (ulong)pkt.SentBytes;
                if (_congestionAvoidanceAckedBytes >= CongestionWindow)
                {
                    _congestionAvoidanceAckedBytes -= CongestionWindow;
                    CongestionWindow += (ulong)MaxDatagramSize;
                }
            }
        }
    }

    private static bool IsInRanges(ulong pn, List<(ulong Start, ulong End)> ranges)
    {
        for (int i = 0; i < ranges.Count; i++)
        {
            if (pn >= ranges[i].Start && pn <= ranges[i].End)
                return true;
        }
        return false;
    }

    private static TimeSpan DecodeAckDelay(ulong encodedAckDelay, int exponent)
    {
        int clampedExp = Math.Clamp(exponent, 0, 20);
        if (encodedAckDelay > (ulong.MaxValue >> clampedExp))
            return TimeSpan.FromSeconds(16);
        ulong us = encodedAckDelay << clampedExp;
        if (us > (ulong)(long.MaxValue / 10L))
            return TimeSpan.FromSeconds(16);
        return TimeSpan.FromTicks((long)us * 10L);
    }
}
