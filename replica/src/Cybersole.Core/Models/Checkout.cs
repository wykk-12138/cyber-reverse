using Newtonsoft.Json;

namespace Cybersole.Core.Models;

/// <summary>Base class of checkout records (Cybersole.Models.BaseCheckout).</summary>
public class BaseCheckout : ObservableObject
{
    private string? _image;
    private string? _product;
    private string? _store;
    private string? _price;
    private DateTime _timestamp = DateTime.UtcNow;
    private string? _size;
    private string? _type;

    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string? Image { get => _image; set => SetProperty(ref _image, value); }
    public string? Product { get => _product; set => SetProperty(ref _product, value); }
    public string? Store { get => _store; set => SetProperty(ref _store, value); }
    public string? Price { get => _price; set => SetProperty(ref _price, value); }
    public DateTime Timestamp { get => _timestamp; set => SetProperty(ref _timestamp, value); }
    public string? Size { get => _size; set => SetProperty(ref _size, value); }
    public string? Type { get => _type; set => SetProperty(ref _type, value); }
    public string? Profile { get; set; }
    public Dictionary<string, string> Properties { get; set; } = new();
}

/// <summary>Completed checkout (Cybersole.Models.Checkout).</summary>
public sealed class Checkout : BaseCheckout
{
    private string? _order;
    private string? _tracking;
    private bool _success;
    private decimal _spent;
    private string _currency = "USD";
    public string? Order { get => _order; set => SetProperty(ref _order, value); }
    public string? Tracking { get => _tracking; set => SetProperty(ref _tracking, value); }

    // R1210: R1192 added a Profile here typed as the Profile model, while the base class already carries one as a
    // string (BaseCheckout.Profile). Two members of one name with two types is a contradiction rather than
    // richness - the derived one hid the inherited one (CS0108) - and R1192's own note recorded the type as
    // Inference because the descriptor cannot tell an object from an id. The inherited string stands, nothing in
    // source or tests assigned the object form, and the descriptor's Profile!Getter/!Setter on
    // Cybersole.Models.Checkout is satisfied by the inherited member.
    public bool Success { get => _success; set => SetProperty(ref _success, value); }
    public decimal Spent { get => _spent; set => SetProperty(ref _spent, value); }
    public string Currency { get => _currency; set => SetProperty(ref _currency, value); }
}

/// <summary>A drop window of a release.</summary>
public sealed class Drop
{
    public DateTime Time { get; set; }
    public List<string> Stores { get; set; } = new();
    public string? Type { get; set; }
}

/// <summary>Release / drop calendar entry.</summary>
public sealed class Release : ObservableObject
{
    private string? _image;
    private string? _product;
    private DateTime? _releaseDate;
    private string? _price;
    private bool _showSitelist;
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string? Image { get => _image; set => SetProperty(ref _image, value); }
    public string? Product { get => _product; set => SetProperty(ref _product, value); }
    public DateTime? ReleaseDate { get => _releaseDate; set => SetProperty(ref _releaseDate, value); }
    public string? Price { get => _price; set => SetProperty(ref _price, value); }
    public bool ShowSitelist { get => _showSitelist; set => SetProperty(ref _showSitelist, value); }
    public List<Drop> Drops { get; set; } = new();
}

/// <summary>Root document of analytics.json.</summary>
public sealed class AnalyticsDocument
{
    public List<ProxyAnalytics> Proxies { get; set; } = new();
}

public sealed class ProxyAnalytics
{
    public string Id { get; set; } = string.Empty;
    public long TotalDownload { get; set; }
    public long TotalUpload { get; set; }
}

/// <summary>Billing group (billing.json root item).</summary>
public sealed class BillingGroup : ObservableObject
{
    private string _name = "Group 1";
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Name { get => _name; set => SetProperty(ref _name, value); }
    public int? Order { get; set; }
    public List<Profile> Profiles { get; set; } = new();
}

/// <summary>Solver window layout + settings (solvers.json root item).</summary>
public sealed class SolverView : ObservableObject
{
    public double? Left { get; set; }
    public double? Top { get; set; }
    public double? Width { get; set; }
    public double? Height { get; set; }
    public List<Solver> Solvers { get; set; } = new();
}

public sealed class Solver : ObservableObject
{
    /// <summary>What the AI solver is doing, as the solver row prints it (bound as <c>AIStatus</c>).</summary>
    public string? AIStatus { get; set; }

    public string? Proxy { get; set; }
    public string? Filter { get; set; }
    public string? Account { get; set; }
    /// <summary>Row title in the solver list (bound as <c>Name</c>, R361).</summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>The captcha this solver was asked about (bound as <c>Captcha</c>).</summary>
    public string? Captcha { get; set; }

    /// <summary>Whether the row is expanded in the list (bound as <c>View</c>).</summary>
    public bool View { get; set; }

    /// <summary>Bumped whenever the row is refreshed, so a view can tell "reload happened" (bound as <c>Reload</c>).</summary>
    public int Reload { get; private set; }

    /// <summary>Marks the row for a refresh (bound as <c>Reload</c>'s action).</summary>
    public void RequestReload() => Reload++;

    public SolverSettings Settings { get; set; } = new();
}

public sealed class SolverSettings : ObservableObject
{
    private bool _autoBoundingBox = true;
    private bool _autoTickBox = true;
    private bool _autoCanvas = true;
    private bool _questionSharing = true;
    private bool _autoClick = true;
    private bool _reCaptchaSegmentation = true;
    private bool _reCaptchaMultiClassification = true;

    public bool AutoBoundingBox { get => _autoBoundingBox; set => SetProperty(ref _autoBoundingBox, value); }
    public bool AutoTickBox { get => _autoTickBox; set => SetProperty(ref _autoTickBox, value); }
    public bool AutoCanvas { get => _autoCanvas; set => SetProperty(ref _autoCanvas, value); }
    public bool QuestionSharing { get => _questionSharing; set => SetProperty(ref _questionSharing, value); }
    public bool AutoClick { get => _autoClick; set => SetProperty(ref _autoClick, value); }
    public bool ReCaptchaSegmentation { get => _reCaptchaSegmentation; set => SetProperty(ref _reCaptchaSegmentation, value); }
    public bool ReCaptchaMultiClassification { get => _reCaptchaMultiClassification; set => SetProperty(ref _reCaptchaMultiClassification, value); }
}

/// <summary>License descriptor (Cybersole.Models.License).</summary>
public sealed class License : ObservableObject
{
    private string? _name;
    private string? _last4;
    private string? _key;
    private DateTime? _expires;
    public string? Name { get => _name; set => SetProperty(ref _name, value); }
    public string? Last4 { get => _last4; set => SetProperty(ref _last4, value); }
    public string? Key { get => _key; set => SetProperty(ref _key, value); }
    public DateTime? Expires { get => _expires; set => SetProperty(ref _expires, value); }
    public string? Plan { get; set; }
    public bool Valid { get; set; }
}

/// <summary>Creation model shared by task/account wizards.</summary>
public sealed class CreateModel : ObservableObject
{
    public string? ProxyGroupId { get; set; }
    public string? ProfileId { get; set; }
    public string? TaskGroupId { get; set; }
    public string? AccountId { get; set; }
    public bool UseSmartActions { get; set; }

    /// <summary>
    /// How accounts are picked for the run — the original binds <c>AccountSelectionMode</c> on this model
    /// (analysis/xaml_bindings.json). Empty means "the group default".
    /// </summary>
    public string? AccountSelectionMode { get; set; }

    // R363: the binding table names seventeen more members on this form model. The ones whose type follows from an
    // existing member of the same name are here; Input / Inputs are left out on purpose — "input" could be a string, a
    // product option or a list of them, and picking one would be a guess about behaviour, not about data.

    /// <summary>The task group this form creates into (bound as <c>Group</c>).</summary>
    public TaskGroup? Group { get; set; }

    /// <summary>
    /// The input rows this form carries (bound as <c>Inputs</c>).
    ///
    /// <para>
    /// R1203: R363 left this out because "input" could be a product option or a list of them and choosing would
    /// have been a guess about behaviour. The binding table settles the shape of the question:
    /// <c>Cybersole.Models.CreateModel</c> binds <b>both</b> <c>Input</c> and <c>Inputs</c>, and a separate bound
    /// type <c>Cybersole.Models.CreateInputModel</c> exists with thirteen members (Minus, Plus, Sizes, MinPrice,
    /// MaxPrice, Quantity, PriceCheckVisible...) that describe one editable input row. A singular member beside a
    /// plural one, with a row model of exactly that shape available, is a pairing rather than a coin toss.
    /// </para>
    ///
    /// <para>
    /// <b>Observation</b>: Inputs exists on CreateModel and is bound with a Setter; CreateInputModel is bound and
    /// carries the row members. <b>Inference</b>: the element type is CreateInputModel, from that pairing.
    /// <b>Unknown</b>: what the original stores per row.
    /// </para>
    /// </summary>
    public List<Cybersole.Models.CreateInputModel> Inputs { get; set; } = new();

    /// <summary>The account group the run draws from (bound as <c>AccountGroup</c>).</summary>
    public AccountGroup? AccountGroup { get; set; }

    /// <summary>The single profile chosen, when one is (bound as <c>Profile</c>).</summary>
    public Profile? Profile { get; set; }

    /// <summary>The proxy group chosen, when one is (bound as <c>ProxyGroup</c>).</summary>
    public ProxyGroup? ProxyGroup { get; set; }

    /// <summary>The profiles the form offers (bound as <c>Profiles</c>).</summary>
    public List<Profile> Profiles { get; set; } = new();

    /// <summary>How many of the product to buy (bound as <c>Quantity</c>).</summary>
    public int Quantity { get; set; } = 1;

    /// <summary>Per-run delay overrides, same shape as on <see cref="BotTask"/> (bound as <c>MonitorDelay</c>…).</summary>
    public int? MonitorDelay { get; set; }
    public int? RetryDelay { get; set; }
    public int? Timeout { get; set; }

    /// <summary>Monitor-only mode (bound as <c>MonitorMode</c>; <see cref="BotTask.MonitorMode"/> is a bool too).</summary>
    public bool MonitorMode { get; set; }

    /// <summary>When the run should start (bound as <c>StartTime</c>).</summary>
    public DateTime? StartTime { get; set; }

    /// <summary>The store this form points at (bound as <c>Store</c>).</summary>
    public string Store { get; set; } = string.Empty;

    /// <summary>The tasks the form produced (bound as <c>Tasks</c>).</summary>
    public List<BotTask> Tasks { get; set; } = new();

    /// <summary>How many tasks it would create — derived, never stored (bound as <c>Total</c>).</summary>
    public int Total => Tasks.Count;

    /// <summary>Whether the form is editing an existing task rather than creating one (bound as <c>IsEditing</c>).</summary>
    public bool IsEditing { get; set; }
}
