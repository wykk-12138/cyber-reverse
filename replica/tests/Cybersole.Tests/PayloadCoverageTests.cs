using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 156: the fingerprint half of the payload, audited into three columns and then closed.
///
/// <para>
/// The sample of R152 says <c>navigator.plugins.count = 5</c> with five names, a connection quartet, and two
/// flags that are not DOM members at all. The replica answered three plugins and no connection. Both are now
/// installed — and the bottom of the audit is the part worth keeping: canvas hashes and js-errors are computed
/// by the page, so a stealth layer that claims to install them is describing reach it does not have.
/// </para>
/// </summary>
public sealed class PayloadCoverageTests
{
    private readonly ITestOutputHelper _out;

    public PayloadCoverageTests(ITestOutputHelper output) => _out = output;

    /// <summary>Three columns, and the read-only one is not empty.</summary>
    [Fact]
    public void TheAuditHasThreeColumns()
    {
        Assert.Equal(9, PayloadCoverage.AlreadyAnswered.Count);
        Assert.Equal(7, PayloadCoverage.Installed.Count);
        Assert.Equal(5, PayloadCoverage.CannotBeInstalled.Count);

        // the columns do not overlap
        var installed = PayloadCoverage.Installed.ToHashSet();
        Assert.Empty(PayloadCoverage.AlreadyAnswered.Where(installed.Contains));
        Assert.Empty(PayloadCoverage.CannotBeInstalled.Where(installed.Contains));

        _out.WriteLine("installed: " + string.Join(", ", PayloadCoverage.Installed));
        _out.WriteLine("read-only: " + string.Join(", ", PayloadCoverage.CannotBeInstalled));
    }

    /// <summary>The four things that cannot be installed are named as such.</summary>
    [Fact]
    public void TheCanvasAndErrorKeysAreReadOnly()
    {
        Assert.True(PayloadCoverage.IsReadOnly("canvas-print-100-999"));
        Assert.True(PayloadCoverage.IsReadOnly("canvas-print-detailed-100-999"));
        Assert.True(PayloadCoverage.IsReadOnly("js-errors"));
        Assert.True(PayloadCoverage.IsReadOnly("font-Arial"));

        Assert.False(PayloadCoverage.IsReadOnly("navigator.plugins"));
        Assert.False(PayloadCoverage.IsReadOnly("navigator.connection.effectiveType"));
        Assert.False(PayloadCoverage.IsReadOnly(null));

        Assert.Contains("not a property to override", PayloadCoverage.Rule);
    }

    /// <summary>The connection values are the sample's.</summary>
    [Fact]
    public void TheConnectionQuartetIsTheSamples()
    {
        Assert.Equal(4, PayloadCoverage.ConnectionSample.Count);
        Assert.Equal("4g", PayloadCoverage.ConnectionSample["effectiveType"]);
        Assert.Equal(50, PayloadCoverage.ConnectionSample["rtt"]);
        Assert.Equal(false, PayloadCoverage.ConnectionSample["saveData"]);
        Assert.Equal(10, PayloadCoverage.ConnectionSample["downlink"]);
    }

    /// <summary>The engine body installs five plugins and the quartet, and never throws.</summary>
    [Fact]
    public void TheEngineBodyInstallsTheFiveAndTheQuartet()
    {
        var js = MobileSurface.EngineBodyJs();

        // R169: the plugin LISTS are left native, so their names no longer appear in the generated body. What the body
        // must still carry is the connection quartet and the two flags.
        Assert.DoesNotContain("PDF Viewer", js);

                Assert.Contains("'4g'", js);
        Assert.Contains("rtt: 50", js);
        Assert.Contains("downlink: 10", js);
        Assert.Contains("'automationEnabled'", js);
        Assert.Contains("'darkMode'", js);

        Assert.DoesNotContain("throw ", js);
        Assert.Equal(js.Count(c => c == '{'), js.Count(c => c == '}'));
        _out.WriteLine($"{js.Length} characters of engine script");
    }

    /// <summary>The bridge installs the engine block for every profile, and the gated two only sometimes.</summary>
    [Fact]
    public void TheEngineBlockIsUnconditional()
    {
        var bridge = System.IO.File.ReadAllText(System.IO.Path.Combine(
            RepoRoot(), "src", "Cybersole.Stores", "Scripts", "ChromiumBridge.cs"));

        Assert.Contains("var surfaceBody = NativeRefs.BodyJs() + NativeMask.BodyJs() + EngineParity.BodyJs() + MobileSurface.EngineBodyJs();", bridge);

        // the engine body is added before the gate, so it is in every composition
        var engine = bridge.IndexOf("MobileSurface.EngineBodyJs()", System.StringComparison.Ordinal);
        var wasm = bridge.IndexOf("WebAssemblySurface.ShouldPatch(userAgent)) surfaceBody", System.StringComparison.Ordinal);
        Assert.True(engine > 0 && wasm > engine, "the gated bodies are appended after the unconditional one");

        // and there is no longer an empty stub that would drop the engine block too
        Assert.DoesNotContain("const applySurface = (realm) => {};", bridge);
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !System.IO.File.Exists(System.IO.Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir!.FullName;
    }
}
