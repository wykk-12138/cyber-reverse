using Newtonsoft.Json;

namespace Cybersole.Core.Models;

/// <summary>Variant of a product (size run / colorway).</summary>
public sealed class Variant : ObservableObject
{
    private string _name = string.Empty;
    public string Name { get => _name; set => SetProperty(ref _name, value); }
    public List<string> Sizes { get; set; } = new();
    public string? Input { get; set; }
    public bool Selected { get; set; } = true;
}

/// <summary>Product being monitored (Cybersole.Models.Product).</summary>
public sealed class Product : ObservableObject
{
    private string _name = string.Empty;
    private string? _image;
    private string? _price;
    private string? _variant;
    private bool _priceCheck;

    public string Name { get => _name; set => SetProperty(ref _name, value); }
    public string? Image { get => _image; set => SetProperty(ref _image, value); }
    public string? Price { get => _price; set => SetProperty(ref _price, value); }
    public string? Variant { get => _variant; set => SetProperty(ref _variant, value); }
    public bool PriceCheck { get => _priceCheck; set => SetProperty(ref _priceCheck, value); }

    /// <summary>Row colour, empty when the product has none (bound as <c>Color</c>, R360).</summary>
    public string Color { get; set; } = string.Empty;

    /// <summary>
    /// Price bounds for the check. R241: the original's input model binds <c>MinPrice</c> / <c>MaxPrice</c> next to
    /// <c>PriceCheck</c> / <c>PriceCheckVisible</c> / <c>TogglePriceCheck</c> (analysis/xaml_bindings.json); the replica
    /// had the switch but no bounds, so a check could only say "any price".
    /// </summary>
    public decimal? MinPrice { get; set; }

    /// <inheritdoc cref="MinPrice"/>
    public decimal? MaxPrice { get; set; }
    public string? Input { get; set; }
    public string? Url { get; set; }
    public List<string> Sizes { get; set; } = new();
}

/// <summary>Task group (tasks.json root item).</summary>
public sealed class TaskGroup : ObservableObject
{
    private string _name = "Group 1";
    private bool _linkedDelays;
    private bool _pinned;
    private CaptchaSource _captchaSource = CaptchaSource.Empty;

    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Name { get => _name; set => SetProperty(ref _name, value); }
    public int? Order { get; set; }

    /// <summary>
    /// How long this group's limits last, before they roll over.
    /// </summary>
    /// <remarks>
    /// R53: this was a <c>DateTime?</c> edited with a date box. The original's is a
    /// <c>Cybersole.TimeSpans</c> enum — the XAML binding
    /// <c>TaskGroupView,Cybersole.TimeSpans</c> → <c>TaskGroup,UsageExpiry</c> says so, and the
    /// locale options are durations ("1 hour", "3 hours", "6 hours", "12 hours", "1 day",
    /// "Manual"). The label reads "Reset limits <em>after</em>", which a date does not answer.
    /// </remarks>
    /// <summary>
    /// How long a usage period lasts, beside <see cref="UsageExpiry"/> (bound and persisted as <c>usagePeriod</c>).
    /// </summary>
    /// <remarks>
    /// R389: a real 5.18.32 backup writes both <c>usagePeriod</c> and <c>usageExpiry</c> on every task group
    /// (<c>Backups/Backup 14 Nov 08h01m.cyb</c>), while this model only had the expiry. The two are separate fields in the
    /// image, so they are separate here.
    /// </remarks>
    public TimeSpans? UsagePeriod { get; set; }

    public TimeSpans? UsageExpiry { get; set; }

    /// <summary>
    /// When the current period ends. Getter-only in the original (<c>get_NextReset</c> exists,
    /// <c>set_NextReset</c> does not), so it is derived rather than stored.
    /// </summary>
    /// <summary>How many of this group's tasks are live right now (bound as <c>Running</c>, R362).</summary>
    public int Running => Tasks.Count(t => t.IsRunning);

    /// <summary>
    /// The Cloudflare solver selected for this group, by configuration id (bound as <c>CloudflareSolverId</c>). The name
    /// stays in <c>CloudflareSolver</c>; this is the id the settings list keys on.
    /// </summary>
    public string? CloudflareSolverId { get; set; }

    public DateTime? NextReset =>
        UsageExpiry is null || UsageExpiry == TimeSpans.Manual
            ? null
            : PeriodStart + UsageExpiry.Value.ToDuration();

    /// <summary>
    /// When the period began. <c>TaskGroup.PeriodStart.Tooltip</c> says "Period starts when you
    /// first start a task", so this is set by the engine on first start, not by the user.
    /// </summary>
    public DateTime? PeriodStart { get; set; }
    public int? CheckoutLimit { get; set; }
    public int? ProfileLimit { get; set; }
    public int? MonitorDelay { get; set; }
    public int? RetryDelay { get; set; }
    public int? Timeout { get; set; }
    public bool LinkedDelays { get => _linkedDelays; set => SetProperty(ref _linkedDelays, value); }
    public bool Pinned { get => _pinned; set => SetProperty(ref _pinned, value); }
    public CaptchaSource CaptchaSource { get => _captchaSource; set => SetProperty(ref _captchaSource, value); }
    public string? CloudflareSolver { get; set; }
    public List<Webhook> Webhooks { get; set; } = new();

    /// <summary>Preferred shipping method/price for this group (ShippingRatesCreatorView).</summary>
    public string? ShippingRate { get; set; }

    // R52: the original's TaskGroup carries running counters. The string table of Cybersole.exe
    // has get_TotalCheckouts / get_TotalDeclines / get_NextReset / get_CheckoutLimit together —
    // and CheckoutStats here is global (AppServices.Stats) with a ByStore view, not a ByGroup one.
    // So per-group totals are a real gap, not a naming difference.
    //
    // Written under a lock in TaskEngine: the same group is shared by every task in it, and
    // `++` on a shared int loses increments. A lock per checkout is cheap next to a checkout.

    /// <summary>Cybersole.Models.TaskGroup.TotalCheckouts — successful orders for this group.</summary>
    public int TotalCheckouts { get; set; }

    /// <summary>Cybersole.Models.TaskGroup.TotalDeclines — failed attempts for this group.</summary>
    public int TotalDeclines { get; set; }

    /// <summary>
    /// Extra backoff after a failure.
    /// </summary>
    /// <remarks>
    /// Not in the original. R52 searched the string table for <c>^Default[A-Z]\w*$</c> and for
    /// <c>errorDelay</c>: neither exists. The group's delay fields are MonitorDelay, RetryDelay
    /// and Timeout; there is no separate error backoff. Kept because removing it would break the
    /// settings UI that edits it, but it should not be described as mirroring the original.
    /// </remarks>
    public int? ErrorDelay { get; set; }

    /// <summary>Cybersole.Models.TaskGroup.ResetLimitsAfter — when the counters roll over.</summary>
    public TimeSpan? ResetLimitsAfter { get; set; }

    /// <summary>Cybersole.Models.TaskGroup.WebhookFilter — which webhooks fire for this group.</summary>
    public string? WebhookFilter { get; set; }
    public List<BotTask> Tasks { get; set; } = new();
}

/// <summary>A monitored task (web / API checkout).</summary>
public sealed class BotTask : ObservableObject
{
    private string _name = string.Empty;
    private TaskState _state = TaskState.Idle;
    private DateTime? _startTime;
    private int? _monitorDelay;
    private int? _retryDelay;
    private int? _timeout;

    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Name { get => _name; set => SetProperty(ref _name, value); }
    public string Store { get; set; } = string.Empty;
    public string? GroupId { get; set; }
    public Product Product { get; set; } = new();
    public string? ProfileId { get; set; }
    public string? ProxyGroupId { get; set; }
    public string? AccountId { get; set; }
    public TaskState State { get => _state; set => SetProperty(ref _state, value); }
    public DateTime? StartTime { get => _startTime; set => SetProperty(ref _startTime, value); }
    public int? MonitorDelay { get => _monitorDelay; set => SetProperty(ref _monitorDelay, value); }
    public int? RetryDelay { get => _retryDelay; set => SetProperty(ref _retryDelay, value); }
    public int? Timeout { get => _timeout; set => SetProperty(ref _timeout, value); }
    public bool MonitorMode { get; set; }
    public int CheckoutDelay { get; set; }

    // R364: the binding table names six more members on this model. Five have an inferable type; "Task" does not (its
    // type could be an engine handle, an interface or a string id, and the name collides with System.Threading.Tasks.Task),
    // so it stays named in docs/BINDING_BACKLOG.md.

    /// <summary>Every product this task watches (bound as <c>Products</c>) — the same list <see cref="AllProducts"/> returns.</summary>
    public IReadOnlyList<Product> Products => AllProducts;

    /// <summary>The profile chosen for this task (bound as <c>Profile</c>).</summary>
    public Profile? Profile { get; set; }

    /// <summary>The proxy group chosen for this task (bound as <c>ProxyGroup</c>).</summary>
    public ProxyGroup? ProxyGroup { get; set; }

    /// <summary>Free-form properties the store module attaches (bound as <c>Properties</c>).</summary>
    public Dictionary<string, string> Properties { get; } = new();

    /// <summary>The one-line status the grid prints (bound as <c>Status</c>).</summary>
    public string Status { get; set; } = string.Empty;

    public bool Enabled { get; set; } = true;

    /// <summary>
    /// How many tasks to create per profile in the group.
    ///
    /// The original's task creator labels this "Quantity (per profile)" and defaults it to 1
    /// (observed in the live UI, round 94). It was absent here — the field, not just the control
    /// — so a group could not be asked for more than one run per profile even though nothing in
    /// the engine objected.
    /// </summary>
    public int Quantity { get; set; } = 1;

    /// <summary>
    /// Further products this task monitors, beyond <see cref="Product"/>.
    ///
    /// The original's task creator has an "Add Input" row on its Cart tab, so one task can carry
    /// several product URLs. The replica only ever had the single <c>Product</c>, which is why
    /// this exists as an addition rather than a change: <see cref="Product"/> stays the primary
    /// entry so every existing consumer keeps working, and <see cref="AllProducts"/> is what a
    /// caller should use when it wants all of them.
    /// </summary>
    public List<Product> ExtraProducts { get; set; } = new();

    /// <summary>Every product this task watches, primary first.</summary>
    [JsonIgnore]
    public IReadOnlyList<Product> AllProducts =>
        ExtraProducts.Count == 0
            ? new[] { Product }
            : new[] { Product }.Concat(ExtraProducts).ToList();

    [JsonIgnore] public bool IsRunning => State is TaskState.Monitoring or TaskState.Waiting or TaskState.CheckingOut;

    /// <summary>
    /// A copy of this task, ready to run independently.
    /// </summary>
    /// <remarks>
    /// R60: <c>TaskGroups.Context.CloneFormat</c> ("Clone {0}") needs task copies, and nothing
    /// could produce one.
    ///
    /// What is copied is the configuration: store, product, size run, profile/proxy/account
    /// bindings, delays, quantity. What is not copied is the run: a new <see cref="Id"/>, and
    /// <see cref="State"/>/<see cref="StartTime"/> reset — a clone that arrived already Running
    /// would make the engine think it had a live task it never started.
    ///
    /// <see cref="Product"/> is deep-copied rather than shared: two tasks pointing at the same
    /// <c>Product</c> instance would overwrite each other's detected price and variant.
    /// </remarks>
    public BotTask Clone() => new()
    {
        Name = Name,
        Store = Store,
        GroupId = GroupId,
        Product = CopyProduct(Product),
        ExtraProducts = ExtraProducts.Select(CopyProduct).ToList(),
        ProfileId = ProfileId,
        ProxyGroupId = ProxyGroupId,
        AccountId = AccountId,
        Quantity = Quantity,
        MonitorMode = MonitorMode,
        CheckoutDelay = CheckoutDelay,
        Enabled = Enabled,
        MonitorDelay = MonitorDelay,
        RetryDelay = RetryDelay,
        Timeout = Timeout,
        // State and StartTime deliberately default: Idle and null.
    };

    private static Product CopyProduct(Product source) => new()
    {
        Name = source.Name,
        Image = source.Image,
        Price = source.Price,
        Variant = source.Variant,
        PriceCheck = source.PriceCheck,
        Input = source.Input,
        Url = source.Url,
        Sizes = source.Sizes.ToList(),
    };
}

/// <summary>A web (browser-less) task bound to an account.</summary>
public sealed class WebTask : ObservableObject
{
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public Account? Account { get; set; }
    public string Store { get; set; } = string.Empty;
    public string? Url { get; set; }
    public Product Product { get; set; } = new();
    public TaskState State { get; set; } = TaskState.Idle;

    /// <summary>The steps this web task has run (bound as <c>Steps</c>, R360) — the same list <see cref="BotTask"/> keeps.</summary>
    public List<TaskStep> Steps { get; } = new();
}

/// <summary>Webhook target (Discord / custom).</summary>
public sealed class Webhook : Cybersole.Core.Webhooks.IWebhook
{
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Url { get; set; } = "https://discord.com/api/webhooks";
    public string? Name { get; set; }
    public bool Enabled { get; set; } = true;

    /// <summary>
    /// Extra key/value pairs posted alongside the payload (R318: the image binds IWebhook.ExtraFields and the locale has
    /// Settings.Webhook.ExtraFields, so the settings page has somewhere to put them).
    /// </summary>
    public Dictionary<string, string> ExtraFields { get; } = new();

    /// <summary>
    /// The platform the payload is shaped for (R342: bound as <c>IWebhook.Type</c>). Empty means "not chosen yet" —
    /// the "New Webhook" modal starts on a "Select provider" placeholder.
    /// </summary>
    public string Type { get; set; } = string.Empty;

    /// <summary>
    /// Which notifications fire this hook (R342: bound as <c>IWebhook.Events</c>). The five names are the locale's
    /// <c>Settings.Webhook.Event.*</c> keys: Checkouts, Declines, PayPal, PaymentRequests, SmartActions.
    /// </summary>
    public List<string> Events { get; } = new();

    /// <inheritdoc />
    System.Collections.Generic.IReadOnlyList<string> Cybersole.Core.Webhooks.IWebhook.Events => Events;
}
