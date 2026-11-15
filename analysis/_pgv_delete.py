import io
p = r"../../replica/src/Cybersole.Ui/Views/Proxies/ProxyGroupView.cs".replace('../../replica/', 'D:\\projects\\cyber-reverse\\replica\\')
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Proxies\ProxyGroupView.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>Closes the hosting dialog (bound as <c>Close</c>). False when this control has no window.</summary>'''
add = '''    /// <summary>
    /// Removes the selected proxy group (bound as <c>Delete</c>). Returns false when nothing is selected, so a caller can
    /// tell "deleted" from "nothing to delete".
    /// </summary>
    public bool Delete()
    {
        var group = _groups.SelectedItem as ProxyGroup;
        if (group is null || !_groups.ItemsSource!.Contains(group)) return false;

        _services.Config.ProxyGroups.Remove(group);
        _services.Config.Save();
        return true;
    }

''' + anchor
if 'public bool Delete()' in t:
    print('already present')
else:
    assert anchor in t
    io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
    print('ProxyGroupView.Delete added')
