using System.Reflection;
using Avalonia.Controls;
using Cybersole.Services;
using Cybersole.Ui.Views.Settings;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Settings shell parity, now pinned to the running 5.18.32 build rather than to a guess.
///
/// The nav was read straight off the live window through UI Automation (docs/GUI_BASELINE.md):
/// fourteen page entries in a specific order, an "ADVANCED" caption that opens a group rather
/// than a page, a version line above, and Log Out below.
///
/// The previous revision of this test asserted an `advanced` *page* and sorted the ids
/// alphabetically; both were wrong and the GUI proved it.
/// </summary>
public class SettingsShellTests
{
    /// <summary>Page entries, in the exact order the real rail shows them.</summary>
    private static readonly string[] LiveNavOrder =
    {
        "general", "appearance", "notifications", "webhooks", "email-accounts",
        "google-accounts", "paypal-accounts", "data",
        "captcha-providers", "cloudflare-solvers", "keyboard-shortcuts",
        "custom-stores", "custom-sizes", "payment", "help",
    };

    /// <summary>Titles exactly as the live build prints them (casing included).</summary>
    private static readonly (string Id, string Title)[] LiveTitles =
    {
        ("general", "General"),
        ("appearance", "Appearance"),
        ("notifications", "Notifications"),
        ("webhooks", "Webhooks"),
        ("email-accounts", "Email Accounts"),
        ("google-accounts", "Google Accounts"),
        ("paypal-accounts", "PayPal Accounts"),
        ("data", "Data"),
        ("captcha-providers", "Captcha Providers"),
        ("cloudflare-solvers", "Cloudflare Providers"),
        ("keyboard-shortcuts", "Keyboard Shortcuts"),
        ("custom-stores", "Custom Stores"),
        ("custom-sizes", "Custom Sizes"),
        ("payment", "Payment"),
        ("help", "Need Help?"),
    };

    /// <summary>View type names recovered from the binary's XAML inventory.</summary>
    private static readonly string[] RecoveredViewTypes =
    {
        "GeneralSettingsView", "AppearanceView", "CaptchaProvidersView", "CloudflareSolversView",
        "CustomSizesView", "CustomStoresView", "DataView", "ImapView", "GoogleAccountsView",
        "NotificationsView", "PaymentView", "PayPalAccountsView", "WebhookView", "KeyBindsView",
        "HelpView", "SettingsShell",
    };

    [Fact]
    public void NavOrderMatchesTheLiveRail()
    {
        var ids = SettingsShell.Sections.Select(s => s.Id).ToList();
        Assert.Equal(LiveNavOrder, ids);
    }

    [Fact]
    public void NavTitlesMatchTheLiveCasing()
    {
        foreach (var (id, title) in LiveTitles)
        {
            var section = SettingsShell.Sections.FirstOrDefault(
                s => string.Equals(s.Id, id, StringComparison.OrdinalIgnoreCase));

            Assert.True(section is not null, $"nav entry '{id}' is missing");
            Assert.Equal(title, section!.Title);
        }
    }

    [Fact]
    public void AdvancedIsAGroupCaptionNotAPage()
    {
        // The live build prints "ADVANCED" as a caption above Captcha Providers. It is not
        // navigable, so it must not appear as a section.
        Assert.DoesNotContain(SettingsShell.Sections,
            s => string.Equals(s.Id, "advanced", StringComparison.OrdinalIgnoreCase));

        var grouped = SettingsShell.Sections.Where(s => s.Group is not null).ToList();
        Assert.Single(grouped);
        Assert.Equal("captcha-providers", grouped[0].Id);
        Assert.Equal("ADVANCED", grouped[0].Group);
    }

    [Fact]
    public void TheVersionLineIsShown()
    {
        Assert.Equal("5.18.32", SettingsShell.DisplayVersion);
    }

    // Round 179 removed LogoutAndUpdateAreWired. It read:
    //
    //     var fired = 0;
    //     shell.LogoutRequested += (_, _) => fired++;
    //     shell.UpdateRequested += (_, _) => fired++;
    //     // both events must exist; firing them is the window's job, not the shell's
    //     Assert.Equal(0, fired);
    //
    // It subscribed to two events, never raised them, and asserted the counter was still zero —
    // a tautology that passes for any implementation, including one where the events do nothing.
    // Worse, those `+=` lines were the only subscriptions in the repository, which is why
    // UnsubscribedEventsTests did not report UpdateRequested earlier: it scans src/, correctly,
    // and the events looked listened-to from anywhere that scanned the whole tree.
    //
    // The events themselves are gone — SettingsShell's buttons do the work directly. What can be
    // asserted without a UI thread is that the version string is the one the build carries:

    [Fact]
    public void DisplayVersionMatchesTheAssemblyVersion()
    {
        var asm = typeof(Cybersole.Ui.Views.Settings.SettingsShell).Assembly;
        var info = asm.GetName().Version;

        Assert.NotNull(info);
        Assert.StartsWith($"{info!.Major}.{info.Minor}.{info.Build}", SettingsShell.DisplayVersion,
            StringComparison.Ordinal);
    }

    [Fact]
    public void NavIdsAreUnique()
    {
        var ids = SettingsShell.Sections.Select(s => s.Id).ToList();
        Assert.Equal(ids.Count, ids.Distinct(StringComparer.OrdinalIgnoreCase).Count());
    }

    [Fact]
    public void EveryRecoveredViewTypeExists()
    {
        var assembly = typeof(SettingsShell).Assembly;
        foreach (var name in RecoveredViewTypes)
        {
            var type = assembly.GetTypes().FirstOrDefault(t => t.Name == name);
            Assert.True(type is not null, $"view type '{name}' not found");
            Assert.True(typeof(UserControl).IsAssignableFrom(type), $"{name} is not a UserControl");
        }
    }

    [Fact]
    public void EverySectionBuildsAControl()
    {
        using var services = TestServices.Create();
        foreach (var (id, view) in SettingsShell.BuildAll(services))
        {
            Assert.True(view is not null, $"section '{id}' built null");
            Assert.IsAssignableFrom<UserControl>(view);
        }
    }

    [Fact]
    public void ShellDefaultSectionIsGeneral()
    {
        using var services = TestServices.Create();
        var shell = new SettingsShell(services);
        Assert.Equal("general", shell.CurrentSection);
    }

    [Fact]
    public void NavigateSwitchesSection()
    {
        using var services = TestServices.Create();
        var shell = new SettingsShell(services, "webhooks");
        Assert.Equal("webhooks", shell.CurrentSection);

        shell.Navigate("data");
        Assert.Equal("data", shell.CurrentSection);
    }

    [Fact]
    public void NavigateIgnoresUnknownIds()
    {
        using var services = TestServices.Create();
        var shell = new SettingsShell(services);
        shell.Navigate("does-not-exist");
        Assert.Equal("general", shell.CurrentSection);
    }

    [Fact]
    public void SectionCountMatchesTheLiveRail()
    {
        Assert.Equal(LiveNavOrder.Length, SettingsShell.Sections.Count);
    }
}

/// <summary>Builds an <see cref="AppServices"/> isolated from the user's real settings.</summary>
internal static class TestServices
{
    public static AppServices Create(Action<Cybersole.Http.Stores.StoreRegistry, Cybersole.Core.Settings.GlobalSettings>? register = null) =>
        AppServices.Create(register);
}
