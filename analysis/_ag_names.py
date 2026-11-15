import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Accounts\AccountGrid.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''    // ---------------------------------------------------------------- actions'''
add = '''    // ------------------------------------------------ bound names (R236)
    //
    // The original binds these two on AccountGrid (analysis/xaml_bindings.json). The behaviour was already here as
    // CopySelectedAccount / CopySelectedPassword, reachable only from the row menu; the bound names are what a keybind
    // or a rebinding addresses. One implementation, two ways in.

    /// <summary>Copies the selected accounts (bound as <c>CopyAccounts</c>).</summary>
    public void CopyAccounts() => CopySelectedAccount();

    /// <summary>Copies the single selected account's password (bound as <c>CopyPassword</c>).</summary>
    public void CopyPassword() => CopySelectedPassword();

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('AccountGrid bound names added')
