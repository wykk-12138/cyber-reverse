import io, re
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\SmartActions.cs'
t = io.open(p, encoding='utf-8').read()

# 1) SmartAction.Actions right after the Filters declaration line
m = re.search(r'( *public List<SmartActionFilter> Filters \{ get; set; \} = new\(\);)', t)
assert m, 'Filters declaration not found'
new_actions = m.group(1) + '''

    /// <summary>
    /// The actions this rule fires (bound as <c>Actions</c> on SmartActions.SmartAction). R252: the replica had a single
    /// kind+target, so a rule could do exactly one thing; the original chains several.
    /// </summary>
    public List<SmartActionStep> Actions { get; set; } = new();'''
t = t[:m.end()] + new_actions + t[m.end():]

# 2) filter Behaviour + Inputs after Value
m2 = re.search(r'( *public string Value \{ get => _value; set => SetProperty\(ref _value, value\); \})', t)
assert m2, 'Value declaration not found'
new_filter = m2.group(1) + '''

    /// <summary>
    /// How this filter combines with the previous one: "And" (default) or "Or" (bound as <c>Behaviour</c> on
    /// SmartActions.Filter). The replica only knew "all must pass".
    /// </summary>
    public string Behaviour { get; set; } = "And";

    /// <summary>The inputs this filter reads (bound as <c>Inputs</c>).</summary>
    public List<SmartActionFilterInput> Inputs { get; set; } = new();'''
t = t[:m2.end()] + new_filter + t[m2.end():]

# 3) the three new types, before the document class
anchor = t.index('public sealed class SmartActionsDocument')
types = '''/// <summary>One action inside a rule (SmartActions.Action: Name / Description / Config / Variables / Image).</summary>
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

'''
t = t[:anchor] + types + t[anchor:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('models extended')
