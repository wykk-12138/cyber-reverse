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
            bridge = await ChromiumBridge.LaunchAsync(ct: ct).ConfigureAwait(false);

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
            await bridge.ApplyStealthAsync(ct: ct).ConfigureAwait(false);
            await bridge.NavigateAsync(pageUrl, ct).ConfigureAwait(false);

            var deadline = DateTime.UtcNow + limit;
            string? ctToken = null;
            string? sbsd = null;
            string? version = null;
            var kpsdkPresent = false;
            var triggered = false;
            var sniffedHeaders = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

            while (DateTime.UtcNow < deadline)
            {
                ct.ThrowIfCancellationRequested();

                var state = await bridge.EvaluateAsync(
                    "typeof window.KPSDK !== 'undefined' ? 'yes' : 'no'", ct).ConfigureAwait(false);

                kpsdkPresent = state == "yes";
                if (!kpsdkPresent)
                {
                    await Task.Delay(250, ct).ConfigureAwait(false);
                    continue;
                }

                // 1) the wire is the reliable source — the page decorates its own requests
                var sniffed = bridge.SniffKasadaHeaders();
                // Both directions, so a caller can show what the server answered -- in particular
                // the /mfc reply whose config decides whether the sensor interrogates at all.
                var replies = bridge.SniffKasadaResponses();
                LastRoundtrips = bridge.SniffRoundtrips();
                if (sniffed.TryGetValue("x-kpsdk-ct", out var hdrCt) && hdrCt.Length > 8)
                {
                    ctToken = hdrCt;
                    sniffed.TryGetValue("x-kpsdk-sb", out sbsd);
                    sniffed.TryGetValue("x-kpsdk-v", out version);

                    // Keep every x-kpsdk-* the request carried: a real checkout needs
                    // h / dt / im / cd as well, and cd is what ciphers the body.
                    foreach (var kv in sniffed) sniffedHeaders[kv.Key] = kv.Value;
                    foreach (var reply in replies)
                        foreach (var kv in reply.Value)
                            sniffedHeaders["response:" + kv.Key] = kv.Value;
                    break;
                }

                // 2) optionally poke a protected endpoint so sb/sbsd has a chance to appear
                if (triggerUrl is not null && !triggered)
                {
                    triggered = true;
                    await bridge.EvaluateAsync(
                        "fetch(" + System.Text.Json.JsonSerializer.Serialize(triggerUrl) +
                        ", { credentials: 'include', headers: { 'accept': 'application/json' } })" +
                        ".then(r => r.status).catch(() => -1)", ct).ConfigureAwait(false);
                }

                // 3) last resort: cookies and the KPSDK object
                foreach (var probe in TokenProbes)
                {
                    var value = await bridge.EvaluateAsync(probe, ct).ConfigureAwait(false);
                    if (!string.IsNullOrWhiteSpace(value) && value!.Length > 8)
                    {
                        ctToken = value;
                        break;
                    }
                }

                if (ctToken is not null) break;

                await Task.Delay(250, ct).ConfigureAwait(false);
            }

            if (ctToken is null)
            {
                var version_ = await bridge.EvaluateAsync(
                    "(window.KPSDK && window.KPSDK.v) ? String(window.KPSDK.v) : null", ct)
                    .ConfigureAwait(false);

                return new KasadaResult
                {
                    Ok = false,
                    ScriptExecuted = kpsdkPresent,
                    NeedsRealBrowser = false,
                    Version = version_,
                    Error = kpsdkPresent
                        ? "KPSDK initialised but exposed no token within the timeout"
                        : "KPSDK never initialised in the browser",
                };
            }

            if (sbsd is null)
            {
                sbsd = await bridge.EvaluateAsync(
                    "(document.cookie.match(/(?:^|;\\s*)sbsd=([^;]+)/) || [])[1] || null", ct)
                    .ConfigureAwait(false);
            }

            if (version is null)
            {
                version = await bridge.EvaluateAsync(
                    "(window.KPSDK && window.KPSDK.v) ? String(window.KPSDK.v) : null", ct)
                    .ConfigureAwait(false);
            }

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
            };

            foreach (var kv in sniffedHeaders) result.Headers[kv.Key] = kv.Value;

            result.Headers["x-kpsdk-ct"] = ctToken;
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
