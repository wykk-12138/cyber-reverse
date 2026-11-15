import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs"
t = io.open(p, encoding='utf-8').read()
old = '''    public static string Loaded(int count) =>
        count == 1 ? LoadedOne : string.Format(LoadedFormat, count);'''
new = '''    /// <summary>"No Profiles Loaded" — the zero form (Profiles.LoadedNone).</summary>
    public const string LoadedNone = "No Profiles Loaded";

    public static string Loaded(int count) => count switch
    {
        0 => LoadedNone,
        1 => LoadedOne,
        _ => string.Format(LoadedFormat, count),
    };'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('ProfileView.Loaded now has the zero form')
