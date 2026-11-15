using Cybersole.Ui.Views.Accounts;
using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 74: the Settings pages that had never been visited, and the version number that had never
/// been checked.
///
/// <para>
/// Four pages were walked for the first time — General, Data, Webhooks and Captcha Providers. Three
/// of them are titled exactly as their nav entry, but the fourth is not: the rail says "Captcha
/// Providers" and the page says "3rd Party Captcha Providers", with its own subtitle. That is now
/// shell chrome (<see cref="SettingsShell.PageHeaders"/>), which is where the original puts it.
/// </para>
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class SettingsPagesTests
{
    private readonly ITestOutputHelper _out;

    public SettingsPagesTests(ITestOutputHelper output) => _out = output;

    /// <summary>The four headers that were read off the live build, word for word.</summary>
    [Fact]
    public void TheWalkedPagesCarryTheirOwnHeader()
    {
        foreach (var id in new[] { "general", "data", "webhooks", "captcha-providers" })
        {
            var (title, subtitle) = SettingsShell.PageHeaderFor(id);
            _out.WriteLine($"{id}: {title} / {subtitle}");
        }

        Assert.Equal(("General", "Profile, delays, and other general preferences"),
            SettingsShell.PageHeaderFor("general"));
        Assert.Equal(("Data", "Import, export and backup data"),
            SettingsShell.PageHeaderFor("data"));
        Assert.Equal(("Webhooks", "Receive real time notifications into your favorite services"),
            SettingsShell.PageHeaderFor("webhooks"));
        Assert.Equal(("3rd Party Captcha Providers",
                      "Add and configure 3rd party captcha solving services"),
            SettingsShell.PageHeaderFor("captcha-providers"));
    }

    /// <summary>
    /// The rail label and the page title disagree for Captcha Providers, and both are right. A
    /// future "unification" that made them equal would be wrong — the same shape as R68.
    /// </summary>
    [Fact]
    public void TheRailAndThePageDisagreeOnPurpose()
    {
        var rail = SettingsShell.Sections.Single(s => s.Id == "captcha-providers").Title;
        var page = SettingsShell.PageHeaderFor("captcha-providers").Title;

        _out.WriteLine($"rail={rail} page={page}");

        Assert.Equal("Captcha Providers", rail);
        Assert.Equal("3rd Party Captcha Providers", page);
        Assert.NotEqual(rail, page);
    }

    /// <summary>
    /// An unknown id falls back to itself and claims no subtitle.
    ///
    /// <para>
    /// R74 wrote this against <c>appearance</c>, which had not been walked yet. R75 swept the last
    /// eleven pages, so every real section now has a header and there is no unvisited page left to
    /// point at — the test had to move to a genuinely unknown id rather than be deleted.
    /// </para>
    /// </summary>
    [Fact]
    public void AnUnknownPageClaimsNoSubtitle()
    {
        var (title, subtitle) = SettingsShell.PageHeaderFor("does-not-exist");

        _out.WriteLine($"{title} / {subtitle ?? "<none>"}");

        Assert.Equal("does-not-exist", title);
        Assert.Null(subtitle);
    }

    /// <summary>
    /// The version the app prints is the version the code holds. R74 found them disagreeing: the
    /// shell had 5.18.32 (read off the GUI) while <c>AppVersion.Current</c> and the build property
    /// both said 5.18.28.
    /// </summary>
    [Fact]
    public void TheShellAndTheVersionConstantAgree()
    {
        _out.WriteLine($"shell={SettingsShell.DisplayVersion} app={Cybersole.Core.Store.AppVersion.Current}");
        Assert.Equal(Cybersole.Core.Store.AppVersion.Current, SettingsShell.DisplayVersion);
    }
}
