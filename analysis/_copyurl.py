import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''    /// <summary>Moves the group picker to the next group (bound as <c>NextGroup</c>).</summary>'''
add = '''    /// <summary>
    /// Copies the selected task's product URL (bound as <c>CopyUrl</c>). The URL copied is the one the engine monitors —
    /// <c>Product.Url</c> — and when the task has none the store's own domain is used, because that is the only other
    /// URL the app knows for it (the store modules claim their domains in <c>IStoreModule.Domains</c>).
    ///
    /// <para>
    /// R228 corrected R227: the previous round removed this command claiming "there is no URL source". That was wrong —
    /// <c>Product.Url</c> exists and <c>TaskEngine</c> polls it. The mistake was looking only at <c>BotTask</c>.
    /// </para>
    /// </summary>
    public bool CopyUrl(Action<string>? copyToClipboard = null)
    {
        var task = _grid?.SelectedTasks.FirstOrDefault();
        if (task is null) return false;

        var url = task.Product?.Url;
        if (string.IsNullOrWhiteSpace(url))
        {
            var module = _services.Stores.Modules.FirstOrDefault(m =>
                string.Equals(m.Name, task.Store, StringComparison.OrdinalIgnoreCase)
                || string.Equals(m.Id, task.Store, StringComparison.OrdinalIgnoreCase));
            var domain = module?.Domains.FirstOrDefault();
            if (!string.IsNullOrWhiteSpace(domain))
                url = domain.Contains("://", StringComparison.Ordinal) ? domain : "https://" + domain;
        }

        if (string.IsNullOrWhiteSpace(url)) return false;

        var sink = copyToClipboard ?? ClipboardWriter;
        if (sink is null)
        {
            _status.Text = url;
            return false;
        }

        sink(url);
        _status.Text = "Copied " + url;
        return true;
    }

    /// <summary>Where <see cref="CopyUrl"/> writes when the caller does not supply a sink.</summary>
    public Action<string>? ClipboardWriter { get; set; }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('CopyUrl restored with real semantics')
