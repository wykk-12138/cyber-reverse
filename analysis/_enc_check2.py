import io
p = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
raw = io.open(p, 'rb').read()
print('bytes:', len(raw), 'BOM:', raw[:3] == b'\xef\xbb\xbf')
try:
    txt = raw.decode('utf-8')
    print('WHOLE FILE DECODES AS UTF-8 OK')
    first = txt.splitlines()[0]
    print('line1 codepoints:', [hex(ord(c)) for c in first[:6]])
    print('line1 length:', len(first))
except UnicodeDecodeError as e:
    print('NOT utf-8:', e)
    print('as gb18030 line1:', raw.decode('gb18030', 'replace').splitlines()[0][:40])
