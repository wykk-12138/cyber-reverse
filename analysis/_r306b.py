import io
jobs = [
 (r'D:\projects\cyber-reverse\replica\src\Cybersole.Services\Captcha\ThirdPartyDrivers.cs', 'json=', '(R298)'),
 (r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\FarfetchFlow.cs', 'ffid', '(R297)'),
]
for p, needle, tag in jobs:
    lines = io.open(p, encoding='utf-8').read().split('\n')
    n = 0
    for i, l in enumerate(lines):
        s = l.strip()
        if needle in l and not s.startswith('//') and 'inferred: no image evidence' not in l:
            lines[i] = l.rstrip() + '  // inferred: no image evidence ' + tag
            n += 1
    io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    print('marked', n, 'line(s) for', needle, 'in', p.split('\\')[-1])
