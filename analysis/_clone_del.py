import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''    /// <summary>Stops everything running (bound as <c>StopAll</c>).</summary>'''
add = '''    /// <summary>Duplicates the selection (bound as <c>CloneSelected</c>).</summary>
    public void CloneSelected() => _grid?.CloneSelectedTasks();

    /// <summary>Removes the selection (bound as <c>DeleteSelected</c>).</summary>
    public void DeleteSelected() => _grid?.DeleteSelectedTasks();

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('CloneSelected + DeleteSelected added')
