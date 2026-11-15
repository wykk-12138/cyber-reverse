import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    private void Save()
    {
        try'''
add = '''    /// <summary>
    /// Removes this group from the configuration (bound as <c>Delete</c> — the live dialog's red button, R350).
    /// Returns false when the group was never saved, so a caller can tell "deleted" from "nothing to delete".
    /// </summary>
    public bool DeleteGroup()
    {
        if (!_services.Config.TaskGroups.Remove(_group)) return false;

        _services.Config.Save();
        _status.Text = "Group deleted.";
        return true;
    }

    private void Save()
    {
        try'''
assert anchor in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('DeleteGroup added')
