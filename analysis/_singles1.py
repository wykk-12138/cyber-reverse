import io
R = r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models'

# Status.Clickable
p = R + r'\Primitives.cs'
t = io.open(p, encoding='utf-8').read()
old = '    public string Text { get => _text; set => SetProperty(ref _text, value); }'
new = '''    public string Text { get => _text; set => SetProperty(ref _text, value); }

    /// <summary>
    /// Whether the status chip is clickable — the original binds this on <c>Models.Status</c>
    /// (analysis/xaml_bindings.json). A chip with a click handler says so here rather than by cursor shape.
    /// </summary>
    public bool Clickable { get; set; }'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('Status.Clickable')

# Solver.AIStatus
p = R + r'\Checkout.cs'
t = io.open(p, encoding='utf-8').read()
old = '''public sealed class Solver : ObservableObject
{
    public string? Proxy { get; set; }'''
new = '''public sealed class Solver : ObservableObject
{
    /// <summary>What the AI solver is doing, as the solver row prints it (bound as <c>AIStatus</c>).</summary>
    public string? AIStatus { get; set; }

    public string? Proxy { get; set; }'''
assert old in t
t = t.replace(old, new, 1)

old2 = '''    public string? AccountId { get; set; }
    public bool UseSmartActions { get; set; }'''
new2 = '''    public string? AccountId { get; set; }
    public bool UseSmartActions { get; set; }

    /// <summary>
    /// How accounts are picked for the run — the original binds <c>AccountSelectionMode</c> on this model
    /// (analysis/xaml_bindings.json). Empty means "the group default".
    /// </summary>
    public string? AccountSelectionMode { get; set; }'''
assert old2 in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old2, new2, 1))
print('Solver.AIStatus + CreateModel.AccountSelectionMode')
