using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 160: a patch is two things — what it does, and what it says it is.
///
/// <para>
/// The image's <c>CRED_SHIM</c> records <c>{ name, length, src }</c> beside every fake. That is only worth recording
/// because a detector can read all three: <c>Function.prototype.toString</c> answers the third, and
/// <c>fn.length</c> the second. The replica patched <c>getVoices</c>, <c>createEvent</c> and a dozen getters and
/// masked none of them, so each one announced itself the moment anything asked.
/// </para>
/// </summary>
public sealed class NativeMaskTests
{
    private readonly ITestOutputHelper _out;

    public NativeMaskTests(ITestOutputHelper output) => _out = output;

    /// <summary>The mask installs a registry and one override, and guards against a second install.</summary>
    [Fact]
    public void TheMaskIsInstalledOnce()
    {
        var js = NativeMask.BodyJs();

        Assert.Contains("__nativeMaskInstalled", js);
        Assert.Contains("__nativeMask", js);
        Assert.Contains("FAKES", js);
        Assert.Contains("Function.prototype, 'toString'", js);
        Assert.Contains("asNative", js);
        Assert.Contains("maskGetter", js);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
    }

    /// <summary>The native text is the exact shape a browser uses.</summary>
    [Fact]
    public void TheNativeTextIsTheBrowsersShape()
    {
        // R172: WebKit prints natives on three lines, V8 on one — and the profile claims WebKit
        Assert.Equal("function getVoices() {\n    [native code]\n}", NativeMask.NativeText("getVoices"));
        Assert.Equal("function toString() {\n    [native code]\n}", NativeMask.NativeText("toString"));

        _out.WriteLine(NativeMask.NativeText("getParameter"));
    }

    /// <summary>Every patched function and getter is on the list that must be masked.</summary>
    [Fact]
    public void TheListsCoverWhatIsPatched()
    {
        foreach (var name in new[] { "getVoices", "createEvent", "getParameter" })
            Assert.True(NativeMask.NeedsMask(name), name);

        foreach (var name in new[] { "plugins", "connection", "maxTouchPoints", "clientWidth" })
            Assert.True(NativeMask.NeedsMask(name), name);

        Assert.False(NativeMask.NeedsMask("userAgent"));
        Assert.False(NativeMask.NeedsMask(null));

        Assert.Equal(3, NativeMask.MaskedFunctions.Count);
        Assert.Equal(13, NativeMask.MaskedGetters.Count);

        _out.WriteLine(string.Join(", ", NativeMask.MaskedGetters));
    }

    /// <summary>The rule says why both halves are required.</summary>
    [Fact]
    public void TheRuleStands()
    {
        Assert.Contains("announcing itself", NativeMask.Rule);
        Assert.Contains("name, length and src", NativeMask.Rule);
    }

    /// <summary>The bridge installs the mask before anything it masks.</summary>
    [Fact]
    public void TheMaskRunsFirst()
    {
        var bridge = System.IO.File.ReadAllText(System.IO.Path.Combine(
            RepoRoot(), "src", "Cybersole.Stores", "Scripts", "ChromiumBridge.cs"));

        Assert.Contains("var surfaceBody = NativeRefs.BodyJs() + NativeMask.BodyJs() + EngineParity.BodyJs() + MobileSurface.EngineBodyJs();", bridge);

        var mask = bridge.IndexOf("NativeMask.BodyJs()", System.StringComparison.Ordinal);
        var engine = bridge.IndexOf("MobileSurface.EngineBodyJs()", System.StringComparison.Ordinal);
        Assert.True(mask > 0 && engine > mask, "the mask precedes the engine block it masks");
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !System.IO.File.Exists(System.IO.Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir!.FullName;
    }
}
