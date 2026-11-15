using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R18: prove the Chromium path works — the bridge can start a browser and evaluate script,
/// which is the capability a bare JS engine (R17) could not provide.
/// </summary>
[Trait("Speed", "Slow")]
public class ChromiumBridgeTests
{
    private readonly ITestOutputHelper _out;
    public ChromiumBridgeTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void ABrowserIsInstalled()
    {
        var path = ChromiumBridge.FindBrowser();
        _out.WriteLine($"browser = {path ?? "(none)"}");
        Assert.NotNull(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public async Task TheBridgeLaunchesAndEvaluates()
    {
        await using var bridge = await ChromiumBridge.LaunchAsync();

        var ua = await bridge.EvaluateAsync("navigator.userAgent");
        _out.WriteLine($"userAgent = {ua}");

        Assert.NotNull(ua);
        Assert.Contains("Chrome", ua);

        var sum = await bridge.EvaluateAsync("1 + 41");
        Assert.Equal("42", sum);
    }

    [Fact]
    public async Task TheBridgeNavigatesAndSeesTheDocument()
    {
        await using var bridge = await ChromiumBridge.LaunchAsync();
        await bridge.NavigateAsync("data:text/html,<title>cyb</title><h1 id=x>hello</h1>");

        await Task.Delay(600);

        var title = await bridge.EvaluateAsync("document.title");
        var heading = await bridge.EvaluateAsync("document.getElementById('x').textContent");

        Assert.Equal("cyb", title);
        Assert.Equal("hello", heading);
    }

    [Fact]
    public async Task TheBrowserExposesApisJintDoesNot()
    {
        // crypto.subtle only exists in a secure context, so drive a loopback origin rather
        // than data:/about: — that is also how the solver uses it (a real https storefront).
        using var server = new Support.TinyServer(_ => (200, "<html><title>secure</title></html>"));
        await using var bridge = await ChromiumBridge.LaunchAsync();
        await bridge.NavigateAsync(server.BaseUrl + "/");
        await Task.Delay(800);

        // These are exactly the surfaces the Kasada payload reaches for.
        var checks = await bridge.EvaluateAsync("""
            JSON.stringify({
              worker: typeof Worker,
              subtle: typeof (crypto && crypto.subtle),
              getRandomValues: typeof (crypto && crypto.getRandomValues),
              performanceNow: typeof performance.now,
              bindOnFunction: typeof Function.prototype.bind,
              promiseResolve: typeof Promise.resolve,
              requestAnimationFrame: typeof requestAnimationFrame
            })
            """);

        _out.WriteLine(checks ?? "(null)");
        Assert.NotNull(checks);

        using var doc = System.Text.Json.JsonDocument.Parse(checks!);
        Assert.Equal("function", doc.RootElement.GetProperty("worker").GetString());
        Assert.Equal("object", doc.RootElement.GetProperty("subtle").GetString());
        Assert.Equal("function", doc.RootElement.GetProperty("getRandomValues").GetString());
        Assert.Equal("function", doc.RootElement.GetProperty("requestAnimationFrame").GetString());
    }
}
