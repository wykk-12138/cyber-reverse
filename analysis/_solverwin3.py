import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SolverWindow.cs"
t = io.open(p, encoding='utf-8').read()
old = '''    /// <summary>
    /// Closes and releases the window (bound as <c>Dispose</c>). Avalonia's Window is already disposable, so this makes the
    /// bound name exist and closes first, leaving one behaviour no matter which name a caller uses.
    /// </summary>
    public new void Dispose()
    {
        Close();
        base.Dispose();
    }'''
new = '''    /// <summary>
    /// Closes the window and stops its queue polling (bound as <c>Dispose</c>). Avalonia's <c>Window</c> has no
    /// <c>Dispose</c> of its own — the bound name is the only one — so this is the single release path.
    /// </summary>
    public void Dispose() => Close();'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('Dispose simplified')
