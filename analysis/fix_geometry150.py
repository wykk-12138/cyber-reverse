import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    private static async Task<ChromiumBridge> LaunchPatchedAsync(string userAgent)
    {
        var bridge = await ChromiumBridge.LaunchAsync();'''

new = '''    private static async Task<ChromiumBridge> LaunchPatchedAsync(string userAgent)
    {
        // R150: the launch size follows the agent, so a phone profile gets a phone-sized window and
        // outerHeight can agree with the screen it claims.
        var bridge = await ChromiumBridge.LaunchAsync(userAgent: userAgent);'''

if old not in t:
    raise SystemExit("launch helper anchor missing")
t = t.replace(old, new, 1)

old2 = '''        // screen, ratio and the top-level viewport are the phone's
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

new2 = '''        // R150: all seven now agree, because the launch size follows the agent the profile claims.
        // Before this round outerHeight reported the host window's height (769) against a claimed 874,
        // which is exactly the impossibility the image's comment warns about.
        Assert.Equal("[402,874,3,402,684,402,874]", shape);'''

if old2 not in t:
    raise SystemExit("geometry assert anchor missing")
t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the geometry assertion is now an equality")
