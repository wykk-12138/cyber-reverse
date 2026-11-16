using Newtonsoft.Json;

namespace Cybersole.Core.Models;

/// <summary>Single proxy endpoint (Cybersole.Models.Proxy).</summary>
public sealed class Proxy : ObservableObject
{
    private string _host = string.Empty;
    private int _port;
    private string? _username;
    private string? _password;
    private Status _status = Status.Idle;

    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Host { get => _host; set => SetProperty(ref _host, value); }
    public int Port { get => _port; set => SetProperty(ref _port, value); }
    public string? Username { get => _username; set => SetProperty(ref _username, value); }
    public string? Password { get => _password; set => SetProperty(ref _password, value); }
    public Status Status { get => _status; set => SetProperty(ref _status, value); }
    public string? GroupId { get; set; }
    public int Usage { get; set; }
    public long TotalDownload { get; set; }
    public long TotalUpload { get; set; }

    /// <summary>Optional protocol override: http, https, socks4, socks5.</summary>
    public string Scheme { get; set; } = "http";

    [JsonIgnore]
    public string Address => $"{Host}:{Port}";

    [JsonIgnore]
    public string Uri => string.IsNullOrEmpty(Username)
        ? $"{Scheme}://{Host}:{Port}"
        : $"{Scheme}://{Username}:{Password}@{Host}:{Port}";

    /// <summary>
    /// A copy of this proxy, ready to be added to any group.
    /// </summary>
    /// <remarks>
    /// R61: <c>Proxies.Context.Clone</c> needs one, and <c>Proxies.Context.MoveTo</c> is the
    /// companion that takes an existing proxy elsewhere — one copies, the other reparents.
    ///
    /// What is not copied is the run: a new <see cref="Id"/>, and <see cref="Usage"/> /
    /// <see cref="Status"/> / the byte counters reset. A clone that arrived already carrying
    /// Usage=8 would be treated as spent by "Clear Over" before it had been used once, and a clone
    /// carrying Status=Failed would be removed by "Clear Failed" while it was still untested.
    ///
    /// <see cref="GroupId"/> is the caller's business, not this method's: a clone made inside a
    /// group should point at that group, and a clone made for "Move to" should point at the
    /// destination. Leaving it null lets the caller say which.
    /// </remarks>
    public Proxy Clone() => new()
    {
        Host = Host,
        Port = Port,
        Username = Username,
        Password = Password,
        Scheme = Scheme,
        // Id, Status, Usage, TotalDownload, TotalUpload and GroupId deliberately default.
    };

    public static Proxy Parse(string line)
    {
        var proxy = new Proxy();
        var s = line.Trim();
        if (s.Contains("://"))
        {
            var uri = new Uri(s);
            proxy.Scheme = uri.Scheme;
            proxy.Host = uri.Host;
            proxy.Port = uri.Port > 0 ? uri.Port : 80;
            if (!string.IsNullOrEmpty(uri.UserInfo))
            {
                var parts = uri.UserInfo.Split(':', 2);
                proxy.Username = parts[0];
                proxy.Password = parts.Length > 1 ? parts[1] : string.Empty;
            }
            return proxy;
        }
        var chunks = s.Split(':');
        if (chunks.Length >= 2 && int.TryParse(chunks[1], out var port))
        {
            proxy.Host = chunks[0];
            proxy.Port = port;
            if (chunks.Length >= 4) { proxy.Username = chunks[2]; proxy.Password = chunks[3]; }
        }
        else
        {
            proxy.Host = s;
            proxy.Port = 80;
        }
        return proxy;
    }
}

/// <summary>Proxy group (proxies.json / Cybersole.Models.ProxyGroup).</summary>
public sealed class ProxyGroup : ObservableObject
{
    private string _name = "Group 1";
    private int? _maxUsage;
    private ProxyGroupBehaviour _behaviour = ProxyGroupBehaviour.RoundRobin;
    private long _totalDownload;
    private long _totalUpload;

    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Name { get => _name; set => SetProperty(ref _name, value); }
    public int Order { get; set; }
    public int? MaxUsage { get => _maxUsage; set => SetProperty(ref _maxUsage, value); }
    public ProxyGroupBehaviour Behaviour { get => _behaviour; set => SetProperty(ref _behaviour, value); }

    /// <summary>
    /// How long this group's usage allowance lasts before it rolls over.
    /// </summary>
    /// <remarks>
    /// R54: was <c>DateTime?</c>, and <c>UsagePeriod</c> sat beside it as a separate
    /// <c>TimeSpan?</c> — the same conflation that was fixed on <c>TaskGroup</c> in R53.
    ///
    /// The original binds <c>ProxyGroupView,Cybersole.TimeSpans</c> to
    /// <c>ProxyGroup,Core.UsageExpiry</c>, exactly as it does for <c>TaskGroup</c>. So this is a
    /// duration choice, and there is no separate period field.
    /// </remarks>
    public TimeSpans? UsageExpiry { get; set; }

    /// <summary>
    /// The allowance window length, persisted beside <see cref="UsageExpiry"/> as <c>usagePeriod</c>.
    /// </summary>
    /// <remarks>
    /// R389: R54 concluded from the binding table that "there is no separate period field" — the XAML does bind only
    /// <c>UsageExpiry</c>. A real 5.18.32 backup writes BOTH <c>usagePeriod</c> and <c>usageExpiry</c> on every proxy group
    /// (<c>Backups/Backup 14 Nov 08h01m.cyb</c>), so the field is persisted even though nothing in the markup edits it.
    /// Persistence evidence outranks a binding list; both stay.
    /// </remarks>
    public TimeSpans? UsagePeriod { get; set; }

    /// <summary>
    /// When the current allowance window ends — derived, matching <c>TaskGroup.NextReset</c>.
    /// The original exposes <c>get_NextReset</c> on <c>ProxyGroup</c> too, with no setter.
    /// </summary>
    public DateTime? NextReset =>
        UsageExpiry is null || UsageExpiry == TimeSpans.Manual
            ? null
            : PeriodStart + UsageExpiry.Value.ToDuration();

    /// <summary>When the allowance window began; set on first use, not by the user.</summary>
    public DateTime? PeriodStart { get; set; }

    public List<Proxy> Proxies { get; set; } = new();
    public long TotalDownload { get => _totalDownload; set => SetProperty(ref _totalDownload, value); }
    public long TotalUpload { get => _totalUpload; set => SetProperty(ref _totalUpload, value); }
}
