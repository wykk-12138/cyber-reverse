// WHY THIS EXISTS: the offline harness can only prove the shape of things. This one runs the whole local
// path against the live site: fetch the real page, find the real sensor URL (which carries two UUID path
// segments), configure the sensor with that directory, and let it issue GET /mfc and POST /r for real.
//
// It is deliberately separate from kasada-probe: that one must stay offline-only so it can run anywhere.
//
// Usage: dotnet exec kasada-live.dll [pageUrl]
using Cybersole.Http;
using Cybersole.Stores.Scripts;

// The default page used to be nike.com, left over from when Nike was the only site with a worked-out sensor.
// Every run that forgot to pass a URL then opened Nike, which is not the site anybody is testing. The
// default is now the Arcteryx product page under study, and the store key that follows it comes from the
// same place, so the two can never disagree again.
var pageUrl = args.FirstOrDefault(a => !a.StartsWith("--"))
              ?? Environment.GetEnvironmentVariable("KASADA_PAGE")
              ?? "https://arcteryx.com/us/en/shop/X000009417";
var storeKey = Environment.GetEnvironmentVariable("KASADA_STORE") ?? "arcteryx";

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
    // A kept profile is the cheapest lever there is: the sensor script alone is about two thirds of the whole
    // harvest, and it does not change between rounds, so on a profile that already has it the network never
    // sees it again. KASADA_PROFILE points at a directory that survives between runs.
    var profileDir = Environment.GetEnvironmentVariable("KASADA_PROFILE");
    if (!string.IsNullOrEmpty(profileDir))
    {
        browser.ProfilePath = profileDir;
        // A warm profile would otherwise sail past the challenge on the identity it remembers, which costs
        // almost nothing and produces no token. FRESH=1 keeps the cached sensor and drops just the identity.
        browser.FreshCookies = Environment.GetEnvironmentVariable("KASADA_FRESH") == "1";
        Console.WriteLine("profile = " + profileDir + (browser.FreshCookies ? "  (cookies cleared)" : ""));
    }
    // Traffic control: a checkout page pulls everything a shopper needs and nothing a sensor does. Over a
    // metered proxy that is the whole bill, so block the categories that cannot matter.
    var blockList = Environment.GetEnvironmentVariable("KASADA_BLOCK");
    if (!string.IsNullOrEmpty(blockList))
    {
        var patterns = blockList.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        foreach (var pattern in patterns) browser.BlockPatterns.Add(pattern);
        Console.WriteLine("blocking " + patterns.Length + " pattern(s): " + string.Join(" ", patterns));
    }

    // Layer two of the verdict -- a gated endpoint -- has to run INSIDE the browser, in the same session,
    // while the profile is still open. Built on the host side it is a different client: no cookies, no
    // client hints, a different TLS and HTTP/2 fingerprint, and a 429 from it says nothing about the token.
    // That was the earlier mistake. So the arms are prepared here and fired from the post-solve hook.
    var cartUrl = Environment.GetEnvironmentVariable("KASADA_CART_URL") ?? "https://arcteryx.com/api/cart.get";
    var cartPath = new Uri(cartUrl).PathAndQuery;
    // The reference body shape: three fields, no id, no token carried inside it.
    //
    // The country code is lower case. Sent as "US" the call comes back invalid_enum_value with the whole
    // option list visible ("at","be","ch","cn","cz","de",...), which is the proof that the request reached
    // the handler and was read: the field was there, only the spelling was wrong. Every arm that failed
    // before this did so for its own reason and none of them indicted the exit node.
    var cartBody = Environment.GetEnvironmentVariable("KASADA_CART_BODY")
                   ?? "{\"country\":\"us\",\"language\":\"en\",\"viewContext\":\"Cart\"}";

    static string CartJs(string cartPath, string cartBody, string headersObject) =>
        "(async()=>{const r=await fetch(" + System.Text.Json.JsonSerializer.Serialize(cartPath)
        + ",{method:'POST',headers:Object.assign({'content-type':'application/json'}," + headersObject + "),"
        + "body:" + System.Text.Json.JsonSerializer.Serialize(cartBody) + ",credentials:'include'});"
        + "const t=await r.text();"
        + "return JSON.stringify({status:r.status,backend:r.headers.get('orig-backend')||'',"
        + "ctype:r.headers.get('content-type')||'',len:t.length,head:t.slice(0,300)});})()";

    // Not every gated path is a POST. cart.get answers a POST with METHOD_NOT_SUPPORTED, which is the
    // application talking, not the WAF -- it calls itself a "query procedure", and queries are read with GET.
    //
    // And the input is not the plain object. A GET carrying the bare object came back with
    //   invalid_type: expected object, received undefined, path []
    // which is what a superjson-style envelope yields when the "json" key it deserialises from is missing:
    // the whole input collapses to undefined before validation ever sees a field. So the query string
    // carries {"json": {...}} -- which is also the exact shape the reference implementation passes.
    static string CartGetJs(string cartPath, string cartInputJson) =>
        "(async()=>{const r=await fetch(" + System.Text.Json.JsonSerializer.Serialize(cartPath)
        + "+'?input='+encodeURIComponent(" + System.Text.Json.JsonSerializer.Serialize(cartInputJson) + "),"
        + "{method:'GET',credentials:'include'});"
        + "const t=await r.text();"
        + "return JSON.stringify({status:r.status,backend:r.headers.get('orig-backend')||'',"
        + "ctype:r.headers.get('content-type')||'',len:t.length,head:t.slice(0,300)});})()";

    var cartInput = "{\"json\":" + cartBody + "}";

    static string Describe(string? json)
    {
        if (string.IsNullOrEmpty(json)) return "(no result)";
        try
        {
            using var doc = System.Text.Json.JsonDocument.Parse(json);
            var r = doc.RootElement;
            var head = r.TryGetProperty("head", out var h0) ? h0.GetString() ?? "" : "";
            return $"status={r.GetProperty("status").GetInt32()} len={r.GetProperty("len").GetInt32()} "
                   + $"backend={(r.TryGetProperty("backend", out var b) ? b.GetString() : "")} "
                   + $"ctype={(r.TryGetProperty("ctype", out var c) ? c.GetString() : "")} "
                   + $"head={Trunc(head, 320)}";
        }
        catch (System.Text.Json.JsonException) { return Trunc(json, 200); }
    }

    // The page is loaded once. Everything after that has to earn its bytes, so the arms below are fired
    // from inside the solved session and measured one by one: how many bytes did this call cost, did the
    // sensor run another round for it, and did the round produce a token that still opens the gate.
    var cartArms = new Dictionary<string, string>(StringComparer.Ordinal);
    var rounds = new List<string>();
    var roundsWanted = int.TryParse(Environment.GetEnvironmentVariable("KASADA_ROUNDS"), out var rn) ? rn : 3;

    browser.AfterSolveAsync = async (b, c) =>
    {
        // G: the method the handler actually declares, carrying the envelope it actually deserialises.
        //    No headers attached -- if the sensor is still live it stamps its own.
        cartArms["G in-page GET {\"json\":...}"] =
            await b.EvaluateAsync(CartGetJs(cartPath, cartInput), c, awaitPromise: true).ConfigureAwait(false)
            ?? "(null)";

        // How much did that one call cost, and did it make the sensor run again?
        var firstBytes = b.WireBytes();
        rounds.Add($"round 0 (page load): {firstBytes:N0} bytes, {b.CompletedTlCount()} submission round(s)");

        // Reuse: a gated call after the first solve either rides the token it already has, or makes the
        // sensor mint another. Both are useful answers, but only one of them costs bytes.
        for (var i = 1; i <= roundsWanted; i++)
        {
            var tlBefore = b.CompletedTlCount();
            var bytesBefore = b.WireBytes();

            var status = await b.EvaluateAsync(CartGetJs(cartPath, cartInput), c, awaitPromise: true)
                                  .ConfigureAwait(false);

            var deadline = DateTime.UtcNow.AddSeconds(15);
            while (DateTime.UtcNow < deadline && b.CompletedTlCount() <= tlBefore)
                await Task.Delay(100, c).ConfigureAwait(false);

            var tlAfter = b.CompletedTlCount();
            var bytesAfter = b.WireBytes();
            var newRounds = tlAfter - tlBefore;
            var body = newRounds > 0 ? await b.ResponseBodyAsync("/tl", c).ConfigureAwait(false) : null;
            var lastTl = b.SniffRoundtrips()
                          .LastOrDefault(r => r.Url.TrimEnd('/').EndsWith("/tl", StringComparison.OrdinalIgnoreCase));
            var ctNow = lastTl?.ResponseHeaders.GetValueOrDefault("x-kpsdk-ct") ?? "";
            var stNow = lastTl?.ResponseHeaders.GetValueOrDefault("x-kpsdk-st") ?? "";

            rounds.Add($"round {i}: +{bytesAfter - bytesBefore,7:N0} bytes, submission +{newRounds}, "
                       + $"ct {Trunc(ctNow, 12)} st {stNow} "
                       + $"body {(body is null ? "(none)" : "[" + Trunc(body, 24) + "]")} "
                       + $"-> {Describe(status)}");
        }
    };

    var live = await browser.SolveAsync(pageUrl, TimeSpan.FromSeconds(60));

    // The full ordered trace: the only way to see which request actually produced the token.
    var trace = browser.LastRoundtrips;
    Console.WriteLine($"roundtrips = {trace.Count}");
    // CDP accounts for what actually crossed the wire; summing per-request response sizes is the closest
    // proxy for proxy traffic that a run can report about itself.
    Console.WriteLine($"wire bytes (CDP loadingFinished) = {browser.WireBytes:N0} across {trace.Count} requests");
    Console.WriteLine($"requests dropped locally = {browser.BlockedRequestCount}");
    Console.WriteLine("largest responses:");
    // The URL is printed whole. Truncating it hid the fact that every sensor request lives under the same
    // two-UUID directory, so their first 95 characters are identical and three different files read as one.
    foreach (var (u, b) in browser.WireBreakdown.Take(12))
        Console.WriteLine($"  {b,10:N0}  {u}");
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
        // Everything the page itself sent to the cart endpoint, with its status and the CD it carried.
        if (rt.Url.Contains("cart.get", StringComparison.Ordinal))
        {
            lines.Add($"      cart.get status={rt.Status} reqbody={rt.RequestBody.Length}b");
            foreach (var h in rt.RequestHeaders.Where(h => h.Key.StartsWith("x-kpsdk-", StringComparison.OrdinalIgnoreCase)))
                lines.Add($"      req {h.Key}: {Trunc(h.Value, 90)}");
            var cd = rt.RequestHeaders.TryGetValue("x-kpsdk-cd", out var cdv) ? cdv : null;
            if (cd is not null) lines.Add($"      CD: {cd}");
        }
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
    // The CD inputs the reference implementation actually needs: a token, a server epoch-ms, and the local
    // time it arrived. fc and the runtime suffix are constants there, not harvested values.
    var tlPair = browser.LastRoundtrips
        .Where(rt => rt.Url.Contains("/tl", StringComparison.Ordinal) && rt.ResponseHeaders.ContainsKey("x-kpsdk-st"))
        .LastOrDefault();
    if (tlPair is not null)
    {
        Console.WriteLine($"tl st = {tlPair.ResponseHeaders["x-kpsdk-st"]}  ct = {Trunc(tlPair.ResponseHeaders.GetValueOrDefault("x-kpsdk-ct", ""), 24)}");
    }
    else
    {
        Console.WriteLine("tl st = (absent from the /tl response headers)");
    }

    Console.WriteLine($"TlSolved = {browser.TlSolved}   TlBody = {(browser.TlBody is null ? "(null)" : browser.TlBody.Length > 40 ? browser.TlBody[..40] + "…" : "[" + browser.TlBody + "]")}");
    Console.WriteLine($"Ok      = {live.Ok}");
    Console.WriteLine($"Ct      = {live.Ct ?? "(null)"}");
    Console.WriteLine($"Version = {live.Version ?? "(null)"}");
    Console.WriteLine($"Error   = {live.Error ?? "-"}");
    foreach (var h in live.Headers.OrderBy(k => k.Key, StringComparer.Ordinal))
        Console.WriteLine($"  {h.Key}: {(h.Value.Length > 70 ? h.Value[..70] + "…" : h.Value)}");

    // The token proving anything requires a gated endpoint. cart.get is the handoff pack's main criterion.
    // Dump the bundle the CD signer needs. Only three values: the token, the server epoch-ms and the local
    // time it arrived. The runtime suffix and the PoW parameters are constants on the reference side.
    var bundlePath = Environment.GetEnvironmentVariable("KASADA_BUNDLE_OUT");
    if (!string.IsNullOrEmpty(bundlePath) && live.Ok)
    {
        var st = tlPair?.ResponseHeaders.GetValueOrDefault("x-kpsdk-st");
        // received_at_ms must be the page's own Date.now() at the moment the reply landed. The server's st is
        // its clock; pairing it with the host clock injects the difference between the two as if it were
        // latency, and the PoW's workTime is derived from exactly that number.

        var bundle = new Dictionary<string, object?>
        {
            ["x-kpsdk-ct"] = live.Ct,
            ["x-kpsdk-st"] = long.TryParse(st, out var stNum) ? stNum : null,
            ["received_at_ms"] = browser.ReceivedAtMs ?? 0,
            ["x-kpsdk-v"] = live.Version,
            ["x-kpsdk-h"] = live.Headers.GetValueOrDefault("x-kpsdk-h"),
            ["user-agent"] = live.UserAgent ?? ChromiumBridge.DefaultUserAgent(),
            ["tl_body"] = browser.TlBody,
            ["cookie"] = browser.CookieHeader,
            ["page_headers"] = browser.RequestHeadersFor("/api/geolocation"),
        };
        File.WriteAllText(bundlePath, System.Text.Json.JsonSerializer.Serialize(bundle, new System.Text.Json.JsonSerializerOptions { WriteIndented = true }));
        Console.WriteLine("bundle -> " + bundlePath);
    }

    // What the page itself got, per API call. A token is only usable if it reproduces one of these.
    Console.WriteLine("page's own /api calls:");
    foreach (var rt in browser.LastRoundtrips.Where(r => r.Url.Contains("/api/", StringComparison.Ordinal)))
        Console.WriteLine($"  {rt.Status,4}  {rt.Method,-4} {Trunc(rt.Url, 78)}");

    // Layer two of the verdict: a gated endpoint. The handoff pack's criterion is cart.get answering 200.
    //
    // WHERE THE REQUEST COMES FROM MATTERS AND THAT WAS THE MISTAKE. The first version of this probe built
    // the request on the host side out of a UA string and a token, which is not the shape the reference
    // implementation uses (docs/KASADA/14 constraint six): there the call carries only ct/h/v plus the
    // user agent and client hints the browser already has, and it rides the browser's own session. A bare
    // host-side request gets judged on everything a real call has and it does not -- cookies, client hints,
    // TLS and HTTP/2 fingerprint, origin, referer -- so a refusal from it says nothing about the token.
    //
    // Three arms, same session, same instant, same network route:
    //   P  in-page fetch WITH the harvested headers  -> the reference shape
    //   N  in-page fetch WITHOUT them                -> negative control; reads are lenient, so this may
    //                                                   pass too, and if it does the token proved nothing
    //   H  host-side request with the same headers    -> the shape that was being misread as a node verdict
    if (live.Ok)
    {
        var ctVal = live.Ct ?? "";
        var hVal = live.Headers.GetValueOrDefault("x-kpsdk-h") ?? "";
        var vVal = live.Headers.GetValueOrDefault("x-kpsdk-v") ?? "";

        var withHeaders = "{"
            + "\"x-kpsdk-ct\":" + System.Text.Json.JsonSerializer.Serialize(ctVal) + ","
            + "\"x-kpsdk-h\":" + System.Text.Json.JsonSerializer.Serialize(hVal) + ","
            + "\"x-kpsdk-v\":" + System.Text.Json.JsonSerializer.Serialize(vVal)
            + "}";

        static string DescribeLocal(string? json) => Describe(json);

        async Task<string?> InPageAsync(string headersObject)
        {
            var js = "(async()=>{const r=await fetch(" + System.Text.Json.JsonSerializer.Serialize(cartPath)
                     + ",{method:'POST',headers:Object.assign({'content-type':'application/json'}," + headersObject + "),"
                     + "body:" + System.Text.Json.JsonSerializer.Serialize(cartBody) + ",credentials:'include'});"
                     + "const t=await r.text();"
                     + "return JSON.stringify({status:r.status,backend:r.headers.get('orig-backend')||'',"
                     + "ctype:r.headers.get('content-type')||'',len:t.length,head:t.slice(0,220)});})()";
            // A page-context call can fail for reasons that have nothing to do with the token -- the document
            // may have navigated, the browser may already be gone. Report that as a result rather than letting
            // it take the whole run down, or the other arms never get to run and the run tells us nothing.
            try
            {
                return await browser.EvaluateAfterRunAsync(js, CancellationToken.None, awaitPromise: true)
                                    .ConfigureAwait(false);
            }
            catch (Exception ex)
            {
                return "{\"status\":-1,\"len\":0,\"head\":" + System.Text.Json.JsonSerializer.Serialize(
                    ex.GetType().Name + ": " + ex.Message) + "}";
            }
        }

        Console.WriteLine();
        Console.WriteLine("--- cart.get, fired inside the solved session ---");
        foreach (var kv in cartArms) Console.WriteLine($"{kv.Key,-32}: " + DescribeLocal(kv.Value));
        if (browser.AfterSolveError is not null)
            Console.WriteLine("post-solve hook failed       : " + browser.AfterSolveError);
        Console.WriteLine();
        Console.WriteLine("--- session reuse: what each further token costs ---");
        foreach (var r in rounds) Console.WriteLine(r);
        Console.WriteLine("H follow-up baseline (after close, same headers, own socket): status="
                          + DescribeLocal(await InPageAsync(withHeaders)));

        using var probeHttp = new NetClient();
        var probeOptions = new RequestOptions { Timeout = TimeSpan.FromSeconds(20), Retries = 0 };
        probeOptions.Headers["User-Agent"] = ChromiumBridge.DefaultUserAgent();
        probeOptions.Headers["Referer"] = pageUrl;
        probeOptions.Headers["Origin"] = KasadaSolver.OriginOf(pageUrl)?.TrimEnd('/') ?? "";
        probeOptions.Headers["Accept"] = "application/json";
        probeOptions.Headers["Content-Type"] = "application/json";
        probeOptions.Content = new StringContent(cartBody, System.Text.Encoding.UTF8, "application/json");
        foreach (var kv in live.Headers.Where(h => h.Key.StartsWith("x-kpsdk-", StringComparison.OrdinalIgnoreCase)))
            probeOptions.Headers[kv.Key] = kv.Value;
        var hostPost = await probeHttp.SendAsync(new HttpMethod("POST"), cartUrl, probeOptions,
                                                 CancellationToken.None).ConfigureAwait(false);
        Console.WriteLine($"H host-side POST    : status={hostPost.StatusCode} len={hostPost.Body.Length} "
                          + $"backend={(hostPost.Headers.TryGetValue("orig-backend", out var ob) ? ob : "")} "
                          + $"head={Trunc(hostPost.Body, 160)}");
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
solver.Store = storeKey;
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
    Store = storeKey,
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

static string Trunc(string v, int n = 60) => v.Length > n ? v[..n] + "…" : v;
