using System.Linq;
using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R383: the field names the running build actually writes to %APPDATA%\\Cybersole, pinned so a rename cannot slip by.
///
/// <para>
/// These lists were read out of the live application's own JSON on 2026-11-14 — settings.json (43 top-level keys),
/// tasks.json (one TaskGroup) and solvers.json (one Solver plus its SolverSettings). They are the hardest evidence in this
/// project: the program wrote them itself. The test asserts each name still resolves to a member, so a property renamed in
/// the replica fails here instead of silently diverging from what the original persists.
/// </para>
/// </summary>
public sealed class LiveSchemaPinsTests
{
    private readonly ITestOutputHelper _out;
    public LiveSchemaPinsTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheSettingsFileFieldsAllExist()
    {
        // R390: 44 keys, read from a backup the ORIGINAL wrote (compact camelCase; this replica wrote indented files until
        // R388, so the compact backup cannot be ours). The earlier version of this test used a settings.json the replica
        // itself had written — that file listed 43 keys and was missing the five credential-ish ones below.
        var names = new[]
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

        // R927: the list above is file keys, read from a backup the original wrote, so the comparison has to be against
        // the name each property serialises to rather than against the property itself. StartupPage and the file's
        // "startup" are the same member under two names -- a binding names the first, the file holds the second -- and
        // comparing property names made that legitimate pair look like a missing key.
        var props = typeof(GlobalSettings).GetProperties()
            .Select(p => (p.GetCustomAttributes(typeof(Newtonsoft.Json.JsonPropertyAttribute), true)
                              .OfType<Newtonsoft.Json.JsonPropertyAttribute>()
                              .FirstOrDefault()?.PropertyName ?? p.Name).ToLowerInvariant())
            .ToHashSet();
        var missing = names.Where(n => !props.Contains(n.ToLowerInvariant())).ToList();

        _out.WriteLine($"{names.Length} live keys, missing: {missing.Count}");
        Assert.Empty(missing);
    }

    [Fact]
    public void TheTaskGroupFileFieldsAllExist()
    {
        var names = new[]
        {
            "id", "name", "running", "linkedDelays", "pinned", "captchaSource", "webhooks",
            "totalCheckouts", "totalDeclines", "tasks"
        };

        var props = typeof(TaskGroup).GetProperties().Select(p => p.Name.ToLowerInvariant()).ToHashSet();
        var missing = names.Where(n => !props.Contains(n.ToLowerInvariant())).ToList();

        _out.WriteLine($"{names.Length} live keys, missing: {missing.Count}");
        Assert.Empty(missing);
    }

    [Fact]
    public void TheSolverFileFieldsAllExist()
    {
        var solver = new[]
        {
            "name", "view", "reload", "settings"
        };

        var settings = new[]
        {
            "autoBoundingBox", "autoTickBox", "autoCanvas", "questionSharing", "autoClick",
            "reCaptchaSegmentation", "reCaptchaMultiClassification"
        };

        var solverProps = typeof(Solver).GetProperties().Select(p => p.Name.ToLowerInvariant()).ToHashSet();
        var settingsProps = typeof(SolverSettings).GetProperties().Select(p => p.Name.ToLowerInvariant()).ToHashSet();

        Assert.Empty(solver.Where(n => !solverProps.Contains(n.ToLowerInvariant())).ToList());
        Assert.Empty(settings.Where(n => !settingsProps.Contains(n.ToLowerInvariant())).ToList());
        _out.WriteLine($"{solver.Length} + {settings.Length} live keys, all present");
    }

    [Fact]
    public void TheBackupFileUsesTheImagesKeyNames()
    {
        // R385: assert the file that would actually be written, not the attribute names — the project serialises with
        // Newtonsoft, so a System.Text.Json attribute here would have passed this test while writing different keys.
        var live = new[]
        {
            "proxies", "billing", "accounts", "solvers", "settings", "tasks",
            "smartActions", "smartActionUtilities", "analytics",
        };

        var json = Newtonsoft.Json.JsonConvert.SerializeObject(
            new Cybersole.Core.Store.BackupDocument(), Cybersole.Core.Store.Json.Default);

        var written = Newtonsoft.Json.Linq.JObject.Parse(json).Properties().Select(p => p.Name).ToList();

        _out.WriteLine(string.Join(", ", written.OrderBy(x => x)));
        Assert.Equal(live.OrderBy(x => x), written.OrderBy(x => x));
    }


    private static List<string> WrittenKeys(object document) =>
        Newtonsoft.Json.Linq.JObject
            .Parse(Newtonsoft.Json.JsonConvert.SerializeObject(document, Cybersole.Core.Store.Json.Default))
            .Properties().Select(p => p.Name).OrderBy(n => n).ToList();

    [Fact]
    public void TheSmallerDocumentsAlsoUseTheImagesKeyNames()
    {
        // each pair is (live top-level keys, a fresh instance of the replica's document type)
        var pairs = new (string[] Live, object Doc)[]
        {
            (new[] { "accountGroups", "payPal", "google", "imap", "aycdInbox" },
                new Cybersole.Core.Models.AccountsDocument()),
            (new[] { "proxies" }, new Cybersole.Core.Models.AnalyticsDocument()),
            (new[] { "actions", "templates" }, new Cybersole.Core.Models.SmartActionsDocument()),
            (new[] { "groups" }, new Cybersole.Core.Models.SmartActionUtilitiesDocument()),
        };

        foreach (var (live, doc) in pairs)
        {
            var written = WrittenKeys(doc);
            _out.WriteLine(doc.GetType().Name + ": " + string.Join(", ", written));
            Assert.Equal(live.OrderBy(x => x), written);
        }
    }

    [Fact]
    public void TheGroupFilesCarryAtLeastTheImagesFields()
    {
        // billing.json and proxies.json are arrays of groups; the image writes a subset of what the replica models, so the
        // test asks that every image field is present and leaves the replica's extras (order, maxUsage, …) alone.
        var billing = new[] { "id", "name", "profiles" };
        var proxies = new[] { "id", "name", "order", "behaviour", "proxies", "totalDownload", "totalUpload" };

        var billingKeys = WrittenKeys(new Cybersole.Core.Models.BillingGroup());
        var proxyKeys = WrittenKeys(new Cybersole.Core.Models.ProxyGroup());

        _out.WriteLine("BillingGroup: " + string.Join(", ", billingKeys));
        _out.WriteLine("ProxyGroup:   " + string.Join(", ", proxyKeys));

        Assert.Empty(billing.Except(billingKeys));
        Assert.Empty(proxies.Except(proxyKeys));
    }

    [Fact]
    public void TheReplicaNeverWritesIntoTheOriginalsDataDirectory()
    {
        // R387: this was true until today, which both endangered the user's live configuration and made every
        // "does my file match the original's?" check circular.
        var replica = Cybersole.Core.Store.AppPaths.DataRoot;
        var original = Cybersole.Core.Store.AppPaths.OriginalDataRoot;

        _out.WriteLine("replica:  " + replica);
        _out.WriteLine("original: " + original);

        Assert.NotEqual(
            original.TrimEnd('\\', '/'),
            replica.TrimEnd('\\', '/'),
            StringComparer.OrdinalIgnoreCase);
    }

    [Fact]
    public void TheOriginalBackupFieldsAllExistOnTheModels()
    {
        // R389: this list comes from a backup the ORIGINAL wrote (compact camelCase bytes — this replica wrote indented
        // files until R388, so a compact backup cannot be ours). Extras on the replica side are allowed; a missing image
        // field is not.
        var group = new[]
        {
            "id", "name", "order", "usagePeriod", "usageExpiry", "checkoutLimit", "profileLimit", "monitorDelay",
            "retryDelay", "timeout", "linkedDelays", "pinned", "captchaSource", "cloudflareSolver", "webhooks", "tasks",
        };

        var proxyGroup = new[]
        {
            "id", "name", "order", "maxUsage", "behaviour", "usagePeriod", "usageExpiry", "proxies",
        };

        var solverDoc = new[] { "left", "top", "width", "height", "solvers" };

        void Check(string what, Type type, string[] fields)
        {
            var props = type.GetProperties().Select(p => p.Name.ToLowerInvariant()).ToHashSet();
            // both sides case-folded: the image writes camelCase, C# properties are PascalCase
            var missing = fields.Where(f => !props.Contains(f.ToLowerInvariant())).ToList();
            _out.WriteLine($"{what}: {fields.Length} fields, missing: {missing.Count}");
            Assert.Empty(missing);
        }

        Check("TaskGroup", typeof(TaskGroup), group);
        Check("ProxyGroup", typeof(ProxyGroup), proxyGroup);
        Check("SolverView", typeof(SolverView), solverDoc);
    }

    [Fact]
    public void TheOriginalBackupsNestedObjectsMatchToo()
    {
        // R391: also from the original's own backup. Two of these were only ever guessed before:
        //  - accounts.aycdInbox is a flat object of five fields, not a list;
        //  - a solver document carries window geometry and a "solvers" list whose entries are proxy/filter/account/settings
        //    (Solver.Name / View / Reload are BOUND in the markup but not persisted — binding and persistence differ).
        var aycd = new[] { "apiKey", "templateId", "appGroup", "timeoutSeconds", "enabled" };
        var solverEntry = new[] { "proxy", "filter", "account", "settings" };

        void Check(string what, Type type, string[] fields)
        {
            var props = type.GetProperties().Select(p => p.Name.ToLowerInvariant()).ToHashSet();
            var missing = fields.Where(f => !props.Contains(f.ToLowerInvariant())).ToList();
            _out.WriteLine($"{what}: {fields.Length} fields, missing: {missing.Count}");
            Assert.Empty(missing);
        }

        Check("AycdInbox", typeof(Cybersole.Core.Models.AycdInbox), aycd);
        Check("Solver", typeof(Solver), solverEntry);
    }

    [Fact]
    public void EverythingTheReplicaWritesStaysUnderItsOwnDataRoot()
    {
        // R405: R387 let the replica write into the ORIGINAL's %APPDATA%\Cybersole. This test pins the consequence: every
        // writable path must sit under DataRoot (the replica's own directory), and the vendor's local install is not
        // reachable as a write target at all.
        var root = Cybersole.Core.Store.AppPaths.DataRoot.TrimEnd('\\', '/');

        foreach (var path in Cybersole.Core.Store.AppPaths.WritablePaths)
        {
            _out.WriteLine(path);
            Assert.StartsWith(root, path, StringComparison.OrdinalIgnoreCase);
        }

        Assert.DoesNotContain(
            Cybersole.Core.Store.AppPaths.LocalRoot,
            Cybersole.Core.Store.AppPaths.WritablePaths,
            StringComparer.OrdinalIgnoreCase);
    }
}
