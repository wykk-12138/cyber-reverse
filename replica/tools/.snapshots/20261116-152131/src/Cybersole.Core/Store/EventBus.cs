using System.Collections.Concurrent;

namespace Cybersole.Core.Store;

public enum LogLevel { Trace, Debug, Info, Warn, Error }

public sealed record LogEntry(DateTime Timestamp, LogLevel Level, string Source, string Message)
{
    public override string ToString() => $"{Timestamp:HH:mm:ss.fff} [{Level,-5}] {Source}: {Message}";
}

/// <summary>In-memory event log + fan-out for the UI and webhook notifier.</summary>
public sealed class EventBus
{
    private readonly ConcurrentQueue<LogEntry> _history = new();

    /// <summary>Hard cap on retained lines (safety net on top of the time window).</summary>
    public int MaxHistory { get; set; } = 20000;

    /// <summary>settings.maxLogSize (MB) — total message characters kept in memory.</summary>
    public int MaxTotalChars { get; set; } = 50 * 1024 * 1024;

    /// <summary>settings.maxLogRetention — entries older than this are dropped.</summary>
    public TimeSpan MaxRetention { get; set; } = TimeSpan.FromDays(1);

    /// <summary>Single message cap, so a huge HTML payload can't flood the UI.</summary>
    public int MaxEntryLength { get; set; } = 8000;

    private long _totalChars;

    public event EventHandler<LogEntry>? Logged;
    public event EventHandler<string>? Notification;
    public event EventHandler<CheckoutEvent>? Checkout;

    public IReadOnlyCollection<LogEntry> History => _history.ToArray();

    public void Log(LogLevel level, string source, string message)
    {
        if (message.Length > MaxEntryLength)
            message = message[..MaxEntryLength] + $"…(+{message.Length - MaxEntryLength})";

        var entry = new LogEntry(DateTime.Now, level, source, message);
        _history.Enqueue(entry);
        Interlocked.Add(ref _totalChars, entry.Message.Length);

        // retention window
        if (MaxRetention > TimeSpan.Zero)
        {
            var cutoff = DateTime.Now - MaxRetention;
            while (_history.TryPeek(out var oldest) && oldest.Timestamp < cutoff)
                if (_history.TryDequeue(out var dropped)) Interlocked.Add(ref _totalChars, -dropped.Message.Length);
        }

        // size budget
        while (Interlocked.Read(ref _totalChars) > MaxTotalChars &&
               _history.TryDequeue(out var over))
            Interlocked.Add(ref _totalChars, -over.Message.Length);

        // absolute line cap
        while (_history.Count > MaxHistory && _history.TryDequeue(out var capped))
            Interlocked.Add(ref _totalChars, -capped.Message.Length);

        Logged?.Invoke(this, entry);
    }

    public void Info(string source, string message) => Log(LogLevel.Info, source, message);
    public void Warn(string source, string message) => Log(LogLevel.Warn, source, message);
    public void Error(string source, string message) => Log(LogLevel.Error, source, message);

    public void Notify(string message) => Notification?.Invoke(this, message);
    public void RaiseCheckout(CheckoutEvent evt) => Checkout?.Invoke(this, evt);
}

public sealed record CheckoutEvent(
    string Store,
    string Product,
    string Size,
    string Price,
    bool Success,
    string? OrderNumber,
    string Profile)
{
    /// <summary>When the checkout completed — used to order the analytics feeds.</summary>
    public DateTime At { get; init; } = DateTime.UtcNow;

    /// <summary>
    /// Where the store's tracking page for this checkout lives, when the flow got one back (R303: CheckoutView's
    /// "Open tracking" button wrote a sentence and nothing else, because this event carried no URL at all).
    /// </summary>
    public string? TrackingUrl { get; init; }
}
