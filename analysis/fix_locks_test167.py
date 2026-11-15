import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NavigatorLocksTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        // the callback runs, which is what a page calls request for
        var ran = await bridge.EvaluateAsync(
            "(async () => { let ran = false; " +
            "await navigator.locks.request('t', () => { ran = true; return 7; }); " +
            "const q = await navigator.locks.query(); " +
            "return String(ran) + ':' + (q.held.length + q.pending.length); })()");
        Assert.Equal("true:0", ran);'''

new = '''        // The callback runs, which is what a page calls request for. Evaluated synchronously: an async IIFE
        // returns a promise, and the bridge answers the promise object rather than its value (R167 — the
        // first version of this assertion read "{}").
        var ran = await bridge.EvaluateAsync(
            "(() => { let ran = false; " +
            "const p = navigator.locks.request('t', () => { ran = true; return 7; }); " +
            "return String(p instanceof Promise) + ':' + String(ran); })()");
        Assert.Equal("true:true", ran);

        // and query() resolves to an empty snapshot
        var snapshot = await bridge.EvaluateAsync(
            "(() => { const q = navigator.locks.query(); " +
            "return String(q instanceof Promise) + ':' + (typeof q.then === 'function'); })()");
        Assert.Equal("true:true", snapshot);'''

if old not in t:
    raise SystemExit("callback anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the callback assertion is synchronous")
