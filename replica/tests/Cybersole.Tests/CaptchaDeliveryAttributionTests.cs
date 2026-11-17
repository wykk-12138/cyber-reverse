using System.IO;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1018: the image's four captcha-delivery literals belong to DataDome, not to PerimeterX.
///
/// <para>
/// R998 found them and was right that they are in the image while px-captcha is not. It then attributed them to the
/// wrong vendor, and the branch order above hid it: a page naming "datadome" is caught one line earlier, so the only
/// page the mistake changed was a DataDome interstitial that names its host and not its vendor -- which is precisely
/// the page a CAPTCHA wall serves. That page was classified as PerimeterX and handed to the wrong solver.
/// </para>
/// </summary>
public sealed class CaptchaDeliveryAttributionTests
{
    private static string Flow() => File.ReadAllText(Path.Combine(RepoRoot(),
        "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

    /// <summary>The literal routes to DataDome, because that is whose host it is.</summary>
    [Fact]
    public void TheCaptchaDeliveryLiteralBelongsToDataDome()
    {
        var doc = Flow();

        Assert.Contains(
            "body.Contains(\"captcha-delivery\", StringComparison.OrdinalIgnoreCase) ? \"datadome\" :",
            doc.Replace("\r\n", "\n").Replace(" ", "  ").Replace("  ", " "));

        // and the perimeterx branch no longer claims it
        Assert.DoesNotContain(
            "body.Contains(\"captcha-delivery\", StringComparison.OrdinalIgnoreCase) ? \"perimeterx\"", doc);
    }

    /// <summary>PerimeterX keeps its own marker, which the image does not carry -- and says so.</summary>
    [Fact]
    public void PerimeterXKeepsItsOwnUnsupportedMarker()
    {
        var doc = Flow();
        Assert.Contains("body.Contains(\"px-captcha\", StringComparison.OrdinalIgnoreCase) ? \"perimeterx\"", doc);

        var audit = File.ReadAllText(Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Scripts", "VendorWiring.cs"));
        // the phrase is split across the source's string concatenation, so assert the half that is not
        Assert.Contains("literals to this vendor when they are DataDome's", audit);
    }

    /// <summary>
    /// The evidence the correction rests on: the image has DdInterstitialClient beside those literals, and DataDome's
    /// prefix is what ties the host to the vendor.
    /// </summary>
    [Fact]
    public void TheCorrectionRestsOnTheImagesOwnVendorPrefix()
    {
        var doc = Flow();
        Assert.Contains("DdInterstitialClient", doc);
        Assert.Contains("0x1435260cb", doc);
    }

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir?.FullName ?? System.AppContext.BaseDirectory;
    }
}
