import io
for p in (r"D:\projects\cyber-reverse\docs\GOAL.md", r"D:\projects\cyber-reverse\AGENTS.md"):
    t = io.open(p, encoding='utf-8').read()
    n = t.count('docs\\BINDING_BACKLOG.md') + t.count('docs/BINDING_BACKLOG.md')
    t = t.replace('docs\\BINDING_BACKLOG.md', 'replica\\docs\\BINDING_BACKLOG.md')
    t = t.replace('docs/BINDING_BACKLOG.md', 'replica/docs/BINDING_BACKLOG.md')
    io.open(p, 'w', encoding='utf-8', newline='').write(t)
    print(p.split('\\')[-1], 'fixed refs:', n)
