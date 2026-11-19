using Cybersole.Stores.Flows;
using System.Text.Json;
using Cybersole.Stores.Scripts;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Kasada token production through a real Chromium.
///
/// R17 proved a bare JS engine cannot finish Nike's payload. The original solves this by
/// embedding DotNetBrowser; this class does the equivalent with whatever Chromium-based
/// browser is already installed, so no runtime has to be shipped or downloaded.
///
/// The token never has to be reverse-engineered out of the script: the page computes it
/// itself, and we simply read the header it puts on the next request (or the cookie it
/// writes), which is exactly what a browser automation tool would see.
/// </summary>
public sealed class ChromiumKasadaSolver
{
    /// <summary>
    /// Every request the page made on the most recent solve, in order, with what came back. Kept so a
    /// caller can see which request actually produced the token instead of guessing from a header set.
    /// </summary>
    public List<ChromiumRoundtrip> LastRoundtrips { get; private set; } = new();

    /// <summary>
    /// URL patterns to drop before they reach the network. A checkout page is mostly things a sensor never
    /// reads -- images, fonts, media, consent banners, analytics -- and over a metered proxy those are the
    /// entire bill. Measured on the arcteryx product page: 20.57 MB per identity unblocked, 0.64 MB with
    /// <see cref="DefaultBlockPatterns"/>, and the submission still answers {"reload":true}.
    /// </summary>
    public List<string> BlockPatterns { get; } = new();

    /// <summary>
    /// Drop the page furniture by default. Set false to load everything the way a shopper would -- the
    /// challenge still solves either way on the pages measured, but that is not a promise for every site.
    /// </summary>
    public bool ReduceTraffic { get; set; } = true;

    /// <summary>
    /// Categories that cannot carry anything the sensor reads. Private media extensions are listed
    /// explicitly because a by-format blacklist misses them (nike serves .cmfv / .cmfa).
    /// </summary>
    public static IReadOnlyList<string> DefaultBlockPatterns { get; } = new[]
    {
        // images, fonts, media
        "*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif", "*.svg", "*.avif", "*.ico",
        "*.woff", "*.woff2", "*.ttf", "*.otf", "*.eot",
        "*.mp4", "*.webm", "*.m3u8", "*.cmfv", "*.cmfa", "*.mpd",
        "*/video/*", "*/video-player/*",
        // third-party analytics and beacons
        "*.nr-data.net/*", "*.newrelic.com/*", "*.demdex.net/*", "*.adobedtm.com/*",
        "*.facebook.net/*", "*.google-analytics.com/*", "*.doubleclick.net/*",
        "*.hotjar.com/*", "*.segment.io/*", "*.googletagmanager.com/*",
        "*mtrx9k*", "cdn.evgnet.com/*", "*.evgnet.com/*",
        "*.bazaarvoice.com/*", "*.switchgrowth.com/*", "*.cloudflareinsights.com/*",
        // consent SDK -- 139 KB of banner on the first paint, read by nothing in the challenge
        "*.cookielaw.org/*", "*.onetrust.com/*",
        // static bundles and edge beacons
        "*/static/*", "*_next/static/*", "*.chunk.*.js", "*/cdn-cgi/*",
    };

    /// <summary>Patterns currently in force, for diagnostics.</summary>
    public List<string> BlockedPatterns => _bridge?.BlockedPatterns ?? new List<string>();

    private ChromiumBridge? _bridge;

    /// <summary>
    /// Run the browser without a window. Off by default: a visible window is the configuration the
    /// challenge is known to accept, and headless adds signals of its own.
    /// </summary>
    public static bool KasadaHeadless { get; set; }

    /// <summary>
    /// Overwrite the browser's surface with a fabricated one before the page runs. Off by default: the
    /// reference implementation does not do it, and each overwritten property is a difference a detector
    /// can look for.
    /// </summary>
    public static bool KasadaStealth { get; set; }

    /// <summary>
    /// The body the submission endpoint answered with. A 200 with an empty body is an unsolved round; only
    /// the 15-byte {"reload":true} means the challenge was actually solved.
    /// </summary>
    public string? TlBody { get; private set; }

    /// <summary>True when the submission answered with the solved marker.</summary>
    public bool TlSolved => TlBody is not null && TlBody.Contains("reload", StringComparison.Ordinal);

    /// <summary>Per-URL bytes, largest first, so a caller can see what to block.</summary>
    public List<(string Url, long Bytes)> WireBreakdown { get; private set; } = new();

    /// <summary>
    /// Evaluate an expression after the harvest has finished. Safe at that point and only then: probing a
    /// page while the challenge is computing is what stopped it from solving.
    /// <para>
    /// This only works while the profile is still open. Once <see cref="SolveAsync"/> returns the browser is
    /// gone, so anything that has to ride the solved session belongs in <see cref="AfterSolveAsync"/>.
    /// </para>
    /// </summary>
    public async Task<string?> EvaluateAfterRunAsync(string expression, CancellationToken ct = default,
        bool awaitPromise = false)
        => _bridge is null
            ? null
            : await _bridge.EvaluateAsync(expression, ct, awaitPromise).ConfigureAwait(false);

    /// <summary>
    /// Runs after the round resolves but before the profile is closed, with the bridge still live. This is
    /// the only place a token can be spent against the session that produced it -- the cookies, client hints
    /// and connection fingerprint it needs are the browser's own and do not survive the shutdown.
    /// </summary>
    public Func<ChromiumBridge, CancellationToken, Task>? AfterSolveAsync { get; set; }

    /// <summary>What <see cref="AfterSolveAsync"/> threw, if it threw. Reported apart from the round itself.</summary>
    public string? AfterSolveError { get; private set; }

    /// <summary>
    /// User-data-dir to launch with. Left null the browser gets a throwaway profile, which means the sensor
    /// script, the page and every static asset are downloaded again on every single harvest. Point this at a
    /// kept directory and the second harvest onwards serves them from the profile cache, leaving only the
    /// challenge itself on the wire.
    /// </summary>
    public string? ProfilePath { get; set; }

    /// <summary>
    /// HTTP cache directory, shared across profiles. Wiping a profile's identity is what makes the site ask
    /// for a round again, but a fresh profile also starts with an empty cache and pays for the page and the
    /// sensor script all over again. A shared cache keeps the identities separate and the downloads common.
    /// </summary>
    public string? CachePath { get; set; }

    /// <summary>
    /// Drop the profile's cookies and page storage before navigating. Only meaningful with a kept profile:
    /// the point is to keep the downloaded sensor and still ask for a fresh round.
    /// </summary>
    public bool FreshCookies { get; set; }

    /// <summary>
    /// The page's own Date.now() at the moment the submission finished. This is the only correct partner for
    /// the server's x-kpsdk-st: pairing st with the host clock instead injects the difference between the two
    /// clocks as if it were latency, and the PoW's workTime is derived from that number.
    /// </summary>
    public long? ReceivedAtMs { get; private set; }

    /// <summary>Cookies the profile held when the harvest finished.</summary>
    public string CookieHeader { get; private set; } = "";

    /// <summary>Headers the page's own last request to a path carried.</summary>
    public Dictionary<string, string> RequestHeadersFor(string fragment) => LastRequestHeaders(fragment);

    /// <summary>Cookies the profile holds after the harvest, so a replay can send what the browser sent.</summary>
    public async Task<string> CookieHeaderAfterRunAsync(CancellationToken ct = default)
        => _bridge is null ? "" : await _bridge.CookieHeaderAsync(ct).ConfigureAwait(false);

    /// <summary>The headers the page's own last request to <paramref name="fragment"/> carried.</summary>
    public Dictionary<string, string> LastRequestHeaders(string fragment)
    {
        var rt = LastRoundtrips.LastOrDefault(r => r.Url.Contains(fragment, StringComparison.OrdinalIgnoreCase));
        return rt is null
            ? new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            : new Dictionary<string, string>(rt.RequestHeaders, StringComparer.OrdinalIgnoreCase);
    }

    /// <summary>Bytes the browser actually pulled, per CDP's own accounting.</summary>
    public long WireBytes { get; private set; }

    /// <summary>Requests dropped locally and never sent.</summary>
    public int BlockedRequestCount { get; private set; }

    /// <summary>
    /// Cookie/DOM expressions probed only after header sniffing has failed. The live Nike
    /// build exposes just <c>configure</c> and <c>isReady</c> on <c>KPSDK</c>, so these are a
    /// long shot kept for other builds — the wire is the reliable source.
    /// </summary>
    private static readonly string[] TokenProbes =
    {
        "(document.cookie.match(/(?:^|;\\s*)ct=([^;]+)/) || [])[1] || null",
        "(document.cookie.match(/(?:^|;\\s*)kpsdk-ct=([^;]+)/) || [])[1] || null",
        "(window.KPSDK && typeof window.KPSDK.ct === 'function') ? window.KPSDK.ct() : null",
        "(window.KPSDK && window.KPSDK.ct) ? String(window.KPSDK.ct) : null",
    };

    /// <summary>True when a Chromium build is available to drive.</summary>
    public static bool IsAvailable => ChromiumBridge.FindBrowser() is not null;

    public string? ScriptUrl { get; private set; }

    /// <summary>
    /// The profile key this token was produced on — the identity the payment must describe.
    /// Empty when the run never reached a browser.
    /// </summary>
    public string ProfileKey { get; private set; } = string.Empty;

    /// <summary>
    /// Load <paramref name="pageUrl"/> in a headless browser, wait for Kasada to initialise,
    /// and read back whatever token it produced. Every step is reported so a failure explains
    /// itself instead of returning an empty string.
    /// </summary>
    /// <summary>
    /// <paramref name="triggerUrl"/> is an optional endpoint the page should call after it
    /// boots. <c>x-kpsdk-sb</c> only materialises once a protected endpoint is exercised, so
    /// without one the result carries <c>ct</c> alone — which is all a browse-style request
    /// needs, and all a storefront will hand out before a cart exists.
    /// </summary>
    public async Task<KasadaResult> SolveAsync(string pageUrl, TimeSpan? timeout = null,
        string? triggerUrl = null, CancellationToken ct = default, FlowSession? session = null)
    {
        var limit = timeout ?? TimeSpan.FromSeconds(45);

        if (!IsAvailable)
        {
            return new KasadaResult
            {
                Ok = false,
                Error = "no Chromium-based browser found (Chrome / Edge / WebView2)",
                NeedsRealBrowser = true,
            };
        }

        ChromiumBridge? bridge = null;
        try
        {
            // Headed by default. The reference implementation runs a normal window and its own notes say a
            // debug port without one is what makes the challenge refuse; headless adds a set of its own
            // signals on top. KasadaHeadless exists for callers that cannot show a window and accept that.
            //
            // A caller-supplied profile is what makes a second harvest cheap: the sensor script is several
            // hundred kilobytes and never changes between rounds, so on a kept profile it comes from the
            // browser cache instead of the network. A fresh one re-downloads it every single time.
            bridge = await ChromiumBridge.LaunchAsync(headed: !KasadaHeadless, profilePath: ProfilePath,
                                                      ct: ct, cachePath: CachePath).ConfigureAwait(false);

            // R135: the browser that solves this token is the browser the payment will describe. One
            // key, recorded here, so the profile folder, the fingerprint and the 3-D Secure profile all
            // belong to the same machine.
            ProfileKey = bridge.ProfilePath;

            if (session is not null)
            {
                BrowserIdentity.RecordProfile(session, bridge.ProfilePath,
                    utcOffsetMinutes: BrowserIdentity.TimeZoneOffset(session),
                    userAgentAlreadySent: true);
            }

            // Look like desktop Chrome before the first request: the UA token, the UA-CH
            // brands and navigator.webdriver are all checked before a token is issued.
            // Stealth injection is skipped by default. The reference implementation injects nothing at all
            // (no addScriptToEvaluateOnNewDocument anywhere in its harvest path) and its notes say the plain
            // configuration is the one the challenge accepts -- so every surface this mask overwrites is
            // itself a difference from a real browser. KasadaStealth restores the old behaviour.
            if (KasadaStealth) await bridge.ApplyStealthAsync(ct: ct).ConfigureAwait(false);

            // Before the first request, so nothing gets pulled and then discarded: the browser drops these
            // itself, and over a metered proxy that is the difference between a few hundred KB and several MB.
            _bridge = bridge;
            if (BlockPatterns.Count == 0 && ReduceTraffic)
                BlockPatterns.AddRange(DefaultBlockPatterns);
            if (BlockPatterns.Count > 0)
                await bridge.BlockAsync(BlockPatterns, ct).ConfigureAwait(false);

            // A kept profile remembers who it was. That identity is still good enough for the site to skip the
            // challenge, which is cheap and yields nothing -- so when the caller wants a token out of a warm
            // profile, the identity has to go while the cache stays.
            if (FreshCookies)
            {
                var origin = Uri.TryCreate(pageUrl, UriKind.Absolute, out var pu)
                    ? pu.GetLeftPart(UriPartial.Authority)
                    : pageUrl;
                // Cookies alone are not always enough: the site also keeps identity in page storage, and one
                // run that cleared only cookies was observed sailing past the challenge with almost nothing on
                // the wire. Clearing both is what makes the round happen every time.
                await bridge.ClearCookiesAsync(origin, ct, includeStorage: true).ConfigureAwait(false);
            }

            await bridge.NavigateAsync(pageUrl, ct).ConfigureAwait(false);

            var deadline = DateTime.UtcNow + limit;
            var sawTl = false;

            // Wait only. The reference implementation's harvest loop does exactly one thing while the page
            // runs -- recv -- and evaluates nothing. Probing a live page every 250 ms is itself a signal and
            // was the one thing this loop did that theirs does not. The token is read afterwards.
            while (DateTime.UtcNow < deadline)
            {
                ct.ThrowIfCancellationRequested();
                if (bridge.FirstTlFinished()) { sawTl = true; break; }
                await Task.Delay(200, ct).ConfigureAwait(false);
            }

            // Captured here, while the profile is still open: both are gone once this method returns.
            var browserNow = await bridge.EvaluateAsync("String(Date.now())", ct).ConfigureAwait(false);
            if (long.TryParse(browserNow, out var parsedNow)) ReceivedAtMs = parsedNow;
            CookieHeader = await bridge.CookieHeaderAsync(ct).ConfigureAwait(false);
            LastRoundtrips = bridge.SniffRoundtrips();

            var sniffed = bridge.SniffKasadaHeaders();
            var tlPair = bridge.SniffRoundtrips()
                .LastOrDefault(rt => rt.Url.Contains("/tl", StringComparison.Ordinal));

            LastRoundtrips = bridge.SniffRoundtrips();
            WireBytes = bridge.WireBytes();
            WireBreakdown = bridge.WireBytesByUrl();
            BlockedRequestCount = bridge.BlockedCount();

            var tlBody = await bridge.ResponseBodyAsync("/tl", ct).ConfigureAwait(false);
            TlBody = tlBody;

            // The accepted round's own headers are the ones that count. A token from an unsolved round is
            // exactly what the handoff pack warns about: lenient endpoints take it, cart.* answers 429.
            var ctToken = tlPair?.ResponseHeaders.GetValueOrDefault("x-kpsdk-ct");
            if (string.IsNullOrEmpty(ctToken) || ctToken!.Length < 8)
                sniffed.TryGetValue("x-kpsdk-ct", out ctToken);
            sniffed.TryGetValue("x-kpsdk-sb", out var sbsd);
            sniffed.TryGetValue("x-kpsdk-v", out var version);

            var sniffedHeaders = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            foreach (var kv in sniffed) sniffedHeaders[kv.Key] = kv.Value;
            if (tlPair is not null)
                foreach (var kv in tlPair.ResponseHeaders) sniffedHeaders["tl:" + kv.Key] = kv.Value;

            // The submission is the gate, not the token count. An empty body is a refusal and a body that is
            // not {"reload":true} is an unusable round; either way the identity must not be reported as usable,
            // because lenient reads accept such a token and cart.* answers 429 with it.
            if (!TlSolved)
            {
                return new KasadaResult
                {
                    Ok = false,
                    ScriptExecuted = true,
                    Version = version,
                    Error = tlBody is null
                        ? "the submission body was unreadable, so the round cannot be counted as solved"
                        : tlBody.Length == 0
                            ? "the submission answered 200 with an empty body (unsolved round)"
                            : "the submission body was not the reload marker",
                };
            }

            if (string.IsNullOrEmpty(ctToken) || ctToken!.Length < 8)
            {
                return new KasadaResult
                {
                    Ok = false,
                    ScriptExecuted = true,
                    Version = version,
                    Error = sawTl
                        ? "the submission finished but stamped no x-kpsdk-ct"
                        : "no submission request appeared within the timeout",
                };
            }

            sbsd ??= await bridge.EvaluateAsync(
                "(document.cookie.match(/(?:^|;\\s*)sbsd=([^;]+)/) || [])[1] || null", ct)
                .ConfigureAwait(false);
            version ??= await bridge.EvaluateAsync(
                "(window.KPSDK && window.KPSDK.v) ? String(window.KPSDK.v) : null", ct)
                .ConfigureAwait(false);
            var usedUserAgent = await bridge.EvaluateAsync("navigator.userAgent", ct)
                .ConfigureAwait(false);

            var result = new KasadaResult
            {
                Ok = true,
                Ct = ctToken,
                Sbsd = sbsd,
                Version = version,
                ScriptExecuted = true,
                ScriptUrl = ScriptUrl,
                UserAgent = usedUserAgent,
                InterrogationBody = tlBody,
            };

            foreach (var kv in sniffedHeaders) result.Headers[kv.Key] = kv.Value;
            result.Headers["x-kpsdk-ct"] = ctToken!;
            if (!string.IsNullOrEmpty(sbsd)) result.Headers["x-kpsdk-sb"] = sbsd!;
            if (!string.IsNullOrEmpty(version)) result.Headers["x-kpsdk-v"] = version!;

            var cookies = await bridge.EvaluateAsync("document.cookie", ct).ConfigureAwait(false);
            if (!string.IsNullOrEmpty(cookies))
            {
                foreach (var part in cookies!.Split(';', StringSplitOptions.RemoveEmptyEntries))
                {
                    var name = part.Split('=')[0].Trim();
                    if (name.StartsWith("kpsdk", StringComparison.OrdinalIgnoreCase) ||
                        name is "ct" or "sbsd" or "cd")
                        result.Cookies.Add(part.Trim());
                }
            }

            // The token is only worth anything against the session that earned it: its cookies, its client
            // hints, its TLS and HTTP/2 fingerprint. All of that disappears when the profile closes, so a
            // caller that wants to spend the token has exactly this window to do it in -- before the return.
            if (AfterSolveAsync is not null)
            {
                try
                {
                    await AfterSolveAsync(bridge, ct).ConfigureAwait(false);
                }
                catch (Exception ex)
                {
                    // A failed follow-up says nothing about the round that just solved, so it must not turn
                    // a good result into a bad one. It is reported separately instead.
                    AfterSolveError = ex.GetType().Name + ": " + ex.Message;
                }
            }

            return result;
        }
        catch (OperationCanceledException)
        {
            return new KasadaResult { Ok = false, NeedsRealBrowser = true, Error = "cancelled" };
        }
        catch (Exception ex)
        {
            return new KasadaResult
            {
                Ok = false,
                NeedsRealBrowser = true,
                Error = "chromium: " + ex.Message,
            };
        }
        finally
        {
            if (bridge is not null) await bridge.DisposeAsync().ConfigureAwait(false);
        }
    }
}
