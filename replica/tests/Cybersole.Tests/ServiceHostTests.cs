using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 114: the third-party services under the store flows, recorded verbatim from the image.
///
/// <para>
/// Three of these are not storefronts, and the image names their purpose in adjacent properties,
/// which is why the code can say what they are instead of only where they are:
/// </para>
///
/// <list type="bullet">
/// <item><c>api.parallaxsystems.io/gen</c> is <c>GenEndpoint</c>, and <c>/holdcaptcha</c> is
/// <c>HoldCaptchaEndpoint</c> — a captcha service with a slot-holding call.</item>
/// <item><c>inbox-api.aycd.io/api/v1/{user/verify, tasks/mail/create, tasks/completed}</c> is the
/// AYCD inbox the Settings → IMAP page is about.</item>
/// <item>Google's geocode and Places calls are how an address field fills from a postcode.</item>
/// </list>
///
/// <para>
/// The storefinding one is Scheels: R103 recorded its Frontastic hub, and this round finds a
/// <b>second</b> API — <c>mobile-api.scheels.com/v5</c> with guest auth and products. A store with a
/// web hub and a mobile API is the same shape as the Demandware <c>App</c>/<c>Dw</c> split in R112.
/// </para>
/// </summary>
public sealed class ServiceHostTests
{
    private readonly ITestOutputHelper _out;

    public ServiceHostTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// Five services, and the total is the sum of the five lists — not a number typed here.
    ///
    /// <para>
    /// A hand-summed total was wrong twice in two rounds (eight, then nine, for a shared-step count;
    /// fourteen here, when the five lists add to thirteen). The assertion is therefore structural:
    /// the per-service counts are pinned, and the total has to agree with them.
    /// </para>
    /// </summary>
    [Fact]
    public void TheImageCarriesFiveServices()
    {
        Assert.Equal(5, ServiceHosts.Services.Count);

        Assert.Equal(2, ServiceHosts.ScheelsMobile.All.Count);   // R115 added /v5/Order/
        Assert.Equal(3, ServiceHosts.EndClothing.All.Count);
        Assert.Equal(3, ServiceHosts.AycdInbox.All.Count);
        Assert.Equal(2, ServiceHosts.ParallaxSystems.All.Count);
        Assert.Equal(3, ServiceHosts.GoogleMaps.All.Count);

        var summed = ServiceHosts.ScheelsMobile.All.Count + ServiceHosts.EndClothing.All.Count
                     + ServiceHosts.AycdInbox.All.Count + ServiceHosts.ParallaxSystems.All.Count
                     + ServiceHosts.GoogleMaps.All.Count;

        _out.WriteLine($"{ServiceHosts.All.Count} literals across five services");
        Assert.Equal(summed, ServiceHosts.All.Count);
        Assert.Equal(ServiceHosts.All.Count, ServiceHosts.All.Distinct().Count());

        foreach (var url in ServiceHosts.All) _out.WriteLine(url);
    }

    /// <summary>Scheels has both APIs — the hub from R103 and the mobile one found here.</summary>
    [Fact]
    public void ScheelsHasAMobileApiAsWellAsTheHub()
    {
        Assert.Equal("https://mobile-api.scheels.com/v5/auth/guest", ServiceHosts.ScheelsMobile.GuestAuth);
        Assert.Equal("https://mobile-api.scheels.com/v5/products/", ServiceHosts.ScheelsMobile.Products);

        // the Frontastic hub is a different host and still recorded by R103's table
        Assert.Contains(RetailApiFamilies.ScheelsFrontastic.All,
            u => u.StartsWith("https://apihub.scheels.com/frontastic/action/", System.StringComparison.Ordinal));

        Assert.NotEqual("mobile-api.scheels.com", "apihub.scheels.com");
        _out.WriteLine("two Scheels APIs: apihub (web hub) + mobile-api v5");
    }

    /// <summary>
    /// Round 115: the mobile API has three endpoints, and the app-side step names line up with them.
    ///
    /// <para>
    /// The mapping is a <b>name correlation</b> — <c>FindProductApp</c> ↔ <c>/v5/products/</c>,
    /// <c>SubmitOrderApp</c> ↔ <c>/v5/Order/</c>, <c>StartAppFast</c> ↔ <c>/v5/auth/guest</c> — and the
    /// code says so in <c>DualApi.Evidence</c>. It is recorded because it is the only bridge available
    /// between a step list and a host until a capture exists; it is labelled so nobody mistakes it for
    /// one.
    /// </para>
    /// </summary>
    /// <summary>
    /// Two endpoints, not three: R115's third was Nike's <c>/v5/Order/</c> appended to the Scheels
    /// base, and R127 removed it.
    /// </summary>
    [Fact]
    public void TheMobileApiHasTwoEndpoints()
    {
        Assert.Equal(2, ServiceHosts.ScheelsMobile.All.Count);
        Assert.Equal("https://mobile-api.scheels.com/v5/auth/guest", ServiceHosts.ScheelsMobile.GuestAuth);
        Assert.Equal("https://mobile-api.scheels.com/v5/products/", ServiceHosts.ScheelsMobile.Products);

        _out.WriteLine(string.Join(", ", ServiceHosts.ScheelsMobile.All));
    }

    /// <summary>The path that was misattributed belongs to Nike, and Nike now carries it.</summary>
    [Fact]
    public void TheOrderPathBelongsToNikeNotScheels()
    {
        Assert.Contains("nike.com", NikeEndpoints.OrderV5);
        Assert.Contains("/v5/Order/", NikeEndpoints.OrderV5);
        Assert.DoesNotContain("scheels", NikeEndpoints.OrderV5);

        // and nothing in the Scheels family mentions it any more
        Assert.All(ServiceHosts.ScheelsMobile.All,
            u => Assert.DoesNotContain("Order", u, System.StringComparison.OrdinalIgnoreCase));

        _out.WriteLine(NikeEndpoints.OrderV5);
    }

    /// <summary>Every app-side step maps onto one of the three, and every target is a real endpoint.</summary>
    [Fact]
    public void TheAppStepsMapOntoTheMobileEndpoints()
    {
        Assert.Equal(4, ServiceHosts.DualApi.AppSteps.Count);   // R127: SubmitOrderApp unmapped

        foreach (var (step, host) in ServiceHosts.DualApi.AppSteps)
        {
            _out.WriteLine($"{step,-18} → {host}");
            Assert.Contains(host, ServiceHosts.ScheelsMobile.All);
        }

        Assert.Equal(ServiceHosts.ScheelsMobile.GuestAuth,
            ServiceHosts.DualApi.AppSteps["StartAppFast"]);
        Assert.Equal(ServiceHosts.ScheelsMobile.Products,
            ServiceHosts.DualApi.AppSteps["FindProductApp"]);
        // SubmitOrderApp is unmapped: its R115 target was Nike's path, so the step waits for a capture
        Assert.False(ServiceHosts.DualApi.AppSteps.ContainsKey("SubmitOrderApp"));
    }

    /// <summary>The web-side steps map onto the Frontastic hub from R103.</summary>
    [Fact]
    public void TheWebStepsMapOntoTheHub()
    {
        Assert.Equal(7, ServiceHosts.DualApi.WebSteps.Count);

        foreach (var (step, host) in ServiceHosts.DualApi.WebSteps)
        {
            _out.WriteLine($"{step,-24} → {host}");
            Assert.Contains(host, RetailApiFamilies.ScheelsFrontastic.All);
        }
    }

    /// <summary>The map is labelled as a correlation, not a capture.</summary>
    [Fact]
    public void TheMapSaysWhatItIs()
    {
        var evidence = ServiceHosts.DualApi.Evidence;

        Assert.Contains("name correlation", evidence);
        Assert.Contains("no request capture", evidence);

        _out.WriteLine(evidence);
    }

    /// <summary>Parallax is a captcha service, and the property names prove it.</summary>
    [Fact]
    public void ParallaxIsACaptchaServiceWithASlotHold()
    {
        Assert.Equal("https://api.parallaxsystems.io/gen", ServiceHosts.ParallaxSystems.Gen);
        Assert.Equal("https://api.parallaxsystems.io/holdcaptcha",
            ServiceHosts.ParallaxSystems.HoldCaptcha);

        // the word "captcha" in the path is the evidence, not an inference
        Assert.Contains("holdcaptcha", ServiceHosts.ParallaxSystems.HoldCaptcha);
        Assert.Equal(2, ServiceHosts.ParallaxSystems.All.Count);
    }

    /// <summary>AYCD's three endpoints are the inbox page's three actions.</summary>
    [Fact]
    public void TheAycdInboxHasThreeActions()
    {
        Assert.Equal(3, ServiceHosts.AycdInbox.All.Count);
        Assert.Contains("/user/verify", ServiceHosts.AycdInbox.Verify);
        Assert.Contains("/tasks/mail/create", ServiceHosts.AycdInbox.CreateMail);
        Assert.Contains("/tasks/completed?group=", ServiceHosts.AycdInbox.Completed);

        // verify, create, poll — the order an inbox integration runs in
        _out.WriteLine(string.Join(" → ", ServiceHosts.AycdInbox.All));
    }

    /// <summary>Matching is exact — a lookalike host is not "known".</summary>
    [Fact]
    public void KnownIsAnExactMatch()
    {
        Assert.True(ServiceHosts.IsKnown(ServiceHosts.ScheelsMobile.GuestAuth));
        Assert.True(ServiceHosts.IsKnown(ServiceHosts.ParallaxSystems.HoldCaptcha));
        Assert.False(ServiceHosts.IsKnown("https://mobile-api.scheels.com/v5/nope"));
        Assert.False(ServiceHosts.IsKnown(null));
    }
}
