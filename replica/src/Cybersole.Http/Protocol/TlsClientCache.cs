using System.Globalization;
using System.Net;
using System.Runtime.CompilerServices;
using Cybersole.Http.Profiles;
using Cybersole.Http.Tls;
using Cybersole.Http.X509;

namespace Cybersole.Http.Protocol;

/// <summary>
/// Options for <see cref="TlsHttpClient"/> matching <c>TlsHttpClientOptions</c> (<c>sub_1412897D0</c>) defaults:
/// <c>chrome_133</c>, 30s connect/request timeout, 90s idle timeout, 256 MiB max response body, 10 max redirects.
/// </summary>
public sealed record TlsHttpClientOptions
{
    public string ProfileName { get; init; } = ProfileRegistry.DefaultClientOptionsProfile;
    public TimeSpan ConnectTimeout { get; init; } = TimeSpan.FromSeconds(30);
    public TimeSpan RequestTimeout { get; init; } = TimeSpan.FromSeconds(30);
    public TimeSpan IdleTimeout { get; init; } = OriginPool.DefaultIdleTimeout;
    public long MaxResponseBodyBytes { get; init; } = 256L * 1024 * 1024;
    public int MaxRedirects { get; init; } = RedirectPolicy.DefaultMaxRedirects;
    public int MaxConnectionsPerOrigin { get; init; } = OriginPool.DefaultMaxConnectionsPerOrigin;
    public bool FollowRedirects { get; init; } = true;
    public bool AutomaticDecompression { get; init; } = true;
    public bool RandomExtensionOrder { get; init; }
    public bool DisableSessionTickets { get; init; }
    public bool ForceHttp11 { get; init; }
    public bool DisableHttp3 { get; init; }
    public bool InsecureSkipVerify { get; init; }
    public bool CloseConnection { get; init; }
    public bool UseCookieJar { get; init; } = true;
    public string? DefaultUserAgent { get; init; }
    public ProxySpec? Proxy { get; init; }
    public CertificateVerifyOptions? VerifyOptions { get; init; }
    public CertificatePinner? CertificatePinner { get; init; }
    public string? PinScope { get; init; }
    public TimeProvider? TimeProvider { get; init; }
    public Func<DateTimeOffset>? Clock { get; init; }
    public Action<string>? KeyLogSink { get; init; }
    public TimeSpan? RaceDelay { get; init; }
    public TimeSpan? Http3Cooldown { get; init; }
    public Func<ConnectionKey, ClientProfile, CancellationToken, Task<IMultiplexedConnection>>? CustomH3Connector { get; init; }
    public Func<ConnectionKey, ClientProfile, CancellationToken, Task<IMultiplexedConnection>>? CustomTcpTlsConnector { get; init; }
    public Func<string, CancellationToken, Task<IPAddress[]>>? DnsResolver { get; init; }
}

/// <summary>
/// Canonical cache partition key for <see cref="TlsClientCache"/>.
/// </summary>
public readonly record struct TlsClientCacheKey(
    string ProfileName,
    string ProxyKey,
    TimeSpan ConnectTimeout,
    TimeSpan IdleTimeout,
    long MaxResponseBodyBytes,
    int MaxRedirects,
    bool InsecureSkipVerify,
    bool ForceHttp11,
    bool DisableHttp3,
    bool DisableSessionTickets,
    bool RandomExtensionOrder,
    string PinScope)
{
    public static TlsClientCacheKey Create(TlsHttpClientOptions options)
    {
        ArgumentNullException.ThrowIfNull(options);

        string normalizedProfile = (options.ProfileName ?? ProfileRegistry.DefaultClientOptionsProfile)
            .Trim()
            .ToLowerInvariant();
        string proxyKey = options.Proxy?.CanonicalKey ?? "direct";
        string pinScope = ComputeEffectivePinScope(options);

        return new TlsClientCacheKey(
            normalizedProfile,
            proxyKey,
            options.ConnectTimeout,
            options.IdleTimeout,
            options.MaxResponseBodyBytes,
            options.MaxRedirects,
            options.InsecureSkipVerify || (options.VerifyOptions?.InsecureSkipVerify ?? false),
            options.ForceHttp11,
            options.DisableHttp3,
            options.DisableSessionTickets,
            options.RandomExtensionOrder,
            pinScope);
    }

    private static string ComputeEffectivePinScope(TlsHttpClientOptions options)
    {
        if (!string.IsNullOrEmpty(options.PinScope))
            return options.PinScope;

        CertificatePinner? pinner = options.CertificatePinner ?? options.VerifyOptions?.Pinner;
        RootCertificateDatabase? customRoots = options.VerifyOptions?.CustomRoots;
        bool useDefaultRoots = options.VerifyOptions?.UseEmbeddedDefaultRoots ?? true;

        if (pinner is null &&
            customRoots is null &&
            useDefaultRoots &&
            options.CustomH3Connector is null &&
            options.CustomTcpTlsConnector is null &&
            options.DnsResolver is null)
        {
            return string.Empty;
        }

        return string.Create(
            CultureInfo.InvariantCulture,
            $"p={GetId(pinner)}|r={GetId(customRoots)}|d={(useDefaultRoots ? 1 : 0)}|h3={GetId(options.CustomH3Connector)}|tcp={GetId(options.CustomTcpTlsConnector)}|dns={GetId(options.DnsResolver)}");
    }

    private static int GetId(object? obj) => obj is null ? 0 : RuntimeHelpers.GetHashCode(obj);
}

/// <summary>
/// Pure managed HTTP/3 + HTTP/2 + HTTP/1.1 client owning TLS session cache (<see cref="LruTlsSessionCache"/>),
/// <see cref="DnsCache"/>, <see cref="ProtocolRacer"/>, <see cref="OriginPool"/>, per-client <c>Alt-Svc</c> hints,
/// cookie jar, and RFC redirect semantics.
/// </summary>
public sealed class TlsHttpClient : IAsyncDisposable
{
    private const string DefaultChromeUserAgent =
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36";

    private readonly Func<DateTimeOffset> _clock;
    private readonly CertificateVerifyOptions? _effectiveVerifyOptions;
    private readonly CookieContainer? _cookieJar;
    private readonly string _pinScope;
    private int _disposed;

    public TlsHttpClient(TlsHttpClientOptions? options = null)
    {
        Options = options ?? new TlsHttpClientOptions();
        _clock = Options.Clock ?? (Options.TimeProvider is not null
            ? () => Options.TimeProvider.GetUtcNow()
            : () => DateTimeOffset.UtcNow);

        Profile = ResolveClientProfile(Options.ProfileName);
        SessionCache = Options.DisableSessionTickets
            ? null
            : new LruTlsSessionCache(LruTlsSessionCache.DefaultCapacity);

        DnsCache = new DnsCache(
            DnsCache.DefaultMaxCapacity,
            DnsCache.DefaultTtl,
            Options.DnsResolver);

        Dialer = new ConnectionDialer(DnsCache, Options.ConnectTimeout);
        _effectiveVerifyOptions = BuildVerifyOptions(Options);
        _pinScope = TlsClientCacheKey.Create(Options).PinScope;

        Racer = new ProtocolRacer(new ProtocolRacerOptions
        {
            RaceDelay = Options.RaceDelay ?? ProtocolRacer.DefaultRaceDelay,
            MaxRaceAttempts = ProtocolRacer.DefaultMaxRaceAttempts,
            Http3Cooldown = Options.Http3Cooldown ?? ProtocolRacer.DefaultHttp3Cooldown,
            ConnectTimeout = Options.ConnectTimeout,
            CloseConnection = Options.CloseConnection,
            Dialer = Dialer,
            Clock = _clock,
            KeyLogSink = Options.KeyLogSink,
            CustomH3Connector = Options.CustomH3Connector,
            CustomTcpTlsConnector = Options.CustomTcpTlsConnector,
        });

        Pool = new OriginPool(
            Racer,
            _ => Profile,
            Options.Proxy,
            _effectiveVerifyOptions,
            SessionCache,
            Options.IdleTimeout,
            Options.MaxConnectionsPerOrigin,
            _clock);

        if (Options.UseCookieJar)
            _cookieJar = new CookieContainer();
    }

    public TlsHttpClientOptions Options { get; }
    public ClientProfile Profile { get; }
    public LruTlsSessionCache? SessionCache { get; }
    public DnsCache DnsCache { get; }
    public ConnectionDialer Dialer { get; }
    public ProtocolRacer Racer { get; }
    public OriginPool Pool { get; }
    public CookieContainer? CookieJar => _cookieJar;
    public bool IsDisposed => Volatile.Read(ref _disposed) != 0;

    public bool HasAltSvcHttp3Hint(Uri uri)
    {
        ArgumentNullException.ThrowIfNull(uri);
        int port = GetEffectivePort(uri);
        return Racer.HasAltSvcHttp3Hint(uri.Host, port, Options.Proxy?.CanonicalKey);
    }

    public IReadOnlyDictionary<string, string> GetCookiesForUri(Uri uri)
    {
        ArgumentNullException.ThrowIfNull(uri);
        if (_cookieJar is null)
            return new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

        var result = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        lock (_cookieJar)
        {
            foreach (Cookie cookie in _cookieJar.GetCookies(uri))
                result[cookie.Name] = cookie.Value;
        }
        return result;
    }

    public Task<PureHttpResponse> SendAsync(PureHttpRequest request, CancellationToken cancellationToken = default)
        => SendCoreAsync(request, followRedirectsOverride: null, suppressDefaultUserAgent: false, cancellationToken);

    internal Task<PureHttpResponse> SendSingleHopForNetClientAsync(
        PureHttpRequest request,
        bool suppressDefaultUserAgent,
        CancellationToken cancellationToken = default)
        => SendCoreAsync(request, followRedirectsOverride: false, suppressDefaultUserAgent: suppressDefaultUserAgent, cancellationToken);

    private async Task<PureHttpResponse> SendCoreAsync(
        PureHttpRequest request,
        bool? followRedirectsOverride,
        bool suppressDefaultUserAgent,
        CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(request);
        ObjectDisposedException.ThrowIf(IsDisposed, this);
        ValidateRequest(request);

        bool followRedirects = followRedirectsOverride ?? Options.FollowRedirects;
        if (!followRedirects)
            return await SendSingleAttemptAsync(request, suppressDefaultUserAgent, cancellationToken).ConfigureAwait(false);

        PureHttpRequest current = request;
        int maxRedirects = Options.MaxRedirects;

        for (int hop = 0; ; hop++)
        {
            cancellationToken.ThrowIfCancellationRequested();

            PureHttpResponse response = await SendSingleAttemptAsync(current, suppressDefaultUserAgent, cancellationToken)
                .ConfigureAwait(false);

            if (!RedirectPolicy.IsRedirect(response.StatusCode))
                return response;

            string? location = response.GetFirstHeader("Location");
            if (string.IsNullOrEmpty(location) || maxRedirects <= 0)
                return response;

            if (hop >= maxRedirects)
            {
                throw new PureHttpException(
                    HttpErrorKind.TooManyRedirects,
                    $"TooManyRedirects: stopped after {maxRedirects} redirects");
            }

            string resolvedUrl = RedirectPolicy.Resolve(current.Uri.AbsoluteUri, location);
            var nextUri = new Uri(resolvedUrl, UriKind.Absolute);
            current = BuildRedirectRequest(current, response.StatusCode, nextUri);
        }
    }

    private async Task<PureHttpResponse> SendSingleAttemptAsync(
        PureHttpRequest request,
        bool suppressDefaultUserAgent,
        CancellationToken cancellationToken)
    {
        PureHttpRequest prepared = PrepareRequest(request, suppressDefaultUserAgent);
        int port = GetEffectivePort(prepared.Uri);
        bool insecure = Options.InsecureSkipVerify || (_effectiveVerifyOptions?.InsecureSkipVerify ?? false);
        bool forceHttp11 = Options.ForceHttp11 || prepared.ForceHttp11;

        var key = ConnectionKey.Create(
            scheme: prepared.Uri.Scheme,
            host: prepared.Uri.Host,
            port: port,
            profileName: Profile.Name,
            proxyKey: Options.Proxy?.CanonicalKey,
            forceHttp11: forceHttp11,
            disableHttp3: Options.DisableHttp3,
            insecureSkipVerify: insecure,
            disableSessionTickets: Options.DisableSessionTickets,
            randomExtensionOrder: Options.RandomExtensionOrder,
            pinScope: _pinScope);

        PureHttpResponse response = await Pool.SendWithRetryAsync(key, prepared, cancellationToken).ConfigureAwait(false);

        if (!string.IsNullOrWhiteSpace(response.AltSvcHeader))
            Racer.RecordAltSvc(key.Host, key.Port, response.AltSvcHeader, key.ProxyKey);

        if (_cookieJar is not null)
            RecordResponseCookies(_cookieJar, prepared.Uri, response);

        return response;
    }

    private PureHttpRequest PrepareRequest(PureHttpRequest request, bool suppressDefaultUserAgent)
    {
        bool hasUserAgent = false;
        bool hasExplicitCookie = false;

        for (int i = 0; i < request.Headers.Count; i++)
        {
            string name = request.Headers[i].Name;
            if (string.Equals(name, "User-Agent", StringComparison.OrdinalIgnoreCase))
                hasUserAgent = true;
            else if (string.Equals(name, "Cookie", StringComparison.OrdinalIgnoreCase))
                hasExplicitCookie = true;
        }

        string? jarCookieHeader = null;
        if (_cookieJar is not null && !hasExplicitCookie)
        {
            lock (_cookieJar)
            {
                CookieCollection cookies = _cookieJar.GetCookies(request.Uri);
                if (cookies.Count > 0)
                {
                    var parts = new string[cookies.Count];
                    for (int i = 0; i < cookies.Count; i++)
                        parts[i] = $"{cookies[i].Name}={cookies[i].Value}";
                    jarCookieHeader = string.Join("; ", parts);
                }
            }
        }

        IReadOnlyList<PureHttpHeader> headers = request.Headers;
        if ((!hasUserAgent && !suppressDefaultUserAgent) || jarCookieHeader is not null)
        {
            var updated = new List<PureHttpHeader>(request.Headers.Count + 2);
            updated.AddRange(request.Headers);
            if (!hasUserAgent && !suppressDefaultUserAgent)
            {
                string defaultUa = string.IsNullOrWhiteSpace(Options.DefaultUserAgent)
                    ? DefaultChromeUserAgent
                    : Options.DefaultUserAgent;
                updated.Add(new PureHttpHeader("User-Agent", defaultUa));
            }
            if (jarCookieHeader is not null)
                updated.Add(new PureHttpHeader("Cookie", jarCookieHeader));

            headers = updated;
        }

        TimeSpan? effectiveTimeout = request.RequestTimeout ?? Options.RequestTimeout;
        long effectiveMaxBytes = Options.MaxResponseBodyBytes > 0
            ? Math.Min(request.MaxResponseBodyBytes, Options.MaxResponseBodyBytes)
            : request.MaxResponseBodyBytes;

        return new PureHttpRequest
        {
            Method = request.Method,
            Uri = request.Uri,
            Headers = headers,
            Body = request.Body,
            ForceHttp11 = request.ForceHttp11 || Options.ForceHttp11,
            AllowAutoDecompression = Options.AutomaticDecompression && request.AllowAutoDecompression,
            MaxResponseBodyBytes = effectiveMaxBytes,
            RequestTimeout = effectiveTimeout,
            VerifyOptions = request.VerifyOptions ?? _effectiveVerifyOptions,
        };
    }

    private static PureHttpRequest BuildRedirectRequest(PureHttpRequest previous, int statusCode, Uri targetUri)
    {
        bool preservesMethod = statusCode is 307 or 308 ||
                               string.Equals(previous.Method, "GET", StringComparison.OrdinalIgnoreCase) ||
                               string.Equals(previous.Method, "HEAD", StringComparison.OrdinalIgnoreCase);

        string nextMethod = preservesMethod ? previous.Method : "GET";
        ReadOnlyMemory<byte> nextBody = statusCode is 307 or 308 ? previous.Body : ReadOnlyMemory<byte>.Empty;
        bool dropBodyHeaders = statusCode is not (307 or 308) &&
                               !string.Equals(previous.Method, "GET", StringComparison.OrdinalIgnoreCase) &&
                               !string.Equals(previous.Method, "HEAD", StringComparison.OrdinalIgnoreCase);

        bool sameOrigin = IsSameOrigin(previous.Uri, targetUri);
        var nextHeaders = new List<PureHttpHeader>(previous.Headers.Count);
        for (int i = 0; i < previous.Headers.Count; i++)
        {
            PureHttpHeader h = previous.Headers[i];
            if (dropBodyHeaders &&
                (string.Equals(h.Name, "Content-Type", StringComparison.OrdinalIgnoreCase) ||
                 string.Equals(h.Name, "Content-Encoding", StringComparison.OrdinalIgnoreCase) ||
                 string.Equals(h.Name, "Content-Length", StringComparison.OrdinalIgnoreCase)))
            {
                continue;
            }

            if (!sameOrigin &&
                (string.Equals(h.Name, "Authorization", StringComparison.OrdinalIgnoreCase) ||
                 string.Equals(h.Name, "Proxy-Authorization", StringComparison.OrdinalIgnoreCase) ||
                 string.Equals(h.Name, "www-authenticate", StringComparison.OrdinalIgnoreCase) ||
                 string.Equals(h.Name, "Cookie", StringComparison.OrdinalIgnoreCase) ||
                 string.Equals(h.Name, "Cookie2", StringComparison.OrdinalIgnoreCase)))
            {
                continue;
            }

            if (string.Equals(h.Name, "Host", StringComparison.OrdinalIgnoreCase))
                continue;

            nextHeaders.Add(h);
        }

        return new PureHttpRequest
        {
            Method = nextMethod,
            Uri = targetUri,
            Headers = nextHeaders,
            Body = nextBody,
            ForceHttp11 = previous.ForceHttp11,
            AllowAutoDecompression = previous.AllowAutoDecompression,
            MaxResponseBodyBytes = previous.MaxResponseBodyBytes,
            RequestTimeout = previous.RequestTimeout,
            VerifyOptions = previous.VerifyOptions,
        };
    }

    private static bool IsSameOrigin(Uri a, Uri b) =>
        string.Equals(a.Scheme, b.Scheme, StringComparison.OrdinalIgnoreCase) &&
        string.Equals(a.Host, b.Host, StringComparison.OrdinalIgnoreCase) &&
        GetEffectivePort(a) == GetEffectivePort(b);

    private static int GetEffectivePort(Uri uri)
    {
        if (uri.Port > 0)
            return uri.Port;
        return string.Equals(uri.Scheme, "https", StringComparison.OrdinalIgnoreCase) ? 443 : 80;
    }

    private static void ValidateRequest(PureHttpRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Method) || !IsValidHttpToken(request.Method.Trim()))
            throw new PureHttpException(HttpErrorKind.Protocol, $"net/http: invalid method \"{request.Method}\"");

        if (request.Uri is null || !request.Uri.IsAbsoluteUri || string.IsNullOrWhiteSpace(request.Uri.Host))
            throw new PureHttpException(HttpErrorKind.Protocol, "net/http: request URI must be an absolute HTTP/HTTPS URI");

        if (!string.Equals(request.Uri.Scheme, "http", StringComparison.OrdinalIgnoreCase) &&
            !string.Equals(request.Uri.Scheme, "https", StringComparison.OrdinalIgnoreCase))
        {
            throw new PureHttpException(HttpErrorKind.Protocol, $"net/http: unsupported URI scheme \"{request.Uri.Scheme}\"");
        }

        for (int i = 0; i < request.Headers.Count; i++)
        {
            PureHttpHeader hdr = request.Headers[i];
            if (string.IsNullOrWhiteSpace(hdr.Name) || !IsValidHttpToken(hdr.Name.Trim()))
                throw new PureHttpException(HttpErrorKind.Protocol, $"net/http: invalid header field name \"{hdr.Name}\"");

            if (hdr.Value is not null && hdr.Value.IndexOfAny(new[] { '\r', '\n', '\0' }) >= 0)
                throw new PureHttpException(HttpErrorKind.Protocol, $"net/http: invalid header field value for \"{hdr.Name}\"");
        }
    }

    private static bool IsValidHttpToken(string value)
    {
        for (int i = 0; i < value.Length; i++)
        {
            char c = value[i];
            if (c <= ' ' || c >= 0x7F || c is '(' or ')' or '<' or '>' or '@' or ',' or ';' or ':' or '\\' or '"' or '/' or '[' or ']' or '?' or '=' or '{' or '}')
                return false;
        }
        return value.Length > 0;
    }

    private static void RecordResponseCookies(CookieContainer jar, Uri requestUri, PureHttpResponse response)
    {
        foreach (string raw in response.GetHeaderValues("Set-Cookie"))
        {
            if (string.IsNullOrWhiteSpace(raw))
                continue;

            lock (jar)
            {
                try
                {
                    jar.SetCookies(requestUri, raw);
                }
                catch (CookieException)
                {
                    string pair = raw.Split(';', 2)[0];
                    int eq = pair.IndexOf('=');
                    if (eq > 0)
                    {
                        try
                        {
                            jar.Add(requestUri, new Cookie(pair[..eq].Trim(), pair[(eq + 1)..].Trim()));
                        }
                        catch (CookieException)
                        {
                            // Ignore malformed cookie names/values.
                        }
                    }
                }
            }
        }
    }

    private static CertificateVerifyOptions? BuildVerifyOptions(TlsHttpClientOptions options)
    {
        CertificateVerifyOptions? src = options.VerifyOptions;
        CertificatePinner? pinner = options.CertificatePinner ?? src?.Pinner;
        bool insecure = options.InsecureSkipVerify || (src?.InsecureSkipVerify ?? false);

        if (src is null && !insecure && pinner is null)
            return null;

        if (src is null)
        {
            return new CertificateVerifyOptions
            {
                InsecureSkipVerify = insecure,
                Pinner = pinner,
            };
        }

        return new CertificateVerifyOptions
        {
            InsecureSkipVerify = insecure,
            VerificationTime = src.VerificationTime,
            CustomRoots = src.CustomRoots,
            UseEmbeddedDefaultRoots = src.UseEmbeddedDefaultRoots,
            Pinner = pinner,
            MaxChainLength = src.MaxChainLength,
            MaxSignatureChecks = src.MaxSignatureChecks,
            AllowSha1 = src.AllowSha1,
        };
    }

    internal static ClientProfile ResolveClientProfile(string? name)
    {
        if (string.IsNullOrWhiteSpace(name))
            return ProfileRegistry.GetOrDefault(ProfileRegistry.DefaultClientOptionsProfile);

        string trimmed = name.Trim();
        if (ProfileRegistry.TryGet(trimmed, out ClientProfile? exact) && exact is not null)
            return exact;

        for (int i = 0; i < ProfileRegistry.RegisteredKeys.Count; i++)
        {
            string key = ProfileRegistry.RegisteredKeys[i];
            if (string.Equals(key, trimmed, StringComparison.OrdinalIgnoreCase) &&
                ProfileRegistry.TryGet(key, out ClientProfile? ciMatch) &&
                ciMatch is not null)
            {
                return ciMatch;
            }
        }

        if (string.Equals(trimmed, "chrome", StringComparison.OrdinalIgnoreCase))
            return ProfileRegistry.GetOrDefault(ProfileRegistry.DefaultFingerprint);
        if (string.Equals(trimmed, "firefox", StringComparison.OrdinalIgnoreCase))
            return ProfileRegistry.GetOrDefault("firefox_135");
        if (string.Equals(trimmed, "safari", StringComparison.OrdinalIgnoreCase))
            return ProfileRegistry.GetOrDefault("safari_16_0");

        return ProfileRegistry.GetOrDefault(ProfileRegistry.DefaultClientOptionsProfile);
    }

    public async ValueTask DisposeAsync()
    {
        if (Interlocked.Exchange(ref _disposed, 1) != 0)
            return;

        await Pool.DisposeAsync().ConfigureAwait(false);
        SessionCache?.Clear();
    }
}

/// <summary>
/// Thread-safe LRU + idle-TTL cache of <see cref="TlsHttpClient"/> instances matching
/// <c>TlsClientCache</c> (<c>0x1412878A0</c>, <c>0x141287A20</c>, <c>0x141287D80</c>):
/// capacity <c>4096</c>, idle eviction <c>600s</c> (10 min), and lock-free async disposal.
/// </summary>
public sealed class TlsClientCache : IAsyncDisposable
{
    public const int DefaultMaxCapacity = 4096;
    public static readonly TimeSpan DefaultIdleEvictionTimeout = TimeSpan.FromSeconds(600);
    private static readonly TimeSpan BackgroundSweepPeriod = TimeSpan.FromSeconds(30);

    private sealed class CacheEntry
    {
        public CacheEntry(TlsClientCacheKey key, TlsHttpClient client, DateTimeOffset lastUsedUtc)
        {
            Key = key;
            Client = client;
            LastUsedUtc = lastUsedUtc;
        }

        public TlsClientCacheKey Key { get; }
        public TlsHttpClient Client { get; }
        public DateTimeOffset LastUsedUtc { get; set; }
    }

    private readonly int _maxCapacity;
    private readonly TimeSpan _idleEvictionTimeout;
    private readonly Func<DateTimeOffset> _clock;
    private readonly object _gate = new();
    private readonly Dictionary<TlsClientCacheKey, LinkedListNode<CacheEntry>> _map;
    private readonly LinkedList<CacheEntry> _lru = new();
    private Timer? _sweepTimer;
    private bool _disposed;

    public TlsClientCache(
        int maxCapacity = DefaultMaxCapacity,
        TimeSpan? idleEvictionTimeout = null,
        Func<DateTimeOffset>? clock = null,
        TimeProvider? timeProvider = null)
    {
        if (maxCapacity < 1)
            throw new ArgumentOutOfRangeException(nameof(maxCapacity), "TlsClientCache MaxCapacity must be >= 1.");

        TimeSpan effectiveIdle = idleEvictionTimeout ?? DefaultIdleEvictionTimeout;
        if (effectiveIdle < TimeSpan.Zero)
            throw new ArgumentOutOfRangeException(nameof(idleEvictionTimeout), "IdleEvictionTimeout cannot be negative.");

        _maxCapacity = maxCapacity;
        _idleEvictionTimeout = effectiveIdle;
        _clock = clock ?? (timeProvider is not null
            ? () => timeProvider.GetUtcNow()
            : () => DateTimeOffset.UtcNow);
        _map = new Dictionary<TlsClientCacheKey, LinkedListNode<CacheEntry>>(Math.Min(maxCapacity, 64));
    }

    public int MaxCapacity => _maxCapacity;
    public TimeSpan IdleEvictionTimeout => _idleEvictionTimeout;

    public int Count
    {
        get
        {
            lock (_gate)
                return _map.Count;
        }
    }

    public TlsHttpClient GetOrCreate(TlsHttpClientOptions? options = null)
    {
        TlsHttpClientOptions effectiveOptions = options ?? new TlsHttpClientOptions();
        TlsClientCacheKey key = TlsClientCacheKey.Create(effectiveOptions);

        TlsHttpClient result;
        List<TlsHttpClient>? evicted = null;

        lock (_gate)
        {
            ObjectDisposedException.ThrowIf(_disposed, this);

            DateTimeOffset now = _clock();
            PruneIdleLocked(now, ref evicted);

            if (_map.TryGetValue(key, out LinkedListNode<CacheEntry>? existing))
            {
                if (!existing.Value.Client.IsDisposed)
                {
                    existing.Value.LastUsedUtc = now;
                    _lru.Remove(existing);
                    _lru.AddFirst(existing);
                    result = existing.Value.Client;
                    goto DisposeEvicted;
                }

                _lru.Remove(existing);
                _map.Remove(key);
            }

            while (_map.Count >= _maxCapacity && _lru.Last is { } victim)
            {
                _lru.RemoveLast();
                _map.Remove(victim.Value.Key);
                evicted ??= new List<TlsHttpClient>();
                evicted.Add(victim.Value.Client);
            }

            TlsHttpClientOptions boundOptions = effectiveOptions.Clock is null && effectiveOptions.TimeProvider is null
                ? effectiveOptions with { Clock = _clock }
                : effectiveOptions;

            var client = new TlsHttpClient(boundOptions);
            var node = new LinkedListNode<CacheEntry>(new CacheEntry(key, client, now));
            _lru.AddFirst(node);
            _map[key] = node;
            EnsureSweepTimerStartedLocked();
            result = client;
        }

    DisposeEvicted:
        if (evicted is not null)
        {
            for (int i = 0; i < evicted.Count; i++)
                _ = DisposeClientSafeAsync(evicted[i]);
        }

        return result;
    }

    public async ValueTask<int> EvictIdleAsync()
    {
        List<TlsHttpClient>? evicted = null;
        lock (_gate)
        {
            if (_disposed)
                return 0;

            PruneIdleLocked(_clock(), ref evicted);
        }

        if (evicted is null || evicted.Count == 0)
            return 0;

        for (int i = 0; i < evicted.Count; i++)
            await DisposeClientSafeAsync(evicted[i]).ConfigureAwait(false);

        return evicted.Count;
    }

    private void PruneIdleLocked(DateTimeOffset now, ref List<TlsHttpClient>? evicted)
    {
        LinkedListNode<CacheEntry>? cur = _lru.Last;
        while (cur is not null)
        {
            LinkedListNode<CacheEntry>? prev = cur.Previous;
            if (cur.Value.Client.IsDisposed || now - cur.Value.LastUsedUtc >= _idleEvictionTimeout)
            {
                _lru.Remove(cur);
                _map.Remove(cur.Value.Key);
                evicted ??= new List<TlsHttpClient>();
                evicted.Add(cur.Value.Client);
            }
            cur = prev;
        }
    }

    private void EnsureSweepTimerStartedLocked()
    {
        if (_disposed || _sweepTimer is not null || _idleEvictionTimeout <= TimeSpan.Zero)
            return;

        _sweepTimer = new Timer(
            static state => ((TlsClientCache)state!).OnSweepTick(),
            this,
            BackgroundSweepPeriod,
            BackgroundSweepPeriod);
    }

    private void OnSweepTick()
    {
        if (_disposed)
            return;

        _ = EvictIdleSafeAsync();
    }

    private async Task EvictIdleSafeAsync()
    {
        try
        {
            await EvictIdleAsync().ConfigureAwait(false);
        }
        catch
        {
            // Never allow background sweep exceptions to crash timer thread.
        }
    }

    private static async Task DisposeClientSafeAsync(TlsHttpClient client)
    {
        try
        {
            await client.DisposeAsync().ConfigureAwait(false);
        }
        catch
        {
            // Ignore disposal errors on evicted clients.
        }
    }

    public async ValueTask DisposeAsync()
    {
        List<TlsHttpClient>? allClients = null;
        Timer? timer;

        lock (_gate)
        {
            if (_disposed)
                return;
            _disposed = true;

            timer = _sweepTimer;
            _sweepTimer = null;

            if (_map.Count > 0)
            {
                allClients = new List<TlsHttpClient>(_map.Count);
                foreach (LinkedListNode<CacheEntry> node in _map.Values)
                    allClients.Add(node.Value.Client);
                _map.Clear();
            }

            _lru.Clear();
        }

        timer?.Dispose();

        if (allClients is not null)
        {
            for (int i = 0; i < allClients.Count; i++)
                await DisposeClientSafeAsync(allClients[i]).ConfigureAwait(false);
        }
    }
}
