import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('        var configs = _services.Captcha.Configs.ToList();',
              '        var configs = _services.Captcha.Registry.Configs.ToList();', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('registry path fixed')
