import io, re
docs = ['docs/PARITY.md', 'docs/XAML_BINDINGS.md', 'docs/GUI_GEOMETRY.md', 'docs/BINDING_BACKLOG.md', 'docs/RESUME.md', 'docs/METHOD.md']
ratchet = re.search(r'MaxRealGap = (\d+)', io.open('tests/Cybersole.Tests/BindingGapRatchetTests.cs', encoding='utf-8').read()).group(1)
print('ratchet =', ratchet)
for d in docs:
    t = io.open(d, encoding='utf-8').read()
    old = [n for n in ('33', '43', '48', '31') if re.search(r'(?:缺口|gap)[^\n]{0,24}?' + n + r'\b', t)]
    if old:
        print('%-26s STALE: %s' % (d.split('/')[-1], old))
        for m in re.finditer(r'[^\n]*(?:缺口|gap)[^\n]*', t):
            line = m.group(0)
            if any(x in line for x in old): print('     ', line.strip()[:110])
    else:
        print('%-26s ok' % d.split('/')[-1])
