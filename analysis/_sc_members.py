import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''    public SizeCreatorView(AppServices services, Action? onChanged = null) : base(DialogTitle, 620, 430)'''
add = '''    // ------------------------------------------------ bound members (R239)
    //
    // The original binds SizeOptions / ToggleSizeSelected on SizeCreatorView (analysis/xaml_bindings.json).
    // SizeOptions is the catalogue this dialog offers; ToggleSizeSelected flips one entry in the pick list.

    /// <summary>The sizes on offer here — the same ladder the task editor uses (bound as <c>SizeOptions</c>).</summary>
    public IReadOnlyList<string> SizeOptions =>
        Cybersole.Core.Models.SizePalette.Build(_services.Config.Settings.CustomSizes);

    /// <summary>Adds the size to the found list, or removes it if it is already there (bound as <c>ToggleSizeSelected</c>).</summary>
    public bool ToggleSizeSelected(string size)
    {
        if (string.IsNullOrWhiteSpace(size)) return false;

        var trimmed = size.Trim();
        if (_discovered.RemoveAll(s => string.Equals(s, trimmed, StringComparison.OrdinalIgnoreCase)) > 0)
            return false;   // removed

        _discovered.Add(trimmed);
        return true;        // added
    }

    /// <summary>What has been picked so far, in order.</summary>
    public IReadOnlyList<string> SelectedSizes => _discovered;

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('SizeCreatorView bound members added')
