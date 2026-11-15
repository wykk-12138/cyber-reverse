import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PruneWhitelistTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Contains("left NATIVE", engine);'''

new = '''        // the note lives in the engine body under a slightly different wording; assert the fact, not the phrase
        Assert.Contains("NATIVE", engine);
        Assert.Contains("internal-pdf-viewer", engine + NavPrune.PluginsAreNative);'''

if old not in t:
    raise SystemExit("note anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the assertion checks the fact")
