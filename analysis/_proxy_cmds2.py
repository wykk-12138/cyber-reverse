import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Proxies\ProxyView.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''    /// <summary>Removes the selection (bound as <c>DeleteProxies</c>).</summary>'''
add = '''    /// <summary>
    /// Adds a group to the rail (bound as <c>CreateGroup</c>). The view is handed the live group list, so the group is
    /// created in the document the caller owns; it returns the new group so the caller can persist and select it.
    /// </summary>
    public ProxyGroup CreateGroup(string? name)
    {
        var group = new ProxyGroup
        {
            Name = string.IsNullOrWhiteSpace(name) ? $"Group {_groups.Count + 1}" : name!.Trim(),
        };
        _groups.Add(group);
        _onChanged?.Invoke();
        Content = Build();
        return group;
    }

    /// <summary>
    /// Moves the selected proxies into <paramref name="target"/> (bound as <c>MoveGroup</c>). Returns how many moved.
    /// </summary>
    public int MoveGroup(ProxyGroup target)
    {
        if (_grid is null || target is null) return 0;

        var picked = _grid.SelectedProxies.ToList();
        if (picked.Count == 0) return 0;

        foreach (var proxy in picked)
        {
            proxy.GroupId = target.Id;
            if (_mover is not null) _ = _mover(proxy, SourceGroupOf(proxy) ?? target);
        }

        _onChanged?.Invoke();
        Content = Build();
        return picked.Count;
    }

    /// <summary>Opens Settings' proxy page (bound as <c>OpenSettings</c>).</summary>
    public bool OpenSettings()
    {
        if (TopLevel.GetTopLevel(this) is not MainWindow shell) return false;
        return shell.Navigate("Settings");
    }

    /// <summary>
    /// How many proxy testers run at once (bound as <c>ProxyTesters</c>). Follows the global concurrency setting when
    /// the host supplies it, otherwise reports the single tester this page drives.
    /// </summary>
    public int ProxyTesters => _testerCount ?? 1;

    private int? _testerCount;

    /// <summary>Supplies the tester count; the caller owns the setting.</summary>
    public ProxyView WithTesterCount(int count)
    {
        _testerCount = count;
        return this;
    }

    /// <summary>
    /// The chord that runs "Test All", as the settings page stores it (bound as <c>TestAllKeybind</c>). Empty when the
    /// host has no keybind set.
    /// </summary>
    public string TestAllKeybind
    {
        get => _testAllKeybind ?? string.Empty;
        set => _testAllKeybind = value;
    }

    private string? _testAllKeybind;

    private ProxyGroup? SourceGroupOf(Proxy proxy) =>
        _groups.FirstOrDefault(g => g.Id == proxy.GroupId);

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ProxyView five bound commands added')
