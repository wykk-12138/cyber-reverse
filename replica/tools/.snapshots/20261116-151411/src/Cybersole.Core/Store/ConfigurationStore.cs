using Cybersole.Core.Models;
using Cybersole.Core.Settings;

namespace Cybersole.Core.Store;

/// <summary>
/// Aggregates every on-disk document and owns the backup file format
/// (Backups/Backup &lt;date&gt;.cyb — plain JSON, as in the original).
/// </summary>
public sealed class ConfigurationStore
{
    private readonly JsonFileStore _settings = new(AppPaths.Settings);
    private readonly JsonFileStore _accounts = new(AppPaths.Accounts);
    private readonly JsonFileStore _tasks = new(AppPaths.Tasks);
    private readonly JsonFileStore _proxies = new(AppPaths.Proxies);
    private readonly JsonFileStore _billing = new(AppPaths.Billing);
    private readonly JsonFileStore _solvers = new(AppPaths.Solvers);
    private readonly JsonFileStore _analytics = new(AppPaths.Analytics);
    private readonly JsonFileStore _smartActions = new(AppPaths.SmartActions);

    public GlobalSettings Settings { get; private set; } = new();
    public AccountsDocument Accounts { get; private set; } = new();
    public List<TaskGroup> TaskGroups { get; private set; } = new();
    public List<ProxyGroup> ProxyGroups { get; private set; } = new();
    public List<BillingGroup> BillingGroups { get; private set; } = new();
    public List<SolverView> Solvers { get; private set; } = new();
    public AnalyticsDocument Analytics { get; private set; } = new();
    public SmartActionsDocument SmartActions { get; private set; } = new();

    public event EventHandler? Saved;

    public void Load()
    {
        AppPaths.EnsureCreated();

        Settings = _settings.LoadOrDefault(() => new GlobalSettings());
        Accounts = _accounts.LoadOrDefault(() => new AccountsDocument());
        TaskGroups = _tasks.LoadOrDefault(() => new List<TaskGroup>()) ?? new List<TaskGroup>();
        ProxyGroups = _proxies.LoadOrDefault(() => new List<ProxyGroup>()) ?? new List<ProxyGroup>();
        BillingGroups = _billing.LoadOrDefault(() => new List<BillingGroup>()) ?? new List<BillingGroup>();
        Solvers = _solvers.LoadOrDefault(() => new List<SolverView>()) ?? new List<SolverView>();
        Analytics = _analytics.LoadOrDefault(() => new AnalyticsDocument());
        SmartActions = _smartActions.LoadOrDefault(() => new SmartActionsDocument());

        if (TaskGroups.Count == 0)
            TaskGroups.Add(new TaskGroup { Name = "Group 1" });
        if (ProxyGroups.Count == 0)
            ProxyGroups.Add(new ProxyGroup { Name = "Group 1" });
        if (BillingGroups.Count == 0)
            BillingGroups.Add(new BillingGroup { Name = "Group 1" });
    }

    public void Save()
    {
        AppPaths.EnsureCreated();
        _settings.Save(Settings);
        _accounts.Save(Accounts);
        _tasks.Save(TaskGroups);
        _proxies.Save(ProxyGroups);
        _billing.Save(BillingGroups);
        _solvers.Save(Solvers);
        _analytics.Save(Analytics);
        _smartActions.Save(SmartActions);
        Saved?.Invoke(this, EventArgs.Empty);
    }

    /// <summary>Full snapshot written to Backups/Backup &lt;timestamp&gt;.cyb.</summary>
    public void Backup()
    {
        AppPaths.EnsureCreated();
        var snapshot = new BackupDocument
        {
            Settings = Settings,
            Accounts = Accounts,
            TaskGroups = TaskGroups,
            ProxyGroups = ProxyGroups,
            BillingGroups = BillingGroups,
            Solvers = Solvers,
            Analytics = Analytics,
            SmartActions = SmartActions,
            SmartActionUtilities = new SmartActionUtilitiesDocument(),
        };
        var name = $"Backup {DateTime.Now:dd MMM HH\\hmm\\m}.cyb";

        // R388: a real 5.18.32 backup is written COMPACT (no newlines, no space after ':'): its first bytes are
        // {"proxies":[{"id":"66da0f96","name":"Group 1",… . Serialising with the indented default produced a file the
        // original would still read, but not one it would have written, so the writer now uses a compact clone.
        var settings = new Newtonsoft.Json.JsonSerializerSettings
        {
            ContractResolver = Json.Default.ContractResolver,
            Formatting = Newtonsoft.Json.Formatting.None,
            NullValueHandling = Json.Default.NullValueHandling,
            DateTimeZoneHandling = Json.Default.DateTimeZoneHandling,
            Converters = Json.Default.Converters,
        };
        File.WriteAllText(Path.Combine(AppPaths.BackupsDir, name), Newtonsoft.Json.JsonConvert.SerializeObject(snapshot, settings));

        // retention
        var files = new DirectoryInfo(AppPaths.BackupsDir)
            .GetFiles("*.cyb")
            .OrderByDescending(f => f.LastWriteTimeUtc)
            .Skip(Math.Max(1, Settings.MaxBackups))
            .ToList();
        foreach (var f in files)
        {
            try { f.Delete(); } catch { /* keep going */ }
        }
    }

    /// <summary>
    /// Load a .cyb file back over the live state and write it out. Returns false when the file is
    /// missing, unparseable, or has no settings — the caller should not report success then.
    ///
    /// Round 117: the Restore button only wrote "Restore from {file}" to a status line. There was
    /// no way to read a backup at all, which made "Backup Now" a one-way door.
    /// </summary>
    public bool Restore(string path)
    {
        if (string.IsNullOrWhiteSpace(path) || !File.Exists(path)) return false;

        BackupDocument? doc;
        try
        {
            doc = Json.Deserialize<BackupDocument>(File.ReadAllText(path));
        }
        catch
        {
            return false;
        }

        if (doc?.Settings is null) return false;

        // everything the snapshot carries, copied field by field so a partial file leaves the
        // untouched collections alone
        Settings = doc.Settings;
        Accounts = doc.Accounts ?? Accounts;
        TaskGroups = doc.TaskGroups ?? TaskGroups;
        ProxyGroups = doc.ProxyGroups ?? ProxyGroups;
        BillingGroups = doc.BillingGroups ?? BillingGroups;
        Solvers = doc.Solvers ?? Solvers;
        Analytics = doc.Analytics ?? Analytics;
        SmartActions = doc.SmartActions ?? SmartActions;

        Save();
        return true;
    }

    /// <summary>
    /// Replace settings with factory defaults and persist. Lives here because
    /// <see cref="Settings"/> has a private setter — the Data page needs the operation without
    /// the right to assign the property directly.
    /// </summary>
    public void ResetSettings()
    {
        Settings = new GlobalSettings();
        Save();
    }

    /// <summary>
    /// Write the requested slice of state to <paramref name="targetPath"/> as JSON.
    /// <paramref name="kind"/> is one of the labels DataView.ExportKinds offers; "All data"
    /// writes the same shape a backup does, so an export can be restored or imported.
    /// </summary>
    public void Export(string targetPath, string? kind)
    {
        var dir = Path.GetDirectoryName(targetPath);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        object payload = (kind ?? "All data").Trim() switch
        {
            "Tasks" => TaskGroups,
            "Profiles" => BillingGroups,
            "Proxies" => ProxyGroups,
            "Accounts" => Accounts,
            "Settings" => Settings,
            _ => new BackupDocument
            {
                Settings = Settings,
                Accounts = Accounts,
                TaskGroups = TaskGroups,
                ProxyGroups = ProxyGroups,
                BillingGroups = BillingGroups,
                Solvers = Solvers,
                Analytics = Analytics,
                SmartActions = SmartActions,
            },
        };

        File.WriteAllText(targetPath, Json.Serialize(payload));
    }
}

/// <summary>
/// One <c>Backups/Backup &lt;date&gt;.cyb</c> snapshot.
///
/// <para>
/// R384: the key names are the image's own. A live 5.18.32 backup is plain JSON whose top-level keys are exactly
/// <c>proxies, billing, accounts, solvers, settings, tasks, smartActions, smartActionUtilities, analytics</c> (measured on
/// a real backup file). The replica used PascalCase property names and had no <c>smartActionUtilities</c> at all, so its
/// files could not be restored by the original and vice versa. Every property is mapped with
/// <see cref="System.Text.Json.Serialization.JsonPropertyNameAttribute"/> so the file matches byte-for-byte in shape.
/// </para>
/// </summary>
public sealed class BackupDocument
{
    [Newtonsoft.Json.JsonProperty("proxies")]
    public List<ProxyGroup> ProxyGroups { get; set; } = new();

    [Newtonsoft.Json.JsonProperty("billing")]
    public List<BillingGroup> BillingGroups { get; set; } = new();

    [Newtonsoft.Json.JsonProperty("accounts")]
    public AccountsDocument Accounts { get; set; } = new();

    [Newtonsoft.Json.JsonProperty("solvers")]
    public List<SolverView> Solvers { get; set; } = new();

    [Newtonsoft.Json.JsonProperty("settings")]
    public GlobalSettings Settings { get; set; } = new();

    [Newtonsoft.Json.JsonProperty("tasks")]
    public List<TaskGroup> TaskGroups { get; set; } = new();

    [Newtonsoft.Json.JsonProperty("smartActions")]
    public SmartActionsDocument SmartActions { get; set; } = new();

    [Newtonsoft.Json.JsonProperty("smartActionUtilities")]
    public SmartActionUtilitiesDocument SmartActionUtilities { get; set; } = new();

    [Newtonsoft.Json.JsonProperty("analytics")]
    public AnalyticsDocument Analytics { get; set; } = new();
}
