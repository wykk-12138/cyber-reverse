import io
for p in (r'D:\projects\cyber-reverse\replica\docs\METHOD.md', r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'):
    raw = io.open(p, 'rb').read()
    try:
        txt = raw.decode('utf-8')
        print(p.split('\\')[-1], ': valid utf-8 |', txt.splitlines()[0][:40])
    except UnicodeDecodeError as e:
        print(p.split('\\')[-1], ': NOT utf-8 ->', e)
