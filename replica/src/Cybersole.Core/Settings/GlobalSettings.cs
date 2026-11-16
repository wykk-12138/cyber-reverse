using Newtonsoft.Json;
using Cybersole.Core.Models;

namespace Cybersole.Core.Settings;

/// <summary>
/// Keybind set for a page (settings.keyBinds.*).
///
/// Codes are <b>Avalonia Key enum values</b>, not Win32 virtual-key codes: A = 44 … Z = 69,
/// D0 = 34 … D9 = 43, F1 = 90, Delete = 32, Space = 18, Left = 23, Right = 25.
/// Round 116 found the defaults were written in the Win32 scheme while settings.json from the
/// live build used Avalonia, so nothing matched; see KeyBindMatcher for the full story.
/// </summary>
public sealed class TaskKeyBinds
{
    // Defaults read off the live 5.18.32 Settings -> Keyboard Shortcuts page.
    public KeyBind New { get; set; } = new() { Key = 50, Modifiers = 2 };            // Ctrl+G
    public KeyBind Creator { get; set; } = new() { Key = 57, Modifiers = 2 };        // Ctrl+N
    public KeyBind Editor { get; set; } = new() { Key = 48, Modifiers = 2 };         // Ctrl+E
    public KeyBind StartAll { get; set; } = new() { Key = 90, Modifiers = 0 };       // F1
    public KeyBind StopAll { get; set; } = new() { Key = 91, Modifiers = 0 };        // F2
    public KeyBind Delete { get; set; } = new() { Key = 32, Modifiers = 0 };         // Delete
    public KeyBind Clone { get; set; } = new() { Key = 46, Modifiers = 2 };          // Ctrl+C
    public KeyBind Search { get; set; } = new() { Key = 49, Modifiers = 2 };         // Ctrl+F
    public KeyBind Quicktask { get; set; } = new() { Key = 60, Modifiers = 2 };      // Ctrl+Q
    public KeyBind LinkChange { get; set; } = new() { Key = 56, Modifiers = 2 };     // Ctrl+M
    public KeyBind NextGroup { get; set; } = new() { Key = 25, Modifiers = 2 };      // Ctrl+Right
    public KeyBind PreviousGroup { get; set; } = new() { Key = 23, Modifiers = 2 };  // Ctrl+Left
}

public sealed class ProxyKeyBinds
{
    public KeyBind New { get; set; } = new() { Key = 50, Modifiers = 2 };        // Ctrl+G
    public KeyBind Add { get; set; } = new() { Key = 57, Modifiers = 2 };        // Ctrl+N
    public KeyBind TestAll { get; set; } = new() { Key = 63, Modifiers = 2 };    // Ctrl+T
    public KeyBind Copy { get; set; } = new() { Key = 46, Modifiers = 2 };       // Ctrl+C
    public KeyBind Clone { get; set; } = new() { Key = 47, Modifiers = 2 };      // Ctrl+D
    public KeyBind Delete { get; set; } = new() { Key = 32, Modifiers = 0 };     // Delete
}

public sealed class BillingKeyBinds
{
    public KeyBind New { get; set; } = new() { Key = 50, Modifiers = 2 };        // Ctrl+G
    public KeyBind Add { get; set; } = new() { Key = 57, Modifiers = 2 };        // Ctrl+N
    public KeyBind Clone { get; set; } = new() { Key = 47, Modifiers = 2 };      // Ctrl+D
    public KeyBind Delete { get; set; } = new() { Key = 32, Modifiers = 0 };     // Delete
}

public sealed class KeyBindSet
{
    public TaskKeyBinds Tasks { get; set; } = new();
    public ProxyKeyBinds Proxies { get; set; } = new();
    public BillingKeyBinds Billing { get; set; } = new();
}

public sealed class NotificationSet
{
    public NotificationOptions Checkout { get; set; } = new();
    public NotificationOptions Decline { get; set; } = new();
    public NotificationOptions Captcha { get; set; } = new();
    public NotificationOptions SmartAction { get; set; } = new();
    public NotificationOptions Other { get; set; } = new();
}

/// <summary>
/// Global application settings — mirrors settings.json one-to-one
/// (camelCase on disk via <see cref="SettingsJson"/> resolver).
/// </summary>
public sealed class GlobalSettings : ObservableObject
{
    private string? _bearer;
    private string? _license;
    private int _monitorDelay = 2500;
    private int _retryDelay = 2500;
    private int _timeout = 10;
    private bool _autoOpen3DS;
    private int _autoOpen3DSLimit = 5;
    private int _browserLimit = 10;
    private BrowserWindowMode _browserWindowMode = BrowserWindowMode.Tab;
    private BrowserProfileAssignment _browserProfileAssignment = BrowserProfileAssignment.RoundRobin;
    private bool _pinGroups;
    private StartupPage _startup = StartupPage.Home;
    private bool _keybinds = true;
    private bool _notifications = true;
    private int _clock;
    private bool _enableClock;
    private string _clockFormat = "HH:mm";
    private Currency _currency = Currency.USD;
    private TimeSpan _maxLogRetention = TimeSpan.FromDays(1);
    private int _maxLogSize = 50;
    private TimeSpan _backupInterval = TimeSpan.FromHours(3);
    private int _maxBackups = 5;
    private bool _smartActions = true;
    private bool _betaUpdates;
    private TaskGroupOrder _taskGroupOrder = TaskGroupOrder.Newest;
    private ProxyGroupOrder _proxyGroupOrder = ProxyGroupOrder.Custom;
    private ProfileGroupOrder _profileGroupOrder = ProfileGroupOrder.Custom;
    private QueuePresentation _queuePresentation = QueuePresentation.Standard;
    private double _scrollbarWidth = 5;
    private string _scrollbarColor = "#29293A";
    private double _scrollbarCornerRadius = 2;
    private string _language = "English";

    // ---- session ----
    public string? Bearer { get => _bearer; set => SetProperty(ref _bearer, value); }
    public string? License { get => _license; set => SetProperty(ref _license, value); }

    // ---- task defaults ----
    public string? QuickTaskProxies { get; set; }
    public List<string> QuickTaskProfiles { get; set; } = new();
    public int MonitorDelay { get => _monitorDelay; set => SetProperty(ref _monitorDelay, value); }
    public int RetryDelay { get => _retryDelay; set => SetProperty(ref _retryDelay, value); }
    public int Timeout { get => _timeout; set => SetProperty(ref _timeout, value); }
    public string? ShopifyBrowserProxy { get; set; }
    public bool AutoOpen3DS { get => _autoOpen3DS; set => SetProperty(ref _autoOpen3DS, value); }
    public int AutoOpen3DSLimit { get => _autoOpen3DSLimit; set => SetProperty(ref _autoOpen3DSLimit, value); }

    // ---- browser ----
    public string? BrowserPath { get; set; }
    public int BrowserLimit { get => _browserLimit; set => SetProperty(ref _browserLimit, value); }
    public BrowserWindowMode BrowserWindowMode { get => _browserWindowMode; set => SetProperty(ref _browserWindowMode, value); }
    public List<string> BrowserProfiles { get; set; } = new();
    public BrowserProfileAssignment BrowserProfileAssignment { get => _browserProfileAssignment; set => SetProperty(ref _browserProfileAssignment, value); }

    // ---- ui behaviour ----
    public bool PinGroups { get => _pinGroups; set => SetProperty(ref _pinGroups, value); }
    // R927: the binding calls this member StartupPage and the settings file calls it startup. Both are facts and
        // neither can give way: the binding is what the original exposes and the file key is what it writes, so the
        // property carries the binding name and the attribute carries the file name. Renaming the property alone made
        // the live-schema pin report a missing "startup" key, which is how the difference surfaced.
        [Newtonsoft.Json.JsonProperty("startup")]
        public StartupPage StartupPage { get => _startup; set => SetProperty(ref _startup, value); }
    public bool Keybinds { get => _keybinds; set => SetProperty(ref _keybinds, value); }
    public bool Notifications { get => _notifications; set => SetProperty(ref _notifications, value); }
    public int Clock { get => _clock; set => SetProperty(ref _clock, value); }

    /// <summary>
    /// The live clock in the navigation bar.
    ///
    /// R198: the locale has Settings.General.EnableClock ("Enable clock") with a tooltip —
    /// "Whether to enable the live clock in the navigation bar and which format it should
    /// use" — and GlobalSettings had no field for it. `Clock` above is the offset in hours,
    /// a different setting. This pair is the one the label describes.
    /// </summary>
    public bool EnableClock { get => _enableClock; set => SetProperty(ref _enableClock, value); }
    public string ClockFormat { get => _clockFormat; set => SetProperty(ref _clockFormat, value); }

    public Currency Currency { get => _currency; set => SetProperty(ref _currency, value); }
    public ConcurrencySettings Concurrency { get; set; } = new();

    /// <summary>
    /// How many monitors run at once (bound as <c>MonitorConcurrency</c>). Distinct from <see cref="Concurrency"/>,
    /// which is the checkout pool: the settings page shows "Monitor Concurrency" as its own row.
    /// </summary>
    public int MonitorConcurrency { get; set; } = 10;

    // ---- logs & backups ----
    public TimeSpan MaxLogRetention { get => _maxLogRetention; set => SetProperty(ref _maxLogRetention, value); }
    public int MaxLogSize { get => _maxLogSize; set => SetProperty(ref _maxLogSize, value); }
    public TimeSpan BackupInterval { get => _backupInterval; set => SetProperty(ref _backupInterval, value); }
    public int MaxBackups { get => _maxBackups; set => SetProperty(ref _maxBackups, value); }
    // R449: the binding table names this member `Cybersole.Global.Settings.SmartActions` (camel-cased
    // binding descriptor `0x143...` -> `SmartActions`), but the replica spelled it `Smartactions`, and the
    // original's own settings.json stores the key as all-lowercase `smartactions`. Both facts are true at
    // once, so the member takes the bound name and the persisted key is pinned explicitly — renaming alone
    // would have flipped the file to `smartActions` and broken the LiveSchemaPins key list.
    [JsonProperty("smartactions")]
    public bool SmartActions { get => _smartActions; set => SetProperty(ref _smartActions, value); }
    public bool BetaUpdates { get => _betaUpdates; set => SetProperty(ref _betaUpdates, value); }

    // ---- ordering ----
    public TaskGroupOrder TaskGroupOrder { get => _taskGroupOrder; set => SetProperty(ref _taskGroupOrder, value); }
    public ProxyGroupOrder ProxyGroupOrder { get => _proxyGroupOrder; set => SetProperty(ref _proxyGroupOrder, value); }
    public ProfileGroupOrder ProfileGroupOrder { get => _profileGroupOrder; set => SetProperty(ref _profileGroupOrder, value); }
    public QueuePresentation QueuePresentation { get => _queuePresentation; set => SetProperty(ref _queuePresentation, value); }

    // ---- integrations ----
    public List<CaptchaProvider> CaptchaProviders { get; set; } = new();
    public List<CloudflareSolverConfig> CloudflareSolvers { get; set; } = new();
    public List<Webhook> Webhooks { get; set; } = new();
    public NotificationSet NotificationOptions { get; set; } = new();
    public KeyBindSet KeyBinds { get; set; } = new();

    // ---- customisation ----
    public List<CustomStore> CustomStores { get; set; } = new();

    /// <summary>Utilities.StoreGroups — named store sets used by tasks and monitors.</summary>
    public List<StoreGroup> StoreGroups { get; set; } = new();
    public List<string> CustomSizes { get; set; } = new();
    public MonitorFilters MonitorFilters { get; set; } = new();
    public double ScrollbarWidth { get => _scrollbarWidth; set => SetProperty(ref _scrollbarWidth, value); }
    public string ScrollbarColor { get => _scrollbarColor; set => SetProperty(ref _scrollbarColor, value); }
    public double ScrollbarCornerRadius { get => _scrollbarCornerRadius; set => SetProperty(ref _scrollbarCornerRadius, value); }
    public string Language { get => _language; set => SetProperty(ref _language, value); }

    public GlobalSettings Clone() => (GlobalSettings)MemberwiseClone();
}

/// <summary>Captcha provider entry (settings.captchaProviders).</summary>
public sealed class CaptchaProvider
{
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Name { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty;
    public string? ApiKey { get; set; }
    public double Balance { get; set; }

    // Round 113: the settings page edits priority, enabled and concurrency, but this record had
    // nowhere to keep them — so Add and Up/Down changed the in-memory registry and the next save
    // wrote nothing. These three make the edit persist.
    public int Priority { get; set; }
    public bool Enabled { get; set; }
    public int Concurrency { get; set; } = 10;

    // R361: the binding table names three more fields on this record; CloudflareSolverConfig already had two of them,
    // CaptchaProvider had none, so the two lists could not be shown the same way.
    public int Count { get; set; }
    public bool BalanceSupported { get; set; }
    public bool IsFetchingBalance { get; set; }
}

/// <summary>Cloudflare solver entry (settings.cloudflareSolvers).</summary>
public sealed class CloudflareSolverConfig
{
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Name { get; set; } = string.Empty;
    public string Type { get; set; } = "cybersole";
    public string? ApiKey { get; set; }
    public double Balance { get; set; }
    public int Count { get; set; }
    public int Concurrency { get; set; } = 10;
    public bool BalanceSupported { get; set; }
}
