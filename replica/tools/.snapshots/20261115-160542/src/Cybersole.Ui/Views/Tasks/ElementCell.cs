namespace Cybersole.Ui.Views.Tasks;

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
    public string Name { get; set; }

    /// <summary>What the cell shows (bound as <c>Content</c>).</summary>
    public object Content { get; set; }

    /// <summary>Zero-based column (bound as <c>Column</c>).</summary>
    public int Column { get; set; }

    /// <summary>How many columns it covers; 1 unless a wide cell needs more (bound as <c>ColumnSpan</c>).</summary>
    public int ColumnSpan { get; set; }
}
