import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

anchor = '''    /// <summary>A Chromium profile gets an empty function, so the honest counts stay honest.</summary>'''

block = '''    /// <summary>
    /// R162: the name and arity of every masked function, read the way a detector reads them.
    /// </summary>
    [Fact]
    public async Task EveryMaskedFunctionCarriesThePlatformsNameAndArity()
    {
        await using var bridge = await LaunchPatchedAsync(IPhoneUserAgent);

        var rows = string.Join(",", MaskTargets.Functions.Select(t => "['" + t.Owner + "','" + t.Property + "']"));

        var report = await bridge.EvaluateAsync(
            "JSON.stringify((() => {\\n" +
            "  const out = [];\\n" +
            "  (" + rows + ").forEach(([ownerExpr, prop]) => {\\n" +
            "    let owner = null;\\n" +
            "    try { owner = eval(ownerExpr); } catch (e) {}\\n" +
            "    const fn = owner ? owner[prop] : null;\\n" +
            "    out.push([prop, typeof fn === 'function' ? fn.name : 'absent',\\n" +
            "              typeof fn === 'function' ? fn.length : -1]);\\n" +
            "  });\\n" +
            "  // a getter answers name 'get <prop>' and length 0\\n" +
            "  const d = Object.getOwnPropertyDescriptor(navigator, 'plugins');\\n" +
            "  out.push(['get plugins', d && d.get ? d.get.name : 'absent', d && d.get ? d.get.length : -1]);\\n" +
            "  return out;\\n" +
            "})())");

        _out.WriteLine(report!);

        var parsed = Newtonsoft.Json.Linq.JArray.Parse(report!);
        foreach (var row in parsed)
        {
            var name = (string)row[0]!;
            var actualName = (string)row[1]!;
            var length = (int)row[2]!;

            if (actualName == "absent") continue;

            Assert.Equal(name == "get plugins" ? "get plugins" : name, actualName);
            Assert.Equal(name == "get plugins" ? 0 : NativeArity.For(name)!.Value, length);
        }
    }

    /// <summary>A Chromium profile gets an empty function, so the honest counts stay honest.</summary>'''

if anchor not in t:
    raise SystemExit("runtime anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, block, 1))
print("the runtime test reads name and arity")
