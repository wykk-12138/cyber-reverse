import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\BillingView.cs'
lines = io.open(p, encoding='utf-8').read().splitlines()
for i, l in enumerate(lines[56:66], 57):
    print(i, repr(l))
