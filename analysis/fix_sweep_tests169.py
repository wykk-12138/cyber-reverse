import io

# both tests assert the pre-sweep shape; the body now sweeps through a helper
p1 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NavPruneTests.cs"
t1 = io.open(p1, encoding="utf-8").read()

t1 = t1.replace('''        Assert.Contains("Object.getOwnPropertyNames(proto).forEach", js);
        Assert.Contains("delete proto[key]", js);''',
'''        Assert.Contains("const sweep = (target)", js);
        Assert.Contains("Object.getOwnPropertyNames(target).forEach", js);
        Assert.Contains("delete target[key]", js);''', 1)

io.open(p1, "w", encoding="utf-8", newline="").write(t1)

p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PruneWhitelistTests.cs"
t2 = io.open(p2, encoding="utf-8").read()

t2 = t2.replace('''        Assert.Contains("Object.getOwnPropertyNames(proto).forEach", js);
        Assert.Contains("if (!keep.has(key) && key !== 'constructor')", js);
        Assert.Contains("delete proto[key]", js);''',
'''        Assert.Contains("const sweep = (target)", js);
        Assert.Contains("Object.getOwnPropertyNames(target).forEach", js);
        Assert.Contains("if (!keep.has(key) && key !== 'constructor')", js);
        Assert.Contains("delete target[key]", js);

        // the sweep covers both the prototype and the instance, because this replica's own scripts still put a
        // few members on the instance
        Assert.Contains("sweep(G.Navigator && G.Navigator.prototype);", js);
        Assert.Contains("sweep(G.navigator);", js);''', 1)

io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("both tests follow the sweep")
