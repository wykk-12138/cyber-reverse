import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NavCensusProbe.cs"
t = io.open(p, encoding="utf-8").read()

start = t.find("        var report = await bridge.EvaluateAsync(")
end = t.find("        foreach (var line in report!")

if start < 0 or end < 0:
    raise SystemExit("probe region missing")

replacement = '''        // One line, no escaped newlines: a literal backslash-n outside a string is a SyntaxError, and this
        // workspace has now made that mistake three times (R157, R164, here).
        var report = await bridge.EvaluateAsync(
            "JSON.stringify((() => { " +
            "const proto = Object.getPrototypeOf(navigator); " +
            "const objProto = Object.prototype; " +
            "const own = new Set(Object.getOwnPropertyNames(proto)); " +
            "const objOwn = new Set(Object.getOwnPropertyNames(objProto)); " +
            "const inst = new Set(Object.getOwnPropertyNames(navigator)); " +
            "const out = {}; " +
            "[" + names + "].forEach((n) => { " +
            "out[n] = own.has(n) ? 'proto' : (inst.has(n) ? 'instance' : " +
            "(objOwn.has(n) ? 'object' : (n in navigator ? 'inherited' : 'absent'))); }); " +
            "return out; })())");

'''

t = t[:start] + replacement + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the census probe is one expression")
