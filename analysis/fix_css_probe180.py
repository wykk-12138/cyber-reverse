import io

# the probe expression had a stray `&&` artefact; keep it simple and synchronous
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\KeyOrderTableTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var css = await bridge.EvaluateAsync(
            "JSON.stringify((() => { const el = document.body; el.style.color = 'red'; " +
            "const k = Object.getOwnPropertyNames(navigator) && " +
            "Object.getOwnPropertyNames(el.style).filter((n) => !/^[0-9]+$/.test(n)); return k.length; })())");'''

new = '''        var css = await bridge.EvaluateAsync(
            "(() => { const el = document.body; el.style.color = 'red'; " +
            "const names = Object.getOwnPropertyNames(el.style); " +
            "return String(names.filter((n) => !/^[0-9]+$/.test(n)).length) + ':' + String(names.length); })()");'''

if old not in t:
    raise SystemExit("css probe anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the css probe is synchronous and simple")
