import io
t = io.open(r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md', encoding='utf-8').read()
lines = t.splitlines()
print('total lines', len(lines))
for l in lines[:30]:
    print(l[:100])
