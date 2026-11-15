import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Checkout.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    public string? AccountSelectionMode { get; set; }
}'''
add = '''    public string? AccountSelectionMode { get; set; }

    // R363: the binding table names seventeen more members on this form model. The ones whose type follows from an
    // existing member of the same name are here; Input / Inputs are left out on purpose — "input" could be a string, a
    // product option or a list of them, and picking one would be a guess about behaviour, not about data.

    /// <summary>The task group this form creates into (bound as <c>Group</c>).</summary>
    public TaskGroup? Group { get; set; }

    /// <summary>The account group the run draws from (bound as <c>AccountGroup</c>).</summary>
    public AccountGroup? AccountGroup { get; set; }

    /// <summary>The single profile chosen, when one is (bound as <c>Profile</c>).</summary>
    public Profile? Profile { get; set; }

    /// <summary>The profiles the form offers (bound as <c>Profiles</c>).</summary>
    public List<Profile> Profiles { get; } = new();

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
    public List<BotTask> Tasks { get; } = new();

    /// <summary>How many tasks it would create — derived, never stored (bound as <c>Total</c>).</summary>
    public int Total => Tasks.Count;

    /// <summary>Whether the form is editing an existing task rather than creating one (bound as <c>IsEditing</c>).</summary>
    public bool IsEditing { get; set; }
}'''
assert anchor in t and 'public TaskGroup? Group { get; set; }' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('CreateModel gains 13 of the 17 bound members')
