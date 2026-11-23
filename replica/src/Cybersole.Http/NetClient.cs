using System.Buffers;
using System.Diagnostics;
using System.Net;
using System.Net.Http.Headers;
using System.Net.Security;
using System.Security.Authentication;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using Cybersole.Core.Store;
using Cybersole.Http.Compression;
using Cybersole.Http.Content;
using Newtonsoft.Json.Linq;

namespace Cybersole.Http;

/// <summary>
/// NetClient — the HTTP engine used by store modules.
/// Holds pooled <see cref="HttpClient"/> instances keyed by <c>(profile, proxy)</c> so negotiated
/// ClientHello settings and proxy tunnels match the advertised options, and reports requests through
/// <see cref="HttpAnalytics"/> / <see cref="HttpDebug"/>.
/// </summary>
public sealed class NetClient : IDisposable
{
    private readonly record struct ClientPoolKey(string ProfileName, string ProxyKey);

    private sealed class ClientPoolKeyComparer : IEqualityComparer<ClientPoolKey>
    {
        public static readonly ClientPoolKeyComparer Instance = new();

        public bool Equals(ClientPoolKey x, ClientPoolKey y) =>
            string.Equals(x.ProfileName, y.ProfileName, StringComparison.OrdinalIgnoreCase) &&
            string.Equals(x.ProxyKey, y.ProxyKey, StringComparison.Ordinal);

        public int GetHashCode(ClientPoolKey obj) =>
            HashCode.Combine(
                StringComparer.OrdinalIgnoreCase.GetHashCode(obj.ProfileName),
                StringComparer.Ordinal.GetHashCode(obj.ProxyKey));
    }

    private readonly Tls12Pool _tlsPool = new();

    private readonly object _poolGate = new();
    private readonly Dictionary<ClientPoolKey, HttpClient> _clients = new(ClientPoolKeyComparer.Instance);
    private readonly Dictionary<string, CookieContainer> _cookieContainers = new(StringComparer.OrdinalIgnoreCase);
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

    /// <summary>Active distinct TLS profile names in the pool (diagnostics / tests).</summary>
    public IReadOnlyCollection<string> ActiveProfiles
    {
        get
        {
            lock (_poolGate)
                return _clients.Keys.Select(k => k.ProfileName).Distinct(StringComparer.OrdinalIgnoreCase).ToArray();
        }
    }

    private static (string ProxyKey, WebProxy? WebProxy) BuildWebProxy(string? proxySpec)
    {
        if (string.IsNullOrWhiteSpace(proxySpec))
            return (string.Empty, null);

        var parsed = Cybersole.Core.Models.Proxy.Parse(proxySpec);
        var proxyUri = new Uri($"{parsed.Scheme}://{parsed.Host}:{parsed.Port}");
        var wp = new WebProxy(proxyUri) { BypassProxyOnLocal = false };
        if (!string.IsNullOrEmpty(parsed.Username))
            wp.Credentials = new NetworkCredential(parsed.Username, parsed.Password ?? string.Empty);

        return (parsed.Uri, wp);
    }

    private HttpClient ClientFor(TlsProfile profile, string? proxySpec, out CookieContainer cookieJar)
    {
        var (proxyKey, webProxy) = BuildWebProxy(proxySpec);
        var key = new ClientPoolKey(profile.Name, proxyKey);

        lock (_poolGate)
        {
            if (!_cookieContainers.TryGetValue(profile.Name, out cookieJar!))
            {
                cookieJar = new CookieContainer();
                _cookieContainers[profile.Name] = cookieJar;
            }

            if (_clients.TryGetValue(key, out var existing))
                return existing;

            // Matches sub_1412897D0 pool/redirect defaults (MaxAutomaticRedirections=10 in single-layer loop,
            // dial=30s, idle=90s, gzip/deflate/br decompression; BCL HTTP/3 disabled; AllowAutoRedirect=false
            // so NetClient's explicit redirect loop handles hop limits, method changes, /http strips, and cookies).
            var handler = new SocketsHttpHandler
            {
                AutomaticDecompression = DecompressionMethods.All,
                AllowAutoRedirect = false,
                MaxAutomaticRedirections = 10,
                ConnectTimeout = _connectTimeout,
                PooledConnectionLifetime = TimeSpan.FromMinutes(5),
                PooledConnectionIdleTimeout = DefaultPooledConnectionIdleTimeout,
                UseCookies = false,
                UseProxy = webProxy is not null,
                Proxy = webProxy,
                SslOptions =
                {
                    EnabledSslProtocols = SslProtocols.Tls12 | SslProtocols.Tls13,
                    ApplicationProtocols = profile.BuildAlpn(),
                    CipherSuitesPolicy = profile.BuildCipherPolicy(),
                    CertificateRevocationCheckMode = X509RevocationMode.NoCheck,
                    TargetHost = string.Empty,
                },
            };

            var client = new HttpClient(handler) { Timeout = Timeout.InfiniteTimeSpan };
            client.DefaultRequestHeaders.ConnectionClose = false;
            _clients[key] = client;
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
        var sw = Stopwatch.StartNew();

        var result = await SendSingleHopAsync(method, url, options, ct).ConfigureAwait(false);

        // Only the outer invocation (hops == 0) drives the single-layer redirect state machine.
        if (hops == 0 &&
            options.FollowRedirects && RedirectPolicy.IsRedirect(result.StatusCode) &&
            options.MaxRedirects is null or > 0 &&
            result.Headers.TryGetValue("Location", out var location) &&
            !string.IsNullOrEmpty(location))
        {
            var limit = RedirectPolicy.LimitFrom(options.MaxRedirects);
            var carried = options;
            var followMethod = method;
            var nextOptions = carried.Clone();
            var accumulatedCookies = new Dictionary<string, string>(result.Cookies, StringComparer.OrdinalIgnoreCase);

            foreach (var kv in result.Cookies)
                options.Cookies[kv.Key] = kv.Value;

            var lastHopStatus = result.StatusCode;
            var lastHopLocation = location;
            var finalResponse = result;
            var isFirstHop = true;

            var followed = await RedirectPolicy.FollowAsync(
                url,
                async (current, token) =>
                {
                    if (isFirstHop)
                    {
                        isFirstHop = false;
                        return new RedirectHop(lastHopStatus, lastHopLocation);
                    }

                    if (!RedirectPolicy.PreservesMethod(lastHopStatus, followMethod.Method))
                    {
                        nextOptions = carried.Clone();
                        nextOptions.Content = null;
                        nextOptions.Body = null;
                        nextOptions.Headers.Remove("Content-Type");
                        nextOptions.Headers.Remove("Content-Encoding");
                        nextOptions.Headers.Remove("Content-Length");
                        followMethod = HttpMethod.Get;
                    }
                    else
                    {
                        nextOptions = carried.Clone();
                    }

                    foreach (var kv in accumulatedCookies)
                        nextOptions.Cookies[kv.Key] = kv.Value;

                    var hopResponse = await SendAsync(followMethod, current, nextOptions, limit + 1, token)
                        .ConfigureAwait(false);

                    finalResponse = hopResponse;
                    foreach (var kv in hopResponse.Cookies)
                    {
                        accumulatedCookies[kv.Key] = kv.Value;
                        options.Cookies[kv.Key] = kv.Value;
                        carried.Cookies[kv.Key] = kv.Value;
                    }

                    lastHopStatus = hopResponse.StatusCode;
                    lastHopLocation = hopResponse.Headers.TryGetValue("Location", out var next) ? next : null;
                    return new RedirectHop(lastHopStatus, lastHopLocation);
                },
                limit,
                ct).ConfigureAwait(false);

            if (followed.TooMany)
                throw new NetException(followed.TooManyMessage());

            sw.Stop();
            var mergedFinal = new NetResponse
            {
                StatusCode = finalResponse.StatusCode,
                Body = finalResponse.Body,
                Url = finalResponse.Url,
                Headers = finalResponse.Headers,
                Cookies = accumulatedCookies,
                Elapsed = sw.Elapsed,
                Bytes = finalResponse.Bytes,
                Protocol = finalResponse.Protocol,
            };

            RecordAnalytics(mergedFinal, followMethod.Method, options, sw.Elapsed);
            return mergedFinal;
        }

        if (hops == 0 && Transport == TransportMode.SChannel)
            RecordAnalytics(result, method.Method, options, result.Elapsed);

        return result;
    }

    private void RecordAnalytics(NetResponse result, string methodName, RequestOptions options, TimeSpan elapsed)
    {
        _analytics.Record(new HttpRequestEvent
        {
            Url = result.Url.ToString(),
            Status = result.StatusCode,
            ElapsedMs = (int)elapsed.TotalMilliseconds,
            Bytes = result.Bytes,
            Protocol = result.Protocol,
            Profile = options.Profile.Name,
            Proxy = options.Proxy,
            Tag = options.Tag,
            Method = methodName,
        });
    }

    private async Task<NetResponse> SendSingleHopAsync(
        HttpMethod method,
        string url,
        RequestOptions options,
        CancellationToken ct)
    {
        if (Transport != TransportMode.SChannel)
        {
            string? bodyText = null;
            if (options.Content is not null)
                bodyText = await options.Content.ReadAsStringAsync(ct).ConfigureAwait(false);
            else if (options.Body is { } customBody)
                bodyText = Encoding.UTF8.GetString(MaterializeBody(customBody).Span);
            var proxy = string.IsNullOrWhiteSpace(options.Proxy) ? null : Cybersole.Core.Models.Proxy.Parse(options.Proxy);
            var headerCopy = options.Headers.ToDictionary(kv => kv.Key, kv => kv.Value, StringComparer.OrdinalIgnoreCase);
            if (options.Cookies.Count > 0 && !headerCopy.ContainsKey("Cookie"))
                headerCopy["Cookie"] = string.Join("; ", options.Cookies.Select(kv => $"{kv.Key}={kv.Value}"));

            if (Transport == TransportMode.OwnTls)
            {
                var ownUri = new Uri(url, UriKind.Absolute);
                try
                {
                    var ownPort = ownUri.Port == 0 ? 443 : ownUri.Port;
                    var own = await _tlsPool.RentAsync(ownUri.Host, ownPort, options.Profile,
                        options.Timeout, ct).ConfigureAwait(false);

                    var path = string.IsNullOrEmpty(ownUri.PathAndQuery) ? "/" : ownUri.PathAndQuery;

                    NetResponse ownResult;
                    try
                    {
                        ownResult = await own.SendAsync(method.Method.ToUpperInvariant(), path,
                            ownUri.Host, bodyText, ct).ConfigureAwait(false);
                    }
                    catch (Exception)
                    {
                        _tlsPool.Discard(own);
                        throw;
                    }

                    _tlsPool.Return(ownUri.Host, ownPort, options.Profile, own);

                    ownResult.Headers["X-Cyb-Transport"] = "own-tls12";
                    ownResult.Headers["X-Cyb-Alpn"] = own.Alpn ?? "-";
                    return ownResult;
                }
                catch (Exception ex) when (!ct.IsCancellationRequested)
                {
                    _fellBackFromOwnTls = true;
                    Interlocked.Increment(ref _ownTlsFallbackCount);
                    Transport = TransportMode.SChannel;
                    _lastOwnTlsError = ex.Message;
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
        var wireId = HttpDebug.StreamEnabled ? Guid.NewGuid().ToString("N") : null;
        byte[]? wireReqBody = null;
        if (wireId is not null)
        {
            if (options.Body is { } debugBody)
                wireReqBody = MaterializeBody(debugBody).ToArray();
            else if (options.Content is not null)
                wireReqBody = await options.Content.ReadAsByteArrayAsync(ct).ConfigureAwait(false);

            HttpDebug.RecordWireRequest(
                wireId, method.Method, url, options.Headers, options.Profile.Name,
                options.Proxy, options.Tag, wireReqBody);
        }

        for (var attempt = 0; attempt <= options.Retries; attempt++)
        {
            using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
            cts.CancelAfter(options.Timeout);
            try
            {
                var client = ClientFor(options.Profile, options.Proxy, out var cookieJar);
                using var request = await BuildRequestAsync(method, url, options, cookieJar, cts.Token)
                    .ConfigureAwait(false);
                using var response = await client.SendAsync(
                    request, HttpCompletionOption.ResponseContentRead, cts.Token).ConfigureAwait(false);

                var body = await ReadBodyAsync(response, cts.Token).ConfigureAwait(false);
                sw.Stop();

                var reqUri = response.RequestMessage?.RequestUri ?? new Uri(url, UriKind.Absolute);
                var hopCookies = ExtractCookies(response);
                RecordResponseCookies(cookieJar, reqUri, response);
                foreach (var kv in hopCookies)
                    options.Cookies[kv.Key] = kv.Value;

                var result = new NetResponse
                {
                    StatusCode = (int)response.StatusCode,
                    Body = body,
                    Url = reqUri,
                    Headers = response.Headers
                        .Concat(response.Content.Headers)
                        .GroupBy(h => h.Key, StringComparer.OrdinalIgnoreCase)
                        .ToDictionary(g => g.Key, g => string.Join(", ", g.SelectMany(v => v.Value)), StringComparer.OrdinalIgnoreCase),
                    Cookies = hopCookies,
                    Elapsed = sw.Elapsed,
                    Bytes = body.Length,
                    Protocol = response.Version.Major >= 2 ? "h2" : "http/1.1",
                };

                if (wireId is not null)
                {
                    HttpDebug.RecordWireResponse(
                        wireId, result.StatusCode, response.ReasonPhrase ?? string.Empty,
                        result.Protocol, result.Headers, result.Elapsed,
                        Encoding.UTF8.GetBytes(result.Body), attempt + 1);
                }

                return result;
            }
            catch (NotSupportedException)
            {
                throw;
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

        if (wireId is not null && last is not null)
            HttpDebug.RecordWireError(wireId, sw.Elapsed, last, last is NetException ne && ne.Message.StartsWith("timeout ", StringComparison.Ordinal));

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

    public Task<NetResponse> PostJsonAsync(string url, JToken json, RequestOptions? options = null,
        CancellationToken ct = default)
    {
        IBody body = json is JArray arr ? new LegacyJarrayBody(arr) : new LegacyJsonBody(json);
        options ??= new RequestOptions();
        options.Headers.TryAdd("Accept", "application/json");
        return PostBodyAsync(url, body, options, ct);
    }

    public Task<NetResponse> PostBodyAsync(string url, IBody body, RequestOptions? options = null,
        CancellationToken ct = default)
    {
        options ??= new RequestOptions();
        options.Body = body;
        return SendAsync(HttpMethod.Post, url, options, ct);
    }

    public Task<NetResponse> PostFormAsync(string url, IDictionary<string, string> form,
        RequestOptions? options = null, CancellationToken ct = default)
    {
        options ??= new RequestOptions();
        options.Content = new FormUrlEncodedContent(form);
        return SendAsync(HttpMethod.Post, url, options, ct);
    }

    private static ReadOnlyMemory<byte> MaterializeBody(IBody body)
    {
        if (body is BytesBody bb) return bb.Memory;
        var writer = new ArrayBufferWriter<byte>(body.SizeHint is > 0 and var hint ? hint : 256);
        body.WriteTo(writer);
        return writer.WrittenMemory;
    }

    private static bool IsContentHeader(string name) =>
        name.Equals("Content-Type", StringComparison.OrdinalIgnoreCase) ||
        name.Equals("Content-Encoding", StringComparison.OrdinalIgnoreCase) ||
        name.Equals("Content-Length", StringComparison.OrdinalIgnoreCase) ||
        name.Equals("Content-Language", StringComparison.OrdinalIgnoreCase) ||
        name.Equals("Content-Location", StringComparison.OrdinalIgnoreCase) ||
        name.Equals("Content-MD5", StringComparison.OrdinalIgnoreCase) ||
        name.Equals("Content-Range", StringComparison.OrdinalIgnoreCase) ||
        name.Equals("Expires", StringComparison.OrdinalIgnoreCase) ||
        name.Equals("Last-Modified", StringComparison.OrdinalIgnoreCase);

    private static async Task<HttpRequestMessage> BuildRequestAsync(
        HttpMethod method,
        string url,
        RequestOptions options,
        CookieContainer cookieJar,
        CancellationToken ct)
    {
        var uri = new Uri(url, UriKind.Absolute);
        var request = new HttpRequestMessage(method, uri);

        if (!options.OverrideHeaders)
        {
            var p = options.Profile;
            void AddDefault(string name, string value)
            {
                if (!options.Headers.ContainsKey(name))
                    request.Headers.TryAddWithoutValidation(name, value);
            }

            AddDefault("User-Agent", p.UserAgent);
            AddDefault("Accept",
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8");
            AddDefault("Accept-Language", p.AcceptLanguage);
            AddDefault("sec-ch-ua", p.SecChUa);
            AddDefault("sec-ch-ua-mobile", p.SecChUaMobile);
            AddDefault("sec-ch-ua-platform", p.SecChUaPlatform);
            AddDefault("sec-fetch-dest", "document");
            AddDefault("sec-fetch-mode", "navigate");
            AddDefault("sec-fetch-site", "none");
            AddDefault("sec-fetch-user", "?1");
            AddDefault("upgrade-insecure-requests", "1");
        }

        // Replace rather than append on request headers; never serialize options.Properties on wire.
        foreach (var (k, v) in options.Headers)
        {
            if (IsContentHeader(k)) continue;
            request.Headers.Remove(k);
            request.Headers.TryAddWithoutValidation(k, v);
        }

        if (!options.Headers.ContainsKey("Cookie"))
        {
            var mergedCookies = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            foreach (Cookie ck in cookieJar.GetCookies(uri))
                mergedCookies[ck.Name] = ck.Value;
            foreach (var (k, v) in options.Cookies)
                mergedCookies[k] = v;

            if (mergedCookies.Count > 0)
            {
                request.Headers.Remove("Cookie");
                request.Headers.TryAddWithoutValidation(
                    "Cookie",
                    string.Join("; ", mergedCookies.Select(kv => $"{kv.Key}={kv.Value}")));
            }
        }

        byte[]? payloadBytes = null;
        string? defaultContentType = null;
        List<KeyValuePair<string, IEnumerable<string>>>? sourceContentHeaders = null;

        if (options.Content is not null)
        {
            payloadBytes = await options.Content.ReadAsByteArrayAsync(ct).ConfigureAwait(false);
            defaultContentType = options.Content.Headers.ContentType?.ToString();
            sourceContentHeaders = new List<KeyValuePair<string, IEnumerable<string>>>();
            foreach (var h in options.Content.Headers)
            {
                if (!h.Key.Equals("Content-Length", StringComparison.OrdinalIgnoreCase))
                    sourceContentHeaders.Add(h);
            }
        }
        else if (options.Body is { } customBody)
        {
            payloadBytes = MaterializeBody(customBody).ToArray();
            defaultContentType = customBody.ContentType;
        }

        if (payloadBytes is not null)
        {
            var hasReqEnc = options.Headers.TryGetValue("Content-Encoding", out var reqEnc) &&
                            !string.IsNullOrWhiteSpace(reqEnc);
            if (hasReqEnc)
                payloadBytes = ContentEncodingCodec.Compress(payloadBytes, reqEnc);

            var content = new ByteArrayContent(payloadBytes);

            if (sourceContentHeaders is not null)
            {
                foreach (var h in sourceContentHeaders)
                    content.Headers.TryAddWithoutValidation(h.Key, h.Value);
            }

            if (options.Headers.TryGetValue("Content-Type", out var explicitContentType))
            {
                content.Headers.Remove("Content-Type");
                if (MediaTypeHeaderValue.TryParse(explicitContentType, out var parsedType))
                    content.Headers.ContentType = parsedType;
                else
                    content.Headers.TryAddWithoutValidation("Content-Type", explicitContentType);
            }
            else if (content.Headers.ContentType is null && !string.IsNullOrEmpty(defaultContentType))
            {
                content.Headers.TryAddWithoutValidation("Content-Type", defaultContentType);
            }

            foreach (var (k, v) in options.Headers)
            {
                if (!IsContentHeader(k) ||
                    k.Equals("Content-Type", StringComparison.OrdinalIgnoreCase) ||
                    k.Equals("Content-Length", StringComparison.OrdinalIgnoreCase))
                    continue;

                content.Headers.Remove(k);
                content.Headers.TryAddWithoutValidation(k, v);
            }

            request.Content = content;
        }

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

    private static void RecordResponseCookies(CookieContainer cookieJar, Uri requestUri, HttpResponseMessage response)
    {
        if (!response.Headers.TryGetValues("Set-Cookie", out var values))
            return;

        foreach (var raw in values)
        {
            try
            {
                cookieJar.SetCookies(requestUri, raw);
            }
            catch (CookieException)
            {
                var pair = raw.Split(';', 2)[0];
                var idx = pair.IndexOf('=');
                if (idx > 0)
                {
                    try
                    {
                        cookieJar.Add(requestUri, new Cookie(pair[..idx].Trim(), pair[(idx + 1)..].Trim()));
                    }
                    catch (CookieException)
                    {
                        // Non-RFC cookie names/values still flow via options.Cookies and NetResponse.Cookies.
                    }
                }
            }
        }
    }

    private static async Task<string> ReadBodyAsync(HttpResponseMessage response, CancellationToken ct)
    {
        var raw = await response.Content.ReadAsByteArrayAsync(ct).ConfigureAwait(false);
        if (response.Content.Headers.ContentEncoding.Count > 0)
            return ContentEncodingCodec.DecompressToString(raw, string.Join(", ", response.Content.Headers.ContentEncoding));

        return ContentEncodingCodec.DecodeUtf8WithBom(raw);
    }

    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;
        lock (_poolGate)
        {
            foreach (var c in _clients.Values) c.Dispose();
            _clients.Clear();
            _cookieContainers.Clear();
        }
    }
}
