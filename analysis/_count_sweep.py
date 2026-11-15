import io, re
# the docs that quote UI-class counts must agree with the scan (104 / 31)
pats = {'PARITY.md': r'(\d+) 个 UI 类：(\d+) 个 `Window` 子类 \+ (\d+) 个 `UserControl` 子类',
        'VERDICT.md': r'\| UI 类 \| (\d+) 个，\*\*(\d+) 个不可达\*\*',
        'RESUME.md': r'不可达 UI 类 \| \*\*(\d+)\*\*（(\d+) 个中）'}
for f, pat in pats.items():
    t = io.open('docs/' + f, encoding='utf-8').read()
    m = re.search(pat, t)
    print('%-12s %s' % (f, m.groups() if m else 'no match'))
