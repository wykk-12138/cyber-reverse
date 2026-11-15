import io

# 1) NotificationsView.Types -> the same five categories the page tabs use
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs'
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>What the first switch on each tab says: "Allow " + tab + " Notifications".</summary>'''
add = '''    /// <summary>The notification categories (bound as <c>Types</c>) — the same five the tabs carry.</summary>
    public static IReadOnlyList<string> Types => Tabs;

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('NotificationsView.Types')

# 2) MainWindow.SettingsView -> the settings page on the Settings tab
p2 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\MainWindow.cs'
t2 = io.open(p2, encoding='utf-8').read()
anchor2 = '''    /// <summary>Opens the monitor window (bound as <c>OpenMonitor</c>).</summary>'''
add2 = '''    /// <summary>The settings page the Settings tab hosts (bound as <c>SettingsView</c>).</summary>
    public Control? SettingsView =>
        _tabs.ItemCount > 5 && _tabs.Items[5] is TabItem tab ? tab.Content as Control : null;

''' + anchor2
assert anchor2 in t2
t2 = t2.replace(anchor2, add2, 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('MainWindow.SettingsView')

# 3) StoreGroupModal.RemoveStore(name)
p3 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Utilities\UtilitiesViews.cs'
t3 = io.open(p3, encoding='utf-8').read()
anchor3 = '''public sealed class StoreGroupModal : Window
{'''
add3 = '''public sealed class StoreGroupModal : Window
{
    // R260: the original binds RemoveStore here (analysis/xaml_bindings.json) — the dialog edits a group, and a group
    // is a list of stores, so removing one belongs to it.

    /// <summary>The group being edited, or the one that will be created.</summary>
    private StoreGroup? _editing;

    /// <summary>
    /// Removes a store from the group being edited (bound as <c>RemoveStore</c>). Returns false when the group does not
    /// contain it. The caller saves afterwards, the same way the other rows of this dialog work.
    /// </summary>
    public bool RemoveStore(string storeId)
    {
        if (_editing is null || string.IsNullOrWhiteSpace(storeId)) return false;
        return _editing.Stores.Remove(storeId);
    }
'''
assert anchor3 in t3
t3 = t3.replace(anchor3, add3, 1)
t3 = t3.replace('''    public StoreGroupModal(AppServices services, StoreGroup? existing = null)
    {
        Title = existing is null ? "New store group" : $"Edit {existing.Name}";''',
'''    public StoreGroupModal(AppServices services, StoreGroup? existing = null)
    {
        _editing = existing;
        Title = existing is null ? "New store group" : $"Edit {existing.Name}";''', 1)
io.open(p3, 'w', encoding='utf-8', newline='').write(t3)
print('StoreGroupModal.RemoveStore')
