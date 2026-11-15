import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''    private void Render()'''
add = '''    /// <summary>
    /// Shows every row, whatever the filter says (bound as <c>ShowAll</c>). The original's history window binds it,
    /// and the replica had only the combo.
    /// </summary>
    public void ShowAll()
    {
        _filter.SelectedIndex = 0;   // "All"; the SelectionChanged handler re-renders
        Render();
    }

    /// <summary>The rows currently on screen, for callers and tests.</summary>
    public IReadOnlyList<object> Rows => _rows.ItemsSource?.Cast<object>().ToList() ?? new List<object>();

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('HistoryWindow.ShowAll added')
