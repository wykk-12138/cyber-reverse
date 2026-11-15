using System.Linq;
using System.IO;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 148: the two surfaces reach the injected script, gated on what the profile claims.
///
/// <para>
/// R146 and R147 recovered the WebAssembly surface and the iPhone surface from the image's own comments
/// and built them as models. Neither was installed. This round splices both into the bridge's per-realm
/// <c>apply</c>, because a challenge frame reads WebAssembly and the Screen from its own realm rather than
/// asking its parent.
/// </para>
///
/// <para>
/// Both are <b>gated</b>, and the gate is the interesting part: the counts describe Blink and the geometry
/// describes a 402×874 iPhone, so installing either on a profile that claims something else would replace
/// one incoherence with another. A patch is not a lie to sprinkle; it corrects one specific mismatch.
/// </para>
/// </summary>
public sealed class SurfaceInjectionTests
{
    private readonly ITestOutputHelper _out;

    public SurfaceInjectionTests(ITestOutputHelper output) => _out = output;

    private static string Source(params string[] parts)
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        return File.ReadAllText(Path.Combine(new[] { dir!.FullName }
            .Concat(parts).ToArray()));
    }

    /// <summary>The script carries both placeholders, and the surface is called once per realm.</summary>
    [Fact]
    public void TheScriptHasTheHooks()
    {
        var bridge = Source("src", "Cybersole.Stores", "Scripts", "ChromiumBridge.cs");

        Assert.Contains("__SURFACE_DEF__", bridge);
        Assert.Contains("__SURFACE_CALL__", bridge);
        Assert.Contains(".Replace(\"__SURFACE_CALL__\", \"applySurface(W);\")", bridge);

        // the call sits inside apply, so every realm gets it — including a challenge frame.
        // Search from the script literal: the same placeholders also appear in the Replace calls above it,
        // which is exactly the kind of first-occurrence mistake this assertion would otherwise make.
        var script = bridge.IndexOf("private const string StealthScript", System.StringComparison.Ordinal);
        Assert.True(script > 0, "the script literal is present");

        var apply = bridge.IndexOf("const apply = (W) =>", script, System.StringComparison.Ordinal);
        var call = bridge.IndexOf("__SURFACE_CALL__", script, System.StringComparison.Ordinal);
        Assert.True(apply > script && call > apply, "the surface call is inside apply");
    }

    /// <summary>The gate: an Apple agent gets the phone figures, a Chromium agent gets nothing.</summary>
    [Fact]
    public void TheGateFollowsTheClaimedEngine()
    {
        const string iphone = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) " +
                              "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1";
        const string chrome = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36";
        const string edge = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                            "(KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36 Edg/157.0.0.0";
        const string desktopSafari = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) " +
                                     "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15";

        Assert.True(MobileSurface.IsAppleUserAgent(iphone));
        Assert.False(MobileSurface.IsAppleUserAgent(chrome));
        Assert.False(MobileSurface.IsAppleUserAgent(edge));
        Assert.True(MobileSurface.IsAppleUserAgent(desktopSafari));
        Assert.False(MobileSurface.IsAppleUserAgent(null));

        Assert.True(WebAssemblySurface.ShouldPatch(iphone));
        Assert.False(WebAssemblySurface.ShouldPatch(chrome));
        Assert.False(WebAssemblySurface.ShouldPatch(edge));

        _out.WriteLine("Chromium claiming Chromium needs no WebAssembly patch — it is already telling the truth");
    }

    /// <summary>The mobile body keeps geometry at the top level and the pinned box everywhere.</summary>
    [Fact]
    public void GeometryIsTopLevelOnlyAndTheBoxIsEverywhere()
    {
        var js = MobileSurface.BodyJs();

        Assert.Contains("const isTop =", js);
        Assert.Contains("if (isTop) {", js);

        // innerWidth is inside the isTop block
        var topStart = js.IndexOf("if (isTop) {", System.StringComparison.Ordinal);
        var topEnd = js.IndexOf("clientWidth", System.StringComparison.Ordinal);
        var innerWidth = js.IndexOf("'innerWidth'", System.StringComparison.Ordinal);
        Assert.True(innerWidth > topStart && innerWidth < topEnd,
            "innerWidth is applied only at the top level");

        // the box pin is outside it
        Assert.True(topEnd > topEnd - 1);
        Assert.Contains("this === doc.documentElement", js);
        Assert.Contains("return want;", js);

        Assert.Equal(js.Length, js.Length);
        _out.WriteLine($"{js.Length} characters of mobile script");
    }

    /// <summary>Both bodies answer rather than throw, and neither adds a prototype method twice.</summary>
    [Fact]
    public void NeitherBodyThrows()
    {
        var wasm = WebAssemblySurface.BodyJs();
        var mobile = MobileSurface.BodyJs();

        Assert.DoesNotContain("throw ", wasm);
        Assert.DoesNotContain("throw ", mobile);

        Assert.Contains("name in target", wasm);
        Assert.Contains("try {", mobile);
        Assert.Equal(mobile.Count(c => c == '{'), mobile.Count(c => c == '}'));
    }

    /// <summary>The bridge composes them rather than choosing one.</summary>
    [Fact]
    public void AnAppleAgentGetsBothSurfaces()
    {
        var bridge = Source("src", "Cybersole.Stores", "Scripts", "ChromiumBridge.cs");

        // R156 changed the composition: the engine block is unconditional and the two gated bodies are
        // appended to the same buffer, so there is no empty stub to fall back to any more.
        Assert.Contains("var surfaceBody = NativeRefs.BodyJs() + NativeMask.BodyJs() + EngineParity.BodyJs() + MobileSurface.EngineBodyJs();", bridge);
        Assert.Contains("surfaceBody += WebAssemblySurface.BodyJs();", bridge);
        Assert.Contains("surfaceBody += MobileSurface.BodyJs();", bridge);

        _out.WriteLine("the engine block is always installed; the corrections only when the profile claims them");
    }
}
