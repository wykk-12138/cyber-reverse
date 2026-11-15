import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        // a child element must still report its own box, so page geometry is untouched'''

new = '''        // R151: the viewport itself reports the phone, which is the half the replica had left alone
        var viewport = await bridge.EvaluateAsync(
            "JSON.stringify([visualViewport.width, visualViewport.height, visualViewport.scale, " +
            "visualViewport.offsetTop, visualViewport.pageTop])");
        _out.WriteLine($"visualViewport = {viewport}");
        Assert.Equal("[402,684,1,0,0]", viewport);

        // and orientation is the browser's own, because the image never patches it
        var orientation = await bridge.EvaluateAsync(
            "JSON.stringify([screen.orientation.type, screen.orientation.angle])");
        _out.WriteLine($"orientation = {orientation}");
        Assert.Contains("portrait", orientation, System.StringComparison.Ordinal);

        // a child element must still report its own box, so page geometry is untouched'''

if old not in t:
    raise SystemExit("viewport test anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the runtime test measures the viewport too")
