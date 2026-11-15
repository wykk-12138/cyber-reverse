import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding='utf-8').read()

# CustomStoresView: expose the rows and a delete-by-index (both bound; View is not — its meaning is unknown)
anchor = '''    /// <summary>The page's count caption. The live page says "Presets" even at zero.</summary>
    public static string CountCaption(int count) => count + (count == 1 ? " Preset" : " Presets");'''
add = anchor + '''

    /// <summary>The presets on the page (bound as <c>Rows</c>).</summary>
    public IReadOnlyList<CustomStore> Rows => _storeRows;

    /// <summary>
    /// Removes the preset at <paramref name="index"/> and saves (bound as <c>Delete</c>). False when the index is out of
    /// range. <c>View</c> is bound too but its meaning is unknown, so it is listed in docs/BINDING_BACKLOG.md instead.
    /// </summary>
    public bool Delete(int index)
    {
        if (index < 0 || index >= _storeRows.Count) return false;

        _storeRows.RemoveAt(index);
        _services.Config.Save();
        return true;
    }'''
assert anchor in t
t = t.replace(anchor, add, 1)

# the class needs the services handle and a stable row list
t = t.replace('''    public CustomStoresView(AppServices services)
    {
        var status = UiKit.Status();
        var stores = services.Config.Settings.CustomStores ?? new List<CustomStore>();''',
'''    private readonly AppServices _services = null!;
    private readonly List<CustomStore> _storeRows = new();

    public CustomStoresView(AppServices services)
    {
        _services = services;
        var status = UiKit.Status();
        var stores = services.Config.Settings.CustomStores ?? new List<CustomStore>();
        _storeRows.AddRange(stores);''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('CustomStoresView: Rows + Delete')
