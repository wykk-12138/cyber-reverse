using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R20: the live proof. Load a real Kasada-protected storefront in the embedded browser and
/// see whether a token comes out. Network-dependent, so it is Slow, and it reports what
/// happened rather than demanding success — a store changing its bot defence is a fact to
/// record, not a build break.
/// </summary>
[Trait("Speed", "Slow")]
public class KasadaLiveTests
{
    private readonly ITestOutputHelper _out;
    public KasadaLiveTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public async Task NikeHandsOutAKasadaToken()
    {
        var solver = new ChromiumKasadaSolver();
        var result = await solver.SolveAsync("https://www.nike.com/", TimeSpan.FromSeconds(40));

        _out.WriteLine($"ok            = {result.Ok}");
        _out.WriteLine($"executed      = {result.ScriptExecuted}");
        _out.WriteLine($"ct            = {result.Ct}");
        _out.WriteLine($"sbsd          = {result.Sbsd}");
        _out.WriteLine($"version       = {result.Version}");
        _out.WriteLine($"needsBrowser  = {result.NeedsRealBrowser}");
        _out.WriteLine($"error         = {result.Error}");

        foreach (var kv in result.Headers)
            _out.WriteLine($"  header {kv.Key} = {kv.Value}");
        foreach (var cookie in result.Cookies)
            _out.WriteLine($"  cookie {cookie}");

        if (result.Ok)
        {
            Assert.False(string.IsNullOrWhiteSpace(result.Ct));
            Assert.True(result.Ct!.Length >= 16, $"token too short: {result.Ct}");
            Assert.True(result.ScriptExecuted);
        }
        else
        {
            // A failure must name its cause — "empty string" would be useless.
            Assert.NotNull(result.Error);
            Assert.NotEqual(string.Empty, result.Error);
        }
    }

    [Fact]
    public async Task TheBrowserActuallyReachesNike()
    {
        await using var bridge = await ChromiumBridge.LaunchAsync();
        await bridge.ApplyStealthAsync();
        await bridge.NavigateAsync("https://www.nike.com/");
        await Task.Delay(5000);

        var title = await bridge.EvaluateAsync("document.title");
        var href = await bridge.EvaluateAsync("location.href");
        var kpsdk = await bridge.EvaluateAsync("typeof window.KPSDK !== 'undefined' ? 'yes' : 'no'");

        _out.WriteLine($"title = {title}");
        _out.WriteLine($"href  = {href}");
        _out.WriteLine($"kpsdk = {kpsdk}");

        var cookies = await bridge.EvaluateAsync("document.cookie");
        _out.WriteLine($"cookies = {cookies}");

        Assert.NotNull(title);
        Assert.Contains("nike", (href ?? string.Empty).ToLowerInvariant());
    }
}
