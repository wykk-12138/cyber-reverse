using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 105: the anti-bot vendors the image knows, read out of the string pool.
///
/// <para>
/// Six vendors, each with its own literals. The replica's captcha layer covers Turnstile /
/// reCAPTCHA / hCaptcha / Geetest — solver kinds — but has nothing for DataDome, PerimeterX, Akamai,
/// TrustDecision or per-store Kasada versions. Those are not captcha kinds; they are challenge
/// systems with their own handshakes.
/// </para>
///
/// <para>
/// The sharpest single fact is <c>datadome.cybersole.io/sensor</c>: the tool runs its <b>own</b>
/// DataDome sensor host rather than calling the vendor's SDK domain for sensor traffic. That is a
/// relay design, and it is why the literal sits next to <c>api-sdk.datadome.co/sdk/</c> in the same
/// pool — both are real, for different traffic.
/// </para>
/// </summary>
public sealed class AntiBotVendorTests
{
    private readonly ITestOutputHelper _out;

    public AntiBotVendorTests(ITestOutputHelper output) => _out = output;

    /// <summary>Six vendors, each with evidence, none empty.</summary>
    [Fact]
    public void TheImageKnowsSixVendors()
    {
        foreach (var vendor in AntiBotVendors.All)
            _out.WriteLine($"{vendor.Name}: {string.Join(", ", vendor.Evidence)}");

        Assert.Equal(6, AntiBotVendors.All.Count);
        Assert.Equal(6, AntiBotVendors.All.Select(v => v.Name).Distinct().Count());
        Assert.All(AntiBotVendors.All, v => Assert.NotEmpty(v.Evidence));

        foreach (var name in new[] { "DataDome", "PerimeterX", "Akamai", "Kasada", "TrustDecision", "Cloudflare" })
            Assert.True(AntiBotVendors.Knows(name), name);

        Assert.False(AntiBotVendors.Knows("hCaptcha"));
        Assert.False(AntiBotVendors.Knows(null));
    }

    /// <summary>The DataDome relay is first-party and coexists with the vendor SDK host.</summary>
    [Fact]
    public void TheDataDomeRelayIsFirstParty()
    {
        Assert.Equal("datadome.cybersole.io/", AntiBotVendors.DataDomeRelay);
        Assert.Equal("datadome.cybersole.io/sensor", AntiBotVendors.DataDomeSensor);
        Assert.Equal("api-sdk.datadome.co/sdk/", AntiBotVendors.DataDomeSdk);

        // the relay is not the vendor's domain
        Assert.DoesNotContain("datadome.co", AntiBotVendors.DataDomeRelay);
        Assert.Contains("cybersole.io", AntiBotVendors.DataDomeRelay);

        // both appear in the evidence set
        var evidence = AntiBotVendors.Evidence();
        Assert.Contains(AntiBotVendors.DataDomeRelay, evidence);
        Assert.Contains(AntiBotVendors.DataDomeSdk, evidence);
    }

    /// <summary>Kasada versions are per store — five headers, five distinct stores.</summary>
    [Fact]
    public void KasadaVersionsArePerStore()
    {
        _out.WriteLine(string.Join(", ", AntiBotVendors.KasadaVersionHeaders));

        Assert.Equal(5, AntiBotVendors.KasadaVersionHeaders.Count);
        Assert.Equal(5, AntiBotVendors.KasadaVersionHeaders.Distinct().Count());
        Assert.All(AntiBotVendors.KasadaVersionHeaders, h => Assert.EndsWith("-Kasada-Version", h));

        // five different prefixes — one shared version would be wrong for four of them
        var stores = AntiBotVendors.KasadaVersionHeaders
            .Select(h => h[..h.IndexOf("-Kasada-Version", System.StringComparison.Ordinal)])
            .Distinct()
            .ToList();
        Assert.Equal(5, stores.Count);
    }

    /// <summary>The Turnstile task name is a solver-service identifier, kept verbatim.</summary>
    [Fact]
    public void TheSolverTaskNameIsRecordedVerbatim()
    {
        Assert.Equal("AntiTurnstileTaskProxyLess", AntiBotVendors.TurnstileTaskName);
        Assert.Contains(AntiBotVendors.TurnstileTaskName, AntiBotVendors.Evidence()
            .Concat(new[] { AntiBotVendors.TurnstileTaskName }));
    }

    /// <summary>TrustDecision ships both a fingerprint SDK and a per-region endpoint.</summary>
    [Fact]
    public void TrustDecisionHasTwoRegions()
    {
        var evidence = AntiBotVendors.All.First(v => v.Name == "TrustDecision").Evidence;

        Assert.Contains("static.trustdecision.com/fra/botd.js", evidence);
        Assert.Contains("static.trustdecision.com/sg/botd.js", evidence);
        Assert.Contains("static.trustdecision.com/tdfp", evidence);

        _out.WriteLine("fra = Frankfurt, sg = Singapore");
    }
}
