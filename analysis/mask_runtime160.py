import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    /// <summary>A Chromium profile gets an empty function, so the honest counts stay honest.</summary>'''

new = '''    /// <summary>
    /// R160: a patched getter must answer <c>toString</c> like a native one, or it announces itself.
    /// </summary>
    [Fact]
    public async Task TheMaskedGettersLookNative()
    {
        await using var bridge = await LaunchPatchedAsync(IPhoneUserAgent);

        var masked = await bridge.EvaluateAsync(
            "JSON.stringify((() => {\\n" +
            "  const d = Object.getOwnPropertyDescriptor(navigator, 'plugins');\\n" +
            "  const getter = d && d.get;\\n" +
            "  const out = [];\\n" +
            "  out.push(getter ? Function.prototype.toString.call(getter) : 'no-getter');\\n" +
            "  out.push(Function.prototype.toString.call(Function.prototype.toString));\\n" +
            "  const cd = Object.getOwnPropertyDescriptor(Element.prototype, 'clientWidth');\\n" +
            "  out.push(cd && cd.get ? Function.prototype.toString.call(cd.get) : 'no-getter');\\n" +
            "  return out;\\n" +
            "})())");

        _out.WriteLine("masked = " + masked);

        // a native function's own toString is [native code], and so is the override's
        Assert.Contains("[native code]", masked, System.StringComparison.Ordinal);
        Assert.DoesNotContain("no-getter", masked, System.StringComparison.Ordinal);

        // and the page's own functions must still print their source — the mask must not silence everything
        var user = await bridge.EvaluateAsync(
            "Function.prototype.toString.call(function named(x) { return x + 1; })");
        Assert.Contains("return x + 1", user, System.StringComparison.Ordinal);
        _out.WriteLine("user function still prints: " + user);
    }

    /// <summary>A Chromium profile gets an empty function, so the honest counts stay honest.</summary>'''

if old not in t:
    raise SystemExit("runtime anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the runtime test checks the mask")
