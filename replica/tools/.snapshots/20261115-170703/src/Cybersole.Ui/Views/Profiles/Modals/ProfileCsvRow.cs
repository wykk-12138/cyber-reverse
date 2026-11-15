using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Ui.Views.Profiles.Modals;

/// <summary>
/// One row of a pasted profile CSV (Cybersole.Ui.Views.Profiles.Modals.ProfileCsvRow, R314).
///
/// <para>
/// The image binds four things on this row: Number, FullySelected, RowStatus and RowError. That is enough to say what a
/// row has to carry and not enough to say how it looks, so this is the data a row exposes — the editor decides how to
/// show it. The rules below are written so they can be tested without a window, which is the only reason they are stated
/// this precisely.
/// </para>
/// </summary>
public sealed class ProfileCsvRow
{
    public ProfileCsvRow(int number, IReadOnlyList<string> cells, IReadOnlyDictionary<string, int> columnMap)
    {
        Number = number;
        Cells = cells;
        ColumnMap = columnMap;

        var missing = columnMap
            .Where(pair => pair.Value < 0 || pair.Value >= cells.Count || string.IsNullOrWhiteSpace(cells[pair.Value]))
            .Select(pair => pair.Key)
            .ToList();

        FullySelected = missing.Count == 0;

        if (cells.Count == 0 || cells.All(string.IsNullOrWhiteSpace))
        {
            RowError = "Row is empty";
            RowStatus = "Empty";
        }
        else if (missing.Count > 0)
        {
            RowError = "Missing " + string.Join(", ", missing);
            RowStatus = $"{columnMap.Count - missing.Count} of {columnMap.Count} columns mapped";
        }
        else
        {
            RowError = string.Empty;
            RowStatus = $"Ready ({cells.Count} columns)";
        }
    }

    /// <summary>The 1-based line the row came from (bound as <c>Number</c>).</summary>
    public int Number { get; set; }

    /// <summary>The raw cells.</summary>
    public IReadOnlyList<string> Cells { get; }

    /// <summary>Column name to cell index.</summary>
    public IReadOnlyDictionary<string, int> ColumnMap { get; }

    /// <summary>True when every mapped column resolves to a non-empty cell (bound as <c>FullySelected</c>).</summary>
    public bool FullySelected { get; set; }

    /// <summary>One line describing the row (bound as <c>RowStatus</c>).</summary>
    public string RowStatus { get; set; }

    /// <summary>Empty when the row is usable, otherwise the first problem (bound as <c>RowError</c>).</summary>
    public string RowError { get; set; }

    public override string ToString() => $"#{Number} {RowStatus}" + (RowError.Length > 0 ? " — " + RowError : string.Empty);
}
