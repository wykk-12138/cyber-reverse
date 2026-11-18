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
    var slice = runtime.TryString(
        $"JSON.stringify((window.__dshSeq||[]).slice({before}, {after}).slice(0, 400))") ?? "[]";
    File.WriteAllText(@"D:\projects\cyber-reverse\.tmp-cfgseq.json", slice);
    Console.WriteLine("configure opcode slice written to .tmp-cfgseq.json");
    // configure may hand its follow-up work to a timer/promise; a browser would run those after the
    // current task, so drain them here before asking whether anything happened.
    var drained = runtime.RunPendingTimers();
    Console.WriteLine($"timers drained after configure = {drained}, left = {runtime.TryString("(window.__dshTimers||[]).length")}");
    Console.WriteLine($"isReady() = {runtime.TryString("String(window.KPSDK.isReady())")}");
    Console.WriteLine($"requests  = {runtime.TryString("JSON.stringify(window.__dshRequests||[])")}");
}

Console.WriteLine();
Console.WriteLine("=== bytecode capture ===");
var head = runtime.TryString("JSON.stringify(((__dshSplices[0]||{}).head)||[])") ?? "[]";
var dec = runtime.DecodedStrings;
File.WriteAllText(@"D:\projects\cyber-reverse\.tmp-cfg2.json",
    "{\"head\":" + head + ",\"decoded\":" + System.Text.Json.JsonSerializer.Serialize(dec) + "}");
Console.WriteLine("headLen=" + head.Length + " decodedLen=" + dec.Length);
return 0;
