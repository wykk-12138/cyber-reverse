import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

anchor = '''    /// <summary>A Chromium profile gets an empty function, so the honest counts stay honest.</summary>'''

block = '''    /// <summary>
    /// R161: walk the table in a real browser and ask every masked property what it says.
    ///
    /// <para>
    /// A row that answers source code is a patch announcing itself, so the assertion is per row rather than on a
    /// sample: nineteen getters and three functions, each one asked the same question a detector would ask.
    /// </para>
    /// </summary>
    [Fact]
    public async Task EveryTableRowLooksNative()
    {
        await using var bridge = await LaunchPatchedAsync(IPhoneUserAgent);

        var rows = string.Join(",", MaskTargets.Getters.Select(t => "['" + t.Owner + "','" + t.Property + "']"));
        var funcs = string.Join(",", MaskTargets.Functions.Select(t => "['" + t.Owner + "','" + t.Property + "']"));

        var report = await bridge.EvaluateAsync(
            "JSON.stringify((() => {\\n" +
            "  const out = { getters: [], functions: [] };\\n" +
            "  const say = (fn) => { try { return Function.prototype.toString.call(fn); } catch (e) { return 'err'; } };\\n" +
            "  (" + rows + ").forEach(([ownerExpr, prop]) => {\\n" +
            "    let owner = null;\\n" +
            "    try { owner = eval(ownerExpr); } catch (e) {}\\n" +
            "    const d = owner ? Object.getOwnPropertyDescriptor(owner, prop) : null;\\n" +
            "    out.getters.push([prop, d && d.get ? say(d.get) : 'absent']);\\n" +
            "  });\\n" +
            "  (" + funcs + ").forEach(([ownerExpr, prop]) => {\\n" +
            "    let owner = null;\\n" +
            "    try { owner = eval(ownerExpr); } catch (e) {}\\n" +
            "    const fn = owner ? owner[prop] : null;\\n" +
            "    out.functions.push([prop, typeof fn === 'function' ? say(fn) : 'absent']);\\n" +
            "  });\\n" +
            "  return out;\\n" +
            "})())");

        _out.WriteLine(report!);

        // every getter the table names is masked, or absent because the platform lacks the member
        Assert.NotNull(report);
        var parsed = Newtonsoft.Json.Linq.JObject.Parse(report!);
        foreach (var row in parsed["getters"]!)
        {
            var name = (string)row[0]!;
            var text = (string)row[1]!;
            Assert.True(text == "absent" || text.Contains("native code", System.StringComparison.Ordinal),
                $"{name} answers {text}");
        }

        foreach (var row in parsed["functions"]!)
        {
            var name = (string)row[0]!;
            var text = (string)row[1]!;
            Assert.True(text == "absent" || text.Contains("native code", System.StringComparison.Ordinal),
                $"{name} answers {text}");
        }
    }

    /// <summary>A Chromium profile gets an empty function, so the honest counts stay honest.</summary>'''

if anchor not in t:
    raise SystemExit("runtime anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, block, 1))
print("the runtime test walks the table")
