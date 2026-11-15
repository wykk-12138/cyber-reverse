import io, re
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs"
t = io.open(p, encoding='utf-8').read()

anchor = '''    public void OpenTaskCreator() => OpenEditor(null);'''
add = '''    // ── the bound names this control carries (R344) ───────────────────────────────────────────────────
    // Cybersole.Ui.Views.TaskView binds 29 operations. Some already exist under a working name (that is what the
    // properties below do); the rest are listed in docs/BINDING_BACKLOG.md as "bound but behaviour not yet recovered",
    // because inventing what Ctrl+M or "Pin Groups" does would be worse than leaving it named.

    /// <summary>Empties the current group (bound as <c>ClearAll</c>; the button says "Clear Tasks").</summary>
    public void ClearAll() => ClearTasks();

    /// <summary>Opens the Settings shell (bound as <c>OpenSettings</c>, as on the proxies page).</summary>
    public bool OpenSettings()
    {
        var shell = TopLevel.GetTopLevel(this) as MainWindow;
        if (shell is null) return false;
        shell.Navigate("Settings");
        return true;
    }

    public void OpenTaskCreator() => OpenEditor(null);'''
assert anchor in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('ClearAll + OpenSettings added')
