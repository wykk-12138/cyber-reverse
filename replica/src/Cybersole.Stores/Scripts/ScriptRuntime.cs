using System.Diagnostics;
using Jint;
using Jint.Native;
using Jint.Runtime;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Sandboxed JS host used to run a store's own anti-bot script in-process.
/// Mirrors what the shipped binary does with Jint 4.17.0 / Acornima 1.7.0:
/// no network round-trip to a third-party solver, the vendor payload is produced locally.
/// </summary>
public sealed class ScriptRuntime : IDisposable
{
    private readonly Engine _engine;
    private readonly Stopwatch _clock = Stopwatch.StartNew();
    public BrowserShim Shim { get; }

    public ScriptRuntime(BrowserShim? shim = null, TimeSpan? timeout = null, long memoryLimit = 64L << 20)
    {
        Shim = shim ?? new BrowserShim();
        _engine = new Engine(o => o
            .Strict(false)
            .TimeoutInterval(timeout ?? TimeSpan.FromSeconds(15))
            .LimitMemory(memoryLimit)
            .MaxStatements(4_000_000));

        _engine.SetValue("__dshNow", new Func<double>(() => _clock.Elapsed.TotalMilliseconds));
        _engine.SetValue("__dshRandom", new Func<int, int[]>(n =>
            BrowserShim.RandomBytes(n).Select(b => (int)b).ToArray()));
        _engine.SetValue("__dshUuid", new Func<string>(BrowserShim.Uuid));
        _engine.SetValue("__dshBtoa", new Func<string, string>(BrowserShim.Btoa));
        _engine.SetValue("__dshAtob", new Func<string, string>(BrowserShim.Atob));

        _engine.Execute(Shim.BuildPrelude());
    }

    public void Execute(string js) => _engine.Execute(js);

    public JsValue Evaluate(string js) => _engine.Evaluate(js);

    /// <summary>Evaluate an expression and coerce to a string, or null when it throws/returns undefined.</summary>
    public string? TryString(string js)
    {
        try
        {
            var v = _engine.Evaluate(js);
            if (v.IsUndefined() || v.IsNull()) return null;
            var s = v.ToString();
            return string.IsNullOrEmpty(s) || s == "undefined" || s == "[object Object]" ? null : s;
        }
        catch (JavaScriptException)
        {
            return null;
        }
        catch (Exception)
        {
            return null;
        }
    }

    public bool TryExecute(string js, out string? error)
    {
        LastErrorWasRuntime = false;
        LastErrorLine = 0;
        LastErrorColumn = 0;
        LastStackTrace = null;

        // Parse first: Jint wraps parser failures in the same exception family as runtime
        // ones, and the two need very different handling — a broken payload is a bug, a
        // missing host function means "go get a browser".
        Jint.Prepared<Acornima.Ast.Script> prepared;
        try
        {
            prepared = Jint.Engine.PrepareScript(js, "payload");
        }
        catch (Exception pex)
        {
            error = "parse: " + pex.Message;
            return false;
        }

        try
        {
            _engine.Evaluate(prepared);
            error = null;
            return true;
        }
        catch (Jint.Runtime.JavaScriptException jex)
        {
            var loc = jex.Location;
            var line = loc.Start.Line;
            var col = loc.Start.Column;

            error = line > 0
                ? $"{jex.Message} @ line {line}, col {col}"
                : jex.Message;
            LastErrorLine = line;
            LastErrorColumn = col;
            LastErrorWasRuntime = true;
            // The message alone says WHAT broke ("undefined.bind"), never WHICH host object was
            // missing at the time. Jint keeps the JS-level stack, and a minified payload's frames
            // are the only way back to the bytecode instruction that asked for it.
            try { LastStackTrace = jex.JavaScriptStackTrace; } catch (Exception) { LastStackTrace = null; }
            return false;
        }
        catch (Exception ex)
        {
            error = ex.Message;
            return false;
        }
    }

    /// <summary>Line of the last script failure, or 0 when it did not come from script code.</summary>
    public int LastErrorLine { get; private set; }

    /// <summary>Column of the last script failure — for a minified payload this is the offset.</summary>
    public int LastErrorColumn { get; private set; }

    /// <summary>
    /// True when the failure came from executing script code (a JavaScriptException) rather
    /// than from parsing it. A runtime failure inside an anti-bot payload almost always means
    /// a host API is missing, which is what an embedded browser would provide.
    /// </summary>
    public bool LastErrorWasRuntime { get; private set; }

    /// <summary>
    /// JS-level stack of the last script failure, when Jint could produce one. A minified payload
    /// reports only a character offset; the frames are what tell us which of its internal calls
    /// was the one that asked for a host object this engine does not have.
    /// </summary>
    public string? LastStackTrace { get; private set; }

    /// <summary>Cookie jar as mutated by the script (document.cookie writes are captured).</summary>
    public IReadOnlyList<string> WrittenCookies
    {
        get
        {
            try
            {
                var arr = _engine.Evaluate(
                    "JSON.stringify(__dshCookieStore.filter(function(x){return x.indexOf('=')>0;}))");
                var json = arr.IsUndefined() ? "[]" : arr.ToString();
                var list = Newtonsoft.Json.JsonConvert.DeserializeObject<List<string>>(json);
                return list ?? new List<string>();
            }
            catch (Exception)
            {
                return Array.Empty<string>();
            }
        }
    }

    public void Dispose() => _engine.Dispose();
}
