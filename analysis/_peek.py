import io
t = io.open(r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md', encoding='utf-8').read()
print(t[:1400].encode('unicode_escape').decode()[:1200])
