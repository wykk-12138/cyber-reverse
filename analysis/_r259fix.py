import io
# GroupGrid: remember the selected key from SetRows instead of inventing a property
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Common\GroupGrid.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('        var selected = SelectedKey;', '        var selected = _selectedKey;', 1)
t = t.replace('    /// <summary>Raised when the bound command asks to delete the selected group (bound as <c>DeleteGroup</c>).</summary>',
'''    private string? _selectedKey;

    /// <summary>The row key the caller last marked as selected.</summary>
    public string? SelectedKey => _selectedKey;

    /// <summary>Raised when the bound command asks to delete the selected group (bound as <c>DeleteGroup</c>).</summary>''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('GroupGrid keeps _selectedKey')

# SetRows must record it: patch the signature body
import re
m = re.search(r'public void SetRows\(IEnumerable<\(string Key, string Name, string Badge\)> rows, string\? selectedKey[^)]*\)\s*\{', t)
if m:
    t2 = t[:m.end()] + '\n        _selectedKey = selectedKey;' + t[m.end():]
    io.open(p, 'w', encoding='utf-8', newline='').write(t2)
    print('SetRows records the selection')
else:
    print('SetRows signature not matched — inspect manually')

# UserView: the sign-out lives on Auth
p2 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Modals\CommonModals.cs'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('        await _services.Session.SignOutAsync().ConfigureAwait(true);',
                '        await _services.Auth.SignOutAsync().ConfigureAwait(true);', 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('UserView uses Auth.SignOutAsync')
