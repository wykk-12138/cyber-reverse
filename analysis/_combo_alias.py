import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Controls\ComboBoxEdit.cs"
t = io.open(p, encoding='utf-8').read()
old = '''    /// <summary>Raised after any change to Selected.</summary>'''
new = '''    /// <summary>
    /// The same removal under the original's binding name (the image binds RemoveTokenCommand here). Kept as a command
    /// over <see cref="RemoveToken"/> rather than a second code path, so there is one source of truth.
    /// </summary>
    public System.Windows.Input.ICommand RemoveTokenCommand =>
        _removeToken ??= new Cybersole.Core.Primitives.RelayCommand(() =>
        {
            if (_selected.Count > 0) RemoveToken(_selected[_selected.Count - 1]);
        });

    /// <summary>The same clear under the original's binding name (ClearSelectionCommand).</summary>
    public System.Windows.Input.ICommand ClearSelectionCommand =>
        _clearSelection ??= new Cybersole.Core.Primitives.RelayCommand(() => ClearSelection());

    private System.Windows.Input.ICommand? _removeToken;
    private System.Windows.Input.ICommand? _clearSelection;

    /// <summary>Raised after any change to Selected.</summary>'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('command aliases added')
