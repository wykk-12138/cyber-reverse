using System.Text;
using System.Text.RegularExpressions;
using Cybersole.Http;

namespace Cybersole.Stores.Scripts;

/// <summary>Result of one Kasada handshake.</summary>
public sealed class KasadaResult
{
    public bool Ok { get; init; }
    public string? Ct { get; init; }
    public string? Sbsd { get; init; }
    public string? Version { get; init; }
    public string? ScriptUrl { get; init; }

    /// <summary>
    /// The user agent the token was minted under. A request carrying this token has to
    /// present the same UA or the store sees a mismatch and rejects it.
    /// </summary>
    public string? UserAgent { get; init; }
    public string? Error { get; init; }

    /// <summary>True when the payload ran to completion in the JS engine.</summary>
    public bool ScriptExecuted { get; init; }

    /// <summary>Byte offset inside the payload where execution stopped (0 when it finished).</summary>
    public int StoppedAt { get; init; }

    /// <summary>
    /// Set when the payload needs a real browser rather than a JS engine. Kasada's own VM
    /// calls host APIs (worker/promise plumbing) that Jint does not expose, so the generated
    /// token has to come from an embedded Chromium — which is what the original ships.
    /// </summary>
    public bool NeedsRealBrowser { get; init; }

    public List<string> Cookies { get; init; } = new();
    public Dictionary<string, string> Headers { get; } = new(StringComparer.OrdinalIgnoreCase);

    /// <summary>
    /// The <c>x-kpsdk-cd</c> payload as observed on the wire. This is what the original feeds
    /// into its body cipher, so it is worth surfacing rather than leaving buried in Headers.
    /// </summary>
    public string? ClientData => Headers.TryGetValue("x-kpsdk-cd", out var cd) ? cd : null;

    // The live build keeps eight per-handshake fields (recovered as _kasadaCt, _kasadaDt,
    // _kasadaDv, _kasadaFc, _kasadaH, _kasadaIm, _kasadaRst, _kasadaSt, _kasadaWorkTime).
    // Four of those are the x-kpsdk-* headers below; the rest are the handshake's own state.
    // Exposing them all makes the two implementations comparable field for field, which is the
    // point of the parity ledger — whether a particular store needs one of them is decided by
    // that store's gate, not here.
    public string? Dt => Header("x-kpsdk-dt");
    public string? Dv => Header("x-kpsdk-dv");
    public string? Fc => Header("x-kpsdk-fc");
    public string? H => Header("x-kpsdk-h");
    public string? Im => Header("x-kpsdk-im");
    public string? Rst => Header("x-kpsdk-rst");
    public string? St => Header("x-kpsdk-st");

    /// <summary>
    /// Wall-clock milliseconds the payload burned before it produced a token. The live build
    /// tracks the same number (<c>_kasadaWorkTime</c>) because Kasada's gate is sensitive to a
    /// handshake that completes suspiciously fast.
    /// </summary>
    public long WorkTimeMs { get; init; }

    private string? Header(string name) => Headers.TryGetValue(name, out var v) ? v : null;

    /// <summary>Every <c>x-kpsdk-*</c> header the browser emitted, for diagnostics.</summary>
    public IReadOnlyDictionary<string, string> KasadaHeaders =>
        Headers
            .Where(kv => kv.Key.StartsWith("x-kpsdk-", StringComparison.OrdinalIgnoreCase))
            .ToDictionary(kv => kv.Key, kv => kv.Value, StringComparer.OrdinalIgnoreCase);
}

/// <summary>
/// Local Kasada (kpsdk) sensor producer.
///
/// The approach matches the original: pull the store's own <c>ips.js</c>, run it in a
/// sandboxed JS engine with a browser shim, then read the generated client token and
/// body cipher straight out of the script's own public API. No solver service is called,
/// which is why the generated headers are indistinguishable from a real browser's.
///
/// Candidate entry points are probed in order because Kasada renames its exports
/// between builds; the first one that yields a plausibly-shaped token wins.
///
/// Measured against Nike's build (2026): <c>KPSDK</c> exposes only <c>configure</c> and
/// <c>isReady</c> — none of the names below exist. The token is only observable on the wire,
/// which is why <see cref="ChromiumKasadaSolver"/> sniffs request headers instead of probing
/// the object. This class stays for engines that cannot host a browser, and is expected to
/// fail on modern builds.
/// </summary>
public sealed class KasadaSolver : IDisposable
{
    private static readonly string[] CtEntryPoints =
    {
        "KPSDK.ct()",
        "window.KPSDK.ct()",
        "_KPSDK.ct()",
        "KpsdkState.ct()",
        "KPSDK.getCt()",
        "KPSDK.clientToken()",
        "KPSDK.token()",
    };

    private static readonly string[] SbsdEntryPoints =
    {
        "KPSDK.sb()",
        "window.KPSDK.sb()",
        "KPSDK.sbsd()",
        "KPSDK.getSbsd()",
        "KPSDK.state && KPSDK.state.sbsd",
    };

    private static readonly string[] BodyEntryPoints =
    {
        "KPSDK.cd({0})",
        "window.KPSDK.cd({0})",
        "KPSDK.encrypt({0})",
        "KPSDK.enc({0})",
        "_KPSDK.cd({0})",
    };

    public ScriptRuntime Runtime { get; }
    public string? ScriptUrl { get; private set; }
    public string? Version { get; private set; }

    public KasadaSolver(BrowserShim? shim = null, TimeSpan? timeout = null)
        => Runtime = new ScriptRuntime(shim, timeout);

    /// <summary>Pull the ips.js payload for a host. Returns the script text on success.</summary>
    public async Task<(string? Script, string? Url)> FetchScriptAsync(NetClient http, string pageUrl,
        RequestOptions options, CancellationToken ct)
    {
        var page = await http.GetAsync(pageUrl, options, ct).ConfigureAwait(false);
        var found = FindScriptUrl(page.Body, pageUrl);
        if (found is not null)
        {
            var res = await http.GetAsync(found, options, ct).ConfigureAwait(false);
            if (res.IsSuccess && res.Body.Length > 512)
            {
                ScriptUrl = found;
                return (res.Body, found);
            }
        }

        // Fallback: the canonical path some builds serve directly.
        var origin = OriginOf(pageUrl);
        // R200: the two paths come from KasadaApi, where each one carries the address it was read at — the bare
        // form and the id-prefixed form, both with the trailing `?` the image actually writes.
        foreach (var candidate in new[] { origin + KasadaApi.BareScriptPath, origin + KasadaApi.ScriptPath })
        {
            try
            {
                var res = await http.GetAsync(candidate, options, ct).ConfigureAwait(false);
                if (res.IsSuccess && res.Body.Length > 512)
                {
                    ScriptUrl = candidate;
                    return (res.Body, candidate);
                }
            }
            catch (Exception)
            {
                // keep probing
            }
        }

        return (null, null);
    }

    /// <summary>Execute the payload and read back the token that the script generated.</summary>
    /// <summary>
    /// What the sensor is told it is protecting, e.g. <c>https://www.nike.com/</c>. Without it the payload
    /// idles: it appends an iframe and waits for a host configuration it will never receive. With it, it
    /// issues GET {origin}/mfc followed by POST {origin}/r.
    /// </summary>
    public string? ResourceAddress { get; set; }

    /// <summary>
    /// Sends the sensor's own interrogation requests. Arguments are (url, method, headersJson, body) and
    /// the return value is JSON {"status":int,"headers":{...},"body":string}. The clearance token only
    /// exists in the /r response headers and the payload never reads it back, so the host must.
    /// </summary>
    public Func<string, string, string, string, string?>? Transport { get; set; }

    private string? TryConfigure(string resourceAddress)
    {
        Runtime.HttpTransport = Transport;
        var literal = System.Text.Json.JsonSerializer.Serialize(resourceAddress);
        return Runtime.TryString(
            "(function(){try{window.KPSDK.configure({resourceAddress:" + literal +
            "});return 'ok';}catch(e){return 'threw:'+String((e&&e.message)||e);}})()");
    }

    /// <summary>Reads a header off whatever response the transport returned, keyed by containing path.</summary>
    private string? HeaderFromTransport(string header)
    {
        var js = "(function(){var r=window.__dshResponses||{};var k=Object.keys(r);" +
                 "for(var i=k.length-1;i>=0;i--){var h=r[k[i]].headers||{};" +
                 "if(h[" + System.Text.Json.JsonSerializer.Serialize(header) + "])return String(h[" +
                 System.Text.Json.JsonSerializer.Serialize(header) + "]);}return null;})()";
        return Runtime.TryString(js);
    }

    /// <summary>
    /// The production transport: sends the sensor's interrogation through the replica's own HTTP stack, so
    /// the TLS/HTTP-2 fingerprint matches everything else the flow sends. JavaScript cannot await, so the
    /// async send is completed synchronously here -- drive the solver from a thread that may block.
    /// <para>
    /// Everything the payload asked for is honoured (its method, headers and body), because the /r body is
    /// the encoded interrogation and a request that differs from it would not be the one Kasada validated.
    /// </para>
    /// </summary>
    public static Func<string, string, string, string, string?> NetTransport(
        NetClient http, RequestOptions? options = null)
    {
        if (http is null) throw new ArgumentNullException(nameof(http));
        return (url, method, headersJson, body) =>
        {
            var opts = options?.Clone() ?? new RequestOptions();
            foreach (var kv in ParseHeaders(headersJson)) opts.Headers[kv.Key] = kv.Value;

            var verb = string.IsNullOrWhiteSpace(method)
                ? HttpMethod.Get
                : new HttpMethod(method!.Trim().ToUpperInvariant());
            if (!string.IsNullOrEmpty(body))
                opts.Content = new StringContent(body, Encoding.UTF8, new System.Net.Http.Headers.MediaTypeHeaderValue("text/plain"));

            try
            {
                var res = http.SendAsync(verb, url, opts, CancellationToken.None)
                              .ConfigureAwait(false).GetAwaiter().GetResult();
                return System.Text.Json.JsonSerializer.Serialize(new
                {
                    status = res.StatusCode,
                    headers = res.Headers,
                    body = res.Body,
                });
            }
            catch (Exception ex) when (ex is not OutOfMemoryException)
            {
                /* A dead endpoint has to look like a failed request, not like a host fault: the caller is a
                   script engine, and an escaping exception there reads as "this site needs a browser"
                   instead of "that host was unreachable". */
                return System.Text.Json.JsonSerializer.Serialize(new
                {
                    status = 0,
                    headers = new Dictionary<string, string>(),
                    body = "",
                    error = ex.Message,
                });
            }
        };
    }

    private static Dictionary<string, string> ParseHeaders(string headersJson)
    {
        var result = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        if (string.IsNullOrWhiteSpace(headersJson)) return result;
        try
        {
            using var doc = System.Text.Json.JsonDocument.Parse(headersJson);
            if (doc.RootElement.ValueKind != System.Text.Json.JsonValueKind.Object) return result;
            foreach (var p in doc.RootElement.EnumerateObject())
                result[p.Name] = p.Value.ValueKind == System.Text.Json.JsonValueKind.String
                    ? p.Value.GetString() ?? string.Empty
                    : p.Value.ToString();
        }
        catch (System.Text.Json.JsonException)
        {
            // A malformed header bag must not abort an otherwise valid interrogation.
        }
        return result;
    }

    /// <summary>
    /// Whether the sensor is allowed to fetch its remote configuration (<c>GET {origin}/mfc</c>).
    /// This mirrors the original's MfcEnabled switch. Kept true by default because the measured flow
    /// always begins with that call: with it disabled the sensor has no configuration and stops.
    /// </summary>
    public bool MfcEnabled { get; set; } = true;

    /// <summary>
    /// The device value reported as <c>x-kpsdk-dv</c> on the mobile path (the original's MobileDv).
    /// Null leaves it out of the header set, which is what the desktop flow does.
    /// </summary>
    public string? MobileDv { get; set; }

    /// <summary>
    /// Supplies <c>x-kpsdk-v</c>. The original has a VersionProvider switch; the default reads the value
    /// the sensor stamped onto its own interrogation request, which is the only authoritative source.
    /// </summary>
    public Func<string?>? VersionProvider { get; set; }

    /// <summary>
    /// Which store this handshake is for, so the per-store sensor build can be resolved when the sensor's
    /// own request header is not observable. Unset means the shared default.
    /// </summary>
    public string? Store { get; set; }

    /// <summary>Reads a header the sensor put on one of the requests it issued (last one wins).</summary>
    private string? HeaderFromIssuedRequest(string header)
    {
        var js = "(function(){var q=window.__dshRequests||[];" +
                 "for(var i=q.length-1;i>=0;i--){var h=q[i].headers;if(!h)continue;" +
                 "var o=JSON.parse(h);for(var k in o){if(k.toLowerCase()===" +
                 System.Text.Json.JsonSerializer.Serialize(header.ToLowerInvariant()) +
                 ")return String(o[k]);}}return null;})()";
        return Runtime.TryString(js);
    }

    public KasadaResult Solve(string script)
    {
        if (string.IsNullOrWhiteSpace(script))
            return new KasadaResult { Ok = false, Error = "empty kasada script" };

        // The live build times the handshake (_kasadaWorkTime) because Kasada's gate treats a
        // token produced in a few milliseconds as machine-generated. Measuring it here means a
        // caller can pace the handshake the way the original does.
        var clock = System.Diagnostics.Stopwatch.StartNew();

        if (!Runtime.TryExecute(script, out var err))
        {
            var stoppedAt = Runtime.LastErrorLine > 0 ? Runtime.LastErrorColumn : 0;

            // A runtime failure (not a parse failure) means the payload ran and asked for
            // something this engine does not provide. That is exactly the case an embedded
            // Chromium solves, which is how the original does it.
            var needsBrowser = Runtime.LastErrorWasRuntime;

            return new KasadaResult
            {
                Ok = false,
                Error = "script threw: " + err,
                ScriptUrl = ScriptUrl,
                ScriptExecuted = false,
                StoppedAt = stoppedAt,
                NeedsRealBrowser = needsBrowser,
                WorkTimeMs = clock.ElapsedMilliseconds,
            };
        }

        /* Nike's current build exposes only configure/isReady -- there is no ct()/sb() entry point to
           probe (measured: docs/KASADA/11 5.23). What the sensor does instead is *issue* its own
           interrogation: with a resourceAddress it goes GET {origin}/mfc then POST {origin}/r, and the
           clearance token only exists in that /r response. Its state machine settles on "Configured" and
           nothing ever reads the state's .type (5.61), so the host has to send the requests and take the
           token off the reply. That is what ResourceAddress + Transport exist for. */
        // MfcEnabled=false means the sensor must not reach its remote configuration endpoint at all.
        // Refusing it here (rather than after the fact) keeps the host from making the call.
        var priorTransport = Transport;
        if (!MfcEnabled && priorTransport is not null)
        {
            Transport = (url, method, headers, body) =>
                url.EndsWith("/mfc", StringComparison.Ordinal)
                    ? "{\"status\":503,\"headers\":{},\"body\":\"\",\"error\":\"mfc disabled\"}"
                    : priorTransport(url, method, headers, body);
        }

        var configured = string.IsNullOrEmpty(ResourceAddress) ? null : TryConfigure(ResourceAddress!);
        Transport = priorTransport;

        var ct = FirstNonEmpty(CtEntryPoints)
                 ?? HeaderFromTransport("x-kpsdk-ct");
        var sbsd = FirstNonEmpty(SbsdEntryPoints);
        /* The sensor stamps its own build onto the requests it issues (x-kpsdk-v: j-1.2.988 on the /mfc
           call), so that is the authoritative version -- not a guess scraped out of the token. The
           original has a VersionProvider switch for exactly this; a caller may override it. */
        Version = VersionProvider?.Invoke()
                  ?? HeaderFromIssuedRequest("x-kpsdk-v")   // authoritative: what the sensor itself reports
                  ?? KasadaVersions.For(Store)              // per-store table, only when that is unobserved
                  ?? Runtime.TryString("KPSDK && KPSDK.v ? String(KPSDK.v) : (window.KPSDK && window.KPSDK.v ? String(window.KPSDK.v) : null)")
                  ?? Regex.Match(ct ?? string.Empty, @"^\s*(\d+)\|").Groups[1].Value;

        var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        if (!string.IsNullOrEmpty(ct)) headers["x-kpsdk-ct"] = ct!;
        if (!string.IsNullOrEmpty(sbsd)) headers["x-kpsdk-sb"] = sbsd!;
        if (!string.IsNullOrEmpty(Version)) headers["x-kpsdk-v"] = Version!;
        if (!string.IsNullOrEmpty(MobileDv)) headers["x-kpsdk-dv"] = MobileDv!;

        var cookies = Runtime.WrittenCookies;
        foreach (var c in cookies)
        {
            var name = c.Split('=')[0].Trim();
            if (name.StartsWith("kpsdk", StringComparison.OrdinalIgnoreCase) && !headers.ContainsKey("x-" + name))
                headers["x-" + name] = c;
        }

        var result = new KasadaResult
        {
            Ok = !string.IsNullOrEmpty(ct),
            ScriptExecuted = true,
            Ct = ct,
            Sbsd = sbsd,
            Version = Version,
            ScriptUrl = ScriptUrl,
            Cookies = cookies.ToList(),
            WorkTimeMs = clock.ElapsedMilliseconds,
            Error = ct is null ? "no kasada client token exposed by the script" : null,
        };

        foreach (var kv in headers) result.Headers[kv.Key] = kv.Value;
        return result;
    }

    /// <summary>Encrypt a request body with the token the script holds (<c>x-kpsdk-cd</c>).</summary>
    public string? EncryptBody(string jsonBody)
    {
        var quoted = BrowserShim.JsStr(jsonBody);
        foreach (var tpl in BodyEntryPoints)
        {
            var expr = string.Format(tpl, quoted);
            var v = Runtime.TryString(expr);
            if (!string.IsNullOrEmpty(v) && v!.Length > 8) return v;
        }
        return null;
    }

    private string? FirstNonEmpty(IEnumerable<string> candidates)
    {
        foreach (var c in candidates)
        {
            var v = Runtime.TryString(c);
            if (!string.IsNullOrEmpty(v) && v!.Length > 4) return v;
        }
        return null;
    }

    public static string? FindScriptUrl(string html, string pageUrl)
    {
        var origin = OriginOf(pageUrl);
        // Nike serves the same payload as /p.js under two UUID path segments on api.nike.com,
        // so the matcher has to accept both names and cross-origin absolute URLs.
        var m = Regex.Match(html,
            @"<script[^>]+src\s*=\s*[""']([^""']*(?:/tl|ips\.js|p\.js)[^""']*)[""']",
            RegexOptions.IgnoreCase);
        if (m.Success) return Absolute(origin, m.Groups[1].Value);

        m = Regex.Match(html, @"[""'](/[0-9a-f]{8}-[0-9a-f-]{27,}/[0-9a-f-]{27,}/)[""']",
            RegexOptions.IgnoreCase);
        if (m.Success) return Absolute(origin, m.Groups[1].Value);

        m = Regex.Match(html, @"[""'](/[A-Za-z0-9_\-]{8,}/tl)[""']");
        if (m.Success) return Absolute(origin, m.Groups[1].Value);

        return null;
    }

    private static string Absolute(string origin, string path) =>
        path.StartsWith("http", StringComparison.OrdinalIgnoreCase)
            ? path
            : origin + (path.StartsWith('/') ? path : "/" + path);

    private static string OriginOf(string url)
    {
        var u = new Uri(url);
        return u.GetLeftPart(UriPartial.Authority);
    }

    public void Dispose() => Runtime.Dispose();
}
