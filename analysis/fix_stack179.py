import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\StackElisionTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var stack = await bridge.EvaluateAsync(
            "(() => { const d = Object.getOwnPropertyDescriptor(Navigator.prototype, 'platform'); " +
            "try { d.get.call({}); return 'no-throw'; } catch (e) { return String(e.stack); } })()");'''

new = '''        // R179 changed the shape as well as the format: JSC's `stack` carries FRAMES ONLY — the message lives on
        // e.message — so both are read here.
        var stack = await bridge.EvaluateAsync(
            "(() => { const d = Object.getOwnPropertyDescriptor(Navigator.prototype, 'platform'); " +
            "try { d.get.call({}); return 'no-throw'; } catch (e) { " +
            "return String(e.message) + ' || ' + String(e.stack); } })()");'''

if old not in t:
    raise SystemExit("stack probe anchor missing")
t = t.replace(old, new, 1)

old2 = '''        var lines = stack!.Split('\\n');
        Assert.Contains("TypeError:", lines[0], System.StringComparison.Ordinal);
        Assert.Contains("getter can only be used on instances of Navigator", lines[0],
            System.StringComparison.Ordinal);'''

new2 = '''        var parts = stack!.Split(" || ");
        Assert.Contains("getter can only be used on instances of Navigator", parts[0],
            System.StringComparison.Ordinal);

        // and the first frame names the accessor, in JSC's `name@location` form
        var firstFrame = parts[1].Split('\\n')[0];
        Assert.Contains("get platform@", firstFrame, System.StringComparison.Ordinal);'''

if old2 not in t:
    raise SystemExit("frame assertion anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old2, new2, 1))
print("the stack test reads message and frames separately")
