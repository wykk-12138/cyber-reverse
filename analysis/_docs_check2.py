import io, re
for p in (r'D:\projects\cyber-reverse\docs\HANDOFF.md', r'D:\projects\cyber-reverse\docs\GOAL.md'):
    t = io.open(p, encoding='utf-8').read()
    print(p.split('\\')[-1], '| .NET 8:', len(re.findall(r'\.NET 8', t)), '| .NET 10:', len(re.findall(r'\.NET 10', t)), '| exe-reverse:', len(re.findall('exe-reverse', t)), '| pe_triage:', len(re.findall('pe_triage', t)))
