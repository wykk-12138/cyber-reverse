import io
p = r'D:\projects\cyber-reverse\replica\tools\flow_dump.py'
raw = io.open(p, 'rb').read().replace(b'\xef\xbb\xbf', b'')
io.open(p, 'wb').write(raw)
print('flow_dump.py shipped,', len(raw), 'bytes')
