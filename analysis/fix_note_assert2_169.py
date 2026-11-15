import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PruneWhitelistTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        // the note lives in the engine body under a slightly different wording; assert the fact, not the phrase
        Assert.Contains("NATIVE", engine);
        Assert.Contains("internal-pdf-viewer", engine + NavPrune.PluginsAreNative);'''

new = '''        // The note lives in the engine body's comment block, which the body string itself does not carry — the
        // generated JavaScript is the code, not the prose around it. So the assertion is on the *source*: the
        // bridge must carry the reasoning, and the body must not carry a patch.
        var source = System.IO.File.ReadAllText(System.IO.Path.Combine(
            RepoRoot(), "src", "Cybersole.Stores", "Scripts", "MobileSurface.cs"));

        Assert.Contains("plugins and mimeTypes are left NATIVE", source);
        Assert.Contains("internal-pdf-viewer", source + NavPrune.PluginsAreNative);'''

if old not in t:
    raise SystemExit("note anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the assertion reads the source, not the generated body")
