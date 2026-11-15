import io
# 1) CSV editor: the multi-cell selection counter (ProfileCsv.Menu.SelectedCells)
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs"
t1 = io.open(p1, encoding='utf-8').read()
anchor1 = '''    /// <summary>The columns the editor accepts (bound as <c>ColumnChoices</c>).</summary>'''
add1 = '''    /// <summary>
    /// "{0} CELLS SELECTED" — the counter the CSV grid shows while several cells are picked
    /// (ProfileCsv.Menu.SelectedCells). The grid has no multi-cell selection yet, so this is the wording only.
    /// </summary>
    public const string SelectedCellsFormat = "{0} CELLS SELECTED";

    /// <summary>The counter for <paramref name="cells"/> picked cells.</summary>
    public static string SelectedCells(int cells) => string.Format(SelectedCellsFormat, cells);

''' + anchor1
assert anchor1 in t1 and 'SelectedCellsFormat' not in t1
io.open(p1, 'w', encoding='utf-8', newline='').write(t1.replace(anchor1, add1, 1))
print('ProfileCsvEditorView.SelectedCells added')

# 2) store groups page: "{0} stores" caption (Utilities.StoreGroups.CountFormat)
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Utilities\UtilitiesViews.cs"
t2 = io.open(p2, encoding='utf-8').read()
anchor2 = '''    private readonly ListBox _groups = new() { Height = 260 };'''
add2 = '''    /// <summary>"{0} stores" — the caption under the stores column (Utilities.StoreGroups.CountFormat).</summary>
    public const string StoresCountFormat = "{0} stores";

    /// <summary>The caption for <paramref name="count"/> stores.</summary>
    public static string StoresCount(int count) => string.Format(StoresCountFormat, count);

''' + anchor2
assert anchor2 in t2 and 'StoresCountFormat' not in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(anchor2, add2, 1))
print('UtilitiesView.StoresCount added')
