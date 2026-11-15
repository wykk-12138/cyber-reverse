import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Accounts\AccountView.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    public AccountGroup? SelectedGroup => _selectedGroup;'''
add = '''    // ------------------------------------------------ copy from the image's locale (R392)
    //
    // Ten strings the live page has and this view did not (Accounts.* in the string table). They are constants rather than
    // literals at the call sites so a test can assert them verbatim, which is how every other recovered string is kept.

    /// <summary>"Delete {0} accounts?" — the delete confirmation's title.</summary>
    public const string DeleteConfirmTitleFormat = "Delete {0} accounts?";

    /// <summary>The delete confirmation's body.</summary>
    public const string DeleteConfirmMessageFormat =
        "Are you sure you want to delete {0} accounts?\\nYou cannot undo this action.";

    /// <summary>"Delete ({0}) accounts" — the confirmation's action button.</summary>
    public const string DeleteConfirmActionFormat = "Delete ({0}) accounts";

    /// <summary>"Edit ({0})" — title of the edit-password dialog.</summary>
    public const string EditPasswordTitleFormat = "Edit ({0})";

    /// <summary>Shown when a search matches no account.</summary>
    public const string NoResultsSubtitle = "There are no accounts matching your search";

    /// <summary>The group list's delete entry.</summary>
    public const string DeleteGroupLabel = "Delete Group";

    /// <summary>"{0} Account Groups Loaded" — the group pane's footer.</summary>
    public const string GroupsLoadedFormat = "{0} Account Groups Loaded";

    /// <summary>"1 Account Group Loaded" — singular footer.</summary>
    public const string GroupsLoadedOne = "1 Account Group Loaded";

    /// <summary>"{0} ACCOUNTS SELECTED" — the selection counter.</summary>
    public const string SelectedManyFormat = "{0} ACCOUNTS SELECTED";

    /// <summary>"{0} ACCOUNT SELECTED" — the singular selection counter.</summary>
    public const string SelectedOneFormat = "{0} ACCOUNT SELECTED";

    /// <summary>The group-pane footer for <paramref name="count"/> groups, with the image's singular/plural split.</summary>
    public static string GroupsLoaded(int count) =>
        count == 1 ? GroupsLoadedOne : string.Format(GroupsLoadedFormat, count);

    /// <summary>The selection counter for <paramref name="count"/> accounts, singular when it is one.</summary>
    public static string SelectionCaption(int count) =>
        string.Format(count == 1 ? SelectedOneFormat : SelectedManyFormat, count);

''' + anchor
assert anchor in t and 'GroupsLoadedOne' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('ten copy strings added to AccountView')
