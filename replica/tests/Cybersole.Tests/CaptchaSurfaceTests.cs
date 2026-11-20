using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1286: the five challenge surfaces the image ships as solver pages, and the classifier that reads them.
///
/// <para>
/// The literals asserted here are copied from the embedded pages (143ca6a9f, 143ca8507, 143cb2699, 147153cf4,
/// 146ab71b4). The point of the test is that <c>DetectAsync</c> can now say <em>which</em> captcha a page wants, not
/// only which wall is in the way — the two are independent, since a Cloudflare edge can serve a Turnstile.
/// </para>
/// </summary>
public sealed class CaptchaSurfaceTests
{
    [Fact]
    public void TheLoadersAreTheImagesOwn()
    {
        Assert.Equal("script[src*='js.hcaptcha.com/1/api.js']", CaptchaSurface.HCaptchaSelector);
        Assert.Equal("js.hcaptcha.com", CaptchaSurface.HCaptchaHost);
        Assert.Equal("https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback",
            CaptchaSurface.TurnstileLoader);
        // the placeholder is part of the literal: the page substitutes the sitekey at load time
        Assert.Equal("https://www.google.com/recaptcha/enterprise.js?render=%sitekey%",
            CaptchaSurface.EnterpriseLoader);
        Assert.Equal("/recaptcha/api2/anchor", CaptchaSurface.RecaptchaAnchorPath);
    }

    [Theory]
    [InlineData("<script src=\"https://js.hcaptcha.com/1/api.js\" async></script>", "hcaptcha")]
    [InlineData("<script src=\"https://challenges.cloudflare.com/turnstile/v0/api.js?onload=x\"></script>", "turnstile")]
    [InlineData("<script src=\"https://www.google.com/recaptcha/enterprise.js?render=k\"></script>", "recaptcha-enterprise")]
    [InlineData("<iframe src=\"/recaptcha/api2/anchor?k=1\"></iframe>", "recaptcha-v2")]
    [InlineData("grecaptcha.execute()", "recaptcha-v3")]
    [InlineData("<html>nothing here</html>", "none")]
    [InlineData(null, "none")]
    public void EachSurfaceIsRecognisedByItsLoader(string? body, string expected) =>
        Assert.Equal(expected, CaptchaSurface.Classify(body));

    /// <summary>
    /// The specific loaders beat the generic one: an Enterprise page also calls into <c>grecaptcha</c>, so testing the
    /// family first would file every Enterprise challenge as v3.
    /// </summary>
    [Fact]
    public void EnterpriseIsNotFiledAsV3()
    {
        const string page = "<script src=\"https://www.google.com/recaptcha/enterprise.js?render=k\"></script>" +
                            "<script>grecaptcha.enterprise.execute(k)</script>";

        Assert.Equal("recaptcha-enterprise", CaptchaSurface.Classify(page));
    }

    /// <summary>
    /// The checkpoint page switches on <c>Captcha.Type</c>: 0 clicks the checkbox, 1 runs the invisible execute.
    /// </summary>
    [Fact]
    public void TheTypeFieldMeansClickOrExecute()
    {
        Assert.Equal(0, CaptchaSurface.TypeInteractive);
        Assert.Equal(1, CaptchaSurface.TypeInvisibleExecute);
        Assert.True(CaptchaSurface.NeedsClick(CaptchaSurface.TypeInteractive));
        Assert.False(CaptchaSurface.NeedsClick(CaptchaSurface.TypeInvisibleExecute));
    }
}
