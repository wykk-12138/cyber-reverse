using Newtonsoft.Json;

namespace Cybersole.Core.Models;

/// <summary>Store / site account (Cybersole.Models.Account).</summary>
public sealed class Account : ObservableObject
{
    private string _email = string.Empty;
    private string _password = string.Empty;
    private string _statusText = "Idle";
    private DateTime _created = DateTime.UtcNow;

    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Email { get => _email; set { if (SetProperty(ref _email, value)) OnPropertyChanged(nameof(Name)); } }
    public string Password { get => _password; set => SetProperty(ref _password, value); }
    public DateTime Created { get => _created; set => SetProperty(ref _created, value); }
    public string? GroupId { get; set; }
    public string? ProfileId { get; set; }
    public string? ProxyGroupId { get; set; }
    public string StatusText { get => _statusText; set => SetProperty(ref _statusText, value); }
    public bool Enabled { get; set; } = true;
    public Dictionary<string, string> Extra { get; set; } = new();

    [JsonIgnore] public string Name => Email;
    [JsonIgnore] public string MaskedPassword => string.IsNullOrEmpty(Password) ? string.Empty : new string('•', Math.Min(12, Password.Length));
}

public sealed class AccountGroup : ObservableObject
{
    private string _name = "Group 1";
    private string _type = string.Empty;
    private string _store = string.Empty;
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Name { get => _name; set => SetProperty(ref _name, value); }

    /// <summary>
    /// The platform the group belongs to — the "Type" field of the original's Create Group dialog
    /// (Cybersole locale <c>CreateGroup.Type</c>), e.g. "Nike", "Demandware", "Shopify".
    /// </summary>
    public string Type { get => _type; set => SetProperty(ref _type, value); }

    /// <summary>
    /// The country site inside that platform — the "Store" field (<c>CreateGroup.Store</c>), e.g.
    /// "Nike US", "Nike GB". The original's Store dropdown lists exactly these; the group title
    /// on screen is <c>{Store} - {Name}</c>.
    /// </summary>
    public string Store { get => _store; set => SetProperty(ref _store, value); }

    public int Order { get; set; }
    public List<Account> Accounts { get; set; } = new();

    /// <summary>The group's caption as the accounts page prints it: <c>Nike US - zz-probe</c>.</summary>
    [JsonIgnore]
    public string Display =>
        string.IsNullOrWhiteSpace(Store) ? Name
        : string.IsNullOrWhiteSpace(Name) ? Store
        : $"{Store} - {Name}";
}

public sealed class GoogleAccount : ObservableObject
{
    private string _email = string.Empty;
    private string _state = "Idle";
    private string? _proxy;
    public string Email { get => _email; set => SetProperty(ref _email, value); }
    public string State { get => _state; set => SetProperty(ref _state, value); }
    public string? Proxy { get => _proxy; set => SetProperty(ref _proxy, value); }

    /// <summary>Display name shown in the Google accounts grid (Cybersole.Models.GoogleAccount.Name).</summary>
    public string? Name { get; set; }
}

public sealed class PayPalAccount : ObservableObject
{
    private DateTime _lastRefresh = DateTime.UtcNow;
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string? Email { get; set; }
    public DateTime LastRefresh { get => _lastRefresh; set => SetProperty(ref _lastRefresh, value); }
    public string? ProxyGroupId { get; set; }
    public string? ProfileId { get; set; }

    /// <summary>Cybersole.Models.PayPalAccount.Running — whether the account is being kept warm.</summary>
    public bool Running { get; set; }

    /// <summary>Cybersole.Models.PayPalAccount.ProxyGroup — the group used for the login proxy.</summary>
    public string? ProxyGroup { get; set; }

    /// <summary>Cybersole.Models.PayPalAccount.UseLoginProxy.</summary>
    public bool UseLoginProxy { get; set; } = true;

    /// <summary>Cybersole.Models.PayPalAccount.AutoReopen.</summary>
    public bool AutoReopen { get; set; }

    /// <summary>
    /// "Max. inactive session duration" as the live dialog labels it. "Permanent" means the
    /// session never times out, which is the default the real build ships with.
    /// </summary>
    public string MaxInactiveSessionDuration { get; set; } = "Permanent";
}

public sealed class ImapAccount : ObservableObject
{
    private string _host = string.Empty;
    private int _port = 993;
    private string _user = string.Empty;
    private string _password = string.Empty;
    public string Host { get => _host; set => SetProperty(ref _host, value); }
    public int Port { get => _port; set => SetProperty(ref _port, value); }
    public string User { get => _user; set => SetProperty(ref _user, value); }
    public string Password { get => _password; set => SetProperty(ref _password, value); }
    public bool UseSsl { get; set; } = true;

    /// <summary>Messages seen in the mailbox; the live Email Accounts grid has this column.</summary>
    public int InboxCount { get; set; }
}

/// <summary>AYCD Inbox integration block from accounts.json.</summary>
public sealed class AycdInbox : ObservableObject
{
    private string? _apiKey;
    private string? _templateId;
    private string? _appGroup;
    private int _timeoutSeconds = 600;
    private bool _enabled = true;

    public string? ApiKey { get => _apiKey; set => SetProperty(ref _apiKey, value); }
    public string? TemplateId { get => _templateId; set => SetProperty(ref _templateId, value); }
    public string? AppGroup { get => _appGroup; set => SetProperty(ref _appGroup, value); }
    public int TimeoutSeconds { get => _timeoutSeconds; set => SetProperty(ref _timeoutSeconds, value); }
    public bool Enabled { get => _enabled; set => SetProperty(ref _enabled, value); }

    public const string CreateUrl = "https://inbox-api.aycd.io/api/v1/tasks/mail/create";
    public const string CompletedUrl = "https://inbox-api.aycd.io/api/v1/tasks/completed?group=";
    public const string VerifyUrl = "https://inbox-api.aycd.io/api/v1/user/verify";
}

/// <summary>Root document of accounts.json.</summary>
public sealed class AccountsDocument
{
    public List<AccountGroup> AccountGroups { get; set; } = new();
    public List<PayPalAccount> PayPal { get; set; } = new();
    public List<GoogleAccount> Google { get; set; } = new();
    public List<ImapAccount> Imap { get; set; } = new();
    public AycdInbox AycdInbox { get; set; } = new();
}
