// WHY THIS EXISTS: the xUnit project is temporarily unbuildable (another session is mid-edit on
// PayPalThreeDs: StageInput.Payload was removed and its test not yet updated). This harness references
// only Cybersole.Stores, so the Kasada payload can still be executed and inspected.
//
// What it answers: what the sensor actually exposes after a full run (the real `KPSDK` surface),
// which DOM events it wires and fires, and whether it ever reaches its ready state.
using Cybersole.Stores.Scripts;

var fixture = @"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\fixtures\nike-p.js";
if (!File.Exists(fixture))
{
    Console.WriteLine("fixture missing: " + fixture);
    return 1;
}

var script = File.ReadAllText(fixture);
using var solver = new KasadaSolver(new BrowserShim());
var executed = solver.Runtime.TryExecute(script, out var error);

Console.WriteLine($"executed = {executed}");
Console.WriteLine($"error    = {error}");
Console.WriteLine($"offset   = {solver.Runtime.LastErrorColumn}");
Console.WriteLine();

Console.WriteLine("KPSDK surface:");
Console.WriteLine(solver.Runtime.TryString("""
    (function () {
      var k = window.KPSDK || window._KPSDK || window.kpsdk;
      var out = { found: !!k, keys: [], probes: {} };
      if (!k) {
        out.kpsdkish = [];
        for (var g in window) if (String(g).toLowerCase().indexOf('kpsdk') >= 0) out.kpsdkish.push(String(g));
        return JSON.stringify(out);
      }
      for (var p in k) out.keys.push(String(p) + ':' + typeof k[p]);
      var names = ['ct','cd','sb','sbds','token','clientToken','getCt','getCd','v','version','state'];
      for (var i = 0; i < names.length; i++) {
        var n = names[i];
        if (typeof k[n] === 'function') {
          try { var r = k[n](); out.probes[n] = (r === undefined ? 'undef' : typeof r + ':' + String(r).slice(0, 40)); }
          catch (e) { out.probes[n] = 'threw'; }
        } else if (k[n] !== undefined) {
          out.probes[n] = typeof k[n];
        }
      }
      return JSON.stringify(out);
    })()
    """) ?? "(null)");
Console.WriteLine();

Console.WriteLine("doc events registered = " + (solver.Runtime.TryString("JSON.stringify(Object.keys(window.__dshDocEvents||{}))") ?? "[]"));
Console.WriteLine("doc dispatch log      = " + (solver.Runtime.TryString("JSON.stringify(window.__dshDocDispatched||[])") ?? "[]"));
Console.WriteLine("pending timers        = " + (solver.Runtime.TryString("(window.__dshTimers||[]).length") ?? "0"));
Console.WriteLine("document.cookie       = " + (solver.Runtime.TryString("document.cookie") ?? ""));
Console.WriteLine("__dshCaptured         = " + (solver.Runtime.TryString("JSON.stringify(window.__dshCaptured||{})") ?? "{}"));
Console.WriteLine();

Console.WriteLine("isReady(cb) fires?");
Console.WriteLine(solver.Runtime.TryString("""
    (function () {
      var out = { fired: false };
      try {
        window.KPSDK.isReady(function () { out.fired = true; });
      } catch (e) { out.err = String((e && e.message) || e).slice(0, 60); }
      return JSON.stringify(out);
    })()
    """) ?? "(null)");

return 0;
