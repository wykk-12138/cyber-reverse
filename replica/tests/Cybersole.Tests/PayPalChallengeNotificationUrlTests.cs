using Cybersole.Stores.Payments;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1147/R1148: the challenge callback base.
///
/// The 3DS family in <c>PayPalThreeDs</c> carried three of its four members; the fourth,
/// <c>…/notify-challenge-cmpl/</c> (0x147098688), turns out not to be a request target at all. The
/// image meets it once, as <c>sub_141CF6230(&amp;off_147098688, v9[9])</c>, and that helper builds a
/// string: allocate a builder, append both arguments, return the join. So the URL is joined with the
/// challenge id and handed to PayPal as <c>challenge_callback_url</c>.
/// </summary>
public sealed class PayPalChallengeCallbackBaseTests
{
    [Fact]
    public void TheBaseKeepsItsTrailingSlash()
    {
        Assert.Equal(
            "https://www.paypal.com/payment-authentication/threeds/v1/notify-challenge-cmpl/",
            PayPalThreeDs.NotifyChallengeCompleteUrl);
        Assert.EndsWith("/", PayPalThreeDs.NotifyChallengeCompleteUrl);
    }

    /// <summary>The join is a path segment, so the slash is what puts the id after a separator.</summary>
    [Fact]
    public void TheChallengeIdIsJoinedAsAPathSegment()
    {
        var basis = PayPalThreeDs.ChallengeCallbackBaseFor("ch-42");
        Assert.Equal(
            "https://www.paypal.com/payment-authentication/threeds/v1/notify-challenge-cmpl/ch-42",
            basis);
    }

    /// <summary>
    /// And the base is what the existing composer appends to: no '?' in it, so the separator is '?'.
    /// </summary>
    [Fact]
    public void TheComposerAppendsItsQueryToThatBase()
    {
        var basis = PayPalThreeDs.ChallengeCallbackBaseFor("ch-42");
        var url = PayPalThreeDs.ChallengeCallbackUrlFor(basis);
        Assert.Equal(basis + "?" + PayPalThreeDs.ChallengeCallbackFragment, url);
        // the fragment is verbatim, so the composed URL keeps the frozen "undefined" values
        Assert.Contains("state=undefined&code=undefined", url);
    }

    /// <summary>The method-side twin has no trailing slash, so the two must not be normalised together.</summary>
    [Fact]
    public void TheTwoSiblingsDifferInMoreThanTheirMiddleWord()
    {
        Assert.False(PayPalThreeDs.NotifyMethodCompleteUrl.EndsWith("/"));
        Assert.NotEqual(
            PayPalThreeDs.NotifyMethodCompleteUrl.Replace("method", "challenge"),
            PayPalThreeDs.NotifyChallengeCompleteUrl);
    }
}
