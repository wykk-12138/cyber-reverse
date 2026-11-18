// WHY THIS EXISTS: the handshake has to be usable in other projects, and the one inside the replica pulls
// in the whole store layer. This file is deliberately self-contained -- System.Net.Http and nothing else --
// so it can be copied into another solution as-is.
//
// What it does, measured against the live site (docs/KASADA/11 sections 6-8):
//
//   GET  {dir}mfc?                    -> x-kpsdk-fc (the sensor's config), x-kpsdk-h (config version)
//   GET  {dir}fp?x-kpsdk-v={build}    -> x-kpsdk-ct (a token), x-kpsdk-r (a continue marker)
//   GET  {dir}ips.js?KP_UIDz={token}  -> x-kpsdk-ct (the token protected requests carry)
//
// {dir} is the directory the sensor script was served from. For Nike that is
// https://api.nike.com/{uuid}/{uuid}/ -- the two UUID segments are part of the address, and the bare origin
// answers 404. Get it from the script URL in the page HTML, not from the origin.
//
// Limits worth knowing before relying on this:
//   * x-kpsdk-dt / x-kpsdk-im / x-kpsdk-st / x-kpsdk-cd are NOT obtainable this way. The endpoint's own
//     Access-Control-Expose-Headers lists ct, r, c, h, fc and omits those, so they are computed client-side
//     by the sensor. If your target checks them, this path is not enough.
//   * The token doubles as the KP_UIDz-ssn cookie; send both.
//   * The server issues a token to any request shape -- a forged KP_UIDz is accepted -- so holding a token
//     proves nothing. Only a gated endpoint can tell you whether it is worth anything. Use ProbeAsync.

using System.Net;
using System.Text.Json;

namespace KasadaStandalone;

/// <summary>The token and the headers that go with it.</summary>
public sealed class KasadaToken
{
    public required string ClientToken { get; init; }
    public required string Build { get; init; }
    public required IReadOnlyDictionary<string, string> Headers { get; init; }

    /// <summary>Call this to put the credentials on a protected request.</summary>
    public void ApplyTo(HttpRequestMessage request)
    {
        foreach (var kv in Headers) request.Headers.TryAddWithoutValidation(kv.Key, kv.Value);
    }
}

/// <summary>What a gated endpoint answered with and without the credentials.</summary>
public sealed record GateResult(int BareStatus, int BareLength, int TokenStatus, int TokenLength)
{
    /// <summary>True when the endpoint answered differently once the token was offered.</summary>
    public bool Gated => BareStatus != TokenStatus || BareLength != TokenLength;

    public override string ToString() =>
        $"bare={BareStatus}({BareLength}b) token={TokenStatus}({TokenLength}b) gated={Gated}";
}

/// <summary>
/// Walks the Kasada handshake with no browser and no JavaScript engine.
/// </summary>
public sealed class KasadaHandshake
{
    private readonly HttpClient _http;

    public KasadaHandshake(HttpClient? http = null) =>
        _http = http ?? new HttpClient(new HttpClientHandler { AutomaticDecompression = DecompressionMethods.All });

    /// <summary>The build to report. Read it from the sensor script name or from the site's own requests.</summary>
    public string Build { get; set; } = "j-1.2.992";

    /// <summary>One line per request, in order. Useful when a site behaves differently than expected.</summary>
    public List<string> Trace { get; } = new();

    /// <summary>
    /// Runs the handshake. <paramref name="sensorScriptUrl"/> is the p.js (or ips.js) URL the page loaded --
    /// the two UUID path segments in it are what makes the endpoints resolve.
    /// </summary>
    public async Task<KasadaToken?> RunAsync(string sensorScriptUrl, CancellationToken ct = default)
    {
        if (!Uri.TryCreate(sensorScriptUrl, UriKind.Absolute, out var scriptUri)) return null;

        var dir = scriptUri.GetLeftPart(UriPartial.Authority) + DirectoryOf(scriptUri.AbsolutePath);
        var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

        // The config hop. h must be present: without it the server answers 304 and returns no config at all,
        // because an absent h reads as "nothing changed" rather than "I know nothing".
        var mfc = await GetAsync(dir + "mfc", new() { ["x-kpsdk-v"] = Build, ["x-kpsdk-h"] = "01" }, ct);
        if (mfc is null) return null;
        Absorb(headers, mfc);

        // The token hop. It issues a token to any request shape, so this cannot fail the way the config hop
        // can -- but it also means success here is not evidence of anything.
        var fp = await GetAsync(dir + "fp?x-kpsdk-v=" + Uri.EscapeDataString(Build), new() { ["x-kpsdk-v"] = Build }, ct);
        if (fp is null) return null;
        Absorb(headers, fp);

        if (!headers.TryGetValue("x-kpsdk-ct", out var first) || first.Length < 8) return null;

        // The token that protected requests actually carry. This one is fetched with the first as KP_UIDz.
        var ips = await GetAsync(dir + "ips.js?KP_UIDz=" + Uri.EscapeDataString(first), new() { ["x-kpsdk-v"] = Build }, ct);
        if (ips is not null) Absorb(headers, ips);

        headers["x-kpsdk-v"] = Build;
        return new KasadaToken
        {
            ClientToken = headers.TryGetValue("x-kpsdk-ct", out var ct2) ? ct2 : first,
            Build = Build,
            Headers = headers,
        };
    }

    /// <summary>
    /// Calls an endpoint twice, once bare and once with the credentials. The difference is the only evidence
    /// that the token is what that endpoint wanted.
    /// </summary>
    public async Task<GateResult> ProbeAsync(string url, KasadaToken token, CancellationToken ct = default)
    {
        var bare = await MeasureAsync(url, null, ct);
        var withToken = await MeasureAsync(url, token, ct);
        return new GateResult(bare.Status, bare.Length, withToken.Status, withToken.Length);
    }

    private async Task<(int Status, int Length)> MeasureAsync(string url, KasadaToken? token, CancellationToken ct)
    {
        try
        {
            using var req = new HttpRequestMessage(HttpMethod.Get, url);
            token?.ApplyTo(req);
            using var res = await _http.SendAsync(req, ct);
            var body = await res.Content.ReadAsStringAsync(ct);
            return ((int)res.StatusCode, body.Length);
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            // A probe that cannot reach the host is a result, not a crash.
            return (0, 0);
        }
    }

    private async Task<Dictionary<string, string>?> GetAsync(string url, Dictionary<string, string> headers,
        CancellationToken ct)
    {
        try
        {
            using var req = new HttpRequestMessage(HttpMethod.Get, url);
            foreach (var kv in headers) req.Headers.TryAddWithoutValidation(kv.Key, kv.Value);

            using var res = await _http.SendAsync(req, ct);
            Trace.Add($"GET {url} -> {(int)res.StatusCode}");
            if (!res.IsSuccessStatusCode) return null;

            var found = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            foreach (var h in res.Headers.Concat(res.Content.Headers))
            {
                if (h.Key.Equals("Set-Cookie", StringComparison.OrdinalIgnoreCase)) continue;
                if (h.Key.StartsWith("x-kpsdk-", StringComparison.OrdinalIgnoreCase))
                    found[h.Key] = string.Join(",", h.Value);
            }

            // The server sets two cookies carrying the same value: KP_UIDz-ssn (HttpOnly; Secure;
            // SameSite=None) and KP_UIDz (HttpOnly). Both, because a request that drops either one is the
            // shape these systems look for.
            var jar = new List<string>();
            foreach (var cookie in res.Headers.TryGetValues("Set-Cookie", out var values) ? values : Array.Empty<string>())
                if (cookie.StartsWith("KP_UIDz", StringComparison.Ordinal))
                    jar.Add(cookie.Split(';')[0]);
            if (jar.Count > 0) found["Cookie"] = string.Join("; ", jar);

            return found;
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            Trace.Add($"GET {url} -> failed: {ex.Message}");
            return null;
        }
    }

    private static string DirectoryOf(string path)
    {
        var slash = path.LastIndexOf('/');
        return slash >= 0 ? path[..(slash + 1)] : "/";
    }

    private static void Absorb(Dictionary<string, string> into, Dictionary<string, string> from)
    {
        foreach (var kv in from) into[kv.Key] = kv.Value;
    }
}
