using System.Text.Json;
using Cybersole.Http;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The Kasada handshake as plain HTTP, with no JavaScript engine and no browser.
/// <para>
/// WHY THIS EXISTS: the sensor is not required to obtain a client token. Measured against the live site
/// (docs/KASADA/11 section 6), a real browser walks four requests in this order:
/// </para>
/// <code>
/// GET  {dir}mfc?                      -> x-kpsdk-fc (config), x-kpsdk-h (config version)
/// GET  {dir}fp?x-kpsdk-v={build}      -> x-kpsdk-ct (first token), x-kpsdk-r (1-AA)
/// GET  {dir}ips.js?KP_UIDz={token}    -> x-kpsdk-ct (the token the protected request actually carries)
/// POST {protected endpoint}           -> carries ct/dt/im/h/v
/// </code>
/// <para>
/// {dir} is the directory the sensor script was served from, which carries two UUID path segments. The
/// bare origin answers 404 there. Nothing in this path needs the payload to run, which is why it is usable
/// from a process that has no browser at all.
/// </para>
/// </summary>
public sealed class KasadaHttpHandshake
{
    private readonly NetClient _http;

    public KasadaHttpHandshake(NetClient http) => _http = http;

    /// <summary>
    /// Optional stand-in for the network, matching KasadaSolver's transport shape. Exists so the hop order
    /// and header plumbing can be pinned in tests without reaching a real host.
    /// </summary>
    public Func<string, string, string, string, string?>? Transport { get; set; }

    /// <summary>Every header value the handshake ends up holding, keyed by the x-kpsdk-* name.</summary>
    public Dictionary<string, string> Headers { get; } = new(StringComparer.OrdinalIgnoreCase);

    /// <summary>The token a protected request should carry.</summary>
    public string? ClientToken { get; private set; }

    /// <summary>
    /// The <c>KP_UIDz-ssn</c> cookie the handshake sets. Measured: the server sends the same value as both
    /// <c>Set-Cookie: KP_UIDz-ssn=...</c> and <c>x-kpsdk-ct</c>, and its CORS exposure list is
    /// <c>x-kpsdk-ct,x-kpsdk-r,x-kpsdk-c,x-kpsdk-h,x-kpsdk-fc</c> -- which is how we know dt, im and st are
    /// computed by the client rather than issued here.
    /// </summary>
    public string? SessionCookie { get; private set; }

    /// <summary>The build the sensor reports, used as x-kpsdk-v.</summary>
    public string Build { get; set; } = KasadaVersions.Observed;

    /// <summary>The directory the sensor was served from, i.e. the handshake root.</summary>
    public string? Root { get; private set; }

    /// <summary>One line per request, in order, for diagnostics.</summary>
    public List<string> Trace { get; } = new();

    public string? Error { get; private set; }

    public bool Ok => !string.IsNullOrEmpty(ClientToken);

    /// <summary>
    /// Walk the handshake. <paramref name="sensorScriptUrl"/> is the p.js / ips.js URL the page loaded;
    /// the handshake root is derived from it, because the UUID segments are part of the address.
    /// </summary>
    public async Task<bool> RunAsync(string sensorScriptUrl, RequestOptions? options = null,
        CancellationToken ct = default)
    {
        Root = KasadaSolver.ResourceAddressOf(sensorScriptUrl);
        if (Root is null)
        {
            Error = "sensor script url is not absolute";
            return false;
        }

        var opts = options?.Clone() ?? new RequestOptions { Timeout = TimeSpan.FromSeconds(20), Retries = 1 };
        opts.Headers["x-kpsdk-v"] = Build;
        // Sent on the very first call. Without it the server answers 304 and hands back no config at all,
        // because an absent h reads as "tell me nothing changed" rather than "I know nothing".
        opts.Headers["x-kpsdk-h"] = "01";

        // 1. config: gives fc (what the sensor is configured with) and h (which config version it holds).
        var mfc = await GetAsync(Root + "mfc", opts, ct).ConfigureAwait(false);
        if (mfc is null) return false;
        Absorb(mfc);
        // The placeholder is deliberate: the server echoes its two-character prefix and appends its own
        // config fingerprint, which is what the later requests are compared against.

        // 2. first token. This is the hop a sensor-driven run never reaches, because the payload is written
        //    to leave it to the page's own frontend code -- see the frontend marker in the /mfc config.
        var fp = await GetAsync(Root + "fp?x-kpsdk-v=" + Uri.EscapeDataString(Build), opts, ct).ConfigureAwait(false);
        if (fp is null) return false;
        Absorb(fp);
        if (!Headers.TryGetValue("x-kpsdk-ct", out var first) || first.Length < 8)
        {
            Error = "/fp did not return a client token";
            return false;
        }
        ClientToken = first;

        // 3. the token that protected requests actually carry. The first one is the KP_UIDz the sensor
        //    script itself is then fetched with, and the reply refreshes it.
        var ips = await GetAsync(Root + "ips.js?KP_UIDz=" + Uri.EscapeDataString(first), opts, ct).ConfigureAwait(false);
        if (ips is not null)
        {
            Absorb(ips);
            if (Headers.TryGetValue("x-kpsdk-ct", out var second) && second.Length > 8) ClientToken = second;
        }

        return Ok;
    }

    private async Task<Dictionary<string, string>?> GetAsync(string url, RequestOptions options,
        CancellationToken ct)
    {
        try
        {
            var status = 200;
            var raw = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

            if (Transport is not null)
            {
                var headersJson = System.Text.Json.JsonSerializer.Serialize(options.Headers);
                var payload = Transport(url, "GET", headersJson, string.Empty);
                if (string.IsNullOrEmpty(payload)) return null;
                using var doc = System.Text.Json.JsonDocument.Parse(payload!);
                var root = doc.RootElement;
                if (root.TryGetProperty("status", out var st)) status = st.GetInt32();
                if (root.TryGetProperty("headers", out var hs))
                    foreach (var h in hs.EnumerateObject())
                        raw[h.Name] = h.Value.GetString() ?? string.Empty;
            }
            else
            {
                var res = await _http.SendAsync(HttpMethod.Get, url, options, ct).ConfigureAwait(false);
                status = res.StatusCode;
                foreach (var h in res.Headers) raw[h.Key] = h.Value;
            }

            Trace.Add($"GET {url} -> {status}");
            if (status is < 200 or >= 300) return null;

            var found = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            foreach (var h in raw)
                if (h.Key.StartsWith("x-kpsdk-", StringComparison.OrdinalIgnoreCase))
                    found[h.Key] = h.Value;

            // The session cookie travels with the token; a request that carries only the header is the
            // shape anti-bot vendors are built to notice.
            if (raw.TryGetValue("Set-Cookie", out var cookie) && cookie.StartsWith("KP_UIDz", StringComparison.Ordinal))
                SessionCookie = cookie.Split(';')[0];
            return found;
        }
        catch (Exception ex) when (ex is not OperationCanceledException and not OutOfMemoryException)
        {
            // A handshake step failing is a result, not a crash: callers fall back to another road.
            Trace.Add($"GET {url} -> failed: {ex.Message}");
            Error = ex.Message;
            return null;
        }
    }

    private void Absorb(Dictionary<string, string> headers)
    {
        foreach (var kv in headers) Headers[kv.Key] = kv.Value;
    }

    /// <summary>Everything a protected request needs, as a plain header dictionary.</summary>
    public Dictionary<string, string> RequestHeaders()
    {
        var copy = new Dictionary<string, string>(Headers, StringComparer.OrdinalIgnoreCase);
        if (!string.IsNullOrEmpty(ClientToken)) copy["x-kpsdk-ct"] = ClientToken!;
        copy["x-kpsdk-v"] = Build;
        if (!string.IsNullOrEmpty(SessionCookie)) copy["Cookie"] = SessionCookie!;
        return copy;
    }

    /// <summary>
    /// The headers a protected request can carry from this path, and the ones it cannot. <c>dt</c> and
    /// <c>im</c> are absent because the server never issues them -- they are computed by the sensor, and
    /// they are not in the endpoint's own CORS exposure list. A caller that needs them needs the sensor to
    /// run, which means a browser or a full payload execution.
    /// </summary>
    public static IReadOnlyList<string> IssuedHeaders { get; } = new[]
    {
        "x-kpsdk-ct", "x-kpsdk-h", "x-kpsdk-fc", "x-kpsdk-r", "x-kpsdk-v",
    };

    /// <summary>Headers a protected request may be checked for that this path cannot produce.</summary>
    public static IReadOnlyList<string> UnavailableHeaders { get; } = new[]
    {
        "x-kpsdk-dt", "x-kpsdk-im", "x-kpsdk-st", "x-kpsdk-cd",
    };
}
