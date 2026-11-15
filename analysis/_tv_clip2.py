import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs"
t = io.open(p, encoding='utf-8').read()

# clipboard seam: no Avalonia Application.Clipboard path (needs a TopLevel); read through the window when there is one
t = t.replace('''    public Func<string?> Clipboard { get; set; } = () =>
        Application.Current?.ApplicationLifetime is IClassicDesktopStyleApplicationLifetime
            ? (Application.Current.Clipboard?.GetTextAsync().GetAwaiter().GetResult()) : null;''',
'''    public Func<string?> Clipboard { get; set; } = () =>
    {
        // the clipboard lives on a TopLevel, so a view without a window simply has nothing to read
        var top = TopLevel.GetTopLevel(this);
        return top is null ? null : top.Clipboard?.GetTextAsync().GetAwaiter().GetResult();
    };''', 1)

# selection comes from the grid, as every other selection-bound member does
t = t.replace('        foreach (var task in SelectedTasks())', '        foreach (var task in _grid?.SelectedTasks ?? Enumerable.Empty<BotTask>())', 1)

# BotTask has no Url in this model; the task's product carries the link
t = t.replace('            task.Url = text;', '            task.Product = new Product { Name = task.Product?.Name ?? string.Empty, Image = text };', 1)
t = t.replace('            var task = new BotTask { Store = parts[0], Url = parts.Length > 1 ? parts[1] : null, GroupId = _group?.Id };',
              '            var task = new BotTask { Store = parts[0], GroupId = _group?.Id };', 1)
t = t.replace('            _services.Tasks.Add(task);', '            _group?.Tasks.Add(task);', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('adapted to the real model')
