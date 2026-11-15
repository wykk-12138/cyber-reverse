using System.Collections.Concurrent;

namespace Cybersole.Http;

/// <summary>
/// Keeps finished TLS 1.2 sessions around so a second request to the same host does not pay
/// for another full handshake.
///
/// Why this exists: the p50 comparison against SChannel came out at 0.92x (own TLS slightly
/// ahead) while p95 was 586ms vs 520ms. The gap is not crypto speed — it is that
/// <see cref="NetClient"/> opened a fresh TCP + TLS connection for every request, and a
/// checkout run makes a dozen of them to the same host. SChannel pools; the hand-written path
/// did not.
///
/// A pooled client is only handed out while it is young enough to be worth reusing. TLS 1.2
/// servers close idle connections without telling the client, so an aged-out connection is
/// closed here instead of being handed out and failing mid-request.
/// </summary>
public sealed class Tls12Pool : IDisposable
{
    /// <summary>
    /// How long an idle connection stays eligible. Well under the usual 60-120s server-side
    /// idle timeout, because being wrong here means a request that fails after the write.
    /// </summary>
    public static readonly TimeSpan MaxIdle = TimeSpan.FromSeconds(45);

    private readonly ConcurrentDictionary<string, ConcurrentBag<Entry>> _idle = new();
    private bool _disposed;

    private sealed record Entry(Tls12Client Client, DateTime IdleSince);

    /// <summary>Pool key: the host, the port, and the fingerprint that produced the session.</summary>
    private static string KeyOf(string host, int port, TlsProfile profile) =>
        string.Concat(host.ToLowerInvariant(), ":", port.ToString(),
            ":", profile.Name, ":", profile.Ja3Hash);

    /// <summary>
    /// Take a live client for this endpoint, or open one. The caller owns the result until it
    /// calls <see cref="Return"/>; an exception inside the request should call
    /// <see cref="Discard"/> instead.
    /// </summary>
    public async Task<Tls12Client> RentAsync(string host, int port, TlsProfile profile,
        TimeSpan? timeout, CancellationToken ct)
    {
        if (!_disposed && _idle.TryGetValue(KeyOf(host, port, profile), out var bag))
        {
            while (bag.TryTake(out var entry))
            {
                if (DateTime.UtcNow - entry.IdleSince < MaxIdle)
                    return entry.Client;

                // too old to trust: TLS servers drop idle sockets silently
                try { entry.Client.Dispose(); } catch (Exception) { /* already gone */ }
            }
        }

        return await Tls12Client.ConnectAsync(host, port, profile, timeout, ct)
            .ConfigureAwait(false);
    }

    /// <summary>Give a healthy client back for the next caller.</summary>
    public void Return(string host, int port, TlsProfile profile, Tls12Client client)
    {
        if (_disposed || client is null) { client?.Dispose(); return; }

        _idle.GetOrAdd(KeyOf(host, port, profile), _ => new ConcurrentBag<Entry>())
            .Add(new Entry(client, DateTime.UtcNow));
    }

    /// <summary>
    /// A client that saw an error is not safe to reuse — the record sequence numbers are no
    /// longer trustworthy, so a retry on the same session would fail again.
    /// </summary>
    public void Discard(Tls12Client? client)
    {
        try { client?.Dispose(); } catch (Exception) { /* already gone */ }
    }

    /// <summary>Idle connections currently held, for tests and diagnostics.</summary>
    public int IdleCount => _idle.Values.Sum(b => b.Count);

    public void Dispose()
    {
        _disposed = true;

        foreach (var bag in _idle.Values)
            while (bag.TryTake(out var entry))
            {
                try { entry.Client.Dispose(); } catch (Exception) { /* already gone */ }
            }

        _idle.Clear();
    }
}
