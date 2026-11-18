// WHY THIS EXISTS: the xUnit project is shared with other sessions and can be mid-edit; this harness
// references only Cybersole.Stores so the Kasada payload can be run and probed independently.
//
// It runs the INSTRUMENTED copy of the payload (analysis/instrument_payload.py) so every dispatch is
// recorded as (pc, opcode). That is what makes `configure`'s 834-opcode detour readable: snapshot the
// dispatch count before and after, then dump the slice in between.
//
// Usage: dotnet exec kasada-probe.dll 'b64:<base64 json config>'
using Cybersole.Stores.Scripts;

var fixtures = @"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\fixtures";
var traced = Path.Combine(fixtures, "nike-p-traced.js");
var plain = Path.Combine(fixtures, "nike-p.js");
var fixture = File.Exists(traced) ? traced : plain;

var config = args.Length > 0
    ? (args[0].StartsWith("b64:", StringComparison.Ordinal)
        ? System.Text.Encoding.UTF8.GetString(Convert.FromBase64String(args[0].Substring(4)))
        : args[0])
    : null;

Console.WriteLine("fixture = " + Path.GetFileName(fixture));

var script = File.ReadAllText(fixture);
using var runtime = new ScriptRuntime(
    new BrowserShim { Href = Environment.GetEnvironmentVariable("KASADA_HREF") ?? "https://www.nike.com/" },
    TimeSpan.FromMinutes(3), 512L << 20);

// Optional stub token: the real clearance token arrives as an x-kpsdk-ct response header, so with no
// live endpoint the only way to see where it gets consumed is to echo one back.
var stubCt = Environment.GetEnvironmentVariable("KASADA_STUB_CT");
if (!string.IsNullOrEmpty(stubCt))
{
    runtime.Execute("window.__dshStubCt = " + System.Text.Json.JsonSerializer.Serialize(stubCt) + ";");
    var stubIc = Environment.GetEnvironmentVariable("KASADA_STUB_IC");
    var stubRc = Environment.GetEnvironmentVariable("KASADA_STUB_RC");
    if (!string.IsNullOrEmpty(stubIc)) runtime.Execute("window.__dshStubIc = " + System.Text.Json.JsonSerializer.Serialize(stubIc) + ";");
    if (!string.IsNullOrEmpty(stubRc)) runtime.Execute("window.__dshStubRc = " + System.Text.Json.JsonSerializer.Serialize(stubRc) + ";");
}

var executed = runtime.TryExecute(script, out var error);
Console.WriteLine($"executed = {executed}  error = {error ?? "-"}");

string SeqLen() => runtime.TryString("(window.__dshSeq||[]).length") ?? "0";

var before = SeqLen();
Console.WriteLine("dispatches after load = " + before);

if (config is not null)
{
    var cfgOk = runtime.TryExecute("window.KPSDK.configure(" + config + ");", out var cfgErr);
    var after = SeqLen();
    Console.WriteLine($"configure ok={cfgOk} err={cfgErr ?? "-"}  dispatches {before} -> {after}");

    // The interesting part: what did configure actually execute?
    // The whole post-load run, not a prefix: the /mfc and /r response handling sits deep inside it.
    var slice = runtime.TryString(
        $"JSON.stringify((window.__dshSeq||[]).slice(0))") ?? "[]";
    File.WriteAllText(@"D:\projects\cyber-reverse\.tmp-cfgseq.json", slice);
    Console.WriteLine("configure opcode slice written to .tmp-cfgseq.json");
    // configure may hand its follow-up work to a timer/promise; a browser would run those after the
    // current task, so drain them here before asking whether anything happened.
    var midSeq = SeqLen();
    var drained = runtime.RunPendingTimers();
    var endSeq = SeqLen();
    Console.WriteLine($"seq lengths: afterLoad={before} afterConfigure={after} afterDrain={midSeq} afterRunTimers={endSeq}");
    // Whatever ran while the stubbed /mfc and /r responses were being consumed is the part that
    // decides whether a token can appear, so keep that slice as well.
    var late = runtime.TryString($"JSON.stringify((window.__dshSeq||[]).slice({after}))") ?? "[]";
    File.WriteAllText(@"D:\projects\cyber-reverse\.tmp-lateseq.json", late);
    Console.WriteLine("post-configure slice written to .tmp-lateseq.json");
    Console.WriteLine($"timers drained after configure = {drained}, left = {runtime.TryString("(window.__dshTimers||[]).length")}");
    Console.WriteLine("stub vars = " + runtime.TryString("String(window.__dshStubCt)+' / '+String(window.__dshStubIc)+' / '+String(window.__dshStubRc)"));
    Console.WriteLine("mfc url seen = " + runtime.TryString("JSON.stringify((window.__dshRequests||[]).map(function(r){return String(r.url)}))"));
    Console.WriteLine($"isReady() = {runtime.TryString("String(window.KPSDK.isReady())")}");
    Console.WriteLine($"requests  = {runtime.TryString("JSON.stringify((window.__dshRequests||[]).map(function(r){{return {{m:r.method,u:r.url,h:r.headers,len:(r.body?String(r.body).length:0)}}}}))")}");
    // The sensor's real output is not a returned string -- it wraps fetch/XHR and injects x-kpsdk-*
    // headers into the page's own requests. So exercise a request through that wrapper and read back
    // what headers actually got attached.
    var probe = runtime.TryExecute("""
        window.__dshRequests.length = 0;
        window.__probeResult = 'pending';
        window.__dshStubCt = window.__dshStubCt || undefined;
        Promise.resolve(fetch('https://www.nike.com/tl', { method: 'POST', body: 'probe=1' }))
          .then(function () { window.__probeResult = 'ok'; },
                function (e) { window.__probeResult = 'rejected'; });
        """, out var probeErr);
    Console.WriteLine($"protected-call issued ok={probe} err={probeErr ?? "-"} result={runtime.TryString("String(window.__probeResult)")}");
    Console.WriteLine($"headers added = {runtime.TryString("JSON.stringify((window.__dshRequests||[])[0]||null)")}");
    Console.WriteLine($"cookie    = {runtime.TryString("document.cookie")}");
    Console.WriteLine($"KPSDK keys= {runtime.TryString("JSON.stringify(Object.keys(window.KPSDK||{}))")}");
    Console.WriteLine($"ct probes = {runtime.TryString("JSON.stringify((function(){var o={};var k=window.KPSDK||{};['ct','cd','sb','v','token'].forEach(function(n){try{o[n]=typeof k[n]+':'+String(k[n]()).slice(0,30)}catch(e){o[n]='-'}});return o})())")}");
}

Console.WriteLine();
Console.WriteLine("=== bytecode capture ===");
var head = runtime.TryString("JSON.stringify(((__dshSplices[0]||{}).head)||[])") ?? "[]";
var dec = runtime.DecodedStrings;
File.WriteAllText(@"D:\projects\cyber-reverse\.tmp-cfg2.json",
    "{\"head\":" + head + ",\"decoded\":" + System.Text.Json.JsonSerializer.Serialize(dec) + "}");
Console.WriteLine("headLen=" + head.Length + " decodedLen=" + dec.Length);
return 0;
