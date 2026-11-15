import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\GlobalSurfaceTests.cs'
t = io.open(p, encoding='utf-8').read()
old = '''    [Fact]
    public async Task NoNameIsAdvertisedWithoutAProperty()
    {
        var probe = await ProbeAsync(
            "(() => { const names = Object.getOwnPropertyNames(window); " +
            "const phantom = names.filter((n) => !(n in window)); " +
            "const noDescriptor = names.filter((n) => Object.getOwnPropertyDescriptor(window, n) === undefined); " +
            "return JSON.stringify([names.length, phantom.length, phantom.join('|'), " +
            "noDescriptor.length]); })()");

        _out.WriteLine("phantom = " + probe);
        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var r = doc.RootElement;

        Assert.Equal(WindowNameTable.AllCount, r[0].GetInt32());
        Assert.Equal(0, r[1].GetInt32());   // every advertised name is actually in the window
        Assert.Equal(0, r[3].GetInt32());   // and has a descriptor
    }
'''
new = '''    [Fact]
    public async Task NoNameIsAdvertisedWithoutAProperty()
    {
        // R206: the probe now returns the NAMES, not just a count. The count alone said "1062 expected, 1063
        // measured" under load and nothing else, which is not enough to act on — this lists the extra ones.
        var probe = await ProbeAsync(
            "(() => { const names = Object.getOwnPropertyNames(window); " +
            "const phantom = names.filter((n) => !(n in window)); " +
            "const noDescriptor = names.filter((n) => Object.getOwnPropertyDescriptor(window, n) === undefined); " +
            "return JSON.stringify([names, phantom, noDescriptor]); })()");

        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var r = doc.RootElement;

        var names = r[0].EnumerateArray().Select(e => e.GetString()!).ToList();
        var phantom = r[1].EnumerateArray().Select(e => e.GetString()!).ToList();
        var noDescriptor = r[2].EnumerateArray().Select(e => e.GetString()!).ToList();

        var expected = WindowNameTable.All.ToHashSet(System.StringComparer.Ordinal);
        var extra = names.Where(n => !expected.Contains(n)).ToList();
        var missing = expected.Where(n => !names.Contains(n, System.StringComparer.Ordinal)).ToList();

        _out.WriteLine($"own names = {names.Count}, expected = {WindowNameTable.AllCount}");
        _out.WriteLine("extra  = " + string.Join(", ", extra));
        _out.WriteLine("missing= " + string.Join(", ", missing));

        Assert.True(extra.Count == 0 && missing.Count == 0,
            $"window names differ from the table (+{extra.Count} / -{missing.Count}): "
            + "extra[" + string.Join(",", extra) + "] missing[" + string.Join(",", missing) + "]");

        Assert.Equal(0, phantom.Count);      // every advertised name is actually in the window
        Assert.Equal(0, noDescriptor.Count); // and has a descriptor
    }
'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new))
print('patched test')
