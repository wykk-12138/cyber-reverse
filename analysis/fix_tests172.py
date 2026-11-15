import io

# 1) JsGuardTests: twelve bodies now, and the literal-escape rule became a scan
p1 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\JsGuardTests.cs"
t1 = io.open(p1, encoding="utf-8").read()

t1 = t1.replace('Assert.Equal(5, names.Length);', 'Assert.Equal(12, names.Length);', 1)
t1 = t1.replace('''        Assert.Equal(new[] { "WebAssembly", "Mobile", "Engine", "Touches", "WebAssembly wrapper" }, names);''',
'''        Assert.Equal(new[]
        {
            "Mask", "WebAssembly", "Mobile", "Engine", "Touches", "Prune", "AudioSession",
            "Share", "Credentials", "Reseat", "MaskTargets", "WebAssembly wrapper",
        }, names);''', 1)

t1 = t1.replace('''        foreach (var (name, body) in JsGuard.AllBodies())
        {
            Assert.False(body.Contains("\\\\n", System.StringComparison.Ordinal), name);

            // a body that is mostly one line has the same cause
            Assert.True(body.Split('\\n').Length > 3, name);
        }''',
'''        // R172: escapes inside string literals are ordinary JavaScript, so the check is the guard's scan, not a
        // Contains — a body may legitimately answer "{\\n    [native code]\\n}".
        foreach (var (name, body) in JsGuard.AllBodies())
        {
            var problems = JsGuard.Inspect(body);
            Assert.DoesNotContain(problems, p => p.Kind.StartsWith("literal-", System.StringComparison.Ordinal));

            // a body that is mostly one line has the same cause
            Assert.True(body.Split('\\n').Length > 3, name);
        }''', 1)

io.open(p1, "w", encoding="utf-8", newline="").write(t1)

# 2) NativeMaskTests: the text is WebKit's three-line form now
p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NativeMaskTests.cs"
t2 = io.open(p2, encoding="utf-8").read()

t2 = t2.replace('''        Assert.Equal("function getVoices() { [native code] }", NativeMask.NativeText("getVoices"));
        Assert.Equal("function toString() { [native code] }", NativeMask.NativeText("toString"));''',
'''        // R172: WebKit prints natives on three lines, V8 on one — and the profile claims WebKit
        Assert.Equal("function getVoices() {\\n    [native code]\\n}", NativeMask.NativeText("getVoices"));
        Assert.Equal("function toString() {\\n    [native code]\\n}", NativeMask.NativeText("toString"));''', 1)

io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("three tests follow R172")
