using Cybersole.Core.Store;

namespace Cybersole.Services;

/// <summary>
/// Clock service (Cybersole.Services.ClockService): keeps a server-aligned time
/// so drops can be timed to the millisecond.
/// </summary>
public sealed class ClockService : IDisposable
{
    private readonly EventBus _bus;
    private readonly Timer _timer;
    private DateTimeOffset _current = DateTimeOffset.UtcNow;
    private long _offsetMs;

    public ClockService(EventBus bus)
    {
        _bus = bus;
        _timer = new Timer(_ => SyncAsync().GetAwaiter().GetResult(),
            null, TimeSpan.FromSeconds(5), TimeSpan.FromMinutes(5));
    }

    /// <summary>Server-aligned "now" used by every task scheduler.</summary>
    public DateTimeOffset Current => _current;

    public long OffsetMs => _offsetMs;

    public event EventHandler<DateTimeOffset>? Ticked;

    public async Task SyncAsync(CancellationToken ct = default)
    {
        try
        {
            var before = DateTimeOffset.UtcNow;
            using var http = new HttpClient { Timeout = TimeSpan.FromSeconds(5) };
            using var resp = await http.SendAsync(
                new HttpRequestMessage(HttpMethod.Head, "https://api.cybersole.io"),
                HttpCompletionOption.ResponseHeadersRead, ct).ConfigureAwait(false);
            var after = DateTimeOffset.UtcNow;

            if (resp.Headers.Date is { } serverDate)
            {
                var rtt = (after - before) / 2;
                _offsetMs = (long)(serverDate - (before + rtt)).TotalMilliseconds;
                _current = DateTimeOffset.UtcNow.AddMilliseconds(_offsetMs);
                _bus.Info("Clock", $"synced offset={_offsetMs}ms rtt={(int)(after - before).TotalMilliseconds}ms");
                Ticked?.Invoke(this, _current);
            }
        }
        catch (Exception ex)
        {
            _bus.Warn("Clock", $"sync failed: {ex.Message}");
        }
    }

    public void Dispose() => _timer.Dispose();
}
