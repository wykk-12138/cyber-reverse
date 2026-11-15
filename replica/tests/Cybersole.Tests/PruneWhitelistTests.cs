using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 169: three corrections from one more paragraph of the image's own comments.
///
/// <list type="number">
/// <item><b>The prune is a whitelist.</b> R163 wrote nine names to delete; the capture deletes every own name not in
/// <c>NAV_KEYS</c>. A blacklist has to be extended whenever the engine ships something new; a whitelist cannot fall
/// behind.</item>
/// <item><b><c>audioSession</c> is <c>{}</c> plus a tag.</b> hCaptcha <c>JSON.stringify</c>s each member, and on the device
/// this one answers <c>{}</c> — so a bare object with <c>Symbol.toStringTag</c> and a non-enumerable <c>type</c> reproduces
/// what is read.</item>
/// <item><b>plugins and mimeTypes must be left alone.</b> Blink's five <c>internal-pdf-viewer</c> entries and two mime
/// types are exactly what an iPhone reports; the earlier override emptied both, so every payload carried
/// <c>plugins: []</c>.</item>
/// </list>
/// </summary>
public sealed class PruneWhitelistTests
{
    private readonly ITestOutputHelper _out;

    public PruneWhitelistTests(ITestOutputHelper output) => _out = output;

    /// <summary>The body deletes what is not on the allowlist, and keeps the constructor.</summary>
    [Fact]
    public void ThePruneIsAWhitelist()
    {
        var js = NavPrune.BodyJs();

        Assert.Contains("G.Navigator && G.Navigator.prototype", js);
        Assert.Contains("const sweep = (target)", js);
        // R187: the sweep enumerates with the reference captured at the top of the surface (0x03d20953 in the
        // target), so the key-order wrapper installed above it cannot filter what it is about to judge.
        Assert.Contains("const own = G.__nativeOwnNames || Object.getOwnPropertyNames;", js);
        Assert.Contains("own(target).forEach((key) => {", js);
        Assert.Contains("if (!keep.has(key) && key !== 'constructor')", js);
        Assert.Contains("delete target[key]", js);

        // the sweep covers both the prototype and the instance, because this replica's own scripts still put a
        // few members on the instance
        Assert.Contains("sweep(G.Navigator && G.Navigator.prototype);", js);
        Assert.Contains("sweep(G.navigator);", js);

        // the allowlist is the recorded order plus the two the record lists separately
        Assert.Equal(MobileNavigator.NavOrder.Count + 2, NavPrune.AllowList.Count);
        Assert.Contains("plugins", NavPrune.AllowList);
        Assert.Contains("mimeTypes", NavPrune.AllowList);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
        _out.WriteLine($"{NavPrune.AllowList.Count} names kept");
    }

    /// <summary>The nine Blink-only names survive as the reason, and none of them is on the allowlist.</summary>
    [Fact]
    public void TheBlinkOnlyNamesAreTheReason()
    {
        Assert.Equal(9, NavPrune.BlinkOnly.Count);
        Assert.Empty(NavPrune.BlinkOnly.Intersect(NavPrune.AllowList, System.StringComparer.Ordinal));

        // connection is the one the engine block installs for desktop profiles — and it is not kept on a phone
        Assert.Contains("connection", NavPrune.BlinkOnly);
        Assert.DoesNotContain("connection", NavPrune.AllowList);
    }

    /// <summary>The audio session shim is the tag recipe, not a simulation.</summary>
    [Fact]
    public void TheAudioSessionIsTheTagRecipe()
    {
        var js = NavPrune.AudioSessionBodyJs();

        Assert.Contains("const session = {};", js);
        Assert.Contains("Symbol.toStringTag", js);
        Assert.Contains("'AudioSession'", js);
        Assert.Contains("'type'", js);
        Assert.Contains("'auto'", js);
        Assert.Contains("enumerable: false", js);
        Assert.Contains("!('audioSession' in proto)", js);

        Assert.Equal("AudioSession", NavPrune.AudioSessionTag);
        Assert.Equal("auto", NavPrune.AudioSessionType);
        Assert.Contains("JSON.stringify", NavPrune.AudioSessionBodyJs() + NavPrune.PluginsAreNative);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
    }

    /// <summary>Nothing overrides the plugin lists any more.</summary>
    [Fact]
    public void ThePluginListsAreLeftNative()
    {
        var engine = MobileSurface.EngineBodyJs();

        Assert.DoesNotContain("'plugins'", engine);
        Assert.DoesNotContain("navigator, 'plugins'", engine);
        // The note lives in the engine body's comment block, which the body string itself does not carry — the
        // generated JavaScript is the code, not the prose around it. So the assertion is on the *source*: the
        // bridge must carry the reasoning, and the body must not carry a patch.
        var source = System.IO.File.ReadAllText(System.IO.Path.Combine(
            RepoRoot(), "src", "Cybersole.Stores", "Scripts", "MobileSurface.cs"));

        Assert.Contains("plugins and mimeTypes are left NATIVE", source);
        Assert.Contains("internal-pdf-viewer", source + NavPrune.PluginsAreNative);

        Assert.Equal(5, NavPrune.NativePluginCount);
        Assert.Equal(2, NavPrune.NativeMimeTypeCount);
        Assert.Contains("plugins: []", NavPrune.PluginsAreNative);

        // and the engine block no longer claims to install them
        Assert.DoesNotContain("internal-pdf-viewer", engine);
    }

    /// <summary>Measured: the native lists already answer 5 and 2.</summary>
    [Fact]
    public async Task TheNativeListsAreAlreadyTheDevices()
    {
        const string iphone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                              "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                              "Mobile/15E148 Safari/604.1";

        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: iphone);
        await bridge.ApplyStealthAsync(iphone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await System.Threading.Tasks.Task.Delay(50);
        }

        var probe = await bridge.EvaluateAsync(
            "JSON.stringify([navigator.plugins.length, navigator.mimeTypes.length, " +
            "navigator.plugins[0] && navigator.plugins[0].filename])");

        _out.WriteLine("plugins = " + probe);
        Assert.StartsWith("[5,2,\"internal-pdf-viewer\"]", probe, System.StringComparison.Ordinal);

        // the audio session exists and serialises as {}
        var session = await bridge.EvaluateAsync(
            "JSON.stringify([JSON.stringify(navigator.audioSession), " +
            "Object.prototype.toString.call(navigator.audioSession), navigator.audioSession.type])");
        _out.WriteLine("audioSession = " + session);
        Assert.Equal("[\"{}\",\"[object AudioSession]\",\"auto\"]", session);
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !System.IO.File.Exists(System.IO.Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir!.FullName;
    }
}
