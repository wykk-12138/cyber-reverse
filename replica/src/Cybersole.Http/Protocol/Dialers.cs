using System.Buffers.Binary;
using System.Net;
using System.Net.Sockets;
using System.Text;
using Cybersole.Http.Tls;
using Cybersole.Http.X509;

namespace Cybersole.Http.Protocol;

/// <summary>
/// Thread-safe LRU + TTL DNS resolution cache (max capacity 4096 per Cybersole.Http DnsCache)
/// that bypasses DNS for IP literals and cleanly separates IPv6 and IPv4 address families.
/// </summary>
public sealed class DnsCache
{
    public const int DefaultMaxCapacity = 4096;
    public static readonly TimeSpan DefaultTtl = TimeSpan.FromSeconds(30);

    private readonly int _maxCapacity;
    private readonly TimeSpan _defaultTtl;
    private readonly Func<string, CancellationToken, Task<IPAddress[]>> _resolver;
    private readonly object _gate = new();
    private readonly Dictionary<string, CacheEntry> _entries = new(StringComparer.OrdinalIgnoreCase);
    private readonly LinkedList<string> _lru = new();

    private sealed class CacheEntry
    {
        public CacheEntry(string key, Task<IPAddress[]> task, long expiresAtMs, LinkedListNode<string> node)
        {
            Key = key;
            Task = task;
            ExpiresAtMs = expiresAtMs;
            Node = node;
        }

        public string Key { get; }
        public Task<IPAddress[]> Task { get; }
        public long ExpiresAtMs { get; }
        public LinkedListNode<string> Node { get; }
    }

    public DnsCache(
        int maxCapacity = DefaultMaxCapacity,
        TimeSpan? defaultTtl = null,
        Func<string, CancellationToken, Task<IPAddress[]>>? resolver = null)
    {
        if (maxCapacity < 1)
            throw new ArgumentOutOfRangeException(nameof(maxCapacity), "DNS cache capacity must be at least 1.");

        TimeSpan effectiveTtl = defaultTtl ?? DefaultTtl;
        if (effectiveTtl < TimeSpan.Zero)
            throw new ArgumentOutOfRangeException(nameof(defaultTtl), "DNS cache TTL cannot be negative.");

        _maxCapacity = maxCapacity;
        _defaultTtl = effectiveTtl;
        _resolver = resolver ?? ((host, ct) => Dns.GetHostAddressesAsync(host, ct));
    }

    public int MaxCapacity => _maxCapacity;

    public TimeSpan DefaultTtlDuration => _defaultTtl;

    public int Count
    {
        get
        {
            lock (_gate)
                return _entries.Count;
        }
    }

    public void Clear()
    {
        lock (_gate)
        {
            _entries.Clear();
            _lru.Clear();
        }
    }

    public static bool TryParseIpLiteral(string? host, out IPAddress? address)
    {
        address = null;
        if (string.IsNullOrWhiteSpace(host))
            return false;

        string trimmed = host.Trim();
        if (trimmed.Length >= 2 && trimmed[0] == '[' && trimmed[^1] == ']')
            trimmed = trimmed[1..^1];

        int zoneIdx = trimmed.IndexOf('%');
        string hostWithoutZone = zoneIdx >= 0 ? trimmed[..zoneIdx] : trimmed;

        UriHostNameType hostType = Uri.CheckHostName(hostWithoutZone);
        if (hostType is not (UriHostNameType.IPv4 or UriHostNameType.IPv6))
            return false;

        return IPAddress.TryParse(trimmed, out address);
    }

    public static (IPAddress[] IPv6, IPAddress[] IPv4) SplitAddressFamilies(IEnumerable<IPAddress> addresses)
    {
        ArgumentNullException.ThrowIfNull(addresses);

        var ipv6 = new List<IPAddress>();
        var ipv4 = new List<IPAddress>();
        var seen = new HashSet<IPAddress>();

        foreach (IPAddress raw in addresses)
        {
            IPAddress addr = raw.IsIPv4MappedToIPv6 ? raw.MapToIPv4() : raw;
            if (!seen.Add(addr))
                continue;

            if (addr.AddressFamily == AddressFamily.InterNetworkV6)
                ipv6.Add(addr);
            else if (addr.AddressFamily == AddressFamily.InterNetwork)
                ipv4.Add(addr);
        }

        return (ipv6.ToArray(), ipv4.ToArray());
    }

    public Task<IPAddress[]> ResolveAsync(string host, CancellationToken cancellationToken = default)
        => ResolveAsync(host, ttl: null, cancellationToken);

    public async Task<IPAddress[]> ResolveAsync(string host, TimeSpan? ttl, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(host))
            throw new ArgumentException("Host cannot be null or empty.", nameof(host));

        cancellationToken.ThrowIfCancellationRequested();

        if (TryParseIpLiteral(host, out IPAddress? literal) && literal is not null)
            return new[] { literal };

        string key = NormalizeHostKey(host);
        TimeSpan effectiveTtl = ttl ?? _defaultTtl;
        long nowMs = Environment.TickCount64;
        long ttlMs = effectiveTtl <= TimeSpan.Zero ? 0 : (long)Math.Ceiling(effectiveTtl.TotalMilliseconds);

        Task<IPAddress[]> lookupTask;
        lock (_gate)
        {
            if (_entries.TryGetValue(key, out CacheEntry? existing))
            {
                if (nowMs < existing.ExpiresAtMs && !existing.Task.IsFaulted && !existing.Task.IsCanceled)
                {
                    _lru.Remove(existing.Node);
                    _lru.AddFirst(existing.Node);
                    lookupTask = existing.Task;
                    goto AwaitResult;
                }

                _entries.Remove(key);
                _lru.Remove(existing.Node);
            }

            if (ttlMs == 0)
            {
                lookupTask = ResolveDirectAsync(key, cancellationToken);
                goto AwaitResult;
            }

            while (_entries.Count >= _maxCapacity && _lru.Last is not null)
            {
                LinkedListNode<string> victim = _lru.Last;
                _lru.RemoveLast();
                _entries.Remove(victim.Value);
            }

            var node = new LinkedListNode<string>(key);
            _lru.AddFirst(node);
            long expiresAt = nowMs + ttlMs;
            Task<IPAddress[]> sharedTask = ResolveAndEvictOnFaultAsync(key, expiresAt, node);
            _entries[key] = new CacheEntry(key, sharedTask, expiresAt, node);
            lookupTask = sharedTask;
        }

    AwaitResult:
        return await lookupTask.WaitAsync(cancellationToken).ConfigureAwait(false);
    }

    public async Task<(IPAddress[] IPv6, IPAddress[] IPv4)> ResolveSeparatedAsync(
        string host,
        CancellationToken cancellationToken = default)
    {
        IPAddress[] all = await ResolveAsync(host, cancellationToken).ConfigureAwait(false);
        return SplitAddressFamilies(all);
    }

    private async Task<IPAddress[]> ResolveAndEvictOnFaultAsync(string key, long expiresAt, LinkedListNode<string> node)
    {
        try
        {
            return await ResolveDirectAsync(key, CancellationToken.None).ConfigureAwait(false);
        }
        catch
        {
            lock (_gate)
            {
                if (_entries.TryGetValue(key, out CacheEntry? current) && ReferenceEquals(current.Node, node) && current.ExpiresAtMs == expiresAt)
                {
                    _entries.Remove(key);
                    _lru.Remove(node);
                }
            }
            throw;
        }
    }

    private async Task<IPAddress[]> ResolveDirectAsync(string key, CancellationToken cancellationToken)
    {
        IPAddress[] raw = await _resolver(key, cancellationToken).ConfigureAwait(false);
        if (raw is null || raw.Length == 0)
            return Array.Empty<IPAddress>();

        (IPAddress[] ipv6, IPAddress[] ipv4) = SplitAddressFamilies(raw);
        var combined = new IPAddress[ipv6.Length + ipv4.Length];
        ipv6.CopyTo(combined, 0);
        ipv4.CopyTo(combined, ipv6.Length);
        return combined;
    }

    private static string NormalizeHostKey(string host)
    {
        string trimmed = host.Trim();
        if (trimmed.Length > 1 && trimmed[^1] == '.')
            trimmed = trimmed[..^1];
        return trimmed.ToLowerInvariant();
    }
}

/// <summary>
/// Direct TCP dialer implementing RFC 8305 Happy Eyeballs (IPv6 preferred with 300ms head-start
/// before racing IPv4), configurable connect timeout (30s default), and <c>Socket.NoDelay = true</c>.
/// </summary>
public sealed class DirectDialer
{
    public static readonly TimeSpan DefaultConnectTimeout = TimeSpan.FromSeconds(30);
    public static readonly TimeSpan DefaultHappyEyeballsDelay = TimeSpan.FromMilliseconds(300);

    private readonly DnsCache _dnsCache;

    public DirectDialer(
        DnsCache? dnsCache = null,
        TimeSpan? connectTimeout = null,
        TimeSpan? happyEyeballsDelay = null)
    {
        _dnsCache = dnsCache ?? new DnsCache();
        ConnectTimeout = connectTimeout ?? DefaultConnectTimeout;
        HappyEyeballsDelay = happyEyeballsDelay ?? DefaultHappyEyeballsDelay;

        if (ConnectTimeout <= TimeSpan.Zero && ConnectTimeout != Timeout.InfiniteTimeSpan)
            throw new ArgumentOutOfRangeException(nameof(connectTimeout), "ConnectTimeout must be positive or infinite.");
        if (HappyEyeballsDelay < TimeSpan.Zero)
            throw new ArgumentOutOfRangeException(nameof(happyEyeballsDelay), "HappyEyeballsDelay cannot be negative.");
    }

    public DnsCache DnsCache => _dnsCache;

    public TimeSpan ConnectTimeout { get; }

    public TimeSpan HappyEyeballsDelay { get; }

    public Task<DialedConnection> DialAsync(
        string host,
        int port,
        CancellationToken cancellationToken = default)
        => DialAsync(host, port, localAddress: null, timeoutOverride: null, cancellationToken);

    public async Task<DialedConnection> DialAsync(
        string host,
        int port,
        IPAddress? localAddress,
        TimeSpan? timeoutOverride = null,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(host))
            throw new ArgumentException("Target host cannot be empty.", nameof(host));
        if (port is < 1 or > 65535)
            throw new ArgumentOutOfRangeException(nameof(port), "Port must be between 1 and 65535.");

        TimeSpan effectiveTimeout = timeoutOverride ?? ConnectTimeout;
        using CancellationTokenSource? timeoutCts =
            effectiveTimeout > TimeSpan.Zero && effectiveTimeout != Timeout.InfiniteTimeSpan
                ? new CancellationTokenSource(effectiveTimeout)
                : null;
        using CancellationTokenSource raceCts = timeoutCts is not null
            ? CancellationTokenSource.CreateLinkedTokenSource(cancellationToken, timeoutCts.Token)
            : CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);

        (IPAddress[] ipv6, IPAddress[] ipv4) addresses;
        try
        {
            addresses = await _dnsCache.ResolveSeparatedAsync(host, raceCts.Token).ConfigureAwait(false);
        }
        catch (OperationCanceledException) when (timeoutCts is not null && timeoutCts.IsCancellationRequested && !cancellationToken.IsCancellationRequested)
        {
            throw new TimeoutException($"DNS resolution for {host}:{port} timed out after {effectiveTimeout.TotalSeconds:0.###}s.");
        }

        List<IPAddress> candidates = InterleaveCandidates(addresses.ipv6, addresses.ipv4);
        if (candidates.Count == 0)
            throw new PureHttpException(HttpErrorKind.DnsResolution, $"No IPv4 or IPv6 addresses resolved for '{host}'.");

        var active = new List<Task<(Socket? Socket, Exception? Error)>>(candidates.Count);
        int nextIndex = 0;
        Socket? winner = null;
        Exception? firstError = null;
        Task? delayTask = null;
        CancellationTokenSource? delayCts = null;

        try
        {
            while (winner is null)
            {
                if (nextIndex < candidates.Count && (active.Count == 0 || delayTask is { IsCompleted: true }))
                {
                    delayCts?.Dispose();
                    delayCts = null;
                    delayTask = null;

                    IPAddress targetIp = candidates[nextIndex++];
                    active.Add(TryConnectAddressAsync(targetIp, port, localAddress, raceCts.Token));

                    if (nextIndex < candidates.Count && HappyEyeballsDelay > TimeSpan.Zero)
                    {
                        delayCts = CancellationTokenSource.CreateLinkedTokenSource(raceCts.Token);
                        delayTask = Task.Delay(HappyEyeballsDelay, delayCts.Token);
                    }
                }

                if (active.Count == 0)
                    break;

                var waitTargets = new List<Task>(active.Count + 1);
                for (int i = 0; i < active.Count; i++)
                    waitTargets.Add(active[i]);
                if (delayTask is not null && nextIndex < candidates.Count)
                    waitTargets.Add(delayTask);

                Task completed = await Task.WhenAny(waitTargets).ConfigureAwait(false);
                if (ReferenceEquals(completed, delayTask))
                    continue;

                var attemptTask = (Task<(Socket? Socket, Exception? Error)>)completed;
                active.Remove(attemptTask);

                (Socket? connectedSocket, Exception? error) = await attemptTask.ConfigureAwait(false);
                if (connectedSocket is not null)
                {
                    winner = connectedSocket;
                    break;
                }

                firstError ??= error;
            }
        }
        finally
        {
            delayCts?.Cancel();
            delayCts?.Dispose();
            raceCts.Cancel();

            for (int i = 0; i < active.Count; i++)
            {
                try
                {
                    (Socket? losingSocket, _) = await active[i].ConfigureAwait(false);
                    losingSocket?.Dispose();
                }
                catch
                {
                    // Never allow unobserved task exceptions on losing Happy Eyeballs attempts.
                }
            }
        }

        if (winner is not null)
        {
            var remoteEndPoint = winner.RemoteEndPoint as IPEndPoint;
            return new DialedConnection(new NetworkStream(winner, ownsSocket: true), remoteEndPoint, isProxied: false);
        }

        if (cancellationToken.IsCancellationRequested)
            throw new OperationCanceledException(cancellationToken);

        if (timeoutCts is not null && timeoutCts.IsCancellationRequested)
            throw new TimeoutException($"TCP connection to {host}:{port} timed out after {effectiveTimeout.TotalSeconds:0.###}s.");

        throw new PureHttpException(
            HttpErrorKind.ConnectFailed,
            $"Failed to connect to {host}:{port}: {firstError?.Message ?? "all connection attempts failed"}",
            firstError);
    }

    private static List<IPAddress> InterleaveCandidates(IPAddress[] ipv6, IPAddress[] ipv4)
    {
        var result = new List<IPAddress>(ipv6.Length + ipv4.Length);
        int max = Math.Max(ipv6.Length, ipv4.Length);
        for (int i = 0; i < max; i++)
        {
            if (i < ipv6.Length)
                result.Add(ipv6[i]);
            if (i < ipv4.Length)
                result.Add(ipv4[i]);
        }
        return result;
    }

    private static async Task<(Socket? Socket, Exception? Error)> TryConnectAddressAsync(
        IPAddress address,
        int port,
        IPAddress? localAddress,
        CancellationToken cancellationToken)
    {
        Socket? socket = null;
        try
        {
            socket = new Socket(address.AddressFamily, SocketType.Stream, ProtocolType.Tcp)
            {
                NoDelay = true,
            };

            if (localAddress is not null && localAddress.AddressFamily == address.AddressFamily)
                socket.Bind(new IPEndPoint(localAddress, 0));

            await socket.ConnectAsync(new IPEndPoint(address, port), cancellationToken).ConfigureAwait(false);
            return (socket, null);
        }
        catch (Exception ex)
        {
            socket?.Dispose();
            return (null, ex);
        }
    }
}

/// <summary>
/// Parses proxy strings in URI (<c>http://</c>, <c>https://</c>, <c>socks5://</c>, <c>socks5h://</c>)
/// or shorthand (<c>host:port</c>, <c>host:port:user:pass</c>) forms into <see cref="ProxySpec"/>.
/// </summary>
public static class ProxyUriParser
{
    public static ProxySpec Parse(string proxyUri)
    {
        if (string.IsNullOrWhiteSpace(proxyUri))
            throw new ArgumentException("Proxy specification cannot be null or empty.", nameof(proxyUri));

        if (!TryParseCore(proxyUri, out ProxySpec? spec, out Exception? error) || spec is null)
            throw error ?? new FormatException($"Invalid proxy specification '{proxyUri}'.");

        return spec;
    }

    public static bool TryParse(string? proxyUri, out ProxySpec? spec)
        => TryParseCore(proxyUri, out spec, out _);

    private static bool TryParseCore(string? proxyUri, out ProxySpec? spec, out Exception? error)
    {
        spec = null;
        error = null;

        if (string.IsNullOrWhiteSpace(proxyUri))
        {
            error = new FormatException("Proxy specification cannot be empty.");
            return false;
        }

        string trimmed = proxyUri.Trim();
        if (trimmed.Contains("://", StringComparison.Ordinal))
            return TryParseUriFormat(trimmed, out spec, out error);

        return TryParseShorthandFormat(trimmed, out spec, out error);
    }

    private static bool TryParseUriFormat(string raw, out ProxySpec? spec, out Exception? error)
    {
        spec = null;
        error = null;

        int schemeSep = raw.IndexOf("://", StringComparison.Ordinal);
        string scheme = raw[..schemeSep].ToLowerInvariant();
        if (scheme is "socks4" or "socks4a")
        {
            error = new NotSupportedException($"Proxy scheme '{scheme}' is not supported by ProxyProtocolKind (use http, https, socks5, or socks5h).");
            return false;
        }

        (ProxyProtocolKind kind, int defaultPort, bool remoteDns) = scheme switch
        {
            "http" => (ProxyProtocolKind.Http, 80, true),
            "https" => (ProxyProtocolKind.Https, 443, true),
            "socks5" => (ProxyProtocolKind.Socks5, 1080, false),
            "socks5h" => (ProxyProtocolKind.Socks5, 1080, true),
            _ => (ProxyProtocolKind.None, 0, true),
        };

        if (kind == ProxyProtocolKind.None)
        {
            error = new FormatException($"Unsupported proxy scheme '{scheme}'.");
            return false;
        }

        if (!Uri.TryCreate(raw, UriKind.Absolute, out Uri? uri) || string.IsNullOrWhiteSpace(uri.Host))
        {
            error = new FormatException($"Malformed proxy URI '{raw}'.");
            return false;
        }

        if (!string.IsNullOrEmpty(uri.PathAndQuery) && uri.PathAndQuery != "/")
        {
            error = new FormatException($"Proxy URI cannot contain a path or query: '{raw}'.");
            return false;
        }

        int port = uri.IsDefaultPort ? defaultPort : uri.Port;
        if (port <= 0)
            port = defaultPort;

        // Verify explicit ":0" or invalid port in authority wasn't normalized away.
        string authority = uri.GetComponents(UriComponents.HostAndPort, UriFormat.Unescaped);
        int lastColon = authority.LastIndexOf(':');
        if (lastColon >= 0 && !authority.EndsWith(']'))
        {
            string explicitPortText = authority[(lastColon + 1)..];
            if (!int.TryParse(explicitPortText, out int explicitPort) || explicitPort is < 1 or > 65535)
            {
                error = new FormatException($"Invalid proxy port in '{raw}'.");
                return false;
            }
            port = explicitPort;
        }

        if (port is < 1 or > 65535)
        {
            error = new FormatException($"Proxy port {port} is outside [1, 65535].");
            return false;
        }

        string host = uri.Host;
        if (host.Length >= 2 && host[0] == '[' && host[^1] == ']')
            host = host[1..^1];

        string? username = null;
        string? password = null;
        if (!string.IsNullOrEmpty(uri.UserInfo))
        {
            int userColon = uri.UserInfo.IndexOf(':');
            if (userColon >= 0)
            {
                username = Uri.UnescapeDataString(uri.UserInfo[..userColon]);
                password = Uri.UnescapeDataString(uri.UserInfo[(userColon + 1)..]);
            }
            else
            {
                username = Uri.UnescapeDataString(uri.UserInfo);
                password = string.Empty;
            }
        }

        spec = new ProxySpec(kind, host, port, username, password, remoteDns);
        return true;
    }

    private static bool TryParseShorthandFormat(string raw, out ProxySpec? spec, out Exception? error)
    {
        spec = null;
        error = null;

        string host;
        string remainder;
        if (raw.StartsWith('['))
        {
            int closeBracket = raw.IndexOf(']');
            if (closeBracket <= 1 || closeBracket + 1 >= raw.Length || raw[closeBracket + 1] != ':')
            {
                error = new FormatException($"Malformed IPv6 proxy shorthand '{raw}'.");
                return false;
            }

            host = raw[1..closeBracket];
            remainder = raw[(closeBracket + 2)..];
        }
        else
        {
            int firstColon = raw.IndexOf(':');
            if (firstColon <= 0)
            {
                error = new FormatException($"Proxy shorthand must be 'host:port' or 'host:port:user:pass': '{raw}'.");
                return false;
            }

            host = raw[..firstColon];
            remainder = raw[(firstColon + 1)..];
        }

        string[] tail = remainder.Split(':', 3);
        if (!int.TryParse(tail[0], out int port) || port is < 1 or > 65535)
        {
            error = new FormatException($"Invalid proxy port in '{raw}'.");
            return false;
        }

        string? username = null;
        string? password = null;
        if (tail.Length == 2)
        {
            username = tail[1];
            password = string.Empty;
        }
        else if (tail.Length == 3)
        {
            username = tail[1];
            password = tail[2];
        }

        spec = new ProxySpec(ProxyProtocolKind.Http, host, port, username, password, RemoteDns: true);
        return true;
    }
}

/// <summary>
/// HTTP/HTTPS CONNECT tunnel dialer (RFC 9110 §9.3.6). For <c>https://</c> proxies, wraps the TCP
/// socket in <see cref="TlsStream"/> configured via <see cref="ProxyTlsSpec.CreateConnectionOptions"/>
/// before transmitting <c>CONNECT</c>.
/// </summary>
public sealed class HttpConnectDialer
{
    private const int MaxProxyHeaderLineBytes = 64 * 1024;
    private const int MaxProxyTotalHeaderBytes = 256 * 1024;

    private readonly DirectDialer _directDialer;

    public HttpConnectDialer(DirectDialer? directDialer = null)
    {
        _directDialer = directDialer ?? new DirectDialer();
    }

    public async Task<DialedConnection> DialAsync(
        ProxySpec proxy,
        string targetHost,
        int targetPort,
        CertificateVerifyOptions? proxyTlsVerifyOptions = null,
        IReadOnlyList<PureHttpHeader>? extraProxyHeaders = null,
        TimeSpan? connectTimeout = null,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(proxy);
        if (proxy.Kind is not (ProxyProtocolKind.Http or ProxyProtocolKind.Https))
            throw new ArgumentException($"HttpConnectDialer requires Http or Https proxy, got {proxy.Kind}.", nameof(proxy));
        if (string.IsNullOrWhiteSpace(targetHost))
            throw new ArgumentException("Target host cannot be empty.", nameof(targetHost));
        if (targetPort is < 1 or > 65535)
            throw new ArgumentOutOfRangeException(nameof(targetPort), "Target port must be between 1 and 65535.");

        DialedConnection tcpConn = await _directDialer.DialAsync(
            proxy.Host,
            proxy.Port,
            localAddress: null,
            timeoutOverride: connectTimeout,
            cancellationToken: cancellationToken).ConfigureAwait(false);

        Stream stream = tcpConn.Stream;
        try
        {
            if (proxy.Kind == ProxyProtocolKind.Https)
            {
                TlsConnectionOptions tlsOptions = ProxyTlsSpec.CreateConnectionOptions(
                    proxy.Host,
                    proxy.Port,
                    proxyTlsVerifyOptions,
                    connectTimeout);
                var proxyTls = new TlsStream(stream, tlsOptions);
                stream = proxyTls;
                await proxyTls.HandshakeAsync(cancellationToken).ConfigureAwait(false);
            }

            string authority = FormatAuthority(targetHost, targetPort);
            byte[] connectBytes = BuildConnectRequest(authority, proxy, extraProxyHeaders);
            await stream.WriteAsync(connectBytes, cancellationToken).ConfigureAwait(false);
            await stream.FlushAsync(cancellationToken).ConfigureAwait(false);

            var reader = new BufferedStreamReader(stream, leaveOpen: true);
            long headerStart = reader.TotalBytesConsumed;
            string? statusLine = await reader.ReadLineAsciiAsync(MaxProxyHeaderLineBytes, cancellationToken).ConfigureAwait(false);
            if (statusLine is null)
                throw new ProxyException("Proxy closed connection before responding to CONNECT.");

            int statusCode = ParseConnectStatusCode(statusLine);

            while (true)
            {
                string? line = await reader.ReadLineAsciiAsync(MaxProxyHeaderLineBytes, cancellationToken).ConfigureAwait(false);
                if (line is null)
                    throw new ProxyException("Proxy closed connection while reading CONNECT response headers.");
                if (reader.TotalBytesConsumed - headerStart > MaxProxyTotalHeaderBytes)
                    throw new ProxyException("Proxy CONNECT response headers exceeded maximum allowed size.");
                if (line.Length == 0)
                    break;
            }

            if (statusCode is < 200 or >= 300)
            {
                throw new ProxyException(
                    $"Proxy responded with non-2xx code: {statusCode} ({statusLine})",
                    proxyStatusCode: statusCode);
            }

            Stream tunnelStream = reader.DetachRemainingStream(leaveInnerOpen: false);
            return new DialedConnection(tunnelStream, tcpConn.RemoteEndPoint, isProxied: true);
        }
        catch
        {
            await stream.DisposeAsync().ConfigureAwait(false);
            throw;
        }
    }

    private static byte[] BuildConnectRequest(
        string authority,
        ProxySpec proxy,
        IReadOnlyList<PureHttpHeader>? extraProxyHeaders)
    {
        var sb = new StringBuilder(256);
        sb.Append("CONNECT ").Append(authority).Append(" HTTP/1.1\r\n");
        sb.Append("Host: ").Append(authority).Append("\r\n");

        if (!string.IsNullOrEmpty(proxy.Username) || !string.IsNullOrEmpty(proxy.Password))
        {
            string credentials = $"{proxy.Username ?? string.Empty}:{proxy.Password ?? string.Empty}";
            string encoded = Convert.ToBase64String(Encoding.UTF8.GetBytes(credentials));
            sb.Append("Proxy-Authorization: Basic ").Append(encoded).Append("\r\n");
        }

        bool hasUserAgent = false;
        bool hasProxyConnection = false;
        if (extraProxyHeaders is not null)
        {
            for (int i = 0; i < extraProxyHeaders.Count; i++)
            {
                PureHttpHeader hdr = extraProxyHeaders[i];
                ValidateProxyHeader(hdr.Name, hdr.Value);
                if (string.Equals(hdr.Name, "host", StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(hdr.Name, "proxy-authorization", StringComparison.OrdinalIgnoreCase))
                {
                    continue;
                }
                if (string.Equals(hdr.Name, "user-agent", StringComparison.OrdinalIgnoreCase))
                    hasUserAgent = true;
                else if (string.Equals(hdr.Name, "proxy-connection", StringComparison.OrdinalIgnoreCase))
                    hasProxyConnection = true;

                sb.Append(hdr.Name).Append(": ").Append(hdr.Value).Append("\r\n");
            }
        }

        if (!hasUserAgent)
            sb.Append("User-Agent: Go-http-client/1.1\r\n");
        if (!hasProxyConnection)
            sb.Append("Proxy-Connection: Keep-Alive\r\n");

        sb.Append("\r\n");
        return Encoding.ASCII.GetBytes(sb.ToString());
    }

    private static void ValidateProxyHeader(string name, string value)
    {
        if (string.IsNullOrWhiteSpace(name) || name.IndexOfAny(new[] { '\r', '\n', ':' }) >= 0)
            throw new ProxyException($"Invalid proxy header name '{name}'.");
        if (value is not null && value.IndexOfAny(new[] { '\r', '\n', '\0' }) >= 0)
            throw new ProxyException($"Invalid proxy header value for '{name}'.");
    }

    private static int ParseConnectStatusCode(string statusLine)
    {
        if (!statusLine.StartsWith("HTTP/1.", StringComparison.OrdinalIgnoreCase) ||
            statusLine.Length < 12 ||
            statusLine[7] < '0' || statusLine[7] > '9' ||
            statusLine[8] != ' ')
        {
            throw new ProxyException($"Invalid HTTP CONNECT status line from proxy: '{statusLine}'.");
        }

        if (!int.TryParse(statusLine.AsSpan(9, 3), out int code) || code is < 100 or > 599)
            throw new ProxyException($"Invalid HTTP CONNECT status code in '{statusLine}'.");

        if (statusLine.Length > 12 && statusLine[12] != ' ')
            throw new ProxyException($"Invalid HTTP CONNECT status line from proxy: '{statusLine}'.");

        return code;
    }

    private static string FormatAuthority(string host, int port)
    {
        string trimmed = host.Trim();
        if (trimmed.Contains(':') && !trimmed.StartsWith('['))
            return $"[{trimmed}]:{port}";
        return $"{trimmed}:{port}";
    }
}

/// <summary>
/// RFC 1928 / RFC 1929 SOCKS5 TCP dialer supporting NoAuth (<c>0x00</c>), Username/Password (<c>0x02</c>),
/// local DNS resolution (<c>socks5://</c>), and remote proxy DNS resolution (<c>socks5h://</c>, <c>ATYP=0x03</c>).
/// </summary>
public sealed class Socks5Dialer
{
    private readonly DirectDialer _directDialer;
    private readonly DnsCache _dnsCache;

    public Socks5Dialer(DirectDialer? directDialer = null, DnsCache? dnsCache = null)
    {
        _dnsCache = dnsCache ?? directDialer?.DnsCache ?? new DnsCache();
        _directDialer = directDialer ?? new DirectDialer(_dnsCache);
    }

    public async Task<DialedConnection> DialAsync(
        ProxySpec proxy,
        string targetHost,
        int targetPort,
        TimeSpan? connectTimeout = null,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(proxy);
        if (proxy.Kind != ProxyProtocolKind.Socks5)
            throw new ArgumentException($"Socks5Dialer requires Socks5 proxy, got {proxy.Kind}.", nameof(proxy));
        if (string.IsNullOrWhiteSpace(targetHost))
            throw new ArgumentException("Target host cannot be empty.", nameof(targetHost));
        if (targetPort is < 1 or > 65535)
            throw new ArgumentOutOfRangeException(nameof(targetPort), "Target port must be between 1 and 65535.");

        DialedConnection tcpConn = await _directDialer.DialAsync(
            proxy.Host,
            proxy.Port,
            localAddress: null,
            timeoutOverride: connectTimeout,
            cancellationToken: cancellationToken).ConfigureAwait(false);

        Stream stream = tcpConn.Stream;
        try
        {
            await NegotiateAuthAsync(stream, proxy, cancellationToken).ConfigureAwait(false);
            await SendConnectAndReadReplyAsync(stream, proxy, targetHost, targetPort, cancellationToken).ConfigureAwait(false);
            return new DialedConnection(stream, tcpConn.RemoteEndPoint, isProxied: true);
        }
        catch
        {
            await stream.DisposeAsync().ConfigureAwait(false);
            throw;
        }
    }

    private static async Task NegotiateAuthAsync(Stream stream, ProxySpec proxy, CancellationToken cancellationToken)
    {
        bool hasCredentials = !string.IsNullOrEmpty(proxy.Username) || !string.IsNullOrEmpty(proxy.Password);
        byte[] greeting = hasCredentials
            ? new byte[] { 0x05, 0x02, 0x00, 0x02 }
            : new byte[] { 0x05, 0x01, 0x00 };

        await stream.WriteAsync(greeting, cancellationToken).ConfigureAwait(false);
        await stream.FlushAsync(cancellationToken).ConfigureAwait(false);

        var methodSelection = new byte[2];
        await ReadExactlyAsync(stream, methodSelection, cancellationToken).ConfigureAwait(false);

        if (methodSelection[0] != 0x05)
            throw new ProxyException($"SOCKS5 proxy returned invalid greeting version 0x{methodSelection[0]:X2}.");

        byte selectedMethod = methodSelection[1];
        if (selectedMethod == 0xFF)
            throw new ProxyException("SOCKS5 proxy rejected all offered authentication methods (0xFF).");

        if (selectedMethod == 0x02)
        {
            if (!hasCredentials)
                throw new ProxyException("SOCKS5 proxy requested username/password auth (0x02) when none were offered.");

            byte[] userBytes = Encoding.UTF8.GetBytes(proxy.Username ?? string.Empty);
            byte[] passBytes = Encoding.UTF8.GetBytes(proxy.Password ?? string.Empty);
            if (userBytes.Length > 255 || passBytes.Length > 255)
                throw new ProxyException("SOCKS5 username and password must each be <= 255 UTF-8 bytes.");

            var authReq = new byte[3 + userBytes.Length + passBytes.Length];
            authReq[0] = 0x01; // RFC 1929 subnegotiation version
            authReq[1] = (byte)userBytes.Length;
            userBytes.CopyTo(authReq, 2);
            authReq[2 + userBytes.Length] = (byte)passBytes.Length;
            passBytes.CopyTo(authReq, 3 + userBytes.Length);

            await stream.WriteAsync(authReq, cancellationToken).ConfigureAwait(false);
            await stream.FlushAsync(cancellationToken).ConfigureAwait(false);

            var authResp = new byte[2];
            await ReadExactlyAsync(stream, authResp, cancellationToken).ConfigureAwait(false);
            if (authResp[0] != 0x01 || authResp[1] != 0x00)
            {
                throw new ProxyException(
                    $"SOCKS5 username/password authentication failed (status 0x{authResp[1]:X2}).",
                    proxyStatusCode: authResp[1]);
            }
        }
        else if (selectedMethod != 0x00)
        {
            throw new ProxyException($"SOCKS5 proxy selected unsupported authentication method 0x{selectedMethod:X2}.");
        }
    }

    private async Task SendConnectAndReadReplyAsync(
        Stream stream,
        ProxySpec proxy,
        string targetHost,
        int targetPort,
        CancellationToken cancellationToken)
    {
        byte atyp;
        byte[] addrPayload;

        string cleanHost = targetHost.Trim();
        if (cleanHost.Length >= 2 && cleanHost[0] == '[' && cleanHost[^1] == ']')
            cleanHost = cleanHost[1..^1];

        if (DnsCache.TryParseIpLiteral(cleanHost, out IPAddress? literalIp) && literalIp is not null)
        {
            EncodeIpAddress(literalIp, out atyp, out addrPayload);
        }
        else if (proxy.RemoteDns)
        {
            byte[] domainBytes = Encoding.UTF8.GetBytes(cleanHost);
            if (domainBytes.Length is 0 or > 255)
                throw new ProxyException($"SOCKS5 domain name length {domainBytes.Length} is invalid.");

            atyp = 0x03;
            addrPayload = new byte[1 + domainBytes.Length];
            addrPayload[0] = (byte)domainBytes.Length;
            domainBytes.CopyTo(addrPayload, 1);
        }
        else
        {
            (IPAddress[] ipv6, IPAddress[] ipv4) = await _dnsCache.ResolveSeparatedAsync(cleanHost, cancellationToken).ConfigureAwait(false);
            IPAddress? resolved = ipv4.Length > 0 ? ipv4[0] : (ipv6.Length > 0 ? ipv6[0] : null);
            if (resolved is null)
                throw new PureHttpException(HttpErrorKind.DnsResolution, $"DNS resolution failed for SOCKS5 local-DNS target '{cleanHost}'.");

            EncodeIpAddress(resolved, out atyp, out addrPayload);
        }

        var connectReq = new byte[4 + addrPayload.Length + 2];
        connectReq[0] = 0x05; // VER
        connectReq[1] = 0x01; // CMD = CONNECT
        connectReq[2] = 0x00; // RSV
        connectReq[3] = atyp;
        addrPayload.CopyTo(connectReq, 4);
        BinaryPrimitives.WriteUInt16BigEndian(connectReq.AsSpan(4 + addrPayload.Length, 2), (ushort)targetPort);

        await stream.WriteAsync(connectReq, cancellationToken).ConfigureAwait(false);
        await stream.FlushAsync(cancellationToken).ConfigureAwait(false);

        var replyHead = new byte[4];
        await ReadExactlyAsync(stream, replyHead, cancellationToken).ConfigureAwait(false);

        if (replyHead[0] != 0x05)
            throw new ProxyException($"SOCKS5 CONNECT reply returned invalid version 0x{replyHead[0]:X2}.");

        byte replyCode = replyHead[1];
        if (replyCode != 0x00)
        {
            string desc = DescribeReplyCode(replyCode);
            throw new ProxyException(
                $"SOCKS5 CONNECT failed with reply 0x{replyCode:X2}: {desc}.",
                proxyStatusCode: replyCode);
        }

        byte bndAtyp = replyHead[3];
        int bndAddrLen = bndAtyp switch
        {
            0x01 => 4,
            0x04 => 16,
            0x03 => await ReadByteLengthAsync(stream, cancellationToken).ConfigureAwait(false),
            _ => throw new ProxyException($"SOCKS5 CONNECT reply contained invalid ATYP 0x{bndAtyp:X2}."),
        };

        var discardTail = new byte[bndAddrLen + 2];
        await ReadExactlyAsync(stream, discardTail, cancellationToken).ConfigureAwait(false);
    }

    private static void EncodeIpAddress(IPAddress ip, out byte atyp, out byte[] addrBytes)
    {
        IPAddress normalized = ip.IsIPv4MappedToIPv6 ? ip.MapToIPv4() : ip;
        if (normalized.AddressFamily == AddressFamily.InterNetwork)
        {
            atyp = 0x01;
            addrBytes = normalized.GetAddressBytes();
        }
        else if (normalized.AddressFamily == AddressFamily.InterNetworkV6)
        {
            atyp = 0x04;
            addrBytes = normalized.GetAddressBytes();
        }
        else
        {
            throw new ProxyException($"Unsupported IP address family {ip.AddressFamily} for SOCKS5.");
        }
    }

    private static async Task<int> ReadByteLengthAsync(Stream stream, CancellationToken cancellationToken)
    {
        var lenBuf = new byte[1];
        await ReadExactlyAsync(stream, lenBuf, cancellationToken).ConfigureAwait(false);
        return lenBuf[0];
    }

    private static async Task ReadExactlyAsync(Stream stream, byte[] buffer, CancellationToken cancellationToken)
    {
        int offset = 0;
        while (offset < buffer.Length)
        {
            int read = await stream.ReadAsync(buffer.AsMemory(offset, buffer.Length - offset), cancellationToken).ConfigureAwait(false);
            if (read == 0)
                throw new EndOfStreamException("SOCKS5 proxy closed connection unexpectedly.");
            offset += read;
        }
    }

    public static string DescribeReplyCode(byte replyCode) => replyCode switch
    {
        0x00 => "succeeded",
        0x01 => "general SOCKS server failure",
        0x02 => "connection not allowed by ruleset",
        0x03 => "Network unreachable",
        0x04 => "Host unreachable",
        0x05 => "Connection refused",
        0x06 => "TTL expired",
        0x07 => "Command not supported",
        0x08 => "Address type not supported",
        _ => $"unassigned reply code 0x{replyCode:X2}",
    };
}

/// <summary>
/// Unified transport dialer dispatching across direct RFC 8305 TCP, HTTP/HTTPS CONNECT proxy,
/// and SOCKS5/SOCKS5h proxy connections.
/// </summary>
public sealed class ConnectionDialer
{
    private readonly DnsCache _dnsCache;
    private readonly DirectDialer _directDialer;
    private readonly HttpConnectDialer _httpConnectDialer;
    private readonly Socks5Dialer _socks5Dialer;

    public ConnectionDialer(
        DnsCache? dnsCache = null,
        TimeSpan? connectTimeout = null,
        TimeSpan? happyEyeballsDelay = null)
    {
        _dnsCache = dnsCache ?? new DnsCache();
        _directDialer = new DirectDialer(_dnsCache, connectTimeout, happyEyeballsDelay);
        _httpConnectDialer = new HttpConnectDialer(_directDialer);
        _socks5Dialer = new Socks5Dialer(_directDialer, _dnsCache);
    }

    public DnsCache DnsCache => _dnsCache;
    public DirectDialer DirectDialer => _directDialer;
    public HttpConnectDialer HttpConnectDialer => _httpConnectDialer;
    public Socks5Dialer Socks5Dialer => _socks5Dialer;

    public Task<DialedConnection> DialAsync(
        string host,
        int port,
        ProxySpec? proxy = null,
        CertificateVerifyOptions? proxyTlsVerifyOptions = null,
        TimeSpan? connectTimeout = null,
        CancellationToken cancellationToken = default)
    {
        if (proxy is null || proxy.Kind == ProxyProtocolKind.None)
        {
            return _directDialer.DialAsync(
                host,
                port,
                localAddress: null,
                timeoutOverride: connectTimeout,
                cancellationToken: cancellationToken);
        }

        return proxy.Kind switch
        {
            ProxyProtocolKind.Http or ProxyProtocolKind.Https => _httpConnectDialer.DialAsync(
                proxy,
                host,
                port,
                proxyTlsVerifyOptions,
                extraProxyHeaders: null,
                connectTimeout: connectTimeout,
                cancellationToken: cancellationToken),
            ProxyProtocolKind.Socks5 => _socks5Dialer.DialAsync(
                proxy,
                host,
                port,
                connectTimeout: connectTimeout,
                cancellationToken: cancellationToken),
            _ => throw new ProxyException($"Unsupported proxy protocol kind: {proxy.Kind}."),
        };
    }
}
