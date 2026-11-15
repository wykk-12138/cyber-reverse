import io

# 1) MaskTargetsTests: two new rows and two new owner expressions
p1 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\MaskTargetsTests.cs"
t1 = io.open(p1, encoding="utf-8").read()

t1 = t1.replace("Assert.Equal(19, MaskTargets.Getters.Count);",
                "Assert.Equal(21, MaskTargets.Getters.Count);", 1)
t1 = t1.replace("Assert.Equal(22, MaskTargets.Count);",
                "Assert.Equal(24, MaskTargets.Count);", 1)
t1 = t1.replace('''                "G.speechSynthesis", "G.Document.prototype", "G.WebGLRenderingContext.prototype",''',
                '''                "G.speechSynthesis", "G.Document.prototype", "G.WebGLRenderingContext.prototype",
                "Object.getPrototypeOf(G.navigator)",''', 1)

io.open(p1, "w", encoding="utf-8", newline="").write(t1)

# 2) NavOrderTests: the reseat measurement now runs after R167 installed two more members, so the count of
#    present names can shift; assert the invariant (relative order) and a floor, not a fixed list order.
p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NavOrderTests.cs"
t2 = io.open(p2, encoding="utf-8").read()

t2 = t2.replace('''        Assert.Contains("maxTouchPoints", achieved);
        Assert.Contains("standalone", achieved);''',
                '''        Assert.Contains("maxTouchPoints", achieved);

        // R167 installs `standalone` and `locks` explicitly, so they are present even where the engine lacked them
        Assert.Contains("standalone", achieved);
        Assert.Contains("locks", achieved);''', 1)

io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("both tests follow R167")
