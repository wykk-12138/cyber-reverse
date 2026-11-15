import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Tasks.cs'
t = io.open(p, encoding='utf-8').read()
old = '''    public bool PriceCheck { get => _priceCheck; set => SetProperty(ref _priceCheck, value); }'''
new = '''    public bool PriceCheck { get => _priceCheck; set => SetProperty(ref _priceCheck, value); }

    /// <summary>
    /// Price bounds for the check. R241: the original's input model binds <c>MinPrice</c> / <c>MaxPrice</c> next to
    /// <c>PriceCheck</c> / <c>PriceCheckVisible</c> / <c>TogglePriceCheck</c> (analysis/xaml_bindings.json); the replica
    /// had the switch but no bounds, so a check could only say "any price".
    /// </summary>
    public decimal? MinPrice { get; set; }

    /// <inheritdoc cref="MinPrice"/>
    public decimal? MaxPrice { get; set; }'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('Product.MinPrice / MaxPrice added')

p2 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs'
t2 = io.open(p2, encoding='utf-8').read()
anchor = '''    // ── bound members (R233) ─────────────────────────────────────────────────'''
add = '''    // ── price check (R241) ───────────────────────────────────────────────────
    //
    // The original's input model binds PriceCheckVisible / TogglePriceCheck. The creator already had the
    // "Price check" checkbox; these two give it the vocabulary the original uses.

    /// <summary>Whether the price bounds apply — true while the price check switch is on (bound as <c>PriceCheckVisible</c>).</summary>
    public bool PriceCheckVisible => _priceCheckBox?.IsChecked == true;

    /// <summary>Flips the price check switch and returns the new state (bound as <c>TogglePriceCheck</c>).</summary>
    public bool TogglePriceCheck()
    {
        if (_priceCheckBox is null) return false;
        _priceCheckBox.IsChecked = !(_priceCheckBox.IsChecked == true);
        return _priceCheckBox.IsChecked == true;
    }

''' + anchor
assert anchor in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(anchor, add, 1))
print('TaskCreatorView price-check members added')
