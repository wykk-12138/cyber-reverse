using System.Globalization;
using Cybersole.Http.Crypto;

namespace Cybersole.Http.Tls;

/// <summary>
/// Cached TLS 1.3 NewSessionTicket material for session resumption (RFC 8446 §4.6.1).
/// </summary>
public sealed class TlsSessionTicket
{
    public TlsSessionTicket(
        byte[] ticket,
        uint ticketAgeAdd,
        uint lifetimeSeconds,
        DateTimeOffset issuedAtUtc,
        byte[] resumptionMasterSecret,
        byte[]? ticketNonce,
        ushort cipherSuite,
        HashAlgorithmKind hashAlg,
        string? negotiatedAlpn = null,
        uint maxEarlyDataSize = 0,
        byte[]? psk = null)
    {
        Ticket = ticket ?? throw new ArgumentNullException(nameof(ticket));
        TicketAgeAdd = ticketAgeAdd;
        LifetimeSeconds = lifetimeSeconds;
        IssuedAtUtc = issuedAtUtc;
        ResumptionMasterSecret = resumptionMasterSecret ?? Array.Empty<byte>();
        TicketNonce = ticketNonce;
        CipherSuite = cipherSuite;
        HashAlg = hashAlg;
        NegotiatedAlpn = negotiatedAlpn;
        MaxEarlyDataSize = maxEarlyDataSize;
        Psk = psk is { Length: > 0 }
            ? psk
            : ResumptionMasterSecret.Length > 0
                ? DerivePsk(hashAlg, ResumptionMasterSecret, ticketNonce)
                : Array.Empty<byte>();
    }

    public byte[] Ticket { get; }
    public uint TicketAgeAdd { get; }
    public uint LifetimeSeconds { get; }
    public DateTimeOffset IssuedAtUtc { get; }
    public byte[] ResumptionMasterSecret { get; }
    public byte[]? TicketNonce { get; }
    public byte[] Psk { get; }
    public ushort CipherSuite { get; }
    public HashAlgorithmKind HashAlg { get; }
    public string? NegotiatedAlpn { get; }
    public uint MaxEarlyDataSize { get; }

    public bool IsValidForUse(DateTimeOffset now)
    {
        if (Ticket.Length == 0 || LifetimeSeconds == 0)
            return false;

        if (Psk.Length == 0 && ResumptionMasterSecret.Length == 0)
            return false;

        if (now < IssuedAtUtc)
            return false;

        return (now - IssuedAtUtc).TotalSeconds < LifetimeSeconds;
    }

    public byte[] ResolvePsk()
    {
        if (Psk.Length > 0)
            return Psk;

        if (ResumptionMasterSecret.Length > 0)
            return DerivePsk(HashAlg, ResumptionMasterSecret, TicketNonce);

        throw new InvalidOperationException("TLS session ticket has neither a PSK nor a resumption master secret.");
    }

    public uint ComputeObfuscatedTicketAge(DateTimeOffset now)
    {
        long ageMs = now > IssuedAtUtc
            ? (long)(now - IssuedAtUtc).TotalMilliseconds
            : 0L;
        if (ageMs < 0)
            ageMs = 0;
        if (ageMs > uint.MaxValue)
            ageMs = uint.MaxValue;

        return unchecked((uint)ageMs + TicketAgeAdd);
    }

    public static byte[] DerivePsk(
        HashAlgorithmKind hashAlg,
        ReadOnlySpan<byte> resumptionMasterSecret,
        ReadOnlySpan<byte> ticketNonce)
    {
        int hashLen = HashPrimitives.DigestLength(hashAlg);
        return HashPrimitives.HkdfExpandLabel(hashAlg, resumptionMasterSecret, "resumption", ticketNonce, hashLen);
    }

    internal void ClearSecrets()
    {
        ConstantTime.ZeroMemory(Psk);
        ConstantTime.ZeroMemory(ResumptionMasterSecret);
    }
}

/// <summary>
/// Thread-safe LRU cache for TLS 1.3 session tickets matching <c>LruTlsSessionCache</c>
/// (capacity 32 in <c>TlsHttpClient</c>, <c>sub_1412A3040..sub_1412A32E0</c>).
/// </summary>
public sealed class LruTlsSessionCache
{
    public const int DefaultCapacity = 32;

    private sealed class CacheEntry
    {
        public CacheEntry(string key, TlsSessionTicket ticket)
        {
            Key = key;
            Ticket = ticket;
        }

        public string Key { get; }
        public TlsSessionTicket Ticket { get; set; }
    }

    private readonly object _gate = new();
    private readonly int _capacity;
    private readonly Dictionary<string, LinkedListNode<CacheEntry>> _map;
    private readonly LinkedList<CacheEntry> _lru;

    public LruTlsSessionCache(int capacity = DefaultCapacity)
    {
        if (capacity <= 0)
            throw new ArgumentOutOfRangeException(nameof(capacity), "LRU cache capacity must be >= 1.");

        _capacity = capacity;
        _map = new Dictionary<string, LinkedListNode<CacheEntry>>(capacity, StringComparer.Ordinal);
        _lru = new LinkedList<CacheEntry>();
    }

    public int Capacity => _capacity;

    public int Count
    {
        get
        {
            lock (_gate)
            {
                return _map.Count;
            }
        }
    }

    public static string MakeKey(string host, int port, string? profileKey = null)
    {
        string normalizedHost = string.IsNullOrWhiteSpace(host)
            ? string.Empty
            : host.Trim().TrimEnd('.').ToLowerInvariant();
        string prof = profileKey ?? string.Empty;
        return string.Concat(normalizedHost, ":", port.ToString(CultureInfo.InvariantCulture), "|", prof);
    }

    public static string MakeKey((string Host, int Port, string ProfileKey) tuple)
        => MakeKey(tuple.Host, tuple.Port, tuple.ProfileKey);

    public void Put(string host, int port, string? profileKey, TlsSessionTicket ticket)
        => Put(MakeKey(host, port, profileKey), ticket);

    public void Put((string Host, int Port, string ProfileKey) key, TlsSessionTicket ticket)
        => Put(MakeKey(key), ticket);

    public void Put(string key, TlsSessionTicket ticket)
    {
        ArgumentNullException.ThrowIfNull(key);
        ArgumentNullException.ThrowIfNull(ticket);

        lock (_gate)
        {
            if (_map.TryGetValue(key, out LinkedListNode<CacheEntry>? existing))
            {
                existing.Value.Ticket = ticket;
                _lru.Remove(existing);
                _lru.AddFirst(existing);
                return;
            }

            if (_map.Count >= _capacity && _lru.Last is { } tail)
            {
                _lru.RemoveLast();
                _map.Remove(tail.Value.Key);
            }

            var node = new LinkedListNode<CacheEntry>(new CacheEntry(key, ticket));
            _lru.AddFirst(node);
            _map[key] = node;
        }
    }

    public bool TryTake(string host, int port, string? profileKey, out TlsSessionTicket? ticket, DateTimeOffset? now = null)
        => TryTake(MakeKey(host, port, profileKey), out ticket, now);

    public bool TryTake((string Host, int Port, string ProfileKey) key, out TlsSessionTicket? ticket, DateTimeOffset? now = null)
        => TryTake(MakeKey(key), out ticket, now);

    public bool TryTake(string key, out TlsSessionTicket? ticket, DateTimeOffset? now = null)
    {
        ArgumentNullException.ThrowIfNull(key);
        DateTimeOffset effectiveNow = now ?? DateTimeOffset.UtcNow;

        lock (_gate)
        {
            PruneExpiredLocked(effectiveNow);

            if (_map.Remove(key, out LinkedListNode<CacheEntry>? node))
            {
                _lru.Remove(node);
                if (node.Value.Ticket.IsValidForUse(effectiveNow))
                {
                    ticket = node.Value.Ticket;
                    return true;
                }
            }

            ticket = null;
            return false;
        }
    }

    public bool TryPeek(string host, int port, string? profileKey, out TlsSessionTicket? ticket, DateTimeOffset? now = null)
        => TryPeek(MakeKey(host, port, profileKey), out ticket, now);

    public bool TryPeek((string Host, int Port, string ProfileKey) key, out TlsSessionTicket? ticket, DateTimeOffset? now = null)
        => TryPeek(MakeKey(key), out ticket, now);

    public bool TryPeek(string key, out TlsSessionTicket? ticket, DateTimeOffset? now = null)
    {
        ArgumentNullException.ThrowIfNull(key);
        DateTimeOffset effectiveNow = now ?? DateTimeOffset.UtcNow;

        lock (_gate)
        {
            PruneExpiredLocked(effectiveNow);

            if (_map.TryGetValue(key, out LinkedListNode<CacheEntry>? node) &&
                node.Value.Ticket.IsValidForUse(effectiveNow))
            {
                _lru.Remove(node);
                _lru.AddFirst(node);
                ticket = node.Value.Ticket;
                return true;
            }

            ticket = null;
            return false;
        }
    }

    public void Clear()
    {
        lock (_gate)
        {
            _lru.Clear();
            _map.Clear();
        }
    }

    private void PruneExpiredLocked(DateTimeOffset now)
    {
        LinkedListNode<CacheEntry>? cur = _lru.Last;
        while (cur is not null)
        {
            LinkedListNode<CacheEntry>? prev = cur.Previous;
            if (!cur.Value.Ticket.IsValidForUse(now))
            {
                _lru.Remove(cur);
                _map.Remove(cur.Value.Key);
            }
            cur = prev;
        }
    }
}
