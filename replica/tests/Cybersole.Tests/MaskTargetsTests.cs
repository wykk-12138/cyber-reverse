using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 161: the mask gets a caller.
///
/// <para>
/// R160 built <c>asNative</c> and <c>maskGetter</c> and registered nothing — the fifth working piece with no
/// caller in this session. <see cref="MaskTargets"/> is the caller: nineteen getters and three functions, each
/// with the object that owns it, masked in one pass that runs after every patch has landed.
/// </para>
/// </summary>
public sealed class MaskTargetsTests
{
    private readonly ITestOutputHelper _out;

    public MaskTargetsTests(ITestOutputHelper output) => _out = output;

    /// <summary>The table is complete and its owner expressions are the ones the bodies use.</summary>
    [Fact]
    public void TheTableIsTheCaller()
    {
        Assert.Equal(21, MaskTargets.Getters.Count);
        Assert.Equal(3, MaskTargets.Functions.Count);
        Assert.Equal(24, MaskTargets.Count);

        var owners = MaskTargets.Getters.Select(t => t.Owner)
            .Concat(MaskTargets.Functions.Select(t => t.Owner))
            .Distinct().ToArray();

        // every owner is a real object expression the surface bodies also use
        foreach (var owner in owners)
            Assert.Contains(owner, new[]
            {
                "G.navigator", "G.Element.prototype", "G", "G.Screen.prototype",
                "G.VisualViewport.prototype", "G.Performance.prototype",
                "G.speechSynthesis", "G.Document.prototype", "G.WebGLRenderingContext.prototype",
                "Object.getPrototypeOf(G.navigator)",
            });

        foreach (var owner in owners) _out.WriteLine(owner);
    }

    /// <summary>The pass is generated cleanly and masks before it finishes.</summary>
    [Fact]
    public void ThePassIsClean()
    {
        var js = MaskTargets.ApplyJs();

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
        Assert.Contains("G.__nativeMask", js);
        Assert.Contains("M.maskGetter(", js);
        Assert.Contains("M.asNative(", js);
        Assert.DoesNotContain("throw ", js);

        // one call per row
        Assert.Equal(MaskTargets.Getters.Count, CountOccurrences(js, "M.maskGetter("));
    }

    /// <summary>Nothing the bodies patch is missing from the table.</summary>
    [Fact]
    public void TheTableCoversWhatTheBodiesPatch()
    {
        var patched = new[]
        {
            "plugins", "mimeTypes", "connection", "maxTouchPoints", "hardwareConcurrency",
            "deviceMemory", "webdriver", "clientWidth", "clientHeight", "devicePixelRatio",
            "outerWidth", "outerHeight", "innerWidth", "innerHeight", "darkMode",
        };

        var covered = MaskTargets.Getters.Select(t => t.Property).ToHashSet();
        foreach (var name in patched) Assert.Contains(name, covered);

        foreach (var name in new[] { "getVoices", "createEvent", "getParameter" })
            Assert.Contains(name, MaskTargets.Functions.Select(t => t.Property));

        _out.WriteLine("nothing patched is left unmasked");
    }

    /// <summary>The bridge runs the pass last.</summary>
    [Fact]
    public void ThePassRunsLast()
    {
        var bridge = System.IO.File.ReadAllText(System.IO.Path.Combine(
            RepoRoot(), "src", "Cybersole.Stores", "Scripts", "ChromiumBridge.cs"));

        Assert.Contains("surfaceBody += MaskTargets.ApplyJs();", bridge);

        var apply = bridge.IndexOf("MaskTargets.ApplyJs()", System.StringComparison.Ordinal);
        var touches = bridge.IndexOf("MobileNavigator.BodyJs(userAgent)", System.StringComparison.Ordinal);
        Assert.True(apply > touches, "the mask pass is appended after every body");
    }

    private static int CountOccurrences(string haystack, string needle)
    {
        var count = 0;
        for (var i = haystack.IndexOf(needle, System.StringComparison.Ordinal);
             i >= 0;
             i = haystack.IndexOf(needle, i + needle.Length, System.StringComparison.Ordinal))
            count++;
        return count;
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !System.IO.File.Exists(System.IO.Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir!.FullName;
    }
}
