using System.IO;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 149: the injected surfaces are run, not just assembled.
///
/// <para>
/// R148 proved the two blocks were spliced into the script by asserting on strings. That is a claim about
/// text, not about behaviour: a brace out of place, a `return` outside a function, or a name that does not
/// exist in the realm would all pass a string assertion and fail in the browser. This test launches a real
/// headless Chromium, installs the same script the bridge installs, and reads the result back out of the
/// page.
/// </para>
///
/// <para>
/// What it measures is exactly what the image's comments say a detector measures: the five
/// <c>getOwnPropertyNames</c> counts, whether <c>createEvent('TouchEvent')</c> throws, the Screen key count,
/// and whether the page-zoom ratio is exactly one. The profile is an iPhone, because that is the only case
/// where the gate installs the phone figures at all.
/// </para>
/// </summary>
[Trait("Speed", "Slow")]
public class SurfaceRuntimeTests
{
    private readonly ITestOutputHelper _out;

    public SurfaceRuntimeTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// Launch, install the script, then navigate — because the bridge installs it with
    /// <c>Page.addScriptToEvaluateOnNewDocument</c>, which by definition only affects the <i>next</i>
    /// document. Evaluating in the current one would measure the browser before the patch, which is
    /// exactly what the first run of this test did.
    /// </summary>
    private static async Task<ChromiumBridge> LaunchPatchedAsync(string userAgent)
    {
        // R150: the launch size follows the agent, so a phone profile gets a phone-sized window and
        // outerHeight can agree with the screen it claims.
        var bridge = await ChromiumBridge.LaunchAsync(userAgent: userAgent);
        await bridge.ApplyStealthAsync(userAgent);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");

        // R159: navigation returns before the document is parsed. Measuring then reads a document that has no
        // root element yet — which is how this round's failure looked ("Cannot read properties of null") and had
        // nothing to do with the pin under test.
        for (var i = 0; i < 100; i++)
        {
            var state = await bridge.EvaluateAsync("document.readyState");
            if (state == "complete") break;
            await Task.Delay(50);
        }

        return bridge;
    }

    private const string IPhoneUserAgent =
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 " +
        "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1";

    /// <summary>
    /// The counts the challenge frame reads, before and after: Blink's five numbers become the phone's.
    /// </summary>
    [Fact]
    public async Task TheWebAssemblyCountsBecomeThePhones()
    {
        await using var bridge = await LaunchPatchedAsync(IPhoneUserAgent);

        const string counts =
            "JSON.stringify([WebAssembly, WebAssembly.Module.prototype, WebAssembly.Instance.prototype, " +
            "WebAssembly.Memory.prototype, WebAssembly.Table.prototype]" +
            ".map((o) => Object.getOwnPropertyNames(o).length))";

        var after = await bridge.EvaluateAsync(counts);
        _out.WriteLine($"after  {after}");

        Assert.Equal(JsonCounts(WebAssemblySurface.SafariCounts), after);

        // and the three JSPI names are gone from the constructor itself
        var jspi = await bridge.EvaluateAsync(
            "JSON.stringify(['Suspending','promising','SuspendError'].filter((n) => n in WebAssembly))");
        Assert.Equal("[]", jspi);

        // the two type-reflection methods exist and answer rather than throw
        var types = await bridge.EvaluateAsync(
            "JSON.stringify([typeof WebAssembly.Memory.prototype.type," +
            " typeof WebAssembly.Table.prototype.type," +
            " (function(){try{return WebAssembly.Memory.prototype.type().kind}catch(e){return 'threw'}})()])");
        _out.WriteLine($"types  {types}");
        Assert.Equal("[\"function\",\"function\",\"memory\"]", types);
    }

    /// <summary>Touch creation returns an event instead of throwing NotSupportedError.</summary>
    [Fact]
    public async Task TouchCreationReturnsAnEvent()
    {
        await using var bridge = await LaunchPatchedAsync(IPhoneUserAgent);

        var result = await bridge.EvaluateAsync(
            "(function(){try{const e=document.createEvent('TouchEvent');" +
            "return JSON.stringify([typeof e, e.type, e.touches.length, e.isTrusted]);}" +
            "catch(err){return 'threw:'+err.name;}})()");

        _out.WriteLine($"createEvent = {result}");
        Assert.Equal("[\"object\",\"\",0,false]", result);
    }

    /// <summary>The Screen reports the phone's keys, and the geometry is the phone's.</summary>
    [Fact]
    public async Task TheScreenAndGeometryAreThePhones()
    {
        await using var bridge = await LaunchPatchedAsync(IPhoneUserAgent);

        var keys = await bridge.EvaluateAsync("String(Object.getOwnPropertyNames(Screen.prototype).length)");
        _out.WriteLine($"Screen.prototype own names = {keys}");
        Assert.True(int.Parse(keys!) >= MobileSurface.ScreenOrder.Count);

        var shape = await bridge.EvaluateAsync(
            "JSON.stringify([screen.width, screen.height, devicePixelRatio, innerWidth, innerHeight, " +
            "outerWidth, outerHeight])");
        _out.WriteLine($"geometry = {shape}");

        // R150: all seven now agree, because the launch size follows the agent the profile claims.
        // Before this round outerHeight reported the host window's height (769) against a claimed 874,
        // which is exactly the impossibility the image's comment warns about.
        Assert.Equal("[402,874,3,402,684,402,874]", shape);

        // Blink's two extras are deleted, so a `for in` sweep sees the phone's shape
        var extras = await bridge.EvaluateAsync(
            "JSON.stringify(['isExtended','onchange'].filter((k) => k in Screen.prototype))");
        Assert.Equal("[]", extras);
    }

    /// <summary>The page-zoom ratio is exactly one and does not depend on the host layout.</summary>
    [Fact]
    public async Task TheZoomRatioIsExactlyOne()
    {
        await using var bridge = await LaunchPatchedAsync(IPhoneUserAgent);

        var ratio = await bridge.EvaluateAsync(
            "JSON.stringify((() => {\n" +
            "  const d = document.documentElement;\n" +
            "  if (!d) return ['no-documentElement', document.readyState];\n" +
            "  return [d.clientWidth, window.innerWidth, d.clientHeight, window.innerHeight];\n" +
            "})())");

        _out.WriteLine($"ratio inputs = {ratio}");
        Assert.Equal("[402,402,684,684]", ratio);

        // R151: the viewport itself reports the phone, which is the half the replica had left alone
        var viewport = await bridge.EvaluateAsync(
            "JSON.stringify([visualViewport.width, visualViewport.height, visualViewport.scale, " +
            "visualViewport.offsetTop, visualViewport.pageTop])");
        _out.WriteLine($"visualViewport = {viewport}");
        Assert.Equal("[402,684,1,0,0]", viewport);

        // R151: orientation is the browser's own, and that is a known incoherence rather than a choice
        // this replica is happy with. The image lists "orientation" in SCREEN_ORDER but never puts it in its
        // SCREEN value object, so it does not patch it either — and measured here it says
        // "landscape-primary" while the profile claims a portrait phone, because Chromium derives it from
        // the host display rather than the window. Pinning a value the image does not pin would be
        // inventing behaviour; leaving it unrecorded would hide a contradiction.
        var orientation = await bridge.EvaluateAsync(
            "JSON.stringify([screen.orientation.type, screen.orientation.angle])");
        _out.WriteLine($"orientation = {orientation} (native, unpatched — see R151 note)");
        Assert.True(orientation!.Contains("portrait-primary", System.StringComparison.Ordinal)
                    || orientation!.Contains("landscape-primary", System.StringComparison.Ordinal),
            "orientation is one of the two native values: " + orientation);
        Assert.DoesNotContain(MobileSurface.OrientationIsNative,
            string.Join(",", MobileSurface.VisualViewportFields));

        // a child element must still report its own box, so page geometry is untouched
        var child = await bridge.EvaluateAsync(
            "(function(){const d=document.createElement('div');d.style.width='50px';" +
            "document.body.appendChild(d);const w=d.clientWidth;d.remove();return String(w);})()");
        Assert.Equal("50", child);
    }

    /// <summary>
    /// R156: the engine members the payload reads — five plugins, the connection quartet, the two flags — are
    /// installed for every profile, because they are what a real Chromium reports.
    /// </summary>
    [Fact]
    public async Task TheEngineMembersAreInstalled()
    {
        await using var bridge = await LaunchPatchedAsync("Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36");

        var plugins = await bridge.EvaluateAsync(
            "JSON.stringify([navigator.plugins.length, Array.from(navigator.plugins).map((p) => p.name)," +
            " Array.from(navigator.plugins).map((p) => p.filename)])");
        _out.WriteLine($"plugins = {plugins}");
        Assert.StartsWith("[5,[\"PDF Viewer\",", plugins, System.StringComparison.Ordinal);
        Assert.Contains("internal-pdf-viewer", plugins, System.StringComparison.Ordinal);

        var connection = await bridge.EvaluateAsync(
            "JSON.stringify([navigator.connection.effectiveType, navigator.connection.rtt," +
            " navigator.connection.saveData, navigator.connection.downlink])");
        _out.WriteLine($"connection = {connection}");
        Assert.Equal("[\"4g\",50,false,10]", connection);

        var flags = await bridge.EvaluateAsync(
            "JSON.stringify([navigator.automationEnabled, screen.darkMode.enabled])");
        Assert.Equal("[false,false]", flags);

        // and a canvas hash is still something only the page can produce — nothing here claims otherwise
        Assert.True(PayloadCoverage.IsReadOnly("canvas-print-100-999"));
    }

    /// <summary>
    /// R160: a patched getter must answer <c>toString</c> like a native one, or it announces itself.
    /// </summary>
    [Fact]
    public async Task TheMaskedGettersLookNative()
    {
        await using var bridge = await LaunchPatchedAsync(IPhoneUserAgent);

        var masked = await bridge.EvaluateAsync(
            "JSON.stringify((() => {\n" +
            "  const d = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(navigator), 'plugins');\n" +
            "  const getter = d && d.get;\n" +
            "  const out = [];\n" +
            "  out.push(getter ? Function.prototype.toString.call(getter) : 'no-getter');\n" +
            "  out.push(Function.prototype.toString.call(Function.prototype.toString));\n" +
            "  const cd = Object.getOwnPropertyDescriptor(Element.prototype, 'clientWidth');\n" +
            "  out.push(cd && cd.get ? Function.prototype.toString.call(cd.get) : 'no-getter');\n" +
            "  return out;\n" +
            "})())");

        _out.WriteLine("masked = " + masked);

        // R169: plugins is native now, so its getter is the browser's own — still [native code], just not ours.
        Assert.Contains("[native code]", masked, System.StringComparison.Ordinal);
        Assert.DoesNotContain("no-getter", masked, System.StringComparison.Ordinal);

        // and the page's own functions must still print their source — the mask must not silence everything
        var user = await bridge.EvaluateAsync(
            "Function.prototype.toString.call(function named(x) { return x + 1; })");
        Assert.Contains("return x + 1", user, System.StringComparison.Ordinal);
        _out.WriteLine("user function still prints: " + user);
    }

    /// <summary>
    /// R161: walk the table in a real browser and ask every masked property what it says.
    ///
    /// <para>
    /// A row that answers source code is a patch announcing itself, so the assertion is per row rather than on a
    /// sample: nineteen getters and three functions, each one asked the same question a detector would ask.
    /// </para>
    /// </summary>
    [Fact]
    public async Task EveryTableRowLooksNative()
    {
        await using var bridge = await LaunchPatchedAsync(IPhoneUserAgent);

        var rows = string.Join(",", MaskTargets.Getters.Select(t => "['" + t.Owner + "','" + t.Property + "']"));
        var funcs = string.Join(",", MaskTargets.Functions.Select(t => "['" + t.Owner + "','" + t.Property + "']"));

        var report = await bridge.EvaluateAsync(
            "JSON.stringify((() => {\n" +
            "  const out = { getters: [], functions: [] };\n" +
            "  const say = (fn) => { try { return Function.prototype.toString.call(fn); } catch (e) { return 'err'; } };\n" +
            "  (" + rows + ").forEach(([ownerExpr, prop]) => {\n" +
            "    let owner = null;\n" +
            "    try { owner = eval(ownerExpr); } catch (e) {}\n" +
            "    const d = owner ? Object.getOwnPropertyDescriptor(owner, prop) : null;\n" +
            "    out.getters.push([prop, d && d.get ? say(d.get) : 'absent']);\n" +
            "  });\n" +
            "  (" + funcs + ").forEach(([ownerExpr, prop]) => {\n" +
            "    let owner = null;\n" +
            "    try { owner = eval(ownerExpr); } catch (e) {}\n" +
            "    const fn = owner ? owner[prop] : null;\n" +
            "    out.functions.push([prop, typeof fn === 'function' ? say(fn) : 'absent']);\n" +
            "  });\n" +
            "  return out;\n" +
            "})())");

        _out.WriteLine(report!);

        // every getter the table names is masked, or absent because the platform lacks the member
        Assert.NotNull(report);
        var parsed = Newtonsoft.Json.Linq.JObject.Parse(report!);
        foreach (var row in parsed["getters"]!)
        {
            var name = (string)row[0]!;
            var text = (string)row[1]!;
            Assert.True(text == "absent" || text.Contains("native code", System.StringComparison.Ordinal),
                $"{name} answers {text}");
        }

        foreach (var row in parsed["functions"]!)
        {
            var name = (string)row[0]!;
            var text = (string)row[1]!;
            Assert.True(text == "absent" || text.Contains("native code", System.StringComparison.Ordinal),
                $"{name} answers {text}");
        }
    }

    /// <summary>
    /// R162: the name and arity of every masked function, read the way a detector reads them.
    /// </summary>
    [Fact]
    public async Task EveryMaskedFunctionCarriesThePlatformsNameAndArity()
    {
        await using var bridge = await LaunchPatchedAsync(IPhoneUserAgent);

        var rows = string.Join(",", MaskTargets.Functions.Select(t => "['" + t.Owner + "','" + t.Property + "']"));

        var report = await bridge.EvaluateAsync(
            "JSON.stringify((() => {\n" +
            "  const out = [];\n" +
            "  (" + rows + ").forEach(([ownerExpr, prop]) => {\n" +
            "    let owner = null;\n" +
            "    try { owner = eval(ownerExpr); } catch (e) {}\n" +
            "    const fn = owner ? owner[prop] : null;\n" +
            "    out.push([prop, typeof fn === 'function' ? fn.name : 'absent',\n" +
            "              typeof fn === 'function' ? fn.length : -1]);\n" +
            "  });\n" +
            "  // a getter answers name 'get <prop>' and length 0\n" +
            "  const d = Object.getOwnPropertyDescriptor(navigator, 'plugins');\n" +
            "  out.push(['get plugins', d && d.get ? d.get.name : 'absent', d && d.get ? d.get.length : -1]);\n" +
            "  return out;\n" +
            "})())");

        _out.WriteLine(report!);

        var parsed = Newtonsoft.Json.Linq.JArray.Parse(report!);
        foreach (var row in parsed)
        {
            var name = (string)row[0]!;
            var actualName = (string)row[1]!;
            var length = (int)row[2]!;

            if (actualName == "absent") continue;

            Assert.Equal(name == "get plugins" ? "get plugins" : name, actualName);
            Assert.Equal(name == "get plugins" ? 0 : NativeArity.For(name)!.Value, length);
        }
    }

    /// <summary>
    /// R163: a phone profile must not have the Blink-only members at all, and a desktop profile must keep the one
    /// the payload reads.
    /// </summary>
    [Fact]
    public async Task ThePruneListAnswersPerProfile()
    {
        var names = string.Join(",", NavPrune.BlinkOnly.Select(n => "'" + n + "'"));

        await using (var phone = await LaunchPatchedAsync(IPhoneUserAgent))
        {
            // the list has to be an array literal: `(a, b, c).filter` is a comma expression, not three names
            var present = await phone.EvaluateAsync(
                "JSON.stringify([" + names + "].filter((n) => n in navigator))");
            _out.WriteLine("phone  leaves = " + present);

            // deviceMemory is the one the replica itself installs, so it is the interesting case
            Assert.DoesNotContain("deviceMemory", present!, System.StringComparison.Ordinal);
            Assert.DoesNotContain("connection", present!, System.StringComparison.Ordinal);
        }

        await using (var desktop = await LaunchPatchedAsync("Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                                                             "AppleWebKit/537.36 (KHTML, like Gecko) " +
                                                             "Chrome/157.0.0.0 Safari/537.36"))
        {
            var connection = await desktop.EvaluateAsync(
                "JSON.stringify([typeof navigator.connection, navigator.connection && " +
                "navigator.connection.effectiveType])");
            _out.WriteLine("desktop keeps = " + connection);
            Assert.StartsWith("[\"object\",\"4g\"]", connection, System.StringComparison.Ordinal);
        }
    }

    /// <summary>A Chromium profile gets an empty function, so the honest counts stay honest.</summary>
    [Fact]
    public async Task AChromiumProfileIsLeftAlone()
    {
        await using var bridge = await LaunchPatchedAsync("Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36");

        var jspi = await bridge.EvaluateAsync("String('Suspending' in WebAssembly)");
        _out.WriteLine($"JSPI present under a Chromium profile = {jspi}");
        Assert.Equal("true", jspi);

        var typeMethod = await bridge.EvaluateAsync("String(typeof WebAssembly.Memory.prototype.type)");
        Assert.Equal("undefined", typeMethod);
    }

    private static string JsonCounts(System.Collections.Generic.IReadOnlyList<int> counts) =>
        "[" + string.Join(",", counts) + "]";
}
