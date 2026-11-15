import io, os
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\ElementCell.cs"
t = '''namespace Cybersole.Ui.Views.Tasks;

/// <summary>
/// One cell placed on the task grid (Cybersole.Ui.Views.Tasks.ElementCell, R319).
///
/// <para>
/// The image binds Name / Content / Column / ColumnSpan on this. Column and ColumnSpan are what the grid needs to place
/// it, so the grid can build its rows from a list of cells instead of hard-coding every Grid.SetColumn call — which is
/// what the replica did until now ("34,1.3*,2.2*,1.2*,1.2*,1.1*,90" with SetColumn written out per child).
/// </para>
/// </summary>
public sealed class ElementCell
{
    public ElementCell(string name, object content, int column, int columnSpan = 1)
    {
        Name = name;
        Content = content;
        Column = column;
        ColumnSpan = columnSpan;
    }

    /// <summary>Identifies the cell in the grid (bound as <c>Name</c>).</summary>
    public string Name { get; }

    /// <summary>What the cell shows (bound as <c>Content</c>).</summary>
    public object Content { get; }

    /// <summary>Zero-based column (bound as <c>Column</c>).</summary>
    public int Column { get; }

    /// <summary>How many columns it covers; 1 unless a wide cell needs more (bound as <c>ColumnSpan</c>).</summary>
    public int ColumnSpan { get; }
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ElementCell written')

# use it in the grid so it is constructed in src (no baseline churn)
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskGrid.cs"
t2 = io.open(p2, encoding='utf-8').read()
anchor = '''        Grid.SetColumn(selectAll, 0);'''
add = '''        // R319: the cells of a header row are described as ElementCell so the placement rule lives in one place.
        foreach (var cell in new[]
                 {
                     new ElementCell("select-all", selectAll, 0),
                     new ElementCell("header-actions", _headerActions, 6),
                 })
        {
            Grid.SetColumn((Avalonia.Controls.Control)cell.Content, cell.Column);
            Grid.SetColumnSpan((Avalonia.Controls.Control)cell.Content, cell.ColumnSpan);
        }

''' + anchor
assert anchor in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(anchor, add, 1))
print('TaskGrid uses ElementCell')
