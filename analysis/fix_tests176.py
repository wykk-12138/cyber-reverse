import io

# R176 replaced the invented frame with an honest elision, so the two tests that asserted the invented frame
# must follow the capture.
p1 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\StackElisionTests.cs"
t1 = io.open(p1, encoding="utf-8").read()

t1 = t1.replace('''        Assert.Contains("nativeCapture(err, getter)", js);
        Assert.Contains("'    at get ' + name + ' (native)'", js);
        Assert.Contains("throw illegalInvocation(", js);''',
'''        Assert.Contains("ELIDE = [getter, '']", js);
        Assert.Contains("finally { ELIDE = null; }", js);
        Assert.Contains("throw new TypeError('The ' + label + '.' + name", js);''', 1)

t1 = t1.replace('''        var captureIndex = js.IndexOf("const nativeCapture", System.StringComparison.Ordinal);
        var throwIndex = js.IndexOf("throw illegalInvocation", System.StringComparison.Ordinal);''',
'''        var captureIndex = js.IndexOf("const nativeCapture", System.StringComparison.Ordinal);
        var throwIndex = js.IndexOf("throw new TypeError('The '", System.StringComparison.Ordinal);''', 1)

t1 = t1.replace('''        Assert.Contains("Illegal invocation", stack!, System.StringComparison.Ordinal);
        Assert.Contains("at get platform (native)", stack, System.StringComparison.Ordinal);''',
'''        // R176: WebKit's sentence, not Blink's, and NO invented frame — the capture says inventing one is a guess
        Assert.Contains("getter can only be used on instances of Navigator", stack!, System.StringComparison.Ordinal);
        Assert.DoesNotContain("(native)", stack, System.StringComparison.Ordinal);''', 1)

t1 = t1.replace('''        var lines = stack!.Split('\\n');
        Assert.Contains("Illegal invocation", lines[0], System.StringComparison.Ordinal);
        Assert.Contains("at get platform (native)", lines[1], System.StringComparison.Ordinal);''',
'''        var lines = stack!.Split('\\n');
        Assert.Contains("TypeError:", lines[0], System.StringComparison.Ordinal);
        Assert.Contains("getter can only be used on instances of Navigator", lines[0],
            System.StringComparison.Ordinal);''', 1)

io.open(p1, "w", encoding="utf-8", newline="").write(t1)

# and the brand-check test's throw assertion
p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\AccessorBrandCheckTests.cs"
t2 = io.open(p2, encoding="utf-8").read()

t2 = t2.replace('''        // R175: the throw goes through the stack-eliding helper rather than constructing the error inline
        Assert.Contains("throw illegalInvocation(", js);
        Assert.Contains("'Illegal invocation'", js);''',
'''        // R176: WebKit's sentence, with the label taken from the target rather than hard-coded
        Assert.Contains("+ ' getter can only be used on instances of ' + label", js);
        Assert.DoesNotContain("'Illegal invocation'", js);''', 1)

io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("both tests follow R176")
