import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Accounts\AccountView.cs"
t = io.open(p, encoding='utf-8').read()
anchor = 'public sealed class AccountView'
i = t.index(anchor); brace = t.index('{', i); line_end = t.index('\n', brace) + 1
add = '''
    /// <summary>
    /// "Are you sure you want to delete the {0} account group?\\nYou cannot undo this action."
    /// (Accounts.Group.DeleteConfirm.MessageFormat) — the group-delete confirmation, wired to the group pane's Delete.
    /// </summary>
    public const string DeleteGroupConfirmFormat =
        "Are you sure you want to delete the {0} account group?\\nYou cannot undo this action.";

    /// <summary>The confirmation text for deleting the group named <paramref name="group"/>.</summary>
    public static string DeleteGroupConfirm(string group) => string.Format(DeleteGroupConfirmFormat, group);
'''
t = t[:line_end] + add + t[line_end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('DeleteGroupConfirm added to AccountView')
