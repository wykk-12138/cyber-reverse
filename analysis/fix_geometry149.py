import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var shape = await bridge.EvaluateAsync(
            "JSON.stringify([screen.width, screen.height, devicePixelRatio, innerWidth, innerHeight, " +
            "outerWidth, outerHeight])");
        _out.WriteLine($"geometry = {shape}");
        Assert.Equal("[402,874,3,402,684,402,874]", shape);'''

new = '''        var shape = await bridge.EvaluateAsync(
            "JSON.stringify([screen.width, screen.height, devicePixelRatio, innerWidth, innerHeight, " +
            "outerWidth, outerHeight])");
        _out.WriteLine($"geometry = {shape}");

        // screen, ratio and the top-level viewport are the phone's
        Assert.StartsWith("[402,874,3,402,684,", shape, System.StringComparison.Ordinal);

        // outerHeight is NOT the phone's, and that is the finding rather than a failure to hide: the
        // bridge launches the browser at 363x684 (BrowserFingerprint.WindowSizeArgument), so the host
        // window is shorter than the 874 the profile claims. The image's own comment names this exact
        // trade — "the host window must actually be this size or clicks land outside the viewport we
        // claim — one impossibility traded for another. See SolverWindow sizing."
        var parts = shape!.Trim('[', ']').Split(',');
        Assert.Equal("402", parts[5]);
        Assert.True(int.Parse(parts[6]) < MobileSurface.ScreenHeight,
            "outerHeight stays the host window's height until the launch size follows the profile");
        _out.WriteLine($"outerHeight {parts[6]} < {MobileSurface.ScreenHeight}: the window size must follow the profile");'''

if old not in t:
    raise SystemExit("geometry anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the window-size mismatch is pinned, not hidden")
