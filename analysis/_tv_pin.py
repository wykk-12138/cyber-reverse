import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    public TaskGroup? SelectedGroup => _group;'''
add = '''    /// <summary>
    /// Pins or unpins the group on screen (bound as <c>PinGroups</c>). The image exposes it as a settable property, so the
    /// value is also the state; the group's own <c>Pinned</c> flag is what the picker reads.
    /// </summary>
    public bool PinGroups
    {
        get => _group?.Pinned ?? false;
        set
        {
            if (_group is null || _group.Pinned == value) return;

            _group.Pinned = value;
            _services.Config.Save();
        }
    }

''' + anchor
assert anchor in t and 'public bool PinGroups' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('TaskView.PinGroups added')
