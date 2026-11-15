import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs'
t = io.open(p, encoding='utf-8').read()

# CaptchaProvidersView: assign the field it reads
t = t.replace('''    public CaptchaProvidersView(AppServices services)
    {
        var registry = services.Captcha.Registry;''',
'''    public CaptchaProvidersView(AppServices services)
    {
        _services = services;
        RefreshProviders();
        var registry = services.Captcha.Registry;''', 1)

# DataView: the field was never needed — RefreshBackups only reads the backup directory
t = t.replace('''    private AppServices? _dataServices;
    private readonly List<string> _backupNames = new();''',
'''    private readonly List<string> _backupNames = new();''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ProviderViews: _services assigned, _dataServices removed')
