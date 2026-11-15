import io
pairs = [
 ("Title", "Utilities", "Utilities.Title"),
 ("Subtitle", "Reusable pieces you can share across your smart actions", "Utilities.Subtitle"),
 ("StoreGroupsTitle", "Store Groups", "Utilities.StoreGroups.Title"),
 ("StoreGroupsSubtitle", "Save a set of stores once and reuse it as a smart action filter", "Utilities.StoreGroups.Subtitle"),
 ("StoreGroupsNew", "New Group", "Utilities.StoreGroups.New"),
 ("StoreGroupsEmpty", "No store groups yet. Create one to reuse it as a filter.", "Utilities.StoreGroups.Empty"),
 ("ContextCloneFormat", "Clone {0}", "Utilities.StoreGroups.Context.CloneFormat"),
 ("ContextDeleteFormat", "Delete {0}", "Utilities.StoreGroups.Context.DeleteFormat"),
 ("ContextEditFormat", "Edit {0}", "Utilities.StoreGroups.Context.EditFormat"),
 ("DeleteTitleFormat", "Delete {0}?", "Utilities.StoreGroups.Delete.TitleFormat"),
 ("ModalTitleNew", "New Store Group", "Utilities.StoreGroups.Modal.Title.New"),
 ("ModalTitleEdit", "Store Group", "Utilities.StoreGroups.Modal.Title.Edit"),
 ("ModalName", "Group Name", "Utilities.StoreGroups.Modal.Name"),
 ("ModalNamePlaceholder", "Enter a group name", "Utilities.StoreGroups.Modal.NamePlaceholder"),
 ("ModalStores", "Stores", "Utilities.StoreGroups.Modal.Stores"),
 ("ModalStoresPlaceholder", "Add a store", "Utilities.StoreGroups.Modal.StoresPlaceholder"),
 ("ModalErrorDuplicate", "A store group with that name already exists", "Utilities.StoreGroups.Modal.Error.Duplicate"),
 ("ModalErrorNoName", "Enter a group name", "Utilities.StoreGroups.Modal.Error.NoName"),
]
lines = ['', "    // ------------------------------------------------ copy from the image's locale (R411)", '    //',
         "    // The Utilities.StoreGroups.* family, verbatim. Same shape as ProfileCsvEditorView.Copy: short name → text, with",
         "    // the locale key on each line. Two Delete messages are left out — their pool values are truncated mid-sentence.",
         "    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)",
         '    {']
for name, value, key in pairs:
    esc = value.replace('\\', '\\\\').replace('"', '\\"')
    lines.append('        ["%s"] = "%s",   // %s' % (name, esc, key))
lines.append('    };')
lines.append('')
lines.append("    /// <summary>One of the image's utilities-page strings, by the short name used in <see cref=\"Copy\"/>.</summary>")
lines.append('    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;')
lines.append('')
block = '\n'.join(lines)

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Utilities\UtilitiesViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    private readonly ListBox _groups = new() { Height = 260 };'''
assert anchor in t and 'IReadOnlyDictionary<string, string> Copy' not in t
t = t.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('18 Utilities strings captured')
