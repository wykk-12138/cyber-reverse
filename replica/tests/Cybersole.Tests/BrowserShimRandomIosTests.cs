using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: the image carries a GenRandomIos switch (0x143448fbe) — pick a random iOS identity per
/// run so the fingerprint is not identical every time. A randomized fingerprint is only worth anything if
/// the device it claims actually exists, so these cases pin consistency, not just variation: the user
/// agent, viewport, core count and memory must describe one real iPhone, never a mixture.
/// </summary>
public sealed class BrowserShimRandomIosTests
{
    [Fact]
    public void EveryProfileIsInternallyConsistent()
    {
        for (var i = 0; i < BrowserShim.IosUserAgents.Count; i++)
        {
            using var runtime = new ScriptRuntime(BrowserShim.Ios(i));

            var ua = runtime.TryString("navigator.userAgent")!;
            Assert.Contains("iPhone", ua, StringComparison.Ordinal);
            Assert.Contains("AppleWebKit/605.1.15", ua, StringComparison.Ordinal);
            Assert.Contains("Safari/604.1", ua, StringComparison.Ordinal);

            // A device that reports Apple as its vendor, five touch points and a real Safari build, but a
            // desktop platform string or zero cores, is exactly the mixture a detector looks for.
            Assert.Equal("iPhone", runtime.TryString("navigator.platform"));
            Assert.Equal("Apple Computer, Inc.", runtime.TryString("navigator.vendor"));
            Assert.Equal("5", runtime.TryString("String(navigator.maxTouchPoints)"));

            var cores = int.Parse(runtime.TryString("String(navigator.hardwareConcurrency)")!);
            Assert.InRange(cores, 4, 8);

            // iPhone viewports are tall and narrow; a desktop-sized screen with an iPhone UA is a tell.
            var width = int.Parse(runtime.TryString("String(screen.width)")!);
            var height = int.Parse(runtime.TryString("String(screen.height)")!);
            Assert.True(height > width, $"{ua}: {width}x{height}");
            Assert.InRange(width, 320, 500);
        }
    }

    [Fact]
    public void RandomSelectionIsReproducibleFromASeed()
    {
        var first = BrowserShim.RandomIos(new Random(1234)).UserAgent;
        var second = BrowserShim.RandomIos(new Random(1234)).UserAgent;
        Assert.Equal(first, second);

        // ...and the pool is genuinely a pool, otherwise "random" would be a fixed identity in disguise.
        var seen = Enumerable.Range(0, 40).Select(i => BrowserShim.RandomIos(new Random(i)).UserAgent).Distinct().Count();
        Assert.True(seen > 1, "RandomIos always produced the same user agent");
    }

    [Fact]
    public void OutOfRangeIndicesWrapInsteadOfThrowing()
    {
        // Callers pick an index off a random number; wrapping keeps a bad index from breaking a run.
        Assert.Equal(BrowserShim.Ios(0).UserAgent, BrowserShim.Ios(BrowserShim.IosUserAgents.Count).UserAgent);
        Assert.Equal(BrowserShim.Ios(0).UserAgent, BrowserShim.Ios(-BrowserShim.IosUserAgents.Count).UserAgent);
    }
}
