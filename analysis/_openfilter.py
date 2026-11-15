import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\MonitorWindow.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''    /// <summary>Minimises the window (bound as <c>Minimise</c>).</summary>'''
add = '''    /// <summary>
    /// Puts the cursor in the filter box and selects what is there, so typing replaces the old filter
    /// (bound as <c>OpenFilter</c> on the original's MonitorView).
    /// </summary>
    public void OpenFilter()
    {
        _filter.Focus();
        _filter.SelectAll();
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('MonitorWindow.OpenFilter added')

# lower the ratchet in the same change, as the discipline says
p2 = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('private const int MaxRealGap = 34;', 'private const int MaxRealGap = 33;')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('ratchet lowered to 33')
