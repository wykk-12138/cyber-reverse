import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\AccessorBrandCheckTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Contains("throw new TypeError('Illegal invocation')", js);'''

new = '''        // R175: the throw goes through the stack-eliding helper rather than constructing the error inline
        Assert.Contains("throw illegalInvocation(", js);
        Assert.Contains("'Illegal invocation'", js);'''

if old not in t:
    raise SystemExit("throw anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the assertion follows the helper")
