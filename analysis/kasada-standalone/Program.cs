// Self-check: run the standalone handshake against the live site and report what it produced, then ask a
// few endpoints whether they care. No dependency on the replica.
//
// dotnet run -- [pageUrl] [probeUrl...]
using KasadaStandalone;

var pageUrl = args.FirstOrDefault(a => !a.StartsWith("--")) ?? "https://www.nike.com/";
var probeUrls = args.Where(a => a.StartsWith("http", StringComparison.Ordinal) && a != pageUrl).ToList();
var ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " +
         "Chrome/131.0.0.0 Safari/537.36";

using var http = new HttpClient(new HttpClientHandler { AutomaticDecompression = System.Net.DecompressionMethods.All });
http.DefaultRequestHeaders.TryAddWithoutValidation("User-Agent", ua);

// 1. find the sensor script URL in the page
using var pageReq = new HttpRequestMessage(HttpMethod.Get, pageUrl);
using var pageRes = await http.SendAsync(pageReq);
var html = await pageRes.Content.ReadAsStringAsync();
Console.WriteLine($"page {(int)pageRes.StatusCode} ({html.Length} chars)");

var scriptUrl = FindScriptUrl(html);
if (scriptUrl is null) { Console.WriteLine("no sensor script found"); return 1; }
Console.WriteLine("sensor script = " + scriptUrl);

// 2. walk the handshake
var hs = new KasadaHandshake(http);
var token = await hs.RunAsync(scriptUrl);
foreach (var line in hs.Trace) Console.WriteLine("  " + line);

if (token is null) { Console.WriteLine("handshake failed"); return 2; }

Console.WriteLine();
Console.WriteLine("token = " + token.ClientToken);
Console.WriteLine("build = " + token.Build);
foreach (var kv in token.Headers.OrderBy(k => k.Key, StringComparer.Ordinal))
    Console.WriteLine($"  {kv.Key}: {(kv.Value.Length > 60 ? kv.Value[..60] + "…" : kv.Value)}");

// 3. ask the caller's endpoints whether the token matters there
foreach (var target in probeUrls)
{
    var gate = await hs.ProbeAsync(target, token);
    Console.WriteLine();
    Console.WriteLine("probe " + target);
    Console.WriteLine("  " + gate);
}

return 0;

static string? FindScriptUrl(string html)
{
    // The sensor is served from a path with two UUID segments and is named p.js / ips.js. Taking the whole
    // match matters: the directories above it are the handshake root.
    var m = System.Text.RegularExpressions.Regex.Match(html,
        @"https://[^""'\s]+/[0-9a-f]{8}-[0-9a-f-]{27,}/[0-9a-f-]{27,}/[^""'\s]*\.js");
    return m.Success ? m.Value : null;
}
