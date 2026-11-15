import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    private readonly AppServices _services;
    private readonly ListBox _profiles = new() { Height = 340 };'''
add = '''    // ------------------------------------------------ copy from the image's locale (R395)

    /// <summary>"Clone Profiles" — the context menu's clone entry.</summary>
    public const string ContextClone = "Clone Profiles";

    /// <summary>"Create Test Profile" — the context menu's test entry.</summary>
    public const string ContextCreateTest = "Create Test Profile";

    /// <summary>"Open in CSV Editor" — the context menu's csv entry.</summary>
    public const string ContextCsvEditor = "Open in CSV Editor";

    /// <summary>"Delete Profiles" — the context menu's delete entry.</summary>
    public const string ContextDelete = "Delete Profiles";

    /// <summary>"Edit Profiles" — the context menu's edit entry.</summary>
    public const string ContextEdit = "Edit Profiles";

    /// <summary>"Delete {0} profiles?" — the delete confirmation's title.</summary>
    public const string DeleteConfirmTitleFormat = "Delete {0} profiles?";

    /// <summary>The delete confirmation's body.</summary>
    public const string DeleteConfirmMessageFormat =
        "Are you sure you want to delete {0} profiles?\\nYou cannot undo this action.";

    /// <summary>"Delete ({0}) profiles" — the confirmation's action button.</summary>
    public const string DeleteConfirmActionFormat = "Delete ({0}) profiles";

    /// <summary>Shown when a search matches no profile.</summary>
    public const string NoResultsSubtitle = "There are no profiles matching your search";

    /// <summary>"{0} Profiles Loaded" / "1 Profile Loaded" — the page footer.</summary>
    public const string LoadedFormat = "{0} Profiles Loaded";

    /// <summary>The singular footer.</summary>
    public const string LoadedOne = "1 Profile Loaded";

    /// <summary>"{0} PROFILES SELECTED" / "{0} PROFILE SELECTED" — the selection counter.</summary>
    public const string SelectedManyFormat = "{0} PROFILES SELECTED";

    /// <summary>The singular selection counter.</summary>
    public const string SelectedOneFormat = "{0} PROFILE SELECTED";

    /// <summary>The footer for <paramref name="count"/> profiles.</summary>
    public static string Loaded(int count) =>
        count == 1 ? LoadedOne : string.Format(LoadedFormat, count);

    /// <summary>The selection counter, singular when one profile is selected.</summary>
    public static string SelectionCaption(int count) =>
        string.Format(count == 1 ? SelectedOneFormat : SelectedManyFormat, count);

''' + anchor
assert anchor in t and 'ContextCsvEditor' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('thirteen profile strings added')
