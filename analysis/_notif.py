import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Modals\CommonModals.cs"
t = io.open(p, encoding='utf-8').read()

# 1) header caption carries the count, as the live popup does ("0 Notifications")
old_title = '''                UiKit.Title("Notifications"),
                UiKit.Row("Clock", _clock),
                _items,'''
new_title = '''                // R336: the live popup's header is "{count} Notifications" beside a single Clear button. It has no
                // clock row and no Delete button (the whole panel tree was read off the running build), so both are
                // gone; the clock field stays for the task engine, it just is not shown here.
                _caption,
                _items,'''
assert old_title in t
t = t.replace(old_title, new_title, 1)

# 2) drop the Delete button and the Close button is the only extra (a window still needs one)
old_btns = '''                UiKit.Buttons(
                    new Button
                    {
                        Content = "Clear",
                        Command = new RelayCommand(() =>
                        {
                            _notifications.Clear();
                            Refresh();
                        }),
                    },
                    new Button
                    {
                        Content = "Delete",
                        Command = new RelayCommand(() =>
                        {
                            var i = _items.SelectedIndex;
                            if (i >= 0 && i < _notifications.Count)
                            {
                                _notifications.RemoveAt(i);
                                Refresh();
                            }
                        }),
                    },
                    new Button { Content = "Close", Command = new RelayCommand(Close) }),'''
new_btns = '''                UiKit.Buttons(
                    new Button
                    {
                        Content = "Clear",
                        Command = new RelayCommand(() =>
                        {
                            _notifications.Clear();
                            Refresh();
                        }),
                    },
                    new Button { Content = "Close", Command = new RelayCommand(Close) }),'''
assert old_btns in t
t = t.replace(old_btns, new_btns, 1)

# 3) empty state, verbatim, and the caption field
old_refresh = '''    private void Refresh() => _items.ItemsSource = _notifications.Count == 0
        ? new List<string> { "(nothing yet)" }
        : _notifications.ToList();'''
new_refresh = '''    /// <summary>The popup's second empty line, verbatim from the running build (R336).</summary>
    public const string EmptyBody = "Your notifications will show up here";

    private void Refresh()
    {
        _caption.Text = $"{_notifications.Count} Notifications";
        _items.ItemsSource = _notifications.Count == 0
            ? new List<string> { Common.EmptyView.Headline, EmptyBody }
            : _notifications.ToList();
    }'''
assert old_refresh in t
t = t.replace(old_refresh, new_refresh, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('NotificationView: caption + empty state, clock row and Delete removed')
