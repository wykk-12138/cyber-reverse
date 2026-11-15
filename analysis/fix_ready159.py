import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var bridge = await ChromiumBridge.LaunchAsync(userAgent: userAgent);
        await bridge.ApplyStealthAsync(userAgent);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        return bridge;'''

new = '''        var bridge = await ChromiumBridge.LaunchAsync(userAgent: userAgent);
        await bridge.ApplyStealthAsync(userAgent);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");

        // R159: navigation returns before the document is parsed. Measuring then reads a document that has no
        // root element yet — which is how this round's failure looked ("Cannot read properties of null") and had
        // nothing to do with the pin under test.
        for (var i = 0; i < 100; i++)
        {
            var state = await bridge.EvaluateAsync("document.readyState");
            if (state == "complete") break;
            await Task.Delay(50);
        }

        return bridge;'''

if old not in t:
    raise SystemExit("launch helper anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the harness waits for the document")
