import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs"
t = io.open(p, encoding='utf-8').read()
old = '''    /// <summary>The filters caption with the image's zero / one / many forms.</summary>
    public static string FiltersCaption(int count) => count switch
    {
        0 => FiltersNone,
        1 => FiltersOne,
        _ => string.Format(FiltersCountFormat, count),
    };'''
new = '''    /// <summary>The filters caption with the image's zero / one / many forms (SmartActions.Filters.*).</summary>
    public static string FiltersCaption(int count) => count switch
    {
        0 => Text("FiltersNone"),
        1 => Text("FiltersOne"),
        _ => string.Format(Text("FiltersCountFormat"), count),
    };'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('FiltersCaption reads from the table')
