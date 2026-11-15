import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\LoginControlTests.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('Assert.Contains("ViewHostModal(\\"Sign in\\"", modal);',
              '// R217: the host is the measured "Login" window at 1536x814, not a small "Sign in" card\n        Assert.Contains("ViewHostModal(\\"Login\\", login, 1536, 814)", modal);')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('login entry assertion updated')
