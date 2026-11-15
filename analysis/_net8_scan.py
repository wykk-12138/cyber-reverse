import io, re
paths = [r'D:\projects\cyber-reverse\AGENTS.md', r'D:\projects\cyber-reverse\docs\GOAL.md',
         r'D:\projects\cyber-reverse\docs\HANDOFF.md', r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md']
for p in paths:
    t = io.open(p, encoding='utf-8').read()
    hits = [m.start() for m in re.finditer(r'\.NET 8|net8\.0|NET 8', t)]
    if hits:
        print('--', p.split('\\')[-1], len(hits))
        for h in hits[:3]:
            print('   ', t[max(0,h-70):h+40].replace('\n',' '))
