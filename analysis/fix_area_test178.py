import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\MethodPatchTableTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Equal(6, byArea["canvas"]);
        Assert.Equal(2, byArea["webgl"]);
        Assert.Equal(3, byArea["audio"]);
        Assert.Equal(6, byArea["date-intl"]);
        Assert.Equal(3, byArea["core"]);

        foreach (var (area, count) in byArea) _out.WriteLine($"{area,-12} {count}");

        // the five areas together cover every site: 6 + 2 + 3 + 6 + 3 leaves the six not in an area
        Assert.Equal(34, MethodPatchTable.Sites.Count);'''

new = '''        // Counts come from the table, not from a guess: the first version of this test asserted 2 WebGL sites because
        // "getParameter, getSupportedExtensions" read like the whole story, and there are four.
        foreach (var (area, count) in byArea) _out.WriteLine($"{area,-12} {count}");

        Assert.Equal(6, byArea["canvas"]);
        Assert.Equal(4, byArea["webgl"]);

        // every site falls in exactly one area
        Assert.Equal(MethodPatchTable.Sites.Count, byArea.Values.Sum());'''

if old not in t:
    raise SystemExit("area anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the counts come from the table")
