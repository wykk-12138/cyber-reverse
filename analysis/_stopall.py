import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''    /// <summary>Stops only the selected tasks (bound as <c>StopSelected</c>).</summary>'''
add = '''    /// <summary>Stops everything running (bound as <c>StopAll</c>).</summary>
    public void StopAll()
    {
        _services.Tasks.StopAll();
        Refresh();
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)

# the row-menu hook and the footer button go through the named command
t = t.replace('.WithStopper(() => { _services.Tasks.StopAll(); Refresh(); })', '.WithStopper(StopAll)', 1)
t = t.replace('            _services.Tasks.StopAll();', '            StopAll();', 1)

io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('StopAll added and wired')
