import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PatchJournalTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var probe = await bridge.EvaluateAsync(
            "(() => { const f = document.createElement('iframe'); document.body.appendChild(f); " +
            "const w = f.contentWindow; " +
            "return JSON.stringify([navigator.platform, w.navigator.platform, " +
            "navigator.maxTouchPoints, w.navigator.maxTouchPoints, " +
            "typeof w.canShare, nav = null]); })()");

        _out.WriteLine("child = " + probe);
        Assert.Contains("[\\"iPhone\\",\\"iPhone\\"", probe!, System.StringComparison.Ordinal);'''

new = '''        // The child document is created asynchronously, so the read waits for its load; and the members live on
        // `w.navigator`, not on `w` — the first version of this probe asked the wrong object and saw `undefined`.
        var probe = await bridge.EvaluateAsync(
            "(async () => { const f = document.createElement('iframe'); document.body.appendChild(f); " +
            "await new Promise((r) => { if (f.contentDocument && f.contentDocument.readyState === 'complete') r(); " +
            "else f.onload = r; }); " +
            "const w = f.contentWindow; " +
            "return JSON.stringify([navigator.platform, w.navigator.platform, " +
            "navigator.maxTouchPoints, w.navigator.maxTouchPoints, " +
            "typeof w.navigator.canShare, " +
            "Function.prototype.toString.call(w.navigator.canShare).indexOf('[native code]') > 0]); })()");

        _out.WriteLine("child = " + probe);
        Assert.Contains("[\\"iPhone\\",\\"iPhone\\",5,5,\\"function\\",true]", probe!, System.StringComparison.Ordinal);'''

if old not in t:
    raise SystemExit("probe anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the child probe reads the right object and waits for load")
