import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\SmartActions.cs'
t = io.open(p, encoding='utf-8').read()

# 1) filter behaviour + inputs (evidence: SmartActions.Filter binds Behaviour/Inputs; FilterInputEntry{Filter,Input})
old = '''    /// <summary>SmartActionsCreator.FilterOne / 鈥ormat 鈥?the filter chain (all must pass).</summary>
    public List<SmartActionFilter> Filters { get; set; } = new();'''
new = '''    /// <summary>SmartActionsCreator.FilterOne / 鈥ormat 鈥?the filter chain (all must pass).</summary>
    public List<SmartActionFilter> Filters { get; set; } = new();

    /// <summary>
    /// The actions this rule fires (bound as <c>Actions</c> on <c>SmartActions.SmartAction</c>). R252: the replica had a
    /// single kind+target, so a rule could do exactly one thing; the original chains several. The first entry mirrors
    /// <see cref="Kind"/>/<see cref="Target"/> so old documents keep working.
    /// </summary>
    public List<SmartActionStep> Actions { get; set; } = new();'''
assert old in t
t = t.replace(old, new, 1)

anchor = '''/// <summary>Root document of smartActions.json (also embedded in settings.json).</summary>'''
add = '''/// <summary>
/// One action inside a rule (<c>SmartActions.Action</c>: Name / Description / Config / Variables / Image). The replica
/// had one kind+target per rule; this is the list form the original binds.
/// </summary>
public sealed class SmartActionStep : ObservableObject
{
    private string _name = "Action";
    private SmartActionKind _kind = SmartActionKind.Notification;
    private string _target = string.Empty;

    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Name { get => _name; set => SetProperty(ref _name, value); }
    public SmartActionKind Kind { get => _kind; set => SetProperty(ref _kind, value); }

    /// <summary>Webhook URL, notification text or task id, depending on <see cref="Kind"/>.</summary>
    public string Target { get => _target; set => SetProperty(ref _target, value); }
}

/// <summary>
/// One parameter on an action (<c>SmartActions.ActionConfig</c>: Name / Required). Bound as <c>Required</c> — the
/// creator marks which parameters must be filled in before the rule can run.
/// </summary>
public sealed class SmartActionStepConfig : ObservableObject
{
    public string Name { get; set; } = string.Empty;

    /// <summary>Whether the parameter must be supplied (bound as <c>Required</c>).</summary>
    public bool Required { get; set; }
}

/// <summary>One input on a filter (<c>SmartActions.FilterInputEntry</c>: Filter / Input / IsFirst).</summary>
public sealed class SmartActionFilterInput : ObservableObject
{
    public string Filter { get; set; } = string.Empty;
    public string Input { get; set; } = string.Empty;
}

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)

# 2) Behaviour + Inputs on the filter
old2 = '''    public string Value { get => _value; set => SetProperty(ref _value, value); }'''
new2 = '''    public string Value { get => _value; set => SetProperty(ref _value, value); }

    /// <summary>
    /// How this filter combines with the previous one — "And" (default) or "Or" (bound as <c>Behaviour</c> on
    /// <c>SmartActions.Filter</c>). The replica only had "all must pass".
    /// </summary>
    public string Behaviour { get; set; } = "And";

    /// <summary>The inputs this filter reads (bound as <c>Inputs</c>).</summary>
    public List<SmartActionFilterInput> Inputs { get; set; } = new();'''
assert old2 in t
t = t.replace(old2, new2, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('models extended: Actions / Behaviour / Inputs / ActionConfig.Required / FilterInputEntry')
