using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 146: the WebAssembly fingerprint, ported from the image's own injected script.
///
/// <para>
/// The original's stealth code counts <c>getOwnPropertyNames</c> on five WebAssembly objects and makes
/// the answer match the device it claims to be. Blink answers <c>[19,1,2,5,5]</c>; the iPhones that passed
/// answered <c>[16,1,2,6,6]</c>. The gap is two engines pointing in opposite directions — Chrome has JSPI,
/// Safari has type reflection — so the fix is to drop three names and add two.
/// </para>
///
/// <para>
/// The replica patched navigator, screen and WebGL and never touched WebAssembly, so a challenge frame
/// asking this one question saw a device claiming one engine while answering the other's numbers.
/// </para>
/// </summary>
public sealed class WebAssemblySurfaceTests
{
    private readonly ITestOutputHelper _out;

    public WebAssemblySurfaceTests(ITestOutputHelper output) => _out = output;

    /// <summary>Five objects, two count vectors, both from the image.</summary>
    [Fact]
    public void TheTwoCountVectorsAreRecorded()
    {
        Assert.Equal(5, WebAssemblySurface.Counted.Count);
        Assert.Equal(new[] { 19, 1, 2, 5, 5 }, WebAssemblySurface.BlinkCounts);
        Assert.Equal(new[] { 16, 1, 2, 6, 6 }, WebAssemblySurface.SafariCounts);

        for (var i = 0; i < WebAssemblySurface.Counted.Count; i++)
            _out.WriteLine($"{WebAssemblySurface.Counted[i],-22} blink {WebAssemblySurface.BlinkCounts[i],3}  safari {WebAssemblySurface.SafariCounts[i],3}");
    }

    /// <summary>The asymmetry: three names to remove, two to add.</summary>
    [Fact]
    public void TheAsymmetryIsTheFix()
    {
        Assert.Equal(3, WebAssemblySurface.JspiNames.Count);
        Assert.Equal(2, WebAssemblySurface.TypeReflectionMethods.Count);
        Assert.Equal(5, WebAssemblySurface.Delta);

        Assert.Contains("Suspending", WebAssemblySurface.JspiNames);
        Assert.Contains("promising", WebAssemblySurface.JspiNames);
        Assert.Contains("SuspendError", WebAssemblySurface.JspiNames);

        // three out, two in, and the first count moves from 19 to 16 by exactly that difference
        Assert.True(WebAssemblySurface.CountsDifferByTheDelta);
        Assert.Equal(19 - 3, WebAssemblySurface.SafariCounts[0]);
    }

    /// <summary>The stub rule: answer, do not throw.</summary>
    [Fact]
    public void TheStubAnswersRatherThanThrows()
    {
        Assert.Contains("threw", WebAssemblySurface.StubRule);
        Assert.Contains("worse answer", WebAssemblySurface.StubRule);

        var js = WebAssemblySurface.ToJavaScript();
        Assert.DoesNotContain("throw", js);
        Assert.Contains("return { kind: 'memory' }", js);
        Assert.Contains("return { kind: 'table' }", js);

        _out.WriteLine(WebAssemblySurface.StubRule);
    }

    /// <summary>The script removes the three, adds the two, and keeps the methods non-enumerable.</summary>
    [Fact]
    public void TheScriptDoesWhatTheCommentSays()
    {
        var js = WebAssemblySurface.ToJavaScript();

        foreach (var name in WebAssemblySurface.JspiNames)
            Assert.Contains("\"" + name + "\"", js);

        Assert.Contains("delete W[name]", js);
        Assert.Contains("enumerable: false", js);
        Assert.Contains("addMethod(W.Memory.prototype, 'type'", js);
        Assert.Contains("addMethod(W.Table.prototype, 'type'", js);

        // a method that already exists must be left alone, or the count overshoots
        Assert.Contains("name in target", js);

        Assert.Equal(js.Count(c => c == '{'), js.Count(c => c == '}'));
        _out.WriteLine($"{js.Length} characters of injected script");
    }

    /// <summary>The two targets are the two prototypes the count looks at.</summary>
    [Fact]
    public void TheAddedMethodsLandOnTheCountedPrototypes()
    {
        Assert.Equal(new[] { "Memory.prototype", "Table.prototype" },
            WebAssemblySurface.TypeReflectionTargets);

        foreach (var target in WebAssemblySurface.TypeReflectionTargets)
            Assert.Contains(target, WebAssemblySurface.Counted);
    }

    /// <summary>The replica's other fingerprint fields and this one measure different things.</summary>
    [Fact]
    public void ThisIsNotTheScreenFingerprint()
    {
        Assert.Empty(WebAssemblySurface.Counted.Intersect(BrowserFingerprint.Fields,
            System.StringComparer.OrdinalIgnoreCase));

        // and it is not the 3-D Secure profile either
        Assert.Empty(WebAssemblySurface.Counted.Intersect(FingerprintLayers.DlpaFields,
            System.StringComparer.OrdinalIgnoreCase));

        _out.WriteLine("layer 1 (screen) and layer 3 (3DS) are separate from this engine surface");
    }
}
