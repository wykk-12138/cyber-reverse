using System.IO;
using System.Linq;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R207: the General panel, pinned to the running 5.18.32 build. The window shows, in this order:
/// Language, <b>Default Delays</b> (Default Monitor / Default Error / Default Timeout),
/// <b>Quicktask Settings</b> (Default Profiles / Default Proxies), <b>Shopify Settings</b>
/// (ATC Browser Proxy / Queue Presentation), Monitor Concurrency, Startup Page, Currency.
///
/// <para>
/// The two Quicktask fields existed on <c>GlobalSettings</c> from the start and the three locale keys existed too —
/// nothing rendered them. That is the same shape as the Nike caller id in R202: field present, label present, no UI.
/// </para>
/// </summary>
public sealed class GeneralSettingsLayoutTests
{
    private readonly ITestOutputHelper _out;
    public GeneralSettingsLayoutTests(ITestOutputHelper output) => _out = output;

    private static string Root()
    {
        var dir = new DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }

    private static string GeneralSource() => File.ReadAllText(Path.Combine(Root(),
        "src", "Cybersole.Ui", "Views", "Settings", "SettingsViews.cs"));

    [Fact]
    public void TheQuicktaskSectionIsOnThePanel()
    {
        var source = GeneralSource();

        Assert.Contains("\"Quicktask Settings\"", source, System.StringComparison.Ordinal);
        Assert.Contains("UiKit.Row(\"Default Profiles\"", source, System.StringComparison.Ordinal);
        Assert.Contains("UiKit.Row(\"Default Proxies\"", source, System.StringComparison.Ordinal);

        // the measured order: Default Delays, then Quicktask, then Shopify. Search for the TextBlock forms, not the
        // bare strings — the explanatory comment above the controls also names the section, and a bare search matches
        // it first (measured: quick@10064 < delays@10167).
        var delays = source.IndexOf("Text = \"Default Delays\"", System.StringComparison.Ordinal);
        var quick = source.IndexOf("Text = \"Quicktask Settings\"", System.StringComparison.Ordinal);
        var shopify = source.IndexOf("Text = \"Shopify Settings\"", System.StringComparison.Ordinal);

        Assert.True(delays >= 0 && quick > delays && shopify > quick,
            $"order is wrong: delays={delays} quick={quick} shopify={shopify}");
        _out.WriteLine($"delays@{delays} quick@{quick} shopify@{shopify}");
    }

    [Fact]
    public void TheSectionWritesTheFieldsItBinds()
    {
        var source = GeneralSource();

        Assert.Contains("s.QuickTaskProfiles =", source, System.StringComparison.Ordinal);
        Assert.Contains("s.QuickTaskProxies =", source, System.StringComparison.Ordinal);

        // "None" is index 0 on both combos, and picking it must clear the field rather than store the word
        Assert.Contains("quickProfiles.SelectedIndex <= 0", source, System.StringComparison.Ordinal);
        Assert.Contains("quickProxies.SelectedIndex <= 0", source, System.StringComparison.Ordinal);
    }

    [Fact]
    public void TheLabelsComeFromLocaleKeysThatExist()
    {
        var locale = File.ReadAllText(Path.Combine(Root(),
            "src", "Cybersole.Core", "Locales", "Cybersole.Locales.en.json"));

        // these four are the ones this round added UI for; they were already in the locale, which is why the
        // missing section was a UI gap and not a translation gap
        foreach (var key in new[]
                 {
                     "Settings.General.QuicktaskSettings",
                     "Settings.General.DefaultProfiles",
                     "Settings.General.DefaultProxies",
                     "Settings.General.ShopifySettings",
                 })
        {
            Assert.Contains(key, locale, System.StringComparison.Ordinal);
        }
    }

    [Fact]
    public void MonitorConcurrencyIsOneRowAndTheTwoInfoRowsStandAlone()
    {
        var source = GeneralSource();

        // measured: "[Maximum ▾] [3 max]" on the same line as the label, with an info marker
        Assert.Contains("ConcurrencyRow(concMode, concMax, concRatio)", source);
        Assert.DoesNotContain("UiKit.Row(\"Mode\"", source);
        Assert.DoesNotContain("UiKit.Row(\"Maximum\"", source);
        Assert.DoesNotContain("UiKit.Row(\"Ratio\"", source);

        // and Startup Page / Currency each get their own row, info-marked
        Assert.Contains("UiKit.Row(\"(i)  Startup Page\"", source);
        Assert.Contains("UiKit.Row(\"(i)  Currency\"", source);
        Assert.Contains("UiKit.Row(\"(i)  Monitor Concurrency\"", source);

        // the clock pair stays, but no longer shares a card with the two above
        Assert.Contains("UiKit.Row(\"Enable clock\"", source);
    }
}
