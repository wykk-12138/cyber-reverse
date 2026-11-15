import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Proxies\ProxyView.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    private readonly IList<ProxyGroup> _groups;'''
add = '''    // ------------------------------------------------ copy from the image's locale (R393)

    /// <summary>"Delete {0} proxies?" — the delete confirmation's title.</summary>
    public const string DeleteConfirmTitleFormat = "Delete {0} proxies?";

    /// <summary>The delete confirmation's body.</summary>
    public const string DeleteConfirmMessageFormat =
        "Are you sure you want to delete {0} proxies?\\nYou cannot undo this action.";

    /// <summary>"Delete ({0}) proxies" — the confirmation's action button.</summary>
    public const string DeleteConfirmActionFormat = "Delete ({0}) proxies";

    /// <summary>"{0} Proxies Loaded" — the page footer.</summary>
    public const string LoadedFormat = "{0} Proxies Loaded";

    /// <summary>"{0} PROXIES SELECTED" — the selection counter.</summary>
    public const string SelectedManyFormat = "{0} PROXIES SELECTED";

    /// <summary>"{0} PROXY SELECTED" — the singular selection counter.</summary>
    public const string SelectedOneFormat = "{0} PROXY SELECTED";

    /// <summary>The footer for <paramref name="count"/> proxies.</summary>
    public static string Loaded(int count) => string.Format(LoadedFormat, count);

    /// <summary>The selection counter, singular when one proxy is selected.</summary>
    public static string SelectionCaption(int count) =>
        string.Format(count == 1 ? SelectedOneFormat : SelectedManyFormat, count);

''' + anchor
assert anchor in t and 'SelectedOneFormat' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('six proxy strings added')
