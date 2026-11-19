using System;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Interval-gated restock polling, reconstructed from two observed facts and one observed sentence.
///
/// <para>
/// <b>Observed</b> (R1260, full string dump):
/// </para>
/// <list type="bullet">
/// <item><description><c>RestockInterval _lastRestockPing</c> at 0x1433A28C7 — two names adjacent in the image, a
/// configured interval and a timestamp of the last ping. The pair is the whole reason this class exists: the original
/// polls on a cadence it tracks, rather than on every tick.</description></item>
/// <item><description><c>Tasks will wait for the in-bot monitor to detect a new product or restock and use the data
/// provided by the monitor. While using this mode, no data will be used while searching for a product/restock.</c> at
/// 0x1435BDD4A — the original's own description of the wait mode: the task does not search, it consumes what the
/// monitor found.</description></item>
/// <item><description><c>WaitForRestock</c> (0x1433A2566) and <c>WaitRestock</c> (0x14337AF05) both exist, so waiting
/// and polling are separate members rather than two names for one.</description></item>
/// </list>
///
/// <para>
/// <b>Inference</b>: a ping is due when at least one interval has elapsed since the last ping. That is the minimum
/// reading of an interval plus a last-ping timestamp; the alternative — a background timer — would not need to store
/// the last ping at all.
/// </para>
///
/// <para>
/// <b>Unknown</b>: the interval's default and units, and what the ping requests. The image keeps the field names and
/// the sentence, not the configured values, so this class takes the interval from the caller and records nothing
/// about the endpoint.
/// </para>
/// </summary>
public sealed class RestockGate
{
    private readonly Func<DateTime> _clock;
    private DateTime? _lastRestockPing;

    public RestockGate(TimeSpan interval, Func<DateTime>? clock = null)
    {
        if (interval <= TimeSpan.Zero)
            throw new ArgumentOutOfRangeException(nameof(interval), "the restock interval must be positive");
        RestockInterval = interval;
        _clock = clock ?? (() => DateTime.UtcNow);
    }

    /// <summary>The configured cadence (field name observed at 0x1433A28C7).</summary>
    public TimeSpan RestockInterval { get; }

    /// <summary>The previous ping, or <c>null</c> when none has happened in this session (0x1433A28C7).</summary>
    public DateTime? LastRestockPing => _lastRestockPing;

    /// <summary>True when a ping is due, and false while the interval since the last one is still running.</summary>
    public bool IsDue => _lastRestockPing is null || _clock() - _lastRestockPing.Value >= RestockInterval;

    /// <summary>
    /// Marks the ping as taken. Separated from <see cref="IsDue"/> so a caller that fails to ping does not advance the
    /// clock it is gated by.
    /// </summary>
    public void MarkPinged() => _lastRestockPing = _clock();
}
