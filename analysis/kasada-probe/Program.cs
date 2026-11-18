// WHY THIS EXISTS: the xUnit project is shared with other sessions and can be mid-edit; this harness
// references only Cybersole.Stores so the Kasada payload can be run and probed independently.
//
// The payload's literal table says `configure` takes `{ endpoints: [{domain, path, method, ...}] }` and
// that the SDK waits for a host-supplied configuration before interrogation. This harness feeds one
// candidate configuration per run (one runtime = one `configure` call, the SDK refuses a second) and
// reports what changes: requests, lifecycle events, readiness, cookies.
//
// Usage: dotnet run --project kasada-probe.csproj -- '<config-json>'   (omit for no configuration)
using Cybersole.Stores.Scripts;

var fixture = @"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\fixtures\nike-p.js";
if (!File.Exists(fixture))
{
    Console.WriteLine("fixture missing: " + fixture);
    return 1;
}

// PowerShell strips double quotes when passing arguments to a native exe, which silently turned
// "path":"/tl" into path:/tl and made the parser read /tl as a regex. Base64 sidesteps quoting entirely.
var config = args.Length > 0
    ? (args[0].StartsWith("b64:", StringComparison.Ordinal)
        ? System.Text.Encoding.UTF8.GetString(Convert.FromBase64String(args[0].Substring(4)))
        : args[0])
    : null;
var script = File.ReadAllText(fixture);

// Raised limits on purpose: with a real endpoint the call throws a JS-uncatchable exception, which in
// Jint usually means a statement/time/memory limit rather than a bug in the payload.
using var runtime = new ScriptRuntime(new BrowserShim { Href = Environment.GetEnvironmentVariable("KASADA_HREF") ?? "https://www.nike.com/" }, TimeSpan.FromMinutes(3), 512L << 20);
var executed = runtime.TryExecute(script, out var error);
var solver = new { Runtime = runtime };

Console.WriteLine($"executed = {executed}  error = {error ?? "-"}");
Console.WriteLine($"surface  = {solver.Runtime.TryString("JSON.stringify(Object.keys(window.KPSDK||{}))")}");

if (config is not null)
{
    // `configure` is one-shot: a second call reports "KPSDK has already been configured", so each
    // candidate gets a fresh runtime and this is the only call made.
    // TryExecute surfaces the C#-level exception text; TryString swallows it, and the interesting
    // failures here are Jint exceptions JavaScript cannot catch.
    var before = solver.Runtime.TryString("(window.__dshOpcodes||[]).length") ?? "?";
    var cfgOk = solver.Runtime.TryExecute("window.KPSDK.configure(" + config + ");", out var cfgErr);
    var after = solver.Runtime.TryString("(window.__dshOpcodes||[]).length") ?? "?";
    Console.WriteLine($"opcodes before={before} after={after}  (equal means configure executed no payload bytecode)");
    Console.WriteLine($"configure ok={cfgOk} err={cfgErr ?? "-"} runtimeError={solver.Runtime.LastErrorWasRuntime}");


    var ran = solver.Runtime.RunPendingTimers();

    // isReady.length === 0: it is a boolean getter, not a callback registrar. Ask it, do not hand it a fn.
    Console.WriteLine($"isReady()= {solver.Runtime.TryString("""
        (function () {
          var out = { value: null, type: 'unknown' };
          try { var r = window.KPSDK.isReady(); out.type = typeof r; out.value = String(r); }
          catch (e) { out.err = String((e && e.message) || e).slice(0, 160); }
          return JSON.stringify(out);
        })()
        """)}");
    Console.WriteLine($"timers   = {ran} drained, {solver.Runtime.TryString("(window.__dshTimers||[]).length")} left");
    Console.WriteLine($"requests = {solver.Runtime.TryString("JSON.stringify(window.__dshRequests||[])")}");
    Console.WriteLine($"events   = {solver.Runtime.TryString("JSON.stringify(window.__dshDocDispatched||[])")}");
    Console.WriteLine($"cookie   = {solver.Runtime.TryString("document.cookie")}");
}
else
{
    Console.WriteLine("(no configuration supplied)");
    Console.WriteLine($"events   = {solver.Runtime.TryString("JSON.stringify(window.__dshDocDispatched||[])")}");
    Console.WriteLine($"requests = {solver.Runtime.TryString("JSON.stringify(window.__dshRequests||[])")}");
}

Console.WriteLine();
Console.WriteLine("=== KPSDK deep introspection ===");
Console.WriteLine(solver.Runtime.TryString("""
    (function () {
      var k = window.KPSDK;
      var out = { own: Object.getOwnPropertyNames(k), syms: [], nested: {} };
      try {
        var syms = Object.getOwnPropertySymbols ? Object.getOwnPropertySymbols(k) : [];
        for (var i = 0; i < syms.length; i++) out.syms.push(String(syms[i]));
      } catch (e) { }
      for (var j = 0; j < out.own.length; j++) {
        var n = out.own[j];
        try {
          var v = k[n];
          if (v && typeof v === 'object') {
            var keys = Object.getOwnPropertyNames(v);
            var flat = {};
            for (var m = 0; m < keys.length && m < 40; m++) flat[keys[m]] = typeof v[keys[m]];
            out.nested[n] = flat;
          }
        } catch (e2) { out.nested[n] = 'threw'; }
      }
      out.configureLen = k.configure.length;
      out.isReadyLen = k.isReady.length;
      out.configureName = k.configure.name;
      return JSON.stringify(out, null, 1).slice(0, 2500);
    })()
    """) ?? "(null)");
return 0;
