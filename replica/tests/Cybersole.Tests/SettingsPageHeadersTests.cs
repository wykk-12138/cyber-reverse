using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 75: every Settings page now has its header, read off the live 5.18.32 build.
///
/// <para>
/// R74 walked four pages and R75 swept the other eleven in one pass of the rail. All fifteen have a
/// gear, a title and a one-line subtitle, and <b>three of them are titled differently from the rail
/// entry that opens them</b>:
/// </para>
///
/// <code>
/// Captcha Providers     ->  3rd Party Captcha Providers
/// Cloudflare Providers  ->  3rd Party Cloudflare Providers
/// Need Help?            ->  Get Help
/// </code>
///
/// <para>
/// Those three are the interesting ones. They are not inconsistencies to tidy away — they are what
/// the original prints, and each is asserted individually so a future "unification" has to delete a
/// test that says why.
/// </para>
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class SettingsPageHeadersTests
{
    private readonly ITestOutputHelper _out;

    public SettingsPageHeadersTests(ITestOutputHelper output) => _out = output;

    /// <summary>Every rail entry has a page header — no page falls back any more.</summary>
    [Fact]
    public void EverySectionHasAHeader()
    {
        var missing = SettingsShell.Sections
            .Where(s => !SettingsShell.PageHeaders.ContainsKey(s.Id))
            .Select(s => s.Id)
            .ToList();

        _out.WriteLine($"sections={SettingsShell.Sections.Count} headers={SettingsShell.PageHeaders.Count}");
        _out.WriteLine("missing: " + string.Join(",", missing));

        Assert.Empty(missing);
        Assert.Equal(SettingsShell.Sections.Count, SettingsShell.PageHeaders.Count);
    }

    /// <summary>Each subtitle is present and is not a repeat of the title.</summary>
    [Fact]
    public void EverySubtitleSaysSomethingElse()
    {
        foreach (var (id, header) in SettingsShell.PageHeaders)
        {
            _out.WriteLine($"{id}: {header.Title} / {header.Subtitle}");
            Assert.False(string.IsNullOrWhiteSpace(header.Subtitle), $"{id} has no subtitle");
            Assert.NotEqual(header.Title, header.Subtitle);
        }
    }

    /// <summary>The exact eleven titles and subtitles the R75 sweep read, word for word.</summary>
    [Theory]
    [InlineData("appearance", "Appearance", "Customize scrollbar appearance and sizing")]
    [InlineData("notifications", "Notifications", "Notifications and sounds")]
    [InlineData("email-accounts", "Email Accounts",
        "Add imap email accounts to automatically login to certain sites")]
    [InlineData("google-accounts", "Google Accounts",
        "Store Google accounts for easy access when using solvers")]
    [InlineData("paypal-accounts", "PayPal Accounts",
        "Store PayPal accounts for easy access when creating tasks")]
    [InlineData("cloudflare-solvers", "3rd Party Cloudflare Providers",
        "Add Cloudflare solving services, then pick one per task group")]
    [InlineData("keyboard-shortcuts", "Keyboard Shortcuts", "Edit and disable keyboard shortcuts")]
    [InlineData("custom-stores", "Custom Stores", "Add custom Shopify store presets for easy access")]
    [InlineData("custom-sizes", "Custom Sizes", "Add custom Shopify size presets for easy access")]
    [InlineData("payment", "Payment", "Configure advanced payment settings")]
    [InlineData("help", "Get Help", "Take a look at common errors or contact support")]
    public void TheSweptPagesCarryTheirOwnHeader(string id, string title, string subtitle)
    {
        Assert.Equal((title, subtitle), SettingsShell.PageHeaderFor(id));
    }

    /// <summary>
    /// The three rail/page title mismatches, asserted one by one. `RailAndPageDisagree` exists so
    /// the count is explicit: three, not "however many happen to differ today".
    /// </summary>
    [Theory]
    [InlineData("captcha-providers", "Captcha Providers", "3rd Party Captcha Providers")]
    [InlineData("cloudflare-solvers", "Cloudflare Providers", "3rd Party Cloudflare Providers")]
    [InlineData("help", "Need Help?", "Get Help")]
    public void TheRailAndThePageDisagreeOnPurpose(string id, string rail, string page)
    {
        var railTitle = SettingsShell.Sections.Single(s => s.Id == id).Title;

        _out.WriteLine($"{id}: rail={railTitle} page={SettingsShell.PageHeaderFor(id).Title}");

        Assert.Equal(rail, railTitle);
        Assert.Equal(page, SettingsShell.PageHeaderFor(id).Title);
        Assert.Equal(3, SettingsShell.RailAndPageDisagree.Count);
    }

    /// <summary>
    /// The per-page count captions. The original does not share one "{0} items" string: stores say
    /// "Presets", sizes say "Custom Sizes", and the three account pages say "Accounts".
    /// </summary>
    [Fact]
    public void TheCountCaptionsArePerPage()
    {
        Assert.Equal("0 Presets", SettingsShell.ListCountCaption("custom-stores", 0));
        Assert.Equal("0 Custom Sizes", SettingsShell.ListCountCaption("custom-sizes", 0));
        Assert.Equal("0 Accounts", SettingsShell.ListCountCaption("email-accounts", 0));
        Assert.Equal("0 Accounts", SettingsShell.ListCountCaption("google-accounts", 0));
        Assert.Equal("0 Accounts", SettingsShell.ListCountCaption("paypal-accounts", 0));

        _out.WriteLine("presets/sizes/accounts captions differ from one another, as they do live");
    }
}
