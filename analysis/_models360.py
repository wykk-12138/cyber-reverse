import io

# 1) WebTask.Steps — the web-task twin of BotTask: a step list
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Tasks.cs"
t1 = io.open(p1, encoding='utf-8').read()
old1 = '''    public Product Product { get; set; } = new();
    public TaskState State { get; set; } = TaskState.Idle;
}'''
new1 = '''    public Product Product { get; set; } = new();
    public TaskState State { get; set; } = TaskState.Idle;

    /// <summary>The steps this web task has run (bound as <c>Steps</c>, R360) — the same list <see cref="BotTask"/> keeps.</summary>
    public List<TaskStep> Steps { get; } = new();
}'''
assert old1 in t1
t1 = t1.replace(old1, new1, 1)

# 2) Product.Color — the colour the grid paints a product row with
old2 = '''    public bool PriceCheck { get => _priceCheck; set => SetProperty(ref _priceCheck, value); }'''
new2 = '''    public bool PriceCheck { get => _priceCheck; set => SetProperty(ref _priceCheck, value); }

    /// <summary>Row colour, empty when the product has none (bound as <c>Color</c>, R360).</summary>
    public string Color { get; set; } = string.Empty;'''
assert old2 in t1
t1 = t1.replace(old2, new2, 1)
io.open(p1, 'w', encoding='utf-8', newline='').write(t1)
print('WebTask.Steps + Product.Color added')

# 3) SmartAction.Logs — the run log lines this action produced
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\SmartActions.cs"
t2 = io.open(p2, encoding='utf-8').read()
anchor = '''    public SmartActionKind Kind { get => _kind; set => SetProperty(ref _kind, value); }'''
add = anchor + '''

    /// <summary>Lines this action has logged (bound as <c>Logs</c>, R360). The engine appends; the view reads.</summary>
    public List<string> Logs { get; } = new();'''
assert anchor in t2 and 'public List<string> Logs' not in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(anchor, add, 1))
print('SmartAction.Logs added')
