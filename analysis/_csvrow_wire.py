import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>Splits the pasted text into rows, skipping a header line and blank lines.</summary>'''
add = '''    /// <summary>
    /// The pasted rows with per-row status (R314: the image binds ProfileCsvRow.FullySelected / RowStatus / RowError).
    ///
    /// <para>
    /// ProfileCount answers "how many"; this answers "which line is wrong". The column map is positional — the editor's
    /// column list is the order it accepts — so a row shorter than the list reports the tail columns as missing.
    /// </para>
    /// </summary>
    public IReadOnlyList<Modals.ProfileCsvRow> Rows
    {
        get
        {
            var map = ColumnNames
                .Select((name, index) => (name, index))
                .ToDictionary(pair => pair.name, pair => pair.index);

            var rows = Parse(_csv.Text ?? string.Empty);
            return rows.Select((cells, index) => new Modals.ProfileCsvRow(index + 1, cells, map)).ToList();
        }
    }

''' + anchor
assert anchor in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('Rows added to ProfileCsvEditorView')
