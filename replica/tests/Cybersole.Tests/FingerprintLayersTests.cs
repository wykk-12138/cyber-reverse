using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 131: three fingerprint layers, not one — and the correction to R130.
///
/// <para>
/// R130 read <c>Fingerprint.template.json</c> as the source of the browser fingerprint. The
/// fully-qualified resource name says otherwise:
/// <c>Cybersole.Core … Cybersole.Helpers.Dlpa.Fingerprint.template.json</c> — the <c>Dlpa</c>
/// namespace, whose payload is a <b>3-D Secure device profile</b>
/// (<c>browserColorDepth</c>, <c>browserScreenHeight/Width</c>, <c>browserTZ</c>,
/// <c>threeDSCompInd</c>, <c>challengeWindowSize</c> …), not a browser surface.
/// </para>
///
/// <para>
/// The browser surface is the eight-field class <see cref="BrowserFingerprint"/> covers; and between
/// them sits a named payload with two variants, <c>fingerprint-v1</c> and
/// <c>fingerprint-v1-sans-ua</c>.
/// </para>
/// </summary>
public sealed class FingerprintLayersTests
{
    private readonly ITestOutputHelper _out;

    public FingerprintLayersTests(ITestOutputHelper output) => _out = output;

    /// <summary>Three layers, named.</summary>
    [Fact]
    public void ThereAreThreeLayers()
    {
        Assert.Equal(3, FingerprintLayers.Layers.Count);
        foreach (var layer in FingerprintLayers.Layers) _out.WriteLine(layer);
    }

    /// <summary>The template belongs to the Dlpa namespace, not to the browser layer.</summary>
    [Fact]
    public void TheTemplateIsTheDlpaDeviceProfile()
    {
        Assert.Equal("Cybersole.Helpers.Dlpa.Fingerprint.template.json",
            FingerprintLayers.DlpaTemplateResource);

        Assert.Contains(".Dlpa.", FingerprintLayers.DlpaTemplateResource);
        Assert.DoesNotContain("browser", FingerprintLayers.DlpaTemplateResource,
            System.StringComparison.OrdinalIgnoreCase);
    }

    /// <summary>The DLPA field set is the 3-D Secure profile's, with the scheme's own spellings.</summary>
    [Fact]
    public void TheDlpaFieldsAreTheThreeDsProfile()
    {
        var fields = FingerprintLayers.DlpaFields;

        foreach (var name in new[]
                 {
                     "browserColorDepth", "browserScreenHeight", "browserScreenWidth", "browserTZ",
                     "browserLanguage", "browserUserAgent", "browserJavaEnabled",
                     "browserJavascriptEnabled", "threeDSCompInd", "challengeWindowSize",
                 })
            Assert.Contains(name, fields);

        Assert.Equal(12, fields.Count);
        foreach (var field in fields) _out.WriteLine(field);
    }

    /// <summary>The observed sample is on record, with its string-typed values.</summary>
    [Fact]
    public void TheObservedSampleIsRecorded()
    {
        Assert.Equal("24", FingerprintLayers.DlpaSample["browserColorDepth"]);
        Assert.Equal("1440", FingerprintLayers.DlpaSample["browserScreenHeight"]);
        Assert.Equal("5120", FingerprintLayers.DlpaSample["browserScreenWidth"]);
        Assert.Equal("-60", FingerprintLayers.DlpaSample["browserTZ"]);

        // the scheme wants strings, which is why the class has a formatter rather than an int
        Assert.Equal("30", FingerprintLayers.DlpaColorDepth(30));
    }

    /// <summary>Two payload variants, chosen by whether the caller already sends the UA.</summary>
    [Fact]
    public void ThePayloadHasTwoVariants()
    {
        Assert.Equal("fingerprint-v1", FingerprintLayers.PayloadFor(userAgentAlreadySent: false));
        Assert.Equal("fingerprint-v1-sans-ua", FingerprintLayers.PayloadFor(userAgentAlreadySent: true));

        Assert.True(FingerprintLayers.IsPayloadVariant("fingerprint-v1"));
        Assert.True(FingerprintLayers.IsPayloadVariant("fingerprint-v1-sans-ua"));
        Assert.False(FingerprintLayers.IsPayloadVariant("fingerprint-v2"));

        // the payload's own field names sit beside the variants in the pool
        foreach (var field in FingerprintLayers.PayloadFields) _out.WriteLine(field);
        Assert.Equal(7, FingerprintLayers.PayloadFields.Count);
    }

    /// <summary>The browser layer's eight fields are unchanged by this round.</summary>
    [Fact]
    public void TheBrowserLayerStillHasEightFields()
    {
        Assert.Equal(8, FingerprintLayers.BrowserFields.Count);
        Assert.Same(BrowserFingerprint.Fields, FingerprintLayers.BrowserFields);

        // and it is a different set from the DLPA one: no overlap, which is the point
        Assert.Empty(FingerprintLayers.BrowserFields.Intersect(FingerprintLayers.DlpaFields,
            System.StringComparer.OrdinalIgnoreCase));
    }
}
