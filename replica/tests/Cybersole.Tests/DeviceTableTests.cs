using System.Reflection;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// The spoof script carries 29 device tables. These tests pin down what they say, so a future
/// edit that "cleans up" a value is caught.
///
/// Why these particular assertions: each is a fact about the captured device that a detector can
/// read back. A user agent with the wrong build number, a screen size that does not match the
/// viewport, or an Intl locale that disagrees with the navigator language are all mismatches a
/// real checker looks for — and all of them are easy to break by hand.
/// </summary>
public class DeviceTableTests
{
    private readonly ITestOutputHelper _out;
    public DeviceTableTests(ITestOutputHelper output) => _out = output;

    private static readonly Lazy<string> SpoofText = new(() =>
    {
        var asm = typeof(Cybersole.Core.Settings.GlobalSettings).Assembly;
        using var stream = asm.GetManifestResourceStream("Cybersole.Engine.hcaptcha-spoof.js");
        Assert.NotNull(stream);
        using var reader = new StreamReader(stream!);
        return reader.ReadToEnd();
    });

    private static string Table(string name)
    {
        // grab from `const NAME =` to the next column-0 or column-4 `const` declaration
        var m = Regex.Match(SpoofText.Value,
            @"\n\s{0,4}(?:const|let|var)\s+" + Regex.Escape(name) + @"\s*=");
        Assert.True(m.Success, $"table {name} not found");

        var rest = SpoofText.Value[m.Index..];
        var next = Regex.Match(rest[1..], @"\n\s{0,4}(?:const|let|var)\s+[A-Z]");
        return next.Success ? rest[..(next.Index + 1)] : rest;
    }

    [Fact]
    public void AllDeviceTablesArePresent()
    {
        string[] expected =
        {
            "PATCHES", "KNOWN", "INTL_NAMES", "MESSAGES", "ORDER", "WINDOW_ALL", "WINDOW_ENUM",
            "CSS_DECL", "NAV", "NAV_ORDER", "CRED_SHIM", "HANDLERS", "SCREEN", "SCREEN_ORDER",
            "QUERIES", "GEOMETRY", "GL_PARAMS", "GL_META", "FONTS", "FONTS_LOOSE", "CANVAS",
            "PROGRAMS", "BLINK_2X2", "DEVICE_2X2", "MEDIA", "CSS_PROPS", "INTL", "GLOBAL_KINDS",
            "VOICES",
        };

        var found = expected.Where(name => SpoofText.Value.Contains("const " + name)
                                           || SpoofText.Value.Contains("let " + name)).ToList();
        _out.WriteLine($"{found.Count}/{expected.Length} tables present");

        var missing = expected.Except(found).ToList();
        Assert.Empty(missing);
        Assert.Equal(29, expected.Length);
    }

    [Fact]
    public void NavigatorMatchesTheCapturedIosBuild()
    {
        var nav = Table("NAV");
        _out.WriteLine("userAgent: " + Regex.Match(nav, @"""userAgent"":\s*""([^""]+)""").Groups[1].Value);

        Assert.Contains("iPhone OS 27_0_1", nav);
        Assert.Contains("CriOS/156.0.8078.54", nav);
        Assert.Contains("\"platform\": \"iPhone\"", nav);
        Assert.Contains("\"hardwareConcurrency\": 4", nav);
        Assert.Contains("\"maxTouchPoints\": 5", nav);
        // a spoofed navigator must not claim webdriver
        Assert.Contains("\"webdriver\": false", nav);
    }

    [Fact]
    public void ScreenAndGeometryAgree()
    {
        var screen = Table("SCREEN");
        var geometry = Table("GEOMETRY");
        _out.WriteLine("screen: " + Regex.Match(screen, @"\{[^}]{0,160}").Value);
        _out.WriteLine("geometry: " + Regex.Match(geometry, @"\{[^}]{0,160}").Value);

        Assert.Contains("\"width\": 402", screen);
        Assert.Contains("\"height\": 874", screen);
        // the viewport must agree with the device, or the pair is internally inconsistent
        Assert.Contains("\"device-width\": 402", geometry);
        Assert.Contains("\"device-height\": 874", geometry);
    }

    [Fact]
    public void IntlLocaleIsDutch()
    {
        var intl = Table("INTL");
        _out.WriteLine("INTL: " + Regex.Match(intl, @"\{[^}]{0,160}").Value);

        // the captured device is a Dutch iPhone; a detector compares this against navigator.language
        Assert.Contains("\"locale\": \"nl-NL\"", intl);
    }

    [Fact]
    public void WindowListsCarryIosOnlyNames()
    {
        var all = Table("WINDOW_ALL");
        _out.WriteLine($"{all.Length} chars");
        _out.WriteLine("has gcrweb: " + all.Contains("gcrweb"));
        _out.WriteLine("has injected form handler: "
            + all.Contains("_injected_programmatic_form_submission_handler"));

        // these exist on iOS Chrome and nowhere else; a desktop-shaped window list is a tell
        Assert.Contains("gcrweb", all);
        Assert.Contains("_injected_programmatic_form_submission_handler", all);
    }

    [Fact]
    public void PixelTablesAreRgbaQuadruples()
    {
        foreach (var name in new[] { "BLINK_2X2", "DEVICE_2X2" })
        {
            var body = Table(name);
            var numbers = Regex.Matches(body, @"\d+").Select(m => int.Parse(m.Value)).ToList();
            _out.WriteLine($"{name}: {numbers.Count} values, first 8 = {string.Join(",", numbers.Take(8))}");

            // a 2x2 RGBA read is 16 bytes
            Assert.True(numbers.Count >= 16, $"{name} has only {numbers.Count} values");
            Assert.All(numbers.Take(16), v => Assert.InRange(v, 0, 255));
        }
    }

    [Fact]
    public void WebglTablesCoverBothContexts()
    {
        var parameters = Table("GL_PARAMS");
        var meta = Table("GL_META");

        // webgl and webgl2 report different parameter sets; both must be present
        Assert.Contains("\"webgl\"", parameters);
        Assert.Contains("\"webgl2\"", parameters);
        Assert.Contains("\"webgl\"", meta);
        Assert.Contains("\"webgl2\"", meta);
        Assert.Contains("extensions", meta);

        _out.WriteLine($"GL_PARAMS {parameters.Length} chars / GL_META {meta.Length} chars");
    }

    [Fact]
    public void CanvasTableHoldsAnActualPng()
    {
        var canvas = Table("CANVAS");
        _out.WriteLine("CANVAS head: " + canvas.Substring(0, Math.Min(120, canvas.Length)));

        Assert.Contains("data:image/png;base64,iVBORw0KGgo", canvas);
        // a blank canvas is a detection signal; the payload must be a real render
        Assert.True(canvas.Length > 400, $"canvas payload is only {canvas.Length} chars");
    }

    [Fact]
    public void CredentialShimDisguisesItsSource()
    {
        var shim = Table("CRED_SHIM");
        _out.WriteLine("CRED_SHIM: " + shim.Substring(0, Math.Min(200, shim.Length)));

        // the shim records the source text a detector would read back through toString
        Assert.Contains("\"src\"", shim);
        Assert.Contains("\"name\"", shim);
        Assert.Contains("\"length\"", shim);
    }
}
