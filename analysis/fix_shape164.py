import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NavigatorPlacementTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Contains("Object.getPrototypeOf(N)", js);
        Assert.Contains("const target = (P && name in P) ? P : N;", js);'''

new = '''        Assert.Contains("Object.getPrototypeOf(N)", js);

        // R164: the first attempt defined on the prototype only, and a defineProperty that the browser accepts
        // and then overrides left `platform` at Win32. The body now tries both targets and verifies by reading
        // back through the instance, which is the only test that cannot be fooled.
        Assert.Contains("const targets = [P, N];", js);
        Assert.Contains("if (N[name] === v) return;", js);'''

if old not in t:
    raise SystemExit("shape anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the shape assertion follows the rewrite")
