import io

# 1) PayloadCoverageTests: the engine body no longer installs plugins — that is now a recorded fact, not a patch
p1 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PayloadCoverageTests.cs"
t1 = io.open(p1, encoding="utf-8").read()

old1 = '''        foreach (var name in SessionPayload.PluginNames)
            Assert.Contains("'" + name + "'", js);'''

new1 = '''        // R169: the plugin LISTS are left native, so their names no longer appear in the generated body. What the body
        // must still carry is the connection quartet and the two flags.
        Assert.DoesNotContain("PDF Viewer", js);'''

if old1 in t1:
    t1 = t1.replace(old1, new1, 1)

t1 = t1.replace('Assert.Contains("\'internal-pdf-viewer\'", js);\n', "", 1)
io.open(p1, "w", encoding="utf-8", newline="").write(t1)

# 2) NavPruneTests: the mechanism is a whitelist now
p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NavPruneTests.cs"
t2 = io.open(p2, encoding="utf-8").read()

old2 = '''        Assert.Contains("delete G.navigator[name]", js);
        Assert.Contains("delete proto[name]", js);
        Assert.Contains("'connection'", js);
        Assert.DoesNotContain("defineProperty", js);'''

new2 = '''        // R169: whitelist, not blacklist — delete every own name on the prototype that is not kept
        Assert.Contains("Object.getOwnPropertyNames(proto).forEach", js);
        Assert.Contains("delete proto[key]", js);
        Assert.Contains("key !== 'constructor'", js);
        Assert.Contains("'connection'", js);'''

if old2 in t2:
    t2 = t2.replace(old2, new2, 1)

io.open(p2, "w", encoding="utf-8", newline="").write(t2)

# 3) RealmReplayTests counts the patches in the main script; the plugin patch is gone, so the count changes
p3 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\RealmReplayTests.cs"
t3 = io.open(p3, encoding="utf-8").read()
t3 = t3.replace("TheEightOriginalPatchesAreAllStillThere", "TheOriginalPatchesAreAllStillThere", 1)
io.open(p3, "w", encoding="utf-8", newline="").write(t3)

print("three tests follow R169")
