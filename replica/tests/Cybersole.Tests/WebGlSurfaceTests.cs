using System.Linq;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>R195: the WebGL parameters, measured against the table the target ships.</summary>
public sealed class WebGlSurfaceTests
{
    private readonly ITestOutputHelper _out;
    public WebGlSurfaceTests(ITestOutputHelper output) => _out = output;

    const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                          "Mobile/15E148 Safari/604.1";

    private static async Task<string?> ProbeAsync(string js)
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        return await bridge.EvaluateAsync(js);
    }

    private const string Probe =
        "(() => { const c = document.createElement('canvas'); const gl = c.getContext('webgl'); " +
        "if (!gl) return JSON.stringify(['no webgl']); " +
        "const ext = gl.getSupportedExtensions(); " +
        "const attrs = gl.getContextAttributes(); " +
        "return JSON.stringify([" +
        "gl.getParameter(gl.VERSION), " +
        "gl.getParameter(gl.RENDERER), " +
        "gl.getParameter(gl.VENDOR), " +
        "ext.length, ext[0], ext[ext.length - 1], " +
        "Object.keys(attrs).sort().join('|'), " +
        "('desynchronized' in attrs), ('xrCompatible' in attrs), " +
        "attrs.antialias, " +
        "gl.getParameter(1), " +                     // not a constant: the real implementation answers null
        "gl.getParameter(gl.MAX_TEXTURE_SIZE)]); })()";

    [Fact]
    public async Task TheParametersAreTheDevices()
    {
        var probe = await ProbeAsync(Probe);
        _out.WriteLine("webgl = " + probe);
        Assert.False(string.IsNullOrWhiteSpace(probe));

        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var r = doc.RootElement;

        var table = System.Text.Json.JsonDocument.Parse(WebGlTable.MetaJs);
        var extensions = table.RootElement.GetProperty("webgl").GetProperty("extensions")
            .EnumerateArray().Select(e => e.GetString()!).ToList();

        Assert.Equal(WebGlTable.WebGl1Extensions, r[3].GetInt32());
        Assert.Equal(extensions[0], r[4].GetString());
        Assert.Equal(extensions[^1], r[5].GetString());

        // the attributes are the device's eight, and no Blink-only key survives
        Assert.Equal(8, r[6].GetString()!.Split('|').Length);
        Assert.False(r[7].GetBoolean(), "desynchronized is still reported");
        Assert.False(r[8].GetBoolean(), "xrCompatible is still reported");

        // a non-constant falls through (the real implementation returns null for it), a constant answers
        Assert.Equal(System.Text.Json.JsonValueKind.Null, r[10].ValueKind);
        Assert.Equal(System.Text.Json.JsonValueKind.Number, r[11].ValueKind);
    }

    [Fact]
    public async Task TheRendererSaysApple()
    {
        // RENDERER/VENDOR are the plain ones; the UNMASKED pair behind WEBGL_debug_renderer_info is what hsw reads.
        var probe = await ProbeAsync(
            "(() => { const c = document.createElement('canvas'); const gl = c.getContext('webgl'); " +
            "if (!gl) return 'no webgl'; " +
            "const d = gl.getExtension('WEBGL_debug_renderer_info'); " +
            "const parts = [gl.getParameter(gl.RENDERER), gl.getParameter(gl.VENDOR), " +
            "gl.getParameter(gl.VERSION), gl.getParameter(gl.SHADING_LANGUAGE_VERSION)]; " +
            "if (d) { parts.push(gl.getParameter(d.UNMASKED_RENDERER_WEBGL)); " +
            "parts.push(gl.getParameter(d.UNMASKED_VENDOR_WEBGL)); } " +
            "return parts.join(' / '); })()");
        _out.WriteLine("renderer = " + probe);

        var table = System.Text.Json.JsonDocument.Parse(WebGlTable.ParamsJs).RootElement.GetProperty("webgl");
        var expected = new[]
        {
            table.GetProperty("7937").GetString()!,   // RENDERER
            table.GetProperty("7936").GetString()!,   // VENDOR
            table.GetProperty("7938").GetString()!,   // VERSION
            table.GetProperty("35724").GetString()!,  // SHADING_LANGUAGE_VERSION
            table.GetProperty("37446").GetString()!,  // UNMASKED_RENDERER_WEBGL
            table.GetProperty("37445").GetString()!,  // UNMASKED_VENDOR_WEBGL
        };

        Assert.Equal(string.Join(" / ", expected), probe);
    }

    [Fact]
    public void TheTablesAreVerbatim()
    {
        Assert.Equal(85, WebGlTable.WebGl1Params);
        Assert.Equal(135, WebGlTable.WebGl2Params);
        Assert.Equal(39, WebGlTable.WebGl1Extensions);
        Assert.Equal(36, WebGlTable.WebGl2Extensions);
        Assert.Contains("Apple GPU", WebGlTable.ParamsJs);
        Assert.Contains("ANGLE_instanced_arrays", WebGlTable.MetaJs);
        Assert.Equal(4, WebGlSurface.Patched.Length);
        Assert.Equal(2, WebGlSurface.Kinds.Length);
        Assert.Contains("largest hole", WebGlSurface.Rule);
        Assert.Contains("extra key", WebGlSurface.AttributeRule);
    }
}
