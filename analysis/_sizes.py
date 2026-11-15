import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding='utf-8').read()

anchor = '''    /// <summary>The page's count caption. The live page says "Custom Sizes" even at zero.</summary>
    public static string CountCaption(int count) =>
        count + (count == 1 ? " Custom Size" : " Custom Sizes");'''
add = anchor + '''

    /// <summary>The size presets on the page (bound as <c>Rows</c>).</summary>
    public IReadOnlyList<string> Rows => _sizeRows;

    /// <summary>
    /// Removes the preset at <paramref name="index"/> and saves (bound as <c>Delete</c>). <c>View</c> is bound too but
    /// its meaning is unknown, so it is listed in docs/BINDING_BACKLOG.md instead of being guessed.
    /// </summary>
    public bool Delete(int index)
    {
        if (index < 0 || index >= _sizeRows.Count) return false;

        _sizeRows.RemoveAt(index);
        _services.Config.Save();
        return true;
    }'''
assert anchor in t
t = t.replace(anchor, add, 1)

t = t.replace('''    public CustomSizesView(AppServices services)
    {
        var status = UiKit.Status();
        var sizes = new List<string>(services.Config.Settings.CustomSizes ?? new List<string>());''',
'''    private readonly AppServices _services = null!;
    private readonly List<string> _sizeRows = new();

    public CustomSizesView(AppServices services)
    {
        _services = services;
        var status = UiKit.Status();
        var sizes = new List<string>(services.Config.Settings.CustomSizes ?? new List<string>());
        _sizeRows.AddRange(sizes);''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('CustomSizesView: Rows + Delete')
