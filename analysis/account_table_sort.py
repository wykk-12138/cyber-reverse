import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding="utf-8").read()

start = t.find("public sealed class AccountTable : UserControl")
end = t.find("/// <summary>General settings (Cybersole.Ui.Views.Settings.GeneralSettingsView).</summary>")
if start < 0 or end < 0 or end <= start:
    raise SystemExit("AccountTable bounds: %d .. %d" % (start, end))

# keep the doc comment that precedes the class
doc_start = t.rfind("/// <summary>", 0, start)
if doc_start < 0 or doc_start > start:
    doc_start = start

new_class = '''/// <summary>
/// A small table for the three account pages: a clickable header row, one row per record, and the
/// two-line empty state the live pages print.
///
/// <para>
/// R84: the three pages had a <see cref="ListBox"/> of formatted strings and nothing else — no
/// columns, and a single-line empty state. The live pages are tables, and the columns came off the
/// running build in R75 (Host / Email / Inbox Count, Name / Email, Email / Status); the binary's
/// locale carries the same sets as <c>Settings.Google.Header.*</c> and
/// <c>Settings.PayPal.Header.*</c>.
/// </para>
///
/// <para>
/// R85: the headers said <c>⇅</c> and did nothing — a dead affordance of exactly the kind
/// <c>DeadButtonTests</c> exists to catch. They are buttons now, and clicking one sorts by that
/// column, toggling ascending/descending, with the glyph following (<c>↑</c> / <c>↓</c> / <c>⇅</c>).
/// </para>
/// </summary>
public sealed class AccountTable : UserControl
{
    private readonly Grid _header = new();
    private readonly StackPanel _body = new();
    private readonly StackPanel _empty;
    private readonly string _columnTemplate;
    private readonly List<Button> _headers = new();

    private int _sortColumn = -1;
    private bool _ascending = true;

    public AccountTable(IReadOnlyList<string> columns, string emptyTitle, string emptySubtitle)
    {
        Columns = columns;
        _columnTemplate = "34," + string.Join(",", columns.Select(_ => "1*"));

        _header.ColumnDefinitions = new ColumnDefinitions(_columnTemplate);
        _header.Children.Add(new TextBlock { Text = string.Empty });

        for (var i = 0; i < columns.Count; i++)
        {
            var index = i;
            var head = new Button
            {
                Content = columns[i] + " ⇅",
                Background = Avalonia.Media.Brushes.Transparent,
                BorderThickness = new Thickness(0),
                Padding = new Thickness(4, 0),
                HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Left,
                HorizontalContentAlignment = Avalonia.Layout.HorizontalAlignment.Left,
                Opacity = 0.7,
            };
            head.Click += (_, _) => SortBy(index);
            Grid.SetColumn(head, i + 1);
            _header.Children.Add(head);
            _headers.Add(head);
        }

        _empty = new StackPanel
        {
            Spacing = 4,
            Margin = new Thickness(0, 30),
            Children =
            {
                new TextBlock
                {
                    Text = emptyTitle,
                    HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                    FontWeight = Avalonia.Media.FontWeight.SemiBold,
                },
                new TextBlock
                {
                    Text = emptySubtitle,
                    HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                    Opacity = 0.6,
                },
            },
        };

        Content = new StackPanel { Spacing = 2, Children = { _header, _body, _empty } };
        Rows = Array.Empty<string[]>();
    }

    /// <summary>The column captions, in order.</summary>
    public IReadOnlyList<string> Columns { get; }

    /// <summary>The selected row, or -1.</summary>
    public int SelectedIndex { get; private set; } = -1;

    /// <summary>Which column the rows are ordered by, or -1 for as-given.</summary>
    public int SortColumn => _sortColumn;

    /// <summary>True when the current sort is ascending.</summary>
    public bool SortAscending => _ascending;

    private string[][] _rows = Array.Empty<string[]>();

    /// <summary>Replaces the rows and repaints. An empty array shows the empty state.</summary>
    public string[][] Rows
    {
        get => _rows;
        set
        {
            _rows = value;
            SelectedIndex = value.Length == 0 ? -1 : Math.Clamp(SelectedIndex, -1, value.Length - 1);
            Repaint();
        }
    }

    /// <summary>Selects a row index (or -1).</summary>
    public void Select(int index)
    {
        SelectedIndex = index >= 0 && index < _rows.Length ? index : -1;
        Repaint();
    }

    /// <summary>
    /// Orders by <paramref name="column"/>: the first click sorts ascending, a second click on the
    /// same column reverses it. Ordinal comparison — these are hostnames, addresses and counts, not
    /// prose.
    /// </summary>
    public void SortBy(int column)
    {
        if (column < 0 || column >= Columns.Count) return;

        if (_sortColumn == column) _ascending = !_ascending;
        else { _sortColumn = column; _ascending = true; }

        Repaint();
    }

    /// <summary>The rows in display order — what the body actually shows.</summary>
    public string[][] Ordered()
    {
        if (_sortColumn < 0) return _rows;

        var column = _sortColumn;
        var ordered = _ascending
            ? _rows.OrderBy(r => Cell(r, column), StringComparer.Ordinal)
            : _rows.OrderByDescending(r => Cell(r, column), StringComparer.Ordinal);

        return ordered.ToArray();
    }

    private static string Cell(string[] row, int column) =>
        column >= 0 && column < row.Length ? row[column] ?? string.Empty : string.Empty;

    private void Repaint()
    {
        for (var i = 0; i < _headers.Count; i++)
        {
            var glyph = _sortColumn == i ? (_ascending ? " ↑" : " ↓") : " ⇅";
            _headers[i].Content = Columns[i] + glyph;
        }

        _body.Children.Clear();

        var rows = Ordered();
        for (var r = 0; r < rows.Length; r++)
        {
            var index = r;
            var row = new Grid
            {
                ColumnDefinitions = new ColumnDefinitions(_columnTemplate),
                Background = r == SelectedIndex
                    ? new Avalonia.Media.SolidColorBrush(Avalonia.Media.Color.Parse("#1C2330"))
                    : Avalonia.Media.Brushes.Transparent,
            };

            var check = new CheckBox { IsChecked = r == SelectedIndex, Margin = new Thickness(4, 0, 0, 0) };
            check.IsCheckedChanged += (_, _) =>
            {
                if (check.IsChecked == true) Select(index);
            };
            row.Children.Add(check);

            for (var c = 0; c < rows[r].Length && c < Columns.Count; c++)
            {
                var cell = new TextBlock
                {
                    Text = rows[r][c],
                    VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
                    Margin = new Thickness(4, 4, 4, 4),
                    TextTrimming = Avalonia.Media.TextTrimming.CharacterEllipsis,
                };
                Grid.SetColumn(cell, c + 1);
                row.Children.Add(cell);
            }

            _body.Children.Add(row);
        }

        var any = rows.Length > 0;
        _header.IsVisible = any;
        _body.IsVisible = any;
        _empty.IsVisible = !any;
    }
}

'''

t = t[:doc_start] + new_class + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("AccountTable now sorts")
