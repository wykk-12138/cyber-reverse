import io
t = io.open(r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md', encoding='utf-8').read().splitlines()
for line in t[:14]:
    print(line[:120])
