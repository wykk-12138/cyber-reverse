import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Proxies\ProxyView.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    private readonly AppServices _services;'''
print('anchor present:', anchor in t)
print('mentions SelectedOneFormat:', 'SelectedOneFormat' in t)
print('mentions DeleteConfirm:', 'DeleteConfirm' in t)
i = t.find('class ProxyView')
print(t[i:i+400].replace('\n', ' | ')[:380])
