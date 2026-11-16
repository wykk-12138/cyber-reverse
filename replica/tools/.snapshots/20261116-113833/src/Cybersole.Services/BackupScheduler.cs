namespace Cybersole.Services;

/// <summary>
/// Periodic full-snapshot backup (settings.backupInterval, default 3h).
/// Extracted from AppServices so the timer behaviour can be unit-tested.
/// </summary>
public sealed class BackupScheduler : IDisposable
{
    private readonly Timer? _timer;
    private readonly Action _backup;
    private int _runs;
    private volatile bool _disposed;

    public BackupScheduler(TimeSpan interval, Action backup)
    {
        _backup = backup;

        if (interval <= TimeSpan.Zero || interval > TimeSpan.FromDays(7))
            return;                       // disabled / absurd value: no timer at all

        _timer = new Timer(_ => Tick(), null, interval, interval);
    }

    /// <summary>How many times the backup callback actually ran.</summary>
    public int Runs => Volatile.Read(ref _runs);

    public bool IsEnabled => _timer is not null;

    private void Tick()
    {
        if (_disposed) return;

        try
        {
            _backup();
            Interlocked.Increment(ref _runs);
        }
        catch
        {
            // a failed backup must never take the timer thread down
        }
    }

    public void Dispose()
    {
        _disposed = true;
        _timer?.Dispose();
    }
}
