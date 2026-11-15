import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ParityProbe.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        // run the parity body by hand and report what it changed
        var body = EngineParity.BodyJs();'''

new = '''        // does the plain assignment work at all?
        _out.WriteLine("direct  = " + await bridge.EvaluateAsync(
            "(() => { try { Error.stackTraceLimit = 100; return String(Error.stackTraceLimit); } " +
            "catch (e) { return 'err:' + e.message; } })()"));

        _out.WriteLine("desc    = " + await bridge.EvaluateAsync(
            "JSON.stringify((() => { const d = Object.getOwnPropertyDescriptor(Error, 'stackTraceLimit'); " +
            "return d ? [d.writable, d.configurable, d.value] : 'none'; })())"));

        // run the parity body by hand and report what it changed
        var body = EngineParity.BodyJs();'''

if old not in t:
    raise SystemExit("probe anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("probe extended")
