import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\BillingView.cs'
raw = io.open(p, 'rb').read()
print('has BOM:', raw[:3] == b'\xef\xbb\xbf')
t = raw.decode('utf-8', errors='replace')
bad = [i for i, ch in enumerate(t) if ch == '\ufffd']
print('replacement chars:', len(bad))
for line in t.splitlines():
    if 're-entrancy to gate' in line:
        print(repr(line))
