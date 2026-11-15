import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Controls\ComboBoxEdit.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('''    public System.Windows.Input.ICommand RemoveTokenCommand =>''',
'''    public System.Windows.Input.ICommand RemoveTokenCommand
    {
        get =>''', 1)
t = t.replace('''            if (_selected.Count > 0) RemoveToken(_selected[_selected.Count - 1]);
        });''',
'''            if (_selected.Count > 0) RemoveToken(_selected[_selected.Count - 1]);
        });
        set => _removeToken = value;
    }''', 1)
t = t.replace('''    public System.Windows.Input.ICommand ClearSelectionCommand =>
        _clearSelection ??= new RelayCommand(() => ClearSelection());''',
'''    public System.Windows.Input.ICommand ClearSelectionCommand
    {
        get => _clearSelection ??= new RelayCommand(() => ClearSelection());
        set => _clearSelection = value;
    }''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ComboBoxEdit commands are settable now')
