using Cybersole.Core.Store;

namespace Cybersole.Services;

/// <summary>
/// Aggregated checkout statistics (drives the Analytics page).
/// Subscribes to <see cref="EventBus.Checkout"/> and keeps running totals
/// plus a per-store breakdown.
/// </summary>
public sealed class CheckoutStats : IDisposable
{
    private readonly EventBus _bus;
    private readonly Dictionary<string, (int Success, int Failed)> _byStore = new(StringComparer.OrdinalIgnoreCase);
    private readonly List<Cybersole.Core.Store.CheckoutEvent> _events = new();
    private readonly object _gate = new();

    private readonly string? _historyPath;

    public CheckoutStats(EventBus bus, string? historyPath = null)
    {
        _bus = bus;
        _historyPath = historyPath;
        _bus.Checkout += OnCheckout;
        if (historyPath is not null) LoadHistory();
    }

    public int Total { get; private set; }
    public int Success { get; private set; }
    public int Failed { get; private set; }
    public decimal Spent { get; private set; }
    public DateTime? LastAt { get; private set; }

    public event EventHandler? Changed;

    /// <summary>Most recent checkouts (bounded, newest last) — used by the CSV export.</summary>
    public IReadOnlyList<Cybersole.Core.Store.CheckoutEvent> Events
    {
        get { lock (_gate) return _events.ToArray(); }
    }

    public IReadOnlyDictionary<string, (int Success, int Failed)> ByStore
    {
        get { lock (_gate) return new Dictionary<string, (int, int)>(_byStore); }
    }

    public double SuccessRate => Total == 0 ? 0 : (double)Success / Total;

    /// <summary>
    /// Events inside a window. AnalyticsView uses this to page through periods
    /// (MovePrevious / MoveNext) instead of only showing the all-time feed.
    /// </summary>
    public IReadOnlyList<Cybersole.Core.Store.CheckoutEvent> InPeriod(DateTimeOffset from,
        DateTimeOffset to)
    {
        var lo = from.UtcDateTime;
        var hi = to.UtcDateTime;
        return _events.Where(e => e.At >= lo && e.At < hi).ToList();
    }

    /// <summary>Tally for a window: attempts, successes, and money spent on successes.</summary>
    public (int Total, int Success, int Failed, decimal Spent) Summarize(DateTimeOffset from,
        DateTimeOffset to)
    {
        var events = InPeriod(from, to);
        var success = events.Count(e => e.Success);
        var spent = events
            .Where(e => e.Success)
            .Sum(e => decimal.TryParse(e.Price, System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var v) ? v : 0m);

        return (events.Count, success, events.Count - success, spent);
    }

    /// <summary>Per-store tally for a window.</summary>
    public IReadOnlyDictionary<string, (int Success, int Failed)> ByStoreInPeriod(
        DateTimeOffset from, DateTimeOffset to)
    {
        return InPeriod(from, to)
            .GroupBy(e => e.Store, StringComparer.OrdinalIgnoreCase)
            .ToDictionary(
                g => g.Key,
                g => (g.Count(e => e.Success), g.Count(e => !e.Success)),
                StringComparer.OrdinalIgnoreCase);
    }

    /// <summary>
    /// Split the history into fixed buckets, newest first. Used by the analytics chart to
    /// show a period rather than the whole lifetime.
    /// </summary>
    public IReadOnlyList<(DateTimeOffset From, DateTimeOffset To, int Total, int Success)> Buckets(
        TimeSpan width, int count = 12)
    {
        var now = DateTimeOffset.UtcNow;
        var buckets = new List<(DateTimeOffset, DateTimeOffset, int, int)>(count);

        for (var i = 0; i < count; i++)
        {
            var to = now - TimeSpan.FromTicks(width.Ticks * i);
            var from = to - width;
            var slice = InPeriod(from, to);
            buckets.Add((from, to, slice.Count, slice.Count(e => e.Success)));
        }

        return buckets;
    }

    private void OnCheckout(object? sender, CheckoutEvent evt)
    {
        lock (_gate)
        {
            Total++;
            if (evt.Success) Success++; else Failed++;

            if (!_byStore.TryGetValue(evt.Store, out var entry)) entry = (0, 0);
            _byStore[evt.Store] = evt.Success
                ? (entry.Success + 1, entry.Failed)
                : (entry.Success, entry.Failed + 1);

            if (evt.Success && decimal.TryParse(evt.Price,
                    System.Globalization.NumberStyles.Any,
                    System.Globalization.CultureInfo.InvariantCulture, out var price))
                Spent += price;

            _events.Add(evt);
            if (_events.Count > 2000) _events.RemoveRange(0, _events.Count - 2000);

            LastAt = DateTime.UtcNow;
        }

        if (Total % 25 == 0) Flush();

        Changed?.Invoke(this, EventArgs.Empty);
    }

    /// <summary>Restore aggregates from a previous session's checkout history.</summary>
    private void LoadHistory()
    {
        try
        {
            if (_historyPath is null || !File.Exists(_historyPath)) return;
            var json = File.ReadAllText(_historyPath);
            var list = Newtonsoft.Json.JsonConvert
                .DeserializeObject<List<Cybersole.Core.Store.CheckoutEvent>>(json);
            if (list is null) return;

            lock (_gate)
            {
                foreach (var evt in list)
                {
                    _events.Add(evt);
                    Total++;
                    if (evt.Success) Success++; else Failed++;

                    if (!_byStore.TryGetValue(evt.Store, out var entry)) entry = (0, 0);
                    _byStore[evt.Store] = evt.Success
                        ? (entry.Success + 1, entry.Failed)
                        : (entry.Success, entry.Failed + 1);

                    if (evt.Success && decimal.TryParse(evt.Price,
                            System.Globalization.NumberStyles.Any,
                            System.Globalization.CultureInfo.InvariantCulture, out var price))
                        Spent += price;
                }
            }
        }
        catch
        {
            // a corrupt history file must never block startup
        }
    }

    /// <summary>Persist the bounded history to disk (called on shutdown).</summary>
    public void Flush()
    {
        if (_historyPath is null) return;

        // R130: nothing to persist and nothing on disk means this instance was constructed and thrown
        // away — a probe, a test, a settings page opened and closed. Creating the directory and writing
        // "[]" there is a side effect nobody asked for: it turns a read into a filesystem write, and on
        // a read-only install it turns into an exception swallowed by the catch below.
        if (_events.Count == 0 && !File.Exists(_historyPath)) return;

        try
        {
            var dir = Path.GetDirectoryName(_historyPath);
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            var json = Newtonsoft.Json.JsonConvert.SerializeObject(_events);
            File.WriteAllText(_historyPath, json);
        }
        catch
        {
            // best effort
        }
    }

    public void Dispose()
    {
        _bus.Checkout -= OnCheckout;
        Flush();
    }
}
