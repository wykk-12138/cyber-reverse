using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R19: the embedded browser must not look headless. These assertions are the checks a
/// Kasada-protected storefront makes before it hands out a token.
/// </summary>
[Trait("Speed", "Slow")]
public class ChromiumStealthTests
{
    private readonly ITestOutputHelper _out;
    public ChromiumStealthTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public async Task TheUserAgentHasNoHeadlessToken()
    {
        using var server = new Support.TinyServer(_ => (200, "<html><title>s</title></html>"));
        await using var bridge = await ChromiumBridge.LaunchAsync();
        await bridge.ApplyStealthAsync();
        await bridge.NavigateAsync(server.BaseUrl + "/");
        await Task.Delay(700);

        var ua = await bridge.EvaluateAsync("navigator.userAgent");
        _out.WriteLine($"ua = {ua}");

        Assert.NotNull(ua);
        Assert.DoesNotContain("Headless", ua!, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("Chrome/", ua);
        Assert.Contains("Windows NT 10.0", ua);
    }

    [Fact]
    public async Task WebdriverIsAbsentRatherThanFalse()
    {
        using var server = new Support.TinyServer(_ => (200, "<html></html>"));
        await using var bridge = await ChromiumBridge.LaunchAsync();
        await bridge.ApplyStealthAsync();
        await bridge.NavigateAsync(server.BaseUrl + "/");
        await Task.Delay(700);

        var webdriver = await bridge.EvaluateAsync("String(navigator.webdriver)");
        _out.WriteLine($"navigator.webdriver = {webdriver}");

        // undefined, not false: a script checking `'webdriver' in navigator` must miss it
        Assert.Equal("undefined", webdriver);
    }

    [Fact]
    public async Task TheRestOfTheFingerprintLooksOrdinary()
    {
        using var server = new Support.TinyServer(_ => (200, "<html></html>"));
        await using var bridge = await ChromiumBridge.LaunchAsync();
        await bridge.ApplyStealthAsync();
        await bridge.NavigateAsync(server.BaseUrl + "/");
        await Task.Delay(700);

        var probe = await bridge.EvaluateAsync("""
            JSON.stringify({
              chrome: typeof window.chrome,
              runtime: typeof (window.chrome && window.chrome.runtime),
              plugins: navigator.plugins.length,
              languages: navigator.languages.join(','),
              cores: navigator.hardwareConcurrency,
              memory: navigator.deviceMemory,
              vendor: (function(){
                try {
                  const c = document.createElement('canvas').getContext('webgl');
                  return c ? c.getParameter(37445) : 'none';
                } catch (e) { return 'throw'; }
              })(),
              uaCh: navigator.userAgentData ? navigator.userAgentData.brands.map(b => b.brand).join('|') : 'none'
            })
            """);

        _out.WriteLine(probe ?? "(null)");
        Assert.NotNull(probe);

        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var root = doc.RootElement;

        Assert.Equal("object", root.GetProperty("chrome").GetString());
        Assert.Equal("object", root.GetProperty("runtime").GetString());
        // R156: five, not three — the image's own payload sample reports navigator.plugins.count = 5, all with
        // the same internal filename, so the earlier three was the replica's number rather than the device's.
        Assert.Equal(5, root.GetProperty("plugins").GetInt32());
        Assert.Equal("en-US,en", root.GetProperty("languages").GetString());
        Assert.Equal(8, root.GetProperty("cores").GetInt32());
        Assert.Equal("Intel Inc.", root.GetProperty("vendor").GetString());

        // UA-CH must not advertise HeadlessChrome either
        var brands = root.GetProperty("uaCh").GetString();
        Assert.NotNull(brands);
        Assert.DoesNotContain("Headless", brands!, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("Google Chrome", brands);
    }

    [Fact]
    public void TheDefaultUserAgentIsARealChromeString()
    {
        var ua = ChromiumBridge.DefaultUserAgent();

        _out.WriteLine($"default ua = {ua}");
        Assert.DoesNotContain("Headless", ua, StringComparison.OrdinalIgnoreCase);
        Assert.Matches(@"Chrome/\d+\.\d+\.\d+\.\d+", ua);
    }

    [Fact]
    public void TheSolverIsAvailableOnThisMachine()
    {
        Assert.True(ChromiumKasadaSolver.IsAvailable,
            "ChromiumKasadaSolver.IsAvailable must be true when a browser is installed");
    }
}
