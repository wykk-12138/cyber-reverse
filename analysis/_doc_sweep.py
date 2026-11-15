import io, re, glob, json
docs = ['docs/PARITY.md', 'docs/XAML_BINDINGS.md', 'docs/GUI_GEOMETRY.md', 'docs/BINDING_BACKLOG.md', 'docs/RESUME.md']
ratchet = re.search(r'MaxRealGap = (\d+)', io.open('tests/Cybersole.Tests/BindingGapRatchetTests.cs', encoding='utf-8').read()).group(1)
print('ratchet =', ratchet)
for d in docs:
    t = io.open(d, encoding='utf-8').read()
    gaps = sorted(set(re.findall(r'(?:缺口|gap|MaxRealGap)[^\n]{0,20}?(\d{1,3})', t)))
    nums = sorted(set(re.findall(r'\b(\d{2,4})\b', t)))
    print('%-28s 提到的缺口类数字: %s' % (d.split('/')[-1], gaps[:6]))
    stray = [n for n in nums if n == '33' or n == '43' or n == '48']
    if stray: print('    ⚠ 旧缺口数字仍出现:', stray)
