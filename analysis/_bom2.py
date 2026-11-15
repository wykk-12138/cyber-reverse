import io
p = r'D:\projects\cyber-reverse\replica\tools\backlog_report.py'
raw = io.open(p, 'rb').read()
print('starts with BOM:', raw[:3] == b'\xef\xbb\xbf')
raw = raw.replace(b'\xef\xbb\xbf', b'')
io.open(p, 'wb').write(raw)
print('bytes written:', len(raw))
