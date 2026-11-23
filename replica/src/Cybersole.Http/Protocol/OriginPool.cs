using Cybersole.Http.Profiles;
using Cybersole.Http.Tls;
using Cybersole.Http.X509;

namespace Cybersole.Http.Protocol;

/// <summary>
/// Checkout lease representing either a shared stream slot on a multiplexed connection (<c>h2</c>/<c>HTTP/3</c>)
/// or exclusive ownership of a single-stream <c>http/1.1</c> connection.
/// </summary>
public sealed class PooledConnectionLease : IAsyncDisposable
{
    private readonly OriginPool _pool;
    private readonly ConnectionKey _key;
    private readonly OriginPool.MuxEntry? _muxEntry;
    private int _disposed;
    private volatile bool _discardRequested;

    internal PooledConnectionLease(
        OriginPool pool,
        ConnectionKey key,
        IMultiplexedConnection connection,
        bool wasReused,
        OriginPool.MuxEntry? muxEntry)
    {
        _pool = pool;
        _key = key;
        Connection = connection;
        WasReused = wasReused;
        _muxEntry = muxEntry;
    }

    public IMultiplexedConnection Connection { get; }
    public bool WasReused { get; }
    internal bool DiscardRequested => _discardRequested;
    internal ConnectionKey Key => _key;
    internal OriginPool.MuxEntry? MuxSlot => _muxEntry;

    public void MarkUnusable() => _discardRequested = true;

    public async ValueTask DisposeAsync()
    {
        if (Interlocked.Exchange(ref _disposed, 1) == 0)
            await _pool.ReleaseLeaseAsync(this).ConfigureAwait(false);
    }
}

/// <summary>
/// Thread-safe per-origin connection pool matching <c>OriginPool</c> (<c>0x141331EE0</c>, <c>0x141332000</c>,
/// <c>0x141332340</c>): supports multiplexed <c>h2</c>/<c>h3</c> stream sharing, exclusive <c>http/1.1</c>
/// checkout leases, 90s idle eviction, and one-shot retry on fresh connections for retryable stale-connection errors.
/// </summary>
public sealed class OriginPool : IAsyncDisposable
{
    public static readonly TimeSpan DefaultIdleTimeout = TimeSpan.FromSeconds(90);
    public const int DefaultMaxConnectionsPerOrigin = 100;

    internal sealed class MuxEntry
    {
        public MuxEntry(IMultiplexedConnection connection, DateTimeOffset lastUsedUtc, int reservedStreams)
        {
            Connection = connection;
            LastUsedUtc = lastUsedUtc;
            ReservedStreams = reservedStreams;
        }

        public IMultiplexedConnection Connection { get; }
        public DateTimeOffset LastUsedUtc { get; set; }
        public int ReservedStreams { get; set; }
    }

    private sealed class IdleHttp1Entry
    {
        public IdleHttp1Entry(IMultiplexedConnection connection, DateTimeOffset lastUsedUtc)
        {
            Connection = connection;
            LastUsedUtc = lastUsedUtc;
        }

        public IMultiplexedConnection Connection { get; }
        public DateTimeOffset LastUsedUtc { get; }
    }

    private sealed class InFlightConnect
    {
        public InFlightConnect(CancellationToken poolToken)
        {
            Cts = CancellationTokenSource.CreateLinkedTokenSource(poolToken);
        }

        public CancellationTokenSource Cts { get; }
        public TaskCompletionSource<bool> Tcs { get; } =
            new(TaskCreationOptions.RunContinuationsAsynchronously);
        public int Waiters;
        public bool Disposing;
    }

    private sealed class OriginBucket
    {
        public readonly List<MuxEntry> Multiplexed = new();
        public readonly List<IdleHttp1Entry> IdleHttp1 = new();
        public readonly List<TaskCompletionSource> SlotWaiters = new();
        public int CheckedOutHttp1Count;
        public int PendingDialsCount;
        public InFlightConnect? InFlight;

        public int TotalConnections =>
            Multiplexed.Count + IdleHttp1.Count + CheckedOutHttp1Count + PendingDialsCount;
    }

    private readonly Func<ConnectionKey, CancellationToken, Task<IMultiplexedConnection>> _connector;
    private readonly TimeSpan _idleTimeout;
    private readonly int _maxConnectionsPerOrigin;
    private readonly Func<DateTimeOffset> _clock;
    private readonly object _gate = new();
    private readonly Dictionary<ConnectionKey, OriginBucket> _buckets = new();
    private readonly CancellationTokenSource _disposeCts = new();
    private readonly TimeSpan _cleanupPeriod;
    private Timer? _cleanupTimer;
    private bool _disposed;

    public OriginPool(
        Func<ConnectionKey, CancellationToken, Task<IMultiplexedConnection>> connector,
        TimeSpan? idleTimeout = null,
        int maxConnectionsPerOrigin = DefaultMaxConnectionsPerOrigin,
        Func<DateTimeOffset>? clock = null)
    {
        _connector = connector ?? throw new ArgumentNullException(nameof(connector));
        TimeSpan effectiveIdle = idleTimeout ?? DefaultIdleTimeout;
        if (effectiveIdle < TimeSpan.Zero)
            throw new ArgumentOutOfRangeException(nameof(idleTimeout), "IdleTimeout cannot be negative.");
        if (maxConnectionsPerOrigin < 0)
            throw new ArgumentOutOfRangeException(nameof(maxConnectionsPerOrigin), "MaxConnectionsPerOrigin cannot be negative.");

        _idleTimeout = effectiveIdle;
        _maxConnectionsPerOrigin = maxConnectionsPerOrigin;
        _clock = clock ?? (() => DateTimeOffset.UtcNow);

        double periodSeconds = Math.Clamp(_idleTimeout.TotalSeconds / 3.0, 1.0, 30.0);
        _cleanupPeriod = TimeSpan.FromSeconds(periodSeconds);
    }

    public OriginPool(
        ProtocolRacer racer,
        Func<ConnectionKey, ClientProfile> profileResolver,
        ProxySpec? proxy = null,
        CertificateVerifyOptions? verifyOptions = null,
        LruTlsSessionCache? sessionCache = null,
        TimeSpan? idleTimeout = null,
        int maxConnectionsPerOrigin = DefaultMaxConnectionsPerOrigin,
        Func<DateTimeOffset>? clock = null)
        : this(
            (key, ct) => racer.ConnectAsync(key, profileResolver(key), proxy, verifyOptions, sessionCache, ct),
            idleTimeout,
            maxConnectionsPerOrigin,
            clock)
    {
        ArgumentNullException.ThrowIfNull(racer);
        ArgumentNullException.ThrowIfNull(profileResolver);
    }

    public TimeSpan IdleTimeout => _idleTimeout;
    public int MaxConnectionsPerOrigin => _maxConnectionsPerOrigin;

    public int PooledConnectionCount
    {
        get
        {
            lock (_gate)
            {
                int total = 0;
                foreach (OriginBucket bucket in _buckets.Values)
                    total += bucket.Multiplexed.Count + bucket.IdleHttp1.Count;
                return total;
            }
        }
    }

    public async Task<PooledConnectionLease> CheckoutAsync(
        ConnectionKey key,
        bool forceFresh = false,
        CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        cancellationToken.ThrowIfCancellationRequested();

        while (true)
        {
            cancellationToken.ThrowIfCancellationRequested();

            List<IMultiplexedConnection>? toDispose = null;
            InFlightConnect? joinAttempt = null;
            TaskCompletionSource? slotWaiter = null;
            InFlightConnect? ownAttempt = null;
            PooledConnectionLease? reusedLease = null;

            lock (_gate)
            {
                ObjectDisposedException.ThrowIf(_disposed, this);

                DateTimeOffset now = _clock();
                OriginBucket bucket = GetOrCreateBucketLocked(key);
                PruneBucketLocked(bucket, now, ref toDispose);

                if (!forceFresh)
                {
                    // 1. Reserve slot on an existing multiplexed (H2/H3) connection first.
                    for (int i = 0; i < bucket.Multiplexed.Count; i++)
                    {
                        MuxEntry mux = bucket.Multiplexed[i];
                        int effectiveActive = Math.Max(mux.ReservedStreams, mux.Connection.ActiveStreams);
                        if (mux.Connection.IsUsable &&
                            mux.Connection.CanAcceptNewStream() &&
                            effectiveActive < mux.Connection.MaxConcurrentStreams)
                        {
                            mux.ReservedStreams++;
                            mux.LastUsedUtc = now;
                            reusedLease = new PooledConnectionLease(this, key, mux.Connection, wasReused: true, mux);
                            break;
                        }
                    }

                    // 2. Pop LIFO idle HTTP/1.1 connection exclusively.
                    if (reusedLease is null && bucket.IdleHttp1.Count > 0)
                    {
                        int lastIdx = bucket.IdleHttp1.Count - 1;
                        IdleHttp1Entry idle = bucket.IdleHttp1[lastIdx];
                        bucket.IdleHttp1.RemoveAt(lastIdx);
                        bucket.CheckedOutHttp1Count++;
                        reusedLease = new PooledConnectionLease(this, key, idle.Connection, wasReused: true, muxEntry: null);
                    }

                    // 3. Join an in-flight cold dial if present.
                    if (reusedLease is null && bucket.InFlight is not null)
                    {
                        joinAttempt = bucket.InFlight;
                        joinAttempt.Waiters++;
                    }
                }

                if (reusedLease is null && joinAttempt is null)
                {
                    if (_maxConnectionsPerOrigin > 0 &&
                        bucket.TotalConnections >= _maxConnectionsPerOrigin &&
                        (bucket.CheckedOutHttp1Count > 0 || bucket.PendingDialsCount > 0 || bucket.Multiplexed.Count > 0))
                    {
                        slotWaiter = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
                        bucket.SlotWaiters.Add(slotWaiter);
                    }
                    else
                    {
                        bucket.PendingDialsCount++;
                        ownAttempt = new InFlightConnect(_disposeCts.Token) { Waiters = 1 };
                        if (!forceFresh && bucket.InFlight is null)
                            bucket.InFlight = ownAttempt;
                    }
                }
            }

            if (toDispose is not null)
                await DisposeConnectionsAsync(toDispose).ConfigureAwait(false);

            if (reusedLease is not null)
                return reusedLease;

            if (joinAttempt is not null)
            {
                try
                {
                    await joinAttempt.Tcs.Task.WaitAsync(cancellationToken).ConfigureAwait(false);
                }
                finally
                {
                    ReleaseInFlightWaiter(joinAttempt);
                }

                forceFresh = false;
                continue;
            }

            if (slotWaiter is not null)
            {
                try
                {
                    await slotWaiter.Task.WaitAsync(cancellationToken).ConfigureAwait(false);
                }
                finally
                {
                    lock (_gate)
                    {
                        if (_buckets.TryGetValue(key, out OriginBucket? b))
                            b.SlotWaiters.Remove(slotWaiter);
                    }
                }

                continue;
            }

            return await ExecuteDialAndPublishAsync(key, ownAttempt!, cancellationToken).ConfigureAwait(false);
        }
    }

    /// <summary>
    /// Executes <paramref name="request"/> using a pooled or newly dialed connection, retrying once on a
    /// fresh connection when a reused connection throws a retryable stale-socket / GOAWAY / REFUSED_STREAM error.
    /// </summary>
    public async Task<PureHttpResponse> SendWithRetryAsync(
        ConnectionKey key,
        PureHttpRequest request,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(request);
        ObjectDisposedException.ThrowIf(_disposed, this);

        bool alreadyRetried = false;
        while (true)
        {
            PooledConnectionLease lease = await CheckoutAsync(
                key,
                forceFresh: alreadyRetried,
                cancellationToken: cancellationToken).ConfigureAwait(false);

            try
            {
                PureHttpResponse response = await lease.Connection.SendAsync(request, cancellationToken).ConfigureAwait(false);
                if (!lease.Connection.IsUsable)
                    lease.MarkUnusable();
                return response;
            }
            catch (Exception ex) when (ShouldRetryOnFreshConnection(request, ex, lease.WasReused, alreadyRetried, cancellationToken))
            {
                lease.MarkUnusable();
                alreadyRetried = true;
            }
            catch
            {
                if (!lease.Connection.IsUsable)
                    lease.MarkUnusable();
                throw;
            }
            finally
            {
                await lease.DisposeAsync().ConfigureAwait(false);
            }
        }
    }

    /// <summary>
    /// Evaluates whether a failed request on a pooled connection may automatically retry once on a fresh connection,
    /// matching <c>CanRetryOnFreshConnection</c> (<c>0x141332340</c>) and <c>IsSafeToResend</c> (<c>0x14128AD60</c>).
    /// </summary>
    public static bool ShouldRetryOnFreshConnection(
        PureHttpRequest request,
        Exception exception,
        bool wasReused,
        bool alreadyRetried,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(request);
        if (!wasReused || alreadyRetried || cancellationToken.IsCancellationRequested)
            return false;

        if (!IsRetryableException(exception))
            return false;

        if (IsSafeToResend(request))
            return true;

        return IsGuaranteedUnprocessedError(exception);
    }

    public static bool IsSafeToResend(PureHttpRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        if (request.Method.Equals("GET", StringComparison.OrdinalIgnoreCase) ||
            request.Method.Equals("HEAD", StringComparison.OrdinalIgnoreCase) ||
            request.Method.Equals("OPTIONS", StringComparison.OrdinalIgnoreCase) ||
            request.Method.Equals("TRACE", StringComparison.OrdinalIgnoreCase))
        {
            return true;
        }

        for (int i = 0; i < request.Headers.Count; i++)
        {
            string name = request.Headers[i].Name;
            if (string.Equals(name, "Idempotency-Key", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(name, "X-Idempotency-Key", StringComparison.OrdinalIgnoreCase))
            {
                return true;
            }
        }

        return false;
    }

    public async ValueTask<int> PruneIdleAsync()
    {
        List<IMultiplexedConnection>? evicted = null;
        lock (_gate)
        {
            if (_disposed)
                return 0;

            DateTimeOffset now = _clock();
            foreach (OriginBucket bucket in _buckets.Values)
            {
                PruneBucketLocked(bucket, now, ref evicted);
                WakeSlotWaitersLocked(bucket);
            }
        }

        if (evicted is null || evicted.Count == 0)
            return 0;

        await DisposeConnectionsAsync(evicted).ConfigureAwait(false);
        return evicted.Count;
    }

    internal async ValueTask ReleaseLeaseAsync(PooledConnectionLease lease)
    {
        IMultiplexedConnection? toDispose = null;
        lock (_gate)
        {
            if (_buckets.TryGetValue(lease.Key, out OriginBucket? bucket))
            {
                DateTimeOffset now = _clock();
                if (lease.MuxSlot is { } mux)
                {
                    mux.ReservedStreams = Math.Max(0, mux.ReservedStreams - 1);
                    mux.LastUsedUtc = now;

                    if (_disposed || lease.DiscardRequested || !mux.Connection.IsUsable)
                    {
                        if (mux.ReservedStreams == 0 && bucket.Multiplexed.Remove(mux))
                            toDispose = mux.Connection;
                    }
                    else
                    {
                        EnsureCleanupTimerStartedLocked();
                    }
                }
                else
                {
                    bucket.CheckedOutHttp1Count = Math.Max(0, bucket.CheckedOutHttp1Count - 1);
                    if (_disposed || lease.DiscardRequested || !lease.Connection.IsUsable || lease.Connection.ActiveStreams > 0)
                    {
                        toDispose = lease.Connection;
                    }
                    else
                    {
                        bucket.IdleHttp1.Add(new IdleHttp1Entry(lease.Connection, now));
                        EnsureCleanupTimerStartedLocked();
                    }
                }

                WakeSlotWaitersLocked(bucket);
            }
            else
            {
                if (!lease.Connection.IsUsable || lease.DiscardRequested || _disposed || !lease.Connection.SupportsMultiplexing)
                    toDispose = lease.Connection;
            }
        }

        if (toDispose is not null)
            await DisposeSingleSafeAsync(toDispose).ConfigureAwait(false);
    }

    private async Task<PooledConnectionLease> ExecuteDialAndPublishAsync(
        ConnectionKey key,
        InFlightConnect attempt,
        CancellationToken callerCt)
    {
        // Link caller cancellation through waiter refcount so canceling one waiter doesn't kill a coalesced dial.
        using CancellationTokenRegistration cancelReg = callerCt.Register(
            static state =>
            {
                var tuple = ((OriginPool Pool, InFlightConnect Attempt))state!;
                tuple.Pool.DecrementAttemptWaiter(tuple.Attempt);
            },
            (this, attempt));

        IMultiplexedConnection? conn = null;
        Exception? dialError = null;
        try
        {
            conn = await _connector(key, attempt.Cts.Token).ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            dialError = ex;
        }

        IMultiplexedConnection? toDispose = null;
        PooledConnectionLease? resultLease = null;

        lock (_gate)
        {
            OriginBucket bucket = GetOrCreateBucketLocked(key);
            bucket.PendingDialsCount = Math.Max(0, bucket.PendingDialsCount - 1);
            if (ReferenceEquals(bucket.InFlight, attempt))
                bucket.InFlight = null;

            bool callerAlive = !callerCt.IsCancellationRequested && !_disposed;
            if (dialError is not null || conn is null)
            {
                WakeSlotWaitersLocked(bucket);
                attempt.Tcs.TrySetException(dialError ?? new PureHttpException(HttpErrorKind.ConnectFailed, "Connector returned null."));
            }
            else if (callerAlive)
            {
                DateTimeOffset now = _clock();
                if (conn.SupportsMultiplexing)
                {
                    var mux = new MuxEntry(conn, now, reservedStreams: 1);
                    bucket.Multiplexed.Add(mux);
                    EnsureCleanupTimerStartedLocked();
                    resultLease = new PooledConnectionLease(this, key, conn, wasReused: false, mux);
                }
                else
                {
                    bucket.CheckedOutHttp1Count++;
                    resultLease = new PooledConnectionLease(this, key, conn, wasReused: false, muxEntry: null);
                }

                WakeSlotWaitersLocked(bucket);
                attempt.Tcs.TrySetResult(conn.SupportsMultiplexing);
            }
            else
            {
                if (_disposed || !conn.IsUsable)
                {
                    toDispose = conn;
                    attempt.Tcs.TrySetCanceled();
                }
                else if (conn.SupportsMultiplexing)
                {
                    bucket.Multiplexed.Add(new MuxEntry(conn, _clock(), reservedStreams: 0));
                    EnsureCleanupTimerStartedLocked();
                    WakeSlotWaitersLocked(bucket);
                    attempt.Tcs.TrySetResult(true);
                }
                else
                {
                    bucket.IdleHttp1.Add(new IdleHttp1Entry(conn, _clock()));
                    EnsureCleanupTimerStartedLocked();
                    WakeSlotWaitersLocked(bucket);
                    attempt.Tcs.TrySetResult(false);
                }
            }
            attempt.Disposing = true;
        }

        attempt.Cts.Dispose();

        if (toDispose is not null)
            await DisposeSingleSafeAsync(toDispose).ConfigureAwait(false);

        if (resultLease is not null)
            return resultLease;

        if (callerCt.IsCancellationRequested)
            throw new OperationCanceledException(callerCt);

        throw dialError ?? new OperationCanceledException();
    }

    private void ReleaseInFlightWaiter(InFlightConnect attempt) => DecrementAttemptWaiter(attempt);

    private void DecrementAttemptWaiter(InFlightConnect attempt)
    {
        bool shouldCancel = false;
        lock (_gate)
        {
            if (attempt.Waiters > 0)
            {
                attempt.Waiters--;
                if (attempt.Waiters == 0 && !attempt.Disposing)
                    shouldCancel = true;
            }
        }

        if (shouldCancel)
        {
            try { attempt.Cts.Cancel(); }
            catch (ObjectDisposedException) { }
        }
    }

    private OriginBucket GetOrCreateBucketLocked(ConnectionKey key)
    {
        if (!_buckets.TryGetValue(key, out OriginBucket? bucket))
        {
            bucket = new OriginBucket();
            _buckets[key] = bucket;
        }
        return bucket;
    }

    private void PruneBucketLocked(OriginBucket bucket, DateTimeOffset now, ref List<IMultiplexedConnection>? evicted)
    {
        for (int i = bucket.Multiplexed.Count - 1; i >= 0; i--)
        {
            MuxEntry mux = bucket.Multiplexed[i];
            bool idleExpired = mux.ReservedStreams == 0 &&
                               mux.Connection.ActiveStreams == 0 &&
                               now - mux.LastUsedUtc >= _idleTimeout;
            bool dead = mux.ReservedStreams == 0 && !mux.Connection.IsUsable;
            if (idleExpired || dead)
            {
                bucket.Multiplexed.RemoveAt(i);
                evicted ??= new List<IMultiplexedConnection>();
                evicted.Add(mux.Connection);
            }
        }

        for (int i = bucket.IdleHttp1.Count - 1; i >= 0; i--)
        {
            IdleHttp1Entry idle = bucket.IdleHttp1[i];
            if (now - idle.LastUsedUtc >= _idleTimeout || !idle.Connection.IsUsable || !idle.Connection.CanAcceptNewStream())
            {
                bucket.IdleHttp1.RemoveAt(i);
                evicted ??= new List<IMultiplexedConnection>();
                evicted.Add(idle.Connection);
            }
        }
    }

    private static void WakeSlotWaitersLocked(OriginBucket bucket)
    {
        if (bucket.SlotWaiters.Count == 0)
            return;

        for (int i = 0; i < bucket.SlotWaiters.Count; i++)
            bucket.SlotWaiters[i].TrySetResult();
        bucket.SlotWaiters.Clear();
    }

    private void EnsureCleanupTimerStartedLocked()
    {
        if (_disposed || _cleanupTimer is not null || _idleTimeout <= TimeSpan.Zero)
            return;

        _cleanupTimer = new Timer(
            static state => ((OriginPool)state!).OnCleanupTimerTick(),
            this,
            _cleanupPeriod,
            _cleanupPeriod);
    }

    private void OnCleanupTimerTick()
    {
        if (_disposed)
            return;

        _ = PruneIdleSafeAsync();
    }

    private async Task PruneIdleSafeAsync()
    {
        try
        {
            await PruneIdleAsync().ConfigureAwait(false);
        }
        catch
        {
            // Never allow background timer callback to throw unhandled exceptions.
        }
    }

    private static bool IsRetryableException(Exception ex)
    {
        if (HttpErrorClassifier.CanRetryOnFreshConnection(ex))
            return true;

        for (Exception? cur = ex; cur is not null; cur = cur.InnerException)
        {
            if (cur is IOException)
                return true;
            if (cur.Message.Contains("server closed the connection", StringComparison.OrdinalIgnoreCase))
                return true;
        }

        return false;
    }

    private static bool IsGuaranteedUnprocessedError(Exception ex)
    {
        for (Exception? cur = ex; cur is not null; cur = cur.InnerException)
        {
            if (cur is Http2Exception h2 &&
                (h2.H2ErrorCode == 0x07u ||
                 (h2.IsRetryableOnFreshConnection &&
                  h2.Message.Contains("GOAWAY", StringComparison.OrdinalIgnoreCase))))
            {
                return true;
            }

            if (cur is Http3Exception h3 && h3.H3ErrorCode == 0x010BUL)
                return true;
        }

        return false;
    }

    private static async Task DisposeConnectionsAsync(List<IMultiplexedConnection> connections)
    {
        for (int i = 0; i < connections.Count; i++)
            await DisposeSingleSafeAsync(connections[i]).ConfigureAwait(false);
    }

    private static async Task DisposeSingleSafeAsync(IMultiplexedConnection connection)
    {
        try
        {
            await connection.DisposeAsync().ConfigureAwait(false);
        }
        catch
        {
            // Ignore disposal exceptions on evicted/dead connections.
        }
    }

    public async ValueTask DisposeAsync()
    {
        List<IMultiplexedConnection>? toDispose = null;
        Timer? timer;

        lock (_gate)
        {
            if (_disposed)
                return;
            _disposed = true;

            timer = _cleanupTimer;
            _cleanupTimer = null;

            foreach (OriginBucket bucket in _buckets.Values)
            {
                for (int i = 0; i < bucket.Multiplexed.Count; i++)
                {
                    toDispose ??= new List<IMultiplexedConnection>();
                    toDispose.Add(bucket.Multiplexed[i].Connection);
                }
                bucket.Multiplexed.Clear();

                for (int i = 0; i < bucket.IdleHttp1.Count; i++)
                {
                    toDispose ??= new List<IMultiplexedConnection>();
                    toDispose.Add(bucket.IdleHttp1[i].Connection);
                }
                bucket.IdleHttp1.Clear();

                bucket.InFlight = null;
                WakeSlotWaitersLocked(bucket);
            }

            _buckets.Clear();
        }

        timer?.Dispose();
        _disposeCts.Cancel();

        if (toDispose is not null)
            await DisposeConnectionsAsync(toDispose).ConfigureAwait(false);

        _disposeCts.Dispose();
    }
}
