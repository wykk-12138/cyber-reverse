using Cybersole.Http.Http3;
using Cybersole.Http.Profiles;
using Cybersole.Http.Quic;
using Cybersole.Http.Tls;
using Cybersole.Http.X509;

namespace Cybersole.Http.Protocol;

/// <summary>
/// Configuration options for <see cref="ProtocolRacer"/>.
/// </summary>
public sealed class ProtocolRacerOptions
{
    public TimeSpan RaceDelay { get; init; } = ProtocolRacer.DefaultRaceDelay;
    public int MaxRaceAttempts { get; init; } = ProtocolRacer.DefaultMaxRaceAttempts;
    public TimeSpan Http3Cooldown { get; init; } = ProtocolRacer.DefaultHttp3Cooldown;
    public TimeSpan ConnectTimeout { get; init; } = TimeSpan.FromSeconds(30);
    public bool CloseConnection { get; init; }
    public ConnectionDialer? Dialer { get; init; }
    public Func<DateTimeOffset>? Clock { get; init; }
    public Action<string>? KeyLogSink { get; init; }
    public Func<ConnectionKey, ClientProfile, CancellationToken, Task<IMultiplexedConnection>>? CustomH3Connector { get; init; }
    public Func<ConnectionKey, ClientProfile, CancellationToken, Task<IMultiplexedConnection>>? CustomTcpTlsConnector { get; init; }
}

/// <summary>
/// Happy Eyeballs HTTP/3 vs HTTP/2+HTTP/1.1 connection racer matching
/// <c>ProtocolRacer</c> (<c>0x1412C7660</c>, <c>0x141367F40</c>, <c>0x141368780</c>):
/// starts H3 immediately, staggers TCP+TLS fallback by 300ms, cancels and disposes the losing attempt,
/// tracks per-origin H3 failure cooldowns, <c>Alt-Svc</c> H3 hints, and cached QUIC RTT.
/// </summary>
public sealed class ProtocolRacer
{
    public static readonly TimeSpan DefaultRaceDelay = TimeSpan.FromMilliseconds(300);
    public const int DefaultMaxRaceAttempts = 3;
    public static readonly TimeSpan DefaultHttp3Cooldown = TimeSpan.FromMinutes(5);

    private sealed class OriginRaceState
    {
        public string? PreferredProtocol;
        public DateTimeOffset? Http3CooldownUntilUtc;
        public DateTimeOffset? AltSvcHttp3ExpiresUtc;
        public ulong? CachedRttUs;
    }

    private readonly TimeSpan _raceDelay;
    private readonly int _maxRaceAttempts;
    private readonly TimeSpan _http3Cooldown;
    private readonly TimeSpan _connectTimeout;
    private readonly bool _closeConnection;
    private readonly ConnectionDialer _dialer;
    private readonly Func<DateTimeOffset> _clock;
    private readonly Action<string>? _keyLogSink;
    private readonly Func<ConnectionKey, ClientProfile, CancellationToken, Task<IMultiplexedConnection>>? _customH3Connector;
    private readonly Func<ConnectionKey, ClientProfile, CancellationToken, Task<IMultiplexedConnection>>? _customTcpTlsConnector;

    private readonly object _gate = new();
    private readonly Dictionary<string, OriginRaceState> _originStates = new(StringComparer.OrdinalIgnoreCase);

    public ProtocolRacer(ProtocolRacerOptions? options = null)
    {
        options ??= new ProtocolRacerOptions();
        if (options.RaceDelay < TimeSpan.Zero)
            throw new ArgumentOutOfRangeException(nameof(options), "RaceDelay cannot be negative.");
        if (options.MaxRaceAttempts < 1)
            throw new ArgumentOutOfRangeException(nameof(options), "MaxRaceAttempts must be >= 1.");
        if (options.Http3Cooldown < TimeSpan.Zero)
            throw new ArgumentOutOfRangeException(nameof(options), "Http3Cooldown cannot be negative.");

        _raceDelay = options.RaceDelay;
        _maxRaceAttempts = options.MaxRaceAttempts;
        _http3Cooldown = options.Http3Cooldown;
        _connectTimeout = options.ConnectTimeout > TimeSpan.Zero ? options.ConnectTimeout : TimeSpan.FromSeconds(30);
        _closeConnection = options.CloseConnection;
        _dialer = options.Dialer ?? new ConnectionDialer(connectTimeout: _connectTimeout);
        _clock = options.Clock ?? (() => DateTimeOffset.UtcNow);
        _keyLogSink = options.KeyLogSink;
        _customH3Connector = options.CustomH3Connector;
        _customTcpTlsConnector = options.CustomTcpTlsConnector;
    }

    public TimeSpan RaceDelay => _raceDelay;
    public int MaxRaceAttempts => _maxRaceAttempts;
    public TimeSpan Http3Cooldown => _http3Cooldown;
    public ConnectionDialer Dialer => _dialer;

    /// <summary>
    /// Returns true if HTTP/3 can be raced for <paramref name="key"/>, <paramref name="profile"/>, and <paramref name="proxy"/>
    /// (requires <c>https</c>, neither <c>ForceHttp11</c> nor <c>DisableHttp3</c>, <c>profile.SupportsHttp3</c>,
    /// direct or UDP-capable SOCKS5 proxy, and not currently in H3 failure cooldown).
    /// </summary>
    public bool CanAttemptHttp3(ConnectionKey key, ClientProfile profile, ProxySpec? proxy = null)
    {
        ArgumentNullException.ThrowIfNull(profile);

        if (!string.Equals(key.Scheme, "https", StringComparison.OrdinalIgnoreCase))
            return false;
        if (key.ForceHttp11 || key.DisableHttp3)
            return false;
        if (!profile.SupportsHttp3)
            return false;
        if (proxy is not null && proxy.Kind != ProxyProtocolKind.None && !proxy.SupportsUdp)
            return false;

        return !IsInHttp3Cooldown(key);
    }

    public bool IsInHttp3Cooldown(ConnectionKey key)
    {
        DateTimeOffset now = _clock();
        string originKey = MakeOriginKey(key);
        lock (_gate)
        {
            if (!_originStates.TryGetValue(originKey, out OriginRaceState? state))
                return false;
            if (state.Http3CooldownUntilUtc is { } until && until > now)
                return true;

            state.Http3CooldownUntilUtc = null;
            return false;
        }
    }

    public string? GetPreferredProtocol(ConnectionKey key)
    {
        string originKey = MakeOriginKey(key);
        lock (_gate)
        {
            return _originStates.TryGetValue(originKey, out OriginRaceState? state)
                ? state.PreferredProtocol
                : null;
        }
    }

    public bool HasAltSvcHttp3Hint(string host, int port, string? proxyKey = null)
    {
        if (string.IsNullOrWhiteSpace(host))
            return false;

        DateTimeOffset now = _clock();
        string originKey = MakeOriginKey(host, port, proxyKey);
        lock (_gate)
        {
            if (!_originStates.TryGetValue(originKey, out OriginRaceState? state))
                return false;
            if (state.AltSvcHttp3ExpiresUtc is { } exp && exp > now)
                return true;

            state.AltSvcHttp3ExpiresUtc = null;
            return false;
        }
    }

    public void RecordAltSvc(string host, int port, string? altSvcHeader, string? proxyKey = null)
    {
        if (string.IsNullOrWhiteSpace(host) || string.IsNullOrWhiteSpace(altSvcHeader))
            return;

        string originKey = MakeOriginKey(host, port, proxyKey);
        string trimmed = altSvcHeader.Trim();
        if (string.Equals(trimmed, "clear", StringComparison.OrdinalIgnoreCase))
        {
            lock (_gate)
            {
                if (_originStates.TryGetValue(originKey, out OriginRaceState? existing))
                    existing.AltSvcHttp3ExpiresUtc = null;
            }
            return;
        }

        long? bestMaxAgeSeconds = null;
        string[] entries = trimmed.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        for (int i = 0; i < entries.Length; i++)
        {
            string[] parts = entries[i].Split(';', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
            if (parts.Length == 0)
                continue;

            int eq = parts[0].IndexOf('=');
            if (eq <= 0)
                continue;

            string proto = parts[0][..eq].Trim();
            if (!string.Equals(proto, "h3", StringComparison.OrdinalIgnoreCase))
                continue;

            long ma = 86_400; // RFC 7838 default 24h
            for (int p = 1; p < parts.Length; p++)
            {
                int peq = parts[p].IndexOf('=');
                if (peq <= 0)
                    continue;
                string pName = parts[p][..peq].Trim();
                if (string.Equals(pName, "ma", StringComparison.OrdinalIgnoreCase))
                {
                    string pVal = parts[p][(peq + 1)..].Trim().Trim('"');
                    if (long.TryParse(pVal, out long parsed) && parsed >= 0)
                        ma = parsed;
                }
            }

            if (bestMaxAgeSeconds is null || ma > bestMaxAgeSeconds.Value)
                bestMaxAgeSeconds = ma;
        }

        if (bestMaxAgeSeconds is null)
            return;

        DateTimeOffset now = _clock();
        lock (_gate)
        {
            OriginRaceState state = GetOrCreateOriginStateLocked(originKey);
            if (bestMaxAgeSeconds.Value == 0)
            {
                state.AltSvcHttp3ExpiresUtc = null;
                return;
            }

            state.AltSvcHttp3ExpiresUtc = now + TimeSpan.FromSeconds(Math.Min(bestMaxAgeSeconds.Value, 30L * 86_400L));
            if (string.Equals(state.PreferredProtocol, "tcp", StringComparison.Ordinal))
                state.PreferredProtocol = null;
        }
    }

    /// <summary>
    /// Acquires and sends a single request using Happy Eyeballs racing with up to <see cref="MaxRaceAttempts"/>
    /// acquisition attempts per <c>ProtocolRacer.SendAsync</c> (<c>0x141368780</c>).
    /// </summary>
    public async Task<PureHttpResponse> SendAsync(
        PureHttpRequest request,
        ConnectionKey key,
        ClientProfile profile,
        ProxySpec? proxy = null,
        CertificateVerifyOptions? verifyOptions = null,
        LruTlsSessionCache? sessionCache = null,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(request);
        ArgumentNullException.ThrowIfNull(profile);

        Exception? lastError = null;
        for (int attempt = 0; attempt < _maxRaceAttempts; attempt++)
        {
            cancellationToken.ThrowIfCancellationRequested();

            IMultiplexedConnection? conn = null;
            try
            {
                conn = await ConnectAsync(key, profile, proxy, verifyOptions, sessionCache, cancellationToken)
                    .ConfigureAwait(false);
                if (!conn.IsUsable)
                {
                    await conn.DisposeAsync().ConfigureAwait(false);
                    conn = null;
                    continue;
                }

                PureHttpResponse response = await conn.SendAsync(request, cancellationToken).ConfigureAwait(false);
                if (!string.IsNullOrWhiteSpace(response.AltSvcHeader))
                    RecordAltSvc(key.Host, key.Port, response.AltSvcHeader, key.ProxyKey);
                return response;
            }
            catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
            {
                throw;
            }
            catch (Exception ex) when (IsNonRetryableAcquisitionFailure(ex))
            {
                throw;
            }
            catch (Exception ex)
            {
                lastError = ex;
            }
            finally
            {
                if (conn is not null)
                {
                    try { await conn.DisposeAsync().ConfigureAwait(false); }
                    catch { /* Best-effort teardown on single-use racer path. */ }
                }
            }
        }

        throw new PureHttpException(
            HttpErrorClassifier.Classify(lastError),
            "protocol racing failed to produce a usable connection",
            lastError);
    }

    /// <summary>
    /// Performs one Happy Eyeballs connection race (H3 vs 300ms-staggered TCP+TLS H2/H1),
    /// cancelling and disposing the losing attempt cleanly.
    /// </summary>
    public async Task<IMultiplexedConnection> ConnectAsync(
        ConnectionKey key,
        ClientProfile profile,
        ProxySpec? proxy = null,
        CertificateVerifyOptions? verifyOptions = null,
        LruTlsSessionCache? sessionCache = null,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(profile);
        cancellationToken.ThrowIfCancellationRequested();

        if (!CanAttemptHttp3(key, profile, proxy))
            return await ConnectTcpAsync(key, profile, proxy, verifyOptions, sessionCache, cancellationToken).ConfigureAwait(false);

        string originKey = MakeOriginKey(key);
        TimeSpan stagger = ResolveStaggerDelay(originKey);

        var h3Cts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        var tcpCts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);

        Task<IMultiplexedConnection> h3Task = ConnectH3Async(key, profile, proxy, verifyOptions, sessionCache, h3Cts.Token);

        if (stagger > TimeSpan.Zero && !h3Task.IsCompleted)
        {
            using var staggerCts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
            Task delayTask = Task.Delay(stagger, staggerCts.Token);
            await Task.WhenAny(h3Task, delayTask).ConfigureAwait(false);
            staggerCts.Cancel();
        }

        if (h3Task.IsCompleted)
        {
            if (h3Task.IsCompletedSuccessfully)
            {
                h3Cts.Dispose();
                tcpCts.Dispose();
                RecordHttp3Success(originKey, h3Task.Result);
                return h3Task.Result;
            }

            if (cancellationToken.IsCancellationRequested)
            {
                _ = ObserveFaultedTask(h3Task);
                h3Cts.Dispose();
                tcpCts.Dispose();
                throw new OperationCanceledException(cancellationToken);
            }

            Exception h3EarlyError = UnwrapTaskException(h3Task);
            h3Cts.Dispose();

            try
            {
                IMultiplexedConnection tcpConn = await ConnectTcpAsync(key, profile, proxy, verifyOptions, sessionCache, tcpCts.Token)
                    .ConfigureAwait(false);
                tcpCts.Dispose();
                RecordHttp3Failure(originKey);
                RecordPreferredProtocol(originKey, "tcp");
                return tcpConn;
            }
            catch (Exception tcpError)
            {
                tcpCts.Dispose();
                if (cancellationToken.IsCancellationRequested)
                    throw new OperationCanceledException(cancellationToken);
                throw SelectWinningFailure(tcpError, h3EarlyError);
            }
        }

        Task<IMultiplexedConnection> tcpTask = ConnectTcpAsync(key, profile, proxy, verifyOptions, sessionCache, tcpCts.Token);
        Task<IMultiplexedConnection> first = await Task.WhenAny(h3Task, tcpTask).ConfigureAwait(false);

        if (ReferenceEquals(first, h3Task))
        {
            if (h3Task.IsCompletedSuccessfully)
            {
                CleanupLosingAttempt(tcpTask, tcpCts);
                h3Cts.Dispose();
                RecordHttp3Success(originKey, h3Task.Result);
                return h3Task.Result;
            }

            if (cancellationToken.IsCancellationRequested)
            {
                _ = ObserveFaultedTask(h3Task);
                CleanupLosingAttempt(tcpTask, tcpCts);
                h3Cts.Dispose();
                throw new OperationCanceledException(cancellationToken);
            }

            Exception h3Error = UnwrapTaskException(h3Task);
            h3Cts.Dispose();

            try
            {
                IMultiplexedConnection tcpConn = await tcpTask.ConfigureAwait(false);
                tcpCts.Dispose();
                RecordHttp3Failure(originKey);
                RecordPreferredProtocol(originKey, "tcp");
                return tcpConn;
            }
            catch (Exception tcpError)
            {
                tcpCts.Dispose();
                if (cancellationToken.IsCancellationRequested)
                    throw new OperationCanceledException(cancellationToken);
                throw SelectWinningFailure(tcpError, h3Error);
            }
        }

        if (tcpTask.IsCompletedSuccessfully)
        {
            bool h3Faulted = h3Task.IsFaulted;
            CleanupLosingAttempt(h3Task, h3Cts);
            tcpCts.Dispose();
            if (h3Faulted)
                RecordHttp3Failure(originKey);
            RecordPreferredProtocol(originKey, "tcp");
            return tcpTask.Result;
        }

        if (cancellationToken.IsCancellationRequested)
        {
            _ = ObserveFaultedTask(tcpTask);
            CleanupLosingAttempt(h3Task, h3Cts);
            tcpCts.Dispose();
            throw new OperationCanceledException(cancellationToken);
        }

        Exception tcpEarlyError = UnwrapTaskException(tcpTask);
        tcpCts.Dispose();

        try
        {
            IMultiplexedConnection h3Conn = await h3Task.ConfigureAwait(false);
            h3Cts.Dispose();
            RecordHttp3Success(originKey, h3Conn);
            return h3Conn;
        }
        catch (Exception h3Error)
        {
            h3Cts.Dispose();
            if (cancellationToken.IsCancellationRequested)
                throw new OperationCanceledException(cancellationToken);
            throw SelectWinningFailure(tcpEarlyError, h3Error);
        }
    }

    private async Task<IMultiplexedConnection> ConnectH3Async(
        ConnectionKey key,
        ClientProfile profile,
        ProxySpec? proxy,
        CertificateVerifyOptions? verifyOptions,
        LruTlsSessionCache? sessionCache,
        CancellationToken cancellationToken)
    {
        if (_customH3Connector is not null)
            return await _customH3Connector(key, profile, cancellationToken).ConfigureAwait(false);

        ulong? cachedRttUs = TryGetCachedRttUs(MakeOriginKey(key));
        var quicOptions = new QuicConnectionOptions
        {
            Host = key.Host,
            Port = key.Port,
            Profile = profile,
            TransportSpec = profile.QuicSpec,
            Proxy = proxy,
            VerifyOptions = BuildEffectiveVerifyOptions(key, verifyOptions),
            SessionCache = (key.OptionsFlagsMask & ConnectionKey.FlagDisableSessionTickets) != 0 ? null : sessionCache,
            ConnectTimeout = _connectTimeout,
            RandomExtensionOrder = (key.OptionsFlagsMask & ConnectionKey.FlagRandomExtensionOrder) != 0,
            DisableSessionTickets = (key.OptionsFlagsMask & ConnectionKey.FlagDisableSessionTickets) != 0,
            KeyLogSink = _keyLogSink,
            DnsResolver = (host, ct) => new ValueTask<System.Net.IPAddress[]>(_dialer.DnsCache.ResolveAsync(host, ct)),
            InitialRttUs = cachedRttUs,
        };

        return await Http3Connection.ConnectAsync(quicOptions, key, cancellationToken).ConfigureAwait(false);
    }

    private async Task<IMultiplexedConnection> ConnectTcpAsync(
        ConnectionKey key,
        ClientProfile profile,
        ProxySpec? proxy,
        CertificateVerifyOptions? verifyOptions,
        LruTlsSessionCache? sessionCache,
        CancellationToken cancellationToken)
    {
        if (_customTcpTlsConnector is not null)
            return await _customTcpTlsConnector(key, profile, cancellationToken).ConfigureAwait(false);

        CertificateVerifyOptions? effectiveVerify = BuildEffectiveVerifyOptions(key, verifyOptions);
        DialedConnection dialed = await _dialer.DialAsync(
            key.Host,
            key.Port,
            proxy,
            effectiveVerify,
            _connectTimeout,
            cancellationToken).ConfigureAwait(false);

        if (string.Equals(key.Scheme, "http", StringComparison.OrdinalIgnoreCase))
        {
            return new Http1Connection(
                dialed.Stream,
                key,
                profile.Http2Settings.HeaderOrder,
                closeConnection: _closeConnection,
                leaveStreamOpen: false);
        }

        if (!string.Equals(key.Scheme, "https", StringComparison.OrdinalIgnoreCase))
        {
            await dialed.DisposeAsync().ConfigureAwait(false);
            throw new PureHttpException(HttpErrorKind.Protocol, $"Unsupported URI scheme '{key.Scheme}'.");
        }

        TlsStream? tlsStream = null;
        try
        {
            var tlsOptions = new TlsConnectionOptions
            {
                ServerName = key.Host,
                Port = key.Port,
                Profile = profile,
                VerifyOptions = effectiveVerify,
                SessionCache = (key.OptionsFlagsMask & ConnectionKey.FlagDisableSessionTickets) != 0 ? null : sessionCache,
                HandshakeTimeout = _connectTimeout,
                ForceHttp11 = key.ForceHttp11,
                RandomExtensionOrder = (key.OptionsFlagsMask & ConnectionKey.FlagRandomExtensionOrder) != 0,
                DisableSessionTickets = (key.OptionsFlagsMask & ConnectionKey.FlagDisableSessionTickets) != 0,
                LeaveInnerStreamOpen = false,
                KeyLogSink = _keyLogSink,
                NowUtc = _clock(),
            };

            tlsStream = new TlsStream(dialed.Stream, tlsOptions);
            await tlsStream.HandshakeAsync(cancellationToken).ConfigureAwait(false);

            string? alpn = tlsStream.NegotiatedAlpn;
            if (string.Equals(alpn, "h2", StringComparison.OrdinalIgnoreCase) &&
                !key.ForceHttp11 &&
                !profile.DisableHttp2)
            {
                return await Http2Connection.ConnectAsync(
                    tlsStream,
                    key,
                    profile.Http2Settings,
                    leaveStreamOpen: false,
                    cancellationToken: cancellationToken).ConfigureAwait(false);
            }

            return new Http1Connection(
                tlsStream,
                key,
                profile.Http2Settings.HeaderOrder,
                closeConnection: _closeConnection,
                leaveStreamOpen: false);
        }
        catch
        {
            if (tlsStream is not null)
                await tlsStream.DisposeAsync().ConfigureAwait(false);
            else
                await dialed.DisposeAsync().ConfigureAwait(false);
            throw;
        }
    }

    private static CertificateVerifyOptions? BuildEffectiveVerifyOptions(
        ConnectionKey key,
        CertificateVerifyOptions? verifyOptions)
    {
        if (!key.InsecureSkipVerify)
            return verifyOptions;

        if (verifyOptions is null)
            return new CertificateVerifyOptions { InsecureSkipVerify = true };

        if (verifyOptions.InsecureSkipVerify)
            return verifyOptions;

        return new CertificateVerifyOptions
        {
            InsecureSkipVerify = true,
            VerificationTime = verifyOptions.VerificationTime,
            CustomRoots = verifyOptions.CustomRoots,
            UseEmbeddedDefaultRoots = verifyOptions.UseEmbeddedDefaultRoots,
            Pinner = verifyOptions.Pinner,
            MaxChainLength = verifyOptions.MaxChainLength,
            MaxSignatureChecks = verifyOptions.MaxSignatureChecks,
            AllowSha1 = verifyOptions.AllowSha1,
        };
    }

    private TimeSpan ResolveStaggerDelay(string originKey)
    {
        DateTimeOffset now = _clock();
        lock (_gate)
        {
            if (!_originStates.TryGetValue(originKey, out OriginRaceState? state))
                return _raceDelay;

            if (state.AltSvcHttp3ExpiresUtc is { } exp)
            {
                if (exp > now)
                    return _raceDelay;
                state.AltSvcHttp3ExpiresUtc = null;
            }

            if (string.Equals(state.PreferredProtocol, "tcp", StringComparison.Ordinal))
                return TimeSpan.Zero;

            return _raceDelay;
        }
    }

    private void RecordHttp3Success(string originKey, IMultiplexedConnection conn)
    {
        ulong? rttUs = null;
        if (conn is Http3Connection h3 && h3.Quic.LossRecovery.HasRttSample)
        {
            TimeSpan srtt = h3.Quic.LossRecovery.SmoothedRtt;
            if (srtt > TimeSpan.Zero)
                rttUs = (ulong)Math.Max(1L, srtt.Ticks / 10L);
        }

        lock (_gate)
        {
            OriginRaceState state = GetOrCreateOriginStateLocked(originKey);
            state.PreferredProtocol = "h3";
            state.Http3CooldownUntilUtc = null;
            if (rttUs.HasValue)
                state.CachedRttUs = rttUs;
        }
    }

    private void RecordHttp3Failure(string originKey)
    {
        if (_http3Cooldown <= TimeSpan.Zero)
            return;

        DateTimeOffset until = _clock() + _http3Cooldown;
        lock (_gate)
        {
            OriginRaceState state = GetOrCreateOriginStateLocked(originKey);
            state.Http3CooldownUntilUtc = until;
        }
    }

    private void RecordPreferredProtocol(string originKey, string protocol)
    {
        lock (_gate)
        {
            OriginRaceState state = GetOrCreateOriginStateLocked(originKey);
            state.PreferredProtocol = protocol;
        }
    }

    private ulong? TryGetCachedRttUs(string originKey)
    {
        lock (_gate)
        {
            return _originStates.TryGetValue(originKey, out OriginRaceState? state)
                ? state.CachedRttUs
                : null;
        }
    }

    private OriginRaceState GetOrCreateOriginStateLocked(string originKey)
    {
        if (!_originStates.TryGetValue(originKey, out OriginRaceState? state))
        {
            state = new OriginRaceState();
            _originStates[originKey] = state;
        }
        return state;
    }

    private static string MakeOriginKey(ConnectionKey key) => MakeOriginKey(key.Host, key.Port, key.ProxyKey);

    private static string MakeOriginKey(string host, int port, string? proxyKey) =>
        $"{host.Trim().ToLowerInvariant()}:{port}|{proxyKey ?? "direct"}";

    private static bool IsNonRetryableAcquisitionFailure(Exception ex)
    {
        for (Exception? cur = ex; cur is not null; cur = cur.InnerException)
        {
            if (cur is CertificateValidationException or ProxyException or OperationCanceledException)
                return true;
        }
        return false;
    }

    private static Exception SelectWinningFailure(Exception tcpError, Exception h3Error)
    {
        if (HasCertificateOrPinFailure(h3Error) && !HasCertificateOrPinFailure(tcpError))
            return h3Error;
        return tcpError;
    }

    private static bool HasCertificateOrPinFailure(Exception ex)
    {
        for (Exception? cur = ex; cur is not null; cur = cur.InnerException)
        {
            if (cur is CertificateValidationException)
                return true;
        }
        return false;
    }

    private static Exception UnwrapTaskException(Task task)
    {
        if (task.Exception is { } agg)
        {
            AggregateException flattened = agg.Flatten();
            return flattened.InnerExceptions.Count == 1 ? flattened.InnerExceptions[0] : flattened;
        }
        return new TaskCanceledException(task);
    }

    private static Exception? ObserveFaultedTask(Task task) => task.Exception;

    private static void CleanupLosingAttempt(Task<IMultiplexedConnection> losingTask, CancellationTokenSource cts)
    {
        cts.Cancel();
        _ = losingTask.ContinueWith(
            static (t, state) => CleanupLosingAttemptCoreAsync(t, (CancellationTokenSource)state!),
            cts,
            CancellationToken.None,
            TaskContinuationOptions.ExecuteSynchronously,
            TaskScheduler.Default);
    }

    private static async Task CleanupLosingAttemptCoreAsync(
        Task<IMultiplexedConnection> losingTask,
        CancellationTokenSource cts)
    {
        try
        {
            if (losingTask.IsCompletedSuccessfully)
                await losingTask.Result.DisposeAsync().ConfigureAwait(false);
            else
                _ = losingTask.Exception;
        }
        catch
        {
            // Ignore losing connection disposal failures.
        }
        finally
        {
            cts.Dispose();
        }
    }
}
