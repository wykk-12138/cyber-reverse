using System.Diagnostics;
using System.Globalization;
using System.Net;
using System.Net.Security;
using System.Security.Authentication;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using Cybersole.Core.Store;

namespace Cybersole.Http;

/// <summary>
/// NetClient — the HTTP engine used by store modules.
/// Holds one <see cref="HttpClient"/> per TLS profile so the negotiated ClientHello
/// (cipher-suite list, ALPN, SNI) matches the advertised fingerprint,
/// and reports every request through <see cref="HttpAnalytics"/> / <see cref="HttpDebug"/>.
/// </summary>
public sealed class NetClient : IDisposable
{
    private readonly Tls12Pool _tlsPool = new();

    private readonly object _poolGate = new();
    private readonly Dictionary<string, HttpClient> _clients = new(StringComparer.OrdinalIgnoreCase);
    private readonly HttpAnalytics _analytics;
    /// <summary>Default dial/connect timeout matching <c>sub_1412897D0</c> (+160, 30s).</summary>
    public static readonly TimeSpan DefaultConnectTimeout = TimeSpan.FromSeconds(30);

    /// <summary>Default idle pooled connection timeout matching <c>sub_1412897D0</c> (+152, 90s).</summary>
    public static readonly TimeSpan DefaultPooledConnectionIdleTimeout = TimeSpan.FromSeconds(90);

    private readonly TimeSpan _connectTimeout;
    private bool _disposed;

    public NetClient(HttpAnalytics? analytics = null, TimeSpan? timeout = null)
    {
        _analytics = analytics ?? new HttpAnalytics();
        _connectTimeout = timeout ?? DefaultConnectTimeout;
    }

    public TimeSpan ConnectTimeout => _connectTimeout;

    public HttpAnalytics Analytics => _analytics;

    /// <summary>
    /// Transport selection. <see cref="TransportMode.SChannel"/> (<see cref="SocketsHttpHandler"/>) is the default and
    /// the production path matching the original binary's HTTP stack. <see cref="TransportMode.OwnTls"/> is an
    /// experimental hand-written TLS 1.2 probe path kept strictly for fingerprint diagnostics — it is NOT a
    /// production path, offers TLS 1.2 only, and performs an automatic one-shot fallback to
    /// <see cref="TransportMode.SChannel"/> on handshake/transport failure.
    /// </summary>
    public TransportMode Transport { get; set; } = TransportMode.SChannel;

    /// <summary>True when <see cref="Transport"/> is on the production SChannel/SocketsHttpHandler path.</summary>
    public bool IsProductionTransport => Transport == TransportMode.SChannel;

    /// <summary>True when <see cref="Transport"/> is opted into a non-production experimental probe stack.</summary>
    public bool IsExperimentalTransport => Transport != TransportMode.SChannel;

    private bool _fellBackFromOwnTls;
    private int _ownTlsFallbackCount;
    private string? _lastOwnTlsError;

    /// <summary>
    /// How many times a request had to abandon <see cref="TransportMode.OwnTls"/> and finish
    /// on the system stack. Non-zero means the hand-written TLS path could not negotiate with
    /// that host. Exposed so tests and diagnostics can see the defect instead of guessing.
    /// </summary>
    public int OwnTlsFallbackCount => Volatile.Read(ref _ownTlsFallbackCount);

    /// <summary>True when the last request silently changed transport.</summary>
    public bool FellBackFromOwnTls => _fellBackFromOwnTls;

    /// <summary>Why OwnTls was abandoned, or null when it was never tried.</summary>
    public string? LastOwnTlsError => _lastOwnTlsError;

    /// <summary>Reset the fallback bookkeeping (one-shot flag plus the counter).</summary>
    public void ResetOwnTlsFallback()
    {
        _fellBackFromOwnTls = false;
        _lastOwnTlsError = null;
        Volatile.Write(ref _ownTlsFallbackCount, 0);
    }

    /// <summary>Active per-profile clients (diagnostics / tests).</summary>
    public IReadOnlyCollection<string> ActiveProfiles
    {
        get
        {
            lock (_poolGate) return _clients.Keys.ToArray();
        }
    }

    private HttpClient ClientFor(TlsProfile profile)
    {
        lock (_poolGate)
        {
            if (_clients.TryGetValue(profile.Name, out var existing)) return existing;

            // Matches sub_1412897D0 pool/redirect defaults (MaxAutomaticRedirections=10, dial=30s, idle=90s,
            // gzip/deflate/br decompression, cookies=true). BCL SocketsHttpHandler.Http3Support is explicitly
            // disabled in the original image (AppContext 0x144b19bd0 = "false"; zero System.Net.Quic/msquic).
            var handler = new SocketsHttpHandler
            {
                AutomaticDecompression = DecompressionMethods.All,
                AllowAutoRedirect = true,
                MaxAutomaticRedirections = 10,
                ConnectTimeout = _connectTimeout,
                PooledConnectionLifetime = TimeSpan.FromMinutes(5),
                PooledConnectionIdleTimeout = DefaultPooledConnectionIdleTimeout,
                UseCookies = true,
                CookieContainer = new CookieContainer(),
                SslOptions =
                {
                    EnabledSslProtocols = SslProtocols.Tls12 | SslProtocols.Tls13,
                    ApplicationProtocols = profile.BuildAlpn(),
                    CipherSuitesPolicy = profile.BuildCipherPolicy(),
                    CertificateRevocationCheckMode = X509RevocationMode.NoCheck,
                    TargetHost = string.Empty, // per-request SNI
                },
            };

            var client = new HttpClient(handler) { Timeout = Timeout.InfiniteTimeSpan };
            client.DefaultRequestHeaders.ConnectionClose = false;
            _clients[profile.Name] = client;
            return client;
        }
    }

    public Task<NetResponse> SendAsync(
        HttpMethod method,
        string url,
        RequestOptions? options = null,
        CancellationToken ct = default) => SendAsync(method, url, options, 0, ct);

    /// <summary>
    /// The hop counter is a separate overload rather than an optional parameter on the public method, so a caller cannot
    /// start a chain half way through by passing a number -- only this class counts redirects.
    /// </summary>
    private async Task<NetResponse> SendAsync(
        HttpMethod method,
        string url,
        RequestOptions? options,
        int hops,
        CancellationToken ct)
    {
        options ??= new RequestOptions();

        if (Transport != TransportMode.SChannel)
        {
            var bodyText = options.Content is null
                ? null
                : await options.Content.ReadAsStringAsync(ct).ConfigureAwait(false);
            var proxy = string.IsNullOrWhiteSpace(options.Proxy) ? null : Cybersole.Core.Models.Proxy.Parse(options.Proxy);
            var headerCopy = options.Headers.ToDictionary(kv => kv.Key, kv => kv.Value, StringComparer.OrdinalIgnoreCase);

            if (Transport == TransportMode.OwnTls)
            {
                var ownUri = new Uri(url, UriKind.Absolute);
                try
                {
                    // Rent from the pool instead of handshaking every time: a checkout run
                    // makes a dozen requests to the same host, and the p95 gap against
                    // SChannel was entirely handshake cost.
                    var ownPort = ownUri.Port == 0 ? 443 : ownUri.Port;
                    var own = await _tlsPool.RentAsync(ownUri.Host, ownPort, options.Profile,
                        options.Timeout, ct).ConfigureAwait(false);

                    var path = string.IsNullOrEmpty(ownUri.PathAndQuery) ? "/" : ownUri.PathAndQuery;

                    NetResponse result;
                    try
                    {
                        result = await own.SendAsync(method.Method.ToUpperInvariant(), path,
                            ownUri.Host, bodyText, ct).ConfigureAwait(false);
                    }
                    catch (Exception)
                    {
                        // a session that saw an error has untrustworthy record sequence numbers
                        _tlsPool.Discard(own);
                        throw;
                    }

                    _tlsPool.Return(ownUri.Host, ownPort, options.Profile, own);

                    result.Headers["X-Cyb-Transport"] = "own-tls12";
                    result.Headers["X-Cyb-Alpn"] = own.Alpn ?? "-";
                    return result;
                }
                catch (Exception ex) when (!ct.IsCancellationRequested)
                {
                    // Some hosts reject this experimental TLS 1.2 stack outright (`bad_record_mac`).
                    // Never leave the client stuck on OwnTls: record the fallback and switch one-shot to SChannel.
                    _fellBackFromOwnTls = true;
                    Interlocked.Increment(ref _ownTlsFallbackCount);
                    Transport = TransportMode.SChannel;
                    _lastOwnTlsError = ex.Message;

                    // fall through to the standard SChannel path below
                }
            }

            if (Transport == TransportMode.BouncyH2)
            {
                using var h2 = new BouncyH2Client(_analytics);
                return await h2.SendAsync(method.Method, url, options.Profile, proxy,
                    headerCopy, bodyText, options.Timeout, options.Tag, ct).ConfigureAwait(false);
            }

            if (method == HttpMethod.Get)
            {
                using var h11 = new BouncyHttpClient(_analytics);
                return await h11.GetAsync(url, options.Profile, true, proxy, options.Timeout, options.Tag, ct)
                    .ConfigureAwait(false);
            }

            throw new NetException($"BouncyHttp11 transport supports GET only (got {method})");
        }

        var sw = Stopwatch.StartNew();
        Exception? last = null;

        for (var attempt = 0; attempt <= options.Retries; attempt++)
        {
            using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
            cts.CancelAfter(options.Timeout);
            try
            {
                using var request = BuildRequest(method, url, options);
                var client = ClientFor(options.Profile);
                using var response = await client.SendAsync(
                    request, HttpCompletionOption.ResponseContentRead, cts.Token).ConfigureAwait(false);

                var body = await ReadBodyAsync(response, cts.Token).ConfigureAwait(false);
                sw.Stop();

                var result = new NetResponse
                {
                    StatusCode = (int)response.StatusCode,
                    Body = body,
                    Url = response.RequestMessage?.RequestUri ?? new Uri(url),
                    Headers = response.Headers
                        .Concat(response.Content.Headers)
                        .GroupBy(h => h.Key, StringComparer.OrdinalIgnoreCase)
                        .ToDictionary(g => g.Key, g => string.Join(", ", g.SelectMany(v => v.Value)), StringComparer.OrdinalIgnoreCase),
                    Cookies = ExtractCookies(response),
                    Elapsed = sw.Elapsed,
                    Bytes = body.Length,
                    Protocol = response.Version.Major >= 2 ? "h2" : "http/1.1",
                };

                // R951: the redirect branch is here rather than in each transport, so all three share one policy.
                // A chain that exceeds the limit throws rather than returning the last hop, because a truncated chain
                // looks like an answer.
                // R952: the recursion is replaced by RedirectPolicy.FollowAsync so the chain walks through one async
                // method rather than through this one calling itself. Two reasons, and the second is the one that
                // matters for parity: an async method keeps its state machine in the image where a small synchronous
                // helper would be inlined and leave no .pdata entry at all.
                if (options.FollowRedirects && RedirectPolicy.IsRedirect(result.StatusCode) &&
                    result.Headers.TryGetValue("Location", out var location) &&
                    !string.IsNullOrEmpty(location))
                {
                    var limit = RedirectPolicy.LimitFrom(options.MaxRedirects);
                    var carried = options;
                    var followMethod = method;

                    var followed = await RedirectPolicy.FollowAsync(
                        url,
                        async (current, token) =>
                        {
                            if (string.Equals(current, url, StringComparison.Ordinal))
                                return new RedirectHop(result.StatusCode, location);

                            // every subsequent hop is a real request, so the chain is walked rather than replayed
                            var nextOptions = carried;
                            if (!RedirectPolicy.PreservesMethod(result.StatusCode, followMethod.Method))
                            {
                                nextOptions = carried.Clone();
                                nextOptions.Content = null;
                                followMethod = HttpMethod.Get;
                            }

                            var hopResponse = await SendAsync(followMethod, current, nextOptions, limit + 1, token)
                                .ConfigureAwait(false);
                            return new RedirectHop(hopResponse.StatusCode,
                                hopResponse.Headers.TryGetValue("Location", out var next) ? next : null);
                        },
                        limit,
                        ct).ConfigureAwait(false);

                    if (followed.TooMany)
                        throw new NetException(followed.TooManyMessage());

                    if (!string.Equals(followed.FinalUrl, url, StringComparison.Ordinal))
                        return await SendAsync(followMethod, followed.FinalUrl, carried, limit + 1, ct)
                            .ConfigureAwait(false);
                }

                _analytics.Record(new HttpRequestEvent
                {
                    Url = result.Url.ToString(),
                    Status = result.StatusCode,
                    ElapsedMs = (int)sw.Elapsed.TotalMilliseconds,
                    Bytes = result.Bytes,
                    Protocol = result.Protocol,
                    Profile = options.Profile.Name,
                    Proxy = options.Proxy,
                    Tag = options.Tag,
                    Method = method.Method,
                });

                return result;
            }
            catch (OperationCanceledException) when (!ct.IsCancellationRequested)
            {
                last = new NetException($"timeout after {options.Timeout.TotalSeconds:0}s: {url}");
            }
            catch (Exception ex)
            {
                last = ex;
            }

            _analytics.RecordFailure(url, options.Proxy, last?.Message ?? "unknown");
            if (attempt < options.Retries)
                await Task.Delay(250 * (attempt + 1), ct).ConfigureAwait(false);
        }

        throw last as NetException ?? new NetException($"request failed: {url}", null, last);
    }

    public Task<NetResponse> GetAsync(string url, RequestOptions? options = null, CancellationToken ct = default)
        => SendAsync(HttpMethod.Get, url, options, ct);

    public Task<NetResponse> PostJsonAsync(string url, string json, RequestOptions? options = null,
        CancellationToken ct = default)
    {
        options ??= new RequestOptions();
        options.Content = new StringContent(json, Encoding.UTF8, "application/json");
        options.Headers.TryAdd("Accept", "application/json");
        return SendAsync(HttpMethod.Post, url, options, ct);
    }

    public Task<NetResponse> PostFormAsync(string url, IDictionary<string, string> form,
        RequestOptions? options = null, CancellationToken ct = default)
    {
        options ??= new RequestOptions();
        options.Content = new FormUrlEncodedContent(form);
        return SendAsync(HttpMethod.Post, url, options, ct);
    }

    private HttpRequestMessage BuildRequest(HttpMethod method, string url, RequestOptions options)
    {
        var request = new HttpRequestMessage(method, url);

        // ---- browser-like default headers (fingerprint parity) ----
        var p = options.Profile;
        request.Headers.TryAddWithoutValidation("User-Agent", p.UserAgent);
        request.Headers.TryAddWithoutValidation("Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8");
        request.Headers.TryAddWithoutValidation("Accept-Language", p.AcceptLanguage);
        request.Headers.TryAddWithoutValidation("sec-ch-ua", p.SecChUa);
        request.Headers.TryAddWithoutValidation("sec-ch-ua-mobile", p.SecChUaMobile);
        request.Headers.TryAddWithoutValidation("sec-ch-ua-platform", p.SecChUaPlatform);
        request.Headers.TryAddWithoutValidation("sec-fetch-dest", "document");
        request.Headers.TryAddWithoutValidation("sec-fetch-mode", "navigate");
        request.Headers.TryAddWithoutValidation("sec-fetch-site", "none");
        request.Headers.TryAddWithoutValidation("sec-fetch-user", "?1");
        request.Headers.TryAddWithoutValidation("upgrade-insecure-requests", "1");

        foreach (var (k, v) in options.Headers)
            request.Headers.TryAddWithoutValidation(k, v);

        if (options.Content is not null)
            request.Content = options.Content;

        return request;
    }

    private static Dictionary<string, string> ExtractCookies(HttpResponseMessage response)
    {
        if (!response.Headers.TryGetValues("Set-Cookie", out var values))
            return new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        var cookies = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        foreach (var raw in values)
        {
            var pair = raw.Split(';', 2)[0];
            var idx = pair.IndexOf('=');
            if (idx > 0) cookies[pair[..idx].Trim()] = pair[(idx + 1)..].Trim();
        }
        return cookies;
    }

    private static async Task<string> ReadBodyAsync(HttpResponseMessage response, CancellationToken ct)
    {
        await using var stream = await response.Content.ReadAsStreamAsync(ct).ConfigureAwait(false);
        using var reader = new StreamReader(stream, Encoding.UTF8, detectEncodingFromByteOrderMarks: true);
        return await reader.ReadToEndAsync(ct).ConfigureAwait(false);
    }

    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;
        lock (_poolGate)
        {
            foreach (var c in _clients.Values) c.Dispose();
            _clients.Clear();
        }
    }
}
