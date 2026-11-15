import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''            var present = await phone.EvaluateAsync(
                "JSON.stringify((" + names + ").filter((n) => n in navigator))");'''

new = '''            // the list has to be an array literal: `(a, b, c).filter` is a comma expression, not three names
            var present = await phone.EvaluateAsync(
                "JSON.stringify([" + names + "].filter((n) => n in navigator))");'''

if old not in t:
    raise SystemExit("filter anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the name list is an array literal")
