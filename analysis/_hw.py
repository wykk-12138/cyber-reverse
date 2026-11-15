import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>Closes the history window (bound as <c>Exit</c>).</summary>'''
add = '''    /// <summary>
    /// Which smart action's history is on screen, or null for all of them (bound as <c>SmartAction</c>). Setting it filters the
    /// list; the window title follows <c>HistoryWindow.LogsFormat</c> — "{0} - Logs".
    /// </summary>
    public SmartAction? SmartAction
    {
        get => _smartAction;
        set
        {
            _smartAction = value;
            Title = string.Format(LocaleLogsFormat, value?.Name ?? "All smart actions");
            Refresh();
        }
    }

    /// <summary>Which of the two views is shown — "History" or "Logs" (bound as <c>View</c>).</summary>
    public string View
    {
        get => _view;
        set
        {
            _view = value;
            Refresh();
        }
    }

    /// <summary>Title format the image uses for this window (<c>HistoryWindow.LogsFormat</c>).</summary>
    public const string LocaleLogsFormat = "{0} - Logs";

    private SmartAction? _smartAction;
    private string _view = "History";

''' + anchor
assert anchor in t and 'public SmartAction? SmartAction' not in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('HistoryWindow gains SmartAction + View')
