import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Auth\LoginControl.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('using Cybersole.Services;', 'using Cybersole.Services;\nusing Cybersole.Services.Auth;', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('using added')
