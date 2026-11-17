using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The names the original binds for payment selection, and the one R955 invented.
///
/// <para>
/// R956. R955 wired a payment dispatch keyed on a session variable called paymentGateway, and listed as Unknown whether
/// the original dispatched the same way. Searching for it found the real names: the backing field _paymentGateway, the
/// bound property _paymentGatewayName, a collection PaymentGateways, and paymentProvider. The descriptor
/// _captchaToken&lt;_paymentGatewayName6_paymentFlexibilityTemplate puts the captcha token and the gateway name next to
/// each other, which says a submission carries both.
/// </para>
///
/// <para>
/// The invented key was close enough to compile and close enough that a reader would not question it, which is exactly
/// the failure mode these rounds keep finding: a plausible name standing in for a searched one.
/// </para>
/// </summary>
public class PaymentGatewayNamingTests
{
    /// <summary>The two keys are the image's spellings, and they are not the invented one.</summary>
    [Fact]
    public void TheKeysAreTheImagesSpellings()
    {
        Assert.Equal("paymentGatewayName", StoreFlow.PaymentGatewayNameKey);
        Assert.Equal("captchaToken", StoreFlow.CaptchaTokenKey);

        Assert.NotEqual("paymentGateway", StoreFlow.PaymentGatewayNameKey);
    }

    /// <summary>
    /// R957 removed the fixed gateway array: the image fetches what a shop offers rather than keeping a list, so the
    /// constant that used to exist here must not come back.
    /// </summary>
    [Fact]
    public void TheGatewayCollectionIsNoLongerAConstant()
    {
        Assert.Null(typeof(StoreFlow).GetField("PaymentGateways",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static));
    }

    /// <summary>
    /// The dispatch reads the corrected key, so the wiring and the constant cannot drift apart.
    /// </summary>
    [Fact]
    public void TheDispatchUsesTheCorrectedKey()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.Contains("TryGetValue(StoreFlow.PaymentGatewayNameKey, out var named)", doc);
        Assert.Contains("R956 searched for how the original selects a gateway", doc);

        // and the recorded correction says what was wrong
        Assert.Contains("had been invented rather than searched for", doc);
    }

    /// <summary>The captcha token is recorded beside the gateway name because the image keeps them adjacent.</summary>
    [Fact]
    public void TheCaptchaTokenSitsBesideTheGateway()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.Contains("_captchaToken", doc);
        Assert.Contains("a token and a gateway, together", doc);
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(System.IO.Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}