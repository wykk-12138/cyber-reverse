import io
for p in (r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md', r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'):
    raw = io.open(p, 'rb').read()
    print(p.split('\\')[-1], 'bytes:', len(raw), '| has BOM:', raw[:3] == b'\xef\xbb\xbf')
    head = raw[:120]
    try:
        txt = head.decode('utf-8')
        print('   utf-8 decodes ok:', txt[:60].replace('\n', ' '))
    except UnicodeDecodeError as e:
        print('   NOT utf-8:', e)
        print('   as gbk:', head.decode('gbk', 'replace')[:60])
