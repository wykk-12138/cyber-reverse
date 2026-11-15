import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Modals\CommonModals.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('if (Owner is { } host)\n                                _ = new Common.ViewHostModal("Sign in", login, 520, 460).ShowDialog(host);',
              'if (Owner is Window host)\n                                _ = new Common.ViewHostModal("Sign in", login, 520, 460).ShowDialog(host);', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('Window typed')
