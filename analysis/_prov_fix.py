import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs'
t = io.open(p, encoding='utf-8').read()
# the class already had a _disabled list — reuse it, drop my duplicate
t = t.replace('''    private AppServices? _services;
    private readonly List<CaptchaProviderConfig> _disabled = new();

    /// <summary>Providers currently switched on''',
'''    private AppServices? _services;

    /// <summary>Providers currently switched on''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('duplicate _disabled removed')
