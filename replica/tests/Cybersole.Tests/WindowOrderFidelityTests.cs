using System.Linq;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R192: the window's enumeration order, checked against the device's own recorded lists rather than described.
/// </summary>
public sealed class WindowOrderFidelityTests
{
    private readonly ITestOutputHelper _out;
    public WindowOrderFidelityTests(ITestOutputHelper output) => _out = output;

    const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                          "Mobile/15E148 Safari/604.1";

    private static async Task<ChromiumBridge> PageAsync()
    {
        var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await Task.Delay(50);
        }
        return bridge;
    }

    [Fact]
    public async Task TheKeysFollowTheDevicesOwnOrder()
    {
        await using var bridge = await PageAsync();

        var probe = await bridge.EvaluateAsync(
            "JSON.stringify([Object.keys(window), Object.getOwnPropertyNames(window)])");

        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var keys = doc.RootElement[0].EnumerateArray().Select(e => e.GetString()!).ToList();
        var own = doc.RootElement[1].EnumerateArray().Select(e => e.GetString()!).ToList();

        _out.WriteLine($"keys: {keys.Count} first5={string.Join(",", keys.Take(5))} last5={string.Join(",", keys.TakeLast(5))}");
        _out.WriteLine($"own : {own.Count} first5={string.Join(",", own.Take(5))} last5={string.Join(",", own.TakeLast(5))}");

        // the first five of the enumerable pass are the device's first five
        Assert.Equal(WindowNameTable.Enum.Take(5), keys.Take(5));

        // the first five of the own-names pass are the device's first five
        Assert.Equal(WindowNameTable.All.Take(5), own.Take(5));

        // the recorded order is not Blink's, so this is only true if the constants are actually in use
        var patchedPrefix = string.Join(",", keys.Take(8));
        _out.WriteLine("prefix = " + patchedPrefix);

        // `webkit` is spliced in front of `Raven` for the top-level enumerable pass
        var at = keys.IndexOf("webkit");
        var raven = keys.IndexOf("Raven");
        if (at >= 0 && raven >= 0) Assert.True(at < raven, "webkit is not before Raven");
    }

    [Fact]
    public async Task TheOwnersLateGlobalsAreNotReportedAsThePages()
    {
        await using var bridge = await PageAsync();

        var probe = await bridge.EvaluateAsync(
            "JSON.stringify([Object.keys(window).indexOf('CSSStyleProperties'), " +
            "Object.keys(window).indexOf('__cssProto'), Object.keys(window).indexOf('__nativeMask'), " +
            "Object.keys(window).indexOf('__windowNames')])");

        _out.WriteLine("indices = " + probe);
        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var r = doc.RootElement;

        // none of this script's own slots may trail the device list: the baseline snapshot is taken last (R192)
        Assert.Equal(-1, r[0].GetInt32());
        Assert.Equal(-1, r[1].GetInt32());
        Assert.Equal(-1, r[2].GetInt32());
        Assert.Equal(-1, r[3].GetInt32());
    }
}
