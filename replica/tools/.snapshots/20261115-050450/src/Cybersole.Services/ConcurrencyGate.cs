namespace Cybersole.Services;

/// <summary>
/// Caps how many tasks may run at once (settings.concurrency). Extracted from the
/// task engine so the limit itself can be unit-tested without spinning up HTTP.
/// </summary>
public sealed class ConcurrencyGate
{
    private readonly SemaphoreSlim _slots;
    private int _inFlight;
    private int _maxObserved;

    public ConcurrencyGate(int max) => _slots = new SemaphoreSlim(Math.Max(1, max));

    /// <summary>Tasks currently holding a slot.</summary>
    public int InFlight => Volatile.Read(ref _inFlight);

    /// <summary>High-water mark since construction (diagnostics / tests).</summary>
    public int MaxObserved => Volatile.Read(ref _maxObserved);

    public int Capacity => _slots.CurrentCount + InFlight;

    /// <summary>Waits for a free slot; dispose the returned lease to release it.</summary>
    public async Task<IDisposable> EnterAsync(CancellationToken ct = default)
    {
        await _slots.WaitAsync(ct).ConfigureAwait(false);

        var now = Interlocked.Increment(ref _inFlight);
        int observed;
        do
        {
            observed = Volatile.Read(ref _maxObserved);
            if (now <= observed) break;
        }
        while (Interlocked.CompareExchange(ref _maxObserved, now, observed) != observed);

        return new Lease(this);
    }

    private void Release()
    {
        Interlocked.Decrement(ref _inFlight);
        _slots.Release();
    }

    private sealed class Lease : IDisposable
    {
        private ConcurrencyGate? _owner;

        public Lease(ConcurrencyGate owner) => _owner = owner;

        public void Dispose() => Interlocked.Exchange(ref _owner, null)?.Release();
    }
}
