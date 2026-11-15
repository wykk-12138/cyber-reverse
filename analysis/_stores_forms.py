import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Utilities\UtilitiesViews.cs"
t = io.open(p, encoding='utf-8').read()
old = '''    /// <summary>"{0} stores" — the caption under the stores column (Utilities.StoreGroups.CountFormat).</summary>
    public const string StoresCountFormat = "{0} stores";

    /// <summary>The caption for <paramref name="count"/> stores.</summary>
    public static string StoresCount(int count) => string.Format(StoresCountFormat, count);'''
new = '''    /// <summary>"{0} stores" — the caption under the stores column (Utilities.StoreGroups.CountFormat).</summary>
    public const string StoresCountFormat = "{0} stores";

    /// <summary>"No stores" — the zero form (Utilities.StoreGroups.CountNone).</summary>
    public const string StoresCountNone = "No stores";

    /// <summary>"1 store" — the singular form (Utilities.StoreGroups.CountOne is "1 " + the noun).</summary>
    public const string StoresCountOne = "1 store";

    /// <summary>The caption for <paramref name="count"/> stores, with the image's zero and one forms.</summary>
    public static string StoresCount(int count) => count switch
    {
        0 => StoresCountNone,
        1 => StoresCountOne,
        _ => string.Format(StoresCountFormat, count),
    };'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('StoresCount now has zero and one forms')
