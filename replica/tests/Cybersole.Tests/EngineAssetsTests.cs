using System.Reflection;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// The engine's fourteen assets must be embedded under the live build's own names, and each must
/// still be the thing its name claims.
///
/// Round 134 carved them out of the single-file image by content signature rather than manifest
/// order, because the two disagree. These tests hold the result down: a wrong slice is caught by
/// the content assertions, not by the size.
/// </summary>
public class EngineAssetsTests
{
    private readonly ITestOutputHelper _out;
    public EngineAssetsTests(ITestOutputHelper output) => _out = output;

    private static readonly Assembly Core = typeof(Cybersole.Core.Settings.GlobalSettings).Assembly;

    private static string Read(string name)
    {
        using var stream = Core.GetManifestResourceStream(name);
        Assert.NotNull(stream);
        using var reader = new StreamReader(stream!);
        return reader.ReadToEnd();
    }

    private static IEnumerable<string> EngineResources() =>
        Core.GetManifestResourceNames().Where(n => n.StartsWith("Cybersole.Engine.", StringComparison.Ordinal));

    [Fact]
    public void AllFourteenAreEmbedded()
    {
        var found = EngineResources().OrderBy(x => x).ToList();
        _out.WriteLine($"engine resources: {found.Count}");
        foreach (var n in found) _out.WriteLine("  " + n);

        Assert.Equal(14, found.Count);
    }

    [Theory]
    [InlineData("Cybersole.Engine.Captcha.html", "g-recaptcha")]
    [InlineData("Cybersole.Engine.CaptchaEnterprise.html", "enterprise")]
    [InlineData("Cybersole.Engine.EmptySolver.html", "data:text/html;base64,")]
    [InlineData("Cybersole.Engine.Geetest.html", "initGeetest")]
    [InlineData("Cybersole.Engine.GeetestV4.html", "initGeetest4")]
    [InlineData("Cybersole.Engine.HCaptcha.html", "hcaptcha")]
    [InlineData("Cybersole.Engine.Question.html", "<input")]
    [InlineData("Cybersole.Engine.Turnstile.html", "turnstile")]
    [InlineData("Cybersole.Engine.Ynap.html", "ynap")]
    [InlineData("Cybersole.Engine.Popmart.html", "popmart")]
    public void EachPageLoadsTheVendorItsNameClaims(string resource, string signature)
    {
        var text = Read(resource);
        _out.WriteLine($"{resource}: {text.Length} chars, contains {signature} = {text.Contains(signature, StringComparison.OrdinalIgnoreCase)}");
        Assert.Contains(signature, text, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void CaptchaAndEnterpriseUseDifferentScripts()
    {
        // these two pages are adjacent in the image and easy to swap; v2 uses api.js, enterprise
        // uses enterprise.js, and the boundary between them is only 7 KB of overlap
        var standard = Read("Cybersole.Engine.Captcha.html");
        var enterprise = Read("Cybersole.Engine.CaptchaEnterprise.html");

        Assert.NotEqual(standard.Length, enterprise.Length);
        Assert.Contains("recaptcha/api.js", standard);
        Assert.Contains("recaptcha/enterprise.js", enterprise);
        _out.WriteLine($"standard {standard.Length} chars / enterprise {enterprise.Length} chars");
    }

    [Fact]
    public void GeetestV4UsesTheV4ScriptAndGeetestDoesNot()
    {
        var v3 = Read("Cybersole.Engine.Geetest.html");
        var v4 = Read("Cybersole.Engine.GeetestV4.html");

        Assert.Contains("gt4.js", v4);
        Assert.DoesNotContain("gt4.js", v3);
        _out.WriteLine($"v3 {v3.Length} chars / v4 {v4.Length} chars");
    }

    [Fact]
    public void CastleScriptCarriesItsPublishableKey()
    {
        var castle = Read("Cybersole.Engine.castle.js");
        _out.WriteLine($"castle.js: {castle.Length} chars, {castle.Split('\n').Length} lines");

        Assert.Contains("requireCastle", castle);
        Assert.Contains("initializeCastle(", castle);
        // the key the live build initialises Castle with
        Assert.Matches(@"initializeCastle\(""pk_[A-Za-z0-9]+""\)", castle);
    }

    [Fact]
    public void HcaptchaSpoofIsTheHandWrittenOne()
    {
        var spoof = Read("Cybersole.Engine.hcaptcha-spoof.js");
        var lines = spoof.Split('\n');
        var comments = lines.Count(l => l.TrimStart().StartsWith("//"));
        _out.WriteLine($"hcaptcha-spoof.js: {spoof.Length} chars, {lines.Length} lines, {comments} comment lines");
        _out.WriteLine($"comment density: {comments * 100.0 / lines.Length:0.0}%");

        // a minified library has almost no comment lines; this file is the project's own
        Assert.True(comments > 700, $"only {comments} comment lines — this does not look hand-written");
        Assert.Contains("WINDOW_BASELINE", spoof);
        Assert.Contains("nativeOwnNames", spoof);
    }

    [Fact]
    public void TrustDeviceScriptsAreTheTwoSigners()
    {
        var fm = Read("Cybersole.Engine.trustdevice.js");
        var botd = Read("Cybersole.Engine.trustdevice-botd.js");

        // one signs through _fmOpt, the other through _TDBotD; swapping them would still compile
        Assert.Contains("_fmOpt", fm);
        Assert.DoesNotContain("_TDBotD", fm);

        Assert.Contains("_TDBotD", botd);
        Assert.DoesNotContain("_fmOpt.sign", botd);

        // both take the path substitution the engine performs at runtime
        Assert.Contains("%path%", fm);
        Assert.Contains("%path%", botd);

        _out.WriteLine($"trustdevice {fm.Length} chars / botd {botd.Length} chars");
    }
}
