import io, re
for p in (r'D:\projects\cyber-reverse\docs\HANDOFF.md', r'D:\projects\cyber-reverse\docs\GOAL.md'):
    t = io.open(p, encoding='utf-8').read()
    print('==', p.split('\\')[-1], len(t), 'chars')
    for pat, label in ((r'\.NET 8', '.NET 8'), (r'net8', 'net8'), (r'exe-reverse', 'exe-reverse'), (r'pe_triage', 'pe_triage')):
        print('   %-14s %d' % (label, len(re.findall(pat, t))))
