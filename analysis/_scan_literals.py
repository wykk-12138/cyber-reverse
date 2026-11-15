import io, re
base = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui'
files = [base + r'\Views\Settings\ProviderViews.cs', base + r'\Views\Settings\SettingsViews.cs', base + r'\Views\Settings\SettingsModals.cs']
for p in files:
    t = io.open(p, encoding='utf-8').read()
    for i, line in enumerate(t.splitlines(), 1):
        if '"Nothing to see here"' in line:
            kind = 'comment' if line.strip().startswith('//') else 'CODE'
            print('%s:%d [%s] %s' % (p.split('Views')[-1], i, kind, line.strip()[:110]))
