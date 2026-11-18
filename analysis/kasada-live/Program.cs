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
    var live = await browser.SolveAsync(pageUrl, TimeSpan.FromSeconds(60));
    Console.WriteLine($"Ok      = {live.Ok}");
    Console.WriteLine($"Ct      = {live.Ct ?? "(null)"}");
    Console.WriteLine($"Version = {live.Version ?? "(null)"}");
    Console.WriteLine($"Error   = {live.Error ?? "-"}");
    foreach (var h in live.Headers.OrderBy(k => k.Key, StringComparer.Ordinal))
        Console.WriteLine($"  {h.Key}: {(h.Value.Length > 70 ? h.Value[..70] + "…" : h.Value)}");
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
