using System.Diagnostics;
using System.Security.Cryptography;
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
        // crypto.subtle needs a real digest: the payload's own literal table contains "sha256", and
        // a browser only exposes `subtle` in a secure context, which is exactly the trap noted in
        // the Kasada dossier. Answering with a stub would be worse than answering with nothing,
        // because the payload would carry a wrong hash into its token instead of failing loudly.
        _engine.SetValue("__dshDigest", new Func<string, int[], int[]>(Digest));
        _engine.SetValue("__dshHmac", new Func<string, int[], int[], int[]>(Hmac));

        /* The sensor only ever *issues* its interrogation requests; it never surfaces the clearance token
           itself (its state machine settles on "Configured" and the .type is never read by anything in a
           standalone host -- measured, docs/KASADA/11 5.61). So the host has to send those requests and
           read x-kpsdk-ct off the response. That makes this the seam: the shim's fetch calls this delegate
           and gets back JSON {status, headers, body}. Returns null when no transport is installed, which
           keeps every sandbox-only path offline by default. */
        _engine.SetValue("__dshHttpCall", new Func<string, string, string, string, string?>(CallHttp));

        _engine.Execute(Shim.BuildPrelude());
    }

    /// <summary>
    /// Installed by the caller that owns a real HTTP client. Arguments are (url, method, headersJson, body);
    /// it must return JSON of the form {"status":200,"headers":{...},"body":"..."} or null to stay offline.
    /// </summary>
    public Func<string, string, string, string, string?>? HttpTransport { get; set; }

    private string? CallHttp(string url, string method, string headersJson, string body)
    {
        var transport = HttpTransport;
        if (transport is null) return null;
        try
        {
            return transport(url, method, headersJson, body);
        }
        catch (Exception ex)
        {
            // A transport failure must look like a network failure to the payload, not like a host crash.
            return "{\"status\":0,\"headers\":{},\"body\":\"\",\"error\":"
                + System.Text.Json.JsonSerializer.Serialize(ex.Message) + "}";
        }
    }

    public void Execute(string js) => _engine.Execute(js);

    private static byte[] AsBytes(int[] data)
    {
        var bytes = new byte[data.Length];
        for (var i = 0; i < data.Length; i++) bytes[i] = (byte)(data[i] & 0xFF);
        return bytes;
    }

    private static int[] AsInts(byte[] data)
    {
        var ints = new int[data.Length];
        for (var i = 0; i < data.Length; i++) ints[i] = data[i];
        return ints;
    }

    private static HashAlgorithmName ParseHash(string algorithm)
    {
        var a = algorithm.Replace("-", string.Empty).ToUpperInvariant();
        return a switch
        {
            "SHA1" => HashAlgorithmName.SHA1,
            "SHA256" => HashAlgorithmName.SHA256,
            "SHA384" => HashAlgorithmName.SHA384,
            "SHA512" => HashAlgorithmName.SHA512,
            _ => throw new NotSupportedException("unsupported digest: " + algorithm),
        };
    }

    private static int[] Digest(string algorithm, int[] data)
        => AsInts(HashData(ParseHash(algorithm), AsBytes(data)));

    private static int[] Hmac(string algorithm, int[] key, int[] data)
        => AsInts(HmacData(ParseHash(algorithm), AsBytes(key), AsBytes(data)));

    // The polymorphic HashAlgorithm.HashData only exists from .NET 9; the concrete types have had
    // their own static one since .NET 5/6, so dispatch by name.
    private static byte[] HashData(HashAlgorithmName name, byte[] data) => name.Name switch
    {
        "SHA1" => SHA1.HashData(data),
        "SHA256" => SHA256.HashData(data),
        "SHA384" => SHA384.HashData(data),
        "SHA512" => SHA512.HashData(data),
        _ => throw new NotSupportedException("unsupported digest: " + name.Name),
    };

    private static byte[] HmacData(HashAlgorithmName name, byte[] key, byte[] data) => name.Name switch
    {
        "SHA1" => HMACSHA1.HashData(key, data),
        "SHA256" => HMACSHA256.HashData(key, data),
        "SHA384" => HMACSHA384.HashData(key, data),
        "SHA512" => HMACSHA512.HashData(key, data),
        _ => throw new NotSupportedException("unsupported hmac: " + name.Name),
    };

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
            // The payload schedules its real work on timers; a browser runs them once the current
            // task ends, so do the same instead of leaving the SDK half-initialised.
            RunPendingTimers();
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

    /// <summary>
    /// Run queued promise/timer continuations. Measured on Jint 4.17: <c>Execute</c> already drains
    /// the job queue, so a <c>.then</c> callback has run by the time the call returns
    /// (probe: <c>var d=0; Promise.resolve(7).then(v=>d=v)</c> read back 7 with no drain). Kept for
    /// the case where a caller evaluates several fragments in sequence and wants to settle between
    /// them; it is a no-op otherwise.
    /// </summary>
    public void DrainMicrotasks(int rounds = 8)
    {
        for (var i = 0; i < rounds; i++)
        {
            try
            {
                _engine.Advanced.ProcessTasks();
            }
            catch (JavaScriptException)
            {
                return;
            }
            catch (Exception)
            {
                return;
            }
        }
    }

    /// <summary>
    /// Everything the payload rebuilt through <c>String.fromCharCode</c>, concatenated. The vendor
    /// payload keeps its literals encoded, so this is the only place its real strings (property
    /// names, host-API probes) become visible. Empty unless the diagnostic recorder is installed.
    /// </summary>
    public string DecodedStrings
    {
        get
        {
            try
            {
                return _engine.Evaluate("(__dshDecoded && __dshDecoded.join) ? __dshDecoded.join('') : ''")
                              .ToString() ?? string.Empty;
            }
            catch (Exception)
            {
                return string.Empty;
            }
        }
    }

    /// <summary>
    /// Drain the shim's deferred-task queue. A browser runs timers after the current task completes;
    /// the shim queues them for exactly that reason, so an anti-bot payload's setup finishes before its
    /// own deferred steps run. Bounded, because an uncleared interval would otherwise never end.
    /// </summary>
    public int RunPendingTimers(int maxRuns = 2000)
    {
        try
        {
            var result = _engine.Evaluate($"window.__dshRunTimers ? window.__dshRunTimers({maxRuns}) : 0");
            return result.IsNumber() ? (int)result.AsNumber() : 0;
        }
        catch (Exception)
        {
            return 0;
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
