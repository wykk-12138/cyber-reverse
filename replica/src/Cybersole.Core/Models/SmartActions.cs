namespace Cybersole.Core.Models;

/// <summary>What fires a smart action.</summary>
public enum SmartTrigger
{
    CheckoutSuccess = 0,
    Decline = 1,
    Captcha = 2,
    TaskFailed = 3,
    TaskStarted = 4,
}

/// <summary>What a smart action does.</summary>
public enum SmartActionKind
{
    Webhook = 0,
    Notification = 1,
    StopTask = 2,
}

/// <summary>
/// Automation rule (settings.smartActions / smartActions.json).
/// Mirrors the original: trigger → optional filters → one action.
/// </summary>
public sealed class SmartAction : ObservableObject
{
    private string _name = "New rule";
    private SmartTrigger _trigger = SmartTrigger.CheckoutSuccess;
    private SmartActionKind _kind = SmartActionKind.Notification;
    private string _target = string.Empty;
    private string? _storeFilter;
    private decimal? _minPrice;
    private bool _enabled = true;

    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Name { get => _name; set => SetProperty(ref _name, value); }
    public SmartTrigger Trigger { get => _trigger; set => SetProperty(ref _trigger, value); }
    public SmartActionKind Kind { get => _kind; set => SetProperty(ref _kind, value); }

    /// <summary>Lines this action has logged (bound as <c>Logs</c>, R360). The engine appends; the view reads.</summary>
    public List<string> Logs { get; set; } = new();

    /// <summary>Webhook URL, notification text or task id depending on <see cref="Kind"/>.</summary>
    public string Target { get => _target; set => SetProperty(ref _target, value); }

    /// <summary>Optional store id filter ("shopify", "nike", …).</summary>
    public string? StoreFilter { get => _storeFilter; set => SetProperty(ref _storeFilter, value); }

    /// <summary>Optional minimum order value.</summary>
    public decimal? MinPrice { get => _minPrice; set => SetProperty(ref _minPrice, value); }

    public bool Enabled { get => _enabled; set => SetProperty(ref _enabled, value); }

    // ── surface recovered from SmartActionSettings / SmartActionsCreator ──
    /// <summary>SmartActionSettings.RunOnce — fire a single time then disable.</summary>
    public bool RunOnce { get; set; }

    /// <summary>SmartActionSettings.RunInterval — minimum gap between runs.</summary>
    public TimeSpan? RunInterval { get; set; }

    /// <summary>SmartActionSettings.Notifications — raise a notification when this runs.</summary>
    public bool Notifications { get; set; }

    /// <summary>SmartActionSettings.Webhooks — webhook ids fired alongside the action.</summary>
    public List<string> Webhooks { get; set; } = new();

    /// <summary>SmartActionsCreator.FilterOne / …Format — the filter chain (all must pass).</summary>
    public List<SmartActionFilter> Filters { get; set; } = new();

    /// <summary>
    /// The actions this rule fires (bound as <c>Actions</c> on SmartActions.SmartAction). R252: the replica had a single
    /// kind+target, so a rule could do exactly one thing; the original chains several.
    /// </summary>
    public List<SmartActionStep> Actions { get; set; } = new();

    /// <summary>SmartActionsCreator.Variable — values exposed to the action payload.</summary>
    public Dictionary<string, string> Variables { get; set; } =
        new(StringComparer.OrdinalIgnoreCase);

    /// <summary>SmartActions.LastRun.Format — when this rule last fired.</summary>
    public DateTime? LastRun { get; set; }

    /// <summary>SmartActions.Context.ViewLogs — result of the most recent run.</summary>
    public string? LastResult { get; set; }

    /// <summary>True when every filter passes; an empty chain always passes.</summary>
    public bool Passes(Cybersole.Core.Store.CheckoutEvent evt) =>
        Filters.All(f => f.Passes(evt));
}

/// <summary>Root document of smartActions.json (also embedded in settings.json).</summary>
/// <summary>
/// One filter row (Cybersole.SmartActions.Filter + Ui.Views.SmartActions.FilterRow):
/// a field, an operator and a value, applied to the checkout event before the action runs.
/// </summary>
public sealed class SmartActionFilter : ObservableObject
{
    private string _field = "store";
    private string _operator = "equals";
    private string _value = string.Empty;

    public string Field { get => _field; set => SetProperty(ref _field, value); }
    public string Operator { get => _operator; set => SetProperty(ref _operator, value); }
    public string Value { get => _value; set => SetProperty(ref _value, value); }

    /// <summary>
    /// How this filter combines with the previous one: "And" (default) or "Or" (bound as <c>Behaviour</c> on
    /// SmartActions.Filter). The replica only knew "all must pass".
    /// </summary>
    public string Behaviour { get; set; } = "And";

    /// <summary>The inputs this filter reads (bound as <c>Inputs</c>).</summary>
    public List<SmartActionFilterInput> Inputs { get; set; } = new();

    public static IReadOnlyList<string> Fields { get; } = new[]
    {
        "store", "product", "price", "size", "profile", "order", "success",
    };

    public static IReadOnlyList<string> Operators { get; } = new[]
    {
        "equals", "not equals", "contains", "not contains", "starts with",
        "greater than", "less than", "regex",
    };

    /// <summary>Evaluate this filter against a checkout event.</summary>
    public bool Passes(Cybersole.Core.Store.CheckoutEvent evt)
    {
        var actual = Field.ToLowerInvariant() switch
        {
            "store" => evt.Store,
            "product" => evt.Product,
            "price" => evt.Price,
            "size" => evt.Size,
            "profile" => evt.Profile,
            "order" => evt.OrderNumber ?? string.Empty,
            "success" => evt.Success.ToString(),
            _ => string.Empty,
        };

        var op = Operator.ToLowerInvariant();
        var value = Value;

        return op switch
        {
            "equals" => string.Equals(actual, value, StringComparison.OrdinalIgnoreCase),
            "not equals" => !string.Equals(actual, value, StringComparison.OrdinalIgnoreCase),
            "contains" => actual.Contains(value, StringComparison.OrdinalIgnoreCase),
            "not contains" => !actual.Contains(value, StringComparison.OrdinalIgnoreCase),
            "starts with" => actual.StartsWith(value, StringComparison.OrdinalIgnoreCase),
            "greater than" => Compare(actual, value) > 0,
            "less than" => Compare(actual, value) < 0,
            "regex" => SafeRegex(actual, value),
            _ => false,
        };
    }

    private static int Compare(string a, string b)
    {
        if (decimal.TryParse(a, System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var da) &&
            decimal.TryParse(b, System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var db))
            return da.CompareTo(db);
        return string.Compare(a, b, StringComparison.OrdinalIgnoreCase);
    }

    private static bool SafeRegex(string input, string pattern)
    {
        try
        {
            return System.Text.RegularExpressions.Regex.IsMatch(input, pattern,
                System.Text.RegularExpressions.RegexOptions.IgnoreCase, TimeSpan.FromMilliseconds(250));
        }
        catch (Exception)
        {
            return false;
        }
    }

    public override string ToString() => $"{Field} {Operator} {Value}";
}

/// <summary>One action inside a rule (SmartActions.Action: Name / Description / Config / Variables / Image).</summary>
public sealed class SmartActionStep : ObservableObject
{
    private string _name = "Action";
    private SmartActionKind _kind = SmartActionKind.Notification;
    private string _target = string.Empty;

    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Name { get => _name; set => SetProperty(ref _name, value); }
    public SmartActionKind Kind { get => _kind; set => SetProperty(ref _kind, value); }
    public string Target { get => _target; set => SetProperty(ref _target, value); }

    /// <summary>The parameters this action takes (SmartActions.ActionConfig: Name / Required).</summary>
    public List<SmartActionStepConfig> Config { get; set; } = new();
}

/// <summary>One parameter of an action (SmartActions.ActionConfig: Name / Required).</summary>
public sealed class SmartActionStepConfig : ObservableObject
{
    public string Name { get; set; } = string.Empty;
    public bool Required { get; set; }
}

/// <summary>One input of a filter (SmartActions.FilterInputEntry: Filter / Input / IsFirst).</summary>
public sealed class SmartActionFilterInput : ObservableObject
{
    public string Filter { get; set; } = string.Empty;
    public string Input { get; set; } = string.Empty;
}

public sealed class SmartActionsDocument
{
    public List<SmartAction> Actions { get; set; } = new();

    /// <summary>
    /// Templates published from an action.
    ///
    /// R256: SmartActionsView's Publish button wrote "Templates are not implemented: SmartAction
    /// has no template flag, so publishing would have nowhere to write." Both halves of that were
    /// wrong — the locale has a full PublishTemplate dialog (Header / Title / Description / Group
    /// / Error.NoTitle) and TemplateView page, and PublishTemplateModal was already written 480
    /// lines up the same file. The only thing genuinely missing was this list.
    /// </summary>
    public List<PublishedTemplate> Templates { get; set; } = new();
}

/// <summary>
/// A template published from a smart action: what PublishTemplate.Title / .Description /
/// .Group describe, plus the action it came from so the origin survives.
/// </summary>
public sealed class PublishedTemplate : ObservableObject
{
    private string _title = string.Empty;
    private string _description = string.Empty;
    private string _group = string.Empty;

    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];

    public string Title { get => _title; set => SetProperty(ref _title, value); }
    public string Description { get => _description; set => SetProperty(ref _description, value); }
    public string Group { get => _group; set => SetProperty(ref _group, value); }

    /// <summary>The SmartAction this template was published from, if any.</summary>
    public string? SourceActionId { get; set; }

    public DateTime PublishedUtc { get; set; } = DateTime.UtcNow;
}

/// <summary>Root document of smartActionUtilities.json.</summary>
public sealed class SmartActionUtilitiesDocument
{
    /// <summary>
    /// The saved utility groups (the store lists the Utilities page edits). The key is <c>groups</c>: a live
    /// <c>smartActionUtilities.json</c> contains exactly <c>{"groups": …}</c> (R386), so the property is named after it rather
    /// than after the file.
    /// </summary>
    public List<string> Groups { get; set; } = new();
}
