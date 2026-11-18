// WHY THIS EXISTS: proves the handshake works from a process with no browser and no JavaScript engine.
// This is the road the user needs in other projects, so it is exercised end to end against the live site
// rather than against a fixture.
//
// Usage: dotnet exec kasada-handshake.dll [pageUrl]
using Cybersole.Http;
using Cybersole.Stores.Scripts;

var pageUrl = args.FirstOrDefault() ?? "https://www.nike.com/";
var ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " +
         "Chrome/131.0.0.0 Safari/537.36";

using var http = new NetClient();
var options = new RequestOptions { Timeout = TimeSpan.FromSeconds(25), Retries = 0 };
options.Headers["User-Agent"] = ua;
options.Headers["Referer"] = pageUrl;
options.Headers["Origin"] = KasadaSolver.OriginOf(pageUrl)?.TrimEnd('/') ?? "https://www.nike.com";

Console.WriteLine("page = " + pageUrl);

using var solver = new KasadaSolver(new BrowserShim { Href = pageUrl, UserAgent = ua });
var (_, scriptUrl) = await solver.FetchScriptAsync(http, pageUrl, options, CancellationToken.None);
Console.WriteLine("script url = " + (scriptUrl ?? "(not found)"));

var handshake = new KasadaHttpHandshake(http);
var ok = await handshake.RunAsync(scriptUrl ?? pageUrl, options);

Console.WriteLine();
foreach (var line in handshake.Trace) Console.WriteLine("  " + line);
Console.WriteLine();
Console.WriteLine($"Ok    = {ok}");
Console.WriteLine($"Root  = {handshake.Root ?? "(null)"}");
Console.WriteLine($"Ct    = {handshake.ClientToken ?? "(null)"}");
Console.WriteLine($"Error = {handshake.Error ?? "-"}");
Console.WriteLine($"Cookie = {handshake.SessionCookie ?? "(none)"}");
Console.WriteLine("issued by the server : " + string.Join(", ", KasadaHttpHandshake.IssuedHeaders));
Console.WriteLine("NOT issued (client-side): " + string.Join(", ", KasadaHttpHandshake.UnavailableHeaders));
foreach (var h in handshake.RequestHeaders().OrderBy(k => k.Key, StringComparer.Ordinal))
    Console.WriteLine($"  {h.Key}: {(h.Value.Length > 60 ? h.Value[..60] + "…" : h.Value)}");

return ok ? 0 : 2;
