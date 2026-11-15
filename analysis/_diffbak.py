import io, difflib, os
bak = r'tools\.mutation-backup'
pairs = {
 'PARITY.md': r'docs\PARITY.md',
 'Cybersole.Core.csproj': r'src\Cybersole.Core\Cybersole.Core.csproj',
 'TasksViews.cs': r'src\Cybersole.Ui\Views\Tasks\TasksViews.cs',
 'SolverWindow.cs': r'src\Cybersole.Ui\Views\SolverWindow.cs',
 'ShopifyFlow.cs': r'src\Cybersole.Stores\Flows\ShopifyFlow.cs',
 'SettingsShell.cs': r'src\Cybersole.Ui\Views\Settings\SettingsShell.cs',
 'ChromiumBridge.cs': r'src\Cybersole.Stores\Scripts\ChromiumBridge.cs',
 'ProviderViews.cs': r'src\Cybersole.Ui\Views\Settings\ProviderViews.cs',
 'SettingsViews.cs': r'src\Cybersole.Ui\Views\Settings\SettingsViews.cs',
 'HttpAnalytics.cs': r'src\Cybersole.Http\HttpAnalytics.cs',
}
for k, live in pairs.items():
    b = io.open(os.path.join(bak,k), encoding='utf-8', errors='replace').read().splitlines()
    l = io.open(live, encoding='utf-8', errors='replace').read().splitlines()
    d = [x for x in difflib.unified_diff(b, l, lineterm='', n=0)][2:]
    print('=====', k, 'diff lines', len(d))
    for line in d[:6]:
        print('   ', line[:130])
