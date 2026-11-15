import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Store\ConfigurationStore.cs"
t = io.open(p, encoding='utf-8').read()
old = '''public sealed class BackupDocument
{
    public string Version { get; set; } = "5.18.32";
    public DateTime CreatedUtc { get; set; } = DateTime.UtcNow;
    public GlobalSettings Settings { get; set; } = new();
    public AccountsDocument Accounts { get; set; } = new();
    public List<TaskGroup> TaskGroups { get; set; } = new();
    public List<ProxyGroup> ProxyGroups { get; set; } = new();
    public List<BillingGroup> BillingGroups { get; set; } = new();
    public List<SolverView> Solvers { get; set; } = new();
    public AnalyticsDocument Analytics { get; set; } = new();
    public SmartActionsDocument SmartActions { get; set; } = new();
}'''
new = '''/// <summary>
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
    [System.Text.Json.Serialization.JsonPropertyName("proxies")]
    public List<ProxyGroup> ProxyGroups { get; set; } = new();

    [System.Text.Json.Serialization.JsonPropertyName("billing")]
    public List<BillingGroup> BillingGroups { get; set; } = new();

    [System.Text.Json.Serialization.JsonPropertyName("accounts")]
    public AccountsDocument Accounts { get; set; } = new();

    [System.Text.Json.Serialization.JsonPropertyName("solvers")]
    public List<SolverView> Solvers { get; set; } = new();

    [System.Text.Json.Serialization.JsonPropertyName("settings")]
    public GlobalSettings Settings { get; set; } = new();

    [System.Text.Json.Serialization.JsonPropertyName("tasks")]
    public List<TaskGroup> TaskGroups { get; set; } = new();

    [System.Text.Json.Serialization.JsonPropertyName("smartActions")]
    public SmartActionsDocument SmartActions { get; set; } = new();

    [System.Text.Json.Serialization.JsonPropertyName("smartActionUtilities")]
    public SmartActionUtilitiesDocument SmartActionUtilities { get; set; } = new();

    [System.Text.Json.Serialization.JsonPropertyName("analytics")]
    public AnalyticsDocument Analytics { get; set; } = new();
}'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('BackupDocument now uses the image key names')
