import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

helper = '''    /// <summary>
    /// Launch, install the script, then navigate — because the bridge installs it with
    /// <c>Page.addScriptToEvaluateOnNewDocument</c>, which by definition only affects the <i>next</i>
    /// document. Evaluating in the current one would measure the browser before the patch, which is
    /// exactly what the first run of this test did.
    /// </summary>
    private static async Task<ChromiumBridge> LaunchPatchedAsync(string userAgent)
    {
        var bridge = await ChromiumBridge.LaunchAsync();
        await bridge.ApplyStealthAsync(userAgent);
        await bridge.NavigateAsync("about:blank");
        return bridge;
    }

    private const string IPhoneUserAgent ='''

t = t.replace("    private const string IPhoneUserAgent =", helper, 1)

# every test uses the helper instead of launch+apply
t = t.replace('''        await using var bridge = await ChromiumBridge.LaunchAsync();
        await bridge.ApplyStealthAsync(IPhoneUserAgent);''',
'''        await using var bridge = await LaunchPatchedAsync(IPhoneUserAgent);''')

t = t.replace('''        await using var bridge = await ChromiumBridge.LaunchAsync();
        await bridge.ApplyStealthAsync("Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36");''',
'''        await using var bridge = await LaunchPatchedAsync("Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36");''')

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("tests navigate after installing the script")
