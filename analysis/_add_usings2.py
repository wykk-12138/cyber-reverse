import io
base = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings'
for name in ('ProviderViews.cs', 'SettingsViews.cs'):
    p = base + '\\' + name
    t = io.open(p, encoding='utf-8').read()
    if 'using Cybersole.Ui.Views.Common;' in t:
        print('already', name); continue
    # insert after the last existing using line
    lines = t.splitlines()
    last = max(i for i, l in enumerate(lines) if l.startswith('using '))
    lines.insert(last + 1, 'using Cybersole.Ui.Views.Common;')
    io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines) + '\n')
    print('using added', name)

# SettingsModals.cs:307 -- check what it is
import glob
for p in glob.glob(r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\**\SettingsModals.cs', recursive=True):
    t = io.open(p, encoding='utf-8').read()
    lines = t.splitlines()
    print(p.split('Views')[-1], 'line 307:', lines[306].strip())
    for i in range(300, 314):
        print(' ', i + 1, lines[i][:100])
