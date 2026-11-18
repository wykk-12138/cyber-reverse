// WHY THIS EXISTS: the offline harness can only prove the shape of things. This one runs the whole local
// path against the live site: fetch the real page, find the real sensor URL (which carries two UUID path
// segments), configure the sensor with that directory, and let it issue GET /mfc and POST /r for real.
//
// It is deliberately separate from kasada-probe: that one must stay offline-only so it can run anywhere.
//
// Usage: dotnet exec kasada-live.dll [pageUrl]
using Cybersole.Http;
using Cybersole.Stores.Scripts;

var pageUrl = args.FirstOrDefault(a => !a.StartsWith("--")) ?? "https://www.nike.com/";

// The browser road: load the real page in the replica's own Chromium and read whatever x-kpsdk-* the
// sensor puts on the wire. This is the road that is expected to produce a token for Nike's current build
// (docs/KASADA/11 5.110), so it is worth being able to run it directly.
if (args.Contains("--browser"))
{
    Console.WriteLine("browser available = " + ChromiumKasadaSolver.IsAvailable);
    if (!ChromiumKasadaSolver.IsAvailable)
    {
        Console.WriteLine("no browser installed; stopping");
        return 1;
    }

    var browser = new ChromiumKasadaSolver();
    // Traffic control: a checkout page pulls everything a shopper needs and nothing a sensor does. Over a
    // metered proxy that is the whole bill, so block the categories that cannot matter.
    var blockList = Environment.GetEnvironmentVariable("KASADA_BLOCK");
    if (!string.IsNullOrEmpty(blockList))
    {
        var patterns = blockList.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        foreach (var pattern in patterns) browser.BlockPatterns.Add(pattern);
        Console.WriteLine("blocking " + patterns.Length + " pattern(s): " + string.Join(" ", patterns));
    }

    var live = await browser.SolveAsync(pageUrl, TimeSpan.FromSeconds(60));

    // The full ordered trace: the only way to see which request actually produced the token.
    var trace = browser.LastRoundtrips;
    Console.WriteLine($"roundtrips = {trace.Count}");
    // CDP accounts for what actually crossed the wire; summing per-request response sizes is the closest
    // proxy for proxy traffic that a run can report about itself.
    Console.WriteLine($"wire bytes (CDP loadingFinished) = {browser.WireBytes:N0} across {trace.Count} requests");
    Console.WriteLine($"requests dropped locally = {browser.BlockedRequestCount}");
    Console.WriteLine("largest responses:");
    foreach (var (u, b) in browser.WireBreakdown.Take(12))
        Console.WriteLine($"  {b,10:N0}  {(u.Length > 95 ? u[..95] : u)}");
    Console.WriteLine($"blocked = {browser.BlockedPatterns.Count} pattern(s)");
    var dumpPath = Environment.GetEnvironmentVariable("KASADA_DUMP_TRACE");
    var lines = new List<string>();
    foreach (var rt in trace)
    {
        // Any request that either carried or received a Kasada header, which is exactly the set that shows
        // where the token is actually used.
        var hit = rt.ResponseHeaders.Keys.Any(k => k.StartsWith("x-kpsdk-", StringComparison.OrdinalIgnoreCase))
                  || rt.RequestHeaders.Keys.Any(k => k.StartsWith("x-kpsdk-", StringComparison.OrdinalIgnoreCase));
        lines.Add($"{(hit ? "** " : "   ")}{rt}");
        if (!hit) continue;
        foreach (var h in rt.RequestHeaders.Where(h => h.Key.StartsWith("x-kpsdk-", StringComparison.OrdinalIgnoreCase)))
            lines.Add($"      req {h.Key}: {Trunc(h.Value)}");
        if (rt.Url.Contains("/tl", StringComparison.Ordinal) && rt.RequestBody.Length > 0)
            lines.Add($"      req body [{rt.RequestBody.Length}b]: {Trunc(rt.RequestBody)}");
        if (rt.Url.Contains("/tl", StringComparison.Ordinal))
            foreach (var h in rt.RequestHeaders.Where(h => !h.Key.StartsWith("x-kpsdk-", StringComparison.OrdinalIgnoreCase)))
                if (h.Key is "content-type" or "accept" or "origin" or "referer" or "content-length")
                    lines.Add($"      req {h.Key}: {Trunc(h.Value)}");
        foreach (var h in rt.ResponseHeaders.Where(h => h.Key.StartsWith("x-kpsdk-", StringComparison.OrdinalIgnoreCase)))
            lines.Add($"      res {h.Key}: {Trunc(h.Value)}");
        if (rt.ResponseHeaders.TryGetValue("content-type", out var ctn)) lines.Add($"      res content-type: {ctn}");
    }
    foreach (var l in lines) Console.WriteLine(l);
    if (!string.IsNullOrEmpty(dumpPath)) File.WriteAllLines(dumpPath, lines);
    Console.WriteLine($"Ok      = {live.Ok}");
    Console.WriteLine($"Ct      = {live.Ct ?? "(null)"}");
    Console.WriteLine($"Version = {live.Version ?? "(null)"}");
    Console.WriteLine($"Error   = {live.Error ?? "-"}");
    foreach (var h in live.Headers.OrderBy(k => k.Key, StringComparer.Ordinal))
        Console.WriteLine($"  {h.Key}: {(h.Value.Length > 70 ? h.Value[..70] + "…" : h.Value)}");

    // The token proving anything requires a gated endpoint. cart.get is the handoff pack's main criterion.
    var cartUrl = Environment.GetEnvironmentVariable("KASADA_CART_URL");
    if (!string.IsNullOrEmpty(cartUrl) && live.Ok)
    {
        using var probeHttp = new NetClient();
        var probeOptions = new RequestOptions { Timeout = TimeSpan.FromSeconds(20), Retries = 0 };
        probeOptions.Headers["User-Agent"] = ChromiumBridge.DefaultUserAgent();
        probeOptions.Headers["Referer"] = pageUrl;
        probeOptions.Headers["Origin"] = KasadaSolver.OriginOf(pageUrl)?.TrimEnd('/') ?? "";
        probeOptions.Headers["Accept"] = "application/json";
        foreach (var kv in live.Headers.Where(h => h.Key.StartsWith("x-kpsdk-", StringComparison.OrdinalIgnoreCase)))
            probeOptions.Headers[kv.Key] = kv.Value;

        // Two calls: one bare, one credentialed. The difference is the only evidence the token mattered.
        var bare = await probeHttp.GetAsync(cartUrl!, new RequestOptions
        {
            Timeout = TimeSpan.FromSeconds(20), Retries = 0,
        }).ConfigureAwait(false);
        var withToken = await probeHttp.GetAsync(cartUrl!, probeOptions).ConfigureAwait(false);
        Console.WriteLine();
        Console.WriteLine($"cart.get bare={bare.StatusCode}({bare.Body.Length}b) token={withToken.StatusCode}({withToken.Body.Length}b)");
    }

    return live.Ok ? 0 : 2;
}

var ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " +
         "Chrome/131.0.0.0 Safari/537.36";

using var http = new NetClient();
var options = new RequestOptions
{
    Timeout = TimeSpan.FromSeconds(25),
    Retries = 0,
};
options.Headers["User-Agent"] = ua;
options.Headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8";
options.Headers["Accept-Language"] = "en-US,en;q=0.9";

Console.WriteLine("page = " + pageUrl);

NetResponse page;
try
{
    page = await http.GetAsync(pageUrl, options);
}
catch (Exception ex)
{
    Console.WriteLine("page fetch failed: " + ex.Message);
    return 1;
}

Console.WriteLine($"page status = {page.StatusCode}  body = {page.Body.Length} chars");
if (page.StatusCode != 200)
{
    Console.WriteLine("page did not load; stopping");
    return 1;
}

// The real sensor URL, with whatever UUID segments the site chose this time.
using var solver = new KasadaSolver(new BrowserShim
{
    Href = pageUrl,
    UserAgent = ua,
    Cookie = string.Join("; ", page.Cookies.Select(c => c.Key + "=" + c.Value)),
});

// Prefer a locally instrumented copy of the same script when one is supplied, so a live run can produce a
// dispatch trace exactly like the offline harness does.
var (script, scriptUrl) = await solver.FetchScriptAsync(http, pageUrl, options, CancellationToken.None);
var tracedPath = Environment.GetEnvironmentVariable("KASADA_TRACED_SCRIPT");
if (!string.IsNullOrEmpty(tracedPath) && File.Exists(tracedPath))
{
    script = File.ReadAllText(tracedPath);
    Console.WriteLine("using traced script: " + tracedPath);
}
Console.WriteLine("script url = " + (scriptUrl ?? "(not found)"));
Console.WriteLine("script     = " + (script?.Length.ToString() ?? "0") + " chars");

var resource = KasadaSolver.ResourceAddressOf(scriptUrl);
Console.WriteLine("resource   = " + (resource ?? "(null)"));
if (script is null || resource is null)
{
    Console.WriteLine("no sensor or no resource address; stopping");
    return 1;
}

Console.WriteLine();
Console.WriteLine("--- running the payload with that resource address ---");

solver.ResourceAddress = resource;
solver.Store = "nike";
var forcedBuild = Environment.GetEnvironmentVariable("KASADA_BUILD");
if (!string.IsNullOrEmpty(forcedBuild)) solver.VersionProvider = () => forcedBuild;

// Walk the handshake first, exactly as the browser does, then hand the answers to the sensor instead of
// letting it ask for them. This mirrors what the original does (docs/KASADA/11 section 10).
if (Environment.GetEnvironmentVariable("KASADA_PRESET") == "1")
{
    var hs = new KasadaHttpHandshake(http);
    var ok = await hs.RunAsync(scriptUrl!, options);
    Console.WriteLine("handshake = " + ok + (ok ? "" : "  (" + hs.Error + ")"));
    foreach (var line in hs.Trace) Console.WriteLine("  " + line);

    if (ok)
    {
        var ctHdr = hs.RequestHeaders();
        // Echo test: stamp an unmistakable value over the real token. If the final result still says the
        // real token, the payload did something with it; if it says this marker, we only read our own
        // input back and the "success" is hollow.
        var echoMarker = Environment.GetEnvironmentVariable("KASADA_ECHO_MARKER");
        if (!string.IsNullOrEmpty(echoMarker)) ctHdr["x-kpsdk-ct"] = echoMarker!;
        solver.PresetResponses["mfc"] = ctHdr;
        solver.PresetResponses["fp"] = ctHdr;
        solver.PresetResponses["ips.js"] = ctHdr;
        Console.WriteLine("preset installed with ct=" + (hs.ClientToken ?? "")[..16] + "...");
    }
}

var seen = new List<string>();
// Isolation switch: answer the sensor with the same shapes the offline stub uses, without touching the
// network. If the sensor then issues POST /r, the difference between the two runs is the response itself
// rather than anything about this harness.
var fakeTransport = Environment.GetEnvironmentVariable("KASADA_FAKE_TRANSPORT") == "1";
if (fakeTransport) Console.WriteLine("fake transport: no network will be used");

solver.Transport = (url, method, headersJson, body) =>
{
    if (fakeTransport)
    {
        seen.Add($"{method} {url} -> 200 (fake)");
        var fh = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        if (url.EndsWith("/mfc", StringComparison.Ordinal))
        {
            fh["x-kpsdk-h"] = "01";
            fh["x-kpsdk-fc"] = Environment.GetEnvironmentVariable("KASADA_FAKE_FC") ?? "1";
        }
        else if (url.EndsWith("/r", StringComparison.Ordinal))
        {
            fh["x-kpsdk-ct"] = "CT-FAKE-TRANSPORT-0123456789";
        }
        return System.Text.Json.JsonSerializer.Serialize(new { status = 200, headers = fh, body = "" });
    }

    // The real send, through the replica's own HTTP stack so the fingerprint matches.
    var opts = options.Clone();
    opts.Timeout = TimeSpan.FromSeconds(25);
    opts.Retries = 0;
    // The live /mfc answers with empty featureFlags to a request that carries none of the page's cookies.
    // A real browser sends them, so send them too.
    foreach (var ck in page.Cookies) opts.Cookies[ck.Key] = ck.Value;
    try
    {
        var parsed = System.Text.Json.JsonDocument.Parse(headersJson);
        foreach (var p in parsed.RootElement.EnumerateObject())
            opts.Headers[p.Name] = p.Value.GetString() ?? string.Empty;
    }
    catch (System.Text.Json.JsonException)
    {
    }

    var verb = new HttpMethod(string.IsNullOrEmpty(method) ? "GET" : method.ToUpperInvariant());
    if (!string.IsNullOrEmpty(body))
        opts.Content = new StringContent(body, System.Text.Encoding.UTF8,
            new System.Net.Http.Headers.MediaTypeHeaderValue("text/plain"));

    var res = http.SendAsync(verb, url, opts, CancellationToken.None)
                  .ConfigureAwait(false).GetAwaiter().GetResult();

    seen.Add($"{verb} {url} -> {res.StatusCode}  bodyLen={res.Body.Length}" +
             (res.Body.Length > 0 ? "  first=" + BitConverter.ToString(System.Text.Encoding.UTF8.GetBytes(res.Body).Take(16).ToArray()) : "") +
             "  ctype=" + (res.Headers.TryGetValue("Content-Type", out var ctyp) ? ctyp : "-"));
    var headers = res.Headers
        .Where(h => h.Key.StartsWith("x-kpsdk-", StringComparison.OrdinalIgnoreCase))
        .ToDictionary(h => h.Key, h => h.Value, StringComparer.OrdinalIgnoreCase);
    headers.TryAdd("content-type-echo", res.Headers.TryGetValue("Content-Type", out var ct) ? ct : "");

    return System.Text.Json.JsonSerializer.Serialize(new
    {
        status = res.StatusCode,
        headers,
        body = res.Body,
    });
};

// A fresh solver for the solve itself: ScriptRuntime measures its timeout from construction, and this
// harness has already spent seconds fetching the page and the script on the same object.
using var solveSolver = new KasadaSolver(new BrowserShim
{
    Href = pageUrl,
    UserAgent = ua,
    Cookie = string.Join("; ", page.Cookies.Select(c => c.Key + "=" + c.Value)),
})
{
    ResourceAddress = resource,
    Store = "nike",
    Transport = solver.Transport,
};

// The preset lives on the solver that actually runs the payload, not the one used for fetching.
foreach (var kv in solver.PresetResponses) solveSolver.PresetResponses[kv.Key] = kv.Value;
// The build override has to reach the instance that actually runs, same as the presets.
if (solver.VersionProvider is not null) solveSolver.VersionProvider = solver.VersionProvider;

var result = await Task.Run(() => solveSolver.Solve(script));
solver.ResourceAddress = resource;

Console.WriteLine();
foreach (var line in seen) Console.WriteLine("  " + line);

Console.WriteLine();
Console.WriteLine($"Ok          = {result.Ok}");
Console.WriteLine($"Ct          = {result.Ct ?? "(null)"}");
Console.WriteLine($"Version     = {result.Version ?? "(null)"}");
Console.WriteLine($"Body     len= {result.InterrogationBody?.Length.ToString() ?? "0"}");
Console.WriteLine($"Error       = {result.Error ?? "-"}");
var seqLen = solver.Runtime.TryString("(window.__dshSeq||[]).length");
Console.WriteLine("dispatch count = " + seqLen);
var seqJson = solver.Runtime.TryString("JSON.stringify((window.__dshSeq||[]))");
if (!string.IsNullOrEmpty(seqJson))
    File.WriteAllText(@"D:\projects\cyber-reverse\.tmp-live-seq.json", seqJson);

Console.WriteLine("headers the host would send:");
foreach (var h in result.Headers.OrderBy(k => k.Key, StringComparer.Ordinal))
    Console.WriteLine($"  {h.Key}: {(h.Value.Length > 60 ? h.Value[..60] + "…" : h.Value)}");

return result.Ok ? 0 : 2;

static string Trunc(string v) => v.Length > 60 ? v[..60] + "…" : v;
