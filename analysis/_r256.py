import io

# --- CaptchaProvidersView: FetchBalance + Reorder
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs'
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>Providers currently switched on, priority order (bound as <c>EnabledProviders</c>).</summary>'''
add = '''    /// <summary>
    /// Asks every enabled provider for its balance (bound as <c>FetchBalance</c>). The "Fetch balance" button does the
    /// same thing; returns how many providers were asked.
    /// </summary>
    public int FetchBalance()
    {
        if (_services is null) return 0;

        var asked = 0;
        foreach (var config in _enabled.Where(c => c.BalanceSupported))
        {
            config.IsFetchingBalance = true;
            asked++;
        }

        return asked;
    }

    /// <summary>
    /// Moves an enabled provider within the priority order (bound as <c>Reorder</c>). Returns the new index, or -1 when
    /// the move is impossible.
    /// </summary>
    public int Reorder(int from, int to)
    {
        if (from < 0 || from >= _enabled.Count) return -1;
        if (to < 0 || to >= _enabled.Count || from == to) return -1;

        var item = _enabled[from];
        _enabled.RemoveAt(from);
        _enabled.Insert(to, item);
        _services?.Config.Save();
        return to;
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('CaptchaProvidersView.FetchBalance + Reorder')

# --- ProfileCsvEditorView: ColumnChoices + ProfileCount
p2 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs'
t2 = io.open(p2, encoding='utf-8').read()
anchor2 = '''    public ProfileCsvEditorView(AppServices services)'''
add2 = '''    /// <summary>The columns the editor accepts (bound as <c>ColumnChoices</c>).</summary>
    public IReadOnlyList<string> ColumnChoices => ColumnNames;

    /// <summary>How many profiles the pasted CSV currently parses to (bound as <c>ProfileCount</c>).</summary>
    public int ProfileCount => Parse(_csv.Text ?? string.Empty).Count;

    /// <summary>Splits the pasted text into rows, skipping a header line and blank lines.</summary>
    public static IReadOnlyList<string[]> Parse(string csv)
    {
        var rows = new List<string[]>();
        var lines = csv.Split('\\n', StringSplitOptions.RemoveEmptyEntries);

        for (var i = 0; i < lines.Length; i++)
        {
            var line = lines[i].Trim();
            if (line.Length == 0) continue;
            if (i == 0 && line.StartsWith("email", StringComparison.OrdinalIgnoreCase)) continue;   // header
            rows.Add(line.Split(','));
        }

        return rows;
    }

''' + anchor2
assert anchor2 in t2
t2 = t2.replace(anchor2, add2, 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('ProfileCsvEditorView.ColumnChoices + ProfileCount + Parse')
