import io

# the two test fixes: the guard's list, and the prepareStackTrace assertion (a C# doc claim, not JS code)
p1 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\JsGuardTests.cs"
t1 = io.open(p1, encoding="utf-8").read()
t1 = t1.replace("Assert.Equal(12, names.Length);", "Assert.Equal(13, names.Length);", 1)
t1 = t1.replace('"Mask", "WebAssembly", "Mobile"', '"Mask", "Parity", "WebAssembly", "Mobile"', 1)
io.open(p1, "w", encoding="utf-8", newline="").write(t1)

p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\EngineParityTests.cs"
t2 = io.open(p2, encoding="utf-8").read()
t2 = t2.replace('''        // the reason prepareStackTrace is not used
        Assert.Contains("prepareStackTrace", js);''',
'''        // The reason prepareStackTrace is not used lives in the C# documentation, not in the generated code — the
        // body must NOT assign it, because doing so makes `typeof Error.prepareStackTrace` report 'function'.
        Assert.DoesNotContain("prepareStackTrace =", js, System.StringComparison.Ordinal);
        Assert.Contains("prepareStackTrace", EngineParity.Rule + string.Join("", EngineParity.Messages.Keys));''', 1)
io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("both test fixes applied")
