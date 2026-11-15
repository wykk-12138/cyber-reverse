import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    /// <summary>A Chromium profile gets an empty function, so the honest counts stay honest.</summary>'''

new = '''    /// <summary>
    /// R156: the engine members the payload reads — five plugins, the connection quartet, the two flags — are
    /// installed for every profile, because they are what a real Chromium reports.
    /// </summary>
    [Fact]
    public async Task TheEngineMembersAreInstalled()
    {
        await using var bridge = await LaunchPatchedAsync("Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36");

        var plugins = await bridge.EvaluateAsync(
            "JSON.stringify([navigator.plugins.length, Array.from(navigator.plugins).map((p) => p.name)," +
            " Array.from(navigator.plugins).map((p) => p.filename)])");
        _out.WriteLine($"plugins = {plugins}");
        Assert.StartsWith("[5,[\\"PDF Viewer\\",", plugins, System.StringComparison.Ordinal);
        Assert.Contains("internal-pdf-viewer", plugins, System.StringComparison.Ordinal);

        var connection = await bridge.EvaluateAsync(
            "JSON.stringify([navigator.connection.effectiveType, navigator.connection.rtt," +
            " navigator.connection.saveData, navigator.connection.downlink])");
        _out.WriteLine($"connection = {connection}");
        Assert.Equal("[\\"4g\\",50,false,10]", connection);

        var flags = await bridge.EvaluateAsync(
            "JSON.stringify([navigator.automationEnabled, screen.darkMode.enabled])");
        Assert.Equal("[false,false]", flags);

        // and a canvas hash is still something only the page can produce — nothing here claims otherwise
        Assert.True(PayloadCoverage.IsReadOnly("canvas-print-100-999"));
    }

    /// <summary>A Chromium profile gets an empty function, so the honest counts stay honest.</summary>'''

if old not in t:
    raise SystemExit("runtime anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the runtime test measures the engine members")
