using Cybersole.Stores.Payments;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1147: the challenge-complete notification URL.
///
/// The 3DS family in <c>PayPalThreeDs</c> carried three of its four members — <c>init-challenge</c>,
/// <c>init-method</c> and <c>notify-method-cmpl</c> — while the image also carries
/// <c>…/notify-challenge-cmpl/</c> at 0x147098688. These facts pin the string, and the trailing slash
/// in particular, because the slashed and unslashed forms are different URLs.
/// </summary>
public sealed class PayPalChallengeNotificationUrlTests
{
    [Fact]
    public void TheChallengeNotificationKeepsItsTrailingSlash()
    {
        Assert.Equal(
            "https://www.paypal.com/payment-authentication/threeds/v1/notify-challenge-cmpl/",
            PayPalThreeDs.NotifyChallengeCompleteUrl);
        Assert.EndsWith("/", PayPalThreeDs.NotifyChallengeCompleteUrl);
    }

    /// <summary>The method-side twin has no trailing slash, so the two must not be normalised together.</summary>
    [Fact]
    public void TheTwoNotificationsDifferInMoreThanTheirMiddleWord()
    {
        Assert.Equal(
            "https://www.paypal.com/payment-authentication/threeds/v1/notify-method-cmpl",
            PayPalThreeDs.NotifyMethodCompleteUrl);
        Assert.False(PayPalThreeDs.NotifyMethodCompleteUrl.EndsWith("/"));
        Assert.NotEqual(
            PayPalThreeDs.NotifyMethodCompleteUrl.Replace("method", "challenge"),
            PayPalThreeDs.NotifyChallengeCompleteUrl);
    }

    [Fact]
    public void AllFourFamilyMembersShareTheirPrefix()
    {
        const string prefix = "https://www.paypal.com/payment-authentication/threeds/v1/";
        Assert.StartsWith(prefix, PayPalThreeDs.InitChallengeUrl);
        Assert.StartsWith(prefix, PayPalThreeDs.InitMethodUrl);
        Assert.StartsWith(prefix, PayPalThreeDs.NotifyMethodCompleteUrl);
        Assert.StartsWith(prefix, PayPalThreeDs.NotifyChallengeCompleteUrl);
    }
}
