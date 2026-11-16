using System.Linq;
using System.Reflection;
using Cybersole.Core.Settings;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The reverse of <see cref="LiveSchemaPinsTests.TheSettingsFileFieldsAllExist"/>: properties that no recovered key names.
///
/// <para>
/// R928. The existing pin checks one direction — every key in the recovered backup has a property. Nothing checked the
/// other, and that direction is where a 1:1 violation would hide: a property the replica writes that the original does
/// not would produce a key the original's own files never carry.
/// </para>
///
/// <para>
/// Scoped to the <see cref="GlobalSettings"/> class body, the file holds forty-eight properties and the backup names
/// forty-four keys, so four are unmatched. Each is pinned below with the reason it is unmatched, because an unexplained
/// difference of four is indistinguishable from four bugs.
/// </para>
/// </summary>
public class SettingsUnmatchedMembersTests
{
    private static string[] RecoveredKeys()
    {
        var t = typeof(LiveSchemaPinsTests);
        // the key list is a local in that test, so it is restated here rather than reflected out of a method body;
        // the two must agree and TheTwoKeyListsAgree below checks that they do
        return new[]
        {
            "bearer", "license", "quickTaskProxies", "quickTaskProfiles", "monitorDelay", "retryDelay", "timeout",
            "shopifyBrowserProxy", "autoOpen3DS", "autoOpen3DSLimit", "browserPath", "browserLimit",
            "browserWindowMode", "browserProfiles", "browserProfileAssignment", "pinGroups", "startup", "keybinds",
            "notifications", "clock", "currency", "concurrency", "maxLogRetention", "maxLogSize", "backupInterval",
            "maxBackups", "smartactions", "betaUpdates", "taskGroupOrder", "proxyGroupOrder", "profileGroupOrder",
            "queuePresentation", "captchaProviders", "cloudflareSolvers", "webhooks", "notificationOptions",
            "keyBinds", "customStores", "customSizes", "monitorFilters", "scrollbarWidth", "scrollbarColor",
            "scrollbarCornerRadius", "language",
        };
    }

    private static string SerialisedName(PropertyInfo p) =>
        (p.GetCustomAttributes(typeof(Newtonsoft.Json.JsonPropertyAttribute), true)
              .OfType<Newtonsoft.Json.JsonPropertyAttribute>()
              .FirstOrDefault()?.PropertyName ?? p.Name).ToLowerInvariant();

    /// <summary>
    /// The four properties with no recovered key, pinned with why. Three name settings whose home is a nested object or
    /// a locale entry rather than a top-level key; the fourth is a contract member whose persistence is unknown.
    /// </summary>
    [Fact]
    public void TheUnmatchedMembersAreTheExpectedFourAndEachHasAReason()
    {
        var keys = RecoveredKeys().Select(k => k.ToLowerInvariant()).ToHashSet();
        var unmatched = typeof(GlobalSettings).GetProperties()
            .Where(p => !keys.Contains(SerialisedName(p)))
            .Select(p => p.Name)
            .OrderBy(n => n)
            .ToArray();

        Assert.Equal(new[] { "ClockFormat", "EnableClock", "MonitorConcurrency", "StoreGroups" }, unmatched);
    }

    /// <summary>
    /// EnableClock is the original's, not ours: R198 tied it to a locale entry named Settings.General.EnableClock with a
    /// tooltip. So the absence of a key for it says the backup predates it, not that the property is invented -- and
    /// that distinction is the whole reason this test exists.
    /// </summary>
    [Fact]
    public void EnableClockIsOriginalDespiteHavingNoKey()
    {
        var source = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Core", "Settings", "GlobalSettings.cs"));

        Assert.Contains("Settings.General.EnableClock", source);
        Assert.Contains("public bool EnableClock", source);
    }

    /// <summary>
    /// ClockFormat and StoreGroups are not in the binding contract at all, so they are replica members whose file
    /// representation is unknown rather than missing.
    /// </summary>
    [Fact]
    public void ClockFormatAndStoreGroupsAreNotInTheContract()
    {
        var contract = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "..", "analysis", "type_presence_triage.py"));

        Assert.DoesNotContain("ClockFormat", contract);
        Assert.DoesNotContain("StoreGroups", contract);
        Assert.Contains("MonitorConcurrency", contract);
    }

    /// <summary>
    /// MonitorConcurrency is the one that stays genuinely open: the contract lists it and the backup has no key for it,
    /// while concurrency is already taken by the nested ConcurrencySettings object. Pinned so the question cannot be
    /// lost.
    /// </summary>
    [Fact]
    public void MonitorConcurrencyIsAContractMemberWithNoKeyAndConcurrencyIsObject()
    {
        var props = typeof(GlobalSettings).GetProperties();

        var monitor = props.Single(p => p.Name == "MonitorConcurrency");
        var concurrency = props.Single(p => p.Name == "Concurrency");

        Assert.Equal(typeof(int), monitor.PropertyType);
        Assert.NotEqual(typeof(int), concurrency.PropertyType);
        Assert.Equal("concurrency", SerialisedName(concurrency));
        Assert.Equal("monitorconcurrency", SerialisedName(monitor));
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(System.IO.Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}