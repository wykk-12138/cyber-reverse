using Cybersole.Stores.Accounts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Google account linking. The live 5.18.32 Add Account dialog opens a real Google sign-in
/// page rather than taking an email and password, so the flow is: sign in, land on
/// myaccount.google.com, then read the identity off the page.
///
/// These cover the pure decision logic — the browser half needs a live Chrome and a real
/// account, which <see cref="KasadaLiveTests"/> already gates behind Speed=Slow.
/// </summary>
public class GoogleOAuthFlowTests
{
    [Theory]
    [InlineData("https://myaccount.google.com/?hl=en", true)]
    [InlineData("https://myaccount.google.com/personal-info", true)]
    [InlineData("https://accounts.google.com/signin", false)]
    [InlineData("https://accounts.google.com/v3/signin/challenge/pwd", false)]
    [InlineData(null, false)]
    public void SignedInIsDetectedFromTheLandingUrl(string? url, bool expected)
    {
        Assert.Equal(expected, GoogleOAuthFlow.LooksSignedIn(url));
    }

    [Theory]
    [InlineData("signed in as ada.lovelace@gmail.com", "ada.lovelace@gmail.com")]
    [InlineData("name@sub.domain.co.uk", "name@sub.domain.co.uk")]
    [InlineData("no address here", null)]
    public void EmailIsPulledOutOfFreeText(string text, string? expected)
    {
        Assert.Equal(expected, GoogleOAuthFlow.ExtractEmail(text));
    }

    [Fact]
    public void SignInUrlAndMarkerMatchTheLiveFlow()
    {
        Assert.Equal("https://accounts.google.com/signin", GoogleOAuthFlow.SignInUrl);
        Assert.Equal("myaccount.google.com", GoogleOAuthFlow.SignedInMarker);
    }

    [Fact]
    public void FailedLinksCarryAReason()
    {
        var timedOut = GoogleLinkResult.TimedOut();
        Assert.False(timedOut.Success);
        Assert.False(string.IsNullOrWhiteSpace(timedOut.Error));
        Assert.Null(timedOut.Account);

        var noIdentity = GoogleLinkResult.NoIdentity();
        Assert.False(noIdentity.Success);
        Assert.Contains("no email", noIdentity.Error, StringComparison.OrdinalIgnoreCase);
    }
}
