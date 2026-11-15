import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

# The failing expression reads document.documentElement directly. When the navigation is still settling the
# root element can be absent, and a single null there fails the whole measurement for a reason that has nothing
# to do with the pin. Wait for the document, then measure — and say which half is null if it ever is.
old = '''        var ratio = await bridge.EvaluateAsync(
            "JSON.stringify([document.documentElement.clientWidth, window.innerWidth, " +
            "document.documentElement.clientHeight, window.innerHeight])");'''

new = '''        var ratio = await bridge.EvaluateAsync(
            "JSON.stringify((() => {\\n" +
            "  const d = document.documentElement;\\n" +
            "  if (!d) return ['no-documentElement', document.readyState];\\n" +
            "  return [d.clientWidth, window.innerWidth, d.clientHeight, window.innerHeight];\\n" +
            "})())");'''

if old not in t:
    raise SystemExit("ratio expression anchor missing")
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the measurement reports which half is missing")
