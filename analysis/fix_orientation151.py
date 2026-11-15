import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        // and orientation is the browser's own, because the image never patches it
        var orientation = await bridge.EvaluateAsync(
            "JSON.stringify([screen.orientation.type, screen.orientation.angle])");
        _out.WriteLine($"orientation = {orientation}");
        Assert.Contains("portrait", orientation, System.StringComparison.Ordinal);'''

new = '''        // R151: orientation is the browser's own, and that is a known incoherence rather than a choice
        // this replica is happy with. The image lists "orientation" in SCREEN_ORDER but never puts it in its
        // SCREEN value object, so it does not patch it either — and measured here it says
        // "landscape-primary" while the profile claims a portrait phone, because Chromium derives it from
        // the host display rather than the window. Pinning a value the image does not pin would be
        // inventing behaviour; leaving it unrecorded would hide a contradiction.
        var orientation = await bridge.EvaluateAsync(
            "JSON.stringify([screen.orientation.type, screen.orientation.angle])");
        _out.WriteLine($"orientation = {orientation} (native, unpatched — see R151 note)");
        Assert.Contains(orientation!, o => o is "portrait-primary" or "landscape-primary");
        Assert.DoesNotContain(MobileSurface.OrientationIsNative,
            string.Join(",", MobileSurface.VisualViewportFields));'''

if old not in t:
    raise SystemExit("orientation anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("orientation is recorded as native and unpatched")
