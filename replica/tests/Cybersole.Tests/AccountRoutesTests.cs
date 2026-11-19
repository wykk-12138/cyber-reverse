using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1257: the account routes the image carries, and the two the replica had assumed.
///
/// <para>
/// The reset route is the interesting one: the replica nested it under <c>account/</c> as <c>/account/recover</c>,
/// while the image's route is the hyphenated top-level <c>/account-passwordreset</c>. Those are not two spellings of
/// one thing — different segment structure, different router match — so the shape has to be recorded rather than
/// treated as a synonym.
/// </para>
/// </summary>
public sealed class AccountRoutesTests
{
    [Fact]
    public void ThePasswordResetRouteIsHyphenatedNotNested()
    {
        Assert.Equal("/account-passwordreset", AccountRoutes.PasswordReset);
        Assert.StartsWith("/account-", AccountRoutes.PasswordReset);
        Assert.DoesNotContain("/account/", AccountRoutes.PasswordReset);
    }

    [Fact]
    public void TheLoginRouteIsThePlainOne()
    {
        Assert.Equal("/account/login", AccountRoutes.Login);
        Assert.Equal("/customer/account/login", AccountRoutes.CustomerAccountLogin);
        Assert.Equal("/Account/User/Login", AccountRoutes.CamelUserLogin);
    }

    [Fact]
    public void TheQueryRoutesKeepTheirParameterNames()
    {
        Assert.Equal("/account/authorize?redirect_uri=", AccountRoutes.Authorize);
        Assert.Equal("/account/searchorder?orderNumber=", AccountRoutes.SearchOrder);
        Assert.Contains("orderNumber=", AccountRoutes.SearchOrder);
    }

    [Fact]
    public void TheMultipassRouteIsStoredAsARegexInTheImage()
    {
        Assert.Contains("[^", AccountRoutes.LoginMultipassPattern);
        Assert.StartsWith("/account/login/multipass/", AccountRoutes.LoginMultipassPattern);
    }

    [Fact]
    public void TheReturnUrlFragmentIsCarried()
    {
        Assert.Contains("returnUrl=/account/login", AccountRoutes.ReturnUrlFragment);
    }
}
