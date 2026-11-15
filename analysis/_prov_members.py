import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs'
t = io.open(p, encoding='utf-8').read()

# --- CaptchaProvidersView: EnabledProviders / DisabledProviders
anchor1 = '''    public CaptchaProvidersView(AppServices services)'''
add1 = '''    // ------------------------------------------------ bound members (R240)
    //
    // The original binds EnabledProviders / DisabledProviders on CaptchaProvidersView (analysis/xaml_bindings.json).
    // The page splits the registry into two lists; these properties are that split, named.

    private AppServices? _services;
    private readonly List<CaptchaProviderConfig> _disabled = new();

    /// <summary>Providers currently switched on, priority order (bound as <c>EnabledProviders</c>).</summary>
    public IReadOnlyList<CaptchaProviderConfig> EnabledProviders => _enabled;

    /// <summary>Providers currently switched off, priority order (bound as <c>DisabledProviders</c>).</summary>
    public IReadOnlyList<CaptchaProviderConfig> DisabledProviders => _disabled;

    /// <summary>Rebuilds the two lists from the registry.</summary>
    public void RefreshProviders()
    {
        if (_services is null) return;

        var configs = _services.Captcha.Configs.ToList();
        _enabled.Clear();
        _enabled.AddRange(configs.Where(c => c.Enabled).OrderByDescending(c => c.Priority));
        _disabled.Clear();
        _disabled.AddRange(configs.Where(c => !c.Enabled).OrderByDescending(c => c.Priority));
    }

''' + anchor1
assert anchor1 in t
t = t.replace(anchor1, add1, 1)

# --- DataView: DataProviders / ViewBackups
anchor2 = '''    public DataView(AppServices services)'''
add2 = '''    // ------------------------------------------------ bound members (R240)
    //
    // The original binds DataProviders / ViewBackups on DataView (analysis/xaml_bindings.json): the first is the
    // export/import kind list, the second is the backup list the page shows.

    private AppServices? _dataServices;
    private readonly List<string> _backupNames = new();

    /// <summary>The data kinds this page can export/import (bound as <c>DataProviders</c>).</summary>
    public IReadOnlyList<string> DataProviders => ExportKinds;

    /// <summary>The backup files currently listed, newest first (bound as <c>ViewBackups</c>).</summary>
    public IReadOnlyList<string> ViewBackups => _backupNames;

    /// <summary>Re-reads the backup directory into <see cref="ViewBackups"/>.</summary>
    public IReadOnlyList<string> RefreshBackups()
    {
        _backupNames.Clear();
        var dir = new DirectoryInfo(Cybersole.Core.Store.AppPaths.BackupsDir);
        if (dir.Exists)
            _backupNames.AddRange(dir.GetFiles("*.cyb")
                .OrderByDescending(f => f.LastWriteTime)
                .Select(f => $"{f.Name}  ({f.Length / 1024} KB)"));

        return _backupNames;
    }

''' + anchor2
assert anchor2 in t
t = t.replace(anchor2, add2, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('CaptchaProvidersView + DataView bound members added')
