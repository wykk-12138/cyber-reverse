using System.Linq;
using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R300: the image names its settings sections in <c>Settings.Nav.*</c> — sixteen of them. The replica had fifteen; the
/// missing one was <c>Advanced</c>, whose view existed but was never placed in the rail. This test pins the mapping so a
/// section cannot disappear again (and so the sixteenth cannot be dropped as "unused").
/// </summary>
public sealed class SettingsNavTests
{
    private readonly ITestOutputHelper _out;
    public SettingsNavTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// The sixteen <c>Settings.Nav.*</c> leaves in the image. Fifteen are pages; <c>Advanced</c> is the caption printed
    /// above Captcha Providers and is not navigable — R300 learned this the hard way when adding it as a page turned
    /// SettingsShellTests.AdvancedIsAGroupCaptionNotAPage red.
    /// </summary>
    private static readonly (string Image, string Id)[] Expected =
    {
        ("Appearance", "appearance"),
        ("CaptchaProviders", "captcha-providers"),
        ("CloudflareSolvers", "cloudflare-solvers"),
        ("CustomSizes", "custom-sizes"),
        ("CustomStores", "custom-stores"),
        ("Data", "data"),
        ("EmailAccounts", "email-accounts"),
        ("General", "general"),
        ("GoogleAccounts", "google-accounts"),
        ("KeyboardShortcuts", "keyboard-shortcuts"),
        ("NeedHelp", "help"),
        ("Notifications", "notifications"),
        ("PayPalAccounts", "paypal-accounts"),
        ("Payment", "payment"),
        ("Webhooks", "webhooks"),
    };

    [Fact]
    public void TheRailHasFifteenPagesAndTheAdvancedCaption()
    {
        var ids = SettingsShell.Sections.Select(s => s.Id).ToList();
        foreach (var id in ids) _out.WriteLine(id);

        Assert.Equal(15, ids.Count);
        // the sixteenth nav label is the caption, which lives on the section it heads
        Assert.Contains(SettingsShell.Sections, s => s.Group == "ADVANCED");
        Assert.Equal(15, ids.Distinct().Count());
        foreach (var (image, id) in Expected)
            Assert.True(ids.Contains(id), $"missing section for Settings.Nav.{image}: {id}");
    }

    [Fact]
    public void EverySectionBuildsAView()
    {
        // a section whose factory throws is a dead entry in the rail
        foreach (var section in SettingsShell.Sections)
        {
            _out.WriteLine($"{section.Id}: {section.Title}");
            Assert.False(string.IsNullOrWhiteSpace(section.Title));
        }
    }
}
