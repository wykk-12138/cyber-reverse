import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Tasks.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    public bool MonitorMode { get; set; }
    public int CheckoutDelay { get; set; }'''
add = '''    public bool MonitorMode { get; set; }
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
'''
assert anchor in t and 'public Profile? Profile { get; set; }' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('BotTask gains Products/Profile/ProxyGroup/Properties/Status')
