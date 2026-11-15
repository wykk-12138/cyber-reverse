using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// A settings page that writes one collection while the feature reads another is a defect that
/// no compiler sees and no click reveals — the value saves fine, and simply is not there when
/// something looks for it.
///
/// Round 113 found the first instance: CaptchaProvidersView edited registry.Configs and saved
/// GlobalSettings.CaptchaProviders — two objects, no wire. Round 187 found the second:
/// CloudflareSolversView added to settings.CloudflareSolvers, while the task group's
/// "Cloudflare solver" dropdown reads _services.Captcha.Registry.Configs. A provider added on
/// that page could not be chosen where providers are chosen.
///
/// This pins the two write sites that must stay linked. It is a source check, not a behavioural
/// one: instantiating these pages needs a UI thread, and the failure being guarded is "the two
/// statements drifted apart in the source", which a source check sees directly.
/// </summary>
public class SettingsStorageLinkTests
{
    private readonly ITestOutputHelper _out;
    public SettingsStorageLinkTests(ITestOutputHelper output) => _out = output;

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;

        return dir?.FullName ?? string.Empty;
    }

    private static string Read(string relative)
    {
        var path = Path.Combine(RepoRoot(), relative.Replace('/', Path.DirectorySeparatorChar));
        Assert.True(File.Exists(path), $"{relative} not found");
        return File.ReadAllText(path);
    }

    /// <summary>
    /// The Add handler must write both. Searched as a block: the 1,600 characters after
    /// `s.CloudflareSolvers.Add` must mention the captcha registry, because that is where the
    /// reader looks.
    /// </summary>
    [Fact]
    public void AddingACloudflareProviderAlsoRegistersItAsACaptchaProvider()
    {
        var text = Read("src/Cybersole.Ui/Views/Settings/ProviderViews.cs");

        var write = text.IndexOf("s.CloudflareSolvers.Add", StringComparison.Ordinal);
        Assert.True(write >= 0, "CloudflareSolversView no longer adds to settings.CloudflareSolvers");

        // Locate the registry call by searching forward from the settings write, rather than
        // slicing a fixed-width window. R188 used 1600 characters; the Type line turned out to be
        // at 1619, so the test reported "typed cfsolver: False" on correct code. A character
        // count is not a boundary — find the call, then look at the call.
        var registryAt = text.IndexOf("Captcha.Registry.AddConfig", write, StringComparison.Ordinal);
        _out.WriteLine($"settings write at {write}, registry write at {registryAt} " +
                       $"({(registryAt < 0 ? -1 : registryAt - write)} chars later)");

        Assert.True(registryAt >= 0,
            "a provider added here is invisible to the task-group dropdown, which reads "
            + "Captcha.Registry.Configs — the round-113 defect in a new place");

        // the initialiser that follows this call
        var initialiser = text[registryAt..Math.Min(text.Length, registryAt + 400)];

        // Presence of the call is not enough: a config typed anything else sits in the registry
        // with no driver to claim it, and a later reader sees "it is in the registry" while the
        // Cloudflare path still cannot find it.
        var typed = initialiser.Contains("Type = \"cfsolver\"", StringComparison.Ordinal);
        _out.WriteLine($"the registered config is typed cfsolver: {typed}");

        Assert.True(typed, "the copy carries no Type, so no driver will claim it");
    }

    /// <summary>
    /// And the other direction: the dropdown must still read a registry, not a settings list that
    /// nothing populates. If someone "fixes" this by switching the dropdown to
    /// settings.CloudflareSolvers, the pairing above becomes meaningless.
    /// </summary>
    [Fact]
    public void TheTaskGroupDropdownStillReadsTheCaptchaRegistry()
    {
        var text = Read("src/Cybersole.Ui/Views/Tasks/TasksViews.cs");

        // R354: the dropdown now reads the bound property instead of the registry directly, so the guard follows the
        // shape: the combo takes CloudflareSolvers, and that property is what reads the captcha registry.
        var read = text.IndexOf("UiKit.Combo(CloudflareSolvers)", StringComparison.Ordinal);
        Assert.True(read >= 0,
            "the Cloudflare solver dropdown changed its source; update "
            + "AddingACloudflareProviderAlsoRegistersItAsACaptchaProvider to match");

        var property = text.IndexOf("public IReadOnlyList<string> CloudflareSolvers", StringComparison.Ordinal);
        Assert.True(property >= 0, "the bound CloudflareSolvers property is gone");

        var propertyBody = text[property..Math.Min(text.Length, property + 400)];
        Assert.Contains("_services.Captcha.Registry.Configs", propertyBody, StringComparison.Ordinal);

        // and the assignment must still land on the group's CloudflareSolver field
        var window = text[read..Math.Min(text.Length, read + 600)];
        Assert.Contains("CloudflareSolver", window, StringComparison.Ordinal);
    }

    /// <summary>
    /// Both settings pages exist as separate sections. If one disappears the pairing above is
    /// guarding a page nobody can reach.
    /// </summary>
    [Fact]
    public void BothSettingsSectionsAreStillRegistered()
    {
        var shell = Read("src/Cybersole.Ui/Views/Settings/SettingsShell.cs");

        foreach (var id in new[] { "captcha-providers", "cloudflare-solvers" })
        {
            var present = shell.Contains($"\"{id}\"", StringComparison.Ordinal);
            _out.WriteLine($"{id}: {present}");
            Assert.True(present, $"settings section {id} is gone");
        }
    }

    /// <summary>
    /// A setting with a locale key and a reader but no control is a value the user cannot change.
    ///
    /// R195: AutoOpen3DSLimit was exactly that — MainWindow read it to cap concurrent 3DS windows,
    /// the property had a setter, the default was 5, and no page offered it. The original exposes
    /// two fields on the payment page ("Auto Open 3DS" and "Max Open"); the replica had one.
    ///
    /// The locale dictionary is the evidence that a control is expected: a key named
    /// Settings.Payment.Xxx is a label somebody wrote for a field somebody meant to add.
    /// </summary>
    [Fact]
    public void EveryThreeDSecureSettingHasAControl()
    {
        var views = Read("src/Cybersole.Ui/Views/Settings/SettingsViews.cs");
        var locale = Read("src/Cybersole.Core/Locales/Cybersole.Locales.en.json");

        // The label the original shows, not the property name: a control is identified by what
        // the user reads, and guessing a local variable name from a property name was wrong once
        // already (AutoOpen3DS is held by a local called `auto3ds`).
        var labels = new (string Property, string Label)[]
        {
            ("AutoOpen3DS", "Auto Open 3DS"),
            ("AutoOpen3DSLimit", "Max Open"),
        };

        foreach (var (property, label) in labels)
        {
            var hasLocale = locale.Contains($"\"Settings.Payment.{property}\"", StringComparison.Ordinal);

            // the label appears as a row caption, and the property is written back on Save
            var row = views.Contains($"UiKit.Row(\"{label}\"", StringComparison.Ordinal);
            var saved = views.Contains($"s.{property} =", StringComparison.Ordinal);

            _out.WriteLine($"{property,-20} locale={hasLocale} row=\"{label}\" saved={saved}");

            Assert.True(hasLocale, $"{property} lost its locale label — the control has nothing to say");
            Assert.True(row, $"{property}: no UiKit.Row(\"{label}\") in SettingsViews");
            Assert.True(saved, $"{property} is displayed but never written back on Save");
        }
    }

    /// <summary>
    /// Round 51: the locale label and the settings field were two halves of one setting, each
    /// orphaned.
    ///
    ///   Settings.General.ATCBrowserProxy   "ATC Browser Proxy"   — a label with no field
    ///   GlobalSettings.ShopifyBrowserProxy                        — a field with no reader
    ///
    /// The label was one of the eight found in round 198. The field had been on GlobalSettings
    /// since it was written and nothing referenced it. They name the same thing: which proxy group
    /// add-to-cart goes through.
    ///
    /// The control is wired; the behaviour is not, because "when does add-to-cart swap proxies"
    /// is a question the binary has not answered yet. This test pins the wiring, and says so.
    /// </summary>
    [Fact]
    public void TheAtcBrowserProxyLabelAndFieldAreConnected()
    {
        var views = Read("src/Cybersole.Ui/Views/Settings/SettingsViews.cs");
        var locale = Read("src/Cybersole.Core/Locales/Cybersole.Locales.en.json");
        var settings = Read("src/Cybersole.Core/Settings/GlobalSettings.cs");

        var hasLocale = locale.Contains("\"Settings.General.ATCBrowserProxy\"", StringComparison.Ordinal);
        var hasField = settings.Contains("ShopifyBrowserProxy", StringComparison.Ordinal);
        var hasRow = views.Contains("UiKit.Row(\"ATC Browser Proxy\"", StringComparison.Ordinal);
        var hasSave = views.Contains("s.ShopifyBrowserProxy =", StringComparison.Ordinal);

        _out.WriteLine($"locale={hasLocale} field={hasField} row={hasRow} save={hasSave}");

        Assert.True(hasLocale, "the ATC Browser Proxy label is gone");
        Assert.True(hasField, "ShopifyBrowserProxy is gone from GlobalSettings");
        Assert.True(hasRow, "the label has no control again — this is the round-198 defect returning");
        Assert.True(hasSave, "the control is displayed but never written back on Save");
    }
}
