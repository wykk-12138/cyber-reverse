import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Proxies\ProxyView.cs'
t = io.open(p, encoding='utf-8').read()

# R226: the original binds these on ProxyView by name (xaml_bindings.json). The replica had the behaviour inside
# inline lambdas, so the names did not exist. Buttons now call named methods.
old_add = '''        var add = UiKit.Button("Add Proxies", () =>
        {
            if (_importer is not null && _importer(target))
            {
                _onChanged?.Invoke();
                Content = Build();
            }
        });'''
new_add = '''        var add = UiKit.Button("Add Proxies", () => AddProxies(target));'''
assert old_add in t
t = t.replace(old_add, new_add, 1)

old_clear = '''        var clearAll = UiKit.Button("Clear All", () =>
        {
            target.Proxies.Clear();
            _onChanged?.Invoke();
            Content = Build();
        });'''
new_clear = '''        var clearAll = UiKit.Button("Clear All", () => ClearAll(target));'''
assert old_clear in t
t = t.replace(old_clear, new_clear, 1)

# the named commands, right before the hooks region
anchor = '    // ---------------------------------------------------------------- hooks'
add = '''    // ------------------------------------------------ bound commands (R226)
    //
    // The original's compiled XAML binds these names on ProxyView:
    //   AddProxies, ClearAll, ClearFailed, ClearOver, CloneProxies, CopyProxies, CreateGroup, Delete, DeleteProxies,
    //   Groups, MoveGroup, OpenSettings, ProxyTesters, Test, TestAll, TestAllKeybind, TestProxies
    // (analysis/xaml_bindings.json). The replica had the behaviour but not the names, inside inline lambdas. A name is
    // what a rebinding, a keybind or a test can reach, so the behaviour now lives behind the original's vocabulary.

    /// <summary>Imports proxies into the selected group (bound as <c>AddProxies</c>).</summary>
    public void AddProxies(ProxyGroup group)
    {
        if (_importer is null || !_importer(group)) return;
        _onChanged?.Invoke();
        Content = Build();
    }

    /// <summary>Empties the selected group (bound as <c>ClearAll</c>).</summary>
    public void ClearAll(ProxyGroup group)
    {
        group.Proxies.Clear();
        _onChanged?.Invoke();
        Content = Build();
    }

    /// <summary>Copies the selection to the clipboard (bound as <c>CopyProxies</c>).</summary>
    public void CopyProxies() => _grid?.CopySelected();

    /// <summary>Duplicates the selection in place (bound as <c>CloneProxies</c>).</summary>
    public void CloneProxies()
    {
        if (_grid is null) return;
        foreach (var proxy in _grid.SelectedProxies.ToList()) _grid.CloneProxy(proxy);
        _onChanged?.Invoke();
        Content = Build();
    }

    /// <summary>Removes the selection (bound as <c>DeleteProxies</c>).</summary>
    public void DeleteProxies()
    {
        if (_grid is null) return;
        _grid.DeleteSelected();
        _onChanged?.Invoke();
        Content = Build();
    }

    /// <summary>Tests the selection against the echo service (bound as <c>TestProxies</c>).</summary>
    public void TestProxies()
    {
        if (_grid is null) return;
        foreach (var proxy in _grid.SelectedProxies.ToList()) _grid.TestProxy(proxy);
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ProxyView: named bound commands added and wired')
