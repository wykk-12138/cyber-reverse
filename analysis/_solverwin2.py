import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SolverWindow.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    private readonly AppServices _services;'''
add = '''    /// <summary>Minimises the solver window (bound as <c>Minimise</c>).</summary>
    public void Minimise() => WindowState = WindowState.Minimized;

    /// <summary>
    /// Closes and releases the window (bound as <c>Dispose</c>). Avalonia's Window is already disposable, so this makes the
    /// bound name exist and closes first, leaving one behaviour no matter which name a caller uses.
    /// </summary>
    public new void Dispose()
    {
        Close();
        base.Dispose();
    }

''' + anchor
assert anchor in t and 'public void Minimise()' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('SolverWindow.Minimise + Dispose added')
