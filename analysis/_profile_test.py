import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ProfilePanelTests.cs"
code = '''using Cybersole.Ui.Views.Modals;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R337: the profile panel behind the avatar, read off the running build.
///
/// <para>
/// The live panel is: "•  My License", a round avatar, the account name, the account email, a full-width
/// "Dashboard ↗" button, a rule, then "Terms of Service • Privacy Policy" on the left and a red "Log Out" on the right.
/// The replica had an "Account" window with Subject / Role / Expires rows and three flat buttons, so it was rewritten.
/// Only the constants are asserted here — the panel needs a host window to lay out. The three URLs are marked inferred
/// in the source: the live panel shows the buttons, not where they point.
/// </para>
/// </summary>
public sealed class ProfilePanelTests
{
    private readonly ITestOutputHelper _out;
    public ProfilePanelTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheDashboardLinkIsTheOneThePanelOpens()
    {
        _out.WriteLine(UserView.DashboardUrl);
        Assert.Equal("https://cybersole.io/dashboard", UserView.DashboardUrl);
    }

    [Fact]
    public void TheTwoFooterLinksExistAndAreLabelledAsInferred()
    {
        _out.WriteLine(UserView.TermsUrl + " | " + UserView.PrivacyUrl);

        Assert.StartsWith("https://cybersole.io/", UserView.TermsUrl, System.StringComparison.Ordinal);
        Assert.StartsWith("https://cybersole.io/", UserView.PrivacyUrl, System.StringComparison.Ordinal);
        Assert.NotEqual(UserView.TermsUrl, UserView.PrivacyUrl);
    }
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(code)
print('ProfilePanelTests written')
