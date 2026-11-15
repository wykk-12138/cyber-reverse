import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PatchJournalTests.cs"
t = io.open(p, encoding="utf-8").read()

start = t.find("        // The child document is created asynchronously")
end = t.find("        _out.WriteLine(\"child = \" + probe);")

if start < 0 or end < 0:
    raise SystemExit("probe region missing")

replacement = '''        // The child document is created asynchronously, so the wait happens HERE and the read is synchronous: an
        // async IIFE returns a promise, and the bridge answers the promise object rather than its value (R167's trap).
        await bridge.EvaluateAsync(
            "(() => { const f = document.createElement('iframe'); f.id = 'probe'; " +
            "document.body.appendChild(f); return 'appended'; })()");

        for (var i = 0; i < 100; i++)
        {
            var ready = await bridge.EvaluateAsync(
                "(() => { const f = document.getElementById('probe'); " +
                "return String(!!(f && f.contentDocument && f.contentDocument.readyState === 'complete')); })()");
            if (ready == "true") break;
            await System.Threading.Tasks.Task.Delay(50);
        }

        // and the members live on `w.navigator`, not on `w` — the first version of this probe asked the wrong object
        var probe = await bridge.EvaluateAsync(
            "(() => { const w = document.getElementById('probe').contentWindow; " +
            "return JSON.stringify([navigator.platform, w.navigator.platform, " +
            "navigator.maxTouchPoints, w.navigator.maxTouchPoints, " +
            "typeof w.navigator.canShare, " +
            "Function.prototype.toString.call(w.navigator.canShare).indexOf('[native code]') > 0]); })()");

'''

t = t[:start] + replacement + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the wait moved into C#")
