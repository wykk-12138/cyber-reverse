import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    private Control Build()'''
member = '''    // ------------------------------------------------ clipboard actions (R372)
    //
    // The locale names both of these and both failure dialogs verbatim:
    //   Tasks.LinkChange.InvalidTitle  = "Invalid URL"
    //   Tasks.LinkChange.InvalidMessage= "The value retrieved from clipboard is not a valid URL."
    //   Tasks.Quicktask.InvalidTitle   = "Invalid Quicktask"
    //   Tasks.Quicktask.InvalidMessage = "The value retrieved from clipboard is not a valid Quicktask format."
    //   Monitor.LinkChange = "Link Change"   Monitor.LaunchQuicktask = "Launch Quicktask"
    // So both read the clipboard, validate it, and complain with those exact words otherwise.

    /// <summary>Where the two clipboard actions read from — a seam so a test can drive them without a real clipboard.</summary>
    public Func<string?> Clipboard { get; set; } = () =>
        Application.Current?.ApplicationLifetime is IClassicDesktopStyleApplicationLifetime
            ? (Application.Current.Clipboard?.GetTextAsync().GetAwaiter().GetResult()) : null;

    /// <summary>
    /// Applies the URL on the clipboard to every selected task, or reports the image's own failure wording (bound as
    /// <c>LinkChange</c>; the menu calls it "Link Change").
    /// </summary>
    public string LinkChange()
    {
        var text = (Clipboard?.Invoke() ?? string.Empty).Trim();

        if (!Uri.TryCreate(text, UriKind.Absolute, out var uri) || (uri.Scheme != "http" && uri.Scheme != "https"))
            return InvalidLinkChangeTitle + "\\n" + InvalidLinkChangeMessage;

        var changed = 0;
        foreach (var task in SelectedTasks())
        {
            task.Url = text;
            changed++;
        }

        _services.Config.Save();
        return "Linked " + changed + (changed == 1 ? " task" : " tasks") + " to " + text;
    }

    /// <summary>
    /// Creates tasks from the quicktask string on the clipboard, or reports the image's own failure wording (bound as
    /// <c>Quicktask</c>; the menu calls it "Launch Quicktask").
    /// </summary>
    public string Quicktask()
    {
        var text = (Clipboard?.Invoke() ?? string.Empty).Trim();

        // one task per line: "store | url" — the format the settings page configures
        var lines = text.Split('\\n', StringSplitOptions.RemoveEmptyEntries)
            .Select(l => l.Trim()).Where(l => l.Length > 0).ToList();

        if (lines.Count == 0 || lines.Any(l => !l.Contains('|')))
            return InvalidQuicktaskTitle + "\\n" + InvalidQuicktaskMessage;

        var created = 0;
        foreach (var line in lines)
        {
            var parts = line.Split('|', 2, StringSplitOptions.TrimEntries);
            var task = new BotTask { Store = parts[0], Url = parts.Length > 1 ? parts[1] : null, GroupId = _group?.Id };

            _services.Tasks.Add(task);
            created++;
        }

        _services.Config.Save();
        return "Created " + created + (created == 1 ? " task" : " tasks");
    }

    /// <summary>Title the image shows when the clipboard is not a URL.</summary>
    public const string InvalidLinkChangeTitle = "Invalid URL";

    /// <summary>Message the image shows when the clipboard is not a URL.</summary>
    public const string InvalidLinkChangeMessage = "The value retrieved from clipboard is not a valid URL.";

    /// <summary>Title the image shows when the clipboard is not a quicktask.</summary>
    public const string InvalidQuicktaskTitle = "Invalid Quicktask";

    /// <summary>Message the image shows when the clipboard is not a quicktask.</summary>
    public const string InvalidQuicktaskMessage = "The value retrieved from clipboard is not a valid Quicktask format.";

''' + anchor
assert anchor in t and 'public string LinkChange()' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, member, 1))
print('LinkChange + Quicktask added')
