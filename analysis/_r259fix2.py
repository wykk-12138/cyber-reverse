import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Modals\CommonModals.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('        await _services.Auth.SignOutAsync().ConfigureAwait(true);',
              '        _services.Auth.SignOut();', 1)
t = t.replace('    public async Task<bool> LogOutAsync()', '    public bool LogOut()', 1)
t = t.replace('''        if (_services is null) return false;

        _services.Auth.SignOut();
        Close();
        return true;''',
'''        if (_services is null) return false;

        _services.Auth.SignOut();
        Close();
        return true;''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('UserView.LogOut uses Auth.SignOut (synchronous)')
