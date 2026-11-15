import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Proxies\ProxyGroupView.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>Closes the hosting dialog (bound as <c>Close</c>). False when this control has no window.</summary>'''
add = '''    /// <summary>
    /// Deletes a proxy group from the configuration (bound as <c>Delete</c>). This view only edits ONE group — it has no
    /// list and no services handle — so the caller passes the list it came from; false when the group is not in it.
    /// </summary>
    public bool Delete(IList<ProxyGroup> from)
    {
        if (from is null || !from.Remove(_group)) return false;

        return true;
    }

''' + anchor
assert anchor in t and 'public bool Delete(' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('Delete(IList) added to ProxyGroupView')
