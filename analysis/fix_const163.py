import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

old = "        const string names = string.Join("
new = "        var names = string.Join("

if old not in t:
    raise SystemExit("const anchor missing")

t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the join is a var, not a const")
